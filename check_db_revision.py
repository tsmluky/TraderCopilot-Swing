
import sqlite3
import os

DB_PATH = "dev_local.db"

if not os.path.exists(DB_PATH):
    print(f"Error: {DB_PATH} not found.")
else:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT version_num FROM alembic_version")
        version = cursor.fetchone()
        print(f"Current DB Revision: {version[0] if version else 'None'}")
        conn.close()
    except Exception as e:
        print(f"Error reading DB: {e}")
