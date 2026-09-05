# Power BI Blueprint

## 1. Purpose

This document defines the architecture, semantic-model strategy, reporting structure, implementation boundaries, and operational design for the Power BI reporting layer of the **Retail Sales Performance Analytics** project.

The blueprint serves as the authoritative design baseline for Power BI implementation in Phase 16 and ensures that:

* Power BI consumes governed analytical data rather than raw source files.
* The semantic model follows dimensional-modeling principles.
* KPI calculations are implemented consistently through governed DAX measures.
* Report pages directly support approved business questions.
* Filters and interactions follow the semantic-model design.
* Performance and maintainability are considered before implementation.
* The Power BI solution remains within the approved project scope.

---

# 2. Business and Analytical Context

The Power BI solution provides descriptive and diagnostic analysis of the Olist retail dataset.

The reporting layer is intended to support:

* Sales performance monitoring
* Order-volume analysis
* Product and category analysis
* Seller performance analysis
* Regional performance analysis
* Customer and repeat-purchase analysis
* Executive decision-making

The solution is **not** intended to provide predictive analytics, profitability analysis, inventory optimization, marketing attribution, or real-time operational monitoring.

---

# 3. End-to-End Architecture

The analytical pipeline is structured as:

```text
Raw Source Data
       ↓
Cleaned Data
       ↓
Processed / Feature-Engineered Data
       ↓
PostgreSQL Analytical Database
       ↓
Power BI Semantic Model
       ↓
DAX Measures
       ↓
Report Pages
       ↓
Business Insights
```

Power BI is therefore a **consumption and semantic-analysis layer**, not a data-cleaning or primary transformation layer.

The PostgreSQL analytical database remains the reporting source of truth.

---

# 4. Data Pipeline Responsibilities

## 4.1 Raw Layer

**Location:**

```text
raw/
```

### Purpose

Preserve the original source data without analytical modification.

### Responsibilities

* Preserve source integrity.
* Maintain reproducibility.
* Provide the original reference point for downstream processing.

### Power BI

**Not connected directly to Power BI.**

---

## 4.2 Cleaned Layer

**Location:**

```text
cleaned/
```

### Purpose

Store data after data-quality treatment.

Typical activities include:

* Data-type standardization
* Missing-value treatment
* Duplicate handling
* Invalid-record handling
* Column standardization
* Data-quality corrections

### Power BI

**Not connected directly to Power BI.**

---

## 4.3 Processed Layer

**Location:**

```text
processed/
```

### Purpose

Store transformed and feature-engineered datasets used to construct the analytical model.

Typical activities include:

* Analytical transformations
* Derived attributes
* Feature engineering
* Dataset preparation
* Business-rule application

### Power BI

**Not connected directly to Power BI.**

---

# 5. PostgreSQL Analytical Layer

PostgreSQL is the centralized analytical storage and reporting-source layer.

## Database

```text
retail_sales_analytics
```

## Schema

```text
analytics
```

The `analytics` schema contains the dimensional model consumed by Power BI.

The database is responsible for:

* Storing governed analytical tables
* Maintaining analytical grain
* Enforcing key relationships
* Providing consistent dimensional attributes
* Providing the source data for Power BI

---

# 6. Power BI Data-Source Strategy

Power BI connects to PostgreSQL through the native PostgreSQL connector.

```text
Power BI
    │
    │ PostgreSQL Connector
    ↓
retail_sales_analytics
    ↓
analytics schema
```

## Source Selection

Power BI should consume the analytical tables in the `analytics` schema.

Power BI should **not** connect directly to:

```text
raw/
cleaned/
processed/
```

CSV files should not be used as the production reporting source when the governed PostgreSQL analytical layer is available.

---

# 7. Storage Mode Decision

## Selected Mode

**Import**

```text
PostgreSQL
      ↓
Power BI Import
      ↓
In-memory Semantic Model
```

## Rationale

Import mode is appropriate because:

* The project is descriptive rather than real-time.
* The analytical dataset is suitable for in-memory analysis.
* Report responsiveness is a priority.
* Complex DAX calculations benefit from the in-memory model.
* Real-time operational reporting is outside project scope.

## DirectQuery

DirectQuery is **not selected** for the current implementation.

It may only be reconsidered if future requirements introduce:

* Near-real-time reporting
* Very large-scale data
* Database-enforced query execution requirements
* Operational reporting requirements

Such a change would require architectural reassessment.

---

# 8. Analytical Table Inventory

The active Power BI model contains four fact tables and five primary dimensions.

## 8.1 Fact Tables

```text
analytics.fact_orders
analytics.fact_order_items
analytics.fact_payments
analytics.fact_reviews
```

### fact_orders

**Grain:**

One row per order.

**Business purpose:**

Order-level lifecycle and order-status analysis.

---

### fact_order_items

**Grain:**

One row per `order_id + order_item_id`.

**Business purpose:**

Product, category, seller, item-volume, price, and freight analysis.

---

### fact_payments

**Grain:**

One row per `order_id + payment_sequential`.

**Business purpose:**

Payment-value and payment-method analysis.

---

### fact_reviews

**Grain:**

One source review record associated with an order.

**Business purpose:**

Customer review and satisfaction analysis.

---

# 9. Dimension Inventory

## 9.1 dim_date

Provides the reporting calendar and time-intelligence attributes.

Key attributes include:

* Date
* Year
* Quarter
* Month
* Month Name
* Month Year
* Week
* Day
* Day of Week
* Weekend Flag

---

## 9.2 dim_customer

Provides customer-level and customer-geographic attributes.

Key attributes include:

* Customer ID
* Customer Unique ID
* ZIP Prefix
* City
* State

---

## 9.3 dim_product

Provides product-level analytical attributes.

Key attributes include:

* Product ID
* Product Category
* Product attributes

---

## 9.4 dim_seller

Provides seller-level and seller-geographic attributes.

Key attributes include:

* Seller ID
* ZIP Prefix
* City
* State

---

## 9.5 dim_order_status

Provides standardized order-status categories.

---

# 10. Excluded Dimension

## dim_geography

`analytics.dim_geography` exists in PostgreSQL but is excluded from the active Power BI semantic model.

### Reason

The current analytical model does not provide the required direct foreign-key path from customer/seller dimensions to `dim_geography`.

Therefore, the Power BI model should **not create an artificial or ambiguous relationship** merely to expose this dimension.

If a future requirement needs ZIP-prefix geographic analysis, the PostgreSQL model should first be redesigned and validated.

---

# 11. Semantic Model Architecture

The Power BI semantic model follows a dimensional star-schema approach.

```text
                     dim_date
                        │
                        ▼
dim_customer ───────► fact_orders
     │
     │
     └──────────────► fact_payments

dim_product ───────► fact_order_items ◄────── dim_seller

dim_order_status ──► fact_orders

dim_customer ──────► fact_reviews
dim_date ──────────► fact_reviews
```

The exact active relationships must follow the relationship specification in:

```text
docs/powerbi/powerbi_data_model.md
```

---

# 12. Relationship Strategy

The default relationship design is:

```text
Dimension
    │
    │ 1:*
    ▼
Fact
```

## Relationship Rules

Use:

* One-to-many cardinality
* Single-direction filtering
* Dimension-to-fact filter propagation

Avoid:

* Many-to-many relationships
* Unnecessary bidirectional relationships
* Fact-to-fact relationships
* Ambiguous filter paths

---

# 13. Fact-to-Fact Relationship Policy

The fact tables must not be directly related.

In particular:

```text
fact_orders       ✕ fact_order_items
fact_orders       ✕ fact_payments
fact_orders       ✕ fact_reviews
fact_order_items  ✕ fact_payments
fact_order_items  ✕ fact_reviews
fact_payments     ✕ fact_reviews
```

Shared dimensions provide the analytical filter paths.

This prevents ambiguous relationships and double-counting risks.

---

# 14. Date Architecture

`dim_date` is the authoritative Power BI date dimension.

The date table should be configured as the Power BI Date Table using:

```text
dim_date[full_date]
```

## Required Date Attributes

* Year
* Quarter
* Month
* Month Number
* Month Name
* Month Year
* Week of Year
* Day
* Day of Month
* Day of Week
* Day Name
* Weekend Flag

## Sorting

`month_name` must be sorted by the numeric month field.

`month_year` must be sorted using an appropriate chronological key rather than alphabetically.

---

# 15. Role-Playing Date Strategy

`fact_orders` contains multiple date roles:

* Purchase Date
* Approved Date
* Delivered-to-Carrier Date
* Delivered-to-Customer Date
* Estimated Delivery Date

These dates represent different business events.

The model must not create multiple active relationships from the same date dimension to the same fact table if that would create ambiguity.

The implementation must explicitly manage active and inactive date relationships and use appropriate DAX time/event-role logic where required.

The primary reporting date should be clearly identified during implementation.

---

# 16. Semantic Layer

The Power BI semantic layer consists of:

```text
Analytical Tables
       ↓
Relationships
       ↓
Date Model
       ↓
Measures
       ↓
Business-Friendly Metadata
       ↓
Report Visuals
```

The semantic layer abstracts database implementation details from report users.

Users should interact primarily with:

* Business-friendly dimensions
* Business-friendly measures
* Consistent KPI terminology

rather than raw database calculations.

---

# 17. DAX Measure Layer

Core measures include:

```text
[Total Sales]
[Total Orders]
[Total Items]
[AOV]

[MoM Sales Growth %]
[YoY Sales Growth %]
[YTD Sales]

[Category Sales]
[Product Sales]
[Category Sales %]
[Product Sales %]
[Top Product]
[Top Category]
[Cumulative Product Sales %]

[Regional Sales]
[Regional Sales %]
[Top Region]

[Seller Sales]
[Seller Orders]

[Total Customers]
[Repeat Customers]
[Repeat Customer %]
[Customer Sales]
[Orders per Customer]
```

Additional classification/supporting measures required by the report design must also be explicitly documented in `dax_plan.md`.

---

# 18. Sales Definition Governance

The Power BI model contains two distinct sales concepts.

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

These definitions must not be silently substituted for one another.

Every report visual must use the appropriate business definition.

---

# 19. Report Architecture

The report consists of four primary pages.

```text
1. Executive Sales Overview
2. Product & Category Analysis
3. Regional & Seller Performance
4. Customer Analysis
```

Each page has a distinct analytical purpose.

---

# 20. Page 1 — Executive Sales Overview

## Purpose

Provide an executive summary of overall sales performance.

## Primary Measures

* Total Sales
* Total Orders
* AOV
* YoY Sales Growth %
* YTD Sales

## Supporting Analysis

* Monthly Sales Trend
* Sales by Category
* Sales by Region

---

# 21. Page 2 — Product & Category Analysis

## Purpose

Analyze product and category performance and sales concentration.

## Primary Measures

* Category Sales
* Category Sales %
* Top Category
* Product Sales
* Product Sales %
* Top Product
* Total Items
* Cumulative Product Sales %

## Supporting Analysis

* Category ranking
* Product ranking
* Product Pareto
* Product performance detail

---

# 22. Page 3 — Regional & Seller Performance

## Purpose

Analyze geographic and seller performance.

## Primary Measures

* Regional Sales
* Regional Sales %
* Top Region
* Seller Sales
* Seller Orders

## Supporting Analysis

* Regional ranking
* Geographic breakdown
* Seller ranking
* Top/bottom sellers
* Seller performance detail

---

# 23. Page 4 — Customer Analysis

## Purpose

Analyze customer scale and repeat-purchasing behavior.

## Primary Measures

* Total Customers
* Repeat Customers
* Repeat Customer %
* Orders per Customer
* Customer Sales

## Supporting Analysis

* Repeat vs Non-Repeat Customers
* Customer-level performance
* Customer geographic analysis

---

# 24. Filter Architecture

## Global / Synchronized Filters

Use:

* Year
* Quarter
* Month

Source:

```text
dim_date
```

## Page-Specific Filters

### Executive

* Category
* Product
* Customer State

### Product & Category

* Category
* Product

### Regional & Seller

* Customer State
* Seller State
* Seller

### Customer

* Customer State

Filters must use dimension attributes rather than unnecessary fact-table fields.

---

# 25. Region and State Governance

The current model uses:

```text
dim_customer[customer_state]
```

for customer geographic analysis.

Therefore, `Region` and `Customer State` must not be represented as two duplicate slicers.

Seller geography is separately represented through:

```text
dim_seller[seller_state]
```

This distinction must be preserved in the report.

---

# 26. Visual Architecture

Visual selection follows analytical purpose.

| Analytical Requirement    | Preferred Visual     |
| ------------------------- | -------------------- |
| Headline KPI              | KPI Card             |
| Time trend                | Line Chart           |
| Ranking                   | Horizontal Bar Chart |
| Contribution              | Bar Chart            |
| Pareto analysis           | Line + Column Chart  |
| Detailed records          | Table / Matrix       |
| Geographic interpretation | Map where justified  |
| Geographic comparison     | Bar Chart            |

Decorative visuals are excluded.

Every visual must have a defined business purpose and documented field/measure dependency.

---

# 27. Interaction Architecture

The report supports controlled:

* Cross-filtering
* Cross-highlighting
* Drill-down
* Drill-through
* Tooltips
* Page navigation

Interaction behavior is governed by:

```text
docs/powerbi/filter_interaction_plan.md
```

Interactions must not create unexpected filter propagation or contradict the semantic-model relationship design.

---

# 28. UX Standards

Primary page hierarchy:

```text
Page Title
      ↓
Filters
      ↓
KPI Cards
      ↓
Primary Analysis
      ↓
Supporting Analysis
      ↓
Detail Table / Matrix
```

## Formatting

### Currency

Brazilian Real:

```text
R$
```

### Percentages

```text
0.0%
```

### Counts

Whole numbers with zero decimal places.

### Averages

Use one or two decimal places according to analytical meaning.

Terminology and number formatting must remain consistent throughout the report.

---

# 29. Performance Strategy

The Power BI model is designed around:

```text
Star Schema
      +
Import Mode
      +
Single-Direction Relationships
      +
Explicit Measures
      +
Controlled Cardinality
      +
Limited Visual Density
```

## Implementation Rules

* Load only required columns.
* Prefer measures over unnecessary calculated columns.
* Avoid high-cardinality slicers.
* Avoid unnecessary text fields.
* Avoid bidirectional relationships unless explicitly justified.
* Avoid fact-to-fact relationships.
* Limit visual count per page.
* Use Top N filtering for high-cardinality rankings.
* Validate performance using Power BI Performance Analyzer.

Optimization should proceed in this order:

```text
Model
 ↓
Columns
 ↓
Relationships
 ↓
DAX
 ↓
Visuals
 ↓
PostgreSQL
```

PostgreSQL views or aggregations should only be introduced when measured performance problems justify the additional complexity.

---

# 30. Refresh Strategy

The project does not require real-time reporting.

The intended refresh pattern is:

```text
Analytical Data
      ↓
PostgreSQL
      ↓
Power BI Dataset Refresh
      ↓
Updated Semantic Model
      ↓
Updated Report
```

A daily refresh cadence is appropriate for the current analytical use case.

The exact production refresh mechanism depends on the eventual Power BI deployment environment and gateway configuration.

---

# 31. Data Lineage

The intended lineage is:

```text
Olist Source Data
       ↓
Raw
       ↓
Cleaned
       ↓
Processed
       ↓
PostgreSQL analytics
       ↓
Power BI Semantic Model
       ↓
DAX Measures
       ↓
Report Visuals
       ↓
Business Insights
```

The Power BI layer should not independently recreate upstream cleaning or business rules that are already governed in PostgreSQL.

---

# 32. Governance and Maintainability

The Power BI implementation should maintain:

* Consistent measure naming
* Consistent business terminology
* Explicit measure definitions
* Documented relationships
* Controlled data-source connections
* Clear separation between dimensions and facts
* Documented report-page purpose
* Controlled filter behavior
* Version-controlled planning documentation

The six Phase 15 documents form the design baseline:

```text
powerbi_blueprint.md
powerbi_data_model.md
report_page_plan.md
visual_plan.md
filter_interaction_plan.md
dax_plan.md
```

Changes to the semantic model or KPI definitions should be reflected in the corresponding documentation.

---

# 33. Security Boundary

The current project does not define a requirement for row-level security.

Therefore, RLS is **not part of the initial implementation scope**.

If the report is later deployed to multiple business audiences requiring restricted access by seller, region, department, or organization, an RLS design should be added before production deployment.

---

# 34. Scope Restrictions

The Power BI solution must not introduce unsupported KPIs or report pages for:

* Profit
* Profit Margin
* Inventory
* Demand Forecasting
* Marketing Attribution
* Customer Lifetime Value
* Churn Prediction
* Real-time operational monitoring

These areas are outside the approved project scope or unsupported by the current analytical model.

---

# 35. Implementation Boundaries

Power BI is responsible for:

* Semantic modeling
* Relationships
* DAX measures
* Report calculations
* Visualization
* User interaction
* Dashboard presentation

PostgreSQL is responsible for:

* Analytical table storage
* Governed analytical structure
* Data preparation already completed upstream
* Analytical grain
* Key relationships
* Source-of-truth data for reporting

Python/SQL validation remains upstream of Power BI and is not replaced by Power BI calculations.

---

# 36. Phase 15 Deliverables

The completed Power BI planning package is:

```text
docs/
└── powerbi/
    ├── powerbi_blueprint.md
    ├── powerbi_data_model.md
    ├── report_page_plan.md
    ├── visual_plan.md
    ├── filter_interaction_plan.md
    └── dax_plan.md
```

These documents collectively define the implementation baseline for Phase 16.

---

# 37. Final Architecture Decision

The approved architecture is:

```text
┌──────────────────────────────┐
│        OLIST SOURCE DATA     │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│          RAW LAYER           │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│        CLEANED LAYER         │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│       PROCESSED LAYER        │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│     POSTGRESQL ANALYTICS     │
│  retail_sales_analytics      │
│          analytics           │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│    POWER BI SEMANTIC MODEL   │
│                              │
│  Facts + Dimensions          │
│  Relationships + Date Model  │
│  DAX Measures                │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│       POWER BI REPORT        │
│                              │
│  Executive                   │
│  Product & Category          │
│  Regional & Seller           │
│  Customer                    │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│      BUSINESS INSIGHTS       │
└──────────────────────────────┘
```

---

# 38. Final Decision

The Power BI solution will use:

* PostgreSQL `analytics` as the governed reporting source
* Four analytical fact tables
* Five active analytical dimensions
* `dim_date` as the authoritative date dimension
* Star-schema semantic modeling
* 1:* dimension-to-fact relationships
* Single-direction filtering
* No fact-to-fact relationships
* Import storage mode
* Explicit DAX measures
* Four primary report pages
* Controlled slicers and interactions
* Daily refresh as the target operational cadence
* Performance optimization based on measured requirements
* Documented scope and implementation boundaries

**Status: POWER BI BLUEPRINT — FINALIZED FOR PHASE 16**
