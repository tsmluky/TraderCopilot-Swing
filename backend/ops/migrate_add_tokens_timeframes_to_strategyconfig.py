from __future__ import annotations

import os
import sys
from sqlalchemy import text, inspect

# Ensure backend root is on sys.path (so "import database" works)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from database import engine  # noqa: E402

TABLE = "strategy_configs"
COLS = [("tokens", "TEXT"), ("timeframes", "TEXT")]

def main():
    insp = inspect(engine)
    if TABLE not in insp.get_table_names():
        print(f"[SKIP] Table not found: {TABLE}")
        return

    existing = {c["name"] for c in insp.get_columns(TABLE)}

    with engine.begin() as conn:
        for col, typ in COLS:
            if col in existing:
                print(f"[OK] Column already exists: {TABLE}.{col}")
                continue
            conn.execute(text(f"ALTER TABLE {TABLE} ADD COLUMN {col} {typ}"))
            print(f"[DONE] Added column: {TABLE}.{col} ({typ})")

if __name__ == "__main__":
    main()
