# backend/stocks.py
# Fetches market data with yfinance + caches it + auto-refreshes every 2 minutes

import yfinance as yf
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import math


# ─────────────────────────────────────────────────────────────
# In-memory cache
# ─────────────────────────────────────────────────────────────

_cache = {
    "indices": {},
    "stocks": {},
    "last_updated": None,
}


# ─────────────────────────────────────────────────────────────
# Market indices to track
# ─────────────────────────────────────────────────────────────

INDICES = {
    "NIFTY50": "^NSEI",
    "SENSEX": "^BSESN",
    "SP500": "^GSPC",
    "NASDAQ": "^IXIC",
}


# ─────────────────────────────────────────────────────────────
# Default stocks to pre-load
# Removed symbols that are currently returning no data
# ─────────────────────────────────────────────────────────────

DEFAULT_STOCKS = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
    "WIPRO",
    "SBIN",
    "BAJFINANCE",
    "ADANIENT",
    "HINDUNILVR",
    "KOTAKBANK",
    "AXISBANK",
    "SUNPHARMA",
]


# ─────────────────────────────────────────────────────────────
# Fetch market indices
# ─────────────────────────────────────────────────────────────
def fetch_indices() -> dict:
    result = {}

    for name, symbol in INDICES.items():
        try:
            ticker = yf.Ticker(symbol)

            hist = ticker.history(
                period="5d",
                interval="1d"
            )

            if hist.empty or len(hist) < 2:
                raise ValueError("No sufficient index price data")

            current_price = float(hist["Close"].iloc[-1])
            previous_price = float(hist["Close"].iloc[-2])

            change_pct = (
                ((current_price - previous_price) / previous_price) * 100
                if previous_price
                else 0
            )

            result[name] = {
                "price": round(current_price, 2),
                "change_pct": round(change_pct, 2),
                "direction": "up" if change_pct >= 0 else "down",
                "symbol": symbol,
            }

        except Exception as e:
            print(f"[stocks] Could not fetch index {symbol}: {e}")

            result[name] = {
                "price": None,
                "change_pct": 0,
                "direction": "neutral",
                "symbol": symbol,
            }

    return result
# def fetch_indices() -> dict:
#     result = {}

#     for name, symbol in INDICES.items():
#         try:
#             ticker = yf.Ticker(symbol)

#             hist = ticker.history(
#                 period="5d",
#                 interval="1d"
#             )

#             if hist.empty or len(hist) < 2:
#                 raise ValueError("No sufficient index price data")

#             current_price = float(hist["Close"].iloc[-1])
#             previous_price = float(hist["Close"].iloc[-2])

#             change_pct = (
#                 ((current_price - previous_price) / previous_price) * 100
#                 if previous_price
#                 else 0
#             )

#             result[name] = {
#                 "price": round(current_price, 2),
#                 "change_pct": round(change_pct, 2),
#                 "symbol": symbol,
#             }

#         except Exception as e:
#             print(f"[stocks] Could not fetch index {symbol}: {e}")

#             result[name] = {
#                 "price": None,
#                 "change_pct": 0,
#                 "symbol": symbol,
#             }

#     return result


# ─────────────────────────────────────────────────────────────
# Fetch one stock
#
# period:
#     "90d" → normal dashboard
#     "2y"  → backtesting
# ─────────────────────────────────────────────────────────────

def fetch_stock(symbol: str, period: str = "90d"):
    yf_symbol = (
        symbol
        if symbol.startswith("^")
        else f"{symbol}.NS"
    )

    try:
        ticker = yf.Ticker(yf_symbol)

        hist = ticker.history(
            period=period,
            interval="1d"
        )

        if hist.empty:
            print(
                f"[stocks] No history for {yf_symbol}"
            )
            return None

        history = []

        # ---------------------------------------------
        # Clean historical price data
        # ---------------------------------------------
        for date, row in hist.iterrows():

            open_price = float(row["Open"])
            high_price = float(row["High"])
            low_price = float(row["Low"])
            close_price = float(row["Close"])
            volume_value = float(row["Volume"])

            # Skip invalid price rows
            if any(
                math.isnan(value) or math.isinf(value)
                for value in [
                    open_price,
                    high_price,
                    low_price,
                    close_price
                ]
            ):
                continue

            # Handle invalid volume
            if (
                math.isnan(volume_value)
                or math.isinf(volume_value)
            ):
                volume_value = 0

            history.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2),
                    "volume": int(volume_value),
                }
            )

        # ---------------------------------------------
        # Make sure valid history exists
        # ---------------------------------------------
        if not history:
            print(
                f"[stocks] No valid price history for {yf_symbol}"
            )
            return None

        # ---------------------------------------------
        # Current and previous closing prices
        # ---------------------------------------------
        last_close = history[-1]["close"]

        if len(history) > 1:
            prev_close = history[-2]["close"]
        else:
            prev_close = last_close

        # ---------------------------------------------
        # Daily percentage change
        # ---------------------------------------------
        if prev_close:
            change_pct = round(
                (last_close - prev_close)
                / prev_close
                * 100,
                2
            )
        else:
            change_pct = 0.0

        # ---------------------------------------------
        # Fundamental data
        # ---------------------------------------------
        info = ticker.info

        return {
            "symbol": symbol,

            "name": (
                info.get("longName")
                or info.get("shortName")
                or symbol
            ),

            "sector": (
                info.get("sector")
                or "default"
            ),

            "current_price": last_close,

            "change_pct": change_pct,

            "direction": (
                "up"
                if change_pct >= 0
                else "down"
            ),

            "history": history,

            "fundamentals": {
                "pe_ratio": info.get(
                    "trailingPE"
                ),

                "pb_ratio": info.get(
                    "priceToBook"
                ),

                "peg_ratio": info.get(
                    "pegRatio"
                ),

                "roe": info.get(
                    "returnOnEquity"
                ),

                "roic": info.get(
                    "returnOnInvestedCapital"
                ),

                "net_margin": info.get(
                    "profitMargins"
                ),

                "market_cap": info.get(
                    "marketCap"
                ),

                "52w_high": info.get(
                    "fiftyTwoWeekHigh"
                ),

                "52w_low": info.get(
                    "fiftyTwoWeekLow"
                ),

                "avg_volume": info.get(
                    "averageVolume"
                ),

                "beta": info.get(
                    "beta"
                ),
            },
        }

    except Exception as e:
        print(
            f"[stocks] Error fetching {yf_symbol}: {e}"
        )
        return None

# ─────────────────────────────────────────────────────────────
# Scheduler
# Automatically refreshes market data every 2 minutes
# ─────────────────────────────────────────────────────────────

_scheduler = None


def refresh_market_data():
    """Refresh cached market index data."""
    try:
        _cache["indices"] = fetch_indices()
        _cache["last_updated"] = datetime.now()

        print("[stocks] Market data refreshed.")

    except Exception as e:
        print(f"[stocks] Market refresh failed: {e}")


def start_scheduler():
    """Start the background market-data scheduler."""

    global _scheduler

    # Prevent starting multiple schedulers
    if _scheduler is not None:
        return

    # Fetch data once when the application starts
    refresh_market_data()

    _scheduler = BackgroundScheduler()

    _scheduler.add_job(
        refresh_market_data,
        "interval",
        minutes=2,
        id="market_data_refresh",
        replace_existing=True,
    )

    _scheduler.start()

    print("[stocks] Scheduler started.")


def get_cached_indices() -> dict:
    """Return the latest cached market index data."""

    # If cache is empty, fetch the data immediately
    if not _cache["indices"]:
        _cache["indices"] = fetch_indices()
        _cache["last_updated"] = datetime.now()

    return _cache["indices"]
