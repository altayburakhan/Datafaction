import duckdb
import plotly.express as px
import streamlit as st

DUCKDB_PATH = "/data/warehouse.duckdb"

st.set_page_config(page_title="Product Analysis", layout="wide")
st.title("📦 Product Analysis")


@st.cache_data(ttl=300)
def load_products():
    conn = duckdb.connect(DUCKDB_PATH, read_only=True)
    df = conn.execute("SELECT * FROM main_marts.mart_product_performance").fetchdf()
    conn.close()
    return df


df = load_products()

# Category filter
categories = ["All"] + sorted(df["category"].dropna().unique().tolist())
selected = st.selectbox("Filter by Category", categories)
if selected != "All":
    df = df[df["category"] == selected]

# KPIs
k1, k2, k3 = st.columns(3)
k1.metric("📦 Total Products", len(df))
k2.metric("💰 Total Revenue", f"${df['net_revenue'].sum():,.0f}")
k3.metric("📊 Avg Margin", f"{df['margin_pct'].mean():.1f}%")

st.markdown("---")

col1, col2 = st.columns(2)

# Top 10 products
top10 = df.nlargest(10, "net_revenue")
fig1 = px.bar(top10, x="net_revenue", y="product_name", orientation="h",
              title="Top 10 Products by Net Revenue", color="category")
col1.plotly_chart(fig1, use_container_width=True)

# Category pie chart
cat_rev = df.groupby("category")["net_revenue"].sum().reset_index()
fig2 = px.pie(cat_rev, values="net_revenue", names="category",
              title="Revenue Distribution by Category")
col2.plotly_chart(fig2, use_container_width=True)

# Revenue vs refund rate scatter
fig3 = px.scatter(
    df.dropna(subset=["refund_rate_pct", "net_revenue"]),
    x="net_revenue", y="refund_rate_pct",
    color="category", hover_name="product_name",
    title="Revenue vs. Refund Rate",
    labels={"net_revenue": "Net Revenue ($)", "refund_rate_pct": "Refund Rate (%)"}
)
st.plotly_chart(fig3, use_container_width=True)
