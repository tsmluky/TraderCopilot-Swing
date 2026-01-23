from core.entitlements import VALID_TOKENS_TRIAL, VALID_TOKENS_FULL, QUOTAS
from core.trial_policy import TIER_TRIAL, TIER_TRADER, TIER_PRO, TIER_OWNER

def print_table():
    print(f"{'TIER':<15} | {'TOKENS':<30} | {'TIMEFRAMES':<15} | {'ADVISOR':<8} | {'TELEGRAM':<8}")
    print("-" * 90)
    
    tiers = [
        (TIER_TRIAL, VALID_TOKENS_TRIAL, "4h, 1d", "❌", "❌"),
        (TIER_TRADER, VALID_TOKENS_FULL, "4h, 1d", "❌", "✅"),
        (TIER_PRO, VALID_TOKENS_FULL, "1h, 4h, 1d", "✅", "✅")
    ]
    
    for name, tokens, tfs, adv, tele in tiers:
        token_str = ",".join(tokens)
        print(f"{name:<15} | {token_str:<30} | {tfs:<15} | {adv:<8} | {tele:<8}")

if __name__ == "__main__":
    print_table()
