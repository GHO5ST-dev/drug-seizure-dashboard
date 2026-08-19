from datetime import date
from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st

from utils.styling import inject_base_css, page_header


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "trafficking_reports.csv"
COLUMNS = [
    "report_id",
    "reported_on",
    "dealer_alias",
    "drug_type",
    "quantity_kg",
    "origin",
    "route_stops",
    "destination",
    "transport_mode",
    "trafficking_pattern",
    "confidence",
    "case_status",
    "notes",
]


def load_reports() -> pd.DataFrame:
    if not DATA_PATH.exists():
        return pd.DataFrame(columns=COLUMNS)
    return pd.read_csv(DATA_PATH)


def save_report(report: dict) -> None:
    reports = load_reports()
    reports = pd.concat([reports, pd.DataFrame([report], columns=COLUMNS)], ignore_index=True)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    reports.to_csv(DATA_PATH, index=False)


st.set_page_config(page_title="Trafficking Intelligence Input", layout="wide")
inject_base_css()
page_header(
    "Trafficking Intelligence Input",
    "Capture structured route observations for analyst review and dashboard context.",
)

st.warning(
    "Use an anonymized dealer alias only. Do not enter names, phone numbers, addresses, "
    "or other directly identifying personal information. Entries are local to this dashboard "
    "and require authorized human review."
)

with st.form("trafficking_intelligence_form", clear_on_submit=True):
    st.subheader("Observation details")
    first, second, third = st.columns(3)
    with first:
        reported_on = st.date_input("Observation date", value=date.today())
        dealer_alias = st.text_input("Dealer alias", placeholder="e.g. Subject-014")
        drug_type = st.text_input("Drug or substance", placeholder="e.g. Heroin")
        quantity_kg = st.number_input("Estimated quantity (kg)", min_value=0.0, value=0.0, step=0.1)
    with second:
        origin = st.text_input("Origin / entry point", placeholder="State, city, port, or border")
        route_stops = st.text_input("Intermediate route stops", placeholder="Separate stops with commas")
        destination = st.text_input("Destination", placeholder="State, city, port, or border")
        transport_mode = st.selectbox(
            "Transport mode",
            ["Road", "Rail", "Air", "Maritime", "Courier", "Unknown", "Other"],
        )
    with third:
        trafficking_pattern = st.selectbox(
            "Trafficking pattern",
            ["Land corridor", "Maritime corridor", "Air route", "Local distribution", "Mixed / multi-modal", "Unknown"],
        )
        confidence = st.select_slider("Analyst confidence", options=["Low", "Medium", "High"], value="Medium")
        case_status = st.selectbox("Case status", ["Unverified", "Under review", "Corroborated", "Closed"])
        notes = st.text_area("Analyst notes", height=110, placeholder="Record source context without personal identifiers.")

    submitted = st.form_submit_button("Save intelligence record", type="primary", use_container_width=True)

if submitted:
    missing = [
        label for label, value in {
            "dealer alias": dealer_alias.strip(),
            "drug or substance": drug_type.strip(),
            "origin / entry point": origin.strip(),
            "destination": destination.strip(),
        }.items() if not value
    ]
    if missing:
        st.error(f"Please complete: {', '.join(missing)}.")
    elif origin.strip().casefold() == destination.strip().casefold():
        st.error("Origin and destination should be different locations.")
    else:
        save_report(
            {
                "report_id": f"TR-{uuid4().hex[:8].upper()}",
                "reported_on": reported_on.isoformat(),
                "dealer_alias": dealer_alias.strip(),
                "drug_type": drug_type.strip(),
                "quantity_kg": quantity_kg,
                "origin": origin.strip(),
                "route_stops": route_stops.strip(),
                "destination": destination.strip(),
                "transport_mode": transport_mode,
                "trafficking_pattern": trafficking_pattern,
                "confidence": confidence,
                "case_status": case_status,
                "notes": notes.strip(),
            }
        )
        st.success("Intelligence record saved.")

st.divider()
st.subheader("Saved route observations")
reports = load_reports()
if reports.empty:
    st.info("No route observations have been entered yet.")
else:
    st.caption(f"{len(reports):,} record(s) stored locally in the dashboard data folder.")
    st.dataframe(
        reports[
            [
                "report_id",
                "reported_on",
                "dealer_alias",
                "drug_type",
                "origin",
                "route_stops",
                "destination",
                "transport_mode",
                "confidence",
                "case_status",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )