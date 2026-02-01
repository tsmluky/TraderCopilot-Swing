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
    
    # 2. Enrich with Stats
    # We query the DB for each offering to get real metrics.
    # We aggregate by matching the strategy_id pattern.
    
    for offering in offerings_data["offerings"]:
        stats = _calculate_stats(db, offering["strategy_code"], offering["timeframe"])
        offering["win_rate"] = stats["win_rate"]
        offering["total_signals"] = stats["total_signals"]
        offering["avg_return"] = stats["avg_return"]

    # Also for locked offerings (so users see what they are missing)
    for offering in offerings_data["locked_offerings"]:
        stats = _calculate_stats(db, offering["strategy_code"], offering["timeframe"])
        offering["win_rate"] = stats["win_rate"]
        offering["total_signals"] = stats["total_signals"]
        offering["avg_return"] = stats["avg_return"]

    return offerings_data


def _calculate_stats(db: Session, strategy_code: str, timeframe: str) -> Dict[str, Any]:
    """
    Aggregates stats for a given strategy code and timeframe.
    Matches strategy_id like "{strategy_code}_{timeframe}".
    e.g. TITAN_BREAKOUT_4H
    """
    try:
        # Construct the exact ID used by Scheduler
        target_id = f"{strategy_code}_{timeframe}"
        
        # 1. Total Signals
        # We also look for legacy IDs if needed, but for now stick to the new standard.
        # If the system is fresh, standard is fine.
        total = db.query(Signal).filter(
            Signal.strategy_id == target_id,
            Signal.is_saved == 1
        ).count()
        
        if total == 0:
            return {"win_rate": "N/A", "total_signals": 0, "avg_return": "0.0"}

        # 2. Win Rate (Evaluated Signals Only)
        from models_db import SignalEvaluation
        
        evals = (
            db.query(SignalEvaluation)
            .join(Signal)
            .filter(Signal.strategy_id == target_id)
            .all()
        )
        
        if not evals:
             return {"win_rate": "N/A", "total_signals": total, "avg_return": "0.0"}
             
        wins = sum(1 for e in evals if e.result == "WIN")
        count = len(evals)
        win_rate = (wins / count * 100) if count > 0 else 0
        
        # 3. Avg Return (PnL)
        pnl_sum = sum(e.pnl_r for e in evals)
        avg_return = (pnl_sum / count) if count > 0 else 0.0

        return {
            "win_rate": f"{round(win_rate, 1)}",
            "total_signals": total,
            "avg_return": f"{round(avg_return, 1)}"
        }
        
    except Exception as e:
        print(f"[STATS] Error calculating for {strategy_code}: {e}")
        return {"win_rate": "N/A", "total_signals": 0, "avg_return": "0.0"}


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
