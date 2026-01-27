
import ccxt
import time
from datetime import datetime

def test_direct():
    print("Testing Binance Direct...")
    try:
        exchange = ccxt.binance({"enableRateLimit": True, "timeout": 10000})
        # exchange.verbose = True # Optional: extremely verbose
        data = exchange.fetch_ohlcv("ETH/USDT", "1h", limit=5)
        print(f"✅ Success! {len(data)} candles.")
        print(data[-1])
        exchange.close()
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct()
