# backend/strategies/TrendFollowingNative.py
"""
Trend Following Native Strategy (No pandas_ta dependency)

Fix (2026-01):
- Remove dependency on DataFrame.ta (pandas_ta not installed in many envs).
- Implement EMA / ATR / ADX using pandas only (Wilder smoothing).
- Make scan less timing-fragile: accept a cross that happened up to `post_cross_window` candles ago.
- Default ADX threshold lowered to 18 (more realistic for swing scans).
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd

from .base import Strategy, StrategyMetadata
from core.schemas import Signal
from core.market_data_api import get_ohlcv_data


class TrendFollowingNative(Strategy):
    """
    Logic:
    - LONG: EMA_fast crossed above EMA_slow within last `post_cross_window` candles AND ADX >= threshold
    - SHORT: EMA_fast crossed below EMA_slow within last `post_cross_window` candles AND ADX >= threshold
    - SL/TP: ATR-based (2*ATR SL, 4*ATR TP)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        self.ema_fast_len = int(self.config.get("ema_fast", 20))
        self.ema_slow_len = int(self.config.get("ema_slow", 100))

        self.adx_period = int(self.config.get("adx_period", 14))
        self.adx_threshold = float(self.config.get("adx_threshold", 18))

        self.atr_period = int(self.config.get("atr_period", 14))

        # How far back we search for last cross event (candles)
        self.cross_lookback = int(self.config.get("cross_lookback", 8))
        # Allow cross detected up to N candles late (0 = only exact cross candle)
        self.post_cross_window = int(self.config.get("post_cross_window", 1))

        # Stops
        self.sl_atr_mult = float(self.config.get("sl_atr_mult", 2.0))
        self.tp_atr_mult = float(self.config.get("tp_atr_mult", 4.0))

        # Avoid micro noise crosses: require some minimal spread between EMAs
        self.min_spread_pct = float(self.config.get("min_spread_pct", 0.001))  # 0.10%

    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            id="trend_following_native_v1",
            name=f"Trend Master Native (EMA{self.ema_fast_len}/{self.ema_slow_len})",
            description="Trend Following with EMA Cross (recent) + ADX Filter + ATR Stops (no pandas_ta)",
            version="1.0.1",
            default_timeframe="4h",
            universe=["*"],
            risk_profile="medium",
            mode="CUSTOM",
            source_type="ENGINE",
            enabled=True,
            config={
                "ema_fast": self.ema_fast_len,
                "ema_slow": self.ema_slow_len,
                "adx_period": self.adx_period,
                "adx_threshold": self.adx_threshold,
                "atr_period": self.atr_period,
                "cross_lookback": self.cross_lookback,
                "post_cross_window": self.post_cross_window,
                "sl_atr_mult": self.sl_atr_mult,
                "tp_atr_mult": self.tp_atr_mult,
                "min_spread_pct": self.min_spread_pct,
            },
        )

    @staticmethod
    def _wilder_smooth(series: pd.Series, period: int) -> pd.Series:
        # Wilder smoothing is equivalent to EMA with alpha=1/period
        return series.ewm(alpha=1.0 / float(period), adjust=False).mean()

    @staticmethod
    def _true_range(d: pd.DataFrame) -> pd.Series:
        prev_close = d["close"].shift(1)
        tr = pd.concat(
            [
                (d["high"] - d["low"]).abs(),
                (d["high"] - prev_close).abs(),
                (d["low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        return tr

    @classmethod
    def _atr(cls, d: pd.DataFrame, period: int) -> pd.Series:
        tr = cls._true_range(d)
        return cls._wilder_smooth(tr, period)

    @classmethod
    def _adx(cls, d: pd.DataFrame, period: int) -> pd.Series:
        high = d["high"]
        low = d["low"]

        up_move = high.diff()
        down_move = -low.diff()  # positive when low goes down

        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)

        tr = cls._true_range(d)

        atr = cls._wilder_smooth(tr, period)
        plus_di = 100.0 * (cls._wilder_smooth(plus_dm, period) / atr)
        minus_di = 100.0 * (cls._wilder_smooth(minus_dm, period) / atr)

        dx = (100.0 * (plus_di - minus_di).abs() / (plus_di + minus_di)).replace([pd.NA, pd.NaT], 0.0)
        dx = dx.fillna(0.0)

        adx = cls._wilder_smooth(dx, period)
        return adx

    @staticmethod
    def _find_cross_age(diff: pd.Series, lookback: int, bullish: bool) -> Optional[int]:
        """
        Returns how many candles ago the last cross happened.
        Age 0 => cross on the most recent candle in the slice.
        """
        if diff is None or len(diff) < 3:
            return None

        n = min(len(diff) - 1, max(2, lookback))
        s = diff.iloc[-(n + 1):].reset_index(drop=True)

        last_cross_idx: Optional[int] = None
        for i in range(1, len(s)):
            prev_v = float(s.iloc[i - 1])
            curr_v = float(s.iloc[i])
            if bullish:
                if prev_v <= 0 and curr_v > 0:
                    last_cross_idx = i
            else:
                if prev_v >= 0 and curr_v < 0:
                    last_cross_idx = i

        if last_cross_idx is None:
            return None

        age = (len(s) - 1) - last_cross_idx
        return int(age)

    def analyze(self, df: pd.DataFrame, token: str, timeframe: str) -> List[Signal]:
        if df.empty or len(df) < self.ema_slow_len + 10:
            return []

        d = df.copy()

        # EMA
        d["ema_fast"] = d["close"].ewm(span=self.ema_fast_len, adjust=False).mean()
        d["ema_slow"] = d["close"].ewm(span=self.ema_slow_len, adjust=False).mean()

        # ATR / ADX
        d["atr"] = self._atr(d, self.atr_period)
        d["adx"] = self._adx(d, self.adx_period)

        d = d.dropna()
        if len(d) < 3:
            return []

        curr = d.iloc[-1]
        close = float(curr["close"])
        ema_fast = float(curr["ema_fast"])
        ema_slow = float(curr["ema_slow"])
        atr = float(curr["atr"])
        adx = float(curr["adx"])

        # sanity: avoid micro-noise crosses
        spread_pct = abs(ema_fast - ema_slow) / close if close > 0 else 0.0
        if spread_pct < self.min_spread_pct:
            return []

        diff = d["ema_fast"] - d["ema_slow"]
        bull_age = self._find_cross_age(diff, self.cross_lookback, bullish=True)
        bear_age = self._find_cross_age(diff, self.cross_lookback, bullish=False)

        signals: List[Signal] = []

        if adx >= self.adx_threshold:
            # LONG
            if bull_age is not None and bull_age <= self.post_cross_window and ema_fast > ema_slow:
                sl = close - (self.sl_atr_mult * atr)
                tp = close + (self.tp_atr_mult * atr)

                freshness = 0.06 if bull_age == 0 else 0.03
                confidence = min(
                    0.92,
                    0.58
                    + min(0.22, (adx - self.adx_threshold) / 80.0)
                    + min(0.12, spread_pct * 8.0)
                    + freshness,
                )

                signals.append(
                    Signal(
                        timestamp=(curr.name if isinstance(curr.name, datetime) else datetime.utcnow()),
                        strategy_id=self.metadata().id,
                        mode="CUSTOM",
                        token=token.upper(),
                        timeframe=timeframe,
                        direction="long",
                        entry=close,
                        tp=tp,
                        sl=sl,
                        confidence=confidence,
                        rationale=f"EMA bull cross (age={bull_age}) + ADX {adx:.1f} (>= {self.adx_threshold})",
                        source="ENGINE",
                        extra={"adx": adx, "atr": atr, "spread_pct": spread_pct, "cross_age": bull_age},
                    )
                )

            # SHORT
            if bear_age is not None and bear_age <= self.post_cross_window and ema_fast < ema_slow:
                sl = close + (self.sl_atr_mult * atr)
                tp = close - (self.tp_atr_mult * atr)

                freshness = 0.06 if bear_age == 0 else 0.03
                confidence = min(
                    0.92,
                    0.58
                    + min(0.22, (adx - self.adx_threshold) / 80.0)
                    + min(0.12, spread_pct * 8.0)
                    + freshness,
                )

                signals.append(
                    Signal(
                        timestamp=(curr.name if isinstance(curr.name, datetime) else datetime.utcnow()),
                        strategy_id=self.metadata().id,
                        mode="CUSTOM",
                        token=token.upper(),
                        timeframe=timeframe,
                        direction="short",
                        entry=close,
                        tp=tp,
                        sl=sl,
                        confidence=confidence,
                        rationale=f"EMA bear cross (age={bear_age}) + ADX {adx:.1f} (>= {self.adx_threshold})",
                        source="ENGINE",
                        extra={"adx": adx, "atr": atr, "spread_pct": spread_pct, "cross_age": bear_age},
                    )
                )

        return signals

    def generate_signals(
        self,
        tokens: List[str],
        timeframe: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Signal]:
        valid_tokens = self.validate_tokens(tokens)
        all_signals: List[Signal] = []

        for token in valid_tokens:
            try:
                if context and "data" in context and token in context["data"]:
                    raw = context["data"][token]
                    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
                else:
                    raw = get_ohlcv_data(token, timeframe, limit=340)
                    if not raw:
                        continue
                    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])

                if "timestamp" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                    df.set_index("timestamp", inplace=True)

                all_signals.extend(self.analyze(df, token, timeframe))
            except Exception as e:
                print(f"[TrendMaster] Error analyzing {token}: {e}")


        return all_signals

    def get_watchlist(self, df: pd.DataFrame, token: str, timeframe: str) -> List[Dict[str, Any]]:
        """
        Identify near-setup opportunities for the watchlist (Trend).
        """
        if df.empty or len(df) < max(self.ema_slow_len, self.adx_period) + 5:
            return []

        # 1. Calc Indicators (local scope)
        d = df.copy()
        d["ema_fast"] = d["close"].ewm(span=self.ema_fast_len, adjust=False).mean()
        d["ema_slow"] = d["close"].ewm(span=self.ema_slow_len, adjust=False).mean()
        d["adx"] = self._adx(d, self.adx_period)
        d["atr"] = self._atr(d, self.atr_period) # Calculate ATR for distance normalization

        curr = d.iloc[-1]
        close = float(curr["close"])
        ema_fast = float(curr["ema_fast"])
        ema_slow = float(curr["ema_slow"])
        adx = float(curr["adx"])
        atr = float(curr.get("atr", 0.0))

        if close <= 0 or atr <= 0:
            return []

        diff = ema_fast - ema_slow
        spread_pct = abs(diff) / close
        
        watchlist_items = []
        
        # --- Logic 1: Near Cross (Golden/Death Cross pending) ---
        # If strict cross hasn't happened but they are converging
        # Definition of "Near": Spread < 0.5% (0.005) or < 0.25% depending on asset
        # Let's use ATR based distance for consistency? EMAs spread in ATR units.
        spread_atr = abs(diff) / atr
        
        if spread_atr < 0.5 and spread_atr > 0.05: # Very close, but not virtually zero/noise
            # Check direction of potential cross
            # If Fast < Slow but rising relative to Slow? Hard to tell without history.
            # Simplified: Just check proximity.
            
            # If Fast is below Slow but close -> Watch for Long
            if ema_fast < ema_slow:
                 watchlist_items.append({
                    "strategy_id": self.metadata().id,
                    "token": token,
                    "timeframe": timeframe,
                    "side": "long",
                    "distance_atr": round(spread_atr, 2),
                    "trigger_price": ema_slow, # Approx trigger
                    "close": close,
                    "reason": f"Posible Golden Cross pronto. Spread actual: {spread_atr:.2f} ATR.",
                    "missing": ["Esperar cruce EMA Fast > EMA Slow"]
                })
            # If Fast is above Slow but close -> Watch for Short
            elif ema_fast > ema_slow:
                 watchlist_items.append({
                    "strategy_id": self.metadata().id,
                    "token": token,
                    "timeframe": timeframe,
                    "side": "short",
                    "distance_atr": round(spread_atr, 2),
                    "trigger_price": ema_slow, # Approx trigger
                    "close": close,
                    "reason": f"Posible Death Cross pronto. Spread actual: {spread_atr:.2f} ATR.",
                    "missing": ["Esperar cruce EMA Fast < EMA Slow"]
                })

        # --- Logic 2: Cross Confirmed but ADX Low (Waiting for strength) ---
        # more complex, requires looking back.
        # Let's stick to simple "Near Cross" or "Recent Cross awaiting ADX" if easy.
        
        # Check if cross happened recently
        diff_series = d["ema_fast"] - d["ema_slow"]
        bull_age = self._find_cross_age(diff_series, self.cross_lookback, True)
        bear_age = self._find_cross_age(diff_series, self.cross_lookback, False)

        has_recent_bull = (bull_age is not None and bull_age <= self.post_cross_window + 2)
        has_recent_bear = (bear_age is not None and bear_age <= self.post_cross_window + 2)
        
        if has_recent_bull and adx < self.adx_threshold:
             watchlist_items.append({
                    "strategy_id": self.metadata().id,
                    "token": token,
                    "timeframe": timeframe,
                    "side": "long",
                    "distance_atr": 0.0, # Condition met, just waiting for filter
                    "trigger_price": close, 
                    "close": close,
                    "reason": f"Cruce alcista confirmado hace {bull_age} velas, pero ADX débil ({adx:.1f} < {self.adx_threshold}).",
                    "missing": [f"Esperar ADX > {self.adx_threshold}"]
                })
        
        if has_recent_bear and adx < self.adx_threshold:
             watchlist_items.append({
                    "strategy_id": self.metadata().id,
                    "token": token,
                    "timeframe": timeframe,
                    "side": "short",
                    "distance_atr": 0.0,
                    "trigger_price": close, 
                    "close": close,
                    "reason": f"Cruce bajista confirmado hace {bear_age} velas, pero ADX débil ({adx:.1f} < {self.adx_threshold}).",
                    "missing": [f"Esperar ADX > {self.adx_threshold}"]
                })

        return watchlist_items
