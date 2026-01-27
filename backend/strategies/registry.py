# backend/strategies/registry.py
"""
Strategy Registry - Catálogo de estrategias disponibles.

Este módulo mantiene el registro de todas las estrategias que pueden
ejecutarse en el backend, tanto built-in como de trading_lab.
"""

from typing import Dict, List, Optional, Type
from .base import Strategy, StrategyMetadata


class StrategyRegistry:
    """
    Registro centralizado de estrategias disponibles.

    Permite:
    - Descubrir qué estrategias están disponibles
    - Instanciar estrategias by ID
    - Listar estrategias activas
    """

    def __init__(self):
        self._strategies: Dict[str, Type[Strategy]] = {}

    def register(self, strategy_class: Type[Strategy]) -> None:
        """
        Registra una clase de estrategia.

        Args:
            strategy_class: Clase que hereda de Strategy
        """
        # Support new META attribute style
        if hasattr(strategy_class, "META"):
            meta = strategy_class.META
        else:
            # Fallback to legacy metadata() method
            try:
                temp_instance = strategy_class()
                meta = temp_instance.metadata()
            except Exception as e:
                print(f" [WARN] Failed to register {strategy_class}: {e}")
                return

        if meta.id in self._strategies:
            print(f" [WARN] Warning: Overwriting strategy '{meta.id}'")

        self._strategies[meta.id] = strategy_class
        print(f" [REG] Registered strategy: {meta.id} - {meta.name}")

    def get(
        self, strategy_id: str, config: Optional[dict] = None
    ) -> Optional[Strategy]:
        """
        Obtiene una instancia de estrategia por ID.

        Args:
            strategy_id: ID de la estrategia
            config: Configuración opcional

        Returns:
            Instancia de la estrategia o None si no existe
        """
        strategy_class = self._strategies.get(strategy_id)
        if not strategy_class:
            return None

        # Instanciar con config si aplica
        try:
            if config:
                return strategy_class(config=config)
            else:
                return strategy_class()
        except TypeError:
            # La estrategia no acepta config
            return strategy_class()

    def list_all(self) -> List[StrategyMetadata]:
        """
        Lista metadatos de todas las estrategias registradas.

        Returns:
            Lista de StrategyMetadata
        """
        metadatas = []
        for strategy_class in self._strategies.values():
            instance = strategy_class()
            metadatas.append(instance.metadata())
        return metadatas

    def list_enabled(self) -> List[StrategyMetadata]:
        """
        Lista solo estrategias habilitadas.

        Returns:
            Lista de StrategyMetadata de estrategias enabled=True
        """
        return [m for m in self.list_all() if m.enabled]


def load_default_strategies():
    """
    Carga EXCLUSIVAMENTE las estrategias Swing-PvP certificadas.
    Cualquier otra estrategia es rechazada.
    """
    print("[REGISTRY] Loading Certified Swing Strategies...")
    
    # 1. Official Strategy Whitelist
    from .DonchianBreakoutV2 import DonchianBreakoutV2
    from .TrendFollowingNative import TrendFollowingNative
    from .MeanReversionBollinger import MeanReversionBollinger

    r = get_registry()
    
    # 2. Strict Registration (Clean Slate)
    r._strategies.clear()
    
    r.register(DonchianBreakoutV2)
    r.register(TrendFollowingNative)
    r.register(MeanReversionBollinger)
    
    # 3. Canonical Aliases (For DB backward compatibility only)
    if "donchian" not in r._strategies:
         r._strategies["donchian"] = DonchianBreakoutV2
         
    # Validate Whitelist
    allowed_ids = {"trend_following_native_v1", "donchian_v2", "donchian", "mean_reversion_v1"}
    current_ids = set(r._strategies.keys())
    
    diff = current_ids - allowed_ids
    if diff:
        print(f"❌ [SECURITY] Unauthorized strategies detected: {diff}")
        # Sanitize
        for illegal in diff:
            del r._strategies[illegal]
            
    print(f"[REGISTRY] Sealed with {len(r._strategies)} strategies.")
    
    # Error handling removed as it was wrapping the old block.
    # New block handles its own logic.



# Instancia global del registry
registry = StrategyRegistry()


def get_registry() -> StrategyRegistry:
    """Helper para obtener el registry global."""
    return registry
