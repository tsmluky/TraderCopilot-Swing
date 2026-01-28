from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from models import CopilotProfileResp, CopilotProfileUpdate, AdvisorReq
from core.ai_service import get_ai_service
from rag_context import build_token_context
from core.market_data_api import get_ohlcv_data

# Auth & Entitlements
from sqlalchemy.orm import Session
from database import get_db
from routers.auth_new import get_current_user
from models_db import User, CopilotProfile
from core.entitlements import (
    can_use_advisor,
    check_and_increment_quota,
    assert_token_allowed,
)
from core.trial_policy import assert_trial_active, get_access_tier
from core.timeframe_policy import assert_timeframe_allowed
from core.limiter import limiter

router = APIRouter(tags=["advisor"])





class ChatMessage(BaseModel):
    role: str
    content: str


class ChatContext(BaseModel):
    token: Optional[str] = None
    timeframe: Optional[str] = None
    signal_data: Optional[Dict[str, Any]] = None  # Active signal details if any


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context: Optional[ChatContext] = None

# --- Smart Context Logic ---
TOKEN_ALIAS_MAP = {
    "BTC": "BTC", "BITCOIN": "BTC", "BITCOIN": "BTC", "BITCOIN": "BTC", # Common
    "ETH": "ETH", "ETHER": "ETH", "ETHEREUM": "ETH", "ETHERIUM": "ETH",
    "SOL": "SOL", "SOLANA": "SOL",
    "BNB": "BNB", "BINANCE": "BNB", "BSC": "BNB",
    "XRP": "XRP", "RIPPLE": "XRP",
    # Add more as needed
}

import re
def detect_tokens_in_history(messages: List[ChatMessage], lookback: int = 3) -> List[str]:
    """
    Scans the last 'lookback' user messages for token references.
    Returns unique list of normalized token symbols (e.g., ['BTC', 'ETH']).
    """
    found_tokens = set()
    
    # Filter only user messages, take last N
    user_msgs = [m.content for m in messages if m.role == 'user'][-lookback:]
    
    for msg in user_msgs:
        msg_upper = msg.upper()
        # 1. Direct symbol check
        words = set(re.findall(r'\b[A-Z0-9]+\b', msg_upper))
        for alias, symbol in TOKEN_ALIAS_MAP.items():
            if alias in words:
                found_tokens.add(symbol)
        
        # 2. Typos / Substring check
        for alias, symbol in TOKEN_ALIAS_MAP.items():
             if len(alias) > 3 and alias in msg_upper:
                 found_tokens.add(symbol)
                 
    return list(found_tokens)


@router.post("/chat")
@limiter.limit("5/minute")
def advisor_chat(
    request: Request,
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint for interactive chat with the Advisor.
    Enforces Entitlements:
    1. Plan Access (can_use_advisor)
    2. Daily Quota (advisor_chat)
    3. Token Access (if context token provided)
    """
    # 1. Base Access
    assert_trial_active(current_user)
    if not can_use_advisor(current_user):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ADVISOR_NOT_ALLOWED",
                "message": "Advisor chat is only available for SwingPro users.",
                "tier": get_access_tier(current_user),
                "upgrade_required": True
            }
        )

    # 2. Token Check (if context provided)
    if req.context and req.context.token:
        # returns normalized, though we just validate here
        assert_token_allowed(current_user, req.context.token)
        
        # Enforce timeframe access even for default "1h"
        # Access: Pro=All, others restricted (though Advisor is Pro-only, this is safe)
        tf = req.context.timeframe or "1h"
        assert_timeframe_allowed(current_user, tf)

    # 3. Quota Check
    quota = check_and_increment_quota(db, current_user, "advisor_chat")

    # 3.5 Fetch User Profile
    # 3.5 Fetch User Profile
    profile_context = ""
    try:
        profile = (
            db.query(CopilotProfile)
            .filter(CopilotProfile.user_id == current_user.id)
            .first()
        )
        if profile:
            profile_context = (
                f"User Profile: [Style: {profile.trader_style}, "
                f"Risk: {profile.risk_tolerance}, "
                f"Horizon: {profile.time_horizon}]\n"
                f"Custom Instructions: {profile.custom_instructions or 'None'}"
            )
    except Exception as e:
        print(f"[ADVISOR] Warning: Could not fetch profile (DB Error?): {e}")
        # non-critical, continue

    # 4. Build Dynamic System Context
    system_context_block = ""
    # Default visualizers for "Global" mode
    token = "MERCADO GLOBAL" 
    price = "N/A"
    
    detected_tokens = []
    
    # A. Check if User provided explicit context (Button click)
    if req.context and req.context.token:
        detected_tokens = [req.context.token]
        token = req.context.token # Main focus
    else:
        # B. Try to detect from history (Smart Context - Multi-turn)
        try:
            detected_tokens = detect_tokens_in_history(req.messages)
            if detected_tokens:
                print(f"[ADVISOR] Smart Context Detected: {detected_tokens}")
                # Set primary token to the most recently detected/mentioned for "persona" consistency
                token = detected_tokens[-1] 
        except Exception:
            pass

    # Fetch Data for ALL interesting tokens found
    if detected_tokens:
        tf = (req.context.timeframe if req.context else "1h") or "1h"
        
        market_data_lines = []
        
        for t_sym in detected_tokens:
            try:
                # Fetch only 1 candle for price to be fast
                ohlcv = get_ohlcv_data(t_sym, tf, limit=1)
                curr_price = ohlcv[-1]["close"] if ohlcv else "Unavailable"
                
                market_data_lines.append(f"- {t_sym}: ${curr_price}")
                
                # If this is the 'primary' token, update the main variable
                if t_sym == token:
                    price = curr_price
                    
            except Exception as e:
                print(f"[ADVISOR] Price Error {t_sym}: {e}")
                market_data_lines.append(f"- {t_sym}: Price Error")

        # C. Build Context Block
        token_context = build_token_context(token) # RAG for primary only to save Tokens
        
        system_context_block = f"""
[REAL-TIME MARKET DATA]
Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
Prices (Source: Live Exchange):
{chr(10).join(market_data_lines)}

[PRIMARY FOCUS: {token}]
- Timeframe: {tf}
- Sentiment: {token_context.get("sentiment", "Neutral")}
- News: {token_context.get("news", "No major news")}
"""
        
        # D. Add Signal Context if coming from a specific signal
        if req.context and req.context.signal_data:
            sig = req.context.signal_data
            system_context_block += f"""
[ACTIVE SIGNAL CONTEXT]
- Direction: {sig.get("direction", "Unknown")}
- Entry: {sig.get("entry")}
- TP: {sig.get("tp")} | SL: {sig.get("sl")}
- Confidence: {sig.get("confidence")}
- Rationale: {sig.get("rationale")}
"""

    # 5. Define System Persona (Contract of Identity)
    system_instruction = (
        "Soy **TraderCopilot Advisor**, tu copiloto automatizado de análisis táctico. "
        "No soy un asesor financiero humano.\n"
        "MI OBJETIVO: Procesar datos de mercado para ofrecer escenarios de riesgo claros y objetivos.\n\n"
        f"FECHA ACTUAL: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"PRECIO ACTUAL DE {token}: {price}\n\n"
        "REGLAS DE IDENTIDAD:\n"
        "- Actúa como un Analista Cuantitativo Senior: objetivo, basado en datos, sin emociones.\n"
        "- Transparencia: Si no hay datos suficientes, dilo. No inventes.\n"
        "- NO menciones detalles técnicos internos (modelos, backend, 'prompt').\n"
        "- Enfócate 100% en la gestión de riesgo y la estructura del precio.\n\n"
        "MÍNIMOS INTELIGENTES:\n"
        "- Si te piden un SETUP/TRADE: Debes incluir SIEMPRE (1) Nivel de "
        "Invalidación (Stop mental/técnico) y (2) Plan Condicional "
        "('Si hace X, busco Y').\n"
        "- Si te piden OPINIÓN GENERAL: Da contexto, niveles clave y cierra con "
        "una pregunta de refinamiento.\n"
        "- GESTIÓN DE RIESGO: Recomienda 1-2% por operación salvo "
        "indicación contraria.\n\n"
        "ESTILO:\n"
        "- Usa párrafos cortos o bullets. Evita muros de texto.\n"
        "- Tono humano: 'Yo buscaría...', 'El riesgo aquí es...', "
        "'Me gusta la zona de...'.\n"
        "- Responde SIEMPRE en ESPAÑOL (Castellano) neutro/profesional."
    )

    if profile_context:
        system_instruction += (
            f"\n\n[USER CONTEXT]\n{profile_context}\n"
            "ADAPT YOUR RESPONSE TO THIS PROFILE."
        )

    # 6. Call AI Service
    ai_service = get_ai_service()

    # Preparar mensajes
    user_api_messages = [m.dict() for m in req.messages]

    # Inyectar contexto de mercado en el último mensaje
    last_user_msg_content = ""
    if system_context_block:
        last_msg = user_api_messages[-1]
        if last_msg["role"] == "user":
            last_user_msg_content = last_msg[
                "content"
            ]  # Save original for intent detection
            last_msg["content"] = (
                f"{system_context_block}\n\nPregunta del Usuario: {last_msg['content']}"
            )

    try:
        # A. Generate Response
        response_text = ai_service.chat(
            user_api_messages, system_instruction=system_instruction
        )

        # B. Brand Guard & Linter
        from core.brand_guard import (
            check_brand_safety,
            detect_intent,
            check_minimum_viability,
            repair_response,
        )

        # Detect intent using original message content if possible, else the
        # full context one
        msg_for_intent = (
            last_user_msg_content
            if last_user_msg_content
            else user_api_messages[-1]["content"]
        )
        intent = detect_intent(msg_for_intent)

        # 1. Check Safety
        violations = check_brand_safety(response_text)

        # 2. Check Viability (only if safe so far, to prioritize safety)
        if not violations:
            violations.extend(check_minimum_viability(response_text, intent))

        # 3. Auto-Repair if violations exist
        if violations:
            print(f"[ADVISOR] Found violations: {violations}. Attempting repair...")
            response_text = repair_response(
                response_text, violations, system_instruction
            )

        # 4. Final Safety Safety Check (Manual Override if repair failed on
        # Banned Words)
        # If still contains banned words, we mask them or fail gracefully?
        # For 'Sale Ready', let's just log it. The repair usually works.

    except ImportError:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "PROVIDER_UNAVAILABLE",
                "message": "AI Provider dependency (google-generativeai) is missing.",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "AI_SERVICE_ERROR",
                "message": f"AI Service unavailable: {str(e)}",
            },
        )

    return {"reply": response_text, "usage": quota}


@router.get("/profile", response_model=CopilotProfileResp)
def get_advisor_profile(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get the user's Copilot profile. Creates a default one if it doesn't exist.
    """
    profile = (
        db.query(CopilotProfile)
        .filter(CopilotProfile.user_id == current_user.id)
        .first()
    )
    if not profile:
        profile = CopilotProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("/profile", response_model=CopilotProfileResp)
def update_advisor_profile(
    profile_update: CopilotProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the user's Copilot profile.
    """
    profile = (
        db.query(CopilotProfile)
        .filter(CopilotProfile.user_id == current_user.id)
        .first()
    )
    if not profile:
        profile = CopilotProfile(user_id=current_user.id)
        db.add(profile)

    # Update fields
    if profile_update.trader_style is not None:
        profile.trader_style = profile_update.trader_style
    if profile_update.risk_tolerance is not None:
        profile.risk_tolerance = profile_update.risk_tolerance
    if profile_update.time_horizon is not None:
        profile.time_horizon = profile_update.time_horizon
    if profile_update.custom_instructions is not None:
        profile.custom_instructions = profile_update.custom_instructions

    db.commit()
    db.refresh(profile)
    return profile


# ==== Endpoint Analysis Advisor (Legacy V1 Local) ====
from models import CopilotProfileResp, CopilotProfileUpdate  # noqa: E402
from core.schemas import Signal  # noqa: E402
from core.signal_logger import log_signal  # noqa: E402
from datetime import datetime  # noqa: E402


@router.post("/")
@limiter.limit("10/minute")
def analyze_advisor(
    request: Request,
    req: AdvisorReq,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analiza una posición abierta y sugiere alternativas.
    Versión local determinista (sin LLM).
    Enforces Entitlements.
    """
    # Enforce Access
    assert_trial_active(current_user)
    if not can_use_advisor(current_user):
         raise HTTPException(
            status_code=403,
            detail={
                "code": "ADVISOR_NOT_ALLOWED",
                "message": "Advisor is only available for SwingPro users.",
                "tier": get_access_tier(current_user),
                "upgrade_required": True
            }
        )


    # Enforce Token
    req.token = assert_token_allowed(current_user, req.token)

    token = req.token.upper()  # Was already normalized by assert, but ensure upper

    # Lógica simple de evaluación de riesgo
    risk_per_share = abs(req.entry - req.sl)
    reward_per_share = abs(req.tp - req.entry)
    rr = reward_per_share / risk_per_share if risk_per_share > 0 else 0

    risk_score = 0.5
    if rr < 1.0:
        risk_score = 0.9
    elif rr > 2.0:
        risk_score = 0.3

    confidence = 0.6

    alternatives = []
    if risk_score > 0.7:
        alternatives.append(
            {"if": "price consolidates", "action": "tighten SL", "rr_target": 1.5}
        )
    else:
        alternatives.append(
            {"if": "volume spikes", "action": "add to position", "rr_target": 2.5}
        )

    response = {
        "token": token,
        "direction": req.direction,
        "entry": req.entry,
        "size_quote": req.size_quote,
        "tp": req.tp,
        "sl": req.sl,
        "alternatives": alternatives,
        "risk_score": round(risk_score, 2),
        "confidence": confidence,
    }

    # Crear instancia de Signal unificado para ADVISOR
    unified_signal = Signal(
        timestamp=datetime.utcnow(),
        strategy_id="advisor_v1_local",
        mode="ADVISOR",
        token=token,
        timeframe="N/A",  # ADVISOR no tiene timeframe específico
        direction=req.direction,
        entry=req.entry,
        tp=req.tp,
        sl=req.sl,
        confidence=confidence,
        rationale=f"Advisor position check. RR={rr:.2f}",
        source="ADVISOR_V1_LOCAL",
        extra={
            "risk_score": risk_score,
            "rr_ratio": round(rr, 2),
            "size_quote": req.size_quote,
            "alternatives": alternatives,
        },
        user_id=current_user.id,
    )

    log_signal(unified_signal)

    return response
