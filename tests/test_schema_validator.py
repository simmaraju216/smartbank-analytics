
import pandas as pd

from src.validation.schema_validator import validate_schema


def valid_transaction_data():
    return pd.DataFrame({
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


def test_valid_transaction_schema():
    result = validate_schema(
        "transactions",
        valid_transaction_data()
    )

    assert result["valid"] is True
    assert result["errors"] == []
    assert result["warnings"] == []


def test_missing_transaction_column():
    df = valid_transaction_data()
    df = df.drop(columns=["transaction_amount"])

    result = validate_schema("transactions", df)

    assert result["valid"] is False
    assert any(
        "Missing columns" in error
        for error in result["errors"]
    )


def test_multiple_missing_columns():
    df = valid_transaction_data()
    df = df.drop(columns=[
        "transaction_amount",
        "transaction_status"
    ])

    result = validate_schema("transactions", df)

    assert result["valid"] is False

    missing_error = next(
        error for error in result["errors"]
        if "Missing columns" in error
    )

    assert "transaction_amount" in missing_error
    assert "transaction_status" in missing_error


def test_empty_dataset():
    df = valid_transaction_data().iloc[0:0]

    result = validate_schema("transactions", df)

    assert result["valid"] is True

    assert any(
        "Dataset contains no records" in warning
        for warning in result["warnings"]
    )


def test_duplicate_transaction_id():
    df = valid_transaction_data()
    df.loc[1, "transaction_id"] = "TXN001"

    result = validate_schema("transactions", df)

    assert result["valid"] is True

    assert any(
        "duplicate values" in warning
        for warning in result["warnings"]
    )


def test_null_account_id():
    df = valid_transaction_data()
    df.loc[0, "account_id"] = None

    result = validate_schema("transactions", df)

    assert result["valid"] is True

    assert any(
        "account_id contains" in warning
        for warning in result["warnings"]
    )


def test_unexpected_column():
    df = valid_transaction_data()
    df["unexpected_column"] = "test"

    result = validate_schema("transactions", df)

    assert result["valid"] is False

    assert any(
        "Unexpected columns" in error
        for error in result["errors"]
    )


def test_invalid_numeric_type():
    df = valid_transaction_data()
    df["transaction_amount"] = [
        "five hundred",
        "one thousand"
    ]

    result = validate_schema("transactions", df)

    assert result["valid"] is False

    assert any(
        "numeric data type" in error
        for error in result["errors"]
    )


def test_ingestion_metadata_columns_are_allowed():
    df = valid_transaction_data()

    df["source_file"] = "transactions.csv"
    df["run_id"] = "RUN_TEST_001"
    df["ingested_at"] = "2026-10-30T10:00:00+00:00"

    result = validate_schema("transactions", df)

    assert result["valid"] is True
    assert result["errors"] == []
    assert result["warnings"] == []


def test_unknown_dataset_name():
    df = valid_transaction_data()

    result = validate_schema(
        "unknown_dataset",
        df
    )

    assert result["valid"] is False
    assert any(
        "Unknown dataset" in error
        for error in result["errors"]
    )


def test_additional_schema_column_is_rejected():
    df = valid_transaction_data()

    # Simulate an unexpected source schema change.
    df["new_source_column"] = "new_value"

    result = validate_schema("transactions", df)

    assert result["valid"] is False
    assert any(
        "Unexpected columns" in error
        for error in result["errors"]
    )
