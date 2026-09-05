# Power BI Data Model

## 1. Purpose

This document defines the Power BI semantic data model for the **Retail Sales Performance Analytics** project.

The model translates the validated PostgreSQL analytical schema into a governed Power BI semantic layer while preserving:

* Analytical grain
* Primary and foreign-key relationships
* Dimension and fact separation
* Filter propagation
* Date-role behavior
* Business hierarchies
* Measure calculation paths
* Model performance requirements

The Power BI model must reflect the approved PostgreSQL analytical design rather than introduce an independent or conflicting data model.

---

# 2. Modeling Principles

The semantic model follows dimensional-modeling principles.

The primary design objectives are:

1. Preserve the grain of every fact table.
2. Use dimensions as the primary filtering mechanism.
3. Maintain one-to-many relationships wherever the model supports them.
4. Prefer single-direction filter propagation.
5. Avoid direct fact-to-fact relationships.
6. Avoid unnecessary many-to-many relationships.
7. Centralize business calculations in DAX measures.
8. Use a dedicated calendar dimension for time analysis.
9. Avoid duplicating upstream business logic in Power BI.
10. Keep the model understandable, performant, and maintainable.

---

# 3. Model Architecture

The Power BI semantic model follows a star-schema architecture.

```text
                    Dimension Layer
                          │
                          │ 1:*
                          ▼
                     Fact Layer
                          │
                          ▼
                    Measure Layer
                          │
                          ▼
                    Report Layer
```

The active semantic model contains:

### Fact Tables

```text
fact_orders
fact_order_items
fact_payments
fact_reviews
```

### Dimension Tables

```text
dim_date
dim_customer
dim_product
dim_seller
dim_order_status
```

### Excluded from Active Model

```text
dim_geography
```

---

# 4. Fact Table Specifications

## 4.1 fact_orders

### Business Grain

**One row per `order_id`.**

This is the authoritative order-level fact.

### Key Fields

* `order_key`
* `order_id`
* `customer_key`
* `order_status_key`
* `purchase_date_key`
* `approved_date_key`
* `delivered_carrier_date_key`
* `delivered_customer_date_key`
* `estimated_delivery_date_key`

### Business Purpose

Supports:

* Order counting
* Order-status analysis
* Order lifecycle analysis
* Delivery analysis
* Order-level customer analysis

### Modeling Rule

`order_id` must remain unique at this fact grain.

---

## 4.2 fact_order_items

### Business Grain

**One row per `order_id + order_item_id`.**

This is the item-level transactional fact.

### Key Fields

* `order_item_key`
* `order_id`
* `product_key`
* `seller_key`
* `order_date_key`
* `price`
* `freight_value`

### Business Purpose

Supports:

* Product sales analysis
* Category sales analysis
* Seller sales analysis
* Item-volume analysis
* Freight analysis

### Modeling Rule

Do not aggregate this fact to order level inside Power BI merely to simplify relationships.

The item-level grain is required for product and seller analysis.

---

## 4.3 fact_payments

### Business Grain

**One row per `order_id + payment_sequential`.**

This is the payment-level transactional fact.

### Key Fields

* `payment_key`
* `order_id`
* `customer_key`
* `payment_date_key`
* `payment_type`
* `payment_installments`
* `payment_value`

### Business Purpose

Supports:

* Payment-value analysis
* Total sales as defined by the approved KPI specification
* Payment-method analysis
* Installment analysis
* Customer sales analysis where payment value is the approved sales definition

### Critical Modeling Rule

`fact_payments` must remain separate from `fact_order_items`.

An order can contain multiple payment records and multiple order-item records. Joining these facts directly can multiply rows and produce incorrect aggregations.

---

## 4.4 fact_reviews

### Business Grain

**One source review record associated with an order.**

### Key Fields

* `review_key`
* `review_id`
* `order_id`
* `customer_key`
* `review_date_key`
* `review_score`
* Review comment attributes where required

### Business Purpose

Supports:

* Customer satisfaction analysis
* Review-score analysis
* Review-volume analysis
* Review trends

### Modeling Rule

Review records remain independent of payment and order-item facts.

---

# 5. Dimension Table Specifications

## 5.1 dim_date

### Business Grain

**One row per calendar date.**

### Key Fields

* `date_key`
* `full_date`
* `year`
* `quarter`
* `quarter_name`
* `month`
* `month_name`
* `month_year`
* `week_of_year`
* `day_of_month`
* `day_of_week`
* `day_name`
* `is_weekend`

### Business Purpose

Provides the common calendar context for:

* Time trends
* Monthly reporting
* Quarterly reporting
* Yearly reporting
* Time intelligence
* Delivery-date analysis
* Date-based filtering

`dim_date` is the authoritative date dimension for Power BI.

---

## 5.2 dim_customer

### Business Grain

**One row per `customer_id`.**

### Key Fields

* `customer_key`
* `customer_id`
* `customer_unique_id`
* ZIP prefix
* City
* State

### Business Purpose

Supports:

* Customer analysis
* Customer counts
* Repeat-customer analysis
* Customer sales
* Customer geography

### Important Identity Distinction

`customer_id` represents the order-level customer record in the source model, while `customer_unique_id` represents the customer identity used for unique-customer analysis.

The appropriate identifier must therefore be selected according to the KPI definition.

---

## 5.3 dim_product

### Business Grain

**One row per `product_id`.**

### Key Fields

* `product_key`
* `product_id`
* Product category
* Product attributes

### Business Purpose

Supports:

* Product performance
* Category performance
* Product ranking
* Product contribution
* Product drill-down

### Hierarchy

```text
Product Category
       ↓
Product
```

---

## 5.4 dim_seller

### Business Grain

**One row per `seller_id`.**

### Key Fields

* `seller_key`
* `seller_id`
* ZIP prefix
* City
* State

### Business Purpose

Supports:

* Seller performance
* Seller ranking
* Seller geography
* Seller drill-down

### Hierarchy

```text
Seller State
      ↓
Seller City
      ↓
Seller
```

---

## 5.5 dim_order_status

### Business Grain

**One row per distinct order status.**

### Key Fields

* `order_status_key`
* Order status

### Business Purpose

Provides standardized order-status filtering and grouping for order analysis.

---

# 6. Relationship Specification

The default relationship pattern is:

```text
Dimension
    │
    │ 1:*
    ▼
Fact
```

## Relationship Standards

| Property                   | Standard                          |
| -------------------------- | --------------------------------- |
| Cardinality                | 1:*                               |
| Filter direction           | Single                            |
| Primary filter path        | Dimension → Fact                  |
| Many-to-many               | Avoid                             |
| Bidirectional filtering    | Avoid unless explicitly justified |
| Fact-to-fact relationships | Prohibited                        |

---

# 7. Customer Relationships

The customer dimension provides customer context to the relevant facts.

```text
dim_customer
      │
      ├────────► fact_orders
      │
      ├────────► fact_payments
      │
      └────────► fact_reviews
```

Customer filters can therefore support:

* Order analysis
* Payment-based sales analysis
* Review analysis

---

# 8. Product Relationship

```text
dim_product
      │
      ▼
fact_order_items
```

This relationship supports:

* Product Sales
* Category Sales
* Product Sales %
* Category Sales %
* Product ranking

---

# 9. Seller Relationship

```text
dim_seller
      │
      ▼
fact_order_items
```

This relationship supports:

* Seller Sales
* Seller Orders
* Seller ranking
* Seller geographic analysis

---

# 10. Order Status Relationship

```text
dim_order_status
      │
      ▼
fact_orders
```

This relationship supports:

* Order-status distribution
* Status-based filtering
* Order lifecycle analysis

---

# 11. Date Relationships

`dim_date` provides date context to the relevant fact tables.

Logical relationships include:

```text
dim_date
   │
   ├────────► fact_order_items
   │
   ├────────► fact_payments
   │
   ├────────► fact_reviews
   │
   └────────► fact_orders
```

For `fact_orders`, multiple date roles exist and must be managed explicitly.

---

# 12. Fact-to-Fact Relationship Policy

Direct fact-to-fact relationships are prohibited in the core model.

Do not create:

```text
fact_orders       ✕ fact_order_items
fact_orders       ✕ fact_payments
fact_orders       ✕ fact_reviews
fact_order_items  ✕ fact_payments
fact_order_items  ✕ fact_reviews
fact_payments     ✕ fact_reviews
```

### Primary Example

```text
fact_payments ✕ fact_order_items
```

must not be directly related.

### Reason

Both tables can contain multiple rows for the same order.

A direct relationship can therefore cause:

* Row multiplication
* Double counting
* Incorrect totals
* Ambiguous filter propagation
* Many-to-many behavior
* Incorrect KPI results

The semantic model must instead use shared dimensions and appropriate measures.

---

# 13. Date Role-Playing Architecture

`fact_orders` contains multiple date keys representing different business events.

## Date Roles

1. Purchase Date
2. Approved Date
3. Delivered-to-Carrier Date
4. Delivered-to-Customer Date
5. Estimated Delivery Date

These represent different analytical events and must not be treated as interchangeable.

## Design Requirement

Power BI must explicitly manage these relationships.

The model must avoid multiple ambiguous active paths from `dim_date` into `fact_orders`.

Where an alternate date role is required, the implementation should use an appropriate inactive relationship and DAX relationship activation, or another explicitly designed role-playing-date pattern.

The selected approach must be documented during implementation.

---

# 14. Primary Reporting Date

For standard sales reporting, the project should establish a single primary reporting date role.

The default business reporting context is based on the approved sales/order-date definition.

Alternate date roles should be used only for analyses that specifically require them, such as:

* Approval timing
* Carrier handoff timing
* Customer delivery timing
* Estimated delivery timing

This prevents date ambiguity and ensures that standard report pages use a predictable date context.

---

# 15. Date Table Configuration

`dim_date[full_date]` should be configured as the Power BI Date Table column.

## Required Attributes

```text
Year
Quarter
Month
Month Number
Month Name
Month Year
Week of Year
Day
Day of Month
Day of Week
Day Name
Weekend Flag
```

## Sorting Requirements

`month_name` must be sorted by:

```text
month
```

`month_year` must be sorted chronologically rather than alphabetically.

---

# 16. Hierarchy Specification

## Date Hierarchy

```text
Year
  ↓
Quarter
  ↓
Month
  ↓
Day
```

Alternative reporting path:

```text
Year
  ↓
Month
```

## Product Hierarchy

```text
Category
   ↓
Product
```

## Seller Geography Hierarchy

```text
Seller State
      ↓
Seller City
      ↓
Seller
```

Hierarchies should be created only where they improve navigation and analytical interpretation.

---

# 17. Geography Architecture

The PostgreSQL analytical schema contains:

```text
dim_geography
```

However, it is excluded from the active Power BI semantic model.

## Reason

The current analytical model does not provide the required direct relationship between `dim_geography` and the customer/seller dimensions.

Creating an artificial relationship would introduce unnecessary modeling complexity and potentially ambiguous filter behavior.

## Approved Geography Sources

### Customer Geography

```text
dim_customer[state]
dim_customer[city]
```

### Seller Geography

```text
dim_seller[state]
dim_seller[city]
```

The current Power BI model therefore performs geographic analysis through the customer and seller dimensions.

---

# 18. Business Filter Paths

## Product Analysis

```text
dim_product
      ↓
fact_order_items
      ↓
Product / Category Measures
```

## Seller Analysis

```text
dim_seller
      ↓
fact_order_items
      ↓
Seller Measures
```

## Customer Analysis

```text
dim_customer
      ↓
fact_orders
fact_payments
fact_reviews
```

## Regional Customer Analysis

```text
dim_customer[state]
      ↓
fact_payments
      ↓
Regional Sales
```

## Time Analysis

```text
dim_date
      ↓
Relevant Fact
      ↓
Time-Based Measure
```

---

# 19. Analytical Grain Governance

The semantic model must preserve the approved grain of each fact.

| Fact               | Grain                                          |
| ------------------ | ---------------------------------------------- |
| `fact_orders`      | One row per order                              |
| `fact_order_items` | One row per order-item                         |
| `fact_payments`    | One row per order-payment sequence             |
| `fact_reviews`     | One source review record per order association |

Measures must be written with the fact grain in mind.

For example:

* Order count should use distinct `order_id`.
* Seller order count should use distinct orders in `fact_order_items`.
* Payment totals should aggregate payment records.
* Item volume should aggregate item records.

---

# 20. KPI-to-Fact Alignment

The semantic model supports different business measures through different facts.

| Business Area  | Primary Fact                    | Key Dimensions                                 |
| -------------- | ------------------------------- | ---------------------------------------------- |
| Total Sales    | `fact_payments`                 | `dim_date`, `dim_customer`                     |
| Orders         | `fact_orders`                   | `dim_date`, `dim_customer`, `dim_order_status` |
| Products       | `fact_order_items`              | `dim_product`, `dim_date`                      |
| Sellers        | `fact_order_items`              | `dim_seller`, `dim_date`                       |
| Customers      | `fact_orders` / `fact_payments` | `dim_customer`, `dim_date`                     |
| Reviews        | `fact_reviews`                  | `dim_customer`, `dim_date`                     |
| Regional Sales | `fact_payments`                 | `dim_customer`, `dim_date`                     |
| Delivery       | `fact_orders`                   | `dim_date`                                     |

The selected fact must match the approved KPI definition.

---

# 21. Sales Measure Governance

The model intentionally contains two different monetary concepts.

## Payment-Based Sales

Source:

```text
fact_payments[payment_value]
```

Used for:

* Total Sales
* AOV
* Time-based sales analysis
* Regional Sales
* Customer Sales

## Item-Price Sales

Source:

```text
fact_order_items[price]
```

Used for:

* Category Sales
* Product Sales
* Seller Sales

These measures must not be treated as interchangeable.

The distinction must be preserved in:

* DAX
* Visual titles
* Documentation
* KPI validation
* Business interpretation

---

# 22. Customer Identity Governance

Two customer identifiers exist:

```text
customer_id
customer_unique_id
```

The semantic model must use the appropriate identifier for the business question.

### `customer_id`

Used for the customer dimension grain and source-level customer/order relationship.

### `customer_unique_id`

Used for unique customer analysis, including:

* Total Customers
* Repeat Customers
* Repeat Customer %

This distinction is critical for correct customer metrics.

---

# 23. Unsupported Tables and Relationships

The Power BI model must not introduce analytical objects that do not exist in the approved PostgreSQL model.

Do not create:

```text
fact_sales
dim_category
dim_payment
```

unless the PostgreSQL analytical architecture is formally changed and revalidated.

The existing design instead uses:

```text
fact_payments
fact_order_items
dim_product
```

to represent the required analytical concepts.

---

# 24. Semantic Model Naming Standards

Power BI display names should be business-friendly while preserving traceability to the PostgreSQL source.

Examples:

| Technical Object   | Report/Semantic Interpretation |
| ------------------ | ------------------------------ |
| `fact_order_items` | Order Items                    |
| `fact_payments`    | Payments                       |
| `dim_product`      | Product                        |
| `dim_customer`     | Customer                       |
| `dim_seller`       | Seller                         |
| `dim_date`         | Date                           |
| `dim_order_status` | Order Status                   |

Measures should use clear business names:

```text
Total Sales
Total Orders
AOV
Product Sales
Category Sales
Seller Sales
Regional Sales
Repeat Customers
```

---

# 25. Model Performance Standards

The semantic model should be optimized around:

```text
Star Schema
      +
Import Storage
      +
Single-Direction Relationships
      +
Controlled Cardinality
      +
Explicit Measures
      +
Minimal Unnecessary Columns
```

## Rules

* Avoid unnecessary columns.
* Avoid unnecessary high-cardinality attributes.
* Avoid unnecessary calculated columns.
* Avoid bidirectional relationships.
* Avoid fact-to-fact relationships.
* Avoid many-to-many relationships.
* Use dimension fields for slicers.
* Use measures for dynamic calculations.
* Keep large ranking visuals appropriately filtered.

Performance optimization must be evidence-based rather than adding complexity preemptively.

---

# 26. Model Validation Checklist

Before the semantic model is considered implementation-ready:

* [ ] All approved fact tables are loaded.
* [ ] All required dimensions are loaded.
* [ ] `dim_geography` remains excluded unless the model is redesigned.
* [ ] Fact grains match PostgreSQL definitions.
* [ ] Primary/foreign-key paths are correct.
* [ ] All intended relationships use the correct cardinality.
* [ ] Filter direction is single-direction.
* [ ] No direct fact-to-fact relationship exists.
* [ ] No unnecessary many-to-many relationship exists.
* [ ] `dim_date` is configured as the Date Table.
* [ ] `month_name` is sorted correctly.
* [ ] `month_year` is chronologically sorted.
* [ ] Order date roles are explicitly managed.
* [ ] Customer identity is correctly handled.
* [ ] Payment-based and item-price sales remain distinct.
* [ ] Model relationships produce expected filter propagation.
* [ ] Model performance is acceptable under representative report usage.

---

# 27. Final Semantic Model Specification

| Component                  | Approved Design               |
| -------------------------- | ----------------------------- |
| Modeling approach          | Star schema                   |
| Fact tables                | 4                             |
| Active dimensions          | 5                             |
| Excluded dimension         | `dim_geography`               |
| Fact-to-fact relationships | None                          |
| Standard cardinality       | 1:*                           |
| Filter direction           | Single                        |
| Date dimension             | `dim_date`                    |
| Date column                | `dim_date[full_date]`         |
| Product hierarchy          | Category → Product            |
| Seller hierarchy           | State → City → Seller         |
| Storage mode               | Import                        |
| Source                     | PostgreSQL `analytics` schema |
| Business calculations      | DAX measures                  |
| Primary reporting layer    | Power BI semantic model       |

---

# 28. Final Model Architecture

```text
                         dim_date
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
   fact_orders      fact_order_items    fact_payments
          │                 │                 │
     ┌────┴────┐       ┌────┴────┐            │
     │         │       │         │            │
     ▼         ▼       ▼         ▼            │
dim_customer  dim_order_status  dim_product  dim_seller
     │
     ▼
fact_reviews
```

The diagram represents the logical semantic structure. The actual Power BI relationship configuration must follow the approved relationship specification and must not introduce direct fact-to-fact relationships.

---

# 29. Model Decision

The Power BI semantic model is finalized as a governed star schema built directly from the PostgreSQL `analytics` schema.

The implementation will:

* Preserve the grain of all four fact tables.
* Use five active dimensions.
* Exclude `dim_geography` from the active model.
* Use one-to-many dimension-to-fact relationships.
* Use single-direction filtering.
* Prevent fact-to-fact relationships.
* Use `dim_date` as the authoritative calendar.
* Explicitly manage multiple order-date roles.
* Preserve payment-based versus item-price sales definitions.
* Use `customer_unique_id` for unique-customer analysis.
* Centralize analytical calculations in DAX measures.

**Status: POWER BI DATA MODEL — FINALIZED FOR IMPLEMENTATION**
