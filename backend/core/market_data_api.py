# backend/market_data_api.py
"""
Módulo para obtener datos de mercado en tiempo real.
Refactorizado para usar CCXT (Binance) para consistencia con Trading Lab.
"""

import ccxt
import time
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
from core.cache import cache  # Importar Cache

print("[DEBUG] LOADING MARKET_DATA_API (Scale-Ready Fix)")


import concurrent.futures

def get_ohlcv_data(
    symbol: str, timeframe: str = "30m", limit: int = 100, return_source: bool = False
) -> Union[List[Dict[str, Any]], Tuple[List[Dict[str, Any]], str]]:
    """
    Obtiene datos OHLCV con Caching + Parallel Race.
    TTL: 60s para reducir latencia.
    """
    timeframe = timeframe.lower() # CCXT expects lowercase
    # 1. Intentar Cache
    cache_key = f"ohlcv:{symbol.upper()}:{timeframe}:{limit}"
    cached_data = cache.get(cache_key)
    if cached_data:
        # print(f"[MARKET] ⚡ Cache Hit for {cache_key}")
        if return_source:
            return cached_data, "cache"
        return cached_data

    # ... execution continues ...

    base_symbol = symbol.upper().replace("USDT", "").replace("-", "")
    ccxt_symbol = f"{base_symbol}/USDT"

    # [HARDENING] Symbol Migration Handling (e.g., MATIC -> POL)
    aliases = {
        "MATIC": "POL",
        "RUNE": "RUNE", # Sometimes exchanges differ
    }
    
    # Priority Exchanges (Concurrent Race)
    exchanges_config = [
        {"id": "binance", "class": ccxt.binance, "timeout": 8000},
        {"id": "kraken", "class": ccxt.kraken, "timeout": 8000},
        {"id": "kucoin", "class": ccxt.kucoin, "timeout": 8000},
        {"id": "bybit", "class": ccxt.bybit, "timeout": 8000},
    ]

    def _fetch_worker(cfg):
        ex_id = cfg["id"]
        try:
            exchange = cfg["class"]({"enableRateLimit": True, "timeout": cfg["timeout"]})
            # Try Primary
            try:
                data = exchange.fetch_ohlcv(ccxt_symbol, timeframe, limit=limit)
                return data, ex_id
            except Exception as e:
                # Try Alias
                alias = aliases.get(base_symbol)
                if alias:
                    alias_sym = f"{alias}/USDT"
                    # print(f"[{ex_id}] Trying alias {alias_sym}...")
                    data = exchange.fetch_ohlcv(alias_sym, timeframe, limit=limit)
                    return data, ex_id
                raise e
        except Exception as e:
            # print(f"[{ex_id}] Failed: {e}")
            raise e
        finally:
             if 'exchange' in locals():
                 exchange.close()

    # 2. Parallel Race
    str_start = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_map = {executor.submit(_fetch_worker, cfg): cfg["id"] for cfg in exchanges_config}
        
        try:
            for future in concurrent.futures.as_completed(future_map, timeout=12): # Max global wait
                ex_id = future_map[future]
                try:
                    data, source_id = future.result()
                    if data and len(data) > 0:
                        print(f"[MARKET DATA] 🚀 Race Won by {source_id} in {time.time()-str_start:.2f}s")
                        
                        # Format
                        ohlcv = []
                        for candle in data:
                            ts = candle[0]
                            dt = datetime.fromtimestamp(ts / 1000)
                            ohlcv.append({
                                "timestamp": ts,
                                "time": dt.strftime("%Y-%m-%d %H:%M"),
                                "open": float(candle[1]),
                                "high": float(candle[2]),
                                "low": float(candle[3]),
                                "close": float(candle[4]),
                                "volume": float(candle[5]),
                            })
                        
                        # Cache Success
                        cache.set(cache_key, ohlcv, ttl=60) # Increased TTL 60s
                        
                        if return_source:
                            return ohlcv, source_id
                        return ohlcv
                        
                except Exception:
                    continue # Try next finished future
        except Exception as e:
            print(f"[MARKET DATA] Race Error: {e}")

    # 3. Last Resort
    print("[MARKET DATA] 🚨 All exchanges failed. Returning EMPTY.")
    if return_source:
        return [], "none"
    return []


def generate_mock_ohlcv(symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Generates synthetic OHLCV data for testing/fallback."""
    import random

    base_price = 50000.0 if "BTC" in symbol else 3000.0
    if "SOL" in symbol:
        base_price = 150.0

    data = []
    current_time = int(time.time() * 1000)
    # 1 hour intervals in ms
    interval_ms = 3600 * 1000

    for i in range(limit):
        ts = current_time - ((limit - i) * interval_ms)
        dt = datetime.fromtimestamp(ts / 1000)

        # Random walk
        change = random.uniform(-0.02, 0.02)
        close = base_price * (1 + change)
        open_p = base_price
        high = max(open_p, close) * 1.01
        low = min(open_p, close) * 0.99

        data.append(
            {
                "timestamp": ts,
                "time": dt.strftime("%Y-%m-%d %H:%M"),
                "open": round(open_p, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close, 2),
                "volume": round(random.uniform(100, 1000), 2),
            }
        )
        base_price = close

    return data


def get_market_summary(symbols: List[str]) -> List[Dict[str, Any]]:
    """
    Obtiene precio y cambio 24h para múltiples símbolos.
    """
    # 1. Cache Check (Strict)
    s_key = "-".join(sorted(symbols))
    cache_key = f"market:summary:{hash(s_key)}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    # 2. Try Fetch with Fallbacks
    exchanges_config = [
        {"id": "binance", "class": ccxt.binance},
        {"id": "kucoin", "class": ccxt.kucoin},
        {"id": "bybit", "class": ccxt.bybit},
        {"id": "kraken", "class": ccxt.kraken}, # Kraken often reliable in US/EU
    ]

    unique_syms = list(set([s.upper().replace("USDT", "").replace("-", "") for s in symbols]))
    # Pairs format might differ slightly per exchange, but "BTC/USDT" is fairly standard. 
    # Some exchanges need specific handling if strictly needed, but CCXT handles most "/"
    pairs = [f"{s}/USDT" for s in unique_syms]

    for cfg in exchanges_config:
        ex_id = cfg["id"]
        try:
            exchange = cfg["class"]({
                "enableRateLimit": True,
                "timeout": 4000
            })
            
            # Special handling for Kraken pairs if needed (often XBT/USD or similar), 
            # but let's stick to standard USDT pairs for crypto-to-crypto exchanges.
            # If Kraken fails on USDT pairs, loop continues.
            
            tickers = exchange.fetch_tickers(pairs)
            
            summary = []
            for p in pairs:
                t = tickers.get(p)
                # Some exchanges return different keys, but CCXT standardizes most.
                if t:
                    change = t.get("percentage")
                    if change is None and t.get("open") and t["open"] > 0:
                        change = ((t["last"] - t["open"]) / t["open"]) * 100
                    
                    summary.append({
                        "symbol": p.replace("/USDT", ""),
                        "price": t["last"],
                        "change_24h": change or 0.0
                    })
            
            if summary:
                # 3. Set Cache: 15s TTL
                cache.set(cache_key, summary, ttl=15)
                # print(f"[MARKET] Got summary from {ex_id}")
                return summary

        except Exception as e:
            print(f"[MARKET] Failed to fetch summary from {ex_id}: {e}")
            continue

    return []


def get_current_price(symbol: str) -> Optional[float]:
    """
    Obtiene el precio actual de un símbolo.
    """
    try:
        data = get_ohlcv_data(symbol, limit=1)
        if data:
            return data[-1]["close"]
    except Exception:
        pass
    return None
