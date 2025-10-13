import streamlit as st
import pandas as pd
from datetime import datetime
from database_manager import DatabaseManager  # ✅ Use your DB interaction class

# -------------------------------
# Initialize DB Connection
# -------------------------------
db = DatabaseManager()

st.title("📅 Daily Billing Sheet")

# -------------------------------
# Consumer Selection
# -------------------------------
consumers = db.get_all_consumers()  # Returns list of Consumer objects
if not consumers:
    st.warning("No consumers found in database.")
    st.stop()

# Use dot notation instead of dict-like access
consumer_display = [f"{c.consumer_id} - {c.name}" for c in consumers]
selected_index = st.selectbox("Select Consumer", range(len(consumers)), format_func=lambda i: consumer_display[i])
selected_consumer = consumers[selected_index]
consumer_id = selected_consumer.consumer_id

st.subheader(f"Billing Records for **{selected_consumer.name}**")

# -------------------------------
# Fetch Consumption Records
# -------------------------------
records = db.get_consumption_history(consumer_id)

if not records:
    st.info("No consumption records found for this consumer.")
else:
    # records is a list of tuples; convert to DataFrame
    df = pd.DataFrame(records, columns=[
        "timestamp", "kwh_consumed", "subsidy_units",
        "energy_charge", "fixed_charge", "total_deduction",
        "balance_before", "balance_after"
    ])

    # Ensure consistent column formatting
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(by="timestamp", ascending=False)

    df["Date"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    df["Energy Charge (EC)"] = df["energy_charge"].apply(lambda x: f"₹{x:.2f}")
    df["Fixed Charge (FC)"] = df["fixed_charge"].apply(lambda x: f"₹{x:.2f}")
    df["Total Deduction"] = df["total_deduction"].apply(lambda x: f"₹{x:.2f}")
    df["Balance Before"] = df["balance_before"].apply(lambda x: f"₹{x:.2f}")
    df["Balance After"] = df["balance_after"].apply(lambda x: f"₹{x:.2f}")

    # Select only display columns
    display_cols = [
        "Date", "kwh_consumed", "subsidy_units",
        "Energy Charge (EC)", "Fixed Charge (FC)",
        "Total Deduction", "Balance Before", "Balance After"
    ]
    df = df[display_cols]

    st.dataframe(df, use_container_width=True)

    # -------------------------------
    # Export Option
    # -------------------------------
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📤 Download Billing Data (CSV)", csv, f"{consumer_id}_billing.csv", "text/csv")

# -------------------------------
# Consumer Summary
st.divider()
st.write("### Consumer Summary")
st.write(f"- **Consumer ID:** {selected_consumer.consumer_id}")
st.write(f"- **Name:** {selected_consumer.name}")
st.write(f"- **Address:** {selected_consumer.address}")
st.write(f"- **Phone:** {selected_consumer.phone}")
st.write(f"- **Current Balance:** ₹{selected_consumer.balance:.2f}")
st.write(f"- **Status:** {selected_consumer.status}")
