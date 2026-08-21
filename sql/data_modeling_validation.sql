-- ============================================================
-- PHASE 6 — ANALYTICAL MODEL VALIDATION
-- ============================================================
-- Project: Retail Sales Performance Analytics
-- Database: retail_sales_analytics
-- Dialect: PostgreSQL
--
-- VALIDATION AREAS
-- ----------------
-- 1. Row-count validation
-- 2. Fact-grain validation
-- 3. Primary-key validation
-- 4. Foreign-key / orphan validation
-- 5. Phase 5 source-to-analytics reconciliation
-- 6. Business-total validation
-- 7. Key completeness validation
-- 8. Date dimension validation
-- ============================================================

\set ON_ERROR_STOP on

\timing on


-- ============================================================
-- 1. VALIDATION RESULT TABLE
-- ============================================================

DROP TABLE IF EXISTS tmp_phase6_validation;

CREATE TEMP TABLE tmp_phase6_validation (
    validation_id   SERIAL PRIMARY KEY,
    validation_area TEXT,
    check_name      TEXT,
    source_count    NUMERIC,
    target_count    NUMERIC,
    difference      NUMERIC,
    status          TEXT,
    notes           TEXT
);


-- ============================================================
-- 2. ROW-COUNT VALIDATION
-- ============================================================


-- ------------------------------------------------------------
-- 2.1 CUSTOMERS
-- ------------------------------------------------------------

INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'ROW_COUNT',
    'Customers → dim_customer',
    (SELECT COUNT(*) FROM olist_customers_dataset),
    (SELECT COUNT(*) FROM analytics.dim_customer),
    (SELECT COUNT(*) FROM olist_customers_dataset)
        - (SELECT COUNT(*) FROM analytics.dim_customer),
    CASE
        WHEN (SELECT COUNT(*) FROM olist_customers_dataset)
           = (SELECT COUNT(*) FROM analytics.dim_customer)
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    'One analytical row per customer_id';


-- ------------------------------------------------------------
-- 2.2 SELLERS
-- ------------------------------------------------------------

INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'ROW_COUNT',
    'Sellers → dim_seller',
    (SELECT COUNT(*) FROM olist_sellers_dataset),
    (SELECT COUNT(*) FROM analytics.dim_seller),
    (SELECT COUNT(*) FROM olist_sellers_dataset)
        - (SELECT COUNT(*) FROM analytics.dim_seller),
    CASE
        WHEN (SELECT COUNT(*) FROM olist_sellers_dataset)
           = (SELECT COUNT(*) FROM analytics.dim_seller)
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    'One analytical row per seller_id';


-- ------------------------------------------------------------
-- 2.3 PRODUCTS
-- ------------------------------------------------------------

INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'ROW_COUNT',
    'Products → dim_product',
    (SELECT COUNT(*) FROM olist_products_dataset),
    (SELECT COUNT(*) FROM analytics.dim_product),
    (SELECT COUNT(*) FROM olist_products_dataset)
        - (SELECT COUNT(*) FROM analytics.dim_product),
    CASE
        WHEN (SELECT COUNT(*) FROM olist_products_dataset)
           = (SELECT COUNT(*) FROM analytics.dim_product)
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    'One analytical row per product_id';


-- ------------------------------------------------------------
-- 2.4 ORDERS
-- ------------------------------------------------------------

INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'ROW_COUNT',
    'Orders → fact_orders',
    (SELECT COUNT(*) FROM olist_orders_dataset),
    (SELECT COUNT(*) FROM analytics.fact_orders),
    (SELECT COUNT(*) FROM olist_orders_dataset)
        - (SELECT COUNT(*) FROM analytics.fact_orders),
    CASE
        WHEN (SELECT COUNT(*) FROM olist_orders_dataset)
           = (SELECT COUNT(*) FROM analytics.fact_orders)
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    'One analytical row per order_id';


-- ------------------------------------------------------------
-- 2.5 ORDER ITEMS
-- ------------------------------------------------------------

INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'ROW_COUNT',
    'Order Items → fact_order_items',
    (SELECT COUNT(*) FROM olist_order_items_dataset),
    (SELECT COUNT(*) FROM analytics.fact_order_items),
    (SELECT COUNT(*) FROM olist_order_items_dataset)
        - (SELECT COUNT(*) FROM analytics.fact_order_items),
    CASE
        WHEN (SELECT COUNT(*) FROM olist_order_items_dataset)
           = (SELECT COUNT(*) FROM analytics.fact_order_items)
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    'One analytical row per order_id + order_item_id';


-- ------------------------------------------------------------
-- 2.6 PAYMENTS
-- ------------------------------------------------------------

INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'ROW_COUNT',
    'Payments → fact_payments',
    (SELECT COUNT(*) FROM olist_order_payments_dataset),
    (SELECT COUNT(*) FROM analytics.fact_payments),
    (SELECT COUNT(*) FROM olist_order_payments_dataset)
        - (SELECT COUNT(*) FROM analytics.fact_payments),
    CASE
        WHEN (SELECT COUNT(*) FROM olist_order_payments_dataset)
           = (SELECT COUNT(*) FROM analytics.fact_payments)
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    'One analytical row per order_id + payment_sequential';


-- ------------------------------------------------------------
-- 2.7 REVIEWS
-- ------------------------------------------------------------

INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'ROW_COUNT',
    'Reviews → fact_reviews',
    (SELECT COUNT(*) FROM olist_order_reviews_dataset),
    (SELECT COUNT(*) FROM analytics.fact_reviews),
    (SELECT COUNT(*) FROM olist_order_reviews_dataset)
        - (SELECT COUNT(*) FROM analytics.fact_reviews),
    CASE
        WHEN (SELECT COUNT(*) FROM olist_order_reviews_dataset)
           = (SELECT COUNT(*) FROM analytics.fact_reviews)
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    'One analytical row per source review record';


-- ------------------------------------------------------------
-- 2.8 GEOLOCATION
-- ------------------------------------------------------------

INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'ROW_COUNT',
    'Geolocation → dim_geography distinct ZIP grain',

    (
        SELECT COUNT(DISTINCT geolocation_zip_code_prefix)
        FROM olist_geolocation_dataset
        WHERE geolocation_zip_code_prefix IS NOT NULL
    ),

    (
        SELECT COUNT(*)
        FROM analytics.dim_geography
    ),

    (
        SELECT COUNT(DISTINCT geolocation_zip_code_prefix)
        FROM olist_geolocation_dataset
        WHERE geolocation_zip_code_prefix IS NOT NULL
    )
    -
    (
        SELECT COUNT(*)
        FROM analytics.dim_geography
    ),

    CASE
        WHEN
            (
                SELECT COUNT(DISTINCT geolocation_zip_code_prefix)
                FROM olist_geolocation_dataset
                WHERE geolocation_zip_code_prefix IS NOT NULL
            )
            =
            (
                SELECT COUNT(*)
                FROM analytics.dim_geography
            )
        THEN 'PASS'
        ELSE 'FAIL'
    END,

    'Validated at analytical ZIP-prefix grain'
;


-- ============================================================
-- 3. FACT GRAIN VALIDATION
-- ============================================================


-- ------------------------------------------------------------
-- 3.1 FACT ORDERS
-- ------------------------------------------------------------

INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'FACT_GRAIN',
    'fact_orders duplicate order_id',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Expected one row per order_id'
FROM (
    SELECT order_id
    FROM analytics.fact_orders
    GROUP BY order_id
    HAVING COUNT(*) > 1
) duplicates;


-- ------------------------------------------------------------
-- 3.2 FACT ORDER ITEMS
-- ------------------------------------------------------------

INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'FACT_GRAIN',
    'fact_order_items duplicate order_id + order_item_id',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Expected one row per order_id + order_item_id'
FROM (
    SELECT
        order_id,
        order_item_id
    FROM analytics.fact_order_items
    GROUP BY order_id, order_item_id
    HAVING COUNT(*) > 1
) duplicates;


-- ------------------------------------------------------------
-- 3.3 FACT PAYMENTS
-- ------------------------------------------------------------

INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'FACT_GRAIN',
    'fact_payments duplicate order_id + payment_sequential',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Expected one row per order_id + payment_sequential'
FROM (
    SELECT
        order_id,
        payment_sequential
    FROM analytics.fact_payments
    GROUP BY order_id, payment_sequential
    HAVING COUNT(*) > 1
) duplicates;


-- ------------------------------------------------------------
-- 3.4 FACT REVIEWS
-- ------------------------------------------------------------

INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'FACT_GRAIN',
    'fact_reviews duplicate review_key',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Expected one row per analytical review_key'
FROM (
    SELECT review_key
    FROM analytics.fact_reviews
    GROUP BY review_key
    HAVING COUNT(*) > 1
) duplicates;


-- ============================================================
-- 4. PRIMARY KEY VALIDATION
-- ============================================================


-- DIM CUSTOMER
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'PRIMARY_KEY',
    'dim_customer duplicate customer_key',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'customer_key must be unique'
FROM (
    SELECT customer_key
    FROM analytics.dim_customer
    GROUP BY customer_key
    HAVING COUNT(*) > 1
) x;


-- DIM SELLER
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'PRIMARY_KEY',
    'dim_seller duplicate seller_key',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'seller_key must be unique'
FROM (
    SELECT seller_key
    FROM analytics.dim_seller
    GROUP BY seller_key
    HAVING COUNT(*) > 1
) x;


-- DIM PRODUCT
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'PRIMARY_KEY',
    'dim_product duplicate product_key',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'product_key must be unique'
FROM (
    SELECT product_key
    FROM analytics.dim_product
    GROUP BY product_key
    HAVING COUNT(*) > 1
) x;


-- FACT ORDERS
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'PRIMARY_KEY',
    'fact_orders duplicate order_key',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'order_key must be unique'
FROM (
    SELECT order_key
    FROM analytics.fact_orders
    GROUP BY order_key
    HAVING COUNT(*) > 1
) x;


-- ============================================================
-- 5. FOREIGN KEY / ORPHAN VALIDATION
-- ============================================================


-- FACT ORDERS → CUSTOMER
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'FOREIGN_KEY',
    'fact_orders → dim_customer',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Every customer_key must resolve'
FROM analytics.fact_orders f
LEFT JOIN analytics.dim_customer d
    ON f.customer_key = d.customer_key
WHERE d.customer_key IS NULL;


-- FACT ORDERS → STATUS
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'FOREIGN_KEY',
    'fact_orders → dim_order_status',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Every order_status_key must resolve'
FROM analytics.fact_orders f
LEFT JOIN analytics.dim_order_status d
    ON f.order_status_key = d.order_status_key
WHERE d.order_status_key IS NULL;


-- FACT ORDER ITEMS → PRODUCT
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'FOREIGN_KEY',
    'fact_order_items → dim_product',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Every product_key must resolve'
FROM analytics.fact_order_items f
LEFT JOIN analytics.dim_product d
    ON f.product_key = d.product_key
WHERE d.product_key IS NULL;


-- FACT ORDER ITEMS → SELLER
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'FOREIGN_KEY',
    'fact_order_items → dim_seller',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Every seller_key must resolve'
FROM analytics.fact_order_items f
LEFT JOIN analytics.dim_seller d
    ON f.seller_key = d.seller_key
WHERE d.seller_key IS NULL;


-- FACT ORDER ITEMS → DATE
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'FOREIGN_KEY',
    'fact_order_items → dim_date',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Every non-null order_date_key must resolve'
FROM analytics.fact_order_items f
LEFT JOIN analytics.dim_date d
    ON f.order_date_key = d.date_key
WHERE f.order_date_key IS NOT NULL
  AND d.date_key IS NULL;


-- FACT PAYMENTS → CUSTOMER
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'FOREIGN_KEY',
    'fact_payments → dim_customer',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Every customer_key must resolve'
FROM analytics.fact_payments f
LEFT JOIN analytics.dim_customer d
    ON f.customer_key = d.customer_key
WHERE d.customer_key IS NULL;


-- FACT REVIEWS → CUSTOMER
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'FOREIGN_KEY',
    'fact_reviews → dim_customer',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Every customer_key must resolve'
FROM analytics.fact_reviews f
LEFT JOIN analytics.dim_customer d
    ON f.customer_key = d.customer_key
WHERE d.customer_key IS NULL;


-- FACT REVIEWS → DATE
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'FOREIGN_KEY',
    'fact_reviews → dim_date',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Every non-null review_date_key must resolve'
FROM analytics.fact_reviews f
LEFT JOIN analytics.dim_date d
    ON f.review_date_key = d.date_key
WHERE f.review_date_key IS NOT NULL
  AND d.date_key IS NULL;


-- ============================================================
-- 6. PHASE 5 SOURCE-TO-ANALYTICS RECONCILIATION
-- ============================================================


-- CUSTOMER
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'RECONCILIATION',
    'Customer business-key reconciliation',
    COUNT(DISTINCT customer_id),
    (
        SELECT COUNT(DISTINCT customer_id)
        FROM analytics.dim_customer
    ),
    COUNT(DISTINCT customer_id)
        -
        (
            SELECT COUNT(DISTINCT customer_id)
            FROM analytics.dim_customer
        ),
    CASE
        WHEN COUNT(DISTINCT customer_id)
             =
             (
                 SELECT COUNT(DISTINCT customer_id)
                 FROM analytics.dim_customer
             )
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Source customer_id set reconciled'
FROM olist_customers_dataset;


-- PRODUCT
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'RECONCILIATION',
    'Product business-key reconciliation',
    COUNT(DISTINCT product_id),
    (
        SELECT COUNT(DISTINCT product_id)
        FROM analytics.dim_product
    ),
    COUNT(DISTINCT product_id)
        -
        (
            SELECT COUNT(DISTINCT product_id)
            FROM analytics.dim_product
        ),
    CASE
        WHEN COUNT(DISTINCT product_id)
             =
             (
                 SELECT COUNT(DISTINCT product_id)
                 FROM analytics.dim_product
             )
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Source product_id set reconciled'
FROM olist_products_dataset;


-- SELLER
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'RECONCILIATION',
    'Seller business-key reconciliation',
    COUNT(DISTINCT seller_id),
    (
        SELECT COUNT(DISTINCT seller_id)
        FROM analytics.dim_seller
    ),
    COUNT(DISTINCT seller_id)
        -
        (
            SELECT COUNT(DISTINCT seller_id)
            FROM analytics.dim_seller
        ),
    CASE
        WHEN COUNT(DISTINCT seller_id)
             =
             (
                 SELECT COUNT(DISTINCT seller_id)
                 FROM analytics.dim_seller
             )
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Source seller_id set reconciled'
FROM olist_sellers_dataset;


-- ORDER
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'RECONCILIATION',
    'Order business-key reconciliation',
    COUNT(DISTINCT order_id),
    (
        SELECT COUNT(DISTINCT order_id)
        FROM analytics.fact_orders
    ),
    COUNT(DISTINCT order_id)
        -
        (
            SELECT COUNT(DISTINCT order_id)
            FROM analytics.fact_orders
        ),
    CASE
        WHEN COUNT(DISTINCT order_id)
             =
             (
                 SELECT COUNT(DISTINCT order_id)
                 FROM analytics.fact_orders
             )
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Source order_id set reconciled'
FROM olist_orders_dataset;


-- ORDER ITEMS
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'RECONCILIATION',
    'Order-item business-key reconciliation',
    COUNT(*),
    (
        SELECT COUNT(*)
        FROM analytics.fact_order_items
    ),
    COUNT(*)
        -
        (
            SELECT COUNT(*)
            FROM analytics.fact_order_items
        ),
    CASE
        WHEN COUNT(*)
             =
             (
                 SELECT COUNT(*)
                 FROM analytics.fact_order_items
             )
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Source order-item grain reconciled'
FROM olist_order_items_dataset;


-- PAYMENTS
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'RECONCILIATION',
    'Payment business-key reconciliation',
    COUNT(*),
    (
        SELECT COUNT(*)
        FROM analytics.fact_payments
    ),
    COUNT(*)
        -
        (
            SELECT COUNT(*)
            FROM analytics.fact_payments
        ),
    CASE
        WHEN COUNT(*)
             =
             (
                 SELECT COUNT(*)
                 FROM analytics.fact_payments
             )
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Source payment grain reconciled'
FROM olist_order_payments_dataset;


-- REVIEWS
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'RECONCILIATION',
    'Review row-count reconciliation',
    COUNT(*),
    (
        SELECT COUNT(*)
        FROM analytics.fact_reviews
    ),
    COUNT(*)
        -
        (
            SELECT COUNT(*)
            FROM analytics.fact_reviews
        ),
    CASE
        WHEN COUNT(*)
             =
             (
                 SELECT COUNT(*)
                 FROM analytics.fact_reviews
             )
        THEN 'PASS'
        ELSE 'FAIL'
    END,
    'Source review records reconciled'
FROM olist_order_reviews_dataset;


-- ============================================================
-- 7. BUSINESS-TOTAL VALIDATION
-- ============================================================


-- PAYMENT VALUE
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'BUSINESS_TOTAL',
    'Payment value reconciliation',

    ROUND(
        COALESCE(
            (SELECT SUM(payment_value)
             FROM olist_order_payments_dataset),
            0
        ),
        2
    ),

    ROUND(
        COALESCE(
            (SELECT SUM(payment_value)
             FROM analytics.fact_payments),
            0
        ),
        2
    ),

    ROUND(
        COALESCE(
            (SELECT SUM(payment_value)
             FROM olist_order_payments_dataset),
            0
        ),
        2
    )
    -
    ROUND(
        COALESCE(
            (SELECT SUM(payment_value)
             FROM analytics.fact_payments),
            0
        ),
        2
    ),

    CASE
        WHEN
            ROUND(
                COALESCE(
                    (SELECT SUM(payment_value)
                     FROM olist_order_payments_dataset),
                    0
                ),
                2
            )
            =
            ROUND(
                COALESCE(
                    (SELECT SUM(payment_value)
                     FROM analytics.fact_payments),
                    0
                ),
                2
            )
        THEN 'PASS'
        ELSE 'FAIL'
    END,

    'Payment value reconciles to source'
;


-- ORDER ITEM PRICE
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'BUSINESS_TOTAL',
    'Order-item price reconciliation',

    ROUND(
        COALESCE(
            (SELECT SUM(price)
             FROM olist_order_items_dataset),
            0
        ),
        2
    ),

    ROUND(
        COALESCE(
            (SELECT SUM(price)
             FROM analytics.fact_order_items),
            0
        ),
        2
    ),

    ROUND(
        COALESCE(
            (SELECT SUM(price)
             FROM olist_order_items_dataset),
            0
        ),
        2
    )
    -
    ROUND(
        COALESCE(
            (SELECT SUM(price)
             FROM analytics.fact_order_items),
            0
        ),
        2
    ),

    CASE
        WHEN
            ROUND(
                COALESCE(
                    (SELECT SUM(price)
                     FROM olist_order_items_dataset),
                    0
                ),
                2
            )
            =
            ROUND(
                COALESCE(
                    (SELECT SUM(price)
                     FROM analytics.fact_order_items),
                    0
                ),
                2
            )
        THEN 'PASS'
        ELSE 'FAIL'
    END,

    'Order-item price reconciles to source'
;


-- FREIGHT VALUE
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'BUSINESS_TOTAL',
    'Freight value reconciliation',

    ROUND(
        COALESCE(
            (SELECT SUM(freight_value)
             FROM olist_order_items_dataset),
            0
        ),
        2
    ),

    ROUND(
        COALESCE(
            (SELECT SUM(freight_value)
             FROM analytics.fact_order_items),
            0
        ),
        2
    ),

    ROUND(
        COALESCE(
            (SELECT SUM(freight_value)
             FROM olist_order_items_dataset),
            0
        ),
        2
    )
    -
    ROUND(
        COALESCE(
            (SELECT SUM(freight_value)
             FROM analytics.fact_order_items),
            0
        ),
        2
    ),

    CASE
        WHEN
            ROUND(
                COALESCE(
                    (SELECT SUM(freight_value)
                     FROM olist_order_items_dataset),
                    0
                ),
                2
            )
            =
            ROUND(
                COALESCE(
                    (SELECT SUM(freight_value)
                     FROM analytics.fact_order_items),
                    0
                ),
                2
            )
        THEN 'PASS'
        ELSE 'FAIL'
    END,

    'Freight value reconciles to source'
;


-- ============================================================
-- 8. KEY COMPLETENESS VALIDATION
-- ============================================================


-- FACT ORDERS → CUSTOMER KEY
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'KEY_COMPLETENESS',
    'fact_orders customer_key NULL',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'customer_key is mandatory'
FROM analytics.fact_orders
WHERE customer_key IS NULL;


-- FACT ORDERS → STATUS KEY
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'KEY_COMPLETENESS',
    'fact_orders order_status_key NULL',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'order_status_key is mandatory'
FROM analytics.fact_orders
WHERE order_status_key IS NULL;


-- FACT ORDER ITEMS → PRODUCT KEY
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'KEY_COMPLETENESS',
    'fact_order_items product_key NULL',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'product_key is mandatory'
FROM analytics.fact_order_items
WHERE product_key IS NULL;


-- FACT ORDER ITEMS → SELLER KEY
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'KEY_COMPLETENESS',
    'fact_order_items seller_key NULL',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'seller_key is mandatory'
FROM analytics.fact_order_items
WHERE seller_key IS NULL;


-- ============================================================
-- 9. DATE DIMENSION VALIDATION
-- ============================================================


-- DATE KEY
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'DATE_DIMENSION',
    'dim_date duplicate date_key',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'One row per date_key'
FROM (
    SELECT date_key
    FROM analytics.dim_date
    GROUP BY date_key
    HAVING COUNT(*) > 1
) x;


-- FULL DATE
INSERT INTO tmp_phase6_validation (
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
)
SELECT
    'DATE_DIMENSION',
    'dim_date duplicate full_date',
    0,
    COUNT(*),
    COUNT(*),
    CASE
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END,
    'One row per calendar date'
FROM (
    SELECT full_date
    FROM analytics.dim_date
    GROUP BY full_date
    HAVING COUNT(*) > 1
) x;


-- ============================================================
-- 10. VALIDATION SUMMARY
-- ============================================================

SELECT
    validation_area,
    COUNT(*) AS checks,
    COUNT(*) FILTER (WHERE status = 'PASS') AS passed,
    COUNT(*) FILTER (WHERE status = 'FAIL') AS failed
FROM tmp_phase6_validation
GROUP BY validation_area
ORDER BY validation_area;


-- ============================================================
-- 11. COMPLETE VALIDATION RESULTS
-- ============================================================

SELECT
    validation_id,
    validation_area,
    check_name,
    source_count,
    target_count,
    difference,
    status,
    notes
FROM tmp_phase6_validation
ORDER BY validation_id;


-- ============================================================
-- 12. FINAL PHASE 6 STATUS
-- ============================================================

SELECT
    CASE
        WHEN COUNT(*) FILTER (WHERE status = 'FAIL') = 0
        THEN 'PASS — ALL PHASE 6 VALIDATION CHECKS PASSED'
        ELSE 'FAIL — PHASE 6 VALIDATION REQUIRES INVESTIGATION'
    END AS phase6_validation_status,

    COUNT(*) AS total_checks,

    COUNT(*) FILTER (
        WHERE status = 'PASS'
    ) AS passed_checks,

    COUNT(*) FILTER (
        WHERE status = 'FAIL'
    ) AS failed_checks

FROM tmp_phase6_validation;


-- ============================================================
-- END OF PHASE 6 VALIDATION
-- ============================================================