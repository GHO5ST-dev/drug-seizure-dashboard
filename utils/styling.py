"""Shared styling helpers for consistent look across pages."""

import streamlit as st

PRIMARY = "#0B3D2E"      # deep green (enforcement / institutional)
ACCENT = "#C0392B"       # alert red for flags/anomalies
BG_CARD = "#F4F6F5"

PLOTLY_TEMPLATE = "plotly_white"

COLOR_SEQUENCE = [
    "#0B3D2E", "#1F6F50", "#3A9D7A", "#C0392B", "#E67E22",
    "#2C5F8A", "#8E44AD", "#B7950B",
]


def inject_base_css():
    st.markdown(
        f"""
        <style>
        .metric-card {{
            background-color: {BG_CARD};
            border-left: 5px solid {PRIMARY};
            border-radius: 6px;
            padding: 14px 18px;
        }}
        .flag-badge {{
            background-color: {ACCENT};
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
        }}
        h1, h2, h3 {{
            color: {PRIMARY};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)
    st.divider()
