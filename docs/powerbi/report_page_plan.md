# Power BI Report Page Plan

## 1. Purpose

This document defines the approved Power BI report-page architecture for the **Retail Sales Performance Analytics** project.

It specifies:

* Page purpose
* Business questions
* KPI responsibilities
* Analytical visuals
* Filter scope
* User interactions
* Navigation
* Drill-through behavior
* Analytical outcomes
* Scope boundaries
* Page acceptance criteria

The report is designed as a **descriptive and diagnostic retail sales analytics solution** built on the approved PostgreSQL analytical model and governed Power BI semantic layer.

---

# 2. Report Architecture

The report contains four primary analytical pages.

| Page                             | Purpose                               | Primary Audience            |
| -------------------------------- | ------------------------------------- | --------------------------- |
| 1. Executive Sales Overview      | Overall business performance          | Management / Executives     |
| 2. Product & Category Analysis   | Product and category performance      | Product / Commercial Teams  |
| 3. Regional & Seller Performance | Geographic and seller performance     | Sales / Operations          |
| 4. Customer Analysis             | Customer base and purchasing behavior | Commercial / Customer Teams |

The page sequence follows an analytical progression:

```text
Monitor
  ↓
Diagnose Product Performance
  ↓
Diagnose Regional & Seller Performance
  ↓
Analyze Customer Behavior
```

Each page must have a distinct analytical purpose.

Duplicate visuals should not be introduced merely to increase page content.

---

# 3. Page 1 — Executive Sales Overview

## 3.1 Purpose

Provide a concise executive view of overall sales performance and the primary drivers of business performance.

The page must allow a decision-maker to understand the current sales position quickly before moving into diagnostic analysis.

---

## 3.2 Business Questions

The page answers:

1. How much sales revenue was generated?
2. How many orders were generated?
3. What is the average order value?
4. Is sales performance increasing or declining?
5. How is sales changing over time?
6. Which product categories contribute most to sales?
7. Which customer states contribute most to sales?

---

## 3.3 Primary KPIs

| KPI                | Business Purpose              |
| ------------------ | ----------------------------- |
| Total Sales        | Overall sales value           |
| Total Orders       | Order volume                  |
| AOV                | Average sales value per order |
| YoY Sales Growth % | Year-over-year performance    |
| YTD Sales          | Current-year cumulative sales |

### KPI Source Governance

`Total Sales`, `AOV`, and regional/customer sales use the approved payment-based sales definition:

```text
SUM(fact_payments[payment_value])
```

Product and category analysis uses item-price sales and is therefore not directly interchangeable with payment-based Total Sales.

---

## 3.4 Visual Specification

### Visual 1 — Total Sales

**Visual type:** KPI Card

**Measure:**

```text
[Total Sales]
```

**Purpose:**

Provide the primary headline sales metric.

---

### Visual 2 — Total Orders

**Visual type:** KPI Card

**Measure:**

```text
[Total Orders]
```

**Purpose:**

Provide order-volume context for sales performance.

---

### Visual 3 — AOV

**Visual type:** KPI Card

**Measure:**

```text
[AOV]
```

**Purpose:**

Show average sales value per order.

---

### Visual 4 — YoY Sales Growth %

**Visual type:** KPI Card

**Measure:**

```text
[YoY Sales Growth %]
```

**Purpose:**

Communicate year-over-year sales direction.

---

### Visual 5 — YTD Sales

**Visual type:** KPI Card

**Measure:**

```text
[YTD Sales]
```

**Purpose:**

Show cumulative sales for the selected year context.

---

### Visual 6 — Monthly Sales Trend

**Visual type:** Line chart

**Axis:**

```text
dim_date[month_year]
```

**Measure:**

```text
[Total Sales]
```

**Purpose:**

Identify:

* Growth
* Decline
* Seasonality
* Peaks
* Troughs
* Structural changes in sales performance

---

### Visual 7 — Sales by Category

**Visual type:** Horizontal bar chart

**Dimension:**

```text
dim_product[product_category_name_english]
```

**Measure:**

```text
[Category Sales]
```

**Purpose:**

Identify the categories generating the highest item-price sales.

---

### Visual 8 — Sales by Customer State

**Visual type:** Horizontal bar chart

**Dimension:**

```text
dim_customer[customer_state]
```

**Measure:**

```text
[Regional Sales]
```

**Purpose:**

Compare sales performance across customer states.

---

## 3.5 Filters

### Report-Level / Synchronized Date Filters

* Year
* Quarter
* Month

### Page-Level Filters

* Product Category
* Product
* Customer State

Filters must use dimension fields rather than fact-table fields wherever possible.

---

## 3.6 Expected User Outcome

After reviewing this page, the user should understand:

* Overall sales performance
* Order volume
* Average order value
* Growth direction
* Sales trend
* Major category drivers
* Major customer-state drivers

The page should answer **"What is happening?"** before users move to diagnostic pages.

---

# 4. Page 2 — Product & Category Analysis

## 4.1 Purpose

Provide detailed analysis of product and category performance and identify concentration within the product portfolio.

---

## 4.2 Business Questions

The page answers:

1. Which categories generate the most sales?
2. What is each category's contribution?
3. Which products generate the most sales?
4. What percentage of sales comes from each product?
5. How concentrated are product sales?
6. Which products account for the largest share of product sales?
7. How many items are being sold?

---

## 4.3 Primary Metrics

* Category Sales
* Category Sales %
* Top Category
* Product Sales
* Product Sales %
* Top Product
* Total Items
* Cumulative Product Sales %

---

## 4.4 Visual Specification

### Visual 1 — Category Revenue

**Visual type:** Horizontal bar chart

**Dimension:**

```text
dim_product[product_category_name_english]
```

**Measure:**

```text
[Category Sales]
```

**Purpose:**

Rank categories by item-price sales.

---

### Visual 2 — Category Contribution %

**Visual type:** Horizontal bar chart

**Dimension:**

```text
Product Category
```

**Measure:**

```text
[Category Sales %]
```

**Purpose:**

Show the relative contribution of each category.

---

### Visual 3 — Top Products

**Visual type:** Horizontal bar chart

**Dimension:**

```text
dim_product[product_id]
```

**Measure:**

```text
[Product Sales]
```

**Filter:**

Top N products by `[Product Sales]`.

**Purpose:**

Identify the strongest individual products without displaying an unnecessarily large product population.

---

### Visual 4 — Product Pareto

**Visual type:** Line and clustered column chart

**Category axis:**

```text
Product
```

**Column measure:**

```text
[Product Sales]
```

**Line measure:**

```text
[Cumulative Product Sales %]
```

**Purpose:**

Determine the concentration of product sales and identify the proportion of total product sales generated by the highest-ranked products.

---

### Visual 5 — Product Performance Table

**Visual type:** Matrix / table

**Fields:**

* Product ID
* Category
* Product Sales
* Product Sales %
* Total Items

**Purpose:**

Provide detailed product-level analysis supporting the ranking visuals.

---

## 4.5 Filters

### Synchronized Date Filters

* Year
* Quarter
* Month

### Page Filters

* Product Category
* Product

---

## 4.6 Expected User Outcome

Users should be able to identify:

* Leading categories
* Leading products
* Category concentration
* Product concentration
* Product contribution
* High-volume products

The page answers:

**"Which products and categories are driving performance?"**

---

# 5. Page 3 — Regional & Seller Performance

## 5.1 Purpose

Analyze customer-state sales performance and seller performance to identify geographic concentration and seller-level performance differences.

---

## 5.2 Business Questions

The page answers:

1. Which customer states generate the most sales?
2. What percentage of sales comes from each state?
3. Which sellers generate the most sales?
4. Which sellers have the lowest sales?
5. How is seller performance distributed geographically?
6. Where are the major sales concentrations?

---

## 5.3 Primary Metrics

* Regional Sales
* Regional Sales %
* Top Region
* Seller Sales
* Seller Orders

---

## 5.4 Visual Specification

### Visual 1 — Regional Sales

**Visual type:** Horizontal bar chart

**Dimension:**

```text
dim_customer[customer_state]
```

**Measure:**

```text
[Regional Sales]
```

**Purpose:**

Rank customer states by payment-based sales.

---

### Visual 2 — Regional Contribution %

**Visual type:** Horizontal bar chart

**Dimension:**

```text
dim_customer[customer_state]
```

**Measure:**

```text
[Regional Sales %]
```

**Purpose:**

Show each customer state's contribution to sales.

---

### Visual 3 — Geographic Breakdown

**Preferred visual:** Bar chart

**Alternative:** Map when spatial interpretation provides meaningful additional insight.

**Dimension:**

```text
Customer State
```

**Measure:**

```text
[Regional Sales]
```

**Purpose:**

Provide geographic context without making a map a mandatory decorative component.

### Governance Rule

A map must only be used when it improves geographic interpretation.

If the analytical question is primarily ranking or comparison, a bar chart is preferred.

---

### Visual 4 — Seller Performance

**Visual type:** Horizontal bar chart

**Dimension:**

```text
dim_seller[seller_id]
```

**Measure:**

```text
[Seller Sales]
```

**Purpose:**

Rank sellers by item-price sales.

---

### Visual 5 — Top / Bottom Sellers

**Visual type:** Horizontal bar chart

**Dimension:**

```text
Seller
```

**Measure:**

```text
[Seller Sales]
```

**Filter:**

Top N or Bottom N.

**Purpose:**

Quickly identify high-performing and low-performing sellers.

---

### Visual 6 — Seller Performance Table

**Visual type:** Matrix / table

**Fields:**

* Seller ID
* Seller City
* Seller State
* Seller Sales
* Seller Orders

**Purpose:**

Provide detailed seller-level performance context.

---

## 5.5 Filters

### Synchronized Date Filters

* Year
* Quarter
* Month

### Page Filters

* Customer State
* Seller State
* Seller

Customer geography and seller geography must remain separate analytical concepts.

---

## 5.6 Expected User Outcome

Users should understand:

* Geographic sales concentration
* Leading customer states
* Seller performance distribution
* Top sellers
* Bottom sellers
* Seller geographic context

The page answers:

**"Where is performance coming from, and which sellers are driving it?"**

---

# 6. Page 4 — Customer Analysis

## 6.1 Purpose

Analyze customer population, repeat purchasing behavior, customer sales contribution, and customer-level performance.

---

## 6.2 Business Questions

The page answers:

1. How many unique customers exist?
2. How many customers are repeat customers?
3. What percentage of customers are repeat customers?
4. How frequently do customers order?
5. Which customers generate the most sales?
6. How does customer performance vary by state?
7. What is the distribution between repeat and non-repeat customers?

---

## 6.3 Primary KPIs

* Total Customers
* Repeat Customers
* Repeat Customer %
* Orders per Customer

Supporting customer-level sales analysis is provided through `[Customer Sales]`.

---

## 6.4 Visual Specification

### Visual 1 — Total Customers

**Visual type:** KPI Card

**Measure:**

```text
[Total Customers]
```

**Purpose:**

Show the size of the unique customer base.

---

### Visual 2 — Repeat Customers

**Visual type:** KPI Card

**Measure:**

```text
[Repeat Customers]
```

**Purpose:**

Show the number of customers with more than one order.

---

### Visual 3 — Repeat Customer %

**Visual type:** KPI Card

**Measure:**

```text
[Repeat Customer %]
```

**Purpose:**

Measure repeat-customer penetration.

---

### Visual 4 — Customer Sales

**Visual type:** Horizontal bar chart

**Dimension:**

```text
dim_customer[customer_unique_id]
```

**Measure:**

```text
[Customer Sales]
```

**Filter:**

Top N customers where appropriate.

**Purpose:**

Identify customers contributing the highest payment-based sales.

---

### Visual 5 — Orders per Customer

**Visual type:** Bar/column chart

**Dimension:**

```text
Customer
```

**Measure:**

```text
[Orders per Customer]
```

**Purpose:**

Provide customer ordering-frequency context.

For high-cardinality customer populations, the visual must use an appropriate aggregation or filtered population rather than attempting to display every customer simultaneously.

---

### Visual 6 — Repeat vs Non-Repeat Customers

**Visual type:** Column or bar chart

**Dimension:**

```text
Customer Type
```

**Measure:**

Customer Count

**Purpose:**

Compare repeat and non-repeat customer populations.

The customer classification must be generated using the approved DAX logic rather than manually entered categories.

---

### Visual 7 — Customer Performance Table

**Visual type:** Matrix / table

**Fields:**

* Customer Unique ID
* Customer State
* Orders
* Customer Sales
* Repeat Customer Status

**Purpose:**

Provide customer-level diagnostic detail.

---

## 6.5 Filters

### Synchronized Date Filters

* Year
* Quarter
* Month

### Page Filter

* Customer State

---

## 6.6 Expected User Outcome

Users should understand:

* Customer-base size
* Repeat-customer population
* Repeat-customer penetration
* Customer purchasing behavior
* High-value customers
* Customer geographic differences

The page answers:

**"Who are the customers, and how are they behaving?"**

---

# 7. Report Navigation

Persistent navigation must be available across the primary report pages.

```text
┌─────────────────────────────────────────────────────┐
│ Executive │ Product │ Regional & Seller │ Customer │
└─────────────────────────────────────────────────────┘
```

Navigation should be implemented using Power BI navigation controls or an equivalent consistent navigation mechanism.

Users must not be required to rely exclusively on page tabs.

---

# 8. Drill-Down Architecture

Drill-down should support analytical exploration without creating unnecessary pages.

## Date

```text
Year
  ↓
Quarter
  ↓
Month
  ↓
Day
```

## Product

```text
Category
   ↓
Product
```

## Seller

```text
State
  ↓
City
  ↓
Seller
```

Drill-down must preserve the current filter context.

---

# 9. Drill-Through Architecture

Drill-through pages are optional and should be implemented only when they provide meaningful diagnostic depth.

## 9.1 Product Detail

**Drill-through context:**

Product

**Potential content:**

* Product ID
* Category
* Product Sales
* Product Sales %
* Total Items
* Product sales trend

---

## 9.2 Seller Detail

**Drill-through context:**

Seller

**Potential content:**

* Seller ID
* Seller City
* Seller State
* Seller Sales
* Seller Orders
* Seller sales trend

---

## 9.3 Customer Detail

**Drill-through context:**

Customer

**Potential content:**

* Customer Unique ID
* Customer State
* Orders
* Customer Sales
* Repeat Customer Status

### Drill-Through Rule

Drill-through pages must provide **deeper detail than the originating page**.

They must not simply reproduce an existing report page.

---

# 10. Filter Architecture

The report uses three filter scopes.

## Report-Level

Common analytical context:

* Year
* Quarter
* Month

## Page-Level

Business-domain filters specific to the page.

## Visual-Level

Used for analytical constraints such as:

* Top N
* Bottom N
* Specific ranking populations

The hierarchy should be:

```text
Report Filter
      ↓
Page Filter
      ↓
Visual Filter
```

Filters must not be duplicated unnecessarily across multiple scopes.

---

# 11. Cross-Page Consistency

The following standards apply to all primary pages:

* Date filters use `dim_date`.
* Customer geography uses `dim_customer`.
* Seller geography uses `dim_seller`.
* Product category uses `dim_product`.
* Product uses `dim_product`.
* Seller uses `dim_seller`.
* Business metrics use governed DAX measures.

Fact-table columns should not be used as primary report slicers unless there is a documented analytical requirement.

---

# 12. Page Layout Standard

All primary pages should follow a consistent visual hierarchy.

```text
┌──────────────────────────────────────────┐
│ Page Title                               │
├──────────────────────────────────────────┤
│ Filters                                  │
├──────────────────────────────────────────┤
│ KPI Cards                                │
├──────────────────────────────────────────┤
│ Primary Analytical Visuals               │
├──────────────────────────────────────────┤
│ Supporting Analysis                      │
├──────────────────────────────────────────┤
│ Detail Table / Matrix                    │
└──────────────────────────────────────────┘
```

The reading sequence should move from:

```text
Headline
   ↓
Trend
   ↓
Drivers
   ↓
Details
```

---

# 13. Visual Density Standards

Pages must prioritize analytical clarity over visual quantity.

Avoid:

* Duplicate charts
* Decorative visuals
* Excessive KPI cards
* Excessive slicers
* Large unfiltered high-cardinality tables
* Multiple visuals answering the same question

Every visual must have a defined analytical purpose.

---

# 14. Analytical Interaction Standards

Cross-filtering and cross-highlighting should be selectively enabled.

Examples:

### Category Selection

A category selection may affect:

* Sales KPIs
* Sales trend
* Product ranking
* Relevant supporting analysis

### Customer State Selection

A state selection may affect:

* Sales KPIs
* Sales trend
* Customer analysis
* Relevant regional analysis

### Seller Selection

A seller selection may affect:

* Seller KPIs
* Seller detail
* Related product analysis

Power BI **Edit Interactions** must be explicitly configured rather than relying on default interaction behavior.

---

# 15. Tooltip Standards

Tooltips should provide additional context without duplicating the visual.

Potential tooltip information:

### Product

* Product Sales
* Product Sales %
* Total Items

### Seller

* Seller Sales
* Seller Orders
* Seller State

### Customer

* Customer Sales
* Orders
* Repeat Customer Status

Tooltips should remain concise and analytical.

---

# 16. Page Performance Requirements

Report pages must be designed with model performance in mind.

### Requirements

* Avoid unnecessarily large detail tables.
* Apply Top N to high-cardinality ranking visuals.
* Avoid excessive simultaneous visuals.
* Avoid unnecessary calculated columns.
* Use measures rather than repeated visual calculations.
* Use dimension attributes for filtering.
* Avoid unnecessary bidirectional filtering.
* Validate performance using Power BI performance tools during implementation.

---

# 17. Scope Boundaries

The current report does **not** include dedicated pages for:

* Profitability
* Profit margin
* Inventory
* Demand forecasting
* Marketing attribution
* Customer lifetime value
* Churn prediction
* Real-time monitoring

These are outside the approved analytical scope.

---

# 18. Supporting Metrics Outside Primary Page Focus

Payment and delivery metrics may support analysis where they directly answer an existing business question.

Examples include:

* Payment Method Distribution
* Average Delivery Time
* On-Time Delivery Rate
* Late Delivery Rate
* Average Customer Review Score
* Order Status Distribution

These metrics do not require standalone report pages under the current Phase 15 architecture.

If later analysis demonstrates a strong business requirement, a dedicated page can be added through formal scope revision.

---

# 19. Page-to-KPI-to-Visual Matrix

| Page                          | Primary KPIs / Metrics                                                                                                               | Primary Visuals                                                                                                 |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| Executive Sales Overview      | Total Sales, Total Orders, AOV, YoY Growth %, YTD Sales                                                                              | Sales Trend, Category Sales, Regional Sales                                                                     |
| Product & Category Analysis   | Category Sales, Category Sales %, Top Category, Product Sales, Product Sales %, Top Product, Total Items, Cumulative Product Sales % | Category Ranking, Category Contribution, Top Products, Pareto, Product Table                                    |
| Regional & Seller Performance | Regional Sales, Regional Sales %, Top Region, Seller Sales, Seller Orders                                                            | Regional Ranking, Regional Contribution, Geographic Breakdown, Seller Ranking, Top/Bottom Sellers, Seller Table |
| Customer Analysis             | Total Customers, Repeat Customers, Repeat Customer %, Orders per Customer, Customer Sales                                            | Customer Sales, Orders per Customer, Repeat vs Non-Repeat, Customer Table                                       |

---

# 20. Page Acceptance Criteria

A page is considered implementation-ready when:

* [ ] Its business purpose is clearly defined.
* [ ] Its business questions are explicitly documented.
* [ ] Every primary KPI maps to an approved DAX measure.
* [ ] Every visual has a documented analytical purpose.
* [ ] Visual dimensions originate from approved dimensions.
* [ ] Filters use the approved filter architecture.
* [ ] Date filtering uses `dim_date`.
* [ ] No unsupported relationships are required.
* [ ] No duplicate analytical responsibility exists across pages.
* [ ] High-cardinality visuals are appropriately constrained.
* [ ] Drill-down behavior is defined where applicable.
* [ ] Drill-through behavior is defined where applicable.
* [ ] Navigation is consistent.
* [ ] Cross-filter interactions are intentionally configured.
* [ ] Page performance is acceptable during implementation testing.

---

# 21. Final Report Architecture

```text
                    POWER BI REPORT
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   Executive         Product &        Regional &
    Overview          Category           Seller
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          ▼
                     Customer
                      Analysis
```

The report follows an executive-to-diagnostic analytical flow:

```text
Overall Performance
        ↓
Product / Category Drivers
        ↓
Regional / Seller Drivers
        ↓
Customer Behavior
```

---

# 22. Phase 15.8 Decision

The Power BI report-page architecture is finalized.

The approved report contains four primary pages:

1. **Executive Sales Overview**
2. **Product & Category Analysis**
3. **Regional & Seller Performance**
4. **Customer Analysis**

The architecture provides a controlled progression from executive monitoring to product, regional/seller, and customer diagnostics.

The page plan is aligned with:

* The approved PostgreSQL analytical schema
* The finalized Power BI semantic model
* The KPI dictionary
* The DAX measure plan
* The filter and interaction strategy
* The defined project scope

**Status: REPORT PAGE PLAN — FINALIZED FOR IMPLEMENTATION**
