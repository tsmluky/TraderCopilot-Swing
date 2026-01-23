import sys
import os

sys.path.insert(0, os.getcwd())

from database import SessionLocal
from models_db import StrategyConfig


def check_strategies():
    db = SessionLocal()
    try:
        configs = db.query(StrategyConfig).all()
        print(f"Found {len(configs)} strategy configurations:")
        for c in configs:
            print(
                f" - ID: {c.strategy_id}, Name: {c.name}, Enabled: {c.enabled}, Interval: {c.interval_seconds}s"
            )

        if not configs:
            print("No strategies found. We need to seed the DB.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    check_strategies()
