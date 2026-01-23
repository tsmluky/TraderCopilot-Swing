"""
Central token allowlists for TraderCopilot-Swing (LOCAL + MVP).

Source of truth:
- VALID_TOKENS_TRIAL: tokens allowed during trial tier
- VALID_TOKENS_FULL: tokens allowed for paid tiers (SwingLite/SwingPro)

IMPORTANT:
Do NOT redefine these later in the file. If you add other lists, use different names.
"""

# ==========================================
# Canonical token allowlists (Swing plan)
# ==========================================
VALID_TOKENS_TRIAL = ["BTC", "ETH"]
VALID_TOKENS_FULL  = ["BTC", "ETH", "SOL", "BNB", "XRP"]

# Optional: if you ever need a "free" list distinct from TRIAL, define it explicitly.
# For Swing MVP, TRIAL is the free experience, so we keep this aligned.
VALID_TOKENS_FREE = VALID_TOKENS_TRIAL


# =========================
# Compatibility aliases
# (expected by some modules)
# =========================
TOKENS_TRIAL = VALID_TOKENS_TRIAL
TOKENS_FULL  = VALID_TOKENS_FULL

SUPPORTED_TOKENS_TRIAL = VALID_TOKENS_TRIAL
SUPPORTED_TOKENS_FULL  = VALID_TOKENS_FULL

ALLOWED_TOKENS_TRIAL = VALID_TOKENS_TRIAL
ALLOWED_TOKENS_FULL  = VALID_TOKENS_FULL
