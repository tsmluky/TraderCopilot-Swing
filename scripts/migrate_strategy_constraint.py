import sqlite3
import os

DB_PATH = "backend/dev_local.db"

def migrate():
    print(f"Migrating {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Rename old table
        print("Renaming old table...")
        cursor.execute("ALTER TABLE strategy_configs RENAME TO strategy_configs_old")
        
        # 2. Create new table (Schema from models_db.py + manual columns)
        print("Creating new table strategy_configs...")
        cursor.execute("""
            CREATE TABLE strategy_configs (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                strategy_id VARCHAR,
                persona_id VARCHAR(128),
                tokens TEXT,
                timeframes TEXT,
                risk_profile VARCHAR,
                expected_roi VARCHAR,
                color VARCHAR DEFAULT 'indigo',
                icon VARCHAR DEFAULT 'Zap',
                is_public INTEGER DEFAULT 0,
                enabled INTEGER DEFAULT 1,
                total_signals INTEGER DEFAULT 0,
                win_rate FLOAT DEFAULT 0.0,
                params_json TEXT,
                name VARCHAR,
                description TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id),
                CONSTRAINT uq_user_persona UNIQUE (user_id, persona_id)
            )
        """)
        
        # 3. Copy data
        print("Copying data...")
        # We need to list columns explicitly to avoid mismatch if order changed
        # Get columns from old table
        cursor.execute("PRAGMA table_info(strategy_configs_old)")
        columns = [row[1] for row in cursor.fetchall()]
        cols_str = ", ".join(columns)
        
        # Construct INSERT SELECT
        sql = f"INSERT INTO strategy_configs ({cols_str}) SELECT {cols_str} FROM strategy_configs_old"
        cursor.execute(sql)
        
        # 4. Drop old table
        print("Dropping old table...")
        cursor.execute("DROP TABLE strategy_configs_old")
        
        conn.commit()
        print("Migration successful! Unique constraint updated to (user_id, persona_id).")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
