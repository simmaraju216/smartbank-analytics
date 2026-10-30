
import pandas as pd


def transform_transactions(df):
    """
    Transform validated banking transactions into
    analytics-ready records.

    Timestamp standard:
        Transaction and ingestion timestamps are stored in UTC.

    Late arrival:
        A transaction received more than 24 hours after
        its event timestamp.

    Out of order:
        An event timestamp earlier than the maximum
        event timestamp in preceding input rows.

    Original row order is preserved.
    Late and out-of-order transactions are not rejected.

    Derived columns:
        transaction_date
        transaction_month
        transaction_year
        arrival_delay_hours
        is_late_arrival
        is_out_of_order
        debit_amount
        credit_amount
    """

    if df.empty:
        return df.copy()

    transformed_df = df.copy()

    # --------------------------------------------------
    # 1. STANDARDIZE COLUMN NAMES
    # --------------------------------------------------

    transformed_df.columns = (
        transformed_df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    # --------------------------------------------------
    # 2. CONVERT TRANSACTION AMOUNT TO NUMERIC
    # --------------------------------------------------

    transformed_df["transaction_amount"] = pd.to_numeric(
        transformed_df["transaction_amount"],
        errors="coerce"
    )

    # --------------------------------------------------
    # 3. CONVERT TRANSACTION TIMESTAMP TO UTC
    # --------------------------------------------------

    transformed_df["transaction_timestamp"] = pd.to_datetime(
        transformed_df["transaction_timestamp"],
        errors="coerce",
        utc=True
    )

    timestamp = transformed_df["transaction_timestamp"]

    # --------------------------------------------------
    # 4. CREATE DATE-RELATED COLUMNS
    # --------------------------------------------------

    transformed_df["transaction_date"] = timestamp.dt.date

    transformed_df["transaction_month"] = timestamp.dt.month

    transformed_df["transaction_year"] = timestamp.dt.year

    # --------------------------------------------------
    # 5. DETECT LATE-ARRIVING TRANSACTIONS
    # --------------------------------------------------

    if "ingested_at" in transformed_df.columns:

        transformed_df["ingested_at"] = pd.to_datetime(
            transformed_df["ingested_at"],
            errors="coerce",
            utc=True
        )

        transformed_df["arrival_delay_hours"] = (
            transformed_df["ingested_at"] - timestamp
        ).dt.total_seconds() / 3600

        transformed_df["is_late_arrival"] = (
            transformed_df["arrival_delay_hours"] > 24
        ).fillna(False).astype(bool)

    else:

        transformed_df["arrival_delay_hours"] = float("nan")

        transformed_df["is_late_arrival"] = False

    # --------------------------------------------------
    # 6. DETECT OUT-OF-ORDER TRANSACTIONS
    # --------------------------------------------------

    previous_max_timestamp = (
        timestamp.cummax().shift(1)
    )

    transformed_df["is_out_of_order"] = (
        timestamp < previous_max_timestamp
    ).fillna(False).astype(bool)

    # --------------------------------------------------
    # 7. CREATE DEBIT AMOUNT
    # --------------------------------------------------

    debit_types = [
        "ATM_WITHDRAWAL",
        "DEBIT_CARD",
        "UPI",
        "NEFT",
        "RTGS",
        "IMPS"
    ]

    transformed_df["debit_amount"] = (
        transformed_df["transaction_amount"].where(
            transformed_df["transaction_type"].isin(debit_types),
            0
        )
    )

    # --------------------------------------------------
    # 8. CREATE CREDIT AMOUNT
    # --------------------------------------------------

    credit_types = [
        "CASH_DEPOSIT"
    ]

    transformed_df["credit_amount"] = (
        transformed_df["transaction_amount"].where(
            transformed_df["transaction_type"].isin(credit_types),
            0
        )
    )

    return transformed_df


# ==================================================
# CUSTOMER TRANSFORMATION
# ==================================================

def transform_customers(df):
    """
    Standardize customer data.

    Normalizes email addresses, city names and state names.
    """

    transformed_df = df.copy()

    # --------------------------------------------------
    # 1. STANDARDIZE COLUMN NAMES
    # --------------------------------------------------

    transformed_df.columns = (
        transformed_df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    # --------------------------------------------------
    # 2. NORMALIZE EMAIL
    # --------------------------------------------------

    if "email" in transformed_df.columns:

        transformed_df["email"] = (
            transformed_df["email"]
            .astype("string")
            .str.strip()
            .str.lower()
        )

    # --------------------------------------------------
    # 3. NORMALIZE CITY
    # --------------------------------------------------

    if "city" in transformed_df.columns:

        transformed_df["city"] = (
            transformed_df["city"]
            .astype("string")
            .str.strip()
            .str.title()
        )

    # --------------------------------------------------
    # 4. NORMALIZE STATE
    # --------------------------------------------------

    if "state" in transformed_df.columns:

        transformed_df["state"] = (
            transformed_df["state"]
            .astype("string")
            .str.strip()
            .str.title()
        )

    return transformed_df
