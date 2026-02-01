import sys
from pathlib import Path
import logging
import io

# Force UTF-8 for Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add backend to path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.append(str(backend_path))

from core.config import load_env_if_needed
load_env_if_needed()

from database import SessionLocal, _ensure_sqlite_users_columns, engine

# Ensure DB schema is patched
_ensure_sqlite_users_columns(engine)
from models_db import User, Signal
from routers.strategies import _calculate_stats
from notify import send_telegram

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verifier")

def verify_stats(db):
    print("\n=== 1. Strategy Stats Verification ===")
    strategies_to_check = [
        ("TITAN_BREAKOUT", "4H"),
        ("FLOW_MASTER", "4H"),
        ("MEAN_REVERSION", "1H")
    ]
    
    for code, tf in strategies_to_check:
        stats = _calculate_stats(db, code, tf)
        print(f"Strategy: {code}_{tf} -> {stats}")

def verify_telegram_users(db):
    print("\n=== 2. Telegram Users Verification ===")
    
    # Check users with Telegram ID
    users = db.query(User).filter(User.telegram_chat_id.isnot(None)).all()
    print(f"Total Users with Telegram Linked: {len(users)}")
    
    for u in users:
        print(f" - User ID: {u.id} | Plan: {u.plan} | Chat: {u.telegram_chat_id}")
        
    return users

def send_test_message(users):
    print("\n=== 3. Sending TEST Alert ===")
    if not users:
        print("❌ No users to test.")
        return

    # Send to the most likely main user (first one found)
    target = users[0] 
    msg = (
        "🧪 <b>Tests Verification</b>\n"
        "This is a test message from TraderCopilot verification script.\n"
        "If you see this, the notification system is CONNECTED."
    )
    
    print(f"Sending test to User {target.id} ({target.telegram_chat_id})...")
    res = send_telegram(msg, chat_id=target.telegram_chat_id)
    print(f"Result: {res}")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        verify_stats(db)
        users = verify_telegram_users(db)
        if len(sys.argv) > 1 and sys.argv[1] == "--send":
            send_test_message(users)
        else:
            print("\n(Skipping send. Run with --send to fire a real alert)")
    finally:
        db.close()
