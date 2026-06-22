"""
Usage:
  python generate_data.py --mode full
  python generate_data.py --mode daily
  python generate_data.py --mode daily --date 2024-01-15
"""

import argparse
import logging
from datetime import datetime, timedelta

from config import Config
from generators import generate_customers, generate_orders, generate_products
from helpers import create_schema, fetch_ids, fetch_product_prices, get_engine, load_table, truncate_all

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_full(config: Config) -> None:
    engine = get_engine(config)
    create_schema(engine)
    truncate_all(engine)

    customers = generate_customers(config.n_customers, config.start_date, config.end_date)
    load_table(customers, "customers", engine)

    products = generate_products(config.n_products, config.categories)
    load_table(products, "products", engine)

    product_prices = products.set_index("product_id")["unit_price"].to_dict()
    orders, items = generate_orders(
        customer_ids=customers["customer_id"].tolist(),
        product_prices=product_prices,
        n=config.n_orders,
        start_date=config.start_date,
        end_date=config.end_date,
    )
    load_table(orders, "orders", engine)
    load_table(items, "order_items", engine)
    logger.info("Full load done")


def run_daily(config: Config, target_date: str | None = None) -> None:
    if not target_date:
        target_date = datetime.now().strftime("%Y-%m-%d")
    next_date = (datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

    engine = get_engine(config)
    customer_ids = fetch_ids(engine, "customers", "customer_id")
    product_prices = fetch_product_prices(engine)

    orders, items = generate_orders(
        customer_ids=customer_ids,
        product_prices=product_prices,
        n=config.n_daily_orders,
        start_date=target_date,
        end_date=next_date,
    )
    load_table(orders, "orders", engine)
    load_table(items, "order_items", engine)
    logger.info(f"Daily load done for {target_date}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["full", "daily"], default="full")
    parser.add_argument("--date", default=None)
    args = parser.parse_args()

    cfg = Config()
    if args.mode == "full":
        run_full(cfg)
    else:
        run_daily(cfg, args.date)
