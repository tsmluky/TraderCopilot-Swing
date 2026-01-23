# backend/setup_strategies.py
"""
Script de setup inicial para registrar estrategias.

Ejecutar una vez para:
1. Registrar estrategias en el registry
2. Crear configuraciones iniciales en la DB
"""

import sys
from pathlib import Path

# Setup path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from strategies.registry import get_registry  # noqa: E402
from strategies.DonchianBreakoutV2 import DonchianBreakoutV2  # noqa: E402
from strategies.supertrend_flow import SuperTrendFlowStrategy  # noqa: E402
from strategies.TrendFollowingNative import TrendFollowingNative  # noqa: E402
from database import SessionLocal  # noqa: E402
from models_db import StrategyConfig  # noqa: E402
import json  # noqa: E402


def register_built_in_strategies():
    """Registra estrategias built-in en el registry."""
    print("\n📦 Registering built-in strategies...")

    registry = get_registry()

    # 1. Donchian V2
    registry.register(DonchianBreakoutV2)

    # 2. SuperTrend Flow (Experimental)
    registry.register(SuperTrendFlowStrategy)

    # 3. Trend Following Native
    registry.register(TrendFollowingNative)

    print("✅ Built-in strategies registered")


def setup_db_configs():
    """
    Crea configuraciones iniciales en la DB para estrategias.
    """
    print("\n💾 Setting up DB configurations...")

    db = SessionLocal()

    try:
        # [REMOVED] RSI MACD Config

        # Configuración para DonchianBreakoutV2
        existing_donchian = (
            db.query(StrategyConfig)
            .filter(StrategyConfig.strategy_id == "donchian_v2")
            .first()
        )

        if not existing_donchian:
            config_donchian = StrategyConfig(
                strategy_id="donchian_v2",
                name="Donchian Breakout V2",
                description="Trend following breakout strategy with Volatility (ATR) and Trend (EMA200) filters.",
                version="2.0.0",
                enabled=1,
                interval_seconds=60,
                tokens=json.dumps(["ETH", "BTC", "SOL"]),
                timeframes=json.dumps(["4h"]),
                risk_profile="medium-high",
                mode="PRO",
                source_type="ENGINE",
                config_json=json.dumps(
                    {
                        "period": 20,
                        "atr_period": 14,
                        "atr_ma_period": 20,
                        "ema_trend_period": 200,
                    }
                ),
            )
            db.add(config_donchian)
            db.commit()
            print("  ✅ Created config for: donchian_v2")

        # Configuración para SuperTrend
        existing_st = (
            db.query(StrategyConfig)
            .filter(StrategyConfig.strategy_id == "supertrend_flow_v1")
            .first()
        )

        if not existing_st:
            config_st = StrategyConfig(
                strategy_id="supertrend_flow_v1",
                name="SuperTrend Flow",
                description="Seguimiento de tendencia puro con SuperTrend indicator.",
                version="1.0.0",
                enabled=1,
                interval_seconds=300,
                tokens=json.dumps(["SOL", "AVAX"]),
                timeframes=json.dumps(["4h"]),
                risk_profile="medium",
                mode="CUSTOM",
                source_type="ENGINE",
                config_json=json.dumps(
                    {
                        "atr_period": 10,
                        "atr_multiplier": 3.0,
                        "tp_atr_mult": 3.0,
                        "sl_atr_mult": 1.5,
                    }
                ),
            )
            db.add(config_st)
            db.commit()
            print("  ✅ Created config for: supertrend_flow_v1")

        # [REMOVED] VWAP Config

    except Exception as e:
        print(f"  ❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    print("=" * 60)
    print("⚙️  TraderCopilot - Strategy Setup")
    print("=" * 60)

    # 1. Registrar estrategias en registry
    register_built_in_strategies()

    # 2. Crear configs en DB
    setup_db_configs()

    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Start backend: python main.py")
    print("  2. Check strategies: curl http://localhost:8000/strategies/")
    print("  3. Start scheduler: python scheduler.py")
    print("\n💡 Tip: Activate strategies via PATCH /strategies/{id}")
    print("=" * 60)


if __name__ == "__main__":
    main()
