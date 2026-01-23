import os

# FORCE LOCAL DB for verification
# Note: running from root, so path is backend/dev_local.db
os.environ["DATABASE_URL"] = "sqlite:///backend/dev_local.db"

from database import SessionLocal
from models_db import StrategyConfig

def check_strategies():
    print(f"Checking DB: {os.environ['DATABASE_URL']}")
    db = SessionLocal()
    try:
        print("\n=== Active Functioning Strategies ===")
        # Check if table exists first by simple query
        try:
            configs = db.query(StrategyConfig).all()
        except Exception as e:
            print(f"Error querying StrategyConfig: {e}")
            return

        active_count = 0
        for config in configs:
            status = "✅ ENABLED" if config.enabled == 1 else "❌ DISABLED"
            print(f"[{config.id}] {config.strategy_id} ({config.name}): {status}")
            if config.enabled == 1:
                active_count += 1
        
        print(f"\nTotal Active Strategies: {active_count}")
        print("======================================\n")
    finally:
        db.close()

if __name__ == "__main__":
    check_strategies()
