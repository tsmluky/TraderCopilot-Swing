
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from main import app
    openapi_schema = app.openapi()
    
    with open('openapi_dump.json', 'w', encoding='utf-8') as f:
        json.dump(openapi_schema, f, indent=2)
        
    print("Successfully wrote openapi_dump.json")
except Exception as e:
    print(f"Error dumping OpenAPI: {e}")
