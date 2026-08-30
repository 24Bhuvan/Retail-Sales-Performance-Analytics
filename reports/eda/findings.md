# EDA Findings Report — Phase 10 Exploratory Data Analysis

**Source notebook:** `04_eda.ipynb`
**Input layer:** `data/processed/*.csv` (8 Phase 9 processed datasets), cross-validated against PostgreSQL analytical outputs and Excel sanity checks
**Analysis period covered by the data:** 2016-09-04 to 2018-10-17
**Currency note:** The notebook's main analysis (Sections 4–17) deliberately reports figures in **monetary units** because the project documentation does not state a currency. The dataset structure (states, cities, "boleto" as a payment type) is consistent with the Brazilian Olist e-commerce dataset, and the notebook's own auto-generated chart/export script labels values as R$. This report follows the notebook's own convention and uses **monetary units (mu)**; treat these as R$ (Brazilian Real) if that has been confirmed elsewhere in the project.

---

## 1. Executive EDA Summary

The processed dataset contains **99,441 orders**, **112,650 order items**, **95,420–96,096 unique customers** (figure depends on population used, see Section 5), **3,095 sellers**, **32,951 products** across **72 translated categories**, and **99,224 review records**, spanning **2016‑09‑04 to 2018‑10‑17**. Both ends of the period are partial (2016 begins in September; 2018 is truncated after mid‑October), so year-level comparisons must account for incomplete coverage.

Headline observations:

- **Total item-level sales:** mu 13,591,643.70 across 98,666 orders with at least one item record (AOV = mu 137.75).
- **Total payment value:** mu 16,008,872.12 — higher than item sales by roughly the amount collected in freight, which is a sensible reconciliation (see Section 8).
- Sales grew substantially from late 2016 through late 2017, then plateaued at a high level through mid‑2018.
- Category-level revenue is **concentrated** (18 of 72 categories ≈ 81% of revenue), while product-level revenue is **diffuse** (top 20 of 32,951 products ≈ 5.4% of revenue) — a "hit categories, long‑tail products" structure.
- The customer base is overwhelmingly **one‑time buyers** (~97%); repeat purchase rate is low (~3%).
- Delivery performance is generally strong (89% of orders arrive early, ~11 days ahead of estimate on average) but a **late-delivery tail (~7.9%)** is associated with materially lower review scores.
- Review scores skew positive (average 4.09/5) but are **polarized**: 57.8% five‑star vs. 11.5% one‑star, with fewer mid‑range scores.
- Independent PostgreSQL cross‑validation passed with **zero difference** for product-level and payment-level revenue; a handful of validation checks (monthly SQL comparison, several QA checklist items) were not automatically confirmed and remain manual‑review items (see Section 13).
- No profit, margin, or cost data exists in the processed datasets; all figures below are gross sales/revenue, not profitability.

---

## 2. Sales & Orders

**Population used:** order-level sales metrics are built from `order_items`, so they cover the **98,666 orders that have at least one item record** (775 of the 99,441 total orders have no item record and are excluded — see Section 13).

| Metric | Value |
|---|---|
| Total sales | mu 13,591,643.70 |
| Total orders (item-backed) | 98,666 |
| Total order items | 112,650 |
| Average Order Value (AOV) | mu 137.75 |
| Median order value | mu 86.90 |
| Min / Max order value | mu 0.85 / mu 13,440.00 |
| Average item price | mu 120.65 (median mu 74.99, max mu 6,735.00) |
| Average freight value | mu 19.99 (median mu 16.26, max mu 409.68) |
| Average items per order | 1.14 (max 21) |

**Order status mix** (all 99,441 orders): 97.02% delivered (96,478), 1.11% shipped, 0.63% canceled, 0.61% unavailable, 0.32% invoiced, 0.30% processing, and negligible created/approved counts.

**Distribution shape:** order value, item price, and freight value are all strongly right‑skewed (long tails of high‑value orders/items), consistent with a retail catalog dominated by low‑to‑mid priced items with a minority of high‑value outliers. Orders‑per‑day is unimodal with a clear ramp‑up as the business scaled (see Section 3).

**IQR-based statistical outliers** (not automatically treated as errors):

| Metric | Upper bound | Flagged count |
|---|---|---|
| Order value | mu 305.90 | 7,913 |
| Item price | mu 277.40 | 8,427 |
| Freight value | mu 33.26 | 11,613 |
| Order‑item count | > 1 item | 9,803 |

The single highest-value order (mu 13,440.00, 8 items, delivered 2017‑09‑29) and the highest single item price (mu 6,735.00, delivered 2017‑02‑12) are both legitimate `delivered` transactions, not obviously erroneous. The order with the most items (21 items, order `8272b63d…`) totals only mu 31.80, i.e., many very cheap items bundled into one order.

---

## 3. Time & Seasonality

**Trend (Section 5):**

| Year | Sales | Coverage |
|---|---|---|
| 2016 | mu 49,785.92 | Partial (Sep 4 – Dec 31 only) |
| 2017 | mu 6,155,806.98 | Full year |
| 2018 | mu 7,386,050.80 | Partial (through Oct 17) |

Monthly sales rose steadily from mu 49,507.66 (Oct‑2016) to a **peak of mu 1,010,271.37 in November 2017** (7,544 orders) — the single highest month in the dataset, consistent with a seasonal shopping event. After that peak, monthly sales plateaued in the mu 850k–1M range through mid‑2018 before the data collection window ends (Sep‑2018 shows only mu 145.00 / 16 orders and Oct‑2018 essentially nothing — this reflects **data‑extraction cutoff, not a real demand collapse**, and both months should be excluded from trend conclusions).

**Seasonality (Section 6)**, aggregated by comparable calendar period:

- **Month‑of‑year:** highest sales in May (mu 1,502,588.82, 10,573 orders); lowest in September (mu 624,814.05, 4,305 orders). Note September/October figures are confounded by the partial‑year coverage at both ends of the dataset, so this specific ranking should be treated cautiously rather than as confirmed seasonality.
- **Quarter:** Q2 highest (mu 4,157,326.71, 29,215 orders), Q4 lowest (mu 2,467,923.53, 17,952 orders) — again partly a coverage artifact since Q4 includes the truncated 2018 tail.
- **Weekday:** Monday is the strongest day (mu 2,230,812.51, 16,068 orders); Saturday is the weakest (mu 1,504,018.36, 10,813 orders).
- **Weekday vs. weekend:** weekdays account for mu 10,498,346.45 across 75,965 orders (~77% of orders) vs. mu 3,093,297.25 across 22,701 orders on weekends — a clear weekday‑dominant buying pattern, plausibly linked to work‑hours browsing/purchasing behavior.

---

## 4. Products & Categories

**Categories (72 valid, English‑translated; 1,627 order items — 1.44% — are missing/untranslated and grouped as "Unknown/Untranslated"):**

| Rank | Category | Sales | Revenue share |
|---|---|---|---|
| 1 | health_beauty | mu 1,258,681.34 | 9.26% |
| 2 | watches_gifts | mu 1,205,005.68 | 8.87% |
| 3 | bed_bath_table | mu 1,036,988.68 | 7.63% |
| 4 | sports_leisure | mu 988,048.97 | 7.27% |
| 5 | computers_accessories | mu 911,954.32 | 6.71% |

The bottom of the ranking (e.g., `security_and_services`, mu 283.29 from 2 orders) is negligible. **18 of 72 categories (25%) account for ~81.2% of total category revenue** — a Pareto-like concentration at the category level.

**Products (32,951 total, all with at least one recorded sale):**

- Top 10 products account for only **3.32%** of total revenue; top 20 account for **5.38%**.
- **8,536 products (26% of the catalog)** are needed to reach ~80% of cumulative revenue — a much longer tail than the category-level concentration, i.e., no small set of SKUs dominates sales.
- Top product: `bb50f2e2…`, mu 63,885.00 across 187 orders / 195 items.
- The product-level SQL cross-validation matched exactly for the top 20 products (difference = 0.00 in all cases).

**Interpretation:** revenue concentration exists at the category level but not at the individual product level — the business is not dependent on a handful of hero SKUs, but certain product categories are structurally more important than others.

---

## 5. Customers

Customer metrics use `customer_unique_id` as required (not `customer_id`).

| Population | Unique customers | Repeat customers | Notes |
|---|---|---|---|
| Item-backed orders only (Section 9) | 95,420 | 2,913 | Base used for AOV-by-segment table below |
| Full orders table (Section 10/17 validation) | 96,096 | 2,997 | Includes the 775 orders without item records |

This is a genuine **grain difference**, not an error — see Section 13.

Using the item-backed population:

| Segment | Customers | Orders | Revenue | AOV | Share of customers |
|---|---|---|---|---|---|
| One-time | 92,507 | 92,507 | mu 12,828,351.84 | mu 138.67 | 96.95% |
| Repeat | 2,913 | 6,159 | mu 763,291.86 | mu 123.93 | 3.05% |

**Key finding:** repeat customers make up only ~3% of the customer base and contribute ~5.6% of revenue — a modest but real recurring-revenue segment. Notably, **repeat customers have a lower average order value (mu 123.93) than one-time customers (mu 138.67)**, so repeat purchasing is not associated with higher per-order spend in this dataset.

The single highest-revenue customer (mu 13,440.00 from one order) is the same customer behind the top order-value anomaly in Section 2. The customer with the most orders placed **17 orders** (IQR/z-score flags this as an extreme outlier for order frequency).

---

## 6. Sellers

The notebook does not include a fully dedicated seller EDA section with its own required charts; seller figures below are drawn from the Geographic Analysis (Section 10) and the independent seller-metrics validation (Section 17.7), which are the only places seller-level aggregates are computed. Treat this section as secondary/derived rather than as thoroughly charted as Sections 2–5.

- **3,095 sellers** total.
- Seller geography is heavily concentrated: **São Paulo (SP) alone accounts for 1,849 sellers (~59.7%)**; the top 5 states (SP, PR, MG, SC, RJ) account for **2,803 sellers (~90.6%)**.
- Several states have 0 or 1 seller despite having customers (e.g., AL and TO show 0 sellers), indicating fulfillment supply is far more geographically concentrated than customer demand.
- Top seller by item sales: `4869f7a5…`, mu 229,472.63 across 1,132 orders / 1,156 items — followed by nine other sellers each exceeding mu 135,000 in sales.

---

## 7. Geography

Geolocation is treated as reference/enrichment data, consistent with the project's data model. 27 states are represented.

| Rank | State | Customers | Orders | Sales | Sellers |
|---|---|---|---|---|---|
| 1 | SP | 40,285 | 41,746 | mu 5,202,955.05 | 1,849 |
| 2 | RJ | 12,380 | 12,852 | mu 1,824,092.67 | 171 |
| 3 | MG | 11,257 | 11,635 | mu 1,585,308.03 | 244 |
| — | RR (smallest) | 45 | 46 | mu 7,829.43 | 0 |

The **top 3 states (SP, RJ, MG) account for roughly 63% of total sales**, and SP alone accounts for ~38%. This mirrors the seller concentration in Section 6: the largest demand market (SP) is also the largest supply market, and it also has the fastest delivery times (Section 10) — consistent with shorter shipping distances driving faster fulfillment.

---

## 8. Payments

- **103,886 payment transactions** across 99,440 of the 99,441 orders (one order has no payment record).
- **5 payment methods**; total payment value **mu 16,008,872.12** (average mu 154.10, median mu 100.00, max mu 13,664.08, min mu 0.00 — the mu 0.00 minimum is a data-quality edge case, see Section 13).
- Average installments: 2.85 (median 1, max 24).

| Payment type | Orders | Payment value | Revenue share |
|---|---|---|---|
| credit_card | 76,505 | mu 12,542,084.19 | 78.34% |
| boleto | 19,784 | mu 2,869,361.27 | 17.92% |
| voucher | 3,866 | mu 379,436.87 | 2.37% |
| debit_card | 1,528 | mu 217,989.79 | 1.36% |
| not_defined | 3 | mu 0.00 | 0.00% |

Single-installment payments are the most common installment plan (49,060 orders, mu 5,907,233.36), though a meaningful share of customers use extended installment plans (up to 24).

**Cross-validation:** the SQL comparison for payment-method revenue matched exactly for every payment type (difference = 0.00, `value_match = True` in all rows).

**Reconciliation insight:** total payment value (mu 16.01M) exceeds total item sales (mu 13.59M) by about mu 2.42M. Total freight collected is approximately mu 19.99 × 112,650 items ≈ mu 2.25M — close to, though not exactly matching, that gap. This is a sensible (not exact) reconciliation suggesting payment values largely represent price + freight collected per order, with a modest unexplained residual worth further investigation outside this EDA phase.

---

## 9. Reviews

- **99,224 review records** covering 98,673 of the 98,666+ orders (near‑complete review coverage for the item-backed order population).
- **Average review score: 4.09 / 5** (median 5.0).
- Distribution is **polarized**, not evenly spread:

| Score | Reviews | Share |
|---|---|---|
| 5 | 57,328 | 57.78% |
| 4 | 19,142 | 19.29% |
| 3 | 8,179 | 8.24% |
| 2 | 3,151 | 3.18% |
| 1 | 11,424 | 11.51% |

Most customers are very satisfied, but a substantial ~11.5% minority are very dissatisfied, with comparatively few "middling" (2–3 star) reviews.

**By category:** best-reviewed categories include `cds_dvds_musicals` (4.64, small sample n=14) and `books_general_interest` (4.45, n=549, a reasonably sized sample). Worst-reviewed categories with meaningful sample sizes include `office_furniture` (3.49, n=1,687) and the `Unknown/Untranslated` bucket (3.16, n=2,381).

**By payment method:** debit_card has the highest average score (4.17); differences across the main methods (credit_card 4.09, boleto 4.09, voucher 4.00) are small.

**Review score vs. delivery delay (relationship to Section 10):** average delay-vs-estimate becomes steadily less negative (i.e., deliveries arrive closer to, or past, the estimated date) as review score drops:

| Review score | Avg. delay vs. estimate (days) |
|---|---|
| 5 | −12.69 |
| 4 | −11.68 |
| 3 | −10.07 |
| 2 | −7.93 |
| 1 | −3.36 |

This is a clear, data-supported **association** between how close a delivery lands to (or past) its estimate and the review score given — consistent with what the delivery-duration-vs-review-score scatterplot shows visually (a longer tail of 100–200+ day deliveries concentrated among 1–2 star reviews). Per the notebook's stated rule, this is reported as a relationship, **not a causal claim**.

---

## 10. Delivery

Based on 96,453 orders with a valid delivered timestamp (of 99,441 total; 99,281 have an approval timestamp, 97,492 have a carrier handoff timestamp).

| Metric | Value |
|---|---|
| Avg. approval time | 10.42 hours (median 0.34 hours) |
| Avg. carrier handoff time | 68.62 hours (median 44.44 hours) |
| Avg. delivery duration (handoff → customer) | 9.34 days (median 7.10) |
| Avg. total delivery time (purchase → customer) | 12.56 days (median 10.22) |
| Avg. variance vs. estimate | −11.18 days (median −11.94) |

**Early / Late split:** 88,626 orders (89.1%) arrive early, 7,827 (7.9%) arrive late, and 2,988 (3.0%) could not be classified due to missing/invalid timestamps. "On-time" (exact match to the estimate) is 0 by construction of this classification — the estimate‑vs‑actual comparison is continuous, not a discrete on‑time bucket.

**By state:** SP has both the fastest average delivery (5.60 days) and highest order volume; RR is the slowest (25.64 days, but a very small volume of 46 orders). AL has the highest late-delivery rate (23.0%) among larger-volume states.

**By category:** delivery speed varies from ~3.6 days (`artes_e_artesanato`) to ~12.0 days (`casa_conforto_2`), suggesting some categories (e.g., furniture/large items) take structurally longer to fulfill.

Approval and total delivery durations show no invalid (negative) values, but **1,193 carrier-handoff records are flagged as invalid durations** — a data-quality item to investigate (see Section 13).

---

## 11. Anomalies

Anomalies are **identified for investigation, not automatically removed**, consistent with the notebook's stated policy. Using IQR, percentile, Z‑score, and domain-threshold methods:

| Anomaly type | Method | Count |
|---|---|---|
| Transaction / payment value | IQR + Z-score | 7,981 |
| Extreme order value | IQR | 7,775 |
| Extreme item price | IQR | 8,427 |
| Extreme freight value | IQR | 12,134 |
| Extreme item count | IQR | 9,803 |
| Extremely long delivery | IQR | 5,065 |
| Delivery after estimate | Domain threshold | 7,827 |
| Unusual cancellation period | Monthly IQR | 2 |
| Extreme customer order frequency | IQR | 2,997 |
| Extreme customer revenue | IQR | 7,643 |

Notable individual anomalies:

- **Highest single order:** mu 13,440.00–13,664.08 (figure varies slightly by field used — see Section 13), 8 items, `delivered`, 2017‑09‑29.
- **Highest single item price:** mu 6,735.00, freight mu 194.31.
- **Highest single freight charge:** mu 409.68 on a mu 979.00 item — and separately, the freight‑vs‑price scatterplot shows one striking outlier of roughly mu 1,800 in freight on a comparatively low‑priced item (~mu 150–200), which stands out visually from the rest of the distribution and is a strong candidate for manual review.
- **Most orders by a single customer:** 17 orders (customer `8d50f5ea…`).
- **Delivery-after-estimate count (7,827) matches the "Late" delivery count from Section 10 exactly** — a useful internal consistency check.

The "Extreme customer order frequency" count (2,997) is close to the total repeat-customer count (2,913–2,997) reported in Section 5, which suggests the IQR bound for this heavily right‑skewed count variable is very tight — effectively flagging almost any customer with more than one order. This is a **method sensitivity note**, not evidence that ~3,000 customers behave unusually; see Section 13.

Only **2 calendar months** show statistically unusual cancellation volume, indicating cancellations are not a systemic, ongoing issue but may reflect isolated operational events worth a targeted follow-up.

---

## 12. Key Business Findings

1. **Sustained growth, then plateau.** Monthly sales grew from tens of thousands of monetary units in late 2016 to a peak of mu 1.01M in November 2017, then held in the mu 850k–1M range through mid‑2018 — the business scaled significantly over roughly two years.
2. **November stands out.** The single highest sales month (Nov 2017) is consistent with a seasonal shopping event; this is worth confirming against known regional retail calendars.
3. **Weekday-dominant demand.** ~77% of orders occur Monday–Friday, with Monday the single strongest day — useful for staffing, promotions, and fulfillment planning.
4. **Category concentration vs. product diffusion.** Revenue is concentrated in a subset of categories (18 of 72 ≈ 81% of revenue) but spread thinly across products (top 20 of ~33,000 products ≈ 5.4% of revenue) — no single SKU drives the business, but category-level strategy (assortment, marketing) matters more than individual product bets.
5. **Low repeat-purchase rate.** Only ~3% of customers are repeat buyers, and they don't spend more per order than one-time customers — repeat customers currently represent an under-leveraged growth lever rather than a proven high-value segment.
6. **Supply and demand are geographically aligned but imbalanced.** São Paulo dominates both customer volume (~42%) and seller volume (~60%), and also has the fastest delivery times — proximity between sellers and customers appears to support faster fulfillment.
7. **Credit card is the primary payment rail.** 78% of payment value flows through credit cards, with most transactions in a single installment — but a meaningful share of customers rely on extended installment plans, indicating price sensitivity for larger purchases.
8. **Delivery reliability is generally strong but not universal.** 89% of orders arrive ahead of the estimated date (11 days early on average), yet the 7.9% that arrive late show a clear association with materially lower review scores — reducing the late-delivery tail is a plausible lever for improving satisfaction.
9. **Reviews are polarized, not just positive.** A high average score (4.09) masks an ~11.5% one-star minority — the underlying causes for this dissatisfied segment (likely including delivery delay, per Section 9) merit dedicated root-cause investigation.
10. **Freight is a material cost component.** Total freight collected (~mu 2.25M) is large relative to item sales (~mu 13.6M, ~16.6%), and closely (though not exactly) reconciles the gap between item sales and total payment value — freight economics are worth a dedicated deep-dive.
11. **A consistent share of records are statistically extreme (7–12%, depending on the metric).** These are candidates for follow-up review (fraud checks, high-value customer service, data-entry verification) rather than automatic exclusion.
12. **Data completeness gaps exist but are small.** 775 orders lack item records, 1 order lacks a payment record, 1,627 items lack a translated category, and 1,193 carrier-handoff timestamps look implausible — none of these are large enough to distort headline figures, but all should be resolved before the data is used for downstream modeling.

---

## 13. Data Limitations

- **Currency is not formally confirmed.** The core analysis reports "monetary units" per project documentation; the dataset's structure strongly suggests Brazilian Real (R$), and the notebook's own auto-export script assumes R$, but this report does not assert a currency beyond what the notebook itself confirms.
- **775 of 99,441 orders (0.78%) have no order-item record** and are excluded from all order-value, AOV, product, category, and customer-revenue calculations. Similarly, 1 order has no payment record.
- **2016 and late-2018 are partial periods.** 2016 coverage begins 2016‑09‑04; 2018 coverage effectively ends by mid‑October (with September/October 2018 showing only 16 and 4 orders respectively, almost certainly a dataset-extraction cutoff). Both periods should be excluded from, or treated cautiously in, any year-over-year or full-calendar-year seasonality conclusion.
- **Minor field-definition inconsistency.** The same order (e.g., `03caa2d0…`) shows a slightly different total (mu 13,440.00 in Section 2's `order_sales`, price-only sum, vs. mu 13,664.08 in Section 11's `sales_amount` field used for anomaly z-scores) — likely due to whether freight is included. The precise definition of `sales_amount` should be confirmed against Phase 9 processing documentation before this figure is used in downstream reporting.
- **Customer counts depend on population.** Unique-customer and repeat-customer counts differ slightly (95,420 / 2,913 vs. 96,096 / 2,997) depending on whether the item-backed order population or the full orders table is used. This is a grain difference, not an error, but the two figures should not be mixed without noting which population is in use.
- **1,627 order items (1.44%) have missing/untranslated product categories**, grouped as "Unknown/Untranslated" in category-level analysis; this bucket appears with a below-average review score (3.16), which may partly reflect the underlying missing-data mechanism rather than genuine dissatisfaction with an identifiable category.
- **Small payment data-quality edge cases:** 3 transactions are typed `not_defined` (mu 0.00 total), and the minimum recorded payment value is mu 0.00 — both warrant investigation before being treated as valid economic transactions.
- **Delivery classification has an "unclassifiable" bucket.** 2,988 orders (3.0%) could not be classified as Early/Late due to missing or invalid timestamps, and 1,193 carrier-handoff durations are flagged as invalid (likely negative or implausible). Delivery statistics in Section 10 are based on the 96,453 orders with valid delivered timestamps.
- **IQR-based anomaly detection is sensitive to skewed count variables.** Fields like order-item count and customer order frequency are heavily right-skewed (most orders have exactly 1 item; most customers place exactly 1 order), so IQR bounds on these fields are very tight and flag a large share of records as "anomalous." These counts should be read as a method artifact requiring judgment, not as confirmed unusual behavior, consistent with the notebook's explicit no-automatic-deletion policy.
- **Relationship analysis (Section 9/11) is primarily qualitative.** The notebook renders scatterplots for price-vs-review, freight-vs-price, delivery-vs-review, installments-vs-payment, photos-vs-review, and description-length-vs-review, and computes a Pearson correlation for freight-vs-price in its chart-export script — but that numeric coefficient was not captured in the retained cell output available for this report, so it is described qualitatively (a general upward association with wide scatter and at least one striking outlier) rather than quoted as an exact figure.
- **SQL cross-validation is incomplete.** Product-level and payment-level revenue matched PostgreSQL outputs exactly (difference = 0.00), but the monthly-sales SQL validation dataframe was empty ("SKIPPED — DATAFRAME EMPTY") and several items on the notebook's own 13-item QA checklist remained "MANUAL CHECK" rather than automatically confirmed (9 of 13 items). Figures not explicitly listed as SQL-matched in this report should be treated as Python-only calculations pending independent confirmation.
- **No seller-specific EDA section exists in the notebook.** Section 6 (Sellers) in this report is derived from the Geographic Analysis and an independent seller-metrics validation step, not from a dedicated, fully charted seller analysis with its own required visuals — it is therefore less thoroughly explored than Sections 2–5.
- **No profit, margin, or cost-basis data is available.** All "sales" and "revenue" figures in this report are gross item price and/or payment value; no conclusions about profitability should be drawn from this EDA.
- **Correlation is not causation.** Wherever this report notes an association (e.g., delivery delay and review score, freight and price), it reflects observed statistical relationship only, per the notebook's explicit analytical rule.
