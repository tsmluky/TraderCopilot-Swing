import sys
import os
from pathlib import Path
from datetime import datetime

# Setup path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Force DB connection
os.environ["DATABASE_URL"] = "sqlite:///backend/dev_local.db"

from database import SessionLocal  # noqa: E402
from models_db import Signal, StrategyConfig  # noqa: E402

def seed_test_signal():
    db = SessionLocal()
    try:
        # Find an active strategy to attribute this signal to
        strat = db.query(StrategyConfig).filter(StrategyConfig.enabled == 1).first()
        if not strat:
            print("No active strategy found. Enable one first.")
            return

        print(f"Attributing signal to: {strat.name} ({strat.persona_id})")

        # Create Signal
        # Make it recent
        new_signal = Signal(
            timestamp=datetime.utcnow(),
            source=f"Marketplace:{strat.persona_id}", # MUST match format expected by filters
            strategy_id=strat.persona_id,
            mode="PRO",
            token="BTC",
            timeframe="4h",
            direction="long",
            entry=95000.0,
            tp=100000.0,
            sl=90000.0,
            confidence=0.95,
            rationale="TEST SIGNAL: Manual injection for UI verification. Double bottom pattern detected.",
            is_saved=1
        )

        db.add(new_signal)
        db.commit()
        db.refresh(new_signal)
        
        print(f"✅ Injected Signal ID: {new_signal.id}")
        print("Go to Dashboard to verify.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_test_signal()
