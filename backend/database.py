import os
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base


def _normalize_sync_db_url(url: str) -> str:
    if not url:
        return "sqlite:///./dev_local.db"

    # Normalize common async drivers to sync URLs for runtime
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    url = url.replace(
        "postgres://", "postgresql://"
    )  # Fix for Railway/Heroku legacy format
    url = url.replace("sqlite+aiosqlite://", "sqlite://")

    # If someone provided a sync sqlite URL, keep it
    # If someone provided postgresql:// already, keep it
    return url


from sqlalchemy.pool import StaticPool  # noqa: E402

# NOTE: Environment should be loaded BEFORE importing this module via core.config.load_env_if_needed()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev_local.db")
SYNC_DATABASE_URL = _normalize_sync_db_url(DATABASE_URL)

print(f"[DB DEBUG] Original URL starts with: {DATABASE_URL[:16]}...")
print(f"[DB DEBUG] Final URL starts with: {SYNC_DATABASE_URL[:28]}...")
print("[DB] Using Configured Database")

connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,
}

if SYNC_DATABASE_URL.startswith("sqlite://"):
    # Needed for SQLite in multi-threaded FastAPI
    connect_args = {"check_same_thread": False}

    # Critical for In-Memory usage: Maintain single connection
    if ":memory:" in SYNC_DATABASE_URL:
        engine_kwargs["poolclass"] = StaticPool
    else:
        # [HARDENING] SQLite Dialect Optimization
        # Large pools in SQLite can cause 'database is locked' under high write concurrency.
        # We use a very conservative pool for SQLite to allow multiple readers but minimize contention.
        # Postgres, however, thrives on larger pools.
        engine_kwargs["pool_size"] = 5  # Reduced from 20 for SQLite safety
        engine_kwargs["max_overflow"] = 10

else:
    # Postgres / Other: High Performance Pool
    engine_kwargs["pool_size"] = 20
    engine_kwargs["max_overflow"] = 10
# --- STABLE_SQLITE_PATH ---
try:
    if isinstance(DATABASE_URL, str) and DATABASE_URL.startswith("sqlite:///"):
        p = DATABASE_URL[len("sqlite:///"):]
        # Si es relativo (./file o file sin drive), anclar a backend/
        if p.startswith("./") or (":/" not in p and not p.startswith("/")):
            rel = p[2:] if p.startswith("./") else p
            base = Path(__file__).resolve().parent
            abs_p = (base / rel).resolve()
            DATABASE_URL = "sqlite:///" + abs_p.as_posix()
except Exception:
    pass
# --- END STABLE_SQLITE_PATH ---
# --- ENGINE BUILDER ---
def get_engine():
    """
    Singleton-like getter for the engine.
    This ensures that we use the latest env var (useful for tests patching os.environ).
    """
    url = os.getenv("DATABASE_URL", "sqlite:///./dev_local.db")
    url = _normalize_sync_db_url(url)
    
    connect_args = {}
    engine_kwargs = {
        "pool_pre_ping": True,
    }

    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        
        if ":memory:" in url:
            from sqlalchemy.pool import StaticPool
            engine_kwargs["poolclass"] = StaticPool
        else:
            # File-based SQLite optimizations
            engine_kwargs["pool_size"] = 5
            engine_kwargs["max_overflow"] = 10
    else:
        # Postgres optimizations
        engine_kwargs["pool_size"] = 20
        engine_kwargs["max_overflow"] = 10

    return create_engine(url, connect_args=connect_args, **engine_kwargs)

# Global Engine instance
engine = get_engine()

# Global SessionLocal
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
# === WAL Mode Enablement (SQLite) ===
if SYNC_DATABASE_URL.startswith("sqlite://") and ":memory:" not in SYNC_DATABASE_URL:
    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")  # Balance safety/speed
        cursor.close()


Base = declarative_base()
# ---------------------------
# DEV: SQLite schema patcher
# ---------------------------
_SQLITE_USERS_PATCH_DONE = False

def _ensure_sqlite_users_columns(engine) -> None:
    global _SQLITE_USERS_PATCH_DONE
    if _SQLITE_USERS_PATCH_DONE:
        return
    try:
        if engine.dialect.name != "sqlite":
            _SQLITE_USERS_PATCH_DONE = True
            return

        insp = inspect(engine)
        if not insp.has_table("users"):
            _SQLITE_USERS_PATCH_DONE = True
            return

        cols = {c.get("name") for c in (insp.get_columns("users") or [])}

        wanted = {
            "billing_provider": "VARCHAR",
            "stripe_customer_id": "VARCHAR",
            "stripe_subscription_id": "VARCHAR",
            "stripe_price_id": "VARCHAR",
            "plan_status": "VARCHAR",
        }

        with engine.begin() as conn:
            for name, sqltype in wanted.items():
                if name not in cols:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {name} {sqltype}"))
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS ix_users_stripe_customer_id "
                     "ON users(stripe_customer_id)")
            )
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS ix_users_stripe_subscription_id "
                     "ON users(stripe_subscription_id)")
            )

        _SQLITE_USERS_PATCH_DONE = True
        print("[DB] SQLite users schema patched (billing/stripe columns ensured).")
    except Exception as e:
        # No bloquear arranque en dev
        print(f"[DB] SQLite users schema patch skipped/failed: {e}")
        _SQLITE_USERS_PATCH_DONE = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



