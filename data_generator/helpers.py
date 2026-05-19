import logging

import pandas as pd
from sqlalchemy import create_engine, text

from config import Config

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id     VARCHAR(36) PRIMARY KEY,
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    email           VARCHAR(200) UNIQUE,
    phone           VARCHAR(50),
    city            VARCHAR(100),
    country         VARCHAR(100),
    signup_date     DATE,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw.products (
    product_id      VARCHAR(36) PRIMARY KEY,
    product_name    VARCHAR(200),
    category        VARCHAR(100),
    subcategory     VARCHAR(100),
    unit_price      NUMERIC(10, 2),
    cost_price      NUMERIC(10, 2),
    stock_quantity  INTEGER,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw.orders (
    order_id         VARCHAR(36) PRIMARY KEY,
    customer_id      VARCHAR(36) REFERENCES raw.customers(customer_id),
    order_date       TIMESTAMP,
    status           VARCHAR(50),
    shipping_city    VARCHAR(100),
    shipping_country VARCHAR(100),
    total_amount     NUMERIC(10, 2),
    discount_pct     NUMERIC(5, 2) DEFAULT 0,
    created_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw.order_items (
    item_id     VARCHAR(36) PRIMARY KEY,
    order_id    VARCHAR(36) REFERENCES raw.orders(order_id),
    product_id  VARCHAR(36) REFERENCES raw.products(product_id),
    quantity    INTEGER,
    unit_price  NUMERIC(10, 2),
    total_price NUMERIC(10, 2),
    created_at  TIMESTAMP DEFAULT NOW()
);
"""


def get_engine(config: Config):
    return create_engine(config.db_url)


def create_schema(engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(SCHEMA_SQL))
    logger.info("Schema and tables ready")


def truncate_all(engine) -> None:
    # FK sırasına göre tersten temizle
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE raw.order_items, raw.orders, raw.products, raw.customers RESTART IDENTITY CASCADE"))
    logger.info("All raw tables truncated")


def load_table(df: pd.DataFrame, table: str, engine, schema: str = "raw") -> None:
    df.to_sql(
        name=table,
        con=engine,
        schema=schema,
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi",
    )
    logger.info(f"Loaded {len(df)} rows into {schema}.{table}")


def fetch_ids(engine, table: str, id_column: str) -> list:
    with engine.connect() as conn:
        rows = conn.execute(text(f"SELECT {id_column} FROM raw.{table}")).fetchall()
    return [r[0] for r in rows]
