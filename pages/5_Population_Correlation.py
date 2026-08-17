import streamlit as st
import plotly.express as px
import numpy as np

from utils.data_loader import load_seizures, load_population
from utils.styling import inject_base_css, page_header, PLOTLY_TEMPLATE, COLOR_SEQUENCE

st.set_page_config(page_title="Population Correlation", page_icon="📊", layout="wide")
inject_base_css()
page_header(
    "📊 Seizure Activity vs. Population Correlation",
    "Normalizes enforcement activity by population to reveal under- and over-policed states.",
)

seizures = load_seizures()
population = load_population()

yr_from, yr_to = st.slider(
    "Year range", int(seizures["year"].min()), int(seizures["year"].max()),
    (int(seizures["year"].min()), int(seizures["year"].max())),
)
filtered = seizures[(seizures["year"] >= yr_from) & (seizures["year"] <= yr_to)]

agg = (
    filtered.groupby("state")
    .agg(total_kg=("quantity_kg", "sum"), incidents=("seizure_id", "count"))
    .reset_index()
    .merge(population, on="state", how="left")
)
agg["kg_per_million"] = agg["total_kg"] / agg["population_millions"]
agg["incidents_per_million"] = agg["incidents"] / agg["population_millions"]

# Simple linear correlation stat
corr = np.corrcoef(agg["population_millions"], agg["total_kg"])[0, 1]

k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Correlation (population vs. total seized kg)", f"{corr:.2f}")
with k2:
    top_gap = agg.sort_values("kg_per_million", ascending=False).iloc[0]
    st.metric("Highest seizure-per-capita state", top_gap["state"])
with k3:
    low_gap = agg[agg["incidents"] > 0].sort_values("incidents_per_million").iloc[0]
    st.metric("Lowest incidents-per-capita (of active states)", low_gap["state"])

st.divider()

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Population vs. Total Quantity Seized")
    fig = px.scatter(
        agg, x="population_millions", y="total_kg", text="state", size="incidents",
        template=PLOTLY_TEMPLATE, color="kg_per_million", color_continuous_scale="YlOrRd",
        labels={
            "population_millions": "Population (millions)",
            "total_kg": "Total Quantity Seized (kg)",
            "kg_per_million": "kg per million people",
        },
        trendline="ols",
    )
    fig.update_traces(textposition="top center", selector=dict(mode="markers+text"))
    fig.update_layout(height=500, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Seizure Volume per Million Population")
    ranked = agg.sort_values("kg_per_million", ascending=False)
    fig2 = px.bar(
        ranked, x="kg_per_million", y="state", orientation="h",
        template=PLOTLY_TEMPLATE, color_discrete_sequence=[COLOR_SEQUENCE[0]],
        labels={"kg_per_million": "kg seized / million population", "state": ""},
    )
    fig2.update_layout(height=500, margin=dict(t=10, b=10), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.subheader("Policing Gap Table")
gap_table = agg[["state", "population_millions", "incidents", "total_kg",
                  "incidents_per_million", "kg_per_million"]].sort_values(
    "kg_per_million", ascending=False
)
st.dataframe(gap_table, use_container_width=True, height=420)

st.markdown(
    """
**Interpreting this module:** states with *high population but disproportionately low*
seizure-per-capita figures may indicate either genuinely lower trafficking activity, or a
**policing/detection gap** — under-resourced enforcement relative to population and
trafficking-corridor exposure. This should be read alongside the Seizure Map module (corridor
proximity) before drawing conclusions about any single state.
"""
)
