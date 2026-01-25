from __future__ import annotations

from typing import List

from fastapi import HTTPException

from core.entitlements import TokenCatalog
from core.trial_policy import get_access_tier


def normalize_token(token: str) -> str:
    return (token or "").strip().upper()


def normalize_timeframe(timeframe: str) -> str:
    tf = (timeframe or "").strip().upper()
    # Normalize common variants if needed
    tf = tf.replace(" ", "")
    return tf


def get_allowed_tokens(user) -> List[str]:
    tier = get_access_tier(user)
    return TokenCatalog.get_allowed_tokens(tier)


def get_allowed_timeframes(user) -> List[str]:
    tier = get_access_tier(user)
    return TokenCatalog.get_allowed_timeframes(tier)


def assert_token_allowed(user, token: str) -> str:
    tok = normalize_token(token)
    allowed = get_allowed_tokens(user)
    if tok not in allowed:
        raise HTTPException(
            status_code=403,
            detail={"code": "TOKEN_NOT_ALLOWED", "message": f"Token '{tok}' not allowed for your tier."},
        )
    return tok


def assert_timeframe_allowed(user, timeframe: str) -> str:
    tf = normalize_timeframe(timeframe)
    allowed = get_allowed_timeframes(user)
    if tf not in allowed:
        raise HTTPException(
            status_code=403,
            detail={"code": "TIMEFRAME_NOT_ALLOWED", "message": f"Timeframe '{tf}' not allowed for your tier."},
        )
    return tf
