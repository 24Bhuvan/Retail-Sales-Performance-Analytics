"""
Retail Sales Performance Analytics
Phase 5 — Data Cleaning Strategy

File:
    src/data/preprocess.py

Purpose:
    Reusable preprocessing utilities shared by the Phase 5 cleaning pipeline.

Responsibilities:
    - Data type normalization
    - Timestamp parsing
    - Numeric conversion
    - Text trimming and standardization
    - Categorical normalization
    - NULL representation normalization

Important:
    This module performs generic preprocessing only.
    Dataset-specific business rules belong in clean_data.py.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Optional

import pandas as pd


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Values that represent missing data in the source files.
# Do NOT include legitimate domain values such as "not_defined".
NULL_LIKE_VALUES = {
    "",
    " ",
    "  ",
    "null",
    "NULL",
    "None",
    "none",
    "NaN",
    "nan",
    "N/A",
    "n/a",
    "NA",
    "na",
}


# ---------------------------------------------------------------------------
# NULL NORMALIZATION
# ---------------------------------------------------------------------------

def normalize_nulls(
    df: pd.DataFrame,
    columns: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    Normalize common textual representations of missing values to pd.NA.

    Parameters
    ----------
    df:
        Input DataFrame.
    columns:
        Columns to process. If None, all object/string columns are processed.

    Returns
    -------
    pd.DataFrame
        DataFrame with standardized missing-value representations.

    Notes
    -----
    This function does not remove rows or impute values.
    It only standardizes representations of missing values.
    """

    result = df.copy()

    if columns is None:
        columns = result.select_dtypes(
            include=["object", "string"]
        ).columns

    for column in columns:
        if column not in result.columns:
            continue

        result[column] = result[column].replace(
            list(NULL_LIKE_VALUES),
            pd.NA,
        )

    return result


# ---------------------------------------------------------------------------
# TEXT NORMALIZATION
# ---------------------------------------------------------------------------

def normalize_text(
    df: pd.DataFrame,
    columns: Optional[Iterable[str]] = None,
    lowercase: bool = False,
) -> pd.DataFrame:
    """
    Trim whitespace and normalize repeated internal whitespace in text columns.

    Parameters
    ----------
    df:
        Input DataFrame.
    columns:
        Text columns to process. If None, all object/string columns are used.
    lowercase:
        Convert text to lowercase when True.

    Returns
    -------
    pd.DataFrame
        DataFrame with standardized text values.

    Notes
    -----
    This function does not perform business-specific category mapping.
    """

    result = df.copy()

    if columns is None:
        columns = result.select_dtypes(
            include=["object", "string"]
        ).columns

    for column in columns:
        if column not in result.columns:
            continue

        series = result[column].astype("string")

        # Remove leading/trailing whitespace.
        series = series.str.strip()

        # Replace repeated whitespace with a single space.
        series = series.str.replace(
            r"\s+",
            " ",
            regex=True,
        )

        if lowercase:
            series = series.str.lower()

        result[column] = series

    return result


# ---------------------------------------------------------------------------
# CATEGORICAL NORMALIZATION
# ---------------------------------------------------------------------------

def normalize_categories(
    df: pd.DataFrame,
    columns: Iterable[str],
    lowercase: bool = True,
) -> pd.DataFrame:
    """
    Normalize categorical columns.

    Operations:
        1. Convert to pandas StringDtype.
        2. Strip leading/trailing whitespace.
        3. Collapse repeated whitespace.
        4. Optionally convert to lowercase.

    Parameters
    ----------
    df:
        Input DataFrame.
    columns:
        Categorical columns to normalize.
    lowercase:
        Convert categorical values to lowercase.

    Returns
    -------
    pd.DataFrame
        DataFrame with normalized categorical values.

    Notes
    -----
    This does not translate Portuguese categories into English.
    Category translation is a separate Phase 5 operation.
    """

    return normalize_text(
        df=df,
        columns=columns,
        lowercase=lowercase,
    )


# ---------------------------------------------------------------------------
# TIMESTAMP PARSING
# ---------------------------------------------------------------------------

def parse_timestamps(
    df: pd.DataFrame,
    columns: Iterable[str],
    errors: str = "coerce",
) -> pd.DataFrame:
    """
    Convert specified columns to pandas datetime values.

    Parameters
    ----------
    df:
        Input DataFrame.
    columns:
        Timestamp columns to convert.
    errors:
        pandas.to_datetime error behavior.
        Recommended value: "coerce".

    Returns
    -------
    pd.DataFrame
        DataFrame with parsed datetime columns.

    Notes
    -----
    Invalid timestamp strings become NaT when errors="coerce".
    This function does not perform chronology corrections.
    """

    result = df.copy()

    for column in columns:
        if column not in result.columns:
            continue

        result[column] = pd.to_datetime(
            result[column],
            errors=errors,
        )

    return result


# ---------------------------------------------------------------------------
# NUMERIC CONVERSION
# ---------------------------------------------------------------------------

def convert_numeric(
    df: pd.DataFrame,
    columns: Iterable[str],
    errors: str = "coerce",
) -> pd.DataFrame:
    """
    Convert specified columns to numeric values.

    Parameters
    ----------
    df:
        Input DataFrame.
    columns:
        Numeric columns to convert.
    errors:
        pandas.to_numeric error behavior.
        Recommended value: "coerce".

    Returns
    -------
    pd.DataFrame
        DataFrame with numeric columns.

    Notes
    -----
    Invalid numeric strings become NaN when errors="coerce".
    This function does not decide whether those values should be
    imputed, removed, or retained.
    """

    result = df.copy()

    for column in columns:
        if column not in result.columns:
            continue

        result[column] = pd.to_numeric(
            result[column],
            errors=errors,
        )

    return result


# ---------------------------------------------------------------------------
# INTEGER CONVERSION
# ---------------------------------------------------------------------------

def convert_integer(
    df: pd.DataFrame,
    columns: Iterable[str],
) -> pd.DataFrame:
    """
    Convert specified columns to nullable pandas integer type.

    Nullable Int64 is used so legitimate missing values can remain
    missing without forcing floating-point representation.
    """

    result = df.copy()

    for column in columns:
        if column not in result.columns:
            continue

        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        ).astype("Int64")

    return result


# ---------------------------------------------------------------------------
# DATA TYPE NORMALIZATION
# ---------------------------------------------------------------------------

def normalize_dtypes(
    df: pd.DataFrame,
    datetime_columns: Optional[Iterable[str]] = None,
    numeric_columns: Optional[Iterable[str]] = None,
    integer_columns: Optional[Iterable[str]] = None,
    string_columns: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    Apply standardized data types to selected columns.

    Parameters
    ----------
    df:
        Input DataFrame.
    datetime_columns:
        Columns that should be datetime.
    numeric_columns:
        Columns that should be numeric.
    integer_columns:
        Columns that should use nullable Int64.
    string_columns:
        Columns that should use pandas StringDtype.

    Returns
    -------
    pd.DataFrame
        DataFrame with normalized data types.
    """

    result = df.copy()

    if datetime_columns:
        result = parse_timestamps(
            result,
            datetime_columns,
        )

    if numeric_columns:
        result = convert_numeric(
            result,
            numeric_columns,
        )

    if integer_columns:
        result = convert_integer(
            result,
            integer_columns,
        )

    if string_columns:
        for column in string_columns:
            if column not in result.columns:
                continue

            result[column] = result[column].astype("string")

    return result


# ---------------------------------------------------------------------------
# COMBINED GENERIC PREPROCESSING
# ---------------------------------------------------------------------------

def preprocess_dataframe(
    df: pd.DataFrame,
    *,
    datetime_columns: Optional[Iterable[str]] = None,
    numeric_columns: Optional[Iterable[str]] = None,
    integer_columns: Optional[Iterable[str]] = None,
    string_columns: Optional[Iterable[str]] = None,
    categorical_columns: Optional[Iterable[str]] = None,
    lowercase_categories: bool = True,
    normalize_all_text: bool = True,
) -> pd.DataFrame:
    """
    Apply the generic preprocessing sequence to a DataFrame.

    Processing order:
        1. Normalize NULL representations
        2. Normalize data types
        3. Normalize text
        4. Normalize categorical values

    Dataset-specific cleaning rules must be implemented separately.
    """

    result = df.copy()

    # 1. Standardize NULL representations.
    result = normalize_nulls(result)

    # 2. Normalize data types.
    result = normalize_dtypes(
        result,
        datetime_columns=datetime_columns,
        numeric_columns=numeric_columns,
        integer_columns=integer_columns,
        string_columns=string_columns,
    )

    # 3. Standardize text.
    if normalize_all_text:
        result = normalize_text(result)

    # 4. Standardize categorical fields.
    if categorical_columns:
        result = normalize_categories(
            result,
            categorical_columns,
            lowercase=lowercase_categories,
        )

    return result


# ---------------------------------------------------------------------------
# DATASET-SPECIFIC COLUMN DEFINITIONS
# ---------------------------------------------------------------------------

CUSTOMERS_DATETIME_COLUMNS: list[str] = []

CUSTOMERS_NUMERIC_COLUMNS = [
    "customer_zip_code_prefix",
]

CUSTOMERS_STRING_COLUMNS = [
    "customer_id",
    "customer_unique_id",
    "customer_city",
    "customer_state",
]

CUSTOMERS_CATEGORICAL_COLUMNS = [
    "customer_city",
    "customer_state",
]


ORDERS_DATETIME_COLUMNS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

ORDERS_NUMERIC_COLUMNS: list[str] = []

ORDERS_STRING_COLUMNS = [
    "order_id",
    "customer_id",
    "order_status",
]

ORDERS_CATEGORICAL_COLUMNS = [
    "order_status",
]


ORDER_ITEMS_DATETIME_COLUMNS = [
    "shipping_limit_date",
]

ORDER_ITEMS_NUMERIC_COLUMNS = [
    "order_item_id",
    "price",
    "freight_value",
]

ORDER_ITEMS_STRING_COLUMNS = [
    "order_id",
    "product_id",
    "seller_id",
]

ORDER_ITEMS_CATEGORICAL_COLUMNS: list[str] = []


PAYMENTS_DATETIME_COLUMNS: list[str] = []

PAYMENTS_NUMERIC_COLUMNS = [
    "payment_sequential",
    "payment_installments",
    "payment_value",
]

PAYMENTS_STRING_COLUMNS = [
    "order_id",
    "payment_type",
]

PAYMENTS_CATEGORICAL_COLUMNS = [
    "payment_type",
]


REVIEWS_DATETIME_COLUMNS = [
    "review_creation_date",
    "review_answer_timestamp",
]

REVIEWS_NUMERIC_COLUMNS = [
    "review_score",
]

REVIEWS_STRING_COLUMNS = [
    "review_id",
    "order_id",
    "review_comment_title",
    "review_comment_message",
]

REVIEWS_CATEGORICAL_COLUMNS: list[str] = []


PRODUCTS_DATETIME_COLUMNS: list[str] = []

PRODUCTS_NUMERIC_COLUMNS = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
]

PRODUCTS_STRING_COLUMNS = [
    "product_id",
    "product_category_name",
]

PRODUCTS_CATEGORICAL_COLUMNS = [
    "product_category_name",
]


SELLERS_DATETIME_COLUMNS: list[str] = []

SELLERS_NUMERIC_COLUMNS = [
    "seller_zip_code_prefix",
]

SELLERS_STRING_COLUMNS = [
    "seller_id",
    "seller_city",
    "seller_state",
]

SELLERS_CATEGORICAL_COLUMNS = [
    "seller_city",
    "seller_state",
]


CATEGORY_TRANSLATION_DATETIME_COLUMNS: list[str] = []

CATEGORY_TRANSLATION_NUMERIC_COLUMNS: list[str] = []

CATEGORY_TRANSLATION_STRING_COLUMNS = [
    "product_category_name",
    "product_category_name_english",
]

CATEGORY_TRANSLATION_CATEGORICAL_COLUMNS = [
    "product_category_name",
    "product_category_name_english",
]


GEOLOCATION_DATETIME_COLUMNS: list[str] = []

GEOLOCATION_NUMERIC_COLUMNS = [
    "geolocation_zip_code_prefix",
    "geolocation_lat",
    "geolocation_lng",
]

GEOLOCATION_STRING_COLUMNS = [
    "geolocation_city",
    "geolocation_state",
]

GEOLOCATION_CATEGORICAL_COLUMNS = [
    "geolocation_city",
    "geolocation_state",
]


# ---------------------------------------------------------------------------
# DATASET PREPROCESSING DISPATCHER
# ---------------------------------------------------------------------------

DATASET_PREPROCESSING_CONFIG: Mapping[str, dict] = {
    "customers": {
        "datetime_columns": CUSTOMERS_DATETIME_COLUMNS,
        "numeric_columns": CUSTOMERS_NUMERIC_COLUMNS,
        "integer_columns": CUSTOMERS_NUMERIC_COLUMNS,
        "string_columns": CUSTOMERS_STRING_COLUMNS,
        "categorical_columns": CUSTOMERS_CATEGORICAL_COLUMNS,
    },
    "orders": {
        "datetime_columns": ORDERS_DATETIME_COLUMNS,
        "numeric_columns": ORDERS_NUMERIC_COLUMNS,
        "integer_columns": [],
        "string_columns": ORDERS_STRING_COLUMNS,
        "categorical_columns": ORDERS_CATEGORICAL_COLUMNS,
    },
    "order_items": {
        "datetime_columns": ORDER_ITEMS_DATETIME_COLUMNS,
        "numeric_columns": ORDER_ITEMS_NUMERIC_COLUMNS,
        "integer_columns": ["order_item_id"],
        "string_columns": ORDER_ITEMS_STRING_COLUMNS,
        "categorical_columns": ORDER_ITEMS_CATEGORICAL_COLUMNS,
    },
    "payments": {
        "datetime_columns": PAYMENTS_DATETIME_COLUMNS,
        "numeric_columns": PAYMENTS_NUMERIC_COLUMNS,
        "integer_columns": [
            "payment_sequential",
            "payment_installments",
        ],
        "string_columns": PAYMENTS_STRING_COLUMNS,
        "categorical_columns": PAYMENTS_CATEGORICAL_COLUMNS,
    },
    "reviews": {
        "datetime_columns": REVIEWS_DATETIME_COLUMNS,
        "numeric_columns": REVIEWS_NUMERIC_COLUMNS,
        "integer_columns": ["review_score"],
        "string_columns": REVIEWS_STRING_COLUMNS,
        "categorical_columns": REVIEWS_CATEGORICAL_COLUMNS,
    },
    "products": {
        "datetime_columns": PRODUCTS_DATETIME_COLUMNS,
        "numeric_columns": PRODUCTS_NUMERIC_COLUMNS,
        "integer_columns": PRODUCTS_NUMERIC_COLUMNS,
        "string_columns": PRODUCTS_STRING_COLUMNS,
        "categorical_columns": PRODUCTS_CATEGORICAL_COLUMNS,
    },
    "sellers": {
        "datetime_columns": SELLERS_DATETIME_COLUMNS,
        "numeric_columns": SELLERS_NUMERIC_COLUMNS,
        "integer_columns": SELLERS_NUMERIC_COLUMNS,
        "string_columns": SELLERS_STRING_COLUMNS,
        "categorical_columns": SELLERS_CATEGORICAL_COLUMNS,
    },
    "category_translation": {
        "datetime_columns": CATEGORY_TRANSLATION_DATETIME_COLUMNS,
        "numeric_columns": CATEGORY_TRANSLATION_NUMERIC_COLUMNS,
        "integer_columns": [],
        "string_columns": CATEGORY_TRANSLATION_STRING_COLUMNS,
        "categorical_columns": CATEGORY_TRANSLATION_CATEGORICAL_COLUMNS,
    },
    "geolocation": {
        "datetime_columns": GEOLOCATION_DATETIME_COLUMNS,
        "numeric_columns": GEOLOCATION_NUMERIC_COLUMNS,
        "integer_columns": ["geolocation_zip_code_prefix"],
        "string_columns": GEOLOCATION_STRING_COLUMNS,
        "categorical_columns": GEOLOCATION_CATEGORICAL_COLUMNS,
    },
}


def preprocess_dataset(
    df: pd.DataFrame,
    dataset_name: str,
) -> pd.DataFrame:
    """
    Preprocess one of the nine Olist datasets using its configured schema.

    Parameters
    ----------
    df:
        Input dataset.
    dataset_name:
        Dataset identifier used in DATASET_PREPROCESSING_CONFIG.

    Returns
    -------
    pd.DataFrame
        Preprocessed DataFrame.

    Raises
    ------
    ValueError
        If dataset_name is not configured.
    """

    if dataset_name not in DATASET_PREPROCESSING_CONFIG:
        valid_names = ", ".join(
            sorted(DATASET_PREPROCESSING_CONFIG.keys())
        )

        raise ValueError(
            f"Unknown dataset '{dataset_name}'. "
            f"Expected one of: {valid_names}"
        )

    config = DATASET_PREPROCESSING_CONFIG[dataset_name]

    return preprocess_dataframe(
        df,
        **config,
    )


# ---------------------------------------------------------------------------
# VALIDATION HELPERS
# ---------------------------------------------------------------------------

def get_dtype_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a compact data-type summary for validation.
    """

    return pd.DataFrame(
        {
            "column": df.columns,
            "dtype": [
                str(dtype)
                for dtype in df.dtypes
            ],
            "null_count": [
                int(df[column].isna().sum())
                for column in df.columns
            ],
        }
    )


def get_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return missing-value counts and percentages.
    """

    total_rows = len(df)

    summary = pd.DataFrame(
        {
            "column": df.columns,
            "missing_count": [
                int(df[column].isna().sum())
                for column in df.columns
            ],
        }
    )

    if total_rows > 0:
        summary["missing_rate_pct"] = (
            summary["missing_count"] / total_rows * 100
        ).round(4)
    else:
        summary["missing_rate_pct"] = 0.0

    return summary


def get_duplicate_summary(
    df: pd.DataFrame,
) -> dict:
    """
    Return generic duplicate statistics.

    This function does not remove duplicates.
    Dataset-specific duplicate rules belong in clean_data.py.
    """

    duplicate_mask = df.duplicated(keep=False)

    return {
        "total_rows": int(len(df)),
        "duplicate_rows": int(duplicate_mask.sum()),
        "duplicate_rows_excluding_first": int(
            df.duplicated(keep="first").sum()
        ),
    }


# ---------------------------------------------------------------------------
# MODULE EXPORTS
# ---------------------------------------------------------------------------

__all__ = [
    "normalize_nulls",
    "normalize_text",
    "normalize_categories",
    "parse_timestamps",
    "convert_numeric",
    "convert_integer",
    "normalize_dtypes",
    "preprocess_dataframe",
    "preprocess_dataset",
    "get_dtype_summary",
    "get_missing_summary",
    "get_duplicate_summary",
    "DATASET_PREPROCESSING_CONFIG",
]