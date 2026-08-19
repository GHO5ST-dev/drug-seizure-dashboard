import streamlit as st


pages = [
    st.Page("Dashboard.py", title="Dashboard", default=True),
    st.Page("pages/1_Seizure_Map.py", title="Seizure Map & Trends"),
    st.Page("pages/2_Precursor_Monitoring.py", title="Precursor Monitoring"),
    st.Page("pages/3_Trade_Finance_Analysis.py", title="Trade Finance Analysis"),
    st.Page("pages/4_Drug_Type_Distribution.py", title="Drug Type Distribution"),
    st.Page("pages/5_Population_Correlation.py", title="Population Correlation"),
]

pg = st.navigation(pages)
pg.run()
