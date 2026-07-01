# Project Layout

This document describes the directory structure of the **Retail Sales Performance Analytics** project.

---

## Repository Structure

```text
Retail-Sales-Performance-Analytics/
│
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
│
├── data/
│   │
│   ├── raw/
│   │   ├── customers.csv
│   │   ├── orders.csv
│   │   ├── order_items.csv
│   │   ├── products.csv
│   │   ├── sellers.csv
│   │   ├── geolocation.csv
│   │   ├── payments.csv
│   │   ├── reviews.csv
│   │   ├── category_translation.csv
│   │   └── README.md
│   │
│   ├── interim/
│   │
│   ├── cleaned/
│   │
│   └── processed/
│       ├── fact_sales.csv
│       ├── dim_customer.csv
│       ├── dim_product.csv
│       ├── dim_seller.csv
│       ├── dim_date.csv
│       └── README.md
│
├── notebooks/
│   ├── 01_Business_Understanding.ipynb
│   ├── 02_Data_Understanding.ipynb
│   ├── 03_Data_Profiling.ipynb
│   ├── 04_Data_Quality_Assessment.ipynb
│   ├── 05_Data_Cleaning.ipynb
│   ├── 06_Data_Modeling.ipynb
│   ├── 07_Excel_Validation.ipynb
│   ├── 08_SQL_Analysis.ipynb
│   ├── 09_Python_ETL.ipynb
│   ├── 10_Exploratory_Data_Analysis.ipynb
│   ├── 11_Statistical_Analysis.ipynb
│   ├── 12_Feature_Engineering.ipynb
│   ├── 13_KPI_Development.ipynb
│   └── 14_Business_Metrics.ipynb
│
├── scripts/
│   ├── profiling.py
│   ├── data_quality.py
│   ├── cleaning.py
│   ├── feature_engineering.py
│   ├── validation.py
│   ├── export_processed_data.py
│   └── utils.py
│
├── sql/
│   ├── 01_database_schema.sql
│   ├── 02_load_data.sql
│   ├── 03_create_star_schema.sql
│   ├── 04_views.sql
│   ├── 05_business_queries.sql
│   ├── 06_window_functions.sql
│   ├── 07_validation_queries.sql
│   └── 08_kpi_queries.sql
│
├── excel/
│   ├── Retail_Sales_Analysis.xlsx
│   └── Pivot_Validation.xlsx
│
├── powerbi/
│   ├── Retail_Sales_Dashboard.pbix
│   ├── dax_measures.md
│   ├── theme.json
│   └── screenshots/
│       ├── Executive_Dashboard.png
│       ├── Sales_Analysis.png
│       ├── Product_Analysis.png
│       └── Regional_Analysis.png
│
├── reports/
│   ├── 01_Project_Charter.pdf
│   ├── 02_Data_Profile_Report.pdf
│   ├── 03_Data_Quality_Report.pdf
│   ├── 04_Data_Cleaning_Report.pdf
│   ├── 05_Star_Schema_Report.pdf
│   ├── 06_EDA_Report.pdf
│   ├── 07_Statistical_Analysis_Report.pdf
│   ├── 08_KPI_Report.pdf
│   ├── 09_Executive_Summary.pdf
│   ├── 10_Final_Report.pdf
│   └── 11_Business_Recommendations.pdf
│
├── docs/
│   ├── project_scope.md
│   ├── business_requirements.md
│   ├── assumptions.md
│   ├── stakeholder_questions.md
│   ├── data_dictionary.md
│   ├── data_quality_checklist.md
│   ├── cleaning_log.md
│   ├── feature_dictionary.md
│   ├── kpi_definitions.md
│   ├── validation_checklist.md
│   ├── dashboard_wireframes.pdf
│   ├── interview_questions.md
│   ├── resume_points.md
│   ├── schema.png
│   ├── star_schema.png
│   ├── etl_pipeline.png
│   └── dashboard_layout.png
│
├── presentation/
│   ├── Retail_Sales_Case_Study.pptx
│   └── Executive_Presentation.pdf
│
├── images/
│   ├── profiling/
│   ├── eda/
│   ├── statistics/
│   ├── sql/
│   ├── powerbi/
│   └── dashboard/
│
└── references/
    ├── research_papers.pdf
    ├── business_references.pdf
    └── citations.md
```

---

## Directory Overview

| Directory         | Description                                                                                                                  |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **data/**         | Contains raw, intermediate, cleaned, and processed datasets used throughout the project.                                     |
| **notebooks/**    | Jupyter notebooks documenting each phase of the analytics workflow.                                                          |
| **scripts/**      | Reusable Python scripts for profiling, cleaning, validation, feature engineering, and data export.                           |
| **sql/**          | Database schema creation, data loading, star schema implementation, validation, KPI, and business analysis queries.          |
| **excel/**        | Excel workbooks for pivot tables, manual validation, and quality checks.                                                     |
| **powerbi/**      | Power BI dashboard, DAX documentation, theme configuration, and dashboard screenshots.                                       |
| **reports/**      | Project reports generated during different phases of the analysis.                                                           |
| **docs/**         | Project documentation, business requirements, data dictionary, KPI definitions, validation checklists, and design documents. |
| **presentation/** | Final project presentation and executive presentation.                                                                       |
| **images/**       | Generated visualizations, dashboard screenshots, SQL outputs, and EDA figures.                                               |
| **references/**   | Research papers, external references, and project citations.                                                                 |

---

## Project Organization Principles

* Keep raw data unchanged.
* Store cleaned and processed data separately from the original source.
* Separate notebooks from reusable Python scripts.
* Organize SQL scripts by execution order.
* Keep project documentation inside the `docs` directory.
* Store generated reports inside the `reports` directory.
* Keep presentation materials separate from technical documentation.
* Use consistent naming conventions across all project assets.
* Maintain a clean and reproducible repository structure.
