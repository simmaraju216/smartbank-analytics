
import time
import statistics
import pandas as pd
import duckdb

from pathlib import Path
from datetime import datetime, timezone


# ==================================================
# CONFIGURATION
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "data" / "smartbank.duckdb"

BASELINE_DIR = PROJECT_ROOT / "sql" / "baseline"

REPORT_DIR = PROJECT_ROOT / "reports" / "performance"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

REPETITIONS = 3

QUERIES = {
    "Q1_monthly_transactions": "q1_monthly_transactions.sql",
    "Q2_customer_analysis": "q2_customer_analysis.sql",
    "Q3_branch_performance": "q3_branch_performance.sql",
    "Q4_merchant_analysis": "q4_merchant_analysis.sql",
    "Q5_daily_debit_credit": "q5_daily_debit_credit.sql"
}


# ==================================================
# LOAD SQL QUERY
# ==================================================

def load_query(file_name):

    file_path = BASELINE_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"SQL query not found: {file_path}"
        )

    return file_path.read_text(encoding="utf-8")


# ==================================================
# EXECUTE AND MEASURE QUERY
# ==================================================

def execute_query(connection, query_name, sql):

    execution_times = []
    result_rows = None

    # Warm-up execution.
    connection.execute(sql).fetchall()

    # Measure repeated executions.
    for run_number in range(1, REPETITIONS + 1):

        start = time.perf_counter()

        result = connection.execute(sql).fetchall()

        elapsed = time.perf_counter() - start

        execution_times.append(elapsed)

        result_rows = len(result)

        print(
            f"  Run {run_number}: {elapsed:.6f} seconds"
        )

    median_time = statistics.median(execution_times)

    return {
        "query_name": query_name,
        "result_rows": result_rows,
        "repetitions": REPETITIONS,
        "execution_times_seconds": [
            round(value, 6)
            for value in execution_times
        ],
        "median_execution_time_seconds": round(
            median_time, 6
        ),
        "average_execution_time_seconds": round(
            statistics.mean(execution_times), 6
        )
    }


# ==================================================
# SAVE EXPLAIN ANALYZE PLANS
# ==================================================

def save_execution_plan(connection, query_name, sql):

    result = connection.execute(
        "EXPLAIN ANALYZE " + sql
    ).fetchall()

    plan_file = REPORT_DIR / f"{query_name}_plan.txt"

    with open(
        plan_file,
        "w",
        encoding="utf-8"
    ) as file:

        for row in result:
            file.write(str(row) + "\n")

    print(f"  Execution plan saved: {plan_file.name}")


# ==================================================
# RUN BASELINE BENCHMARK
# ==================================================

def run_baseline_benchmark():

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB database not found: {DATABASE_PATH}"
        )

    connection = duckdb.connect(
        str(DATABASE_PATH),
        read_only=True
    )

    benchmark_results = []

    print("\nSMARTBANK BASELINE SQL BENCHMARK")
    print("=" * 65)

    print(f"Database: {DATABASE_PATH}")
    print(f"Repetitions: {REPETITIONS}")

    try:

        for query_name, file_name in QUERIES.items():

            print(f"\nExecuting {query_name}")

            sql = load_query(file_name)

            result = execute_query(
                connection,
                query_name,
                sql
            )

            benchmark_results.append(result)

            save_execution_plan(
                connection,
                query_name,
                sql
            )

            print(
                f"  Result rows: {result['result_rows']:,}"
            )

            print(
                "  Median time: "
                f"{result['median_execution_time_seconds']:.6f} seconds"
            )

        # Create summary report.
        summary = pd.DataFrame([
            {
                "query_name": result["query_name"],
                "result_rows": result["result_rows"],
                "repetitions": result["repetitions"],
                "median_execution_time_seconds":
                    result["median_execution_time_seconds"],
                "average_execution_time_seconds":
                    result["average_execution_time_seconds"]
            }
            for result in benchmark_results
        ])

        summary["created_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        report_path = (
            REPORT_DIR / "baseline_results.csv"
        )

        summary.to_csv(
            report_path,
            index=False
        )

        print("\nBASELINE BENCHMARK SUMMARY")
        print("=" * 65)

        print(
            summary[
                [
                    "query_name",
                    "result_rows",
                    "median_execution_time_seconds"
                ]
            ].to_string(index=False)
        )

        print(f"\nReport saved: {report_path}")

        print("\nBASELINE BENCHMARK COMPLETED")

    finally:

        connection.close()


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    run_baseline_benchmark()
