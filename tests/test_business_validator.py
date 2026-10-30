
import pandas as pd

from src.validation.business_validator import (
    validate_transactions,
    validate_fraud_alerts
)


# ==================================================
# SAMPLE DATA
# ==================================================

def create_sample_data():

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

    accounts = pd.DataFrame({
        "account_id": ["ACC001", "ACC002"]
    })

    merchants = pd.DataFrame({
        "merchant_id": ["MER001"]
    })

    cards = pd.DataFrame({
        "card_id": ["CARD001"]
    })

    return transactions, accounts, merchants, cards


# ==================================================
# TRANSACTION TESTS
# ==================================================

def test_valid_transactions():

    transactions, accounts, merchants, cards = create_sample_data()

    valid, rejected = validate_transactions(
        transactions, accounts, merchants, cards
    )

    assert len(valid) == 2
    assert len(rejected) == 0


def test_negative_transaction_amount():

    transactions, accounts, merchants, cards = create_sample_data()

    transactions.loc[0, "transaction_amount"] = -100

    valid, rejected = validate_transactions(
        transactions, accounts, merchants, cards
    )

    assert len(rejected) == 1
    assert "NON_POSITIVE_TRANSACTION_AMOUNT" in (
        rejected.iloc[0]["rejection_reason"]
    )


def test_invalid_account_reference():

    transactions, accounts, merchants, cards = create_sample_data()

    transactions.loc[0, "account_id"] = "ACC999"

    valid, rejected = validate_transactions(
        transactions, accounts, merchants, cards
    )

    assert len(rejected) == 1
    assert "INVALID_ACCOUNT_REFERENCE" in (
        rejected.iloc[0]["rejection_reason"]
    )


def test_invalid_transaction_status():

    transactions, accounts, merchants, cards = create_sample_data()

    transactions.loc[0, "transaction_status"] = "UNKNOWN"

    valid, rejected = validate_transactions(
        transactions, accounts, merchants, cards
    )

    assert len(rejected) == 1
    assert "INVALID_TRANSACTION_STATUS" in (
        rejected.iloc[0]["rejection_reason"]
    )


def test_invalid_timestamp():

    transactions, accounts, merchants, cards = create_sample_data()

    transactions.loc[0, "transaction_timestamp"] = "invalid-date"

    valid, rejected = validate_transactions(
        transactions, accounts, merchants, cards
    )

    assert len(rejected) == 1
    assert "INVALID_TRANSACTION_TIMESTAMP" in (
        rejected.iloc[0]["rejection_reason"]
    )


def test_invalid_optional_merchant_reference():

    transactions, accounts, merchants, cards = create_sample_data()

    transactions.loc[0, "merchant_id"] = "MER999"

    valid, rejected = validate_transactions(
        transactions, accounts, merchants, cards
    )

    assert len(rejected) == 1
    assert "INVALID_MERCHANT_REFERENCE" in (
        rejected.iloc[0]["rejection_reason"]
    )


# ==================================================
# FRAUD ALERT TESTS
# ==================================================

def test_valid_fraud_alert():

    transactions, _, _, _ = create_sample_data()

    alerts = pd.DataFrame({
        "alert_id": ["ALERT001"],
        "transaction_id": ["TXN001"],
        "alert_type": ["HIGH_AMOUNT"],
        "risk_score": [0.85]
    })

    valid, rejected = validate_fraud_alerts(
        alerts, transactions
    )

    assert len(valid) == 1
    assert len(rejected) == 0


def test_invalid_fraud_alert_transaction():

    transactions, _, _, _ = create_sample_data()

    alerts = pd.DataFrame({
        "alert_id": ["ALERT001"],
        "transaction_id": ["TXN999"],
        "alert_type": ["HIGH_AMOUNT"],
        "risk_score": [0.85]
    })

    valid, rejected = validate_fraud_alerts(
        alerts, transactions
    )

    assert len(rejected) == 1
    assert "INVALID_TRANSACTION_REFERENCE" in (
        rejected.iloc[0]["rejection_reason"]
    )


def test_invalid_fraud_risk_score():

    transactions, _, _, _ = create_sample_data()

    alerts = pd.DataFrame({
        "alert_id": ["ALERT001"],
        "transaction_id": ["TXN001"],
        "alert_type": ["HIGH_AMOUNT"],
        "risk_score": [1.5]
    })

    valid, rejected = validate_fraud_alerts(
        alerts, transactions
    )

    assert len(rejected) == 1
    assert "INVALID_RISK_SCORE" in (
        rejected.iloc[0]["rejection_reason"]
    )


# ==================================================
# ADDITIONAL EDGE-CASE TESTS
# ==================================================

def test_multiple_transaction_validation_errors():

    transactions, accounts, merchants, cards = create_sample_data()

    transactions.loc[0, "transaction_amount"] = -100
    transactions.loc[0, "transaction_status"] = "UNKNOWN"
    transactions.loc[0, "account_id"] = "ACC999"

    _, rejected = validate_transactions(
        transactions, accounts, merchants, cards
    )

    assert len(rejected) == 1

    reason = rejected.iloc[0]["rejection_reason"]

    assert "NON_POSITIVE_TRANSACTION_AMOUNT" in reason
    assert "INVALID_TRANSACTION_STATUS" in reason
    assert "INVALID_ACCOUNT_REFERENCE" in reason


def test_invalid_card_reference():

    transactions, accounts, merchants, cards = create_sample_data()

    transactions.loc[0, "card_id"] = "CARD999"

    _, rejected = validate_transactions(
        transactions, accounts, merchants, cards
    )

    assert len(rejected) == 1
    assert "INVALID_CARD_REFERENCE" in (
        rejected.iloc[0]["rejection_reason"]
    )


def test_non_numeric_transaction_amount():

    transactions, accounts, merchants, cards = create_sample_data()

    # Convert to object dtype so Pandas accepts invalid text.
    transactions["transaction_amount"] = (
        transactions["transaction_amount"].astype(object)
    )

    transactions.loc[0, "transaction_amount"] = "invalid"

    _, rejected = validate_transactions(
        transactions, accounts, merchants, cards
    )

    assert len(rejected) == 1
    assert "INVALID_TRANSACTION_AMOUNT" in (
        rejected.iloc[0]["rejection_reason"]
    )


def test_rejected_transaction_preserves_ingestion_metadata():

    transactions, accounts, merchants, cards = create_sample_data()

    transactions["source_file"] = "transactions.csv"
    transactions["run_id"] = "RUN_TEST001"
    transactions["ingested_at"] = "2026-10-30T10:00:00+00:00"

    transactions.loc[0, "transaction_amount"] = -100

    _, rejected = validate_transactions(
        transactions, accounts, merchants, cards
    )

    assert len(rejected) == 1

    assert rejected.iloc[0]["source_file"] == "transactions.csv"
    assert rejected.iloc[0]["run_id"] == "RUN_TEST001"
    assert (
        rejected.iloc[0]["ingested_at"]
        == "2026-10-30T10:00:00+00:00"
    )


def test_invalid_fraud_alert_type():

    transactions, _, _, _ = create_sample_data()

    alerts = pd.DataFrame({
        "alert_id": ["ALERT001"],
        "transaction_id": ["TXN001"],
        "alert_type": ["UNKNOWN_ALERT"],
        "risk_score": [0.85]
    })

    _, rejected = validate_fraud_alerts(
        alerts, transactions
    )

    assert len(rejected) == 1
    assert "INVALID_ALERT_TYPE" in (
        rejected.iloc[0]["rejection_reason"]
    )


def test_non_numeric_fraud_risk_score():

    transactions, _, _, _ = create_sample_data()

    alerts = pd.DataFrame({
        "alert_id": ["ALERT001"],
        "transaction_id": ["TXN001"],
        "alert_type": ["HIGH_AMOUNT"],
        "risk_score": ["invalid"]
    })

    _, rejected = validate_fraud_alerts(
        alerts, transactions
    )

    assert len(rejected) == 1
    assert "INVALID_RISK_SCORE" in (
        rejected.iloc[0]["rejection_reason"]
    )


def test_rejected_fraud_alert_preserves_ingestion_metadata():

    transactions, _, _, _ = create_sample_data()

    alerts = pd.DataFrame({
        "alert_id": ["ALERT001"],
        "transaction_id": ["TXN001"],
        "alert_type": ["HIGH_AMOUNT"],
        "risk_score": [1.5],
        "source_file": ["fraud_alerts.csv"],
        "run_id": ["RUN_TEST002"],
        "ingested_at": ["2026-10-30T10:00:00+00:00"]
    })

    _, rejected = validate_fraud_alerts(
        alerts, transactions
    )

    assert len(rejected) == 1

    assert rejected.iloc[0]["source_file"] == "fraud_alerts.csv"
    assert rejected.iloc[0]["run_id"] == "RUN_TEST002"
    assert (
        rejected.iloc[0]["ingested_at"]
        == "2026-10-30T10:00:00+00:00"
    )
