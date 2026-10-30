
import pandas as pd


# ==================================================
# ALLOWED BANKING VALUES
# ==================================================

VALID_TRANSACTION_TYPES = {
    "UPI",
    "NEFT",
    "RTGS",
    "IMPS",
    "ATM_WITHDRAWAL",
    "DEBIT_CARD",
    "CREDIT_CARD",
    "CASH_DEPOSIT"
}

VALID_TRANSACTION_STATUSES = {
    "SUCCESS",
    "FAILED",
    "PENDING",
    "REVERSED"
}

VALID_ALERT_TYPES = {
    "HIGH_AMOUNT",
    "UNUSUAL_ACTIVITY",
    "SUSPICIOUS_MERCHANT",
    "MULTIPLE_TRANSACTIONS"
}


# ==================================================
# HELPER: BUILD VALID AND REJECTED DATAFRAMES
# ==================================================

def split_valid_and_rejected(df, error_masks):

    # Handle empty DataFrames.
    if df.empty:

        valid_df = df.copy()
        rejected_df = df.copy()

        rejected_df["rejection_reason"] = pd.Series(
            dtype="object"
        )

        return valid_df, rejected_df

    # Initialize rejection reasons.
    reasons = pd.Series(
        "",
        index=df.index,
        dtype="object"
    )

    # Combine all applicable validation errors.
    for error_name, error_mask in error_masks.items():

        current = reasons.loc[error_mask]

        reasons.loc[error_mask] = (
            current.where(
                current.eq(""),
                current + "|"
            ) + error_name
        )

    # Identify invalid records.
    invalid_mask = reasons.ne("")

    # Separate valid records.
    valid_df = df.loc[~invalid_mask].copy()

    # Separate rejected records.
    rejected_df = df.loc[invalid_mask].copy()

    rejected_df["rejection_reason"] = reasons.loc[
        invalid_mask
    ]

    return valid_df, rejected_df


# ==================================================
# TRANSACTION BUSINESS VALIDATION
# ==================================================

def validate_transactions(
    transactions_df,
    accounts_df,
    merchants_df,
    cards_df
):

    df = transactions_df.copy()

    if df.empty:

        return split_valid_and_rejected(df, {})

    # --------------------------------------------------
    # 1. TRANSACTION AMOUNT VALIDATION
    # --------------------------------------------------

    amount = pd.to_numeric(
        df["transaction_amount"],
        errors="coerce"
    )

    invalid_amount = amount.isna()

    non_positive_amount = (
        amount.notna() & (amount <= 0)
    )

    # --------------------------------------------------
    # 2. TRANSACTION TYPE VALIDATION
    # --------------------------------------------------

    invalid_type = ~df["transaction_type"].isin(
        VALID_TRANSACTION_TYPES
    )

    # --------------------------------------------------
    # 3. TRANSACTION STATUS VALIDATION
    # --------------------------------------------------

    invalid_status = ~df["transaction_status"].isin(
        VALID_TRANSACTION_STATUSES
    )

    # --------------------------------------------------
    # 4. ACCOUNT FOREIGN KEY VALIDATION
    # --------------------------------------------------

    account_ids = set(
        accounts_df["account_id"].dropna()
    )

    invalid_account = (
        df["account_id"].isna()
        | ~df["account_id"].isin(account_ids)
    )

    # --------------------------------------------------
    # 5. MERCHANT FOREIGN KEY VALIDATION
    # --------------------------------------------------

    merchant_ids = set(
        merchants_df["merchant_id"].dropna()
    )

    invalid_merchant = (
        df["merchant_id"].notna()
        & ~df["merchant_id"].isin(merchant_ids)
    )

    # --------------------------------------------------
    # 6. CARD FOREIGN KEY VALIDATION
    # --------------------------------------------------

    card_ids = set(
        cards_df["card_id"].dropna()
    )

    invalid_card = (
        df["card_id"].notna()
        & ~df["card_id"].isin(card_ids)
    )

    # --------------------------------------------------
    # 7. TRANSACTION TIMESTAMP VALIDATION
    # --------------------------------------------------

    timestamps = pd.to_datetime(
        df["transaction_timestamp"],
        format="mixed",
        errors="coerce",
        utc=True
    )

    invalid_timestamp = timestamps.isna()

    # --------------------------------------------------
    # 8. BUILD ERROR MASKS
    # --------------------------------------------------

    error_masks = {
        "INVALID_TRANSACTION_AMOUNT": invalid_amount,
        "NON_POSITIVE_TRANSACTION_AMOUNT": non_positive_amount,
        "INVALID_TRANSACTION_TYPE": invalid_type,
        "INVALID_TRANSACTION_STATUS": invalid_status,
        "INVALID_ACCOUNT_REFERENCE": invalid_account,
        "INVALID_MERCHANT_REFERENCE": invalid_merchant,
        "INVALID_CARD_REFERENCE": invalid_card,
        "INVALID_TRANSACTION_TIMESTAMP": invalid_timestamp
    }

    # --------------------------------------------------
    # 9. NORMALIZE DATA TYPES
    # --------------------------------------------------

    df["transaction_amount"] = amount

    df["transaction_timestamp"] = timestamps

    # --------------------------------------------------
    # 10. RETURN VALID AND REJECTED RECORDS
    # --------------------------------------------------

    return split_valid_and_rejected(
        df,
        error_masks
    )


# ==================================================
# FRAUD ALERT BUSINESS VALIDATION
# ==================================================

def validate_fraud_alerts(
    fraud_alerts_df,
    transactions_df
):

    df = fraud_alerts_df.copy()

    if df.empty:

        return split_valid_and_rejected(df, {})

    # --------------------------------------------------
    # 1. TRANSACTION REFERENCE VALIDATION
    # --------------------------------------------------

    transaction_ids = set(
        transactions_df["transaction_id"].dropna()
    )

    invalid_transaction = (
        df["transaction_id"].isna()
        | ~df["transaction_id"].isin(transaction_ids)
    )

    # --------------------------------------------------
    # 2. ALERT TYPE VALIDATION
    # --------------------------------------------------

    invalid_alert_type = ~df["alert_type"].isin(
        VALID_ALERT_TYPES
    )

    # --------------------------------------------------
    # 3. RISK SCORE VALIDATION
    # --------------------------------------------------

    risk_score = pd.to_numeric(
        df["risk_score"],
        errors="coerce"
    )

    invalid_risk_score = (
        risk_score.isna()
        | (risk_score < 0)
        | (risk_score > 1)
    )

    # --------------------------------------------------
    # 4. BUILD ERROR MASKS
    # --------------------------------------------------

    error_masks = {
        "INVALID_TRANSACTION_REFERENCE": invalid_transaction,
        "INVALID_ALERT_TYPE": invalid_alert_type,
        "INVALID_RISK_SCORE": invalid_risk_score
    }

    # Normalize risk score.
    df["risk_score"] = risk_score

    # --------------------------------------------------
    # 5. RETURN VALID AND REJECTED RECORDS
    # --------------------------------------------------

    return split_valid_and_rejected(
        df,
        error_masks
    )
