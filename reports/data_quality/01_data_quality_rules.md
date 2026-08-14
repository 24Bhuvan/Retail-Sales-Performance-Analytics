# 01 — Data Quality Rules

## 1. Purpose

This document defines the data quality dimensions and validation rules that will be tested during Phase 4 — Data Quality Assessment.

The objective is to identify and classify actual data quality issues in the Olist datasets without treating legitimate variation, skewness, or statistical outliers as data errors.

Phase 3 profiling identified observations, potential anomalies, and confirmed anomalies. Phase 4 will validate these findings against explicit data quality rules.

---

## 2. Data Quality Dimensions

| Dimension | What We Check |
|---|---|
| Completeness | Missing / NULL values |
| Uniqueness | Duplicate primary keys and duplicate records |
| Validity | Invalid values, ranges, and domains |
| Consistency | Contradictions within or between datasets |
| Referential Integrity | Foreign-key values existing in parent datasets |
| Timeliness / Chronology | Invalid date sequences |
| Accuracy Proxies | Values violating structural or supported data constraints |

---

## 3. Rule Classification

| Classification | Meaning |
|---|---|
| Pass | No records violate the rule |
| Confirmed Anomaly | Clear structural or logical violation |
| Potential Anomaly | Suspicious condition requiring interpretation |
| Observation | Measurable characteristic that is not necessarily an error |

### Important Principle

A statistical outlier is not automatically a data quality error.

Examples:

- A product price of R$5,000 may be unusual but can be valid.
- A review score of `1` is valid even if statistically unusual.
- Negative latitude or longitude values are valid geographic coordinates.
- Rare categories are not automatically invalid.
- Skewed distributions are not automatically data quality problems.

---

# 4. Completeness Rules

## DQ-C01 — Required Primary Key Completeness

Primary-key columns must not contain NULL values.

**Keys:**

- customers → `customer_id`
- orders → `order_id`
- order_items → `order_id + order_item_id`
- order_payments → `order_id + payment_sequential`
- order_reviews → `review_id`
- products → `product_id`
- sellers → `seller_id`
- product_category_name_translation → `product_category_name`

**Failure:** Any NULL value in a defined primary-key component.

## DQ-C02 — Missing Value Assessment

Calculate NULL counts and NULL percentages for every column.

Missing values are assessed according to structural context rather than automatically classified as errors.

Particular attention:

- `orders.order_approved_at`
- `orders.order_delivered_carrier_date`
- `orders.order_delivered_customer_date`
- `products.product_category_name`
- `products.product_name_lenght`
- `products.product_description_lenght`
- `products.product_photos_qty`
- `products.product_weight_g`
- `products.product_length_cm`
- `products.product_height_cm`
- `products.product_width_cm`
- `order_reviews.review_comment_title`
- `order_reviews.review_comment_message`

Optional or conditionally applicable fields are not invalid solely because they contain NULLs.

---

# 5. Uniqueness Rules

## DQ-U01 — Primary Key Uniqueness

Each defined primary key must uniquely identify a record.

**Failure:** Duplicate primary-key combinations.

## DQ-U02 — Full Row Duplicate Assessment

Identify exact duplicate records across all columns.

Special attention: `olist_geolocation_dataset.csv`.

Phase 3 identified 261,831 exact duplicate rows (26.18%).

These duplicates will be quantified and investigated.

Full-row duplication in geolocation will not automatically be classified as an error because no primary key is defined for this dataset.

---

# 6. Validity Rules

## DQ-V01 — Review Score Domain

**Dataset:** `order_reviews`

```text
1 <= review_score <= 5
```

Any value outside 1–5 is invalid.

## DQ-V02 — Payment Installments Domain

**Dataset:** `order_payments`

```text
payment_installments >= 0
```

Negative installment counts are invalid.

## DQ-V03 — Payment Value Domain

**Dataset:** `order_payments`

```text
payment_value >= 0
```

Negative payment amounts are invalid.

## DQ-V04 — Order Item Price Domain

**Dataset:** `order_items`

```text
price >= 0
```

Negative prices are invalid.

Statistically high prices are not invalid merely because they are outliers.

## DQ-V05 — Freight Value Domain

**Dataset:** `order_items`

```text
freight_value >= 0
```

Negative freight values are invalid.

## DQ-V06 — Product Quantity / Dimension Domains

**Dataset:** `products`

The following fields must not contain negative values:

- `product_photos_qty`
- `product_weight_g`
- `product_length_cm`
- `product_height_cm`
- `product_width_cm`

```text
value >= 0
```

## DQ-V07 — Geographic Coordinate Range

**Dataset:** `geolocation`

```text
-90 <= geolocation_lat <= 90
-180 <= geolocation_lng <= 180
```

Negative latitude and longitude values are valid.

## DQ-V08 — Categorical Domain Validation

Validate categorical values against the values represented in the source data.

Relevant columns:

- `orders.order_status`
- `order_payments.payment_type`
- `order_reviews.review_score`
- `customers.customer_state`
- `sellers.seller_state`
- `products.product_category_name`

Rare categories alone are not considered invalid.

---

# 7. Consistency and Chronology Rules

## DQ-S01 — Order Lifecycle Consistency

Expected sequence:

```text
order_purchase_timestamp
        ↓
order_approved_at
        ↓
order_delivered_carrier_date
        ↓
order_delivered_customer_date
```

Each applicable pair is checked independently.

## DQ-S02 — Approval After Purchase

```text
order_approved_at >= order_purchase_timestamp
```

Failure: approval occurs before purchase.

## DQ-S03 — Carrier Delivery After Purchase

```text
order_delivered_carrier_date >= order_purchase_timestamp
```

Failure: carrier delivery occurs before purchase.

Phase 3 identified 166 such records.

## DQ-S04 — Customer Delivery After Purchase

```text
order_delivered_customer_date >= order_purchase_timestamp
```

Failure: customer delivery occurs before purchase.

## DQ-S05 — Customer Delivery After Carrier Delivery

```text
order_delivered_customer_date >= order_delivered_carrier_date
```

Failure: customer delivery occurs before carrier delivery.

Phase 3 identified 23 such records.

## DQ-S06 — Estimated Delivery After Purchase

```text
order_estimated_delivery_date >= order_purchase_timestamp
```

Failure: estimated delivery occurs before purchase.

## DQ-S07 — Review Chronology

Where both timestamps are available:

```text
review_answer_timestamp >= review_creation_date
```

Failure: review answer occurs before review creation.

---

# 8. Referential Integrity Rules

## DQ-R01 — Orders → Customers

```text
orders.customer_id
    →
customers.customer_id
```

Every non-NULL `orders.customer_id` must exist in `customers.customer_id`.

## DQ-R02 — Order Items → Orders

```text
order_items.order_id
    →
orders.order_id
```

Every `order_items.order_id` must exist in `orders.order_id`.

## DQ-R03 — Order Items → Products

```text
order_items.product_id
    →
products.product_id
```

Every `order_items.product_id` must exist in `products.product_id`.

## DQ-R04 — Order Items → Sellers

```text
order_items.seller_id
    →
sellers.seller_id
```

Every `order_items.seller_id` must exist in `sellers.seller_id`.

## DQ-R05 — Payments → Orders

```text
order_payments.order_id
    →
orders.order_id
```

Every `order_payments.order_id` must exist in `orders.order_id`.

## DQ-R06 — Reviews → Orders

```text
order_reviews.order_id
    →
orders.order_id
```

Every `order_reviews.order_id` must exist in `orders.order_id`.

## DQ-R07 — Products → Category Translation

```text
products.product_category_name
    →
product_category_name_translation.product_category_name
```

Every non-NULL product category expected to have a translation should have a matching category.

Phase 3 identified 13 non-matching records.

## DQ-R08 — Customer ZIP → Geolocation

```text
customers.customer_zip_code_prefix
    →
geolocation.geolocation_zip_code_prefix
```

Customer ZIP prefixes will be checked for representation in geolocation.

Phase 3 identified 278 non-matching references.

## DQ-R09 — Seller ZIP → Geolocation

```text
sellers.seller_zip_code_prefix
    →
geolocation.geolocation_zip_code_prefix
```

Seller ZIP prefixes will be checked for representation in geolocation.

Phase 3 identified 7 non-matching references.

---

# 9. Accuracy Proxy Rules

The project has no independent ground-truth source for verifying the factual accuracy of individual records.

Therefore, Phase 4 will use only supported structural and business-consistency proxies:

- Valid numeric domains
- Valid review score range
- Valid geographic coordinate ranges
- Non-negative monetary values
- Non-negative quantities
- Valid primary keys
- Valid foreign-key relationships
- Valid chronological sequences

No rule will claim factual accuracy without an external ground-truth source.

---

# 10. Outlier Handling Policy

Phase 3 identified many IQR-based potential outliers.

These will **not** automatically be classified as data quality errors.

Relevant variables include:

- `order_items.price`
- `order_items.freight_value`
- `order_payments.payment_value`
- `order_payments.payment_installments`
- `products.product_weight_g`
- `products.product_photos_qty`
- `products.product_description_lenght`
- `order_reviews.review_score`
- `geolocation_lat`
- `geolocation_lng`

### Rule

```text
Statistical outlier ≠ data quality error
```

An outlier becomes a confirmed quality issue only when it violates an explicit validity, consistency, or structural rule.

---

# 11. Rare Category Handling Policy

Rare categories identified in Phase 3 are observations, not errors.

A category will only be classified as invalid if it violates a supported categorical domain rule or is demonstrably malformed.

No category will be removed or merged solely because of low frequency.

---

# 12. Date Range Handling Policy

The datasets do not share identical date ranges.

A date outside the dominant dataset period will not automatically be classified as invalid.

For example, `order_items.shipping_limit_date` contains four records from 2020. These records will be investigated through relationship and chronology checks rather than rejected solely because most order activity occurs during 2016–2018.

---

# 13. Phase 4 Assessment Principle

```text
Observed in profiling
        ↓
Test against explicit quality rule
        ↓
Does it violate the rule?
        ↓
      YES ────────────── NO
       ↓                 ↓
Confirmed/Potential     Pass/
Anomaly                 Observation
```

The assessment will distinguish between:

1. Actual data quality violations
2. Potential anomalies requiring investigation
3. Legitimate statistical characteristics
4. Expected missing or sparse values
5. Passing quality checks

---

# 14. Rules Summary

| Rule ID | Dimension | Check | Expected Result |
|---|---|---|---|
| DQ-C01 | Completeness | PK NULLs | 0 |
| DQ-C02 | Completeness | Column NULLs | Quantify and contextualize |
| DQ-U01 | Uniqueness | Duplicate PKs | 0 |
| DQ-U02 | Uniqueness | Full-row duplicates | Quantify |
| DQ-V01 | Validity | Review score 1–5 | No violations |
| DQ-V02 | Validity | Installments >= 0 | No negative values |
| DQ-V03 | Validity | Payment value >= 0 | No negative values |
| DQ-V04 | Validity | Price >= 0 | No negative values |
| DQ-V05 | Validity | Freight >= 0 | No negative values |
| DQ-V06 | Validity | Product numeric fields >= 0 | No negative values |
| DQ-V07 | Validity | Geographic coordinate ranges | No out-of-range values |
| DQ-V08 | Validity | Categorical domains | No unsupported/malformed values |
| DQ-S01 | Consistency | Order lifecycle sequence | Chronologically valid |
| DQ-S02 | Chronology | Approval >= Purchase | No violations |
| DQ-S03 | Chronology | Carrier >= Purchase | No violations |
| DQ-S04 | Chronology | Customer delivery >= Purchase | No violations |
| DQ-S05 | Chronology | Customer delivery >= Carrier | No violations |
| DQ-S06 | Chronology | Estimated delivery >= Purchase | No violations |
| DQ-S07 | Chronology | Review answer >= Review creation | No violations |
| DQ-R01 | Referential Integrity | Orders → Customers | 100% match |
| DQ-R02 | Referential Integrity | Order Items → Orders | 100% match |
| DQ-R03 | Referential Integrity | Order Items → Products | 100% match |
| DQ-R04 | Referential Integrity | Order Items → Sellers | 100% match |
| DQ-R05 | Referential Integrity | Payments → Orders | 100% match |
| DQ-R06 | Referential Integrity | Reviews → Orders | 100% match |
| DQ-R07 | Referential Integrity | Products → Translation | Investigate non-matches |
| DQ-R08 | Referential Integrity | Customer ZIP → Geolocation | Investigate non-matches |
| DQ-R09 | Referential Integrity | Seller ZIP → Geolocation | Investigate non-matches |

---

# 15. Explicit Non-Rules

The following are **not** automatic data quality errors:

- High product prices
- High payment values
- High freight values
- Rare categories
- Category concentration
- Negative latitude
- Negative longitude
- Distribution skewness
- IQR outliers
- Large date gaps
- Missing optional review text
- Legitimate sparse categories

These characteristics may be reported as observations but require an explicit structural or business constraint before being classified as errors.
