from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


# =============================================================================
# PROJECT PATHS
# =============================================================================
def setup_paths() -> dict[str, Path]:
    """Return project-relative paths for processed data and feature outputs."""
    project_root = Path(__file__).resolve().parents[2]
    processed_dir = project_root / "data" / "processed"
    feature_dir = processed_dir / "features"
    report_dir = project_root / "reports" / "feature_engineering"

    return {
        "project_root": project_root,
        "processed_dir": processed_dir,
        "feature_dir": feature_dir,
        "report_dir": report_dir,
        "summary_file": report_dir / "feature_engineering_summary.json",
        "validation_file": report_dir / "feature_validation.csv",
        "execution_log": report_dir / "feature_engineering_execution.log",
    }


# =============================================================================
# LOGGING
# =============================================================================
def setup_logging() -> tuple[logging.Logger, dict[str, Path]]:
    """Configure logging to both console and the feature engineering execution log."""
    paths = setup_paths()
    paths["feature_dir"].mkdir(parents=True, exist_ok=True)
    paths["report_dir"].mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("phase12_feature_engineering")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger, paths

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(
        paths["execution_log"],
        mode="w",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger, paths


# =============================================================================
# DATASET LOADING AND VALIDATION
# =============================================================================
def load_datasets(logger: logging.Logger, paths: dict[str, Path]) -> dict[str, pd.DataFrame]:
    """Load the processed source datasets required for the Phase 12 feature pipeline."""
    dataset_files = {
        "orders_processed": "orders_processed.csv",
        "order_items_processed": "order_items_processed.csv",
        "customers_processed": "customers_processed.csv",
        "products_processed": "products_processed.csv",
        "payments_processed": "payments_processed.csv",
        "reviews_processed": "reviews_processed.csv",
        "sellers_processed": "sellers_processed.csv",
        "geography_processed": "geography_processed.csv",
    }

    loaded: dict[str, pd.DataFrame] = {}
    for dataset_name, filename in dataset_files.items():
        file_path = paths["processed_dir"] / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Required source dataset not found: {file_path}")

        df = pd.read_csv(file_path, low_memory=False)
        loaded[dataset_name] = df

        logger.info("Dataset loaded: %s | rows=%s | cols=%s", dataset_name, len(df), list(df.columns))

    return loaded


def validate_source_columns(datasets: dict[str, pd.DataFrame], logger: logging.Logger) -> None:
    """Verify that all critical source columns exist before feature calculations begin."""
    required_columns = {
        "orders_processed": [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
            "customer_unique_id",
        ],
        "order_items_processed": [
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "price",
            "freight_value",
        ],
        "customers_processed": [
            "customer_id",
            "customer_unique_id",
        ],
        "products_processed": [
            "product_id",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ],
        "payments_processed": [
            "order_id",
            "payment_sequential",
            "payment_installments",
            "payment_value",
        ],
        "reviews_processed": [
            "order_id",
            "review_score",
        ],
        "sellers_processed": [
            "seller_id",
        ],
        "geography_processed": [
            "geolocation_zip_code_prefix",
        ],
    }

    for dataset_name, required in required_columns.items():
        df = datasets[dataset_name]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"{dataset_name} is missing required columns: {missing}")
        logger.info("Validated required columns for %s: OK", dataset_name)

    key_checks = {
        "orders_processed": ["order_id"],
        "order_items_processed": ["order_id", "order_item_id"],
        "customers_processed": ["customer_unique_id"],
        "products_processed": ["product_id"],
        "payments_processed": ["order_id", "payment_sequential"],
        "reviews_processed": ["order_id"],
    }

    for dataset_name, key_fields in key_checks.items():
        df = datasets[dataset_name]
        duplicates = df.duplicated(subset=key_fields).sum()
        logger.info("Duplicate check for %s on %s: %s", dataset_name, key_fields, duplicates)
        if duplicates > 0:
            logger.warning("Duplicate key combinations detected in %s: %s", dataset_name, duplicates)

    logger.info("Source validation complete.")


def convert_date_columns(datasets: dict[str, pd.DataFrame], logger: logging.Logger) -> dict[str, pd.DataFrame]:
    """Convert the critical temporal columns to pandas datetime and log date coverage."""
    datetime_columns = {
        "orders_processed": [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
        "order_items_processed": [
            "shipping_limit_date",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
        "payments_processed": [
            "order_purchase_timestamp",
        ],
        "reviews_processed": [
            "review_creation_date",
            "review_answer_timestamp",
            "order_purchase_timestamp",
        ],
    }

    for dataset_name, columns in datetime_columns.items():
        if dataset_name not in datasets:
            continue
        df = datasets[dataset_name]
        for column in columns:
            if column in df.columns:
                df[column] = pd.to_datetime(df[column], errors="coerce")
                logger.info("Converted %s.%s to datetime", dataset_name, column)

    return datasets


# =============================================================================
# FEATURE SECTION 1: ORDER ITEM FEATURES
# =============================================================================
def create_order_item_features(
    datasets: dict[str, pd.DataFrame],
    logger: logging.Logger,
) -> pd.DataFrame:
    """Create one row per order item with revenue, weight, and product dimension features."""
    order_items = datasets["order_items_processed"].copy()
    products = datasets["products_processed"].copy()

    item_features = order_items.copy()
    for dimension_col in ["product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]:
        if dimension_col not in item_features.columns:
            product_lookup = products[["product_id", dimension_col]].drop_duplicates(subset=["product_id"])
            item_features = item_features.merge(
                product_lookup,
                on="product_id",
                how="left",
                suffixes=("", "_product"),
            )
            if f"{dimension_col}_product" in item_features.columns:
                item_features[dimension_col] = item_features[dimension_col].combine_first(
                    item_features[f"{dimension_col}_product"]
                )
                item_features = item_features.drop(columns=[f"{dimension_col}_product"])

    item_features["item_revenue"] = item_features["price"]
    item_features["freight_to_price_ratio"] = np.where(
        item_features["price"].notna() & (item_features["price"] != 0),
        item_features["freight_value"] / item_features["price"],
        np.nan,
    )
    item_features["total_item_value"] = item_features["price"] + item_features["freight_value"]
    item_features["product_volume_cm3"] = (
        item_features["product_length_cm"]
        * item_features["product_height_cm"]
        * item_features["product_width_cm"]
    )

    item_features["product_weight_category"] = pd.Series(np.nan, index=item_features.index, dtype="object")
    weight_mask = item_features["product_weight_g"].notna()
    item_features.loc[weight_mask & (item_features["product_weight_g"] < 1000), "product_weight_category"] = "Light"
    item_features.loc[weight_mask & (item_features["product_weight_g"] >= 1000) & (item_features["product_weight_g"] < 5000), "product_weight_category"] = "Medium"
    item_features.loc[weight_mask & (item_features["product_weight_g"] >= 5000) & (item_features["product_weight_g"] < 20000), "product_weight_category"] = "Heavy"
    item_features.loc[weight_mask & (item_features["product_weight_g"] >= 20000), "product_weight_category"] = "Very Heavy"

    volume_values = item_features["product_volume_cm3"].dropna()
    if not volume_values.empty:
        q25 = float(volume_values.quantile(0.25))
        q50 = float(volume_values.quantile(0.50))
        q75 = float(volume_values.quantile(0.75))
        logger.info(
            "Product volume quartile thresholds: q25=%s | q50=%s | q75=%s",
            q25,
            q50,
            q75,
        )

        item_features["product_dimension_category"] = pd.Series(
            [np.nan] * len(item_features),
            index=item_features.index,
            dtype="object",
        )
        volume_mask = item_features["product_volume_cm3"].notna()
        item_features.loc[volume_mask & (item_features["product_volume_cm3"] <= q25), "product_dimension_category"] = "Small"
        item_features.loc[
            volume_mask
            & (item_features["product_volume_cm3"] > q25)
            & (item_features["product_volume_cm3"] <= q50),
            "product_dimension_category",
        ] = "Medium"
        item_features.loc[
            volume_mask
            & (item_features["product_volume_cm3"] > q50)
            & (item_features["product_volume_cm3"] <= q75),
            "product_dimension_category",
        ] = "Large"
        item_features.loc[
            volume_mask
            & (item_features["product_volume_cm3"] > q75),
            "product_dimension_category",
        ] = "Extra Large"
    else:
        item_features["product_dimension_category"] = np.nan
        logger.warning("No valid product volume values were available for dimension quartile classification.")

    output_columns = [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "item_revenue",
        "freight_value",
        "freight_to_price_ratio",
        "total_item_value",
        "product_weight_g",
        "product_volume_cm3",
        "product_weight_category",
        "product_dimension_category",
    ]

    item_features = item_features[output_columns]
    logger.info("Order item features created: rows=%s", len(item_features))
    return item_features


# =============================================================================
# FEATURE SECTION 2: ORDER FEATURES
# =============================================================================
def create_order_features(
    datasets: dict[str, pd.DataFrame],
    order_item_features: pd.DataFrame,
    logger: logging.Logger,
) -> pd.DataFrame:
    """Create order-grain features including sales, delivery, payments, and review signals."""
    orders = datasets["orders_processed"].copy()
    customers = datasets["customers_processed"].copy()
    payments = datasets["payments_processed"].copy()
    reviews = datasets["reviews_processed"].copy()

    # Aggregate item-level revenue to order grain.
    order_revenue_summary = (
        order_item_features.groupby("order_id", as_index=False)
        .agg(
            order_revenue=("item_revenue", "sum"),
            total_order_value=("total_item_value", "sum"),
            items_per_order=("order_item_id", "count"),
        )
    )

    customer_lookup = customers[["customer_id", "customer_unique_id"]].drop_duplicates(subset=["customer_id"])
    orders = orders.merge(
        customer_lookup,
        on="customer_id",
        how="left",
        suffixes=("", "_customer_lookup"),
    )
    if "customer_unique_id_customer_lookup" in orders.columns:
        orders["customer_unique_id"] = orders["customer_unique_id"].combine_first(
            orders["customer_unique_id_customer_lookup"]
        )
        orders = orders.drop(columns=["customer_unique_id_customer_lookup"])
    orders = orders.merge(order_revenue_summary, on="order_id", how="left")

    # Time features based on the purchase timestamp. Where the processed source already
    # contains order_year / order_month / order_quarter, reuse them to avoid duplication.
    purchase_ts = pd.to_datetime(orders["order_purchase_timestamp"], errors="coerce")
    orders["order_date"] = purchase_ts.dt.date
    orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")

    orders["order_year"] = pd.to_numeric(orders["order_year"], errors="coerce")
    orders["order_month_number"] = pd.to_numeric(orders["order_month"], errors="coerce")
    orders["order_month_number"] = orders["order_month_number"].fillna(purchase_ts.dt.month)
    orders["order_year"] = orders["order_year"].fillna(purchase_ts.dt.year)

    orders["order_quarter"] = pd.to_numeric(orders["order_quarter"], errors="coerce")
    orders["order_quarter"] = orders["order_quarter"].fillna((purchase_ts.dt.month - 1) // 3 + 1)

    orders["order_month_name"] = orders["order_month_number"].map({
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    })
    orders["order_weekday"] = purchase_ts.dt.day_name()
    orders["is_weekend"] = purchase_ts.dt.dayofweek.ge(5).astype(int)
    orders["year_month"] = purchase_ts.dt.to_period("M").astype(str)

    season_map = {
        12: "Summer",
        1: "Summer",
        2: "Summer",
        3: "Autumn",
        4: "Autumn",
        5: "Autumn",
        6: "Winter",
        7: "Winter",
        8: "Winter",
        9: "Spring",
        10: "Spring",
        11: "Spring",
    }
    orders["season"] = orders["order_month_number"].map(season_map)
    orders["holiday_season_flag"] = orders["order_month_number"].isin([11, 12]).astype(int)
    orders["quarter_seasonality"] = orders["order_quarter"].map({1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"})

    # Delivery duration logic: if actual customer delivery date is missing or order was not delivered,
    # keep the duration metrics and flags NULL/NaN rather than incorrectly classifying the order.
    order_purchase_ts = pd.to_datetime(orders["order_purchase_timestamp"], errors="coerce")
    delivery_carrier_ts = pd.to_datetime(orders["order_delivered_carrier_date"], errors="coerce")
    delivery_customer_ts = pd.to_datetime(orders["order_delivered_customer_date"], errors="coerce")
    estimated_delivery_ts = pd.to_datetime(orders["order_estimated_delivery_date"], errors="coerce")

    orders["processing_time_days"] = np.where(
        order_purchase_ts.notna() & delivery_carrier_ts.notna(),
        (delivery_carrier_ts - order_purchase_ts).dt.total_seconds() / 86400,
        np.nan,
    )
    orders["delivery_time_days"] = np.where(
        order_purchase_ts.notna() & delivery_customer_ts.notna(),
        (delivery_customer_ts - order_purchase_ts).dt.total_seconds() / 86400,
        np.nan,
    )
    orders["estimated_delivery_time_days"] = np.where(
        order_purchase_ts.notna() & estimated_delivery_ts.notna(),
        (estimated_delivery_ts - order_purchase_ts).dt.total_seconds() / 86400,
        np.nan,
    )
    orders["delivery_difference_days"] = np.where(
        delivery_customer_ts.notna() & estimated_delivery_ts.notna(),
        (delivery_customer_ts - estimated_delivery_ts).dt.total_seconds() / 86400,
        np.nan,
    )

    delivered_mask = orders["order_status"].eq("delivered") & orders["order_delivered_customer_date"].notna()
    orders["late_delivery_flag"] = np.where(
        delivered_mask,
        (orders["delivery_difference_days"] > 0).astype(float),
        np.nan,
    )
    orders["on_time_delivery_flag"] = np.where(
        delivered_mask,
        (orders["delivery_difference_days"] <= 0).astype(float),
        np.nan,
    )
    orders["delivery_status"] = np.select(
        [
            orders["order_status"].eq("delivered")
            & orders["order_delivered_customer_date"].notna()
            & orders["order_estimated_delivery_date"].notna()
            & (delivery_customer_ts > estimated_delivery_ts),
            orders["order_status"].eq("delivered")
            & orders["order_delivered_customer_date"].notna()
            & orders["order_estimated_delivery_date"].notna()
            & (delivery_customer_ts <= estimated_delivery_ts),
            orders["order_status"].eq("delivered")
            & (orders["order_delivered_customer_date"].isna() | orders["order_estimated_delivery_date"].isna()),
        ],
        ["Late", "On Time", "Unavailable"],
        default="Unavailable",
    )

    # Payment aggregation to one row per order_id.
    payment_agg = (
        payments.groupby("order_id", as_index=False)
        .agg(
            number_payment_installments=("payment_installments", "max"),
            payment_value_per_order=("payment_value", "sum"),
        )
    )
    payment_counts = (
        payments.groupby("order_id")["payment_sequential"]
        .count()
        .reset_index(name="payment_record_count")
    )
    payment_agg = payment_agg.merge(payment_counts, on="order_id", how="left")
    payment_agg["multi_payment_flag"] = (payment_agg["payment_record_count"] > 1).astype(int)
    payment_agg = payment_agg[["order_id", "number_payment_installments", "multi_payment_flag", "payment_value_per_order"]]
    orders = orders.merge(payment_agg, on="order_id", how="left")

    # Review aggregation: use the maximum available score per order_id as a deterministic rule.
    review_agg = (
        reviews.groupby("order_id", as_index=False)["review_score"]
        .max()
        .rename(columns={"review_score": "review_score"})
    )
    category_values = pd.Series([np.nan] * len(review_agg), index=review_agg.index, dtype="object")
    mask_low = review_agg["review_score"].notna() & review_agg["review_score"].le(2)
    mask_neutral = review_agg["review_score"].notna() & review_agg["review_score"].eq(3)
    mask_high = review_agg["review_score"].notna() & review_agg["review_score"].ge(4)
    category_values.loc[mask_low] = "Low"
    category_values.loc[mask_neutral] = "Neutral"
    category_values.loc[mask_high] = "High"
    review_agg["review_score_category"] = category_values
    review_agg["low_review_flag"] = np.where(
        review_agg["review_score"].isna(),
        np.nan,
        (review_agg["review_score"] <= 2).astype(float),
    )
    review_agg["high_review_flag"] = np.where(
        review_agg["review_score"].isna(),
        np.nan,
        (review_agg["review_score"] >= 4).astype(float),
    )
    orders = orders.merge(review_agg, on="order_id", how="left")

    # Final order-grain output columns.
    final_columns = [
        "order_id",
        "customer_id",
        "customer_unique_id",
        "order_status",
        "order_date",
        "order_year",
        "order_quarter",
        "order_month_number",
        "order_month_name",
        "order_weekday",
        "is_weekend",
        "year_month",
        "season",
        "holiday_season_flag",
        "quarter_seasonality",
        "order_revenue",
        "total_order_value",
        "items_per_order",
        "processing_time_days",
        "delivery_time_days",
        "estimated_delivery_time_days",
        "delivery_difference_days",
        "late_delivery_flag",
        "on_time_delivery_flag",
        "delivery_status",
        "number_payment_installments",
        "multi_payment_flag",
        "payment_value_per_order",
        "review_score",
        "review_score_category",
        "low_review_flag",
        "high_review_flag",
    ]

    orders = orders[final_columns]
    logger.info("Order features created: rows=%s | unique_order_ids=%s", len(orders), orders["order_id"].nunique())
    return orders


# =============================================================================
# FEATURE SECTION 3: CUSTOMER FEATURES
# =============================================================================
def create_customer_features(orders_features: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    """Create customer features at one row per customer_unique_id."""
    customer_features = (
        orders_features.groupby("customer_unique_id", dropna=False, as_index=False)
        .agg(
            customer_order_count=("order_id", "nunique"),
            customer_lifetime_revenue=("order_revenue", "sum"),
        )
    )
    customer_features["repeat_customer_flag"] = (customer_features["customer_order_count"] > 1).astype(int)
    customer_features["customer_segment"] = np.where(
        customer_features["customer_order_count"].gt(1),
        "Repeat",
        "One-time",
    )
    customer_features["average_customer_order_value"] = np.where(
        customer_features["customer_order_count"].notna() & (customer_features["customer_order_count"] > 0),
        customer_features["customer_lifetime_revenue"] / customer_features["customer_order_count"],
        np.nan,
    )

    customer_features = customer_features[
        [
            "customer_unique_id",
            "customer_order_count",
            "repeat_customer_flag",
            "customer_segment",
            "customer_lifetime_revenue",
            "average_customer_order_value",
        ]
    ]
    logger.info("Customer features created: rows=%s | unique_customer_ids=%s", len(customer_features), customer_features["customer_unique_id"].nunique())
    return customer_features


# =============================================================================
# FEATURE SECTION 4: MONTHLY FEATURES
# =============================================================================
def create_monthly_features(orders_features: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    """Create monthly revenue and trend metrics from the order-level feature set."""
    monthly = orders_features[["order_date", "order_id", "order_revenue"]].copy()
    monthly["year_month"] = pd.PeriodIndex(monthly["order_date"], freq="M").astype(str)

    monthly_revenue = (
        monthly.groupby("year_month", as_index=False)["order_revenue"]
        .sum()
        .rename(columns={"order_revenue": "monthly_revenue"})
    )
    monthly_orders = (
        monthly.groupby("year_month", as_index=False)["order_id"]
        .nunique()
        .rename(columns={"order_id": "monthly_order_count"})
    )

    monthly_features = monthly_revenue.merge(monthly_orders, on="year_month", how="left")
    monthly_features["sort_key"] = pd.PeriodIndex(monthly_features["year_month"], freq="M")
    monthly_features = monthly_features.sort_values("sort_key").reset_index(drop=True)

    monthly_features["3_month_rolling_revenue"] = monthly_features["monthly_revenue"].rolling(window=3, min_periods=1).sum()
    monthly_features["3_month_rolling_order_count"] = monthly_features["monthly_order_count"].rolling(window=3, min_periods=1).sum()

    previous_month_revenue = monthly_features["monthly_revenue"].shift(1)
    monthly_features["monthly_revenue_growth"] = np.where(
        previous_month_revenue.notna() & (previous_month_revenue != 0),
        (monthly_features["monthly_revenue"] - previous_month_revenue) / previous_month_revenue,
        np.nan,
    )
    monthly_features["cumulative_revenue"] = monthly_features["monthly_revenue"].cumsum()

    monthly_features = monthly_features[
        [
            "year_month",
            "monthly_revenue",
            "monthly_order_count",
            "3_month_rolling_revenue",
            "3_month_rolling_order_count",
            "monthly_revenue_growth",
            "cumulative_revenue",
        ]
    ]
    logger.info("Monthly features created: rows=%s | first_month=%s | last_month=%s", len(monthly_features), monthly_features["year_month"].iloc[0], monthly_features["year_month"].iloc[-1])
    return monthly_features


# =============================================================================
# FEATURE VALIDATION
# =============================================================================
def validate_features(
    datasets: dict[str, pd.DataFrame],
    orders_features: pd.DataFrame,
    order_items_features: pd.DataFrame,
    customer_features: pd.DataFrame,
    monthly_features: pd.DataFrame,
    logger: logging.Logger,
) -> list[dict]:
    """Run logical validation checks and return a list of validation records."""
    validation_rows: list[dict] = []

    def add_check(dataset_name: str, check_name: str, expected_value: object, actual_value: object) -> None:
        status = "PASS" if str(expected_value) == str(actual_value) else "FAIL"
        validation_rows.append(
            {
                "dataset_name": dataset_name,
                "validation_check": check_name,
                "expected_value": expected_value,
                "actual_value": actual_value,
                "status": status,
            }
        )
        logger.info("Validation | %s | %s | expected=%s | actual=%s | status=%s", dataset_name, check_name, expected_value, actual_value, status)

    def add_null_check(
        dataset_name: str,
        column_name: str,
        expected_nulls: int = 0,
        *,
        validation_name: str | None = None,
        allowed_nulls: bool = False,
    ) -> None:
        df = {
            "orders_features": orders_features,
            "order_items_features": order_items_features,
            "customer_features": customer_features,
            "monthly_features": monthly_features,
        }[dataset_name]
        actual_nulls = int(df[column_name].isna().sum())
        check_name = validation_name or f"{column_name}_null_count"
        expected_value = "allowed" if allowed_nulls else expected_nulls
        status = "PASS" if (allowed_nulls or actual_nulls == expected_nulls) else "FAIL"
        validation_rows.append(
            {
                "dataset_name": dataset_name,
                "validation_check": check_name,
                "expected_value": expected_value,
                "actual_value": actual_nulls,
                "status": status,
            }
        )
        logger.info(
            "Validation | %s | %s | expected=%s | actual=%s | status=%s",
            dataset_name,
            check_name,
            expected_value,
            actual_nulls,
            status,
        )

    # orders_features validations
    add_check(
        "orders_features",
        "one_row_per_order_id",
        len(orders_features),
        orders_features["order_id"].nunique(),
    )
    add_check(
        "orders_features",
        "no_duplicate_order_id",
        0,
        int(orders_features["order_id"].duplicated().sum()),
    )
    source_order_revenue_total = float(order_items_features["item_revenue"].sum())
    add_check(
        "orders_features",
        "order_revenue_matches_order_items_total",
        round(source_order_revenue_total, 6),
        round(float(orders_features["order_revenue"].sum()), 6),
    )
    add_check(
        "orders_features",
        "items_per_order_matches_order_items_count",
        "aligned",
        "aligned" if orders_features["items_per_order"].equals(
            orders_features["order_id"].map(order_items_features.groupby("order_id")["order_item_id"].count())
        ) else "misaligned",
    )
    add_check(
        "orders_features",
        "items_per_order_non_negative",
        0,
        int((orders_features["items_per_order"] < 0).sum()),
    )
    add_check(
        "orders_features",
        "total_order_value_not_less_than_order_revenue",
        0,
        int((orders_features["total_order_value"].fillna(0) < orders_features["order_revenue"].fillna(0)).sum()),
    )
    add_null_check("orders_features", "order_id", 0, validation_name="no_null_order_id")
    add_null_check("orders_features", "customer_id", 0, validation_name="customer_id_null_count")
    add_null_check("orders_features", "customer_unique_id", 0, validation_name="customer_unique_id_null_count")
    add_null_check("orders_features", "order_status", 0, validation_name="order_status_null_count")
    add_null_check("orders_features", "order_date", 0, validation_name="order_date_null_count")
    add_null_check("orders_features", "delivery_status", 0, validation_name="delivery_status_null_count")
    add_null_check(
        "orders_features",
        "order_revenue",
        0,
        validation_name="order_revenue_null_count",
        allowed_nulls=True,
    )
    add_null_check(
        "orders_features",
        "total_order_value",
        0,
        validation_name="total_order_value_null_count",
        allowed_nulls=True,
    )
    add_null_check(
        "orders_features",
        "items_per_order",
        0,
        validation_name="items_per_order_null_count",
        allowed_nulls=True,
    )

    delivery_flag_mask = (
        orders_features["late_delivery_flag"].notna()
        | orders_features["on_time_delivery_flag"].notna()
    )
    delivered_flag_valid = True
    if delivery_flag_mask.any():
        delivery_df = orders_features.loc[delivery_flag_mask, ["delivery_difference_days", "late_delivery_flag", "on_time_delivery_flag"]].copy()
        later = delivery_df["delivery_difference_days"] > 0
        late_matches = delivery_df["late_delivery_flag"].fillna(0).astype(float).eq(later.astype(float))
        on_time_matches = delivery_df["on_time_delivery_flag"].fillna(0).astype(float).eq((~later).astype(float))
        delivered_flag_valid = bool(late_matches.all() and on_time_matches.all())
    add_check(
        "orders_features",
        "delivery_flags_logically_consistent",
        True,
        delivered_flag_valid,
    )

    # order_items_features validations
    add_check(
        "order_items_features",
        "same_row_count_as_source",
        len(datasets["order_items_processed"]),
        len(order_items_features),
    )
    add_check(
        "order_items_features",
        "no_duplicate_order_item_id_per_order",
        0,
        int(order_items_features.duplicated(subset=["order_id", "order_item_id"]).sum()),
    )
    add_null_check("order_items_features", "order_id", 0, validation_name="no_null_order_item_order_id")
    add_null_check("order_items_features", "order_item_id", 0, validation_name="no_null_order_item_id")
    add_null_check("order_items_features", "product_id", 0, validation_name="product_id_null_count")
    add_null_check("order_items_features", "seller_id", 0, validation_name="seller_id_null_count")
    add_null_check("order_items_features", "item_revenue", 0, validation_name="item_revenue_null_count")
    add_null_check("order_items_features", "freight_value", 0, validation_name="freight_value_null_count")
    add_null_check("order_items_features", "total_item_value", 0, validation_name="total_item_value_null_count")
    ratio_inf_count = int(np.isinf(order_items_features["freight_to_price_ratio"]).sum())
    add_check(
        "order_items_features",
        "no_infinite_freight_to_price_ratio",
        0,
        ratio_inf_count,
    )
    add_check(
        "order_items_features",
        "product_volume_calculation_valid",
        "nonnegative or NaN",
        "nonnegative or NaN" if (order_items_features["product_volume_cm3"].dropna() >= 0).all() else "invalid",
    )

    # customer_features validations
    add_check(
        "customer_features",
        "one_row_per_customer_unique_id",
        customer_features["customer_unique_id"].nunique(),
        len(customer_features),
    )
    add_check(
        "customer_features",
        "no_duplicate_customer_unique_id",
        0,
        int(customer_features["customer_unique_id"].duplicated().sum()),
    )
    add_check(
        "customer_features",
        "customer_totals_reconcile_with_orders",
        round(float(orders_features["order_revenue"].sum()), 6),
        round(float(customer_features["customer_lifetime_revenue"].sum()), 6),
    )
    user_repeat_ok = bool(
        customer_features["repeat_customer_flag"].equals(
            (customer_features["customer_order_count"] > 1).astype(int)
        )
    )
    add_check("customer_features", "repeat_flag_matches_order_count", True, user_repeat_ok)
    add_check(
        "customer_features",
        "customer_order_count_non_negative",
        0,
        int((customer_features["customer_order_count"] < 0).sum()),
    )
    add_null_check("customer_features", "customer_unique_id", 0, validation_name="customer_unique_id_null_count")
    add_null_check("customer_features", "customer_order_count", 0, validation_name="customer_order_count_null_count")
    add_null_check("customer_features", "customer_segment", 0, validation_name="customer_segment_null_count")
    add_null_check("customer_features", "customer_lifetime_revenue", 0, validation_name="customer_lifetime_revenue_null_count")
    add_null_check("customer_features", "average_customer_order_value", 0, validation_name="average_customer_order_value_null_count")
    avg_order_value_ok = bool(
        customer_features.loc[customer_features["customer_order_count"] > 0, "average_customer_order_value"]
        .equals(
            customer_features.loc[customer_features["customer_order_count"] > 0, "customer_lifetime_revenue"]
            / customer_features.loc[customer_features["customer_order_count"] > 0, "customer_order_count"]
        )
    )
    add_check(
        "customer_features",
        "average_customer_order_value_matches_revenue_divided_by_count",
        True,
        avg_order_value_ok,
    )

    # monthly_features validations
    add_check(
        "monthly_features",
        "one_row_per_year_month",
        monthly_features["year_month"].nunique(),
        len(monthly_features),
    )
    month_sort_ok = bool(pd.PeriodIndex(monthly_features["year_month"], freq="M").is_monotonic_increasing)
    add_check("monthly_features", "chronologically_sorted", True, month_sort_ok)
    add_check(
        "monthly_features",
        "monthly_revenue_reconciles_with_orders",
        round(float(orders_features["order_revenue"].sum()), 6),
        round(float(monthly_features["monthly_revenue"].sum()), 6),
    )
    add_check(
        "monthly_features",
        "cumulative_revenue_matches_total_revenue",
        round(float(monthly_features["monthly_revenue"].sum()), 6),
        round(float(monthly_features["cumulative_revenue"].iloc[-1]), 6),
    )
    add_check(
        "monthly_features",
        "monthly_order_count_non_negative",
        0,
        int((monthly_features["monthly_order_count"] < 0).sum()),
    )
    add_null_check("monthly_features", "year_month", 0, validation_name="year_month_null_count")
    add_null_check("monthly_features", "monthly_revenue", 0, validation_name="monthly_revenue_null_count")
    add_null_check("monthly_features", "monthly_order_count", 0, validation_name="monthly_order_count_null_count")
    add_null_check("monthly_features", "cumulative_revenue", 0, validation_name="cumulative_revenue_null_count")
    initial_growth_null_ok = int(monthly_features["monthly_revenue_growth"].isna().iloc[0]) if len(monthly_features) > 0 else 0
    add_check(
        "monthly_features",
        "monthly_revenue_growth_expected_initial_null",
        1,
        initial_growth_null_ok,
    )

    return validation_rows


# =============================================================================
# EXPORTS AND SUMMARY
# =============================================================================
def export_outputs(
    orders_features: pd.DataFrame,
    order_items_features: pd.DataFrame,
    customer_features: pd.DataFrame,
    monthly_features: pd.DataFrame,
    validation_rows: list[dict],
    paths: dict[str, Path],
    logger: logging.Logger,
) -> None:
    """Write feature datasets, validation CSV, and summary JSON to the project output directories."""
    paths["feature_dir"].mkdir(parents=True, exist_ok=True)
    paths["report_dir"].mkdir(parents=True, exist_ok=True)

    orders_features.to_csv(paths["feature_dir"] / "orders_features.csv", index=False)
    order_items_features.to_csv(paths["feature_dir"] / "order_items_features.csv", index=False)
    customer_features.to_csv(paths["feature_dir"] / "customer_features.csv", index=False)
    monthly_features.to_csv(paths["feature_dir"] / "monthly_features.csv", index=False)
    logger.info("Feature datasets exported to %s", paths["feature_dir"])

    validation_df = pd.DataFrame(validation_rows)
    validation_df.to_csv(paths["validation_file"], index=False)
    logger.info("Validation report exported to %s", paths["validation_file"])


def create_summary(
    source_datasets: dict[str, pd.DataFrame],
    orders_features: pd.DataFrame,
    order_items_features: pd.DataFrame,
    customer_features: pd.DataFrame,
    monthly_features: pd.DataFrame,
    validation_rows: list[dict],
) -> dict:
    """Create the summary JSON payload for the feature-engineering execution."""
    summary = {
        "execution_timestamp": datetime.now().isoformat(timespec="seconds"),
        "source_dataset_row_counts": {name: int(len(df)) for name, df in source_datasets.items()},
        "output_dataset_row_counts": {
            "orders_features.csv": int(len(orders_features)),
            "order_items_features.csv": int(len(order_items_features)),
            "customer_features.csv": int(len(customer_features)),
            "monthly_features.csv": int(len(monthly_features)),
        },
        "total_orders": int(orders_features["order_id"].nunique()),
        "total_customers": int(customer_features["customer_unique_id"].nunique()),
        "total_order_revenue": float(orders_features["order_revenue"].sum()),
        "total_order_value": float(orders_features["total_order_value"].sum()),
        "total_monthly_revenue": float(monthly_features["monthly_revenue"].sum()),
        "validation_pass_count": int(sum(1 for row in validation_rows if row["status"] == "PASS")),
        "validation_fail_count": int(sum(1 for row in validation_rows if row["status"] == "FAIL")),
    }
    return summary


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
def main() -> None:
    """Execute the full Phase 12 feature engineering pipeline."""
    logger, paths = setup_logging()
    logger.info("=== Phase 12 feature engineering started ===")

    try:
        datasets = load_datasets(logger, paths)
        validate_source_columns(datasets, logger)
        convert_date_columns(datasets, logger)

        # Order item features
        logger.info("Creating order item features...")
        order_items_features = create_order_item_features(datasets, logger)

        # Order features
        logger.info("Creating order features...")
        orders_features = create_order_features(datasets, order_items_features, logger)

        # Customer features
        logger.info("Creating customer features...")
        customer_features = create_customer_features(orders_features, logger)

        # Monthly features
        logger.info("Creating monthly features...")
        monthly_features = create_monthly_features(orders_features, logger)

        # Validation and export
        logger.info("Running final feature validation...")
        validation_rows = validate_features(
            datasets,
            orders_features,
            order_items_features,
            customer_features,
            monthly_features,
            logger,
        )

        export_outputs(
            orders_features,
            order_items_features,
            customer_features,
            monthly_features,
            validation_rows,
            paths,
            logger,
        )

        summary = create_summary(datasets, orders_features, order_items_features, customer_features, monthly_features, validation_rows)
        with open(paths["summary_file"], "w", encoding="utf-8") as summary_file:
            json.dump(summary, summary_file, indent=2)
        logger.info("Summary JSON exported to %s", paths["summary_file"])

        pass_count = sum(1 for row in validation_rows if row["status"] == "PASS")
        fail_count = sum(1 for row in validation_rows if row["status"] == "FAIL")
        logger.info("Execution completed successfully. PASS=%s | FAIL=%s", pass_count, fail_count)

        print("\n=== Feature Engineering Summary ===")
        print(f"Orders output rows: {len(orders_features)}")
        print(f"Order Items output rows: {len(order_items_features)}")
        print(f"Customer output rows: {len(customer_features)}")
        print(f"Monthly output rows: {len(monthly_features)}")
        print(f"Feature validation: PASS={pass_count}, FAIL={fail_count}")
        print(f"Outputs saved to: {paths['feature_dir']} and {paths['report_dir']}")

    except Exception as exc:  # pragma: no cover - top-level pipeline guard
        logger.exception("Feature engineering execution failed: %s", exc)
        raise


if __name__ == "__main__":
    main()
