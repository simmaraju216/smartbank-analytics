
import pandas as pd
import pytest

from src.main import run_pipeline
from src.monitoring.run_tracker import RunTracker


# ==================================================
# SAMPLE BANKING DATA
# ==================================================

def create_sample_datasets():

    customers = pd.DataFrame({
        "customer_id": ["CUS001", "CUS002"],
        "customer_name": ["Raju", "Kiran"],
        "email": ["raju@example.com", "kiran@example.com"],
        "city": ["Srikakulam", "Vizag"],
        "state": ["Andhra Pradesh", "Andhra Pradesh"]
    })

    branches = pd.DataFrame({
        "branch_id": ["BR001"],
        "branch_name": ["Main Branch"],
        "city": ["Srikakulam"],
        "state": ["Andhra Pradesh"]
    })

    accounts = pd.DataFrame({
        "account_id": ["ACC001", "ACC002"],
        "customer_id": ["CUS001", "CUS002"],
        "branch_id": ["BR001", "BR001"],
        "account_type": ["SAVINGS", "CURRENT"],
        "balance": [10000.0, 20000.0]
    })

    merchants = pd.DataFrame({
        "merchant_id": ["MER001"],
        "merchant_name": ["Test Store"],
        "category": ["RETAIL"]
    })

    cards = pd.DataFrame({
        "card_id": ["CARD001"],
        "customer_id": ["CUS001"],
        "card_type": ["DEBIT"],
        "card_status": ["ACTIVE"]
    })

    transactions = pd.DataFrame({
        "transaction_id": ["TXN001", "TXN002"],
        "account_id": ["ACC001", "ACC002"],
        "merchant_id": [None, "MER001"],
        "card_id": [None, "CARD001"],
        "transaction_type": ["UPI", "DEBIT_CARD"],
        "transaction_amount": [500.0, 1000.0],
        "transaction_status": ["SUCCESS", "PENDING"],
        "transaction_timestamp": [
            "2026-10-30T10:00:00",
            "2026-10-30T11:00:00"
        ]
    })

    fraud_alerts = pd.DataFrame({
        "alert_id": ["ALT001"],
        "transaction_id": ["TXN001"],
        "alert_type": ["HIGH_AMOUNT"],
        "risk_score": [0.85]
    })

    return {
        "customers": customers,
        "branches": branches,
        "accounts": accounts,
        "merchants": merchants,
        "cards": cards,
        "transactions": transactions,
        "fraud_alerts": fraud_alerts
    }


# ==================================================
# TEST HELPERS
# ==================================================

def create_tracker(tmp_path):

    return RunTracker(
        log_dir=str(tmp_path / "logs")
    )


def execute_pipeline(datasets, tmp_path):

    tracker = create_tracker(tmp_path)

    result = run_pipeline(
        datasets=datasets,
        tracker=tracker,
        output_dir=str(tmp_path / "data")
    )

    return result, tracker


# ==================================================
# TEST 1: SUCCESSFUL PIPELINE
# ==================================================

def test_pipeline_success(tmp_path):

    datasets = create_sample_datasets()

    result, tracker = execute_pipeline(
        datasets,
        tmp_path
    )

    assert result["status"] == "SUCCESS"

    assert len(result["processed"]["transactions"]) == 2

    assert len(result["rejected"]["transactions"]) == 0

    # Total input:
    # 2 customers + 1 branch + 2 accounts
    # + 1 merchant + 1 card + 2 transactions
    # + 1 fraud alert = 10 records.

    assert result["metrics"]["input_records"] == 10

    assert (
        result["metrics"]["input_records"]
        ==
        result["metrics"]["output_records"]
        + result["metrics"]["rejected_records"]
    )

    assert result["metrics"]["status"] == "SUCCESS"


# ==================================================
# TEST 2: NEGATIVE TRANSACTION AMOUNT
# ==================================================

def test_pipeline_rejects_negative_transaction(tmp_path):

    datasets = create_sample_datasets()

    datasets["transactions"].loc[
        0, "transaction_amount"
    ] = -500.0

    result, tracker = execute_pipeline(
        datasets,
        tmp_path
    )

    assert len(result["processed"]["transactions"]) == 1

    assert len(result["rejected"]["transactions"]) == 1

    reason = result["rejected"]["transactions"][
        "rejection_reason"
    ].iloc[0]

    assert "NON_POSITIVE_TRANSACTION_AMOUNT" in reason

    assert (
        result["metrics"]["input_records"]
        ==
        result["metrics"]["output_records"]
        + result["metrics"]["rejected_records"]
    )


# ==================================================
# TEST 3: DUPLICATE TRANSACTION
# ==================================================

def test_pipeline_rejects_duplicate_transaction(tmp_path):

    datasets = create_sample_datasets()

    duplicate = datasets["transactions"].iloc[[0]].copy()

    datasets["transactions"] = pd.concat(
        [
            datasets["transactions"],
            duplicate
        ],
        ignore_index=True
    )

    result, tracker = execute_pipeline(
        datasets,
        tmp_path
    )

    assert len(result["processed"]["transactions"]) == 2

    assert len(result["rejected"]["transactions"]) == 1

    reason = result["rejected"]["transactions"][
        "rejection_reason"
    ].iloc[0]

    assert reason == "DUPLICATE_TRANSACTION_ID"


# ==================================================
# TEST 4: SAVE PARQUET OUTPUT
# ==================================================

def test_pipeline_saves_parquet_outputs(tmp_path):

    datasets = create_sample_datasets()

    result, tracker = execute_pipeline(
        datasets,
        tmp_path
    )

    processed_file = (
        tmp_path
        / "data"
        / tracker.run_id
        / "processed"
        / "transactions.parquet"
    )

    assert processed_file.exists()

    saved_df = pd.read_parquet(processed_file)

    assert len(saved_df) == 2


# ==================================================
# TEST 5: INVALID ACCOUNT REFERENCE
# ==================================================

def test_pipeline_rejects_invalid_account_reference(tmp_path):

    datasets = create_sample_datasets()

    datasets["transactions"].loc[
        0, "account_id"
    ] = "ACC999"

    result, tracker = execute_pipeline(
        datasets,
        tmp_path
    )

    assert len(result["processed"]["transactions"]) == 1

    assert len(result["rejected"]["transactions"]) == 1

    reason = result["rejected"]["transactions"][
        "rejection_reason"
    ].iloc[0]

    assert "INVALID_ACCOUNT_REFERENCE" in reason


# ==================================================
# TEST 6: INVALID FRAUD ALERT REFERENCE
# ==================================================

def test_pipeline_rejects_invalid_fraud_alert(tmp_path):

    datasets = create_sample_datasets()

    datasets["fraud_alerts"].loc[
        0, "transaction_id"
    ] = "TXN999"

    result, tracker = execute_pipeline(
        datasets,
        tmp_path
    )

    assert len(result["processed"]["fraud_alerts"]) == 0

    assert len(result["rejected"]["fraud_alerts"]) == 1

    reason = result["rejected"]["fraud_alerts"][
        "rejection_reason"
    ].iloc[0]

    assert "INVALID_TRANSACTION_REFERENCE" in reason


# ==================================================
# TEST 7: EMPTY TRANSACTION DATASET
# ==================================================

def test_pipeline_with_empty_transactions(tmp_path):

    datasets = create_sample_datasets()

    datasets["transactions"] = (
        datasets["transactions"].iloc[0:0].copy()
    )

    # There are no transactions, so the alert must
    # also be removed for this valid empty-data test.
    datasets["fraud_alerts"] = (
        datasets["fraud_alerts"].iloc[0:0].copy()
    )

    result, tracker = execute_pipeline(
        datasets,
        tmp_path
    )

    assert result["status"] == "SUCCESS"

    assert len(result["processed"]["transactions"]) == 0

    assert len(result["processed"]["fraud_alerts"]) == 0


# ==================================================
# TEST 8: RECORD COUNT RECONCILIATION
# ==================================================

def test_pipeline_record_reconciliation(tmp_path):

    datasets = create_sample_datasets()

    datasets["transactions"].loc[
        0, "transaction_amount"
    ] = -100.0

    result, tracker = execute_pipeline(
        datasets,
        tmp_path
    )

    input_count = result["metrics"]["input_records"]

    output_count = result["metrics"]["output_records"]

    rejected_count = result["metrics"]["rejected_records"]

    assert input_count == output_count + rejected_count


# ==================================================
# TEST 9: REQUIRED METADATA
# ==================================================

def test_pipeline_run_metadata(tmp_path):

    datasets = create_sample_datasets()

    result, tracker = execute_pipeline(
        datasets,
        tmp_path
    )

    assert result["metrics"]["run_id"] == tracker.run_id

    assert result["metrics"]["start_time"] is not None

    assert result["metrics"]["end_time"] is not None

    assert result["metrics"]["duration_seconds"] >= 0

# ==================================================
# TEST 10: PIPELINE FAILURE HANDLING
# ==================================================

def test_pipeline_records_failure_and_error(tmp_path):

    datasets = create_sample_datasets()

    # Remove a required column to trigger schema failure.
    datasets["transactions"] = datasets["transactions"].drop(
        columns=["transaction_amount"]
    )

    tracker = create_tracker(tmp_path)

    with pytest.raises(ValueError, match="Structural schema validation failed"):
        run_pipeline(
            datasets=datasets,
            tracker=tracker,
            output_dir=str(tmp_path / "data")
        )

    # Verify failure status.
    assert tracker.metrics["status"] == "FAILED"

    # Verify error was recorded.
    assert len(tracker.metrics["errors"]) > 0

    assert any(
        "Structural schema validation failed" in error
        for error in tracker.metrics["errors"]
    )

    # Verify execution timestamps.
    assert tracker.metrics["start_time"] is not None
    assert tracker.metrics["end_time"] is not None
    assert tracker.metrics["duration_seconds"] >= 0

    # Verify failure report was saved.
    report_file = (
        tmp_path / "logs" / f"{tracker.run_id}.json"
    )

    assert report_file.exists()

# ==================================================
# TEST 11: CLEANUP AFTER OUTPUT WRITE FAILURE
# ==================================================

def test_pipeline_cleans_temporary_output_after_write_failure(
    tmp_path,
    monkeypatch
):
    import src.main as pipeline_module

    datasets = create_sample_datasets()
    tracker = create_tracker(tmp_path)

    original_to_parquet = pd.DataFrame.to_parquet
    call_count = {"value": 0}

    def failing_to_parquet(self, *args, **kwargs):
        call_count["value"] += 1

        # Allow the first write, then simulate a disk/write failure.
        if call_count["value"] == 2:
            raise OSError("Simulated Parquet write failure")

        return original_to_parquet(self, *args, **kwargs)

    monkeypatch.setattr(
        pd.DataFrame,
        "to_parquet",
        failing_to_parquet
    )

    with pytest.raises(
        OSError,
        match="Simulated Parquet write failure"
    ):
        run_pipeline(
            datasets=datasets,
            tracker=tracker,
            output_dir=str(tmp_path / "data")
        )

    # Run must be marked as failed.
    assert tracker.metrics["status"] == "FAILED"

    # Error must be recorded.
    assert any(
        "Simulated Parquet write failure" in error
        for error in tracker.metrics["errors"]
    )

    # Final output directory must not exist.
    final_output = (
        tmp_path / "data" / tracker.run_id
    )
    assert not final_output.exists()

    # Temporary output directories must be removed.
    temporary_directories = list(
        (tmp_path / "data").glob(
            f".{tracker.run_id}_tmp_*"
        )
    )

    assert temporary_directories == []

# ==================================================
# TEST 12: TRANSACTION REJECTION TRACEABILITY
# ==================================================

def test_pipeline_rejection_preserves_transaction_metadata(tmp_path):

    datasets = create_sample_datasets()

    datasets["transactions"]["source_file"] = "transactions.csv"
    datasets["transactions"]["run_id"] = "RUN_TRACE001"
    datasets["transactions"]["ingested_at"] = (
        "2026-10-30T10:00:00+00:00"
    )

    datasets["transactions"].loc[0, "transaction_amount"] = -500

    result, tracker = execute_pipeline(datasets, tmp_path)

    rejected = result["rejected"]["transactions"]

    assert len(rejected) == 1
    assert rejected.iloc[0]["source_file"] == "transactions.csv"
    assert rejected.iloc[0]["run_id"] == "RUN_TRACE001"
    assert rejected.iloc[0]["ingested_at"] == (
        "2026-10-30T10:00:00+00:00"
    )
    assert "rejection_reason" in rejected.columns


# ==================================================
# TEST 13: FRAUD ALERT REJECTION TRACEABILITY
# ==================================================

def test_pipeline_rejection_preserves_fraud_alert_metadata(tmp_path):

    datasets = create_sample_datasets()

    datasets["fraud_alerts"]["source_file"] = "fraud_alerts.csv"
    datasets["fraud_alerts"]["run_id"] = "RUN_TRACE002"
    datasets["fraud_alerts"]["ingested_at"] = (
        "2026-10-30T10:00:00+00:00"
    )

    datasets["fraud_alerts"].loc[0, "risk_score"] = 1.5

    result, tracker = execute_pipeline(datasets, tmp_path)

    rejected = result["rejected"]["fraud_alerts"]

    assert len(rejected) == 1
    assert rejected.iloc[0]["source_file"] == "fraud_alerts.csv"
    assert rejected.iloc[0]["run_id"] == "RUN_TRACE002"
    assert rejected.iloc[0]["ingested_at"] == (
        "2026-10-30T10:00:00+00:00"
    )
    assert "rejection_reason" in rejected.columns
