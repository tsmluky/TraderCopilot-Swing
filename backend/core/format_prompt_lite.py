from __future__ import annotations



def format_lite_prompt(token: str, timeframe: str) -> str:
    # now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"[LITE] {token.upper()} {timeframe} — genera una señal clara y cuantificable con entry/tp/sl."
