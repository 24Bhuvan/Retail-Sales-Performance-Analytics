from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# RETAIL SALES PERFORMANCE ANALYTICS
# Phase 14 — Step 4
# Business Metrics Calculation
#
# File:
# src/analysis/kpi_calculations.py
#
# Purpose:
# - Load controlled feature datasets
# - Calculate all 32 approved KPIs using Pandas
# - Produce kpi_results.csv
# - Produce grouped business metric outputs
# - Preserve controlled analytical grain
# - Preserve NaN for unavailable/invalid denominators
#
# Controlled Analytical Grains:
# - Orders
# - Order Items
# - Customers
# - Monthly
#
# Revenue Standard:
# - Revenue = item_revenue / order_revenue
# - Freight excluded from revenue
# - Payment value remains separate from revenue
# ============================================================


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FEATURE_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "features"
)

CLEANED_DIR = (
    PROJECT_ROOT
    / "data"
    / "cleaned"
)

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "business_metrics"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONSTANTS
# ============================================================

EXPECTED_KPI_COUNT = 32


CURRENT_OUTPUT_FILES = {
    "kpi_results.csv",
    "monthly_metrics.csv",
    "category_metrics.csv",
    "product_metrics.csv",
    "seller_metrics.csv",
    "regional_metrics.csv"
}


# ============================================================
# HELPERS
# ============================================================

def safe_divide(numerator, denominator):
    """
    Divide while preserving NaN when denominator is:
    - None
    - NaN
    - zero
    """

    if denominator is None:
        return np.nan

    if pd.isna(denominator):
        return np.nan

    if denominator == 0:
        return np.nan

    return numerator / denominator


def first_existing_file(directories, filenames):
    """
    Return the first existing file found.

    Searches directories in the provided order and filenames
    in the provided order.
    """

    for directory in directories:

        for filename in filenames:

            path = directory / filename

            if path.exists():

                return path

    return None


def read_csv_required(directory, filename):
    """
    Read a required CSV dataset.
    """

    path = directory / filename

    if not path.exists():

        raise FileNotFoundError(
            f"Required dataset not found: {path}"
        )

    return pd.read_csv(path)


def require_columns(
    dataframe,
    required_columns,
    dataframe_name
):
    """
    Validate that required columns exist.
    """

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:

        raise KeyError(
            f"{dataframe_name} is missing required columns: "
            f"{missing_columns}"
        )


def sum_series(series):
    """
    Sum while preserving NaN if all values are missing.
    """

    return series.sum(
        min_count=1
    )


def calculate_monthly_revenue_from_orders(orders):
    """
    Calculate monthly revenue from order grain.
    """

    require_columns(
        orders,
        [
            "year_month",
            "order_revenue"
        ],
        "orders"
    )

    monthly_revenue = (
        orders
        .dropna(
            subset=[
                "year_month"
            ]
        )
        .groupby(
            "year_month"
        )[
            "order_revenue"
        ]
        .sum(
            min_count=1
        )
        .sort_index()
    )

    return monthly_revenue


def calculate_monthly_growth(series):
    """
    Calculate month-over-month revenue growth.

    Growth is NaN when the previous month is:
    - missing
    - zero

    This prevents division by zero from producing meaningless
    infinite or extreme growth values.
    """

    previous = (
        series.shift(1)
    )

    growth = pd.Series(
        np.nan,
        index=series.index,
        dtype="float64"
    )

    valid_mask = (
        series.notna()
        & previous.notna()
        & previous.ne(0)
    )

    growth.loc[
        valid_mask
    ] = (
        (
            series.loc[
                valid_mask
            ]
            - previous.loc[
                valid_mask
            ]
        )
        / previous.loc[
            valid_mask
        ]
        * 100
    )

    return growth


# ============================================================
# DATA LOADING
# ============================================================

def load_feature_datasets():
    """
    Load controlled feature datasets.

    Required:
    - orders_features.csv
    - order_items_features.csv

    Optional:
    - customers_features.csv
    - monthly_features.csv

    Customers are derived from order grain when a dedicated
    customer feature dataset is unavailable.
    """

    # --------------------------------------------------------
    # ORDERS
    # --------------------------------------------------------

    orders = read_csv_required(
        FEATURE_DIR,
        "orders_features.csv"
    )


    # --------------------------------------------------------
    # ORDER ITEMS
    # --------------------------------------------------------

    order_items = read_csv_required(
        FEATURE_DIR,
        "order_items_features.csv"
    )


    # --------------------------------------------------------
    # CUSTOMERS
    # --------------------------------------------------------

    customers_path = (
        FEATURE_DIR
        / "customers_features.csv"
    )

    if customers_path.exists():

        customers = pd.read_csv(
            customers_path
        )

        print(
            "Loaded customers feature dataset."
        )

    else:

        print(
            "customers_features.csv not found. "
            "Deriving customer grain from orders_features.csv."
        )

        customer_columns = [
            column
            for column in [
                "customer_id",
                "customer_unique_id"
            ]
            if column in orders.columns
        ]

        if customer_columns:

            customers = (
                orders[
                    customer_columns
                ]
                .drop_duplicates()
                .reset_index(
                    drop=True
                )
            )

        else:

            customers = pd.DataFrame()


    # --------------------------------------------------------
    # MONTHLY
    # --------------------------------------------------------

    monthly_path = (
        FEATURE_DIR
        / "monthly_features.csv"
    )

    if monthly_path.exists():

        monthly = pd.read_csv(
            monthly_path
        )

        print(
            "Loaded monthly feature dataset."
        )

    else:

        print(
            "monthly_features.csv not found. "
            "Monthly metrics will be derived from orders."
        )

        monthly = pd.DataFrame()


    return (
        orders,
        order_items,
        customers,
        monthly
    )


# ============================================================
# DATA ENRICHMENT
# ============================================================

def enrich_order_items_with_category(order_items):
    """
    Add product category to order-item grain.

    Search priority:
    1. Existing order_items column
    2. Cleaned products dataset
    3. Processed products dataset

    Supports:
    - olist_products_dataset.csv
    - products_processed.csv
    - products_cleaned.csv
    - products.csv
    """

    # --------------------------------------------------------
    # EXISTING CATEGORY
    # --------------------------------------------------------

    if "product_category" in order_items.columns:

        enriched = (
            order_items.copy()
        )

        enriched[
            "product_category"
        ] = (
            enriched[
                "product_category"
            ]
            .fillna(
                "Unknown/Untranslated"
            )
        )

        return enriched


    # --------------------------------------------------------
    # LOCATE PRODUCTS DATASET
    # --------------------------------------------------------

    products_path = first_existing_file(
        directories=[
            CLEANED_DIR,
            PROCESSED_DIR
        ],
        filenames=[
            "olist_products_dataset.csv",
            "products_processed.csv",
            "products_cleaned.csv",
            "products.csv"
        ]
    )


    if products_path is None:

        print(
            "WARNING: Products dataset not found. "
            "Category metrics will use Unknown/Untranslated."
        )

        enriched = (
            order_items.copy()
        )

        enriched[
            "product_category"
        ] = (
            "Unknown/Untranslated"
        )

        return enriched


    print(
        f"Using products dataset: "
        f"{products_path.name}"
    )


    products = pd.read_csv(
        products_path
    )


    # --------------------------------------------------------
    # IDENTIFY CATEGORY COLUMN
    # --------------------------------------------------------

    category_column = None

    candidate_columns = [
        "product_category",
        "product_category_name_english",
        "product_category_name"
    ]


    for column in candidate_columns:

        if column in products.columns:

            category_column = column

            break


    if (
        "product_id" not in products.columns
        or category_column is None
    ):

        print(
            "WARNING: Product category columns unavailable. "
            "Category metrics will use Unknown/Untranslated."
        )

        enriched = (
            order_items.copy()
        )

        enriched[
            "product_category"
        ] = (
            "Unknown/Untranslated"
        )

        return enriched


    # --------------------------------------------------------
    # PREPARE LOOKUP
    # --------------------------------------------------------

    product_categories = (
        products[
            [
                "product_id",
                category_column
            ]
        ]
        .drop_duplicates(
            subset=[
                "product_id"
            ]
        )
        .rename(
            columns={
                category_column:
                    "product_category"
            }
        )
    )


    # --------------------------------------------------------
    # MERGE
    # --------------------------------------------------------

    enriched = (
        order_items
        .merge(
            product_categories,
            on="product_id",
            how="left",
            validate="many_to_one"
        )
    )


    enriched[
        "product_category"
    ] = (
        enriched[
            "product_category"
        ]
        .fillna(
            "Unknown/Untranslated"
        )
    )


    return enriched


def enrich_orders_with_customer_state(orders):
    """
    Add customer_state to order grain.

    Search priority:
    1. Existing orders column
    2. Cleaned customers dataset
    3. Processed customers dataset

    Supports:
    - olist_customers_dataset.csv
    - customers_processed.csv
    - customers_cleaned.csv
    - customers.csv
    """

    # --------------------------------------------------------
    # EXISTING STATE
    # --------------------------------------------------------

    if "customer_state" in orders.columns:

        enriched = (
            orders.copy()
        )

        enriched[
            "customer_state"
        ] = (
            enriched[
                "customer_state"
            ]
            .fillna(
                "Unknown"
            )
        )

        return enriched


    # --------------------------------------------------------
    # LOCATE CUSTOMERS DATASET
    # --------------------------------------------------------

    customers_path = first_existing_file(
        directories=[
            CLEANED_DIR,
            PROCESSED_DIR
        ],
        filenames=[
            "olist_customers_dataset.csv",
            "customers_processed.csv",
            "customers_cleaned.csv",
            "customers.csv"
        ]
    )


    if customers_path is None:

        print(
            "WARNING: Customers dataset not found. "
            "Regional metrics will use Unknown."
        )

        enriched = (
            orders.copy()
        )

        enriched[
            "customer_state"
        ] = (
            "Unknown"
        )

        return enriched


    print(
        f"Using customers dataset: "
        f"{customers_path.name}"
    )


    customers = pd.read_csv(
        customers_path
    )


    required_columns = [
        "customer_id",
        "customer_state"
    ]


    missing_columns = [
        column
        for column in required_columns
        if column not in customers.columns
    ]


    if missing_columns:

        print(
            "WARNING: Customer state columns unavailable. "
            "Regional metrics will use Unknown."
        )

        enriched = (
            orders.copy()
        )

        enriched[
            "customer_state"
        ] = (
            "Unknown"
        )

        return enriched


    # --------------------------------------------------------
    # PREPARE LOOKUP
    # --------------------------------------------------------

    customer_states = (
        customers[
            [
                "customer_id",
                "customer_state"
            ]
        ]
        .drop_duplicates(
            subset=[
                "customer_id"
            ]
        )
    )


    # --------------------------------------------------------
    # MERGE
    # --------------------------------------------------------

    enriched = (
        orders
        .merge(
            customer_states,
            on="customer_id",
            how="left",
            validate="many_to_one"
        )
    )


    enriched[
        "customer_state"
    ] = (
        enriched[
            "customer_state"
        ]
        .fillna(
            "Unknown"
        )
    )


    return enriched


# ============================================================
# KPI CALCULATIONS
# ============================================================

def calculate_kpis(
    orders,
    order_items,
    customers,
    monthly
):
    """
    Calculate all 32 approved KPIs.
    """

    kpis = []


    # ========================================================
    # PREPARED SERIES
    # ========================================================

    monthly_revenue = (
        calculate_monthly_revenue_from_orders(
            orders
        )
    )


    monthly_growth = (
        calculate_monthly_growth(
            monthly_revenue
        )
    )


    classified_delivery = (
        orders[
            orders[
                "delivery_difference_days"
            ].notna()
        ]
    )


    reviewed_orders = (
        orders[
            orders[
                "review_score"
            ].notna()
        ]
    )


    # ========================================================
    # PRIMARY KPIs
    # ========================================================

    # 1. Total Revenue

    total_revenue = (
        sum_series(
            orders[
                "order_revenue"
            ]
        )
    )

    kpis.append(
        [
            "Total Revenue",
            total_revenue,
            "Primary"
        ]
    )


    # 2. Total Orders

    total_orders = (
        orders[
            "order_id"
        ]
        .nunique()
    )

    kpis.append(
        [
            "Total Orders",
            total_orders,
            "Primary"
        ]
    )


    # 3. Average Order Value

    average_order_value = (
        safe_divide(
            total_revenue,
            total_orders
        )
    )

    kpis.append(
        [
            "Average Order Value",
            average_order_value,
            "Primary"
        ]
    )


    # 4. Monthly Revenue Growth

    monthly_revenue_growth = (
        monthly_growth.mean()
    )

    kpis.append(
        [
            "Monthly Revenue Growth",
            monthly_revenue_growth,
            "Primary"
        ]
    )


    # 5. Total Customers

    total_customers = (
        orders[
            "customer_unique_id"
        ]
        .nunique()
    )

    kpis.append(
        [
            "Total Customers",
            total_customers,
            "Primary"
        ]
    )


    # 6. Repeat Customer Rate

    customer_order_counts = (
        orders
        .dropna(
            subset=[
                "customer_unique_id"
            ]
        )
        .groupby(
            "customer_unique_id"
        )[
            "order_id"
        ]
        .nunique()
    )


    repeat_customers = (
        customer_order_counts
        > 1
    ).sum()


    repeat_customer_rate = (
        safe_divide(
            repeat_customers,
            len(
                customer_order_counts
            )
        )
        * 100
    )


    kpis.append(
        [
            "Repeat Customer Rate",
            repeat_customer_rate,
            "Primary"
        ]
    )


    # 7. On-Time Delivery Rate

    on_time_orders = (
        classified_delivery[
            "delivery_difference_days"
        ]
        <= 0
    ).sum()


    on_time_delivery_rate = (
        safe_divide(
            on_time_orders,
            len(
                classified_delivery
            )
        )
        * 100
    )


    kpis.append(
        [
            "On-Time Delivery Rate",
            on_time_delivery_rate,
            "Primary"
        ]
    )


    # 8. Average Delivery Time

    average_delivery_time = (
        orders[
            "delivery_time_days"
        ]
        .mean()
    )


    kpis.append(
        [
            "Average Delivery Time",
            average_delivery_time,
            "Primary"
        ]
    )


    # 9. Average Review Score

    average_review_score = (
        orders[
            "review_score"
        ]
        .mean()
    )


    kpis.append(
        [
            "Average Review Score",
            average_review_score,
            "Primary"
        ]
    )


    # ========================================================
    # SUPPORTING KPIs
    # ========================================================

    # 10. Total Order Value

    total_order_value = (
        sum_series(
            orders[
                "total_order_value"
            ]
        )
    )


    kpis.append(
        [
            "Total Order Value",
            total_order_value,
            "Supporting"
        ]
    )


    # 11. Monthly Revenue
    # Defined as average monthly revenue.

    monthly_revenue_value = (
        monthly_revenue.mean()
    )


    kpis.append(
        [
            "Monthly Revenue",
            monthly_revenue_value,
            "Supporting"
        ]
    )


    # 12. Average Items per Order

    average_items_per_order = (
        orders[
            "items_per_order"
        ]
        .mean()
    )


    kpis.append(
        [
            "Average Items per Order",
            average_items_per_order,
            "Supporting"
        ]
    )


    # 13. Customer Lifetime Revenue

    customer_lifetime_revenue = (
        orders
        .dropna(
            subset=[
                "customer_unique_id"
            ]
        )
        .groupby(
            "customer_unique_id"
        )[
            "order_revenue"
        ]
        .sum(
            min_count=1
        )
        .mean()
    )


    kpis.append(
        [
            "Customer Lifetime Revenue",
            customer_lifetime_revenue,
            "Supporting"
        ]
    )


    # 14. Average Customer Order Value

    customer_level_metrics = (
        orders
        .dropna(
            subset=[
                "customer_unique_id"
            ]
        )
        .groupby(
            "customer_unique_id"
        )
        .agg(
            customer_revenue=(
                "order_revenue",
                "sum"
            ),
            customer_orders=(
                "order_id",
                "nunique"
            )
        )
    )


    customer_level_metrics[
        "customer_average_order_value"
    ] = (
        customer_level_metrics[
            "customer_revenue"
        ]
        / customer_level_metrics[
            "customer_orders"
        ]
        .replace(
            0,
            np.nan
        )
    )


    average_customer_order_value = (
        customer_level_metrics[
            "customer_average_order_value"
        ]
        .mean()
    )


    kpis.append(
        [
            "Average Customer Order Value",
            average_customer_order_value,
            "Supporting"
        ]
    )


    # 15. Category Revenue
    # Defined as average revenue per category.

    category_revenue = (
        order_items
        .groupby(
            "product_category",
            dropna=False
        )[
            "item_revenue"
        ]
        .sum(
            min_count=1
        )
    )


    average_category_revenue = (
        category_revenue.mean()
    )


    kpis.append(
        [
            "Category Revenue",
            average_category_revenue,
            "Supporting"
        ]
    )


    # 16. Category Revenue Share
    # Largest category share.

    category_revenue_share = (
        safe_divide(
            category_revenue.max(),
            sum_series(
                category_revenue
            )
        )
        * 100
    )


    kpis.append(
        [
            "Category Revenue Share",
            category_revenue_share,
            "Supporting"
        ]
    )


    # 17. Product Revenue
    # Defined as average revenue per product.

    product_revenue = (
        order_items
        .dropna(
            subset=[
                "product_id"
            ]
        )
        .groupby(
            "product_id"
        )[
            "item_revenue"
        ]
        .sum(
            min_count=1
        )
    )


    average_product_revenue = (
        product_revenue.mean()
    )


    kpis.append(
        [
            "Product Revenue",
            average_product_revenue,
            "Supporting"
        ]
    )


    # 18. Seller Revenue
    # Defined as average revenue per seller.

    seller_revenue = (
        order_items
        .dropna(
            subset=[
                "seller_id"
            ]
        )
        .groupby(
            "seller_id"
        )[
            "item_revenue"
        ]
        .sum(
            min_count=1
        )
    )


    average_seller_revenue = (
        seller_revenue.mean()
    )


    kpis.append(
        [
            "Seller Revenue",
            average_seller_revenue,
            "Supporting"
        ]
    )


    # 19. Seller Order Count
    # Defined as average distinct orders per seller.

    seller_order_counts = (
        order_items
        .dropna(
            subset=[
                "seller_id"
            ]
        )
        .groupby(
            "seller_id"
        )[
            "order_id"
        ]
        .nunique()
    )


    average_seller_order_count = (
        seller_order_counts.mean()
    )


    kpis.append(
        [
            "Seller Order Count",
            average_seller_order_count,
            "Supporting"
        ]
    )


    # 20. Revenue by Customer State
    # Defined as average revenue per customer state.

    state_revenue = (
        orders
        .groupby(
            "customer_state",
            dropna=False
        )[
            "order_revenue"
        ]
        .sum(
            min_count=1
        )
    )


    revenue_by_customer_state = (
        state_revenue.mean()
    )


    kpis.append(
        [
            "Revenue by Customer State",
            revenue_by_customer_state,
            "Supporting"
        ]
    )


    # 21. Total Payment Value

    total_payment_value = (
        sum_series(
            orders[
                "payment_value_per_order"
            ]
        )
    )


    kpis.append(
        [
            "Total Payment Value",
            total_payment_value,
            "Supporting"
        ]
    )


    # 22. Payment Method Share
    #
    # payment_type is not guaranteed in the controlled
    # orders feature grain.
    #
    # Preserve NaN if unavailable.

    payment_method_share = np.nan


    kpis.append(
        [
            "Payment Method Share",
            payment_method_share,
            "Supporting"
        ]
    )


    # 23. Average Payment Installments

    average_payment_installments = (
        orders[
            "number_payment_installments"
        ]
        .mean()
    )


    kpis.append(
        [
            "Average Payment Installments",
            average_payment_installments,
            "Supporting"
        ]
    )


    # 24. Average Processing Time

    average_processing_time = (
        orders[
            "processing_time_days"
        ]
        .mean()
    )


    kpis.append(
        [
            "Average Processing Time",
            average_processing_time,
            "Supporting"
        ]
    )


    # 25. Late Delivery Rate

    late_orders = (
        classified_delivery[
            "delivery_difference_days"
        ]
        > 0
    ).sum()


    late_delivery_rate = (
        safe_divide(
            late_orders,
            len(
                classified_delivery
            )
        )
        * 100
    )


    kpis.append(
        [
            "Late Delivery Rate",
            late_delivery_rate,
            "Supporting"
        ]
    )


    # 26. Average Delivery Difference

    average_delivery_difference = (
        orders[
            "delivery_difference_days"
        ]
        .mean()
    )


    kpis.append(
        [
            "Average Delivery Difference",
            average_delivery_difference,
            "Supporting"
        ]
    )


    # 27. Total Freight Value

    total_freight_value = (
        sum_series(
            order_items[
                "freight_value"
            ]
        )
    )


    kpis.append(
        [
            "Total Freight Value",
            total_freight_value,
            "Supporting"
        ]
    )


    # 28. Low Satisfaction Rate

    low_satisfaction_orders = (
        reviewed_orders[
            "review_score"
        ]
        <= 2
    ).sum()


    low_satisfaction_rate = (
        safe_divide(
            low_satisfaction_orders,
            len(
                reviewed_orders
            )
        )
        * 100
    )


    kpis.append(
        [
            "Low Satisfaction Rate",
            low_satisfaction_rate,
            "Supporting"
        ]
    )


    # 29. High Satisfaction Rate

    high_satisfaction_orders = (
        reviewed_orders[
            "review_score"
        ]
        >= 4
    ).sum()


    high_satisfaction_rate = (
        safe_divide(
            high_satisfaction_orders,
            len(
                reviewed_orders
            )
        )
        * 100
    )


    kpis.append(
        [
            "High Satisfaction Rate",
            high_satisfaction_rate,
            "Supporting"
        ]
    )


    # ========================================================
    # DIAGNOSTIC KPIs
    # ========================================================

    # 30. Rolling 3-Month Revenue

    if monthly_revenue.empty:

        rolling_3_month_revenue = np.nan

    else:

        rolling_3_month_revenue = (
            monthly_revenue
            .rolling(
                window=3,
                min_periods=1
            )
            .sum()
            .iloc[-1]
        )


    kpis.append(
        [
            "Rolling 3-Month Revenue",
            rolling_3_month_revenue,
            "Diagnostic"
        ]
    )


    # 31. Multi-Payment Order Rate

    payment_orders = (
        orders[
            orders[
                "multi_payment_flag"
            ].notna()
        ]
    )


    multi_payment_orders = (
        payment_orders[
            "multi_payment_flag"
        ]
        == 1
    ).sum()


    multi_payment_order_rate = (
        safe_divide(
            multi_payment_orders,
            len(
                payment_orders
            )
        )
        * 100
    )


    kpis.append(
        [
            "Multi-Payment Order Rate",
            multi_payment_order_rate,
            "Diagnostic"
        ]
    )


    # 32. Freight-to-Price Ratio

    freight_to_price_ratio = (
        order_items[
            "freight_to_price_ratio"
        ]
        .mean()
    )


    kpis.append(
        [
            "Freight-to-Price Ratio",
            freight_to_price_ratio,
            "Diagnostic"
        ]
    )


    # ========================================================
    # RESULT
    # ========================================================

    kpi_results = pd.DataFrame(
        kpis,
        columns=[
            "kpi_name",
            "kpi_value",
            "kpi_hierarchy"
        ]
    )


    return kpi_results


# ============================================================
# GROUPED BUSINESS METRICS
# ============================================================

def create_grouped_outputs(
    orders,
    order_items
):
    """
    Create grouped business metric outputs.
    """


    # ========================================================
    # MONTHLY METRICS
    # ========================================================

    monthly_metrics = (
        orders
        .dropna(
            subset=[
                "year_month"
            ]
        )
        .groupby(
            "year_month"
        )
        .agg(
            monthly_revenue=(
                "order_revenue",
                "sum"
            ),
            monthly_orders=(
                "order_id",
                "nunique"
            ),
            monthly_customers=(
                "customer_unique_id",
                "nunique"
            )
        )
        .reset_index()
        .sort_values(
            "year_month"
        )
        .reset_index(
            drop=True
        )
    )


    monthly_metrics[
        "average_order_value"
    ] = (
        monthly_metrics[
            "monthly_revenue"
        ]
        / monthly_metrics[
            "monthly_orders"
        ]
        .replace(
            0,
            np.nan
        )
    )


    monthly_metrics[
        "monthly_revenue_growth"
    ] = (
        calculate_monthly_growth(
            monthly_metrics[
                "monthly_revenue"
            ]
        )
    )


    monthly_metrics[
        "rolling_3_month_revenue"
    ] = (
        monthly_metrics[
            "monthly_revenue"
        ]
        .rolling(
            window=3,
            min_periods=1
        )
        .sum()
    )


    monthly_metrics[
        "cumulative_revenue"
    ] = (
        monthly_metrics[
            "monthly_revenue"
        ]
        .cumsum()
    )


    # ========================================================
    # CATEGORY METRICS
    # ========================================================

    category_metrics = (
        order_items
        .assign(
            product_category=(
                order_items[
                    "product_category"
                ]
                .fillna(
                    "Unknown/Untranslated"
                )
            )
        )
        .groupby(
            "product_category"
        )
        .agg(
            category_revenue=(
                "item_revenue",
                "sum"
            ),
            order_count=(
                "order_id",
                "nunique"
            ),
            item_count=(
                "order_item_id",
                "count"
            )
        )
        .reset_index()
    )


    total_category_revenue = (
        sum_series(
            category_metrics[
                "category_revenue"
            ]
        )
    )


    category_metrics[
        "category_revenue_share"
    ] = (
        category_metrics[
            "category_revenue"
        ]
        / (
            total_category_revenue
            if (
                pd.notna(
                    total_category_revenue
                )
                and total_category_revenue != 0
            )
            else np.nan
        )
        * 100
    )


    category_metrics[
        "category_rank"
    ] = (
        category_metrics[
            "category_revenue"
        ]
        .rank(
            method="min",
            ascending=False
        )
        .astype(
            "Int64"
        )
    )


    category_metrics = (
        category_metrics
        .sort_values(
            [
                "category_rank",
                "product_category"
            ]
        )
        .reset_index(
            drop=True
        )
    )


    # ========================================================
    # PRODUCT METRICS
    # ========================================================

    product_metrics = (
        order_items
        .dropna(
            subset=[
                "product_id"
            ]
        )
        .groupby(
            "product_id"
        )
        .agg(
            product_revenue=(
                "item_revenue",
                "sum"
            ),
            order_count=(
                "order_id",
                "nunique"
            ),
            item_count=(
                "order_item_id",
                "count"
            )
        )
        .reset_index()
    )


    product_metrics[
        "product_rank"
    ] = (
        product_metrics[
            "product_revenue"
        ]
        .rank(
            method="min",
            ascending=False
        )
        .astype(
            "Int64"
        )
    )


    product_metrics = (
        product_metrics
        .sort_values(
            [
                "product_rank",
                "product_id"
            ]
        )
        .reset_index(
            drop=True
        )
    )


    # ========================================================
    # SELLER METRICS
    # ========================================================

    seller_metrics = (
        order_items
        .dropna(
            subset=[
                "seller_id"
            ]
        )
        .groupby(
            "seller_id"
        )
        .agg(
            seller_revenue=(
                "item_revenue",
                "sum"
            ),
            seller_order_count=(
                "order_id",
                "nunique"
            ),
            item_count=(
                "order_item_id",
                "count"
            )
        )
        .reset_index()
    )


    seller_metrics[
        "seller_rank"
    ] = (
        seller_metrics[
            "seller_revenue"
        ]
        .rank(
            method="min",
            ascending=False
        )
        .astype(
            "Int64"
        )
    )


    seller_metrics = (
        seller_metrics
        .sort_values(
            [
                "seller_rank",
                "seller_id"
            ]
        )
        .reset_index(
            drop=True
        )
    )


    # ========================================================
    # REGIONAL METRICS
    # ========================================================

    regional_metrics = (
        orders
        .assign(
            customer_state=(
                orders[
                    "customer_state"
                ]
                .fillna(
                    "Unknown"
                )
            )
        )
        .groupby(
            "customer_state"
        )
        .agg(
            revenue=(
                "order_revenue",
                "sum"
            ),
            orders=(
                "order_id",
                "nunique"
            ),
            customers=(
                "customer_unique_id",
                "nunique"
            )
        )
        .reset_index()
    )


    regional_metrics[
        "average_order_value"
    ] = (
        regional_metrics[
            "revenue"
        ]
        / regional_metrics[
            "orders"
        ]
        .replace(
            0,
            np.nan
        )
    )


    regional_metrics[
        "revenue_rank"
    ] = (
        regional_metrics[
            "revenue"
        ]
        .rank(
            method="min",
            ascending=False
        )
        .astype(
            "Int64"
        )
    )


    regional_metrics = (
        regional_metrics
        .sort_values(
            [
                "revenue_rank",
                "customer_state"
            ]
        )
        .reset_index(
            drop=True
        )
    )


    return {
        "monthly_metrics":
            monthly_metrics,

        "category_metrics":
            category_metrics,

        "product_metrics":
            product_metrics,

        "seller_metrics":
            seller_metrics,

        "regional_metrics":
            regional_metrics
    }


# ============================================================
# OUTPUT VALIDATION
# ============================================================

def validate_outputs(
    kpi_results,
    grouped_outputs
):
    """
    Validate Step 4 outputs.
    """


    # --------------------------------------------------------
    # KPI COUNT
    # --------------------------------------------------------

    if len(kpi_results) != EXPECTED_KPI_COUNT:

        raise ValueError(
            f"Expected {EXPECTED_KPI_COUNT} KPIs "
            f"but calculated {len(kpi_results)}."
        )


    # --------------------------------------------------------
    # KPI DUPLICATES
    # --------------------------------------------------------

    duplicate_kpis = (
        kpi_results[
            "kpi_name"
        ]
        .duplicated()
        .sum()
    )


    if duplicate_kpis > 0:

        raise ValueError(
            "Duplicate KPI names detected."
        )


    # --------------------------------------------------------
    # GROUPED OUTPUTS
    # --------------------------------------------------------

    required_outputs = [
        "monthly_metrics",
        "category_metrics",
        "product_metrics",
        "seller_metrics",
        "regional_metrics"
    ]


    for output_name in required_outputs:

        if output_name not in grouped_outputs:

            raise ValueError(
                f"Missing grouped output: "
                f"{output_name}"
            )


        dataframe = (
            grouped_outputs[
                output_name
            ]
        )


        if dataframe.empty:

            raise ValueError(
                f"Grouped output is empty: "
                f"{output_name}"
            )


# ============================================================
# OUTPUT CLEANUP
# ============================================================

def remove_stale_csv_outputs():
    """
    Remove stale legacy CSV outputs from the business metrics
    directory.

    Only current Step 4 output files are preserved.
    """

    for path in OUTPUT_DIR.glob(
        "*.csv"
    ):

        if path.name not in CURRENT_OUTPUT_FILES:

            path.unlink()

            print(
                f"Removed stale output: "
                f"{path.name}"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    print(
        "Loading feature datasets..."
    )


    (
        orders,
        order_items,
        customers,
        monthly
    ) = (
        load_feature_datasets()
    )


    # --------------------------------------------------------
    # ENRICH
    # --------------------------------------------------------

    print(
        "Enriching order items with product category..."
    )


    order_items = (
        enrich_order_items_with_category(
            order_items
        )
    )


    print(
        "Enriching orders with customer state..."
    )


    orders = (
        enrich_orders_with_customer_state(
            orders
        )
    )


    # --------------------------------------------------------
    # CALCULATE KPIs
    # --------------------------------------------------------

    print(
        "Calculating 32 KPIs..."
    )


    kpi_results = (
        calculate_kpis(
            orders,
            order_items,
            customers,
            monthly
        )
    )


    # --------------------------------------------------------
    # GROUPED OUTPUTS
    # --------------------------------------------------------

    print(
        "Creating grouped business metrics..."
    )


    grouped_outputs = (
        create_grouped_outputs(
            orders,
            order_items
        )
    )


    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    print(
        "Validating outputs..."
    )


    validate_outputs(
        kpi_results,
        grouped_outputs
    )


    # --------------------------------------------------------
    # CLEAN OLD OUTPUTS
    # --------------------------------------------------------

    remove_stale_csv_outputs()


    # --------------------------------------------------------
    # SAVE KPI RESULTS
    # --------------------------------------------------------

    kpi_results_path = (
        OUTPUT_DIR
        / "kpi_results.csv"
    )


    kpi_results.to_csv(
        kpi_results_path,
        index=False
    )


    # --------------------------------------------------------
    # SAVE GROUPED OUTPUTS
    # --------------------------------------------------------

    for (
        output_name,
        dataframe
    ) in grouped_outputs.items():

        output_path = (
            OUTPUT_DIR
            / f"{output_name}.csv"
        )


        dataframe.to_csv(
            output_path,
            index=False
        )


    # --------------------------------------------------------
    # COMPLETION
    # --------------------------------------------------------

    print()

    print(
        "=" * 60
    )

    print(
        "Phase 14 — Step 4 Complete"
    )

    print(
        "=" * 60
    )


    print(
        f"KPIs Calculated: "
        f"{len(kpi_results)}"
    )


    print(
        f"Orders Rows: "
        f"{len(orders):,}"
    )


    print(
        f"Order Items Rows: "
        f"{len(order_items):,}"
    )


    print(
        f"Customers Rows: "
        f"{len(customers):,}"
    )


    print(
        f"Category Groups: "
        f"{len(grouped_outputs['category_metrics']):,}"
    )


    print(
        f"Seller Groups: "
        f"{len(grouped_outputs['seller_metrics']):,}"
    )


    print(
        f"Regional Groups: "
        f"{len(grouped_outputs['regional_metrics']):,}"
    )


    print(
        f"KPI Results: "
        f"{kpi_results_path}"
    )


    print(
        f"Output Directory: "
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":

    main()