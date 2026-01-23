import os
os.environ["DATABASE_URL"] = "sqlite:///backend/dev_local.db"

from database import SessionLocal
from models_db import StrategyConfig

def force_cleanup():
    db = SessionLocal()
    try:
        print("Cleaning up strategies...")
        
        # 1. Disable ALL
        rows_affected = db.query(StrategyConfig).update({StrategyConfig.enabled: 0})
        print(f"Disabled {rows_affected} strategies.")
        
        # 2. Enable Targets
        targets = ["trend_following_native_v1", "donchian_v2"]
        
        # Note: If strategy_id is used for lookup
        for t in targets:
            config = db.query(StrategyConfig).filter(StrategyConfig.strategy_id == t).first()
            if config:
                config.enabled = 1
                print(f"✅ Enabled: {t}")
            else:
                print(f"⚠️ Warning: Target strategy '{t}' not found in DB!")
                
        db.commit()
        
        # 3. Verify
        print("\n=== FINAL STATE ===")
        active = db.query(StrategyConfig).filter(StrategyConfig.enabled == 1).all()
        for a in active:
            print(f"ACTIVE: {a.strategy_id} ({a.name})")
            
        if len(active) == 2:
            print("\nSUCCESS: Strict 2 strategies active.")
        else:
            print(f"\nRESULT: {len(active)} strategies active (Expected 2).")

    finally:
        db.close()

if __name__ == "__main__":
    force_cleanup()
