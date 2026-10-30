
import pandas as pd


# ==================================================
# EXPECTED SCHEMAS
# ==================================================

EXPECTED_SCHEMAS = {

    "customers": [
        "customer_id",
        "customer_name",
        "email",
        "city",
        "state"
    ],

    "branches": [
        "branch_id",
        "branch_name",
        "city",
        "state"
    ],

    "accounts": [
        "account_id",
        "customer_id",
        "branch_id",
        "account_type",
        "balance"
    ],

    "merchants": [
        "merchant_id",
        "merchant_name",
        "category"
    ],

    "cards": [
        "card_id",
        "customer_id",
        "card_type",
        "card_status"
    ],

    "transactions": [
        "transaction_id",
        "account_id",
        "merchant_id",
        "card_id",
        "transaction_type",
        "transaction_amount",
        "transaction_status",
        "transaction_timestamp"
    ],

    "fraud_alerts": [
        "alert_id",
        "transaction_id",
        "alert_type",
        "risk_score"
    ]
}


# ==================================================
# PRIMARY KEY CONFIGURATION
# ==================================================

PRIMARY_KEYS = {
    "customers": "customer_id",
    "branches": "branch_id",
    "accounts": "account_id",
    "merchants": "merchant_id",
    "cards": "card_id",
    "transactions": "transaction_id",
    "fraud_alerts": "alert_id"
}


# ==================================================
# REQUIRED NON-NULL COLUMNS
# ==================================================

REQUIRED_COLUMNS = {

    "customers": [
        "customer_id",
        "customer_name",
        "email"
    ],

    "branches": [
        "branch_id",
        "branch_name"
    ],

    "accounts": [
        "account_id",
        "customer_id",
        "branch_id",
        "account_type",
        "balance"
    ],

    "merchants": [
        "merchant_id",
        "merchant_name",
        "category"
    ],

    "cards": [
        "card_id",
        "customer_id",
        "card_type",
        "card_status"
    ],

    "transactions": [
        "transaction_id",
        "account_id",
        "transaction_type",
        "transaction_amount",
        "transaction_status",
        "transaction_timestamp"
    ],

    "fraud_alerts": [
        "alert_id",
        "transaction_id",
        "alert_type",
        "risk_score"
    ]
}


# ==================================================
# NUMERIC COLUMN CONFIGURATION
# ==================================================

NUMERIC_COLUMNS = {

    "accounts": [
        "balance"
    ],

    "transactions": [
        "transaction_amount"
    ],

    "fraud_alerts": [
        "risk_score"
    ]
}


# ==================================================
# INGESTION METADATA COLUMNS
# ==================================================

METADATA_COLUMNS = [
    "source_file",
    "run_id",
    "ingested_at"
]


# ==================================================
# VALIDATE SCHEMA
# ==================================================

def validate_schema(dataset_name, df):

    errors = []
    warnings = []

    # --------------------------------------------------
    # 1. CHECK DATASET NAME
    # --------------------------------------------------

    if dataset_name not in EXPECTED_SCHEMAS:

        return {
            "dataset": dataset_name,
            "valid": False,
            "errors": [
                f"Unknown dataset: {dataset_name}"
            ],
            "warnings": [],
            "record_count": len(df)
        }

    expected_columns = EXPECTED_SCHEMAS[dataset_name]

    allowed_columns = (
        expected_columns + METADATA_COLUMNS
    )

    actual_columns = list(df.columns)

    # --------------------------------------------------
    # 2. CHECK MISSING COLUMNS
    # --------------------------------------------------

    missing_columns = [
        col for col in expected_columns
        if col not in actual_columns
    ]

    if missing_columns:

        errors.append(
            f"Missing columns: {missing_columns}"
        )

    # --------------------------------------------------
    # 3. CHECK UNEXPECTED COLUMNS
    # --------------------------------------------------

    unexpected_columns = [
        col for col in actual_columns
        if col not in allowed_columns
    ]

    if unexpected_columns:

        errors.append(
            f"Unexpected columns: {unexpected_columns}"
        )

    # --------------------------------------------------
    # 4. CHECK EMPTY DATASET
    # --------------------------------------------------

    if df.empty:

        warnings.append(
            "Dataset contains no records"
        )

    # Continue record-level checks only if all
    # expected columns are present.
    if not missing_columns:

        # ----------------------------------------------
        # 5. CHECK NULL VALUES
        # ----------------------------------------------

        for col in REQUIRED_COLUMNS[dataset_name]:

            null_count = int(
                df[col].isna().sum()
            )

            if null_count > 0:

                warnings.append(
                    f"{col} contains {null_count} null values"
                )

        # ----------------------------------------------
        # 6. CHECK DUPLICATE PRIMARY KEYS
        # ----------------------------------------------

        primary_key = PRIMARY_KEYS[dataset_name]

        duplicate_count = int(
            df[primary_key].duplicated().sum()
        )

        if duplicate_count > 0:

            warnings.append(
                f"{primary_key} contains "
                f"{duplicate_count} duplicate values"
            )

        # ----------------------------------------------
        # 7. CHECK NUMERIC DATA TYPES
        # ----------------------------------------------

        numeric_columns = NUMERIC_COLUMNS.get(
            dataset_name,
            []
        )

        for col in numeric_columns:

            if not pd.api.types.is_numeric_dtype(df[col]):

                errors.append(
                    f"{col} must have a numeric data type"
                )

    # --------------------------------------------------
    # 8. FINAL VALIDATION RESULT
    # --------------------------------------------------

    result = {

        "dataset": dataset_name,

        "valid": len(errors) == 0,

        "errors": errors,

        "warnings": warnings,

        "record_count": len(df)
    }

    if result["valid"]:

        print(
            f"{dataset_name}: Schema validation passed"
        )

    else:

        print(
            f"{dataset_name}: Schema validation failed"
        )

    return result


# ==================================================
# VALIDATE ALL DATASETS
# ==================================================

def validate_all_schemas(datasets):

    results = []

    for dataset_name, df in datasets.items():

        result = validate_schema(
            dataset_name,
            df
        )

        results.append(result)

    return results
