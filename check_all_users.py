
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from database import SessionLocal
from models_db import User

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"{'ID':<5} {'Email':<30} {'Plan':<10} {'Role':<10}")
        print("-" * 60)
        for u in users:
            print(f"{u.id:<5} {u.email:<30} {u.plan:<10} {u.role:<10}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
