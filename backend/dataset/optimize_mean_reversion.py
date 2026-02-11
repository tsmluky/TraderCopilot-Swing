
import pandas as pd
import numpy as np
import os
from datetime import datetime

# Configuration
DATA_DIR = r"c:\Users\lukx\Desktop\TraderCopilot-Swing\backend\dataset\data"
TOKENS = ["BTC", "ETH"]
TF = "1h"


# Grid Search Parameters
RSI_PARAMS = [
    (30, 70), (35, 65), (40, 60) # Test tighter RSI for low vol
]
BB_PARAMS = [1.5, 1.8, 2.0, 2.2] # Test tighter bands for "heavy" assets
TREND_FILTER_PARAMS = [True] # Keep Trend Filter ON as it was proven good

def load_data(token):
    path = os.path.join(DATA_DIR, f"{token}_USDT_{TF}.csv")
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return None
    df = pd.read_csv(path)
    # Ensure numeric
    cols = ['open', 'high', 'low', 'close', 'volume']
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna()
    return df.reset_index(drop=True)

def calculate_indicators(df, bb_period=20, bb_std=2.0, rsi_period=14):
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # BB
    df['sma'] = df['close'].rolling(window=bb_period).mean()
    df['std'] = df['close'].rolling(window=bb_period).std()
    df['upper'] = df['sma'] + (bb_std * df['std'])
    df['lower'] = df['sma'] - (bb_std * df['std'])
    
    # Trend Filter
    df['trend_sma'] = df['close'].rolling(window=200).mean()
    
    return df

def backtest(df, rsi_lower, rsi_upper, bb_std, use_trend_filter=False):
    balance = 1000.0
    position = 0
    entry_price = 0.0
    trades = []
    
    closes = df['close'].values
    uppers = df['upper'].values
    lowers = df['lower'].values
    smas = df['sma'].values
    rsis = df['rsi'].values
    trend_smas = df['trend_sma'].values
    
    # Start after warmups
    start_idx = 200 
    
    for i in range(start_idx, len(df)):
        price = closes[i]
        
        # Exits
        if position == 1:
            if price > smas[i]: 
                pnl = (price - entry_price) / entry_price
                balance *= (1 + pnl)
                trades.append(pnl)
                position = 0
        elif position == -1:
            if price < smas[i]:
                pnl = (entry_price - price) / entry_price
                balance *= (1 + pnl)
                trades.append(pnl)
                position = 0
                
        # Entries
        if position == 0:
            trend_bull = True
            trend_bear = True
            
            if use_trend_filter:
                # Long only if Price > TrendSMA (Buy Dips)
                trend_bull = price > trend_smas[i]
                # Short only if Price < TrendSMA (Sell Rallies)
                trend_bear = price < trend_smas[i]
            
            # Long
            if price < lowers[i] and rsis[i] < rsi_lower and trend_bull:
                position = 1
                entry_price = price
            # Short
            elif price > uppers[i] and rsis[i] > rsi_upper and trend_bear:
                position = -1
                entry_price = price
                
    return balance, len(trades), np.mean(trades) if trades else 0

def run_optimization():
    print(f"Starting RECALIBRATION for {TOKENS}...")
    
    results = []
    
    for token in TOKENS:
        df = load_data(token)
        if df is None: continue
        
        print(f"\nAnalyzing {token} ({len(df)} candles)...")
        best_ret = -999
        best_config = None
        
        for rsi_low, rsi_high in RSI_PARAMS:
            for bb_std in BB_PARAMS:
                for use_filter in TREND_FILTER_PARAMS:
                    
                    temp_df = calculate_indicators(df.copy(), bb_std=bb_std)
                    
                    final_bal, trade_count, avg_pnl = backtest(temp_df, rsi_low, rsi_high, bb_std, use_filter)
                    ret_pct = (final_bal - 1000) / 10
                    
                    if trade_count > 15: 
                        results.append({
                            "token": token,
                            "rsi": f"{rsi_low}/{rsi_high}",
                            "bb_std": bb_std,
                            "trend_filter": use_filter,
                            "return": ret_pct,
                            "trades": trade_count
                        })
                        
                        if ret_pct > best_ret:
                            best_ret = ret_pct
                            best_config = (rsi_low, rsi_high, bb_std, use_filter)
        
        if best_config:
            filter_txt = "ON" if best_config[3] else "OFF"
            print(f" -> BEST {token}: Filter={filter_txt}, RSI {best_config[0]}/{best_config[1]}, BB {best_config[2]} => Return: {best_ret:.2f}%")

    print("\n--- NEW OPTIMIZED CONFIG ---")
    final_df = pd.DataFrame(results)
    final_df = final_df.sort_values(by=["token", "return"], ascending=[True, False])
    print(final_df.groupby("token").head(1).to_string())


if __name__ == "__main__":
    run_optimization()
