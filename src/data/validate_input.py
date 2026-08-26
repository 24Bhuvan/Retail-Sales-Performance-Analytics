from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from load_data import load_all_datasets


# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_DIR = PROJECT_ROOT / "reports" / "python_processing"

VALIDATION_FILE = REPORT_DIR / "processing_validation.csv"
STATISTICS_FILE = REPORT_DIR / "dataset_statistics.csv"


# =============================================================================
# EXPECTED KEYS
# =============================================================================

KEY_DEFINITIONS = {
    "customers": ["customer_id"],
    "geolocation": [],
    "orders": ["order_id"],
    "order_items": ["order_id", "order_item_id"],
    "payments": ["order_id", "payment_sequential"],
    "reviews": [],
    "products": ["product_id"],
    "sellers": ["seller_id"],
    "category_translation": ["product_category_name"],
}


# =============================================================================
# DATE COLUMNS
# =============================================================================

DATE_COLUMNS = {
    "customers": [],

    "geolocation": [],

    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],

    "order_items": [
        "shipping_limit_date",
    ],

    "payments": [],

    "reviews": [
        "review_creation_date",
        "review_answer_timestamp",
    ],

    "products": [],

    "sellers": [],

    "category_translation": [],
}


# =============================================================================
# HELPERS
# =============================================================================

def count_nulls(df: pd.DataFrame) -> int:
    """Return total NULL cells in the dataset."""

    return int(
        df.isna().sum().sum()
    )


def count_duplicate_rows(df: pd.DataFrame) -> int:
    """Return exact duplicate rows excluding the first occurrence."""

    return int(
        df.duplicated(keep="first").sum()
    )


def validate_key(
    df: pd.DataFrame,
    key_columns: list[str],
) -> dict:

    if not key_columns:
        return {
            "key_defined": False,
            "key_columns": "",
            "key_null_rows": None,
            "duplicate_key_rows": None,
            "key_unique": None,
        }

    missing_columns = [
        column
        for column in key_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing key columns: {missing_columns}"
        )

    key_null_rows = int(
        df[key_columns]
        .isna()
        .any(axis=1)
        .sum()
    )

    duplicate_key_rows = int(
        df.duplicated(
            subset=key_columns,
            keep=False,
        ).sum()
    )

    return {
        "key_defined": True,
        "key_columns": "|".join(key_columns),
        "key_null_rows": key_null_rows,
        "duplicate_key_rows": duplicate_key_rows,
        "key_unique": (
            key_null_rows == 0
            and duplicate_key_rows == 0
        ),
    }


def get_date_statistics(
    df: pd.DataFrame,
    date_columns: list[str],
) -> dict:

    existing_date_columns = [
        column
        for column in date_columns
        if column in df.columns
    ]

    if not existing_date_columns:
        return {
            "date_columns": "",
            "minimum_date": None,
            "maximum_date": None,
        }

    min_values = []
    max_values = []

    for column in existing_date_columns:

        series = df[column].dropna()

        if series.empty:
            continue

        min_values.append(
            series.min()
        )

        max_values.append(
            series.max()
        )

    minimum_date = (
        min(min_values)
        if min_values
        else None
    )

    maximum_date = (
        max(max_values)
        if max_values
        else None
    )

    return {
        "date_columns": "|".join(
            existing_date_columns
        ),
        "minimum_date": (
            minimum_date.isoformat()
            if minimum_date is not None
            else None
        ),
        "maximum_date": (
            maximum_date.isoformat()
            if maximum_date is not None
            else None
        ),
    }


# =============================================================================
# DATASET VALIDATION
# =============================================================================

def validate_dataset(
    dataset_name: str,
    df: pd.DataFrame,
) -> tuple[dict, list[dict]]:

    key_result = validate_key(
        df,
        KEY_DEFINITIONS.get(
            dataset_name,
            [],
        ),
    )

    date_result = get_date_statistics(
        df,
        DATE_COLUMNS.get(
            dataset_name,
            [],
        ),
    )

    validation_record = {
        "dataset": dataset_name,
        "row_count": len(df),
        "column_count": len(df.columns),
        "null_cells": count_nulls(df),
        "duplicate_rows": count_duplicate_rows(df),
        **key_result,
        "minimum_date": date_result["minimum_date"],
        "maximum_date": date_result["maximum_date"],
        "validation_timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
    }

    statistics_records = []

    for column in df.columns:

        statistics_records.append(
            {
                "dataset": dataset_name,
                "column": column,
                "dtype": str(df[column].dtype),
                "null_count": int(
                    df[column].isna().sum()
                ),
                "null_rate_pct": round(
                    df[column].isna().mean() * 100,
                    4,
                ),
                "unique_count": int(
                    df[column].nunique(
                        dropna=True
                    )
                ),
            }
        )

    return (
        validation_record,
        statistics_records,
    )


# =============================================================================
# MAIN VALIDATION
# =============================================================================

def run_input_validation() -> None:

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 80)
    print("PHASE 9 — STEP 6 INPUT VALIDATION")
    print("=" * 80)

    datasets = load_all_datasets()

    validation_records = []
    statistics_records = []

    for dataset_name, df in datasets.items():

        print(
            f"Validating: {dataset_name}"
        )

        validation_record, dataset_statistics = (
            validate_dataset(
                dataset_name,
                df,
            )
        )

        validation_records.append(
            validation_record
        )

        statistics_records.extend(
            dataset_statistics
        )

    validation_df = pd.DataFrame(
        validation_records
    )

    statistics_df = pd.DataFrame(
        statistics_records
    )

    # -------------------------------------------------------------------------
    # Save validation report
    # -------------------------------------------------------------------------

    validation_df.to_csv(
        VALIDATION_FILE,
        index=False,
    )

    # -------------------------------------------------------------------------
    # Save column-level statistics
    # -------------------------------------------------------------------------

    statistics_df.to_csv(
        STATISTICS_FILE,
        index=False,
    )

    # -------------------------------------------------------------------------
    # Print summary
    # -------------------------------------------------------------------------

    print()
    print("=" * 80)
    print("PHASE 9 INPUT VALIDATION SUMMARY")
    print("=" * 80)

    print(
        validation_df[
            [
                "dataset",
                "row_count",
                "column_count",
                "null_cells",
                "duplicate_rows",
                "key_columns",
                "key_null_rows",
                "duplicate_key_rows",
                "key_unique",
                "minimum_date",
                "maximum_date",
            ]
        ].to_string(index=False)
    )

    print()
    print(
        f"Validation report: {VALIDATION_FILE}"
    )

    print(
        f"Dataset statistics: {STATISTICS_FILE}"
    )

    print()
    print("=" * 80)
    print("STEP 6 INPUT VALIDATION COMPLETE")
    print("=" * 80)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    run_input_validation()