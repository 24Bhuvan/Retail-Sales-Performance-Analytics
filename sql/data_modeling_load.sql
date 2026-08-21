-- ============================================================
-- PHASE 6 — ANALYTICAL MODEL DIMENSION LOAD
-- ============================================================
-- Project: Retail Sales Performance Analytics
-- Database: retail_sales_analytics
-- Dialect: PostgreSQL
--
-- PURPOSE
-- -------
-- Populate the Phase 6 analytical dimensions from the cleaned
-- Olist datasets.
--
-- LOAD ORDER
-- ----------
-- 1. dim_customer
-- 2. dim_seller
-- 3. dim_product
-- 4. dim_geography
-- 5. dim_order_status
-- 6. dim_date
--
-- IMPORTANT
-- ---------
-- This script does NOT modify the cleaned source CSV files.
-- It is designed to be safely re-runnable.
-- ============================================================


BEGIN;


-- ============================================================
-- 1. DIM CUSTOMER
-- ============================================================
-- Grain:
-- One row per customer_id.
-- ============================================================

INSERT INTO analytics.dim_customer (
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
)
SELECT DISTINCT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM olist_customers_dataset
WHERE customer_id IS NOT NULL
ON CONFLICT (customer_id) DO UPDATE
SET
    customer_unique_id       = EXCLUDED.customer_unique_id,
    customer_zip_code_prefix = EXCLUDED.customer_zip_code_prefix,
    customer_city            = EXCLUDED.customer_city,
    customer_state           = EXCLUDED.customer_state;


-- ============================================================
-- 2. DIM SELLER
-- ============================================================
-- Grain:
-- One row per seller_id.
-- ============================================================

INSERT INTO analytics.dim_seller (
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
)
SELECT DISTINCT
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM olist_sellers_dataset
WHERE seller_id IS NOT NULL
ON CONFLICT (seller_id) DO UPDATE
SET
    seller_zip_code_prefix = EXCLUDED.seller_zip_code_prefix,
    seller_city            = EXCLUDED.seller_city,
    seller_state           = EXCLUDED.seller_state;


-- ============================================================
-- 3. DIM PRODUCT
-- ============================================================
-- Grain:
-- One row per product_id.
--
-- Category translation is incorporated here so Power BI and SQL
-- can use the English category directly from the product dimension.
-- ============================================================

INSERT INTO analytics.dim_product (
    product_id,
    product_category_name,
    product_category_name_english,
    product_name_lenght,
    product_description_lenght,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm
)
SELECT
    p.product_id,
    p.product_category_name,
    t.product_category_name_english,
    p.product_name_lenght,
    p.product_description_lenght,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
FROM olist_products_dataset p
LEFT JOIN product_category_name_translation t
    ON p.product_category_name = t.product_category_name
WHERE p.product_id IS NOT NULL
ON CONFLICT (product_id) DO UPDATE
SET
    product_category_name =
        EXCLUDED.product_category_name,

    product_category_name_english =
        EXCLUDED.product_category_name_english,

    product_name_lenght =
        EXCLUDED.product_name_lenght,

    product_description_lenght =
        EXCLUDED.product_description_lenght,

    product_photos_qty =
        EXCLUDED.product_photos_qty,

    product_weight_g =
        EXCLUDED.product_weight_g,

    product_length_cm =
        EXCLUDED.product_length_cm,

    product_height_cm =
        EXCLUDED.product_height_cm,

    product_width_cm =
        EXCLUDED.product_width_cm;


-- ============================================================
-- 4. DIM GEOGRAPHY
-- ============================================================
-- Grain:
-- One row per ZIP-code prefix.
--
-- The cleaned geolocation dataset may contain multiple records
-- for the same ZIP prefix. DISTINCT ON is used to retain one
-- representative record per ZIP prefix.
--
-- Ordering provides deterministic selection.
-- ============================================================

INSERT INTO analytics.dim_geography (
    zip_code_prefix,
    city,
    state,
    latitude,
    longitude
)
SELECT DISTINCT ON (geolocation_zip_code_prefix)
    geolocation_zip_code_prefix,
    geolocation_city,
    geolocation_state,
    geolocation_lat,
    geolocation_lng
FROM olist_geolocation_dataset
WHERE geolocation_zip_code_prefix IS NOT NULL
ORDER BY
    geolocation_zip_code_prefix,
    geolocation_city NULLS LAST,
    geolocation_state NULLS LAST,
    geolocation_lat NULLS LAST,
    geolocation_lng NULLS LAST
ON CONFLICT (zip_code_prefix) DO UPDATE
SET
    city      = EXCLUDED.city,
    state     = EXCLUDED.state,
    latitude  = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude;


-- ============================================================
-- 5. DIM ORDER STATUS
-- ============================================================
-- Grain:
-- One row per distinct order status.
-- ============================================================

INSERT INTO analytics.dim_order_status (
    order_status
)
SELECT DISTINCT
    order_status
FROM olist_orders_dataset
WHERE order_status IS NOT NULL
ON CONFLICT (order_status) DO NOTHING;


-- ============================================================
-- 6. DIM DATE
-- ============================================================
-- Grain:
-- One row per calendar date.
--
-- Date range is derived from the cleaned orders dataset.
--
-- The range covers:
--   minimum order_purchase_timestamp date
-- through
--   maximum order_estimated_delivery_date date
--
-- A small buffer is not added because the date dimension should
-- reflect the actual analytical source range.
-- ============================================================

INSERT INTO analytics.dim_date (
    date_key,
    full_date,
    year,
    quarter,
    quarter_name,
    month,
    month_name,
    month_year,
    week_of_year,
    day_of_month,
    day_of_week,
    day_name,
    is_weekend
)
SELECT
    TO_CHAR(d::DATE, 'YYYYMMDD')::INTEGER AS date_key,
    d::DATE AS full_date,

    EXTRACT(YEAR FROM d)::INTEGER AS year,

    EXTRACT(QUARTER FROM d)::INTEGER AS quarter,

    'Q' ||
    EXTRACT(QUARTER FROM d)::INTEGER AS quarter_name,

    EXTRACT(MONTH FROM d)::INTEGER AS month,

    TO_CHAR(d, 'FMMonth') AS month_name,

    TO_CHAR(d, 'YYYY-MM') AS month_year,

    EXTRACT(WEEK FROM d)::INTEGER AS week_of_year,

    EXTRACT(DAY FROM d)::INTEGER AS day_of_month,

    EXTRACT(ISODOW FROM d)::INTEGER AS day_of_week,

    TO_CHAR(d, 'FMDay') AS day_name,

    CASE
        WHEN EXTRACT(ISODOW FROM d) IN (6, 7)
            THEN TRUE
        ELSE FALSE
    END AS is_weekend

FROM generate_series(
    (
        SELECT MIN(order_purchase_timestamp)::DATE
        FROM olist_orders_dataset
        WHERE order_purchase_timestamp IS NOT NULL
    ),
    (
        SELECT MAX(order_estimated_delivery_date)::DATE
        FROM olist_orders_dataset
        WHERE order_estimated_delivery_date IS NOT NULL
    ),
    INTERVAL '1 day'
) AS series(d)

ON CONFLICT (date_key) DO UPDATE
SET
    full_date      = EXCLUDED.full_date,
    year           = EXCLUDED.year,
    quarter        = EXCLUDED.quarter,
    quarter_name   = EXCLUDED.quarter_name,
    month          = EXCLUDED.month,
    month_name     = EXCLUDED.month_name,
    month_year     = EXCLUDED.month_year,
    week_of_year   = EXCLUDED.week_of_year,
    day_of_month   = EXCLUDED.day_of_month,
    day_of_week    = EXCLUDED.day_of_week,
    day_name       = EXCLUDED.day_name,
    is_weekend     = EXCLUDED.is_weekend;


-- ============================================================
-- 7. LOAD SUMMARY
-- ============================================================

DO $$
BEGIN

    RAISE NOTICE '==============================================';
    RAISE NOTICE 'PHASE 6 DIMENSION LOAD COMPLETED';
    RAISE NOTICE '==============================================';

    RAISE NOTICE 'dim_customer rows: %',
        (SELECT COUNT(*) FROM analytics.dim_customer);

    RAISE NOTICE 'dim_seller rows: %',
        (SELECT COUNT(*) FROM analytics.dim_seller);

    RAISE NOTICE 'dim_product rows: %',
        (SELECT COUNT(*) FROM analytics.dim_product);

    RAISE NOTICE 'dim_geography rows: %',
        (SELECT COUNT(*) FROM analytics.dim_geography);

    RAISE NOTICE 'dim_order_status rows: %',
        (SELECT COUNT(*) FROM analytics.dim_order_status);

    RAISE NOTICE 'dim_date rows: %',
        (SELECT COUNT(*) FROM analytics.dim_date);

    RAISE NOTICE '==============================================';

END $$;


COMMIT;


-- ============================================================
-- END OF DIMENSION LOAD
-- ============================================================