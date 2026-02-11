# backend/strategies/SuperTrend.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import numpy as np

from core.schemas import Signal
from market_data import get_ohlcv


@dataclass
class StrategyMeta:
    id: str
    name: str
    description: str
    supported_tokens: List[str]
    supported_timeframes: List[str]
    mode: str


class SuperTrendStrategy:
    """SuperTrend Strategy.

    Volatility-based trend following using ATR to trail price.
    Effective for high-volatility assets like SOL.
    """

    META = StrategyMeta(
        id="supertrend_v1",
        name="SuperTrend",
        description="Volatility-based trailing stop system (ATR Trailing).",
        supported_tokens=["BTC", "ETH", "SOL", "BNB", "XRP"],
        supported_timeframes=["1h", "4h"],
        mode="PRO",
    )

    # Standard Params (Baseline was successful) or Optimized?
    # results_supertrend_summary.txt used ATR=10, Mult=3.0 and achieved 545% on SOL, 901% on BNB.
    PARMS = {
        "DEFAULT": (10, 3.0)
    }

    def metadata(self):
        return self.META.__dict__

    def __init__(self):
        pass

    def _df_from_context(self, token: str, context: Optional[Dict[str, Any]]) -> Optional[pd.DataFrame]:
        try:
            if not context:
                return None
            data = context.get("data") or {}
            rows = data.get(token)
            if not rows:
                return None
            df = pd.DataFrame(rows)
            for col in ["open", "high", "low", "close", "volume"]:
                if col not in df.columns:
                    return None
            df = df.copy().reset_index(drop=True)
            df[["open", "high", "low", "close", "volume"]] = df[
                ["open", "high", "low", "close", "volume"]
            ].astype(float)
            return df
        except Exception:
            return None

    def _calculate_supertrend(self, df: pd.DataFrame, period=10, multiplier=3.0):
        # ATR
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift(1)))
        tr3 = pd.DataFrame(abs(low - close.shift(1)))
        frames = [tr1, tr2, tr3]
        tr = pd.concat(frames, axis=1, join='outer').max(axis=1)
        atr = tr.rolling(period).mean()
        
        # HL2
        hl2 = (high + low) / 2
        
        # Basic Bands
        basic_upper = hl2 + (multiplier * atr)
        basic_lower = hl2 - (multiplier * atr)
        
        # Final Bands
        # Numba optimization would be better here, but using loop for compatibility
        # We need to iterate
        
        close_vals = close.values
        bu_vals = basic_upper.values
        bl_vals = basic_lower.values
        fu_vals = np.zeros(len(df))
        fl_vals = np.zeros(len(df))
        trend_vals = np.zeros(len(df), dtype=int)
        
        for i in range(period, len(df)):
            # Upper
            if bu_vals[i] < fu_vals[i-1] or close_vals[i-1] > fu_vals[i-1]:
                fu_vals[i] = bu_vals[i]
            else:
                fu_vals[i] = fu_vals[i-1]
            
            # Lower
            if bl_vals[i] > fl_vals[i-1] or close_vals[i-1] < fl_vals[i-1]:
                fl_vals[i] = bl_vals[i]
            else:
                fl_vals[i] = fl_vals[i-1]
                
            # Trend
            prev_trend = trend_vals[i-1]
            if prev_trend == 1: # Uptrend
                if close_vals[i] < fl_vals[i]:
                    trend_vals[i] = -1
                else:
                    trend_vals[i] = 1
            elif prev_trend == -1: # Downtrend
                if close_vals[i] > fu_vals[i]:
                    trend_vals[i] = 1
                else:
                    trend_vals[i] = -1
            else:
                # Init
                if close_vals[i] > fu_vals[i]:
                    trend_vals[i] = 1
                else:
                    trend_vals[i] = -1
        
        return trend_vals, fl_vals, fu_vals, atr

    def generate_signals(
        self,
        tokens: List[str],
        timeframe: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Signal]:
        signals: List[Signal] = []
        tf = str(timeframe).lower().strip()
        period, mult = self.PARMS["DEFAULT"]

        for token in tokens:
            token_u = token.upper().strip()
            df = self._df_from_context(token_u, context)
            if df is None:
                df = get_ohlcv(token_u, tf, limit=300)
            
            if df is None or len(df) < period + 10:
                continue
                
            df = df.copy().reset_index(drop=True)
            
            trend, lower, upper, atr = self._calculate_supertrend(df, period, mult)
            
            last_idx = len(df) - 1
            prev_idx = len(df) - 2
            
            curr_trend = trend[last_idx]
            prev_trend = trend[prev_idx]
            
            close = float(df["close"].iloc[last_idx])
            curr_atr = float(atr.iloc[last_idx])
            
            # Flip Check
            if prev_trend == -1 and curr_trend == 1:
                # Buy Signal
                sl_level = lower[last_idx]
                rationale = "SuperTrend Flip to Bullish. Price closed above Trend Line."
                
                signals.append(Signal(
                    timestamp=datetime.utcnow(),
                    token=token_u,
                    direction="long",
                    entry=close,
                    tp=close + (5*curr_atr), # Open ended usually, but giving target
                    sl=sl_level, # Trailing stop IS the supertrend line
                    confidence=0.8,
                    rationale=rationale,
                    source="LITE",
                    mode=self.META.mode,
                    strategy_id=self.META.id,
                    timeframe=timeframe,
                    extra={"supertrend": sl_level}
                ))
                
            elif prev_trend == 1 and curr_trend == -1:
                # Sell Signal
                sl_level = upper[last_idx]
                rationale = "SuperTrend Flip to Bearish. Price closed below Trend Line."
                
                signals.append(Signal(
                    timestamp=datetime.utcnow(),
                    token=token_u,
                    direction="short",
                    entry=close,
                    tp=close - (5*curr_atr),
                    sl=sl_level,
                    confidence=0.8,
                    rationale=rationale,
                    source="LITE",
                    mode=self.META.mode,
                    strategy_id=self.META.id,
                    timeframe=timeframe,
                    extra={"supertrend": sl_level}
                ))
                
        return signals

    def analyze_watchlist(
        self,
        token: str,
        timeframe: str,
        context: Optional[Dict[str, Any]] = None,
        max_items: int = 2,
        near_pct: float = 1.0,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        # Check if price is near the SuperTrend line (Potential FLIP or Bounce)
        # Actually usually we want FLIPS.
        token_u = token.upper().strip()
        tf = str(timeframe).lower().strip()
        period, mult = self.PARMS["DEFAULT"]
        
        df = self._df_from_context(token_u, context)
        if df is None:
            df = get_ohlcv(token_u, tf, limit=300)
        if df is None or len(df) < period + 10:
            return []
        
        df = df.copy().reset_index(drop=True)
        trend, lower, upper, atr = self._calculate_supertrend(df, period, mult)
        
        last = len(df)-1
        curr_trend = trend[last]
        close = df["close"].iloc[last]
        
        line = lower[last] if curr_trend == 1 else upper[last]
        
        dist = abs(close - line) / close * 100
        
        items = []
        if dist <= near_pct:
            # Near Flip Level
            trend_str = "Bullish" if curr_trend == 1 else "Bearish"
            flip_action = "Breakdown" if curr_trend == 1 else "Breakout"
            
            items.append({
                "strategy_id": self.META.id,
                "token": token_u,
                "timeframe": timeframe,
                "side": "short" if curr_trend == 1 else "long", # Anticipate flip? Or bounce? SuperTrend usually flips.
                "trigger_price": round(line, 2),
                "tp": 0,
                "sl": 0,
                "distance_pct": round(dist, 2),
                "confidence": 0.6,
                "reason": f"Price near SuperTrend ({trend_str}). Dist: {dist:.2f}%. Risk of {flip_action}."
            })
            
        return items

    def find_historical_signals(self, token: str, df: pd.DataFrame, timeframe: str = "1h") -> List[Signal]:
        signals = []
        token_u = token.upper()
        
        period, mult = self.PARMS["DEFAULT"]
        df = df.copy().reset_index(drop=True)
        trend, _, _, _ = self._calculate_supertrend(df, period, mult)
        
        for i in range(period+1, len(df)):
            curr = trend[i]
            prev = trend[i-1]
            ts = df.iloc[i].get("timestamp") or datetime.utcnow()
            close = df["close"].iloc[i]
            
            if prev == -1 and curr == 1:
                signals.append(Signal(
                    timestamp=ts, strategy_id=self.META.id, mode="BACKTEST",
                    token=token_u, timeframe=timeframe, direction="long",
                    entry=close, tp=0, sl=0, confidence=1.0, source="BACKTEST",
                    rationale="Hist ST Flip Bull", extra={}
                ))
            elif prev == 1 and curr == -1:
                signals.append(Signal(
                    timestamp=ts, strategy_id=self.META.id, mode="BACKTEST",
                    token=token_u, timeframe=timeframe, direction="short",
                    entry=close, tp=0, sl=0, confidence=1.0, source="BACKTEST",
                    rationale="Hist ST Flip Bear", extra={}
                 ))
        return signals
