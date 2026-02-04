
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from datetime import datetime

# Setup path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import get_db, SessionLocal
from models_db import Signal

def check_is_saved():
    db = SessionLocal()
    try:
        print("Fetching top 5 recent signals...")
        signals = db.query(Signal).order_by(Signal.timestamp.desc()).limit(5).all()
        
        print(f"{'ID':<5} {'Timestamp':<25} {'Strategy_ID':<30} {'Token':<6} {'Start':<5} {'Saved?':<6}")
        print("-" * 85)
        
        for s in signals:
            print(f"{s.id:<5} {str(s.timestamp):<25} {s.strategy_id:<30} {s.token:<6} {s.timeframe:<5} {s.is_saved:<6}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_is_saved()
