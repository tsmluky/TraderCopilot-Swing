
import sys
import os
from sqlalchemy.orm import Session
from datetime import datetime

# Setup path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import SessionLocal
from routers.strategies import get_marketplace, _calculate_stats
from models_db import User
from core.entitlements import PLANS

# Mock User
class MockUser:
    def __init__(self):
        self.plan = "PRO"
        self.id = 1
        self.plan_expires_at = datetime(2030, 1, 1)

def debug_endpoint():
    db = SessionLocal()
    try:
        user = MockUser()
        print("--- Simulating GET /strategies/marketplace for PRO user ---")
        
        # 1. Run the actual endpoint logic (slightly modified to access internally or just re-impl logic)
        # Since I can't await async easily in script without loop, I'll just run the logic from the file manually
        # OR just import the logic.
        
        from core.entitlements import get_user_entitlements
        
        offerings_data = get_user_entitlements(user)
        print(f"Found {len(offerings_data['offerings'])} offerings.")
        
        for offering in offerings_data["offerings"]:
            # Recalculate stats exactly as the router does
            stats = _calculate_stats(db, offering["strategy_code"], offering["timeframe"])
            
            # Print result
            print(f"Strategy: {offering['strategy_code']} | TF: {offering['timeframe']}")
            print(f"  -> Generated ID: {offering['strategy_code']}_{offering['timeframe']}")
            print(f"  -> Stats: {stats}")
            
            if stats['total_signals'] == 0:
                print("     [WARNING] count is 0. Checking DB details...")
                # Deep dive
                target_id = f"{offering['strategy_code']}_{offering['timeframe']}"
                from models_db import Signal
                # Check DB for any variation
                c_saved = db.query(Signal).filter(Signal.strategy_id == target_id, Signal.is_saved == 1).count()
                c_unsaved = db.query(Signal).filter(Signal.strategy_id == target_id).count()
                c_lower = db.query(Signal).filter(Signal.strategy_id == target_id.lower()).count()
                
                print(f"     DB Check: Saved=1 -> {c_saved}")
                print(f"     DB Check: Any     -> {c_unsaved}")
                print(f"     DB Check: Lower   -> {c_lower}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_endpoint()
