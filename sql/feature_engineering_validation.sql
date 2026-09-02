CREATE SCHEMA IF NOT EXISTS validation;

DROP TABLE IF EXISTS validation.validation_summary;
DROP TABLE IF EXISTS validation.monthly_features;
DROP TABLE IF EXISTS validation.customer_features;
DROP TABLE IF EXISTS validation.order_items_features;
DROP TABLE IF EXISTS validation.orders_features;

CREATE TABLE validation.orders_features (
    order_id TEXT,
    customer_id TEXT,
    customer_unique_id TEXT,
    order_status TEXT,
    order_date DATE,
    order_year INTEGER,
    order_quarter INTEGER,
    order_month_number INTEGER,
    order_month_name TEXT,
    order_weekday TEXT,
    is_weekend INTEGER,
    year_month TEXT,
    season TEXT,
    holiday_season_flag INTEGER,
    quarter_seasonality TEXT,
    order_revenue NUMERIC,
    total_order_value NUMERIC,
    items_per_order NUMERIC,
    processing_time_days NUMERIC,
    delivery_time_days NUMERIC,
    estimated_delivery_time_days NUMERIC,
    delivery_difference_days NUMERIC,
    late_delivery_flag NUMERIC,
    on_time_delivery_flag NUMERIC,
    delivery_status TEXT,
    number_payment_installments NUMERIC,
    multi_payment_flag NUMERIC,
    payment_value_per_order NUMERIC,
    review_score NUMERIC,
    review_score_category TEXT,
    low_review_flag NUMERIC,
    high_review_flag NUMERIC
);

CREATE TABLE validation.order_items_features (
    order_id TEXT,
    order_item_id INTEGER,
    product_id TEXT,
    seller_id TEXT,
    item_revenue NUMERIC,
    freight_value NUMERIC,
    freight_to_price_ratio NUMERIC,
    total_item_value NUMERIC,
    product_weight_g NUMERIC,
    product_volume_cm3 NUMERIC,
    product_weight_category TEXT,
    product_dimension_category TEXT
);

CREATE TABLE validation.customer_features (
    customer_unique_id TEXT,
    customer_order_count INTEGER,
    repeat_customer_flag INTEGER,
    customer_segment TEXT,
    customer_lifetime_revenue NUMERIC,
    average_customer_order_value NUMERIC
);

CREATE TABLE validation.monthly_features (
    year_month TEXT,
    monthly_revenue NUMERIC,
    monthly_order_count INTEGER,
    three_month_rolling_revenue NUMERIC,
    three_month_rolling_order_count NUMERIC,
    monthly_revenue_growth NUMERIC,
    cumulative_revenue NUMERIC
);

\copy validation.orders_features FROM 'C:/Users/Bhuvan Ummidisetti/Desktop/Project 1/Retail-Sales-Performance-Analytics/data/processed/features/orders_features.csv' WITH (FORMAT csv, HEADER true, NULL '');
\copy validation.order_items_features FROM 'C:/Users/Bhuvan Ummidisetti/Desktop/Project 1/Retail-Sales-Performance-Analytics/data/processed/features/order_items_features.csv' WITH (FORMAT csv, HEADER true, NULL '');
\copy validation.customer_features FROM 'C:/Users/Bhuvan Ummidisetti/Desktop/Project 1/Retail-Sales-Performance-Analytics/data/processed/features/customer_features.csv' WITH (FORMAT csv, HEADER true, NULL '');
\copy validation.monthly_features FROM 'C:/Users/Bhuvan Ummidisetti/Desktop/Project 1/Retail-Sales-Performance-Analytics/data/processed/features/monthly_features.csv' WITH (FORMAT csv, HEADER true, NULL '');

CREATE TABLE validation.validation_summary (
    metric TEXT,
    status TEXT,
    mismatched_records INTEGER,
    max_numeric_difference NUMERIC
);

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH source_order_revenue AS (
    SELECT o.order_id, SUM(oi.price)::NUMERIC AS sql_order_revenue
    FROM cleaned.orders o
    LEFT JOIN cleaned.order_items oi ON oi.order_id = o.order_id
    GROUP BY o.order_id
),
python_order_revenue AS (
    SELECT order_id, order_revenue AS python_order_revenue
    FROM validation.orders_features
),
matched AS (
    SELECT s.order_id,
           s.sql_order_revenue,
           p.python_order_revenue,
           ABS(COALESCE(s.sql_order_revenue, 0) - COALESCE(p.python_order_revenue, 0)) AS diff
    FROM source_order_revenue s
    FULL OUTER JOIN python_order_revenue p USING (order_id)
    WHERE ABS(COALESCE(s.sql_order_revenue, 0) - COALESCE(p.python_order_revenue, 0)) >= 0.000001
)
SELECT 'order_revenue' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff)::NUMERIC AS max_numeric_difference
FROM matched;

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH source_total_value AS (
    SELECT o.order_id, SUM(oi.price + oi.freight_value)::NUMERIC AS sql_total_order_value
    FROM cleaned.orders o
    LEFT JOIN cleaned.order_items oi ON oi.order_id = o.order_id
    GROUP BY o.order_id
),
python_total_value AS (
    SELECT order_id, total_order_value AS python_total_order_value
    FROM validation.orders_features
),
matched AS (
    SELECT s.order_id,
           s.sql_total_order_value,
           p.python_total_order_value,
           ABS(COALESCE(s.sql_total_order_value, 0) - COALESCE(p.python_total_order_value, 0)) AS diff
    FROM source_total_value s
    FULL OUTER JOIN python_total_value p USING (order_id)
    WHERE ABS(COALESCE(s.sql_total_order_value, 0) - COALESCE(p.python_total_order_value, 0)) >= 0.000001
)
SELECT 'total_order_value' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff)::NUMERIC AS max_numeric_difference
FROM matched;

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH source_items_per_order AS (
    SELECT o.order_id, COUNT(oi.order_item_id)::NUMERIC AS sql_items_per_order
    FROM cleaned.orders o
    LEFT JOIN cleaned.order_items oi ON oi.order_id = o.order_id
    GROUP BY o.order_id
),
python_items_per_order AS (
    SELECT order_id, items_per_order AS python_items_per_order
    FROM validation.orders_features
),
matched AS (
    SELECT s.order_id,
           s.sql_items_per_order,
           p.python_items_per_order,
           ABS(COALESCE(s.sql_items_per_order, 0) - COALESCE(p.python_items_per_order, 0)) AS diff
    FROM source_items_per_order s
    FULL OUTER JOIN python_items_per_order p USING (order_id)
    WHERE ABS(COALESCE(s.sql_items_per_order, 0) - COALESCE(p.python_items_per_order, 0)) >= 0.000001
)
SELECT 'items_per_order' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff)::NUMERIC AS max_numeric_difference
FROM matched;

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH source_delivery AS (
    SELECT order_id,
           CASE WHEN order_purchase_timestamp IS NOT NULL AND order_delivered_customer_date IS NOT NULL THEN EXTRACT(EPOCH FROM (order_delivered_customer_date - order_purchase_timestamp)) / 86400.0 ELSE NULL END AS sql_delivery_time_days,
           CASE WHEN order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL AND order_estimated_delivery_date IS NOT NULL AND order_delivered_customer_date > order_estimated_delivery_date THEN 1.0
                WHEN order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL AND order_estimated_delivery_date IS NOT NULL THEN 0.0
                ELSE NULL END AS sql_late_delivery_flag
    FROM cleaned.orders
),
python_delivery AS (
    SELECT order_id, delivery_time_days AS python_delivery_time_days, late_delivery_flag AS python_late_delivery_flag
    FROM validation.orders_features
),
matched AS (
    SELECT s.order_id,
           s.sql_delivery_time_days,
           p.python_delivery_time_days,
           ABS(COALESCE(s.sql_delivery_time_days, 0) - COALESCE(p.python_delivery_time_days, 0)) AS diff
    FROM source_delivery s
    FULL OUTER JOIN python_delivery p USING (order_id)
    WHERE ABS(COALESCE(s.sql_delivery_time_days, 0) - COALESCE(p.python_delivery_time_days, 0)) >= 0.000001
)
SELECT 'delivery_time_days' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff)::NUMERIC AS max_numeric_difference
FROM matched;

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH source_late AS (
    SELECT order_id,
           CASE WHEN order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL AND order_estimated_delivery_date IS NOT NULL AND order_delivered_customer_date > order_estimated_delivery_date THEN 1.0
                WHEN order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL AND order_estimated_delivery_date IS NOT NULL THEN 0.0
                ELSE NULL END AS sql_late_delivery_flag
    FROM cleaned.orders
),
python_late AS (
    SELECT order_id, late_delivery_flag AS python_late_delivery_flag
    FROM validation.orders_features
),
matched AS (
    SELECT s.order_id,
           s.sql_late_delivery_flag,
           p.python_late_delivery_flag,
           ABS(COALESCE(s.sql_late_delivery_flag, 0) - COALESCE(p.python_late_delivery_flag, 0)) AS diff
    FROM source_late s
    FULL OUTER JOIN python_late p USING (order_id)
    WHERE COALESCE(s.sql_late_delivery_flag, -1) <> COALESCE(p.python_late_delivery_flag, -1)
)
SELECT 'late_delivery_flag' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff)::NUMERIC AS max_numeric_difference
FROM matched;

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH source_payments AS (
    SELECT order_id, MAX(payment_installments)::NUMERIC AS sql_number_payment_installments
    FROM cleaned.payments
    GROUP BY order_id
),
python_payments AS (
    SELECT order_id, number_payment_installments AS python_number_payment_installments
    FROM validation.orders_features
),
matched AS (
    SELECT s.order_id,
           s.sql_number_payment_installments,
           p.python_number_payment_installments,
           ABS(COALESCE(s.sql_number_payment_installments, 0) - COALESCE(p.python_number_payment_installments, 0)) AS diff
    FROM source_payments s
    FULL OUTER JOIN python_payments p USING (order_id)
    WHERE COALESCE(s.sql_number_payment_installments, -1) <> COALESCE(p.python_number_payment_installments, -1)
)
SELECT 'number_payment_installments' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff)::NUMERIC AS max_numeric_difference
FROM matched;

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH source_reviews AS (
    SELECT order_id, MAX(review_score)::NUMERIC AS sql_review_score
    FROM cleaned.reviews
    GROUP BY order_id
),
python_reviews AS (
    SELECT order_id, review_score AS python_review_score
    FROM validation.orders_features
),
matched AS (
    SELECT s.order_id,
           s.sql_review_score,
           p.python_review_score,
           ABS(COALESCE(s.sql_review_score, 0) - COALESCE(p.python_review_score, 0)) AS diff
    FROM source_reviews s
    FULL OUTER JOIN python_reviews p USING (order_id)
    WHERE COALESCE(s.sql_review_score, -1) <> COALESCE(p.python_review_score, -1)
)
SELECT 'review_score' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff)::NUMERIC AS max_numeric_difference
FROM matched;

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH source_monthly AS (
    SELECT TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM') AS year_month,
           SUM(oi.price)::NUMERIC AS sql_monthly_revenue,
           COUNT(DISTINCT o.order_id)::INTEGER AS sql_monthly_order_count
    FROM cleaned.orders o
    LEFT JOIN cleaned.order_items oi ON oi.order_id = o.order_id
    GROUP BY TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM')
),
python_monthly AS (
    SELECT year_month, monthly_revenue AS python_monthly_revenue, monthly_order_count AS python_monthly_order_count
    FROM validation.monthly_features
),
matched AS (
    SELECT s.year_month,
           s.sql_monthly_revenue,
           p.python_monthly_revenue,
           ABS(COALESCE(s.sql_monthly_revenue, 0) - COALESCE(p.python_monthly_revenue, 0)) AS diff
    FROM source_monthly s
    FULL OUTER JOIN python_monthly p USING (year_month)
    WHERE ABS(COALESCE(s.sql_monthly_revenue, 0) - COALESCE(p.python_monthly_revenue, 0)) >= 0.000001
)
SELECT 'monthly_revenue' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff)::NUMERIC AS max_numeric_difference
FROM matched;

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH source_monthly AS (
    SELECT TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM') AS year_month,
           SUM(oi.price)::NUMERIC AS sql_monthly_revenue,
           COUNT(DISTINCT o.order_id)::INTEGER AS sql_monthly_order_count
    FROM cleaned.orders o
    LEFT JOIN cleaned.order_items oi ON oi.order_id = o.order_id
    GROUP BY TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM')
),
python_monthly AS (
    SELECT year_month, monthly_revenue AS python_monthly_revenue, monthly_order_count AS python_monthly_order_count
    FROM validation.monthly_features
),
matched AS (
    SELECT s.year_month,
           s.sql_monthly_order_count,
           p.python_monthly_order_count,
           ABS(COALESCE(s.sql_monthly_order_count, 0) - COALESCE(p.python_monthly_order_count, 0)) AS diff
    FROM source_monthly s
    FULL OUTER JOIN python_monthly p USING (year_month)
    WHERE COALESCE(s.sql_monthly_order_count, -1) <> COALESCE(p.python_monthly_order_count, -1)
)
SELECT 'monthly_order_count' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff)::NUMERIC AS max_numeric_difference
FROM matched;

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
SELECT 'order_revenue_nulls_allowed' AS metric, 'ALLOWED_NULL' AS status, 0::INTEGER AS mismatched_records, 0::NUMERIC AS max_numeric_difference
WHERE EXISTS (
    SELECT 1
    FROM cleaned.orders o
    LEFT JOIN cleaned.order_items oi ON oi.order_id = o.order_id
    GROUP BY o.order_id
    HAVING COUNT(oi.order_item_id) = 0
);

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
SELECT 'total_order_value_nulls_allowed' AS metric, 'ALLOWED_NULL' AS status, 0::INTEGER AS mismatched_records, 0::NUMERIC AS max_numeric_difference
WHERE EXISTS (
    SELECT 1
    FROM cleaned.orders o
    LEFT JOIN cleaned.order_items oi ON oi.order_id = o.order_id
    GROUP BY o.order_id
    HAVING COUNT(oi.order_item_id) = 0
);

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
SELECT 'items_per_order_nulls_allowed' AS metric, 'ALLOWED_NULL' AS status, 0::INTEGER AS mismatched_records, 0::NUMERIC AS max_numeric_difference
WHERE EXISTS (
    SELECT 1
    FROM cleaned.orders o
    LEFT JOIN cleaned.order_items oi ON oi.order_id = o.order_id
    GROUP BY o.order_id
    HAVING COUNT(oi.order_item_id) = 0
);

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH source_customer_stats AS (
    SELECT c.customer_unique_id,
           COUNT(DISTINCT o.order_id)::INTEGER AS sql_customer_order_count,
           CASE WHEN COUNT(DISTINCT o.order_id) > 1 THEN 1 ELSE 0 END AS sql_repeat_customer_flag
    FROM cleaned.customers c
    LEFT JOIN cleaned.orders o ON o.customer_id = c.customer_id
    GROUP BY c.customer_unique_id
),
python_customer_stats AS (
    SELECT customer_unique_id,
           customer_order_count AS python_customer_order_count,
           repeat_customer_flag AS python_repeat_customer_flag
    FROM validation.customer_features
),
matched AS (
    SELECT s.customer_unique_id,
           s.sql_customer_order_count,
           p.python_customer_order_count,
           s.sql_repeat_customer_flag,
           p.python_repeat_customer_flag
    FROM source_customer_stats s
    FULL OUTER JOIN python_customer_stats p USING (customer_unique_id)
    WHERE s.customer_unique_id IS NULL OR p.customer_unique_id IS NULL
       OR s.sql_customer_order_count IS DISTINCT FROM p.python_customer_order_count
)
SELECT 'customer_order_count' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       0::NUMERIC AS max_numeric_difference
FROM matched;

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH source_customer_stats AS (
    SELECT c.customer_unique_id,
           COUNT(DISTINCT o.order_id)::INTEGER AS sql_customer_order_count,
           CASE WHEN COUNT(DISTINCT o.order_id) > 1 THEN 1 ELSE 0 END AS sql_repeat_customer_flag
    FROM cleaned.customers c
    LEFT JOIN cleaned.orders o ON o.customer_id = c.customer_id
    GROUP BY c.customer_unique_id
),
python_customer_stats AS (
    SELECT customer_unique_id,
           customer_order_count AS python_customer_order_count,
           repeat_customer_flag AS python_repeat_customer_flag
    FROM validation.customer_features
),
matched AS (
    SELECT s.customer_unique_id,
           s.sql_customer_order_count,
           p.python_customer_order_count,
           s.sql_repeat_customer_flag,
           p.python_repeat_customer_flag
    FROM source_customer_stats s
    FULL OUTER JOIN python_customer_stats p USING (customer_unique_id)
    WHERE s.customer_unique_id IS NULL OR p.customer_unique_id IS NULL
       OR s.sql_repeat_customer_flag IS DISTINCT FROM p.python_repeat_customer_flag
)
SELECT 'repeat_customer_flag' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       0::NUMERIC AS max_numeric_difference
FROM matched;

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH source_customer_segments AS (
    SELECT c.customer_unique_id,
           CASE WHEN COUNT(DISTINCT o.order_id) > 1 THEN 'Repeat' ELSE 'One-time' END AS sql_customer_segment
    FROM cleaned.customers c
    LEFT JOIN cleaned.orders o ON o.customer_id = c.customer_id
    GROUP BY c.customer_unique_id
),
python_customer_segments AS (
    SELECT customer_unique_id,
           customer_segment AS python_customer_segment
    FROM validation.customer_features
),
matched AS (
    SELECT s.customer_unique_id,
           s.sql_customer_segment,
           p.python_customer_segment
    FROM source_customer_segments s
    FULL OUTER JOIN python_customer_segments p USING (customer_unique_id)
    WHERE s.customer_unique_id IS NULL OR p.customer_unique_id IS NULL
       OR s.sql_customer_segment IS DISTINCT FROM p.python_customer_segment
)
SELECT 'customer_segment' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       0::NUMERIC AS max_numeric_difference
FROM matched;

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH source_delivery_status AS (
    SELECT order_id,
           CASE
               WHEN order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL AND order_estimated_delivery_date IS NOT NULL AND order_delivered_customer_date > order_estimated_delivery_date THEN 'Late'
               WHEN order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL AND order_estimated_delivery_date IS NOT NULL AND order_delivered_customer_date <= order_estimated_delivery_date THEN 'On Time'
               ELSE 'Unavailable'
           END AS sql_delivery_status
    FROM cleaned.orders
),
python_delivery_status AS (
    SELECT order_id,
           delivery_status AS python_delivery_status
    FROM validation.orders_features
),
matched AS (
    SELECT s.order_id,
           s.sql_delivery_status,
           p.python_delivery_status
    FROM source_delivery_status s
    FULL OUTER JOIN python_delivery_status p USING (order_id)
    WHERE s.order_id IS NULL OR p.order_id IS NULL
       OR s.sql_delivery_status IS DISTINCT FROM p.python_delivery_status
)
SELECT 'delivery_status' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       0::NUMERIC AS max_numeric_difference
FROM matched;

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH order_level_revenue AS (
    SELECT o.customer_id,
           o.order_id,
           COALESCE(SUM(oi.price)::NUMERIC, 0) AS order_revenue
    FROM cleaned.orders o
    LEFT JOIN cleaned.order_items oi ON oi.order_id = o.order_id
    GROUP BY o.customer_id, o.order_id
),
source_customer_revenue AS (
    SELECT c.customer_unique_id,
           COUNT(DISTINCT ol.order_id)::INTEGER AS sql_customer_order_count,
           COALESCE(SUM(ol.order_revenue)::NUMERIC, 0) AS sql_customer_lifetime_revenue
    FROM cleaned.customers c
    LEFT JOIN order_level_revenue ol ON ol.customer_id = c.customer_id
    GROUP BY c.customer_unique_id
),
python_customer_revenue AS (
    SELECT customer_unique_id,
           customer_lifetime_revenue AS python_customer_lifetime_revenue
    FROM validation.customer_features
),
matched AS (
    SELECT s.customer_unique_id,
           s.sql_customer_lifetime_revenue,
           p.python_customer_lifetime_revenue,
           ABS(COALESCE(s.sql_customer_lifetime_revenue, 0) - COALESCE(p.python_customer_lifetime_revenue, 0)) AS diff
    FROM source_customer_revenue s
    FULL OUTER JOIN python_customer_revenue p USING (customer_unique_id)
    WHERE s.customer_unique_id IS NULL OR p.customer_unique_id IS NULL
       OR ABS(COALESCE(s.sql_customer_lifetime_revenue, 0) - COALESCE(p.python_customer_lifetime_revenue, 0)) >= 0.000001
)
SELECT 'customer_lifetime_revenue' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff)::NUMERIC AS max_numeric_difference
FROM matched;

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH order_level_revenue AS (
    SELECT o.customer_id,
           o.order_id,
           COALESCE(SUM(oi.price)::NUMERIC, 0) AS order_revenue
    FROM cleaned.orders o
    LEFT JOIN cleaned.order_items oi ON oi.order_id = o.order_id
    GROUP BY o.customer_id, o.order_id
),
source_customer_average AS (
    SELECT c.customer_unique_id,
           COUNT(DISTINCT ol.order_id)::INTEGER AS sql_customer_order_count,
           COALESCE(SUM(ol.order_revenue)::NUMERIC, 0) AS sql_customer_lifetime_revenue,
           CASE
               WHEN COUNT(DISTINCT ol.order_id) > 0 THEN COALESCE(SUM(ol.order_revenue)::NUMERIC, 0) / COUNT(DISTINCT ol.order_id)
               ELSE NULL
           END AS sql_average_customer_order_value
    FROM cleaned.customers c
    LEFT JOIN order_level_revenue ol ON ol.customer_id = c.customer_id
    GROUP BY c.customer_unique_id
),
python_customer_average AS (
    SELECT customer_unique_id,
           average_customer_order_value AS python_average_customer_order_value
    FROM validation.customer_features
),
matched AS (
    SELECT s.customer_unique_id,
           s.sql_average_customer_order_value,
           p.python_average_customer_order_value,
           ABS(COALESCE(s.sql_average_customer_order_value, 0) - COALESCE(p.python_average_customer_order_value, 0)) AS diff
    FROM source_customer_average s
    FULL OUTER JOIN python_customer_average p USING (customer_unique_id)
    WHERE s.customer_unique_id IS NULL OR p.customer_unique_id IS NULL
       OR ABS(COALESCE(s.sql_average_customer_order_value, 0) - COALESCE(p.python_average_customer_order_value, 0)) >= 0.000001
)
SELECT 'average_customer_order_value' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff)::NUMERIC AS max_numeric_difference
FROM matched;

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH source_order_item_metrics AS (
    SELECT oi.order_id,
           oi.order_item_id,
           oi.price::NUMERIC AS sql_item_revenue,
           oi.freight_value::NUMERIC AS sql_freight_value,
           CASE
               WHEN oi.price IS NULL OR oi.price = 0 THEN NULL
               ELSE (oi.freight_value / oi.price)::NUMERIC
           END AS sql_freight_to_price_ratio,
           (oi.price + oi.freight_value)::NUMERIC AS sql_total_item_value
    FROM cleaned.order_items oi
),
python_order_item_metrics AS (
    SELECT order_id,
           order_item_id,
           item_revenue AS python_item_revenue,
           freight_value AS python_freight_value,
           freight_to_price_ratio AS python_freight_to_price_ratio,
           total_item_value AS python_total_item_value
    FROM validation.order_items_features
),
matched AS (
    SELECT s.order_id,
           s.order_item_id,
           s.sql_item_revenue,
           p.python_item_revenue,
           s.sql_freight_value,
           p.python_freight_value,
           s.sql_freight_to_price_ratio,
           p.python_freight_to_price_ratio,
           s.sql_total_item_value,
           p.python_total_item_value,
           CASE
               WHEN s.sql_item_revenue IS NULL AND p.python_item_revenue IS NULL THEN 0
               WHEN s.sql_item_revenue IS NULL OR p.python_item_revenue IS NULL THEN 1e9
               ELSE ABS(s.sql_item_revenue - p.python_item_revenue)
           END AS diff_item_revenue,
           CASE
               WHEN s.sql_freight_value IS NULL AND p.python_freight_value IS NULL THEN 0
               WHEN s.sql_freight_value IS NULL OR p.python_freight_value IS NULL THEN 1e9
               ELSE ABS(s.sql_freight_value - p.python_freight_value)
           END AS diff_freight_value,
           CASE
               WHEN s.sql_freight_to_price_ratio IS NULL AND p.python_freight_to_price_ratio IS NULL THEN 0
               WHEN s.sql_freight_to_price_ratio IS NULL OR p.python_freight_to_price_ratio IS NULL THEN 1e9
               ELSE ABS(s.sql_freight_to_price_ratio - p.python_freight_to_price_ratio)
           END AS diff_ratio,
           CASE
               WHEN s.sql_total_item_value IS NULL AND p.python_total_item_value IS NULL THEN 0
               WHEN s.sql_total_item_value IS NULL OR p.python_total_item_value IS NULL THEN 1e9
               ELSE ABS(s.sql_total_item_value - p.python_total_item_value)
           END AS diff_total_value
    FROM source_order_item_metrics s
    FULL OUTER JOIN python_order_item_metrics p USING (order_id, order_item_id)
    WHERE s.order_id IS NULL OR p.order_id IS NULL
       OR (s.sql_item_revenue IS NULL AND p.python_item_revenue IS NOT NULL)
       OR (s.sql_item_revenue IS NOT NULL AND p.python_item_revenue IS NULL)
       OR (s.sql_item_revenue IS NOT NULL AND p.python_item_revenue IS NOT NULL AND ABS(s.sql_item_revenue - p.python_item_revenue) >= 0.000001)
)
SELECT 'item_revenue' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff_item_revenue)::NUMERIC AS max_numeric_difference
FROM matched
UNION ALL
SELECT 'freight_value' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff_freight_value)::NUMERIC AS max_numeric_difference
FROM (
    SELECT s.*, CASE
               WHEN s.sql_freight_value IS NULL AND p.python_freight_value IS NULL THEN 0
               WHEN s.sql_freight_value IS NULL OR p.python_freight_value IS NULL THEN 1e9
               ELSE ABS(s.sql_freight_value - p.python_freight_value)
           END AS diff_freight_value
    FROM source_order_item_metrics s
    FULL OUTER JOIN python_order_item_metrics p USING (order_id, order_item_id)
    WHERE s.order_id IS NULL OR p.order_id IS NULL
       OR (s.sql_freight_value IS NULL AND p.python_freight_value IS NOT NULL)
       OR (s.sql_freight_value IS NOT NULL AND p.python_freight_value IS NULL)
       OR (s.sql_freight_value IS NOT NULL AND p.python_freight_value IS NOT NULL AND ABS(s.sql_freight_value - p.python_freight_value) >= 0.000001)
) x
UNION ALL
SELECT 'freight_to_price_ratio' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff_ratio)::NUMERIC AS max_numeric_difference
FROM (
    SELECT s.*, CASE
               WHEN s.sql_freight_to_price_ratio IS NULL AND p.python_freight_to_price_ratio IS NULL THEN 0
               WHEN s.sql_freight_to_price_ratio IS NULL OR p.python_freight_to_price_ratio IS NULL THEN 1e9
               ELSE ABS(s.sql_freight_to_price_ratio - p.python_freight_to_price_ratio)
           END AS diff_ratio
    FROM source_order_item_metrics s
    FULL OUTER JOIN python_order_item_metrics p USING (order_id, order_item_id)
    WHERE s.order_id IS NULL OR p.order_id IS NULL
       OR (s.sql_freight_to_price_ratio IS NULL AND p.python_freight_to_price_ratio IS NOT NULL)
       OR (s.sql_freight_to_price_ratio IS NOT NULL AND p.python_freight_to_price_ratio IS NULL)
       OR (s.sql_freight_to_price_ratio IS NOT NULL AND p.python_freight_to_price_ratio IS NOT NULL AND ABS(s.sql_freight_to_price_ratio - p.python_freight_to_price_ratio) >= 0.000001)
) x
UNION ALL
SELECT 'total_item_value' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff_total_value)::NUMERIC AS max_numeric_difference
FROM (
    SELECT s.*, CASE
               WHEN s.sql_total_item_value IS NULL AND p.python_total_item_value IS NULL THEN 0
               WHEN s.sql_total_item_value IS NULL OR p.python_total_item_value IS NULL THEN 1e9
               ELSE ABS(s.sql_total_item_value - p.python_total_item_value)
           END AS diff_total_value
    FROM source_order_item_metrics s
    FULL OUTER JOIN python_order_item_metrics p USING (order_id, order_item_id)
    WHERE s.order_id IS NULL OR p.order_id IS NULL
       OR (s.sql_total_item_value IS NULL AND p.python_total_item_value IS NOT NULL)
       OR (s.sql_total_item_value IS NOT NULL AND p.python_total_item_value IS NULL)
       OR (s.sql_total_item_value IS NOT NULL AND p.python_total_item_value IS NOT NULL AND ABS(s.sql_total_item_value - p.python_total_item_value) >= 0.000001)
) x;

INSERT INTO validation.validation_summary (metric, status, mismatched_records, max_numeric_difference)
WITH source_monthly AS (
    SELECT TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM') AS year_month,
           COALESCE(SUM(oi.price), 0)::NUMERIC AS monthly_revenue,
           COUNT(DISTINCT o.order_id)::INTEGER AS monthly_order_count
    FROM cleaned.orders o
    LEFT JOIN cleaned.order_items oi ON oi.order_id = o.order_id
    GROUP BY TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM')
),
ranked_monthly AS (
    SELECT year_month,
           monthly_revenue,
           monthly_order_count,
           LAG(monthly_revenue) OVER (ORDER BY year_month) AS previous_month_revenue,
           SUM(monthly_revenue) OVER (ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS sql_three_month_rolling_revenue,
           SUM(monthly_order_count) OVER (ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS sql_three_month_rolling_order_count,
           CASE
               WHEN COALESCE(LAG(monthly_revenue) OVER (ORDER BY year_month), 0) = 0 THEN NULL
               ELSE (monthly_revenue - COALESCE(LAG(monthly_revenue) OVER (ORDER BY year_month), 0)) / COALESCE(LAG(monthly_revenue) OVER (ORDER BY year_month), 0)
           END AS sql_monthly_revenue_growth,
           SUM(monthly_revenue) OVER (ORDER BY year_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS sql_cumulative_revenue
    FROM source_monthly
),
python_monthly AS (
    SELECT year_month,
           monthly_revenue AS python_monthly_revenue,
           monthly_order_count AS python_monthly_order_count,
           three_month_rolling_revenue AS python_three_month_rolling_revenue,
           three_month_rolling_order_count AS python_three_month_rolling_order_count,
           monthly_revenue_growth AS python_monthly_revenue_growth,
           cumulative_revenue AS python_cumulative_revenue
    FROM validation.monthly_features
),
matched AS (
    SELECT s.year_month,
           s.sql_three_month_rolling_revenue,
           p.python_three_month_rolling_revenue,
           s.sql_three_month_rolling_order_count,
           p.python_three_month_rolling_order_count,
           s.sql_monthly_revenue_growth,
           p.python_monthly_revenue_growth,
           s.sql_cumulative_revenue,
           p.python_cumulative_revenue,
           CASE
               WHEN s.sql_three_month_rolling_revenue IS NULL AND p.python_three_month_rolling_revenue IS NULL THEN 0
               WHEN s.sql_three_month_rolling_revenue IS NULL OR p.python_three_month_rolling_revenue IS NULL THEN 1e9
               ELSE ABS(s.sql_three_month_rolling_revenue - p.python_three_month_rolling_revenue)
           END AS diff_roll_revenue,
           CASE
               WHEN s.sql_three_month_rolling_order_count IS NULL AND p.python_three_month_rolling_order_count IS NULL THEN 0
               WHEN s.sql_three_month_rolling_order_count IS NULL OR p.python_three_month_rolling_order_count IS NULL THEN 1e9
               ELSE ABS(s.sql_three_month_rolling_order_count - p.python_three_month_rolling_order_count)
           END AS diff_roll_count,
           CASE
               WHEN s.sql_monthly_revenue_growth IS NULL AND p.python_monthly_revenue_growth IS NULL THEN 0
               WHEN s.sql_monthly_revenue_growth IS NULL OR p.python_monthly_revenue_growth IS NULL THEN 1e9
               ELSE ABS(s.sql_monthly_revenue_growth - p.python_monthly_revenue_growth)
           END AS diff_growth,
           CASE
               WHEN s.sql_cumulative_revenue IS NULL AND p.python_cumulative_revenue IS NULL THEN 0
               WHEN s.sql_cumulative_revenue IS NULL OR p.python_cumulative_revenue IS NULL THEN 1e9
               ELSE ABS(s.sql_cumulative_revenue - p.python_cumulative_revenue)
           END AS diff_cumulative
    FROM ranked_monthly s
    FULL OUTER JOIN python_monthly p USING (year_month)
    WHERE s.year_month IS NULL OR p.year_month IS NULL
       OR (s.sql_three_month_rolling_revenue IS NULL AND p.python_three_month_rolling_revenue IS NOT NULL)
       OR (s.sql_three_month_rolling_revenue IS NOT NULL AND p.python_three_month_rolling_revenue IS NULL)
       OR (s.sql_three_month_rolling_revenue IS NOT NULL AND p.python_three_month_rolling_revenue IS NOT NULL AND ABS(s.sql_three_month_rolling_revenue - p.python_three_month_rolling_revenue) >= 0.000001)
)
SELECT 'three_month_rolling_revenue' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff_roll_revenue)::NUMERIC AS max_numeric_difference
FROM matched
UNION ALL
SELECT 'three_month_rolling_order_count' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff_roll_count)::NUMERIC AS max_numeric_difference
FROM (
    SELECT s.year_month,
           s.sql_three_month_rolling_order_count,
           p.python_three_month_rolling_order_count,
           CASE
               WHEN s.sql_three_month_rolling_order_count IS NULL AND p.python_three_month_rolling_order_count IS NULL THEN 0
               WHEN s.sql_three_month_rolling_order_count IS NULL OR p.python_three_month_rolling_order_count IS NULL THEN 1e9
               ELSE ABS(s.sql_three_month_rolling_order_count - p.python_three_month_rolling_order_count)
           END AS diff_roll_count
    FROM ranked_monthly s
    FULL OUTER JOIN python_monthly p USING (year_month)
    WHERE s.year_month IS NULL OR p.year_month IS NULL
       OR (s.sql_three_month_rolling_order_count IS NULL AND p.python_three_month_rolling_order_count IS NOT NULL)
       OR (s.sql_three_month_rolling_order_count IS NOT NULL AND p.python_three_month_rolling_order_count IS NULL)
       OR (s.sql_three_month_rolling_order_count IS NOT NULL AND p.python_three_month_rolling_order_count IS NOT NULL AND ABS(s.sql_three_month_rolling_order_count - p.python_three_month_rolling_order_count) >= 0.000001)
) x
UNION ALL
SELECT 'monthly_revenue_growth' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff_growth)::NUMERIC AS max_numeric_difference
FROM (
    SELECT s.year_month,
           s.sql_monthly_revenue_growth,
           p.python_monthly_revenue_growth,
           CASE
               WHEN s.sql_monthly_revenue_growth IS NULL AND p.python_monthly_revenue_growth IS NULL THEN 0
               WHEN s.sql_monthly_revenue_growth IS NULL OR p.python_monthly_revenue_growth IS NULL THEN 1e9
               ELSE ABS(s.sql_monthly_revenue_growth - p.python_monthly_revenue_growth)
           END AS diff_growth
    FROM ranked_monthly s
    FULL OUTER JOIN python_monthly p USING (year_month)
    WHERE s.year_month IS NULL OR p.year_month IS NULL
       OR (s.sql_monthly_revenue_growth IS NULL AND p.python_monthly_revenue_growth IS NOT NULL)
       OR (s.sql_monthly_revenue_growth IS NOT NULL AND p.python_monthly_revenue_growth IS NULL)
       OR (s.sql_monthly_revenue_growth IS NOT NULL AND p.python_monthly_revenue_growth IS NOT NULL AND ABS(s.sql_monthly_revenue_growth - p.python_monthly_revenue_growth) > 1e-12)
) x
UNION ALL
SELECT 'cumulative_revenue' AS metric,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*)::INTEGER AS mismatched_records,
       MAX(diff_cumulative)::NUMERIC AS max_numeric_difference
FROM (
    SELECT s.year_month,
           s.sql_cumulative_revenue,
           p.python_cumulative_revenue,
           CASE
               WHEN s.sql_cumulative_revenue IS NULL AND p.python_cumulative_revenue IS NULL THEN 0
               WHEN s.sql_cumulative_revenue IS NULL OR p.python_cumulative_revenue IS NULL THEN 1e9
               ELSE ABS(s.sql_cumulative_revenue - p.python_cumulative_revenue)
           END AS diff_cumulative
    FROM ranked_monthly s
    FULL OUTER JOIN python_monthly p USING (year_month)
    WHERE s.year_month IS NULL OR p.year_month IS NULL
       OR (s.sql_cumulative_revenue IS NULL AND p.python_cumulative_revenue IS NOT NULL)
       OR (s.sql_cumulative_revenue IS NOT NULL AND p.python_cumulative_revenue IS NULL)
       OR (s.sql_cumulative_revenue IS NOT NULL AND p.python_cumulative_revenue IS NOT NULL AND ABS(s.sql_cumulative_revenue - p.python_cumulative_revenue) >= 0.000001)
) x;

SELECT metric, status, mismatched_records, max_numeric_difference
FROM validation.validation_summary
ORDER BY metric;

SELECT COUNT(*) AS total_validation_checks,
       SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) AS pass_count,
       SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) AS fail_count,
       SUM(CASE WHEN status = 'ALLOWED_NULL' THEN 1 ELSE 0 END) AS allowed_null_count,
       SUM(CASE WHEN mismatched_records > 0 THEN mismatched_records ELSE 0 END) AS total_mismatched_records,
       MAX(CASE WHEN max_numeric_difference IS NULL THEN 0 ELSE max_numeric_difference END) AS max_numeric_difference,
       CASE WHEN SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) = 0 THEN 'FULLY_ALIGNED' ELSE 'MISALIGNED' END AS alignment_status
FROM validation.validation_summary;
