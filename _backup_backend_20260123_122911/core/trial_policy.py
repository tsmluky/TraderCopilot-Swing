
# backend/core/trial_policy.py

from datetime import datetime, timedelta
from typing import Literal, Union, Any
from fastapi import HTTPException

# Tiers
TIER_TRIAL = "TRIAL"
TIER_TRIAL_EXPIRED = "TRIAL_EXPIRED"
TIER_TRADER = "TRADER" # SwingLite
TIER_PRO = "PRO"       # SwingPro
TIER_OWNER = "OWNER"

def is_trial_active(user: Any) -> bool:
    """
    Checks if a FREE plan user is within their 3-day trial window.
    Strict check: plan='FREE' AND now < plan_expires_at
    """
    if not user:
        return False
        
    if user.plan != "FREE":
        # Non-free plans are not in 'trial' state logic, or effectively handled by their own entitlements.
        return False

    if user.plan_expires_at:
        return datetime.utcnow() < user.plan_expires_at

    # If FREE but no expiry set, fallback to created_at + 3 days
    if not user.created_at:
        return False
        
    # Fallback logic
    virtual_expiry = user.created_at + timedelta(days=3)
    return datetime.utcnow() < virtual_expiry

def get_access_tier(user: Any) -> Literal["TRIAL", "TRIAL_EXPIRED", "TRADER", "PRO", "OWNER"]:
    """
    Single Source of Truth for User Access Tier.
    Resolves plan + expiration into a concrete Tier.
    """
    if not user:
        return TIER_TRIAL_EXPIRED # Or NONE
    
    # OWNER privileges
    if user.role == "admin" or user.plan == "OWNER":
        return TIER_OWNER
    
    if user.plan == "PRO":
        return TIER_PRO
    
    if user.plan == "TRADER":
        return TIER_TRADER
    
    if user.plan == "FREE":
        if is_trial_active(user):
            return TIER_TRIAL
        else:
            return TIER_TRIAL_EXPIRED
            
    # Default fallback for unknown plans
    return TIER_TRIAL_EXPIRED

def assert_trial_active(user: Any, required_tier: str = None):
    """
    Dependency/Check to gate access for Expired Trial users.
    Raises 403 if user is FREE and Expired.
    Passes allowed for Active Trial, TRADER, PRO, OWNER.
    Optionally enforces minimum tier (e.g. required_tier="PRO").
    """
    tier = get_access_tier(user)
    if tier == TIER_TRIAL_EXPIRED:
         raise HTTPException(
             status_code=403, 
             detail={
                 "code": "TRIAL_EXPIRED", 
                 "message": "Your 3-day Free Trial has expired. Please upgrade to SwingLite or SwingPro to continue."
             }
         )

    if required_tier:
        # Hierarchy check
        # OWNER > PRO > TRADER ~= TRIAL
        
        if required_tier == TIER_PRO:
            if tier not in [TIER_PRO, TIER_OWNER]:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "code": "PRO_REQUIRED",
                        "message": "This feature requires a PRO subscription."
                    }
                )
        
        # If TRADER is required, TRIAL/TRADER/PRO/OWNER are all fine (since EXPIRED is already caught).
        pass
