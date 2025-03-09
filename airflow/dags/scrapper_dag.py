from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from datetime import datetime, timedelta

from scrapper import run_scraper

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'promiedos_scraper',
    default_args=default_args,
    description='Scrape football matches data and upload to GCS',
    schedule_interval='0 2 * * *',  # Run at 2 AM every day
    catchup=False,
) as dag:

    def scrape_wrapper(**context):
        csv_file = run_scraper()
        # Push the filename to XCom for the next task
        context['task_instance'].xcom_push(key='csv_filename', value=csv_file)
        return csv_file

    scrape_task = PythonOperator(
        task_id='scrape_matches',
        python_callable=scrape_wrapper,
    )

    upload_to_gcs = LocalFilesystemToGCSOperator(
        task_id='upload_to_gcs',
        src="{{ task_instance.xcom_pull(task_ids='scrape_matches') }}",
        dst='matches/{{ ds }}/{{ task_instance.xcom_pull(task_ids="scrape_matches") }}',
        bucket='promiedos_data',  # Replace with your bucket name
        gcp_conn_id='google_cloud_default'
    )

    scrape_task >> upload_to_gcs