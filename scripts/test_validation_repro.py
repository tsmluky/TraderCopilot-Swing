
import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import SessionLocal
from models_db import Signal, SignalEvaluation
from core.signal_evaluator import evaluate_pending_signals
from core.market_data_api import get_current_price

def test_validation_logic():
    db = SessionLocal()
    try:
        print("[TEST] 1. Checking connectivity...")
        # Get BTC price to ensure market data works
        btc_price = get_current_price("BTC")
        print(f"[TEST] Current BTC Price: {btc_price}")
        
        if not btc_price:
            print("[TEST] ❌ CRITICAL: Cannot fetch market data. Validation will fail.")
            return

        print("[TEST] 2. Inserting MOCK Signal (Expected LOSS)...")
        # Insert a signal created 25 hours ago (timeout range) or just use SL logic
        # Long BTC at price + 5% (so current price is WAY below entry -> SL hit)
        entry_price = btc_price * 1.05 
        sl_price = btc_price * 1.02 # SL is also above current price
        
        mock_sig = Signal(
            timestamp=datetime.utcnow() - timedelta(hours=2), # Not timed out, but SL hit
            token="BTC",
            direction="long",
            entry=entry_price,
            tp=entry_price * 1.10,
            sl=sl_price,
            confidence=0.99,
            rationale="TEST_SIGNAL_VALIDATION",
            source="TEST_SCRIPT",
            is_saved=1
        )
        db.add(mock_sig)
        db.commit()
        db.refresh(mock_sig)
        print(f"[TEST] Mock Signal Created ID: {mock_sig.id} (Entry: {entry_price}, SL: {sl_price}, Curr: {btc_price})")
        
        print("[TEST] 3. Running Validator...")
        count = evaluate_pending_signals(db)
        print(f"[TEST] Validator processed {count} signals.")
        
        print("[TEST] 4. Verifying Result...")
        evaluation = db.query(SignalEvaluation).filter(SignalEvaluation.signal_id == mock_sig.id).first()
        
        if evaluation:
            print(f"[TEST] ✅ SUCCESS! Created Evaluation ID: {evaluation.id}")
            print(f"[TEST] Result: {evaluation.result}")
            print(f"[TEST] Exit Price: {evaluation.exit_price}")
            print(f"[TEST] PnL (R): {evaluation.pnl_r}")
        else:
            print(f"[TEST] ❌ FAILURE! No evaluation created for Signal {mock_sig.id}")
            
            # Debug: Why?
            # Check timestamps
            print(f"DEBUG: Signal Timestamp: {mock_sig.timestamp}")
            print(f"DEBUG: Now: {datetime.utcnow()}")
            
    except Exception as e:
        print(f"[TEST] 💥 EXCEPTION: {e}")
    finally:
        # Cleanup
        if 'mock_sig' in locals():
            print("[TEST] Cleaning up test signal...")
            db.delete(mock_sig)
            db.commit()
        db.close()

if __name__ == "__main__":
    test_validation_logic()
