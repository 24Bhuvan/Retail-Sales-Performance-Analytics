# Relationship Matrix

## Document Information

| Item | Value |
|------|-------|
| Project | Retail Sales Performance Analytics |
| Phase | Phase 2 — Data Understanding |
| Document | Relationship Matrix |
| Source | `notebooks/02_Data_Understanding.ipynb` |
| Version | 1.0 |

---

# Purpose

This document defines the logical relationships between datasets used in the Retail Sales Performance Analytics project. Relationships were validated during the Data Understanding phase using referential integrity checks, key comparisons, and duplicate key validation.

---

# Relationship Matrix

| Parent Table | Child Table | Join Key | Relationship Type | Relationship Purpose | Validation Status |
|--------------|-------------|----------|-------------------|----------------------|-------------------|
| Customers | Orders | `customer_id` | 1 : Many | Associates each order with the customer who placed it. | ✅ Validated |
| Orders | Order Items | `order_id` | 1 : Many | Associates orders with purchased products. | ✅ Validated |
| Products | Order Items | `product_id` | 1 : Many | Associates purchased items with product information. | ✅ Validated |
| Sellers | Order Items | `seller_id` | 1 : Many | Associates purchased items with the responsible seller. | ✅ Validated |
| Orders | Payments | `order_id` | 1 : Many | Associates payment transactions with orders. | ✅ Validated |
| Orders | Reviews | `order_id` | 1 : Many | Associates customer reviews with orders. | ✅ Validated |
| Category Translation | Products | `product_category_name` | 1 : Many | Maps Portuguese product categories to English category names. | ✅ Validated |

---

# Relationship Validation Details

## 1. Customers → Orders

| Validation | Result |
|------------|--------|
| Join Key | `customer_id` |
| Parent Records | 99,441 |
| Child Records | 99,441 |
| Matching Child Keys | 99,441 |
| Orphan Records | 0 |
| Duplicate Parent Keys | 0 |
| Validation Status | Passed |

**Observation**

- Every order references a valid customer.
- No orphan customer references were detected.
- No duplicate primary keys exist in the Customers table.

---

## 2. Orders → Order Items

| Validation | Result |
|------------|--------|
| Join Key | `order_id` |
| Parent Records | 99,441 |
| Child Records | 112,650 |
| Matching Child Keys | 112,650 |
| Orphan Records | 0 |
| Duplicate Parent Keys | 0 |
| Validation Status | Passed |

**Observation**

- Every order item belongs to a valid order.
- One order may contain multiple products.
- This represents the primary transactional relationship within the dataset.

---

## 3. Products → Order Items

| Validation | Result |
|------------|--------|
| Join Key | `product_id` |
| Parent Records | 32,951 |
| Child Records | 112,650 |
| Matching Child Keys | 112,650 |
| Orphan Records | 0 |
| Duplicate Parent Keys | 0 |
| Validation Status | Passed |

**Observation**

- Every purchased item references an existing product.
- Products may appear in multiple customer orders.

---

## 4. Sellers → Order Items

| Validation | Result |
|------------|--------|
| Join Key | `seller_id` |
| Parent Records | 3,095 |
| Child Records | 112,650 |
| Matching Child Keys | 112,650 |
| Orphan Records | 0 |
| Duplicate Parent Keys | 0 |
| Validation Status | Passed |

**Observation**

- Every order item references a valid seller.
- Sellers may fulfill many products across many orders.

---

## 5. Orders → Payments

| Validation | Result |
|------------|--------|
| Join Key | `order_id` |
| Parent Records | 99,441 |
| Child Records | 103,886 |
| Matching Child Keys | 103,886 |
| Orphan Records | 0 |
| Duplicate Parent Keys | 0 |
| Validation Status | Passed |

**Observation**

- Every payment references an existing order.
- Some orders contain multiple payment transactions.
- One order has no associated payment record.

---

## 6. Orders → Reviews

| Validation | Result |
|------------|--------|
| Join Key | `order_id` |
| Parent Records | 99,441 |
| Child Records | 99,224 |
| Matching Child Keys | 99,224 |
| Orphan Records | 0 |
| Duplicate Parent Keys | 0 |
| Validation Status | Passed |

**Observation**

- Every review references an existing order.
- Not every order has an associated review.
- A small number of orders contain multiple review records.

---

## 7. Category Translation → Products

| Validation | Result |
|------------|--------|
| Join Key | `product_category_name` |
| Parent Records | 71 |
| Child Records | 32,951 |
| Matching Child Records | 32,328 |
| Orphan Records | 0 (for non-null categories) |
| Validation Status | Passed with Exceptions |

**Observation**

- Translation table functions as a lookup dimension.
- Products contain 73 unique categories, while the translation table contains 71 mappings.
- The unmatched records correspond to products with missing category values and categories without English translations.

---

# Referential Integrity Summary

| Validation Check | Result |
|------------------|--------|
| Customers → Orders | Passed |
| Orders → Order Items | Passed |
| Products → Order Items | Passed |
| Sellers → Order Items | Passed |
| Orders → Payments | Passed |
| Orders → Reviews | Passed |
| Category Translation → Products | Passed (minor mapping exceptions) |

---

# Overall Assessment

The validation confirms that the retail dataset follows a consistent relational structure centered on the **Orders** table.

Key findings include:

- All validated foreign key relationships successfully reference existing parent records.
- No orphan records were identified in the Customers, Orders, Products, Sellers, Payments, or Reviews relationships.
- No duplicate values were detected in validated parent key columns.
- The dataset primarily follows one-to-many relationships between dimension tables and transactional tables.
- The Product Category Translation table is nearly complete, with only a small number of unmapped or missing product categories.

The validated relationships documented here provide the foundation for data preparation, dimensional modeling, and analytical reporting in subsequent project phases.