from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
# from models_db import Signal
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

from database import get_db
# from models_db import Signal as SignalDB, User
from models_db import Signal, User
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
        query = query.filter(Signal.source != "verification")
            
        query = query.order_by(Signal.timestamp.desc())
        
        results = query.limit(limit).offset(offset).all()
        
        # Manual serialization to inject 'status' (computed)
        # Frontend expects: ACTIVE, CLOSED, CANCELLED, WATCH, CREATED
        response = []
        for s in results:
            item = s.__dict__.copy()
            if "_sa_instance_state" in item:
                del item["_sa_instance_state"]
            
            # Manual serialization & Mapping
            # Frontend expects: entryPrice, targetPrice, stopLoss (camelCase)
            # Backend has: entry, tp, sl (snake_caseish)
            item["entryPrice"] = item.get("entry")
            item["targetPrice"] = item.get("tp")
            item["stopLoss"] = item.get("sl")
            item["type"] = item.get("direction", "NEUTRAL").upper() # Ensure UPPERCASE for UI mapping
            
            # Compute Status
            if s.evaluation:
                item["status"] = "CLOSED"
            elif s.source and "watchlist" in str(s.source).lower():
                item["status"] = "WATCH"
            else:
                item["status"] = "ACTIVE"
                
            response.append(item)
            
        return response
        
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
@router.post("/{signal_id}/accept", response_model=Dict[str, Any])
def accept_signal(
    signal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept (save) a transient signal.
    """
    try:
        # 1. Find signal (potentially is_saved=0)
        signal = db.query(Signal).filter(Signal.id == signal_id).first()
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")

        # 2. Ownership check
        if signal.user_id and signal.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # 3. Flip to saved
        signal.is_saved = 1
        db.commit()
        
        return {"status": "accepted", "id": signal_id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[SIGNALS] Accept Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/{signal_id}", response_model=Dict[str, Any])
def delete_signal(
    signal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific signal.
    """
    try:
        signal = db.query(Signal).filter(Signal.id == signal_id).first()
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")
        
        # Ownership check: Only owner or admin can delete
        # For now, simplistic check: if it has a user_id, it must match.
        if signal.user_id and signal.user_id != current_user.id:
             raise HTTPException(status_code=403, detail="Not authorized to delete this signal")

        db.delete(signal)
        db.commit()
        return {"status": "deleted", "id": signal_id}
        
    except Exception as e:
        print(f"[SIGNALS] Delete Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{signal_id}", response_model=Dict[str, Any])
def get_signal_by_id(
    signal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific signal by ID.
    Used for Advisor Context.
    """
    try:
        s = db.query(Signal).filter(Signal.id == signal_id).first()
        if not s:
            raise HTTPException(status_code=404, detail="Signal not found")
        
        # Privacy check? Public signals are visible to all?
        # For now, if it's user private, verify owner.
        if s.user_id and s.user_id != current_user.id:
             # If it's not mine, maybe it's system (user_id is Null)?
             # But if user_id is set and != me, block.
             raise HTTPException(status_code=403, detail="Not authorized")

        item = s.__dict__.copy()
        if "_sa_instance_state" in item:
            del item["_sa_instance_state"]
        
        # Consistent Serialization
        item["entryPrice"] = item.get("entry")
        item["targetPrice"] = item.get("tp")
        item["stopLoss"] = item.get("sl")
        item["type"] = item.get("direction", "NEUTRAL").upper()
        
        # Compute Status
        if s.evaluation:
            item["status"] = "CLOSED"
        elif s.source and "watchlist" in str(s.source).lower():
            item["status"] = "WATCH"
        else:
            item["status"] = "ACTIVE"
            
        return item
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[SIGNALS] Get By ID Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
