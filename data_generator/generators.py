import random
import uuid
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

fake = Faker(["en_US", "tr_TR"])

ORDER_STATUSES = ["completed", "completed", "completed", "pending", "cancelled", "refunded"]
DISCOUNT_OPTIONS = [0, 0, 0, 5, 10, 15, 20]


def _random_date(start: datetime, end: datetime) -> datetime:
    delta_seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=random.randint(0, delta_seconds))


def generate_customers(n: int, start_date: str, end_date: str) -> pd.DataFrame:
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    rows = [
        {
            "customer_id": str(uuid.uuid4()),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.unique.email(),
            "phone": fake.phone_number()[:50],
            "city": fake.city(),
            "country": fake.country_code(),
            "signup_date": _random_date(start, end).date(),
            "is_active": random.random() > 0.05,
        }
        for _ in range(n)
    ]
    return pd.DataFrame(rows)


def generate_products(n: int, categories: list) -> pd.DataFrame:
    rows = []
    for _ in range(n):
        unit_price = round(random.uniform(5.0, 500.0), 2)
        rows.append(
            {
                "product_id": str(uuid.uuid4()),
                "product_name": fake.catch_phrase()[:200],
                "category": random.choice(categories),
                "subcategory": fake.word().capitalize(),
                "unit_price": unit_price,
                "cost_price": round(unit_price * random.uniform(0.4, 0.7), 2),
                "stock_quantity": random.randint(0, 1000),
                "is_active": random.random() > 0.1,
            }
        )
    return pd.DataFrame(rows)


def generate_orders(
    customer_ids: list,
    product_ids: list,
    n: int,
    start_date: str,
    end_date: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    orders, items = [], []
    for _ in range(n):
        order_id = str(uuid.uuid4())
        order_date = _random_date(start, end)
        selected_products = random.sample(product_ids, k=min(random.randint(1, 5), len(product_ids)))

        order_total = 0.0
        for product_id in selected_products:
            qty = random.randint(1, 4)
            price = round(random.uniform(5.0, 500.0), 2)
            line_total = round(qty * price, 2)
            order_total += line_total
            items.append(
                {
                    "item_id": str(uuid.uuid4()),
                    "order_id": order_id,
                    "product_id": product_id,
                    "quantity": qty,
                    "unit_price": price,
                    "total_price": line_total,
                }
            )

        discount = random.choice(DISCOUNT_OPTIONS)
        orders.append(
            {
                "order_id": order_id,
                "customer_id": random.choice(customer_ids),
                "order_date": order_date,
                "status": random.choice(ORDER_STATUSES),
                "shipping_city": fake.city(),
                "shipping_country": fake.country_code(),
                "total_amount": round(order_total * (1 - discount / 100), 2),
                "discount_pct": discount,
            }
        )

    return pd.DataFrame(orders), pd.DataFrame(items)
