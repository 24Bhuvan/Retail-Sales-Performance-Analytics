-- ============================================================
-- Retail Sales Performance Analytics
-- Phase 8 — SQL Development
-- Step 8.7 — SQL Validation
-- ============================================================


-- ============================================================
-- 1. ANALYTICAL TABLE ROW COUNTS
-- ============================================================

SELECT 'dim_customer' AS table_name, COUNT(*) AS row_count
FROM analytics.dim_customer
UNION ALL
SELECT 'dim_seller', COUNT(*)
FROM analytics.dim_seller
UNION ALL
SELECT 'dim_product', COUNT(*)
FROM analytics.dim_product
UNION ALL
SELECT 'dim_geography', COUNT(*)
FROM analytics.dim_geography
UNION ALL
SELECT 'fact_orders', COUNT(*)
FROM analytics.fact_orders
UNION ALL
SELECT 'fact_order_items', COUNT(*)
FROM analytics.fact_order_items
UNION ALL
SELECT 'fact_payments', COUNT(*)
FROM analytics.fact_payments
UNION ALL
SELECT 'fact_reviews', COUNT(*)
FROM analytics.fact_reviews
ORDER BY table_name;


-- ============================================================
-- 2. PRIMARY KEY UNIQUENESS
-- ============================================================

SELECT
    'fact_orders.order_key' AS check_name,
    COUNT(*) AS total_rows,
    COUNT(DISTINCT order_key) AS distinct_keys,
    CASE
        WHEN COUNT(*) = COUNT(DISTINCT order_key)
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM analytics.fact_orders

UNION ALL

SELECT
    'fact_order_items.order_item_key',
    COUNT(*),
    COUNT(DISTINCT order_item_key),
    CASE
        WHEN COUNT(*) = COUNT(DISTINCT order_item_key)
        THEN 'PASS'
        ELSE 'FAIL'
    END
FROM analytics.fact_order_items

UNION ALL

SELECT
    'fact_payments.payment_key',
    COUNT(*),
    COUNT(DISTINCT payment_key),
    CASE
        WHEN COUNT(*) = COUNT(DISTINCT payment_key)
        THEN 'PASS'
        ELSE 'FAIL'
    END
FROM analytics.fact_payments

UNION ALL

SELECT
    'fact_reviews.review_key',
    COUNT(*),
    COUNT(DISTINCT review_key),
    CASE
        WHEN COUNT(*) = COUNT(DISTINCT review_key)
        THEN 'PASS'
        ELSE 'FAIL'
    END
FROM analytics.fact_reviews;


-- ============================================================
-- 3. BUSINESS KEY UNIQUENESS
-- ============================================================

SELECT
    'fact_orders.order_id' AS check_name,
    COUNT(*) AS total_rows,
    COUNT(DISTINCT order_id) AS distinct_values,
    CASE
        WHEN COUNT(*) = COUNT(DISTINCT order_id)
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM analytics.fact_orders

UNION ALL

SELECT
    'fact_order_items.order_id + order_item_id',
    COUNT(*),
    COUNT(DISTINCT (order_id, order_item_id)),
    CASE
        WHEN COUNT(*) = COUNT(DISTINCT (order_id, order_item_id))
        THEN 'PASS'
        ELSE 'FAIL'
    END
FROM analytics.fact_order_items

UNION ALL

SELECT
    'fact_payments.order_id + payment_sequential',
    COUNT(*),
    COUNT(DISTINCT (order_id, payment_sequential)),
    CASE
        WHEN COUNT(*) = COUNT(DISTINCT (order_id, payment_sequential))
        THEN 'PASS'
        ELSE 'FAIL'
    END
FROM analytics.fact_payments;


-- ============================================================
-- 4. ORDER ITEM GRAIN VALIDATION
-- ============================================================

SELECT
    COUNT(*) AS order_item_rows,
    COUNT(DISTINCT order_id) AS distinct_orders,
    COUNT(DISTINCT (order_id, order_item_id)) AS distinct_order_items,
    CASE
        WHEN COUNT(*) =
             COUNT(DISTINCT (order_id, order_item_id))
        THEN 'PASS'
        ELSE 'FAIL'
    END AS grain_status
FROM analytics.fact_order_items;


-- ============================================================
-- 5. PAYMENT GRAIN VALIDATION
-- ============================================================

SELECT
    COUNT(*) AS payment_rows,
    COUNT(DISTINCT order_id) AS distinct_orders,
    COUNT(DISTINCT (order_id, payment_sequential))
        AS distinct_payment_records,
    CASE
        WHEN COUNT(*) =
             COUNT(DISTINCT (order_id, payment_sequential))
        THEN 'PASS'
        ELSE 'FAIL'
    END AS grain_status
FROM analytics.fact_payments;


-- ============================================================
-- 6. REVENUE RECONCILIATION
-- ============================================================

SELECT
    ROUND(SUM(price), 2) AS total_item_price,
    CASE
        WHEN ROUND(SUM(price), 2) = 13591643.70
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM analytics.fact_order_items;


-- ============================================================
-- 7. FREIGHT RECONCILIATION
-- ============================================================

SELECT
    ROUND(SUM(freight_value), 2) AS total_freight,
    CASE
        WHEN ROUND(SUM(freight_value), 2) = 2251909.54
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM analytics.fact_order_items;


-- ============================================================
-- 8. PAYMENT VALUE RECONCILIATION
-- ============================================================

SELECT
    ROUND(SUM(payment_value), 2) AS total_payment_value,
    CASE
        WHEN ROUND(SUM(payment_value), 2) = 16008872.12
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM analytics.fact_payments;


-- ============================================================
-- 9. ORDER COUNT RECONCILIATION
-- ============================================================

SELECT
    COUNT(*) AS total_orders,
    CASE
        WHEN COUNT(*) = 99441
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM analytics.fact_orders;


-- ============================================================
-- 10. CUSTOMER COUNT RECONCILIATION
-- ============================================================

SELECT
    COUNT(*) AS total_customers,
    CASE
        WHEN COUNT(*) = 99441
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM analytics.dim_customer;


-- ============================================================
-- 11. SELLER COUNT RECONCILIATION
-- ============================================================

SELECT
    COUNT(*) AS total_sellers,
    CASE
        WHEN COUNT(*) = 3095
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM analytics.dim_seller;


-- ============================================================
-- 12. PRODUCT COUNT RECONCILIATION
-- ============================================================

SELECT
    COUNT(*) AS total_products,
    CASE
        WHEN COUNT(*) = 32951
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM analytics.dim_product;


-- ============================================================
-- 13. REVIEW COUNT RECONCILIATION
-- ============================================================

SELECT
    COUNT(*) AS total_reviews,
    CASE
        WHEN COUNT(*) = 99224
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM analytics.fact_reviews;


-- ============================================================
-- 14. ORDER -> CUSTOMER JOIN INTEGRITY
-- ============================================================

SELECT
    COUNT(*) AS orders_before_join,
    COUNT(o.order_id) AS orders_after_join,
    COUNT(DISTINCT o.order_id) AS distinct_orders_after_join,
    CASE
        WHEN COUNT(*) = COUNT(DISTINCT o.order_id)
        THEN 'PASS'
        ELSE 'FAIL'
    END AS join_status
FROM analytics.fact_orders o
INNER JOIN analytics.dim_customer c
    ON o.customer_key = c.customer_key;


-- ============================================================
-- 15. ORDER ITEM -> PRODUCT JOIN INTEGRITY
-- ============================================================

SELECT
    COUNT(*) AS items_before_join,
    COUNT(oi.order_item_key) AS items_after_join,
    COUNT(DISTINCT oi.order_item_key) AS distinct_items_after_join,
    CASE
        WHEN COUNT(*) = COUNT(DISTINCT oi.order_item_key)
        THEN 'PASS'
        ELSE 'FAIL'
    END AS join_status
FROM analytics.fact_order_items oi
INNER JOIN analytics.dim_product p
    ON oi.product_key = p.product_key;


-- ============================================================
-- 16. ORDER ITEM -> SELLER JOIN INTEGRITY
-- ============================================================

SELECT
    COUNT(*) AS items_before_join,
    COUNT(oi.order_item_key) AS items_after_join,
    COUNT(DISTINCT oi.order_item_key) AS distinct_items_after_join,
    CASE
        WHEN COUNT(*) = COUNT(DISTINCT oi.order_item_key)
        THEN 'PASS'
        ELSE 'FAIL'
    END AS join_status
FROM analytics.fact_order_items oi
INNER JOIN analytics.dim_seller s
    ON oi.seller_key = s.seller_key;


-- ============================================================
-- 17. ORDER -> STATUS JOIN INTEGRITY
-- ============================================================

SELECT
    COUNT(*) AS orders_before_join,
    COUNT(o.order_id) AS orders_after_join,
    COUNT(DISTINCT o.order_id) AS distinct_orders_after_join,
    CASE
        WHEN COUNT(*) = COUNT(DISTINCT o.order_id)
        THEN 'PASS'
        ELSE 'FAIL'
    END AS join_status
FROM analytics.fact_orders o
INNER JOIN analytics.dim_order_status s
    ON o.order_status_key = s.order_status_key;


-- ============================================================
-- 18. DATE JOIN INTEGRITY
-- ============================================================

SELECT
    COUNT(*) AS order_items_before_join,
    COUNT(oi.order_item_key) AS order_items_after_join,
    COUNT(DISTINCT oi.order_item_key) AS distinct_items_after_join,
    CASE
        WHEN COUNT(*) = COUNT(DISTINCT oi.order_item_key)
        THEN 'PASS'
        ELSE 'FAIL'
    END AS join_status
FROM analytics.fact_order_items oi
INNER JOIN analytics.dim_date d
    ON oi.order_date_key = d.date_key;


-- ============================================================
-- 19. PAYMENT JOIN MULTIPLICATION TEST
-- ============================================================
-- Payment records must NOT be directly joined to order items
-- when calculating merchandise revenue.
--
-- This query demonstrates the grain difference.

SELECT
    COUNT(*) AS order_item_rows,
    COUNT(DISTINCT oi.order_item_key) AS distinct_items,
    COUNT(DISTINCT oi.order_id) AS distinct_orders,
    COUNT(DISTINCT p.payment_key) AS distinct_payments
FROM analytics.fact_order_items oi
LEFT JOIN analytics.fact_payments p
    ON oi.order_id = p.order_id;


-- ============================================================
-- 20. SAFE ORDER-LEVEL REVENUE RECONCILIATION
-- ============================================================

WITH order_sales AS (
    SELECT
        order_id,
        SUM(price) AS item_sales
    FROM analytics.fact_order_items
    GROUP BY order_id
)
SELECT
    ROUND(SUM(item_sales), 2) AS aggregated_order_sales,
    ROUND(
        (SELECT SUM(price)
         FROM analytics.fact_order_items),
        2
    ) AS direct_item_sales,
    CASE
        WHEN ROUND(SUM(item_sales), 2) =
             ROUND(
                 (SELECT SUM(price)
                  FROM analytics.fact_order_items),
                 2
             )
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM order_sales;


-- ============================================================
-- 21. REVIEW SCORE RANGE VALIDATION
-- ============================================================

SELECT
    MIN(review_score) AS minimum_score,
    MAX(review_score) AS maximum_score,
    CASE
        WHEN MIN(review_score) >= 1
         AND MAX(review_score) <= 5
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM analytics.fact_reviews
WHERE review_score IS NOT NULL;


-- ============================================================
-- 22. DELIVERY DATE LOGIC
-- ============================================================

SELECT
    COUNT(*) AS completed_orders,
    SUM(
        CASE
            WHEN delivered.full_date < purchase.full_date
            THEN 1
            ELSE 0
        END
    ) AS impossible_delivery_dates,
    CASE
        WHEN SUM(
            CASE
                WHEN delivered.full_date < purchase.full_date
                THEN 1
                ELSE 0
            END
        ) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM analytics.fact_orders o
INNER JOIN analytics.dim_date purchase
    ON o.purchase_date_key = purchase.date_key
INNER JOIN analytics.dim_date delivered
    ON o.delivered_customer_date_key = delivered.date_key
WHERE o.delivered_customer_date_key IS NOT NULL;


-- ============================================================
-- 23. MONTHLY SALES WINDOW VALIDATION
-- ============================================================

WITH monthly_sales AS (
    SELECT
        d.year,
        d.month,
        SUM(oi.price) AS sales
    FROM analytics.fact_order_items oi
    INNER JOIN analytics.dim_date d
        ON oi.order_date_key = d.date_key
    GROUP BY
        d.year,
        d.month
),
running_sales AS (
    SELECT
        year,
        month,
        sales,
        SUM(sales) OVER (
            ORDER BY year, month
        ) AS cumulative_sales
    FROM monthly_sales
)
SELECT
    ROUND(MAX(cumulative_sales), 2) AS final_cumulative_sales,
    ROUND(SUM(sales), 2) AS total_monthly_sales,
    CASE
        WHEN ROUND(MAX(cumulative_sales), 2) =
             ROUND(SUM(sales), 2)
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM running_sales;


-- ============================================================
-- 24. CATEGORY CONTRIBUTION VALIDATION
-- ============================================================

WITH category_sales AS (
    SELECT
        COALESCE(
            p.product_category_name_english,
            p.product_category_name,
            'Unknown'
        ) AS category,
        SUM(oi.price) AS sales
    FROM analytics.fact_order_items oi
    INNER JOIN analytics.dim_product p
        ON oi.product_key = p.product_key
    GROUP BY
        COALESCE(
            p.product_category_name_english,
            p.product_category_name,
            'Unknown'
        )
),
contributions AS (
    SELECT
        category,
        sales,
        100.0 * sales / SUM(sales) OVER () AS contribution_pct
    FROM category_sales
)
SELECT
    ROUND(SUM(contribution_pct), 2) AS total_contribution_pct,
    CASE
        WHEN ROUND(SUM(contribution_pct), 2) = 100.00
        THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM contributions;