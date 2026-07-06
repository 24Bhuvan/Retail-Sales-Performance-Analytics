# Transformation Requirements Log

## Document Information

| Item | Value |
|------|-------|
| Project | Retail Sales Performance Analytics |
| Phase | Phase 2 — Data Understanding |
| Document | Transformation Requirements Log |
| Source | `notebooks/02_Data_Understanding.ipynb` |
| Version | 1.0 |

---

# Purpose

This document records all data quality issues identified during the Data Understanding phase.

No data modifications are performed in this phase. The identified issues will be addressed during the Data Preparation phase.

---

# Transformation Requirements

| Dataset | Issue | Recommended Action | Priority |
|----------|-------|--------------------|----------|
| Customers | No significant data quality issues identified. | No transformation required. | Low |
| Geolocation | 261,831 duplicate records detected. | Evaluate duplicate removal while preserving geographic coverage. | High |
| Geolocation | Geographic coordinates contain repeated ZIP code observations. | Determine appropriate aggregation strategy before analysis. | Medium |
| Orders | `order_purchase_timestamp` stored as object. | Convert to datetime. | High |
| Orders | `order_approved_at` stored as object. | Convert to datetime. | High |
| Orders | `order_delivered_carrier_date` stored as object. | Convert to datetime. | High |
| Orders | `order_delivered_customer_date` stored as object. | Convert to datetime. | High |
| Orders | `order_estimated_delivery_date` stored as object. | Convert to datetime. | High |
| Orders | Missing values in approval timestamp. | Investigate relationship with order status before handling. | Medium |
| Orders | Missing values in carrier delivery timestamp. | Investigate delivery lifecycle. | Medium |
| Orders | Missing values in customer delivery timestamp. | Determine whether missing values represent cancelled or undelivered orders. | Medium |
| Order Items | `shipping_limit_date` stored as object. | Convert to datetime. | High |
| Payments | Multiple payment records exist for some orders. | Validate business rule before aggregation. | High |
| Reviews | `review_creation_date` stored as object. | Convert to datetime. | Medium |
| Reviews | `review_answer_timestamp` stored as object. | Convert to datetime. | Medium |
| Reviews | Large number of missing review titles. | Preserve null values because review titles are optional. | Low |
| Reviews | Large number of missing review messages. | Preserve null values because written reviews are optional. | Low |
| Products | Missing product category values. | Investigate whether category can be recovered or retained as missing. | High |
| Products | Missing product metadata (`product_name_lenght`, `product_description_lenght`, `product_photos_qty`). | Assess impact before imputation or retention. | Medium |
| Products | Missing physical dimensions and weight. | Determine appropriate handling strategy during preparation. | Medium |
| Products | Product category names stored in Portuguese. | Translate using Category Translation dataset. | High |
| Category Translation | Translation table contains fewer categories than Products. | Identify unmapped product categories and determine reporting strategy. | High |
| Sellers | No significant data quality issues identified. | No transformation required. | Low |

---

# Transformation Categories

## Missing Values

Observed in:

- Orders
- Reviews
- Products

These fields require evaluation before any imputation or removal strategy is selected.

---

## Duplicate Records

Observed in:

- Geolocation

Duplicate records require investigation before removal to avoid losing valid geographic information.

---

## Datatype Conversion

The following columns are currently loaded as object data types but represent dates and timestamps:

### Orders

- `order_purchase_timestamp`
- `order_approved_at`
- `order_delivered_carrier_date`
- `order_delivered_customer_date`
- `order_estimated_delivery_date`

### Order Items

- `shipping_limit_date`

### Reviews

- `review_creation_date`
- `review_answer_timestamp`

These columns should be converted to datetime during the Data Preparation phase.

---

## Language Standardization

Product categories are stored in Portuguese.

The `product_category_name_translation` dataset should be used to create English category names for reporting and dashboard development.

---

## Business Rule Validation

The following business rules require confirmation before transformation:

- Multiple payment transactions may exist for a single order.
- Not every order contains a customer review.
- Missing delivery timestamps may correspond to cancelled, unavailable, or in-progress orders.
- Freight charges are stored separately from product prices and require business validation before revenue calculations.
- Translation coverage should be verified for all product categories.

---

# Priority Definitions

| Priority | Description |
|----------|-------------|
| High | Required before data modeling or KPI calculations. |
| Medium | Important for improving analytical quality but not blocking project progress. |
| Low | Minimal impact on analytical results; may be retained without modification. |

---

# Summary

A total of four primary transformation categories were identified during the Data Understanding phase:

- Missing values
- Duplicate records
- Datatype inconsistencies
- Language standardization

No cleaning, imputation, transformation, or feature engineering has been performed.

This document serves as the formal input for the Data Preparation phase.