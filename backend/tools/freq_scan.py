import os
import sys

# Ensure backend/ is on sys.path when running from backend/tools
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.abspath(os.path.join(_THIS_DIR, ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

import pandas as pd  # noqa: E402

from strategies.DonchianBreakoutV2 import DonchianBreakoutV2  # noqa: E402
from strategies.TrendFollowingNative import TrendFollowingNative  # noqa: E402
from core.market_data_api import get_ohlcv_data  # noqa: E402


TOKENS = ["BTC", "ETH", "SOL", "BNB", "XRP"]
TF = "4h"
WINDOW = 120     # last N candles
LIMIT = 350      # fetch candles


def load_df(token: str, limit: int = LIMIT) -> pd.DataFrame:
    raw = get_ohlcv_data(token, TF, limit=limit)
    if not raw:
        return pd.DataFrame()
    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df


def count_signals(strategy, df: pd.DataFrame, token: str, window: int = WINDOW):
    if df.empty or len(df) < 50:
        return 0, None

    start = max(0, len(df) - window)
    c = 0
    last_sig = None

    # walk-forward: check if strategy would emit on each candle
    for i in range(start + 5, len(df) + 1):
        slice_df = df.iloc[:i].copy()
        out = strategy.analyze(slice_df, token, TF)
        if out:
            c += len(out)
            last_sig = out[-1]

    return c, last_sig


def fmt_sig(sig):
    if sig is None:
        return None
    return {
        "direction": sig.direction,
        "entry": float(sig.entry),
        "tp": float(sig.tp),
        "sl": float(sig.sl),
        "confidence": float(sig.confidence),
        "timeframe": sig.timeframe,
        "strategy_id": sig.strategy_id,
        "ts": str(sig.timestamp),
    }


def main():
    s1 = DonchianBreakoutV2()
    s2 = TrendFollowingNative()

    print(f"TF={TF} WINDOW={WINDOW} LIMIT={LIMIT}")
    for t in TOKENS:
        df = load_df(t, LIMIT)
        c1, last1 = count_signals(s1, df, t, WINDOW)
        c2, last2 = count_signals(s2, df, t, WINDOW)

        print(f"\n== {t} ==")
        print(f"Donchian: {c1} | last: {fmt_sig(last1)}")
        print(f"Trend   : {c2} | last: {fmt_sig(last2)}")


if __name__ == "__main__":
    main()
