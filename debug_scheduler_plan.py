import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Load env (though we run this locally)
load_dotenv()

from backend.core.entitlements import PLANS
from backend.strategies.registry import get_registry, load_default_strategies
from backend.scheduler import StrategyScheduler

def debug_mapping():
    print("=== SCHEDULER DEBUG UTILITY ===")
    
    # 1. Load Registry
    try:
        load_default_strategies()
    except Exception as e:
        print(f"ERROR loading strategies: {e}")
        return

    registry = get_registry()
    print(f"\n[REGISTRY] Registered Strategies: {list(registry._strategies.keys())}")
    
    # 2. Check Scheduler Logic
    scheduler = StrategyScheduler()
    # It has existing mapping log we want to check or we can just inspect the hardcoded dict
    
    # Copy from scheduler.py
    impl_map = {
        "TITAN_BREAKOUT": "donchian_v2",
        "FLOW_MASTER": "trend_following_native_v1",
        "MEAN_REVERSION": "mean_reversion_rsi_v1"
    }
    
    print("\n[MAPPING CHECK]")
    for code, impl_id in impl_map.items():
        exists = impl_id in registry._strategies
        status = "✅ OK" if exists else "❌ MISSING"
        print(f"  {code} -> {impl_id} : {status}")
        
    # 3. Simulate Tasks
    print("\n[TASK SIMULATION]")
    now = datetime.utcnow()
    tasks = scheduler.get_execution_tasks(now)
    print(f"  Total Tasks Generated: {len(tasks)}")
    
    if tasks:
        print(f"  First Task: {tasks[0]}")
        
    print("\n=== END DEBUG ===")

if __name__ == "__main__":
    debug_mapping()
