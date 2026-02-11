import os
import sys
from dotenv import load_dotenv

# Load env from backend/.env
load_dotenv(".env")

# Add current dir to path to import notify
sys.path.append(os.getcwd())

from notify import send_telegram

def test_alert():
    print("Testing Telegram Alert...")
    token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TRADERCOPILOT_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    print(f"Token: {'Set' if token else 'MISSING'}")
    print(f"Chat ID (Env): {chat_id}")
    
    if not token:
        print("Error: No bot token found in .env")
        return

    msg = "🚀 <b>TEST ALERT</b>\nThis is a manual test from the backend.\nIf you see this, automatic alerts <i>should</i> work if the scheduler finds a signal."
    
    try:
        # Try sending to env ID first
        if chat_id:
            print(f"Sending to Default Chat ID: {chat_id}")
            res = send_telegram(msg, chat_id=chat_id)
            print(f"Result: {res}")
        else:
            print("No TELEGRAM_CHAT_ID in .env")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_alert()
