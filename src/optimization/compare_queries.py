
import duckdb
import pandas as pd

from pathlib import Path


# ==================================================
# CONFIGURATION
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "data" / "smartbank.duckdb"

BASELINE_DIR = PROJECT_ROOT / "sql" / "baseline"

OPTIMIZED_DIR = PROJECT_ROOT / "sql" / "optimized"


QUERIES = {
    "Q1_monthly_transactions": "q1_monthly_transactions.sql",
    "Q2_customer_analysis": "q2_customer_analysis.sql",
    "Q3_branch_performance": "q3_branch_performance.sql",
    "Q4_merchant_analysis": "q4_merchant_analysis.sql",
    "Q5_daily_debit_credit": "q5_daily_debit_credit.sql",
}


SORT_KEYS = {
    "Q1_monthly_transactions": [
        "transaction_month",
        "transaction_type",
        "transaction_status",
    ],
    "Q2_customer_analysis": ["customer_id"],
    "Q3_branch_performance": ["branch_id"],
    "Q4_merchant_analysis": [
        "merchant_id",
        "transaction_type",
        "transaction_status"
    ],
    
    "Q5_daily_debit_credit": [
    "transaction_date",
    "transaction_status"
    ],
}


# Normalize these columns before sorting/comparison.
DATETIME_COLUMNS = {
    "Q1_monthly_transactions": ["transaction_month"],
}


RELATIVE_TOLERANCE = 1e-9
ABSOLUTE_TOLERANCE = 1e-8


# ==================================================
# LOAD SQL QUERY
# ==================================================

def load_query(directory, filename):

    path = directory / filename

    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")

    return path.read_text(encoding="utf-8")


# ==================================================
# NORMALIZE QUERY RESULTS
# ==================================================

def normalize_datetime_columns(df, query_name):

    df = df.copy()

    columns = DATETIME_COLUMNS.get(query_name, [])

    for column in columns:

        if column in df.columns:

            df[column] = pd.to_datetime(
                df[column],
                errors="coerce",
                utc=True,
            )

            # Remove timezone information after converting
            # both results to UTC.
            df[column] = df[column].dt.tz_localize(None)

    return df


# ==================================================
# COMPARE QUERY RESULTS
# ==================================================

def compare_query_results(connection, query_name, filename):

    baseline_sql = load_query(BASELINE_DIR, filename)

    optimized_sql = load_query(OPTIMIZED_DIR, filename)

    baseline = connection.execute(baseline_sql).fetchdf()

    optimized = connection.execute(optimized_sql).fetchdf()

    print(f"\n{query_name}")
    print("-" * 60)

    print(f"Baseline rows:  {len(baseline):,}")
    print(f"Optimized rows: {len(optimized):,}")

    # --------------------------------------------------
    # CHECK COLUMN NAMES
    # --------------------------------------------------

    if list(baseline.columns) != list(optimized.columns):

        print("FAIL: Column names or column order differ.")
        print("Baseline columns:", list(baseline.columns))
        print("Optimized columns:", list(optimized.columns))

        return False

    # --------------------------------------------------
    # CHECK ROW COUNTS
    # --------------------------------------------------

    if len(baseline) != len(optimized):

        print("FAIL: Row counts differ.")

        return False

    # --------------------------------------------------
    # NORMALIZE DATETIME COLUMNS
    # --------------------------------------------------

    baseline = normalize_datetime_columns(
        baseline,
        query_name,
    )

    optimized = normalize_datetime_columns(
        optimized,
        query_name,
    )

    # --------------------------------------------------
    # SORT RESULTS USING BUSINESS KEYS
    # --------------------------------------------------

    if query_name not in SORT_KEYS:

        raise ValueError(
            f"Sorting keys not defined for {query_name}"
        )

    key_columns = SORT_KEYS[query_name]

    for column in key_columns:

        if column not in baseline.columns:

            raise ValueError(
                f"Sorting column '{column}' missing "
                f"from {query_name}"
            )

    baseline = (
        baseline
        .sort_values(
            by=key_columns,
            na_position="first",
        )
        .reset_index(drop=True)
    )

    optimized = (
        optimized
        .sort_values(
            by=key_columns,
            na_position="first",
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------
    # CHECK BUSINESS IDENTIFIERS
    # --------------------------------------------------

    for column in key_columns:

        if not baseline[column].equals(optimized[column]):

            print(f"FAIL: Business key differs: {column}")

            print("\nBaseline sample:")
            print(baseline[column].head(5).to_string(index=False))

            print("\nOptimized sample:")
            print(optimized[column].head(5).to_string(index=False))

            return False

    # --------------------------------------------------
    # CHECK NUMERIC COLUMNS
    # --------------------------------------------------

    numeric_columns = [
        column
        for column in baseline.columns
        if pd.api.types.is_numeric_dtype(baseline[column])
    ]

    try:

        for column in numeric_columns:

            pd.testing.assert_series_equal(
                baseline[column],
                optimized[column],
                check_names=False,
                check_dtype=False,
                check_exact=False,
                rtol=RELATIVE_TOLERANCE,
                atol=ABSOLUTE_TOLERANCE,
            )

    except AssertionError as error:

        print("FAIL: Numeric values differ.")
        print(error)

        return False

    # --------------------------------------------------
    # CHECK NON-NUMERIC COLUMNS
    # --------------------------------------------------

    non_numeric_columns = [
        column
        for column in baseline.columns
        if column not in numeric_columns
    ]

    try:

        pd.testing.assert_frame_equal(
            baseline[non_numeric_columns],
            optimized[non_numeric_columns],
            check_dtype=False,
            check_exact=True,
        )

    except AssertionError as error:

        print("FAIL: Non-numeric values differ.")
        print(error)

        return False

    # --------------------------------------------------
    # SUCCESS
    # --------------------------------------------------

    print("Results identical within numeric tolerance: True")
    print("PASS: Query results match.")

    return True


# ==================================================
# MAIN
# ==================================================

def main():

    if not DATABASE_PATH.exists():

        raise FileNotFoundError(
            f"DuckDB database not found: {DATABASE_PATH}"
        )

    connection = duckdb.connect(
        str(DATABASE_PATH),
        read_only=True,
    )

    print("\nSMARTBANK SQL CORRECTNESS VALIDATION")
    print("=" * 60)

    passed_count = 0
    failed_count = 0

    try:

        for query_name, filename in QUERIES.items():

            try:

                result = compare_query_results(
                    connection,
                    query_name,
                    filename,
                )

                if result:
                    passed_count += 1
                else:
                    failed_count += 1

            except Exception as error:

                print(f"\nERROR in {query_name}:")
                print(error)

                failed_count += 1

        # --------------------------------------------------
        # FINAL SUMMARY
        # --------------------------------------------------

        print("\nVALIDATION SUMMARY")
        print("=" * 60)

        print(f"Total queries: {len(QUERIES)}")
        print(f"Passed: {passed_count}")
        print(f"Failed: {failed_count}")

        if failed_count == 0:

            print("\nALL OPTIMIZED QUERIES PASSED!")

        else:

            print(
                "\nSOME OPTIMIZED QUERIES FAILED. "
                "Please investigate the differences."
            )

            raise AssertionError(
                f"{failed_count} SQL comparison(s) failed."
            )

    finally:

        connection.close()


if __name__ == "__main__":
    main()
