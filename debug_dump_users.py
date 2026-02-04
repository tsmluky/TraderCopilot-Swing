
import sys
import os
from sqlalchemy.orm import Session

# Setup path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import SessionLocal
from models_db import User

def dump_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Total Users: {len(users)}")
        for u in users:
            print(f"ID: {u.id} | Email: {u.email} | Plan: '{u.plan}' | ChatID: {u.telegram_chat_id}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    dump_users()
