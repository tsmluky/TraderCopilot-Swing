import os
import logging
import asyncio
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from alembic import command
from alembic.config import Config

from dotenv import load_dotenv

# Load env vars immediately to ensure imports (like telegram_listener) see them
load_dotenv()

from database import SessionLocal, engine, Base, get_db
from models_db import User, Signal, SignalEvaluation
from telegram_listener import start_telegram_polling

from routers.auth_new import router as auth_router
from routers.analysis import router as analysis_router
from routers.signals import router as signals_router
from routers.settings import router as settings_router
from routers.webhooks import router as webhooks_router
from routers.billing import router as billing_router
from routers.users import router as users_router
from routers.stats import router as stats_router
from routers.logs import router as logs_router
from routers.strategies import router as strategies_router
from routers.system import router as system_router
from routers.admin import router as admin_router
from routers.alerts import router as alerts_router
from routers.advisor import router as advisor_router

from core.entitlements import get_user_entitlements
from core.trial_policy import get_access_tier
from strategies.registry import load_default_strategies




def setup_logging() -> logging.Logger:
    """
    Logging profesional (console + file).
    - backend/logs/app.log: INFO+
    - backend/logs/error.log: ERROR+
    """
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("tradercopilot")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers on reload
    if logger.handlers:
        return logger

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    fh = RotatingFileHandler(log_dir / "app.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)

    eh = RotatingFileHandler(log_dir / "error.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    eh.setLevel(logging.ERROR)
    eh.setFormatter(fmt)

    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.addHandler(eh)

    # Ensure uvicorn logs propagate
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger_inst = logging.getLogger(name)
        logger_inst.setLevel(logging.INFO)
        logger_inst.propagate = True

    return logger


LOG = setup_logging()

app = FastAPI(
    title="TraderCopilot-Swing API",
    version="1.0.0",
)

# CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log full stack to backend/logs/error.log
    LOG.exception("Unhandled exception | path=%s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


# Routers (MVP runtime set)
app.include_router(auth_router, tags=["Auth"])
app.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
app.include_router(signals_router, prefix="/signals", tags=["Signals"])
app.include_router(settings_router, prefix="/settings", tags=["Settings"])
app.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(stats_router, prefix="/stats", tags=["Stats"])
app.include_router(strategies_router, prefix="/strategies", tags=["Strategies"])
app.include_router(system_router, prefix="/system", tags=["System"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(logs_router, prefix="/logs", tags=["Logs"])
app.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])
app.include_router(advisor_router, prefix="/advisor", tags=["Advisor"])

from fastapi.responses import FileResponse

@app.get("/api/strategies/download_ledger")
def download_ledger(strategy_name: str, period: str, token: str, timeframe: str):
    """
    Serves the pre-computed TXT ledger for a given strategy, period, token, and timeframe.
    Path: backend/data/strategies/{Strategy}/{Period}/{Token}{Timeframe}.txt
    """
    # Sanitize inputs (basic)
    # Sanitize inputs (basic): Titan Breakout -> TitanBreakout
    clean_strategy = strategy_name.replace(" ", "")
    # Map UI names to Directory names if needed, but ideally they match.
    # Strategy Map:
    # "Flow Master" -> "FlowMaster"
    # "Titan Breakout" -> "TitanBreakout" 
    # "Mean Reversion" -> "MeanReversion"
    
    dir_name = clean_strategy.replace(" ", "")
    
    # Period: 6m -> 6M, 2y -> 2Y
    clean_period = period.upper()
    
    # File: ETH4H.txt
    filename = f"{token.upper()}{timeframe.upper()}.txt"
    
    base_dir = Path(__file__).resolve().parent / "data" / "strategies"
    file_path = base_dir / dir_name / clean_period / filename
    
    if not file_path.exists():
        LOG.warning(f"Ledger not found: {file_path}")
        raise HTTPException(status_code=404, detail="Ledger file not found")
        
    return FileResponse(
        path=file_path, 
        filename=f"Ledger_{dir_name}_{token}_{clean_period}.txt",
        media_type='text/plain'
    )


# ====== Database init & Startup ======
@app.on_event("startup")
async def on_startup():
    LOG.info("API startup: init DB + seed strategies")

    # 1) Run Alembic Migrations (Auto-Heal Schema)
    try:
        LOG.info("Running Alembic Migrations...")
        alembic_ini_path = Path(__file__).parent / "alembic.ini"
        alembic_cfg = Config(str(alembic_ini_path))
        
        # FIX: Force DB URL from env if present (Crucial for Production)
        db_url = os.getenv("DATABASE_URL")
        if db_url:
             alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        
        # Point to the script location explicitly to be safe
        alembic_dir = Path(__file__).parent / "alembic"
        alembic_cfg.set_main_option("script_location", str(alembic_dir))
        
        # DEBUG: List versions directory to confirm deployment
        versions_dir = alembic_dir / "versions"
        if versions_dir.exists():
            files = [f.name for f in versions_dir.iterdir()]
            LOG.info(f"Alembic Versions found: {files}")
            
            # NUKE: Clear __pycache__ to prevent ghost revisions
            import shutil
            for pyc in versions_dir.glob("**/__pycache__"):
                shutil.rmtree(pyc, ignore_errors=True)
                LOG.info("Purged __pycache__")
        else:
            LOG.error(f"Alembic Versions dir NOT found: {versions_dir}")
            
        # FIX: Force explicit path to the latest migration instead of generic 'head'
        # This forces Alembic to calculate the path or die trying.
        LOG.info("Forcing upgrade to 'aaaaaaaaaaaa'...")
        command.upgrade(alembic_cfg, "aaaaaaaaaaaa")
        LOG.info("Alembic Migrations completed successfully.")
    except Exception:
        LOG.exception("Alembic Migrations failed!")

    # 2) EMERGENCY PATCH: Raw SQL Fallback (Self-Healing)
    try:
        LOG.info("Running Emergency Schema Patch (Raw SQL)...")
        with engine.connect() as conn:
            sql_check = text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='users' AND column_name='billing_provider'"
            )
            # Safe execution for SQLite/Postgres
            try:
                res = conn.execute(sql_check).scalar()
            except Exception:
                res = None

            if not res:
                LOG.warning("'billing_provider' MISSING. Applying User Schema Patch...")
                # ... (User patching code, keeping existing logic concise or matching original if possible)
                for col_def in [
                    "billing_provider VARCHAR",
                    "stripe_customer_id VARCHAR", 
                    "stripe_subscription_id VARCHAR",
                    "stripe_price_id VARCHAR",
                    "plan_status VARCHAR",
                    "telegram_chat_id VARCHAR",
                    "telegram_username VARCHAR"
                ]:
                     try:
                         col_def.split()[0]
                         conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_def}"))
                     except Exception:
                         pass 

                try:
                    conn.execute(text(
                        "CREATE INDEX IF NOT EXISTS ix_users_stripe_customer_id ON users (stripe_customer_id)"
                    ))
                    conn.execute(text(
                        "CREATE INDEX IF NOT EXISTS ix_users_stripe_subscription_id ON users (stripe_subscription_id)"
                    ))
                except Exception:
                    pass
                
                conn.commit()
                LOG.info("User Schema Patch APPLIED.")
            else:
                LOG.info("User Schema integrity check passed.")

            # === PATCH: Signals Table (Independent Check) ===
            try:
                # Check if is_saved exists
                # SQLite fallback: PRAGMA table_info(signals)
                # But generic approach: Try selecting it.
                # Simplest for SQLite: Just try ADD COLUMN, catch 'duplicate column' error.
                # BUT we need to commit it.
                
                # Let's just try running the ALTER. 
                # SQLite allows ADD COLUMN even if it exists? No, it throws.
                # But Postgres/others throw.
                # We can't rely on information_schema for sqlite easily via SQLA text without exact dialect.
                
                # Just FORCE check via try/except on ADD
                conn.execute(text("ALTER TABLE signals ADD COLUMN is_saved INTEGER DEFAULT 0"))
                conn.commit()
                LOG.info("Signals Schema Patch APPLIED (is_saved added).")
            except Exception:
                # Likely "duplicate column name" -> It exists.
                conn.rollback()
                # LOG.info(f"Signals Schema Patch skipped (likely exists): {e}")
                pass
                
    except Exception:
        LOG.exception("Emergency Schema Patch failed")

    # 3) Start Telegram Bot (Background)
    if os.getenv("RUN_TELEGRAM_BOT") == "true":
        try:
            LOG.info("Starting Telegram Bot (Polling)...")
            threading.Thread(target=start_telegram_polling, daemon=True).start()
        except Exception:
            LOG.exception("Failed to start Telegram Bot")

    Base.metadata.create_all(bind=engine)

    # Ensure registry is loaded for any endpoints relying on it
    try:
        load_default_strategies()
    except Exception:
        LOG.exception("Failed loading default strategies")

    # 3) Telegram Bot Startup (Consolidated)
    args_run_bot = os.getenv("RUN_TELEGRAM_BOT", "false").lower()
    LOG.info(f"Checking Telegram Bot Flag (RUN_TELEGRAM_BOT): {args_run_bot}")

    if args_run_bot == "true":
        try:
            LOG.info("🚀 Starting Telegram Bot (Polling Mode)...")
            import asyncio
            from telegram_listener import start_telegram_bot_async
            
            # Use the running loop to schedule the task
            loop = asyncio.get_event_loop()
            loop.create_task(start_telegram_bot_async())
            LOG.info("Telegram Bot Task scheduled.")
        except Exception:
            LOG.exception("Telegram Bot failed to launch")
    else:
        LOG.info("Telegram Bot is disabled.")

    # Scheduler thread: strictly opt-in (dev-only)
    if os.getenv("RUN_SCHEDULER", "false").lower() in ("1", "true", "yes"):
        def _run():
            try:
                from scheduler import scheduler_instance
                scheduler_instance.run()
            except Exception:
                LOG.exception("Scheduler thread crashed")
        t = threading.Thread(target=_run, daemon=True)
        t.start()
        LOG.warning(
            "Scheduler thread started INSIDE API (RUN_SCHEDULER=true). "
            "Recommended: run scheduler.py as separate process."
        )


# ====== Health ======
@app.get("/health")
def health():
    return {"status": "ok", "ts": datetime.utcnow().isoformat()}


@app.get("/ready")
def ready():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception:
        LOG.exception("Ready check failed")
        raise HTTPException(status_code=500, detail="DB not ready")
    finally:
        db.close()


# ====== Entitlements (legacy convenience) ======
@app.get("/entitlements")
def entitlements(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tier = get_access_tier(user)
    ents = get_user_entitlements(user)
    return {"tier": tier, "entitlements": ents}


# ====== Stats Summary (used by web/app) ======
def compute_stats_summary(db: Session, user: User):
    day_ago = datetime.utcnow() - timedelta(hours=24)
    week_ago = datetime.utcnow() - timedelta(days=7)
    test_sources = ["audit_script", "verification"]

    def apply_filters(q):
        q = q.filter(Signal.source.notin_(test_sources))
        if user.created_at:
            q = q.filter(Signal.timestamp >= user.created_at)
        q = q.filter(Signal.user_id == user.id, Signal.is_saved == 1)
        # avoid noise sources
        q = q.filter(~Signal.source.like("lite-rule%"))
        return q

    # 1) Total evaluated
    q_total = db.query(func.count(SignalEvaluation.id)).join(Signal)
    q_total = apply_filters(q_total)
    total_eval = q_total.scalar() or 0

    # 2) Eval last 24h
    q_eval_24 = db.query(func.count(SignalEvaluation.id)).join(Signal)
    q_eval_24 = apply_filters(q_eval_24).filter(SignalEvaluation.evaluated_at >= day_ago)
    eval_24h_count = q_eval_24.scalar() or 0

    # 3) Wins last 24h
    q_wins = db.query(func.count(SignalEvaluation.id)).join(Signal)
    q_wins = apply_filters(q_wins).filter(
        SignalEvaluation.evaluated_at >= day_ago,
        SignalEvaluation.result == "WIN",
    )
    wins_24h = q_wins.scalar() or 0
    win_rate_24h = (wins_24h / eval_24h_count * 100) if eval_24h_count > 0 else 0

    # 4) Open signals (saved signals without evaluation row)
    open_q = db.query(func.count(Signal.id)).outerjoin(
        SignalEvaluation, SignalEvaluation.signal_id == Signal.id
    )
    open_q = apply_filters(open_q).filter(SignalEvaluation.id.is_(None))
    open_signals_count = int(open_q.scalar() or 0)

    # 5) PnL 7d
    q_pnl = db.query(func.sum(SignalEvaluation.pnl_r)).join(Signal)
    q_pnl = apply_filters(q_pnl).filter(SignalEvaluation.evaluated_at >= week_ago)
    pnl_7d = q_pnl.scalar() or 0.0

    return {
        "win_rate_24h": round(win_rate_24h, 1),
        "signals_evaluated_24h": int(eval_24h_count),
        "signals_total_evaluated": int(total_eval),
        "open_signals": int(open_signals_count),
        "pnl_7d": round(float(pnl_7d), 2),
    }


@app.get("/stats/summary")
def stats_summary(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        return compute_stats_summary(db, user)
    except Exception:
        LOG.exception("stats/summary failed")
        return {
            "win_rate_24h": 0,
            "signals_evaluated_24h": 0,
            "signals_total_evaluated": 0,
            "open_signals": 0,
            "pnl_7d": 0.0,
        }



# Include all routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
app.include_router(signals_router, prefix="/signals", tags=["Signals"])
app.include_router(settings_router, prefix="/settings", tags=["Settings"])
app.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(billing_router, prefix="/billing", tags=["Billing"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(stats_router, prefix="/stats", tags=["Stats"])
app.include_router(logs_router, prefix="/logs", tags=["Logs"])
app.include_router(strategies_router, prefix="/strategies", tags=["Strategies"])
app.include_router(system_router, prefix="/system", tags=["System"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])
app.include_router(advisor_router, prefix="/advisor", tags=["Advisor"])


if __name__ == "__main__":
    import uvicorn

    # Para evitar procesos zombis en Windows, el default es SIN reload.
    reload_flag = os.getenv("UVICORN_RELOAD", "false").lower() in ("1", "true", "yes")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=reload_flag,
    )

