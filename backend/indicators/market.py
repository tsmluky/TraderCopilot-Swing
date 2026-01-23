import pandas as pd
import ta

# Importar desde el módulo core
from core.market_data_api import get_ohlcv_data

# Exchange ID for data source (used by evaluator)
EXCHANGE_ID = "binance"


def get_market_data(symbol: str, timeframe: str = "1h", limit: int = 1000):
    """
    Descarga OHLCV y calcula indicadores técnicos base.
    Retorna: (dataframe, dict_resumen_actual)
    """
    try:
        # Usar la API robusta con fallback
        import inspect
        from core import market_data_api

        print(
            f"[DEBUG MARKET] Signature: {inspect.signature(market_data_api.get_ohlcv_data)}"
        )

        ohlcv_data, source_id = get_ohlcv_data(
            symbol, timeframe, limit, return_source=True
        )

        if not ohlcv_data:
            return None, None

        # Convertir lista de dicts a DataFrame
        # market_data_api devuelve: {'timestamp': ms, 'open': float, ...}
        df = pd.DataFrame(ohlcv_data)

        # Asegurar columnas correctas y tipos
        required_cols = ["timestamp", "open", "high", "low", "close", "volume"]
        for col in required_cols:
            if col not in df.columns:
                print(f"[MARKET ERROR] Missing column {col} in data")
                return None, None

        # Convertir timestamp si es necesario (ya viene como int ms, pandas lo maneja mejor como datetime)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.sort_values("timestamp", inplace=True)

        # Cálculo de Indicadores (Quant Layer) usando librería 'ta'
        # EMA
        df["EMA_21"] = ta.trend.ema_indicator(df["close"], window=21)
        df["EMA_50"] = ta.trend.ema_indicator(df["close"], window=50)

        # RSI
        df["RSI_14"] = ta.momentum.rsi(df["close"], window=14)

        # MACD
        macd = ta.trend.MACD(df["close"])
        df["MACD_12_26_9"] = macd.macd()
        df["MACDh_12_26_9"] = macd.macd_diff()

        # ATR
        df["ATRr_14"] = ta.volatility.average_true_range(
            df["high"], df["low"], df["close"], window=14
        )

        # Limpieza de NaNs generados por indicadores
        df.dropna(inplace=True)

        if df.empty:
            return None, None

        # Extraer última vela
        last = df.iloc[-1]
        # prev = df.iloc[-2] # Puede fallar si solo hay 1 fila tras dropna

        # Mapeo de datos
        data = {
            "price": last["close"],
            "rsi": round(last["RSI_14"], 2),
            "ema21": last["EMA_21"],
            "ema50": last["EMA_50"],
            "macd": last["MACD_12_26_9"],
            "macd_hist": last["MACDh_12_26_9"],
            "atr": last["ATRr_14"],
            # "volume_change_pct": ... (opcional, simplificado para robustez)
            "trend": "BULLISH" if last["close"] > last["EMA_50"] else "BEARISH",
            "source_exchange": source_id,
        }

        return df, data

    except Exception as e:
        print(f"[ERROR MARKET] {e}")
        import traceback

        traceback.print_exc()
        return None, None
