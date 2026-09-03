from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "reports"
    / "business_metrics"
    / "kpi_results.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "reports"
    / "business_metrics"
    / "final_kpi_results.csv"
)


# ============================================================
# KPI METADATA
# ============================================================

KPI_METADATA = {

    "Total Revenue": {
        "business_area": "Sales",
        "unit": "currency",
        "source_dataset": "orders_features",
    },

    "Total Orders": {
        "business_area": "Sales",
        "unit": "count",
        "source_dataset": "orders_features",
    },

    "Average Order Value": {
        "business_area": "Sales",
        "unit": "currency/order",
        "source_dataset": "orders_features",
    },

    "Monthly Revenue Growth": {
        "business_area": "Sales",
        "unit": "percent",
        "source_dataset": "monthly_features",
    },

    "Total Customers": {
        "business_area": "Customer",
        "unit": "count",
        "source_dataset": "customer_features",
    },

    "Repeat Customer Rate": {
        "business_area": "Customer",
        "unit": "percent",
        "source_dataset": "customer_features",
    },

    "On-Time Delivery Rate": {
        "business_area": "Delivery",
        "unit": "percent",
        "source_dataset": "orders_features",
    },

    "Average Delivery Time": {
        "business_area": "Delivery",
        "unit": "days",
        "source_dataset": "orders_features",
    },

    "Average Review Score": {
        "business_area": "Customer Experience",
        "unit": "score",
        "source_dataset": "orders_features",
    },

    "Total Order Value": {
        "business_area": "Sales",
        "unit": "currency",
        "source_dataset": "orders_features",
    },

    "Monthly Revenue": {
        "business_area": "Sales",
        "unit": "currency/month",
        "source_dataset": "monthly_features",
    },

    "Average Items per Order": {
        "business_area": "Sales",
        "unit": "items/order",
        "source_dataset": "orders_features",
    },

    "Customer Lifetime Revenue": {
        "business_area": "Customer",
        "unit": "currency/customer",
        "source_dataset": "customer_features",
    },

    "Average Customer Order Value": {
        "business_area": "Customer",
        "unit": "currency/order",
        "source_dataset": "customer_features",
    },

    "Category Revenue": {
        "business_area": "Product",
        "unit": "currency",
        "source_dataset": "order_items_features",
    },

    "Category Revenue Share": {
        "business_area": "Product",
        "unit": "percent",
        "source_dataset": "order_items_features",
    },

    "Product Revenue": {
        "business_area": "Product",
        "unit": "currency",
        "source_dataset": "order_items_features",
    },

    "Seller Revenue": {
        "business_area": "Seller",
        "unit": "currency",
        "source_dataset": "order_items_features",
    },

    "Seller Order Count": {
        "business_area": "Seller",
        "unit": "count",
        "source_dataset": "order_items_features",
    },

    "Revenue by Customer State": {
        "business_area": "Regional",
        "unit": "currency",
        "source_dataset": "orders_features",
    },

    "Total Payment Value": {
        "business_area": "Payment",
        "unit": "currency",
        "source_dataset": "orders_features",
    },

    "Payment Method Share": {
        "business_area": "Payment",
        "unit": "percent",
        "source_dataset": "orders_features",
    },

    "Average Payment Installments": {
        "business_area": "Payment",
        "unit": "installments",
        "source_dataset": "orders_features",
    },

    "Average Processing Time": {
        "business_area": "Delivery",
        "unit": "days",
        "source_dataset": "orders_features",
    },

    "Late Delivery Rate": {
        "business_area": "Delivery",
        "unit": "percent",
        "source_dataset": "orders_features",
    },

    "Average Delivery Difference": {
        "business_area": "Delivery",
        "unit": "days",
        "source_dataset": "orders_features",
    },

    "Total Freight Value": {
        "business_area": "Shipping",
        "unit": "currency",
        "source_dataset": "order_items_features",
    },

    "Low Satisfaction Rate": {
        "business_area": "Customer Experience",
        "unit": "percent",
        "source_dataset": "orders_features",
    },

    "High Satisfaction Rate": {
        "business_area": "Customer Experience",
        "unit": "percent",
        "source_dataset": "orders_features",
    },

    "Rolling 3-Month Revenue": {
        "business_area": "Sales",
        "unit": "currency",
        "source_dataset": "monthly_features",
    },

    "Multi-Payment Order Rate": {
        "business_area": "Payment",
        "unit": "percent",
        "source_dataset": "orders_features",
    },

    "Freight-to-Price Ratio": {
        "business_area": "Shipping",
        "unit": "ratio",
        "source_dataset": "order_items_features",
    },
}


# ============================================================
# MAIN
# ============================================================

def main():

    print("Loading existing KPI results...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Input KPI rows: {len(df)}")

    expected_columns = {
        "kpi_name",
        "kpi_value",
        "kpi_hierarchy",
    }

    missing = expected_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    missing_metadata = [
        kpi
        for kpi in df["kpi_name"]
        if kpi not in KPI_METADATA
    ]

    if missing_metadata:
        raise ValueError(
            f"Missing KPI metadata for: {missing_metadata}"
        )

    # --------------------------------------------------------
    # Rename existing columns
    # --------------------------------------------------------

    df = df.rename(
        columns={
            "kpi_value": "value",
            "kpi_hierarchy": "hierarchy",
        }
    )

    # --------------------------------------------------------
    # Add metadata
    # --------------------------------------------------------

    df["business_area"] = df["kpi_name"].map(
        lambda x: KPI_METADATA[x]["business_area"]
    )

    df["unit"] = df["kpi_name"].map(
        lambda x: KPI_METADATA[x]["unit"]
    )

    df["source_dataset"] = df["kpi_name"].map(
        lambda x: KPI_METADATA[x]["source_dataset"]
    )

    df["calculation_tool"] = "Python/Pandas"

    df["calculation_status"] = "PASS"

    # --------------------------------------------------------
    # Final column order
    # --------------------------------------------------------

    df = df[
        [
            "kpi_name",
            "business_area",
            "hierarchy",
            "value",
            "unit",
            "source_dataset",
            "calculation_tool",
            "calculation_status",
        ]
    ]

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if len(df) != 32:
        raise ValueError(
            f"Expected 32 KPIs, found {len(df)}"
        )

    if df["kpi_name"].duplicated().any():
        raise ValueError(
            "Duplicate KPI names detected."
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("Final KPI Results created successfully.")
    print(f"Rows: {len(df)}")
    print(f"Output: {OUTPUT_FILE}")
    print()
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()