import sqlite3
import os
import sys

# Define database path
DB_PATH = "dev_local.db"

def migrate_sqlite():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database file {DB_PATH} not found.")
        sys.exit(1)

    print(f"[INFO] Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Define columns to add
    COLUMNS_TO_ADD = {
        "billing_provider": "VARCHAR",
        "stripe_customer_id": "VARCHAR",
        "stripe_subscription_id": "VARCHAR",
        "stripe_price_id": "VARCHAR",
        "plan_status": "VARCHAR"
    }

    # Get existing columns
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # Add missing columns
    for col_name, col_type in COLUMNS_TO_ADD.items():
        if col_name not in existing_columns:
            print(f"[ACTION] Adding column {col_name} ({col_type})...")
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                print(f"[SUCCESS] Added {col_name}.")
            except sqlite3.OperationalError as e:
                print(f"[ERROR] Could not add {col_name}: {e}")
        else:
            print(f"[SKIP] Column {col_name} already exists.")

    # Create Indices
    INDICES = {
        "ix_users_stripe_customer_id": "stripe_customer_id",
        "ix_users_stripe_subscription_id": "stripe_subscription_id"
    }
    
    # Get existing indices to avoid error (though IF NOT EXISTS handles it usually, explicit check is nice)
    # But SQLite 'CREATE INDEX IF NOT EXISTS' is supported in modern versions. checking version...
    # We will just use IF NOT EXISTS.

    for idx_name, col_name in INDICES.items():
        print(f"[ACTION] Creating index {idx_name} on {col_name}...")
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON users({col_name})")
            print(f"[SUCCESS] Index {idx_name} processed.")
        except Exception as e:
            print(f"[ERROR] Failed to create index {idx_name}: {e}")

    conn.commit()
    conn.close()
    print("[DONE] Migration finished.")

if __name__ == "__main__":
    migrate_sqlite()
