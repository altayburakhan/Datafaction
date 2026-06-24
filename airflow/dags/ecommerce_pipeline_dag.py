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


def _get_watermark(conn, table: str):
    """Return MAX(created_at) from a DuckDB raw table, or None if table doesn't exist yet."""
    try:
        row = conn.execute(f"SELECT MAX(created_at) FROM raw.{table}").fetchone()
        return row[0]
    except Exception:
        return None


def load_to_duckdb(**context):
    """Copy raw data from PostgreSQL to DuckDB.

    customers and products are small and can change (is_active, price), so full
    refresh is simpler and safer. orders and order_items only grow, so we append
    only new rows using created_at as the watermark.
    """
    import os
    import pandas as pd
    from sqlalchemy import create_engine

    pg_url = (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_HOST', 'postgres')}:5432/{os.getenv('POSTGRES_DB')}"
    )
    pg_engine = create_engine(pg_url)
    conn = duckdb.connect(DUCKDB_PATH)
    try:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")

        for table in ["customers", "products"]:
            df = pd.read_sql(f"SELECT * FROM raw.{table}", pg_engine)
            conn.execute(f"CREATE OR REPLACE TABLE raw.{table} AS SELECT * FROM df")
            print(f"Loaded {len(df)} rows into DuckDB raw.{table} (full refresh)")

        for table in ["orders", "order_items"]:
            watermark = _get_watermark(conn, table)
            if watermark is None:
                df = pd.read_sql(f"SELECT * FROM raw.{table}", pg_engine)
                conn.execute(f"CREATE OR REPLACE TABLE raw.{table} AS SELECT * FROM df")
                print(f"Loaded {len(df)} rows into DuckDB raw.{table} (initial load)")
            else:
                df = pd.read_sql(
                    f"SELECT * FROM raw.{table} WHERE created_at > %(wm)s",
                    pg_engine,
                    params={"wm": watermark},
                )
                if not df.empty:
                    conn.execute(f"INSERT INTO raw.{table} SELECT * FROM df")
                print(f"Loaded {len(df)} new rows into DuckDB raw.{table} (incremental)")
    finally:
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
    start_date=datetime(2024, 1, 1),
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
