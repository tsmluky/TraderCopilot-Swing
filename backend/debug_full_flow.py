import asyncio
import os
import sys
import traceback
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from core.analysis_logic import _build_lite_from_market, _load_brain_context, _build_pro_analysis  # noqa: E402
from routers.analysis import get_market_data, ProReq  # noqa: E402

async def test_full_flow():
    print("--- START DEBUG FULL FLOW ---")
    token = "BTC"
    timeframe = "1h"
    
    try:
        # 1. Market Data
        print(f"1. Getting Market Data for {token}...")
        _, market = get_market_data(token, timeframe, limit=300)
        print(f"   Market Data Len: {len(market)}")

        # 2. Lite Signal
        print("2. Building Lite Signal...")
        lite_signal, indicators = _build_lite_from_market(token, timeframe, market)
        print(f"   Lite Signal: {lite_signal.direction}")

        # 3. Brain Context
        print("3. Loading Brain Context (RAG)...")
        brain_context = _load_brain_context(token, market_data=market)
        print(f"   Brain Context Keys: {brain_context.keys()}")

        # 4. Pro Analysis (DeepSeek)
        print("4. Running PRO Analysis (DeepSeek)...")
        req = ProReq(token=token, timeframe=timeframe)
        
        # Ensure DeepSeek is active
        os.environ["AI_PROVIDER"] = "deepseek"
        
        # FIX: Actually call the analysis to define 'result'
        result = await _build_pro_analysis(req, lite_signal, indicators, brain_context)
        
        print("5. SUCCESS! Result Type:", type(result))
        
        # 6. VERIFY DB WRITE (The previous crash point)
        print("6. Verifying DB Write (log_signal)...")
        from models import Signal
        from core.signal_logger import log_signal
        
        # Mock signal
        sig = Signal(
            timestamp=datetime.utcnow(),
            strategy_id="debug_pro",
            mode="PRO",
            token=token,
            timeframe=timeframe,
            direction=lite_signal.direction,
            entry=lite_signal.entry,
            tp=lite_signal.tp,
            sl=lite_signal.sl,
            confidence=0.99,
            rationale="Debug Test",
            source="DEBUG",
            extra=result if isinstance(result, dict) else {"raw": str(result)},
            user_id=1 
        )
        
        saved_id = log_signal(sig)
        print(f"   DB Write Result (ID): {saved_id}")
        
        if saved_id is None:
            print("   ⚠️ Note: ID is None (Duplicate or Error), but NO CRASH.")
        else:
            print(f"   ✅ DB Write SUCCESS. ID={saved_id}")

    except Exception:
        print("\n❌ CRASH IN FLOW:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full_flow())
