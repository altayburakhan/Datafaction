# E-Commerce Sales Pipeline

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![dbt](https://img.shields.io/badge/dbt-1.7-orange?logo=dbt)
![Airflow](https://img.shields.io/badge/Airflow-2.8-017CEE?logo=apacheairflow)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![DuckDB](https://img.shields.io/badge/DuckDB-0.10-yellow)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-FF4B4B?logo=streamlit)

A junior-to-mid level Data Engineering portfolio project. Generates fake e-commerce data and builds a full pipeline from raw ingestion to an interactive dashboard.

## Architecture

```
Faker (Python)
     │
     ▼
PostgreSQL (raw schema)
     │
     ▼
Apache Airflow (orchestration)
     │
     ▼
DuckDB (data warehouse)
     │
     ▼
dbt (staging → intermediate → marts)
     │
     ▼
Streamlit (dashboard)
```

## Tech Stack

| Layer | Tool |
|---|---|
| Data Generation | Python 3.11 + Faker |
| Raw Storage | PostgreSQL 15 |
| Orchestration | Apache Airflow 2.8 |
| Transformation | dbt-core 1.7 + dbt-duckdb |
| Data Warehouse | DuckDB |
| Dashboard | Streamlit + Plotly |
| Infrastructure | Docker + Docker Compose |
| CI | GitHub Actions |

## Quick Start

```bash
git clone https://github.com/altayburakhan/Datafaction.git
cd Datafaction

cp .env.example .env        # Fill in your credentials
make init                   # Initialize Airflow DB + create admin user
make up                     # Start all services
make generate               # Generate full dataset (10k customers, 50k orders)
```

- Airflow UI → http://localhost:8080 (admin / admin)
- Dashboard → http://localhost:8501

## Project Structure

```
ecommerce-pipeline/
├── airflow/
│   └── dags/               # Airflow DAG definitions
├── data_generator/         # Faker-based data generation scripts
├── dbt/
│   └── models/
│       ├── staging/        # Raw → cleaned views
│       ├── intermediate/   # Enriched joins
│       └── marts/          # Business-ready tables
├── dashboard/
│   ├── app.py              # Streamlit entry point
│   └── pages/              # Sales / Product / Customer pages
├── docker-compose.yml
├── .env.example
└── Makefile
```

## dbt Models

| Model | Type | Description |
|---|---|---|
| `stg_customers` | view | Cleaned customer data |
| `stg_products` | view | Cleaned product data with margin |
| `stg_orders` | view | Cleaned orders with date parts |
| `stg_order_items` | view | Cleaned order line items |
| `int_orders_enriched` | view | Orders joined with customers and items |
| `mart_sales_daily` | table | Daily revenue, growth rate, cancellation rate |
| `mart_customer_segments` | table | RFM-based segmentation (Champions / Loyal / At Risk / Lost) |
| `mart_product_performance` | table | Revenue, units sold, refund rate per product |

## Useful Commands

```bash
make up         # Start all Docker services
make down       # Stop all services
make generate   # Run full data generation
make test       # Run dbt tests
make logs       # Tail Airflow scheduler logs
make clean      # Remove containers and volumes
```
