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
        min_adx: float = 20.0,
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

    def _rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

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

            # Volume Filter: confirmed by volume surge
            vol_sma = df["volume"].rolling(20).mean().iloc[-1]
            current_vol = float(last["volume"])
            vol_ok = current_vol > vol_sma

            # RSI Trend Filter: Momentum alignment
            # Using adx_period (14) for RSI as standard
            rsi_series = df["close"].diff().apply(lambda x: max(x, 0)).rolling(14).mean() / \
                         df["close"].diff().apply(lambda x: abs(x)).rolling(14).mean() * 100
            # Manually computing RSI here or use helper if available? 
            # Given we are inside generate_signals and no _rsi helper exists, let's implement safe simple RSI or add helper.
            # Adding helper `_rsi` to class is better cleaner. See below.

            rsi = self._rsi(df).iloc[-1]
            
            # LONG SETUP
            # RSI > 50 confirms bullish momentum
            if bullish_cross and vol_ok and rsi > 50:
                entry = close
                tp = entry + (self.tp_atr * atr)
                sl = entry - (self.sl_atr * atr)

                rationale = (
                    f"We detected a Confirmed Uptrend. EMA Fast crossed above Slow EMA. "
                    f"Volume is surging ({int(current_vol/vol_sma*100)}% of avg). "
                    f"RSI ({rsi:.1f}) supports the move (>50). "
                    f"Trend Strength (ADX): {adx:.1f} ({strength_tag})."
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
                            "setup": "EMA Cross + Vol + RSI",
                            "trend_strength": strength_tag,
                            "adx": round(adx, 2),
                            "rsi": round(rsi, 1)
                        },
                    )
                )

            # SHORT SETUP
            # RSI < 50 confirms bearish momentum
            elif bearish_cross and vol_ok and rsi < 50:
                entry = close
                tp = entry - (self.tp_atr * atr)
                sl = entry + (self.sl_atr * atr)

                rationale = (
                    f"We detected a Confirmed Downtrend. EMA Fast crossed below Slow EMA. "
                    f"Volume is surging ({int(current_vol/vol_sma*100)}% of avg). "
                    f"RSI ({rsi:.1f}) supports the move (<50). "
                    f"Trend Strength (ADX): {adx:.1f} ({strength_tag})."
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
                            "setup": "EMA Cross + Vol + RSI",
                            "trend_strength": strength_tag,
                            "adx": round(adx, 2),
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
        near_cross: float = 0.005,
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
                # Gap shown as % (frontend expects 'distance_atr')
                "distance_atr": round(gap * 100, 2),
                "reason": (
                    f"EMAs converging. Gap ≈ {gap:.4f} of price. "
                    f"ADX {adx:.1f} suggests trend strength building."
                ),
            })

        return items[:max_items]

    def find_historical_signals(self, token: str, df: pd.DataFrame, timeframe: str = "1h") -> List[Signal]:
        """Backtesting helper: Scan entire DF for signals."""
        signals = []
        token_u = token.upper()
        
        # Compute indicators on full DF
        df["ema_fast"] = df["close"].ewm(span=self.ema_fast, adjust=False).mean()
        df["ema_slow"] = df["close"].ewm(span=self.ema_slow, adjust=False).mean()
        df["atr"] = self._atr(df)
        df["adx"] = self._adx(df)
        df["rsi"] = self._rsi(df)
        df["vol_sma"] = df["volume"].rolling(20).mean()
        
        # Iterate
        for i in range(120, len(df)):
            last = df.iloc[i]
            prev = df.iloc[i-1]
            
            if pd.isna(last["adx"]) or pd.isna(last["atr"]) or pd.isna(last["rsi"]): continue
            
            if pd.to_datetime(last['timestamp']).year < 2010: continue

            adx = float(last["adx"])
            atr = float(last["atr"])
            rsi = float(last["rsi"])
            close = float(last["close"])
            vol = float(last["volume"])
            vol_sma = float(last["vol_sma"]) if not pd.isna(last["vol_sma"]) else vol
            
            # Cross Logic using PREVIOUS candle for signal (confirmed cross)
            bullish_cross = (
                float(prev["ema_fast"]) <= float(prev["ema_slow"])
                and float(last["ema_fast"]) > float(last["ema_slow"])
            )
            bearish_cross = (
                float(prev["ema_fast"]) >= float(prev["ema_slow"])
                and float(last["ema_fast"]) < float(last["ema_slow"])
            )
            
            if adx < self.min_adx: continue
            
            # Filters
            vol_ok = vol > vol_sma
            
            # Bucket
            conf = self._confidence_bucket(adx)
            ts = last['timestamp']

            # LONG (RSI > 50)
            if bullish_cross and vol_ok and rsi > 50:
                entry = close
                tp = entry + (self.tp_atr * atr)
                sl = entry - (self.sl_atr * atr)
                try:
                    signals.append(Signal(
                        timestamp=ts, strategy_id=self.META.id, mode=self.META.mode, token=token_u, timeframe=timeframe,
                        direction="long", entry=entry, tp=tp, sl=sl, confidence=conf, source="BACKTEST",
                        rationale="Hist Bull + Vol + RSI", extra={"adx":adx}
                    ))
                except Exception: pass
            
            # SHORT (RSI < 50)
            elif bearish_cross and vol_ok and rsi < 50:
                entry = close
                tp = entry - (self.tp_atr * atr)
                sl = entry + (self.sl_atr * atr)
                try:
                    signals.append(Signal(
                        timestamp=ts, strategy_id=self.META.id, mode=self.META.mode, token=token_u, timeframe=timeframe,
                        direction="short", entry=entry, tp=tp, sl=sl, confidence=conf, source="BACKTEST",
                        rationale="Hist Bear + Vol + RSI", extra={"adx":adx}
                    ))
                except Exception: pass
        return signals
