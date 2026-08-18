/*
===============================================================================
PHASE 4 — DATA QUALITY ASSESSMENT
STEP 02 — SQL DATA VALIDATION
PROJECT: Retail Sales Performance Analytics
SOURCE: Olist Brazilian E-Commerce Dataset

PURPOSE
-------
Provide an independent SQL validation layer for Phase 4 Data Quality
Assessment.

This script identifies and quantifies data-quality issues.

IMPORTANT
---------
This script is READ-ONLY.

It does NOT:
    - UPDATE source tables
    - DELETE records
    - INSERT into business/source tables
    - modify raw data
    - clean data

Cleaning belongs to Phase 5.

EXPECTED TABLES
---------------
customers
geolocation
orders
order_items
payments
reviews
products
sellers
category_translation

OUTPUT
------
The script creates a temporary table named:

    dq_results

The temporary table contains standardized validation results:

    TEST_ID
    DATASET
    COLUMN_NAME
    QUALITY_DIMENSION
    RULE
    EXPECTED
    ACTUAL
    FAILED_COUNT
    FAILURE_RATE
    SEVERITY
    STATUS

===============================================================================
*/


/*
===============================================================================
SECTION 00 — TEMPORARY RESULT TABLE
===============================================================================
*/

DROP TABLE IF EXISTS dq_results;

CREATE TEMP TABLE dq_results (
    test_id            VARCHAR(50),
    dataset            VARCHAR(50),
    column_name        VARCHAR(150),
    quality_dimension  VARCHAR(100),
    rule               TEXT,
    expected           TEXT,
    actual             TEXT,
    failed_count       BIGINT,
    failure_rate       NUMERIC(10,4),
    severity           VARCHAR(20),
    status              VARCHAR(10)
);


/*
===============================================================================
SECTION 01 — DATASET ROW COUNTS
===============================================================================

Purpose:
    Verify that all expected datasets contain records.

===============================================================================
*/

INSERT INTO dq_results
SELECT
    'DQ-ROW-001',
    'customers',
    '__DATASET__',
    'Completeness',
    'Customers dataset must contain records',
    '> 0 rows',
    'Rows = ' || COUNT(*)::TEXT,
    CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END,
    CASE
        WHEN COUNT(*) = 0 THEN 100.0000
        ELSE 0.0000
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'CRITICAL'
        ELSE 'NONE'
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'FAIL'
        ELSE 'PASS'
    END
FROM customers;


INSERT INTO dq_results
SELECT
    'DQ-ROW-002',
    'geolocation',
    '__DATASET__',
    'Completeness',
    'Geolocation dataset must contain records',
    '> 0 rows',
    'Rows = ' || COUNT(*)::TEXT,
    CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END,
    CASE
        WHEN COUNT(*) = 0 THEN 100.0000
        ELSE 0.0000
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'CRITICAL'
        ELSE 'NONE'
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'FAIL'
        ELSE 'PASS'
    END
FROM geolocation;


INSERT INTO dq_results
SELECT
    'DQ-ROW-003',
    'orders',
    '__DATASET__',
    'Completeness',
    'Orders dataset must contain records',
    '> 0 rows',
    'Rows = ' || COUNT(*)::TEXT,
    CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END,
    CASE
        WHEN COUNT(*) = 0 THEN 100.0000
        ELSE 0.0000
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'CRITICAL'
        ELSE 'NONE'
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'FAIL'
        ELSE 'PASS'
    END
FROM orders;


INSERT INTO dq_results
SELECT
    'DQ-ROW-004',
    'order_items',
    '__DATASET__',
    'Completeness',
    'Order Items dataset must contain records',
    '> 0 rows',
    'Rows = ' || COUNT(*)::TEXT,
    CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END,
    CASE
        WHEN COUNT(*) = 0 THEN 100.0000
        ELSE 0.0000
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'CRITICAL'
        ELSE 'NONE'
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'FAIL'
        ELSE 'PASS'
    END
FROM order_items;


INSERT INTO dq_results
SELECT
    'DQ-ROW-005',
    'payments',
    '__DATASET__',
    'Completeness',
    'Payments dataset must contain records',
    '> 0 rows',
    'Rows = ' || COUNT(*)::TEXT,
    CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END,
    CASE
        WHEN COUNT(*) = 0 THEN 100.0000
        ELSE 0.0000
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'CRITICAL'
        ELSE 'NONE'
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'FAIL'
        ELSE 'PASS'
    END
FROM payments;


INSERT INTO dq_results
SELECT
    'DQ-ROW-006',
    'reviews',
    '__DATASET__',
    'Completeness',
    'Reviews dataset must contain records',
    '> 0 rows',
    'Rows = ' || COUNT(*)::TEXT,
    CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END,
    CASE
        WHEN COUNT(*) = 0 THEN 100.0000
        ELSE 0.0000
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'CRITICAL'
        ELSE 'NONE'
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'FAIL'
        ELSE 'PASS'
    END
FROM reviews;


INSERT INTO dq_results
SELECT
    'DQ-ROW-007',
    'products',
    '__DATASET__',
    'Completeness',
    'Products dataset must contain records',
    '> 0 rows',
    'Rows = ' || COUNT(*)::TEXT,
    CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END,
    CASE
        WHEN COUNT(*) = 0 THEN 100.0000
        ELSE 0.0000
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'CRITICAL'
        ELSE 'NONE'
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'FAIL'
        ELSE 'PASS'
    END
FROM products;


INSERT INTO dq_results
SELECT
    'DQ-ROW-008',
    'sellers',
    '__DATASET__',
    'Completeness',
    'Sellers dataset must contain records',
    '> 0 rows',
    'Rows = ' || COUNT(*)::TEXT,
    CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END,
    CASE
        WHEN COUNT(*) = 0 THEN 100.0000
        ELSE 0.0000
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'CRITICAL'
        ELSE 'NONE'
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'FAIL'
        ELSE 'PASS'
    END
FROM sellers;


INSERT INTO dq_results
SELECT
    'DQ-ROW-009',
    'category_translation',
    '__DATASET__',
    'Completeness',
    'Category translation dataset must contain records',
    '> 0 rows',
    'Rows = ' || COUNT(*)::TEXT,
    CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END,
    CASE
        WHEN COUNT(*) = 0 THEN 100.0000
        ELSE 0.0000
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'CRITICAL'
        ELSE 'NONE'
    END,
    CASE
        WHEN COUNT(*) = 0 THEN 'FAIL'
        ELSE 'PASS'
    END
FROM category_translation;


/*
===============================================================================
SECTION 02 — NULL CHECKS
===============================================================================
*/


-- CUSTOMERS: customer_id NULL

INSERT INTO dq_results
SELECT
    'DQ-CUST-001',
    'customers',
    'customer_id',
    'Completeness',
    'customer_id must not be NULL',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM customers), 0), 4),
    'CRITICAL',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM customers
WHERE customer_id IS NULL;


-- CUSTOMERS: customer_state NULL

INSERT INTO dq_results
SELECT
    'DQ-CUST-002',
    'customers',
    'customer_state',
    'Completeness',
    'customer_state should not be NULL',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM customers), 0), 4),
    'MEDIUM',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM customers
WHERE customer_state IS NULL;


-- ORDERS: order_id NULL

INSERT INTO dq_results
SELECT
    'DQ-ORD-001',
    'orders',
    'order_id',
    'Completeness',
    'order_id must not be NULL',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM orders), 0), 4),
    'CRITICAL',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM orders
WHERE order_id IS NULL;


-- ORDER ITEMS: order_id NULL

INSERT INTO dq_results
SELECT
    'DQ-ITEM-001',
    'order_items',
    'order_id',
    'Completeness',
    'order_id must not be NULL',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM order_items), 0), 4),
    'CRITICAL',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM order_items
WHERE order_id IS NULL;


-- ORDER ITEMS: product_id NULL

INSERT INTO dq_results
SELECT
    'DQ-ITEM-002',
    'order_items',
    'product_id',
    'Completeness',
    'product_id must not be NULL',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM order_items), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM order_items
WHERE product_id IS NULL;


-- ORDER ITEMS: seller_id NULL

INSERT INTO dq_results
SELECT
    'DQ-ITEM-003',
    'order_items',
    'seller_id',
    'Completeness',
    'seller_id must not be NULL',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM order_items), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM order_items
WHERE seller_id IS NULL;


-- PAYMENTS: order_id NULL

INSERT INTO dq_results
SELECT
    'DQ-PAY-001',
    'payments',
    'order_id',
    'Completeness',
    'order_id must not be NULL',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM payments), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM payments
WHERE order_id IS NULL;


-- REVIEWS: review_id NULL

INSERT INTO dq_results
SELECT
    'DQ-REV-001',
    'reviews',
    'review_id',
    'Completeness',
    'review_id must not be NULL',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM reviews), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM reviews
WHERE review_id IS NULL;


-- REVIEWS: order_id NULL

INSERT INTO dq_results
SELECT
    'DQ-REV-002',
    'reviews',
    'order_id',
    'Completeness',
    'order_id must not be NULL',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM reviews), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM reviews
WHERE order_id IS NULL;


-- PRODUCTS: product_id NULL

INSERT INTO dq_results
SELECT
    'DQ-PROD-001',
    'products',
    'product_id',
    'Completeness',
    'product_id must not be NULL',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM products), 0), 4),
    'CRITICAL',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM products
WHERE product_id IS NULL;


-- PRODUCTS: category NULL

INSERT INTO dq_results
SELECT
    'DQ-PROD-002',
    'products',
    'product_category_name',
    'Completeness',
    'product_category_name should be populated',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM products), 0), 4),
    'MEDIUM',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM products
WHERE product_category_name IS NULL;


-- SELLERS: seller_id NULL

INSERT INTO dq_results
SELECT
    'DQ-SELL-001',
    'sellers',
    'seller_id',
    'Completeness',
    'seller_id must not be NULL',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM sellers), 0), 4),
    'CRITICAL',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM sellers
WHERE seller_id IS NULL;


-- SELLERS: seller_state NULL

INSERT INTO dq_results
SELECT
    'DQ-SELL-002',
    'sellers',
    'seller_state',
    'Completeness',
    'seller_state should not be NULL',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM sellers), 0), 4),
    'MEDIUM',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM sellers
WHERE seller_state IS NULL;


-- TRANSLATION: category NULL

INSERT INTO dq_results
SELECT
    'DQ-TRANS-001',
    'category_translation',
    'product_category_name',
    'Completeness',
    'product_category_name must not be NULL',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM category_translation), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM category_translation
WHERE product_category_name IS NULL;


-- TRANSLATION: English category NULL

INSERT INTO dq_results
SELECT
    'DQ-TRANS-002',
    'category_translation',
    'product_category_name_english',
    'Completeness',
    'English category must not be NULL',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM category_translation), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM category_translation
WHERE product_category_name_english IS NULL;


/*
===============================================================================
SECTION 03 — PRIMARY KEY UNIQUENESS
===============================================================================
*/


-- CUSTOMERS

INSERT INTO dq_results
SELECT
    'DQ-CUST-003',
    'customers',
    'customer_id',
    'Uniqueness',
    'customer_id must be unique',
    '0 duplicate key groups',
    'Duplicate key groups = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM customers), 0), 4),
    'CRITICAL',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM (
    SELECT customer_id
    FROM customers
    GROUP BY customer_id
    HAVING COUNT(*) > 1
) d;


-- ORDERS

INSERT INTO dq_results
SELECT
    'DQ-ORD-002',
    'orders',
    'order_id',
    'Uniqueness',
    'order_id must be unique',
    '0 duplicate key groups',
    'Duplicate key groups = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM orders), 0), 4),
    'CRITICAL',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM (
    SELECT order_id
    FROM orders
    GROUP BY order_id
    HAVING COUNT(*) > 1
) d;


-- ORDER ITEMS COMPOSITE KEY

INSERT INTO dq_results
SELECT
    'DQ-ITEM-004',
    'order_items',
    'order_id, order_item_id',
    'Uniqueness',
    '(order_id, order_item_id) must be unique',
    '0 duplicate key groups',
    'Duplicate key groups = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(
        COUNT(*) * 100.0
        / NULLIF((SELECT COUNT(*) FROM order_items), 0),
        4
    ),
    'CRITICAL',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM (
    SELECT order_id, order_item_id
    FROM order_items
    GROUP BY order_id, order_item_id
    HAVING COUNT(*) > 1
) d;


-- PAYMENTS COMPOSITE KEY

INSERT INTO dq_results
SELECT
    'DQ-PAY-002',
    'payments',
    'order_id, payment_sequential',
    'Uniqueness',
    '(order_id, payment_sequential) must be unique',
    '0 duplicate key groups',
    'Duplicate key groups = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(
        COUNT(*) * 100.0
        / NULLIF((SELECT COUNT(*) FROM payments), 0),
        4
    ),
    'CRITICAL',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM (
    SELECT order_id, payment_sequential
    FROM payments
    GROUP BY order_id, payment_sequential
    HAVING COUNT(*) > 1
) d;


-- PRODUCTS

INSERT INTO dq_results
SELECT
    'DQ-PROD-003',
    'products',
    'product_id',
    'Uniqueness',
    'product_id must be unique',
    '0 duplicate key groups',
    'Duplicate key groups = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM products), 0), 4),
    'CRITICAL',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM (
    SELECT product_id
    FROM products
    GROUP BY product_id
    HAVING COUNT(*) > 1
) d;


-- SELLERS

INSERT INTO dq_results
SELECT
    'DQ-SELL-003',
    'sellers',
    'seller_id',
    'Uniqueness',
    'seller_id must be unique',
    '0 duplicate key groups',
    'Duplicate key groups = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM sellers), 0), 4),
    'CRITICAL',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM (
    SELECT seller_id
    FROM sellers
    GROUP BY seller_id
    HAVING COUNT(*) > 1
) d;


/*
===============================================================================
SECTION 04 — DUPLICATE DETECTION
===============================================================================
*/


-- REVIEWS: review_id duplicate

INSERT INTO dq_results
SELECT
    'DQ-REV-003',
    'reviews',
    'review_id',
    'Uniqueness',
    'review_id should not have duplicate occurrences',
    '0 duplicate key groups',
    'Duplicate key groups = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM reviews), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM (
    SELECT review_id
    FROM reviews
    GROUP BY review_id
    HAVING COUNT(*) > 1
) d;


-- CATEGORY TRANSLATION duplicate

INSERT INTO dq_results
SELECT
    'DQ-TRANS-003',
    'category_translation',
    'product_category_name',
    'Uniqueness',
    'product_category_name should be unique',
    '0 duplicate key groups',
    'Duplicate key groups = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(
        COUNT(*) * 100.0
        / NULLIF((SELECT COUNT(*) FROM category_translation), 0),
        4
    ),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM (
    SELECT product_category_name
    FROM category_translation
    GROUP BY product_category_name
    HAVING COUNT(*) > 1
) d;


-- GEOLOCATION FULL-ROW DUPLICATES

INSERT INTO dq_results
SELECT
    'DQ-GEO-001',
    'geolocation',
    '__FULL_ROW__',
    'Uniqueness',
    'Exact duplicate geolocation rows should be reviewed',
    '0 duplicate rows',
    'Rows participating in duplicates = ' || COALESCE(SUM(row_count), 0)::TEXT,
    COALESCE(SUM(row_count), 0),
    ROUND(
        COALESCE(SUM(row_count), 0) * 100.0
        / NULLIF((SELECT COUNT(*) FROM geolocation), 0),
        4
    ),
    'MEDIUM',
    CASE
        WHEN COALESCE(SUM(row_count), 0) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END
FROM (
    SELECT
        geolocation_zip_code_prefix,
        geolocation_lat,
        geolocation_lng,
        geolocation_city,
        geolocation_state,
        COUNT(*) AS row_count
    FROM geolocation
    GROUP BY
        geolocation_zip_code_prefix,
        geolocation_lat,
        geolocation_lng,
        geolocation_city,
        geolocation_state
    HAVING COUNT(*) > 1
) d;


/*
===============================================================================
SECTION 05 — FOREIGN KEY VALIDATION
===============================================================================

Checks child foreign-key columns for NULL values.

Referential integrity is handled in Section 06.

===============================================================================
*/


-- Orders.customer_id

INSERT INTO dq_results
SELECT
    'DQ-FK-001',
    'orders',
    'customer_id',
    'Completeness',
    'orders.customer_id must not be NULL',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM orders), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM orders
WHERE customer_id IS NULL;


-- Order Items order_id

INSERT INTO dq_results
SELECT
    'DQ-FK-002',
    'order_items',
    'order_id',
    'Completeness',
    'order_items.order_id must not be NULL',
    '0 NULL values',
    'NULL values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM order_items), 0), 4),
    'CRITICAL',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM order_items
WHERE order_id IS NULL;


/*
===============================================================================
SECTION 06 — REFERENTIAL-INTEGRITY VALIDATION
===============================================================================
*/


-- ORDERS -> CUSTOMERS

INSERT INTO dq_results
SELECT
    'DQ-REF-001',
    'orders',
    'customer_id',
    'Referential Integrity',
    'Every orders.customer_id must exist in customers.customer_id',
    '0 orphan customer references',
    'Orphan rows = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM orders), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM orders o
WHERE o.customer_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1
      FROM customers c
      WHERE c.customer_id = o.customer_id
  );


-- ORDER ITEMS -> ORDERS

INSERT INTO dq_results
SELECT
    'DQ-REF-002',
    'order_items',
    'order_id',
    'Referential Integrity',
    'Every order_items.order_id must exist in orders.order_id',
    '0 orphan order references',
    'Orphan rows = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM order_items), 0), 4),
    'CRITICAL',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM order_items oi
WHERE oi.order_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1
      FROM orders o
      WHERE o.order_id = oi.order_id
  );


-- ORDER ITEMS -> PRODUCTS

INSERT INTO dq_results
SELECT
    'DQ-REF-003',
    'order_items',
    'product_id',
    'Referential Integrity',
    'Every order_items.product_id must exist in products.product_id',
    '0 orphan product references',
    'Orphan rows = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM order_items), 0), 4),
    'CRITICAL',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM order_items oi
WHERE oi.product_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1
      FROM products p
      WHERE p.product_id = oi.product_id
  );


-- ORDER ITEMS -> SELLERS

INSERT INTO dq_results
SELECT
    'DQ-REF-004',
    'order_items',
    'seller_id',
    'Referential Integrity',
    'Every order_items.seller_id must exist in sellers.seller_id',
    '0 orphan seller references',
    'Orphan rows = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM order_items), 0), 4),
    'CRITICAL',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM order_items oi
WHERE oi.seller_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1
      FROM sellers s
      WHERE s.seller_id = oi.seller_id
  );


-- PAYMENTS -> ORDERS

INSERT INTO dq_results
SELECT
    'DQ-REF-005',
    'payments',
    'order_id',
    'Referential Integrity',
    'Every payments.order_id must exist in orders.order_id',
    '0 orphan order references',
    'Orphan rows = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM payments), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM payments p
WHERE p.order_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1
      FROM orders o
      WHERE o.order_id = p.order_id
  );


-- REVIEWS -> ORDERS

INSERT INTO dq_results
SELECT
    'DQ-REF-006',
    'reviews',
    'order_id',
    'Referential Integrity',
    'Every reviews.order_id must exist in orders.order_id',
    '0 orphan order references',
    'Orphan rows = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM reviews), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM reviews r
WHERE r.order_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1
      FROM orders o
      WHERE o.order_id = r.order_id
  );


/*
===============================================================================
SECTION 07 — DOMAIN VALIDATION
===============================================================================
*/


-- CUSTOMERS: invalid state

INSERT INTO dq_results
SELECT
    'DQ-DOM-CUST-001',
    'customers',
    'customer_state',
    'Validity',
    'customer_state must be a valid Brazilian state code',
    'Valid Brazilian UF code',
    'Invalid values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM customers), 0), 4),
    'MEDIUM',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM customers
WHERE customer_state IS NOT NULL
  AND customer_state NOT IN (
      'AC','AL','AP','AM','BA','CE','DF','ES','GO',
      'MA','MT','MS','MG','PA','PB','PR','PE','PI',
      'RJ','RN','RS','RO','RR','SC','SP','SE','TO'
  );


-- ORDERS: invalid status

INSERT INTO dq_results
SELECT
    'DQ-DOM-ORD-001',
    'orders',
    'order_status',
    'Categorical Conformity',
    'order_status must belong to the Olist status domain',
    'delivered, shipped, canceled, invoiced, processing, unavailable, approved, created',
    'Invalid values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM orders), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM orders
WHERE order_status IS NOT NULL
  AND order_status NOT IN (
      'delivered',
      'shipped',
      'canceled',
      'invoiced',
      'processing',
      'unavailable',
      'approved',
      'created'
  );


-- PAYMENTS: invalid payment type

INSERT INTO dq_results
SELECT
    'DQ-DOM-PAY-001',
    'payments',
    'payment_type',
    'Categorical Conformity',
    'payment_type must belong to the allowed payment domain',
    'credit_card, boleto, voucher, debit_card, not_defined',
    'Invalid values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM payments), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM payments
WHERE payment_type IS NOT NULL
  AND payment_type NOT IN (
      'credit_card',
      'boleto',
      'voucher',
      'debit_card',
      'not_defined'
  );


-- REVIEWS: score range

INSERT INTO dq_results
SELECT
    'DQ-DOM-REV-001',
    'reviews',
    'review_score',
    'Validity',
    'review_score must be between 1 and 5',
    '1 <= review_score <= 5',
    'Invalid values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM reviews), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM reviews
WHERE review_score IS NOT NULL
  AND review_score NOT BETWEEN 1 AND 5;


-- SELLERS: invalid state

INSERT INTO dq_results
SELECT
    'DQ-DOM-SELL-001',
    'sellers',
    'seller_state',
    'Validity',
    'seller_state must be a valid Brazilian state code',
    'Valid Brazilian UF code',
    'Invalid values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM sellers), 0), 4),
    'MEDIUM',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM sellers
WHERE seller_state IS NOT NULL
  AND seller_state NOT IN (
      'AC','AL','AP','AM','BA','CE','DF','ES','GO',
      'MA','MT','MS','MG','PA','PB','PR','PE','PI',
      'RJ','RN','RS','RO','RR','SC','SP','SE','TO'
  );


/*
===============================================================================
SECTION 08 — NUMERIC RANGE VALIDATION
===============================================================================
*/


-- ORDER ITEMS: price <= 0

INSERT INTO dq_results
SELECT
    'DQ-RANGE-ITEM-001',
    'order_items',
    'price',
    'Validity',
    'Order item price must be greater than zero',
    '> 0',
    'Invalid values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM order_items), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM order_items
WHERE price <= 0;


-- ORDER ITEMS: freight_value < 0

INSERT INTO dq_results
SELECT
    'DQ-RANGE-ITEM-002',
    'order_items',
    'freight_value',
    'Validity',
    'freight_value must not be negative',
    '>= 0',
    'Invalid values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM order_items), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM order_items
WHERE freight_value < 0;


-- PAYMENTS: payment_value < 0

INSERT INTO dq_results
SELECT
    'DQ-RANGE-PAY-001',
    'payments',
    'payment_value',
    'Validity',
    'payment_value must not be negative',
    '>= 0',
    'Invalid values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM payments), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM payments
WHERE payment_value < 0;


-- PAYMENTS: payment_installments < 0

INSERT INTO dq_results
SELECT
    'DQ-RANGE-PAY-002',
    'payments',
    'payment_installments',
    'Validity',
    'payment_installments must not be negative',
    '>= 0',
    'Invalid values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM payments), 0), 4),
    'MEDIUM',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM payments
WHERE payment_installments < 0;


-- PRODUCTS: weight

INSERT INTO dq_results
SELECT
    'DQ-RANGE-PROD-001',
    'products',
    'product_weight_g',
    'Validity',
    'product_weight_g must not be negative',
    '>= 0',
    'Invalid values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM products), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM products
WHERE product_weight_g < 0;


-- PRODUCTS: length

INSERT INTO dq_results
SELECT
    'DQ-RANGE-PROD-002',
    'products',
    'product_length_cm',
    'Validity',
    'product_length_cm must not be negative',
    '>= 0',
    'Invalid values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM products), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM products
WHERE product_length_cm < 0;


-- PRODUCTS: height

INSERT INTO dq_results
SELECT
    'DQ-RANGE-PROD-003',
    'products',
    'product_height_cm',
    'Validity',
    'product_height_cm must not be negative',
    '>= 0',
    'Invalid values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM products), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM products
WHERE product_height_cm < 0;


-- PRODUCTS: width

INSERT INTO dq_results
SELECT
    'DQ-RANGE-PROD-004',
    'products',
    'product_width_cm',
    'Validity',
    'product_width_cm must not be negative',
    '>= 0',
    'Invalid values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM products), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM products
WHERE product_width_cm < 0;


/*
===============================================================================
SECTION 09 — DATE CONSISTENCY VALIDATION
===============================================================================

Chronological rules:

purchase <= approved
purchase <= carrier delivery
purchase <= customer delivery
carrier delivery <= customer delivery

NULL values are excluded from chronology comparisons because NULL dates are
handled separately as completeness conditions.

===============================================================================
*/


-- Approved before purchase

INSERT INTO dq_results
SELECT
    'DQ-DATE-001',
    'orders',
    'order_approved_at',
    'Consistency',
    'Order approval must not occur before order purchase',
    'approved_at >= purchase_timestamp',
    'Violations = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM orders), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM orders
WHERE order_approved_at IS NOT NULL
  AND order_purchase_timestamp IS NOT NULL
  AND order_approved_at < order_purchase_timestamp;


-- Carrier delivery before purchase

INSERT INTO dq_results
SELECT
    'DQ-DATE-002',
    'orders',
    'order_delivered_carrier_date',
    'Consistency',
    'Carrier delivery must not occur before purchase',
    'carrier_date >= purchase_timestamp',
    'Violations = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM orders), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM orders
WHERE order_delivered_carrier_date IS NOT NULL
  AND order_purchase_timestamp IS NOT NULL
  AND order_delivered_carrier_date < order_purchase_timestamp;


-- Customer delivery before purchase

INSERT INTO dq_results
SELECT
    'DQ-DATE-003',
    'orders',
    'order_delivered_customer_date',
    'Consistency',
    'Customer delivery must not occur before purchase',
    'customer_delivery >= purchase_timestamp',
    'Violations = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM orders), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM orders
WHERE order_delivered_customer_date IS NOT NULL
  AND order_purchase_timestamp IS NOT NULL
  AND order_delivered_customer_date < order_purchase_timestamp;


-- Customer delivery before carrier delivery

INSERT INTO dq_results
SELECT
    'DQ-DATE-004',
    'orders',
    'order_delivered_customer_date',
    'Consistency',
    'Customer delivery must not occur before carrier handover',
    'customer_delivery >= carrier_delivery',
    'Violations = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM orders), 0), 4),
    'HIGH',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM orders
WHERE order_delivered_customer_date IS NOT NULL
  AND order_delivered_carrier_date IS NOT NULL
  AND order_delivered_customer_date < order_delivered_carrier_date;


/*
===============================================================================
SECTION 10 — CATEGORICAL VALIDATION
===============================================================================
*/


-- CUSTOMER STATE DOMAIN

INSERT INTO dq_results
SELECT
    'DQ-CAT-001',
    'customers',
    'customer_state',
    'Categorical Conformity',
    'Customer state must use standardized Brazilian UF codes',
    'Valid UF code',
    'Invalid values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM customers), 0), 4),
    'MEDIUM',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM customers
WHERE customer_state IS NOT NULL
  AND customer_state NOT IN (
      'AC','AL','AP','AM','BA','CE','DF','ES','GO',
      'MA','MT','MS','MG','PA','PB','PR','PE','PI',
      'RJ','RN','RS','RO','RR','SC','SP','SE','TO'
  );


-- SELLER STATE DOMAIN

INSERT INTO dq_results
SELECT
    'DQ-CAT-002',
    'sellers',
    'seller_state',
    'Categorical Conformity',
    'Seller state must use standardized Brazilian UF codes',
    'Valid UF code',
    'Invalid values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM sellers), 0), 4),
    'MEDIUM',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM sellers
WHERE seller_state IS NOT NULL
  AND seller_state NOT IN (
      'AC','AL','AP','AM','BA','CE','DF','ES','GO',
      'MA','MT','MS','MG','PA','PB','PR','PE','PI',
      'RJ','RN','RS','RO','RR','SC','SP','SE','TO'
  );


-- GEOLOCATION STATE DOMAIN

INSERT INTO dq_results
SELECT
    'DQ-CAT-003',
    'geolocation',
    'geolocation_state',
    'Categorical Conformity',
    'Geolocation state must use standardized Brazilian UF codes',
    'Valid UF code',
    'Invalid values = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM geolocation), 0), 4),
    'MEDIUM',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM geolocation
WHERE geolocation_state IS NOT NULL
  AND geolocation_state NOT IN (
      'AC','AL','AP','AM','BA','CE','DF','ES','GO',
      'MA','MT','MS','MG','PA','PB','PR','PE','PI',
      'RJ','RN','RS','RO','RR','SC','SP','SE','TO'
  );


/*
===============================================================================
SECTION 11 — BUSINESS-RULE VALIDATION
===============================================================================

These rules test logical business conditions beyond simple constraints.

===============================================================================
*/


-- Delivered orders should have customer delivery date

INSERT INTO dq_results
SELECT
    'DQ-BIZ-001',
    'orders',
    'order_delivered_customer_date',
    'Business Rule',
    'Delivered orders should have a customer delivery timestamp',
    'Delivered order has non-null delivery date',
    'Violations = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(
        COUNT(*) * 100.0
        / NULLIF(
            (
                SELECT COUNT(*)
                FROM orders
                WHERE order_status = 'delivered'
            ),
            0
        ),
        4
    ),
    'MEDIUM',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NULL;


-- Delivered orders should have carrier handover date

INSERT INTO dq_results
SELECT
    'DQ-BIZ-002',
    'orders',
    'order_delivered_carrier_date',
    'Business Rule',
    'Delivered orders should have a carrier handover timestamp',
    'Delivered order has non-null carrier date',
    'Violations = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(
        COUNT(*) * 100.0
        / NULLIF(
            (
                SELECT COUNT(*)
                FROM orders
                WHERE order_status = 'delivered'
            ),
            0
        ),
        4
    ),
    'MEDIUM',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM orders
WHERE order_status = 'delivered'
  AND order_delivered_carrier_date IS NULL;


-- Payment installments should be positive when payment exists

INSERT INTO dq_results
SELECT
    'DQ-BIZ-003',
    'payments',
    'payment_installments',
    'Business Rule',
    'Payment installments should be greater than zero',
    '> 0',
    'Violations = ' || COUNT(*)::TEXT,
    COUNT(*),
    ROUND(
        COUNT(*) * 100.0
        / NULLIF((SELECT COUNT(*) FROM payments), 0),
        4
    ),
    'MEDIUM',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
FROM payments
WHERE payment_installments <= 0;


/*
===============================================================================
SECTION 12 — QUALITY SUMMARY QUERIES
===============================================================================
*/


/*
------------------------------------------------------------------------------
12.1 COMPLETE RESULT SET
------------------------------------------------------------------------------
*/

SELECT
    test_id,
    dataset,
    column_name,
    quality_dimension,
    rule,
    expected,
    actual,
    failed_count,
    failure_rate,
    severity,
    status
FROM dq_results
ORDER BY
    CASE severity
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        WHEN 'LOW' THEN 4
        WHEN 'NONE' THEN 5
        ELSE 6
    END,
    dataset,
    test_id;


/*
------------------------------------------------------------------------------
12.2 TOTAL TEST SUMMARY
------------------------------------------------------------------------------
*/

SELECT
    COUNT(*) AS total_tests,

    COUNT(*) FILTER (
        WHERE status = 'PASS'
    ) AS passed_tests,

    COUNT(*) FILTER (
        WHERE status = 'FAIL'
    ) AS failed_tests,

    COUNT(*) FILTER (
        WHERE severity = 'CRITICAL'
        AND status = 'FAIL'
    ) AS critical_failures,

    COUNT(*) FILTER (
        WHERE severity = 'HIGH'
        AND status = 'FAIL'
    ) AS high_failures,

    COUNT(*) FILTER (
        WHERE severity = 'MEDIUM'
        AND status = 'FAIL'
    ) AS medium_failures,

    COUNT(*) FILTER (
        WHERE severity = 'LOW'
        AND status = 'FAIL'
    ) AS low_failures

FROM dq_results;


/*
------------------------------------------------------------------------------
12.3 DATASET-LEVEL SUMMARY
------------------------------------------------------------------------------
*/

SELECT
    dataset,

    COUNT(*) AS total_tests,

    COUNT(*) FILTER (
        WHERE status = 'PASS'
    ) AS passed_tests,

    COUNT(*) FILTER (
        WHERE status = 'FAIL'
    ) AS failed_tests,

    COUNT(*) FILTER (
        WHERE severity = 'CRITICAL'
        AND status = 'FAIL'
    ) AS critical_failures,

    COUNT(*) FILTER (
        WHERE severity = 'HIGH'
        AND status = 'FAIL'
    ) AS high_failures,

    COUNT(*) FILTER (
        WHERE severity = 'MEDIUM'
        AND status = 'FAIL'
    ) AS medium_failures,

    COUNT(*) FILTER (
        WHERE severity = 'LOW'
        AND status = 'FAIL'
    ) AS low_failures,

    CASE
        WHEN COUNT(*) FILTER (
            WHERE status = 'FAIL'
        ) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END AS overall_status

FROM dq_results
GROUP BY dataset
ORDER BY
    failed_tests DESC,
    dataset;


/*
------------------------------------------------------------------------------
12.4 QUALITY-DIMENSION SUMMARY
------------------------------------------------------------------------------
*/

SELECT
    quality_dimension,

    COUNT(*) AS total_tests,

    COUNT(*) FILTER (
        WHERE status = 'PASS'
    ) AS passed_tests,

    COUNT(*) FILTER (
        WHERE status = 'FAIL'
    ) AS failed_tests,

    COUNT(*) FILTER (
        WHERE severity = 'CRITICAL'
        AND status = 'FAIL'
    ) AS critical_failures,

    COUNT(*) FILTER (
        WHERE severity = 'HIGH'
        AND status = 'FAIL'
    ) AS high_failures,

    COUNT(*) FILTER (
        WHERE severity = 'MEDIUM'
        AND status = 'FAIL'
    ) AS medium_failures,

    COUNT(*) FILTER (
        WHERE severity = 'LOW'
        AND status = 'FAIL'
    ) AS low_failures

FROM dq_results
GROUP BY quality_dimension
ORDER BY failed_tests DESC;


/*
------------------------------------------------------------------------------
12.5 ONLY FAILED RULES
------------------------------------------------------------------------------
*/

SELECT
    test_id,
    dataset,
    column_name,
    quality_dimension,
    rule,
    expected,
    actual,
    failed_count,
    failure_rate,
    severity,
    status
FROM dq_results
WHERE status = 'FAIL'
ORDER BY
    CASE severity
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        WHEN 'LOW' THEN 4
        ELSE 5
    END,
    failed_count DESC;


/*
------------------------------------------------------------------------------
12.6 CRITICAL / HIGH PRIORITY ISSUES
------------------------------------------------------------------------------
*/

SELECT
    test_id,
    dataset,
    column_name,
    quality_dimension,
    rule,
    failed_count,
    failure_rate,
    severity,
    status
FROM dq_results
WHERE status = 'FAIL'
  AND severity IN ('CRITICAL', 'HIGH')
ORDER BY
    CASE severity
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
    END,
    failed_count DESC;


/*
===============================================================================
END OF PHASE 4 — STEP 02
===============================================================================
*/