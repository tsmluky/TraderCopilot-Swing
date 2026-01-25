
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models_db import User

def set_pro_plan(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User {email} not found!")
            return

        print(f"Found user: {user.email}")
        print(f"Current Plan: {user.plan}, Role: {user.role}")

        # Set to PRO
        user.plan = "PRO"
        # Role usually stays 'user' for normal customers, 'admin' implies OWNER access usually.
        # But let's set role to 'user' to simulate a real customer.
        user.role = "user" 
        
        db.commit()
        db.refresh(user)
        
        print(f"Updated Plan: {user.plan}, Role: {user.role}")
        print("Success!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    set_pro_plan("tsmluky@gmail.com")
