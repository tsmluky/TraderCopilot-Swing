from typing import List, Dict, Any

# Define the "Personas" for the Strategy Marketplace
# This maps the "Marketing View" to the "Technical Implementation"

import json
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
USER_STRATEGIES_FILE = DATA_DIR / "user_strategies.json"

# ensures data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

SYSTEM_PERSONAS = [
    # --- STRATEGY 1: Donchian Breakout (Titan) ---
    # BTC
    {
        "id": "titan_btc",
        "name": "Titan Breakout",
        "symbol": "BTC",
        "timeframe": "1d",
        "strategy_id": "donchian_v2",
        "description": "The immovable object. Slow, steady accumulation of Bitcoin using Donchian channels.",
        "risk_level": "Low",
        "expected_roi": "20%",
        "win_rate": "52%",
        "frequency": "Very Low",
        "color": "slate",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "titan_btc_4h",
        "name": "Titan Breakout",
        "symbol": "BTC",
        "timeframe": "4h",
        "strategy_id": "donchian_v2",
        "description": "Faster paced accumulation for Bitcoin on the 4H timeframe.",
        "risk_level": "Medium",
        "expected_roi": "35%",
        "win_rate": "49%",
        "frequency": "Low",
        "color": "orange",
        "is_active": True,
        "is_custom": False,
    },
    # ETH
    {
        "id": "titan_eth_1d",
        "name": "Titan Breakout",
        "symbol": "ETH",
        "timeframe": "1d",
        "strategy_id": "donchian_v2",
        "description": "Daily trend following for Ethereum. Major moves only.",
        "risk_level": "Low",
        "expected_roi": "30%",
        "win_rate": "51%",
        "frequency": "Very Low",
        "color": "indigo",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "titan_eth",
        "name": "Titan Breakout",
        "symbol": "ETH",
        "timeframe": "4h",
        "strategy_id": "donchian_v2",
        "description": "Captures volatility breakouts in Ethereum. Optimized for 4h timeframe.",
        "risk_level": "Medium",
        "expected_roi": "45%",
        "win_rate": "48%",
        "frequency": "Medium",
        "color": "indigo",
        "is_active": True,
        "is_custom": False,
    },
    # SOL
    {
        "id": "titan_sol_1d",
        "name": "Titan Breakout",
        "symbol": "SOL",
        "timeframe": "1d",
        "strategy_id": "donchian_v2",
        "description": "Daily Swing Trading for Solana.",
        "risk_level": "Medium",
        "expected_roi": "150%",
        "win_rate": "48%",
        "frequency": "Low",
        "color": "amber",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "titan_sol",
        "name": "Titan Breakout",
        "symbol": "SOL",
        "timeframe": "4h",
        "strategy_id": "donchian_v2",
        "description": "Aggressive breakout hunter for Solana. High volatility, high reward.",
        "risk_level": "High",
        "expected_roi": "290%",
        "win_rate": "46%",
        "frequency": "Medium",
        "color": "amber",
        "is_active": True,
        "is_custom": False,
    },
    # BNB
    {
        "id": "titan_bnb_1d",
        "name": "Titan Breakout",
        "symbol": "BNB",
        "timeframe": "1d",
        "strategy_id": "donchian_v2",
        "description": "Daily trend following for BNB.",
        "risk_level": "Low",
        "expected_roi": "25%",
        "win_rate": "53%",
        "frequency": "Very Low",
        "color": "yellow",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "titan_bnb",
        "name": "Titan Breakout",
        "symbol": "BNB",
        "timeframe": "4h",
        "strategy_id": "donchian_v2",
        "description": "Steady breakout logic applied to BNB ecosystem price action.",
        "risk_level": "Medium",
        "expected_roi": "35%",
        "win_rate": "50%",
        "frequency": "Low",
        "color": "yellow",
        "is_active": True,
        "is_custom": False,
    },
    # XRP
    {
        "id": "titan_xrp_1d",
        "name": "Titan Breakout",
        "symbol": "XRP",
        "timeframe": "1d",
        "strategy_id": "donchian_v2",
        "description": "Long-term momentum capture for XRP.",
        "risk_level": "Medium",
        "expected_roi": "45%",
        "win_rate": "45%",
        "frequency": "Very Low",
        "color": "slate",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "titan_xrp",
        "name": "Titan Breakout",
        "symbol": "XRP",
        "timeframe": "4h",
        "strategy_id": "donchian_v2",
        "description": "Captures sudden momentum shifts in XRP using channel breakouts.",
        "risk_level": "High",
        "expected_roi": "60%",
        "win_rate": "42%",
        "frequency": "Low",
        "color": "slate",
        "is_active": True,
        "is_custom": False,
    },

    # --- STRATEGY 2: Trend Following (Flow) ---
    # BTC
    {
        "id": "flow_btc",
        "name": "Flow Master",
        "symbol": "BTC",
        "timeframe": "1d",
        "strategy_id": "trend_following_native_v1",
        "description": "Classic trend following for Bitcoin. Rides the major waves.",
        "risk_level": "Low",
        "expected_roi": "25%",
        "win_rate": "55%",
        "frequency": "Low",
        "color": "orange",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "flow_btc_4h",
        "name": "Flow Master",
        "symbol": "BTC",
        "timeframe": "4h",
        "strategy_id": "trend_following_native_v1",
        "description": "Intraday trend following for Bitcoin.",
        "risk_level": "Medium",
        "expected_roi": "35%",
        "win_rate": "52%",
        "frequency": "Medium",
        "color": "orange",
        "is_active": True,
        "is_custom": False,
    },
    # ETH
    {
        "id": "flow_eth_1d",
        "name": "Flow Master",
        "symbol": "ETH",
        "timeframe": "1d",
        "strategy_id": "trend_following_native_v1",
        "description": "Daily Trend Master for Ethereum.",
        "risk_level": "Medium",
        "expected_roi": "35%",
        "win_rate": "53%",
        "frequency": "Low",
        "color": "indigo",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "flow_eth",
        "name": "Flow Master",
        "symbol": "ETH",
        "timeframe": "4h",
        "strategy_id": "trend_following_native_v1",
        "description": "Trend following logic optimized for Ethereum's intraday moves.",
        "risk_level": "Medium",
        "expected_roi": "40%",
        "win_rate": "50%",
        "frequency": "Medium",
        "color": "indigo",
        "is_active": True,
        "is_custom": False,
    },
    # SOL
    {
        "id": "flow_sol_1d",
        "name": "Flow Master",
        "symbol": "SOL",
        "timeframe": "1d",
        "strategy_id": "trend_following_native_v1",
        "description": "Daily Trend Following for Solana.",
        "risk_level": "Medium",
        "expected_roi": "120%",
        "win_rate": "48%",
        "frequency": "Low",
        "color": "cyan",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "flow_sol",
        "name": "Flow Master",
        "symbol": "SOL",
        "timeframe": "4h",
        "strategy_id": "trend_following_native_v1",
        "description": "High-speed trend following for Solana momentum.",
        "risk_level": "High",
        "expected_roi": "150%",
        "win_rate": "45%",
        "frequency": "High",
        "color": "cyan",
        "is_active": True,
        "is_custom": False,
    },
    # BNB
    {
        "id": "flow_bnb_1d",
        "name": "Flow Master",
        "symbol": "BNB",
        "timeframe": "1d",
        "strategy_id": "trend_following_native_v1",
        "description": "Safe Daily Trends for BNB.",
        "risk_level": "Low",
        "expected_roi": "25%",
        "win_rate": "55%",
        "frequency": "Low",
        "color": "yellow",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "flow_bnb",
        "name": "Flow Master",
        "symbol": "BNB",
        "timeframe": "4h",
        "strategy_id": "trend_following_native_v1",
        "description": "Conservative trend following for BNB on 4H.",
        "risk_level": "Low",
        "expected_roi": "30%",
        "win_rate": "52%",
        "frequency": "Low",
        "color": "yellow",
        "is_active": True,
        "is_custom": False,
    },
    # XRP
    {
        "id": "flow_xrp_1d",
        "name": "Flow Master",
        "symbol": "XRP",
        "timeframe": "1d",
        "strategy_id": "trend_following_native_v1",
        "description": "Major moves only Trend Following for XRP.",
        "risk_level": "Medium",
        "expected_roi": "40%",
        "win_rate": "48%",
        "frequency": "Very Low",
        "color": "slate",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "flow_xrp",
        "name": "Flow Master",
        "symbol": "XRP",
        "timeframe": "4h",
        "strategy_id": "trend_following_native_v1",
        "description": "Reacts to XRP's explosive moves with trend logic.",
        "risk_level": "High",
        "expected_roi": "55%",
        "win_rate": "44%",
        "frequency": "Medium",
        "color": "slate",
        "is_active": True,
        "is_custom": False,
    },

    # --- STRATEGY 3: Scalping Pro (1H) ---
    # Titan 1H
    {
        "id": "titan_btc_1h",
        "name": "Titan Breakout",
        "symbol": "BTC",
        "timeframe": "1h",
        "strategy_id": "donchian_v2",
        "description": "Scalping Bitcoin volatility. Requires generic PRO/Trader plan.",
        "risk_level": "High",
        "expected_roi": "60%",
        "win_rate": "47%",
        "frequency": "High",
        "color": "orange",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "titan_eth_1h",
        "name": "Titan Breakout",
        "symbol": "ETH",
        "timeframe": "1h",
        "strategy_id": "donchian_v2",
        "description": "High frequency breakout scalping for ETH.",
        "risk_level": "High",
        "expected_roi": "70%",
        "win_rate": "46%",
        "frequency": "High",
        "color": "indigo",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "titan_sol_1h",
        "name": "Titan Breakout",
        "symbol": "SOL",
        "timeframe": "1h",
        "strategy_id": "donchian_v2",
        "description": "Momentum scalping for Solana.",
        "risk_level": "High",
        "expected_roi": "200%",
        "win_rate": "44%",
        "frequency": "Very High",
        "color": "amber",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "titan_bnb_1h",
        "name": "Titan Breakout",
        "symbol": "BNB",
        "timeframe": "1h",
        "strategy_id": "donchian_v2",
        "description": "Scalping BNB price action.",
        "risk_level": "Medium",
        "expected_roi": "45%",
        "win_rate": "49%",
        "frequency": "High",
        "color": "yellow",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "titan_xrp_1h",
        "name": "Titan Breakout",
        "symbol": "XRP",
        "timeframe": "1h",
        "strategy_id": "donchian_v2",
        "description": "XRP Scalping logic.",
        "risk_level": "High",
        "expected_roi": "80%",
        "win_rate": "41%",
        "frequency": "High",
        "color": "slate",
        "is_active": True,
        "is_custom": False,
    },

    # Flow 1H
    {
        "id": "flow_btc_1h",
        "name": "Flow Master",
        "symbol": "BTC",
        "timeframe": "1h",
        "strategy_id": "trend_following_native_v1",
        "description": "Short term trend following for BTC.",
        "risk_level": "Medium",
        "expected_roi": "45%",
        "win_rate": "50%",
        "frequency": "High",
        "color": "orange",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "flow_eth_1h",
        "name": "Flow Master",
        "symbol": "ETH",
        "timeframe": "1h",
        "strategy_id": "trend_following_native_v1",
        "description": "Intraday trends on Ethereum.",
        "risk_level": "Medium",
        "expected_roi": "55%",
        "win_rate": "49%",
        "frequency": "High",
        "color": "indigo",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "flow_sol_1h",
        "name": "Flow Master",
        "symbol": "SOL",
        "timeframe": "1h",
        "strategy_id": "trend_following_native_v1",
        "description": "Aggressive trend scalping on SOL.",
        "risk_level": "High",
        "expected_roi": "180%",
        "win_rate": "46%",
        "frequency": "Very High",
        "color": "cyan",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "flow_bnb_1h",
        "name": "Flow Master",
        "symbol": "BNB",
        "timeframe": "1h",
        "strategy_id": "trend_following_native_v1",
        "description": "Short term trend capture for BNB.",
        "risk_level": "Medium",
        "expected_roi": "40%",
        "win_rate": "51%",
        "frequency": "High",
        "color": "yellow",
        "is_active": True,
        "is_custom": False,
    },
    {
        "id": "flow_xrp_1h",
        "name": "Flow Master",
        "symbol": "XRP",
        "timeframe": "1h",
        "strategy_id": "trend_following_native_v1",
        "description": "Volatility trend scalping for XRP.",
        "risk_level": "High",
        "expected_roi": "75%",
        "win_rate": "43%",
        "frequency": "High",
        "color": "slate",
        "is_active": True,
        "is_custom": False,
    },
]


SYSTEM_OVERRIDES_FILE = DATA_DIR / "system_overrides.json"


def load_user_strategies():
    """Load strategies from JSON file."""
    if not USER_STRATEGIES_FILE.exists():
        return []
    try:
        with open(USER_STRATEGIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print(f"Error loading user strategies: {e}")
        return []


def save_user_strategies(strategies: List[Dict[str, Any]]):
    """Save user strategies to JSON file."""
    try:
        with open(USER_STRATEGIES_FILE, "w", encoding="utf-8") as f:
            json.dump(strategies, f, indent=4)
        print(f"[MARKETPLACE] Saved {len(strategies)} user strategies.")
    except Exception as e:
        print(f"Error saving user strategies: {e}")


def load_system_overrides():
    """Load system persona overrides (e.g. is_active state)."""
    if not SYSTEM_OVERRIDES_FILE.exists():
        return {}
    try:
        with open(SYSTEM_OVERRIDES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading system overrides: {e}")
        return {}


def save_system_overrides(overrides: Dict[str, Any]):
    """Save system persona overrides."""
    try:
        with open(SYSTEM_OVERRIDES_FILE, "w", encoding="utf-8") as f:
            json.dump(overrides, f, indent=4)
    except Exception as e:
        print(f"Error saving system overrides: {e}")


MARKETPLACE_PERSONAS = []


def refresh_personas():
    """Reloads MARKETPLACE_PERSONAS to include latest file changes and overrides"""
    global MARKETPLACE_PERSONAS

    # 1. Load Overrides
    overrides = load_system_overrides()

    # 2. Apply Overrides to System Personas
    current_system = []
    for p in SYSTEM_PERSONAS:
        p_copy = p.copy()
        if p["id"] in overrides:
            p_copy.update(overrides[p["id"]])
        current_system.append(p_copy)

    # 3. Load User Strategies
    user_strategies = load_user_strategies()

    MARKETPLACE_PERSONAS = current_system + user_strategies
    return MARKETPLACE_PERSONAS


def get_active_strategies():
    """Returns list of strategies to run in the scheduler"""
    refresh_personas()  # Ensure latest
    return [p for p in MARKETPLACE_PERSONAS if p.get("is_active", True)]
