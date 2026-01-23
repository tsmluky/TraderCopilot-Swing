from database import SessionLocal
from models_db import StrategyConfig

def check_strategies():
    db = SessionLocal()
    try:
        print("\n=== Active Functioning Strategies ===")
        configs = db.query(StrategyConfig).all()
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
