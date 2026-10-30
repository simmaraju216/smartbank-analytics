import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = PROJECT_ROOT / "reports" / "performance"

BASELINE_FILE = REPORT_DIR / "baseline_results.csv"
OPTIMIZED_FILE = REPORT_DIR / "optimized_results.csv"
OUTPUT_FILE = REPORT_DIR / "consolidated_performance_report.csv"


def main():

    print("\nCONSOLIDATED PERFORMANCE REPORT")
    print("=" * 75)

    if not BASELINE_FILE.exists():
        raise FileNotFoundError(f"Missing file: {BASELINE_FILE}")

    if not OPTIMIZED_FILE.exists():
        raise FileNotFoundError(f"Missing file: {OPTIMIZED_FILE}")

    baseline = pd.read_csv(BASELINE_FILE)
    optimized = pd.read_csv(OPTIMIZED_FILE)

    required = ["query_name", "median_execution_time_seconds"]

    for name, df in [("Baseline", baseline), ("Optimized", optimized)]:
        missing = set(required) - set(df.columns)
        if missing:
            raise ValueError(f"{name} report missing columns: {missing}")

    baseline = baseline[required].rename(columns={
        "median_execution_time_seconds": "baseline_time_seconds"
    })

    optimized = optimized[required].rename(columns={
        "median_execution_time_seconds": "optimized_time_seconds"
    })

    report = baseline.merge(
        optimized,
        on="query_name",
        how="inner",
        validate="one_to_one"
    )

    if report.empty:
        raise ValueError("No matching queries found.")

    report["improvement_seconds"] = (
        report["baseline_time_seconds"] - report["optimized_time_seconds"]
    )

    report["improvement_percentage"] = (
        report["improvement_seconds"] / report["baseline_time_seconds"]
    ) * 100

    report["performance_status"] = report["improvement_percentage"].apply(
        lambda value: (
            "IMPROVED" if value > 0
            else "SLOWER" if value < 0
            else "UNCHANGED"
        )
    )

    report = report.round(6)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(OUTPUT_FILE, index=False)

    print(report.to_string(index=False))
    print("\nReport saved:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
