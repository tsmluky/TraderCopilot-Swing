import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import threading

from database import SessionLocal, engine, Base, get_db
from models_db import User, Signal, SignalEvaluation

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
from telegram_listener import start_telegram_polling

load_dotenv()


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


# ====== Database init ======
@app.on_event("startup")
def on_startup():
    LOG.info("API startup: init DB + seed strategies (no worker auto-start by default)")
    Base.metadata.create_all(bind=engine)

    # Ensure registry is loaded for any endpoints relying on it
    try:
        load_default_strategies()
    except Exception:
        LOG.exception("Failed loading default strategies")

    # Telegram listener (dev/prod opt-in)
    if os.getenv("TELEGRAM_LISTENER_ENABLED", "false").lower() in ("1", "true", "yes"):
        try:
            start_telegram_polling()
            LOG.info("Telegram listener started")
        except Exception:
            LOG.exception("Telegram listener failed to start")

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


app.include_router(billing_router, prefix="/billing", tags=["Billing"])

