-- ============================================================
-- PHASE 6 — ANALYTICAL MODEL FACT LOAD
-- ============================================================
-- Project: Retail Sales Performance Analytics
-- Database: retail_sales_analytics
-- Dialect: PostgreSQL
--
-- PURPOSE
-- -------
-- Populate Phase 6 analytical fact tables from the cleaned
-- Olist source tables.
--
-- FACT TABLES
-- -----------
-- 1. fact_orders
-- 2. fact_order_items
-- 3. fact_payments
-- 4. fact_reviews
--
-- GRAIN
-- -----
-- fact_orders:
--     One row per order_id
--
-- fact_order_items:
--     One row per order_id + order_item_id
--
-- fact_payments:
--     One row per order_id + payment_sequential
--
-- fact_reviews:
--     One row per source review record
--
-- IMPORTANT
-- ---------
-- - Source business IDs are preserved.
-- - Surrogate dimension keys are resolved through dimensions.
-- - No payment-to-order-item flattening is performed.
-- - No source data is modified.
-- ============================================================


BEGIN;


-- ============================================================
-- 1. FACT ORDERS
-- ============================================================
-- Grain:
-- One row per order_id.
--
-- Date keys are derived from the corresponding timestamps.
-- ============================================================

INSERT INTO analytics.fact_orders (
    order_id,
    customer_key,
    order_status_key,
    purchase_date_key,
    approved_date_key,
    delivered_carrier_date_key,
    delivered_customer_date_key,
    estimated_delivery_date_key
)
SELECT
    o.order_id,

    c.customer_key,

    s.order_status_key,

    TO_CHAR(
        o.order_purchase_timestamp::DATE,
        'YYYYMMDD'
    )::INTEGER AS purchase_date_key,

    TO_CHAR(
        o.order_approved_at::DATE,
        'YYYYMMDD'
    )::INTEGER AS approved_date_key,

    TO_CHAR(
        o.order_delivered_carrier_date::DATE,
        'YYYYMMDD'
    )::INTEGER AS delivered_carrier_date_key,

    TO_CHAR(
        o.order_delivered_customer_date::DATE,
        'YYYYMMDD'
    )::INTEGER AS delivered_customer_date_key,

    TO_CHAR(
        o.order_estimated_delivery_date::DATE,
        'YYYYMMDD'
    )::INTEGER AS estimated_delivery_date_key

FROM olist_orders_dataset o

INNER JOIN analytics.dim_customer c
    ON o.customer_id = c.customer_id

INNER JOIN analytics.dim_order_status s
    ON o.order_status = s.order_status

ON CONFLICT (order_id) DO UPDATE
SET
    customer_key =
        EXCLUDED.customer_key,

    order_status_key =
        EXCLUDED.order_status_key,

    purchase_date_key =
        EXCLUDED.purchase_date_key,

    approved_date_key =
        EXCLUDED.approved_date_key,

    delivered_carrier_date_key =
        EXCLUDED.delivered_carrier_date_key,

    delivered_customer_date_key =
        EXCLUDED.delivered_customer_date_key,

    estimated_delivery_date_key =
        EXCLUDED.estimated_delivery_date_key;


-- ============================================================
-- 2. FACT ORDER ITEMS
-- ============================================================
-- Grain:
-- One row per order_id + order_item_id.
--
-- Product and seller surrogate keys are resolved from dimensions.
--
-- Order date is derived from the order purchase timestamp.
-- ============================================================

INSERT INTO analytics.fact_order_items (
    order_id,
    order_item_id,
    product_key,
    seller_key,
    order_date_key,
    price,
    freight_value
)
SELECT
    oi.order_id,

    oi.order_item_id,

    p.product_key,

    s.seller_key,

    TO_CHAR(
        o.order_purchase_timestamp::DATE,
        'YYYYMMDD'
    )::INTEGER AS order_date_key,

    oi.price,

    oi.freight_value

FROM olist_order_items_dataset oi

INNER JOIN analytics.dim_product p
    ON oi.product_id = p.product_id

INNER JOIN analytics.dim_seller s
    ON oi.seller_id = s.seller_id

INNER JOIN olist_orders_dataset o
    ON oi.order_id = o.order_id

ON CONFLICT (order_id, order_item_id) DO UPDATE
SET
    product_key =
        EXCLUDED.product_key,

    seller_key =
        EXCLUDED.seller_key,

    order_date_key =
        EXCLUDED.order_date_key,

    price =
        EXCLUDED.price,

    freight_value =
        EXCLUDED.freight_value;


-- ============================================================
-- 3. FACT PAYMENTS
-- ============================================================
-- Grain:
-- One row per order_id + payment_sequential.
--
-- IMPORTANT:
-- No payment_date_key is populated because the Olist payment
-- source does not contain a payment timestamp.
--
-- Customer is resolved through fact_orders/dim_customer.
-- ============================================================

INSERT INTO analytics.fact_payments (
    order_id,
    payment_sequential,
    customer_key,
    payment_type,
    payment_installments,
    payment_value
)
SELECT
    op.order_id,

    op.payment_sequential,

    c.customer_key,

    op.payment_type,

    op.payment_installments,

    op.payment_value

FROM olist_order_payments_dataset op

INNER JOIN analytics.fact_orders fo
    ON op.order_id = fo.order_id

INNER JOIN analytics.dim_customer c
    ON fo.customer_key = c.customer_key

ON CONFLICT (order_id, payment_sequential) DO UPDATE
SET
    customer_key =
        EXCLUDED.customer_key,

    payment_type =
        EXCLUDED.payment_type,

    payment_installments =
        EXCLUDED.payment_installments,

    payment_value =
        EXCLUDED.payment_value;


-- ============================================================
-- 4. FACT REVIEWS
-- ============================================================
-- Grain:
-- One row per source review record.
--
-- review_id is NOT assumed to be unique.
-- review_key is generated automatically by BIGSERIAL.
--
-- Review creation date is used for review_date_key.
-- ============================================================

INSERT INTO analytics.fact_reviews (
    review_id,
    order_id,
    customer_key,
    review_date_key,
    review_score,
    review_comment_title,
    review_comment_message,
    review_answer_timestamp
)
SELECT
    r.review_id,

    r.order_id,

    c.customer_key,

    TO_CHAR(
        r.review_creation_date::DATE,
        'YYYYMMDD'
    )::INTEGER AS review_date_key,

    r.review_score,

    r.review_comment_title,

    r.review_comment_message,

    r.review_answer_timestamp

FROM olist_order_reviews_dataset r

INNER JOIN analytics.fact_orders fo
    ON r.order_id = fo.order_id

INNER JOIN analytics.dim_customer c
    ON fo.customer_key = c.customer_key;


-- ============================================================
-- 5. FACT LOAD SUMMARY
-- ============================================================

DO $$
BEGIN

    RAISE NOTICE '==============================================';
    RAISE NOTICE 'PHASE 6 FACT LOAD COMPLETED';
    RAISE NOTICE '==============================================';

    RAISE NOTICE 'fact_orders rows: %',
        (
            SELECT COUNT(*)
            FROM analytics.fact_orders
        );

    RAISE NOTICE 'fact_order_items rows: %',
        (
            SELECT COUNT(*)
            FROM analytics.fact_order_items
        );

    RAISE NOTICE 'fact_payments rows: %',
        (
            SELECT COUNT(*)
            FROM analytics.fact_payments
        );

    RAISE NOTICE 'fact_reviews rows: %',
        (
            SELECT COUNT(*)
            FROM analytics.fact_reviews
        );

    RAISE NOTICE '==============================================';

END $$;


COMMIT;


-- ============================================================
-- END OF FACT LOAD
-- ============================================================