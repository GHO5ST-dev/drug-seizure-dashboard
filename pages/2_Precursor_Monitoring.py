import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

from utils.data_loader import load_precursor_imports
from utils.styling import inject_base_css, page_header, PLOTLY_TEMPLATE, COLOR_SEQUENCE

st.set_page_config(page_title="Precursor Monitoring", layout="wide")
inject_base_css()
page_header(
    "Precursor Chemical Import Monitoring",
    "Statistical anomaly detection on precursor chemical imports — spikes can indicate expansion in illicit drug production.",
)

df = load_precursor_imports()

# ---------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------
c1, c2, c3 = st.columns(3)
with c1:
    chem_sel = st.multiselect("Chemical", sorted(df["chemical_name"].unique()))
with c2:
    port_sel = st.multiselect("Port of entry", sorted(df["port_of_entry"].unique()))
with c3:
    z_thresh = st.slider("Anomaly sensitivity (z-score threshold)", 1.5, 4.0, 2.5, 0.1)

filtered = df.copy()
if chem_sel:
    filtered = filtered[filtered["chemical_name"].isin(chem_sel)]
if port_sel:
    filtered = filtered[filtered["port_of_entry"].isin(port_sel)]

# ---------------------------------------------------------------------
# Recompute anomalies live using z-score per chemical (in addition to the
# pre-flagged is_anomaly column, so the sensitivity slider is meaningful).
# ---------------------------------------------------------------------
monthly = (
    filtered.groupby(["chemical_name", "year", "month"])["quantity_kg"]
    .sum().reset_index()
)
monthly["z_score"] = monthly.groupby("chemical_name")["quantity_kg"].transform(
    lambda x: (x - x.mean()) / x.std(ddof=0) if x.std(ddof=0) > 0 else 0
)
monthly["flagged"] = monthly["z_score"] >= z_thresh
monthly["period"] = pd.to_datetime(
    monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2) + "-01"
)

k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Total Import Records", f"{len(filtered):,}")
with k2:
    st.metric("Total Volume (kg)", f"{filtered['quantity_kg'].sum():,.0f}")
with k3:
    st.metric("Flagged Monthly Anomalies", int(monthly["flagged"].sum()))

st.divider()

# ---------------------------------------------------------------------
# Anomaly chart
# ---------------------------------------------------------------------
st.subheader("Monthly Import Volume with Anomaly Flags")
chem_for_chart = chem_sel if chem_sel else sorted(monthly["chemical_name"].unique())[:4]
chart_df = monthly[monthly["chemical_name"].isin(chem_for_chart)]

fig = px.line(
    chart_df, x="period", y="quantity_kg", color="chemical_name",
    template=PLOTLY_TEMPLATE, color_discrete_sequence=COLOR_SEQUENCE, markers=True,
    labels={"quantity_kg": "Quantity (kg)", "period": "Month", "chemical_name": "Chemical"},
)
flags = chart_df[chart_df["flagged"]]
if len(flags) > 0:
    fig.add_scatter(
        x=flags["period"], y=flags["quantity_kg"], mode="markers",
        marker=dict(size=13, color="#C0392B", symbol="x"),
        name="Anomaly (z ≥ threshold)",
    )
fig.update_layout(height=440, margin=dict(t=10, b=10))
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------
# Anomaly table + by-port breakdown
# ---------------------------------------------------------------------
left, right = st.columns([1.3, 1])

with left:
    st.subheader("Flagged Import Records (Detail)")
    detail_flagged = filtered[filtered["is_anomaly"]].sort_values("quantity_kg", ascending=False)
    st.dataframe(
        detail_flagged[
            ["date", "chemical_name", "port_of_entry", "state", "quantity_kg",
             "declared_purpose", "importer_name"]
        ],
        use_container_width=True, height=380,
    )

with right:
    st.subheader("Anomalies by Port of Entry")
    by_port = detail_flagged.groupby("port_of_entry").size().sort_values(ascending=False).reset_index(name="count")
    fig_p = px.bar(
        by_port, x="count", y="port_of_entry", orientation="h",
        template=PLOTLY_TEMPLATE, color_discrete_sequence=[COLOR_SEQUENCE[3]],
        labels={"count": "Flagged Records", "port_of_entry": ""},
    )
    fig_p.update_layout(height=380, margin=dict(t=10, b=10), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_p, use_container_width=True)

st.info(
    "Methodology: a shipment is statistically flagged when its monthly import volume for a "
    "given chemical deviates by more than the selected z-score threshold from that chemical's "
    "historical mean. This surfaces *unusual* spikes for manual investigation — it is not, by "
    "itself, proof of diversion."
)
