# backend/analysis/technical.py
# Market Timing Study — Moving Averages, MACD, RSI, Bollinger Bands, Bias, Volume

import pandas as pd
import numpy as np

from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands


def _to_df(history: list) -> pd.DataFrame:
    df = pd.DataFrame(history)

    df["date"] = pd.to_datetime(df["date"])

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    return df.sort_values("date").reset_index(drop=True)


def _safe(val):
    if val is None:
        return None

    try:
        v = float(val)

        if np.isnan(v):
            return None

        return round(v, 4)

    except Exception:
        return None


def analyse_moving_averages(df: pd.DataFrame) -> dict:
    close = df["close"]

    ma20 = _safe(
        SMAIndicator(close, 20).sma_indicator().iloc[-1]
    )

    ma50 = (
        _safe(SMAIndicator(close, 50).sma_indicator().iloc[-1])
        if len(df) >= 50
        else None
    )

    ma200 = (
        _safe(SMAIndicator(close, 200).sma_indicator().iloc[-1])
        if len(df) >= 200
        else None
    )

    price = _safe(close.iloc[-1])

    score = 50
    notes = []

    # Price vs MA20
    if price is not None and ma20 is not None:
        if price > ma20:
            score += 10
            notes.append("Price above MA20")
        else:
            score -= 10
            notes.append("Price below MA20")

    # MA50 vs MA200
    if ma50 is not None and ma200 is not None:
        if ma50 > ma200:
            score += 15
            notes.append("Golden Cross — bullish")
        else:
            score -= 15
            notes.append("Death Cross — bearish")

    # Price vs MA50
    if price is not None and ma50 is not None:
        if price > ma50:
            score += 10
        else:
            score -= 10

    # Price vs MA200
    if price is not None and ma200 is not None:
        if price > ma200:
            score += 15
        else:
            score -= 15

    score = max(0, min(100, score))

    signal = (
        "BUY"
        if score >= 60
        else "SELL"
        if score <= 40
        else "NEUTRAL"
    )

    return {
        "signal": signal,
        "score": score,
        "notes": notes,
        "values": {
            "ma20": ma20,
            "ma50": ma50,
            "ma200": ma200,
        },
    }


def analyse_macd(df: pd.DataFrame) -> dict:
    m = MACD(df["close"])

    macd_line = _safe(m.macd().iloc[-1])
    signal_line = _safe(m.macd_signal().iloc[-1])
    histogram = _safe(m.macd_diff().iloc[-1])

    score = 50

    if macd_line is not None and signal_line is not None:
        if macd_line > signal_line:
            score = 72
        else:
            score = 28

    if histogram is not None:
        if histogram > 0:
            score = min(100, score + 8)
        else:
            score = max(0, score - 8)

    signal = (
        "BUY"
        if score >= 60
        else "SELL"
        if score <= 40
        else "NEUTRAL"
    )

    return {
        "signal": signal,
        "score": score,
        "values": {
            "macd": macd_line,
            "signal_line": signal_line,
            "histogram": histogram,
        },
    }


def analyse_rsi(df: pd.DataFrame) -> dict:
    rsi_val = _safe(
        RSIIndicator(df["close"], 14).rsi().iloc[-1]
    )

    if rsi_val is None:
        return {
            "signal": "NEUTRAL",
            "score": 50,
            "values": {
                "rsi": None
            },
        }

    if rsi_val >= 70:
        score, signal = 20, "SELL"

    elif rsi_val >= 60:
        score, signal = 45, "NEUTRAL"

    elif rsi_val >= 40:
        score, signal = 60, "NEUTRAL"

    elif rsi_val >= 30:
        score, signal = 75, "BUY"

    else:
        score, signal = 85, "BUY"

    return {
        "signal": signal,
        "score": score,
        "values": {
            "rsi": round(rsi_val, 1)
        },
    }


def analyse_bollinger_bands(df: pd.DataFrame) -> dict:
    bb = BollingerBands(
        df["close"],
        20,
        2
    )

    upper = _safe(
        bb.bollinger_hband().iloc[-1]
    )

    middle = _safe(
        bb.bollinger_mavg().iloc[-1]
    )

    lower = _safe(
        bb.bollinger_lband().iloc[-1]
    )

    price = _safe(
        df["close"].iloc[-1]
    )

    score = 50
    signal = "NEUTRAL"
    squeeze = False
    position_pct = None

    if (
        upper is not None
        and lower is not None
        and middle is not None
        and price is not None
    ):
        width = upper - lower

        if width > 0:
            position_pct = round(
                (price - lower) / width * 100,
                1
            )

            squeeze = (width / middle) < 0.05

            if price < lower:
                score = 78
                signal = "BUY"

            elif price > upper:
                score = 22
                signal = "SELL"

            elif position_pct < 30:
                score = 65
                signal = "BUY"

            elif position_pct > 70:
                score = 35
                signal = "SELL"

    return {
        "signal": signal,
        "score": score,
        "values": {
            "upper": upper,
            "middle": middle,
            "lower": lower,
            "position_pct": position_pct,
            "squeeze": squeeze,
        },
    }


def analyse_bias(df: pd.DataFrame) -> dict:
    close = df["close"]

    ma20 = SMAIndicator(
        close,
        20
    ).sma_indicator()

    bias = _safe(
        ((close - ma20) / ma20 * 100).iloc[-1]
    )

    if bias is None:
        return {
            "signal": "NEUTRAL",
            "score": 50,
            "values": {
                "bias": None
            },
        }

    if bias < -5:
        score, signal = 72, "BUY"

    elif bias < -2:
        score, signal = 60, "BUY"

    elif bias > 5:
        score, signal = 28, "SELL"

    elif bias > 2:
        score, signal = 40, "SELL"

    else:
        score, signal = 50, "NEUTRAL"

    return {
        "signal": signal,
        "score": score,
        "values": {
            "bias": round(bias, 2)
        },
    }


def analyse_volume(df: pd.DataFrame) -> dict:
    avg_vol = (
        df["volume"]
        .rolling(20)
        .mean()
        .iloc[-1]
    )

    cur_vol = df["volume"].iloc[-1]

    if avg_vol and avg_vol > 0:
        vol_ratio = _safe(
            cur_vol / avg_vol
        )
    else:
        vol_ratio = 1.0

    buy_days = 0
    sell_days = 0

    for _, row in df.tail(5).iterrows():

        if row["close"] >= row["open"]:
            buy_days += 1
        else:
            sell_days += 1

    score = 50
    signal = "NEUTRAL"

    if (
        buy_days > sell_days
        and vol_ratio
        and vol_ratio > 1.0
    ):
        score = min(
            100,
            50 + buy_days * 8
        )
        signal = "BUY"

    elif (
        sell_days > buy_days
        and vol_ratio
        and vol_ratio > 1.0
    ):
        score = max(
            0,
            50 - sell_days * 8
        )
        signal = "SELL"

    return {
        "signal": signal,
        "score": score,
        "values": {
            "volume_ratio": (
                round(vol_ratio, 2)
                if vol_ratio
                else 1.0
            ),
            "buy_days": buy_days,
            "sell_days": sell_days,
        },
    }


def run_technical_analysis(stock_data: dict) -> dict:
    history = stock_data.get("history", [])

    # Minimum data required
    if len(history) < 20:
        return {
            "overall_signal": "NEUTRAL",
            "overall_score": 50,
            "verdict": "Insufficient Data",
            "buy_signals": [],
            "sell_signals": [],
            "indicators": {},
        }

    df = _to_df(history)

    # ---------------------------------------------------------
    # Run individual technical indicators
    # ---------------------------------------------------------

    moving_averages = analyse_moving_averages(df)
    macd = analyse_macd(df)
    rsi = analyse_rsi(df)
    bollinger_bands = analyse_bollinger_bands(df)
    bias = analyse_bias(df)
    volume = analyse_volume(df)

    indicators = {
        "moving_averages": moving_averages,
        "macd": macd,
        "rsi": rsi,
        "bollinger_bands": bollinger_bands,
        "bias": bias,
        "volume": volume,
    }

    # ---------------------------------------------------------
    # Combine Moving Average + Bias into one Trend component
    # ---------------------------------------------------------

    trend_score = round(
        (
            moving_averages["score"]
            + bias["score"]
        ) / 2,
        1
    )

    if trend_score >= 60:
        trend_signal = "BUY"

    elif trend_score <= 40:
        trend_signal = "SELL"

    else:
        trend_signal = "NEUTRAL"

    indicators["trend"] = {
        "signal": trend_signal,
        "score": trend_score,
        "values": {
            "moving_average_score": moving_averages["score"],
            "bias_score": bias["score"],
        },
        "notes": (
            moving_averages.get("notes", [])
            + [
                f"Bias score: {bias['score']}"
            ]
        ),
    }

    # ---------------------------------------------------------
    # Final component weights
    # ---------------------------------------------------------

    weights = {
        "trend": 0.25,
        "macd": 0.20,
        "rsi": 0.20,
        "bollinger_bands": 0.20,
        "volume": 0.15,
    }

    # ---------------------------------------------------------
    # Calculate weight + contribution
    # ---------------------------------------------------------

    for key, indicator in indicators.items():

        if key in weights:

            indicator["weight"] = weights[key]

            indicator["contribution"] = round(
                indicator["score"]
                * indicator["weight"],
                2
            )

        else:

            # Moving averages and bias are now
            # supporting evidence inside Trend.
            indicator["weight"] = 0.0
            indicator["contribution"] = 0.0

    # ---------------------------------------------------------
    # Calculate overall technical score
    # ---------------------------------------------------------

    overall = round(
        sum(
            indicators[key]["contribution"]
            for key in weights
        ),
        1
    )

    # ---------------------------------------------------------
    # Convert score into overall signal
    # ---------------------------------------------------------

    if overall >= 65:
        sig = "STRONG BUY"
        verdict = "Strongly Bullish"

    elif overall >= 55:
        sig = "BUY"
        verdict = "Mildly Bullish"

    elif overall >= 45:
        sig = "NEUTRAL"
        verdict = "Neutral"

    elif overall >= 35:
        sig = "SELL"
        verdict = "Mildly Bearish"

    else:
        sig = "STRONG SELL"
        verdict = "Strongly Bearish"

    # ---------------------------------------------------------
    # Generate buy/sell evidence
    #
    # Only final weighted components are used here.
    # ---------------------------------------------------------

    buy_signals = [
        f"{key.replace('_', ' ').title()}: "
        f"{indicators[key]['signal']}"
        for key in weights
        if indicators[key]["signal"] in (
            "BUY",
            "STRONG BUY"
        )
    ]

    sell_signals = [
        f"{key.replace('_', ' ').title()}: "
        f"{indicators[key]['signal']}"
        for key in weights
        if indicators[key]["signal"] in (
            "SELL",
            "STRONG SELL"
        )
    ]

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    return {
        "overall_signal": sig,
        "overall_score": overall,
        "verdict": verdict,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
        "indicators": indicators,}