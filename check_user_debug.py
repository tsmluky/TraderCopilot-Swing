
import sqlite3
import os

DB_PATH = "dev_local.db"

if not os.path.exists(DB_PATH):
    print(f"Error: {DB_PATH} not found.")
else:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name, role, disabled_strategies FROM users WHERE email='tsmluky@gmail.com'")
        user = cursor.fetchone()
        if user:
            print(f"User Found: ID={user[0]}, Email={user[1]}, Name={user[2]}, Role={user[3]}, Disabled={user[4]}")
        else:
            print("User 'tsmluky@gmail.com' NOT FOUND.")
        
        print("\nAll Users:")
        cursor.execute("SELECT id, email FROM users")
        for u in cursor.fetchall():
            print(f" - {u[0]}: {u[1]}")
            
        conn.close()
    except Exception as e:
        print(f"Error reading DB: {e}")
