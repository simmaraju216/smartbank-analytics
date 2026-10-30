
import os
import pandas as pd

from datetime import datetime, timezone

from src.monitoring.run_tracker import RunTracker


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

RAW_DATA_DIR = "data/raw"

REQUIRED_FILES = [
    "customers.csv",
    "branches.csv",
    "accounts.csv",
    "merchants.csv",
    "cards.csv",
    "transactions.csv",
    "fraud_alerts.csv",
]


# --------------------------------------------------
# DATA INGESTION
# --------------------------------------------------

def ingest_data(input_dir=None, tracker=None):
    """
    Read all required banking CSV files.

    Responsibilities:
    1. Check that the input directory exists.
    2. Check that all required CSV files exist.
    3. Read CSV files into Pandas DataFrames.
    4. Attach source_file, run_id and ingested_at.
    5. Record input row counts.
    6. Return datasets and the shared run tracker.

    If a tracker is supplied by the main pipeline,
    reuse it so the complete pipeline has one run ID.

    If no tracker is supplied, create one locally.
    """

    raw_data_dir = input_dir or RAW_DATA_DIR

    # Track whether this function created the tracker.
    owns_tracker = tracker is None

    if tracker is None:
        tracker = RunTracker()

    datasets = {}

    print("\nSMARTBANK DATA INGESTION")
    print("=" * 60)
    print(f"Run ID: {tracker.run_id}")
    print(f"Input directory: {raw_data_dir}")

    try:

        # ------------------------------------------
        # 1. CHECK INPUT DIRECTORY
        # ------------------------------------------

        if not os.path.isdir(raw_data_dir):
            raise FileNotFoundError(
                f"Input directory not found: {raw_data_dir}"
            )

        # ------------------------------------------
        # 2. READ REQUIRED CSV FILES
        # ------------------------------------------

        for file_name in REQUIRED_FILES:

            file_path = os.path.join(
                raw_data_dir,
                file_name
            )

            if not os.path.isfile(file_path):
                raise FileNotFoundError(
                    f"Required file not found: {file_path}"
                )

            print(f"\nReading: {file_name}")

            try:
                df = pd.read_csv(
                    file_path,
                    on_bad_lines="error"
                )

            except Exception as read_error:
                raise ValueError(
                    f"Unable to read {file_name}: {read_error}"
                ) from read_error

            # --------------------------------------
            # 3. ADD INGESTION METADATA
            # --------------------------------------

            df["source_file"] = file_name
            df["run_id"] = tracker.run_id
            df["ingested_at"] = datetime.now(
                timezone.utc
            ).isoformat()

            # --------------------------------------
            # 4. STORE DATASET
            # --------------------------------------

            dataset_name = file_name.removesuffix(".csv")

            datasets[dataset_name] = df

            # Record the number of input records.
            tracker.add_input_records(len(df))

            print(
                f"Records loaded: {len(df)}"
            )

        # ------------------------------------------
        # 5. INGESTION SUMMARY
        # ------------------------------------------

        print("\n" + "=" * 60)
        print("DATA INGESTION COMPLETED")

        print(
            "Total input records:",
            tracker.metrics["input_records"]
        )

        # Do not finish the shared tracker here.
        # The main pipeline marks SUCCESS only after
        # validation, transformation and publishing.

        return datasets, tracker

    except Exception as error:

        tracker.add_error(error)

        # If this function created its own tracker,
        # it is responsible for recording the failure.
        # Otherwise, the main pipeline handles it.
        if owns_tracker:
            tracker.finish("FAILED")

        print("\nINGESTION FAILED:", error)

        raise


# --------------------------------------------------
# PROGRAM ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":

    # Standalone ingestion uses one tracker.
    standalone_tracker = RunTracker()

    try:

        datasets, tracker = ingest_data(
            tracker=standalone_tracker
        )

        print("\nLOADED DATASETS")
        print("-" * 40)

        for name, df in datasets.items():
            print(
                f"{name}: {len(df)} records"
            )

        tracker.finish("SUCCESS")

        print(
            "\nStandalone ingestion completed successfully."
        )

    except Exception as error:

        # ingest_data has already added the error.
        # Finish the standalone run as FAILED.
        standalone_tracker.finish("FAILED")

        print(
            "\nStandalone ingestion failed:",
            error
        )

        raise
