/*
===============================================================================
Retail Sales Performance Analytics
Phase 5 — Data Cleaning Strategy

File:
    sql/data_cleaning.sql

Purpose:
    Apply the approved Phase 5 cleaning rules in PostgreSQL.

Principles:
    1. Raw/source tables are never modified.
    2. Cleaned tables are generated separately.
    3. Legitimate NULL values are preserved.
    4. Exact duplicate geolocation rows are removed.
    5. review_id is NOT treated as a unique key.
    6. Invalid chronology timestamps are converted to NULL.
    7. Zero payment values are preserved.
    8. Zero freight values are preserved.
    9. Zero product weights are preserved.
   10. Invalid zero payment installments are converted to NULL.
   11. Product category gaps remain NULL.
   12. Translation gaps are not fabricated.
   13. Referential integrity is validated after cleaning.
   14. Before/after statistics are generated.

Source tables:
    public.olist_customers_dataset
    public.olist_geolocation_dataset
    public.olist_orders_dataset
    public.olist_order_items_dataset
    public.olist_order_payments_dataset
    public.olist_order_reviews_dataset
    public.olist_products_dataset
    public.olist_sellers_dataset
    public.product_category_name_translation

Output schema:
    cleaned

Output tables:
    cleaned.customers
    cleaned.geolocation
    cleaned.orders
    cleaned.order_items
    cleaned.payments
    cleaned.reviews
    cleaned.products
    cleaned.sellers
    cleaned.category_translation
    cleaned.cleaning_dataset_summary
===============================================================================
*/

\set ON_ERROR_STOP on

BEGIN;


/*
===============================================================================
0. SCHEMA SETUP
===============================================================================
*/

CREATE SCHEMA IF NOT EXISTS cleaned;


/*
===============================================================================
1. CLEAN CUSTOMERS
===============================================================================

Rules:
    - Preserve all customer records.
    - Preserve legitimate NULLs.
    - Do not remove customers because ZIP geolocation enrichment is missing.
    - Standardize city/state text.
*/

DROP TABLE IF EXISTS cleaned.customers CASCADE;

CREATE TABLE cleaned.customers AS
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    TRIM(UPPER(customer_city))  AS customer_city,
    TRIM(UPPER(customer_state)) AS customer_state
FROM public.olist_customers_dataset;


/*
===============================================================================
2. CLEAN GEOLOCATION
===============================================================================

Rule:
    Remove exact full-row duplicates.

The ZIP prefix is NOT treated as a unique key because multiple valid
geolocation records can exist for the same ZIP prefix.
*/

DROP TABLE IF EXISTS cleaned.geolocation CASCADE;

CREATE TABLE cleaned.geolocation AS
SELECT DISTINCT
    geolocation_zip_code_prefix,
    geolocation_lat,
    geolocation_lng,
    TRIM(UPPER(geolocation_city))  AS geolocation_city,
    TRIM(UPPER(geolocation_state)) AS geolocation_state
FROM public.olist_geolocation_dataset;


/*
===============================================================================
3. CLEAN ORDERS
===============================================================================

Chronology rules:

    carrier_date >= purchase_timestamp

    customer_delivery_date >= carrier_date

Treatment of invalid chronology:

    Convert the offending timestamp to NULL.

Do not:
    - delete the order
    - fabricate timestamps
    - modify purchase timestamp
*/

DROP TABLE IF EXISTS cleaned.orders CASCADE;

CREATE TABLE cleaned.orders AS
SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,

    CASE
        WHEN order_delivered_carrier_date IS NOT NULL
         AND order_purchase_timestamp IS NOT NULL
         AND order_delivered_carrier_date < order_purchase_timestamp
        THEN NULL
        ELSE order_delivered_carrier_date
    END AS order_delivered_carrier_date,

    CASE
        WHEN order_delivered_customer_date IS NOT NULL
         AND order_delivered_carrier_date IS NOT NULL
         AND order_delivered_customer_date < order_delivered_carrier_date
        THEN NULL
        ELSE order_delivered_customer_date
    END AS order_delivered_customer_date,

    order_estimated_delivery_date

FROM public.olist_orders_dataset;


/*
===============================================================================
4. CLEAN ORDER ITEMS
===============================================================================

Phase 4 findings:
    - No invalid negative price values.
    - No invalid negative freight values.
    - Zero freight values exist.

Rules:
    - Preserve zero freight values.
    - Preserve all valid order-item records.
    - Do not introduce a quantity column because the source does not contain it.

No rows are removed.
*/

DROP TABLE IF EXISTS cleaned.order_items CASCADE;

CREATE TABLE cleaned.order_items AS
SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value
FROM public.olist_order_items_dataset;


/*
===============================================================================
5. CLEAN PAYMENTS
===============================================================================

Rules:

    payment_installments = 0
        -> NULL

    payment_value = 0
        -> PRESERVE

Negative payment values:
    None expected from Phase 4, therefore no transformation required.
*/

DROP TABLE IF EXISTS cleaned.payments CASCADE;

CREATE TABLE cleaned.payments AS
SELECT
    order_id,
    payment_sequential,
    payment_type,

    CASE
        WHEN payment_installments = 0
        THEN NULL
        ELSE payment_installments
    END AS payment_installments,

    payment_value

FROM public.olist_order_payments_dataset;


/*
===============================================================================
6. CLEAN REVIEWS
===============================================================================

Important:

    review_id is NOT a unique source key.

Therefore:
    - Do not deduplicate using review_id.
    - Remove only exact full-row duplicates.
    - Preserve legitimate NULL review comments.
*/

DROP TABLE IF EXISTS cleaned.reviews CASCADE;

CREATE TABLE cleaned.reviews AS
SELECT DISTINCT
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date,
    review_answer_timestamp
FROM public.olist_order_reviews_dataset;


/*
===============================================================================
7. CLEAN PRODUCTS
===============================================================================

Rules:
    - Missing product category -> preserve NULL.
    - Missing product attributes -> preserve NULL.
    - Zero product weight -> preserve.
    - Do not fabricate categories.
*/

DROP TABLE IF EXISTS cleaned.products CASCADE;

CREATE TABLE cleaned.products AS
SELECT
    product_id,

    CASE
        WHEN NULLIF(TRIM(product_category_name), '') IS NULL
        THEN NULL
        ELSE LOWER(TRIM(product_category_name))
    END AS product_category_name,

    product_name_lenght,
    product_description_lenght,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm

FROM public.olist_products_dataset;


/*
===============================================================================
8. CLEAN SELLERS
===============================================================================

Rules:
    - Preserve all seller records.
    - Preserve legitimate NULLs.
    - Do not remove sellers because ZIP geolocation enrichment is unavailable.
    - Standardize city/state text.
*/

DROP TABLE IF EXISTS cleaned.sellers CASCADE;

CREATE TABLE cleaned.sellers AS
SELECT
    seller_id,
    seller_zip_code_prefix,
    TRIM(UPPER(seller_city))  AS seller_city,
    TRIM(UPPER(seller_state)) AS seller_state
FROM public.olist_sellers_dataset;


/*
===============================================================================
9. CLEAN CATEGORY TRANSLATION
===============================================================================

Rules:
    - Standardize text.
    - Preserve validated translations.
    - Do not fabricate missing translations.
*/

DROP TABLE IF EXISTS cleaned.category_translation CASCADE;

CREATE TABLE cleaned.category_translation AS
SELECT DISTINCT
    LOWER(TRIM(product_category_name)) AS product_category_name,
    LOWER(TRIM(product_category_name_english))
        AS product_category_name_english
FROM public.product_category_name_translation;


/*
===============================================================================
10. PRIMARY KEYS
===============================================================================

review_id is intentionally excluded because Phase 2 established that it
is not a unique source identifier.
*/

ALTER TABLE cleaned.customers
    ADD CONSTRAINT pk_cleaned_customers
    PRIMARY KEY (customer_id);

ALTER TABLE cleaned.orders
    ADD CONSTRAINT pk_cleaned_orders
    PRIMARY KEY (order_id);

ALTER TABLE cleaned.products
    ADD CONSTRAINT pk_cleaned_products
    PRIMARY KEY (product_id);

ALTER TABLE cleaned.sellers
    ADD CONSTRAINT pk_cleaned_sellers
    PRIMARY KEY (seller_id);

ALTER TABLE cleaned.order_items
    ADD CONSTRAINT pk_cleaned_order_items
    PRIMARY KEY (order_id, order_item_id);

ALTER TABLE cleaned.payments
    ADD CONSTRAINT pk_cleaned_payments
    PRIMARY KEY (order_id, payment_sequential);

ALTER TABLE cleaned.category_translation
    ADD CONSTRAINT pk_cleaned_category_translation
    PRIMARY KEY (product_category_name);


/*
===============================================================================
11. FOREIGN KEYS
===============================================================================
*/

ALTER TABLE cleaned.orders
    ADD CONSTRAINT fk_cleaned_orders_customer
    FOREIGN KEY (customer_id)
    REFERENCES cleaned.customers(customer_id);

ALTER TABLE cleaned.order_items
    ADD CONSTRAINT fk_cleaned_order_items_order
    FOREIGN KEY (order_id)
    REFERENCES cleaned.orders(order_id);

ALTER TABLE cleaned.order_items
    ADD CONSTRAINT fk_cleaned_order_items_product
    FOREIGN KEY (product_id)
    REFERENCES cleaned.products(product_id);

ALTER TABLE cleaned.order_items
    ADD CONSTRAINT fk_cleaned_order_items_seller
    FOREIGN KEY (seller_id)
    REFERENCES cleaned.sellers(seller_id);

ALTER TABLE cleaned.payments
    ADD CONSTRAINT fk_cleaned_payments_order
    FOREIGN KEY (order_id)
    REFERENCES cleaned.orders(order_id);

ALTER TABLE cleaned.reviews
    ADD CONSTRAINT fk_cleaned_reviews_order
    FOREIGN KEY (order_id)
    REFERENCES cleaned.orders(order_id);


/*
===============================================================================
12. INDEXES
===============================================================================
*/

CREATE INDEX IF NOT EXISTS idx_cleaned_orders_customer_id
    ON cleaned.orders(customer_id);

CREATE INDEX IF NOT EXISTS idx_cleaned_order_items_order_id
    ON cleaned.order_items(order_id);

CREATE INDEX IF NOT EXISTS idx_cleaned_order_items_product_id
    ON cleaned.order_items(product_id);

CREATE INDEX IF NOT EXISTS idx_cleaned_order_items_seller_id
    ON cleaned.order_items(seller_id);

CREATE INDEX IF NOT EXISTS idx_cleaned_payments_order_id
    ON cleaned.payments(order_id);

CREATE INDEX IF NOT EXISTS idx_cleaned_reviews_order_id
    ON cleaned.reviews(order_id);

CREATE INDEX IF NOT EXISTS idx_cleaned_products_category
    ON cleaned.products(product_category_name);


/*
===============================================================================
13. BEFORE / AFTER ROW COUNTS
===============================================================================
*/

DROP TABLE IF EXISTS cleaned.cleaning_dataset_summary CASCADE;

CREATE TABLE cleaned.cleaning_dataset_summary AS

SELECT
    'customers' AS dataset,
    (SELECT COUNT(*) FROM public.olist_customers_dataset) AS rows_before,
    (SELECT COUNT(*) FROM cleaned.customers) AS rows_after,
    (SELECT COUNT(*) FROM public.olist_customers_dataset)
        - (SELECT COUNT(*) FROM cleaned.customers) AS rows_removed

UNION ALL

SELECT
    'geolocation',
    (SELECT COUNT(*) FROM public.olist_geolocation_dataset),
    (SELECT COUNT(*) FROM cleaned.geolocation),
    (SELECT COUNT(*) FROM public.olist_geolocation_dataset)
        - (SELECT COUNT(*) FROM cleaned.geolocation)

UNION ALL

SELECT
    'orders',
    (SELECT COUNT(*) FROM public.olist_orders_dataset),
    (SELECT COUNT(*) FROM cleaned.orders),
    (SELECT COUNT(*) FROM public.olist_orders_dataset)
        - (SELECT COUNT(*) FROM cleaned.orders)

UNION ALL

SELECT
    'order_items',
    (SELECT COUNT(*) FROM public.olist_order_items_dataset),
    (SELECT COUNT(*) FROM cleaned.order_items),
    (SELECT COUNT(*) FROM public.olist_order_items_dataset)
        - (SELECT COUNT(*) FROM cleaned.order_items)

UNION ALL

SELECT
    'payments',
    (SELECT COUNT(*) FROM public.olist_order_payments_dataset),
    (SELECT COUNT(*) FROM cleaned.payments),
    (SELECT COUNT(*) FROM public.olist_order_payments_dataset)
        - (SELECT COUNT(*) FROM cleaned.payments)

UNION ALL

SELECT
    'reviews',
    (SELECT COUNT(*) FROM public.olist_order_reviews_dataset),
    (SELECT COUNT(*) FROM cleaned.reviews),
    (SELECT COUNT(*) FROM public.olist_order_reviews_dataset)
        - (SELECT COUNT(*) FROM cleaned.reviews)

UNION ALL

SELECT
    'products',
    (SELECT COUNT(*) FROM public.olist_products_dataset),
    (SELECT COUNT(*) FROM cleaned.products),
    (SELECT COUNT(*) FROM public.olist_products_dataset)
        - (SELECT COUNT(*) FROM cleaned.products)

UNION ALL

SELECT
    'sellers',
    (SELECT COUNT(*) FROM public.olist_sellers_dataset),
    (SELECT COUNT(*) FROM cleaned.sellers),
    (SELECT COUNT(*) FROM public.olist_sellers_dataset)
        - (SELECT COUNT(*) FROM cleaned.sellers)

UNION ALL

SELECT
    'category_translation',
    (SELECT COUNT(*) FROM public.product_category_name_translation),
    (SELECT COUNT(*) FROM cleaned.category_translation),
    (SELECT COUNT(*) FROM public.product_category_name_translation)
        - (SELECT COUNT(*) FROM cleaned.category_translation);


/*
===============================================================================
14. POST-CLEANING CHRONOLOGY VALIDATION
===============================================================================
*/

SELECT
    COUNT(*) AS invalid_carrier_dates_after_cleaning
FROM cleaned.orders
WHERE
    order_delivered_carrier_date IS NOT NULL
    AND order_purchase_timestamp IS NOT NULL
    AND order_delivered_carrier_date < order_purchase_timestamp;


SELECT
    COUNT(*) AS invalid_customer_delivery_dates_after_cleaning
FROM cleaned.orders
WHERE
    order_delivered_customer_date IS NOT NULL
    AND order_delivered_carrier_date IS NOT NULL
    AND order_delivered_customer_date < order_delivered_carrier_date;


/*
===============================================================================
15. PAYMENT INSTALLMENT VALIDATION
===============================================================================
*/

SELECT
    COUNT(*) AS zero_installments_after_cleaning
FROM cleaned.payments
WHERE payment_installments = 0;


/*
===============================================================================
16. NEGATIVE FINANCIAL VALUE VALIDATION
===============================================================================
*/

SELECT
    COUNT(*) AS negative_order_item_prices
FROM cleaned.order_items
WHERE price < 0;


SELECT
    COUNT(*) AS negative_freight_values
FROM cleaned.order_items
WHERE freight_value < 0;


SELECT
    COUNT(*) AS negative_payment_values
FROM cleaned.payments
WHERE payment_value < 0;


/*
===============================================================================
17. PRIMARY KEY VALIDATION
===============================================================================
*/

SELECT
    COUNT(*) AS duplicate_customer_ids
FROM (
    SELECT customer_id
    FROM cleaned.customers
    GROUP BY customer_id
    HAVING COUNT(*) > 1
) AS duplicates;


SELECT
    COUNT(*) AS duplicate_order_ids
FROM (
    SELECT order_id
    FROM cleaned.orders
    GROUP BY order_id
    HAVING COUNT(*) > 1
) AS duplicates;


SELECT
    COUNT(*) AS duplicate_product_ids
FROM (
    SELECT product_id
    FROM cleaned.products
    GROUP BY product_id
    HAVING COUNT(*) > 1
) AS duplicates;


SELECT
    COUNT(*) AS duplicate_seller_ids
FROM (
    SELECT seller_id
    FROM cleaned.sellers
    GROUP BY seller_id
    HAVING COUNT(*) > 1
) AS duplicates;


SELECT
    COUNT(*) AS duplicate_order_item_keys
FROM (
    SELECT
        order_id,
        order_item_id
    FROM cleaned.order_items
    GROUP BY
        order_id,
        order_item_id
    HAVING COUNT(*) > 1
) AS duplicates;


SELECT
    COUNT(*) AS duplicate_payment_keys
FROM (
    SELECT
        order_id,
        payment_sequential
    FROM cleaned.payments
    GROUP BY
        order_id,
        payment_sequential
    HAVING COUNT(*) > 1
) AS duplicates;


/*
===============================================================================
18. REFERENTIAL INTEGRITY VALIDATION
===============================================================================
*/

SELECT
    COUNT(*) AS orphan_orders
FROM cleaned.orders o
LEFT JOIN cleaned.customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;


SELECT
    COUNT(*) AS orphan_order_items_orders
FROM cleaned.order_items oi
LEFT JOIN cleaned.orders o
    ON oi.order_id = o.order_id
WHERE o.order_id IS NULL;


SELECT
    COUNT(*) AS orphan_order_items_products
FROM cleaned.order_items oi
LEFT JOIN cleaned.products p
    ON oi.product_id = p.product_id
WHERE p.product_id IS NULL;


SELECT
    COUNT(*) AS orphan_order_items_sellers
FROM cleaned.order_items oi
LEFT JOIN cleaned.sellers s
    ON oi.seller_id = s.seller_id
WHERE s.seller_id IS NULL;


SELECT
    COUNT(*) AS orphan_payments
FROM cleaned.payments p
LEFT JOIN cleaned.orders o
    ON p.order_id = o.order_id
WHERE o.order_id IS NULL;


SELECT
    COUNT(*) AS orphan_reviews
FROM cleaned.reviews r
LEFT JOIN cleaned.orders o
    ON r.order_id = o.order_id
WHERE o.order_id IS NULL;


/*
===============================================================================
19. PRODUCT CATEGORY GAP VALIDATION
===============================================================================
*/

SELECT
    COUNT(*) AS products_without_category
FROM cleaned.products
WHERE product_category_name IS NULL;


/*
===============================================================================
20. TRANSLATION COVERAGE VALIDATION
===============================================================================
*/

SELECT
    COUNT(*) AS products_without_english_translation
FROM cleaned.products p
LEFT JOIN cleaned.category_translation t
    ON p.product_category_name = t.product_category_name
WHERE
    p.product_category_name IS NOT NULL
    AND t.product_category_name IS NULL;


/*
===============================================================================
21. ZERO-VALUE VALIDATION
===============================================================================

These values are intentionally preserved.
*/

SELECT
    COUNT(*) AS zero_freight_values
FROM cleaned.order_items
WHERE freight_value = 0;


SELECT
    COUNT(*) AS zero_payment_values
FROM cleaned.payments
WHERE payment_value = 0;


SELECT
    COUNT(*) AS zero_product_weights
FROM cleaned.products
WHERE product_weight_g = 0;


/*
===============================================================================
22. FINAL CLEANING SUMMARY
===============================================================================
*/

SELECT
    dataset,
    rows_before,
    rows_after,
    rows_removed
FROM cleaned.cleaning_dataset_summary
ORDER BY dataset;


/*
===============================================================================
23. FINAL STATUS
===============================================================================
*/

SELECT
    'PHASE 5 SQL CLEANING COMPLETE' AS status;


COMMIT;