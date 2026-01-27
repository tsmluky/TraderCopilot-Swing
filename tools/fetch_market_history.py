
import os
import asyncio
import ccxt.pro as ccxt
import pandas as pd
from datetime import datetime, timedelta
import time

# Configuration
TOKENS = ["BTC", "ETH", "SOL", "BNB", "XRP"]
TIMEFRAMES = ["1h", "4h"]
YEARS = 5
OUTPUT_DIR = r"C:\Users\lukx\Desktop\velasccxt"

async def fetch_ohlcv_history(exchange, symbol, timeframe, since_ts, limit_per_req=1000):
    all_ohlcv = []
    current_since = since_ts
    
    print(f"   > Starting fetch for {symbol} {timeframe} since {datetime.fromtimestamp(current_since/1000)}")
    
    while True:
        try:
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, since=current_since, limit=limit_per_req)
            if not ohlcv:
                break
            
            all_ohlcv.extend(ohlcv)
            
            # Move `since` pointer
            last_ts = ohlcv[-1][0]
            
            # If we reached near present, stop
            if last_ts >= (time.time() * 1000) - 60000: # within last minute
                break
                
            # If we didn't get a full batch, we might be at the end
            if len(ohlcv) < limit_per_req:
                current_since = last_ts + 1 
                # Break if we are clearly done? binance usually returns fewer if at end.
                # but let's just update since and try one more time to be sure
                # break 
            else:
                current_since = last_ts + 1
            
            # Rate limit
            # await asyncio.sleep(0.05) 
            
            # Progress marker
            if len(all_ohlcv) % 10000 == 0:
                print(f"     ... collected {len(all_ohlcv)} candles (latest: {datetime.fromtimestamp(last_ts/1000)})")
                
        except Exception as e:
            print(f"     [Error] {e}. Retrying in 5s...")
            await asyncio.sleep(5)
            
    return all_ohlcv

async def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")
        
    ex = ccxt.binance()
    
    start_time = datetime.now() - timedelta(days=365 * YEARS)
    start_ts = int(start_time.timestamp() * 1000)
    
    print(f"🚀 MARKET DATA DOWNLOADER | {YEARS} Years | Target: {OUTPUT_DIR}")
    
    try:
        for token in TOKENS:
            symbol = f"{token}/USDT"
            
            for tf in TIMEFRAMES:
                print(f"\n📥 Processing {symbol} - {tf}...")
                
                filename = f"{token}_{tf}.csv"
                filepath = os.path.join(OUTPUT_DIR, filename)
                
                if os.path.exists(filepath):
                    print(f"   Warning: {filename} exists. Skipping (delete to re-fetch).")
                    continue
                
                data = await fetch_ohlcv_history(ex, symbol, tf, start_ts)
                
                if data:
                    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    # Save as CSV with header
                    df.to_csv(filepath, index=False)
                    print(f"   ✅ Saved {len(df)} rows to {filename}")
                else:
                    print(f"   ⚠️ No data found for {symbol} {tf}")
                    
    finally:
        await ex.close()
        print("\n🏁 All downloads completed.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
