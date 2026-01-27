
import sys
import os
import pandas as pd
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from strategies.TrendFollowingNative import TrendFollowingNative
from strategies.DonchianBreakoutV2 import DonchianBreakoutV2

LOCAL_DATA_DIR = r"C:\Users\lukx\Desktop\velasccxt"

def fetch_data(token, timeframe):
    filename = f"{token}_{timeframe}.csv"
    csv_path = os.path.join(LOCAL_DATA_DIR, filename)
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    df = pd.read_csv(csv_path)
    if 'timestamp' in df.columns:
        first_ts = float(df['timestamp'].iloc[0])
        unit = 'ms' if first_ts > 10000000000 else 's'
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit=unit)
    return df.sort_values('timestamp').reset_index(drop=True)

def quick_backtest(df, strategy):
    try:
        sigs = strategy.find_historical_signals("DEBUG", df, "1h")
    except Exception as e:
        return 0, 0, 0
    
    wins = 0
    losses = 0
    total_r = 0.0
    
    for sig in sigs:
        entry = sig.entry
        tp = sig.tp
        sl = sig.sl
        match = df[df['timestamp'] == sig.timestamp]
        if match.empty: continue
        start_idx = match.index[0]
        
        outcome = "OPEN"
        raw_r = 0.0
        
        for i in range(start_idx+1, len(df)):
            row = df.iloc[i]
            if sig.direction == 'long':
                if row['low'] <= sl: 
                    outcome = "LOSS"
                    raw_r = -1.0
                    break
                if row['high'] >= tp:
                    outcome = "WIN"
                    if tp == 0: # Trailing or open target?
                         raw_r = (row['close'] - entry) / (entry - sl)
                    else:
                         raw_r = (tp - entry) / (entry - sl)
                    break
            else:
                if row['high'] >= sl:
                    outcome = "LOSS"
                    raw_r = -1.0
                    break
                if row['low'] <= tp:
                    outcome = "WIN"
                    if tp == 0:
                        raw_r = (entry - row['close']) / (sl - entry)
                    else:
                        raw_r = (entry - tp) / (sl - entry)
                    break
        
        if outcome == "WIN": wins += 1
        if outcome == "LOSS": losses += 1
        total_r += raw_r
        
    total = wins + losses
    wr = (wins/total*100) if total > 0 else 0
    return total, wr, total_r

tokens = ["SOL", "BTC"]
timeframe = "1h"

print(f"--- OPTIMIZING TITAN BREAKOUT ---")

# Config 1: Scalper Breakout (Current)
# Period 20, ATR 14
c1 = {"donchian_period": 20, "ema_period": 200, "atr_period": 14}
print(f"\n[Titan 1] Short Term (20): {c1}")
for t in tokens:
    df = fetch_data(t, timeframe)
    t_cnt, wr, r = quick_backtest(df, DonchianBreakoutV2(**c1))
    print(f"   {t}: {t_cnt} trades, WR: {wr:.1f}%, R: {r:.1f}")

# Config 2: Turtle Style (55)
c2 = {"donchian_period": 55, "ema_period": 200, "atr_period": 20}
print(f"\n[Titan 2] Mid Term (55): {c2}")
for t in tokens:
    df = fetch_data(t, timeframe)
    t_cnt, wr, r = quick_backtest(df, DonchianBreakoutV2(**c2))
    print(f"   {t}: {t_cnt} trades, WR: {wr:.1f}%, R: {r:.1f}")

# Config 3: Long Trend (100)
c3 = {"donchian_period": 100, "ema_period": 200, "atr_period": 20}
print(f"\n[Titan 3] Long Term (100): {c3}")
for t in tokens:
    df = fetch_data(t, timeframe)
    t_cnt, wr, r = quick_backtest(df, DonchianBreakoutV2(**c3))
    print(f"   {t}: {t_cnt} trades, WR: {wr:.1f}%, R: {r:.1f}")


print(f"\n--- OPTIMIZING FLOW MASTER ---")

# Config 1: Fast (20/50, ADX 20)
f1 = {"ema_fast": 20, "ema_slow": 50, "min_adx": 20.0}
print(f"\n[Flow 1] Fast (20/50): {f1}")
for t in tokens:
    df = fetch_data(t, timeframe)
    t_cnt, wr, r = quick_backtest(df, TrendFollowingNative(**f1))
    print(f"   {t}: {t_cnt} trades, WR: {wr:.1f}%, R: {r:.1f}")

# Config 2: Standard (50/100, ADX 25)
f2 = {"ema_fast": 50, "ema_slow": 100, "min_adx": 25.0}
print(f"\n[Flow 2] Standard (50/100): {f2}")
for t in tokens:
    df = fetch_data(t, timeframe)
    t_cnt, wr, r = quick_backtest(df, TrendFollowingNative(**f2))
    print(f"   {t}: {t_cnt} trades, WR: {wr:.1f}%, R: {r:.1f}")

# Config 3: Swing (50/200, ADX 25)
f3 = {"ema_fast": 50, "ema_slow": 200, "min_adx": 25.0}
print(f"\n[Flow 3] Swing (50/200): {f3}")
for t in tokens:
    df = fetch_data(t, timeframe)
    t_cnt, wr, r = quick_backtest(df, TrendFollowingNative(**f3))
    print(f"   {t}: {t_cnt} trades, WR: {wr:.1f}%, R: {r:.1f}")
