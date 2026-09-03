from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FEATURE_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "features"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "business_metrics"
)

OUTPUT_FILE = (
    REPORT_DIR
    / "reconciliation_checks.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

orders = pd.read_csv(
    FEATURE_DIR / "orders_features.csv"
)

order_items = pd.read_csv(
    FEATURE_DIR / "order_items_features.csv"
)

category = pd.read_csv(
    REPORT_DIR / "category_metrics.csv"
)

regional = pd.read_csv(
    REPORT_DIR / "regional_metrics.csv"
)

product = pd.read_csv(
    REPORT_DIR / "product_metrics.csv"
)


# ============================================================
# RECONCILIATION CHECKS
# ============================================================

checks = []


def add_check(
    check_name,
    left_value,
    right_value,
    tolerance=1e-6,
):
    difference = abs(
        left_value - right_value
    )

    status = (
        "PASS"
        if difference <= tolerance
        else "FAIL"
    )

    checks.append(
        {
            "check_name": check_name,
            "left_value": left_value,
            "right_value": right_value,
            "absolute_difference": difference,
            "status": status,
        }
    )


# ============================================================
# 1. REVENUE RECONCILIATION
#
# SUM(order_revenue) = SUM(item_revenue)
# ============================================================

order_revenue_total = orders[
    "order_revenue"
].sum()

item_revenue_total = order_items[
    "item_revenue"
].sum()

add_check(
    "Revenue: Order Revenue = Item Revenue",
    order_revenue_total,
    item_revenue_total,
)


# ============================================================
# 2. CUSTOMER REVENUE CONTROL
#
# Do NOT sum customer lifetime revenue as another
# Total Revenue measure.
#
# Total Revenue remains the order-grain revenue measure.
# ============================================================

customer_revenue_total = orders[
    "order_revenue"
].sum()

add_check(
    "Customer Revenue: Uses Order Revenue as Total Revenue",
    customer_revenue_total,
    order_revenue_total,
)


# ============================================================
# 3. CATEGORY REVENUE RECONCILIATION
#
# SUM(category_revenue) = Total Revenue
# ============================================================

category_revenue_total = category[
    "category_revenue"
].sum()

add_check(
    "Category Revenue = Total Revenue",
    category_revenue_total,
    order_revenue_total,
)


# ============================================================
# 4. REGIONAL REVENUE RECONCILIATION
#
# SUM(revenue) = Total Revenue
# ============================================================

regional_revenue_total = regional[
    "revenue"
].sum()

add_check(
    "Regional Revenue = Total Revenue",
    regional_revenue_total,
    order_revenue_total,
)


# ============================================================
# 5. PRODUCT REVENUE RECONCILIATION
#
# SUM(product_revenue) = Total Revenue
# ============================================================

product_revenue_total = product[
    "product_revenue"
].sum()

add_check(
    "Product Revenue = Total Revenue",
    product_revenue_total,
    order_revenue_total,
)


# ============================================================
# CREATE RESULT TABLE
# ============================================================

result = pd.DataFrame(
    checks
)


# ============================================================
# SAVE REPORT
# ============================================================

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

result.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print("=" * 70)
print("STEP 9 — RECONCILIATION CHECKS")
print("=" * 70)
print()

print(
    result.to_string(
        index=False
    )
)

print()

passed = (
    result["status"] == "PASS"
).sum()

total = len(result)

print(
    f"Checks Passed: {passed}/{total}"
)

print()

# ============================================================
# FINAL VALIDATION
# ============================================================

if (
    result["status"] != "PASS"
).any():

    print(
        "RECONCILIATION FAILED."
    )

    raise ValueError(
        "One or more reconciliation checks FAILED."
    )

print(
    "All reconciliation checks PASSED."
)

print()

print(
    f"Report: {OUTPUT_FILE}"
)