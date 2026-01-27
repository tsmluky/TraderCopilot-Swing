from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models_db import Signal
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

from database import get_db
from models_db import Signal as SignalDB, User
from routers.auth_new import get_current_user
from core.signal_logger import log_signal
from core.schemas import Signal as SignalSchema

router = APIRouter()

class ManualSignalReq(BaseModel):
    token: str
    timeframe: str
    strategy_id: str
    direction: str
    entry: float
    tp: Optional[float] = None
    sl: Optional[float] = None
    confidence: float = 100.0
    rationale: Optional[str] = "Manual Entry from Scanner"
    extra: Optional[Dict[str, Any]] = None

@router.get("/", response_model=List[Any])
def get_signals(
    limit: int = 50,
    offset: int = 0,
    token: Optional[str] = None,
    strategy_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent signals. 
    Authenticated user can see:
    1. System signals (user_id is NULL)
    2. Their own signals (user_id = current_user.id)
    """
    try:
        query = db.query(Signal).filter(Signal.is_saved == 1)
        
        # Isolation Logic
        query = query.filter(
            or_(
                Signal.user_id == current_user.id,
                Signal.user_id.is_(None)
            )
        )
        
        # Trial/Entitlement check could be here (e.g. hide signals if expired)
        # But for now assume Auth is enough or frontend handles blurring.
        
        if token:
            query = query.filter(Signal.token == token.upper())
            
        if strategy_id:
            query = query.filter(Signal.strategy_id == strategy_id)
            
        # Hard filter out "verification" signals from audit
        query = query.filter(SignalDB.source != "verification")
            
        query = query.order_by(SignalDB.timestamp.desc())
        
        return query.limit(limit).offset(offset).all()
        
    except Exception as e:
        print(f"[SIGNALS] Error fetching signals: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/", response_model=Dict[str, Any])
def create_manual_signal(
    payload: ManualSignalReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually create/accept a signal (e.g. from Scanner Watchlist).
    """
    try:
        # Convert to Schema
        sig_data = SignalSchema(
            timestamp=datetime.utcnow(),
            strategy_id=payload.strategy_id,
            mode="MANUAL",
            token=payload.token.upper(),
            timeframe=payload.timeframe,
            direction=payload.direction,
            entry=payload.entry,
            tp=payload.tp,
            sl=payload.sl,
            confidence=payload.confidence,
            rationale=payload.rationale,
            source="manual_scanner",
            extra=payload.extra,
            user_id=current_user.id
        )
        
        saved_id = log_signal(sig_data)
        return {"status": "ok", "id": saved_id}
        
    except Exception as e:
        print(f"[SIGNALS] Create Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
