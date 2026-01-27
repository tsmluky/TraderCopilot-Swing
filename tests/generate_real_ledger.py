
import sys
import os
import pandas as pd
import ccxt.pro as ccxt 
import asyncio
import json
from datetime import datetime
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from strategies.TrendFollowingNative import TrendFollowingNative
from strategies.DonchianBreakoutV2 import DonchianBreakoutV2
from strategies.MeanReversionBollinger import MeanReversionBollinger

# LOAD FROM LOCAL CSV
def fetch_data(symbol="BTC/USDT", timeframe="1h", desired_candles=4000):
    # Map symbol to filename: BTC/USDT -> BTC_1h.csv
    token = symbol.split('/')[0]
    filename = f"{token}_{timeframe}.csv"
    csv_path = os.path.join(r"C:\Users\lukx\Desktop\velasccxt", filename)
    
    if not os.path.exists(csv_path):
        print(f"   [Warn] Local file not found: {csv_path}. Returning empty.")
        return pd.DataFrame()
        
    print(f"   > Loading local data: {csv_path} ...")
    try:
        df = pd.read_csv(csv_path)
        # Ensure timestamp parsing
        if 'timestamp' in df.columns:
            # Check if likely ms or s
            first_ts = float(df['timestamp'].iloc[0])
            unit = 'ms' if first_ts > 10000000000 else 's' # heuristic
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit=unit)
        
        # Sort and take last N
        df = df.sort_values('timestamp')
        if len(df) > desired_candles:
            df = df.iloc[-desired_candles:]
            
        return df.reset_index(drop=True)
    except Exception as e:
        print(f"   [Error] Loading CSV failed: {e}")
        return pd.DataFrame()


def simulate_outcome(signal, df, index):
    """
    Returns: (Result: 'WIN'|'LOSS'|'OPEN', PnL: floatR, price: float, exit_date: str)
    """
    entry = signal.entry
    tp = signal.tp
    sl = signal.sl
    direction = signal.direction
    
    # Check next candles
    for i in range(index + 1, len(df)):
        row = df.iloc[i]
        high = row['high']
        low = row['low']
        ts = row['timestamp']
        
        if direction == 'long':
            if low <= sl: return ('LOSS', -1.0, sl, ts.isoformat()) 
            if high >= tp: return ('WIN', 2.2, tp, ts.isoformat())  # TP hit (approx)
        else:
            if high >= sl: return ('LOSS', -1.0, sl, ts.isoformat())
            if low <= tp: return ('WIN', 2.2, tp, ts.isoformat())
            
    return ('OPEN', 0.0, df.iloc[-1]['close'], df.iloc[-1]['timestamp'].isoformat())

async def main():
    tokens = ["BTC", "ETH", "SOL", "BNB", "XRP"]
    timeframe = "1h"
    limit = 43000 # Use substantially more history if available (approx 5 years ~ 43800)
    
    print(f"🚀 GENERATING REAL BACKTEST DATA from LOCAL | {timeframe} | Limit: {limit}")
    
    strategies = [
        ("trend_following_native_v1", TrendFollowingNative(ema_fast=20, ema_slow=50, min_adx=20.0)),
        ("donchian_v2", DonchianBreakoutV2(donchian_period=20, ema_period=200, atr_period=14)),
        ("mean_reversion_v1", MeanReversionBollinger(bb_period=20, bb_std=2.5, rsi_period=14))
    ]
    
    export_data = {}

    # Pre-fetch data once per token to save time
    market_data = {}
    for token in tokens:
        symbol = f"{token}/USDT"
        print(f"\n📥 Fetching data for {token}...")
        df = fetch_data(symbol, timeframe, desired_candles=limit)
        market_data[token] = df

    for sid, strategy in strategies:
        print(f"\n🛠️  Processing Strategy: {sid} ({strategy.META.name})")
        export_data[sid] = {}
        
        for token in tokens:
            df = market_data.get(token)
            if df is None or df.empty:
                print(f"   Skipping {token} (no data)")
                continue
            
            print(f"   > Scanning {token} ({len(df)} candles)...")
            
            try:
                sigs = strategy.find_historical_signals(token, df, timeframe)
            except Exception as e:
                print(f"   [Error] Scanning failed: {e}")
                sigs = []

            print(f"   > Found {len(sigs)} signals. Simulating outcomes...")
            
            trades_list = []
            
            for sig in sigs:
                match = df[df['timestamp'] == sig.timestamp]
                if match.empty: continue
                
                idx = match.index[0]
                res, r_val, exit_price, exit_date = simulate_outcome(sig, df, idx)
                
                trades_list.append({
                    "id": "", 
                    "date": sig.timestamp.strftime('%Y-%m-%d'),
                    "type": sig.direction.upper(),
                    "price": f"{sig.entry:.2f}",
                    "r": str(r_val),
                    "exit_date": str(exit_date).split("T")[0],
                    "result": res,
                    "token": token
                })
                
            trades_list.sort(key=lambda x: x["date"], reverse=True)
            
            for i, t in enumerate(trades_list):
                t["id"] = f"TR-{10000+i}"
                
            export_data[sid][token] = trades_list
            print(f"   > Saved {len(trades_list)} trades for {token}.")

    # Write to web/data/real_ledger.json
    out_dir = os.path.join(os.path.dirname(__file__), '../web/data')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'real_ledger.json')
    
    with open(out_path, 'w') as f:
        json.dump(export_data, f, indent=2)
        
    print(f"\n✅ DONE. Full ledger saved to: {out_path}")

if __name__ == "__main__":
    loop = asyncio.events.new_event_loop()
    asyncio.events.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
