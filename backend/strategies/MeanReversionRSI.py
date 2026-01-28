# backend/strategies/MeanReversionRSI.py

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

class MeanReversionRSI:
    """
    Estrategia Premium de Reversión a la Media.
    
    Concepto:
    - Busca "agotamiento" del movimiento en extremos.
    - No entra "contra tendencia" ciega, espera confirmación de rechazo (Cierre dentro de bandas).
    
    Indicadores:
    - Bollinger Bands (20, 2.5): Desviación alta para asegurar extremos reales.
    - RSI (14): Filtro de sobrecompra/sobreventa (>70 / <30).
    """

    META = StrategyMeta(
        id="mean_reversion_rsi_v1",
        name="Mean Reversion (BB+RSI)",
        description="Contra-tendencia en extremos de volatilidad (Bollinger 2.5) con filtro RSI y gatillo de rechazo.",
        supported_tokens=["BTC", "ETH", "SOL", "BNB", "XRP"],
        supported_timeframes=["1h", "4h", "1d"],
        mode="PRO", # Reserved for PRO due to high precision
    )

    def __init__(
        self,
        bb_period: int = 20,
        bb_std: float = 2.0,
        rsi_period: int = 14,
        rsi_overbought: float = 70.0,
        rsi_oversold: float = 30.0,
        tp_atr: float = 2.0, # Target: Return to mean (SMA20) or ATR push? Using ATR for consistency.
        sl_atr: float = 1.5,
        atr_period: int = 14
    ):
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
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
            cols = ["open", "high", "low", "close", "volume"]
            df[cols] = df[cols].astype(float)
            return df
        except Exception:
            return None

    def _atr(self, df: pd.DataFrame) -> pd.Series:
        high = df["high"]
        low = df["low"]
        close = df["close"]
        prev_close = close.shift(1)
        tr = pd.concat([(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
        return tr.rolling(self.atr_period).mean()

    def _rsi(self, series: pd.Series) -> pd.Series:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.rolling(window=self.rsi_period, min_periods=1).mean()
        avg_loss = loss.rolling(window=self.rsi_period, min_periods=1).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def generate_signals(
        self, 
        tokens: List[str], 
        timeframe: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> List[Signal]:
        signals: List[Signal] = []
        tf = str(timeframe).lower().strip()

        for token in tokens:
            token_u = token.upper().strip()
            df = self._df_from_context(token_u, context)
            if df is None:
                df = get_ohlcv(token_u, tf, limit=350)
            
            if df is None or len(df) < 50:
                continue
            
            df = df.copy().reset_index(drop=True)
            
            # Indicators
            df['sma'] = df['close'].rolling(self.bb_period).mean()
            df['std'] = df['close'].rolling(self.bb_period).std()
            df['upper'] = df['sma'] + (self.bb_std * df['std'])
            df['lower'] = df['sma'] - (self.bb_std * df['std'])
            df['rsi'] = self._rsi(df['close'])
            df['atr'] = self._atr(df)
            
            last = df.iloc[-1]
            # prev = df.iloc[-2] # Confirmation candle (Unused)
            
            if pd.isna(last['rsi']) or pd.isna(last['upper']):
                continue
            
            # Logic: We look for a "Rejection" that happened in the LAST CLOSED CANDLE (prev)
            # OR we can look at current live candle if we want aggressive.
            # Standard Swing: Analyze CLOSED candles to avoid fakeouts.
            # Let's say we analyze the 'last' candle as the "just closed" one (depending on how get_ohlcv works).
            # Assuming 'last' is the most recent completed candle for signal generation context:
            
            close = float(last['close'])
            high = float(last['high'])
            low = float(last['low'])
            upper = float(last['upper'])
            lower = float(last['lower'])
            rsi = float(last['rsi'])
            atr = float(last['atr'])

            # LONG SETUP
            # 1. Price touched lower band (Low < Lower)
            # 2. Price closed INSIDE band (Close > Lower) -> Rejection
            # 3. RSI is/was Oversold (<30)
            touched_lower = low < lower
            closed_inside = close > lower
            rsi_oversold = rsi < self.rsi_oversold
            
            if touched_lower and closed_inside and rsi_oversold:
                entry = close
                tp = entry + (self.tp_atr * atr) # Target: Rebound
                sl = entry - (self.sl_atr * atr) # Stop: Below the wick
                
                rationale = (
                    f"Mean Reversion Buy: Price rejected Lower BB ({self.bb_std} std). "
                    f"RSI ({rsi:.1f}) is Oversold (<{self.rsi_oversold})."
                )
                
                signals.append(Signal(
                    timestamp=datetime.utcnow(),
                    token=token_u,
                    direction="long",
                    entry=round(entry, 6),
                    tp=round(tp, 6),
                    sl=round(sl, 6),
                    confidence=0.85, # High confidence due to strict filters
                    rationale=rationale,
                    extra={"setup": "Mean Reversion", "rsi": round(rsi, 1), "bb_std": self.bb_std}
                ))

            # SHORT SETUP
            touched_upper = high > upper
            closed_below = close < upper
            rsi_overbought = rsi > self.rsi_overbought
            
            if touched_upper and closed_below and rsi_overbought:
                entry = close
                tp = entry - (self.tp_atr * atr)
                sl = entry + (self.sl_atr * atr)
                
                rationale = (
                    f"We detected a Reversion Pullback. Price rejected the Upper Bollinger Band ({self.bb_std} std). "
                    f"RSI ({rsi:.1f}) is Overbought (>{self.rsi_overbought}) and confirms exhaustion. "
                    "Probability of pullback is high."
                )
                signals.append(Signal(
                    timestamp=datetime.utcnow(),
                    token=token_u,
                    direction="short",
                    entry=round(entry, 6),
                    tp=round(tp, 6),
                    sl=round(sl, 6),
                    confidence=0.85,
                    rationale=f"Mean Reversion: Rejected Upper BB ({self.bb_std}std) with RSI {rsi:.1f} (Overbought).",
                    extra={"setup": "Mean Reversion", "rsi": round(rsi, 1), "bb_std": self.bb_std}
                ))
                
        return signals

    def analyze_watchlist(
        self,
        token: str,
        timeframe: str,
        context: Optional[Dict[str, Any]] = None,
        near_pct: float = 0.015, # 1.5% distance from band
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Near-setups: Price approaching BB or RSI entering zone.
        """
        token_u = token.upper().strip()
        tf = str(timeframe).lower().strip()

        df = self._df_from_context(token_u, context)
        if df is None:
            df = get_ohlcv(token_u, tf, limit=350)
        
        if df is None or len(df) < 50:
            return []
        
        df = df.copy().reset_index(drop=True)
        # Indicators
        df['sma'] = df['close'].rolling(self.bb_period).mean()
        df['std'] = df['close'].rolling(self.bb_period).std()
        df['upper'] = df['sma'] + (self.bb_std * df['std'])
        df['lower'] = df['sma'] - (self.bb_std * df['std'])
        df['rsi'] = self._rsi(df['close'])
        df['atr'] = self._atr(df)
        
        last = df.iloc[-1]
        if pd.isna(last['rsi']) or pd.isna(last['upper']):
            return []
        
        close = float(last['close'])
        upper = float(last['upper'])
        lower = float(last['lower'])
        rsi = float(last['rsi'])
        # atr = float(last['atr']) # Unused
        
        if close <= 0:
            return []
        
        items = []
        
        # 1. Near Lower Band (Potential Long)
        # Check distance to lower band
        dist_lower = (close - lower) / close
        # "Near" if within near_pct OR if RSI is getting crushed (< 35)
        is_near_lower = abs(dist_lower) <= near_pct
        rsi_low = rsi < 38
        
        if is_near_lower or rsi_low:
             items.append({
                "strategy_id": self.META.id,
                "token": token_u,
                "timeframe": timeframe,
                "side": "long",
                "trigger_price": round(lower, 2),
                # We use 'distance_atr' as a sorting key. 
                # If RSI is low, we treat it as very close (0.1 ATR)
                "distance_atr": round(dist_lower * 10, 2) if not rsi_low else 0.1, 
                "reason": (
                    f"Mean Reversion Watch: RSI {rsi:.1f} (Approaching {self.rsi_oversold}). "
                    f"Price {dist_lower*100:.2f}% from Lower BB."
                ),
            })
             
        # 2. Near Upper Band (Potential Short)
        dist_upper = (upper - close) / close
        is_near_upper = abs(dist_upper) <= near_pct
        rsi_high = rsi > 62
        
        if is_near_upper or rsi_high:
             items.append({
                "strategy_id": self.META.id,
                "token": token_u,
                "timeframe": timeframe,
                "side": "short",
                "trigger_price": round(upper, 2),
                "distance_atr": round(dist_upper * 10, 2) if not rsi_high else 0.1,
                "reason": (
                    f"Mean Reversion Watch: RSI {rsi:.1f} (Approaching {self.rsi_overbought}). "
                    f"Price {dist_upper*100:.2f}% from Upper BB."
                ),
            })
            
        return items

    def find_historical_signals(self, token: str, df: pd.DataFrame, timeframe: str = "1h") -> List[Signal]:
        """Backtesting helper: Scan entire DF for signals."""
        signals = []
        token_u = token.upper()
        
        # Ensure indicators exist
        if 'rsi' not in df.columns:
            df['sma'] = df['close'].rolling(self.bb_period).mean()
            df['std'] = df['close'].rolling(self.bb_period).std()
            df['upper'] = df['sma'] + (self.bb_std * df['std'])
            df['lower'] = df['sma'] - (self.bb_std * df['std'])
            df['rsi'] = self._rsi(df['close'])
            df['atr'] = self._atr(df)

        for i in range(50, len(df)):
            row = df.iloc[i]
            
            if pd.isna(row['rsi']) or pd.isna(row['upper']):
                continue
            
            close = float(row['close'])
            high = float(row['high'])
            low = float(row['low'])
            upper = float(row['upper'])
            lower = float(row['lower'])
            rsi = float(row['rsi'])
            atr = float(row['atr'])
            ts = row['timestamp']

            # LONG
            if low < lower and close > lower and rsi < self.rsi_oversold:
                entry = close
                tp = entry + (self.tp_atr * atr)
                sl = entry - (self.sl_atr * atr)
                signals.append(Signal(
                    timestamp=ts, 
                    strategy_id=self.META.id,
                    mode=self.META.mode,
                    token=token_u, 
                    timeframe=timeframe,
                    direction="long", 
                    entry=entry, 
                    tp=tp, 
                    sl=sl, 
                    confidence=0.85,
                    source="BACKTEST",
                    rationale="Historical test",
                    extra={"rsi": rsi, "bb_std": self.bb_std}
                ))

            # SHORT
            if high > upper and close < upper and rsi > self.rsi_overbought:
                entry = close
                tp = entry - (self.tp_atr * atr)
                sl = entry + (self.sl_atr * atr)
                signals.append(Signal(
                    timestamp=ts, 
                    strategy_id=self.META.id,
                    mode=self.META.mode,
                    token=token_u, 
                    timeframe=timeframe,
                    direction="short", 
                    entry=entry, 
                    tp=tp, 
                    sl=sl, 
                    confidence=0.85,
                    source="BACKTEST",
                    rationale="Historical test",
                    extra={"rsi": rsi, "bb_std": self.bb_std}
                ))
        
        return signals


