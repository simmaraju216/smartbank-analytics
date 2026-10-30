
import os
import json
import time
import pandas as pd

from datetime import datetime, timezone

from src.validation.business_validator import (
    validate_transactions,
    validate_fraud_alerts
)


# ==================================================
# CONFIGURATION
# ==================================================

DATA_DIR = "data/raw"
REPORT_DIR = "reports/performance"

os.makedirs(REPORT_DIR, exist_ok=True)


# ==================================================
# LOAD DATA
# ==================================================

def load_data():

    print("Loading banking datasets...")

    transactions = pd.read_csv(
        os.path.join(DATA_DIR, "transactions.csv")
    )

    accounts = pd.read_csv(
        os.path.join(DATA_DIR, "accounts.csv")
    )

    merchants = pd.read_csv(
        os.path.join(DATA_DIR, "merchants.csv")
    )

    cards = pd.read_csv(
        os.path.join(DATA_DIR, "cards.csv")
    )

    fraud_alerts = pd.read_csv(
        os.path.join(DATA_DIR, "fraud_alerts.csv")
    )

    print(f"Transactions: {len(transactions):,}")
    print(f"Accounts: {len(accounts):,}")
    print(f"Fraud alerts: {len(fraud_alerts):,}")

    return (
        transactions,
        accounts,
        merchants,
        cards,
        fraud_alerts
    )


# ==================================================
# BENCHMARK TRANSACTION VALIDATION
# ==================================================

def benchmark_transactions(
    transactions,
    accounts,
    merchants,
    cards
):

    print("\nBenchmarking transaction validation...")

    start = time.perf_counter()

    valid, rejected = validate_transactions(
        transactions,
        accounts,
        merchants,
        cards
    )

    elapsed = time.perf_counter() - start

    total_records = len(transactions)

    throughput = (
        total_records / elapsed
        if elapsed > 0 else 0
    )

    result = {
        "dataset": "transactions",
        "total_records": total_records,
        "valid_records": len(valid),
        "rejected_records": len(rejected),
        "execution_time_seconds": round(elapsed, 4),
        "records_per_second": round(throughput, 2)
    }

    print("\nTRANSACTION VALIDATION RESULTS")
    print("-" * 50)

    for key, value in result.items():
        print(f"{key}: {value}")

    return result


# ==================================================
# BENCHMARK FRAUD ALERT VALIDATION
# ==================================================

def benchmark_fraud_alerts(
    fraud_alerts,
    transactions
):

    print("\nBenchmarking fraud alert validation...")

    start = time.perf_counter()

    valid, rejected = validate_fraud_alerts(
        fraud_alerts,
        transactions
    )

    elapsed = time.perf_counter() - start

    total_records = len(fraud_alerts)

    throughput = (
        total_records / elapsed
        if elapsed > 0 else 0
    )

    result = {
        "dataset": "fraud_alerts",
        "total_records": total_records,
        "valid_records": len(valid),
        "rejected_records": len(rejected),
        "execution_time_seconds": round(elapsed, 4),
        "records_per_second": round(throughput, 2)
    }

    print("\nFRAUD ALERT VALIDATION RESULTS")
    print("-" * 50)

    for key, value in result.items():
        print(f"{key}: {value}")

    return result


# ==================================================
# SAVE BENCHMARK REPORT
# ==================================================

def save_report(results):

    report = {
        "benchmark_name": "SmartBank Validation Benchmark",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "results": results
    }

    file_path = os.path.join(
        REPORT_DIR,
        "validation_benchmark.json"
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print(f"\nBenchmark report saved: {file_path}")


# ==================================================
# MAIN
# ==================================================

def main():

    (
        transactions,
        accounts,
        merchants,
        cards,
        fraud_alerts
    ) = load_data()

    transaction_result = benchmark_transactions(
        transactions,
        accounts,
        merchants,
        cards
    )

    fraud_result = benchmark_fraud_alerts(
        fraud_alerts,
        transactions
    )

    save_report([
        transaction_result,
        fraud_result
    ])

    print("\nBENCHMARK COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
