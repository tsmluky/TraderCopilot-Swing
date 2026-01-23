import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in environment.")
    print("Please ensure .env is loaded or DATABASE_URL is set.")
    sys.exit(1)

def fix_schema():
    print("🔌 Connecting to database...")
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        # Check if 'signals' table exists
        if not inspector.has_table("signals"):
            print("❌ Table 'signals' not found. Is the DB initialized?")
            return

        # Get columns
        columns = [col['name'] for col in inspector.get_columns("signals")]
        print(f"📊 Current columns in 'signals': {columns}")

        with engine.connect() as conn:
            # Check for 'is_saved'
            if "is_saved" not in columns:
                print("⚠️ Column 'is_saved' MISSING. Attempting to add it...")
                try:
                    # Postgres/SQLite compatible addition
                    # Default 0 (False)
                    conn.execute(text("ALTER TABLE signals ADD COLUMN is_saved INTEGER DEFAULT 0"))
                    conn.commit()
                    print("✅ SUCCESS: Added 'is_saved' column.")
                except Exception as e:
                    print(f"❌ Failed to add 'is_saved': {e}")
            else:
                print("✅ Column 'is_saved' already exists.")

            # Check for 'is_hidden' (often missing too in older schemas)
            if "is_hidden" not in columns:
                print("⚠️ Column 'is_hidden' MISSING. Attempting to add it...")
                try:
                    conn.execute(text("ALTER TABLE signals ADD COLUMN is_hidden INTEGER DEFAULT 0"))
                    conn.commit()
                    print("✅ SUCCESS: Added 'is_hidden' column.")
                except Exception as e:
                    print(f"❌ Failed to add 'is_hidden': {e}")
            else:
                print("✅ Column 'is_hidden' already exists.")

            # Check for 'extra'
            if "extra" not in columns:
                print("⚠️ Column 'extra' MISSING. Attempting to add it...")
                try:
                    conn.execute(text("ALTER TABLE signals ADD COLUMN extra TEXT"))
                    conn.commit()
                    print("✅ SUCCESS: Added 'extra' column.")
                except Exception as e:
                    print(f"❌ Failed to add 'extra': {e}")
            else:
                print("✅ Column 'extra' already exists.")

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    fix_schema()
