
import sys
import os
from sqlalchemy.orm import Session
from datetime import datetime

# Setup path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import SessionLocal
from scheduler import StrategyScheduler
from core.schemas import Signal
from models_db import User

def test_telegram_dispatch():
    if not os.getenv("TELEGRAM_CHAT_ID"):
        print("[WARN] TELEGRAM_CHAT_ID env var is not set! Test might fail.")
    
    db = SessionLocal()
    try:
        scheduler = StrategyScheduler()
        
        # Create Dummy Signal
        sig = Signal(
            timestamp=datetime.utcnow(),
            token="TEST-BTC",
            direction="long",
            entry=100.0,
            tp=110.0,
            sl=90.0,
            confidence=0.99,
            rationale="Test Dispatch",
            strategy_id="TEST_STRAT_1H",
            mode="PRO",
            timeframe="1H",
            source="TEST",
            extra={}
        )
        
        print("--- Testing Fan-Out ---")
        scheduler.fan_out_notifications(db, sig, "PRO")
        print("--- Done ---")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_telegram_dispatch()
