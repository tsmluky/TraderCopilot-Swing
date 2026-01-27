# backend/strategies/MeanReversionBollinger.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

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


class MeanReversionBollinger:
    """Mean Reversion Strategy using Bollinger Bands and RSI.

    Philosophy:
    - Markets range 70% of the time.
    - We fade extremes when Volatility expands (Outer BB 2.5) and Momentum exhausts (RSI).
    - Target: Reversion to the Mean (SMA 20).
    """

    META = StrategyMeta(
        id="mean_reversion_v1",
        name="Mean Reversion (BB+RSI)",
        description="Fades extremes. Buy Low BB + Oversold. Sell High BB + Overbought. Target: SMA20.",
        supported_tokens=["BTC", "ETH", "SOL", "BNB", "XRP"],
        supported_timeframes=["1h", "4h"],
        mode="LITE",
    )

    def metadata(self):
        return self.META.__dict__

    def __init__(
        self,
        bb_period: int = 20,
        bb_std: float = 2.5,
        rsi_period: int = 14,
        rsi_overbought: int = 70,
        rsi_oversold: int = 30,
        tp_method: str = "SMA",  # 'SMA' or 'ATR'
        tp_atr_mult: float = 1.5,
        sl_atr_mult: float = 1.5,
    ):
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.tp_method = tp_method
        self.tp_atr_mult = tp_atr_mult
        self.sl_atr_mult = sl_atr_mult

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

    def _rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        sma = df["close"].rolling(self.bb_period).mean()
        std = df["close"].rolling(self.bb_period).std()
        upper = sma + (std * self.bb_std)
        lower = sma - (std * self.bb_std)
        return sma, upper, lower

    def _confidence(self, rsi_val: float, band_dist_pct: float) -> float:
        # Higher confidence if RSI is deeper in extreme
        base = 0.75
        if rsi_val < 20 or rsi_val > 80:
            base += 0.10
        elif rsi_val < 25 or rsi_val > 75:
            base += 0.05
        
        # Boost if price is significantly outside bands (implied by this being called)
        return min(0.95, base)

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
            df = self._df_from_context(token_u, context)
            
            if df is None:
                # Fallback (should typically rely on context in prod)
                df = get_ohlcv(token_u, tf, limit=200)

            if df is None or len(df) < (self.bb_period + 50):
                continue

            df = df.copy().reset_index(drop=True)
            
            # Indicators
            df["sma"], df["upper"], df["lower"] = self._bollinger_bands(df)
            df["rsi"] = self._rsi(df, self.rsi_period)
            df["atr"] = self._compute_atr(df)

            last = df.iloc[-1]

            if pd.isna(last["sma"]) or pd.isna(last["rsi"]):
                continue

            close = float(last["close"])
            sma = float(last["sma"])
            upper = float(last["upper"])
            lower = float(last["lower"])
            rsi = float(last["rsi"])
            atr = float(last["atr"])

            # Logic
            # LONG: Price < Lower Band AND RSI < Oversold
            # We look for the moment it dips or closes below
            is_oversold = rsi < self.rsi_oversold
            below_band = close < lower
            
            # Additional Filter: Candle Color (Optional). 
            # For now, pure mean reversion: "It's cheap, buy it".
            
            if below_band and is_oversold:
                entry = close
                # TP: Mean (SMA)
                if self.tp_method == "SMA":
                    tp = sma
                else:
                    tp = entry + (self.tp_atr_mult * atr)
                
                # SL: Fixed ATR below
                sl = entry - (self.sl_atr_mult * atr)
                
                conf = self._confidence(rsi, 0.0)
                
                rationale = (
                    "Mean Reversion Setup: "
                    f"Price ({close}) < Lower BB ({lower:.2f}). "
                    f"RSI {rsi:.1f} (Oversold). "
                    "Targeting Reversion to Mean (SMA20)."
                )

                signals.append(
                    Signal(
                        timestamp=datetime.utcnow(),
                        token=token_u,
                        direction="long",
                        entry=round(entry, 6),
                        tp=round(tp, 6),
                        sl=round(sl, 6),
                        confidence=conf,
                        rationale=rationale,
                        extra={
                            "setup": "BB Reversion",
                            "rsi": round(rsi, 1),
                            "bb_dev": self.bb_std
                        },
                    )
                )

            # SHORT
            is_overbought = rsi > self.rsi_overbought
            above_band = close > upper

            if above_band and is_overbought:
                entry = close
                if self.tp_method == "SMA":
                    tp = sma
                else:
                    tp = entry - (self.tp_atr_mult * atr)
                
                sl = entry + (self.sl_atr_mult * atr)
                
                conf = self._confidence(rsi, 0.0)
                
                rationale = (
                    "Mean Reversion Setup: "
                    f"Price ({close}) > Upper BB ({upper:.2f}). "
                    f"RSI {rsi:.1f} (Overbought). "
                    "Targeting Reversion to Mean (SMA20)."
                )

                signals.append(
                    Signal(
                        timestamp=datetime.utcnow(),
                        token=token_u,
                        direction="short",
                        entry=round(entry, 6),
                        tp=round(tp, 6),
                        sl=round(sl, 6),
                        confidence=conf,
                        rationale=rationale,
                        extra={
                            "setup": "BB Reversion",
                            "rsi": round(rsi, 1),
                            "bb_dev": self.bb_std
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
        near_percent: float = 1.0,
    ) -> List[Dict[str, Any]]:
        """Identify if price is approaching bands."""
        token_u = token.upper().strip()
        tf = str(timeframe).lower().strip()

        df = self._df_from_context(token_u, context)
        if df is None:
             df = get_ohlcv(token_u, tf, limit=100)
        
        if df is None or len(df) < 50:
            return []

        df = df.copy().reset_index(drop=True)
        df["sma"], df["upper"], df["lower"] = self._bollinger_bands(df)
        df["rsi"] = self._rsi(df, self.rsi_period)
        
        last = df.iloc[-1]
        close = float(last["close"])
        upper = float(last["upper"])
        lower = float(last["lower"])
        rsi = float(last["rsi"])

        items = []
        
        # Near Lower Band?
        # Check % distance
        dist_lower = (close - lower) / close * 100
        if dist_lower < near_percent and dist_lower > 0:
             # Approaching support
             items.append({
                "strategy_id": self.META.id,
                "token": token_u,
                "timeframe": timeframe,
                "side": "long",
                "trigger_price": round(lower, 2),
                "distance_pct": round(dist_lower, 2),
                "reason": f"Approaching Lower BB. RSI is {rsi:.1f}."
            })
        
        # Near Upper Band?
        dist_upper = (upper - close) / close * 100
        if dist_upper < near_percent and dist_upper > 0:
             items.append({
                "strategy_id": self.META.id,
                "token": token_u,
                "timeframe": timeframe,
                "side": "short",
                "trigger_price": round(upper, 2),
                "distance_pct": round(dist_upper, 2),
                "reason": f"Approaching Upper BB. RSI is {rsi:.1f}."
            })
            
        return items

    def find_historical_signals(self, token: str, df: pd.DataFrame, timeframe: str = "1h") -> List[Signal]:
        # Implementation for backtesting
        signals = []
        token_u = token.upper()
        
        df = df.copy()
        df["sma"], df["upper"], df["lower"] = self._bollinger_bands(df)
        df["rsi"] = self._rsi(df, self.rsi_period)
        df["atr"] = self._compute_atr(df)
        
        # Ensure timestamp column availability
        if "timestamp" not in df.columns and "iso_time" in df.columns:
             df["timestamp"] = df["iso_time"]
        
        for i in range(50, len(df)):
            last = df.iloc[i]
            if pd.isna(last["upper"]):
                continue
            
            close = float(last["close"])
            lower = float(last["lower"])
            upper = float(last["upper"])
            rsi = float(last["rsi"])
            sma = float(last["sma"])
            atr = float(last["atr"])
            
            ts_raw = last.get("timestamp") or last.get("iso_time")
            if not ts_raw:
                 # Fallback to current time if absolutely missing (shouldn't happen)
                 ts = datetime.utcnow()
            elif isinstance(ts_raw, str):
                 try:
                    ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                 except ValueError:
                    # Try other formats if needed
                    ts = datetime.strptime(ts_raw, "%Y-%m-%d %H:%M:%S")
            else:
                 ts = ts_raw

            # Long
            if close < lower and rsi < self.rsi_oversold:
                 signals.append(Signal(
                        timestamp=ts, strategy_id=self.META.id, mode="BACKTEST", token=token_u, timeframe=timeframe,
                        direction="long", entry=close, tp=sma, sl=close-(1.5*atr), confidence=0.8, source="BACKTEST",
                        rationale="Hist BB Reversion", extra={}
                 ))
            
            # Short
            if close > upper and rsi > self.rsi_overbought:
                 signals.append(Signal(
                        timestamp=ts, strategy_id=self.META.id, mode="BACKTEST", token=token_u, timeframe=timeframe,
                        direction="short", entry=close, tp=sma, sl=close+(1.5*atr), confidence=0.8, source="BACKTEST",
                        rationale="Hist BB Reversion", extra={}
                 ))
        
        return signals
