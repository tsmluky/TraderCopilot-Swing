
import unittest
from datetime import datetime, timedelta

# Import the code to test
# Adjust path if needed or run from backend root
try:
    from core.entitlements import get_plan_entitlements, get_user_entitlements, TokenCatalog, PLANS
    from models_db import User
except ImportError:
    # If running directly inside tests folder without package context
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from core.entitlements import get_plan_entitlements, get_user_entitlements, TokenCatalog, PLANS
    from models_db import User

class TestEntitlements(unittest.TestCase):

    def test_plan_normalization(self):
        """Test that aliases are normalized correctly."""
        self.assertEqual(get_plan_entitlements("Free"), PLANS["TRADER"])
        self.assertEqual(get_plan_entitlements("lite"), PLANS["TRADER"])
        self.assertEqual(get_plan_entitlements("swingpro"), PLANS["PRO"])
        self.assertEqual(get_plan_entitlements("Premium"), PLANS["PRO"])
        self.assertEqual(get_plan_entitlements("Unknown"), PLANS["TRIAL"])

    def test_token_catalog_compat(self):
        """Test TokenCatalog compatibility adapter."""
        # FREE -> TRADER -> BTC/ETH/SOL
        tokens = TokenCatalog.get_allowed_tokens("FREE")
        self.assertIn("BTC", tokens)
        self.assertNotIn("XRP", tokens) 
        
        # PRO -> BTC/ETH/SOL/BNB/XRP
        tokens_pro = TokenCatalog.get_allowed_tokens("PRO")
        self.assertIn("XRP", tokens_pro)
        self.assertIn("BNB", tokens_pro)

    def test_user_entitlements_gate_trial_expired(self):
        """Test TRIAL_EXPIRED gate logic."""
        user = User(
            id=1, 
            plan="FREE", 
            plan_expires_at=datetime.utcnow() - timedelta(days=1) # Expired
        )
        ents = get_user_entitlements(user)
        
        # Should have offerings but LOCKED
        offerings = ents["offerings"] # Should be empty? Or we decided logic puts into locked_offerings if expired.
        locked = ents["locked_offerings"]
        
        # Logic says: CASE 2: LOCKED (Trial Expired)
        # So active offerings should be []
        self.assertEqual(len(offerings), 0)
        
        # Locked offerings should contain the Trial stuff
        reasons = [offering["locked_reason"] for offering in locked]
        self.assertIn("TRIAL_EXPIRED", reasons)

    def test_user_entitlements_pro(self):
        """Test PRO user sees upsells as active."""
        user = User(id=2, plan="PRO")
        ents = get_user_entitlements(user)
        
        # PRO users have strict range defined in PLANS["PRO"]
        # Offerings should cover 1H and 4H
        
        titans = [o for o in ents["offerings"] if o["strategy_code"] == "TITAN_BREAKOUT"]
        tfs = [t["timeframe"] for t in titans]
        
        self.assertIn("1H", tfs)
        self.assertIn("4H", tfs)
        
        # PRO should typically NOT see "Upgrade to PRO" locked cards for stuff they already have.
        # Check upsells
        upsells = [o for o in ents["locked_offerings"] if o["locked_reason"] == "UPGRADE_REQUIRED"]
        self.assertEqual(len(upsells), 0)

    def test_legacy_exports(self):
        """Test restored legacy functions (can_use_advisor, etc)."""
        from core.entitlements import can_use_advisor, can_access_telegram, assert_token_allowed
        from fastapi import HTTPException
        
        # 1. Advisor (Pro only)
        user_free = User(id=1, plan="FREE")
        user_pro = User(id=2, plan="PRO")
        self.assertFalse(can_use_advisor(user_free))
        self.assertTrue(can_use_advisor(user_pro))
        
        # 2. Telegram (Active plan)
        # Note: Logic depends on plan type for telegram access
        self.assertTrue(can_access_telegram(user_free))
        
        user_expired = User(id=3, plan="TRIAL", plan_expires_at=datetime.utcnow() - timedelta(days=1))
        self.assertFalse(can_access_telegram(user_expired))
        
        # 3. Assert Token
        # Free user -> BTC allowed
        try:
            assert_token_allowed(user_free, "BTC")
        except HTTPException:
            self.fail("assert_token_allowed raised HTTPException for allowed token")
            
        # Free user -> XRP not allowed
        with self.assertRaises(HTTPException):
            assert_token_allowed(user_free, "XRP")

if __name__ == '__main__':
    unittest.main()
