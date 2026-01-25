# backend/strategies/TrendFollowingNative.py

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


class TrendFollowingNative:
    """Trend Following (Native) con EMA cross + ADX.

    Objetivo (producto): seÃ±ales de tendencia de "calidad", no micro-ruido.
    Confianza en buckets (decisiva).

    Compat:
    - Acepta `context` opcional con OHLCV pre-fetched para evitar fetch duplicado.
    """

    META = StrategyMeta(
        id="trend_following_native_v1",
        name="Trend Following Native",
        description="SeÃ±al de tendencia con cruce de EMAs + confirmaciÃ³n de fuerza (ADX).",
        supported_tokens=["BTC", "ETH", "SOL", "BNB", "XRP"],
        supported_timeframes=["1h", "4h"],
        mode="LITE",
    )

    def __init__(
        self,
        ema_fast: int = 20,
        ema_slow: int = 50,
        adx_period: int = 14,
        min_adx: float = 25.0,
        tp_atr: float = 2.2,
        sl_atr: float = 1.3,
        atr_period: int = 14,
    ):
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.adx_period = adx_period
        self.min_adx = min_adx
        self.tp_atr = tp_atr
        self.sl_atr = sl_atr
        self.atr_period = atr_period

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

    def _atr(self, df: pd.DataFrame) -> pd.Series:
        high = df["high"]
        low = df["low"]
        close = df["close"]
        prev_close = close.shift(1)
        tr = pd.concat(
            [(high - low), (high - prev_close).abs(), (low - prev_close).abs()],
            axis=1,
        ).max(axis=1)
        return tr.rolling(self.atr_period).mean()

    def _adx(self, df: pd.DataFrame) -> pd.Series:
        high = df["high"]
        low = df["low"]
        close = df["close"]

        up_move = high.diff()
        down_move = -low.diff()

        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)

        tr = pd.concat(
            [(high - low), (high - close.shift(1)).abs(), (low - close.shift(1)).abs()],
            axis=1,
        ).max(axis=1)

        atr = tr.rolling(self.adx_period).mean()
        plus_di = 100 * (plus_dm.rolling(self.adx_period).sum() / atr)
        minus_di = 100 * (minus_dm.rolling(self.adx_period).sum() / atr)

        dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di))
        adx = dx.rolling(self.adx_period).mean()
        return adx

    def _trend_strength_tag(self, adx: float) -> str:
        if adx >= 40:
            return "Very Strong"
        if adx >= 32:
            return "Strong"
        if adx >= 25:
            return "Moderate"
        return "Weak"

    def _confidence_bucket(self, adx: float) -> float:
        if adx >= 40:
            return 0.90
        if adx >= 34:
            return 0.86
        if adx >= 28:
            return 0.80
        return 0.74

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
                df = get_ohlcv(token_u, tf, limit=350)

            if df is None or len(df) < 120:
                continue

            df = df.copy().reset_index(drop=True)

            df["ema_fast"] = df["close"].ewm(span=self.ema_fast, adjust=False).mean()
            df["ema_slow"] = df["close"].ewm(span=self.ema_slow, adjust=False).mean()
            df["atr"] = self._atr(df)
            df["adx"] = self._adx(df)

            last = df.iloc[-1]
            prev = df.iloc[-2]

            if pd.isna(last["adx"]) or pd.isna(last["atr"]):
                continue

            adx = float(last["adx"])
            atr = float(last["atr"])
            close = float(last["close"])

            bullish_cross = (
                float(prev["ema_fast"]) <= float(prev["ema_slow"])
                and float(last["ema_fast"]) > float(last["ema_slow"])
            )
            bearish_cross = (
                float(prev["ema_fast"]) >= float(prev["ema_slow"])
                and float(last["ema_fast"]) < float(last["ema_slow"])
            )

            if adx < self.min_adx:
                continue

            strength_tag = self._trend_strength_tag(adx)
            conf = self._confidence_bucket(adx)

            if bullish_cross:
                entry = close
                tp = entry + (self.tp_atr * atr)
                sl = entry - (self.sl_atr * atr)

                rationale = (
                    "Confirmed Uptrend: EMA fast crossed above EMA slow with strong trend strength (ADX). "
                    f"Trend Strength: {strength_tag} (ADX {adx:.1f}). "
                    "Targets derived from ATR."
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
                            "setup": "EMA Cross + ADX",
                            "trend_strength": strength_tag,
                            "adx": round(adx, 2),
                        },
                    )
                )

            elif bearish_cross:
                entry = close
                tp = entry - (self.tp_atr * atr)
                sl = entry + (self.sl_atr * atr)

                rationale = (
                    "Confirmed Downtrend: EMA fast crossed below EMA slow with strong trend strength (ADX). "
                    f"Trend Strength: {strength_tag} (ADX {adx:.1f}). "
                    "Targets derived from ATR."
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
                            "setup": "EMA Cross + ADX",
                            "trend_strength": strength_tag,
                            "adx": round(adx, 2),
                        },
                    )
                )
    def analyze_watchlist(
        self,
        token: str,
        timeframe: str,
        context: Optional[Dict[str, Any]] = None,
        max_items: int = 2,
        near_cross: float = 0.0025,
        min_adx: float = 18.0,
    ) -> List[Dict[str, Any]]:
        """
        Near-setups: proximidad de EMAs + ADX mÃ­nimo para sugerir "posible cross".
        near_cross: distancia relativa (|ema_fast-ema_slow|/price).
        """
        token_u = token.upper().strip()
        tf = str(timeframe).lower().strip()

        df = self._df_from_context(token_u, context)
        if df is None:
            df = get_ohlcv(token_u, tf, limit=350)
        if df is None or len(df) < 120:
            return []

        df = df.copy().reset_index(drop=True)
        df["ema_fast"] = df["close"].ewm(span=self.ema_fast, adjust=False).mean()
        df["ema_slow"] = df["close"].ewm(span=self.ema_slow, adjust=False).mean()
        df["adx"] = self._adx(df)

        last = df.iloc[-1]
        if pd.isna(last["adx"]) or pd.isna(last["ema_fast"]) or pd.isna(last["ema_slow"]):
            return []

        adx = float(last["adx"])
        close = float(last["close"])
        ef = float(last["ema_fast"])
        es = float(last["ema_slow"])
        if close <= 0:
            return []

        gap = abs(ef - es) / close

        if adx < min_adx:
            return []

        items: List[Dict[str, Any]] = []

        if gap <= near_cross:
            bias = "long" if ef > es else "short"
            # trigger price proxy: ema_slow (the level to cross)
            items.append({
                "strategy_id": self.META.id,
                "token": token_u,
                "timeframe": timeframe,
                "side": bias,
                "trigger_price": round(es, 2),
                "distance_atr": round(gap * 100, 2), # Show gap as %-ish or raw? Frontend expects 'ATR'. Let's use gap (rel) as 'distance_atr' proxy for now or 0.0
                "reason": (
                    f"EMAs converging. Gap ≈ {gap:.4f} of price. "
                    f"ADX {adx:.1f} suggests trend strength building."
                ),
            })

        return items[:max_items]
