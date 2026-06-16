## Same as the Raw_Data_Ingestion.py but with range to make it easier##

# Importing the needed lib in the extrction of the raw data
import os 
from google.cloud import bigquery

#importing the dates lib.
from datetime import datetime, timedelta

#credential inside a eniveroment var and creating a client 
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "darkrooms-task-41859b8ff948.json"
client = bigquery.Client()

#config.
PROJECT_ID   = "darkrooms-task"
DATASET_ID   = "darkroom_etl"
TABLE_NAME   = "raw_ga4_events"
TARGET_TABLE = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}" 

# function to get the data ranges knowing that the data is around year 2020 and 2021
def get_date_range(start_date_str,end_date_str):
    start_date = datetime.strptime(start_date_str, '%Y%m%d')
    end_date = datetime.strptime(end_date_str, '%Y%m%d')

    delta=end_date-start_date

    dates=[]
    for i in range(delta.days+1):
        day = start_date + timedelta(days=i)
        dates.append(day.strftime('%Y%m%d'))
    
    return dates

#function to show that data is loading where {data_str} is the date of the day that we want to load
def run_incremental_load(date_str):
    print(f"Loading...  ingestion for data: {date_str}")
    # The SQL query handles table creation, duplicate prevention, and data insertion
    sql = f"""
        --Creat Table if not exsist and partition it by date
        CREATE  TABLE IF NOT EXISTS `{TARGET_TABLE}`
        PARTITION BY parsed_event_date
        AS
        SELECT
            *,
            PARSE_DATE('%Y%m%d', event_date) AS parsed_event_date, -- creating parse or event date
            CURRENT_TIMESTAMP() AS ingestion_timestamp --entry timestamp
        FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_{date_str}`
        LIMIT 0;

        --deletes any existing records for this specific date before inserting new ones.
        DELETE FROM `{TARGET_TABLE}`
        WHERE event_date = '{date_str}';

        -- load new data fresh
        INSERT INTO `{TARGET_TABLE}`
        SELECT 
            *,
            PARSE_DATE('%Y%m%d', event_date)AS parsed_event_date,
            CURRENT_TIMESTAMP() AS ingestion_timestamp --entry timestamp
        FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_{date_str}`;
    """
    ##try & catch for errors
    try:
        query_job = client.query(sql)
        query_job.result()
        print(f"Data Load Success for {date_str} into {TARGET_TABLE}")
    except Exception as e:
        print(f"Data load faild for {date_str} error:{e}")
    ####### End of Function #########

#excution of the incremental pull
if __name__ == "__main__":
    dates_to_load = get_date_range("20201101","20210131") 
    
    for date in dates_to_load:
        run_incremental_load(date)
        
    print("🎉 Dynamic Incremental Load Complete!")


