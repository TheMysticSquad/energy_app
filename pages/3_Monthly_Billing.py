import streamlit as st
import pandas as pd
from prepaid_module_v2 import ConsumptionRecord

if "consumers" not in st.session_state:
    st.warning("Data not initialized. Please go back to the Home page.")
    st.stop()

st.title("Monthly Billing Summary")

# Select consumer
consumer_ids = [c.consumer_id + " - " + c.name for c in st.session_state.consumers]
selected_index = st.selectbox("Select Consumer", range(len(st.session_state.consumers)), format_func=lambda x: consumer_ids[x])
selected_consumer = st.session_state.consumers[selected_index]

st.subheader(f"Monthly Summary for {selected_consumer.name}")

if selected_consumer.consumption_records:
    records_df = pd.DataFrame([rec.__dict__ for rec in selected_consumer.consumption_records])
    records_df['timestamp'] = pd.to_datetime(records_df['timestamp'])
    records_df['Month'] = records_df['timestamp'].dt.to_period('M')

    monthly_summary = records_df.groupby('Month').agg(
        Total_KWh=('kwh_consumed', 'sum'),
        Total_Deductions=('total_deduction', 'sum')
    ).reset_index()

    monthly_summary['Month'] = monthly_summary['Month'].astype(str)
    st.dataframe(monthly_summary, use_container_width=True)
    
    st.subheader("Monthly Usage Visualization")
    st.bar_chart(monthly_summary.set_index('Month'))

else:
    st.info("No consumption records for this consumer.")
