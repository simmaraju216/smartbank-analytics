
import pandas as pd
import pytest

from src.validation.duplicate_handler import handle_duplicates


def create_sample_data():
    return pd.DataFrame({
        "transaction_id": [
            "TXN001",
            "TXN002",
            "TXN001",
            "TXN003",
            "TXN002"
        ],
        "account_id": [
            "ACC001",
            "ACC002",
            "ACC001",
            "ACC003",
            "ACC002"
        ],
        "transaction_amount": [
            500,
            1000,
            500,
            750,
            1000
        ]
    })


def test_remove_duplicate_transactions():
    df = create_sample_data()

    valid_df, rejected_df = handle_duplicates(
        df,
        "transactions",
        "transaction_id"
    )

    assert len(valid_df) == 3
    assert len(rejected_df) == 2
    assert valid_df["transaction_id"].is_unique


def test_duplicate_rejection_reason():
    df = create_sample_data()

    valid_df, rejected_df = handle_duplicates(
        df,
        "transactions",
        "transaction_id"
    )

    assert (
        rejected_df["rejection_reason"]
        == "DUPLICATE_TRANSACTION_ID"
    ).all()


def test_no_duplicates():
    df = pd.DataFrame({
        "transaction_id": ["TXN001", "TXN002"],
        "transaction_amount": [500, 1000]
    })

    valid_df, rejected_df = handle_duplicates(
        df,
        "transactions",
        "transaction_id"
    )

    assert len(valid_df) == 2
    assert len(rejected_df) == 0


def test_all_records_are_duplicates():
    df = pd.DataFrame({
        "transaction_id": [
            "TXN001",
            "TXN001",
            "TXN001"
        ],
        "transaction_amount": [
            500,
            500,
            500
        ]
    })

    valid_df, rejected_df = handle_duplicates(
        df,
        "transactions",
        "transaction_id"
    )

    assert len(valid_df) == 1
    assert len(rejected_df) == 2


def test_missing_primary_key_column():
    df = pd.DataFrame({
        "account_id": ["ACC001", "ACC002"]
    })

    with pytest.raises(
        ValueError,
        match="Primary key"
    ):
        handle_duplicates(
            df,
            "transactions",
            "transaction_id"
        )


def test_empty_dataframe():
    df = pd.DataFrame({
        "transaction_id": pd.Series(dtype="object"),
        "transaction_amount": pd.Series(dtype="float64")
    })

    valid_df, rejected_df = handle_duplicates(
        df,
        "transactions",
        "transaction_id"
    )

    assert len(valid_df) == 0
    assert len(rejected_df) == 0


def test_first_occurrence_is_preserved():
    df = create_sample_data()

    valid_df, rejected_df = handle_duplicates(
        df,
        "transactions",
        "transaction_id"
    )

    first_txn = valid_df[
        valid_df["transaction_id"] == "TXN001"
    ]

    assert len(first_txn) == 1
    assert first_txn.iloc[0]["transaction_amount"] == 500


def test_duplicate_rejection_preserves_metadata():
    df = create_sample_data()

    df["run_id"] = "RUN_TEST_001"
    df["source_file"] = "transactions.csv"

    valid_df, rejected_df = handle_duplicates(
        df,
        "transactions",
        "transaction_id"
    )

    assert "run_id" in rejected_df.columns
    assert "source_file" in rejected_df.columns

    assert (
        rejected_df["run_id"] == "RUN_TEST_001"
    ).all()

    assert (
        rejected_df["source_file"] == "transactions.csv"
    ).all()


def test_null_primary_keys_are_not_treated_as_duplicates():
    df = pd.DataFrame({
        "transaction_id": [
            None,
            None,
            "TXN001"
        ],
        "transaction_amount": [
            100,
            200,
            300
        ]
    })

    valid_df, rejected_df = handle_duplicates(
        df,
        "transactions",
        "transaction_id"
    )

    # Null primary keys remain available for required-field validation.
    assert len(valid_df) == 3
    assert len(rejected_df) == 0

    assert valid_df["transaction_id"].isna().sum() == 2


def test_multiple_null_primary_keys_and_real_duplicates():
    df = pd.DataFrame({
        "transaction_id": [
            None,
            "TXN001",
            None,
            "TXN001",
            "TXN002"
        ],
        "transaction_amount": [
            100,
            200,
            300,
            400,
            500
        ]
    })

    valid_df, rejected_df = handle_duplicates(
        df,
        "transactions",
        "transaction_id"
    )

    assert len(valid_df) == 4
    assert len(rejected_df) == 1

    assert rejected_df.iloc[0]["transaction_id"] == "TXN001"
    assert (
        rejected_df.iloc[0]["rejection_reason"]
        == "DUPLICATE_TRANSACTION_ID"
    )
