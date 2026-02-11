
import sqlite3
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("password")

conn = sqlite3.connect("dev_local.db")
cursor = conn.cursor()

email = "tsmluky@gmail.com"

# Check existence
cursor.execute("SELECT id FROM users WHERE email=?", (email,))
exists = cursor.fetchone()

if exists:
    print("User exists. Updating password...")
    cursor.execute("UPDATE users SET hashed_password=?, role='admin' WHERE email=?", (hashed, email))
else:
    print("Creating user...")
    cursor.execute("""
        INSERT INTO users (email, hashed_password, name, role, plan, disabled_strategies, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (email, hashed, "Lukx", "admin", "OWNER", "[]", datetime.utcnow()))

conn.commit()
conn.close()
print("Done. User tsmluky@gmail.com password set to 'password'.")
