# 🛡️ Drug Seizure Intelligence Dashboard
### Law Enforcement Analytics Toolkit — NCB Seizure, Trade & Finance Data (2018–2024)

An interactive Streamlit analytics dashboard built to help NCB and state police forces
identify drug trafficking hotspots, precursor-chemical diversion, money-laundering
patterns, drug-type trends, and population-normalized policing gaps.

> **Data notice:** The repository ships with a `data/generate_data.py` script that
> produces **simulated** data so the app runs out of the box. Swap in your real,
> lawfully-obtained NCB / trade-finance datasets by replacing the CSVs in `data/`
> using the exact column schema below — no code changes required elsewhere.

---

## 1. Project Structure

```
drug-seizure-dashboard/
├── app.py                              # Streamlit entry point and navigation
├── Dashboard.py                        # Home page: KPIs + overview
├── pages/
│   ├── 1_🗺️_Seizure_Map.py             # Module 1: geo hotspots + temporal trend
│   ├── 2_🧪_Precursor_Monitoring.py     # Module 2: precursor import anomaly detection
│   ├── 3_💰_Trade_Finance_Analysis.py   # Module 3: money-laundering route analysis
│   ├── 4_💊_Drug_Type_Distribution.py   # Module 4: drug type composition & trend
│   ├── 5_📊_Population_Correlation.py   # Module 5: seizures vs. population
│   └── 6_Trafficking_Input.py          # Module 6: analyst-entered route observations
├── utils/
│   ├── data_loader.py                  # Central cached data-access layer
│   └── styling.py                      # Shared theme / CSS helpers
├── data/
│   ├── generate_data.py                # Simulated data generator (documents schema)
│   ├── seizures.csv
│   ├── precursor_imports.csv
│   ├── trade_finance.csv
│   ├── state_population.csv
│   └── trafficking_reports.csv          # Local analyst input; ignored by Git when created
├── .streamlit/config.toml              # Theme config
├── requirements.txt
└── README.md
```

---

## 2. Setup & Run

```bash
# 1. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Re)generate simulated data if needed
python data/generate_data.py

# 4. Launch the dashboard
streamlit run app.py
```

The app opens at `http://localhost:8501`. Navigate between modules using the sidebar.

---

## 3. Modules

| # | Module | What it does |
|---|--------|---------------|
| 1 | **Seizure Map & Trends** | Density map of seizures by lat/lon, district hotspot ranking, and multi-state time-series trend, with year/state/drug filters. |
| 2 | **Precursor Monitoring** | Flags statistically anomalous precursor-chemical import spikes (z-score based, adjustable sensitivity) that may indicate diversion for illicit drug synthesis. |
| 3 | **Trade Finance Analysis** | Risk-scores simulated financial transactions and visualizes flagged inter-state transaction networks to surface potential laundering routes. |
| 4 | **Drug Type Distribution** | Breaks down seizure composition by drug type — pie/bubble views, trend over time, and a state × drug-type heatmap. |
| 5 | **Population Correlation** | Normalizes seizure volume/incidents by state population to highlight potential over-/under-policed states, with a correlation coefficient and OLS trendline. |
| 6 | **Trafficking Intelligence Input** | Captures anonymized dealer aliases, route stops, destinations, transport details, confidence, and case status for local analyst review. |

---

## 4. Data Schema (for plugging in real data)

Replace files inside `data/` with your own CSVs using these **exact column names**.
Dates should be `YYYY-MM-DD`. Everything else in the app (filters, charts, KPIs) will
work automatically since `utils/data_loader.py` reads by column name.

### `seizures.csv`
| Column | Type | Notes |
|---|---|---|
| seizure_id | string | Unique ID |
| date | date | YYYY-MM-DD |
| year | int | 2018–2024 |
| month | int | 1–12 |
| state | string | State/UT name |
| district | string | District name |
| latitude | float | Decimal degrees |
| longitude | float | Decimal degrees |
| drug_type | string | e.g. Heroin, Cannabis (Ganja), Cocaine, etc. |
| quantity_kg | float | Seizure quantity in kilograms |
| agency | string | NCB / State Police / Customs / Coast Guard / BSF / DRI |

### `precursor_imports.csv`
| Column | Type | Notes |
|---|---|---|
| record_id | string | Unique ID |
| date | date | YYYY-MM-DD |
| year | int | |
| month | int | |
| state | string | State of port/entry |
| port_of_entry | string | e.g. Nhava Sheva, Mundra, Chennai Port |
| chemical_name | string | e.g. Acetic Anhydride, Ephedrine |
| quantity_kg | float | |
| declared_purpose | string | Pharmaceutical / Industrial / etc. |
| importer_name | string | |
| is_anomaly | bool | Pre-flagged anomaly (optional; app also recomputes via z-score) |

### `trade_finance.csv` *(simulated by design — see note below)*
| Column | Type | Notes |
|---|---|---|
| transaction_id | string | Unique ID |
| date | date | |
| year | int | |
| sender_state | string | |
| receiver_state | string | |
| sender_account | string | Anonymized/tokenized account reference |
| receiver_account | string | Anonymized/tokenized account reference |
| amount_inr | float | Transaction value in ₹ |
| transaction_type | string | e.g. Trade Invoice Payment, Hawala-linked Transfer |
| channel | string | Bank Transfer / UPI / Hawala Network / Crypto Exchange / Cash |
| risk_score | float | 0–1 |
| flagged | bool | risk_score ≥ threshold |

### `state_population.csv`
| Column | Type | Notes |
|---|---|---|
| state | string | Must match `state` values used in `seizures.csv` |
| population_millions | float | |

---

## 5. Important Notes on Data Provenance

- **Seizure and precursor data** are designed to reflect the structure of publicly
  available NCB annual report statistics. Verify and source real figures from NCB
  before using this dashboard operationally.
- **Trade finance / money-laundering data is entirely simulated.** Real financial
  transaction data of this kind is sensitive, regulated (PMLA, RBI/FIU-IND rules),
  and not publicly distributable. The module exists to *demonstrate the analytics
  approach* (risk scoring, network analysis of flagged flows) that would be applied
  to genuine FIU-IND / bank-shared data under proper legal authorization.
- This is an analytics/decision-support tool, not an investigative or evidentiary
  system. All "anomaly"/"risk" flags require human analyst review before any action.

---

## 6. Extending the Project

- **Swap in real data:** overwrite the CSVs in `data/` (see schema above) and restart the app.
- **Add a new module:** create a new file in `pages/` following the naming pattern
  `N_<emoji>_Title.py`; Streamlit auto-adds it to the sidebar.
- **Change anomaly/risk thresholds:** adjust the sliders in Modules 2 and 3, or edit
  the scoring logic directly in those page files / `data/generate_data.py`.
- **Deploy:** the app is deployable as-is to Streamlit Community Cloud, or containerized
  with a simple Dockerfile (`CMD ["streamlit", "run", "app.py"]`).
