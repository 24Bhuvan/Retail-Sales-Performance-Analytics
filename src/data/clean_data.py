"""
Retail Sales Performance Analytics
Phase 5 — Data Cleaning Strategy

File:
    src/data/clean_data.py

Purpose:
    Execute the dataset-specific Phase 5 cleaning pipeline using the
    findings from Phase 4 — Data Quality Assessment.

Design principles:
    1. Raw data is NEVER modified.
    2. Legitimate NULL values are preserved.
    3. No unsupported values are fabricated.
    4. Referential integrity is preserved.
    5. Exact duplicate geolocation rows are removed.
    6. review_id duplicates are NOT removed because review_id is not
       a unique identifier in the source model.
    7. Invalid chronology timestamps are nullified rather than
       arbitrarily rewritten.
    8. Valid zero values are preserved.
    9. Every transformation is logged.
    10. Before/after statistics are generated.

Outputs:
    data/cleaned/*.csv
    reports/data_cleaning/cleaning_log.csv
    reports/data_cleaning/cleaning_summary.json
    reports/data_cleaning/cleaning_dataset_summary.csv
    reports/data_cleaning/cleaning_execution.log
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable

import pandas as pd

from preprocess import preprocess_dataset


# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
REPORT_DIR = PROJECT_ROOT / "reports" / "data_cleaning"

CLEANING_LOG_FILE = REPORT_DIR / "cleaning_log.csv"
CLEANING_SUMMARY_FILE = REPORT_DIR / "cleaning_summary.json"
DATASET_SUMMARY_FILE = REPORT_DIR / "cleaning_dataset_summary.csv"
EXECUTION_LOG_FILE = REPORT_DIR / "cleaning_execution.log"


# =============================================================================
# DATASET FILES
# =============================================================================

DATASET_FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


# =============================================================================
# LOGGING
# =============================================================================

def configure_logging() -> logging.Logger:
    """
    Configure file and console logging for the Phase 5 pipeline.
    """

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("phase5_cleaning")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(
        EXECUTION_LOG_FILE,
        mode="w",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


LOGGER = configure_logging()


# =============================================================================
# CLEANING LOG
# =============================================================================

cleaning_actions: list[dict] = []


def log_action(
    *,
    dataset: str,
    column: str,
    issue: str,
    rule: str,
    action: str,
    rows_affected: int,
    rows_before: int,
    rows_after: int,
    rationale: str,
    status: str = "APPLIED",
) -> None:
    """
    Record one cleaning action.
    """

    cleaning_actions.append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "dataset": dataset,
            "column": column,
            "issue": issue,
            "rule": rule,
            "action": action,
            "rows_affected": int(rows_affected),
            "rows_before": int(rows_before),
            "rows_after": int(rows_after),
            "rationale": rationale,
            "status": status,
        }
    )


# =============================================================================
# GENERAL HELPERS
# =============================================================================

def ensure_output_directories() -> None:
    """Create Phase 5 output directories."""

    CLEANED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def load_raw_dataset(dataset_name: str) -> pd.DataFrame:
    """
    Load one raw Olist dataset.

    Raw files are read-only inputs.
    """

    filename = DATASET_FILES[dataset_name]
    filepath = RAW_DIR / filename

    if not filepath.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {filepath}"
        )

    LOGGER.info(
        "Loading raw dataset | %s | %s",
        dataset_name,
        filepath,
    )

    return pd.read_csv(
        filepath,
        low_memory=False,
    )


def save_cleaned_dataset(
    dataset_name: str,
    df: pd.DataFrame,
) -> Path:
    """
    Save cleaned dataset to data/cleaned/.
    """

    filename = DATASET_FILES[dataset_name]
    output_path = CLEANED_DIR / filename

    df.to_csv(
        output_path,
        index=False,
    )

    LOGGER.info(
        "Saved cleaned dataset | %s | rows=%s | path=%s",
        dataset_name,
        len(df),
        output_path,
    )

    return output_path


def count_nulls(df: pd.DataFrame) -> int:
    """Return total NULL cells."""

    return int(df.isna().sum().sum())


def count_full_row_duplicates(df: pd.DataFrame) -> int:
    """Return number of rows that are exact duplicates excluding first occurrence."""

    return int(
        df.duplicated(keep="first").sum()
    )


# =============================================================================
# GENERIC PREPROCESSING
# =============================================================================

def apply_generic_preprocessing(
    dataset_name: str,
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Apply reusable preprocessing functions from preprocess.py.

    This performs:
        - NULL representation normalization
        - datatype normalization
        - timestamp parsing
        - numeric conversion
        - text normalization
        - categorical normalization

    No business-specific records are removed here.
    """

    rows_before = len(df)

    processed = preprocess_dataset(
        df,
        dataset_name,
    )

    rows_after = len(processed)

    if rows_before != rows_after:
        raise RuntimeError(
            f"Generic preprocessing changed row count for "
            f"{dataset_name}: {rows_before} -> {rows_after}"
        )

    log_action(
        dataset=dataset_name,
        column="__DATASET__",
        issue="Generic preprocessing",
        rule="Normalize data types, timestamps, numerics, text, categories and NULL representations",
        action="PREPROCESS",
        rows_affected=rows_before,
        rows_before=rows_before,
        rows_after=rows_after,
        rationale=(
            "Apply reusable preprocessing without deleting records "
            "or imputing business values."
        ),
    )

    return processed


# =============================================================================
# CUSTOMERS
# =============================================================================

def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean customers dataset.

    Phase 4:
        - No PK NULLs
        - No PK duplicates
        - No invalid states
        - 278 customer ZIP prefixes without geolocation matches

    Treatment:
        - Preserve all customers.
        - Preserve unmatched ZIP prefixes.
        - Standardize text/dtypes only.
    """

    before = len(df)

    df = apply_generic_preprocessing(
        "customers",
        df,
    )

    # The ZIP/geolocation mismatch does not invalidate the customer record.
    # Geolocation is an enrichment/reference dataset.
    unmatched_count = 278

    log_action(
        dataset="customers",
        column="customer_zip_code_prefix",
        issue="ZIP prefix without geolocation match",
        rule="Customer records must not be removed solely because geolocation enrichment is unavailable",
        action="RETAIN",
        rows_affected=unmatched_count,
        rows_before=before,
        rows_after=len(df),
        rationale=(
            "Geolocation is a reference/enrichment source. "
            "An unmatched ZIP prefix does not invalidate the customer record."
        ),
    )

    return df


# =============================================================================
# GEOLOCATION
# =============================================================================

def clean_geolocation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean geolocation dataset.

    Phase 4:
        DQ-GEO-001 identified 390,005 rows participating in exact
        duplicate groups.

    Treatment:
        Remove exact full-row duplicates.
    """

    before = len(df)

    df = apply_generic_preprocessing(
        "geolocation",
        df,
    )

    duplicate_count = count_full_row_duplicates(df)

    if duplicate_count > 0:
        df = df.drop_duplicates(
            keep="first"
        ).reset_index(drop=True)

    removed = before - len(df)

    log_action(
        dataset="geolocation",
        column="__FULL_ROW__",
        issue="Exact full-row duplicates",
        rule="Remove exact duplicate geolocation records while retaining one occurrence",
        action="DEDUPLICATE",
        rows_affected=removed,
        rows_before=before,
        rows_after=len(df),
        rationale=(
            "Geolocation is a reference/enrichment dataset without a "
            "source primary key. Exact duplicate rows provide no additional "
            "analytical information."
        ),
    )

    return df


# =============================================================================
# ORDERS
# =============================================================================

def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean orders dataset.

    Phase 4 findings:
        - 166 carrier timestamps occur before purchase timestamp.
        - 23 customer delivery timestamps occur before carrier handover.
        - 8 delivered orders lack customer delivery timestamp.
        - 2 delivered orders lack carrier handover timestamp.
        - Other PK/FK/date checks pass.

    Treatment:
        - Do not delete affected orders.
        - Nullify timestamps that violate chronology.
        - Preserve legitimate NULL delivery timestamps.
        - Preserve all valid orders.
    """

    before = len(df)

    df = apply_generic_preprocessing(
        "orders",
        df,
    )

    # -------------------------------------------------------------------------
    # DQ-DATE-002
    # Carrier handover cannot occur before purchase.
    # -------------------------------------------------------------------------

    carrier_invalid_mask = (
        df["order_delivered_carrier_date"].notna()
        & df["order_purchase_timestamp"].notna()
        & (
            df["order_delivered_carrier_date"]
            < df["order_purchase_timestamp"]
        )
    )

    carrier_invalid_count = int(
        carrier_invalid_mask.sum()
    )

    if carrier_invalid_count > 0:
        df.loc[
            carrier_invalid_mask,
            "order_delivered_carrier_date",
        ] = pd.NaT

    log_action(
        dataset="orders",
        column="order_delivered_carrier_date",
        issue="Carrier date before purchase timestamp",
        rule="order_delivered_carrier_date must be >= order_purchase_timestamp",
        action="SET_INVALID_TIMESTAMP_TO_NULL",
        rows_affected=carrier_invalid_count,
        rows_before=before,
        rows_after=len(df),
        rationale=(
            "The timestamp violates chronological integrity. "
            "The source does not provide enough information to infer "
            "the correct timestamp, so the invalid value is removed "
            "rather than fabricated."
        ),
    )

    # -------------------------------------------------------------------------
    # DQ-DATE-004
    # Customer delivery cannot occur before carrier handover.
    # -------------------------------------------------------------------------

    customer_delivery_invalid_mask = (
        df["order_delivered_customer_date"].notna()
        & df["order_delivered_carrier_date"].notna()
        & (
            df["order_delivered_customer_date"]
            < df["order_delivered_carrier_date"]
        )
    )

    customer_delivery_invalid_count = int(
        customer_delivery_invalid_mask.sum()
    )

    if customer_delivery_invalid_count > 0:
        df.loc[
            customer_delivery_invalid_mask,
            "order_delivered_customer_date",
        ] = pd.NaT

    log_action(
        dataset="orders",
        column="order_delivered_customer_date",
        issue="Customer delivery before carrier handover",
        rule="order_delivered_customer_date must be >= order_delivered_carrier_date",
        action="SET_INVALID_TIMESTAMP_TO_NULL",
        rows_affected=customer_delivery_invalid_count,
        rows_before=before,
        rows_after=len(df),
        rationale=(
            "The delivery timestamp violates chronological integrity. "
            "The correct timestamp cannot be safely inferred from the "
            "available source fields."
        ),
    )

    # -------------------------------------------------------------------------
    # DQ-BIZ-001
    # Delivered orders without customer delivery timestamp.
    # -------------------------------------------------------------------------

    delivered_missing_customer_date = (
        (df["order_status"] == "delivered")
        & df["order_delivered_customer_date"].isna()
    )

    delivered_missing_customer_count = int(
        delivered_missing_customer_date.sum()
    )

    log_action(
        dataset="orders",
        column="order_delivered_customer_date",
        issue="Delivered order missing customer delivery timestamp",
        rule="Delivered status normally implies a customer delivery timestamp",
        action="RETAIN_NULL",
        rows_affected=delivered_missing_customer_count,
        rows_before=before,
        rows_after=len(df),
        rationale=(
            "The source does not provide a reliable value for the missing "
            "timestamp. No timestamp is fabricated and the order is not "
            "deleted solely because the delivery timestamp is missing."
        ),
    )

    # -------------------------------------------------------------------------
    # DQ-BIZ-002
    # Delivered orders without carrier timestamp.
    # -------------------------------------------------------------------------

    delivered_missing_carrier_date = (
        (df["order_status"] == "delivered")
        & df["order_delivered_carrier_date"].isna()
    )

    delivered_missing_carrier_count = int(
        delivered_missing_carrier_date.sum()
    )

    log_action(
        dataset="orders",
        column="order_delivered_carrier_date",
        issue="Delivered order missing carrier handover timestamp",
        rule="Delivered status normally implies a carrier handover timestamp",
        action="RETAIN_NULL",
        rows_affected=delivered_missing_carrier_count,
        rows_before=before,
        rows_after=len(df),
        rationale=(
            "The missing timestamp cannot be reliably reconstructed. "
            "The transaction remains valid and is retained."
        ),
    )

    return df


# =============================================================================
# ORDER ITEMS
# =============================================================================

def clean_order_items(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean order_items dataset.

    Phase 4:
        - No PK/FK NULLs
        - No duplicate composite keys
        - No orphan order references
        - No orphan product references
        - No orphan seller references
        - No negative price
        - No negative freight

    Zero freight values are retained.
    """

    before = len(df)

    df = apply_generic_preprocessing(
        "order_items",
        df,
    )

    zero_freight_count = int(
        (df["freight_value"] == 0).sum()
    )

    log_action(
        dataset="order_items",
        column="freight_value",
        issue="Zero freight value",
        rule="Zero freight is not inherently invalid",
        action="RETAIN",
        rows_affected=zero_freight_count,
        rows_before=before,
        rows_after=len(df),
        rationale=(
            "Phase 4 identified zero freight values but no negative "
            "freight values. Zero can represent a legitimate freight charge."
        ),
    )

    return df


# =============================================================================
# PAYMENTS
# =============================================================================

def clean_payments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean payments dataset.

    Phase 4:
        - No orphan order references
        - No negative payment values
        - 2 payment records have zero installments
        - 9 payment records have zero payment value

    Treatment:
        - Set invalid zero installments to NULL.
        - Preserve zero payment values.
        - Preserve all payment rows.
    """

    before = len(df)

    df = apply_generic_preprocessing(
        "payments",
        df,
    )

    zero_installment_mask = (
        df["payment_installments"] == 0
    )

    zero_installment_count = int(
        zero_installment_mask.sum()
    )

    if zero_installment_count > 0:
        df.loc[
            zero_installment_mask,
            "payment_installments",
        ] = pd.NA

    log_action(
        dataset="payments",
        column="payment_installments",
        issue="Zero payment installments",
        rule="payment_installments must be greater than zero",
        action="SET_INVALID_VALUE_TO_NULL",
        rows_affected=zero_installment_count,
        rows_before=before,
        rows_after=len(df),
        rationale=(
            "Zero installments violates the business rule. "
            "The source does not provide enough information to infer "
            "the correct installment count, so the invalid value is "
            "converted to NULL rather than fabricated."
        ),
    )

    zero_payment_value_count = int(
        (df["payment_value"] == 0).sum()
    )

    log_action(
        dataset="payments",
        column="payment_value",
        issue="Zero payment value",
        rule="Zero payment value is not prohibited by the Phase 4 validity rules",
        action="RETAIN",
        rows_affected=zero_payment_value_count,
        rows_before=before,
        rows_after=len(df),
        rationale=(
            "Phase 4 only identified negative payment values as invalid. "
            "Zero payment values are therefore preserved."
        ),
    )

    return df


# =============================================================================
# REVIEWS
# =============================================================================

def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean reviews dataset.

    Phase 4:
        789 duplicate review_id groups.

    Phase 2 model:
        review_id is explicitly documented as NOT unique.

    Treatment:
        - Do NOT deduplicate using review_id.
        - Preserve all review records.
        - Preserve legitimate NULL review comments.
        - Remove only exact full-row duplicates if they exist.
    """

    before = len(df)

    df = apply_generic_preprocessing(
        "reviews",
        df,
    )

    review_id_duplicate_groups = int(
        df.loc[
            df["review_id"].duplicated(keep=False),
            "review_id",
        ].nunique()
    )

    log_action(
        dataset="reviews",
        column="review_id",
        issue="Duplicate review_id groups",
        rule="review_id is not a unique source identifier",
        action="RETAIN",
        rows_affected=review_id_duplicate_groups,
        rows_before=before,
        rows_after=len(df),
        rationale=(
            "Phase 2 documentation explicitly identifies review_id as "
            "non-unique. Removing records by review_id would incorrectly "
            "discard legitimate review records."
        ),
    )

    exact_duplicate_count = count_full_row_duplicates(df)

    if exact_duplicate_count > 0:
        df = df.drop_duplicates(
            keep="first"
        ).reset_index(drop=True)

    exact_duplicates_removed = (
        before - len(df)
        if exact_duplicate_count > 0
        else 0
    )

    log_action(
        dataset="reviews",
        column="__FULL_ROW__",
        issue="Exact full-row duplicates",
        rule="Remove only exact duplicate review records",
        action="DEDUPLICATE",
        rows_affected=exact_duplicates_removed,
        rows_before=before,
        rows_after=len(df),
        rationale=(
            "Exact duplicate rows contain no additional information. "
            "This is distinct from duplicate review_id values."
        ),
    )

    # Review comments can legitimately be NULL.
    comment_columns = [
        "review_comment_title",
        "review_comment_message",
    ]

    for column in comment_columns:
        if column not in df.columns:
            continue

        null_count = int(
            df[column].isna().sum()
        )

        log_action(
            dataset="reviews",
            column=column,
            issue="Missing review text",
            rule="Review comment fields may legitimately be NULL",
            action="RETAIN_NULL",
            rows_affected=null_count,
            rows_before=before,
            rows_after=len(df),
            rationale=(
                "Missing review text does not invalidate the review score "
                "or order relationship. No artificial text is created."
            ),
        )

    return df


# =============================================================================
# PRODUCTS
# =============================================================================

def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean products dataset.

    Phase 4:
        - 610 missing product categories
        - Missing descriptive/physical attributes
        - Zero product weights
        - No negative physical measurements
        - No duplicate product IDs
        - No NULL product IDs

    Treatment:
        - Preserve unknown category as NULL.
        - Do not invent categories.
        - Preserve legitimate zero values.
        - Preserve missing descriptive/physical attributes.
    """

    before = len(df)

    df = apply_generic_preprocessing(
        "products",
        df,
    )

    # -------------------------------------------------------------------------
    # Product category
    # -------------------------------------------------------------------------

    missing_category_count = int(
        df["product_category_name"].isna().sum()
    )

    log_action(
        dataset="products",
        column="product_category_name",
        issue="Missing product category",
        rule="Do not fabricate a category when the source category is unavailable",
        action="RETAIN_NULL",
        rows_affected=missing_category_count,
        rows_before=before,
        rows_after=len(df),
        rationale=(
            "There is no reliable source field from which the missing "
            "category can be inferred. NULL is retained to preserve source truth."
        ),
    )

    # -------------------------------------------------------------------------
    # Missing descriptive/physical attributes
    # -------------------------------------------------------------------------

    nullable_product_columns = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]

    for column in nullable_product_columns:
        if column not in df.columns:
            continue

        null_count = int(
            df[column].isna().sum()
        )

        if null_count == 0:
            continue

        log_action(
            dataset="products",
            column=column,
            issue="Missing product attribute",
            rule="Retain missing attribute when no reliable source value exists",
            action="RETAIN_NULL",
            rows_affected=null_count,
            rows_before=before,
            rows_after=len(df),
            rationale=(
                "No supported source-based value is available for safe "
                "imputation. The product record remains valid."
            ),
        )

    # -------------------------------------------------------------------------
    # Zero product weight
    # -------------------------------------------------------------------------

    zero_weight_count = int(
        (df["product_weight_g"] == 0).sum()
    )

    log_action(
        dataset="products",
        column="product_weight_g",
        issue="Zero product weight",
        rule="Do not automatically classify zero as invalid without source evidence",
        action="RETAIN",
        rows_affected=zero_weight_count,
        rows_before=before,
        rows_after=len(df),
        rationale=(
            "Phase 4 identified zero values but did not classify them as "
            "negative or otherwise invalid. They are retained."
        ),
    )

    return df


# =============================================================================
# SELLERS
# =============================================================================

def clean_sellers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean sellers dataset.

    Phase 4:
        - No seller ID NULLs
        - No seller ID duplicates
        - No invalid states
        - 7 ZIP prefixes without geolocation matches

    Treatment:
        Preserve all seller records.
    """

    before = len(df)

    df = apply_generic_preprocessing(
        "sellers",
        df,
    )

    unmatched_count = 7

    log_action(
        dataset="sellers",
        column="seller_zip_code_prefix",
        issue="ZIP prefix without geolocation match",
        rule="Seller records must not be removed solely because geolocation enrichment is unavailable",
        action="RETAIN",
        rows_affected=unmatched_count,
        rows_before=before,
        rows_after=len(df),
        rationale=(
            "Geolocation is an enrichment/reference source. "
            "An unmatched ZIP prefix does not invalidate the seller."
        ),
    )

    return df


# =============================================================================
# CATEGORY TRANSLATION
# =============================================================================

def clean_category_translation(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Clean product category translation dataset.

    Phase 4:
        - 71 rows
        - No NULL category values
        - No duplicate source categories
        - Translation coverage gaps exist for 2 categories

    Treatment:
        - Standardize text.
        - Preserve only validated mappings.
        - Do not invent missing translations.
    """

    before = len(df)

    df = apply_generic_preprocessing(
        "category_translation",
        df,
    )

    log_action(
        dataset="category_translation",
        column="product_category_name_english",
        issue="Missing translation coverage",
        rule="Do not fabricate English translations for categories absent from translation source",
        action="RETAIN_SOURCE_LIMITATION",
        rows_affected=2,
        rows_before=before,
        rows_after=len(df),
        rationale=(
            "The translation source contains 71 validated mappings. "
            "Missing mappings should remain unresolved rather than being "
            "assigned an invented English category."
        ),
        status="DOCUMENTED",
    )

    return df


# =============================================================================
# REFERENTIAL INTEGRITY VALIDATION
# =============================================================================

def validate_referential_integrity(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """
    Validate core relationships after cleaning.

    Relationships:
        orders.customer_id -> customers.customer_id
        order_items.order_id -> orders.order_id
        order_items.product_id -> products.product_id
        order_items.seller_id -> sellers.seller_id
        payments.order_id -> orders.order_id
        reviews.order_id -> orders.order_id
    """

    LOGGER.info(
        "Running post-cleaning referential integrity validation."
    )

    relationships = [
        (
            "orders",
            "customer_id",
            "customers",
            "customer_id",
        ),
        (
            "order_items",
            "order_id",
            "orders",
            "order_id",
        ),
        (
            "order_items",
            "product_id",
            "products",
            "product_id",
        ),
        (
            "order_items",
            "seller_id",
            "sellers",
            "seller_id",
        ),
        (
            "payments",
            "order_id",
            "orders",
            "order_id",
        ),
        (
            "reviews",
            "order_id",
            "orders",
            "order_id",
        ),
    ]

    for (
        child_dataset,
        child_column,
        parent_dataset,
        parent_column,
    ) in relationships:

        child = datasets[child_dataset]
        parent = datasets[parent_dataset]

        parent_values = set(
            parent[parent_column].dropna()
        )

        orphan_mask = (
            child[child_column].notna()
            & ~child[child_column].isin(parent_values)
        )

        orphan_count = int(
            orphan_mask.sum()
        )

        if orphan_count != 0:
            raise ValueError(
                "Referential integrity failure after cleaning: "
                f"{child_dataset}.{child_column} -> "
                f"{parent_dataset}.{parent_column}; "
                f"orphan rows={orphan_count}"
            )

        LOGGER.info(
            "FK validation PASS | %s.%s -> %s.%s",
            child_dataset,
            child_column,
            parent_dataset,
            parent_column,
        )


# =============================================================================
# PRIMARY KEY VALIDATION
# =============================================================================

def validate_primary_keys(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """
    Validate source primary/composite keys after cleaning.
    """

    key_definitions = {
        "customers": ["customer_id"],
        "orders": ["order_id"],
        "products": ["product_id"],
        "sellers": ["seller_id"],
        "order_items": [
            "order_id",
            "order_item_id",
        ],
        "payments": [
            "order_id",
            "payment_sequential",
        ],
        "category_translation": [
            "product_category_name",
        ],
    }

    for dataset_name, columns in key_definitions.items():

        df = datasets[dataset_name]

        missing_columns = [
            column
            for column in columns
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing key columns in {dataset_name}: "
                f"{missing_columns}"
            )

        null_key_rows = int(
            df[columns]
            .isna()
            .any(axis=1)
            .sum()
        )

        if null_key_rows > 0:
            raise ValueError(
                f"NULL key values remain in {dataset_name}: "
                f"{columns}; rows={null_key_rows}"
            )

        duplicate_key_rows = int(
            df.duplicated(
                subset=columns,
                keep=False,
            ).sum()
        )

        if duplicate_key_rows > 0:
            raise ValueError(
                f"Duplicate key rows remain in {dataset_name}: "
                f"{columns}; rows={duplicate_key_rows}"
            )

        LOGGER.info(
            "Primary key validation PASS | %s | %s",
            dataset_name,
            columns,
        )


# =============================================================================
# DATASET SUMMARY
# =============================================================================

def create_dataset_summary(
    before_data: dict[str, pd.DataFrame],
    after_data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Create before/after dataset statistics.
    """

    records = []

    for dataset_name in DATASET_FILES:

        before = before_data[dataset_name]
        after = after_data[dataset_name]

        records.append(
            {
                "dataset": dataset_name,
                "rows_before": len(before),
                "rows_after": len(after),
                "rows_removed": len(before) - len(after),
                "columns_before": len(before.columns),
                "columns_after": len(after.columns),
                "null_cells_before": count_nulls(before),
                "null_cells_after": count_nulls(after),
                "exact_duplicates_before": count_full_row_duplicates(before),
                "exact_duplicates_after": count_full_row_duplicates(after),
            }
        )

    return pd.DataFrame(records)


# =============================================================================
# SAVE CLEANING LOG
# =============================================================================

def save_cleaning_log() -> None:
    """
    Save all recorded cleaning actions.
    """

    if cleaning_actions:
        log_df = pd.DataFrame(
            cleaning_actions
        )
    else:
        log_df = pd.DataFrame(
            columns=[
                "timestamp",
                "dataset",
                "column",
                "issue",
                "rule",
                "action",
                "rows_affected",
                "rows_before",
                "rows_after",
                "rationale",
                "status",
            ]
        )

    log_df.to_csv(
        CLEANING_LOG_FILE,
        index=False,
    )

    LOGGER.info(
        "Cleaning log saved: %s",
        CLEANING_LOG_FILE,
    )


# =============================================================================
# SAVE SUMMARY JSON
# =============================================================================

def save_cleaning_summary(
    dataset_summary: pd.DataFrame,
) -> None:
    """
    Save high-level Phase 5 cleaning summary.
    """

    rows_before = int(
        dataset_summary["rows_before"].sum()
    )

    rows_after = int(
        dataset_summary["rows_after"].sum()
    )

    rows_removed = int(
        dataset_summary["rows_removed"].sum()
    )

    actions_applied = sum(
        1
        for action in cleaning_actions
        if action["status"] == "APPLIED"
    )

    summary = {
        "phase": "Phase 5 — Data Cleaning Strategy",
        "project": "Retail Sales Performance Analytics",
        "execution_timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
        "datasets_processed": len(DATASET_FILES),
        "total_rows_before": rows_before,
        "total_rows_after": rows_after,
        "total_rows_removed": rows_removed,
        "cleaning_actions_applied": actions_applied,
        "raw_data_modified": False,
        "cleaned_data_directory": str(CLEANED_DIR),
        "cleaning_log": str(CLEANING_LOG_FILE),
        "validation_status": "PENDING_FINAL_POST_CLEANING_VALIDATION",
    }

    with CLEANING_SUMMARY_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=4,
        )

    LOGGER.info(
        "Cleaning summary saved: %s",
        CLEANING_SUMMARY_FILE,
    )


# =============================================================================
# MAIN CLEANING PIPELINE
# =============================================================================

CLEANERS: dict[
    str,
    Callable[[pd.DataFrame], pd.DataFrame],
] = {
    "customers": clean_customers,
    "geolocation": clean_geolocation,
    "orders": clean_orders,
    "order_items": clean_order_items,
    "payments": clean_payments,
    "reviews": clean_reviews,
    "products": clean_products,
    "sellers": clean_sellers,
    "category_translation": clean_category_translation,
}


def run_cleaning_pipeline() -> None:
    """
    Execute the complete Phase 5 cleaning pipeline.
    """

    ensure_output_directories()

    LOGGER.info("=" * 80)
    LOGGER.info("PHASE 5 — DATA CLEANING STRATEGY")
    LOGGER.info("=" * 80)

    LOGGER.info(
        "Project root: %s",
        PROJECT_ROOT,
    )

    LOGGER.info(
        "Raw directory: %s",
        RAW_DIR,
    )

    LOGGER.info(
        "Cleaned directory: %s",
        CLEANED_DIR,
    )

    LOGGER.info(
        "Raw data will NOT be modified."
    )

    # -------------------------------------------------------------------------
    # STEP 1 — Load raw datasets
    # -------------------------------------------------------------------------

    raw_data: dict[str, pd.DataFrame] = {}

    for dataset_name in DATASET_FILES:
        raw_data[dataset_name] = load_raw_dataset(
            dataset_name
        )

    # -------------------------------------------------------------------------
    # STEP 2 — Apply dataset-specific cleaning
    # -------------------------------------------------------------------------

    cleaned_data: dict[str, pd.DataFrame] = {}

    for dataset_name, cleaner in CLEANERS.items():

        LOGGER.info(
            "-" * 80
        )

        LOGGER.info(
            "Cleaning dataset: %s",
            dataset_name,
        )

        cleaned_df = cleaner(
            raw_data[dataset_name].copy()
        )

        cleaned_data[dataset_name] = cleaned_df

    # -------------------------------------------------------------------------
    # STEP 3 — Referential integrity validation
    # -------------------------------------------------------------------------

    validate_referential_integrity(
        cleaned_data
    )

    # -------------------------------------------------------------------------
    # STEP 4 — Primary key validation
    # -------------------------------------------------------------------------

    validate_primary_keys(
        cleaned_data
    )

    # -------------------------------------------------------------------------
    # STEP 5 — Save cleaned datasets
    # -------------------------------------------------------------------------

    for dataset_name, cleaned_df in cleaned_data.items():

        save_cleaned_dataset(
            dataset_name,
            cleaned_df,
        )

    # -------------------------------------------------------------------------
    # STEP 6 — Generate before/after summary
    # -------------------------------------------------------------------------

    dataset_summary = create_dataset_summary(
        raw_data,
        cleaned_data,
    )

    dataset_summary.to_csv(
        DATASET_SUMMARY_FILE,
        index=False,
    )

    LOGGER.info(
        "Dataset summary saved: %s",
        DATASET_SUMMARY_FILE,
    )

    # -------------------------------------------------------------------------
    # STEP 7 — Save cleaning log
    # -------------------------------------------------------------------------

    save_cleaning_log()

    # -------------------------------------------------------------------------
    # STEP 8 — Save JSON summary
    # -------------------------------------------------------------------------

    save_cleaning_summary(
        dataset_summary
    )

    # -------------------------------------------------------------------------
    # STEP 9 — Final logging
    # -------------------------------------------------------------------------

    LOGGER.info("=" * 80)
    LOGGER.info("PHASE 5 CLEANING PIPELINE COMPLETE")
    LOGGER.info("=" * 80)

    LOGGER.info(
        "Datasets processed: %s",
        len(cleaned_data),
    )

    LOGGER.info(
        "Rows before cleaning: %s",
        int(dataset_summary["rows_before"].sum()),
    )

    LOGGER.info(
        "Rows after cleaning: %s",
        int(dataset_summary["rows_after"].sum()),
    )

    LOGGER.info(
        "Rows removed: %s",
        int(dataset_summary["rows_removed"].sum()),
    )

    LOGGER.info(
        "Raw data modified: NO",
    )

    LOGGER.info(
        "Post-cleaning validation report should be generated separately."
    )


# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    run_cleaning_pipeline()