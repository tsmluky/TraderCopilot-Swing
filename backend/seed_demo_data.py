import sys
import os
import random
from datetime import datetime, timedelta

# Add backend directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal, engine_sync, Base
from models_db import Signal, SignalEvaluation, User, StrategyConfig

# --- Configuration ---
NUM_PAST_SIGNALS = 45
DAYS_HISTORY = 7
TOKENS = ["ETH", "BTC", "SOL", "AVAX", "DOT", "LINK"]
DIRECTIONS = ["LONG", "SHORT"]
TIMEFRAMES = ["15m", "1h", "4h"]

# "Pro" rationales for demo
RATIONALES_WIN = [
    "Bullish divergence on RSI (14) coincident with support retest at {price}. "
    "Volume profile suggests accumulation.",
    "Golden Cross (EMA 50/200) confirmed on 4h timeframe. "
    "Breakout above key resistance level with strong momentum.",
    "Inverse Head and Shoulders pattern completion. "
    "Neckline breach confirmed. Smart money inflow detected.",
    "Fibonacci retracement 0.618 held perfectly. "
    "Stochastic oscillator exiting oversold territory.",
    "Symmetrical triangle breakout to the upside. "
    "Funding rates imply bearish sentiment squeeze.",
]

RATIONALES_LOSS = [
    "Failed auction at resistance. Price unable to hold above VWAP. "
    "Momentum divergence suggests exhaustion.",
    "Bear flag breakdown confirmed. "
    "High sell volume at local top suggests distribution.",
    "Rejected from daily supply zone. "
    "Macd crossover indicates shifting momentum to bearish.",
    "False breakout (bull trap) followed by heavy selling. "
    "liquidity grab below swing low likely.",
    "Double top formation at key psychological level. "
    "RSI overbought condition triggered sell-off.",
]


def create_demo_user(db: Session):
    """Ensure the demo user exists."""
    demo_email = "demo@tradercopilot.com"
    user = db.query(User).filter(User.email == demo_email).first()
    if not user:
        print(f"Creating demo user: {demo_email}")
        user = User(
            email=demo_email,
            name="Analista Institucional",
            hashed_password="demo",  # Plaintext for MVP/Demo simplicity as requested
            role="admin",
        )
        db.add(user)
        db.commit()
    else:
        print(f"Demo user already exists: {demo_email}")


def create_strategies(db: Session):
    """Ensure basic strategies exist."""
    strategies = [
        {
            "id": "rsi_divergence",
            "name": "RSI Divergence 2.0",
            "desc": "Counter-trend strategy based on RSI momentum divergence.",
        },
        {
            "id": "donchian_breakout",
            "name": "Donchian Trend",
            "desc": "Trend following system using Donchian Channels.",
        },
        {
            "id": "smart_money_concept",
            "name": "Institutional Flow",
            "desc": "Tracks large wallet movements and liquidity zones.",
        },
    ]

    for s in strategies:
        strat = (
            db.query(StrategyConfig)
            .filter(StrategyConfig.strategy_id == s["id"])
            .first()
        )
        if not strat:
            print(f"Creating strategy: {s['name']}")
            new_strat = StrategyConfig(
                strategy_id=s["id"],
                name=s["name"],
                description=s["desc"],
                enabled=1,
                tokens='["BTC", "ETH", "SOL"]',
                timeframes='["1h", "4h"]',
            )
            db.add(new_strat)
    db.commit()


def generate_signals(db: Session):
    """Generate realistic history."""

    # Check if we already have enough data
    count = db.query(Signal).count()
    if count > 10:
        print(f"Database already has {count} signals. skipping massive seed.")
        # Optionally continue to add just a few fresh ones?
        # return
        print("Adding a few fresh signals anyway...")

    print(f"Seeding {NUM_PAST_SIGNALS} signals...")

    now = datetime.utcnow()

    for i in range(NUM_PAST_SIGNALS):
        # Time distribution: denser in recent days
        days_back = random.uniform(0, DAYS_HISTORY)
        ts = now - timedelta(days=days_back)

        token = random.choice(TOKENS)
        tf = random.choice(TIMEFRAMES)
        direction = random.choice(DIRECTIONS)

        # Realistic Price Simulation (mock)
        # Use simple logic to avoid overly long line
        if token == "ETH":
            base_price = 2500
        elif token == "BTC":
            base_price = 65000
        elif token == "SOL":
            base_price = 150
        else:
            base_price = 20

        noise = random.uniform(-0.05, 0.05)
        entry_price = base_price * (1 + noise)

        # Determine outcome first to write the narrative
        is_win = random.random() < 0.65  # 65% Win rate for demo "Wow" factor

        result_status = "WIN" if is_win else "LOSS"
        # Format rationale
        chosen_rat = random.choice(RATIONALES_WIN if is_win else RATIONALES_LOSS)
        rationale = chosen_rat.format(price=f"{entry_price:.2f}")

        # Calculate TP/SL Logic
        risk_reward = random.uniform(1.5, 3.0)
        risk_pct = 0.015  # 1.5% stop loss

        if direction == "LONG":
            sl_price = entry_price * (1 - risk_pct)
            tp_price = entry_price * (1 + (risk_pct * risk_reward))
            exit_price = tp_price if is_win else sl_price
            pnl_r = risk_reward if is_win else -1.0
        else:
            sl_price = entry_price * (1 + risk_pct)
            tp_price = entry_price * (1 - (risk_pct * risk_reward))
            exit_price = tp_price if is_win else sl_price
            pnl_r = risk_reward if is_win else -1.0

        # Create Signal
        sig = Signal(
            timestamp=ts,
            token=token,
            timeframe=tf,
            direction=direction,
            entry=round(entry_price, 4),
            tp=round(tp_price, 4),
            sl=round(sl_price, 4),
            confidence=round(random.uniform(75, 95), 1),
            rationale=rationale,
            source="Pro_Analyst_AI",  # Premium sounding source
            mode="PRO",
            strategy_id=random.choice(["rsi_divergence", "smart_money_concept"]),
        )
        db.add(sig)
        db.flush()  # get ID

        # Create Evaluation (Result)
        # Randomly leave some recent ones open (no evaluation)
        if (now - ts).total_seconds() > 3600 * 4:  # Older than 4 hours -> Closed
            eval_obj = SignalEvaluation(
                signal_id=sig.id,
                evaluated_at=ts + timedelta(hours=4),  # Assume closed 4h later
                result=result_status,
                pnl_r=round(pnl_r, 2),
                exit_price=round(exit_price, 4),
            )
            db.add(eval_obj)
        else:
            # Open signal!
            # Ensure Dashboard sees it as "Active"
            pass

    db.commit()
    print("Seeding complete.")


def main():
    print("--- Starting Demo Data Seed ---")
    try:
        # Create Tables if not exist (sync way)
        Base.metadata.create_all(bind=engine_sync)

        db = SessionLocal()
        create_demo_user(db)
        create_strategies(db)
        generate_signals(db)
        db.close()
        print("--- Seed Success ---")
    except Exception as e:
        print(f"Seed Failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
