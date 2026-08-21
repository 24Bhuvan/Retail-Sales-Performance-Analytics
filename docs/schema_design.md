# Phase 6 — Data Modeling: Schema Design

## 1. Document Information

| Field | Value |
|---|---|
| Project | Retail Sales Performance Analytics |
| Phase | Phase 6 — Data Modeling |
| Database | `retail_sales_analytics` |
| Database Engine | PostgreSQL |
| Modeling Approach | Dimensional Modeling / Star Schema |
| Source Layer | Cleaned Olist datasets |
| Target Schema | `analytics` |

---

## 2. Purpose

This document defines the analytical data model for the Retail Sales Performance Analytics project.

The model is designed to support:

- Sales performance analysis
- Customer analysis
- Product and category analysis
- Seller performance analysis
- Regional analysis
- Delivery performance analysis
- Customer review analysis
- Payment analysis
- Time-based analysis
- Power BI reporting

The raw/source structure is preserved separately. The analytical model is implemented in the `analytics` schema.

---

## 3. Modeling Principles

1. Raw data is not modified by the analytical model.
2. Cleaned datasets are used as the source for analytical tables.
3. Fact-table grain is explicitly defined.
4. Dimensions contain descriptive business attributes.
5. Fact tables contain foreign keys and measurable transactional information.
6. Different business grains are represented by separate fact tables.
7. Payments and order items remain separate facts to prevent row multiplication.
8. Reviews remain separate because `review_id` is not unique in the source data.
9. A dedicated Date dimension supports time analysis and Power BI time intelligence.
10. Foreign-key relationships are enforced in the analytical layer.
11. Surrogate keys are used for analytical dimensions.
12. The model is designed for reliable aggregation and Power BI consumption.

---

# 4. Analytical Model Architecture

The analytical model contains the following core tables:

### Dimensions

- `dim_date`
- `dim_customer`
- `dim_seller`
- `dim_product`
- `dim_geography`
- `dim_order_status`

### Facts

- `fact_orders`
- `fact_order_items`
- `fact_payments`
- `fact_reviews`

Conceptual structure:

```text
                         dim_date
                            |
                            |
dim_customer ---- fact_orders ---- dim_order_status
                      |
                      |
                fact_order_items
                  /          \
                 /            \
        dim_product        dim_seller


dim_customer ---- fact_payments ---- dim_date


dim_customer ---- fact_reviews ---- dim_date
```

The fact tables remain separated according to their business grain.

---

# 5. Fact Table Grain

Grain is the most important modeling decision because it defines exactly what one row represents.

| Fact Table | Grain |
|---|---|
| `fact_orders` | One row per `order_id` |
| `fact_order_items` | One row per `order_id + order_item_id` |
| `fact_payments` | One row per `order_id + payment_sequential` |
| `fact_reviews` | One source review record associated with an order |

## 5.1 Fact Orders

**Grain:** one row per order.

Primary business identifier:

```text
order_id
```

Supports:

- Total Orders
- Order Status Distribution
- AOV denominator
- Delivery analysis
- Customer order analysis

---

## 5.2 Fact Order Items

**Grain:** one row per order item.

Composite business identifier:

```text
order_id + order_item_id
```

Supports:

- Product performance
- Category performance
- Seller performance
- Item price analysis
- Freight analysis

Important source limitation:

> The Olist `order_items` dataset does not contain a quantity column. Each source row represents an order-item record.

Therefore, the analytical model must not invent a quantity field.

---

## 5.3 Fact Payments

**Grain:** one row per payment sequence within an order.

Composite business identifier:

```text
order_id + payment_sequential
```

Supports:

- Total Sales Revenue
- Payment Method Distribution
- Payment Installment Analysis
- Payment Value Analysis

### Why payments remain separate

An order can contain multiple order-item rows and multiple payment rows.

Joining these tables directly can create row multiplication.

Example:

```text
1 order
3 order items
2 payments

3 × 2 = 6 joined rows
```

This can incorrectly inflate payment values and other measures.

Therefore:

```text
fact_order_items
        +
fact_payments
```

are modeled as separate facts.

---

## 5.4 Fact Reviews

**Grain:** one source review record associated with an order.

`review_id` is retained as a business/source identifier but is not used as the analytical primary key because Phase 3 identified duplicate `review_id` values.

A generated `review_key` provides analytical row uniqueness while preserving the original `review_id`.

Supports:

- Average Customer Review Score
- Review analysis
- Customer satisfaction analysis

---

# 6. Dimension Definitions

## 6.1 `dim_date`

**Grain:** one row per calendar date.

Key:

```text
date_key
```

Attributes include:

- Full date
- Year
- Quarter
- Month
- Month name
- Month-year
- Week
- Day
- Day name
- Weekend flag

Purpose:

- Monthly trends
- Quarterly trends
- Year-over-year analysis
- Monthly growth
- Seasonal analysis
- Power BI time intelligence

The order fact contains multiple role-playing date keys:

- Purchase date
- Approval date
- Carrier delivery date
- Customer delivery date
- Estimated delivery date

---

## 6.2 `dim_customer`

**Grain:** one row per `customer_id`.

Key:

```text
customer_key
```

Business identifier:

```text
customer_id
```

Attributes:

- Customer unique ID
- ZIP-code prefix
- City
- State

Supports customer and regional analysis.

---

## 6.3 `dim_seller`

**Grain:** one row per `seller_id`.

Key:

```text
seller_key
```

Business identifier:

```text
seller_id
```

Attributes:

- ZIP-code prefix
- City
- State

Supports seller and regional performance analysis.

---

## 6.4 `dim_product`

**Grain:** one row per `product_id`.

Key:

```text
product_key
```

Business identifier:

```text
product_id
```

Attributes:

- Product category
- English product category
- Product name length
- Product description length
- Product photo count
- Weight
- Length
- Height
- Width

Supports:

- Product analysis
- Category analysis
- Product ranking
- Category contribution analysis

---

## 6.5 `dim_geography`

**Grain:** one row per unique ZIP-code prefix.

Key:

```text
geography_key
```

Business key:

```text
zip_code_prefix
```

Attributes:

- City
- State
- Latitude
- Longitude

Purpose:

- Geographic enrichment
- Customer geography
- Seller geography
- Regional analysis

The geolocation dataset was deduplicated during Phase 5 before being used as an analytical source.

---

## 6.6 `dim_order_status`

**Grain:** one row per distinct order status.

Key:

```text
order_status_key
```

Business attribute:

```text
order_status
```

Supports:

- Order Status Distribution
- Delivered/cancelled/etc. analysis
- Status filtering

---

# 7. Relationship Design

## Fact Orders

```text
dim_customer
    1
    |
    M
fact_orders
```

```text
dim_order_status
    1
    |
    M
fact_orders
```

Date relationships:

```text
dim_date
    1
    |
    M
fact_orders
```

The order fact contains multiple date foreign keys for different business events.

---

## Fact Order Items

```text
dim_product
    1
    |
    M
fact_order_items
```

```text
dim_seller
    1
    |
    M
fact_order_items
```

```text
dim_date
    1
    |
    M
fact_order_items
```

The order item fact retains `order_id` as the source business identifier.

---

## Fact Payments

```text
dim_customer
    1
    |
    M
fact_payments
```

```text
dim_date
    1
    |
    M
fact_payments
```

The payment fact retains:

```text
order_id
payment_sequential
```

as source-level identifiers.

---

## Fact Reviews

```text
dim_customer
    1
    |
    M
fact_reviews
```

```text
dim_date
    1
    |
    M
fact_reviews
```

The review fact retains:

```text
review_id
order_id
```

while using `review_key` as its analytical primary key.

---

# 8. Primary Keys

| Table | Primary Key |
|---|---|
| `dim_date` | `date_key` |
| `dim_customer` | `customer_key` |
| `dim_seller` | `seller_key` |
| `dim_product` | `product_key` |
| `dim_geography` | `geography_key` |
| `dim_order_status` | `order_status_key` |
| `fact_orders` | `order_key` |
| `fact_order_items` | `order_item_key` |
| `fact_payments` | `payment_key` |
| `fact_reviews` | `review_key` |

---

# 9. Business Keys

| Table | Business Key |
|---|---|
| `dim_customer` | `customer_id` |
| `dim_seller` | `seller_id` |
| `dim_product` | `product_id` |
| `dim_geography` | `zip_code_prefix` |
| `dim_order_status` | `order_status` |
| `fact_orders` | `order_id` |
| `fact_order_items` | `order_id + order_item_id` |
| `fact_payments` | `order_id + payment_sequential` |
| `fact_reviews` | Source `review_id` + order association |

---

# 10. Foreign-Key Design

| Fact | Foreign Key | Dimension |
|---|---|---|
| `fact_orders` | `customer_key` | `dim_customer` |
| `fact_orders` | `order_status_key` | `dim_order_status` |
| `fact_orders` | `purchase_date_key` | `dim_date` |
| `fact_orders` | `approved_date_key` | `dim_date` |
| `fact_orders` | `delivered_carrier_date_key` | `dim_date` |
| `fact_orders` | `delivered_customer_date_key` | `dim_date` |
| `fact_orders` | `estimated_delivery_date_key` | `dim_date` |
| `fact_order_items` | `product_key` | `dim_product` |
| `fact_order_items` | `seller_key` | `dim_seller` |
| `fact_order_items` | `order_date_key` | `dim_date` |
| `fact_payments` | `customer_key` | `dim_customer` |
| `fact_payments` | `payment_date_key` | `dim_date` |
| `fact_reviews` | `customer_key` | `dim_customer` |
| `fact_reviews` | `review_date_key` | `dim_date` |

---

# 11. Source-to-Target Mapping

| Source Dataset | Analytical Target |
|---|---|
| `olist_customers_dataset` | `dim_customer` |
| `olist_geolocation_dataset` | `dim_geography` |
| `olist_orders_dataset` | `fact_orders` + `dim_order_status` |
| `olist_order_items_dataset` | `fact_order_items` |
| `olist_order_payments_dataset` | `fact_payments` |
| `olist_order_reviews_dataset` | `fact_reviews` |
| `olist_products_dataset` | `dim_product` |
| `olist_sellers_dataset` | `dim_seller` |
| `product_category_name_translation` | Enrichment of `dim_product` |

---

# 12. KPI Support

The model is designed to support the Phase 1 KPI dictionary.

| KPI | Primary Analytical Source |
|---|---|
| Total Sales Revenue | `fact_payments` |
| Total Orders | `fact_orders` |
| Average Order Value | `fact_payments` + `fact_orders` |
| Monthly Sales Growth | `fact_payments` + `dim_date` |
| Top Product Categories | `fact_order_items` + `dim_product` |
| Top Performing Sellers | `fact_order_items` + `dim_seller` |
| Regional Sales Performance | Customer/geography + order/payment facts |
| Average Delivery Time | `fact_orders` + `dim_date` |
| On-Time Delivery Rate | `fact_orders` + `dim_date` |
| Average Customer Review Score | `fact_reviews` |
| Order Status Distribution | `fact_orders` + `dim_order_status` |
| Payment Method Distribution | `fact_payments` |

---

# 13. Important Modeling Constraints

## 13.1 No Inventory Fact

The project does not contain an inventory dataset.

Therefore, the model must not introduce:

- Inventory quantity
- Stock levels
- Stockout rate
- Inventory turnover

as actual analytical measures.

---

## 13.2 No Profit Measures

The available source structure does not provide reliable product cost information.

Therefore, the model must not invent:

- Profit
- Profit margin
- Gross margin

as validated business measures.

---

## 13.3 No Marketing Fact

The project does not contain campaign or marketing-spend data.

Therefore, marketing ROI and campaign-effectiveness measures are outside the model scope.

---

## 13.4 Reviews

`review_id` is not assumed to be unique.

The model therefore uses:

```text
review_key
```

as the analytical row identifier.

The original:

```text
review_id
```

is retained for traceability.

---

## 13.5 Geolocation

Geolocation is treated as an enrichment dimension at ZIP-code-prefix grain.

The Phase 5 cleaning process removed excess duplicate geolocation records while preserving one representative row per duplicate group.

---

# 14. Data Integrity Requirements

The analytical model must satisfy:

### Primary-key uniqueness

Every analytical primary key must be unique.

### Foreign-key integrity

Every non-null foreign key must resolve to its corresponding dimension.

### Fact-grain integrity

No fact table may contain duplicate records at its declared grain.

### No accidental many-to-many joins

Payments and order items must not be directly flattened together.

### Date integrity

Every populated date foreign key must correspond to a valid row in `dim_date`.

### Review integrity

Duplicate source `review_id` values must not cause analytical row loss.

---

# 15. Power BI Compatibility

The model is designed for Power BI using:

- One-to-many relationships
- Dimension-to-fact filtering
- Dedicated Date dimension
- Explicit DAX measures
- Separate fact tables by business grain
- Avoidance of unnecessary bidirectional relationships

Recommended relationship direction:

```text
DIMENSION
   |
   | 1:M
   v
FACT
```

The model should avoid unnecessary fact-to-fact relationships.

---

# 16. Analytical Layer Naming Convention

### Dimensions

```text
dim_<entity>
```

Examples:

```text
dim_customer
dim_product
dim_seller
dim_date
```

### Facts

```text
fact_<business_process>
```

Examples:

```text
fact_orders
fact_order_items
fact_payments
fact_reviews
```

Surrogate keys use:

```text
<entity>_key
```

Business/source identifiers retain their original names:

```text
customer_id
product_id
seller_id
order_id
```

---

# 17. Phase 6 Acceptance Criteria

Phase 6 is considered complete only when:

- [ ] Analytical schema is created successfully.
- [ ] All required dimensions exist.
- [ ] All required facts exist.
- [ ] Grain is documented for every fact.
- [ ] Primary keys are defined.
- [ ] Business keys are identified.
- [ ] Foreign keys are defined.
- [ ] Referential integrity is validated.
- [ ] Date dimension is created.
- [ ] Payments remain separated from order items.
- [ ] Review grain is explicitly handled.
- [ ] Geography is modeled at ZIP-prefix grain.
- [ ] Source-to-target mapping is documented.
- [ ] KPI support is documented.
- [ ] Star-schema diagram is finalized.
- [ ] PostgreSQL schema executes successfully.
- [ ] Analytical tables can be populated from the cleaned layer.
- [ ] Model is suitable for Power BI.

---

# 18. Phase 6 Deliverables

The expected Phase 6 deliverables are:

```text
sql/schema.sql
docs/schema_design.md
diagrams/star_schema.png
diagrams/er_diagram.png
reports/data_modeling/
```

The Phase 6 model becomes the structural foundation for:

- Phase 7 — Excel Analysis
- Phase 8 — SQL Development
- Phase 9 — Python Data Processing
- Phase 13 — KPI Design
- Phase 14 — Business Metrics Calculation
- Phase 15 — Power BI Planning
- Phase 17 — Dashboard Development

---

# 19. Final Model Summary

The analytical architecture is intentionally **not one giant flattened table**.

It uses:

```text
                    DIMENSIONS
                         |
        +----------------+----------------+
        |                |                |
        v                v                v
   FACT ORDERS    FACT ORDER ITEMS   FACT PAYMENTS
        |
        |
   FACT REVIEWS
```

with shared dimensions such as:

```text
dim_date
dim_customer
dim_product
dim_seller
dim_geography
dim_order_status
```

This preserves business grain, prevents aggregation errors, and provides a clean foundation for SQL analysis and Power BI.
