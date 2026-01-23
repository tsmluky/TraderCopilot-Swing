import pytest
import random
import string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from main import app
from database import Base, get_db
from models_db import User

# Setup In-Memory DB for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db



@pytest.fixture(scope="module", autouse=True)
def setup_db():
    print(f"[TEST DEBUG] Creating tables: {Base.metadata.tables.keys()} (User table: {User.__tablename__})")
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)


def test_auth_flow_complete():
    # 1. Register (Randomize to avoid conflict)
    rand_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    email = f"test_auth_{rand_suffix}@example.com"
    password = "password123"

    print(f"Registering {email}...")
    reg_payload = {"email": email, "password": password, "name": "Auth Tester"}
    response = client.post("/auth/register", json=reg_payload)
    assert response.status_code == 201, f"Register failed: {response.text}"

    # 2. Login
    login_data = {"username": email, "password": password}
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    assert token is not None

    # 3. Verify Advisor Access (Protected)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/advisor/profile", headers=headers)
    assert response.status_code == 200, f"Profile access failed: {response.text}"

    # 4. Verify Context Endpoint (Requires Auth)
    response = client.get("/auth/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == email
