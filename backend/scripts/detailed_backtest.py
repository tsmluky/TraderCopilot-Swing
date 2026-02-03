
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt # Optional, but good for calc
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from strategies.DonchianBreakoutV2 import DonchianBreakoutV2
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
    """
    Calc Max Drawdown from equity curve (list of cumulative R).
    Returns Max DD (in R) and Max DD %.
    """
    if not equity_curve: return 0.0
    
    peak = -99999
    max_dd = 0
    
    for value in equity_curve:
        if value > peak:
            peak = value
        dd = peak - value
        if dd > max_dd:
            max_dd = dd
            
    return max_dd


def logger(msg):
    print(msg)
    with open("backtest_results.txt", "a") as f:
        f.write(msg + "\n")

def run_detailed_simulation(name, strategy, df):
    logger(f"\n--- ANALYZING: {name} ---")
    signals = strategy.find_historical_signals("BTC", df, "4h")
    
    if not signals:
        logger("No signals generated.")
        return

    # Sort signals by time
    signals.sort(key=lambda x: x.timestamp)

    # Pre-index
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
        
        # Calculate Planned RR
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        rr_ratio = reward / risk if risk > 0 else 0
        
        result = "OPEN"
        pnl_r = 0.0
        
        # Simulation loop
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
            else: # short
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

    # Metrics
    total_trades = len(trades)
    wins = len([t for t in trades if t > 0])
    losses = total_trades - wins
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    total_r = sum(trades)
    avg_r = total_r / total_trades if total_trades > 0 else 0
    max_dd = calculate_max_drawdown(equity)
    
    # Implied RR (Average Winner / Average Loser)
    avg_win = sum([t for t in trades if t > 0]) / wins if wins > 0 else 0
    avg_loss = sum([abs(t) for t in trades if t < 0]) / losses if losses > 0 else 0
    realized_rr_val = avg_win / avg_loss if avg_loss > 0 else 0
    profit_factor = sum([t for t in trades if t > 0]) / sum([abs(t) for t in trades if t < 0]) if losses > 0 else 999

    logger(f"Trades Executed:  {total_trades}")
    logger(f"Win Rate:         {win_rate:.2f}%")
    logger(f"Realized RR:      1:{realized_rr_val:.2f} (Avg Win / Avg Loss)")
    logger(f"Total Return:     {total_r:.2f} R")
    logger(f"Max Drawdown:     {max_dd:.2f} R")
    logger(f"Profit Factor:    {profit_factor:.2f}")

def main():
    # Clear file
    with open("backtest_results.txt", "w") as f:
        f.write("BACKTEST REPORT\n")
        
    logger("Loading Data...")
    df = load_data("BTC", "4h")
    if df is None: return

    # 1. Donchian "Premium"
    # D=20, TP=3.0, SL=1.2
    donchian = DonchianBreakoutV2(
        donchian_period=20,
        tp_atr=3.0,
        sl_atr=1.2,
        ema_period=200
    )
    run_detailed_simulation("Donchian Breakout (TP 3.0)", donchian, df)

    # 2. Trend Following "Turbo"
    # EMA 9/21, TP=8.0, SL=1.5
    trend = TrendFollowingNative(
        ema_fast=9,
        ema_slow=21,
        tp_atr=8.0,
        sl_atr=1.5,
        min_adx=20
    )
    run_detailed_simulation("Trend Following Turbo (TP 8.0)", trend, df)


if __name__ == "__main__":
    main()
