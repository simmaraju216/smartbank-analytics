
import pandas as pd


def transform_transactions(df):
    """
    Transform validated banking transactions into
    analytics-ready records.

    Timestamp standard:
        All transaction timestamps are stored in UTC.

    Derived columns:
        transaction_date
        transaction_month
        transaction_year
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
    # 3. CONVERT TIMESTAMP TO UTC
    # --------------------------------------------------

    transformed_df["transaction_timestamp"] = pd.to_datetime(
        transformed_df["transaction_timestamp"],
        errors="coerce",
        utc=True
    )

    # --------------------------------------------------
    # 4. CREATE DATE-RELATED COLUMNS USING UTC
    # --------------------------------------------------

    timestamp = transformed_df["transaction_timestamp"]

    # Extract the calendar date in UTC.
    transformed_df["transaction_date"] = timestamp.dt.date

    # Extract month in UTC.
    transformed_df["transaction_month"] = timestamp.dt.month

    # Extract year in UTC.
    transformed_df["transaction_year"] = timestamp.dt.year

    # --------------------------------------------------
    # 5. CREATE DEBIT AMOUNT
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
    # 6. CREATE CREDIT AMOUNT
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
