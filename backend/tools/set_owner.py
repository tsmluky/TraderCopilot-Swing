import sys
import os
import argparse

# Setup Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(current_dir)
sys.path.append(backend_root)

from database import SessionLocal  # noqa: E402
from models_db import User  # noqa: E402


def set_owner(email: str):
    print(f"👑 Promoting {email} to OWNER...")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ User not found: {email}")
            print(
                "   (Ensure you have logged in via the UI at least once to create the record)"
            )
            return

        user.plan = "OWNER"
        user.role = "admin"
        db.commit()
        print(f"✅ Success! {user.email} is now an OWNER.")
        print("   -> Access Admin Panel via sidebar or /admin")
        print("   -> Full API access granted.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("email", help="Email of the user to promote")
    args = parser.parse_args()

    set_owner(args.email)
