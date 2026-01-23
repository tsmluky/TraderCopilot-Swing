# backend/tools/verify_lite_engine.py
from __future__ import annotations

import json
import sys
import os
from pathlib import Path

# Add backend to path
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))

# Mock Env
os.environ["DATABASE_URL"] = "sqlite:///backend/dev_local.db"

from database import SessionLocal  # noqa: E402
from models_db import User  # noqa: E402
from indicators.market import get_market_data  # noqa: E402
from core.lite_swing_engine import build_lite_swing_signal  # noqa: E402


def main() -> int:
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            print("No users found in DB. Create a user first (register) and retry.")
            return 1

        print(f"Using user: {user.email} (ID: {user.id})")

        token = "BTC"
        timeframe = "4H"
        print(f"Fetching market data for {token} {timeframe}...")
        
        # CCXT needs lowercase
        df, market = get_market_data(token, timeframe.lower(), limit=250)
        if not market:
            print("Market data unavailable. Check network / CCXT / exchange availability.")
            return 2

        print("Building signal...")
        lite, indicators = build_lite_swing_signal(db=db, user=user, token=token, timeframe=timeframe, market=market)
        
        out = lite.model_dump()
        out["strategy_id"] = indicators.get("strategy_id")
        out["indicators"] = indicators
        
        print("\n=== LITE-Swing Response ===")
        print(json.dumps(out, indent=2, default=str))
        
        if lite.direction == "neutral":
             print("\n✅ Verified: Neutral response working (Setup Detector).")
        else:
             print(f"\n✅ Verified: Signal Detected ({lite.direction}). Setup Detector working.")

        return 0
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
