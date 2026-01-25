
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal, engine, Base
from models_db import User
from routers.auth_new import seed_default_strategies

def init_db():
    Base.metadata.create_all(bind=engine)

def test_strategy_persistence():
    init_db()
    db = SessionLocal()
    try:
        # 1. Setup Mock User
        email = "test_repro@example.com"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Creating test user {email}...")
            user = User(email=email, hashed_password="x", name="Test", role="user", plan="PRO")
            db.add(user)
            db.commit()
            db.refresh(user)
            # Seed
            seed_default_strategies(db, user)
        
        print(f"User ID: {user.id}")

        # 2. Fetch Strategies (Titan SOL and Flow Master BTC)
        # IDs based on logic: titan_sol_{uid}, flow_btc_{uid}

        if not s1 or not s2:
            print("❌ Strategies not found. Seeding failed?")
            return

        # 3. Simulate: Enable Titan SOL in 4H
        print(f"--- Action 1: Enable {s1.name} SOL (4H) ---")
        s1.timeframes = json.dumps(["4h"])
        s1.enabled = 1
        db.commit()

        # Verify
        db.refresh(s1)
        print(f"S1 State: Enabled={s1.enabled}, Timeframe={s1.timeframes}")
        assert s1.enabled == 1
        assert "4h" in s1.timeframes.lower()

        # 4. Simulate: Enable Flow BTC in 1D
        print(f"--- Action 2: Enable {s2.name} BTC (1D) ---")
        s2.timeframes = json.dumps(["1d"])
        s2.enabled = 1
        db.commit()

        # Verify S2 works
        db.refresh(s2)
        print(f"S2 State: Enabled={s2.enabled}, Timeframe={s2.timeframes}")
        assert s2.enabled == 1
        assert "1d" in s2.timeframes.lower()

        # 5. CRITICAL: Verify S1 is STILL Enabled
        db.refresh(s1)
        print("--- Verification: checking S1 state after S2 update ---")
        print(f"S1 State: Enabled={s1.enabled}, Timeframe={s1.timeframes}")
        
        if s1.enabled != 1:
            print("❌ FAILURE: S1 was disabled when S2 was enabled!")
        else:
            print("✅ SUCCESS: S1 remained active.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_strategy_persistence()

