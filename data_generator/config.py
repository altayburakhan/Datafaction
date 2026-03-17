import os
from dataclasses import dataclass


@dataclass
class Config:
    # PostgreSQL
    pg_host: str = os.getenv("POSTGRES_HOST", "localhost")
    pg_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    pg_user: str = os.getenv("POSTGRES_USER", "ecommerce_user")
    pg_password: str = os.getenv("POSTGRES_PASSWORD", "ecommerce_pass")
    pg_db: str = os.getenv("POSTGRES_DB", "ecommerce_raw")

    # Data sizes
    n_customers: int = 10_000
    n_products: int = 500
    n_orders: int = 50_000
    n_daily_orders: int = 100

    # Date range
    start_date: str = "2022-01-01"
    end_date: str = "2024-12-31"

    # Product categories
    categories: list = None

    def __post_init__(self):
        self.categories = [
            "Electronics", "Clothing", "Home & Garden",
            "Sports", "Books", "Toys", "Beauty", "Food & Grocery"
        ]

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.pg_user}:{self.pg_password}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        )
