# backend/analysis/predictor.py
# Combines Fundamental + Technical Analysis
# and generates a Generative AI explanation


from analysis.fundamental import run_fundamental_analysis
from analysis.technical import run_technical_analysis
from analysis.genai import generate_ai_recommendation
from stocks import fetch_stock
import math


def combine_fa_ta(
    fa_score: float,
    ta_score: float
) -> dict:
    """
    Combine fundamental and technical scores.

    Fundamental analysis = 40%
    Technical analysis = 60%

    The combined score is a score, not a statistical probability.
    """

    combined = round(
        (fa_score * 0.40)
        + (ta_score * 0.60),
        1
    )

    if combined >= 72:

        prediction = "Strong Bullish"
        desc = (
            "Strong positive bias based on "
            "the combined analysis."
        )
        color = "green"

    elif combined >= 58:

        prediction = "Mildly Bullish"
        desc = (
            "Moderately positive bias, but "
            "reversal risk should be considered."
        )
        color = "lightgreen"

    elif combined >= 42:

        prediction = "Neutral"
        desc = (
            "The combined indicators provide "
            "mixed signals."
        )
        color = "gray"

    elif combined >= 28:

        prediction = "Mildly Bearish"
        desc = (
            "Moderately negative bias based on "
            "the combined analysis."
        )
        color = "orange"

    else:

        prediction = "Strong Bearish"
        desc = (
            "Strong negative bias based on "
            "the combined analysis."
        )
        color = "red"

    return {
        "prediction": prediction,
        "description": desc,
        "color": color,
        "combined_score": combined,
        "score_range": {
            "minimum": 0,
            "maximum": 100
        }
    }


def generate_key_insights(
    fa_result: dict,
    ta_result: dict,
    stock_data: dict
) -> list:

    insights = []

    fa = fa_result.get(
        "metrics",
        {}
    )

    ind = ta_result.get(
        "indicators",
        {}
    )

    # ---------------------------------------------------------
    # ROE
    # ---------------------------------------------------------

    roe = fa.get(
        "roe",
        {}
    )

    if (
        roe.get("value") is not None
        and roe["value"] > 18
    ):

        insights.append(
            f"Strong business: earns "
            f"{roe['value']:.1f}% return on "
            f"owners' money — above average."
        )

    elif (
        roe.get("value") is not None
        and roe["value"] < 8
    ):

        insights.append(
            f"Weak profitability: ROE of "
            f"{roe['value']:.1f}% is below average."
        )

    # ---------------------------------------------------------
    # P/E
    # ---------------------------------------------------------

    pe = fa.get(
        "pe_ratio",
        {}
    )

    if (
        pe.get("value") is not None
        and pe.get("score", 50) >= 70
    ):

        insights.append(
            f"May be cheap: P/E of "
            f"{pe['value']:.1f}x is below "
            f"the sector average."
        )

    elif (
        pe.get("value") is not None
        and pe.get("score", 50) <= 30
    ):

        insights.append(
            f"Looks expensive: P/E of "
            f"{pe['value']:.1f}x is above "
            f"the sector average."
        )

    # ---------------------------------------------------------
    # Net Margin
    # ---------------------------------------------------------

    margin = fa.get(
        "net_margin",
        {}
    )

    if (
        margin.get("value") is not None
        and margin["value"] < 0
    ):

        insights.append(
            f"Warning: the company is "
            f"loss-making (net margin "
            f"{margin['value']:.1f}%)."
        )

    # ---------------------------------------------------------
    # 52-week position
    # ---------------------------------------------------------

    w52 = fa_result.get(
        "extra",
        {}
    ).get(
        "52w_position"
    )

    if w52 is not None:

        if w52 <= 15:

            insights.append(
                f"Near its 1-year low "
                f"({w52:.0f}% from bottom)."
            )

        elif w52 >= 85:

            insights.append(
                f"Near its 1-year high "
                f"({w52:.0f}%)."
            )

    # ---------------------------------------------------------
    # RSI
    # ---------------------------------------------------------

    rsi = (
        ind.get(
            "rsi",
            {}
        )
        .get(
            "values",
            {}
        )
        .get(
            "rsi"
        )
    )

    if rsi is not None:

        if rsi < 30:

            insights.append(
                f"RSI {rsi:.0f} indicates "
                f"the stock has experienced "
                f"strong recent selling."
            )

        elif rsi > 70:

            insights.append(
                f"RSI {rsi:.0f} indicates "
                f"strong recent buying."
            )

    # ---------------------------------------------------------
    # MACD
    # ---------------------------------------------------------

    macd = ind.get(
        "macd",
        {}
    )

    if macd.get("signal") == "BUY":

        insights.append(
            "MACD indicates positive momentum."
        )

    elif macd.get("signal") == "SELL":

        insights.append(
            "MACD indicates negative momentum."
        )

    # ---------------------------------------------------------
    # Bollinger squeeze
    # ---------------------------------------------------------

    squeeze = (
        ind.get(
            "bollinger_bands",
            {}
        )
        .get(
            "values",
            {}
        )
        .get(
            "squeeze"
        )
    )

    if squeeze:

        insights.append(
            "Price range is unusually tight, "
            "indicating potentially increased "
            "volatility ahead."
        )

    return insights[:5]


def get_full_analysis(
    symbol: str,
    risk_profile: str = "moderate"
):

    # ---------------------------------------------------------
    # Get market data
    # ---------------------------------------------------------

    stock_data = fetch_stock(
        symbol
    )

    if not stock_data:
        return None

    # ---------------------------------------------------------
    # Fundamental analysis
    # ---------------------------------------------------------

    fa_result = run_fundamental_analysis(
        stock_data
    )

    # ---------------------------------------------------------
    # Technical analysis
    # ---------------------------------------------------------

    ta_result = run_technical_analysis(
        stock_data
    )

    # ---------------------------------------------------------
    # Combined prediction
    # ---------------------------------------------------------

    prediction = combine_fa_ta(
        fa_result["overall_score"],
        ta_result["overall_score"]
    )

    # ---------------------------------------------------------
    # Rule-based insights
    # ---------------------------------------------------------

    insights = generate_key_insights(
        fa_result,
        ta_result,
        stock_data
    )

    # ---------------------------------------------------------
    # Generative AI explanation
    # ---------------------------------------------------------

    ai_analysis = generate_ai_recommendation(
        symbol=symbol,
        name=stock_data.get(
            "name",
            symbol
        ),
        risk_profile=risk_profile,
        fundamental=fa_result,
        technical=ta_result,
        prediction=prediction,
    )

    # ---------------------------------------------------------
    # Complete analysis response
    # ---------------------------------------------------------

    result = {
    "symbol": symbol,
    "name": stock_data.get("name", symbol),
    "sector": stock_data.get("sector", "N/A"),
    "current_price": stock_data.get("current_price"),
    "change_pct": stock_data.get("change_pct"),
    "direction": stock_data.get("direction"),
    "fundamental": fa_result,
    "technical": ta_result,
    "prediction": prediction,
    "insights": insights,
    "ai_analysis": ai_analysis,
    "chart_data": stock_data.get("history", [])[-60:],
    "disclaimer": (
        "This analysis is for EDUCATIONAL purposes only and is NOT financial advice. "
        "Markets are unpredictable. Please do your own research and consult a SEBI-registered "
        "financial adviser before investing. Take your own decisions — don't rely on market tips."
    ),
}

    return clean_nan_values(result)
    
def clean_nan_values(obj):
    if isinstance(obj, dict):
        return {
            key: clean_nan_values(value)
            for key, value in obj.items()
        }

    if isinstance(obj, list):
        return [
            clean_nan_values(value)
            for value in obj
        ]

    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None

    return obj