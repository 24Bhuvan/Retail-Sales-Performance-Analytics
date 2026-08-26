from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import psycopg2


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


# =============================================================================
# POSTGRESQL CONFIGURATION
# =============================================================================

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "retail_sales_analytics"
DB_USER = "postgres"


# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

LOGGER = logging.getLogger("phase9_cross_validation")


# =============================================================================
# LOAD PYTHON PROCESSED DATA
# =============================================================================

def load_processed_datasets() -> dict[str, pd.DataFrame]:

    LOGGER.info("Loading Python processed datasets...")

    datasets = {
        "orders": pd.read_csv(
            PROCESSED_DIR / "orders_processed.csv"
        ),
        "order_items": pd.read_csv(
            PROCESSED_DIR / "order_items_processed.csv"
        ),
        "payments": pd.read_csv(
            PROCESSED_DIR / "payments_processed.csv"
        ),
        "reviews": pd.read_csv(
            PROCESSED_DIR / "reviews_processed.csv"
        ),
        "customers": pd.read_csv(
            PROCESSED_DIR / "customers_processed.csv"
        ),
        "products": pd.read_csv(
            PROCESSED_DIR / "products_processed.csv"
        ),
        "sellers": pd.read_csv(
            PROCESSED_DIR / "sellers_processed.csv"
        ),
    }

    for name, df in datasets.items():

        LOGGER.info(
            "PYTHON INPUT | %-15s | rows=%d | columns=%d",
            name,
            len(df),
            len(df.columns),
        )

    return datasets


# =============================================================================
# PYTHON METRICS
# =============================================================================

def calculate_python_metrics(
    datasets: dict[str, pd.DataFrame],
) -> dict[str, float]:

    LOGGER.info(
        "Calculating Python/Pandas validation metrics..."
    )

    orders = datasets["orders"]
    order_items = datasets["order_items"]
    payments = datasets["payments"]
    reviews = datasets["reviews"]
    customers = datasets["customers"]
    products = datasets["products"]
    sellers = datasets["sellers"]

    metrics = {}

    # -------------------------------------------------------------------------
    # ROW COUNTS
    # -------------------------------------------------------------------------

    metrics["orders_rows"] = len(orders)

    metrics["order_items_rows"] = len(order_items)

    metrics["payments_rows"] = len(payments)

    metrics["reviews_rows"] = len(reviews)

    metrics["customers_rows"] = len(customers)

    metrics["products_rows"] = len(products)

    metrics["sellers_rows"] = len(sellers)

    # -------------------------------------------------------------------------
    # DISTINCT COUNTS
    # -------------------------------------------------------------------------

    metrics["order_count"] = (
        orders["order_id"].nunique()
    )

    metrics["order_item_count"] = len(
        order_items
    )

    metrics["payment_count"] = len(
        payments
    )

    metrics["review_count"] = len(
        reviews
    )

    metrics["customer_count"] = (
        customers["customer_id"].nunique()
    )

    metrics["seller_count"] = (
        sellers["seller_id"].nunique()
    )

    metrics["product_count"] = (
        products["product_id"].nunique()
    )

    metrics["category_count"] = (
        products["product_category_name"]
        .nunique()
    )

    # -------------------------------------------------------------------------
    # FINANCIAL AGGREGATES
    # -------------------------------------------------------------------------

    metrics["total_payment_value"] = round(
        payments["payment_value"]
        .sum(),
        2,
    )

    metrics["total_item_price"] = round(
        order_items["price"]
        .sum(),
        2,
    )

    return metrics


# =============================================================================
# POSTGRESQL QUERIES
# =============================================================================

POSTGRES_QUERIES = {

    "orders_rows": """
        SELECT COUNT(*)
        FROM olist_orders_dataset;
    """,

    "order_items_rows": """
        SELECT COUNT(*)
        FROM olist_order_items_dataset;
    """,

    "payments_rows": """
        SELECT COUNT(*)
        FROM olist_order_payments_dataset;
    """,

    "reviews_rows": """
        SELECT COUNT(*)
        FROM olist_order_reviews_dataset;
    """,

    "customers_rows": """
        SELECT COUNT(*)
        FROM olist_customers_dataset;
    """,

    "products_rows": """
        SELECT COUNT(*)
        FROM olist_products_dataset;
    """,

    "sellers_rows": """
        SELECT COUNT(*)
        FROM olist_sellers_dataset;
    """,

    "order_count": """
        SELECT COUNT(DISTINCT order_id)
        FROM olist_orders_dataset;
    """,

    "order_item_count": """
        SELECT COUNT(*)
        FROM olist_order_items_dataset;
    """,

    "payment_count": """
        SELECT COUNT(*)
        FROM olist_order_payments_dataset;
    """,

    "review_count": """
        SELECT COUNT(*)
        FROM olist_order_reviews_dataset;
    """,

    "customer_count": """
        SELECT COUNT(DISTINCT customer_id)
        FROM olist_customers_dataset;
    """,

    "seller_count": """
        SELECT COUNT(DISTINCT seller_id)
        FROM olist_sellers_dataset;
    """,

    "product_count": """
        SELECT COUNT(DISTINCT product_id)
        FROM olist_products_dataset;
    """,

    "category_count": """
        SELECT COUNT(DISTINCT product_category_name)
        FROM olist_products_dataset;
    """,

    "total_payment_value": """
        SELECT ROUND(
            SUM(payment_value)::numeric,
            2
        )
        FROM olist_order_payments_dataset;
    """,

    "total_item_price": """
        SELECT ROUND(
            SUM(price)::numeric,
            2
        )
        FROM olist_order_items_dataset;
    """,
}


# =============================================================================
# POSTGRESQL METRICS
# =============================================================================

def calculate_postgres_metrics() -> dict[str, float]:

    LOGGER.info(
        "Connecting to PostgreSQL..."
    )

    password = input(
        "Enter PostgreSQL password: "
    )

    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=password,
    )

    metrics = {}

    try:

        with connection.cursor() as cursor:

            for metric, query in POSTGRES_QUERIES.items():

                LOGGER.info(
                    "Executing PostgreSQL metric: %s",
                    metric,
                )

                cursor.execute(query)

                value = cursor.fetchone()[0]

                if value is None:
                    value = 0

                metrics[metric] = float(value)

    finally:

        connection.close()

    LOGGER.info(
        "PostgreSQL connection closed."
    )

    return metrics


# =============================================================================
# COMPARISON
# =============================================================================

COUNT_METRICS = {
    "orders_rows",
    "order_items_rows",
    "payments_rows",
    "reviews_rows",
    "customers_rows",
    "products_rows",
    "sellers_rows",
    "order_count",
    "order_item_count",
    "payment_count",
    "review_count",
    "customer_count",
    "seller_count",
    "product_count",
    "category_count",
}


MONEY_METRICS = {
    "total_payment_value",
    "total_item_price",
}


def compare_metrics(
    python_metrics: dict[str, float],
    postgres_metrics: dict[str, float],
) -> pd.DataFrame:

    LOGGER.info(
        "Comparing Python vs PostgreSQL..."
    )

    rows = []

    for metric in python_metrics:

        python_value = float(
            python_metrics[metric]
        )

        postgres_value = float(
            postgres_metrics[metric]
        )

        difference = (
            python_value -
            postgres_value
        )

        absolute_difference = abs(
            difference
        )

        if metric in COUNT_METRICS:

            status = (
                "PASS"
                if absolute_difference == 0
                else "FAIL"
            )

        elif metric in MONEY_METRICS:

            status = (
                "PASS"
                if absolute_difference <= 0.01
                else "FAIL"
            )

        else:

            status = "FAIL"

        rows.append(
            {
                "metric": metric,
                "python_value": python_value,
                "postgresql_value": postgres_value,
                "difference": difference,
                "absolute_difference": absolute_difference,
                "status": status,
            }
        )

    return pd.DataFrame(rows)


# =============================================================================
# VALIDATE CROSS-CHECK
# =============================================================================

def validate_cross_check(
    report: pd.DataFrame,
) -> None:

    failed = report[
        report["status"] != "PASS"
    ]

    if not failed.empty:

        LOGGER.error(
            "PostgreSQL cross-validation FAILED."
        )

        LOGGER.error(
            "\n%s",
            failed.to_string(index=False),
        )

        raise RuntimeError(
            "Step 12 failed. "
            "Python and PostgreSQL results do not match."
        )

    LOGGER.info(
        "All %d cross-validation metrics PASSED.",
        len(report),
    )


# =============================================================================
# SAVE REPORT
# =============================================================================

def save_report(
    report: pd.DataFrame,
) -> Path:

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        REPORT_DIR /
        "postgresql_cross_validation.csv"
    )

    report.to_csv(
        output_path,
        index=False,
    )

    LOGGER.info(
        "Saved cross-validation report: %s",
        output_path,
    )

    return output_path


# =============================================================================
# MAIN
# =============================================================================

def main():

    LOGGER.info("=" * 80)
    LOGGER.info(
        "PHASE 9 — STEP 12"
    )
    LOGGER.info(
        "PYTHON vs POSTGRESQL CROSS-VALIDATION"
    )
    LOGGER.info("=" * 80)

    # -------------------------------------------------------------------------
    # Python
    # -------------------------------------------------------------------------

    datasets = load_processed_datasets()

    python_metrics = calculate_python_metrics(
        datasets
    )

    # -------------------------------------------------------------------------
    # PostgreSQL
    # -------------------------------------------------------------------------

    postgres_metrics = calculate_postgres_metrics()

    # -------------------------------------------------------------------------
    # Compare
    # -------------------------------------------------------------------------

    report = compare_metrics(
        python_metrics,
        postgres_metrics,
    )

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------

    LOGGER.info("=" * 80)
    LOGGER.info(
        "CROSS-VALIDATION RESULTS"
    )
    LOGGER.info("=" * 80)

    for _, row in report.iterrows():

        LOGGER.info(
            "%-30s | Python=%-15s | PostgreSQL=%-15s | Difference=%-10s | %s",
            row["metric"],
            row["python_value"],
            row["postgresql_value"],
            row["difference"],
            row["status"],
        )

    # -------------------------------------------------------------------------
    # Validate
    # -------------------------------------------------------------------------

    validate_cross_check(
        report
    )

    # -------------------------------------------------------------------------
    # Save evidence
    # -------------------------------------------------------------------------

    save_report(
        report
    )

    LOGGER.info("=" * 80)
    LOGGER.info(
        "STEP 12 — POSTGRESQL CROSS-VALIDATION PASSED"
    )
    LOGGER.info("=" * 80)


if __name__ == "__main__":
    main()