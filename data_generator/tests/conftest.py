import random
import uuid
import pytest

from generators import generate_orders

START = "2022-01-01"
END = "2024-12-31"
CATEGORIES = ["Electronics", "Clothing", "Books"]

@pytest.fixture(scope="session")
def fake_customer_ids():
    return [str(uuid.uuid4()) for _ in range(20)]

@pytest.fixture(scope="session")
def fake_product_prices():
    return {str(uuid.uuid4()): round(random.uniform(5.0, 500.0), 2) for _ in range(10)}

@pytest.fixture(scope="session")
def sample_orders(fake_customer_ids, fake_product_prices):
    orders, items = generate_orders(fake_customer_ids, fake_product_prices, 30, START, END)
    return orders, items
