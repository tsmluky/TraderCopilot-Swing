"""
PRO Context Pack Builder
Aggregates all necessary data for an Institutional-Grade Analysis (PRO).

Components:
1. Fixed Horizon (2-6 Weeks).
2. Internal Technical Snapshots (Daily + 4H).
3. LITE-Swing Setup Status (Confluence/Conflict/Neutral).
4. RAG Brain Content (Thesis, Risk, Catalysts).
"""
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from models_db import User
from core.lite_swing_engine import build_lite_swing_signal
from indicators.market import get_market_data

# Reuse RAG logic for loading files
from rag_context import _load_snippet

logger = logging.getLogger(__name__)



def _get_brain_content(token: str) -> Dict[str, str]:
    """Loads specialized PRO RAG content."""
    t = token.upper()
    return {
        "thesis": _load_snippet(t, "thesis"),
        "risk": _load_snippet(t, "risk"),
        "catalysts": _load_snippet(t, "catalysts"),
        "playbook": _load_snippet(t, "playbook"),
        # We can also pull news if we want
        "news_digest": _load_snippet(t, "news")
    }

def build_pro_context_pack(
    db: Session,
    user: User,
    token: str
) -> Dict[str, Any]:
    """
    Builds the full context package for the LLM.
    """
    token_u = token.upper()
    
    # 1. Market Data (Base Snapshot) - using 1D implicitly for "broad" view
    df_daily, market_daily = get_market_data(token_u, "1d", limit=100)
    
    # 2. LITE-Swing "Setup Status"
    # We poll the engine on 4H (standard swing trigger) to see if there is an *active* setup.
    # This provides the "System Status".
    lite_signal, indicators = build_lite_swing_signal(
        db=db,
        user=user,
        token=token_u,
        timeframe="4H",
        market=market_daily or {}
    )
    
    setup_decision = indicators.get("decision", "neutral")
    setup_desc = f"{lite_signal.direction.upper()}"
    if setup_decision == "neutral_no_setup":
        setup_desc = "NEUTRAL (No Setup)"
    elif setup_decision == "conflict":
        setup_desc = "NEUTRAL (Conflict)"
    elif setup_decision == "confluence":
        setup_desc = f"STRONG {lite_signal.direction.upper()} (Confluence)"
    
    # 3. Brain Content
    brain = _get_brain_content(token_u)
    
    # 4. Construct Pack
    return {
        "token": token_u,
        "horizon": "2-6 Weeks",
        "market": {
            "price": market_daily.get("price"),
            "change_24h": market_daily.get("change_24h"),
            "volatility": market_daily.get("volatility"),
            "rsi_daily": market_daily.get("rsi"),
            "trend_daily": market_daily.get("trend") 
        },
        "setup_status": {
            "decision": setup_decision,
            "display": setup_desc,
            "rationale": lite_signal.rationale
        },
        "brain": brain,
        "technicals_snapshot": {
            "daily_trend": market_daily.get("trend", "Unknown"),
            "volatility_state": "High" if (market_daily.get("volatility") or 0) > 3.0 else "Normal"
        }
    }
