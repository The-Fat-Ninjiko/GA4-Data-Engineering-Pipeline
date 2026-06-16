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
TARGET_TABLE = f"{PROJECT_ID}.{DATASET_ID}.weekly_metrics_report"

##Building weekly metrics table
def run_weekly_transforming():
    print("Transformation: Building Weekly Metrics Table...")

    #sql to transform raw GA4 data into weekly business metrics
    sql = f"""
    CREATE OR REPLACE TABLE `{TARGET_TABLE}`
    PARTITION BY report_week
    AS
    WITH weekly_base AS (
        SELECT
            -- DATE_TRUNC groups the dates into the start of the week (Monday)
            DATE_TRUNC(parsed_event_date, ISOWEEK)                       AS report_week,
            COUNTIF(event_name = 'session_start')                        AS total_sessions_started,
            COUNT(DISTINCT ecommerce.transaction_id)                     AS total_orders,
            SUM(COALESCE(ecommerce.purchase_revenue, 0))                 AS gross_revenue, 
            SUM(COALESCE(ecommerce.refund_value, 0))                     AS refund_amount,
            COUNT(DISTINCT user_pseudo_id)                               AS unique_customers,
            COUNT(DISTINCT CASE WHEN event_name = 'first_visit' THEN user_pseudo_id END) AS new_customers
        FROM `{RAW_TABLE}`
        GROUP BY report_week
    )

    SELECT  
        report_week,
        gross_revenue,
        refund_amount,
        (gross_revenue - refund_amount) AS net_revenue,
        total_orders,
        SAFE_DIVIDE(gross_revenue, total_orders) AS average_order_value,
        unique_customers,
        new_customers,
        (unique_customers - new_customers) AS returning_customers,
        total_sessions_started,
        SAFE_DIVIDE(total_orders, total_sessions_started) AS conversion_rate
    FROM weekly_base
    """
    # Note: No ORDER BY here either to avoid the partitioning error!
    
    try:
        query_job = client.query(sql)
        query_job.result()
        print(f"Transformation Complete! Weekly metrics saved to {TARGET_TABLE}")
    except Exception as e:
        print(f" Transformation failed: {e}")

if __name__ == "__main__":
    run_weekly_transforming()