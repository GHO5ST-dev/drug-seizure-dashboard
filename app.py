import streamlit as st
import plotly.express as px
import pandas as pd

from utils.data_loader import load_seizures, load_trade_finance, load_precursor_imports
from utils.styling import inject_base_css, page_header, PLOTLY_TEMPLATE, COLOR_SEQUENCE

st.set_page_config(
    page_title="Drug Seizure Intelligence Dashboard",
    page_icon="🛡️",
    layout="wide",
)
inject_base_css()

st.title("🛡️ Drug Seizure Intelligence Dashboard")
st.caption(
    "Law Enforcement Analytics Toolkit — NCB Seizure, Trade & Finance Data (2018–2024)"
)

st.info(
    "⚠️ **Data notice:** All figures shown are either drawn from publicly available "
    "NCB seizure data or, where noted (trade-finance module), are **simulated** for "
    "demonstration of money-laundering-pattern analytics. Replace files in `data/` "
    "with verified sources before operational use.",
    icon="⚠️",
)

seizures = load_seizures()
trade = load_trade_finance()
precursor = load_precursor_imports()

# ---------------------------------------------------------------------
# Top-line KPIs
# ---------------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Seizure Records", f"{len(seizures):,}")
with col2:
    st.metric("Total Quantity Seized (kg)", f"{seizures['quantity_kg'].sum():,.0f}")
with col3:
    st.metric("States/UTs Covered", seizures["state"].nunique())
with col4:
    flagged = int(trade["flagged"].sum())
    st.metric("Flagged Financial Transactions", f"{flagged:,}", help="Simulated data")
with col5:
    anomalies = int(precursor["is_anomaly"].sum())
    st.metric("Precursor Import Anomalies", anomalies)

st.divider()

# ---------------------------------------------------------------------
# Trend + drug mix overview
# ---------------------------------------------------------------------
left, right = st.columns([1.3, 1])

with left:
    st.subheader("National Seizure Trend (2018–2024)")
    trend = seizures.groupby("year")["quantity_kg"].sum().reset_index()
    fig = px.area(
        trend, x="year", y="quantity_kg",
        template=PLOTLY_TEMPLATE, color_discrete_sequence=COLOR_SEQUENCE,
        labels={"quantity_kg": "Quantity Seized (kg)", "year": "Year"},
    )
    fig.update_layout(height=380, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Top 5 States by Seizure Volume")
    top_states = (
        seizures.groupby("state")["quantity_kg"].sum()
        .sort_values(ascending=False).head(5).reset_index()
    )
    fig2 = px.bar(
        top_states, x="quantity_kg", y="state", orientation="h",
        template=PLOTLY_TEMPLATE, color_discrete_sequence=[COLOR_SEQUENCE[0]],
        labels={"quantity_kg": "Quantity Seized (kg)", "state": ""},
    )
    fig2.update_layout(height=380, margin=dict(t=10, b=10), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.subheader("📂 Module Guide")
st.markdown(
    """
Use the sidebar to navigate between analytical modules:

| Module | Purpose |
|---|---|
| 🗺️ **Seizure Map & Trends** | Geographic hotspot analysis with temporal filters, state/district drill-down |
| 🧪 **Precursor Monitoring** | Detects anomalous precursor chemical import spikes that may signal expanding production |
| 💰 **Trade Finance Analysis** | Flags high-risk transaction patterns consistent with money-laundering routes *(simulated data)* |
| 💊 **Drug Type Distribution** | Breaks down seizure composition by drug type, state, and time |
| 📊 **Population Correlation** | Normalizes seizure activity against state population to surface under-policed hotspots |
"""
)

st.caption(
    "Data sources: National Crime Records Bureau (NCB) public seizure statistics; "
    "trade-finance data simulated for demonstration purposes only."
)
