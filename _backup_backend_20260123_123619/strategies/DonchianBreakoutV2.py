# backend/strategies/DonchianBreakoutV2.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

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


class DonchianBreakoutV2:
    """Donchian Breakout con filtro de tendencia + ATR.

    Filosofía (producto):
    - Emitimos señales solo cuando hay ruptura limpia + contexto a favor.
    - Racional analista-grade: describe setup, filtro, y por qué el riesgo es aceptable.
    - Confianza: bucketed (decisiva). Evitamos 51%.
    """

    META = StrategyMeta(
        id="donchian_v2",
        name="Donchian Breakout V2",
        description="Breakout sobre canal Donchian con filtro EMA200 y targets basados en ATR.",
        supported_tokens=["BTC", "ETH", "SOL", "BNB", "XRP"],
        supported_timeframes=["1h", "4h"],
        mode="LITE",
    )

    def __init__(
        self,
        donchian_period: int = 20,
        ema_period: int = 200,
        atr_period: int = 14,
        tp_atr: float = 2.0,
        sl_atr: float = 1.2,
        min_break_atr: float = 0.05,
    ):
        self.donchian_period = donchian_period
        self.ema_period = ema_period
        self.atr_period = atr_period
        self.tp_atr = tp_atr
        self.sl_atr = sl_atr
        self.min_break_atr = min_break_atr

    def _compute_atr(self, df: pd.DataFrame) -> pd.Series:
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
        atr = tr.rolling(self.atr_period).mean()
        return atr

    def _confidence_bucket(self, break_strength_atr: float) -> float:
        if break_strength_atr >= 0.25:
            return 0.90
        if break_strength_atr >= 0.15:
            return 0.85
        if break_strength_atr >= 0.08:
            return 0.80
        return 0.74

    def generate_signals(self, tokens: List[str], timeframe: str) -> List[Signal]:
        signals: List[Signal] = []

        for token in tokens:
            df = get_ohlcv(token, timeframe)
            if df is None or len(df) < (self.donchian_period + self.ema_period + 5):
                continue

            df = df.copy().reset_index(drop=True)
            df["donchian_high"] = df["high"].rolling(self.donchian_period).max()
            df["donchian_low"] = df["low"].rolling(self.donchian_period).min()
            df["ema200"] = df["close"].ewm(span=self.ema_period, adjust=False).mean()
            df["atr"] = self._compute_atr(df)

            last = df.iloc[-1]
            prev = df.iloc[-2]

            if pd.isna(last["atr"]) or pd.isna(last["ema200"]) or pd.isna(last["donchian_high"]) or pd.isna(last["donchian_low"]):
                continue

            close = float(last["close"])
            atr = float(last["atr"])
            ema200 = float(last["ema200"])
            upper = float(last["donchian_high"])
            lower = float(last["donchian_low"])

            bull_break_strength = (close - upper) / atr if atr > 0 else 0.0
            bear_break_strength = (lower - close) / atr if atr > 0 else 0.0

            is_bull_breakout = (float(prev["close"]) <= float(prev["donchian_high"])) and (close > upper)
            bull_trend_ok = close > ema200

            if is_bull_breakout and bull_trend_ok and bull_break_strength >= self.min_break_atr:
                entry = close
                tp = entry + (self.tp_atr * atr)
                sl = entry - (self.sl_atr * atr)

                conf = self._confidence_bucket(bull_break_strength)

                rationale = (
                    "Strong Bullish Breakout: close above Donchian upper band. "
                    "Trend filter bullish (price above EMA200). "
                    f"Break strength ≈ {bull_break_strength:.2f} ATR; targets derived from ATR."
                )

                signals.append(
                    Signal(
                        timestamp=datetime.utcnow(),
                        token=token,
                        direction="long",
                        entry=round(entry, 6),
                        tp=round(tp, 6),
                        sl=round(sl, 6),
                        confidence=conf,
                        rationale=rationale,
                        extra={
                            "setup": "Donchian Breakout",
                            "trend": "Bullish (EMA200)",
                            "break_strength_atr": round(bull_break_strength, 3),
                            "volatility": "ATR-expanded",
                        },
                    )
                )

            is_bear_breakout = (float(prev["close"]) >= float(prev["donchian_low"])) and (close < lower)
            bear_trend_ok = close < ema200

            if is_bear_breakout and bear_trend_ok and bear_break_strength >= self.min_break_atr:
                entry = close
                tp = entry - (self.tp_atr * atr)
                sl = entry + (self.sl_atr * atr)

                conf = self._confidence_bucket(bear_break_strength)

                rationale = (
                    "Strong Bearish Breakout: close below Donchian lower band. "
                    "Trend filter bearish (price below EMA200). "
                    f"Break strength ≈ {bear_break_strength:.2f} ATR; targets derived from ATR."
                )

                signals.append(
                    Signal(
                        timestamp=datetime.utcnow(),
                        token=token,
                        direction="short",
                        entry=round(entry, 6),
                        tp=round(tp, 6),
                        sl=round(sl, 6),
                        confidence=conf,
                        rationale=rationale,
                        extra={
                            "setup": "Donchian Breakout",
                            "trend": "Bearish (EMA200)",
                            "break_strength_atr": round(bear_break_strength, 3),
                            "volatility": "ATR-expanded",
                        },
                    )
                )

        return signals
