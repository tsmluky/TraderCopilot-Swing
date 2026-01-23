# backend/core/trial_policy.py

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Literal

from fastapi import HTTPException

# Tiers
TIER_TRIAL = "TRIAL"
TIER_TRIAL_EXPIRED = "TRIAL_EXPIRED"
TIER_TRADER = "TRADER"  # SwingLite
TIER_PRO = "PRO"        # SwingPro
TIER_OWNER = "OWNER"

TRIAL_DAYS = 7


def _trial_expires_at(user: Any) -> datetime | None:
    """Derive trial expiration timestamp.

    Source of truth is `user.plan_expires_at` when present.
    Fallback is `user.created_at + TRIAL_DAYS` for legacy rows.
    """
    if not user:
        return None

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
    """Checks if a FREE plan user is within their 7-day trial window."""
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
    """Single Source of Truth for User Access Tier."""
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


def assert_trial_active(user: Any):
    """Gate access for expired trial users."""
    tier = get_access_tier(user)
    if tier == TIER_TRIAL_EXPIRED:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "TRIAL_EXPIRED",
                "message": "Your 7-day Free Trial has expired. Please upgrade to SwingLite or SwingPro to continue.",
            },
        )
