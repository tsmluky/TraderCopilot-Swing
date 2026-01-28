# backend/strategies/DonchianBreakoutV2.py

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


class DonchianBreakoutV2:
    """Donchian Breakout con filtro de tendencia + ATR.

    FilosofÃ­a (producto):
    - Emitimos seÃ±ales solo cuando hay ruptura limpia + contexto a favor.
    - Racional analista-grade: describe setup, filtro, y por quÃ© el riesgo es aceptable.
    - Confianza: bucketed (decisiva). Evitamos 51%.

    Compat:
    - El engine LITE pasa `context` opcional con OHLCV pre-fetched para evitar fetch duplicado.
    """

    META = StrategyMeta(
        id="donchian_v2",
        name="Donchian Breakout V2",
        description="Breakout sobre canal Donchian con filtro EMA200 y targets basados en ATR.",
        supported_tokens=["BTC", "ETH", "SOL", "BNB", "XRP"],
        supported_timeframes=["1h", "4h"],
        mode="LITE",
    )

    def metadata(self):
        return self.META.__dict__

    def __init__(
        self,
        donchian_period: int = 20,
        ema_period: int = 200,
        atr_period: int = 14,
        tp_atr: float = 2.0,
        sl_atr: float = 1.2,
        min_break_atr: float = 0.02,
    ):
        self.donchian_period = donchian_period
        self.ema_period = ema_period
        self.atr_period = atr_period
        self.tp_atr = tp_atr
        self.sl_atr = sl_atr
        self.min_break_atr = min_break_atr

    def _df_from_context(self, token: str, context: Optional[Dict[str, Any]]) -> Optional[pd.DataFrame]:
        """
        context esperado:
          { "data": { "BTC": [ {open,high,low,close,volume,time,timestamp}, ... ] } }
        """
        try:
            if not context:
                return None
            data = context.get("data") or {}
            rows = data.get(token)
            if not rows:
                return None
            df = pd.DataFrame(rows)
            # columnas mÃ­nimas
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

    def _rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _confidence_bucket(self, break_strength_atr: float) -> float:
        if break_strength_atr >= 0.25:
            return 0.90
        if break_strength_atr >= 0.15:
            return 0.85
        if break_strength_atr >= 0.08:
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

            # 1) Preferir contexto (evita doble fetch y hace el sistema mÃ¡s estable)
            df = self._df_from_context(token_u, context)

            # 2) Fallback a provider estÃ¡ndar
            if df is None:
                df = get_ohlcv(token_u, tf, limit=350)

            if df is None or len(df) < (self.donchian_period + self.ema_period + 5):
                continue

            df = df.copy().reset_index(drop=True)
            df["donchian_high"] = df["high"].rolling(self.donchian_period).max()
            df["donchian_low"] = df["low"].rolling(self.donchian_period).min()
            df["ema200"] = df["close"].ewm(span=self.ema_period, adjust=False).mean()
            df["atr"] = self._compute_atr(df)
            df["rsi"] = self._rsi(df)

            last = df.iloc[-1]
            prev = df.iloc[-2]

            if (
                pd.isna(last["atr"])
                or pd.isna(last["ema200"])
                or pd.isna(last["donchian_high"])
                or pd.isna(last["rsi"])
            ):
                continue

            close = float(last["close"])
            atr = float(last["atr"])
            ema200 = float(last["ema200"])
            upper = float(last["donchian_high"])
            lower = float(last["donchian_low"])
            rsi = float(last["rsi"])

            bull_break_strength = (close - upper) / atr if atr > 0 else 0.0
            bear_break_strength = (lower - close) / atr if atr > 0 else 0.0

            is_bull_breakout = (float(prev["close"]) <= float(prev["donchian_high"])) and (close > upper)
            bull_trend_ok = close > ema200
            rsi_safe_long = rsi < 75 # Don't buy if already euphoric

            if is_bull_breakout and bull_trend_ok and rsi_safe_long and bull_break_strength >= self.min_break_atr:
                entry = close
                tp = entry + (self.tp_atr * atr)
                sl = entry - (self.sl_atr * atr)

                conf = self._confidence_bucket(bull_break_strength)

                rationale = (
                    f"We detected a Bullish Breakout. Price broke the Upper Donchian Channel. "
                    f"Trend is favorable (Above EMA200). "
                    f"RSI ({rsi:.1f}) confirms momentum is healthy (Not Overbought). "
                    f"Breakout Strength: {bull_break_strength:.2f} ATR."
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
                            "setup": "Donchian Breakout + RSI",
                            "trend": "Bullish",
                            "break_strength_atr": round(bull_break_strength, 3),
                            "rsi": round(rsi, 1)
                        },
                    )
                )

            is_bear_breakout = (float(prev["close"]) >= float(prev["donchian_low"])) and (close < lower)
            bear_trend_ok = close < ema200
            rsi_safe_short = rsi > 25 # Don't sell if already capitulated

            if is_bear_breakout and bear_trend_ok and rsi_safe_short and bear_break_strength >= self.min_break_atr:
                entry = close
                tp = entry - (self.tp_atr * atr)
                sl = entry + (self.sl_atr * atr)

                conf = self._confidence_bucket(bear_break_strength)

                rationale = (
                    f"We detected a Bearish Breakout. Price broke the Lower Donchian Channel. "
                    f"Trend is favorable (Below EMA200). "
                    f"RSI ({rsi:.1f}) confirms momentum is healthy (Not Oversold). "
                    f"Breakout Strength: {bear_break_strength:.2f} ATR."
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
                            "setup": "Donchian Breakout + RSI",
                            "trend": "Bearish",
                            "break_strength_atr": round(bear_break_strength, 3),
                            "rsi": round(rsi, 1)
                        },
                    )
                )
    def analyze_watchlist(
        self,
        token: str,
        timeframe: str,
        context: Optional[Dict[str, Any]] = None,
        max_items: int = 2,
        near_atr: float = 0.5,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Near-setups para UX: si no hay breakout, reportamos distancia al canal.
        near_atr: umbral de proximidad en unidades de ATR.
        """
        token_u = token.upper().strip()
        tf = str(timeframe).lower().strip()

        df = self._df_from_context(token_u, context)
        if df is None:
            df = get_ohlcv(token_u, tf, limit=350)
        if df is None or len(df) < (self.donchian_period + self.ema_period + 5):
            return []

        df = df.copy().reset_index(drop=True)
        df["donchian_high"] = df["high"].rolling(self.donchian_period).max()
        df["donchian_low"] = df["low"].rolling(self.donchian_period).min()
        df["ema200"] = df["close"].ewm(span=self.ema_period, adjust=False).mean()
        df["atr"] = self._compute_atr(df)

        last = df.iloc[-1]
        if (
            pd.isna(last["atr"])
            or pd.isna(last["ema200"])
            or pd.isna(last["donchian_high"])
            or pd.isna(last["donchian_low"])
        ):
            return []

        close = float(last["close"])
        atr = float(last["atr"])
        ema200 = float(last["ema200"])
        upper = float(last["donchian_high"])
        lower = float(last["donchian_low"])
        if atr <= 0:
            return []

        items: List[Dict[str, Any]] = []

        # Long bias if price above EMA200
        long_bias = close > ema200
        dist_to_upper_atr = (upper - close) / atr
        if long_bias and dist_to_upper_atr >= 0 and dist_to_upper_atr <= near_atr:
            items.append({
                "strategy_id": self.META.id,
                "token": token_u,
                "timeframe": timeframe,
                "side": "long",
                "trigger_price": round(upper, 2),
                "distance_atr": round(dist_to_upper_atr, 3),
                "reason": (
                    f"Near Donchian upper. Need breakout. Dist ≈ {dist_to_upper_atr:.2f} ATR. "
                    "Trend: bullish (above EMA200)."
                ),
            })

        # Short bias if price below EMA200
        short_bias = close < ema200
        dist_to_lower_atr = (close - lower) / atr
        if short_bias and dist_to_lower_atr >= 0 and dist_to_lower_atr <= near_atr:
            items.append({
                "strategy_id": self.META.id,
                "token": token_u,
                "timeframe": timeframe,
                "side": "short",
                "trigger_price": round(lower, 2),
                "distance_atr": round(dist_to_lower_atr, 3),
                "reason": (
                    f"Near Donchian lower. Need breakdown. Dist ≈ {dist_to_lower_atr:.2f} ATR. "
                    "Trend: bearish (below EMA200)."
                ),
            })




    def find_historical_signals(self, token: str, df: pd.DataFrame, timeframe: str = "1h") -> List[Signal]:
        """Backtesting helper: Scan entire DF for signals."""
        signals = []
        token_u = token.upper()

        df["donchian_high"] = df["high"].rolling(self.donchian_period).max()
        df["donchian_low"] = df["low"].rolling(self.donchian_period).min()
        df["ema200"] = df["close"].ewm(span=self.ema_period, adjust=False).mean()
        df["atr"] = self._compute_atr(df)
        df["rsi"] = self._rsi(df)

        for i in range(250, len(df)):
            last = df.iloc[i]
            prev = df.iloc[i-1]
            
            if pd.isna(last["atr"]) or pd.isna(last["ema200"]) or pd.isna(last["rsi"]):
                continue

            close = float(last["close"])
            atr = float(last["atr"])
            ema200 = float(last["ema200"])
            
            # USE PREVIOUS BANDS for breakout level
            upper = float(prev["donchian_high"])
            lower = float(prev["donchian_low"])
            rsi = float(last["rsi"])
            ts = last['timestamp']

            if atr <= 0:
                continue

            bull_break_strength = (close - upper) / atr 
            bear_break_strength = (lower - close) / atr 
            
            is_bull_breakout = (
                (float(prev["close"]) <= float(prev["donchian_high"])) 
                and (close > float(prev["donchian_high"]))
            )
            bull_trend_ok = close > ema200
            rsi_safe_long = rsi < 75 
            
            if is_bull_breakout and bull_trend_ok and rsi_safe_long and bull_break_strength >= self.min_break_atr:
                entry = close
                tp = entry + (self.tp_atr * atr)
                sl = entry - (self.sl_atr * atr)
                conf = self._confidence_bucket(bull_break_strength)
                try:
                    signals.append(Signal(
                        timestamp=ts, strategy_id=self.META.id, mode=self.META.mode, token=token_u, timeframe=timeframe,
                        direction="long", entry=entry, tp=tp, sl=sl, confidence=conf, source="BACKTEST",
                        rationale="Hist Bull Break + RSI", extra={"strength":bull_break_strength}
                    ))
                except Exception:
                    pass

            is_bear_breakout = (
                (float(prev["close"]) >= float(prev["donchian_low"])) 
                and (close < float(prev["donchian_low"]))
            )
            bear_trend_ok = close < ema200
            rsi_safe_short = rsi > 25

            if is_bear_breakout and bear_trend_ok and rsi_safe_short and bear_break_strength >= self.min_break_atr:
                entry = close
                tp = entry - (self.tp_atr * atr)
                sl = entry + (self.sl_atr * atr)
                conf = self._confidence_bucket(bear_break_strength)
                try:
                    signals.append(Signal(
                        timestamp=ts, strategy_id=self.META.id, mode=self.META.mode, token=token_u, timeframe=timeframe,
                        direction="short", entry=entry, tp=tp, sl=sl, confidence=conf, source="BACKTEST",
                        rationale="Hist Bear Break + RSI", extra={"strength":bear_break_strength}
                    ))
                except Exception:
                    pass
        return signals
