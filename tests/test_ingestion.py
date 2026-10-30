
import shutil
from pathlib import Path

import pandas as pd
import pytest

from src.ingestion.ingest_data import REQUIRED_FILES, ingest_data
from src.monitoring.run_tracker import RunTracker


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_INPUT_DIR = PROJECT_ROOT / "sample_data" / "input"


def copy_sample_data(tmp_path):
    """Copy the sample CSV files into an isolated temporary directory."""
    destination = tmp_path / "input"

    shutil.copytree(SAMPLE_INPUT_DIR, destination)

    return destination


def create_tracker(tmp_path):
    """Create a tracker with logs stored in the temporary test directory."""
    return RunTracker(log_dir=tmp_path / "logs")


def test_successful_ingestion_and_metadata(tmp_path):
    input_dir = copy_sample_data(tmp_path)
    tracker = create_tracker(tmp_path)

    datasets, returned_tracker = ingest_data(
        input_dir=str(input_dir),
        tracker=tracker
    )

    # The same tracker must be returned.
    assert returned_tracker is tracker

    # All required datasets must be loaded.
    expected_names = {
        file_name.removesuffix(".csv")
        for file_name in REQUIRED_FILES
    }

    assert set(datasets.keys()) == expected_names

    # Every dataset must contain ingestion metadata.
    for file_name in REQUIRED_FILES:
        dataset_name = file_name.removesuffix(".csv")
        df = datasets[dataset_name]

        assert "source_file" in df.columns
        assert "run_id" in df.columns
        assert "ingested_at" in df.columns

        assert (df["source_file"] == file_name).all()
        assert (df["run_id"] == tracker.run_id).all()

        timestamps = pd.to_datetime(
            df["ingested_at"],
            utc=True,
            errors="coerce"
        )

        assert timestamps.notna().all()

    # Input count must equal the total number of ingested rows.
    expected_count = sum(len(df) for df in datasets.values())

    assert tracker.metrics["input_records"] == expected_count


def test_missing_input_directory_raises_error(tmp_path):
    missing_dir = tmp_path / "does_not_exist"
    tracker = create_tracker(tmp_path)

    with pytest.raises(
        FileNotFoundError,
        match="Input directory not found"
    ):
        ingest_data(
            input_dir=str(missing_dir),
            tracker=tracker
        )

    assert tracker.metrics["status"] == "RUNNING"
    assert len(tracker.metrics["errors"]) == 1


def test_missing_required_csv_file_raises_error(tmp_path):
    input_dir = copy_sample_data(tmp_path)
    tracker = create_tracker(tmp_path)

    missing_file = input_dir / "fraud_alerts.csv"
    missing_file.unlink()

    with pytest.raises(
        FileNotFoundError,
        match="Required file not found"
    ):
        ingest_data(
            input_dir=str(input_dir),
            tracker=tracker
        )

    assert len(tracker.metrics["errors"]) == 1


def test_malformed_csv_raises_value_error(tmp_path):
    input_dir = copy_sample_data(tmp_path)
    tracker = create_tracker(tmp_path)

    transactions_file = input_dir / "transactions.csv"

    # Create an invalid CSV with an unterminated quoted field.
    transactions_file.write_text(
        'transaction_id,account_id\n'
        '1,100\n'
        '2,"unterminated\n',
        encoding="utf-8"
    )

    with pytest.raises(
        ValueError,
        match="Unable to read transactions.csv"
    ):
        ingest_data(
            input_dir=str(input_dir),
            tracker=tracker
        )

    assert len(tracker.metrics["errors"]) == 1


def test_empty_transactions_csv_is_ingested(tmp_path):
    input_dir = copy_sample_data(tmp_path)
    tracker = create_tracker(tmp_path)

    transactions_file = input_dir / "transactions.csv"

    # Keep the original column headers but remove all data rows.
    original_df = pd.read_csv(transactions_file)

    original_df.head(0).to_csv(
        transactions_file,
        index=False
    )

    datasets, returned_tracker = ingest_data(
        input_dir=str(input_dir),
        tracker=tracker
    )

    transactions = datasets["transactions"]

    assert returned_tracker is tracker
    assert transactions.empty

    # Empty datasets must still have ingestion metadata columns.
    assert "source_file" in transactions.columns
    assert "run_id" in transactions.columns
    assert "ingested_at" in transactions.columns

    assert (transactions["source_file"] == "transactions.csv").all()

    expected_count = sum(len(df) for df in datasets.values())

    assert tracker.metrics["input_records"] == expected_count
