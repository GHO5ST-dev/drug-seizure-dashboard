"""
data_loader.py
---------------
Central data access layer for the dashboard. Every page imports from here.

To plug in REAL NCB / trade-finance data: replace the CSV files inside
data/ with your own files using the identical column names described below
(and in README.md). Nothing else in the app needs to change.
"""

from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@st.cache_data(show_spinner=False)
def load_seizures() -> pd.DataFrame:
    """
    Columns:
      seizure_id, date, year, month, state, district, latitude, longitude,
      drug_type, quantity_kg, agency
    """
    df = pd.read_csv(DATA_DIR / "seizures.csv", parse_dates=["date"])
    return df


@st.cache_data(show_spinner=False)
def load_precursor_imports() -> pd.DataFrame:
    """
    Columns:
      record_id, date, year, month, state, port_of_entry, chemical_name,
      quantity_kg, declared_purpose, importer_name, is_anomaly
    """
    df = pd.read_csv(DATA_DIR / "precursor_imports.csv", parse_dates=["date"])
    return df


@st.cache_data(show_spinner=False)
def load_trade_finance() -> pd.DataFrame:
    """
    Columns:
      transaction_id, date, year, sender_state, receiver_state,
      sender_account, receiver_account, amount_inr, transaction_type,
      channel, risk_score, flagged
    """
    df = pd.read_csv(DATA_DIR / "trade_finance.csv", parse_dates=["date"])
    return df


@st.cache_data(show_spinner=False)
def load_population() -> pd.DataFrame:
    """
    Columns:
      state, population_millions
    """
    df = pd.read_csv(DATA_DIR / "state_population.csv")
    return df


@st.cache_data(show_spinner=False)
def get_state_coords(seizures_df: pd.DataFrame) -> dict:
    """Returns {state: (lat, lon)} using the mean coordinates of that state's
    seizure records — used to plot route lines without hardcoding centroids."""
    means = seizures_df.groupby("state")[["latitude", "longitude"]].mean()
    return {state: (row["latitude"], row["longitude"]) for state, row in means.iterrows()}


@st.cache_data(show_spinner=False)
def load_known_corridors() -> pd.DataFrame:
    """
    Columns:
      corridor_name, hop_order, state, latitude, longitude,
      primary_drug_types, source_context
    """
    df = pd.read_csv(DATA_DIR / "known_corridors.csv")
    return df


def year_range(df: pd.DataFrame) -> tuple[int, int]:
    return int(df["year"].min()), int(df["year"].max())
