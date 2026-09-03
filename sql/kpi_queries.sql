-- ============================================================
-- RETAIL SALES PERFORMANCE ANALYTICS
-- Phase 14 — KPI Calculation
-- File: sql/kpi_queries.sql
-- Authority: docs/kpi_dictionary.md
--
-- Revenue = Item Revenue
-- Freight excluded from Revenue
-- Payment Value remains separate from Revenue
-- ============================================================


-- ============================================================
-- 1. SALES & REVENUE
-- KPIs:
-- 1. Total Revenue
-- 2. Total Order Value
-- 3. Average Order Value
-- 4. Monthly Revenue
-- 5. Monthly Revenue Growth
-- 6. Rolling 3-Month Revenue
-- ============================================================

SELECT
    SUM(order_revenue) AS total_revenue,

    SUM(total_order_value) AS total_order_value,

    SUM(order_revenue)
        / NULLIF(COUNT(order_revenue), 0)
        AS average_order_value

FROM validation.orders_features;


SELECT
    year_month,
    monthly_revenue,
    monthly_revenue_growth,
    three_month_rolling_revenue
FROM validation.monthly_features
ORDER BY year_month;


-- ============================================================
-- 2. ORDERS
-- KPIs:
-- 7. Total Orders
-- 8. Average Items per Order
-- ============================================================

SELECT
    COUNT(DISTINCT order_id) AS total_orders,

    AVG(items_per_order) AS average_items_per_order

FROM validation.orders_features;


-- ============================================================
-- 3. CUSTOMERS
-- KPIs:
-- 9. Total Customers
-- 10. Repeat Customer Rate
-- 11. Customer Lifetime Revenue
-- 12. Average Customer Order Value
-- ============================================================

SELECT
    COUNT(DISTINCT customer_unique_id) AS total_customers,

    100.0
        * COUNT(*) FILTER (
            WHERE repeat_customer_flag = 1
        )
        / NULLIF(COUNT(*), 0)
        AS repeat_customer_rate_pct,

    SUM(customer_lifetime_revenue)
        AS customer_lifetime_revenue,

    AVG(average_customer_order_value)
        AS average_customer_order_value

FROM validation.customer_features;


-- ============================================================
-- 4. PRODUCTS & CATEGORIES
-- KPIs:
-- 13. Category Revenue
-- 14. Category Revenue Share
-- 15. Product Revenue
--
-- product_category does not exist in validation.order_items_features.
-- Category is sourced from cleaned.products.
-- ============================================================

WITH category_revenue AS (
    SELECT
        COALESCE(
            p.product_category_name,
            'Unknown/Untranslated'
        ) AS product_category,

        SUM(oif.item_revenue) AS category_revenue

    FROM validation.order_items_features AS oif

    LEFT JOIN cleaned.products AS p
        ON oif.product_id = p.product_id

    GROUP BY
        COALESCE(
            p.product_category_name,
            'Unknown/Untranslated'
        )
)

SELECT
    product_category,
    category_revenue,

    100.0
        * category_revenue
        / NULLIF(SUM(category_revenue) OVER (), 0)
        AS category_revenue_share_pct

FROM category_revenue

ORDER BY category_revenue DESC;


SELECT
    product_id,

    SUM(item_revenue)
        AS product_revenue

FROM validation.order_items_features

WHERE product_id IS NOT NULL

GROUP BY product_id

ORDER BY product_revenue DESC;


-- ============================================================
-- 5. SELLERS
-- KPIs:
-- 16. Seller Revenue
-- 17. Seller Order Count
-- ============================================================

SELECT
    seller_id,

    SUM(item_revenue)
        AS seller_revenue,

    COUNT(DISTINCT order_id)
        AS seller_order_count

FROM validation.order_items_features

WHERE seller_id IS NOT NULL

GROUP BY seller_id

ORDER BY seller_revenue DESC;


-- ============================================================
-- 6. GEOGRAPHY
-- KPI:
-- 18. Revenue by Customer State
-- ============================================================

SELECT
    COALESCE(
        c.customer_state,
        'Unknown'
    ) AS customer_state,

    SUM(ofe.order_revenue)
        AS revenue_by_customer_state

FROM validation.orders_features AS ofe

LEFT JOIN cleaned.customers AS c
    ON ofe.customer_id = c.customer_id

GROUP BY
    COALESCE(
        c.customer_state,
        'Unknown'
    )

ORDER BY revenue_by_customer_state DESC;


-- ============================================================
-- 7. PAYMENTS
-- KPIs:
-- 19. Total Payment Value
-- 20. Payment Method Share
-- 21. Average Payment Installments
-- 22. Multi-Payment Order Rate
-- ============================================================

SELECT
    SUM(payment_value_per_order)
        AS total_payment_value,

    AVG(number_payment_installments)
        AS average_payment_installments,

    100.0
        * COUNT(*) FILTER (
            WHERE multi_payment_flag = 1
        )
        / NULLIF(
            COUNT(*) FILTER (
                WHERE payment_value_per_order IS NOT NULL
            ),
            0
        )
        AS multi_payment_order_rate_pct

FROM validation.orders_features;


SELECT
    payment_type,

    SUM(payment_value)
        AS payment_value,

    100.0
        * SUM(payment_value)
        / NULLIF(
            SUM(SUM(payment_value)) OVER (),
            0
        )
        AS payment_method_share_pct

FROM cleaned.payments

GROUP BY payment_type

ORDER BY payment_value DESC;


-- ============================================================
-- 8. DELIVERY & OPERATIONS
-- KPIs:
-- 23. Average Delivery Time
-- 24. Average Processing Time
-- 25. On-Time Delivery Rate
-- 26. Late Delivery Rate
-- 27. Average Delivery Difference
-- 28. Total Freight Value
-- ============================================================

SELECT
    AVG(delivery_time_days)
        AS average_delivery_time_days,

    AVG(processing_time_days)
        AS average_processing_time_days,

    100.0
        * COUNT(*) FILTER (
            WHERE on_time_delivery_flag = 1
        )
        / NULLIF(
            COUNT(*) FILTER (
                WHERE on_time_delivery_flag = 1
                   OR late_delivery_flag = 1
            ),
            0
        )
        AS on_time_delivery_rate_pct,

    100.0
        * COUNT(*) FILTER (
            WHERE late_delivery_flag = 1
        )
        / NULLIF(
            COUNT(*) FILTER (
                WHERE on_time_delivery_flag = 1
                   OR late_delivery_flag = 1
            ),
            0
        )
        AS late_delivery_rate_pct,

    AVG(delivery_difference_days)
        AS average_delivery_difference_days

FROM validation.orders_features;


SELECT
    SUM(freight_value)
        AS total_freight_value

FROM validation.order_items_features;


-- ============================================================
-- 9. CUSTOMER SATISFACTION
-- KPIs:
-- 29. Average Review Score
-- 30. Low Satisfaction Rate
-- 31. High Satisfaction Rate
-- ============================================================

SELECT
    AVG(review_score)
        AS average_review_score,

    100.0
        * COUNT(*) FILTER (
            WHERE low_review_flag = 1
        )
        / NULLIF(
            COUNT(review_score),
            0
        )
        AS low_satisfaction_rate_pct,

    100.0
        * COUNT(*) FILTER (
            WHERE high_review_flag = 1
        )
        / NULLIF(
            COUNT(review_score),
            0
        )
        AS high_satisfaction_rate_pct

FROM validation.orders_features;


-- ============================================================
-- 10. DIAGNOSTIC METRICS
-- KPI:
-- 32. Freight-to-Price Ratio
--
-- Rolling 3-Month Revenue and Multi-Payment Order Rate are
-- calculated in their relevant KPI sections above.
-- ============================================================

SELECT
    AVG(freight_to_price_ratio)
        AS freight_to_price_ratio

FROM validation.order_items_features

WHERE item_revenue IS NOT NULL
  AND item_revenue <> 0;


-- ============================================================
-- END
-- ============================================================