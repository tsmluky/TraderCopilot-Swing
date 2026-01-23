"""
Config centralizado de estrategias QUANT que TraderCopilot
considera "core" para el MVP.

Este archivo NO ejecuta nada: solo define qué estrategias se consideran
titulares, para que el backend las pueda usar a la hora de:
- escanear el mercado de forma periódica
- exponer señales vivas en /signals/live
- mostrar metadatos en la UI
"""

from typing import TypedDict, List, Dict, Literal


class QuantStrategy(TypedDict):
    id: str  # identificador interno único
    label: str  # nombre legible para UI
    symbol: str  # par, ej. "ETHUSDT"
    token: str  # token normalizado, ej. "ETH"
    timeframe: str  # ej. "4h"
    engine_id: str  # nombre de la estrategia en trading_lab (ma_cross_v1, etc.)
    profile: Literal["core", "experimental"]
    params: Dict[str, float]  # parámetros específicos (fast, slow, etc.)


# Estrategias CORE del MVP
CORE_STRATEGIES: List[QuantStrategy] = [
    # ETHUSDT · MA 20/50 @ 4h
    {
        "id": "eth_ma20_50_4h",
        "label": "ETH · MA Cross 20/50 · 4h",
        "symbol": "ETHUSDT",
        "token": "ETH",
        "timeframe": "4h",
        "engine_id": "ma_cross_v1",
        "profile": "core",
        "params": {
            "fast": 20,
            "slow": 50,
        },
    },
    # SOLUSDT · MA 20/50 @ 4h
    {
        "id": "sol_ma20_50_4h",
        "label": "SOL · MA Cross 20/50 · 4h",
        "symbol": "SOLUSDT",
        "token": "SOL",
        "timeframe": "4h",
        "engine_id": "ma_cross_v1",
        "profile": "core",
        "params": {
            "fast": 20,
            "slow": 50,
        },
    },
]

# Candidatos experimentales (NO usados en el MVP todavía).
# Los dejamos definidos por si queremos activarlos en una versión futura.
EXPERIMENTAL_STRATEGIES: List[QuantStrategy] = [
    {
        "id": "eth_donchian20_1d",
        "label": "ETH · Donchian 20 · 1d (experimental, DD alto)",
        "symbol": "ETHUSDT",
        "token": "ETH",
        "timeframe": "1d",
        "engine_id": "donchian_breakout_v1",
        "profile": "experimental",
        "params": {
            "window": 20,
        },
    },
    {
        "id": "sol_donchian20_1d",
        "label": "SOL · Donchian 20 · 1d (experimental, DD alto)",
        "symbol": "SOLUSDT",
        "token": "SOL",
        "timeframe": "1d",
        "engine_id": "donchian_breakout_v1",
        "profile": "experimental",
        "params": {
            "window": 20,
        },
    },
]


def get_core_strategies() -> List[QuantStrategy]:
    """
    Devuelve la lista de estrategias QUANT que se consideran
    activas para el MVP.
    """
    return CORE_STRATEGIES.copy()


def get_all_strategies() -> List[QuantStrategy]:
    """
    Devuelve core + experimentales. Útil para páginas de configuración
    avanzada o paneles internos.
    """
    return CORE_STRATEGIES + EXPERIMENTAL_STRATEGIES
