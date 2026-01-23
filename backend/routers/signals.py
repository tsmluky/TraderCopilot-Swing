from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Any
from database import get_db
from models_db import Signal, User
from routers.auth_new import get_current_user

router = APIRouter()

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
        
        return query.limit(limit).offset(offset).all()
        
    except Exception as e:
        print(f"[SIGNALS] Error fetching signals: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
