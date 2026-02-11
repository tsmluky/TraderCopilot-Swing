import sys
import os
import json
from datetime import datetime

# Setup paths
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from database import SessionLocal
from models_db import User
from core.lite_swing_engine import build_lite_swing_signal
from strategies.registry import load_default_strategies

# Init Registry
load_default_strategies()

def debug_run(token="BTC", timeframe="1h"): # Use '1h' lowercase to match CCXT expectations if needed, but engine handles it.
    print(f"--- DEBUG RUN: {token} {timeframe} ---")
    db = SessionLocal()
    try:
        # Create dummy user or get first user
        user = db.query(User).first()
        if not user:
            print("No user found, creating dummy.")
            user = User(id=1, email="test@test.com")
        
        print(f"User: {user.email}")
        
        # Run engine
        lite, indicators = build_lite_swing_signal(db, user, token, timeframe)
        
        print(f"\nRESULT: {lite.direction} (Conf: {lite.confidence})")
        print(f"Rationale: {lite.rationale}")
        print(f"Source: {lite.source}")
        
        print("\n--- STRATEGIES RUN ---")
        strats = indicators.get("strategies", [])
        for s in strats:
            print(f"  > {s.get('strategy_id')}: OK={s.get('ok')} Setup={s.get('has_setup')} Dir={s.get('direction')} Err={s.get('error')}")
            if s.get("state"):
                print(f"    State: {str(s.get('state'))[:100]}...")

        print("\n--- WATCHLIST (Fallback) ---")
        watchlist = lite.watchlist
        if watchlist:
            for w in watchlist:
                print(f"  > {w.get('strategy_id')} ({w.get('token')}): Dist={w.get('distance_atr')} Reason={w.get('reason')}")
        else:
            print("  (Empty Watchlist)")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("token", nargs="?", default="BTC")
    parser.add_argument("tf", nargs="?", default="1h")
    args = parser.parse_args()
    
    debug_run(args.token, args.tf)
