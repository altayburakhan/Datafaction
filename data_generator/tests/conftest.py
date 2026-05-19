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
def fake_product_ids():
    return [str(uuid.uuid4()) for _ in range(10)]

@pytest.fixture(scope="session")
def sample_orders(fake_customer_ids, fake_product_ids):
    orders, items = generate_orders(fake_customer_ids, fake_product_ids, 30, START, END)
    return orders, items
