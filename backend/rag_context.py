from __future__ import annotations

import random
from pathlib import Path
from typing import Dict, Optional, Any

import requests

BASE_DIR = Path(__file__).resolve().parent
BRAIN_DIR = BASE_DIR / "brain"

COINGECKO_IDS: Dict[str, str] = {
    "ETH": "ethereum",
    "BTC": "bitcoin",
    "SOL": "solana",
}


def _load_snippet(token: str, name: str) -> str:
    """
    Carga un archivo de brain/{token}/{name}.* y devuelve
    UN snippet aleatorio separado por '---'.

    Si no existe o está vacío, devuelve cadena vacía.
    """
    token = token.lower()
    # insights = .md, el resto los hemos dejado como .txt
    if name == "insights":
        path = BRAIN_DIR / token / "insights.md"
    else:
        path = BRAIN_DIR / token / f"{name}.txt"

    if not path.exists():
        return ""

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return ""

    # Separar por '---' para tener variación
    parts = [p.strip() for p in text.split("\n---\n") if p.strip()]
    if not parts:
        return text

    return random.choice(parts)


def _get_realtime_snapshot(token: str) -> Optional[str]:
    """
    Obtiene un snapshot simple de precio y cambio 24h desde CoinGecko.
    No debe romper el flujo si falla: devuelve None en caso de error.
    """
    token_upper = token.upper()
    cg_id = COINGECKO_IDS.get(token_upper)
    if not cg_id:
        return None

    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": cg_id,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
            },
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
        info = data.get(cg_id)
        if not info:
            return None

        price = info.get("usd")
        change = info.get("usd_24h_change")

        if price is None or change is None:
            return None

        return f"{token_upper} = {price:.2f} USD · 24h: {change:+.2f}%"
    except Exception:
        # No queremos tirar la señal porque CoinGecko falle un día
        return None


from narrative_engine import generate_narrative  # noqa: E402


def build_token_context(
    token: str, market_data: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Devuelve un diccionario con contexto RAG listo.
    Prioriza el MOTOR NARRATIVO DINÁMICO para asegurar calidad en todos los tokens
    (no solo los que tienen archivos estáticos).

    Si existen archivos manuales en brain/, los usa como "override" o complemento.
    """
    token_upper = token.upper()

    # 1. Cargar Archivos Manuales (si existen "Overrides" específicos)
    file_insights = _load_snippet(token_upper, "insights")
    file_news = _load_snippet(token_upper, "news")
    file_sentiment = _load_snippet(token_upper, "sentiment")
    file_onchain = _load_snippet(token_upper, "onchain")

    snapshot = _get_realtime_snapshot(token_upper)

    # 2. Generar Narrativa Dinámica (Fallback de Alta Calidad)
    # Si market_data no viene, usamos defaults en el engine
    if not market_data:
        # Minimal dummy data to prevent crash if backend didn't pass it yet
        market_data = {"price": 0, "change_24h": 0, "rsi": 50, "trend": "NEUTRAL"}

    try:
        dynamic = generate_narrative(token_upper, market_data)
    except Exception as e:
        print(f"[RAG CONTEXT] ⚠️ Error generating narrative for {token}: {e}")
        # Fallback safe
        dynamic = {
            "news": "Análisis técnico en curso.",
            "sentiment": "Mercado mixto a la espera de dirección.",
            "insights": "Monitorear volumen en zonas clave.",
        }

    # 3. Decidir Fuente Final (Preferimos Dynamic si no hay File, o mezclamos)
    # Estrategia: "Dynamic First" para Sentiment/News (más fresco), "File First" para Insights (más profundo si existe)

    final_sentiment = file_sentiment if file_sentiment else dynamic["sentiment"]
    final_news = file_news if file_news else dynamic["news"]
    # Insights: Los del engine son buenos, pero si escribí algo a mano en .md, úsalo.
    final_insights = file_insights if file_insights else dynamic["insights"]

    # Onchain suele ser específico, si no hay file, usamos el insight onchain generico del engine si existe o nada
    final_onchain = file_onchain

    context_blocks = []

    if final_insights:
        context_blocks.append(f"## Insights ({token_upper})\n{final_insights}")

    if final_news:
        context_blocks.append(f"## Narrativa / Noticias\n{final_news}")

    if final_onchain:
        context_blocks.append(f"## On-Chain\n{final_onchain}")

    if final_sentiment:
        context_blocks.append(f"## Sentimiento ({token_upper})\n{final_sentiment}")

    if snapshot:
        context_blocks.append(f"## Snapshot en tiempo real\n{snapshot}")

    full_context = "\n\n".join(context_blocks).strip()

    return {
        "token": token_upper,
        "raw_context": full_context,
        "snapshot": snapshot or "",
        "insights": final_insights,
        "news": final_news,
        "onchain": final_onchain or "",
        "sentiment": final_sentiment,
    }
