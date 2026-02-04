
import os
import sys
import pandas as pd

import glob

# Fix path to import core backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from strategies.DonchianBreakoutV2 import DonchianBreakoutV2
from strategies.TrendFollowingNative import TrendFollowingNative

DATA_PATH = r"C:\Users\lukx\Desktop\velasccxt"

def load_all_data(tf="4h"):
    datasets = {}
    # Look for all _4h.csv files
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

def calculate_max_drawdown(equity_curve):
    if not equity_curve:
        return 0.0
    peak = -99999
    max_dd = 0
    for value in equity_curve:
        if value > peak:
            peak = value
        dd = peak - value
        if dd > max_dd:
            max_dd = dd
    return max_dd

def simulate_trades(signals, df):
    if not signals:
        return 0, 0, 0, 0
    
    df = df.sort_values('timestamp').reset_index(drop=True)
    time_map = {t: i for i, t in enumerate(df['timestamp'])}
    
    trades = []
    equity = [0]
    cumulative = 0
    
    for sig in signals:
        start_idx = time_map.get(sig.timestamp)
        if start_idx is None:
            continue
        
        entry = sig.entry
        tp = sig.tp
        sl = sig.sl
        direction = sig.direction
        
        # RR Calc (Approx based on TP/SL distance)
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        rr_ratio = reward / risk if risk > 0 else 0
        
        result = "OPEN"
        pnl_r = 0.0
        
        for i in range(start_idx + 1, min(len(df), start_idx + 2000)): # Allow long holds for Trend
            row = df.iloc[i]
            if direction == 'long':
                if row['high'] >= tp:
                    pnl_r = rr_ratio
                    result = "WIN"
                    break
                if row['low'] <= sl:
                    pnl_r = -1.0
                    result = "LOSS"
                    break
            else: 
                if row['low'] <= tp:
                    pnl_r = rr_ratio
                    result = "WIN"
                    break
                if row['high'] >= sl:
                    pnl_r = -1.0
                    result = "LOSS"
                    break
        
        if result != "OPEN":
            trades.append(pnl_r)
            cumulative += pnl_r
            equity.append(cumulative)

    total_r = sum(trades)
    max_dd = calculate_max_drawdown(equity)
    count = len(trades)
    wins = len([t for t in trades if t > 0])
    wr = (wins / count * 100) if count > 0 else 0
    
    return total_r, max_dd, count, wr

def logger(msg):
    print(msg)
    with open("multi_asset_results.txt", "a") as f:
        f.write(msg + "\n")

def run_validation():
    with open("multi_asset_results.txt", "w") as f:
        f.write("MULTI-ASSET VALIDATION REPORT\n\n")
        
    print("Loading datasets...")
    datasets = load_all_data("4h")
    tokens = list(datasets.keys())
    print(f"Loaded: {tokens}")
    
    # 1. Trend "STEADY" Config
    # EMA 20/50, TP 4.0, SL 1.3
    trend_config = TrendFollowingNative(ema_fast=20, ema_slow=50, tp_atr=4.0, sl_atr=1.3, min_adx=25)
    
    logger("\n>>> STRATEGY: Trend Following 'STEADY' (EMA 20/50, TP 4.0)")
    
    agg_r = 0
    agg_dd = 0
    
    for token, df in datasets.items():
        sigs = trend_config.find_historical_signals(token, df, "4h")
        r, dd, count, wr = simulate_trades(sigs, df)
        logger(f"[{token}] R: {r:.2f} | DD: {dd:.2f} | Tx: {count} | WR: {wr:.1f}%")
        agg_r += r
        agg_dd = max(agg_dd, dd) # Taking worst case DD roughly
        
    logger(f"TOTAL PORTFOLIO RETURN: {agg_r:.2f} R")

    
    # 2. Donchian "TITAN" Config
    # D=20, TP 3.0, SL 1.2
    donchian_config = DonchianBreakoutV2(donchian_period=20, tp_atr=3.0, sl_atr=1.2)
    
    logger("\n>>> STRATEGY: Donchian 'TITAN' (TP 3.0, SL 1.2)")
    
    agg_r = 0
    agg_dd = 0
    
    for token, df in datasets.items():
        sigs = donchian_config.find_historical_signals(token, df, "4h")
        r, dd, count, wr = simulate_trades(sigs, df)
        logger(f"[{token}] R: {r:.2f} | DD: {dd:.2f} | Tx: {count} | WR: {wr:.1f}%")
        agg_r += r
    
    logger(f"TOTAL PORTFOLIO RETURN: {agg_r:.2f} R")

if __name__ == "__main__":
    run_validation()
