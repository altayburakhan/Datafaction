# E-Commerce Sales Pipeline

Junior-Mid seviye Data Engineering portfolyo projesi.

Sahte e-ticaret verisi üretiminden dashboard'a kadar tam pipeline:
**PostgreSQL → Airflow → dbt → DuckDB → Streamlit**

## Teknoloji Stack

- **Veri Üretimi:** Python 3.11 + Faker
- **Ham Depolama:** PostgreSQL 15
- **Orchestration:** Apache Airflow 2.8
- **Transformation:** dbt-core 1.7 + dbt-duckdb
- **Data Warehouse:** DuckDB
- **Dashboard:** Streamlit
- **Konteyner:** Docker + Docker Compose
- **CI:** GitHub Actions

## Kurulum

```bash
cp .env.example .env
make init
make up
```
