
import pandas as pd


def handle_duplicates(df, dataset_name, primary_key):
    """
    Separate unique records and duplicate records.

    Keeps the first occurrence of each non-null primary key.
    Moves subsequent occurrences to rejected records.

    Null primary keys are not treated as duplicates.
    They are handled separately by required-field validation.

    Args:
        df (pd.DataFrame): Input dataset.
        dataset_name (str): Name of the dataset.
        primary_key (str): Primary key column.

    Returns:
        tuple:
            valid_df: Records retained for further validation.
            rejected_df: Duplicate records with rejection reasons.
    """

    if primary_key not in df.columns:
        raise ValueError(
            f"Primary key '{primary_key}' not found in {dataset_name}"
        )

    # Identify duplicate records after the first occurrence.
    # Null primary keys are excluded from duplicate detection.
    duplicate_mask = (
        df[primary_key].notna()
        & df.duplicated(
            subset=[primary_key],
            keep="first"
        )
    )

    # Separate valid and duplicate records.
    valid_df = df.loc[~duplicate_mask].copy()
    rejected_df = df.loc[duplicate_mask].copy()

    # Add rejection reason to duplicate records.
    if not rejected_df.empty:
        rejected_df["rejection_reason"] = (
            f"DUPLICATE_{primary_key.upper()}"
        )

    return valid_df, rejected_df
