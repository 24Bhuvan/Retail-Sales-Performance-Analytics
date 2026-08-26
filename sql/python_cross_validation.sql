-- ============================================================================
-- PHASE 9 — STEP 12
-- PYTHON vs POSTGRESQL CROSS-VALIDATION
-- ============================================================================

SELECT 'orders_rows' AS metric, COUNT(*)::numeric AS value
FROM olist_orders_dataset

UNION ALL

SELECT 'order_items_rows', COUNT(*)::numeric
FROM olist_order_items_dataset

UNION ALL

SELECT 'payments_rows', COUNT(*)::numeric
FROM olist_order_payments_dataset

UNION ALL

SELECT 'reviews_rows', COUNT(*)::numeric
FROM olist_order_reviews_dataset

UNION ALL

SELECT 'customers_rows', COUNT(*)::numeric
FROM olist_customers_dataset

UNION ALL

SELECT 'products_rows', COUNT(*)::numeric
FROM olist_products_dataset

UNION ALL

SELECT 'sellers_rows', COUNT(*)::numeric
FROM olist_sellers_dataset

UNION ALL

SELECT 'category_translation_rows', COUNT(*)::numeric
FROM product_category_name_translation

UNION ALL

SELECT 'order_count',
       COUNT(DISTINCT order_id)::numeric
FROM olist_orders_dataset

UNION ALL

SELECT 'order_item_count',
       COUNT(*)::numeric
FROM olist_order_items_dataset

UNION ALL

SELECT 'payment_count',
       COUNT(*)::numeric
FROM olist_order_payments_dataset

UNION ALL

SELECT 'review_count',
       COUNT(*)::numeric
FROM olist_order_reviews_dataset

UNION ALL

SELECT 'customer_count',
       COUNT(DISTINCT customer_id)::numeric
FROM olist_customers_dataset

UNION ALL

SELECT 'seller_count',
       COUNT(DISTINCT seller_id)::numeric
FROM olist_sellers_dataset

UNION ALL

SELECT 'product_count',
       COUNT(DISTINCT product_id)::numeric
FROM olist_products_dataset

UNION ALL

SELECT 'category_count',
       COUNT(DISTINCT product_category_name)::numeric
FROM olist_products_dataset

UNION ALL

SELECT 'total_payment_value',
       ROUND(SUM(payment_value)::numeric, 2)
FROM olist_order_payments_dataset

UNION ALL

SELECT 'total_item_price',
       ROUND(SUM(price)::numeric, 2)
FROM olist_order_items_dataset

ORDER BY metric;