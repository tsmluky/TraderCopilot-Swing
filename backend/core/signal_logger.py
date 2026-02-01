# backend/core/signal_logger.py
"""
Unified Signal Logger for TraderCopilot Signal Hub.

Este módulo centraliza TODA la escritura de señales (CSV + DB),
independientemente de su origen (LITE, PRO, ADVISOR, CUSTOM, etc.).

Responsabilidad única: recibir una instancia de Signal y persistirla
en el formato adecuado para logs CSV y base de datos.
"""

from __future__ import annotations
import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from .schemas import Signal


# === Configuración de rutas ===
BACKEND_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BACKEND_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Headers estándar de CSV (compatibles con el schema Signal)
CSV_HEADERS = [
    "timestamp",
    "token",
    "timeframe",
    "direction",
    "entry",
    "tp",
    "sl",
    "confidence",
    "rationale",
    "source",
]


def log_signal(signal: Signal, db_session: Any = None) -> Optional[int]:
    """
    Guarda una señal en DB (Canonical) y si tiene éxito, en CSV.

    Args:
        signal: Instancia del modelo Signal unificado
        db_session: (Opcional) Sesión SQLalchemy existente para reutilizar.

    Returns:
        bool: True si se insertó una NUEVA señal, False si era duplicada o falló.
    """

    mode = signal.mode.upper()
    
    # === 1. Persistir en DB (CANONICAL SOURCE OF TRUTH) ===
    # Si falla dedupe aquí, abortamos todo lo demás.
    saved_id, is_new = _write_to_db(signal, mode, db_session=db_session)
    
    if not saved_id:
        return False
    
    # Si ya existía, retornamos False y no hacemos CSV/Push (idempotency)
    if not is_new:
        return False

    # === 2. Persistir en CSV (Solo si es nueva) ===
    token_lower = signal.token.lower()
    _write_to_csv(signal, mode, token_lower)
    
    # === 3. Push Notification (Mobile) ===
    _send_push_notification(signal)
    
    return saved_id



def _snap_to_grid(dt: datetime, tf_str: str) -> datetime:
    """
    Normaliza el timestamp al inicio de la vela correspondiente.
    Soporta formatos: 5m, 15m, 30m, 1h, 4h, 1d.
    """
    dt = dt.replace(second=0, microsecond=0)
    
    match = re.match(r"(\d+)([mhd])", tf_str)
    if not match:
        return dt # Fallback: return truncated seconds
        
    val = int(match.group(1))
    unit = match.group(2)
    
    if unit == 'm':
        # Minute snapping
        minute = (dt.minute // val) * val
        return dt.replace(minute=minute)
    elif unit == 'h':
        # Hour snapping (assumes val divides 24 or starts at 00:00)
        total_hours = dt.hour
        snapped_hours = (total_hours // val) * val
        return dt.replace(hour=snapped_hours, minute=0)
    elif unit == 'd':
        # Day snapping
        return dt.replace(hour=0, minute=0)
        
    return dt


def _write_to_db(signal: Signal, mode: str, db_session: Any = None) -> tuple[Optional[int], bool]:
    """
    Retorna (id, is_new).
    is_new=True si se hizo INSERT.
    is_new=False si ya existía (deduplicado).
    """
    try:
        from database import SessionLocal
        from models_db import Signal as SignalDB
        from sqlalchemy.exc import IntegrityError

        # 1) Normalize timestamp al inicio de vela (canonical)
        ts_normalized = _snap_to_grid(signal.timestamp, signal.timeframe)
        ts_iso = ts_normalized.isoformat()

        # 2) Idempotency key (estable)
        idem_key = (
            f"{signal.strategy_id}|{signal.token.upper()}|{signal.timeframe}|"
            f"{ts_iso}|{signal.direction.lower()}|{signal.user_id}|{signal.mode}"
        )

        # 3) Construir fila DB
        db_signal = SignalDB(
            timestamp=ts_normalized,
            token=signal.token.upper(),
            timeframe=signal.timeframe,
            direction=signal.direction.lower(),
            entry=signal.entry,
            tp=signal.tp if signal.tp else 0.0,
            sl=signal.sl if signal.sl else 0.0,
            confidence=signal.confidence if signal.confidence is not None else 0.0,
            rationale=signal.rationale if signal.rationale else "",
            source=signal.source,
            mode=mode,
            raw_response=str(signal.extra) if signal.extra else None,
            strategy_id=signal.strategy_id,
            idempotency_key=idem_key,
            user_id=signal.user_id,
        )

        # Campo opcional (si existe en schema)
        if hasattr(signal, "is_saved") and hasattr(db_signal, "is_saved"):
            db_signal.is_saved = getattr(signal, "is_saved")

        if db_session:
            db = db_session
            should_close = False
        else:
            db = SessionLocal()
            should_close = True

        try:
            db.add(db_signal)
            db.commit()
            db.refresh(db_signal)
            print(f"[DB] ✅ INSERT: {signal.token} {signal.direction} @ {ts_normalized} ID={db_signal.id}")
            return db_signal.id, True

        except IntegrityError:
            # Duplicado por idempotency_key: devolvemos el ID existente
            db.rollback()
            try:
                existing = db.query(SignalDB).filter(SignalDB.idempotency_key == idem_key).first()
                if existing:
                    return existing.id, False
            except Exception:
                pass
            return None, False

        except Exception as db_err:
            print(f"[DB] ❌ Error Insert: {db_err}")
            db.rollback()
            return None, False

        finally:
            if should_close:
                db.close()

    except ImportError as imp_err:
        print(f"[DB] ⚠️  Import Error: {imp_err}")
        return None, False
    except Exception as e:
        print(f"[DB] ⚠️  Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return None, False

def _write_to_csv(signal: Signal, mode: str, token_lower: str) -> None:
    """
    Escritura CSV (Solo si DB tuvo éxito).
    """
    mode_dir = LOGS_DIR / mode
    mode_dir.mkdir(parents=True, exist_ok=True)

    if mode == "EVALUATED":
        filename = f"{token_lower}.evaluated.csv"
    else:
        filename = f"{token_lower}.csv"

    filepath = mode_dir / filename
    file_exists = filepath.exists()

    # Convertir Signal a dict para CSV
    # NOTE: Use original timestamp for display, or normalized?
    # User asked for canonical. But CSV is log. Let's use signal.timestamp (the input).
    ts_str = signal.timestamp.replace(microsecond=0).isoformat() + "Z"
    
    row_data = {
        "timestamp": ts_str,
        "token": signal.token.upper(),
        "timeframe": signal.timeframe,
        "direction": signal.direction,
        "entry": signal.entry,
        "tp": signal.tp if signal.tp else "",
        "sl": signal.sl if signal.sl else "",
        "confidence": signal.confidence if signal.confidence is not None else "",
        "rationale": signal.rationale if signal.rationale else "",
        "source": signal.source,
    }

    try:
        with open(filepath, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row_data)
        # print(f"[CSV] ✅ Saved: {filepath}")
    except Exception as e:
        print(f"[CSV] ❌ Error: {e}")


def _send_push_notification(signal: Signal):
    """Encapsulated Push & Telegram Logic."""
    try:
        from notify import send_push_notification, send_telegram

        title = f"New Signal: {signal.direction.upper()} {signal.token}"
        body = (
            f"Entry: {signal.entry} | TP: {signal.tp} | SL: {signal.sl}\n"
            f"Strategy: {signal.strategy_id or 'Unknown'}"
        )
        
        # 1. Telegram Alert (Priority)
        # We send to the default channel (Entitlement/User mapping is complex here, 
        # so we fallback to the Env Var configured chat_id for now).
        # Formatting message for Telegram (HTML)
        tg_msg = (
            f"<b>🚀 New Signal: {signal.token} {signal.direction.upper()}</b>\n\n"
            f"⚡ <b>Entry:</b> {signal.entry}\n"
            f"🎯 <b>TP:</b> {signal.tp}\n"
            f"🛑 <b>SL:</b> {signal.sl}\n"
            f"📊 <b>Confidence:</b> {signal.confidence}%\n"
            f"🧠 <b>Reason:</b> {signal.rationale}\n\n"
            f"<i>Strategy: {signal.strategy_id}</i>"
        )
        # If signal has specific user, we might want to target them, 
        # but simpler to broadcast to Main Channel for MVP if user_id is None.
        send_telegram(tg_msg)

        # 2. Web Push
        res = send_push_notification(
            title, body, data={"token": signal.token, "type": "signal"}
        )
        if res.get("success", 0) > 0:
            print(f"[PUSH] 🔔 Sent ({res['success']} devices).")
    except Exception as push_err:
        print(f"[NOTIFY] ❌ Error: {push_err}")


def signal_from_dict(data: Dict[str, Any], mode: str, strategy_id: str) -> Signal:
    """Helper legacy."""
    ts = data.get("timestamp")
    if isinstance(ts, str):
        try:
            timestamp = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            timestamp = datetime.utcnow()
    elif isinstance(ts, datetime):
        timestamp = ts
    else:
        timestamp = datetime.utcnow()

    return Signal(
        timestamp=timestamp,
        strategy_id=strategy_id,
        mode=mode.upper(),
        token=data.get("token", "UNKNOWN").upper(),
        timeframe=data.get("timeframe", "30m"),
        direction=data.get("direction", "neutral"),
        entry=float(data.get("entry", 0)),
        tp=float(data["tp"]) if data.get("tp") else None,
        sl=float(data["sl"]) if data.get("sl") else None,
        confidence=(
            float(data["confidence"]) if data.get("confidence") is not None else None
        ),
        rationale=data.get("rationale"),
        source=data.get("source", "UNKNOWN"),
        extra=data.get("extra"),
    )





