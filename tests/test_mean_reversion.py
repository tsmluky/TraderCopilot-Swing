import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Mock environment if needed
os.environ["DATABASE_URL"] = "sqlite:///:memory:" 

from strategies.registry import load_default_strategies, get_registry
from market_data import get_ohlcv

def test():
    print("Loading strategies...")
    load_default_strategies()
    r = get_registry()
    print("Strategies Loaded:", list(r._strategies.keys()))
    
    strat_id = "mean_reversion_v1"
    s = r.get(strat_id)
    if not s:
        print(f"FAIL: Strategy {strat_id} not found")
        return
        
    print(f"Strategy {strat_id} instantiation successful.")
    print("Metadata:", s.metadata())
    
    # Fetch data (Live fetch from whatever provider is configured, usually Binance public API)
    print("Fetching SOL 1h (100 candles)...")
    try:
        df = get_ohlcv("SOL", "1h", limit=300)
        if df is None or df.empty:
            print("WARNING: No data returned from get_ohlcv. Skipping signal test.")
            return
            
        print(f"Data Fetched: {len(df)} rows")
        
        # Test Generation
        signals = s.find_historical_signals("SOL", df, "1h")
        print(f"Historical Signals Found (Last 300 candles): {len(signals)}")
        
        if signals:
            print("First Signal:", signals[0])
            print("Last Signal:", signals[-1])
        else:
            print("No signals found in recent history (this is normal for high BB settings).")
            
        # Test Live Generation Interface
        live_signals = s.generate_signals(["SOL"], "1h", context={"data": {"SOL": df.to_dict("records")}})
        print(f"Live Generation Check: {len(live_signals)} signals")
        
    except Exception as e:
        print(f"Runtime Error during signal generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
