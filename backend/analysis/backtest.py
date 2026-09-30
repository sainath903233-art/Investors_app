# backend/analysis/backtest.py
# Historical backtesting for the technical analysis engine

import pandas as pd

from analysis.technical import run_technical_analysis
from stocks import fetch_stock


def calculate_metrics(predictions):
    """
    Calculate evaluation metrics for BUY/SELL predictions.

    NEUTRAL predictions are excluded from directional metrics.
    Baselines are calculated on the same actionable test cases.
    """

    actionable = [
        p for p in predictions
        if p["prediction"] in ("BUY", "SELL")
        and p["actual"] in ("BUY", "SELL")
    ]

    if not actionable:
        return {
            "total_predictions": 0,
            "correct_predictions": 0,
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "confusion_matrix": {
                "true_positive": 0,
                "true_negative": 0,
                "false_positive": 0,
                "false_negative": 0,
            },
            "baseline": {
                "always_buy_accuracy": 0.0,
                "always_sell_accuracy": 0.0,
            },
        }

    # ---------------------------------------------------------
    # Confusion matrix
    #
    # BUY is treated as the positive class.
    # ---------------------------------------------------------

    true_positive = sum(
        1
        for p in actionable
        if p["prediction"] == "BUY"
        and p["actual"] == "BUY"
    )

    true_negative = sum(
        1
        for p in actionable
        if p["prediction"] == "SELL"
        and p["actual"] == "SELL"
    )

    false_positive = sum(
        1
        for p in actionable
        if p["prediction"] == "BUY"
        and p["actual"] == "SELL"
    )

    false_negative = sum(
        1
        for p in actionable
        if p["prediction"] == "SELL"
        and p["actual"] == "BUY"
    )

    # ---------------------------------------------------------
    # Accuracy
    # ---------------------------------------------------------

    correct = true_positive + true_negative

    accuracy = (
        correct / len(actionable) * 100
    )

    # ---------------------------------------------------------
    # Precision
    # ---------------------------------------------------------

    if true_positive + false_positive > 0:
        precision = (
            true_positive
            / (true_positive + false_positive)
            * 100
        )
    else:
        precision = 0.0

    # ---------------------------------------------------------
    # Recall
    # ---------------------------------------------------------

    if true_positive + false_negative > 0:
        recall = (
            true_positive
            / (true_positive + false_negative)
            * 100
        )
    else:
        recall = 0.0

    # ---------------------------------------------------------
    # F1 score
    # ---------------------------------------------------------

    if precision + recall > 0:
        f1_score = (
            2 * precision * recall
            / (precision + recall)
        )
    else:
        f1_score = 0.0

    # ---------------------------------------------------------
    # Simple baselines
    #
    # Evaluate on the same actionable observations.
    # ---------------------------------------------------------

    actual_buy_count = sum(
        1
        for p in actionable
        if p["actual"] == "BUY"
    )

    actual_sell_count = sum(
        1
        for p in actionable
        if p["actual"] == "SELL"
    )

    always_buy_accuracy = (
        actual_buy_count
        / len(actionable)
        * 100
    )

    always_sell_accuracy = (
        actual_sell_count
        / len(actionable)
        * 100
    )

    return {
        "total_predictions": len(actionable),
        "correct_predictions": correct,

        "accuracy": round(
            accuracy,
            2
        ),

        "precision": round(
            precision,
            2
        ),

        "recall": round(
            recall,
            2
        ),

        "f1_score": round(
            f1_score,
            2
        ),

        "confusion_matrix": {
            "true_positive": true_positive,
            "true_negative": true_negative,
            "false_positive": false_positive,
            "false_negative": false_negative,
        },

        "baseline": {
            "always_buy_accuracy": round(
                always_buy_accuracy,
                2
            ),
            "always_sell_accuracy": round(
                always_sell_accuracy,
                2
            ),
        },
    }


def run_backtest(symbol: str, horizon: int = 5) -> dict:
    """
    Backtest the technical analysis engine.

    horizon:
        Number of future trading days used to determine
        actual price direction.
    """

    stock_data = fetch_stock(
        symbol,
        period="2y"
    )

    if not stock_data:
        return {
            "symbol": symbol,
            "error": "No stock data available."
        }

    history = stock_data.get(
        "history",
        []
    )

    if len(history) < 50:
        return {
            "symbol": symbol,
            "error": "Not enough historical data for backtesting."
        }

    df = pd.DataFrame(history)

    df["date"] = pd.to_datetime(
        df["date"]
    )

    df["close"] = df["close"].astype(float)

    df = df.sort_values(
        "date"
    ).reset_index(drop=True)

    predictions = []

    # Enough historical data for the technical indicators
    start_index = 200

    final_index = len(df) - horizon

    if final_index <= start_index:
        return {
            "symbol": symbol,
            "error": (
                "Not enough historical rows for "
                "the selected backtest window."
            )
        }

    for i in range(
        start_index,
        final_index
    ):

        # Only data available up to this historical date
        historical_data = df.iloc[
            :i + 1
        ].copy()

        historical_records = (
            historical_data.to_dict(
                orient="records"
            )
        )

        technical_result = run_technical_analysis(
            {
                "history": historical_records
            }
        )

        signal = technical_result[
            "overall_signal"
        ]

        # Convert technical signal into
        # a directional prediction
        if signal in (
            "BUY",
            "STRONG BUY"
        ):
            prediction = "BUY"

        elif signal in (
            "SELL",
            "STRONG SELL"
        ):
            prediction = "SELL"

        else:
            prediction = "NEUTRAL"

        current_price = float(
            df.iloc[i]["close"]
        )

        future_price = float(
            df.iloc[i + horizon]["close"]
        )

        future_return = (
            (future_price - current_price)
            / current_price
            * 100
        )

        # ---------------------------------------------
        # Meaningful movement threshold
        # ---------------------------------------------

        RETURN_THRESHOLD = 1.0

        if future_return > RETURN_THRESHOLD:
         actual = "BUY"

        elif future_return < -RETURN_THRESHOLD:
          actual = "SELL"

        else:
         actual = "NEUTRAL"

        # ---------------------------------------------
        # Store prediction
        # ---------------------------------------------

        predictions.append(
            {
                "date": df.iloc[i]["date"].strftime(
                    "%Y-%m-%d"
                ),

                "price": round(
                    current_price,
                    2
                ),

                "technical_score": technical_result[
                    "overall_score"
                ],

                "prediction": prediction,

                "actual": actual,

                "future_return_pct": round(
                    future_return,
                    2
                ),
            }
        )
            # ---------------------------------------------------------
    # Calculate evaluation metrics
    # ---------------------------------------------------------

    metrics = calculate_metrics(
        predictions
    )
    # ---------------------------------------------------------
    # Backtest summary counts
    # ---------------------------------------------------------

    total_test_cases = len(predictions)

    neutral_signal_count = sum(
        1
        for p in predictions
        if p["prediction"] == "NEUTRAL"
    )

    directional_signal_count = sum(
        1
        for p in predictions
        if p["prediction"] in ("BUY", "SELL")
    )

    actual_neutral_count = sum(
        1
        for p in predictions
        if p["actual"] == "NEUTRAL"
    )

    return {
        "symbol": symbol,
        "horizon_days": horizon,

        # Total historical cases evaluated
        "data_points_tested": total_test_cases,

        # Model prediction breakdown
        "directional_signals": directional_signal_count,
        "neutral_predictions": neutral_signal_count,

        # Actual market outcome breakdown
        "actual_neutral_outcomes": actual_neutral_count,

        # BUY/SELL cases used for directional metrics
        "metrics": metrics,

        "predictions": predictions,
    }