-- ============================================================
-- PHASE 3 — RAW DATABASE SCHEMA
-- ============================================================
-- Project: Retail Sales Performance Analytics
-- Database: retail_sales_analytics
-- Dialect: PostgreSQL
--
-- PURPOSE
-- -------
-- Creates PostgreSQL tables corresponding to the 9 raw Olist
-- CSV datasets.
--
-- DESIGN PRINCIPLES
-- -----------------
-- 1. Column names match the source CSV files.
-- 2. Data types are selected from the observed raw data structure.
-- 3. No cleaning or transformation is performed.
-- 4. Foreign keys are intentionally NOT enforced in the raw layer.
--    Referential integrity is profiled separately in Phase 3.
-- 5. Primary keys are applied only where the documented raw structure
--    supports uniqueness.
-- ============================================================


-- ============================================================
-- 1. CUSTOMERS
-- ============================================================

CREATE TABLE IF NOT EXISTS olist_customers_dataset (
    customer_id              TEXT PRIMARY KEY,
    customer_unique_id       TEXT,
    customer_zip_code_prefix INTEGER,
    customer_city            TEXT,
    customer_state           TEXT
);


-- ============================================================
-- 2. GEOLOCATION
-- ============================================================

CREATE TABLE IF NOT EXISTS olist_geolocation_dataset (
    geolocation_zip_code_prefix INTEGER,
    geolocation_lat              NUMERIC,
    geolocation_lng              NUMERIC,
    geolocation_city             TEXT,
    geolocation_state            TEXT
);


-- ============================================================
-- 3. ORDERS
-- ============================================================

CREATE TABLE IF NOT EXISTS olist_orders_dataset (
    order_id                         TEXT PRIMARY KEY,
    customer_id                      TEXT,
    order_status                     TEXT,
    order_purchase_timestamp         TIMESTAMP,
    order_approved_at                TIMESTAMP,
    order_delivered_carrier_date     TIMESTAMP,
    order_delivered_customer_date    TIMESTAMP,
    order_estimated_delivery_date    TIMESTAMP
);


-- ============================================================
-- 4. PRODUCTS
-- ============================================================

CREATE TABLE IF NOT EXISTS olist_products_dataset (
    product_id                    TEXT PRIMARY KEY,
    product_category_name         TEXT,
    product_name_lenght           INTEGER,
    product_description_lenght    INTEGER,
    product_photos_qty             INTEGER,
    product_weight_g               INTEGER,
    product_length_cm              INTEGER,
    product_height_cm              INTEGER,
    product_width_cm               INTEGER
);


-- ============================================================
-- 5. SELLERS
-- ============================================================

CREATE TABLE IF NOT EXISTS olist_sellers_dataset (
    seller_id              TEXT PRIMARY KEY,
    seller_zip_code_prefix INTEGER,
    seller_city            TEXT,
    seller_state           TEXT
);


-- ============================================================
-- 6. ORDER ITEMS
-- ============================================================

CREATE TABLE IF NOT EXISTS olist_order_items_dataset (
    order_id            TEXT,
    order_item_id       INTEGER,
    product_id          TEXT,
    seller_id           TEXT,
    shipping_limit_date TIMESTAMP,
    price               NUMERIC,
    freight_value       NUMERIC,

    PRIMARY KEY (order_id, order_item_id)
);


-- ============================================================
-- 7. ORDER PAYMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS olist_order_payments_dataset (
    order_id             TEXT,
    payment_sequential    INTEGER,
    payment_type         TEXT,
    payment_installments INTEGER,
    payment_value        NUMERIC,

    PRIMARY KEY (order_id, payment_sequential)
);


-- ============================================================
-- 8. ORDER REVIEWS
-- ============================================================

CREATE TABLE IF NOT EXISTS olist_order_reviews_dataset (
    review_id              TEXT,
    order_id               TEXT,
    review_score           INTEGER,
    review_comment_title   TEXT,
    review_comment_message TEXT,
    review_creation_date   TIMESTAMP,
    review_answer_timestamp TIMESTAMP
);


-- ============================================================
-- 9. CATEGORY TRANSLATION
-- ============================================================

CREATE TABLE IF NOT EXISTS product_category_name_translation (
    product_category_name         TEXT PRIMARY KEY,
    product_category_name_english TEXT
);


-- ============================================================
-- END OF RAW DATABASE SCHEMA
-- ============================================================