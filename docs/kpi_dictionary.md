# KPI Dictionary

**Project:** Retail Sales Performance Analytics  
**Phase:** 13 — KPI Design  
**Status:** Final KPI Definition Reference  
**Purpose:** Single source of truth for KPI names, definitions, formulas, grains, sources, and calculation rules.

---

## 1. KPI Governance Rules

### Revenue Standard
- **Item Revenue = `price`**
- **Order Revenue = SUM(item price)**
- **Total Revenue = SUM(order_revenue)**
- Freight is excluded from Total Revenue.
- Payment Value is not treated as Revenue.

### Order Standard
- Order-level KPIs use unique `order_id`.
- Item-level KPIs use item records.
- Multi-item orders are aggregated to order level before order-level KPI calculation where required.

### Customer Standard
- Customer identity is based on `customer_unique_id`.
- A repeat customer has `customer_order_count > 1`.

### Monthly Time Basis
- Sales and order trend KPIs use order purchase date.
- Monthly grouping uses the engineered `year_month` feature.

### Delivery Standard
- Delivery KPIs require valid delivery timestamps.
- `delivery_time_days = actual delivery date − purchase date`
- `processing_time_days = carrier delivery date − purchase date`
- On-time delivery: `delivery_difference_days <= 0`
- Late delivery: `delivery_difference_days > 0`

### Review Standard
- Order-level review score uses the engineered order-level review score.
- Low satisfaction: `review_score <= 2`
- Neutral satisfaction: `review_score = 3`
- High satisfaction: `review_score >= 4`
- Missing reviews are excluded from review-based KPI denominators.

### Missing Value Standard
- Missing required values are excluded from the relevant KPI.
- Zero or missing denominators return NULL/NaN.
- Missing values are not converted to zero unless zero is semantically correct.

---

# 2. Primary KPIs

## 2.1 Total Revenue

| Field | Definition |
|---|---|
| KPI Name | Total Revenue |
| Business Definition | Total product sales value excluding freight. |
| Formula | `SUM(Item Revenue)` |
| Unit | Currency |
| Source Dataset | `orders_features.csv` |
| Source Columns | `order_revenue` |
| Grain | Order |
| Filters | Revenue-eligible orders |
| Exclusions | Freight and non-revenue values |
| Aggregation | SUM |
| Time Basis | Order purchase date |
| Hierarchy | Primary |
| Business Importance | Core measure of overall sales performance. |

**SQL Logic:** `SUM(order_revenue)`

**DAX Logic:**
```DAX
Total Revenue = SUM(Orders[order_revenue])
```

---

## 2.2 Total Orders

| Field | Definition |
|---|---|
| KPI Name | Total Orders |
| Business Definition | Number of unique orders. |
| Formula | `COUNT(DISTINCT order_id)` |
| Unit | Count |
| Source Dataset | `orders_features.csv` |
| Source Columns | `order_id` |
| Grain | Order |
| Filters | All orders unless KPI context specifies otherwise |
| Exclusions | Duplicate order records |
| Aggregation | DISTINCT COUNT |
| Time Basis | Order purchase date |
| Hierarchy | Primary |
| Business Importance | Measures transaction volume. |

**SQL Logic:** `COUNT(DISTINCT order_id)`

**DAX Logic:**
```DAX
Total Orders = DISTINCTCOUNT(Orders[order_id])
```

---

## 2.3 Average Order Value

| Field | Definition |
|---|---|
| KPI Name | Average Order Value |
| Business Definition | Average product revenue generated per revenue-eligible order. |
| Formula | `Total Revenue / Revenue-Eligible Orders` |
| Numerator | Total Revenue |
| Denominator | DISTINCTCOUNT(order_id) |
| Unit | Currency |
| Source Dataset | `orders_features.csv` |
| Source Columns | `order_revenue`, `order_id` |
| Grain | Order |
| Filters | Revenue-eligible orders |
| Exclusions | Orders without eligible revenue |
| Aggregation | SUM / DISTINCT COUNT |
| Time Basis | Order purchase date |
| Hierarchy | Primary |
| Business Importance | Measures average transaction value. |

**SQL Logic:** `SUM(order_revenue) / COUNT(DISTINCT order_id)`

**DAX Logic:**
```DAX
Average Order Value =
DIVIDE(
    [Total Revenue],
    DISTINCTCOUNT(Orders[order_id])
)
```

---

## 2.4 Monthly Revenue Growth

| Field | Definition |
|---|---|
| KPI Name | Monthly Revenue Growth |
| Business Definition | Percentage change in revenue compared with the previous month. |
| Formula | `(Current Month Revenue − Previous Month Revenue) / Previous Month Revenue × 100` |
| Numerator | Current Month Revenue − Previous Month Revenue |
| Denominator | Previous Month Revenue |
| Unit | Percentage |
| Source Dataset | `monthly_features.csv` / `orders_features.csv` |
| Source Columns | `year_month`, `order_revenue` |
| Grain | Month |
| Filters | Revenue-eligible orders |
| Exclusions | First month without a prior-month comparison |
| Aggregation | SUM with period comparison |
| Time Basis | Order purchase month |
| Hierarchy | Primary |
| Business Importance | Measures sales momentum. |

**SQL Logic:** Aggregate monthly revenue and compare with `LAG(monthly_revenue)`.

**DAX Logic:**
```DAX
Monthly Revenue Growth =
VAR PreviousRevenue =
    CALCULATE(
        [Total Revenue],
        DATEADD('Date'[Date], -1, MONTH)
    )
RETURN
DIVIDE([Total Revenue] - PreviousRevenue, PreviousRevenue)
```

---

## 2.5 Total Customers

| Field | Definition |
|---|---|
| KPI Name | Total Customers |
| Business Definition | Number of unique customers. |
| Formula | `COUNT(DISTINCT customer_unique_id)` |
| Unit | Count |
| Source Dataset | `customer_features.csv` / `customers_processed.csv` |
| Source Columns | `customer_unique_id` |
| Grain | Customer |
| Filters | All identifiable customers |
| Exclusions | Duplicate customer records |
| Aggregation | DISTINCT COUNT |
| Time Basis | Customer activity context |
| Hierarchy | Primary |
| Business Importance | Measures customer base size. |

**SQL Logic:** `COUNT(DISTINCT customer_unique_id)`

**DAX Logic:**
```DAX
Total Customers =
DISTINCTCOUNT(Customers[customer_unique_id])
```

---

## 2.6 Repeat Customer Rate

| Field | Definition |
|---|---|
| KPI Name | Repeat Customer Rate |
| Business Definition | Percentage of customers with more than one order. |
| Formula | `Repeat Customers / Total Customers × 100` |
| Numerator | Customers where `repeat_customer_flag = 1` |
| Denominator | Total unique customers |
| Unit | Percentage |
| Source Dataset | `customer_features.csv` |
| Source Columns | `customer_unique_id`, `repeat_customer_flag`, `customer_order_count` |
| Grain | Customer |
| Filters | Customers with valid customer identity |
| Exclusions | Duplicate customer records |
| Aggregation | DISTINCT COUNT |
| Time Basis | Customer order history |
| Hierarchy | Primary |
| Business Importance | Measures customer retention and repeat purchasing behavior. |

**SQL Logic:** Count distinct repeat customers divided by distinct customers.

**DAX Logic:**
```DAX
Repeat Customer Rate =
DIVIDE(
    CALCULATE(
        DISTINCTCOUNT(Customers[customer_unique_id]),
        Customers[repeat_customer_flag] = 1
    ),
    [Total Customers]
)
```

---

## 2.7 On-Time Delivery Rate

| Field | Definition |
|---|---|
| KPI Name | On-Time Delivery Rate |
| Business Definition | Percentage of classified delivered orders delivered on or before the estimated date. |
| Formula | `On-Time Delivered Orders / Classified Delivered Orders × 100` |
| Numerator | Orders where `on_time_delivery_flag = 1` |
| Denominator | On-time + late classified orders |
| Unit | Percentage |
| Source Dataset | `orders_features.csv` |
| Source Columns | `on_time_delivery_flag`, `late_delivery_flag`, `delivery_difference_days` |
| Grain | Order |
| Filters | Classified delivered orders |
| Exclusions | Missing or unclassified delivery records |
| Aggregation | COUNT / COUNT |
| Time Basis | Delivery and estimated delivery dates |
| Hierarchy | Primary |
| Business Importance | Measures delivery reliability. |

**SQL Logic:** Count on-time classified orders divided by all classified orders.

**DAX Logic:**
```DAX
On-Time Delivery Rate =
DIVIDE(
    CALCULATE(COUNTROWS(Orders), Orders[on_time_delivery_flag] = 1),
    CALCULATE(
        COUNTROWS(Orders),
        Orders[on_time_delivery_flag] = 1 ||
        Orders[late_delivery_flag] = 1
    )
)
```

---

## 2.8 Average Delivery Time

| Field | Definition |
|---|---|
| KPI Name | Average Delivery Time |
| Business Definition | Average number of days from order purchase to customer delivery. |
| Formula | `AVG(Delivery Date − Purchase Date)` |
| Unit | Days |
| Source Dataset | `orders_features.csv` |
| Source Columns | `delivery_time_days` |
| Grain | Order |
| Filters | Orders with valid delivery duration |
| Exclusions | Missing or invalid delivery timestamps |
| Aggregation | AVG |
| Time Basis | Purchase date to customer delivery date |
| Hierarchy | Primary |
| Business Importance | Measures customer-facing delivery speed. |

**SQL Logic:** `AVG(delivery_time_days)`

**DAX Logic:**
```DAX
Average Delivery Time =
AVERAGE(Orders[delivery_time_days])
```

---

## 2.9 Average Review Score

| Field | Definition |
|---|---|
| KPI Name | Average Review Score |
| Business Definition | Average customer review score across reviewed orders. |
| Formula | `Total Review Score / Reviewed Orders` |
| Unit | Score |
| Source Dataset | `orders_features.csv` / `reviews_processed.csv` |
| Source Columns | `review_score` |
| Grain | Order |
| Filters | Orders with valid review scores |
| Exclusions | Orders without reviews |
| Aggregation | AVG |
| Time Basis | Review availability at order level |
| Hierarchy | Primary |
| Business Importance | Measures overall customer satisfaction. |

**SQL Logic:** `AVG(review_score)`

**DAX Logic:**
```DAX
Average Review Score =
AVERAGE(Orders[review_score])
```

---

# 3. Supporting KPIs

## 3.1 Total Order Value

**Definition:** Total value including item price and freight.

**Formula:** `SUM(Item Price + Freight Value)`

**Source:** `orders_features.csv`

**Columns:** `total_order_value`

**Grain:** Order

**Aggregation:** SUM

**Hierarchy:** Supporting

**SQL Logic:** `SUM(total_order_value)`

**DAX Logic:**
```DAX
Total Order Value = SUM(Orders[total_order_value])
```

---

## 3.2 Monthly Revenue

**Definition:** Revenue aggregated by purchase month.

**Formula:** `SUM(Order Revenue) by Purchase Month`

**Source:** `monthly_features.csv` / `orders_features.csv`

**Columns:** `year_month`, `order_revenue`

**Grain:** Month

**Aggregation:** SUM

**Time Basis:** Order purchase date

**Hierarchy:** Supporting

**SQL Logic:** `SUM(order_revenue) GROUP BY year_month`

**DAX Logic:**
```DAX
Monthly Revenue = [Total Revenue]
```

---

## 3.3 Average Items per Order

**Definition:** Average number of items purchased per order.

**Formula:** `Total Items / Item-Eligible Orders`

**Source:** `orders_features.csv`

**Columns:** `items_per_order`

**Grain:** Order

**Aggregation:** AVG

**Hierarchy:** Supporting

**SQL Logic:** `AVG(items_per_order)`

**DAX Logic:**
```DAX
Average Items per Order =
AVERAGE(Orders[items_per_order])
```

---

## 3.4 Customer Lifetime Revenue

**Definition:** Revenue associated with a customer's complete order history.

**Formula:** `SUM(Customer Lifetime Revenue)` at customer analysis grain.

**Source:** `customer_features.csv`

**Columns:** `customer_lifetime_revenue`

**Grain:** Customer

**Aggregation:** SUM only when customer grain is preserved.

**Hierarchy:** Supporting

**Control:** Do not use as a duplicate global revenue KPI.

**SQL Logic:** `SUM(customer_lifetime_revenue)`

**DAX Logic:**
```DAX
Customer Lifetime Revenue =
SUM(Customers[customer_lifetime_revenue])
```

---

## 3.5 Average Customer Order Value

**Definition:** Average order value at customer analysis grain.

**Formula:** `Customer Lifetime Revenue / Customer Order Count`

**Source:** `customer_features.csv`

**Columns:** `average_customer_order_value`

**Grain:** Customer

**Aggregation:** AVG

**Hierarchy:** Supporting

**Control:** This is not necessarily equal to global Total Revenue / Total Orders.

**SQL Logic:** `AVG(average_customer_order_value)`

**DAX Logic:**
```DAX
Average Customer Order Value =
AVERAGE(Customers[average_customer_order_value])
```

---

## 3.6 Category Revenue

**Definition:** Product revenue generated by each product category.

**Formula:** `SUM(Item Revenue) by Category`

**Source:** `order_items_features.csv`

**Columns:** `item_revenue`, `product_category`

**Grain:** Item / Category

**Aggregation:** SUM

**Hierarchy:** Supporting

**Control:** Aggregate item data before joins that could multiply rows.

**SQL Logic:** `SUM(item_revenue) GROUP BY product_category`

**DAX Logic:**
```DAX
Category Revenue =
SUM(OrderItems[item_revenue])
```

---

## 3.7 Category Revenue Share

**Definition:** Percentage contribution of each category to total revenue.

**Formula:** `Category Revenue / Total Revenue × 100`

**Source:** `order_items_features.csv`

**Columns:** `item_revenue`, `product_category`

**Grain:** Category

**Aggregation:** SUM / SUM

**Hierarchy:** Supporting

**SQL Logic:** `Category Revenue / Total Revenue`

**DAX Logic:**
```DAX
Category Revenue Share =
DIVIDE(
    [Category Revenue],
    CALCULATE([Category Revenue], ALL(Products))
)
```

---

## 3.8 Product Revenue

**Definition:** Revenue generated by each product.

**Formula:** `SUM(Item Revenue) by Product`

**Source:** `order_items_features.csv`

**Columns:** `product_id`, `item_revenue`

**Grain:** Product / Item

**Aggregation:** SUM

**Hierarchy:** Supporting

**SQL Logic:** `SUM(item_revenue) GROUP BY product_id`

**DAX Logic:**
```DAX
Product Revenue =
SUM(OrderItems[item_revenue])
```

---

## 3.9 Seller Revenue

**Definition:** Revenue generated from items sold by each seller.

**Formula:** `SUM(Item Revenue) by Seller`

**Source:** `order_items_features.csv`

**Columns:** `seller_id`, `item_revenue`

**Grain:** Seller / Item

**Aggregation:** SUM

**Hierarchy:** Supporting

**SQL Logic:** `SUM(item_revenue) GROUP BY seller_id`

**DAX Logic:**
```DAX
Seller Revenue =
SUM(OrderItems[item_revenue])
```

---

## 3.10 Seller Order Count

**Definition:** Number of unique orders containing items sold by a seller.

**Formula:** `COUNT(DISTINCT order_id) by Seller`

**Source:** `order_items_features.csv`

**Columns:** `seller_id`, `order_id`

**Grain:** Seller / Order

**Aggregation:** DISTINCT COUNT

**Hierarchy:** Supporting

**Control:** Always use distinct order IDs.

**SQL Logic:** `COUNT(DISTINCT order_id) GROUP BY seller_id`

**DAX Logic:**
```DAX
Seller Order Count =
DISTINCTCOUNT(OrderItems[order_id])
```

---

## 3.11 Revenue by Customer State

**Definition:** Revenue generated by customers located in each state.

**Formula:** `SUM(Order Revenue) by Customer State`

**Source:** `orders_features.csv`, customer data

**Columns:** `order_revenue`, `customer_state`

**Grain:** State / Order

**Aggregation:** SUM

**Hierarchy:** Supporting

**Control:** Controlled customer-to-order join required.

**SQL Logic:** `SUM(order_revenue) GROUP BY customer_state`

**DAX Logic:**
```DAX
State Revenue = [Total Revenue]
```

---

## 3.12 Total Payment Value

**Definition:** Total recorded payment value.

**Formula:** `SUM(Payment Value per Order)`

**Source:** `orders_features.csv` / `payments_processed.csv`

**Columns:** `payment_value_per_order`

**Grain:** Order

**Aggregation:** SUM

**Hierarchy:** Supporting

**Control:** Payment value is not revenue.

**SQL Logic:** `SUM(payment_value_per_order)`

**DAX Logic:**
```DAX
Total Payment Value =
SUM(Orders[payment_value_per_order])
```

---

## 3.13 Payment Method Share

**Definition:** Percentage of total payment value represented by each payment method.

**Formula:** `Payment Value by Method / Total Payment Value × 100`

**Source:** `payments_processed.csv`

**Columns:** `payment_type`, `payment_value`

**Grain:** Payment Method / Payment

**Aggregation:** SUM / SUM

**Hierarchy:** Supporting

**SQL Logic:** `SUM(payment_value) / SUM(SUM(payment_value)) OVER ()`

**DAX Logic:**
```DAX
Payment Method Share =
DIVIDE(
    SUM(Payments[payment_value]),
    CALCULATE(
        SUM(Payments[payment_value]),
        ALL(Payments[payment_type])
    )
)
```

---

## 3.14 Average Payment Installments

**Definition:** Average number of installments per eligible order.

**Formula:** `AVG(number_payment_installments)`

**Source:** `orders_features.csv`

**Columns:** `number_payment_installments`

**Grain:** Order

**Aggregation:** AVG

**Hierarchy:** Supporting

**SQL Logic:** `AVG(number_payment_installments)`

**DAX Logic:**
```DAX
Average Payment Installments =
AVERAGE(Orders[number_payment_installments])
```

---

## 3.15 Average Processing Time

**Definition:** Average time from order purchase to carrier delivery.

**Formula:** `AVG(Carrier Date − Purchase Date)`

**Source:** `orders_features.csv`

**Columns:** `processing_time_days`

**Grain:** Order

**Aggregation:** AVG

**Hierarchy:** Supporting

**SQL Logic:** `AVG(processing_time_days)`

**DAX Logic:**
```DAX
Average Processing Time =
AVERAGE(Orders[processing_time_days])
```

---

## 3.16 Late Delivery Rate

**Definition:** Percentage of classified delivered orders delivered after the estimated date.

**Formula:** `Late Delivered Orders / Classified Delivered Orders × 100`

**Source:** `orders_features.csv`

**Columns:** `late_delivery_flag`, `on_time_delivery_flag`

**Grain:** Order

**Aggregation:** COUNT / COUNT

**Hierarchy:** Supporting

**SQL Logic:** Count late orders divided by classified orders.

**DAX Logic:**
```DAX
Late Delivery Rate =
DIVIDE(
    CALCULATE(COUNTROWS(Orders), Orders[late_delivery_flag] = 1),
    CALCULATE(
        COUNTROWS(Orders),
        Orders[on_time_delivery_flag] = 1 ||
        Orders[late_delivery_flag] = 1
    )
)
```

---

## 3.17 Average Delivery Difference

**Definition:** Average difference between actual and estimated delivery dates.

**Formula:** `AVG(Actual Delivery Date − Estimated Delivery Date)`

**Source:** `orders_features.csv`

**Columns:** `delivery_difference_days`

**Grain:** Order

**Aggregation:** AVG

**Hierarchy:** Supporting

**SQL Logic:** `AVG(delivery_difference_days)`

**DAX Logic:**
```DAX
Average Delivery Difference =
AVERAGE(Orders[delivery_difference_days])
```

---

## 3.18 Total Freight Value

**Definition:** Total freight charged across order items.

**Formula:** `SUM(Freight Value)`

**Source:** `order_items_features.csv`

**Columns:** `freight_value`

**Grain:** Item

**Aggregation:** SUM

**Hierarchy:** Supporting

**SQL Logic:** `SUM(freight_value)`

**DAX Logic:**
```DAX
Total Freight Value =
SUM(OrderItems[freight_value])
```

---

## 3.19 Low Satisfaction Rate

**Definition:** Percentage of reviewed orders with review score of 1 or 2.

**Formula:** `Low Satisfaction Orders / Reviewed Orders × 100`

**Source:** `orders_features.csv`

**Columns:** `low_review_flag`, `review_score`

**Grain:** Order

**Aggregation:** COUNT / COUNT

**Hierarchy:** Supporting

**SQL Logic:** Count low-review orders divided by reviewed orders.

**DAX Logic:**
```DAX
Low Satisfaction Rate =
DIVIDE(
    CALCULATE(COUNTROWS(Orders), Orders[low_review_flag] = 1),
    COUNT(Orders[review_score])
)
```

---

## 3.20 High Satisfaction Rate

**Definition:** Percentage of reviewed orders with review score of 4 or 5.

**Formula:** `High Satisfaction Orders / Reviewed Orders × 100`

**Source:** `orders_features.csv`

**Columns:** `high_review_flag`, `review_score`

**Grain:** Order

**Aggregation:** COUNT / COUNT

**Hierarchy:** Supporting

**SQL Logic:** Count high-review orders divided by reviewed orders.

**DAX Logic:**
```DAX
High Satisfaction Rate =
DIVIDE(
    CALCULATE(COUNTROWS(Orders), Orders[high_review_flag] = 1),
    COUNT(Orders[review_score])
)
```

---

# 4. Diagnostic Metrics

## 4.1 Rolling 3-Month Revenue

**Definition:** Revenue accumulated across the current month and previous two months.

**Formula:** `Revenue from Current Month + Previous 2 Months`

**Source:** `monthly_features.csv`

**Columns:** `year_month`, revenue measure

**Grain:** Month

**Aggregation:** Rolling SUM

**Hierarchy:** Diagnostic

**SQL Logic:** Rolling `SUM()` across current and previous two periods.

**DAX Logic:**
```DAX
Rolling 3M Revenue =
CALCULATE(
    [Total Revenue],
    DATESINPERIOD(
        'Date'[Date],
        MAX('Date'[Date]),
        -3,
        MONTH
    )
)
```

---

## 4.2 Multi-Payment Order Rate

**Definition:** Percentage of orders containing more than one payment record.

**Formula:** `Multi-Payment Orders / Payment Orders × 100`

**Source:** `orders_features.csv`

**Columns:** `multi_payment_flag`, `order_id`

**Grain:** Order

**Aggregation:** COUNT / COUNT

**Hierarchy:** Diagnostic

**SQL Logic:** Count orders where `multi_payment_flag = 1` divided by payment orders.

**DAX Logic:**
```DAX
Multi-Payment Order Rate =
DIVIDE(
    CALCULATE(
        COUNTROWS(Orders),
        Orders[multi_payment_flag] = 1
    ),
    COUNTROWS(Orders)
)
```

---

## 4.3 Freight-to-Price Ratio

**Definition:** Freight cost relative to item revenue.

**Formula:** `Freight Value / Item Revenue`

**Source:** `order_items_features.csv`

**Columns:** `freight_to_price_ratio`, `freight_value`, `item_revenue`

**Grain:** Item

**Aggregation:** Aggregation rule must be explicitly preserved.

**Hierarchy:** Diagnostic

**Control:** Do not blindly average item ratios when a weighted ratio is required.

**SQL Logic:** `AVG(freight_to_price_ratio)` when unweighted item-level average is intended.

**DAX Logic:**
```DAX
Freight-to-Price Ratio =
AVERAGE(OrderItems[freight_to_price_ratio])
```

---

# 5. KPI Summary

| Hierarchy | KPI Count |
|---|---:|
| Primary | 9 |
| Supporting | 20 |
| Diagnostic | 3 |
| **Total** | **32** |

---

# 6. Feasibility Controls

1. Customer Lifetime Revenue must not duplicate Total Revenue in executive reporting.
2. Average Customer Order Value must remain explicitly customer-grain.
3. Category and geography KPIs require controlled aggregation before joins.
4. Seller Order Count must use distinct `order_id`.
5. Freight-to-Price Ratio requires an explicit aggregation method.
6. Payment Value must remain separate from Revenue.
7. Delivery KPIs exclude missing or unclassified records.
8. Review KPIs use order-level review scores to prevent duplicate review counting.

---

**Phase 13 Status:** KPI Dictionary finalized.  
**Boundary:** KPI definitions only. Final KPI computation begins in Phase 14.
