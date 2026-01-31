from core.market_data_api import get_ohlcv_data as get_ohlcv_real
from core.market_data_api import get_current_price as get_price_real
from core.market_data_api import get_market_summary as get_summary_real

# Shim for legacy strategies expecting "get_ohlcv"
def get_ohlcv(symbol: str, timeframe: str = "30m", limit: int = 100):
   return get_ohlcv_real(symbol, timeframe, limit)

def get_current_price(symbol: str):
   return get_price_real(symbol)

def get_market_summary(symbols):
   return get_summary_real(symbols)
