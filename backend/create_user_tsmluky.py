
import sys
import os

# Ensure we can import from local modules
sys.path.append(os.getcwd())

from database import SessionLocal
from models_db import User
from routers.auth_new import get_password_hash

def create_user():
    db = SessionLocal()
    email = "tsmluky@gmail.com"
    password = "password"
    
    # Check if exists (paranoia check)
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print(f"User {email} already exists. Updating password...")
        existing.hashed_password = get_password_hash(password)
        db.commit()
        print("Password updated to 'password'")
        return

    print(f"Creating user {email}...")
    new_user = User(
        email=email,
        name="Lukx",
        hashed_password=get_password_hash(password),
        role="admin",
        plan="OWNER",
        disabled_strategies="[]"
    )
    db.add(new_user)
    db.commit()
    print(f"User {email} created with password '{password}'")
    db.close()

if __name__ == "__main__":
    create_user()
