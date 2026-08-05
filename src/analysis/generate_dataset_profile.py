from pathlib import Path
from io import StringIO
import pandas as pd

RAW_DATA = Path("data/raw")
OUTPUT = Path("reports/profiling")
OUTPUT.mkdir(parents=True, exist_ok=True)

report = []

report.append("=" * 80)
report.append("DATASET PROFILE REPORT")
report.append("=" * 80)
report.append("")

csv_files = sorted(RAW_DATA.glob("*.csv"))

for file in csv_files:

    df = pd.read_csv(file)

    report.append(f"Dataset : {file.name}")
    report.append("-" * 80)

    report.append("Basic Information")
    report.append(f"Rows                : {len(df):,}")
    report.append(f"Columns             : {df.shape[1]}")
    report.append(f"Duplicate Rows      : {df.duplicated().sum():,}")
    report.append(f"Memory Usage (MB)   : {df.memory_usage(deep=True).sum()/1024**2:.2f}")
    report.append("")

    report.append("Column Summary")

    summary = pd.DataFrame({
        "Data Type": df.dtypes.astype(str),
        "Missing": df.isna().sum(),
        "Missing %": (df.isna().mean()*100).round(2),
        "Unique Values": df.nunique()
    })

    report.append(summary.to_string())
    report.append("")

    report.append("Columns")

    for c in df.columns:
        report.append(f"• {c}")

    report.append("")

    report.append("DataFrame Info")

    buffer = StringIO()
    df.info(buf=buffer)

    report.append(buffer.getvalue())
    report.append("")

    report.append("Descriptive Statistics")

    report.append(df.describe(include="all").transpose().to_string())

    report.append("")
    report.append("=" * 80)
    report.append("")

output_file = OUTPUT / "dataset_profile_report.txt"

with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(report))

print(f"Report saved to: {output_file}")