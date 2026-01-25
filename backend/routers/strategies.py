# backend/routers/strategies.py
"""
End-to-End Strategy Management via Entitlements.
Refactored (2026-01-25): No longer uses StrategyConfig for entitlements.
Uses core.entitlements + Plan logic.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from database import get_db
from models_db import User, Signal
from routers.auth_new import get_current_user
from core.entitlements import get_user_entitlements

router = APIRouter(tags=["strategies"])

# === Endpoints ===

@router.get("/marketplace", response_model=Dict[str, List[Any]])
async def get_marketplace(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Returns Strategy Offerings based on User's Plan.
    Returns:
       offerings: List of active strategies (Active)
       locked_offerings: List of visible but locked strategies (Upsell)
    """
    # 1. Calculate Entitlements / Offerings
    offerings_data = get_user_entitlements(current_user)
    
    # 2. Enrich with Stats (Win Rate, Signals, etc.) - Dynamic Calculation per Strategy Code?
    # For MVP, we might show Global Stats per Strategy Code, or per specific Offering ID.
    # Since existing signals have 'strategy_id' like 'titan_btc_4h', we can try to find stats.
    # BUT, the new system uses 'strategy_code' and entitlements.
    # Let's attach basic stats if available, or 0.
    
    # We'll just return the structure as computed by core/entitlements.
    # The frontend expects "win_rate" etc. logic? 
    # The previous code calculated it live. 
    # For performance, we can skip live calc for now or do a quick aggregation if needed.
    # Let's keep it lightweight.
    
    # Just return raw offering data for now. Frontend will render chips.
    # If stats are needed, we can query `SignalEvaluation` by strategy_id matching the ID conventions.
    
    return offerings_data


# === Deprecated Endpoints ===

@router.post("/marketplace/create", include_in_schema=False)
async def create_persona(payload: Dict[str, Any]):
    raise HTTPException(status_code=410, detail="Feature Deprecated: Strategies are now plan-based.")

@router.patch("/marketplace/{id}/toggle", include_in_schema=False)
async def toggle_strategy(id: str):
    # Mock success to avoid breaking legacy frontend if it calls this
    return {"status": "ok", "enabled": True, "msg": "Deprecated: Strategies are managed by Plan."}

@router.delete("/marketplace/{id}", include_in_schema=False)
async def delete_persona(id: str):
     raise HTTPException(status_code=410, detail="Feature Deprecated.")

@router.patch("/marketplace/{id}/update", include_in_schema=False)
async def update_strategy(id: str, payload: Dict[str, Any]):
    # Mock success
    return {"status": "ok", "msg": "Deprecated: Settings are fixed by Plan."}

@router.get("/marketplace/{id}/history")
async def get_persona_history(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns signal history for a specific offering ID (e.g. TITAN_BREAKOUT_4H).
    Query logic: Find signals with strategy_id = id OR (strategy_code + timeframe match).
    New system might not tag signals with 'TITAN_BREAKOUT_4H' yet. 
    Legacy signals were 'titan_btc_4h'. 
    We need to handle the ID transition or just query somewhat loosely?
    
    For now, assume Signals will be tagged with the Offering ID or we query by properties.
    """
    
    # Try exact match first
    signals = (
        db.query(Signal)
        .filter(Signal.strategy_id == id) # e.g. TITAN_BREAKOUT_4H
        .order_by(Signal.timestamp.desc())
        .limit(50)
        .all()
    )
    
    # Format
    history = []
    for sig in signals:
         history.append({
            "id": sig.id,
            "timestamp": sig.timestamp,
            "token": sig.token,
            "direction": sig.direction,
            "entry": sig.entry,
            "tp": sig.tp,
            "sl": sig.sl,
            "result": sig.evaluation.result if sig.evaluation else None,
            "pnl": sig.evaluation.pnl_r if sig.evaluation else None
         })
         
    return history
