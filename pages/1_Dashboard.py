import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

# Import session state data and classes
from prepaid_module_v2 import Consumer, ConsumptionRecord

# Check if data is initialized
if "consumers" not in st.session_state:
    st.warning("Data not initialized. Please go back to the Home page.")
    st.stop()

st.title("Consumer Dashboard & Management")

# Select consumer
consumer_ids = [c.consumer_id + " - " + c.name for c in st.session_state.consumers]
selected_index = st.selectbox("Select Consumer", range(len(st.session_state.consumers)), format_func=lambda x: consumer_ids[x])
selected_consumer = st.session_state.consumers[selected_index]

# Display consumer data horizontally
st.subheader("Consumer Details")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("ID", selected_consumer.consumer_id)
col2.metric("Name", selected_consumer.name)
col3.metric("Address", selected_consumer.address)
col4.metric("Phone", selected_consumer.phone)
col5.metric("Balance (₹)", f"{selected_consumer.balance:.2f}")

# Edit consumer details
st.subheader("Edit Consumer Details")
new_name = st.text_input("Name", selected_consumer.name)
new_address = st.text_input("Address", selected_consumer.address)
new_phone = st.text_input("Phone", selected_consumer.phone)
if st.button("Update Consumer Details"):
    selected_consumer.update_attribute("name", new_name)
    selected_consumer.update_attribute("address", new_address)
    selected_consumer.update_attribute("phone", new_phone)
    st.success("Consumer details updated!")
    st.experimental_rerun()

# Simulate batch consumption
st.subheader("Simulate Daily Consumption for Random Records")
num_records = st.slider("Number of Random Consumption Records", 1, 10, 6)

if st.button("Process Random Consumption"):
    for _ in range(num_records):
        kwh_used = round(random.uniform(1, 10), 2)
        timestamp = datetime.now() - timedelta(days=random.randint(0, 5))
        selected_consumer.billing.process_consumption(kwh_used, st.session_state.tariff, timestamp=timestamp)
    selected_consumer.send_alerts()
    st.success(f"Processed {num_records} random consumption records for {selected_consumer.name}")
    st.experimental_rerun()

# Recharge account
st.subheader("Recharge Account")
recharge_amount = st.number_input("Recharge Amount", min_value=0.0, value=50.0, step=10.0)
voucher_code = st.text_input("Voucher Code (Optional)")
if st.button("Recharge Now"):
    selected_consumer.billing.recharge(recharge_amount, voucher_code)
    selected_consumer.send_alerts()
    st.success(f"Account recharged by ₹{recharge_amount:.2f}")
    st.experimental_rerun()
