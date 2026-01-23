
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database import SessionLocal
from models_db import StrategyConfig

# === CONFIGURATION ===
# Allowed IDs: these are the only ones that should be enabled.
ALLOWED_IDS = {"trend_following_native_v1", "donchian_v2"}
# Experimental (should act as disabled but present)
EXPERIMENTAL_IDS = {"supertrend_flow"}
# All known valid IDs (Enabled or Disabled)
ALL_VALID_IDS = ALLOWED_IDS.union(EXPERIMENTAL_IDS)

def cleanup():
    """
    Idempotent Cleanup for Strategy Configurations.
    1. Disables everything NOT in ALL_VALID_IDS.
    2. Enables ALLOWED_IDS.
    3. Disables EXPERIMENTAL_IDS.
    """
    print("="*60)
    print("🧹 Strategy Cleanup Tool (Swing Pivot)")
    print("="*60)
    
    db = SessionLocal()
    try:
        # 1. Disable Legacy / Invalid
        # Fetch all that are NOT in valid set and are Enabled
        # Actually, simpler loop over all strategies for clarity
        all_configs = db.query(StrategyConfig).all()
        
        for s in all_configs:
            sid = s.strategy_id
            
            if sid in ALLOWED_IDS:
                if s.enabled != 1:
                    print(f"✅ Enabling [CORE]: {sid}")
                    s.enabled = 1
                else:
                    print(f"   [OK] Core enabled: {sid}")
                    
            elif sid in EXPERIMENTAL_IDS:
                if s.enabled != 0:
                    print(f"⚠️ Disabling [EXPERIMENTAL]: {sid}")
                    s.enabled = 0
                else:
                    print(f"   [OK] Experimental disabled: {sid}")
                    
            else:
                # Should be disabled
                if s.enabled != 0:
                    print(f"🚫 Disabling [LEGACY]: {sid}")
                    s.enabled = 0
                else:
                     # Already disabled or fine
                     pass

        db.commit()
        print("\nCleanup Complete synced with DB.")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup()
