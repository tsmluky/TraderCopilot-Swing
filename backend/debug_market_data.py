
import sys
import os
import asyncio
from pathlib import Path

# Add backend to sys.path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from core.market_data_api import get_ohlcv_data

def test_fetch():
    print("Testing ETH fetch...")
    try:
        data = get_ohlcv_data("ETH", "1h", limit=5)
        if data:
            print(f"✅ Success! Fetched {len(data)} candles.")
            print(f"Last close: {data[-1]['close']}")
        else:
            print("❌ Failed. Returned empty list.")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_fetch()
