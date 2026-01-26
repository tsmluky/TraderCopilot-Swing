import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.security import verify_password, get_password_hash

def test_bcrypt_behavior():
    print("Testing Bcrypt/Passlib behavior...")
    
    # 1. Test Hash
    pwd = "password123"
    hashed = get_password_hash(pwd)
    print(f"Hash success: {hashed}")
    
    # 2. Test Verify (Correct)
    valid = verify_password(pwd, hashed)
    print(f"Verify Correct: {valid}")
    assert valid is True
    
    # 3. Test Verify (Wrong)
    invalid = verify_password("wrongpass", hashed)
    print(f"Verify Incorrect (Expected False): {invalid}")
    assert invalid is False
    
    # 4. Test Long Password (72+ chars)
    long_pwd = "a" * 100
    try:
        hashed_long = get_password_hash(long_pwd)
        print("Long hash success")
        # Verify long
        valid_long = verify_password(long_pwd, hashed_long)
        print(f"Long Verify: {valid_long}")
    except Exception as e:
        print(f"Long hash failed: {e}")

if __name__ == "__main__":
    test_bcrypt_behavior()
