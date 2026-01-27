
import sys
import os
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from core.schemas import Signal

@dataclass
class StrategyMeta:
    id: str
    name: str
    description: str
    supported_tokens: List[str]
    supported_timeframes: List[str]
    mode: str

def test_signal_creation():
    print("Testing Signal Creation with Pydantic...")
    
    # Simulate Strategy Meta
    meta = StrategyMeta(
        id="trend_following_native_v1",
        name="Trend Fol",
        description="Desc",
        supported_tokens=["BTC"],
        supported_timeframes=["1h"],
        mode="LITE"
    )
    
    # Simulate Data Types from DataFrame
    ts = pd.Timestamp("2023-01-01 12:00:00")
    entry = 1000.50
    tp = 1020.00
    sl = 990.00
    adx_val = 25.5 # float
    conf = 0.85
    
    # Numpy types which often cause issues
    np_adx = np.float64(25.5)
    
    try:
        # Case 1: Standard types
        s1 = Signal(
            timestamp=ts,
            strategy_id=meta.id,
            mode=meta.mode,
            token="BTC",
            timeframe="1h",
            direction="long",
            entry=entry,
            tp=tp,
            sl=sl,
            confidence=conf,
            source="BACKTEST",
            rationale="Test",
            extra={"adx": adx_val}
        )
        print("Case 1 (Standard): OK")
        
        # Case 2: Numpy types in extra
        s2 = Signal(
            timestamp=ts,
            strategy_id=meta.id,
            mode=meta.mode,
            token="BTC",
            timeframe="1h",
            direction="long",
            entry=entry,
            tp=tp,
            sl=sl,
            confidence=conf,
            source="BACKTEST",
            rationale="Test Numpy",
            extra={"adx": np_adx}
        )
        print("Case 2 (Numpy in Extra): OK")
        
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_signal_creation()
