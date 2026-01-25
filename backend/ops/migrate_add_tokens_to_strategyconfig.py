from __future__ import annotations

from sqlalchemy import text, inspect
from database import engine

TABLE = "strategy_configs"
COL = "tokens"

def main():
    insp = inspect(engine)
    if TABLE not in insp.get_table_names():
        print(f"[SKIP] Table not found: {TABLE}")
        return

    cols = [c["name"] for c in insp.get_columns(TABLE)]
    if COL in cols:
        print(f"[OK] Column already exists: {TABLE}.{COL}")
        return

    # SQLite-safe ALTER TABLE
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE {TABLE} ADD COLUMN {COL} TEXT"))
    print(f"[DONE] Added column: {TABLE}.{COL} (TEXT)")

if __name__ == "__main__":
    main()
