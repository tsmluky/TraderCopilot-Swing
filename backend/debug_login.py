
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models_db import User
from database import DATABASE_URL
from core.trial_policy import get_access_tier, is_trial_active
from core.entitlements import get_plan_entitlements
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_login_logic():
    print(f"Connecting to DB: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Find a user to test
        user = db.query(User).first()
        if not user:
            print("No users found in DB")
            return

        print(f"Testing User: {user.email}")
        print(f"Plan: {user.plan}, Role: {getattr(user, 'role', 'N/A')}")
        print(f"Created At: {user.created_at}, Plan Expires At: {user.plan_expires_at}")

        # Test Trial Policy Logic
        tier = get_access_tier(user)
        print(f"Calculated Tier: {tier}")
        
        is_trial = is_trial_active(user)
        print(f"Is Trial Active: {is_trial}")

        # Test Entitlements Logic
        ent = get_plan_entitlements(tier)
        print(f"Entitlements: {ent}")

        # Test Auth Response Construction (simulating auth_new.py)
        # Just accessing them to verify they exist/don't crash
        _ = (getattr(user, "plan", None) or "FREE").upper()
        _ = getattr(user, "role", "user")
        
        print("Auth Logic Success!")

    except Exception:
        logger.exception("Debug Login Failed!")
    finally:
        db.close()

if __name__ == "__main__":
    debug_login_logic()
