from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# =============================================================================
# 1. Default Arguments Definition
# These arguments are applied to all tasks within this DAG by default.
# This prevents code duplication and ensures consistent behavior across tasks.
# =============================================================================
default_args = {
    'owner': 'data_engineering_team', # The team responsible for maintaining this pipeline
    'depends_on_past': False,         # If True, a task won't run unless the previous day's run succeeded. Set to False for independent daily runs.
    'email_on_failure': True,         # Automatically triggers an email notification if any task fails
    'email_on_retry': False,          # Disables emails for retries to avoid spamming the inbox
    'email': ['alerts@company.com'],  # The distribution list or Slack-integrated email to receive alerts
    'retries': 3,                     # Number of retry attempts before marking the task as strictly "FAILED"
    'retry_delay': timedelta(minutes=5), # Wait time between retry attempts (allows transient API/Network issues to resolve)
}

# =============================================================================
# 2. DAG (Directed Acyclic Graph) Definition
# This acts as the orchestrator/manager that schedules and monitors the tasks.
# =============================================================================
with DAG(
    dag_id='ga4_daily_production_pipeline', # Unique identifier for the DAG in the Airflow UI
    default_args=default_args,            # Bind the previously defined default settings
    description='End-to-End GA4 ETL Pipeline: Extracts raw data, transforms it, and exports to Google Sheets',
    schedule_interval='0 2 * * *',        # Cron expression: Runs exactly at 02:00 AM UTC every day
    start_date=datetime(2026, 6, 1),      # The logical start date of the pipeline (Airflow needs this to track time)
    catchup=False,                        # CRITICAL: If True, Airflow will run all missed past dates since start_date. Set to False to only run the current schedule.
    tags=['ga4', 'etl', 'bigquery', 'sheets', 'production'], # Searchable tags for the Airflow web interface
) as dag:

    # =============================================================================
    # 3. Task Definitions using BashOperator
    # BashOperator simulates running commands directly in the terminal/command line.
    # =============================================================================
    
    # Task A: Ingest raw GA4 data into BigQuery
    extract_and_load_raw = BashOperator(
        task_id='extract_and_load_raw', # Unique ID for this specific task
        bash_command='python /opt/airflow/scripts/Raw_Data_Ingestion_TABLE_SUFFIX.py' # Absolute path to the python script inside the Airflow container
    )

    # Task B: Compute daily aggregated metrics (Revenue, Sessions, etc.)
    transform_daily = BashOperator(
        task_id='transform_daily',
        bash_command='python /opt/airflow/scripts/transform_daily_metrics.py'
    )

    # Task C: Compute weekly aggregated metrics
    transform_weekly = BashOperator(
        task_id='transform_weekly',
        bash_command='python /opt/airflow/scripts/transform_weekly_metrics.py'
    )

    # Task D: Flatten nested product arrays using UNNEST and compute product metrics
    transform_product = BashOperator(
        task_id='transform_product',
        bash_command='python /opt/airflow/scripts/transform_product_metrics.py'
    )

    # Task E: Export the 3 finalized BigQuery tables to Google Sheets
    export_to_sheets = BashOperator(
        task_id='export_to_sheets',
        bash_command='python /opt/airflow/scripts/export_to_sheets.py'
    )

    # =============================================================================
    # 4. Task Dependencies (Execution Order)
    # Using the bitshift operator (>>) to set upstream/downstream relationships.
    # =============================================================================
    
    # Flow Logic:
    # 1. Must finish extracting raw data first.
    # 2. Once raw data is ready, run all 3 transformation scripts simultaneously (in parallel) to save processing time.
    # 3. Only when ALL 3 transformations succeed, proceed to export the final data to Google Sheets.
    
    extract_and_load_raw >> [transform_daily, transform_weekly, transform_product] >> export_to_sheets