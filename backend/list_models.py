
import os
import requests
from dotenv import load_dotenv

from pathlib import Path

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment.")
    exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        print(f"{'NAME':<50} | {'DISPLAY NAME':<30} | {'VERSION'}")
        print("-" * 100)
        
        found = []
        for m in data.get("models", []):
            name = m.get("name", "").replace("models/", "")
            if "flash" in name.lower() or "pro" in name.lower() or "lite" in name.lower():
                found.append(name)
                print(f"{name:<50} | {m.get('displayName', ''):<30} | {m.get('version', '')}")
        
        print("\n--- Summary of Likely Candidates ---")
        for f in sorted(found):
            print(f"- {f}")
            
    else:
        print(f"Error {resp.status_code}: {resp.text}")
except Exception as e:
    print(f"Request Failed: {e}")
