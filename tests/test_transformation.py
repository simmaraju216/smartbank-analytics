import pandas as pd

from src.transformation.transform_data import (
    transform_transactions,
    transform_customers
)


def create_transactions():
    return pd.DataFrame({
        "transaction_id": ["TXN001", "TXN002", "TXN003"],
        "account_id": ["ACC001", "ACC002", "ACC003"],
        "transaction_type": [
            "UPI",
            "CASH_DEPOSIT",
            "ATM_WITHDRAWAL"
        ],
        "transaction_amount": [500, 1000, 750],
        "transaction_timestamp": [
            "2026-10-30T10:00:00",
            "2026-10-30T11:00:00",
            "2026-10-30T12:00:00"
        ]
    })


def test_transaction_date_columns():
    df = create_transactions()

    result = transform_transactions(df)

    assert "transaction_date" in result.columns
    assert "transaction_month" in result.columns
    assert "transaction_year" in result.columns

    assert result["transaction_month"].tolist() == [10, 10, 10]
    assert result["transaction_year"].tolist() == [2026, 2026, 2026]


def test_debit_and_credit_amounts():
    df = create_transactions()

    result = transform_transactions(df)

    assert result["debit_amount"].tolist() == [500, 0, 750]
    assert result["credit_amount"].tolist() == [0, 1000, 0]


def test_timestamp_conversion():
    df = create_transactions()

    result = transform_transactions(df)

    assert isinstance(
        result["transaction_timestamp"].dtype,
        pd.DatetimeTZDtype
    )


def test_original_dataframe_is_not_modified():
    df = create_transactions()
    original_df = df.copy()

    transform_transactions(df)

    pd.testing.assert_frame_equal(df, original_df)


def test_empty_transactions():
    df = create_transactions().iloc[0:0]

    result = transform_transactions(df)

    assert result.empty


def test_customer_standardization():
    df = pd.DataFrame({
        "customer_id": ["CUS001"],
        "email": ["  RAJU@GMAIL.COM  "],
        "city": ["  srikakulam  "],
        "state": ["  andhra pradesh  "]
    })

    result = transform_customers(df)

    assert result.loc[0, "email"] == "raju@gmail.com"
    assert result.loc[0, "city"] == "Srikakulam"
    assert result.loc[0, "state"] == "Andhra Pradesh"