"""
Insight Agent — rule-based insights from dbt mart tables.
Reads DuckDB mart schema and produces structured Insight objects.
No LLM required; statistical heuristics only.
"""

from dataclasses import dataclass
from typing import Literal

import duckdb
import pandas as pd

DUCKDB_PATH = "/data/warehouse.duckdb"
MARTS_SCHEMA = "main_marts"


@dataclass
class Insight:
    category: Literal["revenue", "product", "customer", "anomaly"]
    severity: Literal["info", "warning", "alert"]
    message: str
    value: float | None = None


# --- Data loading ---

def _load_marts(duckdb_path: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    conn = duckdb.connect(duckdb_path, read_only=True)
    sales = conn.execute(
        f"SELECT * FROM {MARTS_SCHEMA}.mart_sales_daily ORDER BY date"
    ).fetchdf()
    products = conn.execute(
        f"SELECT * FROM {MARTS_SCHEMA}.mart_product_performance"
    ).fetchdf()
    customers = conn.execute(
        f"SELECT * FROM {MARTS_SCHEMA}.mart_customer_segments"
    ).fetchdf()
    conn.close()
    return sales, products, customers


# --- Revenue insights ---

def _revenue_insights(sales: pd.DataFrame) -> list[Insight]:
    insights: list[Insight] = []

    if len(sales) < 14:
        return insights

    last7 = sales.tail(7)["net_revenue"].sum()
    prior7 = sales.iloc[-14:-7]["net_revenue"].sum()

    if prior7 > 0:
        wow_pct = (last7 - prior7) / prior7 * 100
        if wow_pct >= 10:
            insights.append(Insight(
                "revenue", "info",
                f"Revenue grew {wow_pct:.1f}% this week vs last week.", wow_pct
            ))
        elif wow_pct <= -10:
            insights.append(Insight(
                "revenue", "warning",
                f"Revenue dropped {abs(wow_pct):.1f}% this week vs last week.", wow_pct
            ))
        else:
            insights.append(Insight(
                "revenue", "info",
                f"Revenue is stable week-over-week ({wow_pct:+.1f}%).", wow_pct
            ))

    # Elevated cancellation rate vs historical average
    recent_cancel = sales.tail(7)["cancellation_rate_pct"].mean()
    overall_cancel = sales["cancellation_rate_pct"].mean()
    if recent_cancel > overall_cancel * 1.5 and recent_cancel > 5:
        insights.append(Insight(
            "revenue", "warning",
            f"Cancellation rate elevated this week: {recent_cancel:.1f}% (avg: {overall_cancel:.1f}%).",
            recent_cancel
        ))

    return insights


# --- Anomaly detection (z-score on daily revenue growth) ---

def _anomaly_insights(sales: pd.DataFrame) -> list[Insight]:
    insights: list[Insight] = []

    growth = sales["revenue_growth_pct"].dropna()
    if len(growth) < 10:
        return insights

    mean, std = growth.mean(), growth.std()
    if std == 0:
        return insights

    recent = sales.tail(7).dropna(subset=["revenue_growth_pct"])
    for _, row in recent.iterrows():
        z = (row["revenue_growth_pct"] - mean) / std
        if abs(z) > 2:
            direction = "spike" if z > 0 else "drop"
            date_str = pd.Timestamp(row["date"]).strftime("%Y-%m-%d")
            insights.append(Insight(
                "anomaly", "alert",
                f"Unusual revenue {direction} on {date_str}: "
                f"{row['revenue_growth_pct']:+.1f}% (z={z:.1f}).",
                float(row["revenue_growth_pct"])
            ))

    return insights


# --- Product insights ---

def _product_insights(products: pd.DataFrame) -> list[Insight]:
    insights: list[Insight] = []

    valid = products.dropna(subset=["net_revenue"]).query("net_revenue > 0")
    if valid.empty:
        return insights

    top3 = valid.nlargest(3, "net_revenue")["product_name"].tolist()
    insights.append(Insight(
        "product", "info",
        f"Top 3 products by revenue: {', '.join(top3)}."
    ))

    cat_profit = valid.groupby("category")["gross_profit"].sum()
    best_cat = cat_profit.idxmax()
    best_profit = cat_profit.max()
    insights.append(Insight(
        "product", "info",
        f"Highest gross profit category: {best_cat} (${best_profit:,.0f})."
    ))

    # Products with > 10% refund rate
    high_refund = valid[valid["refund_rate_pct"] > 10].nlargest(1, "refund_rate_pct")
    if not high_refund.empty:
        row = high_refund.iloc[0]
        insights.append(Insight(
            "product", "warning",
            f"High refund rate: '{row['product_name']}' at {row['refund_rate_pct']:.1f}%.",
            float(row["refund_rate_pct"])
        ))

    return insights


# --- Customer segment insights ---

def _customer_insights(customers: pd.DataFrame) -> list[Insight]:
    insights: list[Insight] = []

    if customers.empty:
        return insights

    total = len(customers)
    seg_pct = (customers["segment"].value_counts() / total * 100).to_dict()

    champions_loyal = seg_pct.get("Champions", 0) + seg_pct.get("Loyal Customers", 0)
    at_risk_lost = seg_pct.get("At Risk", 0) + seg_pct.get("Lost", 0)

    if champions_loyal >= 40:
        insights.append(Insight(
            "customer", "info",
            f"{champions_loyal:.1f}% of customers are Champions or Loyal — strong retention.",
            champions_loyal
        ))
    else:
        insights.append(Insight(
            "customer", "warning",
            f"Only {champions_loyal:.1f}% are Champions or Loyal customers — retention needs attention.",
            champions_loyal
        ))

    if at_risk_lost >= 30:
        insights.append(Insight(
            "customer", "warning",
            f"{at_risk_lost:.1f}% of customers are At Risk or Lost — consider re-engagement campaigns.",
            at_risk_lost
        ))
    else:
        insights.append(Insight(
            "customer", "info",
            f"{at_risk_lost:.1f}% of customers are At Risk or Lost.",
            at_risk_lost
        ))

    return insights


# --- Public API ---

def generate_insights(duckdb_path: str = DUCKDB_PATH) -> list[Insight]:
    """Load mart tables from DuckDB and return all rule-based insights."""
    sales, products, customers = _load_marts(duckdb_path)

    insights: list[Insight] = []
    insights.extend(_revenue_insights(sales))
    insights.extend(_anomaly_insights(sales))
    insights.extend(_product_insights(products))
    insights.extend(_customer_insights(customers))

    return insights
