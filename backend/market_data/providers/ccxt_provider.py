from __future__ import annotations
import ccxt
from datetime import datetime, timezone
from typing import List
from ..models import PriceSnapshot, OHLCVSlice, Candle, Timeframe

# Puedes parametrizar esto desde .env si quieres
_EXCHANGE_ID = "binance"  # Changed from mexc to binance for better stability

# Mapa simple token -> símbolo
_SYMBOLS = {
    "eth": "ETH/USDT",
    "btc": "BTC/USDT",
    "sol": "SOL/USDT",
    "xau": "XAU/USDT",
    "bnb": "BNB/USDT",
    "xrp": "XRP/USDT",
}


def _get_exchange():
    cls = getattr(ccxt, _EXCHANGE_ID)
    # Aquí puedes meter tus apiKey/secret si más adelante firmas peticiones privadas
    return cls({"enableRateLimit": True})


def _get_symbol(token: str) -> str:
    key = token.lower()
    if key not in _SYMBOLS:
        raise ValueError(f"Token no soportado en market_data: {token}")
    return _SYMBOLS[key]


def fetch_price_snapshot(token: str) -> PriceSnapshot:
    exchange = _get_exchange()
    symbol = _get_symbol(token)
    ticker = exchange.fetch_ticker(symbol)

    last = float(ticker["last"])
    # Algunos exchanges dan "percentage", otros "change", revisa el dict:
    change_24h = (
        float(ticker.get("percentage"))
        if ticker.get("percentage") is not None
        else None
    )
    volume_24h = (
        float(ticker.get("baseVolume"))
        if ticker.get("baseVolume") is not None
        else None
    )

    ts_ms = ticker.get("timestamp")
    ts = (
        datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        if ts_ms
        else datetime.now(timezone.utc)
    )

    return PriceSnapshot(
        token=token.lower(),
        symbol=symbol,
        exchange=_EXCHANGE_ID,
        price=last,
        change_24h=change_24h,
        volume_24h=volume_24h,
        ts=ts,
    )


def fetch_ohlcv_slice(token: str, timeframe: Timeframe, limit: int = 200) -> OHLCVSlice:
    exchange = _get_exchange()
    symbol = _get_symbol(token)
    
    # Normalize timeframe to lowercase (Binance strictness: 1h, 4h, not 4H)
    # Ensure it's a string first
    timeframe_str = str(timeframe).lower()
    
    print(f"[DEBUG_MARKET] Fetching {symbol} {timeframe_str} limit={limit}")
    raw = exchange.fetch_ohlcv(symbol, timeframe=timeframe_str, limit=limit)

    candles: List[Candle] = []
    for ts_ms, o, h, l, c, v in raw:  # noqa: E741
        candles.append(
            Candle(
                ts=datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc),
                o=float(o),
                h=float(h),
                l=float(l),
                c=float(c),
                v=float(v),
            )
        )

    return OHLCVSlice(
        token=token.lower(),
        symbol=symbol,
        exchange=_EXCHANGE_ID,
        timeframe=timeframe_str,
        candles=candles,
    )
