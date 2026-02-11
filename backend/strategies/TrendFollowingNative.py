# backend/strategies/TrendFollowingNative.py

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


class TrendFollowingNative:
    """Trend Following (Optimized SMA/EMA Crossover).

    Replaces previous logic with optimized fast/slow Moving Average parameters.
    Based on 'SMA Optimization' (Dataset).
    """

    META = StrategyMeta(
        id="trend_following_native_v1",
        name="Trend Surfer (SMA)",
        description="Optimized Moving Average Crossover system catching major trends.",
        supported_tokens=["BTC", "ETH", "SOL", "BNB", "XRP"],
        supported_timeframes=["1h", "4h"],
        mode="PRO",
    )

    # Optimized Parameters (Fast, Slow)
    # Source: results_sma_optimization_summary.txt (Ranked by Calmar)
    PARAMS = {
        "SOL": (10, 300),   # Calmar 277
        "BNB": (20, 100),   # Calmar 229
        "ETH": (10, 300),   # Calmar 79.5
        "BTC": (20, 150),   # Calmar 14
        "XRP": (20, 100),   # Default
        "DEFAULT": (20, 100)
    }

    def metadata(self):
        return self.META.__dict__

    def __init__(self):
        pass

    def _get_params(self, token: str):
        return self.PARAMS.get(token, self.PARAMS["DEFAULT"])

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
            
    def _compute_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        high = df["high"]
        low = df["low"]
        close = df["close"]
        prev_close = close.shift(1)
        tr = pd.concat(
            [(high - low), (high - prev_close).abs(), (low - prev_close).abs()],
            axis=1,
        ).max(axis=1)
        return tr.rolling(period).mean()

    def generate_signals(
        self,
        tokens: List[str],
        timeframe: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Signal]:
        signals: List[Signal] = []
        tf = str(timeframe).lower().strip()

        for token in tokens:
            token_u = token.upper().strip()
            fast_p, slow_p = self._get_params(token_u)

            # Context
            df = self._df_from_context(token_u, context)
            if df is None:
                df = get_ohlcv(token_u, tf, limit=400)

            if df is None or len(df) < (slow_p + 10):
                continue

            df = df.copy().reset_index(drop=True)

            # Using SMA as per 'SMA' Optimization title. 
            # Note: TrendFollowingNative previously used EMA. 
            # If the optimization was strictly SMA, we use SMA.
            df["fast_ma"] = df["close"].rolling(fast_p).mean()
            df["slow_ma"] = df["close"].rolling(slow_p).mean()
            df["atr"] = self._compute_atr(df)

            last = df.iloc[-1]
            prev = df.iloc[-2]

            if pd.isna(last["fast_ma"]) or pd.isna(last["slow_ma"]):
                continue

            # Check Crossover
            # Bullish: Fast crosses Above Slow
            fast_curr = float(last["fast_ma"])
            slow_curr = float(last["slow_ma"])
            fast_prev = float(prev["fast_ma"])
            slow_prev = float(prev["slow_ma"])
            
            close = float(last["close"])
            atr = float(last["atr"]) if not pd.isna(last["atr"]) else close*0.01

            is_bullish_cross = (fast_prev <= slow_prev) and (fast_curr > slow_curr)
            is_bearish_cross = (fast_prev >= slow_prev) and (fast_curr < slow_curr)
            
            # Since these are long-term trends (e.g. 10/300), we act on crossover.
            
            if is_bullish_cross:
                rationale = (
                    f"Golden Cross Detected. Fast MA ({fast_p}) crossed above Slow MA ({slow_p}). "
                    f"New Uptrend confirmed."
                )
                signals.append(
                    Signal(
                        timestamp=datetime.utcnow(),
                        token=token_u,
                        direction="long",
                        entry=round(close, 6),
                        tp=0, # Trend follower doesn't predict TP
                        sl=round(close - 3*atr, 6), # Wide SL for trend
                        confidence=0.80, 
                        rationale=rationale,
                        source="LITE",
                        mode=self.META.mode,
                        strategy_id=self.META.id,
                        timeframe=timeframe,
                        extra={
                            "fast_ma": fast_p,
                            "slow_ma": slow_p,
                            "ma_gap": round(fast_curr - slow_curr, 4)
                        },
                    )
                )

            elif is_bearish_cross:
                rationale = (
                    f"Death Cross Detected. Fast MA ({fast_p}) crossed below Slow MA ({slow_p}). "
                    f"New Downtrend confirmed."
                )
                signals.append(
                    Signal(
                        timestamp=datetime.utcnow(),
                        token=token_u,
                        direction="short",
                        entry=round(close, 6),
                        tp=0,
                        sl=round(close + 3*atr, 6),
                        confidence=0.80,
                        rationale=rationale,
                        source="LITE",
                        mode=self.META.mode,
                        strategy_id=self.META.id,
                        timeframe=timeframe,
                        extra={
                            "fast_ma": fast_p,
                            "slow_ma": slow_p,
                            "ma_gap": round(slow_curr - fast_curr, 4)
                        },
                    )
                )

        return signals

    def analyze_watchlist(
        self,
        token: str,
        timeframe: str,
        context: Optional[Dict[str, Any]] = None,
        max_items: int = 2,
        near_gap_pct: float = 0.5, # 0.5% distance between MAs
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        token_u = token.upper().strip()
        tf = str(timeframe).lower().strip()
        fast_p, slow_p = self._get_params(token_u)

        df = self._df_from_context(token_u, context)
        if df is None:
            df = get_ohlcv(token_u, tf, limit=400)
        if df is None or len(df) < slow_p + 10:
            return []

        df = df.copy().reset_index(drop=True)
        df["fast_ma"] = df["close"].rolling(fast_p).mean()
        df["slow_ma"] = df["close"].rolling(slow_p).mean()

        last = df.iloc[-1]
        if pd.isna(last["fast_ma"]): return []

        fast = float(last["fast_ma"])
        slow = float(last["slow_ma"])
        close = float(last["close"])
        
        # Calculate Gap as % of price
        gap = abs(fast - slow)
        gap_pct = (gap / close) * 100
        
        items = []
        if gap_pct <= near_gap_pct:
            # Converging
            bias = "Bullish" if fast < slow else "Bearish" # If fast < slow, it's organizing for a bull cross? Or just noise? 
            # Actually if Gap is small, a cross is imminent.
            # If Fast < Slow, we expect Bull Cross (Up)
            # If Fast > Slow, we expect Bear Cross (Down)
            
            direction = "long" if fast < slow else "short"
            action = "Golden Cross" if direction == "long" else "Death Cross"
            
            items.append({
                "strategy_id": self.META.id,
                "token": token_u,
                "timeframe": timeframe,
                "side": direction,
                "trigger_price": round(slow, 2), # Price isn't the trigger, time is. But Slow MA is a good ref.
                "tp": 0,
                "sl": 0,
                "distance_pct": round(gap_pct, 3),
                "confidence": 0.6 + (0.3 * (1 - gap_pct/near_gap_pct)),
                "reason": f"MAs Converging ({fast_p}/{slow_p}). Gap: {gap_pct:.2f}%. Potential {action}."
            })

        return items

    def find_historical_signals(self, token: str, df: pd.DataFrame, timeframe: str = "1h") -> List[Signal]:
        signals = []
        token_u = token.upper()
        fast_p, slow_p = self._get_params(token_u)
        
        df = df.copy()
        df["fast_ma"] = df["close"].rolling(fast_p).mean()
        df["slow_ma"] = df["close"].rolling(slow_p).mean()
        
        for i in range(slow_p, len(df)):
            if pd.isna(df["fast_ma"].iloc[i]): continue
            
            fast = df["fast_ma"].iloc[i]
            slow = df["slow_ma"].iloc[i]
            prev_fast = df["fast_ma"].iloc[i-1]
            prev_slow = df["slow_ma"].iloc[i-1]
            
            ts = df.iloc[i].get("timestamp") or datetime.utcnow()
            close = df["close"].iloc[i]
            
            if prev_fast <= prev_slow and fast > slow:
                 signals.append(Signal(
                    timestamp=ts, strategy_id=self.META.id, mode="BACKTEST",
                    token=token_u, timeframe=timeframe, direction="long",
                    entry=close, tp=0, sl=0, confidence=1.0, source="BACKTEST",
                    rationale="Hist Golden Cross", extra={}
                 ))
            elif prev_fast >= prev_slow and fast < slow:
                  signals.append(Signal(
                    timestamp=ts, strategy_id=self.META.id, mode="BACKTEST",
                    token=token_u, timeframe=timeframe, direction="short",
                    entry=close, tp=0, sl=0, confidence=1.0, source="BACKTEST",
                    rationale="Hist Death Cross", extra={}
                 ))
        return signals
