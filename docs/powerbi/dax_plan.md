    # Power BI DAX Plan

## 1. Purpose

This document defines the governed DAX measure architecture required to implement the approved Power BI report.

The DAX layer translates the validated KPI definitions and semantic model into reusable analytical measures.

The plan establishes:

* Measure inventory
* Measure definitions
* Source facts
* Calculation logic
* Filter-context behavior
* Time intelligence
* Ranking logic
* Contribution calculations
* Customer behavior calculations
* Measure dependencies
* Formatting standards
* Validation requirements

All production KPIs should be implemented as explicit semantic-model measures.

---

# 2. DAX Architecture

The DAX layer follows a reusable measure hierarchy:

```text
Source Facts
     ↓
Base Measures
     ↓
Derived Measures
     ↓
Analytical Measures
     ↓
Report Visuals
```

Example:

```text
fact_payments[payment_value]
          ↓
     [Total Sales]
          ↓
 ┌────────┼─────────┐
 ↓        ↓         ↓
[AOV]   [YTD]   [YoY Growth]
```

Derived measures should reuse existing base measures wherever practical rather than repeating source-table aggregation logic.

---

# 3. DAX Design Principles

The implementation must follow these principles:

1. Use explicit measures for business KPIs.
2. Reuse base measures.
3. Use `DIVIDE()` for ratios.
4. Use `dim_date` for time intelligence.
5. Preserve semantic-model filter context.
6. Modify filter context only when analytically required.
7. Use `ALLSELECTED()` for selection-aware ranking.
8. Use `REMOVEFILTERS()` only for the dimension context that must be removed.
9. Avoid unnecessary calculated columns.
10. Avoid fact-to-fact calculation patterns.
11. Keep measure names business-friendly.
12. Keep measure definitions consistent with the KPI dictionary.
13. Separate payment-based and item-price sales definitions.
14. Validate measures against the approved Phase 14 analytical results where applicable.

---

# 4. Measure Naming Standards

Measures should use business terminology rather than technical implementation terminology.

### Preferred

```text
[Total Sales]
[Total Orders]
[AOV]
[Product Sales]
[Repeat Customers]
```

### Avoid

```text
[SUM Payment Value]
[Order Count Calc]
[Sales Measure 2]
[Temp Revenue]
```

All measures should use a consistent naming convention.

---

# 5. Base Measures

## 5.1 Total Sales

**Measure:** `[Total Sales]`

**Source:**

```text
fact_payments[payment_value]
```

**DAX:**

```DAX
Total Sales =
SUM ( fact_payments[payment_value] )
```

**Business Definition:**

Total payment value under the current filter context.

**Primary Uses:**

* Executive Sales Overview
* AOV
* YoY Sales Growth
* MoM Sales Growth
* YTD Sales
* Regional Sales
* Customer Sales

**Format:**

Currency — `R$`

---

## 5.2 Total Orders

**Measure:** `[Total Orders]`

**Source:**

```text
fact_orders[order_id]
```

**DAX:**

```DAX
Total Orders =
DISTINCTCOUNT ( fact_orders[order_id] )
```

**Business Definition:**

Number of distinct orders under the current filter context.

**Format:**

Whole number.

---

## 5.3 Total Items

**Measure:** `[Total Items]`

**Source:**

```text
fact_order_items
```

**DAX:**

```DAX
Total Items =
COUNTROWS ( fact_order_items )
```

**Business Definition:**

Number of order-item records under the current filter context.

**Format:**

Whole number.

---

## 5.4 AOV

**Measure:** `[AOV]`

**DAX:**

```DAX
AOV =
DIVIDE (
    [Total Sales],
    [Total Orders]
)
```

**Business Definition:**

Average payment-based sales value per order.

**Format:**

Currency — `R$`

---

# 6. Time Intelligence Measures

## 6.1 Monthly Sales

No separate aggregation logic is required for standard monthly sales.

`[Total Sales]` evaluated under:

```text
dim_date[month_year]
```

provides the monthly sales value.

Therefore, `[Total Sales]` is the authoritative measure for the Monthly Sales Trend.

A separate `[Monthly Sales]` measure should only be created if a distinct business definition becomes necessary.

---

## 6.2 MoM Sales Growth %

**Measure:** `[MoM Sales Growth %]`

**DAX:**

```DAX
MoM Sales Growth % =
VAR CurrentSales =
    [Total Sales]
VAR PreviousMonthSales =
    CALCULATE (
        [Total Sales],
        DATEADD (
            dim_date[full_date],
            -1,
            MONTH
        )
    )
RETURN
    DIVIDE (
        CurrentSales - PreviousMonthSales,
        PreviousMonthSales
    )
```

**Purpose:**

Measure month-over-month sales growth.

**Format:**

Percentage — `0.0%`

---

## 6.3 YoY Sales Growth %

**Measure:** `[YoY Sales Growth %]`

**DAX:**

```DAX
YoY Sales Growth % =
VAR CurrentSales =
    [Total Sales]
VAR PreviousYearSales =
    CALCULATE (
        [Total Sales],
        DATEADD (
            dim_date[full_date],
            -1,
            YEAR
        )
    )
RETURN
    DIVIDE (
        CurrentSales - PreviousYearSales,
        PreviousYearSales
    )
```

**Purpose:**

Measure year-over-year sales growth.

**Format:**

Percentage — `0.0%`

---

## 6.4 YTD Sales

**Measure:** `[YTD Sales]`

**DAX:**

```DAX
YTD Sales =
TOTALYTD (
    [Total Sales],
    dim_date[full_date]
)
```

**Purpose:**

Calculate cumulative sales from the beginning of the selected year through the current date context.

**Format:**

Currency — `R$`

---

# 7. Product & Category Measures

## 7.1 Category Sales

**Measure:** `[Category Sales]`

**Source:**

```text
fact_order_items[price]
```

**DAX:**

```DAX
Category Sales =
SUM ( fact_order_items[price] )
```

**Business Definition:**

Item-price sales evaluated under the current category/filter context.

**Format:**

Currency — `R$`

---

## 7.2 Product Sales

**Measure:** `[Product Sales]`

**Source:**

```text
fact_order_items[price]
```

**DAX:**

```DAX
Product Sales =
SUM ( fact_order_items[price] )
```

**Business Definition:**

Item-price sales evaluated under the current product/filter context.

**Format:**

Currency — `R$`

---

## 7.3 Category Sales %

**Measure:** `[Category Sales %]`

**DAX:**

```DAX
Category Sales % =
DIVIDE (
    [Category Sales],
    CALCULATE (
        [Category Sales],
        REMOVEFILTERS (
            dim_product[product_category_name_english]
        )
    )
)
```

**Purpose:**

Measure category contribution relative to the intended comparison total.

**Format:**

Percentage — `0.0%`

### Governance

Only the category filter is removed from the denominator.

Other report context, such as date selections, should remain active.

---

## 7.4 Product Sales %

**Measure:** `[Product Sales %]`

**DAX:**

```DAX
Product Sales % =
DIVIDE (
    [Product Sales],
    CALCULATE (
        [Product Sales],
        REMOVEFILTERS (
            dim_product[product_id]
        )
    )
)
```

**Purpose:**

Measure product contribution relative to the selected product comparison population.

**Format:**

Percentage — `0.0%`

---

## 7.5 Top Product

**Measure:** `[Top Product]`

**DAX:**

```DAX
Top Product =
VAR RankedProducts =
    TOPN (
        1,
        ALLSELECTED (
            dim_product[product_id]
        ),
        [Product Sales],
        DESC
    )
RETURN
    CONCATENATEX (
        RankedProducts,
        dim_product[product_id],
        ", "
    )
```

**Purpose:**

Return the highest-sales product within the current selection.

**Governance:**

The result must respect relevant report and page selections.

Tie behavior should be validated during implementation.

---

## 7.6 Top Category

**Measure:** `[Top Category]`

**DAX:**

```DAX
Top Category =
VAR RankedCategories =
    TOPN (
        1,
        ALLSELECTED (
            dim_product[product_category_name_english]
        ),
        [Category Sales],
        DESC
    )
RETURN
    CONCATENATEX (
        RankedCategories,
        dim_product[product_category_name_english],
        ", "
    )
```

**Purpose:**

Return the highest-sales category within the current selection.

---

## 7.7 Cumulative Product Sales %

**Measure:** `[Cumulative Product Sales %]`

**Purpose:**

Support the Product Pareto visual.

The measure must:

1. Respect the current report selection.
2. Establish the selected product population.
3. Rank products by `[Product Sales]`.
4. Calculate cumulative product sales.
5. Divide cumulative sales by the appropriate selected product-sales total.

### Implementation Requirement

The final production implementation must explicitly validate:

* Product ranking
* Descending sales order
* Tie behavior
* Current filter context
* Denominator definition
* Pareto visual behavior

This measure must not be considered production-ready until its results have been validated against a manually calculated sample.

---

# 8. Regional Measures

## 8.1 Regional Sales

**Measure:** `[Regional Sales]`

**DAX:**

```DAX
Regional Sales =
[Total Sales]
```

**Business Definition:**

Payment-based sales evaluated under the current customer-state filter context.

---

## 8.2 Regional Sales %

**Measure:** `[Regional Sales %]`

**DAX:**

```DAX
Regional Sales % =
DIVIDE (
    [Regional Sales],
    CALCULATE (
        [Regional Sales],
        REMOVEFILTERS (
            dim_customer[customer_state]
        )
    )
)
```

**Purpose:**

Measure each customer state's contribution to the intended comparison total.

**Format:**

Percentage — `0.0%`

---

## 8.3 Top Region

**Measure:** `[Top Region]`

**DAX:**

```DAX
Top Region =
VAR RankedRegions =
    TOPN (
        1,
        ALLSELECTED (
            dim_customer[customer_state]
        ),
        [Regional Sales],
        DESC
    )
RETURN
    CONCATENATEX (
        RankedRegions,
        dim_customer[customer_state],
        ", "
    )
```

**Purpose:**

Return the highest-sales customer state within the active selection.

---

# 9. Seller Measures

## 9.1 Seller Sales

**Measure:** `[Seller Sales]`

**Source:**

```text
fact_order_items[price]
```

**DAX:**

```DAX
Seller Sales =
SUM ( fact_order_items[price] )
```

**Business Definition:**

Item-price sales under the current seller context.

**Format:**

Currency — `R$`

---

## 9.2 Seller Orders

**Measure:** `[Seller Orders]`

**Source:**

```text
fact_order_items[order_id]
```

**DAX:**

```DAX
Seller Orders =
DISTINCTCOUNT ( fact_order_items[order_id] )
```

**Business Definition:**

Distinct orders associated with the current seller context.

**Format:**

Whole number.

---

# 10. Customer Measures

## 10.1 Total Customers

**Measure:** `[Total Customers]`

**Source:**

```text
dim_customer[customer_unique_id]
```

**DAX:**

```DAX
Total Customers =
DISTINCTCOUNT (
    dim_customer[customer_unique_id]
)
```

**Business Definition:**

Number of unique customers under the current filter context.

**Format:**

Whole number.

---

## 10.2 Repeat Customers

**Measure:** `[Repeat Customers]`

**DAX:**

```DAX
Repeat Customers =
COUNTROWS (
    FILTER (
        VALUES (
            dim_customer[customer_unique_id]
        ),
        CALCULATE (
            DISTINCTCOUNT (
                fact_orders[order_id]
            )
        ) > 1
    )
)
```

**Business Definition:**

Number of unique customers with more than one distinct order.

**Format:**

Whole number.

---

## 10.3 Repeat Customer %

**Measure:** `[Repeat Customer %]`

**DAX:**

```DAX
Repeat Customer % =
DIVIDE (
    [Repeat Customers],
    [Total Customers]
)
```

**Purpose:**

Measure repeat-customer penetration.

**Format:**

Percentage — `0.0%`

---

## 10.4 Customer Sales

**Measure:** `[Customer Sales]`

**DAX:**

```DAX
Customer Sales =
[Total Sales]
```

**Business Definition:**

Payment-based sales evaluated under the current customer filter context.

**Format:**

Currency — `R$`

---

## 10.5 Orders per Customer

**Measure:** `[Orders per Customer]`

**DAX:**

```DAX
Orders per Customer =
DIVIDE (
    [Total Orders],
    [Total Customers]
)
```

**Business Definition:**

Average number of distinct orders per unique customer.

**Format:**

Appropriate decimal precision.

---

# 11. Repeat vs Non-Repeat Customer Analysis

The report requires two customer groups:

```text
Repeat Customer
Non-Repeat Customer
```

### Business Rule

```text
Distinct Orders > 1
    → Repeat Customer

Distinct Orders = 1
    → Non-Repeat Customer
```

The classification must be generated dynamically from customer order behavior.

The implementation must avoid hard-coded customer classifications.

A customer-count measure must then aggregate customers within the selected classification.

### Validation Requirement

The final implementation must reconcile:

```text
Repeat Customers
+
Non-Repeat Customers
=
Total Customers
```

under equivalent filter context.

---

# 12. Supporting Measures

## Customer Orders

```DAX
Customer Orders =
[Total Orders]
```

This measure inherits the current customer filter context.

---

## Product Item Volume

```DAX
Product Item Volume =
[Total Items]
```

This may be used in detailed product analysis where item volume is required.

---

# 13. Measure Inventory

The approved DAX inventory is:

|  # | Measure                             |
| -: | ----------------------------------- |
|  1 | Total Sales                         |
|  2 | Total Orders                        |
|  3 | Total Items                         |
|  4 | AOV                                 |
|  5 | MoM Sales Growth %                  |
|  6 | YoY Sales Growth %                  |
|  7 | YTD Sales                           |
|  8 | Category Sales                      |
|  9 | Product Sales                       |
| 10 | Category Sales %                    |
| 11 | Product Sales %                     |
| 12 | Top Product                         |
| 13 | Top Category                        |
| 14 | Cumulative Product Sales %          |
| 15 | Regional Sales                      |
| 16 | Regional Sales %                    |
| 17 | Top Region                          |
| 18 | Seller Sales                        |
| 19 | Seller Orders                       |
| 20 | Total Customers                     |
| 21 | Repeat Customers                    |
| 22 | Repeat Customer %                   |
| 23 | Customer Sales                      |
| 24 | Orders per Customer                 |
| 25 | Customer Orders                     |
| 26 | Product Item Volume                 |
| 27 | Repeat vs Non-Repeat Customer Count |

`Monthly Sales` is not required as an independent calculation because `[Total Sales]` evaluated at monthly `dim_date` context provides the required metric.

---

# 14. DAX → Report Page Mapping

| Report Page                   | Required Measures                                                                                                                    |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Executive Sales Overview      | Total Sales, Total Orders, AOV, YoY Sales Growth %, YTD Sales, Category Sales, Regional Sales                                        |
| Product & Category Analysis   | Category Sales, Category Sales %, Top Category, Product Sales, Product Sales %, Top Product, Total Items, Cumulative Product Sales % |
| Regional & Seller Performance | Regional Sales, Regional Sales %, Top Region, Seller Sales, Seller Orders                                                            |
| Customer Analysis             | Total Customers, Repeat Customers, Repeat Customer %, Customer Sales, Orders per Customer, Repeat vs Non-Repeat Customer Count       |

---

# 15. Measure Dependency Architecture

```text
                     [Total Sales]
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
           [AOV]       [YTD Sales]   [Customer Sales]
             │
             ▼
     [MoM / YoY Growth]

                     [Total Orders]
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
               [AOV]       [Orders per Customer]

                   [Total Customers]
                          │
                 ┌────────┴────────┐
                 ▼                 ▼
        [Repeat Customer %]  [Orders per Customer]

                 [Repeat Customers]
                         │
                         ▼
              [Repeat Customer %]

                 [Category Sales]
                    │       │
                    ▼       ▼
          [Category Sales %] [Top Category]

                  [Product Sales]
                 │      │       │
                 ▼      ▼       ▼
             [Product  [Top    [Cumulative
              Sales %] Product] Product %]

                 [Regional Sales]
                    │       │
                    ▼       ▼
          [Regional Sales %] [Top Region]

              [Seller Sales]
                    │
                    └── Seller Analysis

              [Seller Orders]
                    │
                    └── Seller Analysis
```

---

# 16. Filter Context Governance

Measures must respect the active filter context by default.

Examples:

```text
Year
Quarter
Month
Category
Product
Customer State
Seller State
Seller
```

should affect measures through the semantic model where the relationship path supports the analysis.

Filter context should only be modified intentionally using functions such as:

* `CALCULATE()`
* `REMOVEFILTERS()`
* `ALLSELECTED()`
* `DATEADD()`
* `TOTALYTD()`

---

# 17. `REMOVEFILTERS()` Governance

`REMOVEFILTERS()` must be scoped to the dimension attribute relevant to the denominator.

For example:

```DAX
REMOVEFILTERS (
    dim_customer[customer_state]
)
```

is appropriate for calculating the regional comparison total.

Do not remove the entire model filter context unless the business definition explicitly requires it.

Unnecessary filter removal can produce misleading KPI results.

---

# 18. `ALLSELECTED()` Governance

`ALLSELECTED()` should be used where the measure needs to respect the user's current report/page selections while evaluating a ranking population.

Primary use cases:

* Top Product
* Top Category
* Top Region
* Product Pareto

The resulting ranking behavior must be tested under:

* No filters
* Date filters
* Category filters
* Geography filters
* Combined filters

---

# 19. Time-Intelligence Governance

All standard time intelligence must use:

```text
dim_date[full_date]
```

The date dimension must:

* Contain a continuous calendar.
* Be correctly configured as the Power BI Date Table.
* Use chronological sorting.
* Provide the required year/month/quarter attributes.

Time-intelligence calculations must not depend on fact-table date columns directly.

---

# 20. Sales Definition Governance

The model contains two distinct sales concepts.

## Payment-Based Sales

Source:

```text
fact_payments[payment_value]
```

Used for:

* Total Sales
* AOV
* MoM Sales Growth
* YoY Sales Growth
* YTD Sales
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

These definitions must remain separate.

They must not be renamed or combined into a single generic sales calculation.

---

# 21. Customer Identity Governance

Customer analysis uses:

```text
dim_customer[customer_unique_id]
```

for unique-customer metrics.

Therefore:

```text
Total Customers
Repeat Customers
Repeat Customer %
```

must be based on unique customer identity rather than raw customer-record counts.

This is necessary to maintain consistency with the approved KPI definitions.

---

# 22. DAX Anti-Patterns

The following should be avoided:

* Repeating identical aggregation logic across many measures.
* Unnecessary calculated columns.
* Hard-coded customer classifications.
* Hard-coded rankings.
* Direct fact-to-fact calculations.
* Uncontrolled `ALL()` usage.
* Broad `REMOVEFILTERS()` usage.
* Time intelligence based on fact dates instead of `dim_date`.
* Measures with ambiguous business names.
* DAX logic that contradicts the KPI dictionary.

---

# 23. Measure Formatting Standards

| Measure Type        | Format                        |
| ------------------- | ----------------------------- |
| Sales               | `R$` currency                 |
| AOV                 | `R$` currency                 |
| Counts              | Whole number                  |
| Growth              | `0.0%`                        |
| Contribution        | `0.0%`                        |
| Customer rate       | `0.0%`                        |
| Orders per Customer | Appropriate decimal precision |

Formatting should be applied at the semantic-model measure level wherever practical.

---

# 24. DAX Validation Framework

Every production measure must be validated at three levels.

## Level 1 — Calculation Validation

Confirm the DAX returns the mathematically expected result.

## Level 2 — Filter Validation

Confirm the result changes correctly under:

* Date filters
* Product filters
* Geography filters
* Seller filters
* Customer filters

## Level 3 — Cross-System Reconciliation

Where a corresponding Phase 14 SQL/Python metric exists, compare Power BI output against the validated analytical result.

Expected reconciliation should account for:

* Filter context
* Date context
* Aggregation grain
* Business definition

---

# 25. Critical DAX Validation Tests

The following tests are mandatory:

### Sales

* [ ] `[Total Sales]` reconciles with payment-based sales.
* [ ] `[AOV]` equals Total Sales ÷ Total Orders.
* [ ] `[YTD Sales]` accumulates correctly.
* [ ] `[MoM Sales Growth %]` handles missing prior months appropriately.
* [ ] `[YoY Sales Growth %]` handles missing prior-year periods appropriately.

### Product

* [ ] Category Sales uses `fact_order_items[price]`.
* [ ] Product Sales uses `fact_order_items[price]`.
* [ ] Category Sales % uses the intended denominator.
* [ ] Product Sales % uses the intended denominator.
* [ ] Top Product respects active selections.
* [ ] Product Pareto is correctly ordered.

### Regional

* [ ] Regional Sales uses payment-based sales.
* [ ] Regional Sales % uses the intended state comparison total.
* [ ] Top Region responds to active filters.

### Seller

* [ ] Seller Sales uses item-price sales.
* [ ] Seller Orders counts distinct orders.

### Customer

* [ ] Total Customers uses `customer_unique_id`.
* [ ] Repeat Customers counts customers with >1 distinct order.
* [ ] Repeat Customer % uses the approved denominator.
* [ ] Customer Sales uses payment-based sales.
* [ ] Orders per Customer uses distinct orders / unique customers.
* [ ] Repeat and non-repeat populations reconcile to Total Customers.

---

# 26. Performance Validation

DAX measures should be evaluated for performance during Power BI implementation.

Particular attention should be given to:

* High-cardinality customer calculations
* Product Pareto calculations
* Ranking measures
* Repeat-customer calculations
* Large table visuals

If a measure causes unacceptable query cost, optimization must preserve the original business definition.

Performance optimization must not change KPI semantics merely to improve execution time.

---

# 27. DAX Production Readiness Checklist

* [ ] Measure has an approved business definition.
* [ ] Measure uses the correct fact/dimension.
* [ ] Measure uses the correct grain.
* [ ] Measure name follows naming standards.
* [ ] Measure uses reusable base measures where appropriate.
* [ ] Ratios use `DIVIDE()`.
* [ ] Time intelligence uses `dim_date`.
* [ ] Ranking respects intended selections.
* [ ] Filter removal is intentionally scoped.
* [ ] Customer identity is correctly handled.
* [ ] Payment and item-price sales are not conflated.
* [ ] Measure formatting is correct.
* [ ] Measure has been tested under relevant filters.
* [ ] Measure reconciles with validated SQL/Python output where applicable.
* [ ] Performance is acceptable.

---

# 28. Final DAX Architecture

```text
                  PostgreSQL Analytics
                         │
                         ▼
                  Power BI Semantic Model
                         │
                         ▼
                    Base Measures
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
          Time Logic   Rankings   Ratios
              │          │          │
              └──────────┼──────────┘
                         ▼
                  Analytical Measures
                         │
                         ▼
                    Report Visuals
```

The DAX layer is therefore a governed semantic calculation layer rather than a second data-transformation layer.

---

# 29. Phase 15.7 Decision

The DAX measure architecture is finalized for implementation.

The approved design:

* Uses explicit semantic-model measures.
* Reuses base measures.
* Uses `dim_date` for time intelligence.
* Uses controlled filter-context modification.
* Uses selection-aware ranking.
* Separates payment-based and item-price sales.
* Uses unique customer identity for customer metrics.
* Supports the four approved report pages.
* Provides validation and performance requirements.

The remaining implementation work is to create the measures in Power BI, validate their behavior against the approved definitions, and reconcile applicable outputs with the Phase 14 SQL/Python validation results.

**Status: DAX PLAN — FINALIZED FOR IMPLEMENTATION**
