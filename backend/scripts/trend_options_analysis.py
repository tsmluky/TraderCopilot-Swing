
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from strategies.TrendFollowingNative import TrendFollowingNative

DATA_PATH = r"C:\Users\lukx\Desktop\velasccxt"

def load_data(token="BTC", tf="4h"):
    path = os.path.join(DATA_PATH, f"{token}_{tf}.csv")
    if not os.path.exists(path): return None
    df = pd.read_csv(path)
    if 'timestamp' in df.columns:
        if df['timestamp'].iloc[0] > 1e11:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        else:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    return df

def calculate_max_drawdown(equity_curve):
    if not equity_curve: return 0.0
    peak = -99999
    max_dd = 0
    for value in equity_curve:
        if value > peak: peak = value
        dd = peak - value
        if dd > max_dd: max_dd = dd
    return max_dd

def logger(msg):
    print(msg)
    with open("trend_options.txt", "a") as f:
        f.write(msg + "\n")

def run_simulation(name, strategy, df):
    logger(f"\n>>> OPTION: {name}")
    signals = strategy.find_historical_signals("BTC", df, "4h")
    
    if not signals:
        logger("No signals.")
        return

    df = df.sort_values('timestamp').reset_index(drop=True)
    time_map = {t: i for i, t in enumerate(df['timestamp'])}
    
    trades = []
    equity = [0]
    cumulative = 0
    
    for sig in signals:
        start_idx = time_map.get(sig.timestamp)
        if start_idx is None: continue
        
        entry = sig.entry
        tp = sig.tp
        sl = sig.sl
        direction = sig.direction
        
        # RR Calc
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        rr_ratio = reward / risk if risk > 0 else 0
        
        result = "OPEN"
        pnl_r = 0.0
        
        for i in range(start_idx + 1, min(len(df), start_idx + 1000)):
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

    # Stats
    total = len(trades)
    if total == 0: return
    
    wins = len([t for t in trades if t > 0])
    losses = total - wins
    win_rate = (wins / total * 100)
    total_r = sum(trades)
    max_dd = calculate_max_drawdown(equity)
    
    avg_win = sum([t for t in trades if t > 0]) / wins if wins > 0 else 0
    avg_loss = sum([abs(t) for t in trades if t < 0]) / losses if losses > 0 else 0
    # profit_factor = sum([t for t in trades if t > 0]) / sum([abs(t) for t in trades if t < 0]) if losses > 0 else 999 

    logger(f"Trades: {total} | WR: {win_rate:.1f}%")
    logger(f"Return: {total_r:.2f} R")
    logger(f"Max DD: {max_dd:.2f} R")
    # logger(f"Avg Win: {avg_win:.2f} R | Avg Loss: {avg_loss:.2f} R")

def main():
    with open("trend_options.txt", "w") as f:
        f.write("TREND FOLLOWING OPTIONS REPORT\n")
        
    df = load_data("BTC", "4h")
    if df is None: return

    # Option 1: TURBO (The Aggressive Baseline)
    # EMA 9/21, TP 8.0, SL 1.5
    s1 = TrendFollowingNative(ema_fast=9, ema_slow=21, tp_atr=8.0, sl_atr=1.5, min_adx=20)
    run_simulation("1. TURBO (High Risk/High Reward)", s1, df)

    # Option 2: BALANCED (The Recommendation)
    # EMA 9/21, TP 5.0, SL 1.5
    s2 = TrendFollowingNative(ema_fast=9, ema_slow=21, tp_atr=5.0, sl_atr=1.5, min_adx=20)
    run_simulation("2. BALANCED (Sustainable Growth)", s2, df)

    # Option 3: STEADY (Classic Trend)
    # EMA 20/50, TP 4.0, SL 1.3
    # Slower entry, but looking for solid moves
    s3 = TrendFollowingNative(ema_fast=20, ema_slow=50, tp_atr=4.0, sl_atr=1.3, min_adx=25) # Slightly higher ADX for quality
    run_simulation("3. STEADY (Classic Approach)", s3, df)

if __name__ == "__main__":
    main()
