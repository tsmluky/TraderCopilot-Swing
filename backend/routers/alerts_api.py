from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import json

from database import get_db
from models_db import User, WatchAlert
from routers.auth_new import get_current_user

router = APIRouter()

class WatchAlertCreate(BaseModel):
    token: str
    timeframe: str
    strategy_id: str
    side: str  # direction
    trigger_price: float
    distance_atr: Optional[float] = None
    reason: Optional[str] = None
    
    # Extra fields for 'condition'
    extra: Optional[Dict[str, Any]] = None

@router.post("/watch")
async def create_watch_alert(
    alert: WatchAlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new WatchAlert for the user.
    """
    # Create condition JSON
    condition_data = {
        "trigger_price": alert.trigger_price,
        "strategy_id": alert.strategy_id,
        "reason": alert.reason,
        "distance_atr": alert.distance_atr,
        **(alert.extra or {})
    }
    
    db_alert = WatchAlert(
        user_id=current_user.id,
        token=alert.token.upper(),
        timeframe=alert.timeframe,
        direction=alert.side.lower(),
        condition=json.dumps(condition_data),
        enabled=1
    )
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    return {
        "status": "active",
        "id": db_alert.id,
        "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat() # Example logic
    }

@router.get("/")
async def get_my_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(WatchAlert).filter(
        WatchAlert.user_id == current_user.id,
        WatchAlert.enabled == 1
    ).all()

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(WatchAlert).filter(
        WatchAlert.id == alert_id,
        WatchAlert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    # Soft delete or hard delete? 'enabled=0' or delete.
    # Model has 'enabled', let's toggle off or delete.
    # Frontend expects delete usually.
    db.delete(alert)
    db.commit()
    return {"status": "deleted"}
