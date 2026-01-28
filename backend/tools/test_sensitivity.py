import sys
import os

# Adjust path to include backend root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal
from models_db import User
from core.lite_swing_engine import build_lite_swing_signal
from indicators.market import get_market_data

def test_sensitivity():
    db = SessionLocal()
    # Get a dummy user (first user) or create one context
    user = db.query(User).first()
    if not user:
        print("No user found for context.")
        return

    tokens = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP']
    timeframes = ['1h', '4h', '1d']
    
    results = {
        "signal": 0,
        "watchlist": 0,
        "neutral": 0,
        "total": 0
    }

    print(f"\n{'='*60}")
    print("RUNNING SCANNER SENSITIVITY TEST (Thresholds Relaxed)")
    print(f"{'='*60}\n")
    print(f"{'TOKEN':<8} {'TF':<5} {'TYPE':<10} {'CONFidence':<10} {'ITEMS':<5} {'RATIONALE'}")
    print("-" * 100)

    for t in tokens:
        for tf in timeframes:
            try:
                # 1. Fetch real market data first (mocking request flow)
                df, market = get_market_data(t, tf)
                if not market:
                    print(f"{t:<8} {tf:<5} ERROR: No Market Data")
                    continue

                # 2. Run Engine
                signal, indicators = build_lite_swing_signal(db, user, t, tf, market)
                
                res_type = "NEUTRAL"
                if signal.confidence > 0.6:
                    res_type = "SIGNAL"
                    results["signal"] += 1
                elif signal.watchlist and len(signal.watchlist) > 0:
                    res_type = "WATCHLIST"
                    results["watchlist"] += 1
                else:
                    results["neutral"] += 1
                
                results["total"] += 1
                
                wl_count = len(signal.watchlist) if signal.watchlist else 0
                print(f"{t:<8} {tf:<5} {res_type:<10} {signal.confidence*100:>5.1f}%     "
                      f"{wl_count:<5} {signal.rationale[:50]}...")

            except Exception as e:
                print(f"Error testing {t} {tf}: {e}")

    print("\n" + "="*30)
    print("SUMMARY STATISTICS")
    print("="*30)
    print(f"Total Scans: {results['total']}")
    print(f"Signals:     {results['signal']} ({results['signal']/results['total']*100:.1f}%)")
    print(f"Watchlist:   {results['watchlist']} ({results['watchlist']/results['total']*100:.1f}%)")
    print(f"Neutral:     {results['neutral']} ({results['neutral']/results['total']*100:.1f}%)")
    print("="*30)
    
    if results['neutral'] > (results['total'] * 0.8):
        print("\n[FAIL] Scanner is still too strict (>80% Neutral).")
    else:
        print("\n[PASS] Scanner shows healthy activity.")

if __name__ == "__main__":
    test_sensitivity()
