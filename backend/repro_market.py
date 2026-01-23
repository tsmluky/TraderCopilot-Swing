import ccxt


def test_market():
    print("Trying to fetch tickers from Binance via CCXT...")
    try:
        exchange = ccxt.binance({
            "enableRateLimit": True,
            "timeout": 5000,
        })
        symbols = ["BTC/USDT", "ETH/USDT"]
        tickers = exchange.fetch_tickers(symbols)
        print("✅ Success!")
        for s, t in tickers.items():
            print(f"{s}: {t['last']}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_market()
