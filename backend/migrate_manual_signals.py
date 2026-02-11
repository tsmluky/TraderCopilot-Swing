from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
# import models_db # Avoid importing if possible to avoid deps, but best to use raw SQL or models
import json
import ast
from database import SessionLocal

def migrate_manual_signals():
    db = SessionLocal()
    try:
        # Find signals that are manual but have strategy_id != 'MARKET_SCANNER'
        # source might be 'manual_scanner' or 'manual'
        result = db.execute(text("SELECT id, strategy_id, extra, raw_response FROM signals WHERE (source = 'manual_scanner' OR source = 'manual') AND strategy_id != 'MARKET_SCANNER'"))
        
        count = 0
        for row in result:
            sig_id = row.id
            old_strat_id = row.strategy_id
            
            # Hydrate extra
            current_extra = {}
            if row.extra:
                try:
                    current_extra = json.loads(row.extra)
                except:
                    pass
            elif row.raw_response:
                try:
                    current_extra = ast.literal_eval(row.raw_response)
                except:
                    pass
            
            # Update extra
            current_extra["original_strategy_id"] = old_strat_id
            new_extra_json = json.dumps(current_extra)
            
            # Recalculate Idempotency Key
            # Key format from signal_logger.py: 
            # f"{signal.strategy_id}|{signal.token.upper()}|{signal.timeframe}|{ts_iso}|{signal.direction.lower()}|{signal.user_id}|{signal.mode}"
            
            # We need to fetch other fields to reconstruct key
            # But wait, we can't easily perform string format in SQL in portable way.
            # We should probably do this in Python.
            # Let's fetch the whole row logic or just update ID and let unique constraint handle it?
            # No, if we update ID, the OLD idempotency key becomes invalid/stale relative to the data.
            # Ideally we update the key too to maintain consistency.
            
            # For this script to be simple and safe on production without complex logic:
            # We will just update strategy_id and extra. 
            # The idempotency key was useful for INSERT deduplication. 
            # Updating existing rows doesn't trigger the unique check against *itself*, but might collide with others.
            # BUT, the key is derived. If we ever re-generate the signal, it would generate a NEW key with MARKET_SCANNER.
            # If we don't update the key on the old row, the new signal WOULD be inserted as a duplicate (if it perfectly matches).
            # So we SHOULD update the key to match the new ID, so it "occupies" that slot.
            
            # Fetch full row data for key generation
            full_row = db.execute(text("SELECT * FROM signals WHERE id = :id"), {"id": sig_id}).fetchone()
            
            # Map columns by index or name. SQLAlchemy text result acts like named tuple usually.
            # Let's assume we can access by name.
            
            try:
                ts_iso = full_row.timestamp.isoformat()
                idem_key = (
                    f"MARKET_SCANNER|{full_row.token.upper()}|{full_row.timeframe}|"
                    f"{ts_iso}|{full_row.direction.lower()}|{full_row.user_id}|{full_row.mode}"
                )
                
                # Update DB
                db.execute(text("UPDATE signals SET strategy_id = 'MARKET_SCANNER', extra = :extra, source = 'manual_scanner', idempotency_key = :ikey WHERE id = :id"), 
                           {"extra": new_extra_json, "id": sig_id, "ikey": idem_key})
                count += 1
            except Exception as e:
                print(f"Skipping row {sig_id} due to key generation error: {e}")
            
        db.commit()
        print(f"Migrated {count} manual signals to MARKET_SCANNER ID.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_manual_signals()
