import streamlit as st
import pandas as pd
from prepaid_module_v2 import Consumer

if "consumers" not in st.session_state:
    st.warning("Data not initialized. Please go back to the Home page.")
    st.stop()

st.title("Disconnection Management")

# Check for disconnected and low balance consumers
disconnected_consumers = [c for c in st.session_state.consumers if c.status == "DISCONNECTED"]
low_balance_consumers = [c for c in st.session_state.consumers if c.status != "DISCONNECTED" and c.balance <= st.session_state.tariff.low_balance_threshold]

st.subheader("Disconnected Consumers")
if disconnected_consumers:
    disconnected_data = [{"ID": c.consumer_id, "Name": c.name, "Balance": f"₹{c.balance:.2f}"} for c in disconnected_consumers]
    df_disconnected = pd.DataFrame(disconnected_data)
    st.dataframe(df_disconnected, use_container_width=True)
else:
    st.success("No consumers are currently disconnected.")

st.subheader("Low Balance Alerts")
if low_balance_consumers:
    low_balance_data = [{"ID": c.consumer_id, "Name": c.name, "Balance": f"₹{c.balance:.2f}"} for c in low_balance_consumers]
    df_low_balance = pd.DataFrame(low_balance_data)
    st.warning(f"There are {len(low_balance_consumers)} consumers with low balances.")
    st.dataframe(df_low_balance, use_container_width=True)
else:
    st.success("No consumers have low balances.")

# Management actions
st.subheader("Manage Disconnected Consumers")
if disconnected_consumers:
    consumer_to_manage_id = st.selectbox("Select Consumer to Manage", [c.consumer_id for c in disconnected_consumers])
    consumer_to_manage = next(c for c in disconnected_consumers if c.consumer_id == consumer_to_manage_id)
    recharge_amount = st.number_input(f"Recharge Amount for {consumer_to_manage.name}", min_value=0.0, value=50.0, step=10.0)
    if st.button("Recharge & Reconnect"):
        consumer_to_manage.billing.recharge(recharge_amount)
        st.success(f"Consumer {consumer_to_manage.name} has been recharged and reconnected.")
        st.experimental_rerun()
