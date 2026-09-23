# backend/analysis/fundamental.py
# Company Health Check — scores ROE, ROIC, Net Margin, P/E, P/B, PEG

from typing import Optional

SECTOR_PE_BENCHMARKS = {
    "Technology": 25, "Financial Services": 15, "Banking": 12,
    "Consumer Defensive": 22, "Healthcare": 28, "Energy": 12,
    "Industrials": 18, "Real Estate": 20, "Utilities": 16,
    "Communication Services": 20, "default": 20,
}

def score_roe(roe: Optional[float]) -> dict:
    if roe is None:
        return {"value": None, "score": 50, "label": "N/A", "note": "Data not available"}
    pct = roe * 100
    if pct >= 25:   score, label = 90, "Excellent"
    elif pct >= 18: score, label = 75, "Good"
    elif pct >= 12: score, label = 55, "Moderate"
    elif pct >= 5:  score, label = 35, "Weak"
    else:           score, label = 15, "Poor"
    return {"value": round(pct, 2), "score": score, "label": label,
            "note": f"Earns {round(pct,1)}% return on shareholder equity"}

def score_roic(roic: Optional[float]) -> dict:
    if roic is None:
        return {"value": None, "score": 50, "label": "N/A", "note": "Data not available"}
    pct = roic * 100
    if pct >= 15:   score, label = 90, "Excellent"
    elif pct >= 10: score, label = 72, "Good"
    elif pct >= 5:  score, label = 50, "Moderate"
    elif pct >= 0:  score, label = 30, "Weak"
    else:           score, label = 10, "Negative"
    return {"value": round(pct, 2), "score": score, "label": label,
            "note": f"Returns {round(pct,1)}% on invested assets"}

def score_net_margin(margin: Optional[float]) -> dict:
    if margin is None:
        return {"value": None, "score": 50, "label": "N/A", "note": "Data not available"}
    pct = margin * 100
    if pct >= 20:   score, label = 92, "Excellent"
    elif pct >= 12: score, label = 75, "Good"
    elif pct >= 5:  score, label = 52, "Moderate"
    elif pct >= 0:  score, label = 28, "Weak"
    else:           score, label = 10, "Loss-making"
    return {"value": round(pct, 2), "score": score, "label": label,
            "note": f"Keeps {round(pct,1)}% of revenue as profit"}

def score_pe(pe: Optional[float], sector: str = "default") -> dict:
    if pe is None or pe <= 0:
        return {"value": None, "score": 50, "label": "N/A", "note": "Data not available"}
    benchmark = SECTOR_PE_BENCHMARKS.get(sector, 20)
    ratio = pe / benchmark
    if ratio <= 0.7:    score, label = 88, "Very Undervalued"
    elif ratio <= 0.9:  score, label = 72, "Undervalued"
    elif ratio <= 1.1:  score, label = 58, "Fair Value"
    elif ratio <= 1.4:  score, label = 38, "Slightly Overvalued"
    elif ratio <= 2.0:  score, label = 22, "Overvalued"
    else:               score, label = 10, "Highly Overvalued"
    return {"value": round(pe, 2), "score": score, "label": label,
            "note": f"P/E of {round(pe,1)}x vs sector benchmark {benchmark}x", "benchmark": benchmark}

def score_pb(pb: Optional[float]) -> dict:
    if pb is None or pb <= 0:
        return {"value": None, "score": 50, "label": "N/A", "note": "Data not available"}
    if pb <= 1.0:   score, label = 88, "Below Book Value"
    elif pb <= 2.0: score, label = 72, "Undervalued"
    elif pb <= 3.5: score, label = 55, "Fair Value"
    elif pb <= 5.0: score, label = 35, "Premium"
    else:           score, label = 18, "Highly Overvalued"
    return {"value": round(pb, 2), "score": score, "label": label,
            "note": f"Trading at {round(pb,1)}x book value"}

def score_peg(peg: Optional[float]) -> dict:
    if peg is None or peg <= 0:
        return {"value": None, "score": 50, "label": "N/A", "note": "Data not available"}
    if peg <= 0.5:   score, label = 92, "Deeply Undervalued"
    elif peg <= 1.0: score, label = 78, "Undervalued"
    elif peg <= 1.5: score, label = 55, "Fair"
    elif peg <= 2.0: score, label = 35, "Overvalued"
    else:            score, label = 15, "Highly Overvalued"
    return {"value": round(peg, 2), "score": score, "label": label,
            "note": f"PEG of {round(peg,2)} (below 1.0 is ideal)"}

def run_fundamental_analysis(stock_data: dict) -> dict:
    fa     = stock_data.get("fundamentals", {})
    sector = stock_data.get("sector", "default")
    metrics = {
        "roe":        score_roe(fa.get("roe")),
        "roic":       score_roic(fa.get("roic")),
        "net_margin": score_net_margin(fa.get("net_margin")),
        "pe_ratio":   score_pe(fa.get("pe_ratio"), sector),
        "pb_ratio":   score_pb(fa.get("pb_ratio")),
        "peg_ratio":  score_peg(fa.get("peg_ratio")),
    }
    weights = {"roe": 0.20, "roic": 0.15, "net_margin": 0.15,
               "pe_ratio": 0.20, "pb_ratio": 0.15, "peg_ratio": 0.15}
    overall = round(sum(metrics[k]["score"] * weights[k] for k in weights), 1)

    if overall >= 75:   verdict, color = "Fundamentally Strong", "green"
    elif overall >= 55: verdict, color = "Fundamentally Fair",   "blue"
    elif overall >= 35: verdict, color = "Fundamentally Weak",   "orange"
    else:               verdict, color = "High Risk / Overvalued", "red"

    high_52 = fa.get("52w_high"); low_52 = fa.get("52w_low")
    price   = stock_data.get("current_price", 0)
    w52_pos = None
    if high_52 and low_52 and high_52 != low_52:
        w52_pos = round((price - low_52) / (high_52 - low_52) * 100, 1)

    return {"overall_score": overall, "verdict": verdict, "color": color, "metrics": metrics,
            "extra": {"52w_high": high_52, "52w_low": low_52, "52w_position": w52_pos,
                      "market_cap": fa.get("market_cap"), "beta": fa.get("beta")}}
