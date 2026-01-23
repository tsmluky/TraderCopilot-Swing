# backend/core/trial_policy.py
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Literal, Optional

from fastapi import HTTPException

TIER_TRIAL = "TRIAL"
TIER_TRIAL_EXPIRED = "TRIAL_EXPIRED"
TIER_TRADER = "TRADER"
TIER_PRO = "PRO"
TIER_OWNER = "OWNER"

TRIAL_DAYS = 7


def _trial_expires_at(user: Any) -> datetime | None:
    exp = getattr(user, "plan_expires_at", None)
    if exp:
        return exp
    created = getattr(user, "created_at", None)
    if created:
        try:
            return created + timedelta(days=TRIAL_DAYS)
        except Exception:
            return None
    return None


def is_trial_active(user: Any) -> bool:
    if not user:
        return False
    plan = (getattr(user, "plan", None) or "").upper()
    if plan != "FREE":
        return False
    exp = _trial_expires_at(user)
    if not exp:
        return False
    return datetime.utcnow() < exp


def get_access_tier(user: Any) -> Literal["TRIAL", "TRIAL_EXPIRED", "TRADER", "PRO", "OWNER"]:
    if not user:
        return TIER_TRIAL_EXPIRED

    role = (getattr(user, "role", None) or "").lower()
    plan = (getattr(user, "plan", None) or "").upper()

    if role == "admin" or plan == "OWNER":
        return TIER_OWNER
    if plan == "PRO":
        return TIER_PRO
    if plan == "TRADER":
        return TIER_TRADER
    if plan == "FREE":
        return TIER_TRIAL if is_trial_active(user) else TIER_TRIAL_EXPIRED

    return TIER_TRIAL_EXPIRED


def assert_trial_active(user: Any, required_tier: Optional[str] = None):
    tier = get_access_tier(user)

    if tier == TIER_TRIAL_EXPIRED:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "TRIAL_EXPIRED",
                "message": "Your 7-day Free Trial has expired. Please upgrade to SwingLite or SwingPro to continue.",
            },
        )

    if not required_tier:
        return

    req = required_tier.upper().strip()

    if req == "TRADER":
        if tier in (TIER_TRIAL, TIER_TRADER, TIER_PRO, TIER_OWNER):
            return
    elif req == "PRO":
        if tier in (TIER_PRO, TIER_OWNER):
            return
    elif req == "OWNER":
        if tier == TIER_OWNER:
            return

    raise HTTPException(
        status_code=403,
        detail={
            "code": "UPGRADE_REQUIRED",
            "message": f"Access requires tier {req}. Your current tier is {tier}.",
        },
    )
