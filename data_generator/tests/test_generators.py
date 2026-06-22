from datetime import date

import pytest

from generators import generate_customers, generate_orders, generate_products
from tests.conftest import CATEGORIES, END, START, fake_product_prices

CUSTOMER_COLUMNS = {
    "customer_id", "first_name", "last_name", "email",
    "phone", "city", "country", "signup_date", "is_active",
}
PRODUCT_COLUMNS = {
    "product_id", "product_name", "category", "subcategory",
    "unit_price", "cost_price", "stock_quantity", "is_active",
}
VALID_STATUSES = {"completed", "pending", "cancelled", "refunded"}


class TestGenerateCustomers:
    def test_returns_correct_count(self):
        df = generate_customers(10, START, END)
        assert len(df) == 10

    def test_has_required_columns(self):
        df = generate_customers(5, START, END)
        assert CUSTOMER_COLUMNS.issubset(df.columns)

    def test_customer_ids_are_unique(self):
        df = generate_customers(50, START, END)
        assert df["customer_id"].nunique() == 50

    def test_emails_are_unique(self):
        df = generate_customers(50, START, END)
        assert df["email"].nunique() == 50

    def test_is_active_is_boolean(self):
        df = generate_customers(20, START, END)
        assert df["is_active"].dtype == bool

    def test_signup_date_within_range(self):
        df = generate_customers(50, START, END)
        assert df["signup_date"].min() >= date(2022, 1, 1)
        assert df["signup_date"].max() <= date(2024, 12, 31)

    def test_phone_max_50_chars(self):
        df = generate_customers(20, START, END)
        assert df["phone"].str.len().max() <= 50


class TestGenerateProducts:
    def test_returns_correct_count(self):
        df = generate_products(10, CATEGORIES)
        assert len(df) == 10

    def test_has_required_columns(self):
        df = generate_products(5, CATEGORIES)
        assert PRODUCT_COLUMNS.issubset(df.columns)

    def test_product_ids_are_unique(self):
        df = generate_products(30, CATEGORIES)
        assert df["product_id"].nunique() == 30

    def test_category_is_valid(self):
        df = generate_products(30, CATEGORIES)
        assert df["category"].isin(CATEGORIES).all()

    def test_unit_price_range(self):
        df = generate_products(50, CATEGORIES)
        assert (df["unit_price"] >= 5.0).all()
        assert (df["unit_price"] <= 500.0).all()

    def test_cost_price_less_than_unit_price(self):
        df = generate_products(50, CATEGORIES)
        assert (df["cost_price"] < df["unit_price"]).all()

    def test_stock_quantity_non_negative(self):
        df = generate_products(20, CATEGORIES)
        assert (df["stock_quantity"] >= 0).all()

    def test_product_name_max_200_chars(self):
        df = generate_products(20, CATEGORIES)
        assert df["product_name"].str.len().max() <= 200


class TestGenerateOrders:
    def test_order_count(self, fake_customer_ids, fake_product_prices):
        orders, _ = generate_orders(fake_customer_ids, fake_product_prices, 10, START, END)
        assert len(orders) == 10

    def test_returns_non_empty_dataframes(self, sample_orders):
        orders, items = sample_orders
        assert len(orders) > 0
        assert len(items) > 0

    def test_items_reference_valid_orders(self, sample_orders):
        orders, items = sample_orders
        assert items["order_id"].isin(orders["order_id"]).all()

    def test_items_reference_valid_products(self, sample_orders, fake_product_prices):
        _, items = sample_orders
        assert items["product_id"].isin(fake_product_prices.keys()).all()

    def test_orders_reference_valid_customers(self, sample_orders, fake_customer_ids):
        orders, _ = sample_orders
        assert orders["customer_id"].isin(fake_customer_ids).all()

    def test_order_ids_are_unique(self, sample_orders):
        orders, _ = sample_orders
        assert orders["order_id"].nunique() == len(orders)

    def test_item_ids_are_unique(self, sample_orders):
        _, items = sample_orders
        assert items["item_id"].nunique() == len(items)

    def test_valid_order_statuses(self, sample_orders):
        orders, _ = sample_orders
        assert orders["status"].isin(VALID_STATUSES).all()

    def test_total_amount_non_negative(self, sample_orders):
        orders, _ = sample_orders
        assert (orders["total_amount"] >= 0).all()

    def test_item_quantity_positive(self, sample_orders):
        _, items = sample_orders
        assert (items["quantity"] > 0).all()

    def test_item_unit_price_positive(self, sample_orders):
        _, items = sample_orders
        assert (items["unit_price"] > 0).all()

    def test_daily_mode_date_range(self, fake_customer_ids, fake_product_prices):
        orders, _ = generate_orders(fake_customer_ids, fake_product_prices, 20, "2024-01-15", "2024-01-16")
        assert orders["order_date"].dt.date.min() >= date(2024, 1, 15)
        assert orders["order_date"].dt.date.max() <= date(2024, 1, 16)

    def test_each_order_has_at_least_one_item(self, sample_orders):
        orders, items = sample_orders
        items_per_order = items.groupby("order_id").size()
        assert (items_per_order >= 1).all()
