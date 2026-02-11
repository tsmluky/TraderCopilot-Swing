
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    from backend.models_db import User
    print("Successfully imported User")
    
    u = User(
        email="test@test.com",
        name="Test User",
        role="user",
        plan="FREE",
        plan_status="active"
    )
    print("Successfully instantiated User with name, role, plan_status")
    print(f"User: {u.name}, {u.role}")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
