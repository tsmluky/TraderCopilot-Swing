# backend/scheduler.py
"""TraderCopilot-Swing Scheduler (Worker)

Objetivo (MVP):
- Ejecutar las "Personas" activas (StrategyConfig.enabled=1) en loop.
- Persistir señales en DB (log_signal) y evaluar pendientes (evaluate_pending_signals).
- Notificar por Telegram SOLO si el usuario tiene derecho a ello.

Importante (Runtime Stabilization):
- Este archivo es el entrypoint del worker. Debe ejecutarse como proceso separado de la API.
- La API (main.py) NO debe auto-arrancar el worker salvo opt-in (dev only).

Cost control (MVP):
- El loop puede correr cada X segundos, pero NO conviene ejecutar 1h/4h/1d cada 60s.
- Implementamos cadencia por timeframe para reducir coste/carga sin degradar señales swing.
"""

from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import time
import requests
import ccxt
import uuid
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from database import SessionLocal
from models_db import StrategyConfig, SchedulerLock, User
from strategies.registry import get_registry, load_default_strategies
from core.signal_logger import log_signal
from core.signal_evaluator import evaluate_pending_signals
from core.trial_policy import is_trial_active
from core.entitlements import can_access_telegram
from notify import send_telegram


def setup_worker_logging() -> logging.Logger:
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("scheduler")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    fh = RotatingFileHandler(log_dir / "scheduler.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)

    eh = RotatingFileHandler(log_dir / "scheduler_error.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    eh.setLevel(logging.ERROR)
    eh.setFormatter(fmt)

    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.addHandler(eh)
    return logger


LOG = setup_worker_logging()


def _as_list(v, default: List[str]) -> List[str]:
    if v is None:
        return default
    if isinstance(v, list):
        return v
    try:
        parsed = json.loads(v) if isinstance(v, str) else v
        return parsed if isinstance(parsed, list) else default
    except Exception:
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default


def cadence_for_timeframe(tf: str) -> int:
    """Cadencia (segundos) por timeframe. Ajustable por env vars."""
    t = (tf or "").strip().lower()
    if t in ("1h", "60m"):
        return _env_int("SCHED_CADENCE_1H_SEC", 300)     # 5 min
    if t in ("4h", "240m"):
        return _env_int("SCHED_CADENCE_4H_SEC", 600)     # 10 min
    if t in ("1d", "24h", "1440m"):
        return _env_int("SCHED_CADENCE_1D_SEC", 3600)    # 60 min
    return _env_int("SCHED_CADENCE_DEFAULT_SEC", 600)    # fallback


def get_active_strategies_from_db() -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        configs = (
            db.query(StrategyConfig)
            .filter(StrategyConfig.enabled == 1)
            .all()
        )

        personas: List[Dict[str, Any]] = []
        for c in configs:
            # load user (if any) for gating/telegram
            user: User | None = None
            if c.user_id:
                user = db.query(User).filter(User.id == c.user_id).first()

            # Trial gating: FREE users must have active trial to process personas
            if user and (user.plan or "").upper() == "FREE":
                if not is_trial_active(user):
                    LOG.info("Skipping persona: FREE trial expired | user_id=%s persona=%s", user.id, c.strategy_id)
                    continue

            # Telegram gating
            telegram_chat_id = None
            if user:
                # Use User's personal chat ID for alerts
                if user.telegram_chat_id and can_access_telegram(user):
                    telegram_chat_id = user.telegram_chat_id

            tokens = _as_list(c.tokens, default=["BTC"])
            timeframes = _as_list(c.timeframes, default=["1h"])
            timeframe = timeframes[0] if timeframes else "1h"

            personas.append(
                {
                    "id": c.strategy_id,
                    "name": c.name,
                    "strategy_id": c.strategy_id,
                    "tokens": tokens,
                    "timeframe": timeframe,
                    "enabled": c.enabled,
                    "telegram_chat_id": telegram_chat_id,
                    "user_id": c.user_id,
                }
            )

        return personas
    except Exception:
        LOG.exception("Failed loading active strategies from DB")
        return []
    finally:
        db.close()


class StrategyScheduler:
    def __init__(self, loop_interval: int = 60, lock_ttl: int = 55, max_workers: int = 3):
        self.loop_interval = loop_interval
        self.lock_ttl = lock_ttl
        self.lock_id = str(uuid.uuid4())

        self.registry = get_registry()
        try:
            load_default_strategies()
        except Exception:
            LOG.exception("Failed loading strategy registry")

        self.max_workers = max_workers

        # In-memory caches for spam control / coherence
        self.processed_signals: Dict[str, datetime] = {}
        self.last_signal_direction: Dict[str, str] = {}
        self.token_coherence: Dict[str, Dict[str, Any]] = {}
        self.last_run: Dict[str, datetime] = {}  # persona_id -> last run time
        self.dedupe_cache: Dict[str, datetime] = {}

        # Evaluator cadence (no hace falta correrlo cada loop)
        self.eval_cadence_sec = _env_int("SCHED_EVAL_CADENCE_SEC", 300)
        self._last_eval_at: datetime | None = None

    def acquire_lock(self, db: Session) -> bool:
        now = datetime.utcnow()
        lock = db.query(SchedulerLock).filter(SchedulerLock.lock_name == "main_scheduler").first()

        if not lock:
            lock = SchedulerLock(
                lock_name="main_scheduler",
                owner_id=self.lock_id,
                expires_at=now + timedelta(seconds=self.lock_ttl)
            )
            db.add(lock)
            db.commit()
            return True

        if lock.expires_at < now or lock.owner_id == self.lock_id:
            lock.owner_id = self.lock_id
            lock.expires_at = now + timedelta(seconds=self.lock_ttl)
            db.commit()
            return True

        LOG.info("Lock held by other instance owner=%s; retry", lock.owner_id)
        return False

    def _is_due(self, persona: Dict[str, Any], now: datetime) -> bool:
        """Decide si una persona debe ejecutarse en esta iteración, según su timeframe."""
        pid = persona.get("id")
        tf = persona.get("timeframe") or "1h"
        cadence = cadence_for_timeframe(tf)
        last = self.last_run.get(pid)
        if not last:
            return True
        return (now - last).total_seconds() >= cadence

    def _execute_strategy_task(self, persona: Dict[str, Any]):
        strategy = self.registry.get(persona["strategy_id"])
        if not strategy:
            return []

        try:
            return strategy.generate_signals(tokens=persona["tokens"], timeframe=persona["timeframe"]) or []
        except (
            ccxt.RequestTimeout,
            ccxt.NetworkError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
            TimeoutError
        ) as e:
            # Provider/network flakiness: no ensuciar logs con traceback; continuar.
            LOG.warning(
                "Network timeout | persona=%s tokens=%s tf=%s | %s: %s",
                persona.get("id"),
                persona.get("tokens"),
                persona.get("timeframe"),
                type(e).__name__,
                str(e)[:200],
            )
            return []
        except Exception:
            # Unexpected: mantener traceback real
            LOG.exception("Worker error executing persona=%s", persona.get("id"))
            return []

    def process_single_signal(self, sig, persona: Dict[str, Any]) -> None:
        try:
            sig.source = f"Marketplace:{persona['id']}"
            sig.strategy_id = persona["id"]
            sig.is_saved = 1
            sig.user_id = persona.get("user_id")

            inserted = log_signal(sig)
            if not inserted:
                return

            LOG.info("Logged signal | %s %s | persona=%s", sig.token, sig.direction, persona.get("name"))

            now = datetime.utcnow()
            dedupe_key = f"{persona['id']}_{sig.token}_{sig.direction}"
            last_notif = self.dedupe_cache.get(dedupe_key)
            if last_notif and (now - last_notif) < timedelta(minutes=45):
                return
            self.dedupe_cache[dedupe_key] = now

            chat_id = persona.get("telegram_chat_id")
            if not chat_id:
                return

            icon = "🟢" if sig.direction == "long" else "🔴"
            msg = (
                f"{icon} {sig.direction.upper()}: {sig.token} / USDT\n\n"
                f"Entry: {sig.entry}\n"
                f"Target: {sig.tp}\n"
                f"Stop:   {sig.sl}\n\n"
                f"⚡ Strategy: {persona['name']} ({persona['timeframe']})"
            )
            send_telegram(msg, chat_id=chat_id)

        except Exception:
            LOG.exception("process_single_signal failed")

    def _maybe_eval_pending(self, now: datetime) -> None:
        if self._last_eval_at and (now - self._last_eval_at).total_seconds() < self.eval_cadence_sec:
            return

        try:
            eval_db = SessionLocal()
            try:
                new_evals = evaluate_pending_signals(eval_db)
                if new_evals:
                    LOG.info("Evaluated %s pending signals", new_evals)
            finally:
                eval_db.close()
            self._last_eval_at = now
        except Exception:
            LOG.exception("Evaluator loop error")

    def run(self) -> None:
        import concurrent.futures

        iteration = 0
        while True:
            iteration += 1

            db = SessionLocal()
            try:
                if not self.acquire_lock(db):
                    time.sleep(10)
                    continue
            except Exception:
                LOG.exception("Lock acquisition error")
                time.sleep(5)
                continue
            finally:
                db.close()

            start_ts = datetime.utcnow()
            personas_all = get_active_strategies_from_db()
            personas = [p for p in personas_all if self._is_due(p, start_ts)]

            LOG.info(
                "HEARTBEAT iter=%s personas_total=%s personas_due=%s",
                iteration,
                len(personas_all),
                len(personas),
            )

            # Si no hay nada "due", igual evaluamos pendientes (cadenciado) y dormimos.
            if not personas:
                self._maybe_eval_pending(start_ts)
                LOG.info("Loop done | iter=%s | elapsed=%.2fs | sleep=%ss", iteration, 0.0, self.loop_interval)
                time.sleep(self.loop_interval)
                continue

            all_signals_map: Dict[str, Any] = {}
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as ex:
                    future_to_persona = {ex.submit(self._execute_strategy_task, p): p for p in personas}
                    for fut in concurrent.futures.as_completed(future_to_persona):
                        p = future_to_persona[fut]
                        try:
                            signals = fut.result() or []
                            if signals:
                                all_signals_map[p["id"]] = signals
                        except Exception:
                            LOG.exception("Future exception persona=%s", p.get("id"))
            except Exception:
                LOG.exception("Parallel execution failed")

            for p in personas:
                p_id = p["id"]
                self.last_run[p_id] = start_ts  # marca ejecución para la cadencia

                signals = all_signals_map.get(p_id, [])
                if not signals:
                    continue

                for sig in signals:
                    try:
                        ts_key = f"{p_id}_{sig.token}_{sig.direction}_{sig.timestamp}"
                        last_ts = self.processed_signals.get(ts_key)
                        if last_ts and sig.timestamp <= last_ts:
                            continue
                        self.processed_signals[ts_key] = sig.timestamp

                        direction_key = f"{p_id}_{sig.token}"
                        last_dir = self.last_signal_direction.get(direction_key)
                        if last_dir == sig.direction:
                            if last_ts and (sig.timestamp - last_ts).total_seconds() < 60:
                                continue
                        self.last_signal_direction[direction_key] = sig.direction

                        coherence_key = sig.token
                        last_state = self.token_coherence.get(coherence_key)
                        now_utc = datetime.utcnow()
                        if last_state and last_state.get("direction") != sig.direction:
                            if (now_utc - last_state.get("ts", now_utc)) < timedelta(minutes=30):
                                continue
                        self.token_coherence[coherence_key] = {"direction": sig.direction, "ts": now_utc}

                        self.process_single_signal(sig, p)
                    except Exception:
                        LOG.exception("Signal processing failed persona=%s", p_id)
                        continue

            # Evaluación pendiente (cadenciada)
            self._maybe_eval_pending(datetime.utcnow())

            elapsed = (datetime.utcnow() - start_ts).total_seconds()
            LOG.info("Loop done | iter=%s | elapsed=%.2fs | sleep=%ss", iteration, elapsed, self.loop_interval)
            time.sleep(self.loop_interval)


scheduler_instance = StrategyScheduler(
    loop_interval=int(os.getenv('SCHEDULER_INTERVAL_SEC', '60'))
)


if __name__ == "__main__":
    scheduler_instance.run()
