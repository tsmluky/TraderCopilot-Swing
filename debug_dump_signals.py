
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc

# Setup path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import SessionLocal
from models_db import Signal

def dump_signals():
    db = SessionLocal()
    try:
        print("Dumping top 10 recent signals...")
        signals = db.query(Signal).order_by(Signal.timestamp.desc()).limit(10).all()
        
        for s in signals:
            print(f"ID: {s.id}")
            print(f"  Token:      '{s.token}'")
            print(f"  StrategyID: '{s.strategy_id}'")
            print(f"  Timeframe:  '{s.timeframe}'")
            print(f"  Saved:      {s.is_saved}")
            print("-" * 20)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    dump_signals()
