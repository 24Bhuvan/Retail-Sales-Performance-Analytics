-- ============================================================
-- Retail Sales Performance Analytics
-- Phase 8 — SQL Development
-- Step 8.6 — Advanced SQL Analysis
-- ============================================================


-- ============================================================
-- 1. INNER JOIN — Orders with Customer Details
-- ============================================================

SELECT
    o.order_id,
    c.customer_id,
    c.customer_city,
    c.customer_state
FROM analytics.fact_orders o
INNER JOIN analytics.dim_customer c
    ON o.customer_key = c.customer_key
ORDER BY o.order_id
LIMIT 20;


-- ============================================================
-- 2. LEFT JOIN — Customers With and Without Orders
-- ============================================================

SELECT
    c.customer_id,
    c.customer_city,
    c.customer_state,
    COUNT(o.order_id) AS order_count
FROM analytics.dim_customer c
LEFT JOIN analytics.fact_orders o
    ON c.customer_key = o.customer_key
GROUP BY
    c.customer_id,
    c.customer_city,
    c.customer_state
ORDER BY
    order_count DESC,
    c.customer_id
LIMIT 20;


-- ============================================================
-- 3. MULTI-TABLE JOIN — Product Sales by Category
-- ============================================================

SELECT
    p.product_id,
    COALESCE(
        p.product_category_name_english,
        p.product_category_name,
        'Unknown'
    ) AS category,
    s.seller_state,
    COUNT(*) AS units_sold,
    ROUND(SUM(oi.price), 2) AS sales
FROM analytics.fact_order_items oi
INNER JOIN analytics.dim_product p
    ON oi.product_key = p.product_key
INNER JOIN analytics.dim_seller s
    ON oi.seller_key = s.seller_key
GROUP BY
    p.product_id,
    COALESCE(
        p.product_category_name_english,
        p.product_category_name,
        'Unknown'
    ),
    s.seller_state
ORDER BY sales DESC
LIMIT 20;


-- ============================================================
-- 4. CASE — Classify Order Value
-- ============================================================

WITH order_values AS (
    SELECT
        order_id,
        SUM(price) AS order_value
    FROM analytics.fact_order_items
    GROUP BY order_id
)
SELECT
    order_id,
    ROUND(order_value, 2) AS order_value,
    CASE
        WHEN order_value < 100 THEN 'Low Value'
        WHEN order_value < 500 THEN 'Medium Value'
        ELSE 'High Value'
    END AS order_value_segment
FROM order_values
ORDER BY order_value DESC
LIMIT 50;


-- ============================================================
-- 5. CTE — Monthly Sales Base
-- ============================================================

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
)
SELECT
    year,
    month,
    month_name,
    ROUND(sales, 2) AS sales
FROM monthly_sales
ORDER BY
    year,
    month;


-- ============================================================
-- 6. SUBQUERY — Products Above Average Sales
-- ============================================================

WITH product_sales AS (
    SELECT
        p.product_id,
        SUM(oi.price) AS sales
    FROM analytics.fact_order_items oi
    INNER JOIN analytics.dim_product p
        ON oi.product_key = p.product_key
    GROUP BY p.product_id
)
SELECT
    product_id,
    ROUND(sales, 2) AS sales
FROM product_sales
WHERE sales > (
    SELECT AVG(sales)
    FROM product_sales
)
ORDER BY sales DESC;


-- ============================================================
-- 7. RANK() — Products Within Category
-- ============================================================

WITH product_sales AS (
    SELECT
        p.product_id,
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
        p.product_id,
        COALESCE(
            p.product_category_name_english,
            p.product_category_name,
            'Unknown'
        )
)
SELECT
    product_id,
    category,
    ROUND(sales, 2) AS sales,
    RANK() OVER (
        PARTITION BY category
        ORDER BY sales DESC
    ) AS category_rank
FROM product_sales
ORDER BY
    category,
    category_rank;


-- ============================================================
-- 8. DENSE_RANK() — Sellers Within State
-- ============================================================

WITH seller_sales AS (
    SELECT
        s.seller_id,
        s.seller_state,
        SUM(oi.price) AS sales
    FROM analytics.fact_order_items oi
    INNER JOIN analytics.dim_seller s
        ON oi.seller_key = s.seller_key
    GROUP BY
        s.seller_id,
        s.seller_state
)
SELECT
    seller_id,
    seller_state,
    ROUND(sales, 2) AS sales,
    DENSE_RANK() OVER (
        PARTITION BY seller_state
        ORDER BY sales DESC
    ) AS state_rank
FROM seller_sales
ORDER BY
    seller_state,
    state_rank;


-- ============================================================
-- 9. ROW_NUMBER() — Latest Order Per Customer
-- ============================================================

WITH customer_orders AS (
    SELECT
        o.order_id,
        o.customer_key,
        d.full_date AS purchase_date,
        ROW_NUMBER() OVER (
            PARTITION BY o.customer_key
            ORDER BY d.full_date DESC, o.order_id DESC
        ) AS order_number
    FROM analytics.fact_orders o
    INNER JOIN analytics.dim_date d
        ON o.purchase_date_key = d.date_key
)
SELECT
    order_id,
    customer_key,
    purchase_date
FROM customer_orders
WHERE order_number = 1
ORDER BY purchase_date DESC;


-- ============================================================
-- 10. LAG() — Month-over-Month Sales Growth
-- ============================================================

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
sales_comparison AS (
    SELECT
        year,
        month,
        month_name,
        sales,
        LAG(sales) OVER (
            ORDER BY year, month
        ) AS previous_sales
    FROM monthly_sales
)
SELECT
    year,
    month,
    month_name,
    ROUND(sales, 2) AS sales,
    ROUND(previous_sales, 2) AS previous_month_sales,
    ROUND(
        100.0 * (sales - previous_sales)
        / NULLIF(previous_sales, 0),
        2
    ) AS mom_growth_pct
FROM sales_comparison
ORDER BY
    year,
    month;


-- ============================================================
-- 11. LEAD() — Next Month Sales
-- ============================================================

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
)
SELECT
    year,
    month,
    month_name,
    ROUND(sales, 2) AS sales,
    ROUND(
        LEAD(sales) OVER (
            ORDER BY year, month
        ),
        2
    ) AS next_month_sales
FROM monthly_sales
ORDER BY
    year,
    month;


-- ============================================================
-- 12. RUNNING TOTAL — CUMULATIVE REVENUE
-- ============================================================

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
)
SELECT
    year,
    month,
    month_name,
    ROUND(sales, 2) AS monthly_sales,
    ROUND(
        SUM(sales) OVER (
            ORDER BY year, month
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ),
        2
    ) AS cumulative_sales
FROM monthly_sales
ORDER BY
    year,
    month;


-- ============================================================
-- 13. PERCENTAGE CONTRIBUTION — CATEGORY SALES
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
)
SELECT
    category,
    ROUND(sales, 2) AS sales,
    ROUND(
        100.0 * sales / SUM(sales) OVER (),
        2
    ) AS sales_contribution_pct
FROM category_sales
ORDER BY sales DESC;


-- ============================================================
-- 14. TOP-N WITHIN CATEGORY
-- ============================================================

WITH product_sales AS (
    SELECT
        p.product_id,
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
        p.product_id,
        COALESCE(
            p.product_category_name_english,
            p.product_category_name,
            'Unknown'
        )
),
ranked_products AS (
    SELECT
        product_id,
        category,
        sales,
        ROW_NUMBER() OVER (
            PARTITION BY category
            ORDER BY sales DESC, product_id
        ) AS category_position
    FROM product_sales
)
SELECT
    product_id,
    category,
    ROUND(sales, 2) AS sales,
    category_position
FROM ranked_products
WHERE category_position <= 3
ORDER BY
    category,
    category_position;


-- ============================================================
-- 15. YEAR-OVER-YEAR SALES ANALYSIS
-- ============================================================

WITH yearly_sales AS (
    SELECT
        d.year,
        SUM(oi.price) AS sales
    FROM analytics.fact_order_items oi
    INNER JOIN analytics.dim_date d
        ON oi.order_date_key = d.date_key
    GROUP BY d.year
),
year_comparison AS (
    SELECT
        year,
        sales,
        LAG(sales) OVER (
            ORDER BY year
        ) AS previous_year_sales
    FROM yearly_sales
)
SELECT
    year,
    ROUND(sales, 2) AS sales,
    ROUND(previous_year_sales, 2) AS previous_year_sales,
    ROUND(
        100.0 * (sales - previous_year_sales)
        / NULLIF(previous_year_sales, 0),
        2
    ) AS yoy_growth_pct
FROM year_comparison
ORDER BY year;


-- ============================================================
-- 16. YEAR-OVER-YEAR MONTHLY SALES
-- ============================================================
-- Compares the same calendar month across years.

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
year_comparison AS (
    SELECT
        year,
        month,
        month_name,
        sales,
        LAG(sales) OVER (
            PARTITION BY month
            ORDER BY year
        ) AS previous_year_same_month_sales
    FROM monthly_sales
)
SELECT
    year,
    month,
    month_name,
    ROUND(sales, 2) AS sales,
    ROUND(previous_year_same_month_sales, 2)
        AS previous_year_same_month_sales,
    ROUND(
        100.0 * (sales - previous_year_same_month_sales)
        / NULLIF(previous_year_same_month_sales, 0),
        2
    ) AS yoy_growth_pct
FROM year_comparison
ORDER BY
    year,
    month;


-- ============================================================
-- 17. TOP SELLER WITHIN EACH STATE
-- ============================================================

WITH seller_sales AS (
    SELECT
        s.seller_id,
        s.seller_state,
        SUM(oi.price) AS sales
    FROM analytics.fact_order_items oi
    INNER JOIN analytics.dim_seller s
        ON oi.seller_key = s.seller_key
    GROUP BY
        s.seller_id,
        s.seller_state
),
ranked_sellers AS (
    SELECT
        seller_id,
        seller_state,
        sales,
        ROW_NUMBER() OVER (
            PARTITION BY seller_state
            ORDER BY sales DESC, seller_id
        ) AS state_position
    FROM seller_sales
)
SELECT
    seller_id,
    seller_state,
    ROUND(sales, 2) AS sales,
    state_position
FROM ranked_sellers
WHERE state_position = 1
ORDER BY seller_state;


-- ============================================================
-- 18. CUSTOMER ORDER RANKING
-- ============================================================

WITH customer_order_counts AS (
    SELECT
        c.customer_id,
        c.customer_state,
        COUNT(o.order_id) AS order_count
    FROM analytics.dim_customer c
    LEFT JOIN analytics.fact_orders o
        ON c.customer_key = o.customer_key
    GROUP BY
        c.customer_id,
        c.customer_state
)
SELECT
    customer_id,
    customer_state,
    order_count,
    RANK() OVER (
        ORDER BY order_count DESC
    ) AS customer_rank
FROM customer_order_counts
ORDER BY customer_rank
LIMIT 100;


-- ============================================================
-- 19. CATEGORY RANKING BY REVENUE
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
)
SELECT
    category,
    ROUND(sales, 2) AS sales,
    RANK() OVER (
        ORDER BY sales DESC
    ) AS category_rank
FROM category_sales
ORDER BY category_rank;


-- ============================================================
-- 20. RUNNING CATEGORY CONTRIBUTION
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
ranked_categories AS (
    SELECT
        category,
        sales,
        RANK() OVER (
            ORDER BY sales DESC
        ) AS category_rank
    FROM category_sales
)
SELECT
    category,
    category_rank,
    ROUND(sales, 2) AS sales,
    ROUND(
        100.0 * sales / SUM(sales) OVER (),
        2
    ) AS contribution_pct,
    ROUND(
        100.0 *
        SUM(sales) OVER (
            ORDER BY sales DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )
        / SUM(sales) OVER (),
        2
    ) AS cumulative_contribution_pct
FROM ranked_categories
ORDER BY category_rank;