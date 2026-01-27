# backend/core/lite_swing_engine.py
"""
LITE-Swing Signal Engine (Setup Detector)

Objetivo:
- Reemplazar heurísticas "forzadas" por sondeo on-demand de estrategias Swing reales.
- Retornar LONG/SHORT solo si existe setup válido.
- Retornar NEUTRAL cuando:
  - No hay setup, o
  - Hay conflicto entre estrategias.

Notas de diseño (MVP):
- Whitelist estricta: DonchianBreakoutV2 + TrendFollowingNative (via registry.load_default_strategies()).
- Compatibilidad con StrategyConfig (DB) si existe; fallback a defaults si no hay configs.
- No ejecuta trades; solo produce señales para UI/logging.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from core.market_data_api import get_ohlcv_data

from sqlalchemy.orm import Session

from models_db import StrategyConfig, User
from strategies.registry import get_registry

from models import LiteSignal


ALLOWED_STRATEGY_IDS = {
    # canonical
    "donchian_v2",
    "trend_following_native_v1",
    "mean_reversion_rsi_v1",
    # backwards-compat alias
    "donchian",
}


def _safe_json_list(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    try:
        v = json.loads(raw)
        if isinstance(v, list):
            return [str(x).upper() for x in v if str(x).strip()]
        return []
    except Exception:
        return []


def _safe_json_dict(raw: Optional[str]) -> Dict[str, Any]:
    if not raw:
        return {}
    try:
        v = json.loads(raw)
        return v if isinstance(v, dict) else {}
    except Exception:
        return {}


def _to_ccxt_tf(tf: str) -> str:
    """Convierte timeframe UI/canónico (1H/4H/1D) a formato CCXT (1h/4h/1d)."""
    if not tf:
        return tf
    t = str(tf).strip()
    # CCXT expects lower-case like 4h, 1d; keep minutes as-is.
    if t.upper() in {"1H", "4H", "1D"}:
        return t.lower()
    return t.lower() if t.endswith("H") or t.endswith("D") else t


def _matches_scope(cfg: StrategyConfig, token: str, timeframe: str) -> bool:
    token_u = token.upper()
    tf = timeframe

    tokens = _safe_json_list(cfg.tokens)
    tfs = _safe_json_list(cfg.timeframes)

    token_ok = (not tokens) or ("*" in tokens) or (token_u in tokens)

    # tolerate stored "4H" vs "4h"
    tf_ok = (not tfs) or (tf.upper() in tfs) or (tf.lower() in [x.lower() for x in tfs])
    return bool(token_ok and tf_ok)


def _load_candidate_configs(db: Session, user: User) -> List[StrategyConfig]:
    # Prefer user-specific configs, but allow system defaults (user_id is NULL).
    q = (
        db.query(StrategyConfig)
        .filter(StrategyConfig.enabled == 1)
        .filter(StrategyConfig.strategy_id.in_(list(ALLOWED_STRATEGY_IDS)))
        .filter((StrategyConfig.user_id == user.id) | (StrategyConfig.user_id.is_(None)))
    )
    rows = q.all()
    return rows or []


def build_lite_swing_signal(
    db: Session,
    user: User,
    token: str,
    timeframe: str,
    market: Dict[str, Any],
) -> Tuple[LiteSignal, Dict[str, Any]]:
    """
    Construye una señal LITE (Swing) sondeando estrategias reales.

    Returns:
        (LiteSignal, indicators_dict)
    """
    token_u = token.upper()
    now = datetime.utcnow()

    # Market snapshot (for neutral & context)
    price = float(market.get("price") or 0.0)
    if price <= 0:
        # fallback defensivo: no bloqueamos el endpoint por esto
        price = 1.0

    registry = get_registry()

    # 1) Candidate StrategyConfigs (DB) or fallback
    candidates = []
    try:
        candidates = _load_candidate_configs(db, user)
    except Exception:
        candidates = []

    scoped = [c for c in candidates if _matches_scope(c, token_u, timeframe)]

    # --- DEDUPE (user config wins over system defaults) ---
    # If user has both system (user_id NULL) and user-specific configs enabled,
    # we must keep only one per strategy_id to avoid duplicated runs.
    scoped_map = {}
    for c in scoped:
        sid = (getattr(c, "strategy_id", None) or "").strip()
        if not sid:
            continue
        prev = scoped_map.get(sid)
        if not prev:
            scoped_map[sid] = c
            continue

        prev_uid = getattr(prev, "user_id", None)
        uid = getattr(c, "user_id", None)

        # prefer explicit user config over system default
        if prev_uid is None and uid == user.id:
            scoped_map[sid] = c

    # drop backward compat alias if canonical exists
    if "donchian_v2" in scoped_map and "donchian" in scoped_map:
        del scoped_map["donchian"]

    preferred = ["donchian_v2", "trend_following_native_v1", "mean_reversion_rsi_v1", "donchian"]
    ordered = []
    for sid in preferred:
        if sid in scoped_map:
            ordered.append(scoped_map[sid])
    for sid, c in scoped_map.items():
        if sid not in preferred:
            ordered.append(c)
    scoped = ordered
    # Fallback: if user has no scoped configs, try system configs scoped
    if not scoped and candidates:
        scoped = [c for c in candidates if c.user_id is None and _matches_scope(c, token_u, timeframe)]

    # De-dupe: si existen configs duplicadas (system + user), preferimos user-specific.
    deduped = {}
    for cfg in scoped:
        sid = (getattr(cfg, "strategy_id", None) or "").strip()
        if not sid:
            continue
        # Preferir la config del usuario sobre system (user_id None)
        existing = deduped.get(sid)
        if existing is None:
            deduped[sid] = cfg
            continue

        cur_uid = getattr(cfg, "user_id", None)
        ex_uid  = getattr(existing, "user_id", None)
        if cur_uid is not None and ex_uid is None:
            deduped[sid] = cfg

    scoped = list(deduped.values())
    # Final fallback: if still none, run both strategies with default configs
    if not scoped:
        scoped = [
            StrategyConfig(
                strategy_id="donchian_v2",
                tokens=json.dumps([token_u]),
                timeframes=json.dumps([timeframe]),
            ),
            StrategyConfig(
                strategy_id="trend_following_native_v1",
                tokens=json.dumps([token_u]),
                timeframes=json.dumps([timeframe]),
            ),
        ]

# Pre-fetch data to avoid redundant API calls (Timeout Optimization)
    try:
        raw_candles = get_ohlcv_data(token_u, timeframe, limit=350)
    except Exception as e:
        print(f"Error pre-fetching data: {e}")
        raw_candles = []

    context = {"data": {token_u: raw_candles}} if raw_candles else {}

    # 2) Execute strategies
    per_strategy: List[Dict[str, Any]] = []
    for cfg in scoped:
        sid = (cfg.strategy_id or "").strip()
        if sid not in ALLOWED_STRATEGY_IDS:
            continue

        config = _safe_json_dict(getattr(cfg, "config_json", None))

        strat = registry.get(sid, config=config)
        if not strat:
            per_strategy.append({"strategy_id": sid, "ok": False, "error": "strategy_not_registered"})
            continue

        try:
            # 2a. Capture Technical State (Transparency)
            strat_state = {}
            if hasattr(strat, "analyze_state"):
                try:
                    strat_state = strat.analyze_state(token_u, _to_ccxt_tf(timeframe))
                except Exception as e:
                    print(f"Error extracting state from {sid}: {e}")

            signals = strat.generate_signals([token_u], _to_ccxt_tf(timeframe), context=context)
            if not signals:
                per_strategy.append({
                    "strategy_id": sid,
                    "ok": True,
                    "has_setup": False,
                    "state": strat_state
                })
                continue

            sig = signals[0]
            direction = str(sig.direction).lower().strip()
            confidence = float(sig.confidence or 0.0)

            # Normalize
            if direction not in {"long", "short"}:
                per_strategy.append({
                    "strategy_id": sid,
                    "ok": True,
                    "has_setup": False,
                    "state": strat_state
                })
                continue

            per_strategy.append(
                {
                    "strategy_id": sid,
                    "ok": True,
                    "has_setup": True,
                    "direction": direction,
                    "confidence": confidence,
                    "entry": float(sig.entry),
                    "tp": float(sig.tp) if sig.tp else 0.0,
                    "sl": float(sig.sl) if sig.sl else 0.0,
                    "rationale": str(sig.rationale or "").strip(),
                    "state": strat_state
                }
            )
        except Exception as e:
            per_strategy.append({"strategy_id": sid, "ok": False, "error": str(e)})

    # 3) Consensus
    setups = [x for x in per_strategy if x.get("ok") and x.get("has_setup")]

    indicators: Dict[str, Any] = {
        "engine": "lite_swing_engine@v1",
        "token": token_u,
        "timeframe": timeframe,
        "timeframe_ccxt": _to_ccxt_tf(timeframe),
        "price": price,
        "strategies": per_strategy,
    }

    watchlist_data: Optional[List[Dict[str, Any]]] = None

    if not setups:
        indicators["decision"] = "neutral_check_watchlist"
        indicators["strategy_id"] = "lite_swing_watchlist"

        # --- WATCHLIST GENERATION (On-Demand Fallback) ---
        try:
            # 1. Reuse fetched data
            if raw_candles:
                # Ensure context is robust
                all_watch_items = []
                for cfg in scoped:
                    sid = (cfg.strategy_id or "").strip()
                    config = _safe_json_dict(getattr(cfg, "config_json", None))
                    strat = registry.get(sid, config=config)
                    
                    if strat and hasattr(strat, "analyze_watchlist"):
                        try:
                            # Looser params for On-Demand "Weak Signal" checking
                            # We want to show SOMETHING if the user asks.
                            w_items = strat.analyze_watchlist(
                                token_u, timeframe, context=context, 
                                near_atr=1.5,  # Relaxed from 1.2
                                near_cross=0.03 # Relaxed from 0.02
                            )
                            if w_items:
                                all_watch_items.extend(w_items)
                        except Exception as ex:
                            print(f"Error generating watchlist for {sid}: {ex}")
                
                # Sort by distance (ascending)
                all_watch_items.sort(key=lambda x: float(x.get("distance_atr", 999.0)))
                watchlist_data = all_watch_items[:5]

        except Exception as e:
            print(f"Error generating watchlist global: {e}")
            watchlist_data = []

        # --- LOGIC UPGRADE: Promote Watchlist to Weak Signal ---
        if watchlist_data:
            best_watch = watchlist_data[0]
            # Convert "Near Setup" to "Weak Signal"
            # Confidence: 30-50%
            base_conf = 0.32  # > 30% as requested
            
            # Simple TP/SL estimation for manual entry
            # SL = 1.5 ATR from price (rough heuristic if not provided)
            # TP = 2.0 ATR
            # We assume current price is entry
            
            direction = best_watch.get("side", "long")
            # Try to get ATR from context if strategies computed it? Hard to reach back.
            # We'll assume % based fallback if no ATR
            est_atr_pct = 0.02 # 2% default volatility assumption
            
            est_tp = price * (1 + (2 * est_atr_pct)) if direction == "long" else price * (1 - (2 * est_atr_pct))
            est_sl = price * (1 - (1.5 * est_atr_pct)) if direction == "long" else price * (1 + (1.5 * est_atr_pct))

            lite = LiteSignal(
                timestamp=now,
                token=token_u,
                timeframe=timeframe,
                direction=direction,
                entry=price,
                tp=round(est_tp, 4),
                sl=round(est_sl, 4),
                confidence=base_conf,
                rationale=f"[SCANNER] Near Setup detected. {best_watch.get('reason', '')}",
                source=f"lite:watchlist:{best_watch.get('strategy_id', 'unknown')}",
                indicators=indicators,
                watchlist=watchlist_data
            )
            return lite, indicators

        # If truly nothing found even with relaxed search:
        lite = LiteSignal(
            timestamp=now,
            token=token_u,
            timeframe=timeframe,
            direction="neutral",
            entry=price,
            tp=0.0,
            sl=0.0,
            confidence=0.0,
            rationale="Market is flat or choppy. No clear setup or near-setup detected.",
            source="lite-swing@v1",
            indicators=indicators,
            watchlist=watchlist_data
        )
        return lite, indicators

    if len(setups) == 1:
        s = setups[0]
        indicators["decision"] = "single_strategy"
        indicators["strategy_id"] = s["strategy_id"]
        lite = LiteSignal(
            timestamp=now,
            token=token_u,
            timeframe=timeframe,
            direction=s["direction"],
            entry=float(s["entry"]),
            tp=float(s["tp"]),
            sl=float(s["sl"]),
            confidence=max(0.0, min(1.0, float(s["confidence"]))),
            rationale=(s.get("rationale") or "Setup detectado por estrategia Swing.").strip(),
            source=f"lite-swing:{s['strategy_id']}",
            indicators=indicators,
        )
        return lite, indicators

    dirs = {x["direction"] for x in setups}
    if len(dirs) == 1:
        d = list(dirs)[0]
        best = max(setups, key=lambda x: float(x.get("confidence") or 0.0))
        base_conf = float(best.get("confidence") or 0.0)
        boosted = max(0.0, min(1.0, base_conf + 0.10))

        indicators["decision"] = "confluence"
        indicators["strategy_id"] = "lite_swing_confluence"
        indicators["confluence_direction"] = d
        indicators["base_confidence"] = base_conf
        indicators["boosted_confidence"] = boosted

        rationale_bits = []
        for x in setups:
            rid = x.get("strategy_id")
            rr = (x.get("rationale") or "").strip()
            if rr:
                rationale_bits.append(f"[{rid}] {rr}")
            else:
                rationale_bits.append(f"[{rid}] setup confirmado")

        lite = LiteSignal(
            timestamp=now,
            token=token_u,
            timeframe=timeframe,
            direction=d,
            entry=float(best["entry"]),
            tp=float(best["tp"]),
            sl=float(best["sl"]),
            confidence=boosted,
            rationale=("Confluencia detectada. " + " | ".join(rationale_bits))[:240],
            source="lite-swing:confluence",
            indicators=indicators,
        )
        return lite, indicators

    indicators["decision"] = "conflict"
    indicators["strategy_id"] = "lite_swing_conflict"
    indicators["conflict_directions"] = sorted(list(dirs))

    lite = LiteSignal(
        timestamp=now,
        token=token_u,
        timeframe=timeframe,
        direction="neutral",
        entry=price,
        tp=0.0,
        sl=0.0,
        confidence=0.05,
        rationale=(
            "Conflicto entre estrategias Swing (direcciones opuestas). Signal NEUTRAL para proteger credibilidad."
        ),
        source="lite-swing@v1",
        indicators=indicators,
    )
    return lite, indicators



