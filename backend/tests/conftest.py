import os
import pytest

# 1. Force In-Memory DB for all tests immediately
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from main import app
from database import Base, engine, SessionLocal, get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Create tables once for the session.
    With StaticPool, data persists across connections for the process lifetime.
    Also overrides app dependency to use this engine.
    """
    print("[CONFTEST] Creating all tables in in-memory DB...")
    Base.metadata.create_all(bind=engine)
    
    # Global Override for all tests
    def override_get_db_global():
        connection = engine.connect()
        # transaction = connection.begin() 
        # Note: Nested transaction might be tricky with some drivers, 
        # but for sqlite memory + static pool, standard session is fine.
        # However, to be safe, we yield a session bound to this connection.
        db = SessionLocal(bind=connection)
        try:
            yield db
        finally:
            db.close()
            connection.close()

    app.dependency_overrides[get_db] = override_get_db_global
    
    yield
    
    print("[CONFTEST] Dropping all tables...")
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

# Helpers
def _extract_error_code(resp_json):
    if resp_json is None:
        return None
    if isinstance(resp_json, dict):
        if "code" in resp_json and isinstance(resp_json["code"], str):
            return resp_json["code"]
        detail = resp_json.get("detail")
        if isinstance(detail, dict):
            code = detail.get("code")
            if isinstance(code, str):
                return code
        if isinstance(detail, str):
            head = detail.split(":")[0].strip()
            return head or None
    return None

