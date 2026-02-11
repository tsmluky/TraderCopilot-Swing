from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
import json

from database import get_db
from models_db import User
from routers.auth_new import get_current_user

router = APIRouter()

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current user profile including disabled strategies.
    """
    try:
        disabled = json.loads(current_user.disabled_strategies) if current_user.disabled_strategies else []
    except Exception:
        disabled = []
        
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "plan": current_user.plan,
        "disabled_strategies": disabled
    }

@router.patch("/me/strategies")
def update_strategy_preferences(
    disabled_strategies: List[str] = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the list of disabled strategies for the current user.
    """
    # Simple validation could be added here to ensure IDs are valid
    
    try:
        current_user.disabled_strategies = json.dumps(disabled_strategies)
        db.commit()
        db.refresh(current_user)
        return {"status": "success", "disabled_strategies": disabled_strategies}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
