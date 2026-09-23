# backend/tips.py
# Rule-based loss-minimisation tips, shaped by the user's risk profile

def generate_tips(analysis: dict, risk_profile: str = "moderate") -> list:
    tips  = []
    ta    = analysis.get("technical", {})
    fa    = analysis.get("fundamental", {})
    pred  = analysis.get("prediction", {})
    fa_m  = fa.get("metrics", {})
    ind   = ta.get("indicators", {})
    price = analysis.get("current_price", 0)

    rsi_val = ind.get("rsi", {}).get("values", {}).get("rsi")
    if rsi_val:
        if rsi_val > 75:
            tips.append(f"RSI is {rsi_val:.0f} (bought too much). Consider booking partial profits (20-30%); such stocks often pull back 5-10%.")
        elif rsi_val < 28:
            if risk_profile in ("moderate", "aggressive"):
                tips.append(f"RSI is {rsi_val:.0f} (sold too much). Could be a buying chance — buy in small parts, not all at once.")
            else:
                tips.append(f"RSI is {rsi_val:.0f} (sold too much). Careful investors: wait for RSI to cross above 35 before entering.")

    bb_lower = ind.get("bollinger_bands", {}).get("values", {}).get("lower")
    if bb_lower and price > 0:
        sl = round((price - bb_lower) / price * 100, 1)
        if risk_profile == "conservative": sl = min(sl, 3)
        elif risk_profile == "moderate":   sl = min(sl, 5)
        else:                              sl = min(sl, 8)
        tips.append(f"Stop-loss idea: sell if price falls to Rs.{round(price*(1-sl/100),2)} ({sl}% below now). This limits your maximum loss.")

    ma = ind.get("moving_averages", {}).get("values", {})
    if ma.get("ma50") and ma.get("ma200") and ma["ma50"] < ma["ma200"]:
        tips.append("Death Cross: the medium-term trend is down. Avoid big positions until the trend turns up again.")

    vol = ind.get("volume", {})
    if vol.get("signal") == "SELL" and vol.get("values", {}).get("volume_ratio", 1) >= 1.5:
        tips.append("Heavy selling detected. Big players may be exiting. Consider reducing your position.")

    pe = fa_m.get("pe_ratio", {})
    if pe.get("score", 50) <= 25:
        tips.append(f"P/E of {pe.get('value','N/A')} is very high. Such stocks fall harder in a correction. Keep the position small.")

    margin = fa_m.get("net_margin", {})
    if margin.get("value") is not None and margin["value"] < 0:
        tips.append(f"Loss-making company (net margin {margin['value']:.1f}%). Limit exposure to 2-3% of your total money.")

    pred_text = pred.get("prediction", "")
    if "Bearish" in pred_text and risk_profile == "conservative":
        tips.append("Both studies point down. Careful investors: wait for signals to turn neutral or positive before entering.")
    elif pred_text == "Strong Bullish" and risk_profile == "aggressive":
        tips.append("Strong positive signal. Enter in 2-3 parts instead of one lump sum to average your buying price.")

    tips.append("General rule: never put more than 5-10% of your total money into a single stock. Spreading out protects you.")
    return tips[:6]
