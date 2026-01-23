from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Path as FPath
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models_db import WatchAlert, User
from routers.auth_new import get_current_user


router = APIRouter()


def _ttl_for_timeframe(tf: str) -> timedelta:
    """TTL conservador para alertas (MVP)."""
    tf_u = (tf or "").upper().strip()
    if tf_u == "1H":
        return timedelta(hours=8)
    if tf_u == "4H":
        return timedelta(hours=36)
    if tf_u == "1D":
        return timedelta(days=5)
    return timedelta(hours=24)


def _serialize(a: WatchAlert) -> Dict[str, Any]:
    return {
        "id": a.id,
        "user_id": a.user_id,
        "token": a.token,
        "timeframe": a.timeframe,
        "strategy_id": a.strategy_id,
        "side": a.side,
        "trigger_price": a.trigger_price,
        "distance_atr": a.distance_atr,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "expires_at": a.expires_at.isoformat() if a.expires_at else None,
        "status": a.status,
        "fired_at": a.fired_at.isoformat() if a.fired_at else None,
        "last_check_at": a.last_check_at.isoformat() if a.last_check_at else None,
        "payload": a.payload,
    }


class CreateAlertRequest(BaseModel):
    token: str = Field(..., min_length=2, max_length=10)
    timeframe: str = Field(..., min_length=1, max_length=10)
    strategy_id: str = Field(..., min_length=2, max_length=64)
    side: str = Field(..., min_length=2, max_length=10)  # LONG/SHORT
    trigger_price: float
    distance_atr: float = 0.0
    reason: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


class CancelAlertResponse(BaseModel):
    ok: bool
    id: int
    status: str


@router.get("/")
def list_alerts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    include_expired: bool = False,
) -> Dict[str, Any]:
    q = db.query(WatchAlert).filter(WatchAlert.user_id == user.id)
    if not include_expired:
        q = q.filter(WatchAlert.status.in_(["PENDING", "TRIGGERED"]))
    q = q.order_by(WatchAlert.created_at.desc())
    items = q.limit(200).all()
    return {"items": [_serialize(a) for a in items]}


@router.post("/", status_code=201)
def create_alert(
    body: CreateAlertRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    token_u = body.token.upper().strip()
    tf_u = body.timeframe.upper().strip()
    side_u = body.side.upper().strip()

    if side_u not in ("LONG", "SHORT"):
        raise HTTPException(status_code=422, detail="side must be LONG or SHORT")

    ttl = _ttl_for_timeframe(tf_u)
    now = datetime.utcnow()

    payload = dict(body.payload or {})
    if body.reason:
        payload["reason"] = body.reason

    a = WatchAlert(
        user_id=user.id,
        token=token_u,
        timeframe=tf_u,
        strategy_id=body.strategy_id.strip(),
        side=side_u,
        trigger_price=float(body.trigger_price),
        distance_atr=float(body.distance_atr or 0.0),
        created_at=now,
        expires_at=now + ttl,
        status="PENDING",
        payload=None if not payload else __import__("json").dumps(payload),
    )

    db.add(a)
    db.commit()
    db.refresh(a)
    return {"item": _serialize(a)}


@router.post("/{alert_id}/cancel", response_model=CancelAlertResponse)
def cancel_alert(
    alert_id: int = FPath(..., ge=1),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CancelAlertResponse:
    a = db.query(WatchAlert).filter(WatchAlert.id == alert_id, WatchAlert.user_id == user.id).first()
    if not a:
        raise HTTPException(status_code=404, detail="alert not found")

    if a.status not in ("PENDING", "TRIGGERED"):
        return CancelAlertResponse(ok=True, id=a.id, status=a.status)

    a.status = "CANCELED"
    db.add(a)
    db.commit()
    return CancelAlertResponse(ok=True, id=a.id, status=a.status)


@router.delete("/{alert_id}")
def delete_alert(
    alert_id: int = FPath(..., ge=1),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    a = db.query(WatchAlert).filter(WatchAlert.id == alert_id, WatchAlert.user_id == user.id).first()
    if not a:
        raise HTTPException(status_code=404, detail="alert not found")

    db.delete(a)
    db.commit()
    return {"ok": True, "id": alert_id}
