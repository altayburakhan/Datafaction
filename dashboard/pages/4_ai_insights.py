import sys

import streamlit as st

sys.path.insert(0, "/app")

from agents.insight_agent import generate_insights

st.set_page_config(page_title="AI Insights", layout="wide")
st.title("🤖 AI Insights")
st.caption("Rule-based insights generated from dbt mart tables. No LLM required.")

SEVERITY_CONFIG = {
    "info": ("🟢", "success"),
    "warning": ("🟡", "warning"),
    "alert": ("🔴", "error"),
}

CATEGORY_LABELS = {
    "revenue": "📈 Revenue",
    "product": "📦 Products",
    "customer": "👥 Customers",
    "anomaly": "⚠️ Anomalies",
}

try:
    insights = generate_insights()

    if not insights:
        st.info("No insights available yet. Run the Airflow pipeline first.")
    else:
        # Summary row: count by severity
        alerts = sum(1 for i in insights if i.severity == "alert")
        warnings = sum(1 for i in insights if i.severity == "warning")
        infos = sum(1 for i in insights if i.severity == "info")

        c1, c2, c3 = st.columns(3)
        c1.metric("🟢 Info", infos)
        c2.metric("🟡 Warnings", warnings)
        c3.metric("🔴 Alerts", alerts)

        st.markdown("---")

        # Group by category
        by_category: dict = {}
        for ins in insights:
            by_category.setdefault(ins.category, []).append(ins)

        for cat, cat_insights in by_category.items():
            st.subheader(CATEGORY_LABELS.get(cat, cat))
            for ins in cat_insights:
                icon, msg_type = SEVERITY_CONFIG[ins.severity]
                msg = f"{icon} {ins.message}"
                if msg_type == "error":
                    st.error(msg)
                elif msg_type == "warning":
                    st.warning(msg)
                else:
                    st.success(msg)
            st.markdown("---")

except Exception as e:
    st.error(f"Could not load insights: {e}")
    st.caption("Make sure the Airflow pipeline has run at least once to populate DuckDB.")
