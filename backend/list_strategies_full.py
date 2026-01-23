import os
# FORCE LOCAL DB
os.environ["DATABASE_URL"] = "sqlite:///backend/dev_local.db"

from database import SessionLocal
from models_db import StrategyConfig

def list_strategies():
    db = SessionLocal()
    try:
        configs = db.query(StrategyConfig).all()
        print(f"{'ID':<4} | {'STRATEGY_ID':<25} | {'PERSONA_ID':<20} | {'ENABLED':<8} | {'NAME'}")
        print("-" * 100)
        for c in configs:
            print(f"{c.id:<4} | {c.strategy_id:<25} | {str(c.persona_id):<20} | {c.enabled:<8} | {c.name}")
    finally:
        db.close()

if __name__ == "__main__":
    list_strategies()
