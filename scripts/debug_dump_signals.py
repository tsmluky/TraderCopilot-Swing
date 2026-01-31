
import sys
import os
from sqlalchemy.orm import Session
# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import SessionLocal
from models_db import Signal, SignalEvaluation

def dump_pending_signals():
    db = SessionLocal()
    try:
        # Find signals without evaluation
        pending = (
            db.query(Signal)
            .outerjoin(SignalEvaluation, Signal.id == SignalEvaluation.signal_id)
            .filter(SignalEvaluation.id.is_(None))
            .order_by(Signal.timestamp.desc())
            .limit(20)
            .all()
        )
        
        print(f"Found {len(pending)} pending signals (showing top 20):")
        print("-" * 80)
        print(f"{'ID':<5} | {'Token':<6} | {'Dir':<5} | {'Entry':<10} | {'TP':<10} | {'SL':<10} | {'Time (UTC)':<20}")
        print("-" * 80)
        
        for s in pending:
            print(f"{s.id:<5} | {s.token:<6} | {s.direction:<5} | {s.entry:<10} | {s.tp:<10} | {s.sl:<10} | {s.timestamp}")
            
    finally:
        db.close()

if __name__ == "__main__":
    dump_pending_signals()
