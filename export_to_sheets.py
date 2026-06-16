import os
import pandas as pd
import gspread
from google.cloud import bigquery
from google.oauth2.service_account import Credentials

# 1. Authentication & Configs
KEY_FILE = "darkrooms-task-41859b8ff948.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_FILE

PROJECT_ID   = "darkrooms-task"
DATASET_ID   = "darkroom_etl"
SHEET_URL    = "https://docs.google.com/spreadsheets/d/11EjYgOArs7Os-urVXetVe9rW-W0XC6dHriQnuIWf46U/edit?usp=sharing" 

def export_to_sheets():
    print("Connecting to Google Services...")
    
    # 2. Connect to BigQuery
    bq_client = bigquery.Client()
    
    # 3. Connect to Google Sheets using the same Service Account
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = Credentials.from_service_account_file(KEY_FILE, scopes=scopes)
    gc = gspread.authorize(credentials)
    
    # Open the Google Sheet
    try:
        sh = gc.open_by_url(SHEET_URL)
    except Exception as e:
        print(f"Error opening Google Sheet. Error: {e}")
        return

    # 4. Helper Function to extract from BigQuery and load to Sheets
    def load_table_to_sheet(table_name, tab_name):
        print(f"Fetching data from BigQuery table: {table_name}...")
        
        # Read data into a Pandas DataFrame
        query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}` ORDER BY 1"
        df = bq_client.query(query).to_dataframe()
        
        df = df.astype(str)
            
        # Replace string representations of Null/NaN with actual empty strings
        df = df.replace(["nan", "None", "<NA>", "NaT"], "")

        print(f"Uploading to Google Sheets tab: {tab_name}...")
        try:
            # Try to open the tab if it exists
            worksheet = sh.worksheet(tab_name)
        except gspread.exceptions.WorksheetNotFound:
            # If it doesn't exist, create it
            worksheet = sh.add_worksheet(title=tab_name, rows="100", cols="20")
            
        # Overwrite Logic: Clear old data to prevent duplication, then insert new data
        worksheet.clear()
        
        # Prepare data for upload (Headers + Rows)
        data_to_upload = [df.columns.values.tolist()] + df.values.tolist()
        
        # Upload in one API call
        worksheet.update(values=data_to_upload, range_name="A1")
        print(f"Successfully updated '{tab_name}'!")

    # 5. Execute the function for all 3 reporting tables
    load_table_to_sheet("daily_metrics_report", "Daily Metrics")
    load_table_to_sheet("weekly_metrics_report", "Weekly Metrics")
    load_table_to_sheet("product_metrics_report", "Product Metrics")
    
    print("🎉 BOOM! All reporting data successfully exported to Google Sheets!")

if __name__ == "__main__":
    export_to_sheets()