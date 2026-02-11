# backend/strategies/DonchianBreakoutV2.py

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


class DonchianBreakoutV2:
    """Donchian Breakout Optimized (Split Windows).

    Optimized logic based on 2022-2025 dataset:
    - Uses separate windows for Entry (Breakout) and Exit (Trailing Stop).
    - Per-Token parameters injected dynamically.
    """

    META = StrategyMeta(
        id="donchian_v2",
        name="Donchian Breakout Optimized",
        description="Trend Following system with split Entry/Exit windows.",
        supported_tokens=["BTC", "ETH", "SOL", "BNB", "XRP"],
        supported_timeframes=["1h", "4h"],
        mode="PRO",
    )

    # Optimized Parameters from final_results_optimized.csv
    # Format: Token: (Entry_Window, Exit_Window)
    PARAMS = {
        "SOL": (110, 80),  # Max Return
        "BNB": (55, 55),
        "BTC": (80, 80),
        "ETH": (55, 35),
        "XRP": (20, 20),   # Default/Fallback
        "DEFAULT": (20, 20)
    }

    def metadata(self):
        return self.META.__dict__

    def __init__(self):
        # Parameters are now dynamic per token
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
            [
                (high - low),
                (high - prev_close).abs(),
                (low - prev_close).abs(),
            ],
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
            entry_w, exit_w = self._get_params(token_u)

            # Context or Fetch
            df = self._df_from_context(token_u, context)
            if df is None:
                df = get_ohlcv(token_u, tf, limit=350)

            min_req = max(entry_w, exit_w) + 10
            if df is None or len(df) < min_req:
                continue

            df = df.copy().reset_index(drop=True)
            
            # Donchian Channels
            # Shift 1 to avoid lookahead bias
            df["long_entry_band"] = df["high"].rolling(window=entry_w).max().shift(1)
            df["long_exit_band"] = df["low"].rolling(window=exit_w).min().shift(1)
            
            # For Short:
            df["short_entry_band"] = df["low"].rolling(window=entry_w).min().shift(1)
            df["short_exit_band"] = df["high"].rolling(window=exit_w).max().shift(1)

            df["atr"] = self._compute_atr(df)

            last = df.iloc[-1]
            prev = df.iloc[-2]

            if pd.isna(last["long_entry_band"]) or pd.isna(last["long_exit_band"]):
                continue

            close = float(last["close"])
            prev_close = float(prev["close"])
            atr = float(last["atr"]) if not pd.isna(last["atr"]) else (close * 0.05)

            # --- LONG LOGIC ---
            entry_band = float(last["long_entry_band"])
            prev_entry_band = float(prev["long_entry_band"])
            
            is_bull_breakout = (prev_close <= prev_entry_band) and (close > entry_band)
            
            if is_bull_breakout:
                entry = close
                tp = entry + (3.0 * atr)
                sl = entry - (1.5 * atr) 

                rationale = (
                    f"Donchian Bullish Breakout (Optimized). "
                    f"Price broke {entry_w}-period High ({entry_band}). "
                    f"Trailing Exit set at {exit_w}-period Low."
                )

                signals.append(
                    Signal(
                        timestamp=datetime.utcnow(),
                        token=token_u,
                        direction="long",
                        entry=round(entry, 6),
                        tp=round(tp, 6),
                        sl=round(sl, 6),
                        confidence=0.85, 
                        rationale=rationale,
                        source="LITE",
                        mode=self.META.mode,
                        strategy_id=self.META.id,
                        timeframe=timeframe,
                        extra={
                            "entry_window": entry_w,
                            "exit_window": exit_w,
                            "breakout_level": entry_band
                        },
                    )
                )

            # --- SHORT LOGIC ---
            short_band = float(last["short_entry_band"])
            prev_short_band = float(prev["short_entry_band"])
            
            is_bear_breakout = (prev_close >= prev_short_band) and (close < short_band)
            
            if is_bear_breakout:
                entry = close
                tp = entry - (3.0 * atr)
                sl = entry + (1.5 * atr)

                rationale = (
                    f"Donchian Bearish Breakout (Optimized). "
                    f"Price broke {entry_w}-period Low ({short_band}). "
                    f"Trailing Exit set at {exit_w}-period High."
                )

                signals.append(
                    Signal(
                        timestamp=datetime.utcnow(),
                        token=token_u,
                        direction="short",
                        entry=round(entry, 6),
                        tp=round(tp, 6),
                        sl=round(sl, 6),
                        confidence=0.85,
                        rationale=rationale,
                        source="LITE",
                        mode=self.META.mode,
                        strategy_id=self.META.id,
                        timeframe=timeframe,
                        extra={
                            "entry_window": entry_w,
                            "exit_window": exit_w,
                            "breakout_level": short_band
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
        near_percent: float = 1.5, # 1.5% distance
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        token_u = token.upper().strip()
        tf = str(timeframe).lower().strip()
        entry_w, exit_w = self._get_params(token_u)

        df = self._df_from_context(token_u, context)
        if df is None:
            df = get_ohlcv(token_u, tf, limit=350)
        if df is None or len(df) < max(entry_w, exit_w) + 10:
            return []

        df = df.copy().reset_index(drop=True)
        # We focus on ENTRY bands for watchlist
        df["long_entry_band"] = df["high"].rolling(window=entry_w).max().shift(1)
        df["short_entry_band"] = df["low"].rolling(window=entry_w).min().shift(1)
        df["atr"] = self._compute_atr(df)

        last = df.iloc[-1]
        if pd.isna(last["long_entry_band"]):
            return []

        close = float(last["close"])
        upper = float(last["long_entry_band"])
        lower = float(last["short_entry_band"])
        atr = float(last["atr"]) if not pd.isna(last["atr"]) else close*0.05

        items: List[Dict[str, Any]] = []

        # Near Upper?
        dist_upper_pct = (upper - close) / close * 100
        if 0 <= dist_upper_pct <= near_percent:
            items.append({
                "strategy_id": self.META.id,
                "token": token_u,
                "timeframe": timeframe,
                "side": "long",
                "trigger_price": round(upper, 2),
                "tp": round(upper + 3*atr, 2),
                "sl": round(upper - 1.5*atr, 2),
                "distance_pct": round(dist_upper_pct, 2),
                "confidence": 0.70 + (0.2 * (1 - dist_upper_pct/near_percent)),
                "reason": f"Near {entry_w}-High Breakout ({upper}). Dist: {dist_upper_pct:.2f}%"
            })

        # Near Lower?
        dist_lower_pct = (close - lower) / close * 100
        if 0 <= dist_lower_pct <= near_percent:
            items.append({
                "strategy_id": self.META.id,
                "token": token_u,
                "timeframe": timeframe,
                "side": "short",
                "trigger_price": round(lower, 2),
                "tp": round(lower - 3*atr, 2),
                "sl": round(lower + 1.5*atr, 2),
                "distance_pct": round(dist_lower_pct, 2),
                "confidence": 0.70 + (0.2 * (1 - dist_lower_pct/near_percent)),
                "reason": f"Near {entry_w}-Low Breakdown ({lower}). Dist: {dist_lower_pct:.2f}%"
            })

        return items

    def find_historical_signals(self, token: str, df: pd.DataFrame, timeframe: str = "1h") -> List[Signal]:
        # Simple backtest implementation for the frontend "historical" view
        signals = []
        token_u = token.upper()
        entry_w, exit_w = self._get_params(token_u)

        df = df.copy()
        df["long_entry_band"] = df["high"].rolling(window=entry_w).max().shift(1)
        df["short_entry_band"] = df["low"].rolling(window=entry_w).min().shift(1)
        
        for i in range(max(entry_w, 20), len(df)):
            if pd.isna(df["long_entry_band"].iloc[i]): continue
            
            close = df["close"].iloc[i]
            prev_close = df["close"].iloc[i-1]
            try:
                entry_band = df["long_entry_band"].iloc[i]
                prev_entry_band = df["long_entry_band"].iloc[i-1]
                
                short_band = df["short_entry_band"].iloc[i]
                prev_short_band = df["short_entry_band"].iloc[i-1]
                
                ts = df.iloc[i].get("timestamp") or datetime.utcnow()

                # Long
                if prev_close <= prev_entry_band and close > entry_band:
                     signals.append(Signal(
                        timestamp=ts, strategy_id=self.META.id, mode="BACKTEST",
                        token=token_u, timeframe=timeframe, direction="long",
                        entry=close, tp=0, sl=0, confidence=1.0, source="BACKTEST",
                        rationale="Hist Breakout", extra={}
                     ))
                
                # Short
                if prev_close >= prev_short_band and close < short_band:
                     signals.append(Signal(
                        timestamp=ts, strategy_id=self.META.id, mode="BACKTEST",
                        token=token_u, timeframe=timeframe, direction="short",
                        entry=close, tp=0, sl=0, confidence=1.0, source="BACKTEST",
                        rationale="Hist Breakdown", extra={}
                     ))
            except Exception:
                pass
        return signals
