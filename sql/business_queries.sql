-- ============================================================
-- Retail Sales Performance Analytics
-- Phase 8 — SQL Development
-- Step 8.4 — Basic SQL Analysis
-- ============================================================

-- ============================================================
-- 1. TOTAL ORDERS
-- ============================================================
-- Grain: one row per order
-- Purpose: Count the total number of orders.

SELECT
    COUNT(*) AS total_orders
FROM analytics.fact_orders;


-- ============================================================
-- 2. TOTAL ORDER ITEMS
-- ============================================================
-- Grain: one row per order item
-- Purpose: Count the total number of order-item records.

SELECT
    COUNT(*) AS total_order_items
FROM analytics.fact_order_items;


-- ============================================================
-- 3. TOTAL PAYMENT VALUE
-- ============================================================
-- Grain: one row per payment sequence
-- Purpose: Calculate total recorded payment value.

SELECT
    SUM(payment_value) AS total_payment_value
FROM analytics.fact_payments;


-- ============================================================
-- 4. TOTAL ITEM PRICE
-- ============================================================
-- Grain: one row per order item
-- Purpose: Calculate total merchandise/item price.

SELECT
    SUM(price) AS total_item_price
FROM analytics.fact_order_items;


-- ============================================================
-- 5. TOTAL FREIGHT
-- ============================================================
-- Grain: one row per order item
-- Purpose: Calculate total freight value.

SELECT
    SUM(freight_value) AS total_freight_value
FROM analytics.fact_order_items;


-- ============================================================
-- 6. AVERAGE ORDER VALUE
-- ============================================================
-- Definition:
-- Total item price / number of distinct orders
--
-- Payment records are deliberately not joined here because
-- multiple payment records can exist for the same order.

SELECT
    SUM(price) / COUNT(DISTINCT order_id) AS average_order_value
FROM analytics.fact_order_items;


-- ============================================================
-- 7. AVERAGE ITEM PRICE
-- ============================================================
-- Grain: one row per order item
-- Purpose: Calculate the average merchandise price per item.

SELECT
    AVG(price) AS average_item_price
FROM analytics.fact_order_items;


-- ============================================================
-- 8. ORDERS BY STATUS
-- ============================================================
-- Purpose: Show the distribution of orders across order statuses.

SELECT
    s.order_status,
    COUNT(*) AS order_count
FROM analytics.fact_orders o
INNER JOIN analytics.dim_order_status s
    ON o.order_status_key = s.order_status_key
GROUP BY
    s.order_status
ORDER BY
    order_count DESC;


-- ============================================================
-- 9. ORDERS BY YEAR AND MONTH
-- ============================================================
-- Purpose: Show monthly order volume over time.

SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(*) AS order_count
FROM analytics.fact_orders o
INNER JOIN analytics.dim_date d
    ON o.purchase_date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    d.month_name
ORDER BY
    d.year,
    d.month;


-- ============================================================
-- 10. TOTAL CUSTOMERS
-- ============================================================
-- Purpose: Count customers in the analytical customer dimension.

SELECT
    COUNT(*) AS total_customers
FROM analytics.dim_customer;


-- ============================================================
-- 11. TOTAL SELLERS
-- ============================================================
-- Purpose: Count sellers in the analytical seller dimension.

SELECT
    COUNT(*) AS total_sellers
FROM analytics.dim_seller;


-- ============================================================
-- 12. TOTAL PRODUCTS
-- ============================================================
-- Purpose: Count products in the analytical product dimension.

SELECT
    COUNT(*) AS total_products
FROM analytics.dim_product;



-- ============================================================
-- Phase 8 — SQL Development
-- Step 8.5 — Business Analysis Queries
-- ============================================================


-- ============================================================
-- SALES ANALYSIS
-- ============================================================


-- ============================================================
-- 13. MONTHLY SALES
-- ============================================================
-- Definition:
-- Merchandise sales = SUM(order item price)
--
-- Grain: order item
-- Date: order purchase date

SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(SUM(oi.price), 2) AS monthly_sales
FROM analytics.fact_order_items oi
INNER JOIN analytics.dim_date d
    ON oi.order_date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    d.month_name
ORDER BY
    d.year,
    d.month;


-- ============================================================
-- 14. YEARLY SALES
-- ============================================================

SELECT
    d.year,
    ROUND(SUM(oi.price), 2) AS yearly_sales
FROM analytics.fact_order_items oi
INNER JOIN analytics.dim_date d
    ON oi.order_date_key = d.date_key
GROUP BY
    d.year
ORDER BY
    d.year;


-- ============================================================
-- 15. MONTHLY SALES GROWTH
-- ============================================================
-- LAG compares the current month's sales with the previous
-- chronological month.

WITH monthly_sales AS (
    SELECT
        d.year,
        d.month,
        d.month_name,
        SUM(oi.price) AS sales
    FROM analytics.fact_order_items oi
    INNER JOIN analytics.dim_date d
        ON oi.order_date_key = d.date_key
    GROUP BY
        d.year,
        d.month,
        d.month_name
),
sales_with_previous AS (
    SELECT
        year,
        month,
        month_name,
        sales,
        LAG(sales) OVER (
            ORDER BY year, month
        ) AS previous_month_sales
    FROM monthly_sales
)
SELECT
    year,
    month,
    month_name,
    ROUND(sales, 2) AS sales,
    ROUND(previous_month_sales, 2) AS previous_month_sales,
    ROUND(
        100.0 * (sales - previous_month_sales)
        / NULLIF(previous_month_sales, 0),
        2
    ) AS monthly_growth_pct
FROM sales_with_previous
ORDER BY
    year,
    month;


-- ============================================================
-- 16. SALES BY CATEGORY
-- ============================================================

SELECT
    COALESCE(
        p.product_category_name_english,
        p.product_category_name,
        'Unknown'
    ) AS category,
    ROUND(SUM(oi.price), 2) AS sales
FROM analytics.fact_order_items oi
INNER JOIN analytics.dim_product p
    ON oi.product_key = p.product_key
GROUP BY
    COALESCE(
        p.product_category_name_english,
        p.product_category_name,
        'Unknown'
    )
ORDER BY
    sales DESC;


-- ============================================================
-- 17. SALES BY PRODUCT
-- ============================================================

SELECT
    p.product_id,
    COALESCE(
        p.product_category_name_english,
        p.product_category_name,
        'Unknown'
    ) AS category,
    COUNT(*) AS units_sold,
    ROUND(SUM(oi.price), 2) AS sales
FROM analytics.fact_order_items oi
INNER JOIN analytics.dim_product p
    ON oi.product_key = p.product_key
GROUP BY
    p.product_id,
    COALESCE(
        p.product_category_name_english,
        p.product_category_name,
        'Unknown'
    )
ORDER BY
    sales DESC;


-- ============================================================
-- 18. SALES BY SELLER
-- ============================================================

SELECT
    s.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(*) AS units_sold,
    COUNT(DISTINCT oi.order_id) AS orders,
    ROUND(SUM(oi.price), 2) AS sales,
    ROUND(AVG(oi.price), 2) AS average_item_price
FROM analytics.fact_order_items oi
INNER JOIN analytics.dim_seller s
    ON oi.seller_key = s.seller_key
GROUP BY
    s.seller_id,
    s.seller_city,
    s.seller_state
ORDER BY
    sales DESC;


-- ============================================================
-- 19. SALES BY STATE
-- ============================================================
-- Seller state is used because the sales fact is directly
-- associated with sellers.

SELECT
    s.seller_state,
    COUNT(DISTINCT oi.order_id) AS orders,
    COUNT(*) AS units_sold,
    ROUND(SUM(oi.price), 2) AS sales
FROM analytics.fact_order_items oi
INNER JOIN analytics.dim_seller s
    ON oi.seller_key = s.seller_key
GROUP BY
    s.seller_state
ORDER BY
    sales DESC;


-- ============================================================
-- 20. TOP 10 PRODUCTS
-- ============================================================

SELECT
    p.product_id,
    COALESCE(
        p.product_category_name_english,
        p.product_category_name,
        'Unknown'
    ) AS category,
    COUNT(*) AS units_sold,
    ROUND(SUM(oi.price), 2) AS sales
FROM analytics.fact_order_items oi
INNER JOIN analytics.dim_product p
    ON oi.product_key = p.product_key
GROUP BY
    p.product_id,
    COALESCE(
        p.product_category_name_english,
        p.product_category_name,
        'Unknown'
    )
ORDER BY
    sales DESC
LIMIT 10;


-- ============================================================
-- 21. TOP 10 SELLERS
-- ============================================================

SELECT
    s.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(DISTINCT oi.order_id) AS orders,
    COUNT(*) AS units_sold,
    ROUND(SUM(oi.price), 2) AS sales
FROM analytics.fact_order_items oi
INNER JOIN analytics.dim_seller s
    ON oi.seller_key = s.seller_key
GROUP BY
    s.seller_id,
    s.seller_city,
    s.seller_state
ORDER BY
    sales DESC
LIMIT 10;


-- ============================================================
-- CUSTOMER ANALYSIS
-- ============================================================


-- ============================================================
-- 22. ORDERS PER CUSTOMER
-- ============================================================

SELECT
    c.customer_id,
    c.customer_city,
    c.customer_state,
    COUNT(o.order_key) AS order_count
FROM analytics.dim_customer c
LEFT JOIN analytics.fact_orders o
    ON c.customer_key = o.customer_key
GROUP BY
    c.customer_id,
    c.customer_city,
    c.customer_state
ORDER BY
    order_count DESC,
    c.customer_id;


-- ============================================================
-- 23. REPEAT CUSTOMERS
-- ============================================================
-- Definition:
-- Customers with more than one order.

SELECT
    COUNT(*) AS repeat_customer_count
FROM (
    SELECT
        customer_key
    FROM analytics.fact_orders
    GROUP BY
        customer_key
    HAVING COUNT(*) > 1
) repeat_customers;


-- ============================================================
-- 24. CUSTOMER PURCHASE FREQUENCY
-- ============================================================
-- Distribution of customers by number of orders.

WITH customer_orders AS (
    SELECT
        customer_key,
        COUNT(*) AS order_count
    FROM analytics.fact_orders
    GROUP BY
        customer_key
)
SELECT
    order_count,
    COUNT(*) AS customer_count
FROM customer_orders
GROUP BY
    order_count
ORDER BY
    order_count;


-- ============================================================
-- 25. TOP CUSTOMERS
-- ============================================================
-- Customer sales are calculated from order items and mapped
-- through fact_orders to the customer dimension.
--
-- The order-item table is aggregated by order first to avoid
-- mixing customer and item grains incorrectly.

WITH order_sales AS (
    SELECT
        oi.order_id,
        SUM(oi.price) AS order_sales
    FROM analytics.fact_order_items oi
    GROUP BY
        oi.order_id
)
SELECT
    c.customer_id,
    c.customer_city,
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(os.order_sales), 2) AS total_sales
FROM analytics.fact_orders o
INNER JOIN analytics.dim_customer c
    ON o.customer_key = c.customer_key
INNER JOIN order_sales os
    ON o.order_id = os.order_id
GROUP BY
    c.customer_id,
    c.customer_city,
    c.customer_state
ORDER BY
    total_sales DESC
LIMIT 10;


-- ============================================================
-- OPERATIONS ANALYSIS
-- ============================================================


-- ============================================================
-- 26. ORDER STATUS DISTRIBUTION
-- ============================================================

SELECT
    s.order_status,
    COUNT(*) AS order_count,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage_of_orders
FROM analytics.fact_orders o
INNER JOIN analytics.dim_order_status s
    ON o.order_status_key = s.order_status_key
GROUP BY
    s.order_status
ORDER BY
    order_count DESC;


-- ============================================================
-- 27. DELIVERY DURATION
-- ============================================================
-- Delivery duration:
-- Delivered customer date - purchase date
--
-- Only orders with both dates are included.

SELECT
    COUNT(*) AS delivered_orders,
    ROUND(
        AVG(
            delivered.full_date - purchase.full_date
        ),
        2
    ) AS average_delivery_days,
    MIN(
        delivered.full_date - purchase.full_date
    ) AS minimum_delivery_days,
    MAX(
        delivered.full_date - purchase.full_date
    ) AS maximum_delivery_days
FROM analytics.fact_orders o
INNER JOIN analytics.dim_date purchase
    ON o.purchase_date_key = purchase.date_key
INNER JOIN analytics.dim_date delivered
    ON o.delivered_customer_date_key = delivered.date_key
WHERE
    o.delivered_customer_date_key IS NOT NULL;


-- ============================================================
-- 28. ESTIMATED VS ACTUAL DELIVERY
-- ============================================================
-- Positive value = delivered after estimated date.
-- Negative value = delivered before estimated date.

SELECT
    COUNT(*) AS completed_orders,
    ROUND(
        AVG(
            delivered.full_date - estimated.full_date
        ),
        2
    ) AS average_delivery_variance_days,
    SUM(
        CASE
            WHEN delivered.full_date > estimated.full_date
            THEN 1
            ELSE 0
        END
    ) AS late_orders,
    SUM(
        CASE
            WHEN delivered.full_date <= estimated.full_date
            THEN 1
            ELSE 0
        END
    ) AS on_time_or_early_orders
FROM analytics.fact_orders o
INNER JOIN analytics.dim_date delivered
    ON o.delivered_customer_date_key = delivered.date_key
INNER JOIN analytics.dim_date estimated
    ON o.estimated_delivery_date_key = estimated.date_key
WHERE
    o.delivered_customer_date_key IS NOT NULL
    AND o.estimated_delivery_date_key IS NOT NULL;


-- ============================================================
-- 29. LATE DELIVERIES
-- ============================================================

WITH delivery_performance AS (
    SELECT
        o.order_id,
        delivered.full_date AS actual_delivery_date,
        estimated.full_date AS estimated_delivery_date
    FROM analytics.fact_orders o
    INNER JOIN analytics.dim_date delivered
        ON o.delivered_customer_date_key = delivered.date_key
    INNER JOIN analytics.dim_date estimated
        ON o.estimated_delivery_date_key = estimated.date_key
    WHERE
        o.delivered_customer_date_key IS NOT NULL
        AND o.estimated_delivery_date_key IS NOT NULL
)
SELECT
    COUNT(*) AS completed_orders,
    SUM(
        CASE
            WHEN actual_delivery_date > estimated_delivery_date
            THEN 1
            ELSE 0
        END
    ) AS late_orders,
    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN actual_delivery_date > estimated_delivery_date
                THEN 1
                ELSE 0
            END
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS late_delivery_rate_pct
FROM delivery_performance;


-- ============================================================
-- PAYMENT ANALYSIS
-- ============================================================


-- ============================================================
-- 30. PAYMENT METHODS
-- ============================================================

SELECT
    payment_type,
    COUNT(*) AS payment_records,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(payment_value), 2) AS payment_value
FROM analytics.fact_payments
GROUP BY
    payment_type
ORDER BY
    payment_value DESC;


-- ============================================================
-- 31. INSTALLMENT DISTRIBUTION
-- ============================================================

SELECT
    payment_installments,
    COUNT(*) AS payment_records,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(payment_value), 2) AS payment_value
FROM analytics.fact_payments
GROUP BY
    payment_installments
ORDER BY
    payment_installments;


-- ============================================================
-- 32. PAYMENT VALUE BY MONTH
-- ============================================================

SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(SUM(p.payment_value), 2) AS payment_value
FROM analytics.fact_payments p
INNER JOIN analytics.dim_date d
    ON p.payment_date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    d.month_name
ORDER BY
    d.year,
    d.month;


-- ============================================================
-- REVIEW ANALYSIS
-- ============================================================


-- ============================================================
-- 33. AVERAGE REVIEW SCORE
-- ============================================================

SELECT
    ROUND(AVG(review_score), 2) AS average_review_score
FROM analytics.fact_reviews
WHERE
    review_score IS NOT NULL;


-- ============================================================
-- 34. REVIEW SCORE DISTRIBUTION
-- ============================================================

SELECT
    review_score,
    COUNT(*) AS review_count,
    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        2
    ) AS percentage_of_reviews
FROM analytics.fact_reviews
WHERE
    review_score IS NOT NULL
GROUP BY
    review_score
ORDER BY
    review_score;


-- ============================================================
-- 35. REVIEW SCORE BY CATEGORY
-- ============================================================
-- Reviews are mapped to categories through order_id:
--
-- fact_reviews -> order_id -> fact_order_items -> product
--
-- Because an order can contain multiple products/categories,
-- the query uses DISTINCT order/category combinations before
-- aggregating reviews to avoid multiplying a review by the
-- number of items in the order.

WITH order_categories AS (
    SELECT DISTINCT
        oi.order_id,
        p.product_category_name_english AS category
    FROM analytics.fact_order_items oi
    INNER JOIN analytics.dim_product p
        ON oi.product_key = p.product_key
)
SELECT
    COALESCE(oc.category, 'Unknown') AS category,
    COUNT(fr.review_key) AS review_count,
    ROUND(AVG(fr.review_score), 2) AS average_review_score
FROM analytics.fact_reviews fr
INNER JOIN order_categories oc
    ON fr.order_id = oc.order_id
WHERE
    fr.review_score IS NOT NULL
GROUP BY
    COALESCE(oc.category, 'Unknown')
ORDER BY
    average_review_score DESC;


-- ============================================================
-- 36. REVIEW SCORE VS DELIVERY PERFORMANCE
-- ============================================================
-- Compare average review scores for late versus
-- on-time/early deliveries.

WITH delivery_performance AS (
    SELECT
        o.order_id,
        CASE
            WHEN delivered.full_date > estimated.full_date
                THEN 'Late'
            ELSE 'On Time / Early'
        END AS delivery_status
    FROM analytics.fact_orders o
    INNER JOIN analytics.dim_date delivered
        ON o.delivered_customer_date_key = delivered.date_key
    INNER JOIN analytics.dim_date estimated
        ON o.estimated_delivery_date_key = estimated.date_key
    WHERE
        o.delivered_customer_date_key IS NOT NULL
        AND o.estimated_delivery_date_key IS NOT NULL
),
order_reviews AS (
    SELECT
        order_id,
        AVG(review_score) AS average_review_score
    FROM analytics.fact_reviews
    WHERE
        review_score IS NOT NULL
    GROUP BY
        order_id
)
SELECT
    dp.delivery_status,
    COUNT(*) AS reviewed_orders,
    ROUND(AVG(orv.average_review_score), 2) AS average_review_score
FROM delivery_performance dp
INNER JOIN order_reviews orv
    ON dp.order_id = orv.order_id
GROUP BY
    dp.delivery_status
ORDER BY
    dp.delivery_status;