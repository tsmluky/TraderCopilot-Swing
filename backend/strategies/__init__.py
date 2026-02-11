from .DonchianBreakoutV2 import DonchianBreakoutV2
from .MeanReversionBollinger import MeanReversionBollinger
from .MeanReversionRSI import MeanReversionRSI
from .TrendFollowingNative import TrendFollowingNative
from .SuperTrend import SuperTrendStrategy

# Registry for dynamic loading
ALL_STRATEGIES = [
    DonchianBreakoutV2,
    TrendFollowingNative,
    MeanReversionBollinger,
    SuperTrendStrategy
]
