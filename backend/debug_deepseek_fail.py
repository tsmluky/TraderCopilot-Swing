import asyncio
import os
import sys
import traceback
from dotenv import load_dotenv

# Ensure backend path is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from core.analysis_logic import _build_pro_analysis  # noqa: E402
from models import ProReq, LiteSignal  # noqa: E402
from datetime import datetime  # noqa: E402

async def main():
    print("--- DEBUGGING DEEPSEEK PRO ANALYSIS CRASH ---")
    
    # Mock Inputs
    req = ProReq(token="SOL", timeframe="1h", user_message="Debug crash")
    
    lite_signal = LiteSignal(
        timestamp=datetime.utcnow(),
        token="SOL",
        timeframe="1h",
        direction="long",
        entry=145.0,
        tp=155.0,
        sl=140.0,
        confidence=0.85,
        rationale="Test signal",
        source="debug_script"
    )
    
    indicators = {
        "rsi": 45.0,
        "trend": "BULLISH",
        "ema21": 142.0
    }
    
    brain_context = {
        "news": "SOL network congestion resolved.",
        "sentiment": "Positive",
        "insights": "DeFi activity ATH.",
        "onchain": "TVL rising.",
        "snapshot": "SOL $145"
    }
    
    try:
        print("Calling _build_pro_analysis (Expecting DeepSeek)...")
        # Ensure we are using DeepSeek
        os.environ["AI_PROVIDER"] = "deepseek"
        
        result = await _build_pro_analysis(
            req, lite_signal, indicators, brain_context
        )
        print("✅ Success! Result type:", type(result))
        import json
        print(json.dumps(result, indent=2, default=str))
        
    except Exception:
        print("❌ CRASH DETECTED!")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
