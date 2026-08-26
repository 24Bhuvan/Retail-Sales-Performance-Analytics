from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd


# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"


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
# DATA TYPES
# =============================================================================

STRING_COLUMNS = {
    "customers": [
        "customer_id",
        "customer_unique_id",
        "customer_city",
        "customer_state",
    ],
    "geolocation": [
        "geolocation_city",
        "geolocation_state",
    ],
    "orders": [
        "order_id",
        "customer_id",
        "order_status",
    ],
    "order_items": [
        "order_id",
        "product_id",
        "seller_id",
    ],
    "payments": [
        "order_id",
        "payment_type",
    ],
    "reviews": [
        "review_id",
        "order_id",
        "review_comment_title",
        "review_comment_message",
    ],
    "products": [
        "product_id",
        "product_category_name",
    ],
    "sellers": [
        "seller_id",
        "seller_city",
        "seller_state",
    ],
    "category_translation": [
        "product_category_name",
        "product_category_name_english",
    ],
}


INTEGER_COLUMNS = {
    "customers": [
        "customer_zip_code_prefix",
    ],
    "geolocation": [
        "geolocation_zip_code_prefix",
    ],
    "order_items": [
        "order_item_id",
    ],
    "payments": [
        "payment_sequential",
        "payment_installments",
    ],
    "reviews": [
        "review_score",
    ],
    "products": [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ],
    "sellers": [
        "seller_zip_code_prefix",
    ],
}


FLOAT_COLUMNS = {
    "geolocation": [
        "geolocation_lat",
        "geolocation_lng",
    ],
    "order_items": [
        "price",
        "freight_value",
    ],
    "payments": [
        "payment_value",
    ],
}


DATETIME_COLUMNS = {
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
    "reviews": [
        "review_creation_date",
        "review_answer_timestamp",
    ],
}


# =============================================================================
# LOGGING
# =============================================================================

LOGGER = logging.getLogger("phase9_load_data")

if not LOGGER.handlers:
    LOGGER.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    handler.setFormatter(formatter)

    LOGGER.addHandler(handler)


# =============================================================================
# VALIDATION HELPERS
# =============================================================================

def validate_file_exists(
    dataset_name: str,
    file_path: Path,
) -> None:
    """Verify that the expected cleaned CSV exists."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found for '{dataset_name}': "
            f"{file_path}"
        )


def validate_row_count(
    dataset_name: str,
    df: pd.DataFrame,
) -> None:
    """Validate that the loaded DataFrame contains rows."""

    if len(df) == 0:
        raise ValueError(
            f"Dataset '{dataset_name}' loaded successfully "
            f"but contains zero rows."
        )


# =============================================================================
# TYPE CONVERSION
# =============================================================================

def apply_column_types(
    df: pd.DataFrame,
    dataset_name: str,
) -> pd.DataFrame:
    """
    Apply Phase 9 analysis-ready data types.

    No rows are filtered, deleted, or deduplicated here.
    """

    result = df.copy()

    # -------------------------------------------------------------------------
    # Identifier / string columns
    # -------------------------------------------------------------------------

    for column in STRING_COLUMNS.get(dataset_name, []):
        if column in result.columns:
            result[column] = result[column].astype("string")

    # -------------------------------------------------------------------------
    # Integer columns
    # -------------------------------------------------------------------------

    for column in INTEGER_COLUMNS.get(dataset_name, []):
        if column in result.columns:
            result[column] = pd.to_numeric(
                result[column],
                errors="raise",
            ).astype("Int64")

    # -------------------------------------------------------------------------
    # Floating-point columns
    # -------------------------------------------------------------------------

    for column in FLOAT_COLUMNS.get(dataset_name, []):
        if column in result.columns:
            result[column] = pd.to_numeric(
                result[column],
                errors="raise",
            ).astype("Float64")

    # -------------------------------------------------------------------------
    # Datetime columns
    # -------------------------------------------------------------------------

    for column in DATETIME_COLUMNS.get(dataset_name, []):
        if column in result.columns:
            result[column] = pd.to_datetime(
                result[column],
                errors="raise",
            )

    return result


# =============================================================================
# SINGLE DATASET EXTRACTION
# =============================================================================

def load_dataset(
    dataset_name: str,
) -> pd.DataFrame:
    """
    Load one Phase 5 cleaned dataset.

    Responsibilities:
        1. Build explicit file path.
        2. Verify file exists.
        3. Read CSV.
        4. Apply explicit data types.
        5. Preserve every source row.
        6. Log extraction statistics.
    """

    if dataset_name not in DATASET_FILES:
        raise ValueError(
            f"Unknown dataset: {dataset_name}"
        )

    filename = DATASET_FILES[dataset_name]
    file_path = CLEANED_DIR / filename

    validate_file_exists(
        dataset_name,
        file_path,
    )

    LOGGER.info(
        "Loading dataset | %s | %s",
        dataset_name,
        file_path,
    )

    df = pd.read_csv(
        file_path,
        low_memory=False,
    )

    rows_loaded = len(df)
    columns_loaded = len(df.columns)

    validate_row_count(
        dataset_name,
        df,
    )

    df = apply_column_types(
        df,
        dataset_name,
    )

    # Important:
    # No filtering, deduplication, or row deletion occurs here.
    if len(df) != rows_loaded:
        raise RuntimeError(
            f"Row count changed during extraction for "
            f"{dataset_name}: "
            f"{rows_loaded} -> {len(df)}"
        )

    LOGGER.info(
        "Extraction PASS | dataset=%s | rows=%d | columns=%d",
        dataset_name,
        rows_loaded,
        columns_loaded,
    )

    return df


# =============================================================================
# LOAD ALL DATASETS
# =============================================================================

def load_all_datasets() -> dict[str, pd.DataFrame]:
    """
    Load all nine Phase 5 cleaned datasets.
    """

    LOGGER.info("=" * 80)
    LOGGER.info("PHASE 9 — CLEANED DATA EXTRACTION")
    LOGGER.info("=" * 80)

    LOGGER.info(
        "Cleaned data directory: %s",
        CLEANED_DIR,
    )

    datasets: dict[str, pd.DataFrame] = {}

    for dataset_name in DATASET_FILES:
        datasets[dataset_name] = load_dataset(
            dataset_name
        )

    LOGGER.info("=" * 80)
    LOGGER.info(
        "ALL 9 DATASETS LOADED SUCCESSFULLY"
    )
    LOGGER.info("=" * 80)

    return datasets


# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

if __name__ == "__main__":

    datasets = load_all_datasets()

    print()
    print("=" * 80)
    print("PHASE 9 EXTRACTION SUMMARY")
    print("=" * 80)

    for dataset_name, df in datasets.items():
        print(
            f"{dataset_name:25s} "
            f"rows={len(df):>10,} "
            f"columns={len(df.columns):>3}"
        )

    print("=" * 80)