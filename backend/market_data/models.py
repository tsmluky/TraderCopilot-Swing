from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel


# Timeframes soportados para OHLCV
Timeframe = Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d"]


class PriceSnapshot(BaseModel):
    """
    Snapshot simple de mercado:
    - último precio
    - cambio 24h
    - volumen 24h
    """

    token: str
    symbol: str
    exchange: str
    price: float
    change_24h: Optional[float] = None  # porcentaje
    volume_24h: Optional[float] = None  # volumen base
    ts: datetime


class Candle(BaseModel):
    """
    Una vela OHLCV estándar.
    """

    ts: datetime
    o: float
    h: float
    l: float  # noqa: E741
    c: float
    v: float


class OHLCVSlice(BaseModel):
    """
    Conjunto de velas para un token/timeframe concreto.
    """

    token: str
    symbol: str
    exchange: str
    timeframe: Timeframe
    candles: List[Candle]
