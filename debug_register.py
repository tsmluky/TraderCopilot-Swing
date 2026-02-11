
import sys
import os
import logging

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)

try:
    from backend.database import SessionLocal, engine, Base
    from backend.models_db import User
    from backend.core.security import get_password_hash
    from datetime import datetime, timedelta
    
    print("Imports successful")
    
    db = SessionLocal()
    print("DB Session created")
    
    email = "debug_reg_2@example.com"
    password = "password123"
    
    # Check if user exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print(f"User {email} already exists. Deleting...")
        db.delete(existing)
        db.commit()
    
    print("Creating new user...")
    hashed_pwd = get_password_hash(password)
    
    new_user = User(
        email=email,
        hashed_password=hashed_pwd,
        name="Debug User",
        plan="FREE",
        plan_expires_at=datetime.utcnow() + timedelta(days=7),
        created_at=datetime.utcnow(),
    )
    
    print("Adding to DB...")
    db.add(new_user)
    print("Committing...")
    db.commit()
    print("Refeshing...")
    db.refresh(new_user)
    
    print(f"User created with ID: {new_user.id}")
    print(f"Disabled strategies: {new_user.disabled_strategies}")
    
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
finally:
    if 'db' in locals():
        db.close()
