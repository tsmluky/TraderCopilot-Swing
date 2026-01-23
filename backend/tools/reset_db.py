import sys
import os

# Ensure backend root is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(current_dir)  # points to .../backend
sys.path.append(backend_root)
from backend.core.config import load_env_if_needed  # noqa: E402

load_env_if_needed()

import asyncio  # noqa: E402
from database import AsyncSessionLocal  # noqa: E402
from sqlalchemy import text  # noqa: E402


async def reset_db():
    print("🧹 Starting Factory Reset...")
    try:
        async with AsyncSessionLocal() as session:
            # 1. Truncate Signal Evaluations
            print("   - Deleting Signal Evaluations...")
            await session.execute(text("DELETE FROM signal_evaluations"))

            # 2. Truncate Signals
            print("   - Deleting Signals...")
            await session.execute(text("DELETE FROM signals"))

            await session.commit()
            print("✅ DB Reset Complete. Clean slate.")

    except Exception as e:
        print(f"❌ Error during reset: {e}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(reset_db())
