from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models_db import Signal, SignalEvaluation, User

# Import robusto: primero relativo (recomendado), fallback absoluto
try:
    from .auth_new import get_current_user
except Exception:
    from routers.auth_new import get_current_user  # type: ignore

router = APIRouter()

def _is_privileged(user: User) -> bool:
    role = (getattr(user, "role", "") or "").lower()
    plan = (getattr(user, "plan", "") or "").upper()
    return role in ("admin", "owner") or plan in ("OWNER",)

def _serialize_signal(sig: Signal, ev: Optional[SignalEvaluation]) -> Dict[str, Any]:
    return {
        "id": sig.id,
        "timestamp": sig.timestamp.isoformat() if sig.timestamp else None,
        "token": sig.token,
        "timeframe": sig.timeframe,
        "direction": sig.direction,
        "entry": sig.entry,
        "tp": sig.tp,
        "sl": sig.sl,
        "confidence": sig.confidence,
        "rationale": sig.rationale,
        "source": sig.source,
        "mode": sig.mode,
        "strategy_id": sig.strategy_id,
        "user_id": sig.user_id,
        "is_saved": sig.is_saved,
        "evaluation": None if not ev else {
            "id": ev.id,
            "evaluated_at": ev.evaluated_at.isoformat() if ev.evaluated_at else None,
            "result": ev.result,
            "pnl_r": ev.pnl_r,
            "exit_price": ev.exit_price,
        },
    }

def _base_query(db: Session, user: User):
    # Regla MVP:
    # - Usuario normal: ver señales del sistema (user_id NULL) + las suyas (user_id = me)
    # - Privileged: ver todo
    if _is_privileged(user):
        return db.query(Signal)
    return db.query(Signal).filter((Signal.user_id == None) | (Signal.user_id == user.id))  # noqa: E711

@router.get("/recent")
def get_recent_logs(
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = _base_query(db, user).order_by(Signal.timestamp.desc()).limit(limit)
    signals = q.all()

    # Map evaluaciones 1:1
    ids = [s.id for s in signals if s.id is not None]
    ev_map: Dict[int, SignalEvaluation] = {}
    if ids:
        evs = db.query(SignalEvaluation).filter(SignalEvaluation.signal_id.in_(ids)).all()
        ev_map = {e.signal_id: e for e in evs if e.signal_id is not None}

    return {"items": [_serialize_signal(s, ev_map.get(s.id)) for s in signals]}

@router.get("/{mode}/{token}")
def get_logs_by_mode_token(
    mode: str,
    token: str,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    mode_u = (mode or "").upper()
    token_u = (token or "").upper()

    q = (
        _base_query(db, user)
        .filter(Signal.mode == mode_u)
        .filter(Signal.token == token_u)
        .order_by(Signal.timestamp.desc())
        .limit(limit)
    )
    signals = q.all()

    ids = [s.id for s in signals if s.id is not None]
    ev_map: Dict[int, SignalEvaluation] = {}
    if ids:
        evs = db.query(SignalEvaluation).filter(SignalEvaluation.signal_id.in_(ids)).all()
        ev_map = {e.signal_id: e for e in evs if e.signal_id is not None}

    return {"items": [_serialize_signal(s, ev_map.get(s.id)) for s in signals]}

@router.post("/track")
def track_signal(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # payload esperado: {"signal_id": 123}
    signal_id = payload.get("signal_id")
    if not signal_id:
        raise HTTPException(status_code=400, detail="signal_id is required")

    sig = db.query(Signal).filter(Signal.id == int(signal_id)).first()
    if not sig:
        raise HTTPException(status_code=404, detail="Signal not found")

    # Permisos: si no sos privileged, solo podés trackear señales system o tuyas
    if not _is_privileged(user) and (sig.user_id not in (None, user.id)):
        raise HTTPException(status_code=403, detail="Forbidden")

    sig.is_saved = 1
    # Si era system, la “adoptás” (útil para UI de guardadas)
    if sig.user_id is None:
        sig.user_id = user.id

    db.add(sig)
    db.commit()
    return {"ok": True, "id": sig.id, "is_saved": sig.is_saved}

@router.post("/{signal_id}/toggle_save")
def toggle_save(
    signal_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sig = db.query(Signal).filter(Signal.id == int(signal_id)).first()
    if not sig:
        raise HTTPException(status_code=404, detail="Signal not found")

    if not _is_privileged(user) and (sig.user_id not in (None, user.id)):
        raise HTTPException(status_code=403, detail="Forbidden")

    new_val = 0 if (sig.is_saved or 0) == 1 else 1
    sig.is_saved = new_val

    if new_val == 1 and sig.user_id is None:
        sig.user_id = user.id
    if new_val == 0 and sig.user_id == user.id:
        # opcional: volver a system si lo des-guardás
        sig.user_id = None

    db.add(sig)
    db.commit()
    return {"ok": True, "id": sig.id, "is_saved": sig.is_saved}
