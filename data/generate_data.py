"""
generate_data.py
-----------------
Generates SIMULATED datasets for the Drug Seizure Intelligence Dashboard.

These files exist so the dashboard is runnable out-of-the-box. When you have
real NCB / trade-finance data, replace the CSVs in this folder with your own
files that follow the SAME COLUMN SCHEMA documented in each section below and
in the project README. The dashboard code does not need to change.

Run:  python data/generate_data.py
"""

import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)
OUT_DIR = Path(__file__).parent
YEARS = list(range(2018, 2025))

# ---------------------------------------------------------------------------
# Reference data: states, approx lat/lon centroids, and 2024 projected
# population (in millions) -- rounded, for illustrative/demo purposes only.
# ---------------------------------------------------------------------------
STATES = {
    "Punjab":            (31.15, 75.34, 30.8),
    "Rajasthan":         (27.02, 74.22, 81.0),
    "Gujarat":           (22.26, 71.19, 71.5),
    "Maharashtra":       (19.75, 75.71, 126.0),
    "Delhi":             (28.70, 77.10, 33.8),
    "Uttar Pradesh":     (26.85, 80.95, 235.0),
    "Manipur":           (24.66, 93.91, 3.3),
    "Mizoram":           (23.16, 92.94, 1.2),
    "Assam":             (26.20, 92.94, 35.6),
    "West Bengal":       (22.99, 87.86, 99.6),
    "Odisha":            (20.95, 85.10, 45.4),
    "Andhra Pradesh":    (15.91, 79.74, 53.9),
    "Tamil Nadu":        (11.13, 78.66, 77.8),
    "Kerala":            (10.85, 76.27, 35.1),
    "Karnataka":         (15.32, 75.71, 67.6),
    "Madhya Pradesh":    (22.97, 78.66, 86.5),
    "Bihar":             (25.10, 85.31, 128.5),
    "Jammu and Kashmir": (33.78, 76.58, 13.6),
    "Haryana":           (29.06, 76.09, 30.0),
    "Telangana":         (18.11, 79.02, 38.5),
}

DISTRICTS = {
    "Punjab": ["Amritsar", "Ferozepur", "Gurdaspur", "Ludhiana", "Tarn Taran"],
    "Rajasthan": ["Jaisalmer", "Barmer", "Jodhpur", "Kota", "Bikaner"],
    "Gujarat": ["Kutch", "Porbandar", "Surat", "Ahmedabad", "Bhavnagar"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Thane"],
    "Delhi": ["New Delhi", "South Delhi", "North West Delhi", "East Delhi"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Ghaziabad", "Agra"],
    "Manipur": ["Imphal East", "Imphal West", "Churachandpur", "Chandel"],
    "Mizoram": ["Aizawl", "Champhai", "Lunglei"],
    "Assam": ["Guwahati", "Cachar", "Karimganj", "Dibrugarh"],
    "West Bengal": ["Kolkata", "North 24 Parganas", "Malda", "Nadia"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Koraput", "Ganjam"],
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Anantapur"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tirunelveli"],
    "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode", "Kollam"],
    "Karnataka": ["Bengaluru Urban", "Mysuru", "Mangaluru", "Belagavi"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Neemuch"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur"],
    "Jammu and Kashmir": ["Srinagar", "Jammu", "Baramulla", "Poonch"],
    "Haryana": ["Karnal", "Sirsa", "Faridabad", "Gurugram"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Khammam"],
}

DRUG_TYPES = [
    "Heroin", "Cannabis (Ganja)", "Charas/Hashish", "Opium", "Cocaine",
    "Methamphetamine", "MDMA", "Ketamine", "Pharmaceutical Opioids",
    "Poppy Husk",
]

# States that sit on known trafficking corridors get elevated seizure
# probability (Punjab/Rajasthan/Gujarat = western smuggling route from
# Pakistan/Afghanistan; Manipur/Mizoram = Golden Triangle route via Myanmar).
HOTSPOT_WEIGHT = {
    "Punjab": 9, "Rajasthan": 7, "Gujarat": 8, "Delhi": 6,
    "Manipur": 7, "Mizoram": 6, "Maharashtra": 6, "Uttar Pradesh": 4,
    "Assam": 5, "West Bengal": 4, "Odisha": 3, "Andhra Pradesh": 3,
    "Tamil Nadu": 3, "Kerala": 3, "Karnataka": 4, "Madhya Pradesh": 3,
    "Bihar": 3, "Jammu and Kashmir": 5, "Haryana": 4, "Telangana": 3,
}

AGENCIES = ["NCB", "State Police", "Customs", "Coast Guard", "BSF", "DRI"]


def jitter(val, spread):
    return val + RNG.uniform(-spread, spread)


# ---------------------------------------------------------------------------
# 1. Seizures dataset (Module 1 map/trends, Module 4 drug type, Module 5 pop.)
# Schema: seizure_id, date, year, month, state, district, latitude, longitude,
#         drug_type, quantity_kg, agency
# ---------------------------------------------------------------------------
def generate_seizures(n=6500):
    rows = []
    states = list(STATES.keys())
    weights = np.array([HOTSPOT_WEIGHT[s] for s in states], dtype=float)
    weights /= weights.sum()

    # Slight upward trend in total seizures over the years (2018-2024) to
    # reflect increasing enforcement activity / trafficking volume.
    year_weights = {y: 0.9 + 0.035 * (y - 2018) for y in YEARS}

    for i in range(n):
        state = RNG.choice(states, p=weights)
        lat0, lon0, _ = STATES[state]
        district = RNG.choice(DISTRICTS[state])
        year = RNG.choice(YEARS, p=np.array(list(year_weights.values())) / sum(year_weights.values()))
        month = RNG.integers(1, 13)
        day = RNG.integers(1, 28)

        drug = RNG.choice(
            DRUG_TYPES,
            p=[0.20, 0.24, 0.10, 0.08, 0.05, 0.12, 0.06, 0.03, 0.07, 0.05],
        )
        # Quantity distributions differ meaningfully by drug (kg equivalent)
        qty_base = {
            "Heroin": 4, "Cannabis (Ganja)": 120, "Charas/Hashish": 8,
            "Opium": 15, "Cocaine": 2, "Methamphetamine": 6, "MDMA": 1.5,
            "Ketamine": 3, "Pharmaceutical Opioids": 10, "Poppy Husk": 200,
        }[drug]
        quantity = max(0.05, RNG.exponential(qty_base))

        rows.append({
            "seizure_id": f"SZ{i+1:06d}",
            "date": f"{year}-{month:02d}-{day:02d}",
            "year": year,
            "month": month,
            "state": state,
            "district": district,
            "latitude": round(jitter(lat0, 0.8), 4),
            "longitude": round(jitter(lon0, 0.8), 4),
            "drug_type": drug,
            "quantity_kg": round(quantity, 2),
            "agency": RNG.choice(AGENCIES, p=[0.35, 0.30, 0.15, 0.05, 0.10, 0.05]),
        })

    df = pd.DataFrame(rows)

    # -----------------------------------------------------------------
    # Inject a lagged "surge wave" pattern along known corridor states so
    # the route-inference module has genuine signal to detect (rather than
    # only noise). Each year, a corridor gets 2-3 surge months where the
    # source state spikes, followed 1-2 months later by spikes in the
    # downstream corridor states, for the corridor's associated drug.
    # This is illustrative only -- real trafficking timing must come from
    # actual seizure records.
    # -----------------------------------------------------------------
    corridor_waves = [
        (["Punjab", "Rajasthan", "Gujarat", "Maharashtra"], "Heroin"),
        (["Manipur", "Mizoram", "Assam", "West Bengal"], "Methamphetamine"),
    ]
    extra_rows = []
    next_id = len(rows) + 1
    for states_seq, drug in corridor_waves:
        for year in YEARS:
            for _ in range(3):  # 3 surge events per corridor per year
                start_month = int(RNG.integers(1, 9))  # leave room for lag hops
                for hop_idx, state in enumerate(states_seq):
                    month = start_month + hop_idx  # +1 month lag per hop
                    if month > 12:
                        continue
                    lat0, lon0, _ = STATES[state]
                    district = RNG.choice(DISTRICTS[state])
                    day = int(RNG.integers(1, 28))
                    quantity = max(0.5, RNG.exponential(6) + 8)  # elevated surge quantity
                    extra_rows.append({
                        "seizure_id": f"SZC{next_id:06d}",
                        "date": f"{year}-{month:02d}-{day:02d}",
                        "year": year,
                        "month": month,
                        "state": state,
                        "district": district,
                        "latitude": round(jitter(lat0, 0.8), 4),
                        "longitude": round(jitter(lon0, 0.8), 4),
                        "drug_type": drug,
                        "quantity_kg": round(quantity, 2),
                        "agency": RNG.choice(AGENCIES, p=[0.35, 0.30, 0.15, 0.05, 0.10, 0.05]),
                    })
                    next_id += 1

    df = pd.concat([df, pd.DataFrame(extra_rows)], ignore_index=True)
    df.to_csv(OUT_DIR / "seizures.csv", index=False)
    print(f"seizures.csv -> {len(df)} rows (incl. {len(extra_rows)} corridor-wave records)")
    return df


# ---------------------------------------------------------------------------
# 2. Precursor chemical imports (Module 2)
# Schema: record_id, date, year, month, state, port_of_entry, chemical_name,
#         quantity_kg, declared_purpose, importer_name, is_anomaly
# ---------------------------------------------------------------------------
PRECURSORS = ["Acetic Anhydride", "Ephedrine", "Pseudoephedrine",
              "Potassium Permanganate", "Toluene", "Piperonal"]
PORTS = ["Nhava Sheva (JNPT)", "Mundra Port", "Chennai Port", "Kandla Port",
         "Kolkata Port", "Delhi Air Cargo", "Cochin Port"]


def generate_precursor_imports(n=1400):
    rows = []
    ports_state = {
        "Nhava Sheva (JNPT)": "Maharashtra", "Mundra Port": "Gujarat",
        "Chennai Port": "Tamil Nadu", "Kandla Port": "Gujarat",
        "Kolkata Port": "West Bengal", "Delhi Air Cargo": "Delhi",
        "Cochin Port": "Kerala",
    }
    for i in range(n):
        year = RNG.choice(YEARS)
        month = RNG.integers(1, 13)
        day = RNG.integers(1, 28)
        chem = RNG.choice(PRECURSORS)
        port = RNG.choice(PORTS)
        base_qty = {"Acetic Anhydride": 500, "Ephedrine": 50,
                    "Pseudoephedrine": 60, "Potassium Permanganate": 300,
                    "Toluene": 800, "Piperonal": 40}[chem]
        quantity = max(1, RNG.normal(base_qty, base_qty * 0.25))

        # Inject anomalies: ~4% of records get an unusually large spike,
        # simulating potential diversion for illicit drug synthesis.
        is_anomaly = RNG.random() < 0.04
        if is_anomaly:
            quantity *= RNG.uniform(4, 9)

        rows.append({
            "record_id": f"PC{i+1:06d}",
            "date": f"{year}-{month:02d}-{day:02d}",
            "year": year,
            "month": month,
            "state": ports_state[port],
            "port_of_entry": port,
            "chemical_name": chem,
            "quantity_kg": round(quantity, 1),
            "declared_purpose": RNG.choice(
                ["Pharmaceutical", "Textile/Dye", "Industrial Solvent", "Agrochemical"]
            ),
            "importer_name": f"Importer_{RNG.integers(1000, 9999)}",
            "is_anomaly": is_anomaly,
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "precursor_imports.csv", index=False)
    print(f"precursor_imports.csv -> {len(df)} rows")
    return df


# ---------------------------------------------------------------------------
# 3. Trade finance transactions (Module 3) -- SIMULATED for demonstration
# Schema: transaction_id, date, year, sender_state, receiver_state,
#         sender_account, receiver_account, amount_inr, transaction_type,
#         channel, risk_score, flagged
# ---------------------------------------------------------------------------
TXN_TYPES = ["Trade Invoice Payment", "Remittance", "Hawala-linked Transfer",
             "Shell Company Transfer", "Cash Deposit", "Crypto Off-ramp"]


def generate_trade_finance(n=3200):
    states = list(STATES.keys())
    rows = []
    for i in range(n):
        year = RNG.choice(YEARS)
        month = RNG.integers(1, 13)
        day = RNG.integers(1, 28)
        sender_state = RNG.choice(states)
        receiver_state = RNG.choice(states)
        txn_type = RNG.choice(
            TXN_TYPES, p=[0.35, 0.25, 0.10, 0.10, 0.15, 0.05]
        )
        amount = max(1000, RNG.lognormal(mean=11.5, sigma=1.3))

        # Higher risk score for hawala/shell-company/crypto patterns and
        # very large or suspiciously round amounts.
        risk = 0.0
        if txn_type in ("Hawala-linked Transfer", "Shell Company Transfer", "Crypto Off-ramp"):
            risk += 0.45
        if amount > 2_000_000:
            risk += 0.25
        if amount % 100000 == 0:
            risk += 0.10
        if sender_state != receiver_state:
            risk += 0.10
        risk += RNG.uniform(0, 0.2)
        risk = min(1.0, round(risk, 2))

        rows.append({
            "transaction_id": f"TX{i+1:07d}",
            "date": f"{year}-{month:02d}-{day:02d}",
            "year": year,
            "sender_state": sender_state,
            "receiver_state": receiver_state,
            "sender_account": f"ACC{RNG.integers(100000, 999999)}",
            "receiver_account": f"ACC{RNG.integers(100000, 999999)}",
            "amount_inr": round(amount, 2),
            "transaction_type": txn_type,
            "channel": RNG.choice(["Bank Transfer", "UPI", "Hawala Network", "Crypto Exchange", "Cash"]),
            "risk_score": risk,
            "flagged": risk >= 0.65,
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "trade_finance.csv", index=False)
    print(f"trade_finance.csv -> {len(df)} rows")
    return df


# ---------------------------------------------------------------------------
# 4. State population reference (Module 5)
# Schema: state, population_millions
# ---------------------------------------------------------------------------
def generate_population():
    df = pd.DataFrame(
        [{"state": s, "population_millions": v[2]} for s, v in STATES.items()]
    )
    df.to_csv(OUT_DIR / "state_population.csv", index=False)
    print(f"state_population.csv -> {len(df)} rows")
    return df


# ---------------------------------------------------------------------------
# 5. Known trafficking corridors (reference data for route overlay on map)
# These reflect broad, publicly-reported trafficking corridor patterns
# (e.g. NCB annual reports, press briefings) at a state-level granularity —
# NOT operational intelligence. Schema:
#   corridor_name, hop_order, state, latitude, longitude, primary_drug_types, source_context
# ---------------------------------------------------------------------------
def generate_known_corridors():
    corridors = [
        # Golden Crescent (Afghanistan/Pakistan) western land route
        ("Golden Crescent Route", ["Punjab", "Rajasthan", "Gujarat", "Maharashtra"],
         "Heroin, Opium", "Land border entry via Punjab/Rajasthan, onward via road/port"),
        # Golden Triangle (Myanmar) north-eastern route
        ("Golden Triangle Route", ["Manipur", "Mizoram", "Assam", "West Bengal"],
         "Heroin, Methamphetamine", "Land border entry via Manipur/Mizoram, onward via Assam"),
        # Southern maritime route
        ("Southern Maritime Route", ["Kerala", "Tamil Nadu", "Andhra Pradesh"],
         "Hashish, Cocaine", "Maritime entry via southern coastline"),
        # Northern route via J&K/Punjab into NCR
        ("Northern Route", ["Jammu and Kashmir", "Punjab", "Haryana", "Delhi"],
         "Charas/Hashish, Heroin", "Land route from northern border areas toward NCR"),
        # Western Gujarat maritime route (synthetic drug labs)
        ("Western Maritime Route", ["Gujarat", "Rajasthan", "Madhya Pradesh"],
         "Methamphetamine, MDMA", "Coastal entry via Gujarat, onward to synthetic drug production hubs"),
    ]

    rows = []
    for corridor_name, states, drugs, context in corridors:
        for hop_order, state in enumerate(states, start=1):
            lat, lon, _ = STATES[state]
            rows.append({
                "corridor_name": corridor_name,
                "hop_order": hop_order,
                "state": state,
                "latitude": lat,
                "longitude": lon,
                "primary_drug_types": drugs,
                "source_context": context,
            })

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "known_corridors.csv", index=False)
    print(f"known_corridors.csv -> {len(df)} rows")
    return df


if __name__ == "__main__":
    generate_seizures()
    generate_precursor_imports()
    generate_trade_finance()
    generate_population()
    generate_known_corridors()
    print("\nAll simulated datasets generated in:", OUT_DIR)
