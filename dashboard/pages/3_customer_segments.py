import duckdb
import plotly.express as px
import streamlit as st

DUCKDB_PATH = "/data/warehouse.duckdb"

st.set_page_config(page_title="Customer Segments", layout="wide")
st.title("👥 Customer Segments — RFM Analysis")


@st.cache_data(ttl=300)
def load_segments():
    conn = duckdb.connect(DUCKDB_PATH, read_only=True)
    df = conn.execute("SELECT * FROM main_marts.mart_customer_segments").fetchdf()
    conn.close()
    return df


df = load_segments()

# KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("👥 Total Customers", len(df))
k2.metric("🏆 Champions", len(df[df["segment"] == "Champions"]))
k3.metric("⚠️ At Risk", len(df[df["segment"] == "At Risk"]))
k4.metric("💸 Avg LTV", f"${df['monetary'].mean():,.2f}")

st.markdown("---")

col1, col2 = st.columns(2)

# Segment distribution
seg_counts = df["segment"].value_counts().reset_index()
seg_counts.columns = ["segment", "count"]
fig1 = px.bar(seg_counts, x="segment", y="count",
              title="Segment Distribution (Customer Count)",
              color="segment")
col1.plotly_chart(fig1, use_container_width=True)

# Revenue by segment
seg_rev = df.groupby("segment")["monetary"].sum().reset_index()
fig2 = px.pie(seg_rev, values="monetary", names="segment",
              title="Total Revenue by Segment")
col2.plotly_chart(fig2, use_container_width=True)

# RFM Scatter
fig3 = px.scatter(
    df, x="recency_days", y="frequency",
    size="monetary", color="segment",
    title="RFM Distribution (Recency vs Frequency)",
    labels={"recency_days": "Days Since Last Order", "frequency": "Order Frequency"},
    hover_name="full_name",
)
st.plotly_chart(fig3, use_container_width=True)
