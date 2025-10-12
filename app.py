# app.py
import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from prepaid_module_v2 import Consumer, TariffPlan, ConsumptionRecord

# -----------------------------
# Dummy Data
# -----------------------------
dummy_consumers = [
    Consumer("C101", "John Doe", "123 Street", "9999999999", balance=50),
    Consumer("C102", "Alice Smith", "456 Avenue", "8888888888", balance=100),
    Consumer("C103", "Bob Johnson", "789 Road", "7777777777", balance=30)
]

# Dummy tariff (same for all)
tariff = TariffPlan(
    plan_id="A1",
    rate_per_kwh=5,
    fixed_charge_daily=2,
    low_balance_threshold=20,
    subsidy_units=2,
    subsidy_rate=1.0
)

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Prepaid Electricity Management")

# Select consumer
consumer_ids = [c.consumer_id + " - " + c.name for c in dummy_consumers]
selected_index = st.selectbox("Select Consumer", range(len(dummy_consumers)), format_func=lambda x: consumer_ids[x])
selected_consumer = dummy_consumers[selected_index]

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

# Simulate batch consumption
st.subheader("Simulate Daily Consumption for Random Records")
num_records = st.slider("Number of Random Consumption Records", 1, 10, 6)

if st.button("Process Random Consumption"):
    for _ in range(num_records):
        kwh_used = round(random.uniform(1, 10), 2)  # Random consumption 1-10 kWh
        timestamp = datetime.now() - timedelta(days=random.randint(0, 5))  # Random past 5 days
        selected_consumer.billing.process_consumption(kwh_used, tariff, timestamp=timestamp)
    selected_consumer.send_alerts()
    st.success(f"Processed {num_records} random consumption records for {selected_consumer.name}")

# Recharge account
st.subheader("Recharge Account")
recharge_amount = st.number_input("Recharge Amount", min_value=0.0, value=50.0, step=10.0)
voucher_code = st.text_input("Voucher Code (Optional)")
if st.button("Recharge Now"):
    selected_consumer.billing.recharge(recharge_amount, voucher_code)
    selected_consumer.send_alerts()
    st.success(f"Account recharged by ₹{recharge_amount:.2f}")

# Show updated daily billing sheet
st.subheader("Daily Billing Sheet")
if selected_consumer.consumption_records:
    records = []
    for rec in selected_consumer.consumption_records:
        records.append({
            "Date": rec.timestamp.strftime("%Y-%m-%d %H:%M"),
            "KWh Used": rec.kwh_consumed,
            "Subsidy Units": rec.subsidy_units,
            "Energy Charge (EC)": rec.energy_charge,
            "Fixed Charge (FC)": rec.fixed_charge,
            "Total Deduction": rec.total_deduction,
            "Balance Before": rec.balance_before,
            "Balance After": rec.balance_after,
            "Status": selected_consumer.status
        })
    df = pd.DataFrame(records).sort_values(by="Date", ascending=False)
    st.dataframe(df)
else:
    st.write("No consumption records yet.")
