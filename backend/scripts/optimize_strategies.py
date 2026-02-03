
import os
import sys
import pandas as pd
import numpy as np
from itertools import product
from datetime import datetime

# Fix path to import core backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from strategies.DonchianBreakoutV2 import DonchianBreakoutV2
from strategies.TrendFollowingNative import TrendFollowingNative

DATA_PATH = r"C:\Users\lukx\Desktop\velasccxt"

def load_data(token="BTC", tf="4h"):
    path = os.path.join(DATA_PATH, f"{token}_{tf}.csv")
    if not os.path.exists(path):
        print(f"Data not found: {path}")
        return None
    df = pd.read_csv(path)
    if 'timestamp' in df.columns:
        if df['timestamp'].iloc[0] > 1e11:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        else:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    return df

def simulate_trades(signals, df):
    if not signals:
        return 0, 0, 0
    
    # Pre-index DF
    df = df.sort_values('timestamp').reset_index(drop=True)
    time_map = {t: i for i, t in enumerate(df['timestamp'])}
    
    trades = []
    
    for sig in signals:
        start_idx = time_map.get(sig.timestamp)
        if start_idx is None: continue
        
        entry = sig.entry
        tp = sig.tp
        sl = sig.sl
        direction = sig.direction
        
        result = "OPEN"
        pnl_r = 0.0
        
        # Fast forward simulation
        # Limit max hold to 100 candles to speed up? No, let it run.
        # But for optimization speed, we assume result is hit eventually or check high/low arrays
        
        # Optimization: Slicing is faster than iterating rows
        future = df.iloc[start_idx+1:]
        if future.empty: continue
        
        # Vectorized check attempt (simplified for robustness)
        # Iterating is slow for Grid Search, but robust for logic. 
        # For this script, we'll iterate but break fast.
        
        for i in range(start_idx + 1, min(len(df), start_idx + 500)): # Cap holding period to avoid infinite loops in bad logic
            row = df.iloc[i]
            if direction == 'long':
                if row['high'] >= tp:
                    pnl_r = (tp - entry) / (entry - sl)
                    trades.append(pnl_r)
                    break
                if row['low'] <= sl:
                    trades.append(-1.0)
                    break
            else:
                if row['low'] <= tp:
                    pnl_r = (entry - tp) / (sl - entry)
                    trades.append(pnl_r)
                    break
                if row['high'] >= sl:
                    trades.append(-1.0)
                    break
    
    if not trades:
        return 0, 0, 0
        
    total_r = sum(trades)
    count = len(trades)
    win_rate = len([t for t in trades if t > 0]) / count
    return total_r, count, win_rate

def run_grid_search():
    print("Loading BTC 4H Data...")
    df = load_data("BTC", "4h")
    if df is None: return

    # --- DONCHIAN OPTIMIZATION ---
    print("\n>>> OPTIMIZING DONCHIAN BREAKOUT <<<")
    # Parameters to test
    donchian_periods = [20, 50] # Short vs Medium term
    tp_multipliers = [2.0, 3.0, 4.0, 5.0, 6.0]
    sl_multipliers = [1.0, 1.2, 1.5]
    
    best_r = -9999
    best_config = {}
    
    # Grid Search
    for d_per, tp, sl in product(donchian_periods, tp_multipliers, sl_multipliers):
        # Initialize strategy with config
        strat = DonchianBreakoutV2(
            donchian_period=d_per,
            tp_atr=tp,
            sl_atr=sl,
            ema_period=200 # Keep trend filter constant for now
        )
        
        # Run Backtest
        sigs = strat.find_historical_signals("BTC", df, "4h")
        r, count, wr = simulate_trades(sigs, df)
        
        print(f"Conf: D={d_per} TP={tp} SL={sl} -> R={r:.1f} (Tx={count}, WR={wr:.2%})")
        
        if r > best_r:
            best_r = r
            best_config = {"d": d_per, "tp": tp, "sl": sl, "count": count, "wr": wr}

    print(f"\n🏆 BEST DONCHIAN: {best_config} -> {best_r:.2f} R")


    # --- TREND FOLLOWING OPTIMIZATION ---
    print("\n>>> OPTIMIZING TREND FOLLOWING <<<")
    tp_multipliers = [3.0, 5.0, 8.0, 10.0]
    sl_multipliers = [1.0, 1.5, 2.0]
    ema_pairs = [(20, 50), (9, 21)] # Standard vs Fast
    
    best_r = -9999
    best_config = {}
    
    for (fast, slow), tp, sl in product(ema_pairs, tp_multipliers, sl_multipliers):
        strat = TrendFollowingNative(
            ema_fast=fast,
            ema_slow=slow,
            tp_atr=tp,
            sl_atr=sl,
            min_adx=20
        )
        
        sigs = strat.find_historical_signals("BTC", df, "4h")
        r, count, wr = simulate_trades(sigs, df)
        
        print(f"Conf: EMA={fast}/{slow} TP={tp} SL={sl} -> R={r:.1f} (Tx={count}, WR={wr:.2%})")
        
        if r > best_r:
            best_r = r
            best_config = {"ema": f"{fast}/{slow}", "tp": tp, "sl": sl, "count": count, "wr": wr}

    print(f"\n🏆 BEST TREND: {best_config} -> {best_r:.2f} R")

if __name__ == "__main__":
    run_grid_search()
