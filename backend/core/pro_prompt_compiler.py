"""
PRO Prompt Compiler
Assembles the Context Pack into a strict prompt for Institutional Analysis.
Enforces Markdown structure.
"""
from typing import Dict, Any
import re

REQUIRED_SECTIONS = [
    "## Thesis",
    "## Market Regime",
    "## Structural Analysis",
    "## Catalysts & Flows",
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
    brain.get("playbook", "Trade per standard technicals.")
    brain.get("news_digest", "No recent news.")

    # Language Config
    lang_name = "Spanish" if language == "es" else "English"
    
    # Horizon Localization
    horizon_weeks = "2-6 Weeks"
    if language == "es":
        horizon_weeks = "2-6 Semanas"
    
    prompt = f"""
You are the Head of Quantitative Strategy at a top-tier Crypto Hedge Fund.
Your task is to write a **Premium Institutional Swing Report** for {token}.

**INTERNAL GUIDELINES (STRICT):**
1. **Tone**: Authoritative, concise, precision-focused. No "fluff" or generic definitions.
2. **Perspective**: Use "We", "Our Model", "Institutional Flows".
3. **Horizon**: {horizon_weeks} (Swing/Position).
4. **No Retail Disclaimers**: Do not use phrases like "Not financial advice".
   We are professionals. Use "Invalidation", "Risk Parameters".
5. **Output Language**: {lang_name}.

---

### INPUT DATA

**1. Market Snapshot:**
- Price: ${market.get('price')} (Vol: {market.get('volatility')}%)
- Trend: {market.get('trend_daily')}

**2. Quant Engine Signal:**
- Status: **{setup.get('display')}**
- Rationale: {setup.get('rationale')}
(If NEUTRAL, explain why we are sitting on hands. If ACTIVE, sell it with conviction.)

**3. Intellectual Capital (Internal Research):**
- **Thesis**: {thesis_txt[:500]}...
- **Risks**: {risk_txt[:500]}...
- **Catalysts**: {catalyst_txt[:500]}...

**4. Client Inquiry:**
{user_message or "N/A"}

---

### REPORT FORMAT (STRICT MARKDOWN)

## Thesis
**(Executive Summary)**
Write a high-level conviction statement focusing on the primary driver for this trade.

## Market Regime
(Assess the environment: Risk-On/Off, Liquidity, Volatility. Is this a trend or chop environment?)

## Structural Analysis
(Key Levels & Market Structure. Be precise with "$" figures.)

## Catalysts & Flows
(What moves the needle? Events, On-chain data, Macro correlations.)

## Risks & Invalidation
(The "Kill Switch". Specific invalidation level.)

## Scenarios
*   **Base Case (50%):** (The most likely path. Be specific.)
*   **Bull Case (30%):** (Upside tail risk.)
*   **Bear Case (20%):** (Downside protection.)

## Execution Plan
(Direct actionable advice based on Quant Engine Status: **{setup.get('display')}**)

*   **Action:** (Wait / Accumulate / Distribute)
*   **Entry Zone:** (Specific Range)
*   **Invalidation (Stop):** (Hard Level)
*   **Targets:** (TP1, TP2)

## Confirmation Checklist
(3 bullet points for final trigger confirmation)

## TL;DR
(2 sentences max. Bottom line up front.)

---
Write the report now in **{lang_name}**. 
IMPORTANT: 
- Use `## Header` (H2) for every section title exactly as shown above.
- LEAVE A BLANK LINE BEFORE AND AFTER EVERY HEADER.
- Use **bold** for key numbers and signals.
"""
    return prompt.strip()

def validate_pro_output(text: str) -> bool:
    """
    Checks if all required headers are present.
    """
    if not text:
        return False
    
    missing = []
    # We check keys without ## because sometimes we strip them or they vary slightly
    for sec in REQUIRED_SECTIONS:
        # Check simple presence
        if sec.replace('## ', '') not in text:
            missing.append(sec)
            
    if missing:
        return False
    return True



def fix_markdown_spacing(text: str) -> str:
    """
    Post-processes the AI output to ensure clean Markdown rendering.
    Specifically fixes:
    1. Headers glued to content (e.g. '## ThesisContent')
    2. Missing newlines before/after headers.
    3. Forces paragraph breaks for single newlines.
    """
    if not text:
        return text

    clean_text = text

    # 1. Force paragraph breaks FIRST: Convert single \n to \n\n
    # This ensures we have clear lines to work with.
    # Look for a newline that is NOT preceded by a newline and NOT followed by a newline
    clean_text = re.sub(r'(?<!\n)\n(?!\n)', '\n\n', clean_text)

    # 2. Ensure Headers are distinct and consistently formatted as H2
    sections = [
        "Thesis", "Market Regime", "Structural Analysis",
        "Catalysts & Flows", "Risks & Invalidation",
        "Scenarios", "Execution Plan", "Confirmation Checklist", "TL;DR"
    ]

    for sec in sections:
        # Regex to capture the section header in various AI-generated formats:
        # Matches: Newline/Start, optional * or #, spaces, Name, optional * or # or :, spaces
        pattern = rf"(?i)(?:^|\n)\s*(?:[*#]*)\s*{re.escape(sec)}\s*(?:[*#:]*)\s*"
        
        # Replacement: Double newline, ## Header, Double newline
        replacement = f"\n\n## {sec}\n\n"
        
        clean_text = re.sub(pattern, replacement, clean_text)

    # 3. Clean up excessive newlines (3+ -> 2)
    clean_text = re.sub(r"\n{3,}", "\n\n", clean_text)
    
    return clean_text.strip()
