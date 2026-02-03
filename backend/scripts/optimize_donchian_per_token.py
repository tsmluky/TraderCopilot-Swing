
import os
import sys
import pandas as pd
import numpy as np
import glob
from itertools import product

# Fix path to import core backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from strategies.DonchianBreakoutV2 import DonchianBreakoutV2

DATA_PATH = r"C:\Users\lukx\Desktop\velasccxt"

def load_all_data(tf="4h"):
    datasets = {}
    pattern = os.path.join(DATA_PATH, f"*_{tf}.csv")
    files = glob.glob(pattern)
    
    for f in files:
        token = os.path.basename(f).split('_')[0]
        try:
            df = pd.read_csv(f)
            if 'timestamp' in df.columns:
                if df['timestamp'].iloc[0] > 1e11:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                else:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            datasets[token] = df
        except Exception as e:
            print(f"Error loading {token}: {e}")
            
    return datasets

def simulate_trades(signals, df):
    if not signals: return 0.0, 0, 0, 0.0
    
    df = df.sort_values('timestamp').reset_index(drop=True)
    time_map = {t: i for i, t in enumerate(df['timestamp'])}
    
    # Optimization: pre-calc high/low arrays
    high_arr = df['high'].values
    low_arr = df['low'].values
    
    trades = []
    
    for sig in signals:
        start_idx = time_map.get(sig.timestamp)
        if start_idx is None: continue
        
        entry = sig.entry
        tp = sig.tp
        sl = sig.sl
        direction = sig.direction
        
        if entry == sl: continue # Avoid div by zero

        rr_ratio = abs(tp - entry) / abs(entry - sl)
        
        pnl_r = 0.0
        result = "OPEN"
        
        # Max hold 1000 candles
        end_idx = min(len(df), start_idx + 1000)
        
        # Simple loop is safer than vectorization for logic with break
        for i in range(start_idx + 1, end_idx):
            h = high_arr[i]
            l = low_arr[i]
            
            if direction == 'long':
                if h >= tp:
                    pnl_r = rr_ratio
                    result = "WIN"
                    break
                if l <= sl:
                    pnl_r = -1.0
                    result = "LOSS"
                    break
            else:
                if l <= tp:
                    pnl_r = rr_ratio
                    result = "WIN"
                    break
                if h >= sl:
                    pnl_r = -1.0
                    result = "LOSS"
                    break
                    
        if result != "OPEN":
            trades.append(pnl_r)

    if not trades: return 0.0, 0, 0, 0.0
    
    total_r = sum(trades)
    count = len(trades)
    wins = len([t for t in trades if t > 0])
    wr = wins / count
    
    # Calc Max DD approx
    equity = [0]
    agg = 0
    peak = -999
    max_dd = 0
    for t in trades:
        agg += t
        if agg > peak: peak = agg
        dd = peak - agg
        if dd > max_dd: max_dd = dd
        
    return total_r, max_dd, count, wr

def logger(msg):
    print(msg)
    with open("donchian_deep_dive.txt", "a") as f:
        f.write(msg + "\n")

def run_deep_dive():
    with open("donchian_deep_dive.txt", "w") as f:
        f.write("DONCHIAN DEEP DIVE REPORT\n\n")
        
    datasets = load_all_data("4h")
    tokens = sorted(datasets.keys())
    
    # Grid Parameters to Test
    # Periods: Fast (14) vs Standard (20) vs Slow (30)
    # TPs: Agile (2.0) vs Standard (3.0) vs Aggressive (4.0, 5.0)
    # SLs: Tight (1.0) vs Standard (1.2) vs Loose (1.5)
    
    periods = [14, 20, 30]
    tps = [2.0, 3.0, 4.0, 5.0, 6.0]
    sls = [1.0, 1.2, 1.5]
    
    for token in tokens:
        logger(f"\n>>> OPTIMIZING: {token}")
        df = datasets[token]
        
        best_r = -9999
        best_config = {}
        
        # Run Grid
        # Count iterations
        total_iter = len(periods) * len(tps) * len(sls)
        # logger(f"Testing {total_iter} combinations...")
        
        for p, tp, sl in product(periods, tps, sls):
            strat = DonchianBreakoutV2(
                donchian_period=p,
                tp_atr=tp,
                sl_atr=sl,
                ema_period=200 # Standard filter
            )
            
            sigs = strat.find_historical_signals(token, df, "4h")
            r, dd, count, wr = simulate_trades(sigs, df)
            
            # Score Improvement?
            # Metric: Total R. Using DD as tie breaker?
            # Basic validation: ensure minimal trades (>20) to avoid lucky shots
            
            if r > best_r and count >= 20:
                best_r = r
                best_config = {
                    "p": p, "tp": tp, "sl": sl,
                    "r": r, "dd": dd, "wr": wr, "count": count
                }
                # logger(f"  New Best: {best_config}")
        
        # Report Winner vs Baseline (P=20, TP=3.0, SL=1.2)
        baseline = DonchianBreakoutV2(20, 200, 14, 3.0, 1.2)
        sigs_base = baseline.find_historical_signals(token, df, "4h")
        r_b, dd_b, c_b, wr_b = simulate_trades(sigs_base, df)
        
        logger(f"--- RESULTS: {token} ---")
        logger(f"BASELINE (20/3.0/1.2): {r_b:.2f} R (DD: {dd_b:.2f}, WR: {wr_b:.1%})")
        logger(f"OPTIMAL  ({best_config['p']}/{best_config['tp']}/{best_config['sl']})  : {best_config['r']:.2f} R (DD: {best_config['dd']:.2f}, WR: {best_config['wr']:.1%})")
        
        improvement = best_config['r'] - r_b
        if improvement > 5:
            logger(f"[!!!] SIGNIFICANT IMPROVEMENT: +{improvement:.2f} R")
        else:
            logger(f"[OK] Baseline is solid (Delta < 5R)")

if __name__ == "__main__":
    run_deep_dive()
