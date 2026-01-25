
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict



from models_db import Signal, SignalEvaluation, StrategyConfig
from core.market_data_api import get_current_price

# Minimum age to evaluate (avoid instant evaluation on creation)
MIN_SIGNAL_AGE_MINUTES = 5
# Timeout for signals (e.g., 24h)
SIGNAL_TIMEOUT_HOURS = 24


def evaluate_pending_signals(db: Session) -> int:
    """
    Evaluates pending signals against current market data.
    Returns the number of newly evaluated signals.
    """
    # 1. Find Pending Signals
    # Signals active (no evaluation) and older than MIN_SIGNAL_AGE
    cutoff_time = datetime.utcnow() - timedelta(minutes=MIN_SIGNAL_AGE_MINUTES)

    # We want Signals where NO SignalEvaluation exists
    # Using specific query pattern for efficiency
    pending_signals = (
        db.query(Signal)
        .outerjoin(SignalEvaluation, Signal.id == SignalEvaluation.signal_id)
        .filter(SignalEvaluation.id.is_(None), Signal.timestamp < cutoff_time)
        .all()
    )

    if not pending_signals:
        return 0

    # 2. Group by Token to optimize API calls
    signals_by_token: Dict[str, List[Signal]] = {}
    for sig in pending_signals:
        if sig.token not in signals_by_token:
            signals_by_token[sig.token] = []
        signals_by_token[sig.token].append(sig)

    new_evaluations_count = 0

    # 3. Evaluate by Token
    for token, signals in signals_by_token.items():
        current_price = get_current_price(token)
        if not current_price or current_price <= 0:
            continue

        for sig in signals:
            result = None
            exit_price = current_price

            # Basic Validation
            if not sig.entry or sig.entry <= 0:
                result = "neutral"  # Invalid entry

            # --- Check TP/SL ---
            elif sig.direction.lower() == "long":
                if sig.tp and current_price >= sig.tp:
                    result = "WIN"
                    exit_price = sig.tp
                elif sig.sl and current_price <= sig.sl:
                    result = "LOSS"
                    exit_price = sig.sl

            elif sig.direction.lower() == "short":
                if sig.tp and current_price <= sig.tp:
                    result = "WIN"
                    exit_price = sig.tp
                elif sig.sl and current_price >= sig.sl:
                    result = "LOSS"
                    exit_price = sig.sl

            # --- Check Timeout ---
            if not result:
                age = datetime.utcnow() - sig.timestamp
                if age > timedelta(hours=SIGNAL_TIMEOUT_HOURS):
                    # Timeout - Calculate result at current price
                    pnl_pct = 0.0
                    if sig.direction.lower() == "long":
                        pnl_pct = (current_price - sig.entry) / sig.entry
                    else:
                        pnl_pct = (sig.entry - current_price) / sig.entry

                    if pnl_pct > 0.005:
                        result = "WIN"  # > 0.5% profit
                    elif pnl_pct < -0.005:
                        result = "LOSS"  # < -0.5% loss
                    else:
                        result = "BE"  # Break Even / Stagnant

            # --- Save Evaluation if Result Found ---
            if result:
                # Calculate R-Multiple (PnL / Risk)
                # Risk = |Entry - SL|
                risk = abs(sig.entry - (sig.sl if sig.sl else sig.entry * 0.99))
                if risk == 0:
                    risk = sig.entry * 0.01  # Prevent div/0

                raw_pnl = 0.0
                if sig.direction.lower() == "long":
                    raw_pnl = exit_price - sig.entry
                else:
                    raw_pnl = sig.entry - exit_price

                pnl_r = raw_pnl / risk

                eval_obj = SignalEvaluation(
                    signal_id=sig.id,
                    evaluated_at=datetime.utcnow(),
                    result=result,
                    pnl_r=round(pnl_r, 2),
                    exit_price=exit_price,
                )

                db.add(eval_obj)
                new_evaluations_count += 1

                # Update Strategy Stats
                # TODO: Re-enable when _update_strategy_stats is implemented
                # if sig.strategy_id:
                #     _update_strategy_stats(db, sig.strategy_id)

    db.commit()
    return new_evaluations_count
    """
    Recalculates Win Rate for the Persona (StrategyConfig).
    """
    try:
        total = (
            db.query(Signal)
            .join(SignalEvaluation)
            .count()
        )
        wins = (
            db.query(Signal)
            .join(SignalEvaluation)
            .count()
        )

        # Calculate Total PnL (Sum of R-Multiples)
        pnl_r_sum = 0.0
        evals = (
            db.query(SignalEvaluation)
            .join(Signal)
            .all()
        )
        for e in evals:
            if e.pnl_r:
                pnl_r_sum += e.pnl_r

        if total > 0:
            win_rate = (wins / total) * 100  # Store as 0-100

            # Upsert config
            config = (
                db.query(StrategyConfig)
                .first()
            )
            if config:
                config.win_rate = win_rate
                config.total_signals = total
                # Do NOT overwrite expected_roi with realized PnL.
                # Expected ROI is a static backtest metric.
                # Realized PnL should be calculated on the fly or stored in a new column.

    except Exception as e:
        pass


