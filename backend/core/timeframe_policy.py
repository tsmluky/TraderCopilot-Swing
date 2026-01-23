from __future__ import annotations

from typing import List, Union, Any
from fastapi import HTTPException

from core.trial_policy import (
    get_access_tier,
    TIER_TRIAL,
    TIER_TRIAL_EXPIRED,
    TIER_TRADER,   # SwingLite
    TIER_PRO,      # SwingPro
    TIER_OWNER,
)

# Swing defaults:
# - Lite/Trial: 4H, 1D (menos ruido, más "swing")
# - Pro/Owner: 1H, 4H, 1D (abre 1H como feature Pro)
_ALLOWED = {
    TIER_TRIAL: ["4H", "1D"],
    TIER_TRADER: ["4H", "1D"],
    TIER_PRO: ["1H", "4H", "1D"],
    TIER_OWNER: ["1H", "4H", "1D"],
    TIER_TRIAL_EXPIRED: [],
}

# Normalización tolerante (por si UI manda "1h", "4h", "1d", etc.)
_TF_ALIASES = {
    "1H": "1H",
    "H1": "1H",
    "60M": "1H",
    "60MIN": "1H",
    "1HR": "1H",
    "1HOUR": "1H",

    "4H": "4H",
    "H4": "4H",
    "240M": "4H",
    "240MIN": "4H",
    "4HR": "4H",
    "4HOUR": "4H",

    "1D": "1D",
    "D1": "1D",
    "DAY": "1D",
    "DAILY": "1D",
    "24H": "1D",
}

def normalize_timeframe(tf: str) -> str:
    if not tf:
        return ""
    t = str(tf).strip().upper()
    return _TF_ALIASES.get(t, t)

def allowed_timeframes_for(tier: str) -> List[str]:
    if not tier:
        return []
    return _ALLOWED.get(tier, [])

def _tier_from_user_or_tier(user_or_tier: Union[str, Any]) -> str:
    """
    Acepta:
      - tier string (e.g. "TRIAL", "TRADER", "PRO", "OWNER")
      - user object (SQLAlchemy User) -> get_access_tier(user)
    """
    if user_or_tier is None:
        return ""
    if isinstance(user_or_tier, str):
        return user_or_tier
    # duck-typing: si parece User, usamos get_access_tier
    return get_access_tier(user_or_tier)

def assert_timeframe_allowed(user_or_tier: Union[str, Any], raw_timeframe: str) -> str:
    """
    Valida timeframe por tier.
    Devuelve timeframe normalizado si OK.
    Lanza 403 si no permitido.
    """
    tier = _tier_from_user_or_tier(user_or_tier)
    tf = normalize_timeframe(raw_timeframe)

    allowed = allowed_timeframes_for(tier)

    if not tf or tf not in allowed:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "TIMEFRAME_NOT_ALLOWED",
                "message": f"Your plan ({tier}) does not allow timeframe {tf}.",
                "tier": tier,
                "timeframe_requested": tf,
                "allowed_timeframes": allowed,
                "upgrade_required": True,
            },
        )

    return tf
