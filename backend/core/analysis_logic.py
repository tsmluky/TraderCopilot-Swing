from typing import Dict, Any, Tuple
from datetime import datetime
import traceback
import json

# Imports from project
from models import LiteSignal, ProReq
from rag_context import build_token_context

# from deepseek_client import generate_pro_analysis # REMOVED (Legacy)
# from narrative_engine import generate_dynamic_rationale

from fastapi import HTTPException


def _build_lite_from_market(
    token: str, timeframe: str, market: Dict[str, Any]
) -> Tuple[LiteSignal, Dict[str, Any]]:
    """
    Aplica la lógica LITE v2 sobre los datos de mercado y devuelve:
    - LiteSignal (modelo oficial)
    - dict con indicadores (para enriquecer la respuesta)
    """
    # Extract & normalize
    try:
        price = float(market["price"])
        rsi = float(market["rsi"])
        trend = str(market.get("trend", "NEUTRAL")).upper()
        ema21 = float(market["ema21"])
        macd = float(market["macd"])
        macd_hist = float(market["macd_hist"])
        atr = float(market.get("atr", price * 0.01))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"Invalid market data: {exc!r}")

    if price <= 0:
        raise HTTPException(status_code=502, detail="Market data inválido: price <= 0")

    # == 2. Inicialización ==
    direction: str | None = None
    rationale = "Contexto sin setup claro."
    confidence = 0.5
    tp = price
    sl = price

    # == 3. Lógica de decisión (Lite v2 adaptada) ==

    # A) Reversión (Contratendencia)
    if rsi < 30:
        direction = "long"
        rationale = f"Setup LONG (scalp) por sobreventa extrema (RSI {rsi:.1f}). Posible rebote."
        confidence = 0.7
        sl = price * 0.98
        tp = price * 1.03

    elif rsi > 75:
        direction = "short"
        rationale = f"Setup SHORT (scalp) por sobrecompra extrema (RSI {rsi:.1f}). Posible corrección."
        confidence = 0.7
        sl = price * 1.02
        tp = price * 0.97

    # B) Trend Following (a favor de tendencia) en rango de RSI medio
    elif 35 < rsi < 65:
        # Setup bajista
        if price < ema21 and macd < 0 and macd_hist < 0:
            direction = "short"
            rationale = (
                "Setup SHORT (trend): precio < EMA21 con MACD bajista. "
                "Tendencia bajista consolidada."
            )
            confidence = 0.8
            sl = price * 1.025
            tp = price * 0.95

        # Setup alcista
        elif price > ema21 and macd > 0 and macd_hist > 0:
            direction = "long"
            rationale = (
                "Setup LONG (trend): precio > EMA21 con MACD alcista. "
                "Tendencia alcista consolidada."
            )
            confidence = 0.8
            sl = price * 0.975
            tp = price * 1.05

    # C) Fallback si no hay setup claro (pero siempre devolvemos long|short)
    if direction is None:
        if trend == "BULLISH":
            direction = "long"
            rationale = (
                f"Sin setup claro, pero tendencia global alcista (trend={trend}, RSI {rsi:.1f}). "
                "Señal exploratoria de menor confianza."
            )
        else:
            direction = "short"
            rationale = (
                f"Sin setup claro, pero tendencia global bajista (trend={trend}, RSI {rsi:.1f}). "
                "Señal exploratoria de menor confianza."
            )
        confidence = 0.45
        if direction == "long":
            sl = price * 0.985
            tp = price * 1.02
        else:
            sl = price * 1.015
            tp = price * 0.98

    # Limitar rationale a 240 caracteres por contrato (Wait, we removed this limit in models.py, but logic stays here?)
    # Users requirement was no limits. The code I read from main.py still had it:
    # 339:     if len(rationale) > 240:
    # 340:         rationale = rationale[:237] + "..."
    # I MUST REMOVE THIS!!!
    # This refactoring is also a cleanup.

    # Timestamp UTC (sin tzinfo pero con sufijo Z en logs)
    now_dt = datetime.utcnow()

    lite = LiteSignal(
        timestamp=now_dt,
        token=token.upper(),  # ETH/BTC/SOL/XAU
        timeframe=timeframe,
        direction=direction,  # type: ignore[arg-type]
        entry=round(price, 6),  # Increased precision for low-cap tokens
        tp=round(tp, 6),
        sl=round(sl, 6),
        confidence=round(confidence, 2),
        rationale=rationale,
        source="lite-rule@v2",  # versión de la regla LITE
    )

    indicators = {
        "rsi": rsi,
        "trend": trend,
        "macd": round(macd, 2),
        "ema21": round(ema21, 2),
        "atr": atr,
        "source_exchange": market.get("source_exchange", "unknown"),
    }

    return lite, indicators


def _load_brain_context(
    token: str, market_data: Dict[str, Any] = None
) -> Dict[str, str]:
    """
    Wrapper sobre build_token_context(token)
    """
    token_ctx = build_token_context(token, market_data)
    return {
        "insights": token_ctx.get("insights", "") or "",
        "news": token_ctx.get("news", "") or "",
        "onchain": token_ctx.get("onchain", "") or "",
        "sentiment": token_ctx.get("sentiment", "") or "",
        "snapshot": token_ctx.get("snapshot", "") or "",
        "raw_context": token_ctx.get("raw_context", "") or "",
    }


def _inject_rag_into_lite_rationale(
    token: str,
    timeframe: str,
    lite: LiteSignal,
    market: Dict[str, Any],
) -> str:
    """
    Ajusta la rationale de LITE combinando:
    - Texto base de la regla (lite-rule@v2).
    - Comentario simple sobre el entorno 24h.
    - Una frase corta de contexto RAG (sentiment/news) sin recortes agresivos.
    """
    base = (lite.rationale or "").strip()
    extra_parts = []

    # 1) Ajuste por cambio 24h
    change_24h = market.get("price_change_24h")
    if isinstance(change_24h, (int, float)):
        ch = round(change_24h, 2)
        if ch <= -5 and lite.direction == "long":
            extra_parts.append(
                "24h en fuerte caída; usar tamaño de posición conservador."
            )
        elif ch >= 5 and lite.direction == "short":
            extra_parts.append("24h muy alcistas; evitar shorts agresivos.")
        elif abs(ch) >= 4:
            extra_parts.append("Entorno 24h volátil; gestionar bien el riesgo.")

    # 2) Frase de contexto desde RAG
    try:
        brain = _load_brain_context(
            token, market
        )  # Optim: pass market if possible or just token
        # main.py called _load_brain_context(token). It's fine.
        raw_sentiment = (brain.get("sentiment") or "").strip()
        raw_news = (brain.get("news") or "").strip()

        raw = raw_sentiment or raw_news

        tagline = None
        if raw:
            for line in raw.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                tagline = line.lstrip("# ").strip()
                break

        if tagline:
            extra_parts.append(f"Ctx: {tagline}")
    except Exception:
        pass

    combined = base
    if extra_parts:
        if not combined.endswith("."):
            combined += "."
        combined += " " + " ".join(extra_parts)

    return combined


async def _build_pro_analysis(
    req: ProReq,
    lite: LiteSignal,
    indicators: Dict[str, Any],
    brain: Dict[str, str],
) -> Dict[str, Any]:
    """
    Construye un prompt y delega en Gemini Flash para el análisis PRO (Output JSON).
    """
    # 1. Extract context
    token_up = lite.token
    tf = lite.timeframe
    user_msg = (req.user_message or "").strip()

    rsi = indicators.get("rsi", "N/D")
    trend = indicators.get("trend", "NEUTRAL")
    ema21 = indicators.get("ema21", "N/D")

    # Format numbers
    rsi_str = f"{rsi:.1f}" if isinstance(rsi, (int, float)) else str(rsi)
    ema21_str = f"{ema21:.2f}" if isinstance(ema21, (int, float)) else str(ema21)

    insights = brain.get("insights", "Sin información").strip()
    news = brain.get("news", "Sin noticias recientes").strip()
    onchain = brain.get("onchain", "Sin datos onchain relevantes").strip()
    sentiment_txt = brain.get("sentiment", "Neutral").strip()
    snapshot = brain.get("snapshot", "").strip()

    # 2. Build Prompt
    # 2. Build Prompt (Institucional / V3 Optimized)
    system_instruction = (
        "Eres TraderCopilot, un Senior Hedge Fund Analyst especializado en Crypto Quant.\n"
        "Tu objetivo es generar un 'Institutional Report' en formato JSON.\n"
        "NO describas los indicadores (ej 'RSI es 50'), eso ya lo veo.\n"
        "INTERPRETA la confluencia de datos: ¿Qué nos dice la divergencia entre Precio y OnChain?\n"
        "¿Por qué la EMA21 actúa de barrera?\n\n"
        "ESTRUCTURA DE RESPUESTA (JSON estricto):\n"
        "{\n"
        "  \"context\": {\n"
        "    \"summary\": \"Narrativa macro/fundamental. Causa y efecto.\",\n"
        "    \"sentiment\": \"Bearish/Bullish/Neutral\"\n"
        "  },\n"
        "  \"technical\": {\n"
        "    \"summary\": \"Análisis de estructura de mercado, liquidez y Price Action.\",\n"
        "    \"key_levels\": [\"Soporte $X\", \"Resistencia $Y\"]\n"
        "  },\n"
        "  \"plan\": {\n"
        "    \"strategy\": \"Plan de ejecución preciso.\",\n"
        "    \"management\": \"Gestión de riesgo (Invalidación).\"\n"
        "  },\n"
        "  \"insight\": {\n"
        "    \"type\": \"Institutional Edge\",\n"
        "    \"content\": \"Dato no obvio que da ventaja (Alpha).\"\n"
        "  },\n"
        "  \"params\": {\"entry\": 0.0, \"tp\": 0.0, \"sl\": 0.0}\n"
        "}\n\n"
        "REGLAS DE CALIDAD:\n"
        "- Tono: Profesional, directo, sin relleno.\n"
        "- Razonamiento: Busca la 'Historia detrás del precio'.\n"
        "- Params: Optimiza entry/sl/tp basándote en volatilidad y estructura.\n"
        "- Idioma: Español Financiero Profesional.\n"
    )

    prompt = f"""
ANÁLISIS PRO PARA {token_up} ({tf}).

DATOS TÉCNICOS (Base LITE):
- Dirección: {lite.direction.upper()}
- RSI: {rsi_str} | EMA21: {ema21_str} | Tendencia: {trend}
- Sugeridos: Entry={lite.entry}, TP={lite.tp}, SL={lite.sl}

CONTEXTO RAG:
- Noticias: {news}
- Sentiment: {sentiment_txt}
- Insight: {insights}
- OnChain: {onchain}
- Snapshot: {snapshot}

USER REQUEST: {user_msg}

GENERA EL JSON AHORA.
"""

    # 3. Offload to threadpool
    from fastapi.concurrency import run_in_threadpool
    from core.ai_service import get_ai_service

    def _generate_safe():
        try:
            service = get_ai_service()
            # Call generate logic
            # Gemini Flash supports JSON mode via MIME type usually, but text works if prompted well.
            # We can try to enforce formatting in `generate_analysis` or just parse here.
            # Ideally ai_service could expose `generate_structured` but let's parse text for now.
            raw_text = service.generate_analysis(prompt, system_instruction=system_instruction)
            
            # Strip markdown fences if present
            clean_text = raw_text.replace("```json", "").replace("```", "").strip()
            try:
                return json.loads(clean_text)
            except json.JSONDecodeError:
                # [RELIABILITY FIX] Soft Fallback:
                # Si falla el JSON, no crasheamos. Devolvemos el texto crudo en la estructura.
                # Así el usuario SIEMPRE recibe el análisis de valor.
                
                print(f"[AI WARN] JSON Parsing failed. Using Raw Text Fallback. Len: {len(raw_text)}")
                
                try:
                    with open("analysis_fallback.log", "a", encoding="utf-8") as f:
                        f.write(f"[{datetime.utcnow()}] RAW TEXT CAPTURE:\n{raw_text}\n{'-'*50}\n")
                except Exception:
                    pass # Don't crash on logging

                # Intentar limpiar texto para que no sea inmenso en un solo campo
                # O simplemente ponerlo todo en context y el resto defaults.
                safe_summary = raw_text[:500] + "..." if len(raw_text) > 500 else raw_text
                
                return {
                    "context": {
                        "summary": safe_summary, 
                        "sentiment": "Neutral (Parse Error)"
                    },
                    "technical": {
                        "summary": "Ver análisis detallado en Contexto (Formato AI raw).", 
                        "key_levels": ["Soporte (Estimado)", "Resistencia (Estimado)"]
                    },
                    "plan": {
                        "strategy": "Gestión Manual recomendada (AI Format Issue).", 
                        "management": "Revisar gráfico."
                    },
                    "insight": {
                        "type": "Raw Output Preservation", 
                        "content": (
                            "La IA generó el análisis pero falló la estructura JSON. "
                            "La información principal está en 'Market Context'."
                        )
                    },
                    "params": {"entry": lite.entry, "tp": lite.tp, "sl": lite.sl}
                }
        except Exception as e:
            try:
                with open("analysis_crash.log", "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.utcnow()}] CRASH: {str(e)}\n{traceback.format_exc()}\n")
            except Exception:
                pass
            raise e

    return await run_in_threadpool(_generate_safe)
