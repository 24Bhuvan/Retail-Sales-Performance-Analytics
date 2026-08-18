"""
Phase 4 — Data Quality Assessment
Retail Sales Performance Analytics

Purpose
-------
Identify, validate, quantify, classify, and prioritize data-quality issues
across all 9 Olist datasets.

This script:
    1. Loads all raw datasets.
    2. Executes explicit data-quality rules.
    3. Produces machine-readable validation results.
    4. Produces dataset-level quality summaries.
    5. Produces referential-integrity results.
    6. Produces a JSON execution summary.

IMPORTANT
---------
This script is READ-ONLY against data/raw/.

It does NOT:
    - clean data
    - remove duplicates
    - impute missing values
    - modify raw CSV files
    - overwrite source data

Cleaning belongs to Phase 5.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "data_quality"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# LOGGING
# =============================================================================

LOG_FILE = OUTPUT_DIR / "data_quality_assessment.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


# =============================================================================
# DATASET CONFIGURATION
# =============================================================================

DATASETS = {
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
# EXPECTED SCHEMAS
# =============================================================================

EXPECTED_COLUMNS = {
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
    "order_items": [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
    ],
    "payments": [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_installments",
        "payment_value",
    ],
    "reviews": [
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
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
    "category_translation": [
        "product_category_name",
        "product_category_name_english",
    ],
}


# =============================================================================
# PRIMARY / COMPOSITE KEYS
# =============================================================================

PRIMARY_KEYS = {
    "customers": ["customer_id"],
    "geolocation": [],  # No declared single PK
    "orders": ["order_id"],
    "order_items": ["order_id", "order_item_id"],
    "payments": ["order_id", "payment_sequential"],
    "reviews": [],  # review_id is assessed for duplicate occurrences
    "products": ["product_id"],
    "sellers": ["seller_id"],
    "category_translation": ["product_category_name"],
}


# =============================================================================
# EXPECTED DATA TYPES
# =============================================================================

EXPECTED_DTYPES = {
    "customers": {
        "customer_id": "string",
        "customer_unique_id": "string",
        "customer_zip_code_prefix": "integer",
        "customer_city": "string",
        "customer_state": "string",
    },
    "geolocation": {
        "geolocation_zip_code_prefix": "integer",
        "geolocation_lat": "numeric",
        "geolocation_lng": "numeric",
        "geolocation_city": "string",
        "geolocation_state": "string",
    },
    "orders": {
        "order_id": "string",
        "customer_id": "string",
        "order_status": "string",
        "order_purchase_timestamp": "datetime",
        "order_approved_at": "datetime",
        "order_delivered_carrier_date": "datetime",
        "order_delivered_customer_date": "datetime",
        "order_estimated_delivery_date": "datetime",
    },
    "order_items": {
        "order_id": "string",
        "order_item_id": "integer",
        "product_id": "string",
        "seller_id": "string",
        "shipping_limit_date": "datetime",
        "price": "numeric",
        "freight_value": "numeric",
    },
    "payments": {
        "order_id": "string",
        "payment_sequential": "integer",
        "payment_type": "string",
        "payment_installments": "integer",
        "payment_value": "numeric",
    },
    "reviews": {
        "review_id": "string",
        "order_id": "string",
        "review_score": "integer",
        "review_comment_title": "string",
        "review_comment_message": "string",
        "review_creation_date": "datetime",
        "review_answer_timestamp": "datetime",
    },
    "products": {
        "product_id": "string",
        "product_category_name": "string",
        "product_name_lenght": "numeric",
        "product_description_lenght": "numeric",
        "product_photos_qty": "numeric",
        "product_weight_g": "numeric",
        "product_length_cm": "numeric",
        "product_height_cm": "numeric",
        "product_width_cm": "numeric",
    },
    "sellers": {
        "seller_id": "string",
        "seller_zip_code_prefix": "integer",
        "seller_city": "string",
        "seller_state": "string",
    },
    "category_translation": {
        "product_category_name": "string",
        "product_category_name_english": "string",
    },
}


# =============================================================================
# DOMAIN DEFINITIONS
# =============================================================================

VALID_ORDER_STATUSES = {
    "delivered",
    "shipped",
    "canceled",
    "invoiced",
    "processing",
    "unavailable",
    "approved",
    "created",
}

VALID_PAYMENT_TYPES = {
    "credit_card",
    "boleto",
    "voucher",
    "debit_card",
    "not_defined",
}

VALID_BRAZILIAN_STATES = {
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
}


# =============================================================================
# RESULT STORAGE
# =============================================================================

QUALITY_RESULTS: list[dict[str, Any]] = []


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def normalize_value(value: Any) -> Any:
    """Convert Pandas/NumPy values into JSON-safe Python values."""

    if pd.isna(value):
        return None

    if isinstance(value, (np.integer,)):
        return int(value)

    if isinstance(value, (np.floating,)):
        return float(value)

    if isinstance(value, (np.bool_,)):
        return bool(value)

    return value


def add_result(
    test_id: str,
    dataset: str,
    column: str,
    quality_dimension: str,
    rule: str,
    expected: str,
    actual: str,
    failed_count: int,
    total_count: int,
    severity: str,
) -> None:
    """Add one standardized data-quality result."""

    failure_rate = (
        (failed_count / total_count) * 100
        if total_count > 0
        else 0.0
    )

    status = "PASS" if failed_count == 0 else "FAIL"

    QUALITY_RESULTS.append(
        {
            "TEST_ID": test_id,
            "DATASET": dataset,
            "COLUMN": column,
            "QUALITY_DIMENSION": quality_dimension,
            "RULE": rule,
            "EXPECTED": expected,
            "ACTUAL": actual,
            "FAILED_COUNT": int(failed_count),
            "FAILURE_RATE": round(failure_rate, 4),
            "SEVERITY": severity if failed_count > 0 else "NONE",
            "STATUS": status,
        }
    )


def load_dataset(dataset_name: str, filename: str) -> pd.DataFrame | None:
    """Load one raw CSV without modifying it."""

    file_path = RAW_DIR / filename

    if not file_path.exists():
        logger.error("Missing dataset: %s", file_path)

        add_result(
            test_id=f"DQ-EXIST-{dataset_name.upper()}",
            dataset=dataset_name,
            column="__DATASET__",
            quality_dimension="Completeness",
            rule="Expected raw dataset file must exist",
            expected="File exists",
            actual="File not found",
            failed_count=1,
            total_count=1,
            severity="CRITICAL",
        )

        return None

    try:
        df = pd.read_csv(
            file_path,
            low_memory=False,
        )

        logger.info(
            "Loaded %-20s | rows=%-10s | columns=%s",
            dataset_name,
            len(df),
            len(df.columns),
        )

        return df

    except Exception as exc:
        logger.exception(
            "Failed to load %s: %s",
            file_path,
            exc,
        )

        add_result(
            test_id=f"DQ-LOAD-{dataset_name.upper()}",
            dataset=dataset_name,
            column="__DATASET__",
            quality_dimension="Validity",
            rule="Dataset must be readable as CSV",
            expected="Readable CSV",
            actual=str(exc),
            failed_count=1,
            total_count=1,
            severity="CRITICAL",
        )

        return None


def is_integer_dtype(series: pd.Series) -> bool:
    """Check whether a Pandas series is integer-like."""

    return pd.api.types.is_integer_dtype(series)


def is_numeric_dtype(series: pd.Series) -> bool:
    """Check whether a Pandas series is numeric."""

    return pd.api.types.is_numeric_dtype(series)


def is_datetime_dtype(series: pd.Series) -> bool:
    """Check whether a Pandas series is datetime."""

    return pd.api.types.is_datetime64_any_dtype(series)


def is_string_like_dtype(series: pd.Series) -> bool:
    """Accept object/string/category for textual Olist fields."""

    return (
        pd.api.types.is_object_dtype(series)
        or pd.api.types.is_string_dtype(series)
        or pd.api.types.is_categorical_dtype(series)
    )


def expected_dtype_matches(
    series: pd.Series,
    expected_type: str,
) -> bool:
    """Validate a series against the expected logical type."""

    if expected_type == "integer":
        return is_integer_dtype(series)

    if expected_type == "numeric":
        return is_numeric_dtype(series)

    if expected_type == "datetime":
        return is_datetime_dtype(series)

    if expected_type == "string":
        return is_string_like_dtype(series)

    return True


def check_dataset_existence(datasets: dict[str, pd.DataFrame | None]) -> None:
    """Test 01 — Dataset existence."""

    for dataset_name in DATASETS:
        if datasets.get(dataset_name) is None:
            continue

        add_result(
            test_id=f"DQ-EXIST-{dataset_name.upper()}",
            dataset=dataset_name,
            column="__DATASET__",
            quality_dimension="Completeness",
            rule="Expected raw dataset file must exist",
            expected="Dataset exists",
            actual="Dataset exists",
            failed_count=0,
            total_count=1,
            severity="CRITICAL",
        )


def check_row_column_counts(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Test 02 — Row and column counts."""

    for dataset_name, df in datasets.items():

        if df is None:
            continue

        expected_columns = EXPECTED_COLUMNS[dataset_name]

        missing_columns = set(expected_columns) - set(df.columns)
        unexpected_columns = set(df.columns) - set(expected_columns)

        actual = (
            f"rows={len(df)}, "
            f"columns={len(df.columns)}, "
            f"missing_columns={sorted(missing_columns)}, "
            f"unexpected_columns={sorted(unexpected_columns)}"
        )

        failed = 1 if missing_columns else 0

        add_result(
            test_id=f"DQ-SCHEMA-{dataset_name.upper()}",
            dataset=dataset_name,
            column="__DATASET__",
            quality_dimension="Conformity",
            rule="Dataset schema must contain all expected columns",
            expected=f"Required columns={expected_columns}",
            actual=actual,
            failed_count=failed,
            total_count=1,
            severity="CRITICAL",
        )


def check_missing_values(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Test 03 — Missing-value checks."""

    test_number = 1

    for dataset_name, df in datasets.items():

        if df is None:
            continue

        for column in df.columns:

            missing_count = int(df[column].isna().sum())

            # Missing values are reported rather than universally treated
            # as errors because some Olist columns legitimately contain NULLs.
            severity = (
                "HIGH"
                if missing_count > 0
                and column in PRIMARY_KEYS.get(dataset_name, [])
                else "MEDIUM"
            )

            add_result(
                test_id=f"DQ-MISS-{test_number:04d}",
                dataset=dataset_name,
                column=column,
                quality_dimension="Completeness",
                rule="Column should not contain unexpected missing values",
                expected="0 missing values unless business rule permits NULL",
                actual=f"{missing_count} missing values",
                failed_count=missing_count,
                total_count=len(df),
                severity=severity,
            )

            test_number += 1


def check_primary_key_nulls(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Test 04 — Primary-key null checks."""

    test_number = 1

    for dataset_name, df in datasets.items():

        if df is None:
            continue

        for key_column in PRIMARY_KEYS.get(dataset_name, []):

            if key_column not in df.columns:
                continue

            null_count = int(df[key_column].isna().sum())

            add_result(
                test_id=f"DQ-PKNULL-{test_number:04d}",
                dataset=dataset_name,
                column=key_column,
                quality_dimension="Completeness",
                rule=f"Primary key {key_column} must not be NULL",
                expected="0 NULL values",
                actual=f"{null_count} NULL values",
                failed_count=null_count,
                total_count=len(df),
                severity="CRITICAL",
            )

            test_number += 1


def check_primary_key_uniqueness(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Test 05 — Primary/composite-key uniqueness."""

    test_number = 1

    for dataset_name, df in datasets.items():

        if df is None:
            continue

        keys = PRIMARY_KEYS.get(dataset_name, [])

        if not keys:
            continue

        duplicate_mask = df.duplicated(
            subset=keys,
            keep=False,
        )

        duplicate_count = int(duplicate_mask.sum())

        key_name = ", ".join(keys)

        add_result(
            test_id=f"DQ-PKUNIQ-{test_number:04d}",
            dataset=dataset_name,
            column=key_name,
            quality_dimension="Uniqueness",
            rule=f"Primary/composite key ({key_name}) must be unique",
            expected="No duplicate key combinations",
            actual=f"{duplicate_count} rows participate in duplicate keys",
            failed_count=duplicate_count,
            total_count=len(df),
            severity="CRITICAL",
        )

        test_number += 1


def check_full_row_duplicates(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Test 06 — Full-row duplicate checks."""

    test_number = 1

    for dataset_name, df in datasets.items():

        if df is None:
            continue

        duplicate_count = int(
            df.duplicated(
                keep=False
            ).sum()
        )

        add_result(
            test_id=f"DQ-DUP-{test_number:04d}",
            dataset=dataset_name,
            column="__FULL_ROW__",
            quality_dimension="Uniqueness",
            rule="Exact duplicate rows should not exist unless explicitly justified",
            expected="0 exact duplicate rows",
            actual=f"{duplicate_count} rows are exact duplicates",
            failed_count=duplicate_count,
            total_count=len(df),
            severity="MEDIUM",
        )

        test_number += 1


def check_data_types(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Test 07 — Logical data-type checks."""

    test_number = 1

    for dataset_name, df in datasets.items():

        if df is None:
            continue

        expected_types = EXPECTED_DTYPES[dataset_name]

        for column, expected_type in expected_types.items():

            if column not in df.columns:
                continue

            actual_dtype = str(df[column].dtype)

            # Date columns are explicitly parsed before this test.
            if expected_type == "datetime":
                try:
                    parsed = pd.to_datetime(
                        df[column],
                        errors="coerce",
                    )

                    non_null_original = int(df[column].notna().sum())
                    invalid_dates = int(
                        parsed.notna().sum() < non_null_original
                    )

                    # The actual failure count is calculated precisely.
                    failed_count = int(
                        (
                            df[column].notna()
                            & parsed.isna()
                        ).sum()
                    )

                except Exception:
                    failed_count = len(df)

            else:
                failed_count = (
                    0
                    if expected_dtype_matches(
                        df[column],
                        expected_type,
                    )
                    else len(df)
                )

            add_result(
                test_id=f"DQ-DTYPE-{test_number:04d}",
                dataset=dataset_name,
                column=column,
                quality_dimension="Conformity",
                rule=f"Column must conform to logical type '{expected_type}'",
                expected=expected_type,
                actual=actual_dtype,
                failed_count=failed_count,
                total_count=len(df),
                severity="HIGH",
            )

            test_number += 1


def check_domain_ranges(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Test 08 — Domain and range validation."""

    test_number = 1

    # -------------------------------------------------------------------------
    # Review score
    # -------------------------------------------------------------------------

    df = datasets.get("reviews")

    if df is not None and "review_score" in df.columns:

        invalid = ~df["review_score"].isna() & ~df[
            "review_score"
        ].between(1, 5)

        failed_count = int(invalid.sum())

        add_result(
            test_id=f"DQ-DOMAIN-{test_number:04d}",
            dataset="reviews",
            column="review_score",
            quality_dimension="Validity",
            rule="Review score must be between 1 and 5",
            expected="1 <= review_score <= 5",
            actual=f"{failed_count} values outside valid range",
            failed_count=failed_count,
            total_count=len(df),
            severity="HIGH",
        )

        test_number += 1

    # -------------------------------------------------------------------------
    # Order status
    # -------------------------------------------------------------------------

    df = datasets.get("orders")

    if df is not None and "order_status" in df.columns:

        invalid = ~df["order_status"].isna() & ~df[
            "order_status"
        ].isin(VALID_ORDER_STATUSES)

        failed_count = int(invalid.sum())

        add_result(
            test_id=f"DQ-DOMAIN-{test_number:04d}",
            dataset="orders",
            column="order_status",
            quality_dimension="Validity",
            rule="Order status must belong to the defined Olist status domain",
            expected=f"{sorted(VALID_ORDER_STATUSES)}",
            actual=f"{failed_count} invalid status values",
            failed_count=failed_count,
            total_count=len(df),
            severity="HIGH",
        )

        test_number += 1

    # -------------------------------------------------------------------------
    # Payment type
    # -------------------------------------------------------------------------

    df = datasets.get("payments")

    if df is not None and "payment_type" in df.columns:

        invalid = ~df["payment_type"].isna() & ~df[
            "payment_type"
        ].isin(VALID_PAYMENT_TYPES)

        failed_count = int(invalid.sum())

        add_result(
            test_id=f"DQ-DOMAIN-{test_number:04d}",
            dataset="payments",
            column="payment_type",
            quality_dimension="Validity",
            rule="Payment type must belong to the defined payment domain",
            expected=f"{sorted(VALID_PAYMENT_TYPES)}",
            actual=f"{failed_count} invalid payment types",
            failed_count=failed_count,
            total_count=len(df),
            severity="HIGH",
        )

        test_number += 1

    # -------------------------------------------------------------------------
    # Brazilian states
    # -------------------------------------------------------------------------

    state_columns = [
        ("customers", "customer_state"),
        ("sellers", "seller_state"),
        ("geolocation", "geolocation_state"),
    ]

    for dataset_name, column in state_columns:

        df = datasets.get(dataset_name)

        if df is None or column not in df.columns:
            continue

        invalid = ~df[column].isna() & ~df[column].isin(
            VALID_BRAZILIAN_STATES
        )

        failed_count = int(invalid.sum())

        add_result(
            test_id=f"DQ-DOMAIN-{test_number:04d}",
            dataset=dataset_name,
            column=column,
            quality_dimension="Validity",
            rule="State code must belong to Brazilian UF domain",
            expected=f"{sorted(VALID_BRAZILIAN_STATES)}",
            actual=f"{failed_count} invalid state codes",
            failed_count=failed_count,
            total_count=len(df),
            severity="MEDIUM",
        )

        test_number += 1


def check_zero_values(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Test 09 — Zero-value checks."""

    rules = [
        ("products", "product_weight_g"),
        ("products", "product_length_cm"),
        ("products", "product_height_cm"),
        ("products", "product_width_cm"),
        ("products", "product_photos_qty"),
        ("order_items", "price"),
        ("order_items", "freight_value"),
        ("payments", "payment_value"),
        ("payments", "payment_installments"),
    ]

    test_number = 1

    for dataset_name, column in rules:

        df = datasets.get(dataset_name)

        if df is None or column not in df.columns:
            continue

        zero_count = int(
            (df[column] == 0).sum()
        )

        add_result(
            test_id=f"DQ-ZERO-{test_number:04d}",
            dataset=dataset_name,
            column=column,
            quality_dimension="Validity",
            rule="Zero values should be reviewed for business validity",
            expected="No unexplained zero values",
            actual=f"{zero_count} zero values",
            failed_count=zero_count,
            total_count=len(df),
            severity="LOW",
        )

        test_number += 1


def check_negative_values(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Test 10 — Negative numeric-value checks."""

    numeric_columns = [
        ("order_items", "price"),
        ("order_items", "freight_value"),
        ("payments", "payment_value"),
        ("payments", "payment_installments"),
        ("products", "product_weight_g"),
        ("products", "product_length_cm"),
        ("products", "product_height_cm"),
        ("products", "product_width_cm"),
        ("products", "product_photos_qty"),
    ]

    test_number = 1

    for dataset_name, column in numeric_columns:

        df = datasets.get(dataset_name)

        if df is None or column not in df.columns:
            continue

        negative_count = int(
            (df[column] < 0).sum()
        )

        add_result(
            test_id=f"DQ-NEG-{test_number:04d}",
            dataset=dataset_name,
            column=column,
            quality_dimension="Validity",
            rule="Numeric field must not contain negative values",
            expected="0 negative values",
            actual=f"{negative_count} negative values",
            failed_count=negative_count,
            total_count=len(df),
            severity="HIGH",
        )

        test_number += 1


def check_date_parsing(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Test 11 — Date parsing checks."""

    date_columns = {
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

    test_number = 1

    for dataset_name, columns in date_columns.items():

        df = datasets.get(dataset_name)

        if df is None:
            continue

        for column in columns:

            if column not in df.columns:
                continue

            parsed = pd.to_datetime(
                df[column],
                errors="coerce",
            )

            invalid_count = int(
                (
                    df[column].notna()
                    & parsed.isna()
                ).sum()
            )

            add_result(
                test_id=f"DQ-DATEPARSE-{test_number:04d}",
                dataset=dataset_name,
                column=column,
                quality_dimension="Validity",
                rule="Non-null date values must be parseable as datetime",
                expected="0 unparseable non-null values",
                actual=f"{invalid_count} unparseable values",
                failed_count=invalid_count,
                total_count=len(df),
                severity="HIGH",
            )

            test_number += 1


def check_date_chronology(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Test 12 — Chronological business-rule checks."""

    df = datasets.get("orders")

    if df is None:
        return

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    parsed = {}

    for column in date_columns:

        if column in df.columns:

            parsed[column] = pd.to_datetime(
                df[column],
                errors="coerce",
            )

    chronology_rules = [
        (
            "order_approved_at",
            "order_purchase_timestamp",
            "Approval should not occur before purchase",
            "HIGH",
        ),
        (
            "order_delivered_carrier_date",
            "order_purchase_timestamp",
            "Carrier delivery should not occur before purchase",
            "HIGH",
        ),
        (
            "order_delivered_customer_date",
            "order_purchase_timestamp",
            "Customer delivery should not occur before purchase",
            "HIGH",
        ),
        (
            "order_delivered_customer_date",
            "order_delivered_carrier_date",
            "Customer delivery should not occur before carrier delivery",
            "HIGH",
        ),
    ]

    test_number = 1

    for later_column, earlier_column, rule, severity in chronology_rules:

        if (
            later_column not in parsed
            or earlier_column not in parsed
        ):
            continue

        invalid = (
            parsed[later_column].notna()
            & parsed[earlier_column].notna()
            & (
                parsed[later_column]
                < parsed[earlier_column]
            )
        )

        failed_count = int(invalid.sum())

        add_result(
            test_id=f"DQ-CHRON-{test_number:04d}",
            dataset="orders",
            column=f"{earlier_column} -> {later_column}",
            quality_dimension="Consistency",
            rule=rule,
            expected="Chronological order must be valid",
            actual=f"{failed_count} chronology violations",
            failed_count=failed_count,
            total_count=len(df),
            severity=severity,
        )

        test_number += 1


def check_referential_integrity(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Test 13 — Foreign-key / parent-child relationship checks."""

    relationships = [
        (
            "orders",
            "customer_id",
            "customers",
            "customer_id",
            "Order customer_id must exist in customers.customer_id",
            "HIGH",
        ),
        (
            "order_items",
            "order_id",
            "orders",
            "order_id",
            "Order item order_id must exist in orders.order_id",
            "CRITICAL",
        ),
        (
            "order_items",
            "product_id",
            "products",
            "product_id",
            "Order item product_id must exist in products.product_id",
            "CRITICAL",
        ),
        (
            "order_items",
            "seller_id",
            "sellers",
            "seller_id",
            "Order item seller_id must exist in sellers.seller_id",
            "CRITICAL",
        ),
        (
            "payments",
            "order_id",
            "orders",
            "order_id",
            "Payment order_id must exist in orders.order_id",
            "HIGH",
        ),
        (
            "reviews",
            "order_id",
            "orders",
            "order_id",
            "Review order_id must exist in orders.order_id",
            "HIGH",
        ),
    ]

    test_number = 1

    for (
        child_dataset,
        child_column,
        parent_dataset,
        parent_column,
        rule,
        severity,
    ) in relationships:

        child = datasets.get(child_dataset)
        parent = datasets.get(parent_dataset)

        if child is None or parent is None:
            continue

        if (
            child_column not in child.columns
            or parent_column not in parent.columns
        ):
            continue

        parent_keys = set(
            parent[parent_column]
            .dropna()
            .astype(str)
        )

        child_values = child[child_column]

        orphan_mask = (
            child_values.notna()
            & ~child_values.astype(str).isin(parent_keys)
        )

        orphan_count = int(orphan_mask.sum())

        add_result(
            test_id=f"DQ-FK-{test_number:04d}",
            dataset=child_dataset,
            column=child_column,
            quality_dimension="Referential Integrity",
            rule=rule,
            expected="All non-null child keys match parent keys",
            actual=f"{orphan_count} orphan records",
            failed_count=orphan_count,
            total_count=len(child),
            severity=severity,
        )

        test_number += 1


def check_categorical_conformity(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Test 14 — Categorical conformity checks."""

    categorical_rules = [
        (
            "orders",
            "order_status",
            VALID_ORDER_STATUSES,
            "Order status values must use the defined categorical domain",
        ),
        (
            "payments",
            "payment_type",
            VALID_PAYMENT_TYPES,
            "Payment type values must use the defined categorical domain",
        ),
        (
            "customers",
            "customer_state",
            VALID_BRAZILIAN_STATES,
            "Customer state values must use Brazilian UF codes",
        ),
        (
            "sellers",
            "seller_state",
            VALID_BRAZILIAN_STATES,
            "Seller state values must use Brazilian UF codes",
        ),
        (
            "geolocation",
            "geolocation_state",
            VALID_BRAZILIAN_STATES,
            "Geolocation state values must use Brazilian UF codes",
        ),
    ]

    test_number = 1

    for (
        dataset_name,
        column,
        valid_values,
        rule,
    ) in categorical_rules:

        df = datasets.get(dataset_name)

        if df is None or column not in df.columns:
            continue

        invalid_mask = (
            df[column].notna()
            & ~df[column].isin(valid_values)
        )

        invalid_count = int(invalid_mask.sum())

        actual_values = sorted(
            df.loc[
                invalid_mask,
                column,
            ].astype(str).unique().tolist()
        )

        add_result(
            test_id=f"DQ-CAT-{test_number:04d}",
            dataset=dataset_name,
            column=column,
            quality_dimension="Conformity",
            rule=rule,
            expected=f"Allowed values={sorted(valid_values)}",
            actual=(
                f"{invalid_count} invalid values; "
                f"examples={actual_values[:10]}"
            ),
            failed_count=invalid_count,
            total_count=len(df),
            severity="MEDIUM",
        )

        test_number += 1


def check_translation_coverage(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Test 15 — Product category translation coverage."""

    products = datasets.get("products")
    translation = datasets.get("category_translation")

    if products is None or translation is None:
        return

    if (
        "product_category_name" not in products.columns
        or "product_category_name" not in translation.columns
    ):
        return

    translated_categories = set(
        translation["product_category_name"]
        .dropna()
        .astype(str)
    )

    product_categories = (
        products["product_category_name"]
        .dropna()
        .astype(str)
    )

    missing_translation_mask = ~product_categories.isin(
        translated_categories
    )

    missing_count = int(
        missing_translation_mask.sum()
    )

    distinct_missing = int(
        product_categories[
            missing_translation_mask
        ].nunique()
    )

    add_result(
        test_id="DQ-TRANS-001",
        dataset="products",
        column="product_category_name",
        quality_dimension="Referential Integrity",
        rule=(
            "Non-null product categories should have a corresponding "
            "translation entry"
        ),
        expected="All non-null categories covered by translation table",
        actual=(
            f"{missing_count} product rows without translation; "
            f"{distinct_missing} distinct categories"
        ),
        failed_count=missing_count,
        total_count=len(products),
        severity="MEDIUM",
    )


def check_zip_code_relationships(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Test 16 — Customer/seller ZIP prefix coverage against geolocation."""

    geolocation = datasets.get("geolocation")
    customers = datasets.get("customers")
    sellers = datasets.get("sellers")

    if geolocation is None:
        return

    if "geolocation_zip_code_prefix" not in geolocation.columns:
        return

    geo_zip = set(
        geolocation["geolocation_zip_code_prefix"]
        .dropna()
        .astype(str)
    )

    relationships = [
        (
            "customers",
            "customer_zip_code_prefix",
            "Customer ZIP prefix should exist in geolocation",
        ),
        (
            "sellers",
            "seller_zip_code_prefix",
            "Seller ZIP prefix should exist in geolocation",
        ),
    ]

    test_number = 1

    for dataset_name, column, rule in relationships:

        df = datasets.get(dataset_name)

        if df is None or column not in df.columns:
            continue

        source_values = df[column]

        missing_mask = (
            source_values.notna()
            & ~source_values.astype(str).isin(geo_zip)
        )

        missing_count = int(missing_mask.sum())

        add_result(
            test_id=f"DQ-ZIP-{test_number:03d}",
            dataset=dataset_name,
            column=column,
            quality_dimension="Referential Integrity",
            rule=rule,
            expected="All non-null ZIP prefixes found in geolocation",
            actual=f"{missing_count} ZIP prefixes without geolocation match",
            failed_count=missing_count,
            total_count=len(df),
            severity="LOW",
        )

        test_number += 1


def check_numeric_plausibility(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Test 17 — Numeric plausibility checks."""

    # -------------------------------------------------------------------------
    # Geographic coordinates
    # -------------------------------------------------------------------------

    df = datasets.get("geolocation")

    if df is not None:

        coordinate_rules = [
            (
                "geolocation_lat",
                -90,
                90,
                "Latitude must be between -90 and 90",
            ),
            (
                "geolocation_lng",
                -180,
                180,
                "Longitude must be between -180 and 180",
            ),
        ]

        test_number = 1

        for column, minimum, maximum, rule in coordinate_rules:

            if column not in df.columns:
                continue

            invalid = (
                df[column].notna()
                & ~df[column].between(
                    minimum,
                    maximum,
                )
            )

            invalid_count = int(invalid.sum())

            add_result(
                test_id=f"DQ-NUM-{test_number:03d}",
                dataset="geolocation",
                column=column,
                quality_dimension="Validity",
                rule=rule,
                expected=f"{minimum} <= value <= {maximum}",
                actual=f"{invalid_count} implausible coordinate values",
                failed_count=invalid_count,
                total_count=len(df),
                severity="HIGH",
            )

            test_number += 1

    # -------------------------------------------------------------------------
    # ZIP prefix plausibility
    # -------------------------------------------------------------------------

    zip_rules = [
        (
            "customers",
            "customer_zip_code_prefix",
        ),
        (
            "sellers",
            "seller_zip_code_prefix",
        ),
        (
            "geolocation",
            "geolocation_zip_code_prefix",
        ),
    ]

    test_number = 10

    for dataset_name, column in zip_rules:

        df = datasets.get(dataset_name)

        if df is None or column not in df.columns:
            continue

        invalid = (
            df[column].notna()
            & (
                (df[column] < 0)
                | (df[column] > 99999)
            )
        )

        invalid_count = int(invalid.sum())

        add_result(
            test_id=f"DQ-NUM-{test_number:03d}",
            dataset=dataset_name,
            column=column,
            quality_dimension="Validity",
            rule="ZIP code prefix must be a five-digit numeric range",
            expected="0 <= ZIP prefix <= 99999",
            actual=f"{invalid_count} implausible ZIP prefixes",
            failed_count=invalid_count,
            total_count=len(df),
            severity="MEDIUM",
        )

        test_number += 1


def classify_quality_results() -> None:
    """
    Test 18 — Quality-rule result classification.

    The actual classification is already stored by add_result().
    This function provides a final sanity check that every rule has a
    valid status and severity classification.
    """

    valid_statuses = {"PASS", "FAIL"}
    valid_severities = {
        "NONE",
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }

    for result in QUALITY_RESULTS:

        if result["STATUS"] not in valid_statuses:
            raise ValueError(
                f"Invalid status: {result['STATUS']}"
            )

        if result["SEVERITY"] not in valid_severities:
            raise ValueError(
                f"Invalid severity: {result['SEVERITY']}"
            )


# =============================================================================
# SUMMARY GENERATION
# =============================================================================

def generate_dataset_summary() -> pd.DataFrame:
    """Generate dataset-level quality summary."""

    results_df = pd.DataFrame(QUALITY_RESULTS)

    if results_df.empty:
        return pd.DataFrame()

    summary_rows = []

    for dataset_name in DATASETS:

        dataset_results = results_df[
            results_df["DATASET"] == dataset_name
        ]

        if dataset_results.empty:
            continue

        failed = dataset_results[
            dataset_results["STATUS"] == "FAIL"
        ]

        summary_rows.append(
            {
                "DATASET": dataset_name,
                "TOTAL_TESTS": len(dataset_results),
                "PASSED_TESTS": int(
                    (dataset_results["STATUS"] == "PASS").sum()
                ),
                "FAILED_TESTS": int(
                    (dataset_results["STATUS"] == "FAIL").sum()
                ),
                "CRITICAL_ISSUES": int(
                    (failed["SEVERITY"] == "CRITICAL").sum()
                ),
                "HIGH_ISSUES": int(
                    (failed["SEVERITY"] == "HIGH").sum()
                ),
                "MEDIUM_ISSUES": int(
                    (failed["SEVERITY"] == "MEDIUM").sum()
                ),
                "LOW_ISSUES": int(
                    (failed["SEVERITY"] == "LOW").sum()
                ),
                "OVERALL_STATUS": (
                    "FAIL"
                    if not failed.empty
                    else "PASS"
                ),
            }
        )

    return pd.DataFrame(summary_rows)


def generate_quality_dimension_summary() -> pd.DataFrame:
    """Summarize failures by data-quality dimension."""

    results_df = pd.DataFrame(QUALITY_RESULTS)

    if results_df.empty:
        return pd.DataFrame()

    rows = []

    for dimension, group in results_df.groupby(
        "QUALITY_DIMENSION"
    ):

        failed = group[
            group["STATUS"] == "FAIL"
        ]

        rows.append(
            {
                "QUALITY_DIMENSION": dimension,
                "TOTAL_TESTS": len(group),
                "PASSED_TESTS": int(
                    (group["STATUS"] == "PASS").sum()
                ),
                "FAILED_TESTS": int(
                    (group["STATUS"] == "FAIL").sum()
                ),
                "CRITICAL_ISSUES": int(
                    (failed["SEVERITY"] == "CRITICAL").sum()
                ),
                "HIGH_ISSUES": int(
                    (failed["SEVERITY"] == "HIGH").sum()
                ),
                "MEDIUM_ISSUES": int(
                    (failed["SEVERITY"] == "MEDIUM").sum()
                ),
                "LOW_ISSUES": int(
                    (failed["SEVERITY"] == "LOW").sum()
                ),
            }
        )

    return pd.DataFrame(rows)


def generate_dataset_inventory(
    datasets: dict[str, pd.DataFrame | None],
) -> pd.DataFrame:
    """Create machine-readable dataset inventory for Phase 4."""

    rows = []

    for dataset_name in DATASETS:

        df = datasets.get(dataset_name)

        if df is None:
            rows.append(
                {
                    "DATASET": dataset_name,
                    "FILE": DATASETS[dataset_name],
                    "EXISTS": False,
                    "ROWS": None,
                    "COLUMNS": None,
                    "MEMORY_MB": None,
                }
            )

            continue

        rows.append(
            {
                "DATASET": dataset_name,
                "FILE": DATASETS[dataset_name],
                "EXISTS": True,
                "ROWS": len(df),
                "COLUMNS": len(df.columns),
                "MEMORY_MB": round(
                    df.memory_usage(
                        deep=True
                    ).sum()
                    / (1024 ** 2),
                    3,
                ),
            }
        )

    return pd.DataFrame(rows)


# =============================================================================
# JSON SUMMARY
# =============================================================================

def generate_json_summary(
    datasets: dict[str, pd.DataFrame | None],
) -> None:
    """Save a compact machine-readable execution summary."""

    results_df = pd.DataFrame(QUALITY_RESULTS)

    total_tests = len(results_df)

    passed_tests = int(
        (
            results_df["STATUS"] == "PASS"
        ).sum()
    ) if total_tests else 0

    failed_tests = int(
        (
            results_df["STATUS"] == "FAIL"
        ).sum()
    ) if total_tests else 0

    summary = {
        "phase": "Phase 4 — Data Quality Assessment",
        "project": "Retail Sales Performance Analytics",
        "raw_data_directory": str(RAW_DIR),
        "output_directory": str(OUTPUT_DIR),
        "raw_data_modified": False,
        "datasets_expected": len(DATASETS),
        "datasets_loaded": sum(
            df is not None
            for df in datasets.values()
        ),
        "datasets_failed_to_load": sum(
            df is None
            for df in datasets.values()
        ),
        "total_quality_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "critical_failures": (
            int(
                (
                    results_df["SEVERITY"] == "CRITICAL"
                ).sum()
            )
            if total_tests
            else 0
        ),
        "high_failures": (
            int(
                (
                    results_df["SEVERITY"] == "HIGH"
                ).sum()
            )
            if total_tests
            else 0
        ),
        "medium_failures": (
            int(
                (
                    results_df["SEVERITY"] == "MEDIUM"
                ).sum()
            )
            if total_tests
            else 0
        ),
        "low_failures": (
            int(
                (
                    results_df["SEVERITY"] == "LOW"
                ).sum()
            )
            if total_tests
            else 0
        ),
    }

    output_file = OUTPUT_DIR / "data_quality_summary.json"

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
        )


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main() -> None:
    """Run the complete Phase 4 Pandas data-quality assessment."""

    logger.info("=" * 80)
    logger.info("PHASE 4 — DATA QUALITY ASSESSMENT")
    logger.info("=" * 80)

    logger.info("Project root: %s", PROJECT_ROOT)
    logger.info("Raw data directory: %s", RAW_DIR)
    logger.info("Output directory: %s", OUTPUT_DIR)

    # -------------------------------------------------------------------------
    # LOAD DATA
    # -------------------------------------------------------------------------

    datasets: dict[str, pd.DataFrame | None] = {}

    for dataset_name, filename in DATASETS.items():

        datasets[dataset_name] = load_dataset(
            dataset_name,
            filename,
        )

    # -------------------------------------------------------------------------
    # EXECUTE QUALITY TESTS
    # -------------------------------------------------------------------------

    logger.info("Running Test 01 — Dataset existence")
    check_dataset_existence(datasets)

    logger.info("Running Test 02 — Row/column counts")
    check_row_column_counts(datasets)

    logger.info("Running Test 03 — Missing values")
    check_missing_values(datasets)

    logger.info("Running Test 04 — Primary-key NULLs")
    check_primary_key_nulls(datasets)

    logger.info("Running Test 05 — Primary-key uniqueness")
    check_primary_key_uniqueness(datasets)

    logger.info("Running Test 06 — Full-row duplicates")
    check_full_row_duplicates(datasets)

    logger.info("Running Test 07 — Data types")
    check_data_types(datasets)

    logger.info("Running Test 08 — Domain/range validity")
    check_domain_ranges(datasets)

    logger.info("Running Test 09 — Zero values")
    check_zero_values(datasets)

    logger.info("Running Test 10 — Negative values")
    check_negative_values(datasets)

    logger.info("Running Test 11 — Date parsing")
    check_date_parsing(datasets)

    logger.info("Running Test 12 — Date chronology")
    check_date_chronology(datasets)

    logger.info("Running Test 13 — Referential integrity")
    check_referential_integrity(datasets)

    logger.info("Running Test 14 — Categorical conformity")
    check_categorical_conformity(datasets)

    logger.info("Running Test 15 — Translation coverage")
    check_translation_coverage(datasets)

    logger.info("Running Test 16 — ZIP-code relationships")
    check_zip_code_relationships(datasets)

    logger.info("Running Test 17 — Numeric plausibility")
    check_numeric_plausibility(datasets)

    logger.info("Running Test 18 — Quality classification")
    classify_quality_results()

    # -------------------------------------------------------------------------
    # CREATE OUTPUT DATAFRAMES
    # -------------------------------------------------------------------------

    results_df = pd.DataFrame(QUALITY_RESULTS)

    dataset_summary_df = generate_dataset_summary()

    dimension_summary_df = (
        generate_quality_dimension_summary()
    )

    inventory_df = generate_dataset_inventory(
        datasets
    )

    # -------------------------------------------------------------------------
    # SAVE MACHINE-READABLE OUTPUTS
    # -------------------------------------------------------------------------

    results_file = (
        OUTPUT_DIR
        / "data_quality_results.csv"
    )

    summary_file = (
        OUTPUT_DIR
        / "data_quality_dataset_summary.csv"
    )

    dimension_file = (
        OUTPUT_DIR
        / "data_quality_dimension_summary.csv"
    )

    inventory_file = (
        OUTPUT_DIR
        / "data_quality_dataset_inventory.csv"
    )

    results_df.to_csv(
        results_file,
        index=False,
        encoding="utf-8-sig",
    )

    dataset_summary_df.to_csv(
        summary_file,
        index=False,
        encoding="utf-8-sig",
    )

    dimension_summary_df.to_csv(
        dimension_file,
        index=False,
        encoding="utf-8-sig",
    )

    inventory_df.to_csv(
        inventory_file,
        index=False,
        encoding="utf-8-sig",
    )

    generate_json_summary(datasets)

    # -------------------------------------------------------------------------
    # CONSOLE SUMMARY
    # -------------------------------------------------------------------------

    total_tests = len(results_df)

    passed = int(
        (
            results_df["STATUS"] == "PASS"
        ).sum()
    )

    failed = int(
        (
            results_df["STATUS"] == "FAIL"
        ).sum()
    )

    critical = int(
        (
            results_df["SEVERITY"] == "CRITICAL"
        ).sum()
    )

    high = int(
        (
            results_df["SEVERITY"] == "HIGH"
        ).sum()
    )

    medium = int(
        (
            results_df["SEVERITY"] == "MEDIUM"
        ).sum()
    )

    low = int(
        (
            results_df["SEVERITY"] == "LOW"
        ).sum()
    )

    logger.info("=" * 80)
    logger.info("PHASE 4 ASSESSMENT COMPLETE")
    logger.info("=" * 80)

    logger.info("Datasets expected       : %s", len(DATASETS))
    logger.info(
        "Datasets loaded         : %s",
        sum(df is not None for df in datasets.values()),
    )
    logger.info("Total quality tests     : %s", total_tests)
    logger.info("Passed tests            : %s", passed)
    logger.info("Failed tests            : %s", failed)
    logger.info("Critical issues         : %s", critical)
    logger.info("High issues             : %s", high)
    logger.info("Medium issues           : %s", medium)
    logger.info("Low issues              : %s", low)

    logger.info("-" * 80)
    logger.info("Output files:")
    logger.info("1. %s", results_file)
    logger.info("2. %s", summary_file)
    logger.info("3. %s", dimension_file)
    logger.info("4. %s", inventory_file)
    logger.info(
        "5. %s",
        OUTPUT_DIR / "data_quality_summary.json",
    )
    logger.info("6. %s", LOG_FILE)
    logger.info("=" * 80)

    logger.info(
        "RAW DATA MODIFIED: NO"
    )


if __name__ == "__main__":
    main()