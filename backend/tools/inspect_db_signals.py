from database import get_db
from models_db import Signal
import sys

db = next(get_db())
signals = db.query(Signal).order_by(Signal.timestamp.desc()).limit(5).all()

print(f"{'ID':<5} {'TOKEN':<6} {'STRATEGY_ID':<20} {'SOURCE':<20}")
print("-" * 60)
for s in signals:
    sid = str(s.strategy_id) if s.strategy_id else "None"
    src = str(s.source) if s.source else "None"
    print(f"{s.id:<5} {s.token:<6} {sid:<20} {src:<20}")
