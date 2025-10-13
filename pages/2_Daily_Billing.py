import streamlit as st
import pandas as pd
from prepaid_module_v2 import ConsumptionRecord

if "consumers" not in st.session_state:
    st.warning("Data not initialized. Please go back to the Home page.")
    st.stop()

st.title("Daily Billing Sheet")

# Select consumer
consumer_ids = [c.consumer_id + " - " + c.name for c in st.session_state.consumers]
selected_index = st.selectbox("Select Consumer", range(len(st.session_state.consumers)), format_func=lambda x: consumer_ids[x])
selected_consumer = st.session_state.consumers[selected_index]

st.subheader(f"Billing Records for {selected_consumer.name}")

if selected_consumer.consumption_records:
    records = []
    for rec in selected_consumer.consumption_records:
        records.append({
            "Date": rec.timestamp.strftime("%Y-%m-%d %H:%M"),
            "KWh Used": rec.kwh_consumed,
            "Subsidy Units": rec.subsidy_units,
            "Energy Charge (EC)": f"₹{rec.energy_charge:.2f}",
            "Fixed Charge (FC)": f"₹{rec.fixed_charge:.2f}",
            "Total Deduction": f"₹{rec.total_deduction:.2f}",
            "Balance Before": f"₹{rec.balance_before:.2f}",
            "Balance After": f"₹{rec.balance_after:.2f}",
        })
    df = pd.DataFrame(records).sort_values(by="Date", ascending=False)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No consumption records for this consumer.")
