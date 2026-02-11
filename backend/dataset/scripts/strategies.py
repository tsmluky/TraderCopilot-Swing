import pandas as pd
import numpy as np

class Strategy:
    def generate_signals(self, df):
        raise NotImplementedError("Should implement generate_signals method")

class DonchianStrategy(Strategy):
    def __init__(
        self, window=20, exit_window=None, ema_filter=None, rsi_filter=None, 
        adx_threshold=None, atr_trailing=None, fixed_sl_atr=None, 
        fixed_tp_atr=None, allow_short=False
    ):
        self.window = window
        self.exit_window = exit_window if exit_window else window
        self.ema_filter = ema_filter
        self.rsi_filter = rsi_filter
        self.adx_threshold = adx_threshold
        self.atr_trailing = atr_trailing 
        self.fixed_sl_atr = fixed_sl_atr 
        self.fixed_tp_atr = fixed_tp_atr 
        self.allow_short = allow_short

    def generate_signals(self, df):
        data = df.copy()
        
        # Donchian Channels
        data['upper'] = data['high'].rolling(window=self.window).max().shift(1)
        data['lower'] = data['low'].rolling(window=self.exit_window).min().shift(1)
        
        # Indicators
        if self.ema_filter:
            data['ema'] = data['close'].ewm(span=self.ema_filter, adjust=False).mean()
            
        if self.rsi_filter:
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['rsi'] = 100 - (100 / (1 + rs))

        # ADX Calculation (if threshold set)
        if self.adx_threshold is not None:
             data['tr0'] = abs(data['high'] - data['low'])
             data['tr1'] = abs(data['high'] - data['close'].shift())
             data['tr2'] = abs(data['low'] - data['close'].shift())
             data['tr'] = data[['tr0', 'tr1', 'tr2']].max(axis=1)
             data['up_move'] = data['high'] - data['high'].shift()
             data['down_move'] = data['low'].shift() - data['low']
             data['plus_dm'] = np.where(
                 (data['up_move'] > data['down_move']) & (data['up_move'] > 0), 
                 data['up_move'], 0
             )
             data['minus_dm'] = np.where(
                 (data['down_move'] > data['up_move']) & (data['down_move'] > 0), 
                 data['down_move'], 0
             )
             adx_window = 14
             tr_smooth = data['tr'].rolling(window=adx_window).mean()
             data['plus_di'] = 100 * (data['plus_dm'].rolling(window=adx_window).mean() / tr_smooth)
             data['minus_di'] = 100 * (data['minus_dm'].rolling(window=adx_window).mean() / tr_smooth)
             
             data['dx'] = 100 * abs(data['plus_di'] - data['minus_di']) / (data['plus_di'] + data['minus_di'])
             data['adx'] = data['dx'].rolling(window=adx_window).mean()

        if self.atr_trailing or self.fixed_sl_atr or self.fixed_tp_atr:
            high_low = data['high'] - data['low']
            high_close = np.abs(data['high'] - data['close'].shift())
            low_close = np.abs(data['low'] - data['close'].shift())
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr_window = self.atr_trailing[0] if self.atr_trailing else 14
            data['atr'] = tr.rolling(window=atr_window).mean()
        
        data['signal'] = 0
        
        # Conditions
        long_condition = data['close'] > data['upper']
        short_condition = data['close'] < data['lower']
        
        if self.ema_filter:
            long_condition &= (data['close'] > data['ema'])
            short_condition &= (data['close'] < data['ema'])
            
        if self.rsi_filter:
            long_condition &= (data['rsi'] > self.rsi_filter)
            
        if self.adx_threshold is not None:
            # Filter Entries: Trend must be strong
            # We use fillna(0) to avoid issues at start
            is_trending = data['adx'].fillna(0) > self.adx_threshold
            long_condition &= is_trending
            short_condition &= is_trending
        
        # Loop for Complex Exits or Vectorized for Speed
        if self.atr_trailing or self.fixed_sl_atr or self.fixed_tp_atr or self.allow_short:
             # Loop is safer for Bi-Directional state adherence if using allow_short to ensure clean flips
            position = 0
            entry_price = 0
            highest_since_entry = 0
            lowest_since_entry = 99999999
            
            for i in range(len(data)):
                if i < self.window:
                    continue
                price = data['close'].iloc[i]
                high = data['high'].iloc[i]
                low = data['low'].iloc[i]
                idx = data.index[i]
                atr = data['atr'].iloc[i] if 'atr' in data.columns else 0
                
                # Manage Long
                if position == 1:
                    exit_signal = False
                    if self.fixed_sl_atr and low < (entry_price - atr * self.fixed_sl_atr):
                        exit_signal = True
                    if self.fixed_tp_atr and high > (entry_price + atr * self.fixed_tp_atr):
                        exit_signal = True
                    if self.atr_trailing and price < (highest_since_entry - (atr * self.atr_trailing[1])):
                        exit_signal = True
                    
                    # Channel Exit
                    if price < data['lower'].iloc[i]:
                        if self.allow_short:
                            # Flip to Short (Only if ADX allows re-entry? Or Flip is always allowed?)
                            # Standard: Reversal signal usually implies logic is met.
                            # But wait, short_condition ALREADY checks ADX?
                            # If short_condition[i] is True, it means ADX is > 25.
                            # So we check short_condition.
                            if short_condition.iloc[i]:
                                data.at[idx, 'signal'] = -1
                                position = -1
                                entry_price = price
                                lowest_since_entry = low
                                continue
                            else:
                                exit_signal = True # Close Long, but don't open Short (choppy reversal)
                        else:
                            exit_signal = True

                    if exit_signal:
                        data.at[idx, 'signal'] = 0
                        position = 0
                    else:
                        highest_since_entry = max(highest_since_entry, high)
                        
                # Manage Short
                elif position == -1:
                    exit_signal = False
                    if self.fixed_sl_atr and high > (entry_price + atr * self.fixed_sl_atr):
                        exit_signal = True
                    if self.fixed_tp_atr and low < (entry_price - atr * self.fixed_tp_atr):
                        exit_signal = True
                    if self.atr_trailing and price > (lowest_since_entry + (atr * self.atr_trailing[1])):
                        exit_signal = True
                    
                    # Channel Exit
                    if price > data['upper'].iloc[i]:
                        if True: # Always allow flip back to long? Check ADX condition
                            if long_condition.iloc[i]: # Checks ADX internally
                                data.at[idx, 'signal'] = 1
                                position = 1
                                entry_price = price
                                highest_since_entry = high
                                continue
                            else:
                                exit_signal = True # Close Short, don't open Long

                    if exit_signal:
                        data.at[idx, 'signal'] = 0
                        position = 0
                    else:
                        lowest_since_entry = min(lowest_since_entry, low)

                # Entry
                elif position == 0:
                    if long_condition.iloc[i]:
                        data.at[idx, 'signal'] = 1
                        position = 1
                        entry_price = price
                        highest_since_entry = high
                    elif self.allow_short and short_condition.iloc[i]:
                        data.at[idx, 'signal'] = -1
                        position = -1
                        entry_price = price
                        lowest_since_entry = low

        else:
            # Simple Vectorized
            data.loc[long_condition, 'signal'] = 1
            if self.allow_short:
                data.loc[short_condition, 'signal'] = -1
            else:
                 data.loc[short_condition, 'signal'] = 0
        
        return data

class MeanReversionStrategy(Strategy):
    def __init__(self, window=20, std_dev=2.0, adx_threshold=None, rsi_threshold=None, sl_atr=None):
        self.window = window
        self.std_dev = std_dev
        self.adx_threshold = adx_threshold 
        self.rsi_threshold = rsi_threshold 
        self.sl_atr = sl_atr

    def generate_signals(self, df):
        data = df.copy()
        
        # Bollinger Bands
        data['ma'] = data['close'].rolling(window=self.window).mean()
        data['std'] = data['close'].rolling(window=self.window).std()
        data['upper'] = data['ma'] + (data['std'] * self.std_dev)
        data['lower'] = data['ma'] - (data['std'] * self.std_dev)
        
        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))

        # ADX
        data['tr0'] = abs(data['high'] - data['low'])
        data['tr1'] = abs(data['high'] - data['close'].shift())
        data['tr2'] = abs(data['low'] - data['close'].shift())
        data['tr'] = data[['tr0', 'tr1', 'tr2']].max(axis=1)
        data['up_move'] = data['high'] - data['high'].shift()
        data['down_move'] = data['low'].shift() - data['low']
        data['plus_dm'] = np.where(
            (data['up_move'] > data['down_move']) & (data['up_move'] > 0), 
            data['up_move'], 0
        )
        data['minus_dm'] = np.where(
            (data['down_move'] > data['up_move']) & (data['down_move'] > 0), 
            data['down_move'], 0
        )
        adx_window = 14
        tr_smooth = data['tr'].rolling(window=adx_window).mean()
        data['plus_di'] = 100 * (data['plus_dm'].rolling(window=adx_window).mean() / tr_smooth)
        data['minus_di'] = 100 * (data['minus_dm'].rolling(window=adx_window).mean() / tr_smooth)
        
        data['dx'] = 100 * abs(data['plus_di'] - data['minus_di']) / (data['plus_di'] + data['minus_di'])
        data['adx'] = data['dx'].rolling(window=adx_window).mean()

        data['signal'] = 0
        
        # Entry Logic (Long Only for now as implemented previously)
        long_condition = data['close'] < data['lower']
        
        if self.adx_threshold:
            long_condition &= (data['adx'] < self.adx_threshold)

        if self.rsi_threshold:
            long_condition &= (data['rsi'] < self.rsi_threshold)

        # Signal Generation
        has_sl_atr = hasattr(self, 'sl_atr') and self.sl_atr is not None
        
        if not has_sl_atr:
            exit_condition = data['close'] > data['ma']
            data.loc[long_condition, 'signal'] = 1
            data.loc[exit_condition, 'signal'] = 0 # Ensure 0 for exit
        else:
            position = 0
            entry_price = 0
            atr_series = data['tr'].rolling(window=14).mean() # Approx ATR

            for i in range(len(data)):
                if i < self.window:
                    continue
                price = data['close'].iloc[i]
                low = data['low'].iloc[i]
                idx = data.index[i]
                atr = atr_series.iloc[i]
                
                if position == 1:
                    exit_signal = False
                    if self.sl_atr:
                        if low < (entry_price - atr * self.sl_atr):
                            exit_signal = True
                    
                    if not exit_signal and price > data['ma'].iloc[i]:
                        exit_signal = True
                            
                    if exit_signal:
                        data.at[idx, 'signal'] = 0 # Exit
                        position = 0
                
                if position == 0:
                    if long_condition.iloc[i]:
                        data.at[idx, 'signal'] = 1
                        position = 1
                        entry_price = price
        
        return data

class CompositeStrategy(Strategy):
    def __init__(self, donchian_params, mean_rev_params, adx_threshold=25):
        self.donchian = DonchianStrategy(**donchian_params)
        self.mean_rev = MeanReversionStrategy(**mean_rev_params)
        self.adx_threshold = adx_threshold

    def generate_signals(self, df):
        data = df.copy()
        
        # 1. Generate Sub-Signals
        df_donchian = self.donchian.generate_signals(df)
        df_mean_rev = self.mean_rev.generate_signals(df)
        
        # 2. Calculate Regime Indicator (ADX)
        data['tr0'] = abs(data['high'] - data['low'])
        data['tr1'] = abs(data['high'] - data['close'].shift())
        data['tr2'] = abs(data['low'] - data['close'].shift())
        data['tr'] = data[['tr0', 'tr1', 'tr2']].max(axis=1)
        data['up_move'] = data['high'] - data['high'].shift()
        data['down_move'] = data['low'].shift() - data['low']
        data['plus_dm'] = np.where(
            (data['up_move'] > data['down_move']) & (data['up_move'] > 0), 
            data['up_move'], 0
        )
        data['minus_dm'] = np.where(
            (data['down_move'] > data['up_move']) & (data['down_move'] > 0), 
            data['down_move'], 0
        )
        adx_window = 14
        tr_smooth = data['tr'].rolling(window=adx_window).mean()
        data['plus_di'] = 100 * (data['plus_dm'].rolling(window=adx_window).mean() / tr_smooth)
        data['minus_di'] = 100 * (data['minus_dm'].rolling(window=adx_window).mean() / tr_smooth)
        
        data['dx'] = 100 * abs(data['plus_di'] - data['minus_di']) / (data['plus_di'] + data['minus_di'])
        data['adx'] = data['dx'].rolling(window=adx_window).mean()
        
        # 3. Combine Signals based on Regime
        # Vectorized choice
        is_trend = data['adx'].fillna(0) >= self.adx_threshold
        
        # We need to align indices potentially, but since we copy logic:
        # Donchian Signals
        sig_trend = df_donchian['signal']
        # Mean Rev Signals
        sig_range = df_mean_rev['signal']
        
        # Final Signal
        data['signal'] = np.where(is_trend, sig_trend, sig_range)
        
        # Optional: Save debug info
        data['regime'] = np.where(is_trend, 'TREND', 'RANGE')
        
        return data

class SMACrossoverStrategy(Strategy):
    def __init__(self, fast_window=50, slow_window=200, use_ema=False, adx_threshold=None, allow_short=False):
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.use_ema = use_ema
        self.adx_threshold = adx_threshold
        self.allow_short = allow_short

    def generate_signals(self, df):
        data = df.copy()
        
        if self.use_ema:
            data['fast_ma'] = data['close'].ewm(span=self.fast_window, adjust=False).mean()
            data['slow_ma'] = data['close'].ewm(span=self.slow_window, adjust=False).mean()
        else:
            data['fast_ma'] = data['close'].rolling(window=self.fast_window).mean()
            data['slow_ma'] = data['close'].rolling(window=self.slow_window).mean()
        
        data['signal'] = 0
        
        cond_long = data['fast_ma'] > data['slow_ma']
        cond_short = data['fast_ma'] < data['slow_ma']
        
        if self.adx_threshold:
            # ADX Calc
            data['tr0'] = abs(data['high'] - data['low'])
            data['tr1'] = abs(data['high'] - data['close'].shift())
            data['tr2'] = abs(data['low'] - data['close'].shift())
            data['tr'] = data[['tr0', 'tr1', 'tr2']].max(axis=1)
            data['up_move'] = data['high'] - data['high'].shift()
            data['down_move'] = data['low'].shift() - data['low']
            data['plus_dm'] = np.where(
                (data['up_move'] > data['down_move']) & (data['up_move'] > 0), 
                data['up_move'], 0
            )
            data['minus_dm'] = np.where(
                (data['down_move'] > data['up_move']) & (data['down_move'] > 0), 
                data['down_move'], 0
            )
            adx_window = 14
            tr_smooth = data['tr'].rolling(window=adx_window).mean()
            data['plus_di'] = 100 * (data['plus_dm'].rolling(window=adx_window).mean() / tr_smooth)
            data['minus_di'] = 100 * (data['minus_dm'].rolling(window=adx_window).mean() / tr_smooth)
            
            data['dx'] = 100 * abs(data['plus_di'] - data['minus_di']) / (data['plus_di'] + data['minus_di'])
            data['adx'] = data['dx'].rolling(window=adx_window).mean()
            
            strong_trend = data['adx'] > self.adx_threshold
            cond_long &= strong_trend
            cond_short &= strong_trend

        if self.allow_short:
            data['signal'] = np.select([cond_long, cond_short], [1, -1], default=0)
        else:
            data['signal'] = np.select([cond_long, cond_short], [1, 0], default=0)
        
        return data

class RSI2Strategy(Strategy):
    def __init__(
        self, rsi_window=2, sma_filter=200, exit_sma=5, 
        rsi_long_threshold=10, rsi_short_threshold=90, sl_atr=None
    ):
        self.rsi_window = rsi_window
        self.sma_filter = sma_filter # Trend Filter (200 SMA)
        self.exit_sma = exit_sma # Mean Reversion Target
        self.rsi_long_threshold = rsi_long_threshold
        self.rsi_short_threshold = rsi_short_threshold
        self.sl_atr = sl_atr

    def generate_signals(self, df):
        data = df.copy()
        
        # Indicators
        # SMA 200 (Trend Filter)
        if self.sma_filter:
            data['trend_ma'] = data['close'].rolling(window=self.sma_filter).mean()
            
        # SMA 5 (Exit/Target)
        data['exit_ma'] = data['close'].rolling(window=self.exit_sma).mean()
        
        # RSI 2
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_window).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # ATR (for SL)
        if self.sl_atr:
            data['tr0'] = abs(data['high'] - data['low'])
            data['tr1'] = abs(data['high'] - data['close'].shift())
            data['tr2'] = abs(data['low'] - data['close'].shift())
            data['atr'] = data[['tr0', 'tr1', 'tr2']].max(axis=1).rolling(window=14).mean()

        data['signal'] = 0
        
        # --- Logic ---
        # 1. Long Entry: Price < ExitSMA AND RSI < 10
        # Optional: Close > TrendMA (Buy only in uptrend)
        long_condition = (data['close'] < data['exit_ma']) & (data['rsi'] < self.rsi_long_threshold)
        if self.sma_filter:
            long_condition &= (data['close'] > data['trend_ma'])
            
        # 2. Short Entry: Price > ExitSMA AND RSI > 90
        # Optional: Close < TrendMA (Sell only in downtrend)
        short_condition = (data['close'] > data['exit_ma']) & (data['rsi'] > self.rsi_short_threshold)
        if self.sma_filter:
            short_condition &= (data['close'] < data['trend_ma'])
            
        # 3. Exit Logic
        # Long Exit: Price > ExitSMA
        # Short Exit: Price < ExitSMA
        
        # Data preparation for fast loop
        closes = data['close'].values
        highs = data['high'].values
        lows = data['low'].values
        exit_mas = data['exit_ma'].values
        atrs = data['atr'].values if self.sl_atr else None
        
        long_conds = long_condition.values
        short_conds = short_condition.values
        
        signals = np.zeros(len(data), dtype=int)
        
        # Fast Loop
        position = 0
        entry_price = 0.0
        
        start_idx = max(self.sma_filter or 0, 20)
        
        for i in range(start_idx, len(data)):
            price = closes[i]
            exit_ma = exit_mas[i]
            
            # Manage Position
            if position == 1:
                # Exit Long
                exit_signal = False
                
                # Standard Exit
                if price > exit_ma:
                    exit_signal = True
                
                # Stop Loss
                if self.sl_atr:
                    atr = atrs[i]
                    if lows[i] < (entry_price - atr * self.sl_atr):
                        exit_signal = True
                        
                if exit_signal:
                    signals[i] = 0
                    position = 0
                    
            elif position == -1:
                # Exit Short
                exit_signal = False
                
                # Standard Exit
                if price < exit_ma:
                    exit_signal = True
                    
                # Stop Loss
                if self.sl_atr:
                    atr = atrs[i]
                    if highs[i] > (entry_price + atr * self.sl_atr):
                        exit_signal = True
                        
                if exit_signal:
                    signals[i] = 0
                    position = 0
            
            # Entry Logic
            if position == 0:
                if long_conds[i]:
                    signals[i] = 1
                    position = 1
                    entry_price = price
                elif short_conds[i]:
                    signals[i] = -1
                    position = -1
                    entry_price = price
                    
        data['signal'] = signals
        return data

class BollingerBreakoutStrategy(Strategy):
    def __init__(self, window=20, std_dev=2.0, keltner_mult=1.5, allow_short=False):
        self.window = window
        self.std_dev = std_dev
        self.keltner_mult = keltner_mult
        self.allow_short = allow_short

    def generate_signals(self, df):
        data = df.copy()
        
        # 1. Bollinger Bands
        data['ma'] = data['close'].rolling(window=self.window).mean()
        data['std'] = data['close'].rolling(window=self.window).std()
        data['upper_bb'] = data['ma'] + (data['std'] * self.std_dev)
        data['lower_bb'] = data['ma'] - (data['std'] * self.std_dev)
        
        # 2. Keltner Channels (for Squeeze detection)
        # KC = MA +/- (ATR * Multiplier)
        data['tr0'] = abs(data['high'] - data['low'])
        data['tr1'] = abs(data['high'] - data['close'].shift())
        data['tr2'] = abs(data['low'] - data['close'].shift())
        data['atr'] = data[['tr0', 'tr1', 'tr2']].max(axis=1).rolling(window=self.window).mean()
        
        data['upper_kc'] = data['ma'] + (data['atr'] * self.keltner_mult)
        data['lower_kc'] = data['ma'] - (data['atr'] * self.keltner_mult)
        
        # 3. Squeeze Indicator
        # Squeeze is ON when BB is INSIDE KC
        data['squeeze_on'] = (data['upper_bb'] < data['upper_kc']) & (data['lower_bb'] > data['lower_kc'])
        
        # 4. Signals
        data['signal'] = 0
        
        # Vectorized Signal Logic
        # Entry: Squeeze was ON recently? 
        # Strict version: Squeeze ON NOW.
        # Or: Squeeze ON within last X bars + Breakout.
        # Let's keep it simple: Breakout occurs while Squeeze is ON (or just ending).
        
        closes = data['close'].values
        upper_bb = data['upper_bb'].values
        lower_bb = data['lower_bb'].values
        ma = data['ma'].values
        squeeze = data['squeeze_on'].values
        
        signals = np.zeros(len(data), dtype=int)
        position = 0
        
        for i in range(self.window, len(data)):
             # Entry Logic
             if position == 0:
                 is_squeeze = squeeze[i] # or squeeze[i-1]
                 
                 # Long Breakout
                 if is_squeeze and closes[i] > upper_bb[i]:
                     signals[i] = 1
                     position = 1
                     
                 # Short Breakout
                 elif self.allow_short and is_squeeze and closes[i] < lower_bb[i]:
                     signals[i] = -1
                     position = -1
            
             # Exit Logic (Reversion to Mean)
             elif position == 1:
                 # Exit if price crosses below MA (or touches it? usually cross)
                 if closes[i] < ma[i]:
                     signals[i] = 0 # Exit
                     position = 0
                     
             elif position == -1:
                 # Exit if price crosses above MA
                 if closes[i] > ma[i]:
                     signals[i] = 0 # Exit
                     position = 0
                     
        data['signal'] = signals
        return data

class SuperTrendStrategy(Strategy):
    def __init__(self, atr_window=10, multiplier=3.0, allow_short=False):
        self.atr_window = atr_window
        self.multiplier = multiplier
        self.allow_short = allow_short

    def generate_signals(self, df):
        data = df.copy()
        
        # ATR Calculation
        data['tr0'] = abs(data['high'] - data['low'])
        data['tr1'] = abs(data['high'] - data['close'].shift())
        data['tr2'] = abs(data['low'] - data['close'].shift())
        data['tr'] = data[['tr0', 'tr1', 'tr2']].max(axis=1)
        data['atr'] = data['tr'].rolling(window=self.atr_window).mean()
        
        # HL2
        data['hl2'] = (data['high'] + data['low']) / 2
        
        # Basic Bands
        data['basic_upper'] = data['hl2'] + (self.multiplier * data['atr'])
        data['basic_lower'] = data['hl2'] - (self.multiplier * data['atr'])
        
        # Final Bands & Trend (Loop required for state dependency)
        # Using numpy arrays for speed
        closes = data['close'].values
        basic_upper = data['basic_upper'].values
        basic_lower = data['basic_lower'].values
        
        final_upper = np.zeros(len(data))
        final_lower = np.zeros(len(data))
        trend = np.zeros(len(data), dtype=int) # 1: Long, -1: Short
        
        n = len(data)
        
        # Initialize
        # Start from atr_window
        start_idx = self.atr_window
        
        # Determine first valid values
        # We need check if data is long enough
        if len(data) > start_idx:
            final_upper[start_idx-1] = basic_upper[start_idx-1]
            final_lower[start_idx-1] = basic_lower[start_idx-1]
            trend[start_idx-1] = 1 
            
            for i in range(start_idx, n):
                # Final Upper
                if basic_upper[i] < final_upper[i-1] or closes[i-1] > final_upper[i-1]:
                    final_upper[i] = basic_upper[i]
                else:
                    final_upper[i] = final_upper[i-1]
                    
                # Final Lower
                if basic_lower[i] > final_lower[i-1] or closes[i-1] < final_lower[i-1]:
                    final_lower[i] = basic_lower[i]
                else:
                    final_lower[i] = final_lower[i-1]
                    
                # Trend Direction
                prev_trend = trend[i-1]
                
                if prev_trend == 1:
                    # In Uptrend. Check for Reversal.
                    if closes[i] < final_lower[i]:
                        trend[i] = -1 # Switch to Downtrend
                    else:
                        trend[i] = 1
                else:
                    # In Downtrend. Check for Reversal.
                    if closes[i] > final_upper[i]:
                        trend[i] = 1 # Switch to Uptrend
                    else:
                        trend[i] = -1
                    
        data['supertrend'] = np.where(trend==1, final_lower, final_upper)
        data['trend'] = trend
        
        # Signal Generation
        signals = np.zeros(len(data), dtype=int)
        
        if self.allow_short:
             signals = trend
        else:
             # Long Only: 1 (Buy), 0 (Exit)
             signals = np.where(trend == 1, 1, 0)
        
        # Ensure signals before start_idx are 0
        signals[:start_idx] = 0
             
        data['signal'] = signals
        return data
