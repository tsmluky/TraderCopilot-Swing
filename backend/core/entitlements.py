from typing import List, Dict, TypedDict, Optional, Literal
from models_db import User
from datetime import datetime
from sqlalchemy.orm import Session # For quota

# Enums / Types
PlanType = Literal["TRIAL", "TRADER", "PRO"]
StrategyCode = Literal["TITAN_BREAKOUT", "FLOW_MASTER"]
TimeframeCode = Literal["1H", "4H", "1D"]
TokenCode = Literal["BTC", "ETH", "SOL", "BNB", "XRP"]

class StrategyOffering(TypedDict):
    id: str
    strategy_code: StrategyCode
    strategy_name: str
    timeframe: TimeframeCode
    tokens: List[TokenCode] # User's allowed tokens
    all_tokens: List[TokenCode] # All tokens supported by this strategy (for visualization)
    locked: bool
    locked_reason: Optional[Literal["UPGRADE_REQUIRED", "TRIAL_EXPIRED"]]
    plan_required: Optional[PlanType]
    badges: List[str]


class PlanEntitlements(TypedDict):
    tokens: List[TokenCode]
    timeframes: List[TimeframeCode]
    strategies: List[StrategyCode]

# --- Configuration ---

PLANS: Dict[PlanType, PlanEntitlements] = {
    "TRIAL": {
        "tokens": ["BTC", "ETH", "SOL"],
        "timeframes": ["4H", "1D"],
        "strategies": ["TITAN_BREAKOUT", "FLOW_MASTER"],
    },
    "TRADER": {
        "tokens": ["BTC", "ETH", "SOL"],
        "timeframes": ["4H", "1D"],
        "strategies": ["TITAN_BREAKOUT", "FLOW_MASTER"],
    },
    "PRO": {
        "tokens": ["BTC", "ETH", "SOL", "BNB", "XRP"],
        "timeframes": ["1H", "4H", "1D"],
        "strategies": ["TITAN_BREAKOUT", "FLOW_MASTER"],
    }
}

STRATEGY_NAMES = {
    "TITAN_BREAKOUT": "Titan Breakout",
    "FLOW_MASTER": "Flow Master"
}

# --- Core Logic ---

def get_plan_entitlements(plan: str) -> PlanEntitlements:
    """Returns the static entitlements for a given plan (normalized)."""
    norm_plan = (plan or "TRIAL").upper()
    if norm_plan in ["FREE", "LITE", "SWINGLITE"]:
        norm_plan = "TRADER"
    if norm_plan in ["SWINGPRO", "PREMIUM", "OWNER", "ADMIN"]:
        norm_plan = "PRO"
    if norm_plan not in PLANS:
        norm_plan = "TRIAL"
    return PLANS[norm_plan]

def get_user_entitlements(user: Optional[User]) -> Dict[str, List[StrategyOffering]]:
    """
    Returns the offerings for a specific user, calculating locks and trial expiration.
    Returns: { "offerings": [...], "locked_offerings": [...] }
    """
    offerings: List[StrategyOffering] = []
    locked_offerings: List[StrategyOffering] = []
    
    # 1. Determine Effective Plan
    if not user:
        effective_plan = "TRIAL"
        is_trial_expired = False
    else:
        effective_plan = (user.plan or "TRIAL").upper()
        if effective_plan in ["FREE", "LITE", "SWINGLITE"]:
            effective_plan = "TRADER"
        if effective_plan in ["SWINGPRO", "PREMIUM"]:
            effective_plan = "PRO"
        
        is_trial_expired = False
        if effective_plan == "TRIAL" or (user.plan or "").upper() == "FREE":
             if user.plan_expires_at and user.plan_expires_at < datetime.utcnow():
                 is_trial_expired = True

    # 2. Get Entitlements for User's Plan
    my_entitlements = get_plan_entitlements(effective_plan)
    pro_entitlements = get_plan_entitlements("PRO")
    
    # 4. Build Offerings
    all_strategies = ["TITAN_BREAKOUT", "FLOW_MASTER"]
    canonical_timeframes = ["1H", "4H", "1D"]

    for strat_code in all_strategies:
        for tf in canonical_timeframes:
            
            is_in_my_plan = (tf in my_entitlements["timeframes"] and strat_code in my_entitlements["strategies"])
            is_in_pro_plan = (tf in pro_entitlements["timeframes"] and strat_code in pro_entitlements["strategies"])
            
            offering_id = f"{strat_code}_{tf}"
            name = STRATEGY_NAMES.get(strat_code, strat_code)
            
            # Determine ALL possible tokens for this strategy if one had the best plan
            # Here we assume PRO entitlements define the "max" for the strategy
            max_tokens = pro_entitlements["tokens"]

            if is_in_my_plan and not is_trial_expired:
                # Active Offering
                # User gets intersection of their allowed tokens and max tokens
                # (which is just their allowed tokens usually)
                user_tokens = my_entitlements["tokens"]
                
                offerings.append({
                    "id": offering_id, "strategy_code": strat_code, "strategy_name": name,
                    "timeframe": tf, 
                    "tokens": user_tokens,
                    "all_tokens": max_tokens, # Send full list so UI can show diff
                    "locked": False, "locked_reason": None, "plan_required": None, "badges": [] 
                })
            elif is_in_my_plan and is_trial_expired:
                 locked_offerings.append({
                    "id": offering_id, "strategy_code": strat_code, "strategy_name": name,
                    "timeframe": tf, 
                    "tokens": [], # Expired means no tokens usable? Or just show what they had?
                    "all_tokens": max_tokens,
                    "locked": True, "locked_reason": "TRIAL_EXPIRED", "plan_required": "TRADER", "badges": ["EXPIRED"]
                })
            elif is_in_pro_plan and not is_in_my_plan:
                 locked_offerings.append({
                    "id": offering_id, "strategy_code": strat_code, "strategy_name": name,
                    "timeframe": tf, 
                    "tokens": [],
                    "all_tokens": max_tokens,
                    "locked": True, "locked_reason": "UPGRADE_REQUIRED", "plan_required": "PRO", "badges": ["PRO"]
                })

    return { "offerings": offerings, "locked_offerings": locked_offerings }


# === COMPATIBILITY LAYER (Legacy Exports) ===

class TokenCatalog:
    """Adapter for legacy code that expects TokenCatalog.get_allowed_tokens(tier)."""
    @staticmethod
    def get_allowed_tokens(tier: str) -> List[str]:
        plan = tier
        if tier == "TRIAL_EXPIRED":
            plan = "TRIAL"
        ent = get_plan_entitlements(plan)
        return ent["tokens"]

def can_access_telegram(user: User) -> bool:
    """Checks if user is entitled to Telegram alerts."""
    # Simplified logic: If plan is not Trial Expired, and they have it configured.
    # We can be broader: Everyone gets it if they are active plan.
    # Just check if plan is valid.
    # Using existing logic pattern:
    plan = (user.plan or "FREE").upper()
    # User feedback: Telegram is the differentiator between FREE vs TRADER.
    # Therefore, FREE/TRIAL should NOT have access. Paid plans (TRADER, PRO, OWNER) should.
    
    if plan in ["FREE", "TRIAL"]:
        return False
        
    if plan in ["LITE", "TRADER", "SWINGLITE", "PRO", "SWINGPRO", "PREMIUM", "OWNER", "ADMIN"]:
        return True
        
    return False

def can_use_advisor(user: User) -> bool:
    """
    Checks if user is entitled to Advisor.
    Policy: Only PRO (SWINGPRO) users.
    """
    plan = (user.plan or "FREE").upper()
    if plan in ["PRO", "SWINGPRO", "PREMIUM", "OWNER"]:
        return True
    return False

def check_and_increment_quota(db: Session, user: User, feature: str) -> int:
    """
    Stub for legacy quota check. 
    Ideally this logic should stay in core/limiter or similar but was here.
    For now, return arbitrary usage number or just pass.
    """
    # Simply return 1 to allow logic to proceed without crashing,
    # or implementing real DB check if tables exist.
    # Advisor uses this.
    try:
         from models_db import DailyUsage
         now_date = datetime.utcnow().strftime("%Y-%m-%d")
         usage = db.query(DailyUsage).filter(
             DailyUsage.user_id == user.id, 
             DailyUsage.feature == feature,
             DailyUsage.date == now_date
         ).first()
         
         if not usage:
             usage = DailyUsage(user_id=user.id, feature=feature, date=now_date, count=0)
             db.add(usage)
         
         usage.count += 1
         db.commit()
         return usage.count
         
    except ImportError:
        return 1
    except Exception:
        # DB error fallback
        return 1

def assert_token_allowed(user: User, token: str) -> str:
    """
    Raises HTTPException if token not allowed.
    Returns normalized token.
    """
    norm_token = token.upper().strip()
    ent = get_user_entitlements(user)
    
    # Check if any active offering covers this token
    # or just check base allowed tokens directly?
    # Using TokenCatalog behavior for consistency:
    
    # But wait, User entitlements might be locked.
    # The 'offerings' list contains what is ACTIVE.
    
    active_tokens = set()
    for off in ent["offerings"]:
        for t in off["tokens"]:
            active_tokens.add(t)
            
    if norm_token not in active_tokens:
        # Fallback: maybe it's allowed for the plan but 
        # this specific function is used for ADVISOR context.
        # Strict checking based on ACTIVE offerings prevents 
        # using Advisor on locked tokens.
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403, 
            detail=f"Token {norm_token} is not active in your current plan."
        )
        
    return norm_token
