
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from strategies.registry import get_registry, load_default_strategies
from strategies.DonchianBreakoutV2 import DonchianBreakoutV2

def test_instantiation():
    print("Loading strategies...")
    load_default_strategies()
    registry = get_registry()
    
    print("Getting strategy instance...")
    strategy = registry.get("donchian_v2")
    print(f"Strategy: {strategy}, Type: {type(strategy)}")
    
    if strategy is None:
        print("ERROR: Strategy not found")
        return

    print("Checking generate_signals method...")
    if hasattr(strategy, 'generate_signals'):
        print(f"Method found: {strategy.generate_signals}")
    else:
        print("ERROR: generate_signals not found")

    print("Attempting to call generate_signals...")
    try:
        # Pseudo-call
        signals = strategy.generate_signals(tokens=["BTC"], timeframe="1h")
        print(f"Success! Signals: {signals}")
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

    print("Checking for accidental callability...")
    try:
        strategy()
        print("Strategy object IS callable (Unexpected!)")
    except TypeError as e:
        print(f"Strategy object is NOT callable (Expected): {e}")

if __name__ == "__main__":
    test_instantiation()
