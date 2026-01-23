import sys
import os
import shutil

# Add backend to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base


def manual_reset():
    """
    FACTORY RESET: Borra la base de datos y logs.
    Usage: python reset_db_manual.py
    """
    print("!!! INITIATING MANUAL FACTORY RESET !!!")
    confirm = input("Are you sure? This will WIPE ALL DATA. (yes/no): ")
    if confirm.lower() != "yes":
        print("Aborted.")
        return

    # 1. Drop tables
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("DB Tables dropped and recreated.")
    except Exception as e:
        print(f"Error resetting DB: {e}")

    # 2. Clear Logs CSV Folder
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    if os.path.exists(logs_dir):
        try:
            shutil.rmtree(logs_dir)
            os.makedirs(logs_dir, exist_ok=True)
            print("Logs folder wiped.")
        except Exception as e:
            print(f"Error wiping logs: {e}")

    print("System Factory Reset Complete.")


if __name__ == "__main__":
    manual_reset()
