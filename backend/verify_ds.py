import os
import sys
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from core.ai_service import get_ai_service  # noqa: E402

# FORCE DEEPSEEK
os.environ["AI_PROVIDER"] = "deepseek"
# Ensure key is present (for printing status, not value)
key = os.getenv("DEEPSEEK_API_KEY")
print(f"DeepSeek Key Present: {bool(key)}")
if key:
    print(f"Key Prefix: {key[:5]}...")

def test_ds():
    try:
        service = get_ai_service()
        print(f"Service Class: {service.__class__.__name__}")
        
        prompt = "Explain why the sky is blue."
        sys_instr = "You are a helpful assistant. OUTPUT JSON: { 'answer': '...' }"
        
        print("Sending request to DeepSeek...")
        res = service.chat([{"role": "user", "content": prompt}], system_instruction=sys_instr)
        
        print("\n--- RESPONSE ---")
        print(res)
        print("----------------")
        
        if "Error" in res and "DEEPSEEK" in res:
             print("❌ DeepSeek API Error detected!")
             sys.exit(1)
             
    except Exception as e:
        print(f"❌ CRASH: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ds()
