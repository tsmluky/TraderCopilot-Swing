
import sqlite3
from database import DATABASE_URL

# Parse the database path (assuming sqlite:///./dev_local.db)
db_path = DATABASE_URL.replace("sqlite:///", "")

print(f"Migrating database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if "telegram_username" not in columns:
        print("Adding column 'telegram_username' to 'users' table...")
        cursor.execute("ALTER TABLE users ADD COLUMN telegram_username TEXT")
        conn.commit()
        print("Migration successful.")
    else:
        print("Column 'telegram_username' already exists.")
        
    conn.close()

except Exception as e:
    print(f"Migration failed: {e}")
