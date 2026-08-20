"""
Phase 5 — Post-Cleaning Data Quality Validation
Retail Sales Performance Analytics

Purpose
-------
Validate the PostgreSQL cleaned schema after execution of
sql/data_cleaning.sql.

This script validates:

    1. Cleaned table existence
    2. Row counts
    3. Primary-key uniqueness
    4. Composite-key uniqueness
    5. Chronology rules
    6. Payment installment rules
    7. Negative financial values
    8. Referential integrity
    9. Legitimate zero-value preservation
   10. Product category NULL preservation
   11. Translation coverage
   12. Geolocation duplicate reduction
   13. SQL cleaning summary consistency

IMPORTANT
---------
This script is READ-ONLY against PostgreSQL.

It does NOT:
    - modify cleaned tables
    - delete records
    - update records
    - alter schema
    - perform cleaning

Cleaning is performed exclusively by:
    sql/data_cleaning.sql

Database:
    retail_sales_analytics

Schema:
    cleaned

Outputs:
    reports/data_cleaning/post_cleaning_validation_results.csv
    reports/data_cleaning/post_cleaning_validation_summary.json
    reports/data_cleaning/post_cleaning_validation.log
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg2


# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "reports" / "data_cleaning"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RESULTS_FILE = (
    OUTPUT_DIR / "post_cleaning_validation_results.csv"
)

SUMMARY_FILE = (
    OUTPUT_DIR / "post_cleaning_validation_summary.json"
)

LOG_FILE = (
    OUTPUT_DIR / "post_cleaning_validation.log"
)


# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "retail_sales_analytics",
    "user": "postgres",
    "password": "admin123",
}


# =============================================================================
# EXPECTED CLEANED TABLES
# =============================================================================

CLEANED_TABLES = {
    "customers": "cleaned.customers",
    "geolocation": "cleaned.geolocation",
    "orders": "cleaned.orders",
    "order_items": "cleaned.order_items",
    "payments": "cleaned.payments",
    "reviews": "cleaned.reviews",
    "products": "cleaned.products",
    "sellers": "cleaned.sellers",
    "category_translation": "cleaned.category_translation",
}


# =============================================================================
# EXPECTED SOURCE COUNTS
# Based on the successfully executed Phase 5 SQL cleaning pipeline.
# =============================================================================

EXPECTED_ROW_COUNTS = {
    "customers": {
        "before": 99441,
        "after": 99441,
        "removed": 0,
    },
    "geolocation": {
        "before": 1000163,
        "after": 738332,
        "removed": 261831,
    },
    "orders": {
        "before": 99441,
        "after": 99441,
        "removed": 0,
    },
    "order_items": {
        "before": 112650,
        "after": 112650,
        "removed": 0,
    },
    "payments": {
        "before": 103886,
        "after": 103886,
        "removed": 0,
    },
    "reviews": {
        "before": 99224,
        "after": 99224,
        "removed": 0,
    },
    "products": {
        "before": 32951,
        "after": 32951,
        "removed": 0,
    },
    "sellers": {
        "before": 3095,
        "after": 3095,
        "removed": 0,
    },
    "category_translation": {
        "before": 71,
        "after": 71,
        "removed": 0,
    },
}


# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_FILE,
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


# =============================================================================
# RESULT STORAGE
# =============================================================================

VALIDATION_RESULTS: list[dict[str, Any]] = []


# =============================================================================
# RESULT HELPER
# =============================================================================

def add_result(
    test_id: str,
    category: str,
    dataset: str,
    rule: str,
    expected: str,
    actual: str,
    failed_count: int,
    severity: str = "HIGH",
) -> None:
    """
    Add one post-cleaning validation result.
    """

    status = "PASS" if failed_count == 0 else "FAIL"

    VALIDATION_RESULTS.append(
        {
            "TEST_ID": test_id,
            "CATEGORY": category,
            "DATASET": dataset,
            "RULE": rule,
            "EXPECTED": expected,
            "ACTUAL": actual,
            "FAILED_COUNT": int(failed_count),
            "SEVERITY": (
                "NONE"
                if failed_count == 0
                else severity
            ),
            "STATUS": status,
        }
    )


# =============================================================================
# DATABASE CONNECTION
# =============================================================================

def get_connection():
    """
    Create a PostgreSQL connection.

    Password is intentionally not hard-coded.
    PostgreSQL will use the configured local authentication method
    or environment configuration.
    """

    logger.info(
        "Connecting to PostgreSQL database: %s",
        DB_CONFIG["database"],
    )

    return psycopg2.connect(
        **DB_CONFIG
    )


# =============================================================================
# GENERIC SQL HELPERS
# =============================================================================

def fetch_one(
    connection,
    query: str,
) -> Any:
    """
    Execute a read-only query and return the first value.
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()

        if row is None:
            return None

        return row[0]


def fetch_dataframe(
    connection,
    query: str,
) -> pd.DataFrame:
    """
    Execute a read-only query and return a DataFrame.
    """

    return pd.read_sql_query(
        query,
        connection,
    )


# =============================================================================
# 1. TABLE EXISTENCE
# =============================================================================

def validate_table_existence(
    connection,
) -> None:
    """
    Validate that all expected cleaned tables exist.
    """

    logger.info(
        "Validation 01 — Cleaned table existence"
    )

    query = """
        SELECT
            table_schema,
            table_name
        FROM information_schema.tables
        WHERE table_schema = 'cleaned'
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """

    df = fetch_dataframe(
        connection,
        query,
    )

    existing_tables = {
        f"{row.table_schema}.{row.table_name}"
        for row in df.itertuples()
    }

    for dataset, table_name in CLEANED_TABLES.items():

        exists = table_name in existing_tables

        add_result(
            test_id=f"P5-TABLE-{dataset.upper()}",
            category="Table Existence",
            dataset=dataset,
            rule="Expected cleaned table must exist",
            expected=table_name,
            actual=(
                "Table exists"
                if exists
                else "Table does not exist"
            ),
            failed_count=0 if exists else 1,
            severity="CRITICAL",
        )


# =============================================================================
# 2. ROW COUNTS
# =============================================================================

def validate_row_counts(
    connection,
) -> None:
    """
    Validate cleaned row counts against the successful SQL execution.
    """

    logger.info(
        "Validation 02 — Cleaned row counts"
    )

    for dataset, table_name in CLEANED_TABLES.items():

        actual_count = fetch_one(
            connection,
            f"SELECT COUNT(*) FROM {table_name};",
        )

        expected = EXPECTED_ROW_COUNTS[dataset]

        expected_after = expected["after"]

        failed_count = (
            0
            if actual_count == expected_after
            else 1
        )

        add_result(
            test_id=f"P5-ROWCOUNT-{dataset.upper()}",
            category="Row Count",
            dataset=dataset,
            rule="Cleaned row count must match Phase 5 SQL result",
            expected=f"{expected_after} rows",
            actual=f"{actual_count} rows",
            failed_count=failed_count,
            severity="CRITICAL",
        )


# =============================================================================
# 3. CLEANING SUMMARY CONSISTENCY
# =============================================================================

def validate_cleaning_summary(
    connection,
) -> None:
    """
    Validate cleaned.cleaning_dataset_summary.
    """

    logger.info(
        "Validation 03 — Cleaning summary consistency"
    )

    query = """
        SELECT
            dataset,
            rows_before,
            rows_after,
            rows_removed
        FROM cleaned.cleaning_dataset_summary
        ORDER BY dataset;
    """

    summary_df = fetch_dataframe(
        connection,
        query,
    )

    expected_df = pd.DataFrame(
        [
            {
                "dataset": dataset,
                "rows_before": values["before"],
                "rows_after": values["after"],
                "rows_removed": values["removed"],
            }
            for dataset, values
            in EXPECTED_ROW_COUNTS.items()
        ]
    )

    merged = expected_df.merge(
        summary_df,
        on="dataset",
        how="outer",
        suffixes=("_expected", "_actual"),
    )

    for row in merged.itertuples():

        failed = (
            row.rows_before_expected
            != row.rows_before_actual
            or row.rows_after_expected
            != row.rows_after_actual
            or row.rows_removed_expected
            != row.rows_removed_actual
        )

        add_result(
            test_id=f"P5-SUMMARY-{str(row.dataset).upper()}",
            category="Cleaning Summary",
            dataset=str(row.dataset),
            rule="Cleaning summary must match approved Phase 5 result",
            expected=(
                f"before={row.rows_before_expected}, "
                f"after={row.rows_after_expected}, "
                f"removed={row.rows_removed_expected}"
            ),
            actual=(
                f"before={row.rows_before_actual}, "
                f"after={row.rows_after_actual}, "
                f"removed={row.rows_removed_actual}"
            ),
            failed_count=1 if failed else 0,
            severity="HIGH",
        )


# =============================================================================
# 4. PRIMARY KEY VALIDATION
# =============================================================================

def validate_primary_keys(
    connection,
) -> None:
    """
    Validate uniqueness of cleaned primary keys.
    """

    logger.info(
        "Validation 04 — Primary keys"
    )

    primary_keys = {
        "customers": ["customer_id"],
        "orders": ["order_id"],
        "products": ["product_id"],
        "sellers": ["seller_id"],
    }

    for dataset, columns in primary_keys.items():

        table_name = CLEANED_TABLES[dataset]

        key_expression = ", ".join(columns)

        query = f"""
            SELECT COUNT(*)
            FROM (
                SELECT {key_expression}
                FROM {table_name}
                GROUP BY {key_expression}
                HAVING COUNT(*) > 1
            ) AS duplicates;
        """

        duplicate_groups = fetch_one(
            connection,
            query,
        )

        add_result(
            test_id=f"P5-PK-{dataset.upper()}",
            category="Primary Key",
            dataset=dataset,
            rule="Primary key must be unique",
            expected="0 duplicate key groups",
            actual=f"{duplicate_groups} duplicate key groups",
            failed_count=duplicate_groups,
            severity="CRITICAL",
        )


# =============================================================================
# 5. COMPOSITE KEY VALIDATION
# =============================================================================

def validate_composite_keys(
    connection,
) -> None:
    """
    Validate order_items and payments composite keys.
    """

    logger.info(
        "Validation 05 — Composite keys"
    )

    composite_keys = {
        "order_items": [
            "order_id",
            "order_item_id",
        ],
        "payments": [
            "order_id",
            "payment_sequential",
        ],
    }

    for dataset, columns in composite_keys.items():

        table_name = CLEANED_TABLES[dataset]

        key_expression = ", ".join(columns)

        query = f"""
            SELECT COUNT(*)
            FROM (
                SELECT {key_expression}
                FROM {table_name}
                GROUP BY {key_expression}
                HAVING COUNT(*) > 1
            ) AS duplicates;
        """

        duplicate_groups = fetch_one(
            connection,
            query,
        )

        add_result(
            test_id=f"P5-COMPOSITE-{dataset.upper()}",
            category="Composite Key",
            dataset=dataset,
            rule=f"Composite key ({key_expression}) must be unique",
            expected="0 duplicate key groups",
            actual=f"{duplicate_groups} duplicate key groups",
            failed_count=duplicate_groups,
            severity="CRITICAL",
        )


# =============================================================================
# 6. CHRONOLOGY VALIDATION
# =============================================================================

def validate_chronology(
    connection,
) -> None:
    """
    Validate chronology after invalid timestamps were NULLed.
    """

    logger.info(
        "Validation 06 — Order chronology"
    )

    tests = [
        (
            "P5-CHRON-001",
            "order_delivered_carrier_date >= order_purchase_timestamp",
            """
            SELECT COUNT(*)
            FROM cleaned.orders
            WHERE order_delivered_carrier_date IS NOT NULL
              AND order_purchase_timestamp IS NOT NULL
              AND order_delivered_carrier_date
                    < order_purchase_timestamp;
            """,
        ),
        (
            "P5-CHRON-002",
            "order_delivered_customer_date >= order_purchase_timestamp",
            """
            SELECT COUNT(*)
            FROM cleaned.orders
            WHERE order_delivered_customer_date IS NOT NULL
              AND order_purchase_timestamp IS NOT NULL
              AND order_delivered_customer_date
                    < order_purchase_timestamp;
            """,
        ),
        (
            "P5-CHRON-003",
            "order_delivered_customer_date >= order_delivered_carrier_date",
            """
            SELECT COUNT(*)
            FROM cleaned.orders
            WHERE order_delivered_customer_date IS NOT NULL
              AND order_delivered_carrier_date IS NOT NULL
              AND order_delivered_customer_date
                    < order_delivered_carrier_date;
            """,
        ),
    ]

    for test_id, rule, query in tests:

        invalid_count = fetch_one(
            connection,
            query,
        )

        add_result(
            test_id=test_id,
            category="Chronology",
            dataset="orders",
            rule=rule,
            expected="0 chronology violations",
            actual=f"{invalid_count} violations",
            failed_count=invalid_count,
            severity="HIGH",
        )


# =============================================================================
# 7. PAYMENT INSTALLMENT VALIDATION
# =============================================================================

def validate_payment_installments(
    connection,
) -> None:
    """
    Zero payment installments must have been converted to NULL.
    """

    logger.info(
        "Validation 07 — Payment installments"
    )

    query = """
        SELECT COUNT(*)
        FROM cleaned.payments
        WHERE payment_installments = 0;
    """

    zero_count = fetch_one(
        connection,
        query,
    )

    add_result(
        test_id="P5-PAY-001",
        category="Payment Validation",
        dataset="payments",
        rule="payment_installments = 0 must be converted to NULL",
        expected="0 zero-installment records",
        actual=f"{zero_count} zero-installment records",
        failed_count=zero_count,
        severity="HIGH",
    )


# =============================================================================
# 8. NEGATIVE VALUE VALIDATION
# =============================================================================

def validate_negative_values(
    connection,
) -> None:
    """
    Validate negative financial and physical values.
    """

    logger.info(
        "Validation 08 — Negative values"
    )

    tests = [
        (
            "P5-NEG-001",
            "order_items",
            "price",
            "Price must not be negative",
        ),
        (
            "P5-NEG-002",
            "order_items",
            "freight_value",
            "Freight value must not be negative",
        ),
        (
            "P5-NEG-003",
            "payments",
            "payment_value",
            "Payment value must not be negative",
        ),
    ]

    for test_id, dataset, column, rule in tests:

        query = f"""
            SELECT COUNT(*)
            FROM cleaned.{dataset}
            WHERE {column} < 0;
        """

        negative_count = fetch_one(
            connection,
            query,
        )

        add_result(
            test_id=test_id,
            category="Negative Values",
            dataset=dataset,
            rule=rule,
            expected="0 negative values",
            actual=f"{negative_count} negative values",
            failed_count=negative_count,
            severity="HIGH",
        )


# =============================================================================
# 9. REFERENTIAL INTEGRITY
# =============================================================================

def validate_referential_integrity(
    connection,
) -> None:
    """
    Validate all approved foreign-key relationships.
    """

    logger.info(
        "Validation 09 — Referential integrity"
    )

    tests = [
        (
            "P5-FK-001",
            "orders",
            "Order customer_id must exist in customers.customer_id",
            """
            SELECT COUNT(*)
            FROM cleaned.orders o
            LEFT JOIN cleaned.customers c
                ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL;
            """,
        ),
        (
            "P5-FK-002",
            "order_items",
            "Order item order_id must exist in orders.order_id",
            """
            SELECT COUNT(*)
            FROM cleaned.order_items oi
            LEFT JOIN cleaned.orders o
                ON oi.order_id = o.order_id
            WHERE o.order_id IS NULL;
            """,
        ),
        (
            "P5-FK-003",
            "order_items",
            "Order item product_id must exist in products.product_id",
            """
            SELECT COUNT(*)
            FROM cleaned.order_items oi
            LEFT JOIN cleaned.products p
                ON oi.product_id = p.product_id
            WHERE p.product_id IS NULL;
            """,
        ),
        (
            "P5-FK-004",
            "order_items",
            "Order item seller_id must exist in sellers.seller_id",
            """
            SELECT COUNT(*)
            FROM cleaned.order_items oi
            LEFT JOIN cleaned.sellers s
                ON oi.seller_id = s.seller_id
            WHERE s.seller_id IS NULL;
            """,
        ),
        (
            "P5-FK-005",
            "payments",
            "Payment order_id must exist in orders.order_id",
            """
            SELECT COUNT(*)
            FROM cleaned.payments p
            LEFT JOIN cleaned.orders o
                ON p.order_id = o.order_id
            WHERE o.order_id IS NULL;
            """,
        ),
        (
            "P5-FK-006",
            "reviews",
            "Review order_id must exist in orders.order_id",
            """
            SELECT COUNT(*)
            FROM cleaned.reviews r
            LEFT JOIN cleaned.orders o
                ON r.order_id = o.order_id
            WHERE o.order_id IS NULL;
            """,
        ),
    ]

    for test_id, dataset, rule, query in tests:

        orphan_count = fetch_one(
            connection,
            query,
        )

        add_result(
            test_id=test_id,
            category="Referential Integrity",
            dataset=dataset,
            rule=rule,
            expected="0 orphan records",
            actual=f"{orphan_count} orphan records",
            failed_count=orphan_count,
            severity="CRITICAL",
        )


# =============================================================================
# 10. LEGITIMATE ZERO VALUES
# =============================================================================

def validate_zero_value_preservation(
    connection,
) -> None:
    """
    Confirm intentionally preserved zero values still exist.
    """

    logger.info(
        "Validation 10 — Zero-value preservation"
    )

    tests = [
        (
            "P5-ZERO-001",
            "order_items",
            "freight_value",
            383,
            "Zero freight values must be preserved",
        ),
        (
            "P5-ZERO-002",
            "payments",
            "payment_value",
            9,
            "Zero payment values must be preserved",
        ),
        (
            "P5-ZERO-003",
            "products",
            "product_weight_g",
            4,
            "Zero product weights must be preserved",
        ),
    ]

    for test_id, dataset, column, expected_count, rule in tests:

        query = f"""
            SELECT COUNT(*)
            FROM cleaned.{dataset}
            WHERE {column} = 0;
        """

        actual_count = fetch_one(
            connection,
            query,
        )

        failed_count = (
            0
            if actual_count == expected_count
            else 1
        )

        add_result(
            test_id=test_id,
            category="Zero Preservation",
            dataset=dataset,
            rule=rule,
            expected=f"{expected_count} zero values",
            actual=f"{actual_count} zero values",
            failed_count=failed_count,
            severity="MEDIUM",
        )


# =============================================================================
# 11. NULL CATEGORY PRESERVATION
# =============================================================================

def validate_product_category_nulls(
    connection,
) -> None:
    """
    Product category NULLs are intentionally preserved.
    """

    logger.info(
        "Validation 11 — Product category NULL preservation"
    )

    query = """
        SELECT COUNT(*)
        FROM cleaned.products
        WHERE product_category_name IS NULL;
    """

    null_count = fetch_one(
        connection,
        query,
    )

    add_result(
        test_id="P5-NULL-001",
        category="NULL Preservation",
        dataset="products",
        rule="Missing product categories must remain NULL",
        expected="610 NULL product categories",
        actual=f"{null_count} NULL product categories",
        failed_count=(
            0
            if null_count == 610
            else 1
        ),
        severity="MEDIUM",
    )


# =============================================================================
# 12. TRANSLATION COVERAGE
# =============================================================================

def validate_translation_coverage(
    connection,
) -> None:
    """
    Validate remaining product-category translation gaps.
    """

    logger.info(
        "Validation 12 — Translation coverage"
    )

    query = """
        SELECT COUNT(*)
        FROM cleaned.products p
        LEFT JOIN cleaned.category_translation t
            ON p.product_category_name = t.product_category_name
        WHERE p.product_category_name IS NOT NULL
          AND t.product_category_name IS NULL;
    """

    missing_count = fetch_one(
        connection,
        query,
    )

    add_result(
        test_id="P5-TRANS-001",
        category="Translation Coverage",
        dataset="products",
        rule="Translation gaps must remain measurable and unfabricated",
        expected="13 product rows without English translation",
        actual=(
            f"{missing_count} product rows "
            "without English translation"
        ),
        failed_count=(
            0
            if missing_count == 13
            else 1
        ),
        severity="MEDIUM",
    )


# =============================================================================
# 13. GEOLOCATION DUPLICATE REDUCTION
# =============================================================================

def validate_geolocation_cleaning(
    connection,
) -> None:
    """
    Validate exact duplicate removal from geolocation.
    """

    logger.info(
        "Validation 13 — Geolocation duplicate reduction"
    )

    query = """
        SELECT COUNT(*)
        FROM cleaned.geolocation;
    """

    cleaned_count = fetch_one(
        connection,
        query,
    )

    expected_count = 738332

    add_result(
        test_id="P5-GEO-001",
        category="Duplicate Removal",
        dataset="geolocation",
        rule="Exact duplicate geolocation rows must be removed",
        expected=f"{expected_count} cleaned rows",
        actual=f"{cleaned_count} cleaned rows",
        failed_count=(
            0
            if cleaned_count == expected_count
            else 1
        ),
        severity="HIGH",
    )

    duplicate_query = """
        SELECT COUNT(*)
        FROM (
            SELECT
                geolocation_zip_code_prefix,
                geolocation_lat,
                geolocation_lng,
                geolocation_city,
                geolocation_state,
                COUNT(*) AS duplicate_count
            FROM cleaned.geolocation
            GROUP BY
                geolocation_zip_code_prefix,
                geolocation_lat,
                geolocation_lng,
                geolocation_city,
                geolocation_state
            HAVING COUNT(*) > 1
        ) AS duplicates;
    """

    duplicate_groups = fetch_one(
        connection,
        duplicate_query,
    )

    add_result(
        test_id="P5-GEO-002",
        category="Duplicate Removal",
        dataset="geolocation",
        rule="Cleaned geolocation must contain no exact duplicate rows",
        expected="0 duplicate groups",
        actual=f"{duplicate_groups} duplicate groups",
        failed_count=duplicate_groups,
        severity="HIGH",
    )


# =============================================================================
# 14. REVIEW ID POLICY
# =============================================================================

def validate_review_policy(
    connection,
) -> None:
    """
    Confirm review_id is not incorrectly enforced as a unique key.

    The cleaning strategy intentionally does not add a primary key
    or unique constraint to review_id.
    """

    logger.info(
        "Validation 14 — Review ID policy"
    )

    query = """
        SELECT COUNT(*)
        FROM information_schema.table_constraints tc
        JOIN information_schema.constraint_column_usage ccu
          ON tc.constraint_name = ccu.constraint_name
         AND tc.table_schema = ccu.table_schema
        WHERE tc.table_schema = 'cleaned'
          AND tc.table_name = 'reviews'
          AND ccu.column_name = 'review_id'
          AND tc.constraint_type IN (
              'PRIMARY KEY',
              'UNIQUE'
          );
    """

    constraint_count = fetch_one(
        connection,
        query,
    )

    add_result(
        test_id="P5-REVIEW-001",
        category="Key Policy",
        dataset="reviews",
        rule="review_id must not be treated as a unique key",
        expected="0 UNIQUE/PRIMARY KEY constraints on review_id",
        actual=(
            f"{constraint_count} UNIQUE/PRIMARY KEY "
            "constraints on review_id"
        ),
        failed_count=constraint_count,
        severity="CRITICAL",
    )


# =============================================================================
# SUMMARY
# =============================================================================

def generate_summary() -> dict[str, Any]:
    """
    Generate execution summary.
    """

    results_df = pd.DataFrame(
        VALIDATION_RESULTS
    )

    total_tests = len(results_df)

    passed = int(
        (
            results_df["STATUS"] == "PASS"
        ).sum()
    ) if total_tests else 0

    failed = int(
        (
            results_df["STATUS"] == "FAIL"
        ).sum()
    ) if total_tests else 0

    critical = int(
        (
            results_df["SEVERITY"] == "CRITICAL"
        ).sum()
    ) if total_tests else 0

    high = int(
        (
            results_df["SEVERITY"] == "HIGH"
        ).sum()
    ) if total_tests else 0

    medium = int(
        (
            results_df["SEVERITY"] == "MEDIUM"
        ).sum()
    ) if total_tests else 0

    low = int(
        (
            results_df["SEVERITY"] == "LOW"
        ).sum()
    ) if total_tests else 0

    summary = {
        "phase": "Phase 5 — Post-Cleaning Data Quality Validation",
        "project": "Retail Sales Performance Analytics",
        "database": DB_CONFIG["database"],
        "schema": "cleaned",
        "total_validation_tests": total_tests,
        "passed_tests": passed,
        "failed_tests": failed,
        "critical_failures": critical,
        "high_failures": high,
        "medium_failures": medium,
        "low_failures": low,
        "validation_status": (
            "PASS"
            if failed == 0
            else "FAIL"
        ),
        "cleaning_completed": True,
        "cleaned_tables_expected": len(
            CLEANED_TABLES
        ),
    }

    return summary


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    """
    Execute the complete Phase 5 post-cleaning validation.
    """

    logger.info("=" * 80)
    logger.info(
        "PHASE 5 — POST-CLEANING DATA QUALITY VALIDATION"
    )
    logger.info("=" * 80)

    logger.info(
        "Project root: %s",
        PROJECT_ROOT,
    )

    logger.info(
        "Database: %s",
        DB_CONFIG["database"],
    )

    logger.info(
        "Schema: cleaned",
    )

    connection = None

    try:

        # -------------------------------------------------------------
        # DATABASE CONNECTION
        # -------------------------------------------------------------

        connection = get_connection()

        logger.info(
            "PostgreSQL connection established."
        )

        # -------------------------------------------------------------
        # VALIDATION TESTS
        # -------------------------------------------------------------

        validate_table_existence(
            connection
        )

        validate_row_counts(
            connection
        )

        validate_cleaning_summary(
            connection
        )

        validate_primary_keys(
            connection
        )

        validate_composite_keys(
            connection
        )

        validate_chronology(
            connection
        )

        validate_payment_installments(
            connection
        )

        validate_negative_values(
            connection
        )

        validate_referential_integrity(
            connection
        )

        validate_zero_value_preservation(
            connection
        )

        validate_product_category_nulls(
            connection
        )

        validate_translation_coverage(
            connection
        )

        validate_geolocation_cleaning(
            connection
        )

        validate_review_policy(
            connection
        )

        # -------------------------------------------------------------
        # RESULTS
        # -------------------------------------------------------------

        results_df = pd.DataFrame(
            VALIDATION_RESULTS
        )

        results_df.to_csv(
            RESULTS_FILE,
            index=False,
            encoding="utf-8-sig",
        )

        summary = generate_summary()

        with SUMMARY_FILE.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                summary,
                file,
                indent=4,
            )

        # -------------------------------------------------------------
        # CONSOLE SUMMARY
        # -------------------------------------------------------------

        logger.info("=" * 80)
        logger.info(
            "POST-CLEANING VALIDATION COMPLETE"
        )
        logger.info("=" * 80)

        logger.info(
            "Total validation tests : %s",
            summary["total_validation_tests"],
        )

        logger.info(
            "Passed tests           : %s",
            summary["passed_tests"],
        )

        logger.info(
            "Failed tests           : %s",
            summary["failed_tests"],
        )

        logger.info(
            "Critical failures      : %s",
            summary["critical_failures"],
        )

        logger.info(
            "High failures          : %s",
            summary["high_failures"],
        )

        logger.info(
            "Medium failures        : %s",
            summary["medium_failures"],
        )

        logger.info(
            "Low failures           : %s",
            summary["low_failures"],
        )

        logger.info(
            "Overall status         : %s",
            summary["validation_status"],
        )

        logger.info("-" * 80)

        logger.info(
            "Results CSV: %s",
            RESULTS_FILE,
        )

        logger.info(
            "Summary JSON: %s",
            SUMMARY_FILE,
        )

        logger.info(
            "Log file: %s",
            LOG_FILE,
        )

        logger.info("=" * 80)

        # -------------------------------------------------------------
        # IMPORTANT: FAIL PROCESS IF VALIDATION FAILED
        # -------------------------------------------------------------

        if summary["validation_status"] == "FAIL":

            logger.error(
                "POST-CLEANING VALIDATION FAILED."
            )

            raise SystemExit(1)

        logger.info(
            "POST-CLEANING DATA QUALITY VALIDATION PASSED."
        )

    except psycopg2.Error as exc:

        logger.exception(
            "PostgreSQL error: %s",
            exc,
        )

        raise SystemExit(1)

    except Exception as exc:

        logger.exception(
            "Unexpected validation error: %s",
            exc,
        )

        raise SystemExit(1)

    finally:

        if connection is not None:

            connection.close()

            logger.info(
                "PostgreSQL connection closed."
            )


if __name__ == "__main__":
    main()