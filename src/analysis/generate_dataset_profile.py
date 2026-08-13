from pathlib import Path
import pandas as pd

RAW_DATA = Path("data/raw")
OUTPUT = Path("reports/profiling")
OUTPUT.mkdir(parents=True, exist_ok=True)

# Expected primary keys based on Phase 2 Data Understanding
PRIMARY_KEYS = {
    "olist_customers_dataset.csv": ["customer_id"],
    "olist_orders_dataset.csv": ["order_id"],
    "olist_order_items_dataset.csv": ["order_id", "order_item_id"],
    "olist_order_payments_dataset.csv": ["order_id", "payment_sequential"],
    "olist_order_reviews_dataset.csv": ["review_id"],
    "olist_products_dataset.csv": ["product_id"],
    "olist_sellers_dataset.csv": ["seller_id"],
    "product_category_name_translation.csv": ["product_category_name"],
}

# Phase 3 - Step 2: Target numeric columns mapped to their specific datasets
TARGET_NUMERIC_MAPPING = {
    "olist_order_items_dataset.csv": ["price", "freight_value"],
    "olist_order_payments_dataset.csv": ["payment_value", "payment_installments"],
    "olist_order_reviews_dataset.csv": ["review_score"],
    "olist_products_dataset.csv": [
        "product_weight_g",
        "product_photos_qty",
        "product_name_lenght",
        "product_description_lenght",
    ],
    "olist_geolocation_dataset.csv": ["geolocation_lat", "geolocation_lng"],
}

# Phase 3 - Step 3: Target categorical columns mapped to their specific datasets
TARGET_CATEGORICAL_MAPPING = {
    "olist_orders_dataset.csv": ["order_status"],
    "olist_order_payments_dataset.csv": ["payment_type"],
    "olist_order_reviews_dataset.csv": ["review_score"],
    "olist_customers_dataset.csv": ["customer_state"],
    "olist_sellers_dataset.csv": ["seller_state"],
    "olist_products_dataset.csv": ["product_category_name"],
    "product_category_name_translation.csv": [
        "product_category_name",
        "product_category_name_english",
    ],
}

# Phase 3 - Step 4: Target date columns mapped to their specific datasets
TARGET_DATE_MAPPING = {
    "olist_orders_dataset.csv": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "olist_order_reviews_dataset.csv": [
        "review_creation_date",
        "review_answer_timestamp",
    ],
    "olist_order_items_dataset.csv": [
        "shipping_limit_date",
    ],
}

# Phase 3 - Step 7: Columns where a negative value is logically invalid.
# Used only to classify negative-value anomalies; not used to alter any data.
NEGATIVE_INVALID_COLUMNS = {
    "price",
    "freight_value",
    "payment_value",
    "payment_installments",
    "review_score",
    "product_weight_g",
    "product_photos_qty",
    "product_name_lenght",
    "product_description_lenght",
}

csv_files = sorted(RAW_DATA.glob("*.csv"))

# Store loaded DataFrames in a dictionary to avoid re-reading files across steps
dataframes = {}
for file in csv_files:
    dataframes[file.name] = pd.read_csv(file)


def profile_key_columns(df, key_cols):
    """
    Profile a (possibly composite) primary key.

    - Null key rows: rows where any key column is null (evaluated separately).
    - Unique key count: distinct VALID (non-null) key combinations.
    - Duplicate key rows: rows belonging to a valid key combination that
      appears more than once (composite keys evaluated as full combinations).
    - Uniqueness %: unique valid combinations / valid (non-null) rows.
    - Duplicate %: duplicate key rows / total rows.

    Read-only profiling function — does not modify the underlying data.
    """
    total_rows = len(df)
    key_data = df[key_cols].copy()
    null_mask = key_data.isna().any(axis=1)
    null_key_rows = int(null_mask.sum())

    valid_key_data = key_data[~null_mask]
    valid_total = len(valid_key_data)

    if valid_total > 0:
        unique_key_count = valid_key_data.drop_duplicates().shape[0]
        duplicate_key_rows = int(valid_key_data.duplicated(keep=False).sum())
    else:
        unique_key_count = 0
        duplicate_key_rows = 0

    uniqueness_pct = (unique_key_count / valid_total * 100) if valid_total > 0 else 0.0
    duplicate_pct = (duplicate_key_rows / total_rows * 100) if total_rows > 0 else 0.0

    return {
        "total_rows": total_rows,
        "valid_total": valid_total,
        "null_key_rows": null_key_rows,
        "unique_key_count": unique_key_count,
        "duplicate_key_rows": duplicate_key_rows,
        "uniqueness_pct": round(uniqueness_pct, 2),
        "duplicate_pct": round(duplicate_pct, 2),
    }


# ----------------------------------------------------------------------
# Section Collectors for Steps 1 - 3
# ----------------------------------------------------------------------
step1_dataset_overview_sections = []
consolidated_numeric_profile = []
consolidated_categorical_profile = []
detailed_categorical_sections = []

for file_name, df in dataframes.items():
    sec_s1 = []
    sec_s1.append(f"Dataset : {file_name}")
    sec_s1.append("-" * 80)

    # 1. Dataset Overview
    sec_s1.append("Dataset Overview")
    sec_s1.append(f"Rows                : {len(df):,}")
    sec_s1.append(f"Columns             : {df.shape[1]}")
    sec_s1.append(f"Duplicate Rows      : {df.duplicated().sum():,}")
    sec_s1.append(
        f"Memory Usage (MB)   : "
        f"{df.memory_usage(deep=True).sum() / 1024**2:.2f}"
    )
    sec_s1.append("")

    # 2. Column Summary
    sec_s1.append("Column Summary")
    summary = pd.DataFrame({
        "Data Type": df.dtypes.astype(str),
        "Missing": df.isna().sum(),
        "Missing %": (df.isna().mean() * 100).round(2),
        "Unique Values": df.nunique(dropna=True)
    })
    sec_s1.append(summary.to_string())
    sec_s1.append("")

    # 3. Numeric Statistics
    numeric_columns = df.select_dtypes(include="number").columns
    sec_s1.append("Numeric Statistics")
    if len(numeric_columns) == 0:
        sec_s1.append("No numeric columns.")
    else:
        numeric_stats = pd.DataFrame({
            "Min": df[numeric_columns].min(),
            "Max": df[numeric_columns].max(),
            "Mean": df[numeric_columns].mean(),
            "Median": df[numeric_columns].median(),
            "Std": df[numeric_columns].std()
        })
        sec_s1.append(numeric_stats.round(4).to_string())
    sec_s1.append("")

    # Phase 3 — Step 2: Extended Numeric Profile Analysis
    target_cols = TARGET_NUMERIC_MAPPING.get(file_name, [])
    for col in target_cols:
        if col in df.columns:
            series = df[col].dropna()

            count = len(series)
            min_val = series.min()
            q1 = series.quantile(0.25)
            median_val = series.median()
            q3 = series.quantile(0.75)
            max_val = series.max()
            mean_val = series.mean()
            std_val = series.std()
            iqr = q3 - q1
            skewness = series.skew()
            abs_skew = abs(skewness)
            if abs_skew < 0.5:
                shape = "Approximately symmetric"
                direction = "Approximately symmetric"
            elif abs_skew <= 1.0:
                shape = "Moderately skewed"
                direction = "Right-skewed" if skewness > 0 else "Left-skewed"
            else:
                shape = "Highly skewed"
                direction = "Right-skewed" if skewness > 0 else "Left-skewed"
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = series[(series < lower_bound) | (series > upper_bound)]
            outlier_count = len(outliers)
            outlier_pct = (outlier_count / count * 100) if count > 0 else 0.0
            zero_count = (series == 0).sum()
            negative_count = (series < 0).sum()
            dataset_name = file_name.replace("olist_", "").replace("_dataset.csv", "")
            consolidated_numeric_profile.append({
                "Dataset": dataset_name,
                "Column": col,
                "Count": count,
                "Min": round(min_val, 2),
                "Q1": round(q1, 2),
                "Median": round(median_val, 2),
                "Q3": round(q3, 2),
                "Max": round(max_val, 2),
                "Mean": round(mean_val, 2),
                "Std": round(std_val, 2),
                "IQR": round(iqr, 2),
                "Skewness": round(skewness, 2),
                "Shape": shape,
                "Direction": direction,
                "Lower Bound": round(lower_bound, 2),
                "Upper Bound": round(upper_bound, 2),
                "Potential Outliers": outlier_count,
                "Outlier %": round(outlier_pct, 2),
                "Zero Count": zero_count,
                "Negative Count": negative_count
            })

    # Phase 3 — Step 3: Targeted Categorical Distribution Analysis
    target_cat_cols = TARGET_CATEGORICAL_MAPPING.get(file_name, [])
    for col in target_cat_cols:
        if col in df.columns:
            counts = df[col].value_counts(dropna=False)
            total_obs = len(df)
            unique_cat_count = len(counts)
            cat_df = pd.DataFrame({
                "Category": counts.index.astype(str),
                "Frequency": counts.values,
                "Percentage Share": (counts.values / total_obs * 100) if total_obs > 0 else 0.0
            })
            top_category = cat_df.iloc[0]["Category"] if unique_cat_count > 0 else None
            top_frequency = cat_df.iloc[0]["Frequency"] if unique_cat_count > 0 else 0
            top_pct = cat_df.iloc[0]["Percentage Share"] if unique_cat_count > 0 else 0.0
            rare_df = cat_df[cat_df["Percentage Share"] < 1.0]
            rare_cat_count = len(rare_df)
            rare_cat_pct = (rare_cat_count / unique_cat_count * 100) if unique_cat_count > 0 else 0.0
            rare_rows = rare_df["Frequency"].sum()
            rare_rows_pct = (rare_rows / total_obs * 100) if total_obs > 0 else 0.0
            dataset_name = file_name.replace("olist_", "").replace("_dataset.csv", "")
            consolidated_categorical_profile.append({
                "Dataset": dataset_name,
                "Column": col,
                "Unique Categories": unique_cat_count,
                "Top Category": top_category,
                "Top Frequency": top_frequency,
                "Top %": round(top_pct, 2),
                "Rare Categories": rare_cat_count,
                "Rare Category %": round(rare_cat_pct, 2),
                "Rare Rows": rare_rows,
                "Rare Rows %": round(rare_rows_pct, 2)
            })
            full_df = cat_df.copy()
            full_df["Percentage Share"] = full_df["Percentage Share"].round(2)
            top_5_df = cat_df.head(5).copy()
            top_5_df["Percentage Share"] = top_5_df["Percentage Share"].round(2)
            rare_detailed_df = rare_df.copy()
            rare_detailed_df["Percentage Share"] = rare_detailed_df["Percentage Share"].round(2)

            sec = []
            sec.append(f"Dataset : {dataset_name}")
            sec.append(f"Column  : {col}")
            sec.append("")
            sec.append(f"Unique Categories : {unique_cat_count}")
            sec.append("")
            sec.append("Full Category Distribution")
            sec.append(full_df.to_string(index=False))
            sec.append("")
            sec.append("Top Categories (up to 5)")
            sec.append(top_5_df.to_string(index=False))
            sec.append("")
            sec.append("Rare Categories (< 1% Threshold)")
            if rare_cat_count == 0:
                sec.append("No rare categories identified.")
            else:
                sec.append(rare_detailed_df.to_string(index=False))
            sec.append("")
            sec.append("Interpretation:")
            sec.append(
                f"\"{col}\" contains {unique_cat_count} categories. "
                f"The dominant category is '{top_category}', representing {top_pct:.2f}% of observations. "
                f"{rare_cat_count} categories fall below the 1% rare-category threshold (an observation, "
                f"not necessarily an anomaly), representing {rare_rows_pct:.2f}% of overall rows."
            )
            sec.append("-" * 80)

            detailed_categorical_sections.append("\n".join(sec))

    # 4. Categorical Statistics (General)
    categorical_columns = df.select_dtypes(include=["object", "category"]).columns
    sec_s1.append("Categorical Statistics")
    if len(categorical_columns) == 0:
        sec_s1.append("No categorical columns.")
    else:
        categorical_rows = []
        for column in categorical_columns:
            value_counts = df[column].value_counts(dropna=True)
            if len(value_counts) == 0:
                top_value = None
                top_count = 0
                top_percentage = 0.0
            else:
                top_value = value_counts.index[0]
                top_count = value_counts.iloc[0]
                top_percentage = (top_count / value_counts.sum()) * 100
            categorical_rows.append({
                "Column": column,
                "Unique Values": df[column].nunique(dropna=True),
                "Top Value": top_value,
                "Top Count": top_count,
                "Top %": round(top_percentage, 2)
            })
        categorical_stats = pd.DataFrame(categorical_rows)
        sec_s1.append(categorical_stats.to_string(index=False))
    sec_s1.append("")

    # 5. Date Statistics (General)
    sec_s1.append("Date Statistics")
    date_columns = [
        col for col in df.columns
        if "date" in col.lower() or "timestamp" in col.lower()
    ]
    if len(date_columns) == 0:
        sec_s1.append("No date/timestamp columns identified.")
    else:
        date_rows = []
        for column in date_columns:
            parsed_dates = pd.to_datetime(df[column], errors="coerce")
            date_rows.append({
                "Column": column,
                "Minimum Date": parsed_dates.min(),
                "Maximum Date": parsed_dates.max(),
                "Missing": df[column].isna().sum(),
                "Missing %": round(df[column].isna().mean() * 100, 2)
            })
        date_stats = pd.DataFrame(date_rows)
        sec_s1.append(date_stats.to_string(index=False))
    sec_s1.append("")

    # 6. Primary Key Profile
    sec_s1.append("Primary Key Profile")
    primary_key_columns = PRIMARY_KEYS.get(file_name)
    if primary_key_columns is None:
        sec_s1.append("No primary key defined for this dataset.")
    else:
        missing_columns = [c for c in primary_key_columns if c not in df.columns]
        if missing_columns:
            sec_s1.append("Primary key columns missing from dataset: " + ", ".join(missing_columns))
        else:
            key_prof = profile_key_columns(df, primary_key_columns)
            key_name = " + ".join(primary_key_columns)
            sec_s1.append(f"Primary Key                  : {key_name}")
            sec_s1.append(f"Total Rows                   : {key_prof['total_rows']:,}")
            sec_s1.append(f"Valid (Non-Null) Key Rows    : {key_prof['valid_total']:,}")
            sec_s1.append(f"Null Key Rows                : {key_prof['null_key_rows']:,}")
            sec_s1.append(f"Unique Keys (Valid Combos)   : {key_prof['unique_key_count']:,}")
            sec_s1.append(f"Duplicate Key Rows           : {key_prof['duplicate_key_rows']:,}")
            sec_s1.append(f"Uniqueness % (of valid rows) : {key_prof['uniqueness_pct']:.2f}")
            sec_s1.append(f"Duplicate % (of total rows)  : {key_prof['duplicate_pct']:.2f}")
    sec_s1.append("")

    sec_s1.append("=" * 80)
    sec_s1.append("")
    step1_dataset_overview_sections.append("\n".join(sec_s1))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Phase 3 — Step 4: Date Distribution Analysis
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
consolidated_date_profile = []
detailed_date_sections = []
suspicious_sequence_results = []

for file_name, target_dates in TARGET_DATE_MAPPING.items():
    if file_name not in dataframes:
        continue
    df = dataframes[file_name]
    dataset_name = file_name.replace("olist_", "").replace("_dataset.csv", "")
    for col in target_dates:
        if col not in df.columns:
            continue
        dt_series = pd.to_datetime(df[col], errors="coerce")
        total_records = len(df)
        missing_count = dt_series.isna().sum()
        missing_pct = (missing_count / total_records * 100) if total_records > 0 else 0.0
        valid_dates = dt_series.dropna()
        min_date = valid_dates.min() if len(valid_dates) > 0 else None
        max_date = valid_dates.max() if len(valid_dates) > 0 else None

        # Year distribution
        if len(valid_dates) > 0:
            years = valid_dates.dt.year.value_counts().sort_index()
            year_df = pd.DataFrame({
                "Year": years.index.astype(str),
                "Frequency": years.values,
                "Percentage Share": (years.values / len(valid_dates) * 100).round(2)
            })
        else:
            year_df = pd.DataFrame(columns=["Year", "Frequency", "Percentage Share"])

        # Month distribution
        if len(valid_dates) > 0:
            months = valid_dates.dt.month.value_counts().sort_index()
            month_df = pd.DataFrame({
                "Month": months.index.astype(int),
                "Frequency": months.values,
                "Percentage Share": (months.values / len(valid_dates) * 100).round(2)
            })
        else:
            month_df = pd.DataFrame(columns=["Month", "Frequency", "Percentage Share"])

        # Phase 3 — Step 4 (improved): consecutive date gaps + top 5 largest
        if len(valid_dates) > 1:
            sorted_unique_dates = pd.Series(valid_dates.unique()).sort_values().reset_index(drop=True)
            gap_df = pd.DataFrame({
                "Previous Date": sorted_unique_dates.iloc[:-1].values,
                "Current Date": sorted_unique_dates.iloc[1:].values,
            })
            gap_df["Gap"] = pd.to_datetime(gap_df["Current Date"]) - pd.to_datetime(gap_df["Previous Date"])
            gap_df_sorted = gap_df.sort_values("Gap", ascending=False).reset_index(drop=True)
            top_gaps_df = gap_df_sorted.head(5).copy()
            max_gap = gap_df["Gap"].max() if len(gap_df) > 0 else pd.Timedelta(0)
        else:
            top_gaps_df = pd.DataFrame(columns=["Previous Date", "Current Date", "Gap"])
            max_gap = pd.Timedelta(0)

        consolidated_date_profile.append({
            "Dataset": dataset_name,
            "Column": col,
            "Total Records": total_records,
            "Min Date": min_date,
            "Max Date": max_date,
            "Missing Count": missing_count,
            "Missing %": round(missing_pct, 2),
            "Max Gap": str(max_gap)
        })

        sec = []
        sec.append(f"Dataset : {dataset_name}")
        sec.append(f"Column  : {col}")
        sec.append("")
        sec.append(f"Minimum Date : {min_date}")
        sec.append(f"Maximum Date : {max_date}")
        sec.append(f"Total Records: {total_records:,}")
        sec.append(f"Missing Date : {missing_count:,} ({missing_pct:.2f}%)")
        sec.append(f"Maximum Gap  : {max_gap}")
        sec.append("")
        sec.append("Records by Year:")
        sec.append(year_df.to_string(index=False))
        sec.append("")
        sec.append("Records by Month:")
        sec.append(month_df.to_string(index=False))
        sec.append("")
        sec.append("Top 5 Largest Date Gaps (profiling observation only):")
        if top_gaps_df.empty:
            sec.append("Not enough valid date points to compute gaps.")
        else:
            display_gaps_df = top_gaps_df.copy()
            display_gaps_df["Gap"] = display_gaps_df["Gap"].astype(str)
            sec.append(display_gaps_df.to_string(index=False))
        sec.append("-" * 80)
        detailed_date_sections.append("\n".join(sec))

# Suspicious sequence checks for olist_orders_dataset.csv
# NaT comparisons evaluate to False, so rows with missing dates are
# automatically excluded from these checks (never flagged as suspicious).
if "olist_orders_dataset.csv" in dataframes:
    orders_df = dataframes["olist_orders_dataset.csv"].copy()
    total_orders = len(orders_df)
    p_col = pd.to_datetime(orders_df["order_purchase_timestamp"], errors="coerce")
    a_col = pd.to_datetime(orders_df["order_approved_at"], errors="coerce")
    c_col = pd.to_datetime(orders_df["order_delivered_carrier_date"], errors="coerce")
    d_col = pd.to_datetime(orders_df["order_delivered_customer_date"], errors="coerce")
    e_col = pd.to_datetime(orders_df["order_estimated_delivery_date"], errors="coerce")

    sequences = [
        ("approval before purchase", a_col < p_col),
        ("carrier delivery before purchase", c_col < p_col),
        ("customer delivery before purchase", d_col < p_col),
        ("customer delivery before carrier delivery", d_col < c_col),
        ("estimated delivery before purchase", e_col < p_col),
    ]
    for label, mask in sequences:
        cnt = mask.sum()
        pct = (cnt / total_orders * 100) if total_orders > 0 else 0.0
        suspicious_sequence_results.append({
            "Sequence Check": label,
            "Count": cnt,
            "Percentage": round(pct, 4)
        })

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Phase 3 — Step 5: Key and Duplicate Profiling
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
consolidated_key_profile = []
for file_name, key_cols in PRIMARY_KEYS.items():
    if file_name not in dataframes:
        continue
    df = dataframes[file_name]
    dataset_name = file_name.replace("olist_", "").replace("_dataset.csv", "")

    key_prof = profile_key_columns(df, key_cols)

    consolidated_key_profile.append({
        "Dataset": dataset_name,
        "Key Name": " + ".join(key_cols),
        "Total Rows": key_prof["total_rows"],
        "Valid Rows": key_prof["valid_total"],
        "Unique Key Count": key_prof["unique_key_count"],
        "Duplicate Key Rows": key_prof["duplicate_key_rows"],
        "Null Key Rows": key_prof["null_key_rows"],
        "Uniqueness %": key_prof["uniqueness_pct"],
        "Duplicate %": key_prof["duplicate_pct"]
    })

# Full row duplicates
full_row_duplicates = []
for file_name, df in dataframes.items():
    dataset_name = file_name.replace("olist_", "").replace("_dataset.csv", "")
    dup_count = df.duplicated().sum()
    full_row_duplicates.append({
        "Dataset": dataset_name,
        "Total Rows": len(df),
        "Full Duplicate Rows": dup_count,
        "Duplicate %": round((dup_count / len(df) * 100), 2) if len(df) > 0 else 0.0
    })

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Phase 3 — Step 6: Relationship Consistency Profiling
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
consolidated_relationship_profile = []


# Helper function to evaluate relationship consistency
def check_relationship(rel_name, child_df, parent_df, child_cols, parent_cols):
    child_keys = child_df[child_cols].dropna()
    parent_keys = parent_df[parent_cols].dropna()

    if isinstance(child_cols, list) and len(child_cols) > 1:
        c_tuples = set(zip(*[child_keys[c] for c in child_cols]))
        p_tuples = set(zip(*[parent_keys[c] for c in parent_cols]))
        matches = sum(1 for t in c_tuples if t in p_tuples)
        total_checked = len(c_tuples)
    else:
        c_col = child_cols[0] if isinstance(child_cols, list) else child_cols
        p_col = parent_cols[0] if isinstance(parent_cols, list) else parent_cols

        child_series = child_df[c_col].dropna()
        parent_set = set(parent_df[p_col].dropna().unique())

        total_checked = len(child_series)
        matches = child_series.isin(parent_set).sum()

    non_matches = total_checked - matches
    match_pct = (matches / total_checked * 100) if total_checked > 0 else 0.0
    non_match_pct = (non_matches / total_checked * 100) if total_checked > 0 else 0.0

    return {
        "Relationship": rel_name,
        "Child Rows Checked": total_checked,
        "Match Count": matches,
        "Non-Match Count": non_matches,
        "Match %": round(match_pct, 2),
        "Non-Match %": round(non_match_pct, 2)
    }


# 1. Orders without Customers
if "olist_orders_dataset.csv" in dataframes and "olist_customers_dataset.csv" in dataframes:
    consolidated_relationship_profile.append(
        check_relationship(
            "Orders -> Customers (customer_id)",
            dataframes["olist_orders_dataset.csv"],
            dataframes["olist_customers_dataset.csv"],
            ["customer_id"], ["customer_id"]
        )
    )

# 2. Order Items without Orders
if "olist_order_items_dataset.csv" in dataframes and "olist_orders_dataset.csv" in dataframes:
    consolidated_relationship_profile.append(
        check_relationship(
            "Order Items -> Orders (order_id)",
            dataframes["olist_order_items_dataset.csv"],
            dataframes["olist_orders_dataset.csv"],
            ["order_id"], ["order_id"]
        )
    )

# 3. Order Items without Products
if "olist_order_items_dataset.csv" in dataframes and "olist_products_dataset.csv" in dataframes:
    consolidated_relationship_profile.append(
        check_relationship(
            "Order Items -> Products (product_id)",
            dataframes["olist_order_items_dataset.csv"],
            dataframes["olist_products_dataset.csv"],
            ["product_id"], ["product_id"]
        )
    )

# 4. Order Items without Sellers
if "olist_order_items_dataset.csv" in dataframes and "olist_sellers_dataset.csv" in dataframes:
    consolidated_relationship_profile.append(
        check_relationship(
            "Order Items -> Sellers (seller_id)",
            dataframes["olist_order_items_dataset.csv"],
            dataframes["olist_sellers_dataset.csv"],
            ["seller_id"], ["seller_id"]
        )
    )

# 5. Payments without Orders
if "olist_order_payments_dataset.csv" in dataframes and "olist_orders_dataset.csv" in dataframes:
    consolidated_relationship_profile.append(
        check_relationship(
            "Payments -> Orders (order_id)",
            dataframes["olist_order_payments_dataset.csv"],
            dataframes["olist_orders_dataset.csv"],
            ["order_id"], ["order_id"]
        )
    )

# 6. Reviews without Orders
if "olist_order_reviews_dataset.csv" in dataframes and "olist_orders_dataset.csv" in dataframes:
    consolidated_relationship_profile.append(
        check_relationship(
            "Reviews -> Orders (order_id)",
            dataframes["olist_order_reviews_dataset.csv"],
            dataframes["olist_orders_dataset.csv"],
            ["order_id"], ["order_id"]
        )
    )

# 7. Products without category translation
if "olist_products_dataset.csv" in dataframes and "product_category_name_translation.csv" in dataframes:
    consolidated_relationship_profile.append(
        check_relationship(
            "Products -> Translation (product_category_name)",
            dataframes["olist_products_dataset.csv"],
            dataframes["product_category_name_translation.csv"],
            ["product_category_name"], ["product_category_name"]
        )
    )

# 8. Customer ZIP prefixes without geolocation matches
if "olist_customers_dataset.csv" in dataframes and "olist_geolocation_dataset.csv" in dataframes:
    geo_df_distinct = dataframes["olist_geolocation_dataset.csv"][["geolocation_zip_code_prefix"]].drop_duplicates()
    consolidated_relationship_profile.append(
        check_relationship(
            "Customer ZIP -> Geolocation ZIP (customer_zip_code_prefix)",
            dataframes["olist_customers_dataset.csv"],
            geo_df_distinct,
            ["customer_zip_code_prefix"], ["geolocation_zip_code_prefix"]
        )
    )

# 9. Seller ZIP prefixes without geolocation matches
if "olist_sellers_dataset.csv" in dataframes and "olist_geolocation_dataset.csv" in dataframes:
    geo_df_distinct = dataframes["olist_geolocation_dataset.csv"][["geolocation_zip_code_prefix"]].drop_duplicates()
    consolidated_relationship_profile.append(
        check_relationship(
            "Seller ZIP -> Geolocation ZIP (seller_zip_code_prefix)",
            dataframes["olist_sellers_dataset.csv"],
            geo_df_distinct,
            ["seller_zip_code_prefix"], ["geolocation_zip_code_prefix"]
        )
    )

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Phase 3 — Step 7: Anomaly Identification and Classification
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
anomaly_list = []

# 1. Missing Values
# Missingness is reported as "Observation" unless the missing field is a
# documented primary-key column, in which case it is a "Confirmed anomaly"
# (a required identifier cannot legitimately be null). No missing-%
# threshold is used to infer anomaly status — that would invent a rule.
for file_name, df in dataframes.items():
    dataset_name = file_name.replace("olist_", "").replace("_dataset.csv", "")
    key_cols_for_file = set(PRIMARY_KEYS.get(file_name, []))
    for col in df.columns:
        null_cnt = df[col].isna().sum()
        if null_cnt > 0:
            null_pct = (null_cnt / len(df) * 100)
            if col in key_cols_for_file:
                classification = "Confirmed anomaly"
                description = (
                    f"Primary key column contains {null_cnt:,} missing values "
                    f"({null_pct:.2f}%)."
                )
            else:
                classification = "Observation"
                description = f"Column contains {null_cnt:,} missing values ({null_pct:.2f}%)."
            anomaly_list.append({
                "Dataset": dataset_name,
                "Column / Relationship": col,
                "Anomaly Type": "Missing values",
                "Classification": classification,
                "Count": null_cnt,
                "Percentage": round(null_pct, 2),
                "Description": description
            })

# 2. Duplicate Keys
for k_prof in consolidated_key_profile:
    if k_prof["Duplicate Key Rows"] > 0:
        # review_id is documented as a primary key but is not actually
        # unique in the source data.
        if "review_id" in k_prof["Key Name"]:
            classification = "Confirmed anomaly"
        else:
            classification = "Potential anomaly"
        anomaly_list.append({
            "Dataset": k_prof["Dataset"],
            "Column / Relationship": k_prof["Key Name"],
            "Anomaly Type": "Duplicate keys",
            "Classification": classification,
            "Count": k_prof["Duplicate Key Rows"],
            "Percentage": k_prof["Duplicate %"],
            "Description": f"Primary key contains {k_prof['Duplicate Key Rows']:,} duplicate rows ({k_prof['Duplicate %']}%, based on valid non-null key combinations)."
        })

# Geolocation duplicates
if "olist_geolocation_dataset.csv" in dataframes:
    geo_df = dataframes["olist_geolocation_dataset.csv"]
    geo_dup = geo_df.duplicated().sum()
    if geo_dup > 0:
        anomaly_list.append({
            "Dataset": "geolocation",
            "Column / Relationship": "Full row duplicate",
            "Anomaly Type": "Duplicate keys",
            "Classification": "Observation",
            "Count": geo_dup,
            "Percentage": round((geo_dup / len(geo_df) * 100), 2),
            "Description": f"Geolocation dataset contains {geo_dup:,} duplicate full rows."
        })

# 3. Extreme Values / Potential Outliers from Step 2
# An IQR outlier is not automatically an erroneous value — classified as
# "Potential anomaly" only. No correction, capping, or removal is implied.
for num_prof in consolidated_numeric_profile:
    if num_prof["Potential Outliers"] > 0:
        anomaly_list.append({
            "Dataset": num_prof["Dataset"],
            "Column / Relationship": num_prof["Column"],
            "Anomaly Type": "Extreme values",
            "Classification": "Potential anomaly",
            "Count": num_prof["Potential Outliers"],
            "Percentage": num_prof["Outlier %"],
            "Description": f"Identified {num_prof['Potential Outliers']:,} potential IQR outliers ({num_prof['Outlier %']}%)."
        })

# 4. Invalid Numeric Values (domain-aware)
# Negative values are only flagged where negative is logically invalid for
# that specific variable (e.g. price, freight_value). Columns such as
# geolocation latitude/longitude are not evaluated here since negative
# values are legitimate for those variables.
# Zero values are never automatically treated as invalid — reported as an
# "Observation" only, for every profiled numeric column.
for num_prof in consolidated_numeric_profile:
    col = num_prof["Column"]
    count = num_prof["Count"]

    if col in NEGATIVE_INVALID_COLUMNS and num_prof["Negative Count"] > 0:
        anomaly_list.append({
            "Dataset": num_prof["Dataset"],
            "Column / Relationship": col,
            "Anomaly Type": "Invalid values",
            "Classification": "Confirmed anomaly",
            "Count": num_prof["Negative Count"],
            "Percentage": round((num_prof["Negative Count"] / count * 100), 2) if count > 0 else 0.0,
            "Description": f"Contains {num_prof['Negative Count']} negative values, which are invalid for '{col}'."
        })

    if num_prof["Zero Count"] > 0:
        anomaly_list.append({
            "Dataset": num_prof["Dataset"],
            "Column / Relationship": col,
            "Anomaly Type": "Zero values",
            "Classification": "Observation",
            "Count": num_prof["Zero Count"],
            "Percentage": round((num_prof["Zero Count"] / count * 100), 2) if count > 0 else 0.0,
            "Description": f"Contains {num_prof['Zero Count']} zero values."
        })

# 5. Date Anomalies (Suspicious date sequences)
# These directly violate chronological ordering and are therefore
# classified as "Confirmed anomaly". Rows with missing dates are excluded
# automatically (NaT comparisons evaluate to False) and are never counted
# as suspicious sequences.
for seq in suspicious_sequence_results:
    if seq["Count"] > 0:
        anomaly_list.append({
            "Dataset": "orders",
            "Column / Relationship": seq["Sequence Check"],
            "Anomaly Type": "Date anomalies",
            "Classification": "Confirmed anomaly",
            "Count": seq["Count"],
            "Percentage": seq["Percentage"],
            "Description": f"Suspicious date sequence identified: {seq['Sequence Check']} in {seq['Count']} rows."
        })

# 6. Distribution Anomalies (Highly Skewed numeric distributions)
# Reported as "Observation" — describes the distribution, does not imply error.
for num_prof in consolidated_numeric_profile:
    if num_prof["Shape"] == "Highly skewed":
        anomaly_list.append({
            "Dataset": num_prof["Dataset"],
            "Column / Relationship": num_prof["Column"],
            "Anomaly Type": "Distribution anomalies",
            "Classification": "Observation",
            "Count": num_prof["Count"],
            "Percentage": 100.0,
            "Description": f"Highly skewed distribution detected (skewness = {num_prof['Skewness']})."
        })

# 7. Referential Anomalies (Unmatched foreign key references)
# Core documented relationships (orders/customers/items/products/sellers/
# payments/reviews) are "Confirmed anomaly" since they violate documented
# Phase 2 relationships. ZIP-to-geolocation and product-category-translation
# mismatches are "Potential anomaly" since unmatched mappings may have
# legitimate explanations.
for rel in consolidated_relationship_profile:
    if rel["Non-Match Count"] > 0:
        classification = "Potential anomaly" if "ZIP" in rel["Relationship"] or "Translation" in rel["Relationship"] else "Confirmed anomaly"
        anomaly_list.append({
            "Dataset": rel["Relationship"].split(" -> ")[0],
            "Column / Relationship": rel["Relationship"],
            "Anomaly Type": "Referential anomalies",
            "Classification": classification,
            "Count": rel["Non-Match Count"],
            "Percentage": rel["Non-Match %"],
            "Description": f"Contains {rel['Non-Match Count']:,} non-matching references ({rel['Non-Match %']}%)."
        })

# 8. Category Distribution Observations (Rare categories < 1%)
# Rare categories are not inherently anomalous — reported as "Observation".
for cat_prof in consolidated_categorical_profile:
    if cat_prof["Rare Categories"] > 0:
        anomaly_list.append({
            "Dataset": cat_prof["Dataset"],
            "Column / Relationship": cat_prof["Column"],
            "Anomaly Type": "Category distribution",
            "Classification": "Observation",
            "Count": cat_prof["Rare Categories"],
            "Percentage": cat_prof["Rare Category %"],
            "Description": f"Rare category (<1% threshold): {cat_prof['Rare Categories']} categories representing {cat_prof['Rare Rows %']}% of total rows."
        })

anomaly_df = pd.DataFrame(anomaly_list)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Phase 3 — Step 8: Final Profiling Report
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
final_report = []
final_report.append("=" * 80)
final_report.append("DATASET PROFILE REPORT")
final_report.append("=" * 80)
final_report.append("")

# 1. Dataset overview & Column summary & Numeric statistics (per dataset)
for section_str in step1_dataset_overview_sections:
    final_report.append(section_str)

# 4. Step 2 — Consolidated Numeric Distribution Profile
if consolidated_numeric_profile:
    num_df = pd.DataFrame(consolidated_numeric_profile)
    final_report.append("Phase 3 — Step 2: Consolidated Numeric Distribution Profile")
    final_report.append("=" * 80)
    final_report.append(num_df.to_string(index=False))
    final_report.append("")

# 5. Step 2 — Numeric Distribution Interpretations
if consolidated_numeric_profile:
    final_report.append("Phase 3 — Step 2: Numeric Distribution Interpretations")
    final_report.append("-" * 80)
    for row in consolidated_numeric_profile:
        final_report.append(f"Variable: {row['Dataset']} -> {row['Column']}")
        final_report.append(f"  Shape       : {row['Shape']} ({row['Direction']}) [Skewness: {row['Skewness']}]")
        final_report.append(f"  IQR Range   : Q1={row['Q1']} | Median={row['Median']} | Q3={row['Q3']} (IQR={row['IQR']})")
        final_report.append(f"  Outliers    : {row['Potential Outliers']} potential outliers ({row['Outlier %']}%) [Bounds: {row['Lower Bound']} to {row['Upper Bound']}]")
        final_report.append(f"  Special     : Zeros={row['Zero Count']} | Negatives={row['Negative Count']}")

        narrative = "  Interpretation: "
        if row['Mean'] > row['Median']:
            narrative += "Mean > Median indicates right-tail extension. "
        elif row['Mean'] < row['Median']:
            narrative += "Mean < Median indicates left-tail extension. "

        final_report.append(narrative)
        final_report.append("")

    final_report.append("Distribution Summary Section")
    final_report.append("-" * 80)
    final_report.append("1. Shape Classification:")
    final_report.append(f"   - Approx. Symmetric : {', '.join(num_df[num_df['Shape'] == 'Approximately symmetric']['Column'].tolist()) or 'None'}")
    final_report.append(f"   - Moderately Skewed : {', '.join(num_df[num_df['Shape'] == 'Moderately skewed']['Column'].tolist()) or 'None'}")
    final_report.append(f"   - Highly Skewed     : {', '.join(num_df[num_df['Shape'] == 'Highly skewed']['Column'].tolist()) or 'None'}")
    final_report.append("")
    final_report.append("2. Variables with Potential Outliers:")
    outlier_vars = num_df[num_df['Potential Outliers'] > 0][['Column', 'Potential Outliers', 'Outlier %']].to_dict('records')
    for ov in outlier_vars:
        final_report.append(f"   - {ov['Column']}: {ov['Potential Outliers']:,} rows ({ov['Outlier %']}%)")
    final_report.append("")
    final_report.append("3. Zero and Negative Values:")
    final_report.append(f"   - Zero Values     : {', '.join(num_df[num_df['Zero Count'] > 0]['Column'].tolist()) or 'None'}")
    final_report.append(f"   - Negative Values : {', '.join(num_df[num_df['Negative Count'] > 0]['Column'].tolist()) or 'None'}")
    final_report.append("")
    final_report.append("=" * 80)

# 7. Step 3 — Consolidated Categorical Distribution Profile
if consolidated_categorical_profile:
    cat_summary_df = pd.DataFrame(consolidated_categorical_profile)
    final_report.append("Phase 3 — Step 3: Consolidated Categorical Distribution Profile")
    final_report.append("=" * 80)
    final_report.append(cat_summary_df.to_string(index=False))
    final_report.append("")
    final_report.append("=" * 80)

# 8. Step 3 — Detailed Categorical Distributions
if detailed_categorical_sections:
    final_report.append("Phase 3 — Step 3: Detailed Categorical Distributions")
    final_report.append("-" * 80)
    for section in detailed_categorical_sections:
        final_report.append(section)
    final_report.append("")

# 9. Step 3 — Categorical Distribution Summary
if consolidated_categorical_profile:
    final_report.append("Phase 3 — Step 3: Categorical Distribution Summary")
    final_report.append("-" * 80)
    final_report.append("1. Dominant Categories:")
    for row in consolidated_categorical_profile:
        final_report.append(f"   - {row['Column']} ({row['Dataset']}): '{row['Top Category']}' ({row['Top %']}%)")
    final_report.append("")
    final_report.append("2. Rare Category Counts (< 1% Threshold):")
    for row in consolidated_categorical_profile:
        final_report.append(f"   - {row['Column']} ({row['Dataset']}): {row['Rare Categories']} rare categories ({row['Rare Rows %']}% of total rows)")
    final_report.append("")
    final_report.append("3. Category Concentration:")
    for row in consolidated_categorical_profile:
        final_report.append(f"   - {row['Column']} ({row['Dataset']}): Total Unique = {row['Unique Categories']}, Top Share = {row['Top %']}%")
    final_report.append("")
    final_report.append("=" * 80)

# 11. Step 4 — Consolidated Date Distribution Profile
if consolidated_date_profile:
    date_prof_df = pd.DataFrame(consolidated_date_profile)
    final_report.append("Phase 3 — Step 4: Consolidated Date Distribution Profile")
    final_report.append("=" * 80)
    final_report.append(date_prof_df.to_string(index=False))
    final_report.append("")
    final_report.append("Phase 3 — Step 4: Detailed Date Distributions (incl. Top 5 Largest Gaps)")
    final_report.append("-" * 80)
    for sec_str in detailed_date_sections:
        final_report.append(sec_str)
    final_report.append("")

# 12. Step 4 — Date Distribution Summary
if consolidated_date_profile:
    final_report.append("Phase 3 — Step 4: Date Distribution Summary")
    final_report.append("-" * 80)
    final_report.append("Date Gaps & Range Summary:")
    for row in consolidated_date_profile:
        final_report.append(f"   - {row['Column']} ({row['Dataset']}): Span [{row['Min Date']} to {row['Max Date']}] | Max Gap: {row['Max Gap']}")
    final_report.append("")

    if suspicious_sequence_results:
        final_report.append("Suspicious Date Sequences Summary:")
        seq_df = pd.DataFrame(suspicious_sequence_results)
        final_report.append(seq_df.to_string(index=False))
        final_report.append("")
    final_report.append("=" * 80)

# 13. Step 5 — Consolidated Key/Duplicate Profile
if consolidated_key_profile:
    key_prof_df = pd.DataFrame(consolidated_key_profile)
    final_report.append("Phase 3 — Step 5: Consolidated Key/Duplicate Profile")
    final_report.append("=" * 80)
    final_report.append(key_prof_df.to_string(index=False))
    final_report.append("")

# 14. Step 5 — Key/Duplicate Summary
if consolidated_key_profile:
    final_report.append("Phase 3 — Step 5: Key/Duplicate Summary")
    final_report.append("-" * 80)
    final_report.append("1. Primary Key Anomaly Observations:")
    for row in consolidated_key_profile:
        if row["Duplicate Key Rows"] > 0:
            final_report.append(f"   - {row['Key Name']} ({row['Dataset']}): {row['Duplicate Key Rows']:,} duplicate rows ({row['Duplicate %']}%), {row['Null Key Rows']:,} null key rows")
    final_report.append("")
    final_report.append("2. Full Row Duplicate Summary:")
    full_dup_df = pd.DataFrame(full_row_duplicates)
    final_report.append(full_dup_df.to_string(index=False))
    final_report.append("")
    final_report.append("=" * 80)

# 15. Step 6 — Relationship Consistency Profile
if consolidated_relationship_profile:
    rel_prof_df = pd.DataFrame(consolidated_relationship_profile)
    final_report.append("Phase 3 — Step 6: Relationship Consistency Profile")
    final_report.append("=" * 80)
    final_report.append(rel_prof_df.to_string(index=False))
    final_report.append("")

# 16. Step 6 — Relationship Summary
if consolidated_relationship_profile:
    final_report.append("Phase 3 — Step 6: Relationship Summary")
    final_report.append("-" * 80)
    for row in consolidated_relationship_profile:
        final_report.append(
            f"   - {row['Relationship']}: Match Rate = {row['Match %']}% "
            f"({row['Match Count']:,}/{row['Child Rows Checked']:,}) | Non-Match = {row['Non-Match Count']:,}"
        )
    final_report.append("")
    final_report.append("=" * 80)

# 17. Step 7 — Anomaly Summary
if not anomaly_df.empty:
    final_report.append("Phase 3 — Step 7: Consolidated Anomaly Summary")
    final_report.append("=" * 80)
    final_report.append(anomaly_df.to_string(index=False))
    final_report.append("")
    final_report.append("=" * 80)

# 18. Phase 3 — Profiling Observations (fully data-driven)
final_report.append("Phase 3 — Profiling Observations")
final_report.append("=" * 80)

# 1. Dataset coverage
total_rows_all = sum(len(df) for df in dataframes.values())
final_report.append("1. Dataset Coverage:")
final_report.append(f"   - Datasets processed        : {len(dataframes)}")
final_report.append(f"   - Total rows across datasets: {total_rows_all:,}")
final_report.append("")

# 2. Missing-value observations
missing_rows = [a for a in anomaly_list if a["Anomaly Type"] == "Missing values"]
final_report.append("2. Missing-Value Observations:")
if missing_rows:
    final_report.append(f"   - Columns with missing values : {len(missing_rows)}")
    top_missing = sorted(missing_rows, key=lambda r: r["Percentage"], reverse=True)[:5]
    final_report.append("   - Highest missing percentages:")
    for r in top_missing:
        final_report.append(f"     * {r['Dataset']} -> {r['Column / Relationship']}: {r['Percentage']}% ({r['Classification']})")
else:
    final_report.append("   - No missing values identified across datasets.")
final_report.append("")

# 3. Numeric distribution observations
final_report.append("3. Numeric Distribution Observations:")
if consolidated_numeric_profile:
    num_df_full = pd.DataFrame(consolidated_numeric_profile)
    highly_skewed = num_df_full[num_df_full["Shape"] == "Highly skewed"]["Column"].tolist()
    moderately_skewed = num_df_full[num_df_full["Shape"] == "Moderately skewed"]["Column"].tolist()
    outlier_vars = num_df_full[num_df_full["Potential Outliers"] > 0][["Dataset", "Column", "Potential Outliers", "Outlier %"]].to_dict("records")
    final_report.append(f"   - Highly skewed variables    : {', '.join(highly_skewed) or 'None'}")
    final_report.append(f"   - Moderately skewed variables: {', '.join(moderately_skewed) or 'None'}")
    if outlier_vars:
        final_report.append("   - Variables with IQR-based potential outliers:")
        for ov in outlier_vars:
            final_report.append(f"     * {ov['Dataset']} -> {ov['Column']}: {ov['Potential Outliers']:,} rows ({ov['Outlier %']}%)")
    else:
        final_report.append("   - No IQR-based outliers identified.")
else:
    final_report.append("   - No numeric target columns profiled.")
final_report.append("")

# 4. Categorical observations
final_report.append("4. Categorical Observations:")
if consolidated_categorical_profile:
    for row in consolidated_categorical_profile:
        final_report.append(
            f"   - {row['Dataset']} -> {row['Column']}: dominant category '{row['Top Category']}' "
            f"({row['Top %']}%), {row['Rare Categories']} rare categories ({row['Rare Rows %']}% of rows)"
        )
else:
    final_report.append("   - No categorical target columns profiled.")
final_report.append("")

# 5. Date observations
final_report.append("5. Date Observations:")
if consolidated_date_profile:
    for row in consolidated_date_profile:
        final_report.append(
            f"   - {row['Dataset']} -> {row['Column']}: range [{row['Min Date']} to {row['Max Date']}], "
            f"missing {row['Missing Count']:,} ({row['Missing %']}%), max gap {row['Max Gap']}"
        )
    if suspicious_sequence_results:
        flagged = [s for s in suspicious_sequence_results if s["Count"] > 0]
        if flagged:
            final_report.append("   - Suspicious chronological sequences identified:")
            for s in flagged:
                final_report.append(f"     * {s['Sequence Check']}: {s['Count']:,} rows ({s['Percentage']}%)")
        else:
            final_report.append("   - No suspicious chronological sequences identified.")
else:
    final_report.append("   - No date target columns profiled.")
final_report.append("")

# 6. Key observations
final_report.append("6. Key Observations:")
if consolidated_key_profile:
    any_key_issue = False
    for row in consolidated_key_profile:
        if row["Duplicate Key Rows"] > 0 or row["Null Key Rows"] > 0:
            any_key_issue = True
            final_report.append(
                f"   - {row['Dataset']} ({row['Key Name']}): {row['Duplicate Key Rows']:,} duplicate key rows "
                f"({row['Duplicate %']}%), {row['Null Key Rows']:,} null key rows"
            )
    if not any_key_issue:
        final_report.append("   - No duplicate or null primary keys identified among documented keys.")
if "olist_geolocation_dataset.csv" in dataframes:
    geo_df = dataframes["olist_geolocation_dataset.csv"]
    geo_dup_count = geo_df.duplicated().sum()
    geo_dup_pct = round((geo_dup_count / len(geo_df) * 100), 2) if len(geo_df) > 0 else 0.0
    final_report.append(f"   - geolocation dataset full-row duplicates: {geo_dup_count:,} ({geo_dup_pct}%)")
final_report.append("")

# 7. Relationship observations
final_report.append("7. Relationship Observations:")
if consolidated_relationship_profile:
    mismatched = [r for r in consolidated_relationship_profile if r["Non-Match Count"] > 0]
    if mismatched:
        for r in mismatched:
            final_report.append(f"   - {r['Relationship']}: {r['Non-Match Count']:,} non-matching rows ({r['Non-Match %']}%)")
    else:
        final_report.append("   - All evaluated relationships show full referential match.")
else:
    final_report.append("   - No relationships evaluated.")
final_report.append("")

# 8. Anomaly classification summary
final_report.append("8. Anomaly Classification Summary:")
if not anomaly_df.empty:
    class_counts = anomaly_df["Classification"].value_counts()
    for cls in ["Observation", "Potential anomaly", "Confirmed anomaly"]:
        final_report.append(f"   - {cls:<18}: {int(class_counts.get(cls, 0)):,}")
else:
    final_report.append("   - No anomalies identified.")
final_report.append("")
final_report.append("=" * 80)

# ----------------------------------------------------------------------
# Output Generation
# ----------------------------------------------------------------------
output_file = OUTPUT / "dataset_profile_report.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(final_report))

print(f"Report saved to: {output_file}")