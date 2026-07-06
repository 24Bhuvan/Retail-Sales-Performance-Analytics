# Data Inventory

## Document Information

| Item | Value |
|------|-------|
| Project | Retail Sales Performance Analytics |
| Phase | Phase 2 — Data Understanding |
| Document | Data Inventory |
| Source | `notebooks/01_Data_Understanding.ipynb` |
| Version | 1.0 |

---

# Purpose

This document provides a business inventory of every dataset used in the Retail Sales Performance Analytics project. It summarizes the role of each dataset within the retail business process and documents its expected relationships with other datasets.

---

# Dataset Inventory

| Dataset | Business Purpose | Business Process | Type | Grain | Primary Key | Foreign Keys | Parent Tables | Child Tables |
|----------|------------------|------------------|------|--------|-------------|--------------|---------------|--------------|
| Customers | Stores customer identity and geographic information. | Customer Management | Dimension | One row per customer | `customer_id` | — | — | Orders |
| Orders | Stores order lifecycle information from purchase to delivery. | Order Management | Fact | One row per order | `order_id` | `customer_id` | Customers | Order Items, Payments, Reviews |
| Order Items | Stores products purchased within each order. | Sales Transactions | Fact | One row per product within an order | (`order_id`, `order_item_id`) | `order_id`, `product_id`, `seller_id` | Orders, Products, Sellers | — |
| Products | Stores product attributes and specifications. | Product Management | Dimension | One row per product | `product_id` | `product_category_name` | Category Translation | Order Items |
| Sellers | Stores seller information and location. | Seller Management | Dimension | One row per seller | `seller_id` | — | — | Order Items |
| Payments | Stores payment transactions for customer orders. | Payment Processing | Fact | One row per payment transaction | No confirmed single-column key* | `order_id` | Orders | — |
| Reviews | Stores customer ratings and review comments. | Customer Feedback | Fact | One row per review | `review_id` | `order_id` | Orders | — |
| Geolocation | Stores geographic coordinates for ZIP code prefixes. | Geographic Reference | Dimension / Reference | One row per ZIP code observation | No confirmed primary key | — | — | Customers, Sellers |
| Product Category Translation | Translates Portuguese product categories into English. | Reference Data | Dimension / Lookup | One row per category | `product_category_name` | — | — | Products |

---

# Dataset Descriptions

## Customers

**Business Purpose**

Stores customer identity and location information used to identify purchasers and perform geographic analysis.

**Description**

Contains customer identifiers together with ZIP code prefix, city, and state. Multiple customer IDs may belong to the same real customer through `customer_unique_id`.

---

## Orders

**Business Purpose**

Represents the central business transaction within the retail system.

**Description**

Contains the complete order lifecycle, including purchase, approval, shipment, delivery, estimated delivery date, and order status.

---

## Order Items

**Business Purpose**

Represents individual products purchased within an order.

**Description**

Contains product-level sales information including seller, item price, freight value, and shipping deadline.

---

## Products

**Business Purpose**

Stores product master data.

**Description**

Contains product category, physical dimensions, weight, product description metadata, and image counts.

---

## Sellers

**Business Purpose**

Stores seller master information.

**Description**

Contains seller identifiers together with geographic location information.

---

## Payments

**Business Purpose**

Stores financial transactions associated with customer orders.

**Description**

Contains payment method, installment information, payment sequence, and payment value. Some orders contain multiple payment records.

---

## Reviews

**Business Purpose**

Captures customer satisfaction following order completion.

**Description**

Contains review scores, optional review comments, review creation dates, and response timestamps.

---

## Geolocation

**Business Purpose**

Provides geographic reference information.

**Description**

Maps ZIP code prefixes to latitude, longitude, city, and state. Primarily supports geographic reporting and mapping.

---

## Product Category Translation

**Business Purpose**

Provides standardized English product category names.

**Description**

Maps Portuguese category names to their English equivalents for reporting and dashboard presentation.

---

# Business Process Coverage

| Business Process | Supporting Dataset(s) |
|------------------|-----------------------|
| Customer Management | Customers |
| Order Management | Orders |
| Sales Transactions | Order Items |
| Product Management | Products |
| Seller Management | Sellers |
| Payment Processing | Payments |
| Customer Satisfaction | Reviews |
| Geographic Analysis | Geolocation |
| Product Standardization | Product Category Translation |

---

# Notes

- The **Orders** dataset is expected to serve as the central transactional table within the analytical model.
- **Order Items** represents the lowest level of transactional detail and is expected to function as the primary sales fact table.
- **Customers**, **Products**, **Sellers**, and **Geolocation** provide descriptive attributes used during analysis.
- **Product Category Translation** functions as a lookup table for standardized reporting.
- Primary keys and foreign keys documented here represent logical business relationships identified during the Data Understanding phase and will be formally validated during the Relationship Analysis phase.