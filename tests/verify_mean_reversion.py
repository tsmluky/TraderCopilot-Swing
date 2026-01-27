
import sys
import os
import pandas as pd
import asyncio
import ccxt.async_support as ccxt
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from strategies.MeanReversionRSI import MeanReversionRSI

async def fetch_historical_data(symbol, timeframe, months=24):
    ex = ccxt.binance({'enableRateLimit': True})
    limit = 1000
    all_ohlcv = []
    
    # Calculate start time
    now = datetime.utcnow()
    start_date = now - timedelta(days=30*months)
    since = int(start_date.timestamp() * 1000)
    
    try:
        while True:
            ohlcv = await ex.fetch_ohlcv(symbol, timeframe, limit=limit, since=since)
            if not ohlcv:
                break
            
            all_ohlcv.extend(ohlcv)
            
            last_ts = ohlcv[-1][0]
            since = last_ts + 1
            
            if len(ohlcv) < limit:
                break
            # Safety limit
            if len(all_ohlcv) > 50000: 
                break
                
        df = pd.DataFrame(all_ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['time'], unit='ms')
        return df.to_dict('records')  
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return []
    finally:
        await ex.close()

def simulate_outcome(signal, df, index):
    entry = signal.entry
    tp = signal.tp
    sl = signal.sl
    direction = signal.direction
    
    # R-Multiple approx
    r_win = 1.33 
    r_loss = -1.0
    
    for i in range(index + 1, len(df)):
        row = df.iloc[i]
        high = row['high']
        low = row['low']
        
        if direction == 'long':
            if low <= sl: return ('LOSS', r_loss)
            if high >= tp: return ('WIN', r_win)
        else:
            if high >= sl: return ('LOSS', r_loss)
            if low <= tp: return ('WIN', r_win)
            
    return ('OPEN', 0.0)

async def main():
    tokens = ["BTC", "ETH", "SOL", "BNB", "XRP"]
    timeframes = ["1h", "4h"] 
    history_months = 12 # 1 Year for quick validation
    
    print(f"| Token | Timeframe | Trades (1y) | Win Rate | Total R | Wins | Losses |")
    print(f"|-------|-----------|-------------|----------|---------|------|--------|")
    
    # v1 Standard
    strat = MeanReversionRSI(bb_period=20, bb_std=2.0, rsi_period=14, rsi_oversold=30, rsi_overbought=70)
    
    cache = {}

    # 1. Fetch Data
    for token in tokens:
        for tf in timeframes:
            symbol = f"{token}/USDT"
            # print(f"Fetching {symbol} {tf}...", flush=True)
            raw = await fetch_historical_data(symbol, tf, months=history_months)
            if raw and len(raw) > 100:
                cache[f"{token}_{tf}"] = raw

    # 2. Run Backtest
    for token in tokens:
        for tf in timeframes:
            key = f"{token}_{tf}"
            if key not in cache:
                print(f"| {token} | {tf} | ERR | 0% | 0.0R | 0 | 0 |")
                continue
            
            raw = cache[key]
            df = pd.DataFrame(raw)
            
            # Use the correct historical method
            if hasattr(strat, 'find_historical_signals'):
                signals = strat.find_historical_signals(token, df, timeframe=tf)
            else:
                context = {"data": {token: raw}}
                signals = strat.generate_signals([token], tf, context)
            
            wins = 0
            losses = 0
            total_r = 0.0
            
            for s in signals:
                match = df[df['timestamp'] == s.timestamp]
                if not match.empty:
                    idx = match.index[0]
                    res, r_val = simulate_outcome(s, df, idx)
                    if res == 'WIN': wins += 1
                    if res == 'LOSS': losses += 1
                    total_r += r_val
            
            total = wins + losses
            wr = (wins/total*100) if total > 0 else 0.0
            
            if total > 0:
                print(f"| {token} | {tf} | {total} | {wr:.1f}% | {total_r:.1f}R | {wins} | {losses} |")
            else:
                print(f"| {token} | {tf} | 0 | 0.0% | 0.0R | 0 | 0 |")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
