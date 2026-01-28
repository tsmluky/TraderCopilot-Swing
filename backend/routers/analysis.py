from __future__ import annotations

from datetime import datetime
import traceback

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from routers.auth_new import get_current_user
from database import get_db
from models import LiteReq, ProReq
from models_db import User
from core.signal_logger import log_signal
from core.schemas import Signal
from core.trial_policy import assert_trial_active
from core.timeframe_policy import assert_timeframe_allowed, normalize_timeframe
from core.token_policy import assert_token_allowed, normalize_token



# Legacy LITE heuristics (kept for PRO context & backward compatibility)

# New LITE-Swing Engine (Setup Detector)
from core.lite_swing_engine import build_lite_swing_signal

# PRO Analysis

router = APIRouter()


def _analyze_lite_unsafe(req: LiteReq, current_user: User, db: Session, tf_norm: str):
    """
    Internal logic for LITE analysis, decoupled from the route handler for safer reuse.
    Now uses the centralized LITE-SWING ENGINE.
    """
    print(f"[ANALYSIS] STARTING LITE SCAN: {req.token} {tf_norm}")
    
    # 1. Lazy Fetch (Delegated to Engine)
    # Optimized: We pass market=None so the engine fetches once.
    
    # 2. Run LITE-Swing Engine (Unified Logic)
    try:
        print("[ANALYSIS] Building Lite Swing Signal...")
        # build_lite_swing_signal returns Tuple[LiteSignal, Dict]
        lite_signal, indicators = build_lite_swing_signal(
            db=db,
            user=current_user,
            token=req.token,
            timeframe=tf_norm,
            market=None
        )
        print(f"[ANALYSIS] Signal generated: {lite_signal.direction} {lite_signal.confidence}")
        
        # Log price from the engine's result
        price = indicators.get("market_snapshot", {}).get("price", "N/A")
        print(f"[ANALYSIS] Market data checked via Engine. Price: {price}")

        print(f"[ANALYSIS] Signal generated: {lite_signal.direction} {lite_signal.confidence}")
        
    except Exception as e:
        print(f"[ANALYSIS] Engine Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis Engine Error: {str(e)}")

    # 3. Augment with specifics if needed (rationale, extra)
    try:
        if req.message:
            lite_signal.rationale += f" (User Context: {req.message})"
        
        # 4. Log Signal (Persistence)
        # Convert LiteSignal (models.py) -> Signal (schemas.py)
        
        strat_id = indicators.get("strategy_id", "lite_swing_engine")
        
        # FIX: Ensure tp/sl are None if they are 0, because Signal schema enforces gt=0
        final_tp = lite_signal.tp if lite_signal.tp and lite_signal.tp > 0 else None
        final_sl = lite_signal.sl if lite_signal.sl and lite_signal.sl > 0 else None

        signal_to_log = Signal(
            timestamp=lite_signal.timestamp,
            strategy_id=strat_id,
            mode="LITE",
            token=lite_signal.token,
            timeframe=lite_signal.timeframe,
            direction=lite_signal.direction,
            entry=lite_signal.entry,
            tp=final_tp,
            sl=final_sl,
            confidence=lite_signal.confidence,
            rationale=lite_signal.rationale,
            source=lite_signal.source,
            extra=indicators, # Map indicators -> extra
            user_id=current_user.id,
            is_saved=0 # Transient! Must be accepted by user to become visible (1)
        )
        
        print("[ANALYSIS] Logging signal...")
        saved_id = log_signal(signal_to_log)
        print(f"[ANALYSIS] Signal logged with ID: {saved_id}")
        
        # 5. Return JSON
        # Return the LiteSignal dict which the frontend expects, plus the ID.
        resp = lite_signal.dict()
        resp["id"] = saved_id if saved_id else 0
        return resp
        
    except Exception as e:
        print(f"[ANALYSIS] Logging/Response Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Logging Error: {str(e)}")


@router.post("/lite")
def analyze_lite(
    req: LiteReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Trial gate + timeframe entitlements
    assert_trial_active(current_user, required_tier="TRADER")
    tf_norm = normalize_timeframe(req.timeframe)
    token_norm = normalize_token(req.token)
    
    assert_timeframe_allowed(current_user, tf_norm)
    assert_token_allowed(current_user, token_norm)

    return _analyze_lite_unsafe(req, current_user, db, tf_norm=tf_norm)


@router.post("/pro")
async def analyze_pro(
    req: ProReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Trial gate + timeframe entitlements
    assert_trial_active(current_user, required_tier="PRO")

    # [NEW] Enforce Daily Quota (Fair Use)
    from core.entitlements import check_and_increment_quota
    check_and_increment_quota(db, current_user, "ai_analysis")

    # PRO does not strictly require timeframe logic on backend, but we validate user access.
    # We ignore req.timeframe for the text generation (uses fixed horizon), 
    
    # 1. Build Context
    from core.pro_context_pack import build_pro_context_pack
    context = build_pro_context_pack(db, current_user, str(req.token))
    
    # 2. Compile Prompt
    from core.pro_prompt_compiler import compile_pro_prompt, validate_pro_output, fix_markdown_spacing
    prompt = compile_pro_prompt(context, req.user_message, language=req.language)
    
    # 3. Call AI Service
    from core.ai_service import get_ai_service
    ai = get_ai_service()
    
    try:
        # System instruction can be simplified or part of prompt. 
        # We included strict instructions in the prompt itself.
        analysis_text = ai.generate_analysis(prompt, system_instruction="You are a professional crypto quant analyst.")
        
        # 4. Validation & Repair (One retry)
        if not validate_pro_output(analysis_text):
            print("[PRO] Output validation failed. Retrying with format repair...")
            retry_prompt = (
                prompt
                + "\n\nCRITICAL: You missed some required headers in the previous attempt. "
                "ENSURE ALL HEADERS ARE PRESENT."
            )
            analysis_text = ai.generate_analysis(
                retry_prompt,
                system_instruction=(
                    "You are a professional crypto quant analyst. Strict formatting required."
                ),
            )

        # 4.5. Post-Process Formatting (Force Newlines)
        analysis_text = fix_markdown_spacing(analysis_text)
            
    except Exception as e:
        # Graceful error if AI fails
        raise HTTPException(status_code=500, detail=f"AI Generation Failed: {str(e)}")

    # 5. Log & Return
    # Construct "LiteSignal" compatible object just for the UI "cards" if needed, 
    # but PRO UI usually just displays the text. 
    # The existing frontend expects `raw` (the text) and maybe `indicators`.
    
    return {
        "analysis": analysis_text, # Legacy
        "raw": analysis_text,      # Standard
        "id": 0,                   # Placeholder for DB ID
        "indicators": {
            "setup_status": context["setup_status"],
            "market_snapshot": context["market"],
            "horizon": context["horizon"]
        },
        "meta": {
            "token": req.token,
            "horizon": context["horizon"],
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
    }

def normalize_token_tf(token: str | None, timeframe: str | None):
    # Canonical forms used by entitlements / internal routing
    t = (token or "").strip()
    tf = (timeframe or "").strip()
    t_up = t.upper()
    tf_up = tf.upper()
    return t_up, tf_up
