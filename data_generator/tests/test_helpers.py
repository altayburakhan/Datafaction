from unittest.mock import MagicMock, patch

import pandas as pd

from helpers import create_schema, fetch_ids, load_table


class TestLoadTable:
    def test_calls_to_sql_with_correct_args(self):
        df = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})
        engine = MagicMock()

        with patch.object(df, "to_sql") as mock_to_sql:
            load_table(df, "customers", engine)
            mock_to_sql.assert_called_once_with(
                name="customers",
                con=engine,
                schema="raw",
                if_exists="append",
                index=False,
                chunksize=1000,
                method="multi",
            )

    def test_custom_schema(self):
        df = pd.DataFrame({"id": [1]})
        engine = MagicMock()

        with patch.object(df, "to_sql") as mock_to_sql:
            load_table(df, "mytable", engine, schema="staging")
            assert mock_to_sql.call_args.kwargs["schema"] == "staging"

    def test_empty_dataframe_still_calls_to_sql(self):
        df = pd.DataFrame(columns=["id", "name"])
        engine = MagicMock()

        with patch.object(df, "to_sql") as mock_to_sql:
            load_table(df, "customers", engine)
            mock_to_sql.assert_called_once()


class TestFetchIds:
    def test_returns_list_of_ids(self):
        engine = MagicMock()
        conn = engine.connect.return_value.__enter__.return_value
        conn.execute.return_value.fetchall.return_value = [("id-1",), ("id-2",), ("id-3",)]

        result = fetch_ids(engine, "customers", "customer_id")

        assert result == ["id-1", "id-2", "id-3"]

    def test_returns_empty_list_when_no_rows(self):
        engine = MagicMock()
        conn = engine.connect.return_value.__enter__.return_value
        conn.execute.return_value.fetchall.return_value = []

        result = fetch_ids(engine, "customers", "customer_id")

        assert result == []

    def test_uses_correct_table_and_column(self):
        engine = MagicMock()
        conn = engine.connect.return_value.__enter__.return_value
        conn.execute.return_value.fetchall.return_value = []

        fetch_ids(engine, "products", "product_id")

        executed_sql = str(conn.execute.call_args[0][0])
        assert "products" in executed_sql
        assert "product_id" in executed_sql


class TestCreateSchema:
    def test_executes_sql(self):
        engine = MagicMock()
        ctx = engine.begin.return_value.__enter__.return_value

        create_schema(engine)

        ctx.execute.assert_called_once()

    def test_sql_contains_all_tables(self):
        engine = MagicMock()
        ctx = engine.begin.return_value.__enter__.return_value

        create_schema(engine)

        executed_sql = str(ctx.execute.call_args[0][0])
        for table in ["customers", "products", "orders", "order_items"]:
            assert table in executed_sql
