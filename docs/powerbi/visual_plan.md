# Power BI Visual Plan

## 1. Purpose

This document defines the approved visual layer for the **Retail Sales Performance Analytics** Power BI report.

It specifies:

* Visual type
* Business purpose
* Analytical question
* Dimensions
* Measures
* Sorting
* Filtering
* Interaction behavior
* Formatting
* Tooltip requirements
* Drill-down behavior
* Performance considerations
* Visual acceptance criteria

The visual layer must remain consistent with:

* The approved PostgreSQL analytical schema
* The finalized Power BI semantic model
* The KPI dictionary
* The DAX measure plan
* The report page plan
* The filter and interaction plan
* The project scope

---

# 2. Visual Design Philosophy

The report follows an **evidence-first analytical design**.

Visuals must prioritize:

1. Decision usefulness
2. Analytical accuracy
3. Comparability
4. Readability
5. Consistency
6. Performance

Visuals must not be added solely to make a page appear more complete.

The intended analytical flow is:

```text
Headline KPI
     ↓
Trend / Direction
     ↓
Drivers / Comparisons
     ↓
Detailed Diagnosis
```

---

# 3. Visual Selection Standards

| Analytical Requirement    | Preferred Visual        |
| ------------------------- | ----------------------- |
| Single headline metric    | KPI Card                |
| Time trend                | Line Chart              |
| Ranking                   | Horizontal Bar Chart    |
| Category comparison       | Horizontal Bar Chart    |
| Contribution %            | Bar Chart               |
| Product concentration     | Pareto Chart            |
| Detailed records          | Table / Matrix          |
| Hierarchical exploration  | Matrix / Drill-down     |
| Geographic interpretation | Map only when justified |
| Top / Bottom ranking      | Horizontal Bar Chart    |

---

# 4. General Visual Standards

## 4.1 Ranking

Ranking visuals should:

* Sort descending for Top N analysis.
* Sort ascending when emphasizing Bottom N.
* Use horizontal bars for long category names.
* Avoid displaying unnecessarily large populations.

---

## 4.2 Time Series

Time-series visuals should:

* Use `dim_date`.
* Use chronological sorting.
* Use `month_year` rather than text-only month names for monthly trends.
* Respond to the report date context.
* Avoid mixing incompatible date roles.

---

## 4.3 High-Cardinality Dimensions

High-cardinality dimensions include:

* Product ID
* Seller ID
* Customer Unique ID

These should not normally be displayed as unrestricted visual populations.

Use:

* Top N
* Bottom N
* Drill-through
* Search/filter context
* Detail tables with controlled filtering

where appropriate.

---

## 4.4 Measures

Visuals must use approved DAX measures wherever the metric represents business logic.

Avoid:

* Ad hoc aggregation logic
* Repeated visual-level calculations
* Manually entered KPI values
* Duplicated business definitions

---

# 5. Page 1 — Executive Sales Overview

## 5.1 Visual Inventory

| ID    | Visual              | Type       | Primary Purpose            |
| ----- | ------------------- | ---------- | -------------------------- |
| EX-01 | Total Sales         | KPI Card   | Headline sales performance |
| EX-02 | Total Orders        | KPI Card   | Order volume               |
| EX-03 | AOV                 | KPI Card   | Average order value        |
| EX-04 | YoY Sales Growth %  | KPI Card   | Growth direction           |
| EX-05 | YTD Sales           | KPI Card   | Cumulative annual sales    |
| EX-06 | Monthly Sales Trend | Line Chart | Time trend                 |
| EX-07 | Sales by Category   | Bar Chart  | Category drivers           |
| EX-08 | Sales by State      | Bar Chart  | Regional drivers           |

---

## 5.2 EX-01 — Total Sales

**Visual Type:** KPI Card

**Measure:**

```text id="6s4b0c"
[Total Sales]
```

**Source Concept:**

```text id="5h8ov5"
fact_payments[payment_value]
```

**Analytical Question:**

> How much sales revenue was generated?

**Purpose:**

Provide the primary business-performance headline.

**Formatting:**

* Currency: `R$`
* Appropriate compact notation where required

---

## 5.3 EX-02 — Total Orders

**Visual Type:** KPI Card

**Measure:**

```text id="zq2by6"
[Total Orders]
```

**Source:**

```text id="v4ljfg"
fact_orders[order_id]
```

**Analytical Question:**

> How many orders were generated?

**Formatting:**

* Whole number

---

## 5.4 EX-03 — AOV

**Visual Type:** KPI Card

**Measure:**

```text id="s5w7f8"
[AOV]
```

**Analytical Question:**

> What is the average sales value per order?

**Formatting:**

* `R$`
* Appropriate decimal precision

---

## 5.5 EX-04 — YoY Sales Growth %

**Visual Type:** KPI Card

**Measure:**

```text id="x4sp0h"
[YoY Sales Growth %]
```

**Analytical Question:**

> Is sales performance improving or declining year over year?

**Formatting:**

* Percentage
* One decimal place

---

## 5.6 EX-05 — YTD Sales

**Visual Type:** KPI Card

**Measure:**

```text id="9yp7oa"
[YTD Sales]
```

**Analytical Question:**

> How much sales has been generated cumulatively during the selected year?

---

## 5.7 EX-06 — Monthly Sales Trend

**Visual Type:** Line Chart

**X-Axis:**

```text id="6d2nmc"
dim_date[month_year]
```

**Y-Axis:**

```text id="l8l6az"
[Total Sales]
```

**Analytical Questions:**

* How is sales changing over time?
* Are there identifiable peaks or declines?
* Is there evidence of seasonality?

**Sorting:**

Chronological.

**Interaction:**

Date selections must update the visual appropriately.

---

## 5.8 EX-07 — Sales by Category

**Visual Type:** Horizontal Bar Chart

**Dimension:**

```text id="8u4j6e"
dim_product[product_category_name_english]
```

**Measure:**

```text id="1zv08u"
[Category Sales]
```

**Analytical Question:**

> Which categories are the major sales drivers?

**Sorting:**

Descending by `[Category Sales]`.

**Optional Filter:**

Top N categories when required for readability.

---

## 5.9 EX-08 — Sales by State

**Visual Type:** Horizontal Bar Chart

**Dimension:**

```text id="3m7x4w"
dim_customer[customer_state]
```

**Measure:**

```text id="8d3w4j"
[Regional Sales]
```

**Analytical Question:**

> Which customer states generate the most sales?

**Sorting:**

Descending by `[Regional Sales]`.

---

# 6. Page 2 — Product & Category Analysis

## 6.1 Visual Inventory

| ID    | Visual                  | Type         | Primary Purpose     |
| ----- | ----------------------- | ------------ | ------------------- |
| PC-01 | Category Revenue        | Bar Chart    | Category ranking    |
| PC-02 | Category Contribution % | Bar Chart    | Category share      |
| PC-03 | Top Products            | Bar Chart    | Product ranking     |
| PC-04 | Product Pareto          | Combo Chart  | Sales concentration |
| PC-05 | Product Performance     | Table/Matrix | Product detail      |

---

## 6.2 PC-01 — Category Revenue

**Visual Type:** Horizontal Bar Chart

**Dimension:**

```text id="pl2s4x"
dim_product[product_category_name_english]
```

**Measure:**

```text id="8unf3z"
[Category Sales]
```

**Analytical Question:**

> Which product categories generate the highest sales?

**Sorting:**

Descending by `[Category Sales]`.

---

## 6.3 PC-02 — Category Contribution %

**Visual Type:** Horizontal Bar Chart

**Dimension:**

```text id="pgk0a7"
dim_product[product_category_name_english]
```

**Measure:**

```text id="e5h7vf"
[Category Sales %]
```

**Analytical Question:**

> What proportion of category sales is represented by each category?

**Formatting:**

* Percentage
* One decimal place

---

## 6.4 PC-03 — Top Products

**Visual Type:** Horizontal Bar Chart

**Dimension:**

```text id="n8v8o7"
dim_product[product_id]
```

**Measure:**

```text id="k5e8s9"
[Product Sales]
```

**Filter:**

Top N by `[Product Sales]`.

**Analytical Question:**

> Which individual products generate the highest sales?

**Sorting:**

Descending.

---

## 6.5 PC-04 — Product Pareto

**Visual Type:** Line and Clustered Column Chart

**Axis:**

Product

**Column:**

```text id="9v7k0m"
[Product Sales]
```

**Line:**

```text id="5s7n6x"
[Cumulative Product Sales %]
```

**Analytical Question:**

> How concentrated are sales among the highest-performing products?

**Required Ordering:**

Products must be ordered by `[Product Sales]` descending.

**Interpretation:**

The cumulative line shows the proportion of total product sales accounted for as progressively lower-ranked products are included.

---

## 6.6 PC-05 — Product Performance Table

**Visual Type:** Matrix / Table

**Dimensions:**

* Product ID
* Category

**Measures:**

* Product Sales
* Product Sales %
* Total Items

**Analytical Question:**

> What is the detailed performance of individual products?

**Performance Rule:**

Avoid unrestricted display of the complete product population when it creates excessive rendering cost.

---

# 7. Page 3 — Regional & Seller Performance

## 7.1 Visual Inventory

| ID    | Visual                   | Type         | Primary Purpose    |
| ----- | ------------------------ | ------------ | ------------------ |
| RS-01 | Regional Sales           | Bar Chart    | State ranking      |
| RS-02 | Regional Contribution %  | Bar Chart    | State contribution |
| RS-03 | Geographic Breakdown     | Bar/Map      | Geographic context |
| RS-04 | Seller Performance       | Bar Chart    | Seller ranking     |
| RS-05 | Top / Bottom Sellers     | Bar Chart    | Extremes           |
| RS-06 | Seller Performance Table | Table/Matrix | Seller detail      |

---

## 7.2 RS-01 — Regional Sales

**Visual Type:** Horizontal Bar Chart

**Dimension:**

```text id="8p2t6q"
dim_customer[customer_state]
```

**Measure:**

```text id="0j2d5f"
[Regional Sales]
```

**Analytical Question:**

> Which customer states generate the highest sales?

**Sorting:**

Descending.

---

## 7.3 RS-02 — Regional Contribution %

**Visual Type:** Horizontal Bar Chart

**Dimension:**

```text id="v8o5q3"
dim_customer[customer_state]
```

**Measure:**

```text id="6j3p5r"
[Regional Sales %]
```

**Analytical Question:**

> What percentage of sales does each customer state contribute?

---

## 7.4 RS-03 — Geographic Breakdown

**Preferred Visual:** Horizontal Bar Chart

**Alternative:** Map.

**Dimension:**

Customer State

**Measure:**

```text id="4v4v8j"
[Regional Sales]
```

**Analytical Question:**

> How is sales performance distributed geographically?

### Map Governance

A map may be used only when spatial positioning provides meaningful insight.

If the objective is simply comparison or ranking, the bar chart remains the preferred visual.

---

## 7.5 RS-04 — Seller Performance

**Visual Type:** Horizontal Bar Chart

**Dimension:**

```text id="7v9w5s"
dim_seller[seller_id]
```

**Measure:**

```text id="4x3x1a"
[Seller Sales]
```

**Analytical Question:**

> Which sellers generate the highest sales?

**Filter:**

Top N when required.

---

## 7.6 RS-05 — Top / Bottom Sellers

**Visual Type:** Horizontal Bar Chart

**Dimension:**

```text id="6y0s7v"
dim_seller[seller_id]
```

**Measure:**

```text id="4m9f0d"
[Seller Sales]
```

**Filter:**

* Top N or
* Bottom N

**Analytical Question:**

> Which sellers are at the performance extremes?

---

## 7.7 RS-06 — Seller Performance Table

**Visual Type:** Matrix / Table

**Dimensions:**

* Seller ID
* Seller City
* Seller State

**Measures:**

* Seller Sales
* Seller Orders

**Analytical Question:**

> What is the detailed performance of individual sellers?

---

# 8. Page 4 — Customer Analysis

## 8.1 Visual Inventory

| ID    | Visual               | Type         | Primary Purpose      |
| ----- | -------------------- | ------------ | -------------------- |
| CU-01 | Total Customers      | KPI Card     | Customer population  |
| CU-02 | Repeat Customers     | KPI Card     | Repeat population    |
| CU-03 | Repeat Customer %    | KPI Card     | Repeat penetration   |
| CU-04 | Customer Sales       | Bar Chart    | High-value customers |
| CU-05 | Orders per Customer  | Bar/Column   | Ordering frequency   |
| CU-06 | Repeat vs Non-Repeat | Bar/Column   | Customer composition |
| CU-07 | Customer Performance | Table/Matrix | Customer detail      |

---

## 8.2 CU-01 — Total Customers

**Visual Type:** KPI Card

**Measure:**

```text id="3n8p4z"
[Total Customers]
```

**Analytical Question:**

> How large is the unique customer base?

---

## 8.3 CU-02 — Repeat Customers

**Visual Type:** KPI Card

**Measure:**

```text id="4z7n8x"
[Repeat Customers]
```

**Analytical Question:**

> How many customers have placed more than one order?

---

## 8.4 CU-03 — Repeat Customer %

**Visual Type:** KPI Card

**Measure:**

```text id="8q6b4m"
[Repeat Customer %]
```

**Analytical Question:**

> What percentage of the customer base is repeat?

**Formatting:**

* Percentage
* One decimal place

---

## 8.5 CU-04 — Customer Sales

**Visual Type:** Horizontal Bar Chart

**Dimension:**

```text id="5x9m3p"
dim_customer[customer_unique_id]
```

**Measure:**

```text id="0s8j7c"
[Customer Sales]
```

**Filter:**

Top N customers.

**Analytical Question:**

> Which customers generate the highest payment-based sales?

**Performance Requirement:**

Do not display the complete high-cardinality customer population without an appropriate filter.

---

## 8.6 CU-05 — Orders per Customer

**Visual Type:** Bar / Column Chart

**Dimension:**

Customer

**Measure:**

```text id="9f6n5k"
[Orders per Customer]
```

**Analytical Question:**

> How frequently are customers ordering?

**Performance Requirement:**

Use an appropriately filtered population or aggregation rather than rendering every customer simultaneously.

---

## 8.7 CU-06 — Repeat vs Non-Repeat Customers

**Visual Type:** Bar / Column Chart

**Dimension:**

Customer Type

**Measure:**

Customer Count

**Categories:**

```text id="j9f4z2"
Repeat Customer
Non-Repeat Customer
```

**Analytical Question:**

> What is the composition of the customer base?

The classification must be generated through approved DAX logic.

---

## 8.8 CU-07 — Customer Performance Table

**Visual Type:** Matrix / Table

**Dimensions:**

* Customer Unique ID
* Customer State

**Measures:**

* Customer Orders
* Customer Sales
* Repeat Customer Status

**Analytical Question:**

> What is the detailed performance and purchasing status of customers?

---

# 9. Visual-to-Measure Dependency Matrix

| Visual                      | Required Measure                                  | Dimension      |
| --------------------------- | ------------------------------------------------- | -------------- |
| EX-01 Total Sales           | `[Total Sales]`                                   | —              |
| EX-02 Total Orders          | `[Total Orders]`                                  | —              |
| EX-03 AOV                   | `[AOV]`                                           | —              |
| EX-04 YoY Growth            | `[YoY Sales Growth %]`                            | `dim_date`     |
| EX-05 YTD Sales             | `[YTD Sales]`                                     | `dim_date`     |
| EX-06 Monthly Sales         | `[Total Sales]`                                   | `dim_date`     |
| EX-07 Category Sales        | `[Category Sales]`                                | `dim_product`  |
| EX-08 Regional Sales        | `[Regional Sales]`                                | `dim_customer` |
| PC-01 Category Revenue      | `[Category Sales]`                                | `dim_product`  |
| PC-02 Category Contribution | `[Category Sales %]`                              | `dim_product`  |
| PC-03 Top Products          | `[Product Sales]`                                 | `dim_product`  |
| PC-04 Product Pareto        | `[Product Sales]`, `[Cumulative Product Sales %]` | `dim_product`  |
| PC-05 Product Table         | Product Sales, Product Sales %, Total Items       | `dim_product`  |
| RS-01 Regional Sales        | `[Regional Sales]`                                | `dim_customer` |
| RS-02 Regional Contribution | `[Regional Sales %]`                              | `dim_customer` |
| RS-03 Geographic Breakdown  | `[Regional Sales]`                                | `dim_customer` |
| RS-04 Seller Performance    | `[Seller Sales]`                                  | `dim_seller`   |
| RS-05 Seller Ranking        | `[Seller Sales]`                                  | `dim_seller`   |
| RS-06 Seller Table          | Seller Sales, Seller Orders                       | `dim_seller`   |
| CU-01 Total Customers       | `[Total Customers]`                               | `dim_customer` |
| CU-02 Repeat Customers      | `[Repeat Customers]`                              | `dim_customer` |
| CU-03 Repeat Customer %     | `[Repeat Customer %]`                             | `dim_customer` |
| CU-04 Customer Sales        | `[Customer Sales]`                                | `dim_customer` |
| CU-05 Orders per Customer   | `[Orders per Customer]`                           | `dim_customer` |
| CU-06 Repeat vs Non-Repeat  | Customer Count                                    | `dim_customer` |
| CU-07 Customer Table        | Customer Sales, Orders                            | `dim_customer` |

---

# 10. Sorting Standards

| Visual Type           | Sorting Standard         |
| --------------------- | ------------------------ |
| Monthly trend         | Chronological            |
| Category ranking      | Sales descending         |
| Product ranking       | Sales descending         |
| Regional ranking      | Sales descending         |
| Seller ranking        | Sales descending         |
| Bottom Seller ranking | Sales ascending          |
| Pareto                | Product Sales descending |
| Contribution %        | Contribution descending  |

Sorting must be explicitly configured where Power BI's default behavior could produce misleading results.

---

# 11. Filter Standards

## Date

Use:

* Year
* Quarter
* Month

from `dim_date`.

All time-sensitive visuals must respect the selected date context.

## Product

Use:

* Product Category
* Product

from `dim_product`.

## Customer Geography

Use:

```text id="fzqz5s"
dim_customer[customer_state]
dim_customer[customer_city]
```

where applicable.

## Seller Geography

Use:

```text id="9z1w5m"
dim_seller[seller_state]
dim_seller[seller_city]
```

---

# 12. Top N / Bottom N Standards

Top N and Bottom N are visual-level analytical constraints.

Use them for:

* Top Products
* Top Sellers
* Bottom Sellers
* Top Customers

Do not introduce a global Top N slicer unless a future business requirement explicitly requires dynamic ranking control.

---

# 13. Interaction Standards

Visual interactions must be deliberately configured.

## Cross-Filtering

Selections should affect related visuals where the analytical relationship is meaningful.

Example:

```text
Category Selection
       ↓
Product Analysis
       ↓
Relevant KPIs / Trend
```

## Cross-Highlighting

Use only where the comparison remains understandable.

## Edit Interactions

Power BI **Edit Interactions** must be used to explicitly control visual behavior.

The default interaction behavior must not be assumed to be appropriate for every visual.

---

# 14. Drill-Down Standards

## Date

```text id="n7g6q4"
Year
  ↓
Quarter
  ↓
Month
  ↓
Day
```

## Product

```text id="0j8w2v"
Category
   ↓
Product
```

## Seller

```text id="8f2m5k"
State
  ↓
City
  ↓
Seller
```

Drill-down should preserve the active filter context.

---

# 15. Tooltip Standards

Tooltips should provide supporting information without duplicating permanent visuals.

## Product Tooltip

* Product
* Category
* Product Sales
* Product Sales %
* Total Items

## Seller Tooltip

* Seller
* Seller City
* Seller State
* Seller Sales
* Seller Orders

## Customer Tooltip

* Customer
* Customer State
* Customer Sales
* Orders
* Repeat Customer Status

Tooltip content must remain concise.

---

# 16. Formatting Standards

## Currency

Use:

```text id="5d3s2n"
R$
```

## Percentage

Use:

```text id="y4f8j7"
0.0%
```

## Counts

Use:

```text id="r3s8n1"
0 decimal places
```

## Averages

Use an appropriate decimal precision, normally one or two decimal places.

---

# 17. Visual Title Standards

Titles should communicate the analytical meaning of the visual.

Preferred:

```text id="l2s7c9"
Monthly Sales Trend
Sales by Category
Sales by Customer State
Top Products
Seller Performance
Customer Sales
```

Avoid technical titles such as:

```text id="w7f4n8"
SUM(payment_value)
fact_order_items.price
customer_state Analysis
```

Dynamic titles may be introduced where they materially improve filter-context clarity.

---

# 18. Accessibility Standards

The report should support accessible interpretation.

Requirements include:

* Clear visual titles
* Meaningful field names
* Sufficient text readability
* Avoid reliance on color alone to communicate meaning
* Logical tab/focus order where applicable
* Consistent visual hierarchy
* Alt text where appropriate
* Avoid excessive visual density

Conditional formatting should reinforce an analytical message rather than act as decoration.

---

# 19. Visuals Explicitly Excluded

The following are excluded unless a documented business requirement is introduced:

* Decorative gauges
* Word clouds
* 3D charts
* Decorative images
* Unnecessary donut/pie charts
* Unsupported geographic maps
* Excessive KPI cards
* Duplicate charts
* Unfiltered high-cardinality charts
* Visuals without an analytical purpose

---

# 20. Visual Performance Standards

Visual design must account for Power BI rendering performance.

### Requirements

* Limit unnecessary visuals per page.
* Apply Top N to high-cardinality ranking charts.
* Avoid unrestricted customer/product/seller visual populations.
* Avoid unnecessary calculated columns.
* Prefer reusable DAX measures.
* Avoid excessive interactions.
* Avoid unnecessary map visuals.
* Validate expensive visuals using Power BI Performance Analyzer during implementation.

Performance optimization must be validated empirically rather than based solely on assumptions.

---

# 21. Visual Governance Rules

Every production visual must satisfy the following:

### Data Integrity

The visual uses approved model fields and measures.

### Business Definition

The metric has a documented business definition.

### Analytical Purpose

The visual answers a defined business question.

### Filter Integrity

The visual responds correctly to intended filters.

### Interaction Integrity

Cross-filter and cross-highlight behavior is intentional.

### Formatting Integrity

Units, percentages, counts, and labels are correctly formatted.

### Performance Integrity

The visual does not introduce unacceptable rendering cost.

---

# 22. Visual Acceptance Checklist

Before a visual is considered production-ready:

* [ ] Correct visual type selected.
* [ ] Correct dimension used.
* [ ] Correct DAX measure used.
* [ ] Business question documented.
* [ ] Sorting configured correctly.
* [ ] Filters configured correctly.
* [ ] Date context behaves correctly.
* [ ] Cross-interactions tested.
* [ ] Tooltip configured where useful.
* [ ] Drill-down tested where applicable.
* [ ] Formatting validated.
* [ ] Units validated.
* [ ] High-cardinality behavior controlled.
* [ ] Performance tested.
* [ ] Visual does not duplicate another analytical purpose.

---

# 23. Final Visual Architecture

```text
Executive Sales Overview
│
├── KPI Cards
├── Sales Trend
├── Category Drivers
└── Regional Drivers

Product & Category Analysis
│
├── Category Ranking
├── Category Contribution
├── Top Products
├── Product Pareto
└── Product Detail

Regional & Seller Performance
│
├── Regional Ranking
├── Regional Contribution
├── Geographic Context
├── Seller Ranking
├── Top / Bottom Sellers
└── Seller Detail

Customer Analysis
│
├── Customer KPIs
├── Customer Sales
├── Ordering Frequency
├── Repeat vs Non-Repeat
└── Customer Detail
```

---

# 24. Phase 15.9 Decision

The Power BI visual architecture is finalized.

The report will use a controlled visual vocabulary:

* **KPI Cards** for headline metrics
* **Line Charts** for time-series analysis
* **Horizontal Bar Charts** for rankings and comparisons
* **Pareto Analysis** for product concentration
* **Tables/Matrices** for detailed analysis
* **Maps only when spatial interpretation provides incremental analytical value**

Every visual must be traceable to an approved business question, semantic-model field, and governed DAX measure.

**Status: VISUAL PLAN — FINALIZED FOR IMPLEMENTATION**
