
import os
import sys
from sqlalchemy import text

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database import engine

def cleanup_signals():
    print("🧹 Starting cleanup of invalid signals (TP=0 and SL=0)...")
    
    with engine.connect() as conn:
        try:
            # 1. Count targets
            count_query = text("SELECT COUNT(*) FROM signals WHERE tp = 0 AND sl = 0")
            count = conn.execute(count_query).scalar()
            
            if count == 0:
                print("✅ No invalid signals found.")
                return

            print(f"⚠️  Found {count} invalid signals. Deleting...")

            # 2. Delete dependency (SignalEvaluation) first
            # We use a subquery to find usage
            print("   - Deleting associated SignalEvaluation records...")
            del_evals = text("""
                DELETE FROM signal_evaluations 
                WHERE signal_id IN (
                    SELECT id FROM signals WHERE tp = 0 AND sl = 0
                )
            """)
            res_evals = conn.execute(del_evals)
            
            # 3. Delete Signals
            print("   - Deleting Signals...")
            del_signals = text("DELETE FROM signals WHERE tp = 0 AND sl = 0")
            res_signals = conn.execute(del_signals)
            
            conn.commit()
            print("✅ Cleanup Complete!")
            print(f"   - Removed {res_evals.rowcount} evaluations.")
            print(f"   - Removed {res_signals.rowcount} signals.")

        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            conn.rollback()

if __name__ == "__main__":
    cleanup_signals()
