# streamlit_prepaid_app.py
import streamlit as st
from prepaid_module_v2 import Consumer, TariffPlan

# -----------------------------
# Dummy Data
# -----------------------------
dummy_consumers = [
    Consumer("C101", "John Doe", "123 Street", "9999999999", balance=50),
    Consumer("C102", "Alice Smith", "456 Avenue", "8888888888", balance=100),
    Consumer("C103", "Bob Johnson", "789 Road", "7777777777", balance=30)
]

# Dummy tariff (same for all, can extend later)
tariff = TariffPlan(plan_id="A1", rate_per_kwh=5, fixed_charge_daily=2, low_balance_threshold=20, subsidy_units=2, subsidy_rate=1.0)

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Prepaid Electricity Management")

# Select consumer
consumer_ids = [c.consumer_id + " - " + c.name for c in dummy_consumers]
selected = st.selectbox("Select Consumer", consumer_ids)
selected_consumer = dummy_consumers[consumer_ids.index(selected)]

st.subheader("Consumer Details")
st.write(f"**ID:** {selected_consumer.consumer_id}")
st.write(f"**Name:** {selected_consumer.name}")
st.write(f"**Address:** {selected_consumer.address}")
st.write(f"**Phone:** {selected_consumer.phone}")
st.write(f"**Balance:** ₹{selected_consumer.balance:.2f}")
st.write(f"**Status:** {selected_consumer.status}")

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

# Simulate consumption
st.subheader("Simulate Daily Consumption")
kwh_used = st.number_input("KWh Consumed Today", min_value=0.0, value=5.0)
if st.button("Process Consumption"):
    selected_consumer.billing.process_consumption(kwh_used, tariff)
    selected_consumer.send_alerts()
    st.success(f"Processed {kwh_used} kWh for {selected_consumer.name}")

# Recharge account
st.subheader("Recharge Account")
recharge_amount = st.number_input("Recharge Amount", min_value=0.0, value=50.0)
voucher_code = st.text_input("Voucher Code (Optional)")
if st.button("Recharge"):
    selected_consumer.billing.recharge(recharge_amount, voucher_code)
    selected_consumer.send_alerts()
    st.success(f"Account recharged by ₹{recharge_amount:.2f}")

# Show daily billing sheet
st.subheader("Daily Billing Sheet")
import pandas as pd

if selected_consumer.consumption_records:
    records = []
    for rec in selected_consumer.consumption_records:
        records.append({
            "Date": rec.timestamp.strftime("%Y-%m-%d"),
            "KWh Used": rec.kwh_consumed,
            "Subsidy Units": rec.subsidy_units,
            "Energy Charge (EC)": rec.energy_charge,
            "Fixed Charge (FC)": rec.fixed_charge,
            "Total Deduction": rec.total_deduction,
            "Balance Before": rec.balance_before,
            "Balance After": rec.balance_after,
            "Status": selected_consumer.status
        })
    df = pd.DataFrame(records)
    st.dataframe(df)
else:
    st.write("No consumption records yet.")
