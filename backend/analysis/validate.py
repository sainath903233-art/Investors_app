# backend/analysis/validate.py
# Multi-stock validation for InvestSmart

from analysis.backtest import run_backtest


# ---------------------------------------------------------
# Stocks used for validation
# ---------------------------------------------------------

STOCKS = {
    "RELIANCE": "Energy",
    "TCS": "IT",
    "INFY": "IT",
    "WIPRO": "IT",

    "HDFCBANK": "Banking",
    "ICICIBANK": "Banking",
    "SBIN": "Banking",
    "AXISBANK": "Banking",
    "BAJFINANCE": "Financial Services",

    "LT": "Infrastructure",

    "BHARTIARTL": "Telecom",

    "HINDUNILVR": "FMCG",
    "ITC": "FMCG",

    "SUNPHARMA": "Healthcare",

    "MARUTI": "Automobile",

    "ASIANPAINT": "Consumer",

    "ADANIENT": "Conglomerate",

    "KOTAKBANK": "Banking",
}


def run_validation():
    """
    Run historical backtesting for all configured stocks.

    Stocks that fail because of unavailable market data
    are recorded instead of stopping the entire validation.
    """

    results = []

    for symbol, sector in STOCKS.items():

        try:

            print(
                f"Testing {symbol}..."
            )

            result = run_backtest(
                symbol
            )

            # ---------------------------------------------
            # Backtest failed
            # ---------------------------------------------

            if "error" in result:

                results.append({
                    "symbol": symbol,
                    "sector": sector,
                    "success": False,
                    "error": result["error"],
                })

                print(
                    f"{symbol}: "
                    f"{result['error']}"
                )

                continue

            metrics = result["metrics"]

            results.append({
                "symbol": symbol,
                "sector": sector,
                "success": True,

                "cases": result[
                    "data_points_tested"
                ],

                "actionable": metrics[
                    "total_predictions"
                ],

                "correct": metrics[
                    "correct_predictions"
                ],

                "accuracy": metrics[
                    "accuracy"
                ],

                "precision": metrics[
                    "precision"
                ],

                "recall": metrics[
                    "recall"
                ],

                "f1_score": metrics[
                    "f1_score"
                ],

                "baseline": metrics[
                    "baseline"
                ],

                "confusion_matrix": metrics[
                    "confusion_matrix"
                ],
            })

            print(
                f"{symbol}: "
                f"Accuracy={metrics['accuracy']}% | "
                f"Precision={metrics['precision']}% | "
                f"Recall={metrics['recall']}% | "
                f"F1={metrics['f1_score']}%"
            )

        except Exception as e:

            results.append({
                "symbol": symbol,
                "sector": sector,
                "success": False,
                "error": str(e),
            })

            print(
                f"{symbol}: ERROR - {e}"
            )


    # -----------------------------------------------------
    # Successful results
    # -----------------------------------------------------

    successful = [
        result
        for result in results
        if result["success"]
    ]


    failed = [
        result
        for result in results
        if not result["success"]
    ]


    # -----------------------------------------------------
    # Macro averages
    # -----------------------------------------------------

    if successful:

        macro_accuracy = round(
            sum(
                r["accuracy"]
                for r in successful
            )
            / len(successful),
            2
        )

        macro_precision = round(
            sum(
                r["precision"]
                for r in successful
            )
            / len(successful),
            2
        )

        macro_recall = round(
            sum(
                r["recall"]
                for r in successful
            )
            / len(successful),
            2
        )

        macro_f1 = round(
            sum(
                r["f1_score"]
                for r in successful
            )
            / len(successful),
            2
        )

    else:

        macro_accuracy = 0.0
        macro_precision = 0.0
        macro_recall = 0.0
        macro_f1 = 0.0


    # -----------------------------------------------------
    # Final validation result
    # -----------------------------------------------------

    return {
        "stocks_requested": len(STOCKS),

        "stocks_tested": len(
            successful
        ),

        "stocks_failed": len(
            failed
        ),

        "macro_average": {
            "accuracy": macro_accuracy,
            "precision": macro_precision,
            "recall": macro_recall,
            "f1_score": macro_f1,
        },

        "results": results,
    }


# ---------------------------------------------------------
# Terminal output
# ---------------------------------------------------------

if __name__ == "__main__":

    validation = run_validation()

    print("\n========================================")
    print("INVESTSMART MULTI-STOCK VALIDATION")
    print("========================================")

    print(
        f"\nStocks requested: "
        f"{validation['stocks_requested']}"
    )

    print(
        f"Stocks successfully tested: "
        f"{validation['stocks_tested']}"
    )

    print(
        f"Stocks with unavailable/error data: "
        f"{validation['stocks_failed']}"
    )

    print("\n========================================")
    print("STOCK RESULTS")
    print("========================================")

    print(
        f"{'Stock':<12}"
        f"{'Sector':<20}"
        f"{'Cases':<8}"
        f"{'Actionable':<12}"
        f"{'Accuracy':<11}"
        f"{'Precision':<11}"
        f"{'Recall':<10}"
        f"{'F1':<10}"
    )

    print("-" * 105)

    for result in validation["results"]:

        if not result["success"]:

            print(
                f"{result['symbol']:<12}"
                f"{result['sector']:<20}"
                f"ERROR: {result['error']}"
            )

            continue

        print(
            f"{result['symbol']:<12}"
            f"{result['sector']:<20}"
            f"{result['cases']:<8}"
            f"{result['actionable']:<12}"
            f"{result['accuracy']:<11}"
            f"{result['precision']:<11}"
            f"{result['recall']:<10}"
            f"{result['f1_score']:<10}"
        )

    print("\n========================================")
    print("MACRO AVERAGE")
    print("========================================")

    print(
        f"Accuracy:   "
        f"{validation['macro_average']['accuracy']}%"
    )

    print(
        f"Precision:  "
        f"{validation['macro_average']['precision']}%"
    )

    print(
        f"Recall:     "
        f"{validation['macro_average']['recall']}%"
    )

    print(
        f"F1 Score:   "
        f"{validation['macro_average']['f1_score']}%"
    )

    failed = [
        result
        for result in validation["results"]
        if not result["success"]
    ]

    if failed:

        print("\n========================================")
        print("UNAVAILABLE / FAILED STOCKS")
        print("========================================")

        for result in failed:

            print(
                f"{result['symbol']} "
                f"({result['sector']}): "
                f"{result['error']}"
            )