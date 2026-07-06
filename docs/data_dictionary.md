# Business Data Dictionary

## Document Information

| Item | Value |
|------|-------|
| Project | Retail Sales Performance Analytics |
| Phase | Phase 2 — Data Understanding |
| Document | Business Data Dictionary |
| Version | 1.0 |

---

# Purpose

This document defines the key business fields used throughout the Retail Sales Performance Analytics project.

Only business-relevant columns are documented. Technical fields with no analytical significance are intentionally omitted.

---

# Business Data Dictionary

| Column Name | Table | Data Type | Nullable | Business Meaning | Business Usage | Example Value | Notes |
|-------------|-------|-----------|----------|------------------|----------------|---------------|-------|
| customer_id | Customers | Text | No | Unique identifier assigned to each customer record | Join Customers with Orders | `06b8999e...` | Foreign key in Orders |
| customer_unique_id | Customers | Text | No | Identifies the same customer across multiple purchases | Repeat customer analysis | `861eff47...` | One customer may have multiple customer_ids |
| customer_city | Customers | Text | No | Customer city | Geographic reporting | `sao paulo` | |
| customer_state | Customers | Text | No | Customer state | State-level analysis | `SP` | |
| order_id | Orders | Text | No | Unique order identifier | Primary business transaction | `e481f51c...` | Primary key |
| order_status | Orders | Text | No | Current order status | KPI filtering | `delivered` | Important for sales calculations |
| order_purchase_timestamp | Orders | Datetime* | No | Date and time when the customer placed the order | Time-series analysis | `2018-02-13 21:18:39` | Loaded as object during exploration |
| order_approved_at | Orders | Datetime* | Yes | Date and time payment/order approval occurred | Order processing analysis | `2018-02-13 22:20:29` | |
| order_delivered_customer_date | Orders | Datetime* | Yes | Date delivered to customer | Delivery performance | `2018-02-16 18:17:02` | |
| order_estimated_delivery_date | Orders | Datetime* | No | Estimated delivery date | Delivery SLA analysis | `2018-02-26` | |
| product_id | Products | Text | No | Unique product identifier | Product analysis | `1e9e8ef...` | Primary key |
| product_category_name | Products | Text | Yes | Product category (Portuguese) | Category analysis | `perfumaria` | Requires translation |
| product_weight_g | Products | Numeric | Yes | Product weight | Logistics analysis | `225` | grams |
| product_length_cm | Products | Numeric | Yes | Product length | Shipping analysis | `16` | centimeters |
| product_height_cm | Products | Numeric | Yes | Product height | Shipping analysis | `10` | centimeters |
| product_width_cm | Products | Numeric | Yes | Product width | Shipping analysis | `14` | centimeters |
| order_item_id | Order Items | Integer | No | Item sequence within an order | Composite transaction identifier | `1` | Used with order_id |
| seller_id | Order Items | Text | No | Seller fulfilling the order | Seller performance | `48436d...` | Foreign key |
| price | Order Items | Decimal | No | Product selling price | Revenue calculations | `58.90` | Excludes freight |
| freight_value | Order Items | Decimal | No | Shipping charge | Freight analysis | `13.29` | Separate from product price |
| shipping_limit_date | Order Items | Datetime* | No | Shipping deadline | Logistics analysis | `2017-09-19 09:45:35` | |
| payment_type | Payments | Text | No | Payment method used | Payment analysis | `credit_card` | |
| payment_installments | Payments | Integer | No | Number of installments | Installment analysis | `8` | |
| payment_value | Payments | Decimal | No | Amount paid | Revenue validation | `99.33` | Requires reconciliation |
| review_score | Reviews | Integer | No | Customer satisfaction rating | Satisfaction KPIs | `5` | Scale of 1–5 |
| review_creation_date | Reviews | Datetime* | No | Review submission date | Review trend analysis | `2018-01-18` | |
| seller_city | Sellers | Text | No | Seller city | Geographic analysis | `campinas` | |
| seller_state | Sellers | Text | No | Seller state | Seller distribution | `SP` | |
| geolocation_zip_code_prefix | Geolocation | Integer | No | ZIP code prefix | Geographic mapping | `1037` | |
| geolocation_lat | Geolocation | Decimal | No | Latitude | Mapping | `-23.545621` | |
| geolocation_lng | Geolocation | Decimal | No | Longitude | Mapping | `-46.639292` | |
| product_category_name | Category Translation | Text | No | Portuguese category name | Join with Products | `beleza_saude` | Lookup key |
| product_category_name_english | Category Translation | Text | No | English category name | Reporting | `health_beauty` | Dashboard-friendly |

---

# Notes

- Datetime fields were loaded as object data types during the Data Understanding phase and will be converted during Data Preparation.
- Nullable values indicate that missing records were observed during dataset exploration.
- Business meanings reflect the expected analytical use of each field and may be refined during later project phases.
- Only business-relevant columns are documented. Technical attributes not required for analysis are intentionally excluded.