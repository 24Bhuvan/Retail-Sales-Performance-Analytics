-- ============================================================
-- RETAIL SALES PERFORMANCE ANALYTICS
-- Phase 14 — Business Metrics Calculation
-- File: sql/business_metrics_queries.sql
--
-- Purpose:
-- Generate baseline analytical tables for Phase 14.
--
-- Revenue Definition:
-- Revenue = Item Revenue / order_revenue
-- Freight is excluded from Revenue.
-- ============================================================


-- ============================================================
-- 1. MONTHLY SALES
-- ============================================================

WITH monthly_sales AS (
    SELECT
        ofe.year_month,

        SUM(ofe.order_revenue) AS monthly_revenue,

        COUNT(DISTINCT ofe.order_id) AS monthly_orders,

        COUNT(DISTINCT ofe.customer_unique_id) AS monthly_customers,

        SUM(ofe.order_revenue)
            / NULLIF(COUNT(DISTINCT ofe.order_id), 0)
            AS average_order_value

    FROM validation.orders_features AS ofe

    WHERE
        ofe.order_date IS NOT NULL
        AND ofe.order_revenue IS NOT NULL

    GROUP BY
        ofe.year_month
),

monthly_metrics AS (
    SELECT
        year_month,
        monthly_revenue,
        monthly_orders,
        monthly_customers,
        average_order_value,

        LAG(monthly_revenue) OVER (
            ORDER BY year_month
        ) AS previous_month_revenue,

        SUM(monthly_revenue) OVER (
            ORDER BY year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS rolling_3_month_revenue,

        SUM(monthly_revenue) OVER (
            ORDER BY year_month
            ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
        ) AS cumulative_revenue

    FROM monthly_sales
)

SELECT
    year_month,
    monthly_revenue,
    monthly_orders,
    monthly_customers,
    average_order_value,

    100.0
        * (
            monthly_revenue
            - previous_month_revenue
        )
        / NULLIF(previous_month_revenue, 0)
        AS monthly_revenue_growth,

    rolling_3_month_revenue,

    cumulative_revenue

FROM monthly_metrics

ORDER BY
    year_month;


-- ============================================================
-- 2. CATEGORY METRICS
-- ============================================================
-- Category comes from cleaned.products.
-- ============================================================

WITH category_metrics AS (
    SELECT
        COALESCE(
            p.product_category_name,
            'Unknown/Untranslated'
        ) AS product_category,

        SUM(oif.item_revenue) AS category_revenue,

        COUNT(DISTINCT oif.order_id) AS order_count,

        COUNT(*) AS item_count

    FROM validation.order_items_features AS oif

    LEFT JOIN cleaned.products AS p
        ON oif.product_id = p.product_id

    WHERE
        oif.item_revenue IS NOT NULL

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
        / NULLIF(
            SUM(category_revenue) OVER (),
            0
        )
        AS category_revenue_share,

    order_count,
    item_count

FROM category_metrics

ORDER BY
    category_revenue DESC,
    product_category;


-- ============================================================
-- 3. PRODUCT METRICS
-- ============================================================

WITH product_metrics AS (
    SELECT
        product_id,

        SUM(item_revenue)
            AS product_revenue,

        COUNT(DISTINCT order_id)
            AS order_count,

        COUNT(*)
            AS item_count

    FROM validation.order_items_features

    WHERE
        product_id IS NOT NULL
        AND item_revenue IS NOT NULL

    GROUP BY
        product_id
)

SELECT
    product_id,
    product_revenue,
    order_count,
    item_count,

    RANK() OVER (
        ORDER BY product_revenue DESC
    ) AS product_rank

FROM product_metrics

ORDER BY
    product_rank,
    product_id;


-- ============================================================
-- 4. REGIONAL METRICS
-- ============================================================

WITH regional_metrics AS (
    SELECT
        COALESCE(
            c.customer_state,
            'Unknown'
        ) AS customer_state,

        SUM(ofe.order_revenue)
            AS revenue,

        COUNT(DISTINCT ofe.order_id)
            AS orders,

        COUNT(DISTINCT ofe.customer_unique_id)
            AS customers,

        SUM(ofe.order_revenue)
            / NULLIF(
                COUNT(DISTINCT ofe.order_id),
                0
            )
            AS average_order_value

    FROM validation.orders_features AS ofe

    LEFT JOIN cleaned.customers AS c
        ON ofe.customer_id = c.customer_id

    WHERE
        ofe.order_revenue IS NOT NULL

    GROUP BY
        COALESCE(
            c.customer_state,
            'Unknown'
        )
)

SELECT
    customer_state,
    revenue,
    orders,
    customers,
    average_order_value,

    RANK() OVER (
        ORDER BY revenue DESC
    ) AS revenue_rank

FROM regional_metrics

ORDER BY
    revenue_rank,
    customer_state;


-- ============================================================
-- END
-- Phase 14 — Step 3
--
-- Outputs:
-- 1. Monthly Sales
-- 2. Category Metrics
-- 3. Product Metrics
-- 4. Regional Metrics
-- ============================================================