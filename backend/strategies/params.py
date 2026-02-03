# backend/strategies/params.py

"""
Strategy Parameter Registry (Optimization Layer)

This file defines the specific parameter overrides for each Token/Strategy combination.
This allows us to treat "Donchian on BTC" and "Donchian on SOL" as distinct, 
optimized strategies ("15 Strategies" concept).
"""

from typing import Dict, Any

# Default parameters if no specific override is found
DEFAULTS = {
    "donchian_v2": {
        "donchian_period": 20,
        "ema_period": 200,
        "atr_period": 14,
        "tp_atr": 2.0,
        "sl_atr": 1.2,
        "min_break_atr": 0.02,
    },
    "trend_following_native_v1": {
        "ema_fast": 20,
        "ema_slow": 50,
        "adx_period": 14,
    },
    "mean_reversion_v1": {
        "bb_period": 20,
        "bb_std": 2.0,
        "rsi_period": 14,
    }
}

# Specific Overrides per Token
# Structure: Key = "{strategy_id}_{token}" (upper case token)
OVERRIDES = {
    # --- Donchian V2 Optimizations ---
    # BTC & ETH: Conservative, high liquidity
    "donchian_v2_BTC": {"tp_atr": 2.5, "sl_atr": 1.0, "donchian_period": 20},
    "donchian_v2_ETH": {"tp_atr": 2.5, "sl_atr": 1.2, "donchian_period": 20},
    
    # SOL & BNB: Volatile alts, wider bands
    "donchian_v2_SOL": {"donchian_period": 30, "tp_atr": 3.0, "sl_atr": 1.5},
    "donchian_v2_BNB": {"donchian_period": 24, "tp_atr": 2.8, "sl_atr": 1.4},
    
    # XRP: Very choppy, strict entry
    "donchian_v2_XRP": {"min_break_atr": 0.05, "tp_atr": 2.0, "sl_atr": 1.0},

    # --- Trend Following (FlowMaster) Optimizations ---
    # BTC/ETH: Standard Trend
    "trend_following_native_v1_BTC": {"ema_fast": 20, "ema_slow": 50},
    "trend_following_native_v1_ETH": {"ema_fast": 20, "ema_slow": 50},

    # SOL/BNB: Faster reaction needed
    "trend_following_native_v1_SOL": {"ema_fast": 15, "ema_slow": 45, "adx_period": 12},
    "trend_following_native_v1_BNB": {"ema_fast": 18, "ema_slow": 48},

    # XRP: Slow trends usually fakeouts, longer validation
    "trend_following_native_v1_XRP": {"ema_fast": 25, "ema_slow": 60, "adx_period": 18},

    # --- Mean Reversion Optimizations ---
    # BTC/ETH: Standard Reversion (2.0 SD)
    "mean_reversion_v1_BTC": {"bb_std": 2.0, "rsi_period": 14},
    "mean_reversion_v1_ETH": {"bb_std": 2.0, "rsi_period": 14},

    # SOL/BNB: High Beta, needs 2.5 SD to not get run over
    "mean_reversion_v1_SOL": {"bb_std": 2.5, "rsi_period": 14},
    "mean_reversion_v1_BNB": {"bb_std": 2.4, "rsi_period": 14},

    # XRP: Range bound often, tighter bands ok? No, spikes are common.
    "mean_reversion_v1_XRP": {"bb_std": 2.2, "rsi_period": 10}, # Faster RSI
}

def get_strategy_params(strategy_code: str, token: str) -> Dict[str, Any]:
    """
    Returns the merged parameters for a specific strategy + token combo.
    """
    s_code = strategy_code.lower()
    t_code = token.upper()
    
    # 1. Start with defaults
    params = DEFAULTS.get(s_code, {}).copy()
    
    # 2. Apply Overrides
    override_key = f"{s_code}_{t_code}"
    if override_key in OVERRIDES:
        overrides = OVERRIDES[override_key]
        params.update(overrides)
        
    return params
