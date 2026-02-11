import numpy as np

class Strategy:
    """Base Class for all Strategies"""
    def generate_signals(self, df):
        raise NotImplementedError("Should implement generate_signals method")

class DonchianStrategy(Strategy):
    """
    Strategy 1: Donchian Breakout (Trend Following)
    - Captures 100% of major trends.
    - Logic: Buy > Upper Channel (20), Sell < Lower Channel (20).
    - Best for: BNB, ETH.
    """
    def __init__(self, window=20, allow_short=False):
        self.window = window
        self.allow_short = allow_short

    def generate_signals(self, df):
        data = df.copy()
        
        # Donchian Channels
        data['upper'] = data['high'].rolling(window=self.window).max().shift(1)
        data['lower'] = data['low'].rolling(window=self.window).min().shift(1)
        
        data['signal'] = 0
        
        # Long Logic
        long_condition = data['close'] > data['upper']
        short_condition = data['close'] < data['lower']
        
        # Vectorized Signal Generation
        # 1 = Long, 0 = Exit
        data.loc[long_condition, 'signal'] = 1
        
        if self.allow_short:
            data.loc[short_condition, 'signal'] = -1
        else:
            data.loc[short_condition, 'signal'] = 0
            
        return data

class SMACrossoverStrategy(Strategy):
    """
    Strategy 2: SMA/EMA Crossover (Trend Following)
    - Captures established trends with less false breakouts than Donchian.
    - Logic: Golden Cross (Fast > Slow).
    - Best for: BTC, SOL.
    """
    def __init__(self, fast_window=50, slow_window=200, use_ema=False, allow_short=False):
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.use_ema = use_ema
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
        
        if self.allow_short:
            data['signal'] = np.select([cond_long, cond_short], [1, -1], default=0)
        else:
            data['signal'] = np.select([cond_long, cond_short], [1, 0], default=0)
        
        return data

class SuperTrendStrategy(Strategy):
    """
    Strategy 3: SuperTrend (Volatility Trailing)
    - Dynamic trailing stop based on ATR.
    - Logic: Close > Trend Line.
    - Best for: SOL (High Volatility), BNB.
    """
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
        data['atr'] = data[['tr0', 'tr1', 'tr2']].max(axis=1).rolling(window=self.atr_window).mean()
        
        # HL2
        data['hl2'] = (data['high'] + data['low']) / 2
        
        # Basic Bands
        data['basic_upper'] = data['hl2'] + (self.multiplier * data['atr'])
        data['basic_lower'] = data['hl2'] - (self.multiplier * data['atr'])
        
        # Final Bands & Trend Loop
        closes = data['close'].values
        basic_upper = data['basic_upper'].values
        basic_lower = data['basic_lower'].values
        
        final_upper = np.zeros(len(data))
        final_lower = np.zeros(len(data))
        trend = np.zeros(len(data), dtype=int)
        
        n = len(data)
        start_idx = self.atr_window
        
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
                if trend[i-1] == 1:
                    if closes[i] < final_lower[i]:
                        trend[i] = -1
                    else:
                        trend[i] = 1
                else:
                    if closes[i] > final_upper[i]:
                        trend[i] = 1
                    else:
                        trend[i] = -1
        
        # Signal Generation
        if self.allow_short:
             signals = trend
        else:
             signals = np.where(trend == 1, 1, 0)
        
        signals[:start_idx] = 0
        data['signal'] = signals
        return data
