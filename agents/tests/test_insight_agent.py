# Tests for insight_agent rule-based logic.
# All tests use synthetic DataFrames — no DuckDB connection required.

import pandas as pd
import pytest

from agents.insight_agent import (
    Insight,
    _anomaly_insights,
    _customer_insights,
    _product_insights,
    _revenue_insights,
)


# --- Helpers ---

def make_sales(net_revenues: list[float], cancellation_rates: list[float] | None = None) -> pd.DataFrame:
    n = len(net_revenues)
    if cancellation_rates is None:
        cancellation_rates = [2.0] * n
    dates = pd.date_range("2023-01-01", periods=n)
    growth = [None] + [
        (net_revenues[i] - net_revenues[i - 1]) / net_revenues[i - 1] * 100
        for i in range(1, n)
    ]
    return pd.DataFrame({
        "date": dates,
        "net_revenue": net_revenues,
        "revenue_growth_pct": growth,
        "cancellation_rate_pct": cancellation_rates,
    })


def make_products(**kwargs) -> pd.DataFrame:
    defaults = {
        "product_name": ["A", "B", "C"],
        "category": ["Electronics", "Clothing", "Electronics"],
        "net_revenue": [1000.0, 500.0, 750.0],
        "gross_profit": [300.0, 150.0, 200.0],
        "refund_rate_pct": [2.0, 3.0, 1.0],
    }
    defaults.update(kwargs)
    return pd.DataFrame(defaults)


def make_customers(segments: list[str]) -> pd.DataFrame:
    return pd.DataFrame({"segment": segments})


# --- Revenue insights ---

class TestRevenueInsights:
    def test_insufficient_data_returns_empty(self):
        df = make_sales([100.0] * 10)
        assert _revenue_insights(df) == []

    def test_detects_growth(self):
        prior = [100.0] * 7
        recent = [120.0] * 7  # +20% WoW
        df = make_sales(prior + recent)
        insights = _revenue_insights(df)
        assert any(i.severity == "info" and "grew" in i.message for i in insights)

    def test_detects_drop(self):
        prior = [200.0] * 7
        recent = [100.0] * 7  # -50% WoW
        df = make_sales(prior + recent)
        insights = _revenue_insights(df)
        assert any(i.severity == "warning" and "dropped" in i.message for i in insights)

    def test_stable_revenue_is_info(self):
        df = make_sales([100.0] * 14)
        insights = _revenue_insights(df)
        assert any("stable" in i.message for i in insights)

    def test_elevated_cancellation_rate_is_warning(self):
        # Overall avg ~2%, recent week ~8%
        normal = [2.0] * 30
        elevated = [8.0] * 7
        df = make_sales([100.0] * 37, cancellation_rates=normal + elevated)
        insights = _revenue_insights(df)
        assert any("ancellation" in i.message and i.severity == "warning" for i in insights)


# --- Anomaly insights ---

class TestAnomalyInsights:
    def test_insufficient_data_returns_empty(self):
        df = make_sales([100.0] * 5)
        assert _anomaly_insights(df) == []

    def test_detects_spike_anomaly(self):
        # 28 normal days + 1 massive spike at the end
        normal = [0.0] * 28
        spike = [999.0]
        revenues = [100.0] * 29
        df = make_sales(revenues)
        df["revenue_growth_pct"] = normal + spike
        insights = _anomaly_insights(df)
        assert any(i.severity == "alert" and "spike" in i.message for i in insights)

    def test_no_anomaly_in_flat_data(self):
        df = make_sales([100.0] * 30)
        # All growth values are 0 — std is 0, no anomaly
        assert _anomaly_insights(df) == []


# --- Product insights ---

class TestProductInsights:
    def test_empty_products_returns_empty(self):
        df = pd.DataFrame(columns=["product_name", "category", "net_revenue", "gross_profit", "refund_rate_pct"])
        assert _product_insights(df) == []

    def test_returns_top3_insight(self):
        df = make_products()
        insights = _product_insights(df)
        assert any("Top 3" in i.message for i in insights)

    def test_returns_best_category_insight(self):
        df = make_products()
        insights = _product_insights(df)
        assert any("Electronics" in i.message for i in insights)

    def test_high_refund_rate_is_warning(self):
        df = make_products(refund_rate_pct=[15.0, 3.0, 1.0])
        insights = _product_insights(df)
        assert any(i.severity == "warning" and "efund" in i.message for i in insights)

    def test_no_warning_for_low_refund_rate(self):
        df = make_products(refund_rate_pct=[2.0, 3.0, 1.0])
        insights = _product_insights(df)
        assert not any("efund" in i.message and i.severity == "warning" for i in insights)


# --- Customer insights ---

class TestCustomerInsights:
    def test_empty_customers_returns_empty(self):
        df = pd.DataFrame(columns=["segment"])
        assert _customer_insights(df) == []

    def test_strong_retention_is_info(self):
        segments = ["Champions"] * 25 + ["Loyal Customers"] * 20 + ["Lost"] * 5
        df = make_customers(segments)
        insights = _customer_insights(df)
        assert any("strong retention" in i.message for i in insights)

    def test_high_at_risk_is_warning(self):
        segments = ["At Risk"] * 20 + ["Lost"] * 15 + ["Champions"] * 15
        df = make_customers(segments)
        insights = _customer_insights(df)
        assert any(i.severity == "warning" and "At Risk" in i.message for i in insights)

    def test_low_champions_is_warning(self):
        segments = ["Potential Loyalists"] * 80 + ["Champions"] * 5 + ["Loyal Customers"] * 15
        df = make_customers(segments)
        insights = _customer_insights(df)
        assert any("retention needs attention" in i.message for i in insights)
