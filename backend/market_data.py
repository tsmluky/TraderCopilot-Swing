from __future__ import annotations
from typing import Dict, Any


# Minimal stub. Replace with real provider later.
def snapshot(token: str) -> Dict[str, Any]:
    return {
        "token": token.upper(),
        "price": "N/D",
        "volume_24h": "N/D",
        "change_24h": "N/D",
        "market_cap": "N/D",
    }
