import sqlite3
import json
import os
import sys

# Add backend to path to import config
sys.path.append(os.path.join(os.getcwd(), "backend"))

from marketplace_config import SYSTEM_PERSONAS

DB_PATH = "backend/dev_local.db"

def reset_timeframes():
    print("Resetting canonical timeframes...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    updates = 0
    
    # Fetch all user strategies to iterate
    # We assume user_id=1 for the main user
    user_id = 1 
    
    for p in SYSTEM_PERSONAS:
        # Construct the expected persona_id
        # e.g. default_titan_btc_1
        # We need to handle potential user_id variation if needed, but for now strict user_1
        
        # We match strictly by the suffix pattern or just iterate all db rows?
        # Let's iterate DB rows and match against system.
        pass
    
    # Better approach: Iterate DB rows
    cursor.execute("SELECT id, persona_id, timeframes FROM strategy_configs")
    rows = cursor.fetchall()
    
    for row in rows:
        db_id, persona_id, tf_json = row
        
        if not persona_id or not persona_id.startswith("default_"):
            continue
            
        # Parse ID: default_{system_id}_{user_id}
        # Be careful of extra underscores in system_id.
        # Assuming user_id is integer at end.
        try:
            parts = persona_id.rsplit("_", 1)
            if len(parts) != 2: continue
            
            # Reconstruct potential system id
            # prefix is "default_{system_id}"
            prefix = parts[0] # default_titan_btc_4h
            if not prefix.startswith("default_"): continue
            
            system_id = prefix[8:] # titan_btc_4h
            
            # Find system persona
            system_p = next((sp for sp in SYSTEM_PERSONAS if sp["id"] == system_id), None)
            
            if system_p:
                canonical_tf = system_p["timeframe"]
                
                # Check current
                try:
                    current_tf = json.loads(tf_json)[0]
                except:
                    current_tf = tf_json
                    
                if current_tf != canonical_tf:
                    print(f"Fixing {persona_id}: {current_tf} -> {canonical_tf}")
                    new_json = json.dumps([canonical_tf])
                    cursor.execute("UPDATE strategy_configs SET timeframes=? WHERE id=?", (new_json, db_id))
                    updates += 1
                    
        except Exception as e:
            print(f"Error processing {persona_id}: {e}")
            continue

    conn.commit()
    conn.close()
    print(f"Reset complete. Fixed {updates} strategies.")

if __name__ == "__main__":
    reset_timeframes()
