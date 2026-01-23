import sys
import os
import json
from sqlalchemy import create_engine, text
from pywebpush import webpush, WebPushException

# Configurar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.core.config import load_env_if_needed

load_env_if_needed()

from database import DATABASE_URL  # noqa: E402

VAPID_PRIVATE = os.getenv("VAPID_PRIVATE_KEY")
VAPID_MAIL = os.getenv("VAPID_MAIL", "mailto:test@test.com")


def diagnose():
    print("🕵️  STARTING DEEP SYSTEM DIAGNOSIS...\n")

    # 1. DATABASE CONNECTION
    print("1️⃣  Checking Database...")
    if not DATABASE_URL:
        print("   ❌ DATABASE_URL is missing!")
        return

    try:
        # Force sync
        sync_url = DATABASE_URL.replace("+asyncpg", "")
        engine = create_engine(sync_url)
        with engine.connect() as conn:
            # Check Tables
            tables = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
                )
            ).fetchall()
            table_names = [t[0] for t in tables]
            print(f"   ✅ DB Connected. Tables found: {table_names}")

            # Check Strategies
            if "strategy_configs" in table_names:
                strats = conn.execute(
                    text("SELECT strategy_id, enabled, name FROM strategy_configs")
                ).fetchall()
                print(f"   📊 Strategies Configured ({len(strats)}):")
                for s in strats:
                    print(
                        f"      - {s[0]}: {'🟢 Enabled' if s[1] else '🔴 Disabled'} ({s[2]})"
                    )

            # Check Subscriptions for Push
            if "push_subscriptions" in table_names:
                subs = conn.execute(text("SELECT * FROM push_subscriptions")).fetchall()
                print(f"   🔔 Push Subscriptions: {len(subs)}")
                if len(subs) == 0:
                    print(
                        "      ⚠️  No subscriptions found! Frontend hasn't registered properly."
                    )
            else:
                print("   ❌ 'push_subscriptions' table is MISSING!")

    except Exception as e:
        print(f"   ❌ DB Connection Failed: {e}")
        return

    # 2. VAPID KEYS
    print("\n2️⃣  Checking Notification Keys...")
    if not VAPID_PRIVATE:
        print("   ❌ VAPID_PRIVATE_KEY is missing in env!")
    else:
        print("   ✅ VAPID Private Key is present.")

    # 3. TEST PUSH RECOVERY
    print("\n3️⃣  Testing Notification Delivery (Mock)...")
    if "push_subscriptions" in table_names and len(subs) > 0:
        print(f"   Attempting to send test push to {len(subs)} devices...")
        try:
            # Try sending to first sub manually
            sub = subs[0]
            # sub is tuple: (id, endpoint, p256dh, auth, created_at) - adjust based on schema
            # Assuming schema: id(0), endpoint(1), p256dh(2), auth(3) ...

            payload = json.dumps(
                {
                    "title": "Test Diagnosis",
                    "body": "If you see this, push works!",
                    "icon": "/icon-192.png",
                }
            )

            webpush(
                subscription_info={
                    "endpoint": sub[1],
                    "keys": {"p256dh": sub[2], "auth": sub[3]},
                },
                data=payload,
                vapid_private_key=VAPID_PRIVATE,
                vapid_claims={"sub": VAPID_MAIL},
            )
            print("   ✅ Test notification SENT successfully.")
        except WebPushException as e:
            print(f"   ❌ WebPush Error: {e}")
            print(
                f"      (Status: {e.response.status_code if e.response else 'Unknown'})"
            )
        except Exception as e:
            print(f"   ❌ Generic Push Error: {e}")
    else:
        print("   ⚠️  Skipping push test (no subscribers).")

    print("\n✅ Diagnosis Complete.")


if __name__ == "__main__":
    diagnose()
