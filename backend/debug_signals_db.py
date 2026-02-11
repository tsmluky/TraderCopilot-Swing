from sqlalchemy import text
import os

# Setup DB
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db") 
# Use the real production DB url if possible, but I don't have it.
# Assuming standard backend path and sqlite default or existing env.

# I will try to infer DB from context or just use relative path to test.db if exists, 
# or more likely, I need to use the `database.py` logic.

import sys
sys.path.append(".")
from database import engine

def check_signals():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, strategy_id, source, raw_response, extra "
                                   "FROM signals ORDER BY id DESC LIMIT 5"))
        for row in result:
            print(f"ID: {row.id} | Strat: {row.strategy_id} | Source: {row.source} | "
                  f"Raw: {row.raw_response} | Extra: {row.extra}")

if __name__ == "__main__":
    check_signals()
