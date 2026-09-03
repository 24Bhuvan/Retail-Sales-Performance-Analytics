from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# RETAIL SALES PERFORMANCE ANALYTICS
# Phase 14 — Business Metrics Pipeline
# File: src/analysis/business_metrics.py
#
# Purpose:
# Create detailed baseline analytical tables.
#
# This script is separate from kpi_calculations.py.
#
# kpi_calculations.py
#     → KPI inventory
#
# business_metrics.py
#     → Detailed analytical tables
# ============================================================


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FEATURE_DIR = PROJECT_ROOT / "data" / "processed" / "features"

CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"

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
# HELPERS
# ============================================================

def find_file(directory, filename):
    """
    Locate a required CSV file.
    """

    path = directory / filename

    if not path.exists():

        raise FileNotFoundError(
            f"Required dataset not found: {path}"
        )

    return path


def read_csv_required(directory, filename):
    """
    Read required CSV dataset.
    """

    path = find_file(
        directory,
        filename
    )

    return pd.read_csv(path)


def first_existing_file(directory, filenames):
    """
    Return first existing file from candidate filenames.
    """

    for filename in filenames:

        path = directory / filename

        if path.exists():

            return path

    return None


def safe_divide(
    numerator,
    denominator
):
    """
    Safe division.
    """

    denominator = (
        denominator
        .replace(0, np.nan)
        if isinstance(
            denominator,
            pd.Series
        )
        else denominator
    )

    return numerator / denominator


def clean_numeric_columns(
    dataframe,
    columns
):
    """
    Convert selected columns to numeric.
    """

    dataframe = dataframe.copy()

    for column in columns:

        if column in dataframe.columns:

            dataframe[column] = (
                pd.to_numeric(
                    dataframe[column],
                    errors="coerce"
                )
            )

    return dataframe


# ============================================================
# DATA LOADING
# ============================================================

def load_feature_datasets():
    """
    Load required feature datasets.
    """

    print(
        "Loading feature datasets..."
    )


    orders = read_csv_required(
        FEATURE_DIR,
        "orders_features.csv"
    )


    order_items = read_csv_required(
        FEATURE_DIR,
        "order_items_features.csv"
    )


    return (
        orders,
        order_items
    )


# ============================================================
# DATA ENRICHMENT
# ============================================================

def enrich_order_items_with_category(
    order_items
):
    """
    Add product category using cleaned products dataset.
    """

    if (
        "product_category"
        in order_items.columns
    ):

        return order_items


    products_path = first_existing_file(
        CLEANED_DIR,
        [
            "olist_products_dataset.csv",
            "products_cleaned.csv",
            "products.csv"
        ]
    )


    if products_path is None:

        print(
            "WARNING: Products dataset not found."
        )

        order_items = (
            order_items.copy()
        )

        order_items[
            "product_category"
        ] = "Unknown/Untranslated"

        return order_items


    print(
        f"Using products dataset: "
        f"{products_path.name}"
    )


    products = pd.read_csv(
        products_path
    )


    required_columns = [
        "product_id",
        "product_category_name"
    ]


    missing_columns = [
        column
        for column in required_columns
        if column not in products.columns
    ]


    if missing_columns:

        raise ValueError(
            "Products dataset missing columns: "
            f"{missing_columns}"
        )


    product_categories = (
        products[
            [
                "product_id",
                "product_category_name"
            ]
        ]
        .drop_duplicates(
            subset="product_id"
        )
        .rename(
            columns={
                "product_category_name":
                    "product_category"
            }
        )
    )


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


def enrich_orders_with_customer_state(
    orders
):
    """
    Add customer state using cleaned customers dataset.
    """

    if (
        "customer_state"
        in orders.columns
    ):

        return orders


    customers_path = first_existing_file(
        CLEANED_DIR,
        [
            "olist_customers_dataset.csv",
            "customers_cleaned.csv",
            "customers.csv"
        ]
    )


    if customers_path is None:

        print(
            "WARNING: Customers dataset not found."
        )

        orders = (
            orders.copy()
        )

        orders[
            "customer_state"
        ] = "Unknown"

        return orders


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

        raise ValueError(
            "Customers dataset missing columns: "
            f"{missing_columns}"
        )


    customer_states = (
        customers[
            [
                "customer_id",
                "customer_state"
            ]
        ]
        .drop_duplicates(
            subset="customer_id"
        )
    )


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
# 1. MONTHLY PERFORMANCE METRICS
# ============================================================

def create_monthly_metrics(
    orders
):

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
    ] = safe_divide(
        monthly_metrics[
            "monthly_revenue"
        ],
        monthly_metrics[
            "monthly_orders"
        ]
    )


    monthly_metrics[
        "monthly_revenue_growth"
    ] = (
        monthly_metrics[
            "monthly_revenue"
        ]
        .pct_change()
        * 100
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


    return monthly_metrics


# ============================================================
# 2. CATEGORY PERFORMANCE
# ============================================================

def create_category_metrics(
    order_items
):

    category_metrics = (
        order_items
        .assign(
            product_category=
            order_items[
                "product_category"
            ]
            .fillna(
                "Unknown/Untranslated"
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


    total_revenue = (
        category_metrics[
            "category_revenue"
        ]
        .sum()
    )


    category_metrics[
        "category_revenue_share"
    ] = (
        safe_divide(
            category_metrics[
                "category_revenue"
            ],
            pd.Series(
                total_revenue,
                index=category_metrics.index
            )
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


    return category_metrics


# ============================================================
# 3. PRODUCT RANKING
# ============================================================

def create_product_metrics(
    order_items
):

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


    return product_metrics


# ============================================================
# 4. REGIONAL PERFORMANCE
# ============================================================

def create_regional_metrics(
    orders
):

    regional_metrics = (
        orders
        .assign(
            customer_state=
            orders[
                "customer_state"
            ]
            .fillna(
                "Unknown"
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
    ] = safe_divide(
        regional_metrics[
            "revenue"
        ],
        regional_metrics[
            "orders"
        ]
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


    return regional_metrics


# ============================================================
# 5. CUSTOMER METRICS
# ============================================================

def create_customer_metrics(
    orders
):

    customer_metrics = (
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
            order_count=(
                "order_id",
                "nunique"
            ),
            average_order_value=(
                "order_revenue",
                "mean"
            )
        )
        .reset_index()
    )


    customer_metrics[
        "repeat_customer_flag"
    ] = (
        customer_metrics[
            "order_count"
        ]
        > 1
    ).astype(
        int
    )


    customer_metrics[
        "customer_rank"
    ] = (
        customer_metrics[
            "customer_revenue"
        ]
        .rank(
            method="min",
            ascending=False
        )
        .astype(
            "Int64"
        )
    )


    customer_metrics = (
        customer_metrics
        .sort_values(
            [
                "customer_rank",
                "customer_unique_id"
            ]
        )
        .reset_index(
            drop=True
        )
    )


    return customer_metrics


# ============================================================
# 6. SELLER METRICS
# ============================================================

def create_seller_metrics(
    order_items
):

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


    return seller_metrics


# ============================================================
# 7. PAYMENT METRICS
# ============================================================

def create_payment_metrics(
    orders
):

    payment_columns = [
        "payment_value_per_order",
        "number_payment_installments",
        "multi_payment_flag"
    ]


    available_columns = [
        column
        for column in payment_columns
        if column in orders.columns
    ]


    if not available_columns:

        raise ValueError(
            "Payment feature columns not found."
        )


    payment_metrics = (
        orders[
            [
                "order_id"
            ]
            + available_columns
        ]
        .copy()
    )


    payment_metrics = (
        payment_metrics
        .groupby(
            "order_id"
        )
        .agg(
            payment_value=(
                "payment_value_per_order",
                "first"
            ),
            payment_installments=(
                "number_payment_installments",
                "first"
            ),
            multi_payment_flag=(
                "multi_payment_flag",
                "first"
            )
        )
        .reset_index()
    )


    payment_metrics[
        "multi_payment_flag"
    ] = (
        payment_metrics[
            "multi_payment_flag"
        ]
        .fillna(0)
        .astype(int)
    )


    return payment_metrics


# ============================================================
# 8. DELIVERY METRICS
# ============================================================

def create_delivery_metrics(
    orders
):

    delivery_metrics = (
        orders[
            [
                "order_id",
                "delivery_time_days",
                "delivery_difference_days",
                "processing_time_days"
            ]
        ]
        .copy()
    )


    delivery_metrics[
        "on_time_flag"
    ] = (
        delivery_metrics[
            "delivery_difference_days"
        ]
        <= 0
    ).astype(
        "Int64"
    )


    delivery_metrics[
        "late_flag"
    ] = (
        delivery_metrics[
            "delivery_difference_days"
        ]
        > 0
    ).astype(
        "Int64"
    )


    return delivery_metrics


# ============================================================
# 9. REVIEW METRICS
# ============================================================

def create_review_metrics(
    orders
):

    review_metrics = (
        orders[
            [
                "order_id",
                "review_score"
            ]
        ]
        .copy()
    )


    review_metrics[
        "low_satisfaction_flag"
    ] = (
        review_metrics[
            "review_score"
        ]
        <= 2
    ).astype(
        "Int64"
    )


    review_metrics[
        "high_satisfaction_flag"
    ] = (
        review_metrics[
            "review_score"
        ]
        >= 4
    ).astype(
        "Int64"
    )


    return review_metrics


# ============================================================
# VALIDATION
# ============================================================

def validate_outputs(
    outputs
):

    expected_outputs = [
        "monthly_metrics",
        "category_metrics",
        "product_metrics",
        "regional_metrics",
        "customer_metrics",
        "seller_metrics",
        "payment_metrics",
        "delivery_metrics",
        "review_metrics"
    ]


    missing_outputs = [
        output
        for output in expected_outputs
        if output not in outputs
    ]


    if missing_outputs:

        raise ValueError(
            f"Missing outputs: "
            f"{missing_outputs}"
        )


    for (
        output_name,
        dataframe
    ) in outputs.items():

        if dataframe.empty:

            raise ValueError(
                f"Output is empty: "
                f"{output_name}"
            )


# ============================================================
# SAVE OUTPUTS
# ============================================================

def save_outputs(
    outputs
):

    for (
        output_name,
        dataframe
    ) in outputs.items():

        output_path = (
            OUTPUT_DIR
            / f"{output_name}.csv"
        )


        dataframe.to_csv(
            output_path,
            index=False
        )


        print(
            f"Saved: "
            f"{output_path.name}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    (
        orders,
        order_items
    ) = load_feature_datasets()


    print(
        "Enriching product categories..."
    )

    order_items = (
        enrich_order_items_with_category(
            order_items
        )
    )


    print(
        "Enriching customer states..."
    )

    orders = (
        enrich_orders_with_customer_state(
            orders
        )
    )


    print(
        "Creating business metric tables..."
    )


    outputs = {


        # 1
        "monthly_metrics":
            create_monthly_metrics(
                orders
            ),


        # 2
        "category_metrics":
            create_category_metrics(
                order_items
            ),


        # 3
        "product_metrics":
            create_product_metrics(
                order_items
            ),


        # 4
        "regional_metrics":
            create_regional_metrics(
                orders
            ),


        # 5
        "customer_metrics":
            create_customer_metrics(
                orders
            ),


        # 6
        "seller_metrics":
            create_seller_metrics(
                order_items
            ),


        # 7
        "payment_metrics":
            create_payment_metrics(
                orders
            ),


        # 8
        "delivery_metrics":
            create_delivery_metrics(
                orders
            ),


        # 9
        "review_metrics":
            create_review_metrics(
                orders
            )
    }


    print(
        "Validating outputs..."
    )

    validate_outputs(
        outputs
    )


    print(
        "Exporting final reports..."
    )

    save_outputs(
        outputs
    )


    print(
        "\n"
        "============================================================"
    )

    print(
        "Phase 14 — Step 5 Complete"
    )

    print(
        "============================================================"
    )


    print(
        f"Monthly Rows: "
        f"{len(outputs['monthly_metrics']):,}"
    )

    print(
        f"Category Rows: "
        f"{len(outputs['category_metrics']):,}"
    )

    print(
        f"Product Rows: "
        f"{len(outputs['product_metrics']):,}"
    )

    print(
        f"Regional Rows: "
        f"{len(outputs['regional_metrics']):,}"
    )

    print(
        f"Customer Rows: "
        f"{len(outputs['customer_metrics']):,}"
    )

    print(
        f"Seller Rows: "
        f"{len(outputs['seller_metrics']):,}"
    )

    print(
        f"Payment Rows: "
        f"{len(outputs['payment_metrics']):,}"
    )

    print(
        f"Delivery Rows: "
        f"{len(outputs['delivery_metrics']):,}"
    )

    print(
        f"Review Rows: "
        f"{len(outputs['review_metrics']):,}"
    )

    print(
        f"\nOutput Directory: "
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()