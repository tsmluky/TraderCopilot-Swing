
import sys
import os
import pandas as pd
import ccxt.pro as ccxt # or normal ccxt
import asyncio
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from strategies.TrendFollowingNative import TrendFollowingNative
from strategies.DonchianBreakoutV2 import DonchianBreakoutV2

async def fetch_data(symbol="BTC/USDT", timeframe="4h", limit=500):
    ex = ccxt.binance()
    try:
        ohlcv = await ex.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        # timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['time'], unit='ms')
        return df.to_dict('records')
    finally:
        await ex.close()

def run_test():
    print("📉 Fetching Market Data (BTC/USDT 4h)...")
    # specific loop for async fetch in sync wrapper if needed, or just run main async
    pass


def simulate_outcome(signal, df, index):
    """
    Simula el resultado del trade mirando velas futuras.
    Retorna: (Result: 'WIN'|'LOSS'|'OPEN', PnL: float)
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
        
        if direction == 'long':
            if low <= sl: return ('LOSS', -1.0) # SL hit first (pessimistic)
            if high >= tp: return ('WIN', 2.0)  # TP hit (approx 2R usually)
        else:
            if high >= sl: return ('LOSS', -1.0)
            if low <= tp: return ('WIN', 2.0)
            
    return ('OPEN', 0.0)

async def main():
    tokens = ["BTC", "ETH", "SOL"]
    timeframe = "1h" # PRO Tier
    limit = 1000     
    
    print(f"📊 Strategy Commercial Test (Backtest) | {timeframe} | {len(tokens)} Tokens | Last {limit} candles")
    print("="*60)
    
    # Store aggregated stats
    stats = {
        "Conservative": {"wins": 0, "losses": 0, "total": 0},
        "Balanced":     {"wins": 0, "losses": 0, "total": 0},
        "Aggressive":   {"wins": 0, "losses": 0, "total": 0}
    }

    for token in tokens:
        symbol = f"{token}/USDT"
        print(f"\n🔍 Analyzing {token}...")
        
        try:
            raw_data = await fetch_data(symbol, timeframe, limit=limit)
        except Exception as e:
            print(f"  [ERROR] data fetch failed: {e}")
            continue

        context = {"data": {token: raw_data}}
        df = pd.DataFrame(raw_data) # Need raw DF for simulation
        
        # Define Variants
        variants = [
            ("Conservative", TrendFollowingNative(ema_fast=20, ema_slow=50, min_adx=25.0)),
            ("Balanced",     TrendFollowingNative(ema_fast=20, ema_slow=50, min_adx=20.0)),
            ("Aggressive",   TrendFollowingNative(ema_fast=9, ema_slow=21, min_adx=18.0))
        ]
        
        for name, strat in variants:
            sigs = strat.generate_signals([token], timeframe, context) or []
            
            # Backtest each signal
            wins = 0
            losses = 0
            
            for sig in sigs:
                # Find index of signal timestamp
                # Optimization: In real backtest we'd align properly, here we approximate by finding timestamp match
                match = df[df['timestamp'] == sig.timestamp]
                if not match.empty:
                    idx = match.index[0]
                    res, pnl = simulate_outcome(sig, df, idx)
                    if res == 'WIN': wins += 1
                    if res == 'LOSS': losses += 1
            
            total = wins + losses
            wr = (wins/total*100) if total > 0 else 0.0
            
            stats[name]["wins"] += wins
            stats[name]["losses"] += losses
            stats[name]["total"] += total
            
            print(f"    - {name:12}: {len(sigs)} sigs | {wins}W - {losses}L | WR: {wr:.1f}%")

    print("\n📈 AGGREGATED RESULTS (All Tokens)")
    print("-" * 60)
    for name, s in stats.items():
        total = s["total"]
        wr = (s["wins"]/total*100) if total > 0 else 0.0
        print(f"  {name:12}: {s['wins']} Wins | {s['losses']} Losses | Total: {total} | WR: {wr:.1f}%")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
