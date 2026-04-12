import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

DUCKDB_PATH = "/data/warehouse.duckdb"

st.set_page_config(page_title="Sales Overview", layout="wide")
st.title("📈 Sales Overview")


@st.cache_data(ttl=300)
def load_sales():
    conn = duckdb.connect(DUCKDB_PATH, read_only=True)
    df = conn.execute("SELECT * FROM main_marts.mart_sales_daily ORDER BY date").fetchdf()
    conn.close()
    return df


df = load_sales()

# Date filter
col1, col2 = st.columns(2)
with col1:
    start = st.date_input("Start date", value=df["date"].min())
with col2:
    end = st.date_input("End date", value=df["date"].max())

df = df[(df["date"] >= pd.Timestamp(start)) & (df["date"] <= pd.Timestamp(end))]

# KPI cards
k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Total Revenue", f"${df['net_revenue'].sum():,.0f}")
k2.metric("🛒 Total Orders", f"{df['total_orders'].sum():,}")
k3.metric("👤 Unique Customers", f"{df['unique_customers'].sum():,}")
k4.metric("📦 Avg Order Value", f"${df['avg_order_value'].mean():,.2f}")

st.markdown("---")

# Revenue trend
fig1 = px.line(
    df, x="date", y="net_revenue",
    title="Daily Net Revenue Trend",
    labels={"net_revenue": "Net Revenue ($)", "date": "Date"},
    color_discrete_sequence=["#2ecc71"]
)
st.plotly_chart(fig1, use_container_width=True)

col1, col2 = st.columns(2)

# Monthly revenue
monthly = df.groupby(["year", "month"])["net_revenue"].sum().reset_index()
monthly["period"] = monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2)
fig2 = px.bar(monthly, x="period", y="net_revenue", title="Monthly Revenue")
col1.plotly_chart(fig2, use_container_width=True)

# Cancellation rate trend
fig3 = px.line(df, x="date", y="cancellation_rate_pct", title="Daily Cancellation Rate (%)")
col2.plotly_chart(fig3, use_container_width=True)
