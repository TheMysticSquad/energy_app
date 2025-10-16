import streamlit as st
import pandas as pd
from billing_engine import BillingEngine
from database_manager import DatabaseManager

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Monthly Billing Summary", page_icon="📊", layout="wide")

st.title("📊 Monthly Billing Summary")

# -----------------------------
# INITIALIZE DB + BILLING ENGINE
# -----------------------------
db = DatabaseManager()
engine = BillingEngine()

# -----------------------------
# CONSUMER SELECTION
# -----------------------------
st.subheader("🔍 Select Consumer to View Billing Summary")

consumers = db.get_all_consumers()
if not consumers:
    st.warning("⚠️ No consumers found in the database.")
    st.stop()

consumer_options = {f"{c.consumer_id} - {c.name}": c.consumer_id for c in consumers}
selected_label = st.selectbox("Choose Consumer", list(consumer_options.keys()))
selected_consumer_id = consumer_options[selected_label]

# -----------------------------
# FETCH CONSUMPTION HISTORY
# -----------------------------
records = db.get_consumption_history(selected_consumer_id)

if not records or len(records) == 0:
    st.info("ℹ️ No consumption records found for this consumer.")
    st.stop()

# Convert to DataFrame
columns = [
    "timestamp", "kwh_consumed", "subsidy_units", "energy_charge",
    "fixed_charge", "total_deduction", "balance_before", "balance_after"
]
df = pd.DataFrame(records, columns=columns)

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["Month"] = df["timestamp"].dt.to_period("M").astype(str)

# -----------------------------
# MONTHLY AGGREGATION
# -----------------------------
monthly_summary = df.groupby("Month").agg(
    Total_KWh=("kwh_consumed", "sum"),
    Energy_Charge=("energy_charge", "sum"),
    Fixed_Charge=("fixed_charge", "sum"),
    Total_Deductions=("total_deduction", "sum"),
).reset_index()

st.markdown(f"### 💡 Monthly Summary for **{selected_label}**")

st.dataframe(
    monthly_summary.style.format({
        "Total_KWh": "{:.2f}",
        "Energy_Charge": "₹{:.2f}",
        "Fixed_Charge": "₹{:.2f}",
        "Total_Deductions": "₹{:.2f}",
    }),
    width="stretch"
)

# -----------------------------
# VISUALIZATION
# -----------------------------
st.subheader("📈 Monthly Consumption Trend")

tab1, tab2 = st.tabs(["📊 Energy Usage", "💰 Deductions Trend"])

with tab1:
    st.bar_chart(monthly_summary.set_index("Month")[["Total_KWh"]])

with tab2:
    st.line_chart(monthly_summary.set_index("Month")[["Total_Deductions"]])

# -----------------------------
# ACTIONS
# -----------------------------
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔁 Refresh Data"):
        st.experimental_rerun()

with col2:
    if st.button("🧾 Generate Monthly Invoice"):
        engine.run_monthly_invoice()
        st.success("✅ Monthly invoice generated successfully!")

with col3:
    if st.button("☁️ Sync with RMS Server"):
        engine.sync_invoices_with_rms()
        st.success("✅ RMS Sync Completed Successfully!")

st.markdown("---")

st.caption("⚡ Data powered by Prepaid Billing Engine | Version 2.0")
