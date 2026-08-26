from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from load_data import load_all_datasets

# =============================================================================
# PROJECT PATHS
# =============================================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = (
    PROJECT_ROOT / "data" / "processed"
)
REPORT_DIR = (
    PROJECT_ROOT / "reports" / "python_processing"
)
CLEANED_DIR = (
    PROJECT_ROOT / "data" / "cleaned"
)

# =============================================================================
# LOGGING
# =============================================================================
LOGGER = logging.getLogger("phase9_process")
LOGGER.setLevel(logging.INFO)
LOGGER.propagate = False

# =============================================================================
# REPORT STORAGE
# =============================================================================
JOIN_VALIDATION_RESULTS: list[dict] = []
GRAIN_VALIDATION_RESULTS: list[dict] = []
TRACEABILITY_RESULTS: list[dict] = []

# =============================================================================
# STEP 16 — DETERMINISTIC SORT RULES
#
# Defines the analytical keys used to deterministically order BOTH the
# raw cleaned input datasets and the processed output datasets before
# hashing / exporting.
#
# This guarantees that reproducibility hashes and exported CSVs never
# depend on arbitrary upstream row ordering.
#
# NOTE:
# These keys alone are not guaranteed to be unique for every dataset.
#
# Example:
# reviews_processed intentionally preserves the source review-record
# grain and may contain duplicate review_id/order_id combinations.
#
# Therefore a deterministic full-row SHA-256 fingerprint is always
# applied as a secondary tie-breaker.
#
# If two rows are completely identical across every column, their
# fingerprints will also be identical. This is not a reproducibility
# problem because swapping two completely identical rows produces
# identical CSV bytes and therefore the same SHA-256 hash.
# =============================================================================
SORT_RULES: dict[str, list[str]] = {
    # -------------------------------------------------------------------------
    # Input / cleaned datasets
    # -------------------------------------------------------------------------
    "customers": [
        "customer_id",
    ],
    "geolocation": [
        "geolocation_zip_code_prefix",
        "geolocation_city",
        "geolocation_state",
        "geolocation_lat",
        "geolocation_lng",
    ],
    "orders": [
        "order_id",
    ],
    "order_items": [
        "order_id",
        "order_item_id",
    ],
    "payments": [
        "order_id",
        "payment_sequential",
    ],
    "reviews": [
        "review_id",
        "order_id",
    ],
    "products": [
        "product_id",
    ],
    "sellers": [
        "seller_id",
    ],
    "category_translation": [
        "product_category_name",
    ],
    # -------------------------------------------------------------------------
    # Processed / output datasets
    # -------------------------------------------------------------------------
    "orders_processed": [
        "order_id",
    ],
    "order_items_processed": [
        "order_id",
        "order_item_id",
    ],
    "payments_processed": [
        "order_id",
        "payment_sequential",
    ],
    "reviews_processed": [
        "review_id",
        "order_id",
    ],
    "customers_processed": [
        "customer_id",
    ],
    "products_processed": [
        "product_id",
    ],
    "sellers_processed": [
        "seller_id",
    ],
    "geography_processed": [
        "geolocation_zip_code_prefix",
    ],
}


# =============================================================================
# GENERAL HELPERS
# =============================================================================
def validate_columns(
    df: pd.DataFrame,
    required_columns: list[str],
    dataset_name: str,
) -> None:
    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]
    if missing:
        raise ValueError(
            f"{dataset_name}: missing required columns: {missing}"
        )


def validate_key_uniqueness(
    df: pd.DataFrame,
    keys: list[str],
    dataset_name: str,
) -> None:
    validate_columns(
        df,
        keys,
        dataset_name,
    )
    duplicates = (
        df[keys]
        .duplicated()
        .sum()
    )
    if duplicates != 0:
        raise ValueError(
            f"{dataset_name}: duplicate key combinations found "
            f"for {keys}: {duplicates}"
        )


def validate_no_row_multiplication(
    before: int,
    after: int,
    operation: str,
) -> None:
    if before != after:
        raise ValueError(
            f"Unexpected row-count change during {operation}: "
            f"{before} -> {after}"
        )


# =============================================================================
# STEP 5 — ANALYSIS-READY DTYPE VALIDATION
# =============================================================================
EXPECTED_STRING_COLUMNS: dict[str, list[str]] = {
    "customers": [
        "customer_id",
        "customer_unique_id",
    ],
    "orders": [
        "order_id",
        "customer_id",
    ],
    "order_items": [
        "order_id",
        "product_id",
        "seller_id",
    ],
    "payments": [
        "order_id",
    ],
    "reviews": [
        "review_id",
        "order_id",
    ],
    "products": [
        "product_id",
    ],
    "sellers": [
        "seller_id",
    ],
    # -------------------------------------------------------------------------
    # CHANGE 4: geolocation previously had zero dtype validation coverage
    # despite its numeric fields feeding a .mean() aggregation directly in
    # build_geography_processed(). City/state are validated as string here;
    # zip prefix / lat / lng are validated as numeric below.
    # -------------------------------------------------------------------------
    "geolocation": [
        "geolocation_city",
        "geolocation_state",
    ],
}
EXPECTED_DATETIME_COLUMNS: dict[str, list[str]] = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "reviews": [
        "review_creation_date",
        "review_answer_timestamp",
    ],
}
EXPECTED_NUMERIC_COLUMNS: dict[str, list[str]] = {
    "order_items": [
        "order_item_id",
        "price",
        "freight_value",
    ],
    "payments": [
        "payment_sequential",
        "payment_installments",
        "payment_value",
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
    # -------------------------------------------------------------------------
    # CHANGE 4 (cont.): geolocation numeric fields.
    # -------------------------------------------------------------------------
    "geolocation": [
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
    ],
}


def validate_analysis_ready_dtypes(
    datasets: dict[str, pd.DataFrame],
) -> None:
    """
    Step 5:
    Validate IDs, datetime fields, and numeric fields.
    """
    LOGGER.info("=" * 80)
    LOGGER.info("STEP 5 — ANALYSIS-READY DTYPE VALIDATION")
    LOGGER.info("=" * 80)

    # -------------------------------------------------------------------------
    # IDs
    # -------------------------------------------------------------------------
    for dataset_name, columns in EXPECTED_STRING_COLUMNS.items():
        df = datasets[dataset_name]
        for column in columns:
            validate_columns(
                df,
                [column],
                dataset_name,
            )
            dtype = df[column].dtype
            if not (
                pd.api.types.is_string_dtype(dtype)
                or pd.api.types.is_object_dtype(dtype)
            ):
                raise TypeError(
                    f"{dataset_name}.{column}: expected string/object "
                    f"identifier dtype, got {dtype}"
                )
            LOGGER.info(
                "DTYPE PASS | %-20s | %-35s | %s",
                dataset_name,
                column,
                dtype,
            )

    # -------------------------------------------------------------------------
    # Dates
    # -------------------------------------------------------------------------
    for dataset_name, columns in EXPECTED_DATETIME_COLUMNS.items():
        df = datasets[dataset_name]
        for column in columns:
            validate_columns(
                df,
                [column],
                dataset_name,
            )
            dtype = df[column].dtype
            if not pd.api.types.is_datetime64_any_dtype(dtype):
                raise TypeError(
                    f"{dataset_name}.{column}: expected datetime64 "
                    f"dtype, got {dtype}"
                )
            LOGGER.info(
                "DATETIME PASS | %-20s | %-35s | %s",
                dataset_name,
                column,
                dtype,
            )

    # -------------------------------------------------------------------------
    # Numeric
    # -------------------------------------------------------------------------
    for dataset_name, columns in EXPECTED_NUMERIC_COLUMNS.items():
        df = datasets[dataset_name]
        for column in columns:
            validate_columns(
                df,
                [column],
                dataset_name,
            )
            dtype = df[column].dtype
            if not pd.api.types.is_numeric_dtype(dtype):
                raise TypeError(
                    f"{dataset_name}.{column}: expected numeric "
                    f"dtype, got {dtype}"
                )
            LOGGER.info(
                "NUMERIC PASS | %-20s | %-35s | %s",
                dataset_name,
                column,
                dtype,
            )

    LOGGER.info("STEP 5 — ANALYSIS-READY DTYPE VALIDATION PASSED")


# =============================================================================
# STEP 10 — JOIN VALIDATION
# =============================================================================
def record_join_validation(
    *,
    join_name: str,
    left_dataset: str,
    right_dataset: str,
    join_keys: list[str],
    left_rows: int,
    result_rows: int,
    unmatched_rows: int,
    duplicate_right_keys: int,
    unmatched_allowed: bool,
) -> None:
    row_change = (
        result_rows - left_rows
    )

    if row_change != 0:
        status = "FAIL"
    elif duplicate_right_keys != 0:
        status = "FAIL"
    elif unmatched_rows != 0 and not unmatched_allowed:
        status = "FAIL"
    else:
        status = "PASS"

    JOIN_VALIDATION_RESULTS.append(
        {
            "join_name": join_name,
            "left_dataset": left_dataset,
            "right_dataset": right_dataset,
            "join_keys": ", ".join(join_keys),
            "join_type": "LEFT",
            "validation_rule": "many_to_one",
            "left_rows": left_rows,
            "result_rows": result_rows,
            "row_change": row_change,
            "unmatched_rows": int(unmatched_rows),
            "unmatched_allowed": unmatched_allowed,
            "duplicate_right_keys": int(
                duplicate_right_keys
            ),
            "status": status,
        }
    )

    LOGGER.info(
        "JOIN | %-40s | %d -> %d | unmatched=%d | status=%s",
        join_name,
        left_rows,
        result_rows,
        unmatched_rows,
        status,
    )

    if status == "FAIL":
        raise ValueError(
            f"Join validation failed: {join_name} | "
            f"rows={left_rows}->{result_rows} | "
            f"unmatched={unmatched_rows} | "
            f"duplicate_right_keys={duplicate_right_keys}"
        )


def validated_many_to_one_merge(
    *,
    left: pd.DataFrame,
    right: pd.DataFrame,
    left_dataset: str,
    right_dataset: str,
    join_name: str,
    join_keys: list[str],
    right_columns: list[str],
    unmatched_allowed: bool = False,
) -> pd.DataFrame:
    # -------------------------------------------------------------------------
    # Validate columns
    # -------------------------------------------------------------------------
    validate_columns(
        left,
        join_keys,
        left_dataset,
    )
    validate_columns(
        right,
        right_columns,
        right_dataset,
    )

    # -------------------------------------------------------------------------
    # Validate right-side uniqueness
    # -------------------------------------------------------------------------
    duplicate_right_keys = (
        right[join_keys]
        .duplicated()
        .sum()
    )
    if duplicate_right_keys != 0:
        # -----------------------------------------------------------------------
        # CHANGE 5: record_join_validation() raises ValueError itself once it
        # determines status == "FAIL" (which duplicate_right_keys != 0
        # guarantees here), so execution never falls through past this call.
        # The separate raise that previously followed was unreachable dead
        # code and has been removed.
        # -----------------------------------------------------------------------
        record_join_validation(
            join_name=join_name,
            left_dataset=left_dataset,
            right_dataset=right_dataset,
            join_keys=join_keys,
            left_rows=len(left),
            result_rows=len(left),
            unmatched_rows=0,
            duplicate_right_keys=duplicate_right_keys,
            unmatched_allowed=unmatched_allowed,
        )

    # -------------------------------------------------------------------------
    # Merge
    # -------------------------------------------------------------------------
    left_rows = len(left)
    result = left.merge(
        right[right_columns],
        on=join_keys,
        how="left",
        validate="many_to_one",
        indicator="_join_status",
    )
    result_rows = len(result)

    # -------------------------------------------------------------------------
    # Unmatched records
    # -------------------------------------------------------------------------
    unmatched_rows = int(
        (
            result["_join_status"]
            == "left_only"
        ).sum()
    )

    # -------------------------------------------------------------------------
    # Validate row count
    # -------------------------------------------------------------------------
    if result_rows != left_rows:
        record_join_validation(
            join_name=join_name,
            left_dataset=left_dataset,
            right_dataset=right_dataset,
            join_keys=join_keys,
            left_rows=left_rows,
            result_rows=result_rows,
            unmatched_rows=unmatched_rows,
            duplicate_right_keys=duplicate_right_keys,
            unmatched_allowed=unmatched_allowed,
        )
        raise ValueError(
            f"Unexpected row multiplication in {join_name}: "
            f"{left_rows} -> {result_rows}"
        )

    # -------------------------------------------------------------------------
    # Record validation
    # -------------------------------------------------------------------------
    record_join_validation(
        join_name=join_name,
        left_dataset=left_dataset,
        right_dataset=right_dataset,
        join_keys=join_keys,
        left_rows=left_rows,
        result_rows=result_rows,
        unmatched_rows=unmatched_rows,
        duplicate_right_keys=duplicate_right_keys,
        unmatched_allowed=unmatched_allowed,
    )

    result.drop(
        columns="_join_status",
        inplace=True,
    )
    return result


# =============================================================================
# STEP 7.1 — ORDER-LEVEL DATASET
# =============================================================================
def build_orders_processed(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    LOGGER.info(
        "Building orders_processed..."
    )
    validate_key_uniqueness(
        orders,
        ["order_id"],
        "orders",
    )
    validate_key_uniqueness(
        customers,
        ["customer_id"],
        "customers",
    )

    customer_columns = [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ]

    result = validated_many_to_one_merge(
        left=orders,
        right=customers,
        left_dataset="orders",
        right_dataset="customers",
        join_name="orders_to_customers",
        join_keys=["customer_id"],
        right_columns=customer_columns,
    )

    validate_key_uniqueness(
        result,
        ["order_id"],
        "orders_processed",
    )

    LOGGER.info(
        "orders_processed grain: 1 row = 1 order"
    )
    return result


# =============================================================================
# STEP 7.2 — ORDER-ITEM DATASET
# =============================================================================
def build_order_items_processed(
    order_items: pd.DataFrame,
    orders: pd.DataFrame,
    products: pd.DataFrame,
    sellers: pd.DataFrame,
    category_translation: pd.DataFrame,
) -> pd.DataFrame:
    LOGGER.info(
        "Building order_items_processed..."
    )

    # -------------------------------------------------------------------------
    # Source key validation
    # -------------------------------------------------------------------------
    validate_key_uniqueness(
        order_items,
        ["order_id", "order_item_id"],
        "order_items",
    )
    validate_key_uniqueness(
        orders,
        ["order_id"],
        "orders",
    )
    validate_key_uniqueness(
        products,
        ["product_id"],
        "products",
    )
    validate_key_uniqueness(
        sellers,
        ["seller_id"],
        "sellers",
    )
    validate_key_uniqueness(
        category_translation,
        ["product_category_name"],
        "category_translation",
    )

    # -------------------------------------------------------------------------
    # Columns
    # -------------------------------------------------------------------------
    order_columns = [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    product_columns = [
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]
    seller_columns = [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ]
    category_columns = [
        "product_category_name",
        "product_category_name_english",
    ]

    # -------------------------------------------------------------------------
    # order_items → orders
    # -------------------------------------------------------------------------
    result = validated_many_to_one_merge(
        left=order_items,
        right=orders,
        left_dataset="order_items",
        right_dataset="orders",
        join_name="order_items_to_orders",
        join_keys=["order_id"],
        right_columns=order_columns,
    )

    # -------------------------------------------------------------------------
    # order_items → products
    # -------------------------------------------------------------------------
    result = validated_many_to_one_merge(
        left=result,
        right=products,
        left_dataset="order_items_enriched",
        right_dataset="products",
        join_name="order_items_to_products",
        join_keys=["product_id"],
        right_columns=product_columns,
    )

    # -------------------------------------------------------------------------
    # order_items → sellers
    # -------------------------------------------------------------------------
    result = validated_many_to_one_merge(
        left=result,
        right=sellers,
        left_dataset="order_items_enriched",
        right_dataset="sellers",
        join_name="order_items_to_sellers",
        join_keys=["seller_id"],
        right_columns=seller_columns,
    )

    # -------------------------------------------------------------------------
    # products → category translation
    #
    # Missing translations are EXPECTED in Olist.
    # They are reported but do not cause pipeline failure.
    # -------------------------------------------------------------------------
    result = validated_many_to_one_merge(
        left=result,
        right=category_translation,
        left_dataset="order_items_enriched",
        right_dataset="category_translation",
        join_name="products_to_category_translation",
        join_keys=["product_category_name"],
        right_columns=category_columns,
        unmatched_allowed=True,
    )

    # -------------------------------------------------------------------------
    # Grain validation
    # -------------------------------------------------------------------------
    validate_key_uniqueness(
        result,
        ["order_id", "order_item_id"],
        "order_items_processed",
    )
    if len(result) != len(order_items):
        raise ValueError(
            "Order-item grain failed: "
            f"source={len(order_items)} | "
            f"processed={len(result)}"
        )

    LOGGER.info(
        "order_items_processed grain: "
        "1 row = 1 order item"
    )
    return result


# =============================================================================
# STEP 7.3 — PAYMENT DATASET
# =============================================================================
def build_payments_processed(
    payments: pd.DataFrame,
    orders: pd.DataFrame,
) -> pd.DataFrame:
    LOGGER.info(
        "Building payments_processed..."
    )
    validate_key_uniqueness(
        payments,
        ["order_id", "payment_sequential"],
        "payments",
    )
    validate_key_uniqueness(
        orders,
        ["order_id"],
        "orders",
    )

    order_columns = [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
    ]

    result = validated_many_to_one_merge(
        left=payments,
        right=orders,
        left_dataset="payments",
        right_dataset="orders",
        join_name="payments_to_orders",
        join_keys=["order_id"],
        right_columns=order_columns,
    )

    validate_key_uniqueness(
        result,
        ["order_id", "payment_sequential"],
        "payments_processed",
    )
    if len(result) != len(payments):
        raise ValueError(
            "Payment grain failed: "
            f"source={len(payments)} | "
            f"processed={len(result)}"
        )

    LOGGER.info(
        "payments_processed grain: "
        "1 row = 1 payment sequence"
    )
    return result


# =============================================================================
# STEP 7.4 — REVIEW DATASET
# =============================================================================
def build_reviews_processed(
    reviews: pd.DataFrame,
    orders: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    LOGGER.info(
        "Building reviews_processed..."
    )
    validate_key_uniqueness(
        orders,
        ["order_id"],
        "orders",
    )
    validate_key_uniqueness(
        customers,
        ["customer_id"],
        "customers",
    )

    order_columns = [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
    ]
    customer_columns = [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ]

    result = validated_many_to_one_merge(
        left=reviews,
        right=orders,
        left_dataset="reviews",
        right_dataset="orders",
        join_name="reviews_to_orders",
        join_keys=["order_id"],
        right_columns=order_columns,
    )
    result = validated_many_to_one_merge(
        left=result,
        right=customers,
        left_dataset="reviews_enriched",
        right_dataset="customers",
        join_name="reviews_to_customers",
        join_keys=["customer_id"],
        right_columns=customer_columns,
    )

    # -------------------------------------------------------------------------
    # IMPORTANT:
    # Do not deduplicate review_id.
    #
    # The source review-record grain is preserved exactly.
    # -------------------------------------------------------------------------
    if len(result) != len(reviews):
        raise ValueError(
            "Review grain failed: "
            f"source={len(reviews)} | "
            f"processed={len(result)}"
        )

    LOGGER.info(
        "reviews_processed grain preserved: "
        "1 row = 1 source review record"
    )
    return result


# =============================================================================
# STEP 8 — CONTROLLED TRANSFORMATIONS
# =============================================================================
def apply_order_time_fields(
    df: pd.DataFrame,
) -> pd.DataFrame:
    result = df.copy()
    validate_columns(
        result,
        ["order_purchase_timestamp"],
        "orders_processed",
    )
    result["order_purchase_timestamp"] = pd.to_datetime(
        result["order_purchase_timestamp"],
        errors="raise",
    )
    result["order_date"] = (
        result["order_purchase_timestamp"]
        .dt.normalize()
    )
    result["order_year"] = (
        result["order_purchase_timestamp"]
        .dt.year
    )
    result["order_month"] = (
        result["order_purchase_timestamp"]
        .dt.month
    )
    result["order_quarter"] = (
        result["order_purchase_timestamp"]
        .dt.quarter
    )
    LOGGER.info(
        "Created order_date, order_year, "
        "order_month, order_quarter."
    )
    return result


def apply_order_item_fields(
    df: pd.DataFrame,
) -> pd.DataFrame:
    result = df.copy()
    validate_columns(
        result,
        ["price"],
        "order_items_processed",
    )
    if "quantity" in result.columns:
        raise ValueError(
            "Quantity column detected. "
            "Do not invent quantity for Olist."
        )
    result["sales_amount"] = result["price"]
    LOGGER.info(
        "Created sales_amount = price."
    )
    LOGGER.info(
        "Quantity intentionally not created."
    )
    LOGGER.info(
        "Profit/margin intentionally not created."
    )
    return result


# =============================================================================
# STEP 9 — SOURCE TRACEABILITY
# =============================================================================
def validate_source_key_preservation(
    source: pd.DataFrame,
    processed: pd.DataFrame,
    source_keys: list[str],
    dataset_name: str,
) -> None:
    validate_columns(
        processed,
        source_keys,
        dataset_name,
    )

    for key in source_keys:
        # ---------------------------------------------------------------------
        # CHANGE 7: use value_counts() rather than a bare set() so both
        # presence AND per-value occurrence counts can be checked. A plain
        # set-difference proves no distinct value disappeared, but it does
        # NOT prove that a key value wasn't silently duplicated or partially
        # dropped while at least one instance survived.
        # ---------------------------------------------------------------------
        source_counts = (
            source[key]
            .dropna()
            .astype(str)
            .value_counts()
        )
        processed_counts = (
            processed[key]
            .dropna()
            .astype(str)
            .value_counts()
        )

        source_values = set(
            source_counts.index
        )
        processed_values = set(
            processed_counts.index
        )

        missing_values = (
            source_values - processed_values
        )
        if missing_values:
            raise ValueError(
                f"{dataset_name}: source key '{key}' "
                f"lost {len(missing_values)} values."
            )

        # -----------------------------------------------------------------------
        # Row-count-preserving datasets (everything except reviews_processed,
        # which intentionally preserves the raw review-record grain and is
        # not guaranteed to have a strict 1:1 count relationship on every
        # key) must also preserve per-value occurrence counts, not just
        # presence.
        # -----------------------------------------------------------------------
        if dataset_name != "reviews_processed":
            aligned_processed_counts = (
                processed_counts.reindex(
                    source_counts.index,
                    fill_value=0,
                )
            )
            mismatched_counts = int(
                (
                    source_counts
                    != aligned_processed_counts
                ).sum()
            )
            if mismatched_counts:
                raise ValueError(
                    f"{dataset_name}: source key '{key}' has "
                    f"{mismatched_counts} value(s) whose occurrence "
                    "count changed between source and processed."
                )

        TRACEABILITY_RESULTS.append(
            {
                "dataset": dataset_name,
                "source_key": key,
                "source_unique_values": len(
                    source_values
                ),
                "processed_unique_values": len(
                    processed_values
                ),
                "missing_values": len(
                    missing_values
                ),
                "status": "PASS",
            }
        )
        LOGGER.info(
            "TRACEABILITY PASS | %s.%s | source=%d | processed=%d",
            dataset_name,
            key,
            len(source_values),
            len(processed_values),
        )


def validate_all_traceability(
    datasets: dict[str, pd.DataFrame],
    processed: dict[str, pd.DataFrame],
) -> None:
    LOGGER.info("=" * 80)
    LOGGER.info(
        "STEP 9 — SOURCE TRACEABILITY"
    )
    LOGGER.info("=" * 80)

    rules = {
        "orders_processed": (
            "orders",
            [
                "order_id",
                "customer_id",
            ],
        ),
        "order_items_processed": (
            "order_items",
            [
                "order_id",
                "order_item_id",
                "product_id",
                "seller_id",
            ],
        ),
        "payments_processed": (
            "payments",
            [
                "order_id",
                "payment_sequential",
            ],
        ),
        "reviews_processed": (
            "reviews",
            [
                "review_id",
                "order_id",
            ],
        ),
        "customers_processed": (
            "customers",
            [
                "customer_id",
                "customer_unique_id",
            ],
        ),
        "products_processed": (
            "products",
            [
                "product_id",
            ],
        ),
        "sellers_processed": (
            "sellers",
            [
                "seller_id",
            ],
        ),
    }

    for processed_name, (
        source_name,
        keys,
    ) in rules.items():
        validate_source_key_preservation(
            datasets[source_name],
            processed[processed_name],
            keys,
            processed_name,
        )

    LOGGER.info(
        "STEP 9 — SOURCE TRACEABILITY PASSED"
    )


# =============================================================================
# STEP 11 — ANALYTICAL GRAIN VALIDATION
# =============================================================================
def record_grain_validation(
    *,
    dataset_name: str,
    grain_name: str,
    grain_columns: list[str],
    row_count: int,
    unique_grain_count: int,
    duplicate_grain_rows: int,
    status: str,
) -> None:
    GRAIN_VALIDATION_RESULTS.append(
        {
            "dataset": dataset_name,
            "grain": grain_name,
            "grain_columns": ", ".join(
                grain_columns
            ),
            "row_count": row_count,
            "unique_grain_count": unique_grain_count,
            "duplicate_grain_rows": duplicate_grain_rows,
            "status": status,
        }
    )


def validate_analytical_grain(
    df: pd.DataFrame,
    dataset_name: str,
    grain_columns: list[str],
    grain_name: str,
) -> None:
    validate_columns(
        df,
        grain_columns,
        dataset_name,
    )

    row_count = len(df)
    duplicate_grain_rows = int(
        df[grain_columns]
        .duplicated()
        .sum()
    )
    unique_grain_count = int(
        df[grain_columns]
        .drop_duplicates()
        .shape[0]
    )

    if duplicate_grain_rows != 0:
        record_grain_validation(
            dataset_name=dataset_name,
            grain_name=grain_name,
            grain_columns=grain_columns,
            row_count=row_count,
            unique_grain_count=unique_grain_count,
            duplicate_grain_rows=duplicate_grain_rows,
            status="FAIL",
        )
        raise ValueError(
            f"{dataset_name}: analytical grain failed. "
            f"Grain={grain_name}, "
            f"duplicate_rows={duplicate_grain_rows}"
        )

    if unique_grain_count != row_count:
        record_grain_validation(
            dataset_name=dataset_name,
            grain_name=grain_name,
            grain_columns=grain_columns,
            row_count=row_count,
            unique_grain_count=unique_grain_count,
            duplicate_grain_rows=duplicate_grain_rows,
            status="FAIL",
        )
        raise ValueError(
            f"{dataset_name}: grain count mismatch. "
            f"rows={row_count}, "
            f"unique_grain={unique_grain_count}"
        )

    record_grain_validation(
        dataset_name=dataset_name,
        grain_name=grain_name,
        grain_columns=grain_columns,
        row_count=row_count,
        unique_grain_count=unique_grain_count,
        duplicate_grain_rows=duplicate_grain_rows,
        status="PASS",
    )
    LOGGER.info(
        "GRAIN PASS | %-30s | grain=%s | rows=%d | unique=%d",
        dataset_name,
        grain_name,
        row_count,
        unique_grain_count,
    )


def validate_all_analytical_grains(
    processed: dict[str, pd.DataFrame],
) -> None:
    LOGGER.info("=" * 80)
    LOGGER.info(
        "STEP 11 — ANALYTICAL GRAIN VALIDATION"
    )
    LOGGER.info("=" * 80)

    # -------------------------------------------------------------------------
    # Fact Orders
    # -------------------------------------------------------------------------
    validate_analytical_grain(
        processed["orders_processed"],
        "orders_processed",
        ["order_id"],
        "1 row / order_id",
    )

    # -------------------------------------------------------------------------
    # Fact Order Items
    # -------------------------------------------------------------------------
    validate_analytical_grain(
        processed["order_items_processed"],
        "order_items_processed",
        [
            "order_id",
            "order_item_id",
        ],
        "1 row / order_id + order_item_id",
    )

    # -------------------------------------------------------------------------
    # Fact Payments
    # -------------------------------------------------------------------------
    validate_analytical_grain(
        processed["payments_processed"],
        "payments_processed",
        [
            "order_id",
            "payment_sequential",
        ],
        "1 row / order_id + payment_sequential",
    )

    # -------------------------------------------------------------------------
    # Reviews
    #
    # IMPORTANT:
    #
    # The source review dataset is not guaranteed to have unique
    # review_id + order_id combinations.
    #
    # Therefore the analytical grain is explicitly defined as:
    #
    #     1 row = 1 preserved source review record
    #
    # The validation criterion is exact row-count preservation.
    #
    # We do NOT pretend that review_id + order_id is a unique grain.
    # -------------------------------------------------------------------------
    reviews = processed[
        "reviews_processed"
    ]
    if len(reviews) == 0:
        raise ValueError(
            "reviews_processed contains zero rows."
        )
    review_source_rows = len(reviews)
    LOGGER.info(
        "GRAIN PASS | %-30s | "
        "grain=source review record | rows=%d",
        "reviews_processed",
        review_source_rows,
    )
    GRAIN_VALIDATION_RESULTS.append(
        {
            "dataset": "reviews_processed",
            "grain": "source review record",
            "grain_columns": "source row",
            "row_count": review_source_rows,
            "unique_grain_count": review_source_rows,
            "duplicate_grain_rows": 0,
            "status": "PASS",
        }
    )

    LOGGER.info(
        "STEP 11 — ANALYTICAL GRAIN VALIDATION PASSED"
    )


# =============================================================================
# PASSTHROUGH DATASETS
# =============================================================================
def build_customers_processed(
    customers: pd.DataFrame,
) -> pd.DataFrame:
    validate_key_uniqueness(
        customers,
        ["customer_id"],
        "customers",
    )
    return customers.copy()


def build_products_processed(
    products: pd.DataFrame,
) -> pd.DataFrame:
    validate_key_uniqueness(
        products,
        ["product_id"],
        "products",
    )
    return products.copy()


def build_sellers_processed(
    sellers: pd.DataFrame,
) -> pd.DataFrame:
    validate_key_uniqueness(
        sellers,
        ["seller_id"],
        "sellers",
    )
    return sellers.copy()


# =============================================================================
# REPORTS
# =============================================================================
def save_join_validation_report() -> None:
    report = pd.DataFrame(
        JOIN_VALIDATION_RESULTS
    )
    output_path = (
        REPORT_DIR / "join_validation.csv"
    )
    report.to_csv(
        output_path,
        index=False,
    )
    LOGGER.info(
        "Saved join validation report: %s",
        output_path,
    )


def save_grain_validation_report() -> None:
    report = pd.DataFrame(
        GRAIN_VALIDATION_RESULTS
    )
    output_path = (
        REPORT_DIR / "grain_validation.csv"
    )
    report.to_csv(
        output_path,
        index=False,
    )
    LOGGER.info(
        "Saved grain validation report: %s",
        output_path,
    )


def save_traceability_report() -> None:
    report = pd.DataFrame(
        TRACEABILITY_RESULTS
    )
    output_path = (
        REPORT_DIR / "traceability_validation.csv"
    )
    report.to_csv(
        output_path,
        index=False,
    )
    LOGGER.info(
        "Saved traceability report: %s",
        output_path,
    )


# =============================================================================
# STEP 14 — PHASE 9 VALIDATION EVIDENCE
# =============================================================================
def configure_file_logging() -> Path:
    """
    Configure a dedicated execution log for the Phase 9 pipeline.
    """
    log_path = (
        REPORT_DIR / "processing_execution.log"
    )
    file_handler = logging.FileHandler(
        log_path,
        mode="w",
        encoding="utf-8",
    )
    file_handler.setLevel(
        logging.INFO
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
    )

    # Prevent duplicate handlers if main() is called more than once.
    existing_file_handlers = [
        handler
        for handler in LOGGER.handlers
        if isinstance(
            handler,
            logging.FileHandler,
        )
    ]
    if not existing_file_handlers:
        LOGGER.addHandler(
            file_handler
        )

    return log_path


def save_dataset_statistics(
    datasets: dict[str, pd.DataFrame],
    processed: dict[str, pd.DataFrame],
) -> None:
    """
    Save row, column, NULL, and duplicate statistics for
    Phase 9 input and processed datasets.
    """
    results = []

    # -------------------------------------------------------------------------
    # Input datasets
    # -------------------------------------------------------------------------
    for name, df in datasets.items():
        results.append(
            {
                "stage": "input",
                "dataset": name,
                "rows": len(df),
                "columns": len(df.columns),
                "null_count": int(
                    df.isna()
                    .sum()
                    .sum()
                ),
                "duplicate_rows": int(
                    df.duplicated()
                    .sum()
                ),
            }
        )

    # -------------------------------------------------------------------------
    # Processed datasets
    # -------------------------------------------------------------------------
    for name, df in processed.items():
        results.append(
            {
                "stage": "processed",
                "dataset": name,
                "rows": len(df),
                "columns": len(df.columns),
                "null_count": int(
                    df.isna()
                    .sum()
                    .sum()
                ),
                "duplicate_rows": int(
                    df.duplicated()
                    .sum()
                ),
            }
        )

    report = pd.DataFrame(
        results
    )
    output_path = (
        REPORT_DIR / "dataset_statistics.csv"
    )
    report.to_csv(
        output_path,
        index=False,
    )
    LOGGER.info(
        "Saved dataset statistics report: %s",
        output_path,
    )


def save_processing_validation(
    datasets: dict[str, pd.DataFrame],
    processed: dict[str, pd.DataFrame],
) -> None:
    """
    Compare source and processed datasets at the dataset level.
    """
    source_mapping = {
        "orders_processed": "orders",
        "order_items_processed": "order_items",
        "payments_processed": "payments",
        "reviews_processed": "reviews",
        "customers_processed": "customers",
        "products_processed": "products",
        "sellers_processed": "sellers",
        # Geography intentionally has different grain because
        # raw geolocation is aggregated to ZIP-prefix level.
    }

    results = []
    for processed_name, source_name in source_mapping.items():
        source_df = datasets[
            source_name
        ]
        processed_df = processed[
            processed_name
        ]
        row_change = (
            len(processed_df)
            - len(source_df)
        )
        status = (
            "PASS"
            if row_change == 0
            else "FAIL"
        )
        results.append(
            {
                "dataset": processed_name,
                "source_dataset": source_name,
                "input_rows": len(source_df),
                "output_rows": len(processed_df),
                "row_change": row_change,
                "input_columns": len(
                    source_df.columns
                ),
                "output_columns": len(
                    processed_df.columns
                ),
                "status": status,
            }
        )

    # -------------------------------------------------------------------------
    # Geography is intentionally aggregated.
    #
    # CHANGE 1: this previously appended "status": "PASS" unconditionally,
    # with no actual comparison performed. The real invariant this
    # transformation must satisfy is:
    #
    #     len(geography_processed) == nunique(geolocation_zip_code_prefix)
    #
    # This is now genuinely computed and checked, and is subject to the
    # same "failed = report[report['status'] != 'PASS']" gate below as
    # every other dataset.
    # -------------------------------------------------------------------------
    geography_input = datasets[
        "geolocation"
    ]
    geography_output = processed[
        "geography_processed"
    ]
    expected_zip_count = int(
        geography_input[
            "geolocation_zip_code_prefix"
        ]
        .nunique(dropna=True)
    )
    actual_zip_count = len(
        geography_output
    )
    geography_status = (
        "PASS"
        if actual_zip_count == expected_zip_count
        else "FAIL"
    )
    results.append(
        {
            "dataset": "geography_processed",
            "source_dataset": "geolocation",
            "input_rows": len(
                geography_input
            ),
            "output_rows": len(
                geography_output
            ),
            "row_change": (
                len(geography_output)
                - len(geography_input)
            ),
            "input_columns": len(
                geography_input.columns
            ),
            "output_columns": len(
                geography_output.columns
            ),
            "expected_unique_zip_prefixes": expected_zip_count,
            "status": geography_status,
        }
    )

    report = pd.DataFrame(
        results
    )
    output_path = (
        REPORT_DIR / "processing_validation.csv"
    )
    report.to_csv(
        output_path,
        index=False,
    )
    LOGGER.info(
        "Saved processing validation report: %s",
        output_path,
    )

    failed = report[
        report["status"] != "PASS"
    ]
    if not failed.empty:
        raise RuntimeError(
            "Processing validation failed:\n"
            f"{failed.to_string(index=False)}"
        )


def save_processing_summary(
    datasets: dict[str, pd.DataFrame],
    processed: dict[str, pd.DataFrame],
    steps_completed: list[str],
    status: str = "PASS",
) -> None:
    """
    Save machine-readable Phase 9 execution summary.

    This must only be called with status="PASS" after every upstream
    validation — including Step 16 reproducibility validation — has
    actually completed successfully.

    `execution_timestamp` is execution metadata only.
    It is NOT included in any dataset SHA-256 reproducibility hash,
    is not part of any dataset's contents, and must never be treated
    as a transformation result.
    """
    summary = {
        "phase": "Phase 9 — Python Data Processing",
        "status": status,
        "execution_timestamp": (
            pd.Timestamp.now().isoformat()
        ),
        "input_dataset_count": len(
            datasets
        ),
        "output_dataset_count": len(
            processed
        ),
        "total_input_rows": int(
            sum(
                len(df)
                for df in datasets.values()
            )
        ),
        "total_output_rows": int(
            sum(
                len(df)
                for df in processed.values()
            )
        ),
        "steps_completed": steps_completed,
    }

    output_path = (
        REPORT_DIR / "processing_summary.json"
    )
    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=4,
        )
    LOGGER.info(
        "Saved processing summary: %s",
        output_path,
    )


# =============================================================================
# STEP 16 — REPRODUCIBILITY
# =============================================================================
# -----------------------------------------------------------------------------
# Deterministic file hashing
# -----------------------------------------------------------------------------
def calculate_file_sha256(
    file_path: Path,
    chunk_size: int = 1024 * 1024,
) -> str:
    """
    Calculate SHA-256 checksum for a file.

    Used to prove that the same input/output files are produced
    across repeated executions.
    """
    sha256 = hashlib.sha256()
    with file_path.open("rb") as file:
        while True:
            chunk = file.read(
                chunk_size
            )
            if not chunk:
                break
            sha256.update(
                chunk
            )
    return sha256.hexdigest()


# -----------------------------------------------------------------------------
# Deterministic row-level tie-breaking
# -----------------------------------------------------------------------------
def _canonicalize_cell(value) -> str:
    """
    Convert a single DataFrame cell into a canonical deterministic string.

    Rules:
        - All pandas-recognized missing values use one fixed sentinel.
        - pandas Timestamp values use ISO-8601 representation.
        - pandas Timedelta values use ISO-8601 representation.
        - NumPy scalar types (np.int64, np.float64, ...) are normalized
          to native Python types via .item() before repr() is applied.
        - Numeric values use repr().
        - Everything else uses str().

    The representation does not depend on:
        - DataFrame index
        - row position
        - Python object memory address
        - arbitrary dtype-specific string formatting
        - the installed NumPy version

    Missing-value handling is deliberately defensive because pandas
    scalar values such as pd.NA can otherwise produce an ambiguous
    boolean result when evaluated directly.
    """
    # -------------------------------------------------------------------------
    # Robust missing-value detection
    #
    # pd.isna(value) can return:
    #     bool
    #     numpy.bool_
    #     array-like values
    #
    # A DataFrame cell should normally produce a scalar result, but this
    # implementation explicitly handles scalar and item()-compatible
    # results so pd.NA cannot trigger an ambiguous truth-value error.
    # -------------------------------------------------------------------------
    try:
        missing = pd.isna(
            value
        )
    except (
        TypeError,
        ValueError,
    ):
        missing = False

    if isinstance(
        missing,
        bool,
    ):
        if missing:
            return "\x00NULL\x00"
    elif hasattr(
        missing,
        "item",
    ):
        if bool(
            missing.item()
        ):
            return "\x00NULL\x00"

    # -------------------------------------------------------------------------
    # Timestamp
    # -------------------------------------------------------------------------
    if isinstance(
        value,
        pd.Timestamp,
    ):
        return value.isoformat()

    # -------------------------------------------------------------------------
    # Timedelta
    # -------------------------------------------------------------------------
    if isinstance(
        value,
        pd.Timedelta,
    ):
        return value.isoformat()

    # -------------------------------------------------------------------------
    # CHANGE 3: NumPy scalar normalization.
    #
    # df.apply(..., axis=1) typically hands back NumPy scalar types
    # (np.int64, np.float64, ...) rather than native Python int/float.
    # repr() of a NumPy scalar is NOT guaranteed to be stable across
    # NumPy versions (e.g. NumPy 2.x renders floats as
    # "np.float64(1.5)" instead of "1.5"). Normalizing via .item()
    # before applying repr() keeps this fingerprint — and therefore
    # every dataset's SHA-256 hash — independent of the installed
    # NumPy version.
    # -------------------------------------------------------------------------
    if isinstance(
        value,
        np.generic,
    ):
        value = value.item()

    # -------------------------------------------------------------------------
    # Numeric
    # -------------------------------------------------------------------------
    if isinstance(
        value,
        (int, float),
    ):
        return repr(value)

    # -------------------------------------------------------------------------
    # Everything else
    # -------------------------------------------------------------------------
    return str(value)


def _compute_row_fingerprints(
    df: pd.DataFrame,
) -> pd.Series:
    """
    Compute a deterministic SHA-256 fingerprint for every row.

    The fingerprint is based exclusively on:
        1. the DataFrame's existing column order
        2. the canonicalized cell values

    It never uses:
        - DataFrame index
        - row position
        - Python object identity

    The fingerprint exists only as an in-memory deterministic sort
    tie-breaker and is never exported.

    If two rows are completely identical across every column, they
    necessarily receive the same fingerprint. This is harmless because
    exchanging identical rows produces identical CSV content and
    therefore the same dataset SHA-256 hash.
    """
    columns = list(
        df.columns
    )

    def fingerprint_row(
        row: pd.Series,
    ) -> str:
        canonical_values = [
            _canonicalize_cell(
                row[column]
            )
            for column in columns
        ]
        row_text = "\x1f".join(
            canonical_values
        )
        return hashlib.sha256(
            row_text.encode("utf-8")
        ).hexdigest()

    return df.apply(
        fingerprint_row,
        axis=1,
    )


# -----------------------------------------------------------------------------
# Dataset hashing
# -----------------------------------------------------------------------------
def calculate_dataframe_sha256(
    df: pd.DataFrame,
) -> str:
    """
    Calculate a deterministic SHA-256 hash from a DataFrame.

    The DataFrame is serialized deterministically using:
        - the DataFrame's existing column order, preserved exactly as
          provided by the caller
        - fixed row order
        - index=False
        - LF line endings

    The DataFrame index is never included in the hashed representation.
    """
    csv_bytes = df.to_csv(
        index=False,
        lineterminator="\n",
    ).encode(
        "utf-8"
    )
    return hashlib.sha256(
        csv_bytes
    ).hexdigest()


# -----------------------------------------------------------------------------
# Deterministic dataset ordering
# -----------------------------------------------------------------------------
def sort_dataframe_deterministically(
    df: pd.DataFrame,
    dataset_name: str,
) -> pd.DataFrame:
    """
    Apply deterministic ordering before export or hashing.

    Rows are ordered first by the dataset's analytical sort keys
    (SORT_RULES), then by a deterministic full-row content fingerprint
    used strictly as a tie-breaker.

    Sorting is stable ("mergesort") and NULLs are always placed last
    (na_position="last").

    The DataFrame's column order is preserved exactly.

    The input DataFrame is never mutated.
    """
    if dataset_name not in SORT_RULES:
        raise ValueError(
            f"No deterministic sort rule defined for "
            f"{dataset_name}"
        )

    keys = SORT_RULES[
        dataset_name
    ]
    validate_columns(
        df,
        keys,
        dataset_name,
    )

    working = df.copy()
    tie_breaker_column = (
        "_deterministic_row_fingerprint"
    )
    while tie_breaker_column in working.columns:
        tie_breaker_column = (
            f"{tie_breaker_column}_"
        )

    working[
        tie_breaker_column
    ] = _compute_row_fingerprints(
        df
    )

    result = (
        working
        .sort_values(
            by=keys + [
                tie_breaker_column
            ],
            kind="mergesort",
            na_position="last",
        )
        .drop(
            columns=[
                tie_breaker_column
            ]
        )
        .reset_index(
            drop=True
        )
    )

    # -------------------------------------------------------------------------
    # Confirm that deterministic sorting changed only row order.
    # -------------------------------------------------------------------------
    if list(
        result.columns
    ) != list(
        df.columns
    ):
        raise RuntimeError(
            f"{dataset_name}: deterministic sort unexpectedly altered "
            "column order."
        )

    return result


# -----------------------------------------------------------------------------
# Deterministic geography aggregation
# -----------------------------------------------------------------------------
def build_geography_processed(
    geolocation: pd.DataFrame,
) -> pd.DataFrame:
    LOGGER.info(
        "Building geography_processed..."
    )
    zip_column = (
        "geolocation_zip_code_prefix"
    )
    required_columns = [
        zip_column,
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state",
    ]
    validate_columns(
        geolocation,
        required_columns,
        "geolocation",
    )

    # -------------------------------------------------------------------------
    # Sort deterministically before using "first".
    #
    # This prevents the selected city/state from depending on arbitrary
    # source row ordering.
    # -------------------------------------------------------------------------
    geography_source = (
        sort_dataframe_deterministically(
            geolocation[
                required_columns
            ],
            "geolocation",
        )
    )

    geography = (
        geography_source
        .groupby(
            zip_column,
            as_index=False,
            dropna=False,
            sort=True,
        )
        .agg(
            geolocation_lat=(
                "geolocation_lat",
                "mean",
            ),
            geolocation_lng=(
                "geolocation_lng",
                "mean",
            ),
            geolocation_city=(
                "geolocation_city",
                "first",
            ),
            geolocation_state=(
                "geolocation_state",
                "first",
            ),
        )
    )

    validate_key_uniqueness(
        geography,
        [zip_column],
        "geography_processed",
    )

    LOGGER.info(
        "Geography: %d raw rows -> %d ZIP prefixes",
        len(geolocation),
        len(geography),
    )
    return geography


# -----------------------------------------------------------------------------
# Deterministic dataset validation + hashing
# -----------------------------------------------------------------------------
def validate_and_hash_dataset(
    name: str,
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, str]:
    """
    Perform deterministic-output validation for a single dataset.

    Steps:
        1. Confirm the dataset exists.
        2. Confirm the dataset is non-empty.
        3. Confirm a deterministic sort rule exists.
        4. Deterministically sort the dataset.
        5. Calculate its SHA-256 hash.

    Returns:
        deterministic sorted DataFrame
        SHA-256 digest
    """
    if df is None:
        raise RuntimeError(
            f"Dataset does not exist: {name}"
        )
    if df.empty:
        raise RuntimeError(
            "Dataset is empty, cannot compute a deterministic hash: "
            f"{name}"
        )
    if name not in SORT_RULES:
        raise ValueError(
            "No deterministic sort rule registered for dataset: "
            f"{name}"
        )

    sorted_df = (
        sort_dataframe_deterministically(
            df,
            name,
        )
    )
    digest = calculate_dataframe_sha256(
        sorted_df
    )
    return sorted_df, digest


def log_input_fingerprints(
    datasets: dict[str, pd.DataFrame],
) -> dict[str, str]:
    """
    STEP 16 — deterministic input fingerprinting.

    Before any transformation runs, deterministically sort and hash
    every cleaned input dataset.

    This produces a machine-readable fingerprint of the exact cleaned
    inputs consumed by this run.
    """
    LOGGER.info("=" * 80)
    LOGGER.info(
        "STEP 16 — DETERMINISTIC INPUT FINGERPRINTING"
    )
    LOGGER.info("=" * 80)

    fingerprints: dict[str, str] = {}
    for name, df in datasets.items():
        _, digest = (
            validate_and_hash_dataset(
                name,
                df,
            )
        )
        fingerprints[name] = digest
        LOGGER.info(
            "INPUT FINGERPRINT | %-25s | rows=%d | sha256=%s",
            name,
            len(df),
            digest,
        )
    return fingerprints


# -----------------------------------------------------------------------------
# Reproducibility evidence
# -----------------------------------------------------------------------------
def save_reproducibility_report(
    datasets: dict[str, pd.DataFrame],
    processed: dict[str, pd.DataFrame],
) -> tuple[
    dict[str, str],
    dict[str, str],
]:
    """
    Save deterministic hashes for all input and output datasets.

    Returns:
        input_hashes
        processed_hashes
    """
    results = []
    input_hashes: dict[str, str] = {}
    processed_hashes: dict[str, str] = {}

    # -------------------------------------------------------------------------
    # Input hashes
    # -------------------------------------------------------------------------
    for name, df in datasets.items():
        sorted_df, digest = (
            validate_and_hash_dataset(
                name,
                df,
            )
        )
        input_hashes[name] = digest
        results.append(
            {
                "stage": "input",
                "dataset": name,
                "rows": len(sorted_df),
                "columns": len(
                    sorted_df.columns
                ),
                "sha256": digest,
            }
        )

    # -------------------------------------------------------------------------
    # Processed hashes
    # -------------------------------------------------------------------------
    for name, df in processed.items():
        sorted_df, digest = (
            validate_and_hash_dataset(
                name,
                df,
            )
        )
        processed_hashes[name] = digest
        results.append(
            {
                "stage": "processed",
                "dataset": name,
                "rows": len(sorted_df),
                "columns": len(
                    sorted_df.columns
                ),
                "sha256": digest,
            }
        )

    report = pd.DataFrame(
        results
    )
    output_path = (
        REPORT_DIR
        / "reproducibility_hashes.csv"
    )
    report.to_csv(
        output_path,
        index=False,
        lineterminator="\n",
    )
    LOGGER.info(
        "Saved reproducibility hashes: %s",
        output_path,
    )

    return (
        input_hashes,
        processed_hashes,
    )


# -----------------------------------------------------------------------------
# STRONG EXPORT VALIDATION
# -----------------------------------------------------------------------------
def validate_exported_datasets(
    processed: dict[str, pd.DataFrame],
    export_hashes: dict[str, str],
    processed_hashes: dict[str, str],
) -> None:
    """
    Validate the complete relationship between processed DataFrames
    and their exported CSV files.

    For every processed dataset this verifies:
        1. An export hash was recorded.
        2. A processed DataFrame hash was recorded.
        3. The exported CSV exists on disk.
        4. The deterministic processed DataFrame hash can be
           independently recalculated and matches processed_hashes.
        5. The exported CSV file hash matches the hash captured
           immediately after export.
        6. The deterministic processed DataFrame representation and
           exported CSV representation produce the same SHA-256 hash.

    The exported CSV is read only for byte-level integrity validation.
    It is never used as an input to the transformation pipeline.
    """
    # -------------------------------------------------------------------------
    # Confirm that every processed dataset has an export record.
    # -------------------------------------------------------------------------
    if set(export_hashes) != set(processed):
        missing_export_hashes = (
            set(processed)
            - set(export_hashes)
        )
        unexpected_export_hashes = (
            set(export_hashes)
            - set(processed)
        )
        raise RuntimeError(
            "Export hash registry does not match processed dataset registry: "
            f"missing={sorted(missing_export_hashes)} | "
            f"unexpected={sorted(unexpected_export_hashes)}"
        )

    # -------------------------------------------------------------------------
    # Confirm that every processed dataset has a DataFrame hash.
    # -------------------------------------------------------------------------
    if set(processed_hashes) != set(processed):
        missing_processed_hashes = (
            set(processed)
            - set(processed_hashes)
        )
        unexpected_processed_hashes = (
            set(processed_hashes)
            - set(processed)
        )
        raise RuntimeError(
            "Processed hash registry does not match processed dataset "
            f"registry: missing={sorted(missing_processed_hashes)} | "
            f"unexpected={sorted(unexpected_processed_hashes)}"
        )

    # -------------------------------------------------------------------------
    # Validate every dataset.
    # -------------------------------------------------------------------------
    for name in processed:
        filename = (
            f"{name}.csv"
        )
        output_path = (
            PROCESSED_DIR
            / filename
        )

        # ---------------------------------------------------------------------
        # Confirm exported file exists.
        # ---------------------------------------------------------------------
        if not output_path.exists():
            raise RuntimeError(
                "Exported CSV file is missing on disk: "
                f"{output_path}"
            )
        if not output_path.is_file():
            raise RuntimeError(
                "Expected exported CSV path to be a file: "
                f"{output_path}"
            )

        # ---------------------------------------------------------------------
        # Recreate the exact deterministic DataFrame representation.
        # ---------------------------------------------------------------------
        deterministic_df = (
            sort_dataframe_deterministically(
                processed[name],
                name,
            )
        )

        # ---------------------------------------------------------------------
        # Independently recalculate DataFrame hash.
        # ---------------------------------------------------------------------
        recalculated_dataframe_hash = (
            calculate_dataframe_sha256(
                deterministic_df
            )
        )
        if (
            recalculated_dataframe_hash
            != processed_hashes[name]
        ):
            raise RuntimeError(
                f"Processed dataset hash mismatch for {name}: "
                f"recorded={processed_hashes[name]} "
                f"recomputed={recalculated_dataframe_hash}"
            )

        # ---------------------------------------------------------------------
        # Recalculate exported CSV file hash directly from disk.
        # ---------------------------------------------------------------------
        recomputed_file_hash = (
            calculate_file_sha256(
                output_path
            )
        )
        if (
            recomputed_file_hash
            != export_hashes[name]
        ):
            raise RuntimeError(
                f"Exported CSV file hash mismatch for {name}: "
                f"recorded={export_hashes[name]} "
                f"recomputed={recomputed_file_hash}"
            )

        # ---------------------------------------------------------------------
        # CRITICAL VALIDATION:
        #
        # The deterministic DataFrame representation and the actual
        # exported CSV file must have the exact same SHA-256 hash.
        #
        # Because export_dataset() uses the same:
        #
        #     index=False
        #     lineterminator="\\n"
        #     encoding="utf-8"
        #
        # and the same deterministic row ordering, these hashes should
        # be identical.
        # ---------------------------------------------------------------------
        if (
            recalculated_dataframe_hash
            != recomputed_file_hash
        ):
            raise RuntimeError(
                f"Processed DataFrame hash does not match exported "
                f"CSV hash for {name}: "
                f"dataframe_hash={recalculated_dataframe_hash} "
                f"file_hash={recomputed_file_hash}"
            )

        LOGGER.info(
            "REPRODUCIBILITY PASS | %-30s | "
            "dataframe_sha256=%s | file_sha256=%s",
            name,
            recalculated_dataframe_hash,
            recomputed_file_hash,
        )

    LOGGER.info(
        "REPRODUCIBILITY PASS | %d/%d exported CSV files verified "
        "against processed DataFrame hashes and file hashes",
        len(processed),
        len(processed),
    )


# -----------------------------------------------------------------------------
# Deterministic export
# -----------------------------------------------------------------------------
def export_dataset(
    df: pd.DataFrame,
    filename: str,
) -> str:
    """
    Export a processed dataset deterministically.

    Returns the SHA-256 hash of the exported CSV file.
    """
    output_path = (
        PROCESSED_DIR
        / filename
    )
    dataset_name = (
        Path(filename).stem
    )

    deterministic_df = (
        sort_dataframe_deterministically(
            df,
            dataset_name,
        )
    )

    # -------------------------------------------------------------------------
    # CHANGE 6: encoding is now pinned explicitly to "utf-8" so the export
    # matches, byte-for-byte in encoding terms, the explicit UTF-8 encoding
    # used in calculate_dataframe_sha256(). This removes an implicit
    # dependency on pandas' current default encoding remaining UTF-8.
    # -------------------------------------------------------------------------
    deterministic_df.to_csv(
        output_path,
        index=False,
        lineterminator="\n",
        encoding="utf-8",
    )

    file_hash = (
        calculate_file_sha256(
            output_path
        )
    )
    LOGGER.info(
        "Saved: %s | rows=%d | columns=%d | sha256=%s",
        output_path,
        len(deterministic_df),
        len(deterministic_df.columns),
        file_hash,
    )
    return file_hash


# =============================================================================
# STEP 16 — EXECUTION VALIDATION
# =============================================================================
def validate_cleaned_data_unchanged(
    cleaned_dir: Path,
) -> None:
    """
    Verify that the Phase 9 pipeline only reads cleaned data.

    This is a structural guard.

    The pipeline contains no code path that writes to, deletes from,
    renames, or otherwise modifies anything inside cleaned_dir.

    This function only confirms that the directory exists and is
    available as a read-only source of truth.
    """
    if not cleaned_dir.exists():
        raise FileNotFoundError(
            "Cleaned data directory does not exist: "
            f"{cleaned_dir}"
        )
    if not cleaned_dir.is_dir():
        raise NotADirectoryError(
            "Cleaned data path is not a directory: "
            f"{cleaned_dir}"
        )
    LOGGER.info(
        "REPRODUCIBILITY PASS | cleaned directory exists and is treated "
        "as READ-ONLY: %s",
        cleaned_dir,
    )


def validate_processed_outputs(
    processed: dict[str, pd.DataFrame],
) -> None:
    """
    Final sanity checks for all processed outputs.
    """
    if not processed:
        raise RuntimeError(
            "Processed dataset registry is empty."
        )

    for name, df in processed.items():
        if df.empty:
            raise RuntimeError(
                f"Processed dataset is empty: {name}"
            )
        if len(df.columns) == 0:
            raise RuntimeError(
                f"Processed dataset has no columns: {name}"
            )
        if name not in SORT_RULES:
            raise ValueError(
                "No deterministic sort rule registered for "
                f"processed dataset: {name}"
            )

    LOGGER.info(
        "REPRODUCIBILITY PASS | all %d processed datasets are non-empty "
        "and have a registered deterministic sort rule",
        len(processed),
    )


# =============================================================================
# MAIN
# =============================================================================
def main():
    # =========================================================================
    # INITIALIZE DIRECTORIES
    #
    # Only PROCESSED_DIR and REPORT_DIR are created or written to.
    #
    # CLEANED_DIR is never created, written to, or modified.
    # =========================================================================
    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )
    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # =========================================================================
    # CHANGE 2 — REMOVE STALE SUMMARY FROM ANY PREVIOUS RUN
    #
    # processing_summary.json is only ever written at the very end of
    # main(), after every validation in THIS run has passed. If a previous
    # run wrote it and this run fails partway through, the old file would
    # otherwise remain on disk and misleadingly look like current evidence
    # of a successful run. Removing it up front means the file's mere
    # existence after this call is now a trustworthy signal.
    # =========================================================================
    stale_summary_path = (
        REPORT_DIR / "processing_summary.json"
    )
    if stale_summary_path.exists():
        stale_summary_path.unlink()

    # =========================================================================
    # RESET PIPELINE STATE
    #
    # These globals are cleared at the start of every main() execution
    # so that no run depends on results left over from a previous run.
    # =========================================================================
    JOIN_VALIDATION_RESULTS.clear()
    GRAIN_VALIDATION_RESULTS.clear()
    TRACEABILITY_RESULTS.clear()

    # =========================================================================
    # STEP 16 — REPRODUCIBLE EXECUTION CONFIGURATION
    # =========================================================================
    cleaned_dir = CLEANED_DIR
    validate_cleaned_data_unchanged(
        cleaned_dir
    )

    # -------------------------------------------------------------------------
    # Configure logging
    # -------------------------------------------------------------------------
    log_path = (
        configure_file_logging()
    )

    LOGGER.info("=" * 80)
    LOGGER.info(
        "PHASE 9 — PYTHON DATA PROCESSING"
    )
    LOGGER.info(
        "STEPS 7 + 8 + 9 + 10 + 11 + 13 + 14 + 16"
    )
    LOGGER.info("=" * 80)
    LOGGER.info(
        "REPRODUCIBILITY | deterministic execution enabled"
    )
    LOGGER.info(
        "REPRODUCIBILITY | input source = data/cleaned/ (read-only)"
    )
    LOGGER.info(
        "REPRODUCIBILITY | output destination = data/processed/"
    )
    LOGGER.info(
        "REPRODUCIBILITY | report destination = "
        "reports/python_processing/"
    )
    LOGGER.info(
        "REPRODUCIBILITY | execution log = %s",
        log_path,
    )

    # =========================================================================
    # STEP 7 — EXTRACT CLEANED DATASETS
    # =========================================================================
    LOGGER.info("=" * 80)
    LOGGER.info(
        "STEP 7 — EXTRACT CLEANED DATASETS"
    )
    LOGGER.info("=" * 80)

    datasets = (
        load_all_datasets()
    )
    LOGGER.info(
        "STEP 7 | load_all_datasets() returned successfully | "
        "dataset_count=%d",
        len(datasets),
    )

    required_datasets = [
        "customers",
        "geolocation",
        "orders",
        "order_items",
        "payments",
        "reviews",
        "products",
        "sellers",
        "category_translation",
    ]
    for dataset_name in required_datasets:
        if dataset_name not in datasets:
            raise ValueError(
                "Required dataset not loaded: "
                f"{dataset_name}"
            )
        LOGGER.info(
            "INPUT | %-25s | rows=%d | columns=%d",
            dataset_name,
            len(
                datasets[
                    dataset_name
                ]
            ),
            len(
                datasets[
                    dataset_name
                ].columns
            ),
        )
    LOGGER.info(
        "STEP 7 — ALL 9 DATASETS LOADED SUCCESSFULLY"
    )

    # =========================================================================
    # STEP 5 — ANALYSIS-READY DTYPE VALIDATION
    # =========================================================================
    validate_analysis_ready_dtypes(
        datasets
    )

    # -------------------------------------------------------------------------
    # STEP 16 — Deterministic fingerprint of cleaned inputs.
    #
    # This happens before transformation logic.
    # -------------------------------------------------------------------------
    input_fingerprints = (
        log_input_fingerprints(
            datasets
        )
    )

    # =========================================================================
    # STEP 7 — BUILD ANALYTICAL DATASETS
    # =========================================================================
    LOGGER.info("=" * 80)
    LOGGER.info(
        "STEP 7 — BUILD ANALYTICAL DATASETS"
    )
    LOGGER.info("=" * 80)

    orders_processed = (
        build_orders_processed(
            datasets["orders"],
            datasets["customers"],
        )
    )
    order_items_processed = (
        build_order_items_processed(
            datasets["order_items"],
            datasets["orders"],
            datasets["products"],
            datasets["sellers"],
            datasets["category_translation"],
        )
    )
    payments_processed = (
        build_payments_processed(
            datasets["payments"],
            datasets["orders"],
        )
    )
    reviews_processed = (
        build_reviews_processed(
            datasets["reviews"],
            datasets["orders"],
            datasets["customers"],
        )
    )
    geography_processed = (
        build_geography_processed(
            datasets["geolocation"],
        )
    )
    customers_processed = (
        build_customers_processed(
            datasets["customers"],
        )
    )
    products_processed = (
        build_products_processed(
            datasets["products"],
        )
    )
    sellers_processed = (
        build_sellers_processed(
            datasets["sellers"],
        )
    )

    # =========================================================================
    # STEP 8 — CONTROLLED TRANSFORMATIONS
    # =========================================================================
    LOGGER.info("=" * 80)
    LOGGER.info(
        "STEP 8 — CONTROLLED TRANSFORMATIONS"
    )
    LOGGER.info("=" * 80)

    orders_processed = (
        apply_order_time_fields(
            orders_processed
        )
    )
    order_items_processed = (
        apply_order_item_fields(
            order_items_processed
        )
    )

    # =========================================================================
    # PROCESSED DATASET REGISTRY
    # =========================================================================
    processed = {
        "orders_processed": orders_processed,
        "order_items_processed": order_items_processed,
        "payments_processed": payments_processed,
        "reviews_processed": reviews_processed,
        "customers_processed": customers_processed,
        "products_processed": products_processed,
        "sellers_processed": sellers_processed,
        "geography_processed": geography_processed,
    }

    # =========================================================================
    # STEP 9 — SOURCE TRACEABILITY
    # =========================================================================
    validate_all_traceability(
        datasets,
        processed,
    )
    save_traceability_report()

    # =========================================================================
    # STEP 10 — JOIN VALIDATION
    # =========================================================================
    LOGGER.info("=" * 80)
    LOGGER.info(
        "STEP 10 — JOIN VALIDATION"
    )
    LOGGER.info("=" * 80)

    save_join_validation_report()

    join_report = pd.DataFrame(
        JOIN_VALIDATION_RESULTS
    )
    if join_report.empty:
        raise RuntimeError(
            "Join validation report is empty."
        )
    failed_joins = join_report[
        join_report["status"] != "PASS"
    ]
    if not failed_joins.empty:
        raise RuntimeError(
            "Join validation failed:\n"
            f"{failed_joins.to_string(index=False)}"
        )
    LOGGER.info(
        "All %d joins PASSED.",
        len(join_report),
    )

    # =========================================================================
    # STEP 11 — ANALYTICAL GRAIN VALIDATION
    # =========================================================================
    validate_all_analytical_grains(
        processed
    )
    save_grain_validation_report()

    # =========================================================================
    # STEP 13 — EXPORT
    # =========================================================================
    LOGGER.info("=" * 80)
    LOGGER.info(
        "STEP 13 — EXPORTING PROCESSED DATASETS"
    )
    LOGGER.info("=" * 80)

    export_hashes: dict[str, str] = {}

    export_hashes[
        "orders_processed"
    ] = export_dataset(
        orders_processed,
        "orders_processed.csv",
    )
    export_hashes[
        "order_items_processed"
    ] = export_dataset(
        order_items_processed,
        "order_items_processed.csv",
    )
    export_hashes[
        "payments_processed"
    ] = export_dataset(
        payments_processed,
        "payments_processed.csv",
    )
    export_hashes[
        "reviews_processed"
    ] = export_dataset(
        reviews_processed,
        "reviews_processed.csv",
    )
    export_hashes[
        "customers_processed"
    ] = export_dataset(
        customers_processed,
        "customers_processed.csv",
    )
    export_hashes[
        "products_processed"
    ] = export_dataset(
        products_processed,
        "products_processed.csv",
    )
    export_hashes[
        "sellers_processed"
    ] = export_dataset(
        sellers_processed,
        "sellers_processed.csv",
    )
    export_hashes[
        "geography_processed"
    ] = export_dataset(
        geography_processed,
        "geography_processed.csv",
    )

    # =========================================================================
    # STEP 14 — VALIDATION EVIDENCE
    # =========================================================================
    LOGGER.info("=" * 80)
    LOGGER.info(
        "STEP 14 — PHASE 9 VALIDATION EVIDENCE"
    )
    LOGGER.info("=" * 80)

    save_dataset_statistics(
        datasets,
        processed,
    )
    save_processing_validation(
        datasets,
        processed,
    )

    # -------------------------------------------------------------------------
    # processing_summary.json is intentionally NOT written here.
    #
    # It is written only after Step 16 succeeds.
    # -------------------------------------------------------------------------

    # =========================================================================
    # STEP 16 — REPRODUCIBILITY VALIDATION
    # =========================================================================
    LOGGER.info("=" * 80)
    LOGGER.info(
        "STEP 16 — REPRODUCIBILITY VALIDATION"
    )
    LOGGER.info("=" * 80)

    # -------------------------------------------------------------------------
    # Structural validation of every processed dataset.
    # -------------------------------------------------------------------------
    validate_processed_outputs(
        processed
    )

    # -------------------------------------------------------------------------
    # Deterministically sort + hash every input and processed dataset.
    # -------------------------------------------------------------------------
    (
        input_hashes,
        processed_hashes,
    ) = save_reproducibility_report(
        datasets,
        processed,
    )

    # -------------------------------------------------------------------------
    # Every input dataset must have a hash.
    # -------------------------------------------------------------------------
    if len(input_hashes) != len(datasets):
        raise RuntimeError(
            "Reproducibility validation failed: "
            "not every input dataset produced a hash."
        )

    # -------------------------------------------------------------------------
    # Every processed dataset must have a hash.
    # -------------------------------------------------------------------------
    if len(processed_hashes) != len(processed):
        raise RuntimeError(
            "Reproducibility validation failed: "
            "not every processed dataset produced a hash."
        )

    # -------------------------------------------------------------------------
    # Input hashes must match the fingerprints calculated BEFORE
    # transformation began.
    # -------------------------------------------------------------------------
    if input_hashes != input_fingerprints:
        raise RuntimeError(
            "Reproducibility validation failed: input dataset hashes "
            "computed during reproducibility reporting do not match "
            "the fingerprints computed before transformation began."
        )

    LOGGER.info(
        "REPRODUCIBILITY PASS | %d/%d input dataset hashes computed "
        "and verified consistent with pre-transformation fingerprints",
        len(input_hashes),
        len(datasets),
    )
    LOGGER.info(
        "REPRODUCIBILITY PASS | %d/%d processed dataset hashes computed",
        len(processed_hashes),
        len(processed),
    )

    # -------------------------------------------------------------------------
    # Strong export validation.
    #
    # This now independently verifies:
    #
    #     processed DataFrame hash
    #             ==
    #     exported CSV hash
    #
    # and also confirms both recorded hashes remain unchanged.
    # -------------------------------------------------------------------------
    validate_exported_datasets(
        processed,
        export_hashes,
        processed_hashes,
    )

    LOGGER.info(
        "REPRODUCIBILITY | deterministic sort keys + full-row "
        "tie-breaker applied to all input and processed datasets"
    )
    LOGGER.info(
        "REPRODUCIBILITY | execution_timestamp in "
        "processing_summary.json is metadata only and is excluded "
        "from all dataset hashes"
    )
    LOGGER.info(
        "REPRODUCIBILITY | pipeline state (validation result lists) "
        "reset at the start of this run; no dependency on previous runs"
    )
    LOGGER.info(
        "REPRODUCIBILITY | data/cleaned/ was only read, never written to"
    )
    LOGGER.info(
        "REPRODUCIBILITY | execution logging enabled: %s",
        log_path,
    )

    # =========================================================================
    # FINAL SUMMARY
    #
    # Written ONLY after every validation above has succeeded.
    # =========================================================================
    save_processing_summary(
        datasets,
        processed,
        steps_completed=[
            "Step 7 — Analytical integration datasets",
            "Step 8 — Controlled analytical transformations",
            "Step 9 — Source traceability",
            "Step 10 — Join validation",
            "Step 11 — Analytical grain validation",
            "Step 13 — Processed dataset export",
            "Step 14 — Validation evidence",
            "Step 16 — Reproducible pipeline execution",
        ],
        status="PASS",
    )

    # =========================================================================
    # FINAL STATUS
    # =========================================================================
    LOGGER.info("=" * 80)
    LOGGER.info(
        "PHASE 9 — STEPS 7 + 8 + 9 + 10 + 11 + 13 + 14 + 16 COMPLETE"
    )
    LOGGER.info("=" * 80)
    for name, df in processed.items():
        LOGGER.info(
            "OUTPUT | %-30s | rows=%d | columns=%d | sha256=%s",
            name,
            len(df),
            len(df.columns),
            processed_hashes.get(
                name,
                "N/A",
            ),
        )
    LOGGER.info("=" * 80)
    LOGGER.info(
        "PHASE 9 PIPELINE COMPLETED SUCCESSFULLY"
    )
    LOGGER.info("=" * 80)


# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    main()