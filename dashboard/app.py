import streamlit as st

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🛒 E-Commerce Sales Analytics")
st.markdown("""
Welcome! Select an analysis page from the left menu:

- 📈 **Sales Overview** — Daily/weekly revenue trends and KPIs
- 📦 **Product Analysis** — Top products and category breakdown
- 👥 **Customer Segments** — RFM-based customer segmentation
- 🤖 **AI Insights** — Automated trends, anomalies, and recommendations
""")

with st.sidebar:
    st.markdown("### 🔗 Links")
    st.markdown("[GitHub Repo](https://github.com/altayburakhan/Datafaction)")
    st.markdown("---")
    st.markdown("**Stack:** Python · dbt · Airflow · DuckDB")
