# KPI Design Summary

## Phase

Phase 13 — KPI Design

## Objective

Define standardized KPI definitions, calculation rules, formulas, data sources, grains, and implementation feasibility for the Retail Sales Performance Analytics project.

## KPI Inventory

**Total KPIs Approved: 32**

### Primary KPIs — 9

- Total Revenue
- Total Orders
- Average Order Value
- Monthly Revenue Growth
- Total Customers
- Repeat Customer Rate
- On-Time Delivery Rate
- Average Delivery Time
- Average Review Score

### Supporting KPIs — 20

- Total Order Value
- Monthly Revenue
- Average Items per Order
- Customer Lifetime Revenue
- Average Customer Order Value
- Category Revenue
- Category Revenue Share
- Product Revenue
- Seller Revenue
- Seller Order Count
- Revenue by Customer State
- Total Payment Value
- Payment Method Share
- Average Payment Installments
- Average Processing Time
- Late Delivery Rate
- Average Delivery Difference
- Total Freight Value
- Low Satisfaction Rate
- High Satisfaction Rate

### Diagnostic Metrics — 3

- Rolling 3-Month Revenue
- Multi-Payment Order Rate
- Freight-to-Price Ratio

## Business Areas

1. Sales & Revenue
2. Orders
3. Customers
4. Products & Categories
5. Sellers
6. Geography
7. Payments
8. Delivery & Operations
9. Customer Satisfaction

## Data Feasibility

- KPIs technically feasible: **32/32**
- PostgreSQL implementation: **32/32**
- Pandas implementation: **32/32**
- Power BI implementation: **32/32**

The KPI feasibility validation identified that all approved KPIs are technically implementable using the available processed datasets and engineered feature layer.

## Implementation Risks and Controls

The following KPIs require explicit aggregation, grain, or join controls:

- **Customer Lifetime Revenue** — Must not be summed globally as a replacement for Total Revenue because it is a customer-grain metric.
- **Average Customer Order Value** — Must explicitly define whether it represents the average of customer-level AOV values or total revenue divided by total orders.
- **Category Revenue** — Item-level revenue must be aggregated at the appropriate grain before joins that could multiply rows.
- **Category Revenue Share** — Category and total revenue must use controlled aggregation to ensure consistent denominators.
- **Seller Order Count** — Must use distinct order counting because a seller can have multiple items within an order.
- **Revenue by Customer State** — Order-level revenue must be joined to customer geography without row multiplication.
- **Freight-to-Price Ratio** — Aggregate calculation must be explicitly defined; blindly averaging item-level ratios may be misleading.

## Key Calculation Rules

- Revenue is based on item revenue.
- Freight is excluded from revenue.
- Payment value is separate from revenue.
- Multi-item orders require distinct order counting where order counts are used.
- Customer identity uses `customer_unique_id`.
- Monthly KPIs use purchase month as the standard time basis.
- Delivery KPIs exclude records with missing required timestamps or unclassified delivery status.
- Review KPIs use order-level review features to avoid duplicate review records.
- Payment metrics are calculated independently from revenue metrics.
- Multi-payment behavior is evaluated using the engineered order-level payment features.

## KPI Governance

The KPI definitions, formulas, source datasets, source columns, grains, filters, exclusions, aggregation rules, and business relevance are maintained in:

- `docs/kpi_dictionary.md`
- `docs/kpi_specification.md`

These documents serve as the Phase 13 reference for consistent KPI implementation in PostgreSQL, Pandas, Excel, and Power BI.

## Phase Boundary

Phase 13 defines and validates KPI design only.

No final KPI values are calculated in this phase.

Final KPI calculations, SQL implementation, Pandas implementation, and final metric outputs begin in **Phase 14 — Business Metrics Calculation**.

## Status

**Phase 13 — KPI Design: Complete**

Completed deliverables:

- `docs/kpi_dictionary.md`
- `docs/kpi_specification.md`
- `reports/kpi_design/kpi_candidate_audit.csv`
- `reports/kpi_design/kpi_feasibility_validation.csv`
- `reports/kpi_design/kpi_design_summary.md`

Phase 14 implementation files remain outside the scope of Phase 13:

- `sql/kpi_queries.sql`
- `src/analysis/kpi_calculations.py`
- `src/analysis/business_metrics.py`
