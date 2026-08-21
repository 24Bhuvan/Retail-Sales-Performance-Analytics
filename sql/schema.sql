-- ============================================================
-- PHASE 6 — ANALYTICAL DATA MODEL / STAR SCHEMA
-- ============================================================
-- Project: Retail Sales Performance Analytics
-- Database: retail_sales_analytics
-- Dialect: PostgreSQL
--
-- PURPOSE
-- -------
-- Preserve the existing RAW source schema and create a separate
-- ANALYTICS layer based on a dimensional/star-schema design.
--
-- DESIGN PRINCIPLES
-- -----------------
-- 1. RAW tables remain unchanged.
-- 2. ANALYTICS tables are built from the cleaned data layer.
-- 3. Fact-table grain is explicitly defined.
-- 4. Dimensions contain descriptive attributes.
-- 5. Facts contain foreign keys and measurable transactional data.
-- 6. Payments and order items remain separate facts to prevent
--    many-to-many row multiplication.
-- 7. Reviews remain a separate fact because review_id is not unique.
-- 8. Date dimensions are role-playing dimensions for different
--    business dates.
-- 9. Foreign keys are enforced in the ANALYTICS layer.
-- ============================================================


-- ============================================================
-- 0. RAW SCHEMA
-- ============================================================
-- Existing Phase 3 raw schema is preserved.
-- ============================================================


-- ============================================================
-- 1. ANALYTICS SCHEMA
-- ============================================================

CREATE SCHEMA IF NOT EXISTS analytics;


-- ============================================================
-- 2. DIMENSION: DATE
-- ============================================================
-- Grain:
-- One row per calendar date.
--
-- Purpose:
-- Supports time-based analysis, filtering, and Power BI
-- time-intelligence.
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_key        INTEGER PRIMARY KEY,
    full_date       DATE NOT NULL UNIQUE,
    year            INTEGER NOT NULL,
    quarter         INTEGER NOT NULL,
    quarter_name    TEXT NOT NULL,
    month           INTEGER NOT NULL,
    month_name      TEXT NOT NULL,
    month_year      TEXT NOT NULL,
    week_of_year    INTEGER NOT NULL,
    day_of_month    INTEGER NOT NULL,
    day_of_week     INTEGER NOT NULL,
    day_name        TEXT NOT NULL,
    is_weekend      BOOLEAN NOT NULL
);


-- ============================================================
-- 3. DIMENSION: CUSTOMER
-- ============================================================
-- Grain:
-- One row per unique customer_id.
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.dim_customer (
    customer_key            BIGSERIAL PRIMARY KEY,
    customer_id             TEXT NOT NULL UNIQUE,
    customer_unique_id      TEXT,
    customer_zip_code_prefix INTEGER,
    customer_city           TEXT,
    customer_state          TEXT
);


-- ============================================================
-- 4. DIMENSION: SELLER
-- ============================================================
-- Grain:
-- One row per unique seller_id.
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.dim_seller (
    seller_key              BIGSERIAL PRIMARY KEY,
    seller_id               TEXT NOT NULL UNIQUE,
    seller_zip_code_prefix  INTEGER,
    seller_city              TEXT,
    seller_state             TEXT
);


-- ============================================================
-- 5. DIMENSION: PRODUCT
-- ============================================================
-- Grain:
-- One row per unique product_id.
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.dim_product (
    product_key                  BIGSERIAL PRIMARY KEY,
    product_id                   TEXT NOT NULL UNIQUE,
    product_category_name        TEXT,
    product_category_name_english TEXT,
    product_name_lenght          INTEGER,
    product_description_lenght   INTEGER,
    product_photos_qty           INTEGER,
    product_weight_g             INTEGER,
    product_length_cm            INTEGER,
    product_height_cm            INTEGER,
    product_width_cm             INTEGER
);


-- ============================================================
-- 6. DIMENSION: GEOGRAPHY
-- ============================================================
-- Grain:
-- One row per unique ZIP-code prefix.
--
-- Purpose:
-- Provides geographic enrichment for customers and sellers.
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.dim_geography (
    geography_key             BIGSERIAL PRIMARY KEY,
    zip_code_prefix            INTEGER NOT NULL UNIQUE,
    city                       TEXT,
    state                      TEXT,
    latitude                   NUMERIC,
    longitude                  NUMERIC
);


-- ============================================================
-- 7. DIMENSION: ORDER STATUS
-- ============================================================
-- Grain:
-- One row per distinct order status.
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.dim_order_status (
    order_status_key    SERIAL PRIMARY KEY,
    order_status        TEXT NOT NULL UNIQUE
);


-- ============================================================
-- 8. FACT: ORDERS
-- ============================================================
-- Grain:
-- One row per order.
--
-- Business purpose:
-- Supports:
--   - Total Orders
--   - Order Status Distribution
--   - Delivery analysis
--   - AOV denominator
--   - Customer order analysis
--
-- IMPORTANT:
-- Dates are stored as role-playing date foreign keys.
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.fact_orders (
    order_key                    BIGSERIAL PRIMARY KEY,

    order_id                     TEXT NOT NULL UNIQUE,

    customer_key                 BIGINT NOT NULL,
    order_status_key             INTEGER NOT NULL,

    purchase_date_key            INTEGER,
    approved_date_key            INTEGER,
    delivered_carrier_date_key   INTEGER,
    delivered_customer_date_key  INTEGER,
    estimated_delivery_date_key  INTEGER,

    CONSTRAINT fk_fact_orders_customer
        FOREIGN KEY (customer_key)
        REFERENCES analytics.dim_customer(customer_key),

    CONSTRAINT fk_fact_orders_status
        FOREIGN KEY (order_status_key)
        REFERENCES analytics.dim_order_status(order_status_key),

    CONSTRAINT fk_fact_orders_purchase_date
        FOREIGN KEY (purchase_date_key)
        REFERENCES analytics.dim_date(date_key),

    CONSTRAINT fk_fact_orders_approved_date
        FOREIGN KEY (approved_date_key)
        REFERENCES analytics.dim_date(date_key),

    CONSTRAINT fk_fact_orders_carrier_date
        FOREIGN KEY (delivered_carrier_date_key)
        REFERENCES analytics.dim_date(date_key),

    CONSTRAINT fk_fact_orders_customer_delivery_date
        FOREIGN KEY (delivered_customer_date_key)
        REFERENCES analytics.dim_date(date_key),

    CONSTRAINT fk_fact_orders_estimated_delivery_date
        FOREIGN KEY (estimated_delivery_date_key)
        REFERENCES analytics.dim_date(date_key)
);


-- ============================================================
-- 9. FACT: ORDER ITEMS / SALES
-- ============================================================
-- Grain:
-- One row per order_id + order_item_id.
--
-- Business purpose:
-- Supports:
--   - Product performance
--   - Category performance
--   - Seller performance
--   - Item price analysis
--   - Freight analysis
--
-- NOTE:
-- Olist order_items does not contain a quantity column.
-- Each row represents one order-item record.
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.fact_order_items (
    order_item_key          BIGSERIAL PRIMARY KEY,

    order_id                TEXT NOT NULL,
    order_item_id           INTEGER NOT NULL,

    product_key             BIGINT NOT NULL,
    seller_key              BIGINT NOT NULL,
    order_date_key          INTEGER,

    price                   NUMERIC(12,2),
    freight_value           NUMERIC(12,2),

    CONSTRAINT uq_fact_order_items
        UNIQUE (order_id, order_item_id),

    CONSTRAINT fk_fact_order_items_product
        FOREIGN KEY (product_key)
        REFERENCES analytics.dim_product(product_key),

    CONSTRAINT fk_fact_order_items_seller
        FOREIGN KEY (seller_key)
        REFERENCES analytics.dim_seller(seller_key),

    CONSTRAINT fk_fact_order_items_date
        FOREIGN KEY (order_date_key)
        REFERENCES analytics.dim_date(date_key)
);


-- ============================================================
-- 10. FACT: PAYMENTS
-- ============================================================
-- Grain:
-- One row per order_id + payment_sequential.
--
-- Business purpose:
-- Supports:
--   - Total Sales Revenue
--   - Payment Method Distribution
--   - Payment Installment Analysis
--   - Payment Value Analysis
--
-- IMPORTANT:
-- Kept separate from fact_order_items to prevent row
-- multiplication between multiple payments and multiple items.
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.fact_payments (
    payment_key             BIGSERIAL PRIMARY KEY,

    order_id                TEXT NOT NULL,
    payment_sequential      INTEGER NOT NULL,

    customer_key            BIGINT,
    payment_date_key        INTEGER,

    payment_type            TEXT,
    payment_installments    INTEGER,
    payment_value           NUMERIC(12,2),

    CONSTRAINT uq_fact_payments
        UNIQUE (order_id, payment_sequential),

    CONSTRAINT fk_fact_payments_customer
        FOREIGN KEY (customer_key)
        REFERENCES analytics.dim_customer(customer_key),

    CONSTRAINT fk_fact_payments_date
        FOREIGN KEY (payment_date_key)
        REFERENCES analytics.dim_date(date_key)
);


-- ============================================================
-- 11. FACT: REVIEWS
-- ============================================================
-- Grain:
-- One source review record associated with an order.
--
-- IMPORTANT:
-- review_id is NOT treated as a primary key because Phase 3
-- identified duplicate review_id values.
--
-- A generated review_key provides uniqueness in the analytical
-- table while preserving the original review_id.
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.fact_reviews (
    review_key               BIGSERIAL PRIMARY KEY,

    review_id                TEXT,
    order_id                 TEXT NOT NULL,

    customer_key             BIGINT,
    review_date_key          INTEGER,

    review_score             INTEGER,

    review_comment_title     TEXT,
    review_comment_message   TEXT,

    review_answer_timestamp  TIMESTAMP,

    CONSTRAINT fk_fact_reviews_customer
        FOREIGN KEY (customer_key)
        REFERENCES analytics.dim_customer(customer_key),

    CONSTRAINT fk_fact_reviews_date
        FOREIGN KEY (review_date_key)
        REFERENCES analytics.dim_date(date_key),

    CONSTRAINT chk_fact_reviews_score
        CHECK (
            review_score IS NULL
            OR review_score BETWEEN 1 AND 5
        )
);


-- ============================================================
-- 12. INDEXES — DIMENSIONS
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_dim_customer_state
    ON analytics.dim_customer(customer_state);

CREATE INDEX IF NOT EXISTS idx_dim_customer_zip
    ON analytics.dim_customer(customer_zip_code_prefix);

CREATE INDEX IF NOT EXISTS idx_dim_seller_state
    ON analytics.dim_seller(seller_state);

CREATE INDEX IF NOT EXISTS idx_dim_seller_zip
    ON analytics.dim_seller(seller_zip_code_prefix);

CREATE INDEX IF NOT EXISTS idx_dim_product_category
    ON analytics.dim_product(product_category_name);

CREATE INDEX IF NOT EXISTS idx_dim_product_category_english
    ON analytics.dim_product(product_category_name_english);

CREATE INDEX IF NOT EXISTS idx_dim_geography_state
    ON analytics.dim_geography(state);


-- ============================================================
-- 13. INDEXES — FACT ORDERS
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_orders_customer
    ON analytics.fact_orders(customer_key);

CREATE INDEX IF NOT EXISTS idx_fact_orders_status
    ON analytics.fact_orders(order_status_key);

CREATE INDEX IF NOT EXISTS idx_fact_orders_purchase_date
    ON analytics.fact_orders(purchase_date_key);

CREATE INDEX IF NOT EXISTS idx_fact_orders_approved_date
    ON analytics.fact_orders(approved_date_key);

CREATE INDEX IF NOT EXISTS idx_fact_orders_carrier_date
    ON analytics.fact_orders(delivered_carrier_date_key);

CREATE INDEX IF NOT EXISTS idx_fact_orders_customer_delivery_date
    ON analytics.fact_orders(delivered_customer_date_key);

CREATE INDEX IF NOT EXISTS idx_fact_orders_estimated_date
    ON analytics.fact_orders(estimated_delivery_date_key);


-- ============================================================
-- 14. INDEXES — FACT ORDER ITEMS
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_order_items_order
    ON analytics.fact_order_items(order_id);

CREATE INDEX IF NOT EXISTS idx_fact_order_items_product
    ON analytics.fact_order_items(product_key);

CREATE INDEX IF NOT EXISTS idx_fact_order_items_seller
    ON analytics.fact_order_items(seller_key);

CREATE INDEX IF NOT EXISTS idx_fact_order_items_date
    ON analytics.fact_order_items(order_date_key);


-- ============================================================
-- 15. INDEXES — FACT PAYMENTS
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_payments_order
    ON analytics.fact_payments(order_id);

CREATE INDEX IF NOT EXISTS idx_fact_payments_customer
    ON analytics.fact_payments(customer_key);

CREATE INDEX IF NOT EXISTS idx_fact_payments_date
    ON analytics.fact_payments(payment_date_key);

CREATE INDEX IF NOT EXISTS idx_fact_payments_type
    ON analytics.fact_payments(payment_type);


-- ============================================================
-- 16. INDEXES — FACT REVIEWS
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_reviews_order
    ON analytics.fact_reviews(order_id);

CREATE INDEX IF NOT EXISTS idx_fact_reviews_customer
    ON analytics.fact_reviews(customer_key);

CREATE INDEX IF NOT EXISTS idx_fact_reviews_date
    ON analytics.fact_reviews(review_date_key);

CREATE INDEX IF NOT EXISTS idx_fact_reviews_score
    ON analytics.fact_reviews(review_score);


-- ============================================================
-- 17. TABLE COMMENTS
-- ============================================================

COMMENT ON TABLE analytics.dim_date IS
'Calendar dimension. Grain: one row per calendar date.';

COMMENT ON TABLE analytics.dim_customer IS
'Customer dimension. Grain: one row per customer_id.';

COMMENT ON TABLE analytics.dim_seller IS
'Seller dimension. Grain: one row per seller_id.';

COMMENT ON TABLE analytics.dim_product IS
'Product dimension. Grain: one row per product_id.';

COMMENT ON TABLE analytics.dim_geography IS
'Geographic enrichment dimension. Grain: one row per ZIP-code prefix.';

COMMENT ON TABLE analytics.dim_order_status IS
'Order-status dimension. Grain: one row per order status.';

COMMENT ON TABLE analytics.fact_orders IS
'Order fact. Grain: one row per order_id.';

COMMENT ON TABLE analytics.fact_order_items IS
'Sales/order-item fact. Grain: one row per order_id + order_item_id.';

COMMENT ON TABLE analytics.fact_payments IS
'Payment fact. Grain: one row per order_id + payment_sequential.';

COMMENT ON TABLE analytics.fact_reviews IS
'Review fact. Grain: one source review record associated with an order.';


-- ============================================================
-- END OF PHASE 6 ANALYTICAL SCHEMA
-- ============================================================