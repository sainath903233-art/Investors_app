# backend/stocks.py
# Fetches market data with yfinance + caches it + auto-refreshes every 2 minutes

import yfinance as yf
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# ── In-memory cache (a simple global object, like a JS module-level variable) ──
_cache = {"indices": {}, "stocks": {}, "last_updated": None}

# ── Market indices to track ───────────────────────────────────────
INDICES = {
    "Nifty 50": "^NSEI",
    "Sensex":   "^BSESN",
    "S&P 500":  "^GSPC",
    "Nasdaq":   "^IXIC",
}

# ── Default stocks to pre-load in cache ──────────────────────────
DEFAULT_STOCKS = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "WIPRO", "SBIN", "BAJFINANCE", "TATAMOTORS", "ADANIENT",
    "HINDUNILVR", "KOTAKBANK", "AXISBANK", "LTIM", "SUNPHARMA",
]


def fetch_indices() -> dict:
    result = {}
    for name, symbol in INDICES.items():
        try:
            info  = yf.Ticker(symbol).fast_info
            price = round(float(info.last_price), 2)
            prev  = float(info.previous_close)
            change = round((price - prev) / prev * 100, 2) if prev else 0
            result[name] = {"price": price, "change_pct": change, "symbol": symbol}
        except Exception as e:
            print(f"[stocks] Could not fetch index {symbol}: {e}")
            result[name] = {"price": None, "change_pct": 0, "symbol": symbol}
    return result


def fetch_stock(symbol: str):
    """Fetch 90 days of prices + fundamentals for one NSE stock."""
    yf_symbol = symbol if symbol.startswith("^") else f"{symbol}.NS"
    try:
        ticker = yf.Ticker(yf_symbol)
        hist   = ticker.history(period="90d", interval="1d")
        if hist.empty:
            print(f"[stocks] No history for {yf_symbol}")
            return None

        history = []
        for date, row in hist.iterrows():
            history.append({
                "date":   date.strftime("%Y-%m-%d"),
                "open":   round(float(row["Open"]),  2),
                "high":   round(float(row["High"]),  2),
                "low":    round(float(row["Low"]),   2),
                "close":  round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            })

        last_close = history[-1]["close"] if history else None
        prev_close = history[-2]["close"] if len(history) > 1 else last_close
        change_pct = round((last_close - prev_close) / prev_close * 100, 2) if prev_close else 0

        info = ticker.info
        return {
            "symbol":        symbol,
            "name":          info.get("longName") or info.get("shortName") or symbol,
            "sector":        info.get("sector") or "default",
            "current_price": last_close,
            "change_pct":    change_pct,
            "direction":     "up" if change_pct >= 0 else "down",
            "history":       history,
            "fundamentals": {
                "pe_ratio":   info.get("trailingPE"),
                "pb_ratio":   info.get("priceToBook"),
                "peg_ratio":  info.get("pegRatio"),
                "roe":        info.get("returnOnEquity"),
                "roic":       info.get("returnOnAssets"),
                "net_margin": info.get("profitMargins"),
                "market_cap": info.get("marketCap"),
                "52w_high":   info.get("fiftyTwoWeekHigh"),
                "52w_low":    info.get("fiftyTwoWeekLow"),
                "avg_volume": info.get("averageVolume"),
                "beta":       info.get("beta"),
            },
        }
    except Exception as e:
        print(f"[stocks] Error fetching {yf_symbol}: {e}")
        return None


def get_cached_indices() -> dict:
    return _cache["indices"]

def get_stock_data(symbol: str):
    symbol = symbol.upper()
    if symbol in _cache["stocks"]:
        return _cache["stocks"][symbol]
    data = fetch_stock(symbol)
    if data:
        _cache["stocks"][symbol] = data
    return data


def refresh_all_data():
    print(f"[scheduler] Refreshing market data at {datetime.now().strftime('%H:%M:%S')}")
    _cache["indices"] = fetch_indices()
    for symbol in list(_cache["stocks"].keys()) + DEFAULT_STOCKS:
        data = fetch_stock(symbol)
        if data:
            _cache["stocks"][symbol.upper()] = data
    _cache["last_updated"] = datetime.now().isoformat()


def start_scheduler():
    refresh_all_data()   # run once at startup
    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_all_data, "interval", minutes=2)
    scheduler.start()
    print("[scheduler] Background refresh started — every 2 minutes")
