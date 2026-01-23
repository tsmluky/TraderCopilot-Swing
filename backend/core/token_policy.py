from fastapi import HTTPException
from models_db import User

def normalize_token(token: str) -> str:
    return token.upper().strip()

def get_allowed_tokens(user: User) -> list[str]:
    """
    Returns list of allowed tokens based on user plan.
    """
    plan = user.plan.upper()
    
    # OWNER / PRO / TRADER -> All Tokens (for now)
    if plan in ["OWNER", "PRO", "TRADER"]:
        return ["BTC", "ETH", "SOL", "BNB", "XRP"]
        
    # FREE / TRIAL -> Restricted
    # Trial usually allows testing the platform, but if requirements say "BNB prohibited",
    # then Trial follows FREE constraints for tokens.
    return ["BTC", "ETH"]

def assert_token_allowed(user: User, token: str):
    """
    Raises 403 if token is not allowed for the user's plan.
    """
    token_norm = normalize_token(token)
    allowed = get_allowed_tokens(user)
    
    if token_norm not in allowed:
         raise HTTPException(
             status_code=403, 
             detail={
                 "code": "TOKEN_RESTRICTED", 
                 "message": f"Access to {token_norm} is restricted on your current plan. Upgrade to trade more assets.",
                 "allowed": allowed
             }
         )
