from sqlalchemy import create_engine, text
import os
import sys

# Add parent directory to path to import database config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.core.config import load_env_if_needed

load_env_if_needed()

from database import DATABASE_URL  # noqa: E402


def fix_schema():
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found.")
        return

    print("🔧 Fixing Database Schema...")

    # Force sync driver
    sync_url = DATABASE_URL.replace("+asyncpg", "")
    if "postgresql" in sync_url and "+" not in sync_url:
        # ensure it uses psycopg2 if default
        pass

    engine = create_engine(sync_url)

    with engine.connect() as conn:
        conn.execute(text("COMMIT"))  # Ensure no transaction is active
        try:
            print("   Dropping table 'signal_evaluations'...")
            conn.execute(text("DROP TABLE IF EXISTS signal_evaluations CASCADE"))
            print("   Dropping table 'signals'...")
            conn.execute(text("DROP TABLE IF EXISTS signals CASCADE"))
            conn.commit()
            print(
                "✅ Tables dropped. Restart the backend to recreate them with new columns."
            )
        except Exception as e:
            print(f"❌ Error dropping tables: {e}")


if __name__ == "__main__":
    fix_schema()
