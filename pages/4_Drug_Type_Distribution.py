import streamlit as st
import plotly.express as px

from utils.data_loader import load_seizures
from utils.styling import inject_base_css, page_header, PLOTLY_TEMPLATE, COLOR_SEQUENCE

st.set_page_config(page_title="Drug Type Distribution", page_icon="💊", layout="wide")
inject_base_css()
page_header(
    "💊 Drug Type Distribution Analysis",
    "Composition of seized substances by type, geography, and time — informs targeted interdiction strategy.",
)

df = load_seizures()

c1, c2 = st.columns(2)
with c1:
    states_sel = st.multiselect("State filter (blank = all)", sorted(df["state"].unique()))
with c2:
    yr_from, yr_to = st.slider(
        "Year range", int(df["year"].min()), int(df["year"].max()),
        (int(df["year"].min()), int(df["year"].max())),
    )

filtered = df[(df["year"] >= yr_from) & (df["year"] <= yr_to)]
if states_sel:
    filtered = filtered[filtered["state"].isin(states_sel)]

left, right = st.columns([1, 1.3])

with left:
    st.subheader("Overall Composition (by Volume)")
    mix = filtered.groupby("drug_type")["quantity_kg"].sum().sort_values(ascending=False).reset_index()
    fig = px.pie(
        mix, names="drug_type", values="quantity_kg", hole=0.45,
        template=PLOTLY_TEMPLATE, color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(height=440, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Composition by Record Count vs Volume")
    mix2 = filtered.groupby("drug_type").agg(
        records=("seizure_id", "count"), volume=("quantity_kg", "sum")
    ).reset_index()
    fig2 = px.scatter(
        mix2, x="records", y="volume", text="drug_type", size="volume",
        template=PLOTLY_TEMPLATE, color="drug_type", color_discrete_sequence=COLOR_SEQUENCE,
        labels={"records": "Number of Seizure Incidents", "volume": "Total Volume (kg)"},
    )
    fig2.update_traces(textposition="top center")
    fig2.update_layout(height=440, margin=dict(t=10, b=10), showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.subheader("Drug Type Trend Over Time")
trend = filtered.groupby(["year", "drug_type"])["quantity_kg"].sum().reset_index()
fig3 = px.area(
    trend, x="year", y="quantity_kg", color="drug_type",
    template=PLOTLY_TEMPLATE, color_discrete_sequence=COLOR_SEQUENCE,
    labels={"quantity_kg": "Quantity (kg)", "year": "Year", "drug_type": "Drug Type"},
)
fig3.update_layout(height=420, margin=dict(t=10, b=10))
st.plotly_chart(fig3, use_container_width=True)

st.divider()

st.subheader("Drug Type by State (Heatmap)")
heat = filtered.groupby(["state", "drug_type"])["quantity_kg"].sum().reset_index()
heat_pivot = heat.pivot(index="state", columns="drug_type", values="quantity_kg").fillna(0)
fig4 = px.imshow(
    heat_pivot, aspect="auto", color_continuous_scale="YlOrRd",
    labels=dict(color="kg seized"), template=PLOTLY_TEMPLATE,
)
fig4.update_layout(height=520, margin=dict(t=10, b=10))
st.plotly_chart(fig4, use_container_width=True)
