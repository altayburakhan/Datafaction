"""
E-Commerce Data Generator
Usage:
  python generate_data.py --mode full      # Initial load: generate all data
  python generate_data.py --mode daily     # Daily: generate new orders only
  python generate_data.py --mode daily --date 2024-01-15  # Specific date
"""

import argparse
import logging
import random
import uuid
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from faker import Faker
from sqlalchemy import create_engine, text

from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)
fake = Faker(['en_US', 'tr_TR'])
config = Config()


def get_engine():
    return create_engine(config.db_url)


def create_schema(engine):
    """Create raw schema and tables"""
    sql = """
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
        order_id        VARCHAR(36) PRIMARY KEY,
        customer_id     VARCHAR(36) REFERENCES raw.customers(customer_id),
        order_date      TIMESTAMP,
        status          VARCHAR(50),
        shipping_city   VARCHAR(100),
        shipping_country VARCHAR(100),
        total_amount    NUMERIC(10, 2),
        discount_pct    NUMERIC(5, 2) DEFAULT 0,
        created_at      TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS raw.order_items (
        item_id         VARCHAR(36) PRIMARY KEY,
        order_id        VARCHAR(36) REFERENCES raw.orders(order_id),
        product_id      VARCHAR(36) REFERENCES raw.products(product_id),
        quantity        INTEGER,
        unit_price      NUMERIC(10, 2),
        total_price     NUMERIC(10, 2),
        created_at      TIMESTAMP DEFAULT NOW()
    );
    """
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    logger.info("Schema and tables created successfully")


def generate_customers() -> pd.DataFrame:
    """Generate customer records"""
    logger.info(f"Generating {config.n_customers} customers...")
    rows = []
    start = datetime.strptime(config.start_date, "%Y-%m-%d")
    end = datetime.strptime(config.end_date, "%Y-%m-%d")

    for _ in range(config.n_customers):
        signup = start + timedelta(days=random.randint(0, (end - start).days))
        rows.append({
            "customer_id": str(uuid.uuid4()),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.unique.email(),
            "phone": fake.phone_number()[:50],
            "city": fake.city(),
            "country": fake.country_code(),
            "signup_date": signup.date(),
            "is_active": random.random() > 0.05,
        })
    df = pd.DataFrame(rows)
    logger.info(f"{len(df)} customers generated")
    return df


def generate_products() -> pd.DataFrame:
    """Generate product records"""
    logger.info(f"Generating {config.n_products} products...")
    rows = []
    for _ in range(config.n_products):
        category = random.choice(config.categories)
        unit_price = round(random.uniform(5.0, 500.0), 2)
        rows.append({
            "product_id": str(uuid.uuid4()),
            "product_name": fake.catch_phrase()[:200],
            "category": category,
            "subcategory": fake.word().capitalize(),
            "unit_price": unit_price,
            "cost_price": round(unit_price * random.uniform(0.4, 0.7), 2),
            "stock_quantity": random.randint(0, 1000),
            "is_active": random.random() > 0.1,
        })
    df = pd.DataFrame(rows)
    logger.info(f"{len(df)} products generated")
    return df


def generate_orders(
    customer_ids: list,
    product_ids: list,
    n_orders: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate orders and order items"""
    logger.info(f"Generating {n_orders} orders...")

    start = datetime.strptime(start_date or config.start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date or config.end_date, "%Y-%m-%d")
    statuses = ["completed", "completed", "completed", "pending", "cancelled", "refunded"]

    orders, items = [], []
    for _ in range(n_orders):
        order_id = str(uuid.uuid4())
        order_date = start + timedelta(
            seconds=random.randint(0, int((end - start).total_seconds()))
        )
        n_items = random.randint(1, 5)
        order_products = random.sample(product_ids, min(n_items, len(product_ids)))

        total = 0
        for prod_id in order_products:
            qty = random.randint(1, 4)
            price = round(random.uniform(5.0, 500.0), 2)
            line_total = round(qty * price, 2)
            total += line_total
            items.append({
                "item_id": str(uuid.uuid4()),
                "order_id": order_id,
                "product_id": prod_id,
                "quantity": qty,
                "unit_price": price,
                "total_price": line_total,
            })

        discount = round(random.choice([0, 0, 0, 5, 10, 15, 20]), 2)
        orders.append({
            "order_id": order_id,
            "customer_id": random.choice(customer_ids),
            "order_date": order_date,
            "status": random.choice(statuses),
            "shipping_city": fake.city(),
            "shipping_country": fake.country_code(),
            "total_amount": round(total * (1 - discount / 100), 2),
            "discount_pct": discount,
        })

    logger.info(f"{len(orders)} orders and {len(items)} items generated")
    return pd.DataFrame(orders), pd.DataFrame(items)


def load_to_postgres(df: pd.DataFrame, table: str, engine, schema: str = "raw"):
    """Load DataFrame into PostgreSQL"""
    df.to_sql(
        name=table,
        con=engine,
        schema=schema,
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi",
    )
    logger.info(f"{len(df)} rows loaded into raw.{table}")


def run_full(engine):
    """Full load: generate and load all data"""
    create_schema(engine)

    customers = generate_customers()
    load_to_postgres(customers, "customers", engine)

    products = generate_products()
    load_to_postgres(products, "products", engine)

    customer_ids = customers["customer_id"].tolist()
    product_ids = products["product_id"].tolist()

    orders, items = generate_orders(customer_ids, product_ids, config.n_orders)
    load_to_postgres(orders, "orders", engine)
    load_to_postgres(items, "order_items", engine)

    logger.info("Full load completed successfully!")


def run_daily(engine, target_date: Optional[str] = None):
    """Incremental daily load"""
    if not target_date:
        target_date = datetime.now().strftime("%Y-%m-%d")

    next_date = (datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

    with engine.connect() as conn:
        customer_ids = [r[0] for r in conn.execute(text("SELECT customer_id FROM raw.customers")).fetchall()]
        product_ids = [r[0] for r in conn.execute(text("SELECT product_id FROM raw.products")).fetchall()]

    orders, items = generate_orders(
        customer_ids, product_ids,
        config.n_daily_orders,
        start_date=target_date,
        end_date=next_date,
    )
    load_to_postgres(orders, "orders", engine)
    load_to_postgres(items, "order_items", engine)
    logger.info(f"Daily load completed for {target_date}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["full", "daily"], default="full")
    parser.add_argument("--date", type=str, default=None, help="Date in YYYY-MM-DD format")
    args = parser.parse_args()

    engine = get_engine()
    if args.mode == "full":
        run_full(engine)
    else:
        run_daily(engine, args.date)
