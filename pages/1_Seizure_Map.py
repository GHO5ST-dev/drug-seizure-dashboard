import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils.data_loader import load_seizures, load_known_corridors, get_state_coords, year_range
from utils.route_analysis import infer_routes, attach_coords
from utils.styling import inject_base_css, page_header, PLOTLY_TEMPLATE, COLOR_SEQUENCE

st.set_page_config(page_title="Seizure Map & Trends", page_icon="🗺️", layout="wide")
inject_base_css()
page_header(
    "🗺️ Interactive Seizure Map & Temporal Trends",
    "Geographic hotspots across states/districts, with enforcement-gap indicators over time.",
)

df = load_seizures()
ymin, ymax = year_range(df)

# ---------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------
f1, f2, f3 = st.columns([2, 1.2, 1.2])
with f1:
    yr_from, yr_to = st.slider(
        "Year range", min_value=ymin, max_value=ymax, value=(ymin, ymax)
    )
with f2:
    states_sel = st.multiselect("State filter (blank = all)", sorted(df["state"].unique()))
with f3:
    drugs_sel = st.multiselect("Drug type filter (blank = all)", sorted(df["drug_type"].unique()))

filtered = df[(df["year"] >= yr_from) & (df["year"] <= yr_to)]
if states_sel:
    filtered = filtered[filtered["state"].isin(states_sel)]
if drugs_sel:
    filtered = filtered[filtered["drug_type"].isin(drugs_sel)]

st.caption(f"Showing **{len(filtered):,}** seizure records matching filters.")

# ---------------------------------------------------------------------
# Route overlay controls
# ---------------------------------------------------------------------
st.subheader("🧭 Trafficking Route Overlay")
r1, r2, r3 = st.columns([1.2, 1.2, 1.6])
with r1:
    show_known = st.checkbox("Show known trafficking corridors", value=True)
with r2:
    show_inferred = st.checkbox("Show data-inferred routes", value=False)
with r3:
    infer_drug = None
    min_corr = 0.45
    if show_inferred:
        infer_drug = st.selectbox(
            "Drug type to infer routes for",
            sorted(filtered["drug_type"].unique()) if len(filtered) else sorted(df["drug_type"].unique()),
        )
        min_corr = st.slider("Minimum correlation to show route", 0.3, 0.9, 0.45, 0.05)

corridors = load_known_corridors()
state_coords = get_state_coords(df)

inferred_routes = pd.DataFrame()
if show_inferred and infer_drug:
    inferred_routes = infer_routes(filtered if len(filtered) else df, infer_drug, min_corr=min_corr)
    inferred_routes = attach_coords(inferred_routes, state_coords)

# ---------------------------------------------------------------------
# Map
# ---------------------------------------------------------------------
map_col, side_col = st.columns([2.2, 1])

with map_col:
    st.subheader("Seizure Density Map")
    if len(filtered) > 0:
        sample = filtered if len(filtered) <= 4000 else filtered.sample(4000, random_state=1)
        fig = px.density_mapbox(
            sample, lat="latitude", lon="longitude", z="quantity_kg",
            radius=18, center=dict(lat=22.5, lon=80), zoom=3.6,
            mapbox_style="carto-positron", template=PLOTLY_TEMPLATE,
            color_continuous_scale="YlOrRd",
            hover_data=["state", "district", "drug_type", "quantity_kg"],
        )

        # -- Known corridor overlay (sequential hop lines per corridor) --
        if show_known:
            corridor_colors = {
                name: COLOR_SEQUENCE[i % len(COLOR_SEQUENCE)]
                for i, name in enumerate(corridors["corridor_name"].unique())
            }
            for name, grp in corridors.sort_values("hop_order").groupby("corridor_name"):
                fig.add_trace(go.Scattermapbox(
                    lat=grp["latitude"], lon=grp["longitude"],
                    mode="lines+markers",
                    line=dict(width=3, color=corridor_colors[name]),
                    marker=dict(size=8, color=corridor_colors[name]),
                    name=name,
                    hovertext=[
                        f"{name}<br>Stop: {s}<br>Drugs: {d}"
                        for s, d in zip(grp["state"], grp["primary_drug_types"])
                    ],
                    hoverinfo="text",
                    showlegend=True,
                ))

        # -- Data-inferred route overlay (source -> target lines) --
        if show_inferred and len(inferred_routes) > 0:
            max_corr = inferred_routes["correlation"].max() or 1
            for _, r in inferred_routes.iterrows():
                width = 2 + 6 * (r["correlation"] / max_corr)
                fig.add_trace(go.Scattermapbox(
                    lat=[r["src_lat"], r["tgt_lat"]],
                    lon=[r["src_lon"], r["tgt_lon"]],
                    mode="lines+markers",
                    line=dict(width=width, color="#8E44AD"),
                    marker=dict(size=[6, 12], color="#8E44AD", symbol="circle"),
                    name=f"{r['source_state']} → {r['target_state']}",
                    hovertext=(
                        f"Inferred route: {r['source_state']} → {r['target_state']}<br>"
                        f"Drug: {r['drug_type']}<br>Lag: {r['lag_months']} month(s)<br>"
                        f"Correlation: {r['correlation']}"
                    ),
                    hoverinfo="text",
                    showlegend=False,
                ))
        elif show_inferred:
            st.caption("No candidate routes met the correlation threshold for this drug type/filter combination.")

        fig.update_layout(
            height=560, margin=dict(t=10, b=0, l=0, r=0),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15) if show_known else None,
        )
        st.plotly_chart(fig, use_container_width=True)

        if show_known or show_inferred:
            legend_bits = []
            if show_known:
                legend_bits.append("🟢🔴🟣 lines = **known documented corridors** (hover for stop details)")
            if show_inferred:
                legend_bits.append("🟪 purple lines = **data-inferred routes** (line thickness ≈ correlation strength; arrow direction = larger marker end = likely destination)")
            st.caption(" · ".join(legend_bits))
    else:
        st.warning("No records match the current filters.")

with side_col:
    st.subheader("District Hotspots")
    top_districts = (
        filtered.groupby(["state", "district"])["quantity_kg"]
        .sum().sort_values(ascending=False).head(10).reset_index()
    )
    top_districts["label"] = top_districts["district"] + ", " + top_districts["state"]
    fig_d = px.bar(
        top_districts, x="quantity_kg", y="label", orientation="h",
        template=PLOTLY_TEMPLATE, color_discrete_sequence=[COLOR_SEQUENCE[3]],
        labels={"quantity_kg": "kg seized", "label": ""},
    )
    fig_d.update_layout(height=560, margin=dict(t=10, b=10), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_d, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------
# Temporal trend by state (small multiples via line chart)
# ---------------------------------------------------------------------
st.subheader("Temporal Trend by State")
trend = (
    filtered.groupby(["year", "state"])["quantity_kg"].sum().reset_index()
)
default_states = (
    filtered.groupby("state")["quantity_kg"].sum().sort_values(ascending=False).head(6).index.tolist()
)
show_states = states_sel if states_sel else default_states
trend_plot = trend[trend["state"].isin(show_states)]

fig_t = px.line(
    trend_plot, x="year", y="quantity_kg", color="state", markers=True,
    template=PLOTLY_TEMPLATE, color_discrete_sequence=COLOR_SEQUENCE,
    labels={"quantity_kg": "Quantity Seized (kg)", "year": "Year", "state": "State"},
)
fig_t.update_layout(height=420, margin=dict(t=10, b=10))
st.plotly_chart(fig_t, use_container_width=True)

if show_inferred and len(inferred_routes) > 0:
    st.subheader("Data-Inferred Route Candidates (Detail)")
    st.dataframe(
        inferred_routes[["source_state", "target_state", "drug_type", "lag_months", "correlation"]],
        use_container_width=True, height=250,
    )

st.markdown(
    """
**Reading the map for enforcement gaps:** a district showing a sudden *drop* in seizure
volume relative to its multi-year trend — not explained by a genuine decline in trafficking
elsewhere in the corridor — is a candidate signal for reduced enforcement coverage rather than
reduced trafficking activity, and warrants inter-agency review.

**Route overlay methodology:**
- *Known corridors* are broad, publicly-documented trafficking corridor patterns (e.g. Golden
  Crescent, Golden Triangle) at state-level granularity, included for geographic context — not
  operational intelligence.
- *Data-inferred routes* are a simple exploratory heuristic: for a chosen drug type, states whose
  monthly seizure volumes are correlated with a 1–2 month lag (one state's spikes tend to precede
  another's) are surfaced as directional candidate routes. Higher correlation and shorter, more
  consistent lags are more suggestive of an actual supply link. **These are analyst-triage signals,
  not confirmed trafficking routes**, and should be validated against ground intelligence.
"""
)
