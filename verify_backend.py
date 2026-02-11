
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_backend():
    print("Testing Backend...")
    
    # 1. Health Check (OpenAPI)
    try:
        resp = requests.get(f"{BASE_URL}/openapi.json")
        if resp.status_code == 200:
            print("✅ Backend is UP (OpenAPI accessible)")
        else:
            print(f"❌ Backend returned {resp.status_code}")
            return
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # 2. Register User
    email = "test_toggle@example.com"
    password = "password123"
    
    print(f"Registering user {email}...")
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "name": "Test Toggle"
    })
    
    if resp.status_code == 201:
        print("✅ User registered")
    elif resp.status_code == 409:
        print("ℹ️ User already exists (OK)")
    else:
        print(f"❌ Register failed: {resp.text}")
        return

    # 3. Login
    print("Logging in...")
    resp = requests.post(f"{BASE_URL}/auth/token", data={
        "username": email,
        "password": password
    })
    
    if resp.status_code != 200:
        print(f"❌ Login failed: {resp.text}")
        return
        
    token = resp.json()["access_token"]
    print("✅ Login successful")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 4. Get Current User (users/me)
    print("Getting User Profile...")
    resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if resp.status_code != 200:
        print(f"❌ Get Profile failed: {resp.text}")
        return
        
    data = resp.json()
    print(f"✅ User ID: {data['id']}")
    print(f"ℹ️ Disabled Strategies: {data.get('disabled_strategies')}")
    
    # 5. Toggle Strategy
    print("Disabling 'SuperTrend'...")
    payload = {"disabled_strategies": ["SuperTrend_1h"]}
    resp = requests.patch(f"{BASE_URL}/users/me/strategies", json=payload, headers=headers)
    
    if resp.status_code != 200:
        print(f"❌ Update failed: {resp.text}")
        return
        
    print("✅ Update successful")
    
    # 6. Verify Update
    print("Verifying update...")
    resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
    data = resp.json()
    disabled = data.get("disabled_strategies")
    if disabled == ["SuperTrend_1h"]:
        print(f"✅ Verified: {disabled}")
    else:
        print(f"❌ Mismatch: {disabled}")

if __name__ == "__main__":
    test_backend()
