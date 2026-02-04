
import sys
import os
from sqlalchemy.orm import Session

# Setup path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import SessionLocal
from models_db import Signal

def check_stats(strategy_code, timeframe):
    db = SessionLocal()
    try:
        target_id = f"{strategy_code}_{timeframe}"
        print(f"Checking stats for Target ID: '{target_id}'")
        
        # 1. Check strict count (is_saved=1)
        count_strict = db.query(Signal).filter(
            Signal.strategy_id == target_id,
            Signal.is_saved == 1
        ).count()
        
        # 2. Check loose count (ignore is_saved)
        count_loose = db.query(Signal).filter(
            Signal.strategy_id == target_id
        ).count()
        
        print(f"  Strict Count (is_saved=1): {count_strict}")
        print(f"  Loose Count (any saved):   {count_loose}")
        
        # 3. Debug actual rows if mismatch
        if count_loose > 0:
            print("\n  Sample Signal Data:")
            sigs = db.query(Signal).filter(Signal.strategy_id == target_id).limit(3).all()
            for s in sigs:
                print(f"    ID={s.id} | StratID='{s.strategy_id}' | Saved={s.is_saved} | TS={s.timestamp}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_stats("TITAN_BREAKOUT", "1D")
    print("-" * 30)
    check_stats("TITAN_BREAKOUT", "4H")
