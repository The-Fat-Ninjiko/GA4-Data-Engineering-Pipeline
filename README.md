# GA4 Data Engineering ETL Pipeline 🚀

**Author:** Omar Hesham Ali Kamel  
**Task:** Data Engineer Take-Home Assignment

## 📌 Project Overview
This project is a lightweight, end-to-end ETL pipeline designed to extract Google Analytics 4 (GA4) obfuscated sample ecommerce data, load it into a BigQuery data warehouse, transform it into business-ready reporting metrics, and finally export it to Google Sheets for daily and weekly tracking.

## 🛠️ Architecture & Tech Stack
* **Extraction & Loading (EL):** Python, Google Cloud BigQuery API
* **Transformation (T):** BigQuery SQL (Full Refresh & Incremental Logic)
* **Reporting / Output:** Google Sheets API, Pandas, Gspread
* **Cloud Infrastructure:** Google Cloud Platform (GCP)

## 📂 Project Structure
* `Raw_Data_Ingestion_TABLE_SUFFIX.py`: Extracts raw GA4 data iteratively (using `_TABLE_SUFFIX` for optimal bulk loading) and creates the partitioned `raw_ga4_events` table.
* `transform_daily_metrics.py`: Computes daily aggregated metrics (Revenue, Orders, Customers, Traffic).
* `transform_weekly_metrics.py`: Computes weekly aggregated metrics ensuring daily reconciliation.
* `transform_product_metrics.py`: Flattens the nested item arrays using `UNNEST` to calculate product-level performance (Revenue & Quantity).
* `export_to_sheets.py`: Reads the transformed BigQuery tables and dynamically overwrites the respective tabs in Google Sheets.
* `System_Design.pdf` *(or .docx)*: Contains the Part 5 production architecture design.

## ⚙️ Prerequisites
To run this project locally, ensure you have Python 3 installed and the following libraries:
```bash
pip install google-cloud-bigquery pandas gspread db-dtypes google-auth


Note: A GCP Service Account JSON key is required for authentication (darkrooms-task-***.json). Ensure the service account has BigQuery Admin and Google Sheets API editing permissions.

🚀 Execution Order
To reproduce the pipeline, execute the scripts in the following order:

Extract & Load Raw Data:

Bash
python Raw_Data_Ingestion.py
Run Transformations:

Bash
python transform_daily_metrics.py
python transform_weekly_metrics.py
python transform_product_metrics.py
Export to Google Sheets:

Bash
python export_to_sheets.py
📊 Final Deliverables
Google Sheets Report: [Insert Your Google Sheet Link Here]

(The sheet contains Daily Metrics, Weekly Metrics, and Product Metrics tabs and is publicly viewable).

Production Design: Please refer to the attached System_Design document for Part 5 of the assignment.
