
import os
import sys
import pandas as pd
import pandas as pd

# Fix path to import core backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from strategies.DonchianBreakoutV2 import DonchianBreakoutV2


DATA_PATH = r"C:\Users\lukx\Desktop\velasccxt"

def load_data(token="BTC", tf="4h"):
    path = os.path.join(DATA_PATH, f"{token}_{tf}.csv")
    if not os.path.exists(path):
        print(f"Data not found: {path}")
        return None
    df = pd.read_csv(path)
    # Convert ms timestamp to datetime object
    if 'timestamp' in df.columns:
        # Check if looks like MS (13 digits)
        if df['timestamp'].iloc[0] > 1e11:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        else:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            
    return df

def simulate_trades(signals, df):
    """
    Simulate trade outcomes based on TP/SL.
    Returns list of trades with 'pnl' (R-multiple).
    """
    if not signals:
        return []

    # Map dataframe by index or timestamp for fast lookup
    # Heuristic: signals from find_historical_signals usually have 'timestamp' matching df
    
    # We need to find the candle index for each signal entry
    # This is O(N*M) if naive. Let's rely on finding row by closest time.
    
    trades = []
    
    # Pre-index DF by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)
    # Create a lookup for index
    time_map = {t: i for i, t in enumerate(df['timestamp'])}
    
    for sig in signals:
        # Signal timestamp is the candle CLOSE time or signal trigger time.
        # We start checking outcomes from the NEXT candle.
        start_ts = sig.timestamp
        # find closest in data (exact match expected if backtest gen used this data)
        start_idx = time_map.get(start_ts)
        
        if start_idx is None:
            continue
            
        entry = sig.entry
        tp = sig.tp
        sl = sig.sl
        direction = sig.direction
        
        # Simulate forward
        result = "OPEN"
        pnl = 0.0
        
        for i in range(start_idx + 1, len(df)):
            row = df.iloc[i]
            high = row['high']
            low = row['low']
            
            if direction == 'long':
                if high >= tp:
                    result = "WIN"
                    pnl = sig.tp_r if hasattr(sig, 'tp_r') else (tp - entry) / (entry - sl) # Approx R
                    break
                if low <= sl:
                    result = "LOSS"
                    pnl = -1.0
                    break
            else: # short
                if low <= tp:
                    result = "WIN"
                    pnl = sig.tp_r if hasattr(sig, 'tp_r') else (entry - tp) / (sl - entry)
                    break
                if high >= sl:
                    result = "LOSS"
                    pnl = -1.0
                    break
                    
        trades.append({
            "timestamp": start_ts,
            "token": sig.token,
            "type": direction,
            "result": result,
            "pnl_r": round(pnl if result != "OPEN" else 0.0, 2)
        })
        
    return trades

def print_stats(name, trades):
    if not trades:
        print(f"[{name}] No trades found.")
        return

    wins = [t for t in trades if t['result'] == "WIN"]
    losses = [t for t in trades if t['result'] == "LOSS"]
    total = len(wins) + len(losses)
    
    if total == 0:
        print(f"[{name}] No closed trades.")
        return

    win_rate = len(wins) / total * 100
    total_r = sum(t['pnl_r'] for t in trades)
    
    print(f"--- {name} ---")
    print(f"Trades: {total}")
    print(f"Win Rate: {win_rate:.1f}%")
    print(f"Total Return: {total_r:.2f} R")
    print(f"Avg Return: {total_r/total:.2f} R / trade")
    print("-" * 20)

def run_comparison():
    print("Loading BTC 4H Data...")
    df = load_data("BTC", "4h")
    if df is None:
        return

    print(f"Loaded {len(df)} candles.\n")

    # --- DONCHIAN COMPARISON ---
    print(">>> TESTING DONCHIAN BREAKOUT (Breakout Logic) <<<")
    
    # 1. Current (Default)
    # tp_atr=2.0, sl_atr=1.2 (~1.66 R)
    strat_don_curr = DonchianBreakoutV2(tp_atr=2.0, sl_atr=1.2)
    sigs_curr = strat_don_curr.find_historical_signals("BTC", df, "4h")
    trades_curr = simulate_trades(sigs_curr, df)
    print_stats("Donchian (Current: TP=2.0 ATR)", trades_curr)

    # 2. Proposed
    # tp_atr=3.0, sl_atr=1.2 (~2.5 R)
    strat_don_prop = DonchianBreakoutV2(tp_atr=3.0, sl_atr=1.2)
    sigs_prop = strat_don_prop.find_historical_signals("BTC", df, "4h")
    trades_prop = simulate_trades(sigs_prop, df)
    print_stats("Donchian (Proposed: TP=3.0 ATR)", trades_prop)
    
    print("\n")

    # Trend Following skipped for isolation
    pass

if __name__ == "__main__":
    run_comparison()
