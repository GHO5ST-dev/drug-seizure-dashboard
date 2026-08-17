import streamlit as st
import plotly.express as px
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

from utils.data_loader import load_trade_finance
from utils.styling import inject_base_css, page_header, PLOTLY_TEMPLATE, COLOR_SEQUENCE

st.set_page_config(page_title="Trade Finance Analysis", page_icon="💰", layout="wide")
inject_base_css()
page_header(
    "💰 Trade Finance & Money Laundering Route Analysis",
    "Identifies high-risk transaction patterns across states consistent with layering/laundering.",
)

st.warning(
    "**This module uses SIMULATED transaction data** for demonstration purposes only. "
    "No real account or personal data is used. Replace `data/trade_finance.csv` with a "
    "verified, lawfully-obtained dataset before any operational use.",
    icon="⚠️",
)

df = load_trade_finance()

# ---------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------
c1, c2, c3 = st.columns(3)
with c1:
    yr_from, yr_to = st.slider(
        "Year range", int(df["year"].min()), int(df["year"].max()),
        (int(df["year"].min()), int(df["year"].max())),
    )
with c2:
    txn_types = st.multiselect("Transaction type", sorted(df["transaction_type"].unique()))
with c3:
    risk_min = st.slider("Minimum risk score", 0.0, 1.0, 0.0, 0.05)

filtered = df[(df["year"] >= yr_from) & (df["year"] <= yr_to) & (df["risk_score"] >= risk_min)]
if txn_types:
    filtered = filtered[filtered["transaction_type"].isin(txn_types)]

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Transactions in View", f"{len(filtered):,}")
with k2:
    st.metric("Total Value (₹)", f"{filtered['amount_inr'].sum():,.0f}")
with k3:
    st.metric("Flagged (high risk)", int(filtered["flagged"].sum()))
with k4:
    st.metric("Avg. Risk Score", f"{filtered['risk_score'].mean():.2f}" if len(filtered) else "—")

st.divider()

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Inter-State Transaction Flows (Flagged)")
    flagged_flows = (
        filtered[filtered["flagged"]]
        .groupby(["sender_state", "receiver_state"])
        .agg(total_amount=("amount_inr", "sum"), n=("transaction_id", "count"))
        .reset_index()
        .sort_values("total_amount", ascending=False)
        .head(25)
    )

    if len(flagged_flows) > 0:
        G = nx.DiGraph()
        for _, row in flagged_flows.iterrows():
            G.add_edge(row["sender_state"], row["receiver_state"], weight=row["total_amount"])
        pos = nx.spring_layout(G, seed=7, k=0.9)

        edge_x, edge_y = [], []
        for u, v in G.edges():
            x0, y0 = pos[u]; x1, y1 = pos[v]
            edge_x += [x0, x1, None]; edge_y += [y0, y1, None]
        edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color="#C0392B"),
                                 mode="lines", hoverinfo="none")

        node_x = [pos[n][0] for n in G.nodes()]
        node_y = [pos[n][1] for n in G.nodes()]
        node_trace = go.Scatter(
            x=node_x, y=node_y, mode="markers+text", text=list(G.nodes()),
            textposition="top center",
            marker=dict(size=16, color=COLOR_SEQUENCE[0]),
            hoverinfo="text",
        )
        fig_net = go.Figure(data=[edge_trace, node_trace])
        fig_net.update_layout(
            height=480, showlegend=False, margin=dict(t=10, b=10),
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            template=PLOTLY_TEMPLATE,
        )
        st.plotly_chart(fig_net, use_container_width=True)
    else:
        st.info("No flagged transactions match the current filters.")

with right:
    st.subheader("Risk Score Distribution by Channel")
    fig_box = px.box(
        filtered, x="channel", y="risk_score", color="channel",
        template=PLOTLY_TEMPLATE, color_discrete_sequence=COLOR_SEQUENCE,
        labels={"risk_score": "Risk Score", "channel": ""},
    )
    fig_box.update_layout(height=480, margin=dict(t=10, b=10), showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

st.divider()

st.subheader("Highest-Risk Flagged Transactions")
top_risk = filtered[filtered["flagged"]].sort_values("risk_score", ascending=False).head(20)
st.dataframe(
    top_risk[
        ["transaction_id", "date", "sender_state", "receiver_state",
         "amount_inr", "transaction_type", "channel", "risk_score"]
    ],
    use_container_width=True, height=380,
)

st.markdown(
    """
**Risk scoring logic (simplified, for demo):** transactions gain risk weight for using
hawala/shell-company/crypto channels, unusually large or suspiciously round amounts, and
cross-state movement — patterns commonly associated with layering stages of money laundering.
A production system should incorporate KYC linkage, beneficial-ownership data, and
FIU-IND typologies rather than rule-of-thumb scoring.
"""
)
