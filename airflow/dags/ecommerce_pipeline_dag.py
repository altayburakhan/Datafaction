"""
E-Commerce Pipeline DAG
Schedule: Daily @daily
Flow: generate_daily_data >> load_to_duckdb >> run_dbt_models >> run_dbt_tests
"""

import subprocess
import sys
from datetime import datetime, timedelta

import duckdb
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

default_args = {
    "owner": "data_engineer",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

DUCKDB_PATH = "/opt/airflow/data/warehouse.duckdb"
DBT_DIR = "/opt/airflow/dbt"


def generate_daily_data(**context):
    """Insert daily order data into PostgreSQL"""
    sys.path.insert(0, "/opt/airflow/data_generator")
    from config import Config
    from generate_data import run_daily

    execution_date = context["ds"]  # YYYY-MM-DD
    run_daily(Config(), target_date=execution_date)


def load_to_duckdb(**context):
    """Copy raw data from PostgreSQL to DuckDB"""
    import os
    import pandas as pd
    from sqlalchemy import create_engine

    pg_url = (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_HOST', 'postgres')}:5432/{os.getenv('POSTGRES_DB')}"
    )
    pg_engine = create_engine(pg_url)
    conn = duckdb.connect(DUCKDB_PATH)

    conn.execute("CREATE SCHEMA IF NOT EXISTS raw")

    tables = ["customers", "products", "orders", "order_items"]
    for table in tables:
        df = pd.read_sql(f"SELECT * FROM raw.{table}", pg_engine)
        conn.execute(f"CREATE OR REPLACE TABLE raw.{table} AS SELECT * FROM df")
        print(f"✅ {table}: {len(df)} rows loaded into DuckDB")

    conn.close()
    pg_engine.dispose()


def run_dbt_models(**context):
    """Run dbt transformation models"""
    result = subprocess.run(
        ["dbt", "run", "--profiles-dir", DBT_DIR, "--project-dir", DBT_DIR],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise Exception("dbt run failed!")


def run_dbt_tests(**context):
    """Run dbt data quality tests"""
    result = subprocess.run(
        ["dbt", "test", "--profiles-dir", DBT_DIR, "--project-dir", DBT_DIR],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise Exception("dbt test failed!")


with DAG(
    dag_id="ecommerce_daily_pipeline",
    description="E-Commerce daily data pipeline",
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval="@daily",
    catchup=False,
    tags=["ecommerce", "dbt", "duckdb"],
) as dag:

    t1 = PythonOperator(
        task_id="generate_daily_data",
        python_callable=generate_daily_data,
    )

    t2 = PythonOperator(
        task_id="load_to_duckdb",
        python_callable=load_to_duckdb,
    )

    t3 = PythonOperator(
        task_id="run_dbt_models",
        python_callable=run_dbt_models,
    )

    t4 = PythonOperator(
        task_id="run_dbt_tests",
        python_callable=run_dbt_tests,
    )

    t1 >> t2 >> t3 >> t4
