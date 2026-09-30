# backend/tips.py
# Rule-based risk-awareness tips shaped by the user's risk profile

def generate_tips(analysis: dict, risk_profile: str = "moderate") -> list:
    tips = []

    ta = analysis.get("technical", {})
    fa = analysis.get("fundamental", {})
    pred = analysis.get("prediction", {})

    fa_m = fa.get("metrics", {})
    ind = ta.get("indicators", {})

    price = analysis.get("current_price", 0)

    # ---------------------------------------------------------
    # RSI
    # ---------------------------------------------------------
    rsi_val = ind.get("rsi", {}).get("values", {}).get("rsi")

    if rsi_val is not None:
        if rsi_val > 75:
            tips.append(
                f"RSI is {rsi_val:.1f}, indicating strong recent buying pressure. "
                "A pullback is possible, so monitor the position carefully."
            )

        elif rsi_val < 28:
            tips.append(
                f"RSI is {rsi_val:.1f}, indicating strong recent selling pressure. "
                "This may indicate oversold conditions, but it does not guarantee a rebound."
            )

    # ---------------------------------------------------------
    # Bollinger Band risk reference
    # ---------------------------------------------------------
    bb_lower = (
        ind.get("bollinger_bands", {})
        .get("values", {})
        .get("lower")
    )

    if bb_lower is not None and price > 0 and bb_lower < price:

        distance_pct = ((price - bb_lower) / price) * 100

        # Avoid extremely small or excessively large levels.
        if risk_profile == "conservative":
            reference_pct = max(3.0, min(distance_pct, 5.0))
        elif risk_profile == "moderate":
            reference_pct = max(4.0, min(distance_pct, 7.0))
        else:
            reference_pct = max(5.0, min(distance_pct, 10.0))

        risk_reference = round(
            price * (1 - reference_pct / 100),
            2
        )

        tips.append(
            f"Risk reference level: Rs.{risk_reference:.2f}, "
            f"approximately {reference_pct:.1f}% below the current price. "
            "This is an educational reference based on recent price behaviour, "
            "not a guaranteed stop-loss."
        )

    # ---------------------------------------------------------
    # Moving-average trend
    # ---------------------------------------------------------
    ma = ind.get("moving_averages", {}).get("values", {})

    ma50 = ma.get("ma50")
    ma200 = ma.get("ma200")

    if ma50 is not None and ma200 is not None and ma50 < ma200:
        tips.append(
            "The 50-day moving average is below the 200-day moving average, "
            "indicating a weaker medium-term trend."
        )

    # ---------------------------------------------------------
    # Volume
    # ---------------------------------------------------------
    vol = ind.get("volume", {})

    volume_ratio = vol.get("values", {}).get("volume_ratio", 1)

    if (
        vol.get("signal") == "SELL"
        and volume_ratio >= 1.5
    ):
        tips.append(
            "Trading volume is relatively high on recent selling days. "
            "Monitor whether this selling pressure continues."
        )

    # ---------------------------------------------------------
    # P/E
    # ---------------------------------------------------------
    pe = fa_m.get("pe_ratio", {})

    if pe.get("score", 50) <= 25:
        tips.append(
            f"P/E of {pe.get('value', 'N/A')} is relatively high according "
            "to the application's valuation score. Higher valuations can "
            "increase sensitivity to disappointing results."
        )

    # ---------------------------------------------------------
    # Net margin
    # ---------------------------------------------------------
    margin = fa_m.get("net_margin", {})

    if (
        margin.get("value") is not None
        and margin["value"] < 0
    ):
        tips.append(
            f"The company currently has a negative net margin "
            f"({margin['value']:.1f}%). This indicates that the company "
            "is currently reporting a loss."
        )

    # ---------------------------------------------------------
    # Combined prediction
    # ---------------------------------------------------------
    pred_text = pred.get("prediction", "")

    if "Bearish" in pred_text:
        tips.append(
            "The combined analysis has a bearish signal. "
            "Consider monitoring the stock for confirmation before making decisions."
        )

    elif pred_text == "Strong Bullish":
        tips.append(
            "The combined analysis has a strong positive signal, "
            "but market conditions can change. Consider diversification and position sizing."
        )

    # ---------------------------------------------------------
    # General diversification reminder
    # ---------------------------------------------------------
    tips.append(
        "Diversification can help reduce the impact of a single stock "
        "performing poorly. Avoid concentrating too much of your portfolio "
        "in one company."
    )

    return tips[:6]