# backend/strategies/__init__.py
"""
Strategy Base Module for TraderCopilot Signal Hub.
"""

from .base import Strategy, StrategyMetadata

# Import Strategy Implementations
from .DonchianBreakoutV2 import DonchianBreakoutV2
from .TrendFollowingNative import TrendFollowingNative


__all__ = [
    "Strategy",
    "StrategyMetadata",
    "DonchianBreakoutV2",
    "TrendFollowingNative",
]
