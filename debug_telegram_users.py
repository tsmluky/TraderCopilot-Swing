
import sys
import os
from sqlalchemy.orm import Session

# Setup path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import SessionLocal
from models_db import User

def check_telegram_users():
    db = SessionLocal()
    try:
        print("Checking Telegram Subscribers...")
        
        # Test PRO
        plans_pro = ["PRO", "SWINGPRO", "PREMIUM", "OWNER", "ADMIN"]
        users_pro = db.query(User).filter(
            User.plan.in_(plans_pro),
            User.telegram_chat_id.isnot(None)
        ).all()
        print(f"PRO Users with Telegram: {len(users_pro)}")
        for u in users_pro:
            print(f"  - {u.email} ({u.plan}) -> ChatID: {u.telegram_chat_id}")
            
        # Test TRADER
        plans_trader = ["TRADER", "FREE", "LITE", "SWINGLITE"]
        users_trader = db.query(User).filter(
            User.plan.in_(plans_trader),
            User.telegram_chat_id.isnot(None)
        ).all()
        print(f"TRADER Users with Telegram: {len(users_trader)}")
        for u in users_trader:
            print(f"  - {u.email} ({u.plan}) -> ChatID: {u.telegram_chat_id}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_telegram_users()
