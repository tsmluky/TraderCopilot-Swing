# backend/strategies/DonchianBreakoutV2.py
"""
Donchian Breakout V2 (Native)

CRITICAL FIX (2026-01):
- Donchian channel must be computed on PREVIOUS candles (shift=1).
  If you include the current candle in rolling max/min, then close > upper is virtually impossible
  because upper >= high >= close. That kills signals.

Additional hardening:
- "First breakout candle only" (anti-spam): we only emit when the breakout condition becomes true
  this candle and was false on the previous candle.
- Slight tolerance on ATR rising filter via atr_ma_tolerance.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd

from .base import Strategy, StrategyMetadata
from core.schemas import Signal
from core.market_data_api import get_ohlcv_data


class DonchianBreakoutV2(Strategy):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        self.donchian_period = int(self.config.get("donchian_period", 20))
        self.ema200_period = int(self.config.get("ema200_period", 200))
        self.atr_period = int(self.config.get("atr_period", 14))
        self.atr_ma_period = int(self.config.get("atr_ma_period", 20))

        # How far beyond the channel (in ATR units) we require the wick to go
        # 0.0 is most permissive; 0.10 is still reasonable for swing.
        self.breakout_buffer_atr = float(self.config.get("breakout_buffer_atr", 0.00))

        # Allow ATR to be "almost rising" instead of strictly > MA
        # 0.95 means ATR >= 95% of ATR_MA passes.
        self.atr_ma_tolerance = float(self.config.get("atr_ma_tolerance", 0.95))

        # SL/TP in ATR units
        self.sl_atr_mult = float(self.config.get("sl_atr_mult", 2.0))
        self.tp_atr_mult = float(self.config.get("tp_atr_mult", 4.0))

        # Close tolerance to count as breakout confirmation even if close doesn't fully clear the channel
        self.close_confirm_atr = float(self.config.get("close_confirm_atr", 0.10))

    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            id="donchian_breakout_v2",
            name="Donchian Breakout V2 (Fixed)",
            description="Donchian Breakout (prev-channel) + EMA200 trend filter + ATR rising filter",
            version="2.0.1",
            default_timeframe="4h",
            universe=["*"],
            risk_profile="medium",
            mode="CUSTOM",
            source_type="ENGINE",
            enabled=True,
            config={
                "donchian_period": self.donchian_period,
                "ema200_period": self.ema200_period,
                "atr_period": self.atr_period,
                "atr_ma_period": self.atr_ma_period,
                "breakout_buffer_atr": self.breakout_buffer_atr,
                "atr_ma_tolerance": self.atr_ma_tolerance,
                "sl_atr_mult": self.sl_atr_mult,
                "tp_atr_mult": self.tp_atr_mult,
                "close_confirm_atr": self.close_confirm_atr,
            },
        )

    def analyze(self, df: pd.DataFrame, token: str, timeframe: str) -> List[Signal]:
        if df.empty or len(df) < max(self.ema200_period, self.donchian_period) + 5:
            return []

        d = df.copy()

        # Indicators
        d["ema200"] = d["close"].ewm(span=self.ema200_period, adjust=False).mean()
        d["atr"] = (d["high"] - d["low"]).rolling(window=self.atr_period).mean()
        d["atr_ma"] = d["atr"].rolling(window=self.atr_ma_period).mean()

        # Donchian channel must be based on *previous* candles (shift 1)
        # This is the key fix.
        d["donchian_upper"] = d["high"].rolling(window=self.donchian_period).max().shift(1)
        d["donchian_lower"] = d["low"].rolling(window=self.donchian_period).min().shift(1)

        d = d.dropna()
        if len(d) < 3:
            return []

        curr = d.iloc[-1]
        prev = d.iloc[-2]

        close = float(curr["close"])
        high = float(curr["high"])
        low = float(curr["low"])

        upper = float(curr["donchian_upper"])
        lower = float(curr["donchian_lower"])

        ema200 = float(curr["ema200"])
        atr = float(curr["atr"])
        atr_ma = float(curr["atr_ma"])

        buf = self.breakout_buffer_atr * atr
        confirm = self.close_confirm_atr * atr

        # Filters
        atr_ok = atr >= (atr_ma * self.atr_ma_tolerance)

        signals: List[Signal] = []

        # --- Long breakout condition (wick breaks + close confirms near channel) ---
        long_break_now = (high >= (upper + buf)) and (close >= (upper - confirm)) and (close > ema200) and atr_ok

        # Anti-spam: only first breakout candle (previous candle was not breaking)
        prev_upper = float(prev["donchian_upper"])
        prev_atr = float(prev["atr"])
        prev_buf = self.breakout_buffer_atr * prev_atr
        prev_confirm = self.close_confirm_atr * prev_atr
        prev_long_break = (float(prev["high"]) >= (prev_upper + prev_buf)) and (float(prev["close"]) >= (prev_upper - prev_confirm))

        if long_break_now and (not prev_long_break):
            sl = close - (self.sl_atr_mult * atr)
            tp = close + (self.tp_atr_mult * atr)

            # Confidence: combine ATR% and how far the wick cleared the channel
            atr_pct = (atr / close) if close > 0 else 0.0
            clear = (high - upper) / atr if atr > 0 else 0.0
            confidence = min(0.90, 0.58 + min(0.18, atr_pct * 3.0) + min(0.14, max(0.0, clear) * 0.08))

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
                    rationale=f"Donchian LONG breakout: wick >= upper(+{self.breakout_buffer_atr} ATR), close confirmed; ATR rising; price > EMA200",
                    source="ENGINE",
                    extra={
                        "donchian_upper": upper,
                        "donchian_lower": lower,
                        "ema200": ema200,
                        "atr": atr,
                        "atr_ma": atr_ma,
                        "breakout_buffer_atr": self.breakout_buffer_atr,
                        "close_confirm_atr": self.close_confirm_atr,
                    },
                )
            )

        # --- Short breakout condition ---
        short_break_now = (low <= (lower - buf)) and (close <= (lower + confirm)) and (close < ema200) and atr_ok

        prev_lower = float(prev["donchian_lower"])
        prev_short_break = (float(prev["low"]) <= (prev_lower - prev_buf)) and (float(prev["close"]) <= (prev_lower + prev_confirm))

        if short_break_now and (not prev_short_break):
            sl = close + (self.sl_atr_mult * atr)
            tp = close - (self.tp_atr_mult * atr)

            atr_pct = (atr / close) if close > 0 else 0.0
            clear = (lower - low) / atr if atr > 0 else 0.0
            confidence = min(0.90, 0.58 + min(0.18, atr_pct * 3.0) + min(0.14, max(0.0, clear) * 0.08))

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
                    rationale=f"Donchian SHORT breakout: wick <= lower(-{self.breakout_buffer_atr} ATR), close confirmed; ATR rising; price < EMA200",
                    source="ENGINE",
                    extra={
                        "donchian_upper": upper,
                        "donchian_lower": lower,
                        "ema200": ema200,
                        "atr": atr,
                        "atr_ma": atr_ma,
                        "breakout_buffer_atr": self.breakout_buffer_atr,
                        "close_confirm_atr": self.close_confirm_atr,
                    },
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
                    raw = get_ohlcv_data(token, timeframe, limit=350)
                    if not raw:
                        continue
                    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])

                if "timestamp" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                    df.set_index("timestamp", inplace=True)
                all_signals.extend(self.analyze(df, token, timeframe))
            except Exception as e:
                print(f"[DonchianBreakoutV2] Error analyzing {token}: {e}")

        return all_signals

    def get_watchlist(self, df: pd.DataFrame, token: str, timeframe: str) -> List[Dict[str, Any]]:
        """
        Identify near-setup opportunities for the watchlist.
        """
        if df.empty or len(df) < max(self.ema200_period, self.donchian_period) + 5:
            return []

        # Recalculate indicators (lightweight) - ideally this would be shared but for now we re-calc
        # to ensure stateless safety or reuse if passed. 
        # For performance, we assume df is the same pre-processed one.
        
        # We need the last candle
        curr = df.iloc[-1]
        
        close = float(curr["close"])
        upper = float(curr.get("donchian_upper", 0.0))
        lower = float(curr.get("donchian_lower", 0.0))
        ema200 = float(curr.get("ema200", 0.0))
        atr = float(curr.get("atr", 0.0))
        
        if atr <= 0:
            return []

        watchlist_items = []
        
        # --- Long Watch ---
        # Trend is up (Close > EMA200) AND Price is getting close to Upper Band
        if close > ema200 and upper > 0:
            distance_to_upper = upper - close
            distance_atr = distance_to_upper / atr
            
            # Watch if within 0.35 ATR of breakout, or even slightly above not yet confirmed
            if distance_atr <= 0.35:
                # Trigger price estimate
                trigger_price = upper + (self.breakout_buffer_atr * atr)
                
                watchlist_items.append({
                    "strategy_id": self.metadata().id,
                    "token": token,
                    "timeframe": timeframe,
                    "side": "long",
                    "distance_atr": round(distance_atr, 2),
                    "trigger_price": trigger_price,
                    "close": close,
                    "reason": f"Setup Long cercano ({distance_atr:.2f} ATR del Upper Channel). Tendencia alcista confirmada.",
                    "missing": ["Esperar ruptura confirmada del Upper Channel"]
                })

        # --- Short Watch ---
        # Trend is down (Close < EMA200) AND Price is getting close to Lower Band
        if close < ema200 and lower > 0:
            distance_to_lower = close - lower
            distance_atr = distance_to_lower / atr
            
            if distance_atr <= 0.35:
                # Trigger price estimate
                trigger_price = lower - (self.breakout_buffer_atr * atr)
                
                watchlist_items.append({
                    "strategy_id": self.metadata().id,
                    "token": token,
                    "timeframe": timeframe,
                    "side": "short",
                    "distance_atr": round(distance_atr, 2),
                    "trigger_price": trigger_price,
                    "close": close,
                    "reason": f"Setup Short cercano ({distance_atr:.2f} ATR del Lower Channel). Tendencia bajista confirmada.",
                    "missing": ["Esperar ruptura confirmada del Lower Channel"]
                })

        return watchlist_items
