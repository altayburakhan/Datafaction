1- Bir guncellemeyi githuba push ederken tum imza bana(altayburakhan) ait olmali claude gormek istemiyorum.
2- Bir kod yazacagin zaman yapilabiliyorsa unit testini de yaz, Uretilen kodlarin baslarina commentler ekle ingilizce.

# Datafaction — AI Agents Layer (MVP)

This document defines the minimal AI/LLM extension layer for the Datafaction project.

The goal is NOT to build a complex AI system, but to demonstrate:
- data understanding
- insight generation
- basic decision support

All components must be:
- free or open-source
- run locally if possible
- optional (project must still work without LLM)

---

# 1. DESIGN PRINCIPLE

We extend the existing pipeline:

Raw Data → dbt marts → Streamlit dashboards

NEW:

dbt marts → AI Agent Layer → Insights / Recommendations

The agent layer is read-only.

It does NOT modify data.

---

# 2. AGENT ARCHITECTURE

We define 3 lightweight agents:

---

## 2.1 Insight Agent (core MVP)

### Purpose
Generate human-readable insights from dbt marts.

### Input:
- mart_sales_daily
- mart_customer_segments
- mart_product_performance

### Output:
- bullet-point insights
- trends
- anomalies

### Example output:
- Revenue increased 12% week-over-week
- Electronics category is the main growth driver
- Customer churn risk increased in At Risk segment

### Implementation:
- Python script
- optional LLM (OpenAI / local model)
- fallback: rule-based insights

---

## 2.2 Query Agent (natural language → SQL)

### Purpose
Allow users to ask questions in plain English.

### Example:
User:
"Which product has highest revenue?"

Agent:
→ converts to SQL on mart tables
→ returns result + explanation

### Stack:
- dbt marts as context
- SQL generator (LLM optional)

---

## 2.3 Recommendation Agent (advanced MVP+)

### Purpose
Suggest business actions.

### Input:
- RFM segments
- revenue trends
- product performance

### Output:
- business recommendations

### Example:
- "Offer discount to At Risk customers"
- "Focus marketing on Electronics category"
- "Reduce inventory for low-margin products"

---

# 3. LLM USAGE POLICY

To keep cost = 0:

## Default mode (no LLM):
- rule-based heuristics
- SQL aggregations

## Optional mode (LLM enabled):
- OpenAI API (user optional key)
- or local models (Ollama)

System must work without LLM.

---

# 4. DATA ACCESS LAYER

Agents can only access:

- DuckDB warehouse
- dbt marts schema

No direct access to:
- raw PostgreSQL
- Airflow internals

This ensures clean abstraction.

---

# 5. INSIGHT ENGINE (RULE BASED BASELINE)

Before LLM, implement:

- revenue growth % calculation
- top/bottom product detection
- segment movement tracking
- anomaly detection (simple z-score or threshold)

This ensures "LLM is enhancement, not dependency"

---

# 6. FUTURE EXTENSIONS (NOT MVP)

- real-time streaming insights (Kafka)
- vector database memory layer
- multi-agent collaboration
- automated marketing campaign generator

---

# 7. SUCCESS CRITERIA

This layer is successful if:

- A user can ask a question in natural language
- System returns structured answer
- System works without LLM
- Insights match dbt mart data

---