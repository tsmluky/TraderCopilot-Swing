from datetime import datetime
import json
import ast
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
    source_filter: str = "ALL", # ALL, MANUAL, STRATEGY
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
            
        # Source Filter
        if source_filter == "MANUAL":
            query = query.filter(Signal.source == "manual_scanner")
        elif source_filter == "STRATEGY":
            query = query.filter(Signal.source != "manual_scanner")
            
        # Hard filter out "verification" signals from audit
        query = query.filter(Signal.source != "verification")
            
        # Filter out Disabled Strategies (User Preference)
        if current_user.disabled_strategies:
            import json
            try:
                disabled_list = json.loads(current_user.disabled_strategies)
                for code in disabled_list:
                    # Filter out any strategy_id that starts with the disabled code
                    # e.g. "DONCHIAN" hides "DONCHIAN_1H", "DONCHIAN_4H"
                    query = query.filter(Signal.strategy_id.notlike(f"{code}%"))
            except Exception as e:
                print(f"[SIGNALS] Error parsing disabled strategies: {e}")

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
            
            # Explicitly ensure strategy_id and source are present
            item["strategy_id"] = s.strategy_id
            item["source"] = s.source

            
            # Explicitly ensure strategy_id and source are present
            item["strategy_id"] = s.strategy_id
            item["source"] = s.source
            
            # Compute Status & Evaluation
            if s.evaluation:
                item["status"] = "CLOSED"
                item["evaluation"] = "evaluated"
                item["pnl"] = s.evaluation.pnl_r
            elif s.source and "watchlist" in str(s.source).lower():
                item["status"] = "WATCH"
                item["evaluation"] = "pending"
            else:
                item["status"] = "ACTIVE"
                item["evaluation"] = "pending"
                
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
        # Prepare Extra Data with Original Strategy ID
        extra_data = payload.extra or {}
        extra_data["original_strategy_id"] = payload.strategy_id
        
        # Convert to Schema
        sig_data = SignalSchema(
            timestamp=datetime.utcnow(),
            strategy_id="MARKET_SCANNER", # Standardized ID for Filter
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
            extra=extra_data,
            user_id=current_user.id,
            is_saved=1
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

        # 3. Flip to saved & Standardize ID
        signal.is_saved = 1
        
        # Standardize as Market Scanner Signal if not already
        if signal.strategy_id != "MARKET_SCANNER":
            # Hydrate current extra (Handle legacy raw_response)
            current_extra = {}
            if signal.extra:
                try:
                    current_extra = json.loads(signal.extra)
                except Exception:
                    pass
            elif signal.raw_response:
                try:
                    # Legacy fallback: raw_response stored str(dict)
                    current_extra = ast.literal_eval(signal.raw_response)
                except Exception:
                    pass

            current_extra["original_strategy_id"] = signal.strategy_id
            
            # Save back as JSON string
            signal.extra = json.dumps(current_extra)
            signal.strategy_id = "MARKET_SCANNER"
            signal.source = "manual_scanner"
            
            # Optional: Clear raw_response to avoid confusion? 
            # signal.raw_response = None 

        db.commit()
        
        return {"status": "accepted", "id": signal_id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[SIGNALS] Accept Error: {e}")
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
        
        # Compute Status & Evaluation
        if s.evaluation:
            item["status"] = "CLOSED"
            item["evaluation"] = "evaluated"
            item["pnl"] = s.evaluation.pnl_r
        elif s.source and "watchlist" in str(s.source).lower():
            item["status"] = "WATCH"
            item["evaluation"] = "pending"
        else:
            item["status"] = "ACTIVE"
            item["evaluation"] = "pending"
            
        return item
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[SIGNALS] Get By ID Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/{signal_id}", response_model=Dict[str, Any])
def delete_signal(
    signal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a signal and its associated data (evaluations).
    """
    try:
        # 1. Find signal
        signal = db.query(Signal).filter(Signal.id == signal_id).first()
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")

        # 2. Ownership / Permission Check
        # User can delete their own signals.
        # System signals (user_id is NULL) can represent shared strategies. 
        # Requirement: "borrarla completamente de la base de datos de ese usuario en particular"
        # Since 'System' signals are shared, deleting them deletes for EVERYONE.
        # IF the intention is to "Hide" it from this user, we should use 'is_hidden'.
        # BUT the user asked "borrarla completamente".
        # If the user is ADMIN, allow everything.
        # If the user is OWNER of the signal, allow.
        
        is_owner = signal.user_id == current_user.id
        is_admin = current_user.role == "admin"
        
        if not (is_owner or is_admin):
             # If it's a shared signal, checking if we should just "Hide" it?
             # For now, strictly follow "Delete" semantics but protect shared data.
             raise HTTPException(status_code=403, detail="Not authorized to delete this signal (System Signal).")

        # 3. Cascade Delete (Evaluation)
        from models_db import SignalEvaluation
        db.query(SignalEvaluation).filter(SignalEvaluation.signal_id == signal_id).delete()

        # 4. Delete Signal
        db.delete(signal)
        db.commit()

        return {"status": "deleted", "id": signal_id}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[SIGNALS] Delete Error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
