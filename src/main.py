import os
import shutil
import uuid
from pathlib import Path

import pandas as pd

from src.ingestion.ingest_data import ingest_data
from src.monitoring.run_tracker import RunTracker

from src.validation.schema_validator import (
    validate_all_schemas,
    PRIMARY_KEYS,
    REQUIRED_COLUMNS
)

from src.validation.duplicate_handler import handle_duplicates

from src.validation.business_validator import (
    validate_transactions,
    validate_fraud_alerts
)

from src.transformation.transform_data import (
    transform_transactions,
    transform_customers
)


# ==================================================
# RECORD-LEVEL REQUIRED FIELD VALIDATION
# ==================================================

def validate_required_fields(df, required_columns):

    if df.empty:
        return df.copy(), df.copy()

    null_mask = df[required_columns].isna().any(axis=1)

    valid_df = df.loc[~null_mask].copy()
    rejected_df = df.loc[null_mask].copy()

    if not rejected_df.empty:

        reasons = []

        for _, row in rejected_df.iterrows():

            missing = [
                col for col in required_columns
                if pd.isna(row[col])
            ]

            reasons.append(
                "|".join(
                    f"NULL_REQUIRED_FIELD:{col}"
                    for col in missing
                )
            )

        rejected_df["rejection_reason"] = reasons

    return valid_df, rejected_df


# ==================================================
# FOREIGN KEY VALIDATION
# ==================================================

def validate_foreign_key(
    df,
    column,
    reference_df,
    reference_column
):

    if df.empty:
        return df.copy(), df.copy()

    valid_ids = set(
        reference_df[reference_column].dropna()
    )

    invalid_mask = ~df[column].isin(valid_ids)

    valid_df = df.loc[~invalid_mask].copy()
    rejected_df = df.loc[invalid_mask].copy()

    if not rejected_df.empty:

        rejected_df["rejection_reason"] = (
            f"INVALID_{column.upper()}_REFERENCE"
        )

    return valid_df, rejected_df


# ==================================================
# COMBINE REJECTED RECORDS
# ==================================================

def combine_rejections(*frames):

    non_empty = [
        frame for frame in frames
        if not frame.empty
    ]

    if not non_empty:
        return pd.DataFrame()

    return pd.concat(
        non_empty,
        ignore_index=True,
        sort=False
    )


# ==================================================
# SAFE OUTPUT PUBLISHING
# ==================================================

def save_pipeline_outputs(
    processed,
    rejected,
    output_dir,
    reconciliation_report=None
):
    """
    Save pipeline outputs into a temporary directory.

    Publish the final directory only after all files
    have been written and checked.
    """

    output_path = Path(output_dir)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temp_dir = output_path.parent / (
        f".{output_path.name}_tmp_{uuid.uuid4().hex[:8]}"
    )

    try:

        processed_dir = temp_dir / "processed"
        rejected_dir = temp_dir / "rejected"

        processed_dir.mkdir(parents=True)
        rejected_dir.mkdir(parents=True)

        # ----------------------------------------------
        # Save reconciliation report
        # ----------------------------------------------

        if reconciliation_report is not None:

            report_path = (
                temp_dir / "reconciliation_report.csv"
            )

            reconciliation_report.to_csv(
                report_path,
                index=False
            )

            if not report_path.is_file():

                raise FileNotFoundError(
                    f"Missing reconciliation report: {report_path}"
                )

        # ----------------------------------------------
        # Save processed datasets
        # ----------------------------------------------

        for dataset_name, df in processed.items():

            file_path = (
                processed_dir / f"{dataset_name}.parquet"
            )

            df.to_parquet(
                file_path,
                index=False
            )

        # ----------------------------------------------
        # Save rejected datasets
        # ----------------------------------------------

        for dataset_name, df in rejected.items():

            if df.empty:
                continue

            file_path = (
                rejected_dir /
                f"{dataset_name}_rejected.parquet"
            )

            df.to_parquet(
                file_path,
                index=False
            )

        # ----------------------------------------------
        # Verify processed files
        # ----------------------------------------------

        for dataset_name in processed:

            file_path = (
                processed_dir / f"{dataset_name}.parquet"
            )

            if not file_path.is_file():

                raise FileNotFoundError(
                    f"Missing processed output: {file_path}"
                )

        # ----------------------------------------------
        # Verify rejected files
        # ----------------------------------------------

        for dataset_name, df in rejected.items():

            if df.empty:
                continue

            file_path = (
                rejected_dir /
                f"{dataset_name}_rejected.parquet"
            )

            if not file_path.is_file():

                raise FileNotFoundError(
                    f"Missing rejected output: {file_path}"
                )

        # ----------------------------------------------
        # Prevent overwriting existing run output
        # ----------------------------------------------

        if output_path.exists():

            raise FileExistsError(
                f"Output directory already exists: {output_path}"
            )

        # ----------------------------------------------
        # Publish completed output directory
        # ----------------------------------------------

        temp_dir.rename(output_path)

        print("\nOUTPUT FILES SAVED")
        print(f"Processed: {output_path / 'processed'}")
        print(f"Rejected:  {output_path / 'rejected'}")
        print(
            f"Reconciliation: "
            f"{output_path / 'reconciliation_report.csv'}"
        )

    except Exception:

        # Remove incomplete temporary output.
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

        raise


# ==================================================
# MAIN PIPELINE
# ==================================================

def run_pipeline(
    datasets=None,
    tracker=None,
    output_dir="data",
    input_dir=None
):
    """
    Execute the complete SmartBank Analytics pipeline.

    Run tracking begins before ingestion so failures
    during ingestion can also be recorded.
    """

    loaded_through_ingestion = datasets is None

    # Create the tracker before starting any pipeline work.
    if tracker is None:
        tracker = RunTracker()

    processed = {}
    rejected = {}

    try:

        # --------------------------------------------------
        # 1. DATA INGESTION
        # --------------------------------------------------

        if loaded_through_ingestion:

            print("\nSTEP 1: DATA INGESTION")

            datasets, tracker = ingest_data(
                input_dir=input_dir,
                tracker=tracker
            )

        else:

            # Directly supplied datasets must be counted here.
            input_count = sum(
                len(df) for df in datasets.values()
            )

            tracker.add_input_records(input_count)

        print("\nSMARTBANK ANALYTICS PIPELINE")
        print("=" * 65)

        print(f"Run ID: {tracker.run_id}")

        # --------------------------------------------------
        # 2. SCHEMA VALIDATION
        # --------------------------------------------------

        print("\nSTEP 2: SCHEMA VALIDATION")

        schema_results = validate_all_schemas(datasets)

        schema_failures = [
            result for result in schema_results
            if not result["valid"]
        ]

        if schema_failures:

            for result in schema_failures:

                for error in result["errors"]:

                    tracker.add_error(
                        f"{result['dataset']}: {error}"
                    )

            raise ValueError(
                "Structural schema validation failed"
            )

        # --------------------------------------------------
        # 3. DUPLICATE AND REQUIRED FIELD VALIDATION
        # --------------------------------------------------

        print("\nSTEP 3: DUPLICATE AND NULL VALIDATION")

        clean = {}

        for dataset_name, df in datasets.items():

            primary_key = PRIMARY_KEYS[dataset_name]

            unique_df, duplicate_df = handle_duplicates(
                df,
                dataset_name,
                primary_key
            )

            required_valid, null_rejected = (
                validate_required_fields(
                    unique_df,
                    REQUIRED_COLUMNS[dataset_name]
                )
            )

            clean[dataset_name] = required_valid

            rejected[dataset_name] = combine_rejections(
                duplicate_df,
                null_rejected
            )

            print(
                f"{dataset_name}: "
                f"{len(required_valid)} valid, "
                f"{len(rejected[dataset_name])} rejected"
            )

        # --------------------------------------------------
        # 4. ACCOUNT FOREIGN KEY VALIDATION
        # --------------------------------------------------

        print("\nSTEP 4: ACCOUNT REFERENCE VALIDATION")

        accounts = clean["accounts"]

        accounts_valid, accounts_rejected = (
            validate_foreign_key(
                accounts,
                "customer_id",
                clean["customers"],
                "customer_id"
            )
        )

        accounts_valid, branch_rejected = (
            validate_foreign_key(
                accounts_valid,
                "branch_id",
                clean["branches"],
                "branch_id"
            )
        )

        clean["accounts"] = accounts_valid

        rejected["accounts"] = combine_rejections(
            rejected["accounts"],
            accounts_rejected,
            branch_rejected
        )

        # --------------------------------------------------
        # 5. CARD FOREIGN KEY VALIDATION
        # --------------------------------------------------

        print("\nSTEP 5: CARD REFERENCE VALIDATION")

        cards_valid, cards_rejected = (
            validate_foreign_key(
                clean["cards"],
                "customer_id",
                clean["customers"],
                "customer_id"
            )
        )

        clean["cards"] = cards_valid

        rejected["cards"] = combine_rejections(
            rejected["cards"],
            cards_rejected
        )

        # --------------------------------------------------
        # 6. TRANSACTION BUSINESS VALIDATION
        # --------------------------------------------------

        print("\nSTEP 6: TRANSACTION BUSINESS VALIDATION")

        transactions_valid, transactions_rejected = (
            validate_transactions(
                clean["transactions"],
                clean["accounts"],
                clean["merchants"],
                clean["cards"]
            )
        )

        clean["transactions"] = transactions_valid

        rejected["transactions"] = combine_rejections(
            rejected["transactions"],
            transactions_rejected
        )

        # --------------------------------------------------
        # 7. FRAUD ALERT VALIDATION
        # --------------------------------------------------

        print("\nSTEP 7: FRAUD ALERT VALIDATION")

        alerts_valid, alerts_rejected = (
            validate_fraud_alerts(
                clean["fraud_alerts"],
                clean["transactions"]
            )
        )

        clean["fraud_alerts"] = alerts_valid

        rejected["fraud_alerts"] = combine_rejections(
            rejected["fraud_alerts"],
            alerts_rejected
        )

        # --------------------------------------------------
        # 8. DATA TRANSFORMATION
        # --------------------------------------------------

        print("\nSTEP 8: DATA TRANSFORMATION")

        clean["transactions"] = transform_transactions(
            clean["transactions"]
        )

        clean["customers"] = transform_customers(
            clean["customers"]
        )

        processed = clean

        # --------------------------------------------------
        # 9. RECORD COUNT RECONCILIATION
        # --------------------------------------------------

        print("\nSTEP 9: RECORD COUNT RECONCILIATION")

        reconciliation_rows = []

        for dataset_name, input_df in datasets.items():

            input_count = len(input_df)
            valid_count = len(processed[dataset_name])
            rejected_count = len(rejected[dataset_name])

            difference = input_count - (
                valid_count + rejected_count
            )

            status = (
                "PASS" if difference == 0 else "FAIL"
            )

            reconciliation_rows.append({
                "dataset": dataset_name,
                "input_records": input_count,
                "valid_records": valid_count,
                "rejected_records": rejected_count,
                "difference": difference,
                "status": status
            })

            print(
                f"{dataset_name}: "
                f"input={input_count:,}, "
                f"valid={valid_count:,}, "
                f"rejected={rejected_count:,}, "
                f"difference={difference:,} "
                f"[{status}]"
            )

        reconciliation_report = pd.DataFrame(
            reconciliation_rows,
            columns=[
                "dataset",
                "input_records",
                "valid_records",
                "rejected_records",
                "difference",
                "status"
            ]
        )

        total_input = int(
            reconciliation_report["input_records"].sum()
        )

        total_output = int(
            reconciliation_report["valid_records"].sum()
        )

        total_rejected = int(
            reconciliation_report["rejected_records"].sum()
        )

        print("\nOVERALL RECONCILIATION")

        print(f"Input records:    {total_input:,}")
        print(f"Output records:   {total_output:,}")
        print(f"Rejected records: {total_rejected:,}")

        if (
            reconciliation_report["status"] != "PASS"
        ).any():

            failed_datasets = reconciliation_report.loc[
                reconciliation_report["status"] != "PASS",
                "dataset"
            ].tolist()

            raise ValueError(
                "Record reconciliation failed for datasets: "
                + ", ".join(failed_datasets)
            )

        if total_input != total_output + total_rejected:

            raise ValueError(
                "Overall record reconciliation failed: "
                "input does not equal output plus rejected"
            )

        # --------------------------------------------------
        # 10. SAVE OUTPUTS
        # --------------------------------------------------

        print("\nSTEP 10: SAVING OUTPUTS")

        run_output_dir = os.path.join(
            output_dir,
            tracker.run_id
        )

        save_pipeline_outputs(
            processed,
            rejected,
            run_output_dir,
            reconciliation_report=reconciliation_report
        )

        # --------------------------------------------------
        # 11. UPDATE RUN TRACKER
        # --------------------------------------------------

        tracker.add_output_records(total_output)

        tracker.add_rejected_records(total_rejected)

        # Only mark SUCCESS after publishing completes.
        tracker.finish("SUCCESS")

        print("\nPIPELINE COMPLETED SUCCESSFULLY")

        return {
            "status": "SUCCESS",
            "processed": processed,
            "rejected": rejected,
            "reconciliation_report": reconciliation_report,
            "metrics": tracker.metrics,
            "output_dir": run_output_dir
        }

    except Exception as error:

        # Record failures from ingestion, validation,
        # transformation, reconciliation, or publishing.
        tracker.add_error(error)

        tracker.finish("FAILED")

        print("\nPIPELINE FAILED:", error)

        raise


# ==================================================
# PROGRAM ENTRY POINT
# ==================================================

if __name__ == "__main__":

    result = run_pipeline()

    print("\nFINAL PIPELINE STATUS:")
    print(result["status"])