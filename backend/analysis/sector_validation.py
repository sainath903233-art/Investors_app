from analysis.validate import run_validation


def run_sector_validation():

    validation = run_validation()

    sector_data = {}

    for result in validation["results"]:

        if not result["success"]:
            continue

        sector = result["sector"]

        if sector not in sector_data:
            sector_data[sector] = []

        sector_data[sector].append(result)


    print("\n========================================")
    print("SECTOR VALIDATION")
    print("========================================")

    for sector, stocks in sector_data.items():

        accuracy = round(
            sum(r["accuracy"] for r in stocks)
            / len(stocks),
            2
        )

        precision = round(
            sum(r["precision"] for r in stocks)
            / len(stocks),
            2
        )

        recall = round(
            sum(r["recall"] for r in stocks)
            / len(stocks),
            2
        )

        f1_score = round(
            sum(r["f1_score"] for r in stocks)
            / len(stocks),
            2
        )

        print(
            f"{sector:<22}"
            f"Accuracy={accuracy:<8}"
            f"Precision={precision:<8}"
            f"Recall={recall:<8}"
            f"F1={f1_score}"
        )


if __name__ == "__main__":
    run_sector_validation()