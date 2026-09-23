# backend/analysis/predictor.py
# Combines the Company Health Check + Market Timing Study into a weekly outlook

from analysis.fundamental import run_fundamental_analysis
from analysis.technical import run_technical_analysis
from stocks import get_stock_data


def combine_fa_ta(fa_score: float, ta_score: float) -> dict:
    combined = round((fa_score * 0.40) + (ta_score * 0.60), 1)
    if combined >= 72:   prediction, desc, color, bull = "Strong Bullish",  "High chance of upward movement next week",   "green",      min(95, int(combined))
    elif combined >= 58: prediction, desc, color, bull = "Mildly Bullish",  "Slight upward bias, watch for reversal",      "lightgreen", int(50 + (combined-50)*0.8)
    elif combined >= 42: prediction, desc, color, bull = "Neutral",         "Mixed signals — could go either way",         "gray",       50
    elif combined >= 28: prediction, desc, color, bull = "Mildly Bearish",  "Slight downward bias — consider caution",     "orange",     int(50 - (50-combined)*0.8)
    else:                prediction, desc, color, bull = "Strong Bearish",  "High chance of downward movement next week",  "red",        max(5, int(combined))
    return {"prediction": prediction, "description": desc, "color": color,
            "combined_score": combined, "probability": {"bullish": bull, "bearish": 100 - bull}}


def generate_key_insights(fa_result: dict, ta_result: dict, stock_data: dict) -> list:
    insights = []
    fa = fa_result.get("metrics", {})
    ind = ta_result.get("indicators", {})

    roe = fa.get("roe", {})
    if roe.get("value") and roe["value"] > 18:
        insights.append(f"Strong business: earns {roe['value']:.1f}% return on owners' money — above average.")
    elif roe.get("value") and roe["value"] < 8:
        insights.append(f"Weak profitability: ROE of {roe['value']:.1f}% is below average.")

    pe = fa.get("pe_ratio", {})
    if pe.get("value") and pe.get("score", 50) >= 70:
        insights.append(f"May be cheap: P/E of {pe['value']:.1f}x is below the sector average.")
    elif pe.get("value") and pe.get("score", 50) <= 30:
        insights.append(f"Looks expensive: P/E of {pe['value']:.1f}x is above the sector average.")

    margin = fa.get("net_margin", {})
    if margin.get("value") and margin["value"] < 0:
        insights.append(f"Warning: the company is loss-making (net margin {margin['value']:.1f}%).")

    w52 = fa_result.get("extra", {}).get("52w_position")
    if w52 is not None:
        if w52 <= 15:
            insights.append(f"Near its 1-year low ({w52:.0f}% from bottom) — possible recovery play.")
        elif w52 >= 85:
            insights.append(f"Near its 1-year high ({w52:.0f}%) — be careful chasing it.")

    rsi = ind.get("rsi", {}).get("values", {}).get("rsi")
    if rsi:
        if rsi < 30:   insights.append(f"RSI {rsi:.0f} — sold too much recently; a short bounce is likely.")
        elif rsi > 70: insights.append(f"RSI {rsi:.0f} — bought too much recently; a pullback is possible.")

    macd = ind.get("macd", {})
    if macd.get("signal") == "BUY":   insights.append("Momentum is turning upward.")
    elif macd.get("signal") == "SELL": insights.append("Momentum is turning downward — selling pressure rising.")

    if ind.get("bollinger_bands", {}).get("values", {}).get("squeeze"):
        insights.append("Price range is unusually tight — a big move may be coming. Wait for direction.")

    return insights[:5]


def get_full_analysis(symbol: str):
    stock_data = get_stock_data(symbol)
    if not stock_data:
        return None
    fa_result  = run_fundamental_analysis(stock_data)
    ta_result  = run_technical_analysis(stock_data)
    prediction = combine_fa_ta(fa_result["overall_score"], ta_result["overall_score"])
    insights   = generate_key_insights(fa_result, ta_result, stock_data)
    return {
        "symbol": symbol, "name": stock_data.get("name", symbol),
        "sector": stock_data.get("sector", "N/A"),
        "current_price": stock_data.get("current_price"),
        "change_pct": stock_data.get("change_pct"),
        "direction": stock_data.get("direction"),
        "fundamental": fa_result, "technical": ta_result,
        "prediction": prediction, "insights": insights,
        "chart_data": stock_data.get("history", [])[-60:],
        "disclaimer": (
            "This analysis is for EDUCATIONAL purposes only and is NOT financial advice. "
            "Markets are unpredictable. Please do your own research and consult a SEBI-registered "
            "financial adviser before investing. Take your own decisions — don't rely on market tips."
        ),
    }
