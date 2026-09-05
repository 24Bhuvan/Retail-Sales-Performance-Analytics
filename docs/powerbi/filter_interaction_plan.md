# Power BI Filter & Interaction Plan

## 1. Purpose

This document defines the approved filtering and interaction architecture for the **Retail Sales Performance Analytics** Power BI report.

It governs:

* Report-level filters
* Page-level filters
* Visual-level filters
* Slicers
* Synchronized filters
* Cross-filtering
* Cross-highlighting
* Drill-down
* Drill-through
* Tooltips
* Navigation
* Filter propagation
* Date-role behavior
* Reset behavior
* Performance
* Validation

The interaction architecture must operate within the finalized Power BI star schema and must not introduce unsupported relationships, ambiguous filter paths, or uncontrolled filter propagation.

---

# 2. Interaction Design Principles

The report follows these principles:

1. **Dimensions are the primary filtering layer.**
2. **Date filtering is standardized through `dim_date`.**
3. **Filter behavior must be predictable.**
4. **Interactions must support the analytical question of each page.**
5. **Cross-filtering is preferred where users need a focused subset.**
6. **Cross-highlighting is used only where comparison remains meaningful.**
7. **Fact-to-fact filtering is prohibited.**
8. **Many-to-many relationships are not introduced to solve interaction problems.**
9. **High-cardinality fields are not used unnecessarily as slicers.**
10. **Every important interaction must be explicitly validated.**

---

# 3. Filter Scope Architecture

The report uses three primary filter scopes.

```text id="0r8q4w"
Report-Level
     ↓
Page-Level
     ↓
Visual-Level
```

## 3.1 Report-Level Filters

Used for context that should apply consistently across the report.

Primary report-wide context:

* Year
* Quarter
* Month

These are implemented through synchronized slicers using `dim_date`.

---

## 3.2 Page-Level Filters

Used for business-domain filtering specific to an analytical page.

Examples:

* Product Category
* Product
* Customer State
* Seller State
* Seller

---

## 3.3 Visual-Level Filters

Used for visual-specific analytical constraints.

Examples:

* Top N Products
* Top N Sellers
* Bottom N Sellers
* Top N Customers

Visual-level filters must not unintentionally override the broader analytical context.

---

# 4. Global Date Filter Architecture

Date filtering is standardized across all four primary report pages.

## Global Date Fields

Use:

```text id="r1u4y8"
dim_date[year]
dim_date[quarter]
dim_date[month]
```

Where appropriate, expose:

* Year
* Quarter
* Month

as synchronized slicers.

---

# 5. Date Hierarchy

The approved date hierarchy is:

```text id="2h0j7k"
Year
  ↓
Quarter
  ↓
Month
  ↓
Day
```

An abbreviated reporting path may also be used:

```text id="1j7q9n"
Year
  ↓
Month
```

For monthly trend visuals, use:

```text id="g6d0v5"
dim_date[month_year]
```

`month_year` must be chronologically sorted using its appropriate numeric/date sort column.

---

# 6. Date Filter Governance

The date dimension is the authoritative source for report time filtering.

Do not use:

* Fact-table date columns as general report slicers
* Independent date slicers from multiple fact tables
* Text-only month fields without chronological sorting

All standard report date selections must originate from `dim_date`.

---

# 7. Page-Specific Filter Architecture

## Page 1 — Executive Sales Overview

### Filters

* Category
* Product
* Customer State

### Source

```text id="f3r7q2"
dim_product[product_category_name_english]
dim_product[product_id]
dim_customer[customer_state]
```

### Purpose

Allow users to narrow executive sales performance by product and customer geography.

---

## Page 2 — Product & Category Analysis

### Filters

* Category
* Product

### Source

```text id="h5n4k2"
dim_product[product_category_name_english]
dim_product[product_id]
```

### Purpose

Focus analysis on selected categories and products.

---

## Page 3 — Regional & Seller Performance

### Filters

* Customer State
* Seller State
* Seller

### Source

```text id="9m5w3v"
dim_customer[customer_state]
dim_seller[seller_state]
dim_seller[seller_id]
```

### Purpose

Allow customer geography and seller performance to be analyzed as distinct dimensions.

---

## Page 4 — Customer Analysis

### Filter

* Customer State

### Source

```text id="6j8p4c"
dim_customer[customer_state]
```

### Purpose

Analyze customer behavior within a selected customer geography.

---

# 8. Geography Filter Governance

The model distinguishes between:

### Customer Geography

```text id="q8v1x5"
dim_customer[state]
dim_customer[city]
```

### Seller Geography

```text id="4s9w3m"
dim_seller[state]
dim_seller[city]
```

These must not be treated as the same analytical dimension.

---

# 9. Region / State Rule

The active model does not contain a separate analytical `Region` dimension.

Therefore, do not create duplicate slicers such as:

```text id="8f2k6n"
Region
Customer State
```

when both represent the same customer-geography concept.

The approved customer geography filter is:

```text id="y4x7p1"
dim_customer[customer_state]
```

Seller geography remains independently represented by:

```text id="k3m8q5"
dim_seller[seller_state]
```

---

# 10. Slicer Standards

## 10.1 Date Slicers

Use:

* Year
* Quarter
* Month

Synchronize these across all primary pages.

---

## 10.2 Product Slicers

Use:

* Category
* Product

Category should logically precede Product.

---

## 10.3 Customer Geography

Use:

* Customer State

on pages where customer geography is analytically relevant.

---

## 10.4 Seller Geography

Use:

* Seller State

on the Regional & Seller Performance page.

---

## 10.5 Seller

Use:

* Seller

on the Regional & Seller Performance page.

---

# 11. Slicer Design Standards

Slicers must be:

* Clearly labeled
* Business-friendly
* Consistently positioned
* Limited to fields with meaningful analytical value
* Easy to clear or reset

Avoid excessive slicers that create unnecessary cognitive load.

---

# 12. High-Cardinality Filter Policy

High-cardinality fields include:

* Product ID
* Seller ID
* Customer Unique ID

These should not normally be used as report-wide slicers.

Where filtering is required, use:

* Search-enabled slicers
* Page-level filters
* Drill-through
* Top N
* Controlled detail tables

The objective is to maintain usability and report performance.

---

# 13. Fact-Table Filter Policy

Do not use raw fact-table fields as general-purpose slicers when an equivalent dimension field exists.

Preferred:

```text id="5x0f4a"
dim_date
dim_product
dim_customer
dim_seller
dim_order_status
```

Fact-table fields should primarily support measures and analytical calculations.

---

# 14. Filter Propagation Architecture

The semantic model follows:

```text id="2z8r4v"
Dimension
    │
    │ 1:*
    ▼
Fact
```

with single-direction filtering.

Therefore:

```text id="3x7w2m"
Dimension Selection
       ↓
Related Fact
       ↓
Measure
       ↓
Visual
```

A fact table must not become a general-purpose filter source for another fact table.

---

# 15. Cross-Filtering

Cross-filtering should be used when selecting a data point should narrow the analytical context of related visuals.

## Category Selection

Selecting a category may affect:

* Sales KPIs
* Monthly sales
* Product analysis
* Regional sales

where the underlying model and measure logic support the propagation.

---

## Customer State Selection

Selecting a customer state may affect:

* Sales KPIs
* Monthly sales
* Category analysis
* Customer analysis

---

## Seller Selection

Selecting a seller may affect:

* Seller performance
* Seller detail
* Related product analysis

Cross-filtering must not create a new relationship path.

---

# 16. Cross-Highlighting

Cross-highlighting should be used selectively.

It is appropriate when users need to compare:

* Selected vs unselected categories
* Selected vs unselected regions
* Selected vs unselected products

Cross-highlighting should not be used when the resulting partial visual state becomes difficult to interpret.

When a focused subset is more useful than a comparison, use cross-filtering.

---

# 17. Interaction Configuration

Power BI **Edit Interactions** must be explicitly configured for important visuals.

For every significant source-target interaction, select one of:

```text id="9h1m3c"
Filter
Highlight
No Effect
```

Default Power BI interaction behavior must not be treated as the final report design.

---

# 18. Interaction Matrix

The implementation should maintain an interaction matrix similar to:

| Source Visual  | Target             | Expected Behavior |
| -------------- | ------------------ | ----------------- |
| Category chart | KPI Cards          | Filter            |
| Category chart | Sales Trend        | Filter            |
| Category chart | Product visuals    | Filter            |
| State chart    | KPI Cards          | Filter            |
| State chart    | Customer visuals   | Filter            |
| Seller chart   | Seller detail      | Filter            |
| Product chart  | Product detail     | Filter            |
| Ranking visual | Unrelated analysis | No Effect         |

The final configuration must be validated in Power BI after implementation.

---

# 19. Date Role-Playing Interaction

`fact_orders` contains multiple date roles:

* Purchase Date
* Approved Date
* Delivered-to-Carrier Date
* Delivered-to-Customer Date
* Estimated Delivery Date

These dates represent different business events.

The report must not allow multiple ambiguous active date relationships to control the same analysis simultaneously.

---

# 20. Primary Date Context

Standard report analysis should use the approved primary reporting date.

Alternate date roles should only be activated for specific analytical requirements.

Examples:

```text id="n4y7v2"
Purchase Date
    → Sales / Order Trend

Approved Date
    → Approval Timing

Carrier Date
    → Carrier Handoff Analysis

Delivered Customer Date
    → Delivery Analysis

Estimated Delivery Date
    → Delivery Expectation Analysis
```

The exact Power BI implementation must follow the finalized semantic-model date-role design.

---

# 21. Drill-Down Architecture

## Date

```text id="j5r8x2"
Year
  ↓
Quarter
  ↓
Month
  ↓
Day
```

## Product

```text id="m8k2v5"
Category
  ↓
Product
```

## Seller

```text id="p3x9c7"
Seller State
  ↓
Seller City
  ↓
Seller
```

Drill-down should be available only where it adds analytical value.

---

# 22. Drill-Down Rules

Drill-down must:

* Preserve the current filter context.
* Follow approved hierarchy definitions.
* Maintain chronological date ordering.
* Avoid introducing unsupported dimensions.
* Return the user to a comprehensible analytical state.

The default report view should remain at the appropriate summary level.

---

# 23. Drill-Through Architecture

Optional drill-through pages may be implemented for:

### Product Detail

Context:

```text
Product
```

Content may include:

* Product ID
* Category
* Product Sales
* Product Sales %
* Total Items
* Time trend

### Seller Detail

Context:

```text
Seller
```

Content may include:

* Seller ID
* Seller City
* Seller State
* Seller Sales
* Seller Orders
* Time trend

### Customer Detail

Context:

```text
Customer
```

Content may include:

* Customer Unique ID
* Customer State
* Orders
* Customer Sales
* Repeat Customer Status

Drill-through pages must provide additional diagnostic depth and must not duplicate primary pages.

---

# 24. Drill-Through Navigation

Every drill-through page should provide a clear:

**Back**

control.

The originating context must be preserved when the user enters the drill-through page.

---

# 25. Tooltip Interaction

Tooltips should provide contextual information when additional permanent visuals would create clutter.

## Product

* Product
* Category
* Product Sales
* Product Sales %
* Total Items

## Seller

* Seller
* Seller State
* Seller City
* Seller Sales
* Seller Orders

## Customer

* Customer
* Customer State
* Customer Sales
* Orders
* Repeat Customer Status

Tooltips should not contain unnecessary duplicate information.

---

# 26. Top N / Bottom N Interaction

Top N and Bottom N are visual-level analytical constraints.

Use them for:

* Top Products
* Top Sellers
* Bottom Sellers
* Top Customers

They should respond to the applicable report/page filter context.

Do not create a global Top N slicer unless a future business requirement specifically requires dynamic ranking controls.

---

# 27. Navigation Architecture

Persistent navigation should be available across all primary pages.

```text id="8x4j1n"
Executive
   │
   ├── Product & Category
   │
   ├── Regional & Seller
   │
   └── Customer
```

Recommended implementation:

* Power BI page navigation buttons
* Consistent placement
* Clear current-page state
* Back navigation for drill-through pages

---

# 28. Filter Reset Strategy

Users should be able to clear filters using standard Power BI controls.

For complex report states, a reset mechanism may be implemented using bookmarks.

Reset functionality must:

* Restore the intended default filter state.
* Avoid changing unrelated navigation settings.
* Be clearly labeled.

Bookmarks should supplement, not replace, standard slicer behavior.

---

# 29. Filter Behavior by Page

| Page                          | Global Date          | Page Filters                         | Primary Interactions                    |
| ----------------------------- | -------------------- | ------------------------------------ | --------------------------------------- |
| Executive Sales Overview      | Year, Quarter, Month | Category, Product, Customer State    | Category / State → KPIs, Trend, Drivers |
| Product & Category Analysis   | Year, Quarter, Month | Category, Product                    | Category → Product Analysis             |
| Regional & Seller Performance | Year, Quarter, Month | Customer State, Seller State, Seller | Geography / Seller → Related Analysis   |
| Customer Analysis             | Year, Quarter, Month | Customer State                       | Geography → Customer Analysis           |

---

# 30. Performance Rules

Interaction design must account for report performance.

### Requirements

* Avoid unnecessary high-cardinality slicers.
* Avoid excessive visual interactions.
* Avoid unrestricted customer/product/seller visuals.
* Use Top N for large ranking populations.
* Use dimension fields for slicers.
* Avoid unnecessary bidirectional relationships.
* Avoid fact-to-fact filtering.
* Avoid unnecessary map visuals.
* Validate interaction performance using Power BI Performance Analyzer.

---

# 31. User Experience Standards

Filters should be:

* Predictable
* Consistent
* Clearly labeled
* Logically grouped
* Easy to clear
* Consistent across pages

Recommended visual grouping:

```text id="1j8q3z"
Date
  ↓
Product
  ↓
Geography
  ↓
Seller / Customer
```

The actual filter layout may vary by page while maintaining the same logical ordering.

---

# 32. Interaction Anti-Patterns

The following are prohibited unless formally justified:

* Fact-to-fact filtering
* Bidirectional filtering used merely to make a slicer work
* Many-to-many relationships introduced for convenience
* Duplicate geography slicers
* Multiple independent date dimensions for the same reporting context
* Global high-cardinality ID slicers
* Excessive cross-highlighting
* Hidden filter logic that users cannot understand
* Drill-through pages that simply duplicate primary pages

---

# 33. Interaction Validation Matrix

Before production release, validate at minimum:

| Test                     | Expected Result                           |
| ------------------------ | ----------------------------------------- |
| Year selection           | All relevant pages respond                |
| Quarter selection        | All relevant pages respond                |
| Month selection          | All relevant pages respond                |
| Category selection       | Related visuals update                    |
| Product selection        | Related product visuals update            |
| Customer State selection | Customer-related analysis updates         |
| Seller State selection   | Seller-related analysis updates           |
| Seller selection         | Seller analysis updates                   |
| Top N filter             | Correct ranking population displayed      |
| Bottom N filter          | Correct ranking population displayed      |
| Date drill-down          | Correct hierarchy and chronological order |
| Product drill-down       | Category → Product works                  |
| Seller drill-down        | State → City → Seller works               |
| Drill-through            | Context preserved                         |
| Tooltip                  | Correct entity context shown              |
| Navigation               | All primary pages accessible              |
| Back button              | Drill-through returns correctly           |
| Reset                    | Default state restored                    |
| Fact isolation           | No unintended fact-to-fact filtering      |

---

# 34. Production Acceptance Checklist

* [ ] Report-level date filters are synchronized.
* [ ] Date filters originate from `dim_date`.
* [ ] Page-level filters use approved dimensions.
* [ ] High-cardinality filters are controlled.
* [ ] Customer and seller geography remain separate.
* [ ] No duplicate region/customer-state slicers exist.
* [ ] Cross-filter interactions are intentional.
* [ ] Cross-highlighting is intentional.
* [ ] Edit Interactions are explicitly configured.
* [ ] Date-role behavior is validated.
* [ ] Drill-down hierarchies work correctly.
* [ ] Drill-through context is preserved.
* [ ] Tooltips display correct context.
* [ ] Navigation works across all primary pages.
* [ ] Reset behavior works as intended.
* [ ] No fact-to-fact filter path exists.
* [ ] No unsupported many-to-many relationship is required.
* [ ] Performance is acceptable.
* [ ] User-facing filter terminology is consistent.

---

# 35. Final Interaction Architecture

```text id="f3d8w0"
                    USER
                      │
                      ▼
              Report Date Context
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Product     Geography     Seller
       Filters      Filters      Filters
          │           │           │
          └───────────┼───────────┘
                      ▼
                 Dimensions
                      │
                    1:*
                      ▼
                    Facts
                      │
                      ▼
                  DAX Measures
                      │
                      ▼
                   Visuals
```

All filtering must propagate through the approved semantic model rather than through manually created fact-to-fact paths.

---

# 36. Phase 15.10–15.11 Decision

The Power BI filter and interaction architecture is finalized.

The approved design uses:

* Synchronized date filtering
* Dimension-based slicers
* Controlled page-level filtering
* Visual-level Top N / Bottom N filtering
* Explicit cross-filtering
* Selective cross-highlighting
* Explicit Edit Interactions configuration
* Governed date-role behavior
* Drill-down hierarchies
* Optional drill-through pages
* Contextual tooltips
* Persistent navigation
* Controlled reset behavior

All interaction behavior must remain consistent with the finalized Power BI star schema and its single-direction dimension-to-fact filtering architecture.

**Status: FILTER & INTERACTION PLAN — FINALIZED FOR IMPLEMENTATION**
