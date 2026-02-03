# backend/scheduler.py
"""
TraderCopilot-Swing Scheduler (Plan-Based Entitlements)
Refactored (2026-01-25):
- Executes Strategies per PLAN (Trial/Trader/Pro) x Strategy x Timeframe.
- Persists Signals as MASTER SIGNALS (user_id=NULL, mode=PLAN).
- Fans out notifications to eligible users.
"""

from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import time
import uuid
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

# DB / Models
from database import SessionLocal
from models_db import SchedulerLock, User
from sqlalchemy.orm import Session

# Core
from strategies.registry import get_registry, load_default_strategies
from strategies.params import get_strategy_params
from core.signal_logger import log_signal
from core.entitlements import PLANS
from notify import send_telegram

# -------------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------------

def setup_worker_logging() -> logging.Logger:
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("scheduler")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    
    fh = RotatingFileHandler(log_dir / "scheduler.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    
    # Console
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    
    return logger

LOG = setup_worker_logging()

# Global Instance (for import by main.py if needed)
# Defined at the end of file to ensure class is loaded.




# -------------------------------------------------------------------------
# Utils
# -------------------------------------------------------------------------

def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default

def cadence_for_timeframe(tf: str) -> int:
    t = (tf or "").strip().lower()
    if t in ("1h", "60m"):
        return _env_int("SCHED_CADENCE_1H_SEC", 300)
    if t in ("4h", "240m"):
        return _env_int("SCHED_CADENCE_4H_SEC", 600)
    if t in ("1d", "24h"):
        return _env_int("SCHED_CADENCE_1D_SEC", 3600)
    return 600

# -------------------------------------------------------------------------
# Scheduler
# -------------------------------------------------------------------------

class StrategyScheduler:
    def __init__(self, loop_interval: int = 60, lock_ttl: int = 55):
        self.loop_interval = loop_interval
        self.lock_ttl = lock_ttl
        self.lock_id = str(uuid.uuid4())
        
        self.registry = get_registry()
        try:
            load_default_strategies()
        except Exception:
            LOG.exception("Registry load failed")
            
        # State
        self.last_run: Dict[str, datetime] = {} # Key: "{plan}_{strat}_{tf}"
        self.dedupe_cache: Dict[str, datetime] = {}
        
    def acquire_lock(self, db: Session) -> bool:
        """
        Simple DB-based lock using `acquired_at`.
        Refactored to match `models_db.SchedulerLock` (id, lock_name, acquired_at).
        """
        now = datetime.utcnow()
        try:
            lock = db.query(SchedulerLock).filter(
                SchedulerLock.lock_name == "main_scheduler"
            ).with_for_update().first() # Row lock if possible

            if not lock:
                lock = SchedulerLock(
                    lock_name="main_scheduler",
                    acquired_at=now
                )
                db.add(lock)
                db.commit()
                return True
            
            # Check expiration
            expiration = lock.acquired_at + timedelta(seconds=self.lock_ttl)
            
            if now > expiration:
                # Lock is stale (dead worker) OR I am refreshing my own lock (if logic permits)
                # In this simple model without owner_id, we just take it if expired.
                lock.acquired_at = now
                db.commit()
                return True
            
            # Locked and fresh
            return False
            
        except Exception as e:
            LOG.error(f"Lock acquisition failed: {e}")
            db.rollback()
            return False

    def get_execution_tasks(self, now: datetime) -> List[Dict[str, Any]]:
        """
        Generates list of tasks to run based on PLANS.
        Complexity: O(Plans * Strategies * Timeframes).
        """
        tasks = []
        
        # Iterate over normalized plans defined in entitlements.py
        # PLANS keys: TRIAL, TRADER, PRO.
        # Note: TRIAL and TRADER might have same content, we can dedup execution if we want,
        # but simpler to run them as separate scopes for signal tagging.
        
        for plan_name, ent in PLANS.items():
            strategies = ent["strategies"] # ["TITAN_BREAKOUT", "FLOW_MASTER"]
            timeframes = ent["timeframes"] # ["4H", "1D"] etc.
            tokens = ent["tokens"]         # ["BTC", "ETH", ...]
            
            for strat_code in strategies:
                for tf in timeframes:
                    
                    # Unit of Execution: (Plan, Strategy, Timeframe)
                    # We execute for the whole token set at once.
                    
                    task_key = f"{plan_name}_{strat_code}_{tf}"
                    
                    # Check Cadence
                    cadence = cadence_for_timeframe(tf)
                    last = self.last_run.get(task_key)
                    
                    if not last or (now - last).total_seconds() >= cadence:
                        tasks.append({
                            "key": task_key,
                            "plan": plan_name,
                            "strategy_code": strat_code,
                            "timeframe": tf,
                            "tokens": tokens
                        })
                        
        return tasks

    def execute_task(self, task: Dict[str, Any]):
        """Runs the strategy logic for a set of tokens."""
        self.registry.get(task["strategy_code"].lower()) # Registry uses snake_case usually? Check.
        # Registry keys usually: "titan_breakout" or "donchian_v2"? 
        # Existing marketplace_config used "donchian_v2" mapped to "Titan Breakout".
        # We need to map StrategyCode (TITAN_BREAKOUT) to Implementation ID.
        
        # MAPPING (Hardcoded for MVP or import from entitlements if we add it there)
        impl_map = {
            "TITAN_BREAKOUT": "donchian_v2",
            "FLOW_MASTER": "trend_following_native_v1",
            "MEAN_REVERSION": "mean_reversion_v1"
        }
        impl_id = impl_map.get(task["strategy_code"], "").lower()
        
        strategy_impl = self.registry.get(impl_id)
        if not strategy_impl:
            # Try direct code lower
            strategy_impl = self.registry.get(task["strategy_code"].lower())
            
        if not strategy_impl:
            LOG.warning("Strategy implementation not found: %s", task["strategy_code"])
            return []

        try:
             # Refactored Loop: "Strategy per Token" (15 Strategies Mode)
             # Instead of passing all tokens to one instance, we iterate and instantiate
             # the strategy with specific params for EACH token.
             
             # Map Offering Code to Internal Prefix
             prefix_map = {
                 "donchian_v2": "Donchian",
                 "trend_following_native_v1": "TrendFollowing",
                 "mean_reversion_v1": "MeanReversion"
             }
             metric_prefix = prefix_map.get(impl_id, impl_id)

             all_signals = []
             
             for token in task["tokens"]:
                 # 1. Get Params for this specific token (e.g. SOL might have wider stops)
                 params = get_strategy_params(impl_id, token)
                 
                 # 2. Instantiate Strategy
                 # strategy_impl is an INSTANCE returned by registry.get()
                 # We need the CLASS to create a fresh one with specific params.
                 StrategyClass = type(strategy_impl)
                 
                 try:
                     strategy_instance = StrategyClass(**params)
                 except TypeError as te:
                     LOG.warning(f"Param mismatch for {impl_id} on {token}: {te}. Using defaults.")
                     strategy_instance = StrategyClass()

                 # 3. Generate Signal (Single Token)
                 # We execute just for this token to ensure parameters are isolated
                 sigs = strategy_instance.generate_signals(
                     tokens=[token],
                     timeframe=task["timeframe"]
                 )
                 
                 # 4. Enrich Signals with Explicit IDs
                 for s in sigs:
                    # Construct specific ID: Donchian_BTC (No timeframe suffix per request)
                    s.strategy_id = f"{metric_prefix}_{token.upper()}"
                    s.source = f"PLAN:{task['plan']}:{task['strategy_code']}" 
                    all_signals.append(s)

                 # 5. Activity/Watchlist Logic (Per Token)
                 if not sigs:
                     try:
                         # Ensure imported locally if not at top
                         from core.schemas import Signal 
                         
                         items = strategy_instance.analyze_watchlist(token, task["timeframe"])
                         for item in items:
                             w_sig = Signal(
                                 timestamp=datetime.utcnow(),
                                 token=item["token"],
                                 direction=item["side"],
                                 entry=item["trigger_price"],
                                 tp=0.0,
                                 sl=0.0,
                                 confidence=0.0,
                                 rationale=f"[WATCHLIST] {item['reason']}",
                                 # Explicit ID: Donchian_BTC
                                 strategy_id=f"{metric_prefix}_{token.upper()}",
                                 source=f"WATCH:{task['plan']}:{task['strategy_code']}",
                                 mode=task["plan"],
                                 timeframe=task["timeframe"],
                                 extra={
                                     "setup": "Watchlist Monitor",
                                     "distance_atr": item.get("distance_atr"),
                                     "is_watchlist": True
                                 }
                             )
                             # Limit 1 watchlist item per token per run 
                             all_signals.append(w_sig)
                             break 
                     except Exception as we:
                         LOG.warning(f"Watchlist check failed for {token}: {we}")

             return all_signals

        except Exception as e:
            LOG.error("Task failed %s: %s", task["key"], e)
            return []

    def process_and_persist_signals(self, signals: List[Any], task: Dict[str, Any]):
        """
        Persist signals as Master Signals (user_id=NULL, mode=PLAN).
        Then Fan-out notifications.
        """
        if not signals:
            return
        
        db = SessionLocal()
        try:
            # 1. Persist Master Signals
            cnt = 0
            for sig in signals:
                if not sig.strategy_id:
                     # Fallback if somehow missing - Use simplified format
                     # This might happen if 'signals' passed in didn't go through the enrichment loop above
                     # But in execute_task we append enriched signals.
                     # Default fallback:
                     sig.strategy_id = f"{task['strategy_code']}_{task['strategy_code']}" # Ugly but failsafe

                # Ensure source is set if not already
                if not sig.source:
                     sig.source = f"PLAN:{task['plan']}:{task['strategy_code']}"

                sig.mode = task["plan"] # Scope
                sig.user_id = None # Master Signal
                sig.is_saved = 1
                
                if log_signal(sig, db_session=db):
                    cnt += 1
                    # Notification Fan-out
                    self.fan_out_notifications(db, sig, task["plan"])
            
            if cnt > 0:
                LOG.info("Persisted %d signals for %s", cnt, task["key"])
                
        except Exception:
            LOG.exception("Persistence failed")
        finally:
            db.close()

    def fan_out_notifications(self, db: Session, sig: Any, plan: str):
        """
        Sends Telegram alerts to all users in 'plan' who have Telegram configured.
        """
        # 1. Find Users in Plan (active coverage)
        # Normalize plan query often requires handling aliases if DB has mixed data.
        # We assume strict adherence to 'TRADER', 'PRO' etc. or map aliases.
        
        target_plans = [plan]
        if plan == "TRADER": 
            target_plans.extend(["FREE", "LITE", "SWINGLITE"]) # Legacy compat
        if plan == "PRO":
            target_plans.extend(["SWINGPRO", "PREMIUM"])

        # 2. Query Users with Chat ID
        users = db.query(User).filter(
            User.plan.in_(target_plans),
            User.telegram_chat_id.isnot(None)
        ).all()
        
        if not users:
            return

        # 3. Dedupe & Send
        # We use a cache key to avoid spamming the same global signal repeated times 
        # (log_signal handles idempotency DB-side, but duplicate execution might trigger this)
        
        LOG.info(f"[Fan-Out] Found {len(users)} users for plan {plan}. Sending alerts...")

        msg = (
            f"⚡ <b>{plan} ALERT</b>\n"
            f"{'🟢' if sig.direction=='long' else '🔴'} <b>{sig.token} {sig.direction.upper()}</b>\n"
            f"TF: {sig.timeframe}\n"
            f"Entry: {sig.entry}\n"
            f"Stop: {sig.sl}\n"
            f"Target: {sig.tp}"
        )
        
        sent_count = 0
        for u in users:
            # Simple check if user wants alerts? Assuming 'Yes' if ChatID present for MVP.
            # In future: check User preferences.
            res = send_telegram(msg, chat_id=u.telegram_chat_id)
            if res.get("ok"):
                sent_count += 1
            else:
                LOG.error(f"[Fan-Out] Failed to send to {u.id} (Chat {u.telegram_chat_id}): {res}")
        
        LOG.info(f"[Fan-Out] Summary: Sent {sent_count}/{len(users)} alerts for {sig.token}.")


    def run(self):
        LOG.info("Scheduler Starting... (Plan-Based)")
        while True:
            db = SessionLocal()
            has_lock = False
            try:
                has_lock = self.acquire_lock(db)
            except Exception as e:
                LOG.error(f"Lock loop error: {e}")
            finally:
                db.close()

            if not has_lock:
                time.sleep(10)
                continue

            # Core Loop
            try:
                now = datetime.utcnow()
                tasks = self.get_execution_tasks(now)
                
                if tasks:
                    LOG.info("Executing %d eligible tasks...", len(tasks))
                    
                for task in tasks:
                    # Mark run time
                    self.last_run[task["key"]] = now
                    
                    # Execute
                    signals = self.execute_task(task)
                    
                    # Persist
                    self.process_and_persist_signals(signals, task)

                # === VALIDATION STEP ===
                
                db_val = SessionLocal()
                try:
                    from core.signal_evaluator import evaluate_pending_signals
                    validated_count = evaluate_pending_signals(db_val)
                    if validated_count > 0:
                        LOG.info(f"Validator: Updated {validated_count} signals (TP/SL/Timeout)")
                except Exception as e:
                    LOG.error(f"Validator failed: {e}")
                finally:
                    db_val.close()

                # Heartbeat (approx every 10 mins if loop is 60s)
                # Just log "Alive" occasionally to prove we aren't stuck
                if int(time.time()) % 600 < self.loop_interval + 5:
                     LOG.info(f"❤️ Scheduler Heartbeat - Active | Last Check: {now.isoformat()}")

            except Exception as main_e:
                LOG.exception(f"CRITICAL: Scheduler Main Loop Crash prevented: {main_e}")
                # Sleep a bit longer to let system recover (e.g. DB connectivity)
                time.sleep(10)

            time.sleep(self.loop_interval)

# Global Instance (for import by main.py if needed)
try:
    scheduler_instance = StrategyScheduler()
except Exception as e:
    LOG.error(f"Failed to instantiate global StrategyScheduler: {e}")
    scheduler_instance = None

if __name__ == "__main__":
    if scheduler_instance:
        scheduler_instance.run()
    else:
        LOG.error("Cannot run scheduler: Instance failed to initialize.")
