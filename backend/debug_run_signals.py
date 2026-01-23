import sys
import os
import time
from pathlib import Path

# Setup path to ensure imports work
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Mock Environment if needed (though .env should be loaded by main modules)
os.environ["DATABASE_URL"] = "sqlite:///backend/dev_local.db"

from scheduler import StrategyScheduler, get_active_strategies_from_db
from database import SessionLocal
from models_db import Signal

def run_debug_cycle():
    print("="*60)
    print(" [DEBUG] SIGNAL GENERATION SINGLE-SHOT TRIGGERS")
    print("="*60)

    try:
        scheduler = StrategyScheduler(loop_interval=0)
    except Exception as e:
        print(f"Failed to init scheduler: {e}")
        return

    # 1. Fetch Strategies
    personas = get_active_strategies_from_db()
    print(f"\n[INFO] Found {len(personas)} active strategies in DB.")
    
    if not personas:
        print("❌ No active strategies found! Check database or run 'force_active_strategies.py'.")
        return

    total_signals = 0
    generated_details = []

    # 2. Sequential Execution (easier to debug than ThreadPool for this script)
    for p in personas:
        print(f"\n🔹 Running: {p['name']} ({p['id']})...")
        print(f"   tokens: {p['tokens']}")
        print(f"   timeframe: {p['timeframe']}")
        
        start_t = time.time()
        try:
            signals = scheduler._execute_strategy_task(p)
            duration = time.time() - start_t
            
            if signals:
                print(f"   ✅ Generated {len(signals)} signals in {duration:.2f}s")
                for s in signals:
                    print(f"      -> {s.token} {s.direction.upper()} @ {s.entry}")
                    
                    # Manually persist since _execute_strategy_task doesn't do it
                    # (The scheduler does it in step 3)
                    scheduler.process_single_signal(s, p)
                    generated_details.append(f"{p['id']}: {s.token} {s.direction}")
                    total_signals += 1
            else:
                print(f"   ⚪ No signals (Conditions not met) - {duration:.2f}s")

        except Exception as e:
            print(f"   ❌ CRASH: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*60)
    print(f" [SUMMARY] Total Signals Generated: {total_signals}")
    print("="*60)
    if generated_details:
        print("Signals:")
        for d in generated_details:
            print(f" - {d}")

if __name__ == "__main__":
    run_debug_cycle()
