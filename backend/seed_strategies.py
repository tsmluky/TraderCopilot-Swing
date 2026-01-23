from database import SessionLocal
from models_db import StrategyConfig
from strategies.registry import get_registry
from strategies.ma_cross import MACrossStrategy
from strategies.DonchianBreakoutV2 import DonchianBreakoutV2 as DonchianStrategy
from strategies.bb_mean_reversion import BBMeanReversionStrategy
from strategies.DonchianBreakoutV2 import DonchianBreakoutV2
from strategies.rsi_divergence import RSIDivergenceStrategy
import json
import sys


def seed_strategies():
    db = SessionLocal()
    registry = get_registry()

    # Registrar clases
    registry.register(MACrossStrategy)
    registry.register(DonchianStrategy)
    registry.register(BBMeanReversionStrategy)
    registry.register(DonchianBreakoutV2)
    registry.register(RSIDivergenceStrategy)

    print("🌱 Seeding Optimized Strategies...")

    try:
        # 1. Deshabilitar TODAS las estrategias primero
        print("  - Disabling all strategies...")
        db.query(StrategyConfig).update(
            {StrategyConfig.enabled: 0}
        )  # Use 0 instead of False
        db.commit()

        # 2. Configurar las ganadoras
        strategies_config = [
            # (Strategy Class, Timeframes)
            (DonchianBreakoutV2(), ["4h"]),
            (BBMeanReversionStrategy(), ["1h", "15m"]),
            (RSIDivergenceStrategy(), ["1h"]),  # NUEVA ESTRATEGIA ACTIVADA
        ]

        for strategy, timeframes in strategies_config:
            meta = strategy.metadata()

            # Buscar si ya existe
            existing = (
                db.query(StrategyConfig)
                .filter(StrategyConfig.strategy_id == meta.id)
                .first()
            )

            if existing:
                print(f"  - Enabling {meta.name} ({meta.id})")
                existing.name = meta.name
                existing.config_json = json.dumps(meta.config)
                existing.tokens = json.dumps(["ETH", "BTC", "SOL"])
                existing.timeframes = json.dumps(timeframes)
                existing.enabled = 1  # Use 1 instead of True
                existing.interval_seconds = 60
                db.add(existing)  # Explicit add to session
            else:
                print(f"  - Creating {meta.name} ({meta.id})")
                new_config = StrategyConfig(
                    strategy_id=meta.id,
                    name=meta.name,
                    config_json=json.dumps(meta.config),
                    tokens=json.dumps(["ETH", "BTC", "SOL"]),
                    timeframes=json.dumps(timeframes),
                    enabled=1,  # Use 1 instead of True
                    interval_seconds=60,
                    last_execution=None,
                )
                db.add(new_config)

            # Commit after each strategy to avoid transaction issues
            db.commit()

        print("✅ Strategies seeded successfully!")

        # Mostrar resumen final
        active = (
            db.query(StrategyConfig).filter(StrategyConfig.enabled == 1).all()
        )  # Use 1 instead of True
        print(f"\n🚀 Active Strategies ({len(active)}):")
        for s in active:
            tfs = json.loads(s.timeframes)
            print(f"  - {s.name}: {', '.join(tfs)}")

    except Exception as e:
        print(f"❌ Error seeding strategies: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_strategies()
