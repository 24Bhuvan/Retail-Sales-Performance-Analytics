"""
Phase 4 — Data Quality Assessment
Step 2 — Completeness Assessment

Purpose
-------
Validate missing-value observations identified during Phase 3.

Checks:
1. NULL count for every column
2. NULL percentage for every column
3. Primary-key completeness
4. Required-field completeness
5. Important analytical field completeness
6. Validation of known Phase 3 missing-value findings

Important
---------
Missing values are reported as data-quality findings, but they are not
automatically classified as errors.

For example:
- Missing review comments are expected/optional fields.
- Missing delivery dates can occur for orders that were not delivered.
- Missing product category information is a completeness finding.
- Missing primary-key values are a structural quality violation.

The script does not invent business rules unsupported by the Olist data.
"""

from pathlib import Path
import pandas as pd


# =============================================================================
# 1. PROJECT PATHS
# =============================================================================

# Project root:
# Retail-Sales-Performance-Analytics/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"

REPORT_DIR = PROJECT_ROOT / "reports" / "data_quality"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = REPORT_DIR / "02_completeness_assessment.csv"


# =============================================================================
# 2. DATASET DEFINITIONS
# =============================================================================

DATASETS = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "product_category_name_translation":
        "product_category_name_translation.csv",
}


# =============================================================================
# 3. PRIMARY KEYS
# =============================================================================

# Primary keys identified during Phase 2 / Phase 3.

PRIMARY_KEYS = {
    "customers": ["customer_id"],

    "orders": ["order_id"],

    "order_items": [
        "order_id",
        "order_item_id",
    ],

    "order_payments": [
        "order_id",
        "payment_sequential",
    ],

    "order_reviews": ["review_id"],

    "products": ["product_id"],

    "sellers": ["seller_id"],

    "product_category_name_translation": [
        "product_category_name",
    ],

    # Geolocation has no defined primary key.
    "geolocation": [],
}


# =============================================================================
# 4. IMPORTANT ANALYTICAL FIELDS
# =============================================================================

# These fields are important for downstream analysis, but missingness does
# not automatically mean that the record is invalid.

IMPORTANT_FIELDS = {
    "customers": [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ],

    "geolocation": [
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state",
    ],

    "order_items": [
        "order_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
    ],

    "order_payments": [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value",
    ],

    "order_reviews": [
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
    ],

    "orders": [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],

    "products": [
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ],

    "sellers": [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ],

    "product_category_name_translation": [
        "product_category_name",
        "product_category_name_english",
    ],
}


# =============================================================================
# 5. REQUIRED FIELDS
# =============================================================================

# Required fields are structural identifiers.
#
# We deliberately do NOT classify all analytical columns as required.
# Optional/conditional fields can legitimately contain NULLs.

REQUIRED_FIELDS = {
    dataset: key_columns
    for dataset, key_columns in PRIMARY_KEYS.items()
}


# =============================================================================
# 6. PHASE 3 EXPECTED FINDINGS
# =============================================================================

# These values come directly from the Phase 3 profile supplied for this
# project. Step 2 validates whether the same missing-value findings exist
# when the raw data is reassessed.

PHASE_3_EXPECTED_MISSING = {
    ("order_reviews", "review_comment_title"): 87656,
    ("order_reviews", "review_comment_message"): 58247,

    ("orders", "order_approved_at"): 160,
    ("orders", "order_delivered_carrier_date"): 1783,
    ("orders", "order_delivered_customer_date"): 2965,

    ("products", "product_category_name"): 610,
    ("products", "product_name_lenght"): 610,
    ("products", "product_description_lenght"): 610,
    ("products", "product_photos_qty"): 610,

    ("products", "product_weight_g"): 2,
    ("products", "product_length_cm"): 2,
    ("products", "product_height_cm"): 2,
    ("products", "product_width_cm"): 2,
}


# =============================================================================
# 7. DATASET LOADER
# =============================================================================

def load_dataset(dataset_name: str, filename: str) -> pd.DataFrame:
    """
    Load one Olist CSV dataset.

    Parameters
    ----------
    dataset_name : str
        Internal dataset name.
    filename : str
        CSV filename.

    Returns
    -------
    pd.DataFrame
        Loaded dataset.
    """

    file_path = RAW_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n"
            f"  Dataset : {dataset_name}\n"
            f"  Path    : {file_path}"
        )

    print(f"Loading: {dataset_name}")
    print(f"  File: {file_path}")

    return pd.read_csv(
        file_path,
        low_memory=False,
    )


# =============================================================================
# 8. NULL PROFILE
# =============================================================================

def profile_column_missingness(
    dataset_name: str,
    df: pd.DataFrame,
) -> list[dict]:
    """
    Calculate NULL count and NULL percentage for every column.
    """

    total_rows = len(df)

    results = []

    for column in df.columns:

        null_count = int(df[column].isna().sum())

        if total_rows > 0:
            null_percentage = (null_count / total_rows) * 100
        else:
            null_percentage = 0.0

        results.append(
            {
                "dataset": dataset_name,
                "column": column,
                "total_rows": total_rows,
                "null_count": null_count,
                "null_percentage": round(null_percentage, 4),
                "field_type": (
                    "Primary Key"
                    if column in PRIMARY_KEYS.get(dataset_name, [])
                    else (
                        "Important Analytical Field"
                        if column in IMPORTANT_FIELDS.get(dataset_name, [])
                        else "Other Field"
                    )
                ),
            }
        )

    return results


# =============================================================================
# 9. PRIMARY-KEY COMPLETENESS
# =============================================================================

def check_primary_key_completeness(
    dataset_name: str,
    df: pd.DataFrame,
) -> list[dict]:
    """
    Check NULL values in every component of the defined primary key.
    """

    results = []

    primary_keys = PRIMARY_KEYS.get(dataset_name, [])

    # Geolocation has no defined PK.
    if not primary_keys:
        return results

    for key_column in primary_keys:

        if key_column not in df.columns:
            results.append(
                {
                    "dataset": dataset_name,
                    "column": key_column,
                    "total_rows": len(df),
                    "null_count": None,
                    "null_percentage": None,
                    "field_type": "Primary Key",
                    "status": "FAIL — KEY COLUMN MISSING",
                    "classification": "Structural Issue",
                    "phase_3_expected_nulls": None,
                    "phase_3_validation": "Not testable",
                }
            )

            continue

        null_count = int(df[key_column].isna().sum())

        null_percentage = (
            (null_count / len(df)) * 100
            if len(df) > 0
            else 0
        )

        if null_count == 0:
            status = "PASS"
            classification = "Pass"
        else:
            status = "FAIL"
            classification = "Confirmed Quality Issue"

        results.append(
            {
                "dataset": dataset_name,
                "column": key_column,
                "total_rows": len(df),
                "null_count": null_count,
                "null_percentage": round(null_percentage, 4),
                "field_type": "Primary Key",
                "status": status,
                "classification": classification,
                "phase_3_expected_nulls": 0,
                "phase_3_validation": (
                    "Confirmed"
                    if null_count == 0
                    else "Different from Phase 3"
                ),
            }
        )

    return results


# =============================================================================
# 10. REQUIRED-FIELD CHECK
# =============================================================================

def check_required_fields(
    dataset_name: str,
    df: pd.DataFrame,
) -> list[dict]:
    """
    Check completeness of required fields.

    Required fields currently correspond to defined PK components.
    """

    results = []

    required_fields = REQUIRED_FIELDS.get(dataset_name, [])

    for column in required_fields:

        if column not in df.columns:
            results.append(
                {
                    "dataset": dataset_name,
                    "column": column,
                    "total_rows": len(df),
                    "null_count": None,
                    "null_percentage": None,
                    "field_type": "Required Field",
                    "status": "FAIL — COLUMN MISSING",
                    "classification": "Structural Issue",
                    "phase_3_expected_nulls": None,
                    "phase_3_validation": "Not testable",
                }
            )

            continue

        null_count = int(df[column].isna().sum())

        null_percentage = (
            (null_count / len(df)) * 100
            if len(df) > 0
            else 0
        )

        results.append(
            {
                "dataset": dataset_name,
                "column": column,
                "total_rows": len(df),
                "null_count": null_count,
                "null_percentage": round(null_percentage, 4),
                "field_type": "Required Field",
                "status": "PASS" if null_count == 0 else "FAIL",
                "classification": (
                    "Pass"
                    if null_count == 0
                    else "Confirmed Quality Issue"
                ),
                "phase_3_expected_nulls": 0,
                "phase_3_validation": (
                    "Confirmed"
                    if null_count == 0
                    else "Different from Phase 3"
                ),
            }
        )

    return results


# =============================================================================
# 11. PHASE 3 VALIDATION
# =============================================================================

def validate_phase_3_finding(
    dataset_name: str,
    column: str,
    actual_null_count: int,
) -> dict:
    """
    Validate a known Phase 3 missing-value finding.
    """

    expected = PHASE_3_EXPECTED_MISSING.get(
        (dataset_name, column)
    )

    if expected is None:
        return {
            "phase_3_expected_nulls": None,
            "phase_3_validation": "Not a Phase 3 tracked finding",
        }

    if actual_null_count == expected:
        validation = "Confirmed"
    else:
        validation = "Changed — investigate"

    return {
        "phase_3_expected_nulls": expected,
        "phase_3_validation": validation,
    }


# =============================================================================
# 12. CLASSIFICATION
# =============================================================================

def classify_missingness(
    dataset_name: str,
    column: str,
    null_count: int,
) -> tuple[str, str]:
    """
    Classify missingness according to the Step 2 rules.

    Important:
    Missingness is not automatically an error.

    Review comments are explicitly treated as optional observations.
    """

    if null_count == 0:
        return "Pass", "No Missing Values"

    # Optional review comment fields.
    if (
        dataset_name == "order_reviews"
        and column in {
            "review_comment_title",
            "review_comment_message",
        }
    ):
        return (
            "Observation",
            "Optional / Sparse Field"
        )

    # Primary key fields.
    if column in PRIMARY_KEYS.get(dataset_name, []):
        return (
            "Confirmed Quality Issue",
            "Missing Primary-Key Value"
        )

    # Other missing analytical fields.
    return (
        "Observation",
        "Missing Value"
    )


# =============================================================================
# 13. CONSOLIDATED ASSESSMENT
# =============================================================================

def assess_dataset(
    dataset_name: str,
    df: pd.DataFrame,
) -> list[dict]:
    """
    Perform complete completeness assessment for one dataset.
    """

    results = []

    total_rows = len(df)

    for column in df.columns:

        null_count = int(df[column].isna().sum())

        null_percentage = (
            (null_count / total_rows) * 100
            if total_rows > 0
            else 0
        )

        classification, finding_type = classify_missingness(
            dataset_name,
            column,
            null_count,
        )

        phase_3_validation = validate_phase_3_finding(
            dataset_name,
            column,
            null_count,
        )

        field_type = (
            "Primary Key"
            if column in PRIMARY_KEYS.get(dataset_name, [])
            else (
                "Important Analytical Field"
                if column in IMPORTANT_FIELDS.get(dataset_name, [])
                else "Other Field"
            )
        )

        results.append(
            {
                "dataset": dataset_name,
                "column": column,
                "total_rows": total_rows,
                "null_count": null_count,
                "null_percentage": round(null_percentage, 4),
                "field_type": field_type,
                "finding_type": finding_type,
                "classification": classification,
                "phase_3_expected_nulls":
                    phase_3_validation["phase_3_expected_nulls"],
                "phase_3_validation":
                    phase_3_validation["phase_3_validation"],
            }
        )

    return results


# =============================================================================
# 14. SUMMARY
# =============================================================================

def print_summary(report_df: pd.DataFrame) -> None:
    """
    Print a concise completeness assessment summary.
    """

    print("\n")
    print("=" * 80)
    print("PHASE 4 — STEP 2: COMPLETENESS ASSESSMENT")
    print("=" * 80)

    print(
        f"Datasets assessed : "
        f"{report_df['dataset'].nunique()}"
    )

    print(
        f"Columns assessed  : "
        f"{len(report_df):,}"
    )

    missing_columns = report_df[
        report_df["null_count"] > 0
    ]

    print(
        f"Columns with NULLs: "
        f"{len(missing_columns):,}"
    )

    confirmed = report_df[
        report_df["classification"] == "Confirmed Quality Issue"
    ]

    observations = report_df[
        report_df["classification"] == "Observation"
    ]

    print(
        f"Confirmed quality issues : "
        f"{len(confirmed):,}"
    )

    print(
        f"Missing-value observations: "
        f"{len(observations):,}"
    )

    print("\n")
    print("FIELDS WITH MISSING VALUES")
    print("-" * 80)

    if missing_columns.empty:
        print("No missing values detected.")
    else:

        display_columns = [
            "dataset",
            "column",
            "null_count",
            "null_percentage",
            "field_type",
            "classification",
        ]

        print(
            missing_columns[
                display_columns
            ].to_string(index=False)
        )

    print("\n")
    print("PHASE 3 VALIDATION")
    print("-" * 80)

    tracked = report_df[
        report_df["phase_3_expected_nulls"].notna()
    ]

    if tracked.empty:
        print("No Phase 3 findings configured.")
    else:

        display_columns = [
            "dataset",
            "column",
            "null_count",
            "phase_3_expected_nulls",
            "phase_3_validation",
        ]

        print(
            tracked[
                display_columns
            ].to_string(index=False)
        )

    print("\n")
    print("=" * 80)
    print("Assessment complete.")
    print("=" * 80)


# =============================================================================
# 15. MAIN
# =============================================================================

def main() -> None:
    """
    Execute the complete Step 2 assessment.
    """

    print("=" * 80)
    print("PHASE 4 — STEP 2: COMPLETENESS ASSESSMENT")
    print("=" * 80)

    print(f"Project root : {PROJECT_ROOT}")
    print(f"Raw data     : {RAW_DIR}")
    print(f"Output       : {OUTPUT_FILE}")
    print()

    all_results = []

    # -------------------------------------------------------------------------
    # Load and assess all datasets
    # -------------------------------------------------------------------------

    for dataset_name, filename in DATASETS.items():

        try:
            df = load_dataset(
                dataset_name,
                filename,
            )

            dataset_results = assess_dataset(
                dataset_name,
                df,
            )

            all_results.extend(dataset_results)

            print(
                f"  Rows: {len(df):,} | "
                f"Columns: {len(df.columns)}"
            )

        except FileNotFoundError as error:

            print()
            print(f"ERROR: {error}")
            print()

            # Continue with remaining datasets rather than stopping the
            # complete assessment.
            continue

        except Exception as error:

            print(
                f"ERROR processing {dataset_name}: "
                f"{type(error).__name__}: {error}"
            )

            continue

    # -------------------------------------------------------------------------
    # Create consolidated report
    # -------------------------------------------------------------------------

    if not all_results:
        raise RuntimeError(
            "No datasets were successfully assessed."
        )

    report_df = pd.DataFrame(all_results)

    # Stable column ordering.
    report_df = report_df[
        [
            "dataset",
            "column",
            "total_rows",
            "null_count",
            "null_percentage",
            "field_type",
            "finding_type",
            "classification",
            "phase_3_expected_nulls",
            "phase_3_validation",
        ]
    ]

    # Sort by dataset and highest missingness first.
    report_df = report_df.sort_values(
        by=[
            "dataset",
            "null_count",
            "column",
        ],
        ascending=[
            True,
            False,
            True,
        ],
    )

    # Save CSV.
    report_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print(f"Report saved to:")
    print(f"  {OUTPUT_FILE}")

    # -------------------------------------------------------------------------
    # Print summary
    # -------------------------------------------------------------------------

    print_summary(report_df)


if __name__ == "__main__":
    main()