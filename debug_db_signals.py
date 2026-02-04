
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc
from datetime import datetime

# Setup path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import get_db, SessionLocal
from models_db import Signal

def inspect_signals():
    db = SessionLocal()
    try:
        print("Fetching recent signals...")
        signals = db.query(Signal).order_by(Signal.timestamp.desc()).limit(10).all()
        
        print(f"{'ID':<5} {'Timestamp':<25} {'Strategy_ID':<30} {'Token':<8} {'TF':<5}")
        print("-" * 80)
        
        for s in signals:
            print(f"{s.id:<5} {str(s.timestamp):<25} {s.strategy_id:<30} {s.token:<8} {s.timeframe:<5}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_signals()
