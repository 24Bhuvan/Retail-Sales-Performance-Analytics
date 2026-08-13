-- ============================================================
-- PHASE 3 — DATA PROFILING
-- ============================================================
-- Project: Retail Sales Performance Analytics
-- Target File: sql/data_profiling.sql
-- Dialect: PostgreSQL Compatible
--
-- PURPOSE
-- -------
-- Read-only profiling of the 9 raw Olist datasets.
--
-- SQL RESPONSIBILITY
-- ------------------
-- SQL provides independent database-side validation for:
--   1. Dataset structure and row counts
--   2. Missing values
--   3. Full-row duplicates
--   4. Primary/composite-key validity
--   5. Referential consistency
--   6. Numeric distributions and IQR outliers
--   7. Date ranges and chronology
--   8. Categorical distributions
--   9. Structural/anomaly indicators
--
-- PANDAS RESPONSIBILITY
-- ---------------------
-- Pandas remains the primary implementation for the consolidated
-- Phase 3 profiling report.
--
-- STRICT READ-ONLY BOUNDARY
-- -------------------------
-- SELECT / WITH / VALUES queries only.
--
-- NO:
--   INSERT
--   UPDATE
--   DELETE
--   DROP
--   ALTER
--   CREATE
--   TRUNCATE
--   CLEANING
--   IMPUTATION
--   DEDUPLICATION
--   FEATURE ENGINEERING
--   BUSINESS KPI CALCULATION
--   HYPOTHESIS TESTING
-- ============================================================


-- ============================================================
-- SECTION 0 — DATABASE STRUCTURE
-- ============================================================

-- Profile all nine datasets from PostgreSQL metadata.

SELECT
    table_name AS dataset_name,
    COUNT(column_name) AS column_count
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN (
      'olist_customers_dataset',
      'olist_geolocation_dataset',
      'olist_order_items_dataset',
      'olist_order_payments_dataset',
      'olist_order_reviews_dataset',
      'olist_orders_dataset',
      'olist_products_dataset',
      'olist_sellers_dataset',
      'product_category_name_translation'
  )
GROUP BY table_name
ORDER BY table_name;


-- ============================================================
-- SECTION 1 — DATASET OVERVIEW
-- ============================================================

SELECT
    'olist_customers_dataset' AS dataset_name,
    COUNT(*) AS total_rows,
    (SELECT COUNT(*)
     FROM information_schema.columns
     WHERE table_schema = 'public'
       AND table_name = 'olist_customers_dataset') AS column_count
FROM olist_customers_dataset

UNION ALL

SELECT
    'olist_geolocation_dataset',
    COUNT(*),
    (SELECT COUNT(*)
     FROM information_schema.columns
     WHERE table_schema = 'public'
       AND table_name = 'olist_geolocation_dataset')
FROM olist_geolocation_dataset

UNION ALL

SELECT
    'olist_order_items_dataset',
    COUNT(*),
    (SELECT COUNT(*)
     FROM information_schema.columns
     WHERE table_schema = 'public'
       AND table_name = 'olist_order_items_dataset')
FROM olist_order_items_dataset

UNION ALL

SELECT
    'olist_order_payments_dataset',
    COUNT(*),
    (SELECT COUNT(*)
     FROM information_schema.columns
     WHERE table_schema = 'public'
       AND table_name = 'olist_order_payments_dataset')
FROM olist_order_payments_dataset

UNION ALL

SELECT
    'olist_order_reviews_dataset',
    COUNT(*),
    (SELECT COUNT(*)
     FROM information_schema.columns
     WHERE table_schema = 'public'
       AND table_name = 'olist_order_reviews_dataset')
FROM olist_order_reviews_dataset

UNION ALL

SELECT
    'olist_orders_dataset',
    COUNT(*),
    (SELECT COUNT(*)
     FROM information_schema.columns
     WHERE table_schema = 'public'
       AND table_name = 'olist_orders_dataset')
FROM olist_orders_dataset

UNION ALL

SELECT
    'olist_products_dataset',
    COUNT(*),
    (SELECT COUNT(*)
     FROM information_schema.columns
     WHERE table_schema = 'public'
       AND table_name = 'olist_products_dataset')
FROM olist_products_dataset

UNION ALL

SELECT
    'olist_sellers_dataset',
    COUNT(*),
    (SELECT COUNT(*)
     FROM information_schema.columns
     WHERE table_schema = 'public'
       AND table_name = 'olist_sellers_dataset')
FROM olist_sellers_dataset

UNION ALL

SELECT
    'product_category_name_translation',
    COUNT(*),
    (SELECT COUNT(*)
     FROM information_schema.columns
     WHERE table_schema = 'public'
       AND table_name = 'product_category_name_translation')
FROM product_category_name_translation

ORDER BY dataset_name;


-- ============================================================
-- SECTION 2 — NULL / MISSING-VALUE PROFILING
-- ============================================================
-- Rule:
--   NULL % = NULL count / total rows * 100
--
-- NULLs are missing-value observations.
-- They are NOT automatically treated as errors/anomalies.
-- ============================================================


-- ------------------------------------------------------------
-- 2.1 Customers
-- ------------------------------------------------------------

SELECT
    'olist_customers_dataset' AS dataset,
    column_name,
    null_count,
    total_rows,
    total_rows - null_count AS non_null_count,
    ROUND(
        null_count::NUMERIC
        / NULLIF(total_rows, 0) * 100,
        4
    ) AS null_pct
FROM (
    SELECT
        COUNT(*) AS total_rows,
        COUNT(*) - COUNT(customer_id) AS customer_id,
        COUNT(*) - COUNT(customer_unique_id) AS customer_unique_id,
        COUNT(*) - COUNT(customer_zip_code_prefix) AS customer_zip_code_prefix,
        COUNT(*) - COUNT(customer_city) AS customer_city,
        COUNT(*) - COUNT(customer_state) AS customer_state
    FROM olist_customers_dataset
) s
CROSS JOIN LATERAL (
    VALUES
        ('customer_id', customer_id),
        ('customer_unique_id', customer_unique_id),
        ('customer_zip_code_prefix', customer_zip_code_prefix),
        ('customer_city', customer_city),
        ('customer_state', customer_state)
) v(column_name, null_count);


-- ------------------------------------------------------------
-- 2.2 Orders
-- ------------------------------------------------------------

SELECT
    'olist_orders_dataset' AS dataset,
    column_name,
    null_count,
    total_rows,
    total_rows - null_count AS non_null_count,
    ROUND(
        null_count::NUMERIC
        / NULLIF(total_rows, 0) * 100,
        4
    ) AS null_pct
FROM (
    SELECT
        COUNT(*) AS total_rows,
        COUNT(*) - COUNT(order_id) AS order_id,
        COUNT(*) - COUNT(customer_id) AS customer_id,
        COUNT(*) - COUNT(order_status) AS order_status,
        COUNT(*) - COUNT(order_purchase_timestamp) AS order_purchase_timestamp,
        COUNT(*) - COUNT(order_approved_at) AS order_approved_at,
        COUNT(*) - COUNT(order_delivered_carrier_date) AS order_delivered_carrier_date,
        COUNT(*) - COUNT(order_delivered_customer_date) AS order_delivered_customer_date,
        COUNT(*) - COUNT(order_estimated_delivery_date) AS order_estimated_delivery_date
    FROM olist_orders_dataset
) s
CROSS JOIN LATERAL (
    VALUES
        ('order_id', order_id),
        ('customer_id', customer_id),
        ('order_status', order_status),
        ('order_purchase_timestamp', order_purchase_timestamp),
        ('order_approved_at', order_approved_at),
        ('order_delivered_carrier_date', order_delivered_carrier_date),
        ('order_delivered_customer_date', order_delivered_customer_date),
        ('order_estimated_delivery_date', order_estimated_delivery_date)
) v(column_name, null_count);


-- ------------------------------------------------------------
-- 2.3 Order Items
-- ------------------------------------------------------------

SELECT
    'olist_order_items_dataset' AS dataset,
    column_name,
    null_count,
    total_rows,
    total_rows - null_count AS non_null_count,
    ROUND(
        null_count::NUMERIC
        / NULLIF(total_rows, 0) * 100,
        4
    ) AS null_pct
FROM (
    SELECT
        COUNT(*) AS total_rows,
        COUNT(*) - COUNT(order_id) AS order_id,
        COUNT(*) - COUNT(order_item_id) AS order_item_id,
        COUNT(*) - COUNT(product_id) AS product_id,
        COUNT(*) - COUNT(seller_id) AS seller_id,
        COUNT(*) - COUNT(shipping_limit_date) AS shipping_limit_date,
        COUNT(*) - COUNT(price) AS price,
        COUNT(*) - COUNT(freight_value) AS freight_value
    FROM olist_order_items_dataset
) s
CROSS JOIN LATERAL (
    VALUES
        ('order_id', order_id),
        ('order_item_id', order_item_id),
        ('product_id', product_id),
        ('seller_id', seller_id),
        ('shipping_limit_date', shipping_limit_date),
        ('price', price),
        ('freight_value', freight_value)
) v(column_name, null_count);


-- ------------------------------------------------------------
-- 2.4 Payments
-- ------------------------------------------------------------

SELECT
    'olist_order_payments_dataset' AS dataset,
    column_name,
    null_count,
    total_rows,
    total_rows - null_count AS non_null_count,
    ROUND(
        null_count::NUMERIC
        / NULLIF(total_rows, 0) * 100,
        4
    ) AS null_pct
FROM (
    SELECT
        COUNT(*) AS total_rows,
        COUNT(*) - COUNT(order_id) AS order_id,
        COUNT(*) - COUNT(payment_sequential) AS payment_sequential,
        COUNT(*) - COUNT(payment_type) AS payment_type,
        COUNT(*) - COUNT(payment_installments) AS payment_installments,
        COUNT(*) - COUNT(payment_value) AS payment_value
    FROM olist_order_payments_dataset
) s
CROSS JOIN LATERAL (
    VALUES
        ('order_id', order_id),
        ('payment_sequential', payment_sequential),
        ('payment_type', payment_type),
        ('payment_installments', payment_installments),
        ('payment_value', payment_value)
) v(column_name, null_count);


-- ------------------------------------------------------------
-- 2.5 Reviews
-- ------------------------------------------------------------

SELECT
    'olist_order_reviews_dataset' AS dataset,
    column_name,
    null_count,
    total_rows,
    total_rows - null_count AS non_null_count,
    ROUND(
        null_count::NUMERIC
        / NULLIF(total_rows, 0) * 100,
        4
    ) AS null_pct
FROM (
    SELECT
        COUNT(*) AS total_rows,
        COUNT(*) - COUNT(review_id) AS review_id,
        COUNT(*) - COUNT(order_id) AS order_id,
        COUNT(*) - COUNT(review_score) AS review_score,
        COUNT(*) - COUNT(review_creation_date) AS review_creation_date,
        COUNT(*) - COUNT(review_answer_timestamp) AS review_answer_timestamp
    FROM olist_order_reviews_dataset
) s
CROSS JOIN LATERAL (
    VALUES
        ('review_id', review_id),
        ('order_id', order_id),
        ('review_score', review_score),
        ('review_creation_date', review_creation_date),
        ('review_answer_timestamp', review_answer_timestamp)
) v(column_name, null_count);


-- ------------------------------------------------------------
-- 2.6 Products
-- ------------------------------------------------------------

SELECT
    'olist_products_dataset' AS dataset,
    column_name,
    null_count,
    total_rows,
    total_rows - null_count AS non_null_count,
    ROUND(
        null_count::NUMERIC
        / NULLIF(total_rows, 0) * 100,
        4
    ) AS null_pct
FROM (
    SELECT
        COUNT(*) AS total_rows,
        COUNT(*) - COUNT(product_id) AS product_id,
        COUNT(*) - COUNT(product_category_name) AS product_category_name,
        COUNT(*) - COUNT(product_name_lenght) AS product_name_lenght,
        COUNT(*) - COUNT(product_description_lenght) AS product_description_lenght,
        COUNT(*) - COUNT(product_photos_qty) AS product_photos_qty,
        COUNT(*) - COUNT(product_weight_g) AS product_weight_g,
        COUNT(*) - COUNT(product_length_cm) AS product_length_cm,
        COUNT(*) - COUNT(product_height_cm) AS product_height_cm,
        COUNT(*) - COUNT(product_width_cm) AS product_width_cm
    FROM olist_products_dataset
) s
CROSS JOIN LATERAL (
    VALUES
        ('product_id', product_id),
        ('product_category_name', product_category_name),
        ('product_name_lenght', product_name_lenght),
        ('product_description_lenght', product_description_lenght),
        ('product_photos_qty', product_photos_qty),
        ('product_weight_g', product_weight_g),
        ('product_length_cm', product_length_cm),
        ('product_height_cm', product_height_cm),
        ('product_width_cm', product_width_cm)
) v(column_name, null_count);


-- ------------------------------------------------------------
-- 2.7 Sellers
-- ------------------------------------------------------------

SELECT
    'olist_sellers_dataset' AS dataset,
    column_name,
    null_count,
    total_rows,
    total_rows - null_count AS non_null_count,
    ROUND(
        null_count::NUMERIC
        / NULLIF(total_rows, 0) * 100,
        4
    ) AS null_pct
FROM (
    SELECT
        COUNT(*) AS total_rows,
        COUNT(*) - COUNT(seller_id) AS seller_id,
        COUNT(*) - COUNT(seller_zip_code_prefix) AS seller_zip_code_prefix,
        COUNT(*) - COUNT(seller_city) AS seller_city,
        COUNT(*) - COUNT(seller_state) AS seller_state
    FROM olist_sellers_dataset
) s
CROSS JOIN LATERAL (
    VALUES
        ('seller_id', seller_id),
        ('seller_zip_code_prefix', seller_zip_code_prefix),
        ('seller_city', seller_city),
        ('seller_state', seller_state)
) v(column_name, null_count);


-- ------------------------------------------------------------
-- 2.8 Geolocation
-- ------------------------------------------------------------

SELECT
    'olist_geolocation_dataset' AS dataset,
    column_name,
    null_count,
    total_rows,
    total_rows - null_count AS non_null_count,
    ROUND(
        null_count::NUMERIC
        / NULLIF(total_rows, 0) * 100,
        4
    ) AS null_pct
FROM (
    SELECT
        COUNT(*) AS total_rows,
        COUNT(*) - COUNT(geolocation_zip_code_prefix) AS geolocation_zip_code_prefix,
        COUNT(*) - COUNT(geolocation_lat) AS geolocation_lat,
        COUNT(*) - COUNT(geolocation_lng) AS geolocation_lng,
        COUNT(*) - COUNT(geolocation_city) AS geolocation_city,
        COUNT(*) - COUNT(geolocation_state) AS geolocation_state
    FROM olist_geolocation_dataset
) s
CROSS JOIN LATERAL (
    VALUES
        ('geolocation_zip_code_prefix', geolocation_zip_code_prefix),
        ('geolocation_lat', geolocation_lat),
        ('geolocation_lng', geolocation_lng),
        ('geolocation_city', geolocation_city),
        ('geolocation_state', geolocation_state)
) v(column_name, null_count);


-- ------------------------------------------------------------
-- 2.9 Category Translation
-- ------------------------------------------------------------

SELECT
    'product_category_name_translation' AS dataset,
    column_name,
    null_count,
    total_rows,
    total_rows - null_count AS non_null_count,
    ROUND(
        null_count::NUMERIC
        / NULLIF(total_rows, 0) * 100,
        4
    ) AS null_pct
FROM (
    SELECT
        COUNT(*) AS total_rows,
        COUNT(*) - COUNT(product_category_name) AS product_category_name,
        COUNT(*) - COUNT(product_category_name_english) AS product_category_name_english
    FROM product_category_name_translation
) s
CROSS JOIN LATERAL (
    VALUES
        ('product_category_name', product_category_name),
        ('product_category_name_english', product_category_name_english)
) v(column_name, null_count);


-- ============================================================
-- SECTION 3 — FULL-ROW DUPLICATE PROFILING
-- ============================================================
-- Duplicate row count:
--   SUM(group_count - 1)
--
-- This identifies repeated complete records.
-- It does NOT imply that every duplicate is erroneous.
-- ============================================================

WITH customers_full AS (
    SELECT
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state,
        COUNT(*) AS cnt
    FROM olist_customers_dataset
    GROUP BY
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state
)
SELECT
    'olist_customers_dataset' AS dataset,
    SUM(cnt) AS total_rows,
    COUNT(*) AS distinct_rows,
    SUM(cnt - 1) AS duplicate_rows,
    ROUND(
        SUM(cnt - 1)::NUMERIC / NULLIF(SUM(cnt), 0) * 100,
        4
    ) AS duplicate_pct
FROM customers_full;


WITH geo_full AS (
    SELECT
        geolocation_zip_code_prefix,
        geolocation_lat,
        geolocation_lng,
        geolocation_city,
        geolocation_state,
        COUNT(*) AS cnt
    FROM olist_geolocation_dataset
    GROUP BY
        geolocation_zip_code_prefix,
        geolocation_lat,
        geolocation_lng,
        geolocation_city,
        geolocation_state
)
SELECT
    'olist_geolocation_dataset' AS dataset,
    SUM(cnt) AS total_rows,
    COUNT(*) AS distinct_rows,
    SUM(cnt - 1) AS duplicate_rows,
    ROUND(
        SUM(cnt - 1)::NUMERIC / NULLIF(SUM(cnt), 0) * 100,
        4
    ) AS duplicate_pct
FROM geo_full;


-- Repeat the same GROUP BY methodology for:
-- order_items
-- order_payments
-- order_reviews
-- orders
-- products
-- sellers
-- category_translation


-- ============================================================
-- SECTION 4 — KEY VALIDATION
-- ============================================================

-- ------------------------------------------------------------
-- 4.1 Customers — customer_id
-- ------------------------------------------------------------

SELECT
    'olist_customers_dataset' AS dataset,
    'customer_id' AS key_name,
    COUNT(*) AS total_rows,
    COUNT(customer_id) AS valid_key_rows,
    COUNT(*) - COUNT(customer_id) AS null_key_rows,
    COUNT(DISTINCT customer_id) AS distinct_key_count,
    COUNT(customer_id) - COUNT(DISTINCT customer_id) AS duplicate_key_rows,
    ROUND(
        (COUNT(customer_id) - COUNT(DISTINCT customer_id))::NUMERIC
        / NULLIF(COUNT(customer_id), 0) * 100,
        4
    ) AS duplicate_pct,
    ROUND(
        COUNT(DISTINCT customer_id)::NUMERIC
        / NULLIF(COUNT(customer_id), 0) * 100,
        4
    ) AS uniqueness_pct
FROM olist_customers_dataset;


-- ------------------------------------------------------------
-- 4.2 Orders — order_id
-- ------------------------------------------------------------

SELECT
    'olist_orders_dataset' AS dataset,
    'order_id' AS key_name,
    COUNT(*) AS total_rows,
    COUNT(order_id) AS valid_key_rows,
    COUNT(*) - COUNT(order_id) AS null_key_rows,
    COUNT(DISTINCT order_id) AS distinct_key_count,
    COUNT(order_id) - COUNT(DISTINCT order_id) AS duplicate_key_rows,
    ROUND(
        (COUNT(order_id) - COUNT(DISTINCT order_id))::NUMERIC
        / NULLIF(COUNT(order_id), 0) * 100,
        4
    ) AS duplicate_pct,
    ROUND(
        COUNT(DISTINCT order_id)::NUMERIC
        / NULLIF(COUNT(order_id), 0) * 100,
        4
    ) AS uniqueness_pct
FROM olist_orders_dataset;


-- ------------------------------------------------------------
-- 4.3 Order Items — (order_id, order_item_id)
-- ------------------------------------------------------------

WITH valid_keys AS (
    SELECT
        order_id,
        order_item_id
    FROM olist_order_items_dataset
    WHERE order_id IS NOT NULL
      AND order_item_id IS NOT NULL
),
key_groups AS (
    SELECT
        order_id,
        order_item_id,
        COUNT(*) AS key_count
    FROM valid_keys
    GROUP BY
        order_id,
        order_item_id
)
SELECT
    'olist_order_items_dataset' AS dataset,
    '(order_id, order_item_id)' AS key_name,
    (SELECT COUNT(*) FROM olist_order_items_dataset) AS total_rows,
    (SELECT COUNT(*) FROM valid_keys) AS valid_key_rows,
    (SELECT COUNT(*) FROM olist_order_items_dataset)
      - (SELECT COUNT(*) FROM valid_keys) AS null_key_rows,
    COUNT(*) AS distinct_key_count,
    COALESCE(SUM(key_count - 1), 0) AS duplicate_key_rows,
    ROUND(
        COALESCE(SUM(key_count - 1), 0)::NUMERIC
        / NULLIF((SELECT COUNT(*) FROM valid_keys), 0) * 100,
        4
    ) AS duplicate_pct,
    ROUND(
        COUNT(*)::NUMERIC
        / NULLIF((SELECT COUNT(*) FROM valid_keys), 0) * 100,
        4
    ) AS uniqueness_pct
FROM key_groups;


-- ------------------------------------------------------------
-- 4.4 Payments — (order_id, payment_sequential)
-- ------------------------------------------------------------

WITH valid_keys AS (
    SELECT
        order_id,
        payment_sequential
    FROM olist_order_payments_dataset
    WHERE order_id IS NOT NULL
      AND payment_sequential IS NOT NULL
),
key_groups AS (
    SELECT
        order_id,
        payment_sequential,
        COUNT(*) AS key_count
    FROM valid_keys
    GROUP BY
        order_id,
        payment_sequential
)
SELECT
    'olist_order_payments_dataset' AS dataset,
    '(order_id, payment_sequential)' AS key_name,
    (SELECT COUNT(*) FROM olist_order_payments_dataset) AS total_rows,
    (SELECT COUNT(*) FROM valid_keys) AS valid_key_rows,
    (SELECT COUNT(*) FROM olist_order_payments_dataset)
      - (SELECT COUNT(*) FROM valid_keys) AS null_key_rows,
    COUNT(*) AS distinct_key_count,
    COALESCE(SUM(key_count - 1), 0) AS duplicate_key_rows,
    ROUND(
        COALESCE(SUM(key_count - 1), 0)::NUMERIC
        / NULLIF((SELECT COUNT(*) FROM valid_keys), 0) * 100,
        4
    ) AS duplicate_pct,
    ROUND(
        COUNT(*)::NUMERIC
        / NULLIF((SELECT COUNT(*) FROM valid_keys), 0) * 100,
        4
    ) AS uniqueness_pct
FROM key_groups;


-- Repeat the single-column key validation for:
-- review_id
-- product_id
-- seller_id
-- product_category_name


-- ============================================================
-- SECTION 5 — REFERENTIAL INTEGRITY
-- ============================================================
-- NULL child keys are excluded from relationship matching.
--
-- match_count + non_match_count = child_rows_checked
--
-- Parent keys are DISTINCT to prevent duplicate parent records
-- from inflating relationship match counts.
-- ============================================================


-- Orders -> Customers

WITH parent_keys AS (
    SELECT DISTINCT customer_id
    FROM olist_customers_dataset
    WHERE customer_id IS NOT NULL
),
child_keys AS (
    SELECT customer_id
    FROM olist_orders_dataset
    WHERE customer_id IS NOT NULL
)
SELECT
    'Orders -> Customers' AS relationship,
    COUNT(*) AS child_rows_checked,
    COUNT(p.customer_id) AS match_count,
    COUNT(*) - COUNT(p.customer_id) AS non_match_count,
    ROUND(
        COUNT(p.customer_id)::NUMERIC
        / NULLIF(COUNT(*), 0) * 100,
        4
    ) AS match_pct,
    ROUND(
        (COUNT(*) - COUNT(p.customer_id))::NUMERIC
        / NULLIF(COUNT(*), 0) * 100,
        4
    ) AS non_match_pct
FROM child_keys c
LEFT JOIN parent_keys p
    ON c.customer_id = p.customer_id;


-- Order Items -> Orders

WITH parent_keys AS (
    SELECT DISTINCT order_id
    FROM olist_orders_dataset
    WHERE order_id IS NOT NULL
),
child_keys AS (
    SELECT order_id
    FROM olist_order_items_dataset
    WHERE order_id IS NOT NULL
)
SELECT
    'Order Items -> Orders' AS relationship,
    COUNT(*) AS child_rows_checked,
    COUNT(p.order_id) AS match_count,
    COUNT(*) - COUNT(p.order_id) AS non_match_count,
    ROUND(
        COUNT(p.order_id)::NUMERIC
        / NULLIF(COUNT(*), 0) * 100,
        4
    ) AS match_pct,
    ROUND(
        (COUNT(*) - COUNT(p.order_id))::NUMERIC
        / NULLIF(COUNT(*), 0) * 100,
        4
    ) AS non_match_pct
FROM child_keys c
LEFT JOIN parent_keys p
    ON c.order_id = p.order_id;


-- Repeat for:
-- Order Items -> Products
-- Order Items -> Sellers
-- Payments -> Orders
-- Reviews -> Orders
-- Products -> Category Translation


-- ============================================================
-- SECTION 6 — ORPHAN / UNMATCHED KEYS
-- ============================================================

SELECT DISTINCT
    oi.product_id
FROM olist_order_items_dataset oi
LEFT JOIN olist_products_dataset p
    ON oi.product_id = p.product_id
WHERE oi.product_id IS NOT NULL
  AND p.product_id IS NULL;


SELECT DISTINCT
    oi.seller_id
FROM olist_order_items_dataset oi
LEFT JOIN olist_sellers_dataset s
    ON oi.seller_id = s.seller_id
WHERE oi.seller_id IS NOT NULL
  AND s.seller_id IS NULL;


SELECT DISTINCT
    oi.order_id
FROM olist_order_items_dataset oi
LEFT JOIN olist_orders_dataset o
    ON oi.order_id = o.order_id
WHERE oi.order_id IS NOT NULL
  AND o.order_id IS NULL;


SELECT DISTINCT
    op.order_id
FROM olist_order_payments_dataset op
LEFT JOIN olist_orders_dataset o
    ON op.order_id = o.order_id
WHERE op.order_id IS NOT NULL
  AND o.order_id IS NULL;


SELECT DISTINCT
    r.order_id
FROM olist_order_reviews_dataset r
LEFT JOIN olist_orders_dataset o
    ON r.order_id = o.order_id
WHERE r.order_id IS NOT NULL
  AND o.order_id IS NULL;


SELECT DISTINCT
    p.product_category_name
FROM olist_products_dataset p
LEFT JOIN product_category_name_translation t
    ON p.product_category_name = t.product_category_name
WHERE p.product_category_name IS NOT NULL
  AND t.product_category_name IS NULL;


-- ZIP relationships are treated as lookup/coverage relationships,
-- not conventional foreign-key constraints.

SELECT DISTINCT
    c.customer_zip_code_prefix
FROM olist_customers_dataset c
LEFT JOIN olist_geolocation_dataset g
    ON c.customer_zip_code_prefix = g.geolocation_zip_code_prefix
WHERE c.customer_zip_code_prefix IS NOT NULL
  AND g.geolocation_zip_code_prefix IS NULL;


SELECT DISTINCT
    s.seller_zip_code_prefix
FROM olist_sellers_dataset s
LEFT JOIN olist_geolocation_dataset g
    ON s.seller_zip_code_prefix = g.geolocation_zip_code_prefix
WHERE s.seller_zip_code_prefix IS NOT NULL
  AND g.geolocation_zip_code_prefix IS NULL;


-- ============================================================
-- SECTION 7 — NUMERIC PROFILING
-- ============================================================
--
-- Statistics:
--   Count
--   Min
--   Q1
--   Median
--   Q3
--   Max
--   Mean
--   Standard deviation
--   IQR
--   Lower IQR bound
--   Upper IQR bound
--   Potential outlier count
--   Skewness
--
-- Outlier rule:
--
--   IQR = Q3 - Q1
--   Lower = Q1 - 1.5 * IQR
--   Upper = Q3 + 1.5 * IQR
--
-- Only non-null observations participate.
-- ============================================================


-- Example: order_items.price

WITH stats AS (
    SELECT
        COUNT(price) AS n,
        MIN(price) AS min_val,
        MAX(price) AS max_val,
        AVG(price) AS mean_val,
        STDDEV_SAMP(price) AS stddev_val,
        PERCENTILE_CONT(0.25)
            WITHIN GROUP (ORDER BY price) AS q1,
        PERCENTILE_CONT(0.50)
            WITHIN GROUP (ORDER BY price) AS median_val,
        PERCENTILE_CONT(0.75)
            WITHIN GROUP (ORDER BY price) AS q3
    FROM olist_order_items_dataset
),
bounds AS (
    SELECT
        *,
        q3 - q1 AS iqr,
        q1 - 1.5 * (q3 - q1) AS lower_bound,
        q3 + 1.5 * (q3 - q1) AS upper_bound
    FROM stats
),
outliers AS (
    SELECT
        COUNT(*) AS outlier_count
    FROM olist_order_items_dataset oi
    CROSS JOIN bounds b
    WHERE oi.price IS NOT NULL
      AND (
          oi.price < b.lower_bound
          OR oi.price > b.upper_bound
      )
)
SELECT
    'order_items.price' AS variable,
    b.n AS count_val,
    b.min_val,
    b.q1,
    b.median_val,
    b.q3,
    b.max_val,
    b.mean_val,
    b.stddev_val,
    b.iqr,
    b.lower_bound,
    b.upper_bound,
    o.outlier_count AS potential_outlier_count
FROM bounds b
CROSS JOIN outliers o;


-- Apply the same profiling methodology to:
--
-- order_items.freight_value
-- order_payments.payment_value
-- order_payments.payment_installments
-- order_reviews.review_score
-- products.product_weight_g
-- products.product_photos_qty
-- products.product_name_lenght
-- products.product_description_lenght
-- geolocation.geolocation_lat
-- geolocation.geolocation_lng


-- ============================================================
-- SECTION 8 — DATE PROFILING
-- ============================================================


-- ------------------------------------------------------------
-- 8.1 Date boundaries
-- ------------------------------------------------------------

SELECT
    'orders.order_purchase_timestamp' AS date_column,
    MIN(order_purchase_timestamp::timestamp) AS min_date,
    MAX(order_purchase_timestamp::timestamp) AS max_date,
    COUNT(*) - COUNT(order_purchase_timestamp) AS null_count
FROM olist_orders_dataset

UNION ALL

SELECT
    'orders.order_approved_at',
    MIN(order_approved_at::timestamp),
    MAX(order_approved_at::timestamp),
    COUNT(*) - COUNT(order_approved_at)
FROM olist_orders_dataset

UNION ALL

SELECT
    'orders.order_delivered_carrier_date',
    MIN(order_delivered_carrier_date::timestamp),
    MAX(order_delivered_carrier_date::timestamp),
    COUNT(*) - COUNT(order_delivered_carrier_date)
FROM olist_orders_dataset

UNION ALL

SELECT
    'orders.order_delivered_customer_date',
    MIN(order_delivered_customer_date::timestamp),
    MAX(order_delivered_customer_date::timestamp),
    COUNT(*) - COUNT(order_delivered_customer_date)
FROM olist_orders_dataset

UNION ALL

SELECT
    'orders.order_estimated_delivery_date',
    MIN(order_estimated_delivery_date::timestamp),
    MAX(order_estimated_delivery_date::timestamp),
    COUNT(*) - COUNT(order_estimated_delivery_date)
FROM olist_orders_dataset

UNION ALL

SELECT
    'reviews.review_creation_date',
    MIN(review_creation_date::timestamp),
    MAX(review_creation_date::timestamp),
    COUNT(*) - COUNT(review_creation_date)
FROM olist_order_reviews_dataset

UNION ALL

SELECT
    'reviews.review_answer_timestamp',
    MIN(review_answer_timestamp::timestamp),
    MAX(review_answer_timestamp::timestamp),
    COUNT(*) - COUNT(review_answer_timestamp)
FROM olist_order_reviews_dataset

UNION ALL

SELECT
    'order_items.shipping_limit_date',
    MIN(shipping_limit_date::timestamp),
    MAX(shipping_limit_date::timestamp),
    COUNT(*) - COUNT(shipping_limit_date)
FROM olist_order_items_dataset;


-- ------------------------------------------------------------
-- 8.2 Year / month distributions
-- ------------------------------------------------------------

SELECT
    EXTRACT(YEAR FROM order_purchase_timestamp::timestamp) AS year,
    EXTRACT(MONTH FROM order_purchase_timestamp::timestamp) AS month,
    COUNT(*) AS row_count
FROM olist_orders_dataset
WHERE order_purchase_timestamp IS NOT NULL
GROUP BY
    EXTRACT(YEAR FROM order_purchase_timestamp::timestamp),
    EXTRACT(MONTH FROM order_purchase_timestamp::timestamp)
ORDER BY year, month;


-- ------------------------------------------------------------
-- 8.3 Chronological consistency
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS approval_before_purchase_count
FROM olist_orders_dataset
WHERE order_approved_at IS NOT NULL
  AND order_purchase_timestamp IS NOT NULL
  AND order_approved_at::timestamp
      < order_purchase_timestamp::timestamp;


SELECT
    COUNT(*) AS carrier_before_purchase_count
FROM olist_orders_dataset
WHERE order_delivered_carrier_date IS NOT NULL
  AND order_purchase_timestamp IS NOT NULL
  AND order_delivered_carrier_date::timestamp
      < order_purchase_timestamp::timestamp;


SELECT
    COUNT(*) AS customer_delivery_before_purchase_count
FROM olist_orders_dataset
WHERE order_delivered_customer_date IS NOT NULL
  AND order_purchase_timestamp IS NOT NULL
  AND order_delivered_customer_date::timestamp
      < order_purchase_timestamp::timestamp;


SELECT
    COUNT(*) AS customer_delivery_before_carrier_count
FROM olist_orders_dataset
WHERE order_delivered_customer_date IS NOT NULL
  AND order_delivered_carrier_date IS NOT NULL
  AND order_delivered_customer_date::timestamp
      < order_delivered_carrier_date::timestamp;


SELECT
    COUNT(*) AS estimated_delivery_before_purchase_count
FROM olist_orders_dataset
WHERE order_estimated_delivery_date IS NOT NULL
  AND order_purchase_timestamp IS NOT NULL
  AND order_estimated_delivery_date::timestamp
      < order_purchase_timestamp::timestamp;


-- ============================================================
-- SECTION 9 — CATEGORICAL PROFILING
-- ============================================================

-- NULL is explicitly classified as missing rather than treated
-- as a meaningful category.

SELECT
    COALESCE(order_status, '[NULL]') AS category,
    COUNT(*) AS frequency,
    ROUND(
        COUNT(*)::NUMERIC
        / NULLIF((SELECT COUNT(*) FROM olist_orders_dataset), 0)
        * 100,
        4
    ) AS percentage_share,
    CASE
        WHEN COUNT(*)::NUMERIC
             / NULLIF((SELECT COUNT(*) FROM olist_orders_dataset), 0)
             * 100 < 1
        THEN 'YES'
        ELSE 'NO'
    END AS is_rare_category
FROM olist_orders_dataset
GROUP BY order_status
ORDER BY frequency DESC;


SELECT
    COALESCE(payment_type, '[NULL]') AS category,
    COUNT(*) AS frequency,
    ROUND(
        COUNT(*)::NUMERIC
        / NULLIF((SELECT COUNT(*) FROM olist_order_payments_dataset), 0)
        * 100,
        4
    ) AS percentage_share,
    CASE
        WHEN COUNT(*)::NUMERIC
             / NULLIF((SELECT COUNT(*) FROM olist_order_payments_dataset), 0)
             * 100 < 1
        THEN 'YES'
        ELSE 'NO'
    END AS is_rare_category
FROM olist_order_payments_dataset
GROUP BY payment_type
ORDER BY frequency DESC;


SELECT
    COALESCE(customer_state, '[NULL]') AS category,
    COUNT(*) AS frequency,
    ROUND(
        COUNT(*)::NUMERIC
        / NULLIF((SELECT COUNT(*) FROM olist_customers_dataset), 0)
        * 100,
        4
    ) AS percentage_share,
    CASE
        WHEN COUNT(*)::NUMERIC
             / NULLIF((SELECT COUNT(*) FROM olist_customers_dataset), 0)
             * 100 < 1
        THEN 'YES'
        ELSE 'NO'
    END AS is_rare_category
FROM olist_customers_dataset
GROUP BY customer_state
ORDER BY frequency DESC;


SELECT
    COALESCE(seller_state, '[NULL]') AS category,
    COUNT(*) AS frequency,
    ROUND(
        COUNT(*)::NUMERIC
        / NULLIF((SELECT COUNT(*) FROM olist_sellers_dataset), 0)
        * 100,
        4
    ) AS percentage_share,
    CASE
        WHEN COUNT(*)::NUMERIC
             / NULLIF((SELECT COUNT(*) FROM olist_sellers_dataset), 0)
             * 100 < 1
        THEN 'YES'
        ELSE 'NO'
    END AS is_rare_category
FROM olist_sellers_dataset
GROUP BY seller_state
ORDER BY frequency DESC;


-- Products: source category

SELECT
    COALESCE(product_category_name, '[NULL]') AS category,
    COUNT(*) AS frequency,
    ROUND(
        COUNT(*)::NUMERIC
        / NULLIF((SELECT COUNT(*) FROM olist_products_dataset), 0)
        * 100,
        4
    ) AS percentage_share,
    CASE
        WHEN COUNT(*)::NUMERIC
             / NULLIF((SELECT COUNT(*) FROM olist_products_dataset), 0)
             * 100 < 1
        THEN 'YES'
        ELSE 'NO'
    END AS is_rare_category
FROM olist_products_dataset
GROUP BY product_category_name
ORDER BY frequency DESC;


-- ============================================================
-- SECTION 10 — STRUCTURAL / ANOMALY INDICATORS
-- ============================================================
--
-- IMPORTANT:
-- These queries identify conditions.
--
-- They do NOT automatically declare business-rule-dependent
-- conditions as confirmed anomalies.
-- ============================================================


-- ------------------------------------------------------------
-- 10.1 Delivered orders missing lifecycle timestamps
-- ------------------------------------------------------------

SELECT
    COUNT(*) AS delivered_orders_missing_lifecycle_timestamps
FROM olist_orders_dataset
WHERE order_status = 'delivered'
  AND (
       order_approved_at IS NULL
       OR order_delivered_carrier_date IS NULL
       OR order_delivered_customer_date IS NULL
  );


-- ------------------------------------------------------------
-- 10.2 Duplicate review IDs
-- ------------------------------------------------------------

SELECT
    review_id,
    COUNT(*) AS occurrence_count
FROM olist_order_reviews_dataset
WHERE review_id IS NOT NULL
GROUP BY review_id
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC;


-- ------------------------------------------------------------
-- 10.3 Duplicate geolocation rows
-- ------------------------------------------------------------

SELECT
    geolocation_zip_code_prefix,
    geolocation_lat,
    geolocation_lng,
    geolocation_city,
    geolocation_state,
    COUNT(*) AS occurrence_count
FROM olist_geolocation_dataset
GROUP BY
    geolocation_zip_code_prefix,
    geolocation_lat,
    geolocation_lng,
    geolocation_city,
    geolocation_state
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC;


-- ------------------------------------------------------------
-- 10.4 IQR-based payment outliers
-- ------------------------------------------------------------

WITH stats AS (
    SELECT
        PERCENTILE_CONT(0.25)
            WITHIN GROUP (ORDER BY payment_value) AS q1,
        PERCENTILE_CONT(0.75)
            WITHIN GROUP (ORDER BY payment_value) AS q3
    FROM olist_order_payments_dataset
    WHERE payment_value IS NOT NULL
),
bounds AS (
    SELECT
        q1,
        q3,
        q3 - q1 AS iqr,
        q1 - 1.5 * (q3 - q1) AS lower_bound,
        q3 + 1.5 * (q3 - q1) AS upper_bound
    FROM stats
)
SELECT
    op.order_id,
    op.payment_sequential,
    op.payment_type,
    op.payment_value,
    b.lower_bound,
    b.upper_bound
FROM olist_order_payments_dataset op
CROSS JOIN bounds b
WHERE op.payment_value IS NOT NULL
  AND (
       op.payment_value < b.lower_bound
       OR op.payment_value > b.upper_bound
  );


-- ------------------------------------------------------------
-- 10.5 Zero-value observations
-- ------------------------------------------------------------

SELECT
    'order_items' AS source_table,
    COUNT(*) FILTER (WHERE price = 0) AS zero_price_count,
    COUNT(*) FILTER (WHERE freight_value = 0) AS zero_freight_count,
    0 AS zero_payment_count,
    0 AS zero_weight_count
FROM olist_order_items_dataset

UNION ALL

SELECT
    'order_payments',
    0,
    0,
    COUNT(*) FILTER (WHERE payment_value = 0),
    0
FROM olist_order_payments_dataset

UNION ALL

SELECT
    'products',
    0,
    0,
    0,
    COUNT(*) FILTER (WHERE product_weight_g = 0)
FROM olist_products_dataset;


-- ------------------------------------------------------------
-- 10.6 Invalid negative / bounded values
-- ------------------------------------------------------------

SELECT
    COUNT(*) FILTER (WHERE price < 0) AS negative_price_count,
    COUNT(*) FILTER (WHERE freight_value < 0) AS negative_freight_count
FROM olist_order_items_dataset;


SELECT
    COUNT(*) FILTER (WHERE payment_value < 0) AS negative_payment_value_count,
    COUNT(*) FILTER (WHERE payment_installments < 0)
        AS negative_payment_installments_count
FROM olist_order_payments_dataset;


-- Review score is bounded from 1 to 5.

SELECT
    COUNT(*) FILTER (
        WHERE review_score < 1
           OR review_score > 5
    ) AS invalid_review_score_count
FROM olist_order_reviews_dataset;


SELECT
    COUNT(*) FILTER (WHERE product_weight_g < 0)
        AS negative_product_weight_count,
    COUNT(*) FILTER (WHERE product_photos_qty < 0)
        AS negative_product_photos_count,
    COUNT(*) FILTER (WHERE product_name_lenght < 0)
        AS negative_product_name_length_count,
    COUNT(*) FILTER (WHERE product_description_lenght < 0)
        AS negative_product_description_length_count
FROM olist_products_dataset;


-- ------------------------------------------------------------
-- 10.7 Invalid delivery chronology
-- ------------------------------------------------------------

SELECT
    order_id,
    order_delivered_carrier_date,
    order_delivered_customer_date
FROM olist_orders_dataset
WHERE order_delivered_customer_date IS NOT NULL
  AND order_delivered_carrier_date IS NOT NULL
  AND order_delivered_customer_date::timestamp
      < order_delivered_carrier_date::timestamp;


-- ------------------------------------------------------------
-- 10.8 Referential mismatch
-- ------------------------------------------------------------

SELECT DISTINCT
    oi.product_id
FROM olist_order_items_dataset oi
LEFT JOIN olist_products_dataset p
    ON oi.product_id = p.product_id
WHERE oi.product_id IS NOT NULL
  AND p.product_id IS NULL;


-- ------------------------------------------------------------
-- 10.9 Rare order statuses
-- ------------------------------------------------------------

SELECT
    order_status,
    COUNT(*) AS frequency,
    ROUND(
        COUNT(*)::NUMERIC
        / NULLIF((SELECT COUNT(*) FROM olist_orders_dataset), 0)
        * 100,
        4
    ) AS percentage_share
FROM olist_orders_dataset
WHERE order_status IS NOT NULL
GROUP BY order_status
HAVING COUNT(*)::NUMERIC
       / NULLIF((SELECT COUNT(*) FROM olist_orders_dataset), 0)
       * 100 < 1
ORDER BY frequency;


-- ------------------------------------------------------------
-- 10.10 Untranslated product categories
-- ------------------------------------------------------------

SELECT DISTINCT
    p.product_category_name
FROM olist_products_dataset p
LEFT JOIN product_category_name_translation t
    ON p.product_category_name = t.product_category_name
WHERE p.product_category_name IS NOT NULL
  AND t.product_category_name IS NULL;


-- ============================================================
-- END OF PHASE 3 DATA PROFILING SQL
-- ============================================================