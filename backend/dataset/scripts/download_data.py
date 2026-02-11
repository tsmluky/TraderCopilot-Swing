import ccxt
import pandas as pd
import os
from datetime import datetime
import time

def download_candles(symbol, timeframe='1h', since_years=8):
    print(f"Downloading {symbol} data...")
    exchange = ccxt.binance()
    
    # Calculate start time
    now = exchange.milliseconds()
    since = now - (since_years * 365 * 24 * 60 * 60 * 1000)
    
    all_ohlcv = []
    limit = 1000  # Binance limit per request
    
    while since < now:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            if not ohlcv:
                break
            
            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + 1  # Move to next timestamp
            
            # Simple progress release
            last_date = datetime.fromtimestamp(ohlcv[-1][0] / 1000)
            print(f"Downloaded until {last_date}")
            
            # Respect rate limits
            time.sleep(exchange.rateLimit / 1000)
            
        except Exception as e:
            print(f"Error downloading {symbol}: {e}")
            break
            
    if not all_ohlcv:
        print(f"No data found for {symbol}")
        return

    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Save to CSV
    filename = f"data/{symbol.replace('/', '_')}_{timeframe}.csv"
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} rows to {filename}")

if __name__ == "__main__":
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']
    for symbol in symbols:
        download_candles(symbol)
