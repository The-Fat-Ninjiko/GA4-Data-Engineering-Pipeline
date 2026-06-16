##needed lib.
import os
from google.cloud import bigquery

#credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "darkrooms-task-41859b8ff948.json"
client = bigquery.Client()

##congigs.
PROJECT_ID   = "darkrooms-task"
DATASET_ID   = "darkroom_etl"
RAW_TABLE    = f"{PROJECT_ID}.{DATASET_ID}.raw_ga4_events"
TARGET_TABLE = f"{PROJECT_ID}.{DATASET_ID}.product_metrics_report"


def run_product_transforming():
    print("Transforming Data: Building Product Metrics Table...")

    # This SQL query uses UNNEST to flatten the items array and calculate Top Products
    sql = f"""
        CREATE OR REPLACE TABLE `{TARGET_TABLE}`
        AS
        SELECT
            item.item_name AS Product_Name,
            SUM(COALESCE(item.item_revenue, 0)) AS Total_Revenue,
            SUM(COALESCE(item.quantity, 0)) AS Total_Quantity_Sold
        FROM `{RAW_TABLE}`,
        UNNEST(items) AS item
        WHERE event_name = 'purchase' 
        AND item.item_name IS NOT NULL 
        AND item.item_name != '(not set)'
        GROUP BY Product_Name
    """
    
    try:
        query_job = client.query(sql)
        query_job.result()
        print(f"Transform Data Complete! Product metrics saved to {TARGET_TABLE}")
    except Exception as e:
        print(f"Transformation failed: {e}")

if __name__ == "__main__":
    run_product_transforming()