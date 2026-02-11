
import sqlite3
import os

DB_PATH = "dev_local.db"

if not os.path.exists(DB_PATH):
    print(f"Error: {DB_PATH} not found.")
else:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
        if not cursor.fetchone():
            print("alembic_version table missing! Creating it...")
            cursor.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))")
            cursor.execute("INSERT INTO alembic_version (version_num) VALUES ('bbbbbbbbbbbb')")
        else:
            print("Updating alembic_version to 'bbbbbbbbbbbb'")
            cursor.execute("DELETE FROM alembic_version")
            cursor.execute("INSERT INTO alembic_version (version_num) VALUES ('bbbbbbbbbbbb')")
            
        conn.commit()
        print("Success: DB revision forced to 'bbbbbbbbbbbb'")
        conn.close()
    except Exception as e:
        print(f"Error updating DB: {e}")
