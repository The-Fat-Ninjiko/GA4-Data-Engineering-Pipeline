#import required lib.
import os 
from google.cloud import bigquery

# Authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "darkrooms-task-41859b8ff948.json"
client = bigquery.Client()

##configs.
PROJECT_ID   = "darkrooms-task"
DATASET_ID   = "darkroom_etl"
TARGET_TABLE = f"{PROJECT_ID}.{DATASET_ID}.raw_ga4_events" 

def run_bulk_incremental_load(start_date, end_date):
    print(f"Bulk Loading data from {start_date} to {end_date} in ONE shot...")
    
    # This SQL query performs the following operations:
    # -Creates the table if it does not exist
    # -Deletes the specified date range if it already exists (to prevent data duplication)
    # -Extracts the entire date range efficiently in a single bulk operation using _TABLE_SUFFIX
    sql = f"""
        CREATE TABLE IF NOT EXISTS `{TARGET_TABLE}`
        PARTITION BY parsed_event_date
        AS
        SELECT 
            *,
            PARSE_DATE('%Y%m%d', event_date) AS parsed_event_date,
            CURRENT_TIMESTAMP() AS ingestion_timestamp
        FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
        LIMIT 0;

        DELETE FROM `{TARGET_TABLE}`
        WHERE event_date BETWEEN '{start_date}' AND '{end_date}';

        INSERT INTO `{TARGET_TABLE}`
        SELECT 
            *,
            PARSE_DATE('%Y%m%d', event_date) AS parsed_event_date,
            CURRENT_TIMESTAMP() AS ingestion_timestamp
        FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
        WHERE _TABLE_SUFFIX BETWEEN '{start_date}' AND '{end_date}';
    """
    try:
        query_job = client.query(sql)
        query_job.result()
        print(f"✅ Data Load Success! All days from {start_date} to {end_date} loaded seamlessly.")
    except Exception as e:
        print(f"Data load failed: {e}")

if __name__ == "__main__":
    # Executing this function will pull the entire specified date range in seconds!
    run_bulk_incremental_load("20201101", "20210131")