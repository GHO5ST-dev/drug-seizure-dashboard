"""
route_analysis.py
------------------
Infers likely trafficking route directions from seizure data by looking for
states whose monthly seizure activity (for the same drug type) is correlated
with a time lag — i.e. State A's seizure volume tends to rise a month or two
before State B's, consistent with product moving from A toward B along a
supply chain.

This is a simple exploratory heuristic for analyst triage, not a definitive
route-detection algorithm. Results should always be cross-checked against
known corridors and ground intelligence.
"""

import pandas as pd
import numpy as np
from itertools import combinations


def _monthly_series(df: pd.DataFrame, drug_type: str) -> pd.DataFrame:
    sub = df[df["drug_type"] == drug_type].copy()
    sub["period"] = pd.to_datetime(
        sub["year"].astype(str) + "-" + sub["month"].astype(str).str.zfill(2) + "-01"
    )
    pivot = (
        sub.groupby(["period", "state"])["quantity_kg"].sum()
        .unstack(fill_value=0)
        .sort_index()
    )
    return pivot


def infer_routes(
    df: pd.DataFrame,
    drug_type: str,
    min_corr: float = 0.45,
    max_lag: int = 2,
    min_state_volume: float = 1.0,
    top_n_states: int = 10,
) -> pd.DataFrame:
    """
    Returns a DataFrame of candidate directed routes:
      source_state, target_state, drug_type, lag_months, correlation
    A row means: source_state's monthly volume tends to lead target_state's
    monthly volume by `lag_months`, with Pearson correlation `correlation`.
    """
    pivot = _monthly_series(df, drug_type)
    if pivot.shape[0] < 6 or pivot.shape[1] < 2:
        return pd.DataFrame(
            columns=["source_state", "target_state", "drug_type", "lag_months", "correlation"]
        )

    totals = pivot.sum().sort_values(ascending=False)
    states = [s for s in totals.index if totals[s] >= min_state_volume][:top_n_states]

    results = []
    for a, b in combinations(states, 2):
        series_a = pivot[a]
        series_b = pivot[b]
        best = None
        for lag in range(0, max_lag + 1):
            if lag == 0:
                sa, sb = series_a, series_b
            else:
                sa, sb = series_a[:-lag], series_b[lag:]
            if len(sa) < 4 or sa.std() == 0 or sb.std() == 0:
                continue
            corr = np.corrcoef(sa.values, sb.values)[0, 1]
            if best is None or abs(corr) > abs(best[1]):
                best = (lag, corr)

        if best is None:
            continue
        lag, corr = best
        if lag > 0 and corr >= min_corr:
            # a leads b -> candidate route a -> b
            results.append((a, b, drug_type, lag, round(corr, 2)))
        elif lag == 0:
            # simultaneous: check the reverse lag direction too
            for lag2 in range(1, max_lag + 1):
                sb2, sa2 = series_b[:-lag2], series_a[lag2:]
                if len(sa2) < 4 or sa2.std() == 0 or sb2.std() == 0:
                    continue
                corr2 = np.corrcoef(sb2.values, sa2.values)[0, 1]
                if corr2 >= min_corr:
                    results.append((b, a, drug_type, lag2, round(corr2, 2)))
                    break

    return pd.DataFrame(
        results, columns=["source_state", "target_state", "drug_type", "lag_months", "correlation"]
    ).sort_values("correlation", ascending=False)


def attach_coords(routes: pd.DataFrame, state_coords: dict) -> pd.DataFrame:
    routes = routes.copy()
    routes["src_lat"] = routes["source_state"].map(lambda s: state_coords.get(s, (None, None))[0])
    routes["src_lon"] = routes["source_state"].map(lambda s: state_coords.get(s, (None, None))[1])
    routes["tgt_lat"] = routes["target_state"].map(lambda s: state_coords.get(s, (None, None))[0])
    routes["tgt_lon"] = routes["target_state"].map(lambda s: state_coords.get(s, (None, None))[1])
    return routes.dropna(subset=["src_lat", "src_lon", "tgt_lat", "tgt_lon"])
