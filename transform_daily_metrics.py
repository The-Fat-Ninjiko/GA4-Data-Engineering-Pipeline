#importing needed lib.
import os
from google.cloud import bigquery

#credentials 
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "darkrooms-task-41859b8ff948.json"
client = bigquery.Client()

#configs.
PROJECT_ID   = "darkrooms-task"
DATASET_ID   = "darkroom_etl"
RAW_TABLE    = f"{PROJECT_ID}.{DATASET_ID}.raw_ga4_events"
TARGET_TABLE = f"{PROJECT_ID}.{DATASET_ID}.daily_metrics_report"

##Building daily metrics table
def run_daily_transforming():
    print("Transformation: Building Daily Metrics Table...")

    #sql to transform raw GA4 data into daily business metrics
    sql = f"""
    CREATE OR REPLACE TABLE `{TARGET_TABLE}`
    PARTITION BY report_date
    AS
    WITH daily_base as (
        SELECT
            parsed_event_date                                                            as Report_Date,
            COUNTIF(event_name = 'session_start')                                        AS Total_Sessions_Started,
            COUNT(DISTINCT ecommerce.transaction_id)                                     AS Total_Orders,
            SUM(COALESCE(ecommerce.purchase_revenue, 0))                                 AS Gross_Revenue, 
            SUM(COALESCE(ecommerce.refund_value, 0))                                     AS Refund_Amount,
            COUNT(DISTINCT user_pseudo_id)                                               AS Unique_Customers,
            COUNT(DISTINCT CASE WHEN event_name = 'first_visit' THEN user_pseudo_id END) AS New_Customers

        FROM `{RAW_TABLE}`
        GROUP BY parsed_event_date
    )

    SELECT  
        Report_Date,
        Gross_Revenue,
        Refund_Amount,
        (gross_revenue - refund_amount) AS Net_Revenue,
        Total_Orders,
        SAFE_DIVIDE(gross_revenue, total_orders) AS Average_Order_Value_AOV,
        Unique_Customers,
        New_Customers,
        (Unique_Customers - New_Customers) AS Returning_Customers,
        Total_Sessions_Started,
        SAFE_DIVIDE(total_orders, Total_Sessions_Started) AS Conversion_Rate
    FROM daily_base;
    """
    try:
        query_job = client.query(sql)
        query_job.result()
        print(f"Transformation Complete! Daily metrics saved to {TARGET_TABLE}")
    except Exception as e:
        print(f"Transformation failed: {e}")

if __name__ == "__main__":
    run_daily_transforming()
