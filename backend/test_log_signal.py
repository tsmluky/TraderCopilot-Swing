import sys
import os
from datetime import datetime
from unittest.mock import MagicMock

# Setup paths
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from core.signal_logger import log_signal
from core.schemas import Signal

def test_log_duplicate():
    # Mocking isn't easy here due to local imports in signal_logger.
    # But we can try to run it against the local DB.
    
    print("Testing duplicate signal logging...")
    
    sig = Signal(
        timestamp=datetime.utcnow(),
        token="TEST_DUP",
        timeframe="1h",
        direction="long",
        entry=100.0,
        tp=110.0,
        sl=90.0,
        confidence=0.9,
        rationale="Test duplicate",
        source="test",
        mode="LITE",
        strategy_id="test_strat",
        user_id=1,
        is_saved=0
    )
    
    # First insert
    id1 = log_signal(sig)
    print(f"First ID: {id1}")
    
    # Second insert (Duplicate)
    id2 = log_signal(sig)
    print(f"Second ID: {id2}")
    
    if id1 == id2 and id1 is not False and id2 is not False:
        print("SUCCESS: Duplicate returned same ID")
    else:
        print(f"FAILURE: ID1={id1}, ID2={id2}")

if __name__ == "__main__":
    test_log_duplicate()
