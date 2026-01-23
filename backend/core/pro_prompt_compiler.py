"""
PRO Prompt Compiler
Assembles the Context Pack into a strict prompt for Institutional Analysis.
Enforces Markdown structure.
"""
from typing import Dict, Any

REQUIRED_SECTIONS = [
    "## Thesis",
    "## Market Regime",
    "## Structure & Levels",
    "## Catalysts",
    "## Risks & Invalidation",
    "## Scenarios",
    "## Execution Plan",
    "## Confirmation Checklist",
    "## TL;DR"
]

def compile_pro_prompt(context: Dict[str, Any], user_message: str = None, language: str = "es") -> str:
    """
    Generates the strict system prompt + user context.
    """
    token = context.get("token", "UNKNOWN")
    brain = context.get("brain", {})
    market = context.get("market", {})
    setup = context.get("setup_status", {})
    
    # Brain Injection
    thesis_txt = brain.get("thesis", "No specific thesis data.")
    risk_txt = brain.get("risk", "Standard crypto risks apply.")
    catalyst_txt = brain.get("catalysts", "No specific calendar events.")
    playbook_txt = brain.get("playbook", "Trade per standard technicals.")
    news_txt = brain.get("news_digest", "No recent news.")

    # Language Config
    lang_name = "Spanish" if language == "es" else "English"
    tone = "Professional/Institutional Tone"
    
    prompt = f"""
You are a Senior Institutional Crypto Analyst (Quant/Macro).
Your task is to write a **Professional Swing Trading Report** for {token}.

**INTERNAL CONSTRAINTS (STRICT):**
1. Horizon: **{context.get('horizon')}**.
2. No ambiguous "not financial advice" disclaimers. Use professional language ("invalidation level", "risk factors").
3. You MUST output strictly in the requested Markdown format.
4. Integrate the provided "Setup Status" from our Quant Engine without blindly following it—analyze it.
5. **Output Language**: {lang_name} ({tone}).

---

### INPUT DATA

**1. Market Snapshot (Daily):**
- Price: ${market.get('price')}
- 24h Change: {market.get('change_24h')}%
- Volatility: {market.get('volatility')}%
- Daily Trend: {market.get('trend_daily')}

**2. Quant Engine Setup Status (LITE-Swing):**
- Status: **{setup.get('display')}**
- Rationale: {setup.get('rationale')}
(Use this to inform the "Execution Plan" and "Scenarios".)

**3. Institutional Context (Brain):**
- **Thesis**: {thesis_txt[:500]}...
- **Risks**: {risk_txt[:500]}...
- **Catalysts**: {catalyst_txt[:500]}...
- **Playbook**: {playbook_txt[:500]}...
- **News Stream**: {news_txt[:500]}...

**4. User Question (Context):**
{user_message or "N/A"}

---

### OUTPUT FORMAT (MANDATORY)

You must produce a report with EXACTLY these headers (Markdown H2):

## Thesis
(Synthesize macro + token profile + current price action. First line must be: `**Horizon/Horizonte:** 2-6 {("weeks" if language == "en" else "semanas")} (Swing/Position)`)

## Market Regime
(Risk-on/off, Liquidity, Volatility Assessment)

## Structure & Levels
(Key Support/Resistance, Market Structure HH/LL)

## Catalysts
(Specific events or news driving price)

## Risks & Invalidation
(What kills the thesis? Specific price level for invalidation)

## Scenarios
- **Base Case** (% Prob): ...
- **Bull Case** (% Prob): ...
- **Bear Case** (% Prob): ...

## Execution Plan
(Actionable plan. Reference the Quant Engine Status: {setup.get('display')}. Suggest Entry Zone, Stop Loss, Take Profit targets.)

## Confirmation Checklist
(3-5 bullet points to confirm entry)

## TL;DR
(Executive summary)

---
Write the report now in **{lang_name}**.
"""
    return prompt.strip()

def validate_pro_output(text: str) -> bool:
    """
    Checks if all required headers are present.
    """
    if not text:
        return False
    
    missing = []
    for sec in REQUIRED_SECTIONS:
        if sec not in text:
            missing.append(sec)
            
    if missing:
        # Loose check: maybe they used # instead of ## or different casing?
        # For now, strict.
        return False
    return True
