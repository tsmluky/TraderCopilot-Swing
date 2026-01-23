# backend/evaluated_logger.py
from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple

from indicators.market import get_market_data, EXCHANGE_ID


BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
LITE_DIR = LOGS_DIR / "LITE"
EVAL_DIR = LOGS_DIR / "EVALUATED"

# Tiempo mínimo (en minutos) desde la señal hasta la evaluación
# Para pruebas lo dejamos en 0; cuando todo funcione, súbelo a 120.
EVAL_DELAY_MIN = 0

# Umbral para considerar un movimiento como "neutral" aunque no haya tocado TP/SL (en %)
NEUTRAL_THRESHOLD_PCT = 0.20

EVAL_HEADERS = [
    "signal_ts",
    "evaluated_at",
    "token",
    "timeframe",
    "entry",
    "tp",
    "sl",
    "price_at_eval",
    "result",
    "move_pct",
    "notes",
    "source",
]


def _parse_iso_ts(ts_str: str) -> datetime:
    """
    Parsea timestamps tipo '2025-11-16T14:00:00Z' a datetime naive UTC.
    """
    s = ts_str.strip()
    if s.endswith("Z"):
        s = s[:-1]
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        # Si está corrupto, lo tratamos como "ahora" para que se salte
        dt = datetime.utcnow()
    return dt


def _load_evaluated_signal_ts(token: str) -> Set[str]:
    """
    Devuelve el conjunto de timestamps (signal_ts) ya evaluados para un token.
    """
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    path = EVAL_DIR / f"{token}.evaluated.csv"
    if not path.exists():
        return set()

    ts_set: Set[str] = set()
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = row.get("signal_ts")
            if ts:
                ts_set.add(ts)
    return ts_set


def _append_evaluations(token: str, rows: List[Dict[str, str]]) -> int:
    """
    Añade las evaluaciones al CSV de EVALUATED/{token}.evaluated.csv.
    Y TAMBIÉN guarda en la base de datos (SignalEvaluation).
    Devuelve el número de filas nuevas escritas.
    """
    # 1. CSV
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    path = EVAL_DIR / f"{token}.evaluated.csv"
    file_exists = path.exists()

    if not rows:
        return 0

    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EVAL_HEADERS)
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)

    # 2. DB
    try:
        from backend.database import SessionLocal
        from backend.models_db import (
            Signal,
            SignalEvaluation,
        )
        from sqlalchemy import select

        db = SessionLocal()
        strategies_to_update = set()

        try:
            for row in rows:
                # Buscar la señal original
                ts_str = row.get("signal_ts")
                if not ts_str:
                    continue

                # Parse timestamp to match DB format
                try:
                    ts_dt = _parse_iso_ts(ts_str)
                except Exception:
                    continue

                # Buscar Signal por token y timestamp
                stmt = select(Signal).where(
                    Signal.token == token.upper(), Signal.timestamp == ts_dt
                )
                signal_obj = db.execute(stmt).scalars().first()

                if not signal_obj:
                    # Fallback: buscar por rango de 1 segundo
                    stmt = select(Signal).where(
                        Signal.token == token.upper(),
                        Signal.timestamp >= ts_dt - timedelta(seconds=1),
                        Signal.timestamp <= ts_dt + timedelta(seconds=1),
                    )
                    signal_obj = db.execute(stmt).scalars().first()

                if signal_obj:
                    # Verificar si ya tiene evaluación
                    if signal_obj.evaluation:
                        continue

                    # Crear evaluación
                    eval_obj = SignalEvaluation(
                        signal_id=signal_obj.id,
                        evaluated_at=datetime.utcnow(),
                        result=row.get("result"),
                        pnl_r=0.0,
                        exit_price=float(row.get("price_at_eval", 0)),
                    )
                    db.add(eval_obj)

                    # Mark strategy for stats update if present
                    if signal_obj.strategy_id:
                        strategies_to_update.add(signal_obj.strategy_id)

            db.commit()

            # 3. Update Strategy Stats
            for strat_id in strategies_to_update:
                _update_strategy_stats(strat_id, db)

        except Exception as e:
            print(f"[DB ERROR] Error guardando evaluaciones en DB: {e}")
            db.rollback()
        finally:
            db.close()

    except ImportError:
        print("[DB WARNING] No se pudieron importar modelos DB. Solo se guardó CSV.")
    except Exception as e:
        print(f"[DB ERROR] Fallo general DB: {e}")

    return len(rows)


def _update_strategy_stats(strategy_id: str, db) -> None:
    """Recalculate and update stats for a given strategy."""
    from models_db import Signal, SignalEvaluation, StrategyConfig
    from sqlalchemy import func

    # Count total evaluated for this strategy
    total_eval = (
        db.query(func.count(SignalEvaluation.id))
        .join(Signal, Signal.id == SignalEvaluation.signal_id)
        .filter(Signal.strategy_id == strategy_id)
        .scalar()
        or 0
    )

    # Count wins (hit-tp)
    total_wins = (
        db.query(func.count(SignalEvaluation.id))
        .join(Signal, Signal.id == SignalEvaluation.signal_id)
        .filter(Signal.strategy_id == strategy_id)
        .filter(SignalEvaluation.result == "hit-tp")
        .scalar()
        or 0
    )

    # Calculate Rate
    win_rate = (total_wins / total_eval) if total_eval > 0 else 0.0

    # Update Config
    strat_config = (
        db.query(StrategyConfig)
        .filter(StrategyConfig.strategy_id == strategy_id)
        .first()
    )
    if strat_config:
        strat_config.win_rate = win_rate
        db.commit()
        print(
            f"[STATS] Updated {strategy_id}: WinRate={win_rate:.2%} ({total_wins}/{total_eval})"
        )


def _evaluate_signal_row(row: Dict[str, str]) -> Dict[str, str]:
    """
    Dada una fila de logs LITE, calcula la evaluación:

    - result ∈ {"hit-tp", "hit-sl", "open", "neutral"}
    - move_pct en porcentaje (ej. +1.23)
    """
    token = row.get("token", "").upper() or "UNKNOWN"
    timeframe = row.get("timeframe", "30m")
    direction = row.get("direction", "long").lower()
    signal_ts_str = row.get("timestamp", "")

    # Parse numéricos básicos
    try:
        entry = float(row.get("entry", "0") or 0)
        tp = float(row.get("tp", "0") or 0)
        sl = float(row.get("sl", "0") or 0)
    except ValueError:
        entry = 0.0
        tp = 0.0
        sl = 0.0

    evaluated_at_dt = datetime.utcnow()

    # Si entry no tiene sentido, devolvemos neutral
    if entry <= 0:
        return {
            "signal_ts": signal_ts_str,
            "evaluated_at": evaluated_at_dt.replace(microsecond=0).isoformat() + "Z",
            "token": token,
            "timeframe": timeframe,
            "entry": f"{entry:.2f}",
            "tp": f"{tp:.2f}",
            "sl": f"{sl:.2f}",
            "price_at_eval": f"{entry:.2f}",
            "result": "neutral",
            "move_pct": "0.0",
            "notes": "Entrada inválida al evaluar; marcado como neutral.",
        }

    # Obtener precio actual via capa Quant existente
    df, market = get_market_data(token.lower(), timeframe)
    if not market:
        price_at_eval = entry
        result = "neutral"
        move_pct_pct = 0.0
        notes = f"Sin market data en evaluación ({EXCHANGE_ID}, {timeframe})."
    else:
        price_at_eval = float(market["price"])
        notes = f"Evaluado via {EXCHANGE_ID} en {timeframe}."

        if direction == "long":
            if price_at_eval >= tp > 0:
                result = "hit-tp"
            elif price_at_eval <= sl < entry:
                result = "hit-sl"
            else:
                result = "open"
            move_pct_pct = (price_at_eval / entry - 1.0) * 100.0
        else:  # short
            if price_at_eval <= tp < entry:
                result = "hit-tp"
            elif price_at_eval >= sl > 0:
                result = "hit-sl"
            else:
                result = "open"
            move_pct_pct = (entry / price_at_eval - 1.0) * 100.0

        # Ajuste a neutral si el movimiento es insignificante Y ha pasado tiempo (2h)
        ts_dt = _parse_iso_ts(signal_ts_str)
        age = datetime.utcnow() - ts_dt
        if (
            result == "open"
            and age > timedelta(hours=2)
            and abs(move_pct_pct) < NEUTRAL_THRESHOLD_PCT
        ):
            result = "neutral"

    eval_row = {
        "signal_ts": signal_ts_str,
        "evaluated_at": evaluated_at_dt.replace(microsecond=0).isoformat() + "Z",
        "token": token,
        "timeframe": timeframe,
        "entry": f"{entry:.2f}",
        "tp": f"{tp:.2f}",
        "sl": f"{sl:.2f}",
        "price_at_eval": f"{price_at_eval:.2f}",
        "result": result,
        "move_pct": f"{move_pct_pct:.3f}",
        "notes": notes,
        "source": row.get("source", "UNKNOWN"),
    }

    return eval_row


def _eligible_signals_for_token(token: str) -> List[Dict[str, str]]:
    """
    Carga las señales LITE de logs/LITE/{token}.csv que:

    - tengan al menos EVAL_DELAY_MIN minutos de antigüedad
    - aún no estén en logs/EVALUATED/{token}.evaluated.csv
    """
    lite_path = LITE_DIR / f"{token}.csv"
    if not lite_path.exists():
        return []

    already_eval = _load_evaluated_signal_ts(token)

    now = datetime.utcnow()
    min_age = timedelta(minutes=EVAL_DELAY_MIN)

    candidates: List[Dict[str, str]] = []

    with lite_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts_str = row.get("timestamp", "")
            if not ts_str:
                continue

            if ts_str in already_eval:
                continue

            ts = _parse_iso_ts(ts_str)
            if now - ts >= min_age:
                candidates.append(row)

    return candidates


def evaluate_all_tokens() -> Tuple[int, int]:
    """
    Recorre todos los CSV en logs/LITE/ y evalúa las señales pendientes
    para cada token.

    Devuelve (num_tokens_procesados, num_evaluaciones_nuevas).
    """
    if not LITE_DIR.exists():
        print("[EVAL] No existe logs/LITE, nada que evaluar.")
        return 0, 0

    tokens = sorted(p.stem for p in LITE_DIR.glob("*.csv"))
    total_tokens = 0
    total_evals = 0

    for token in tokens:
        total_tokens += 1
        pending_rows = _eligible_signals_for_token(token)
        if not pending_rows:
            # print(f"[EVAL] {token}: sin señales elegibles.") # Less verbose
            continue

        eval_rows_to_save: List[Dict[str, str]] = []
        for row in pending_rows:
            eval_result = _evaluate_signal_row(row)

            # SOLO guardar si es terminal (TP/SL/Neutral).
            # Si sigue OPEN, la ignoramos para que se re-evalue luego.
            if eval_result["result"] in ["hit-tp", "hit-sl", "neutral"]:
                eval_rows_to_save.append(eval_result)
            else:
                # pass # Debug: print(f"Signal {row.get('timestamp')} is still OPEN")
                pass

        if eval_rows_to_save:
            written = _append_evaluations(token, eval_rows_to_save)
            total_evals += written
            print(f"[EVAL] {token}: {written} señales finalizadas (TP/SL/Neutral).")

    if total_evals > 0:
        print(
            f"[EVAL] Resumen → tokens: {total_tokens}, evaluaciones nuevas: {total_evals}"
        )
    return total_tokens, total_evals


def main() -> None:
    evaluate_all_tokens()


if __name__ == "__main__":
    main()
