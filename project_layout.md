# Project Layout

``` text
Retail-Sales-Performance-Analytics/
│
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   ├── interim/
│   ├── cleaned/
│   ├── processed/
│   └── external/
│
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_profiling.ipynb
│   ├── 03_data_cleaning.ipynb
│   ├── 04_eda.ipynb
│   ├── 05_feature_engineering.ipynb
│   └── 06_statistical_analysis.ipynb
│
├── src/
│   ├── data/
│   │   ├── load_data.py
│   │   ├── clean_data.py
│   │   ├── preprocess.py
│   │   └── feature_engineering.py
│   │
│   ├── visualization/
│   │   ├── plots.py
│   │   └── dashboard_charts.py
│   │
│   ├── analysis/
│   │   ├── kpi_calculations.py
│   │   ├── business_metrics.py
│   │   └── statistical_tests.py
│   │
│   └── utils/
│       ├── config.py
│       └── helpers.py
│
├── sql/
│   ├── schema.sql
│   ├── data_validation.sql
│   ├── kpi_queries.sql
│   └── business_queries.sql
│
├── excel/
│   └── Retail_Analysis.xlsx
│
├── powerbi/
│   ├── RetailDashboard.pbix
│   ├── dax_measures.md
│   └── wireframes/
│
├── reports/
│   ├── business_understanding/
│   ├── data_quality/
│   ├── profiling/
│   ├── insights/
│   ├── executive_summary/
│   └── final_report/
│
├── docs/
│   ├── project_charter.md
│   ├── business_requirements.md
│   ├── data_dictionary.md
│   ├── schema_design.md
│   ├── kpi_dictionary.md
│   ├── methodology.md
│   └── references.md
│
├── diagrams/
│   ├── er_diagram.png
│   ├── star_schema.png
│   ├── workflow.png
│   └── dashboard_wireframe.png
│
├── presentation/
│   └── Retail_Sales_Case_Study.pptx
│
└── assets/
    ├── images/
    └── icons/
```
