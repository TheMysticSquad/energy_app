import streamlit as st
from datetime import datetime
from billing_logic import calculate_ht_bill

st.set_page_config(page_title="HT Billing Calculator", layout="wide")

st.title("⚡ HT Billing Simulator")

st.subheader("Enter Meter Readings")

col1, col2, col3, col4 = st.columns(4)

# Readings
prev_H1 = col1.number_input("Prev H1", 0.0)
curr_H1 = col2.number_input("Curr H1", 0.0)

prev_H2 = col1.number_input("Prev H2", 0.0)
curr_H2 = col2.number_input("Curr H2", 0.0)

prev_H3 = col1.number_input("Prev H3", 0.0)
curr_H3 = col2.number_input("Curr H3", 0.0)

prev_kvah = col3.number_input("Prev kVAh", 0.0)
curr_kvah = col4.number_input("Curr kVAh", 0.0)

mf = st.number_input("MF", min_value=0.1, value=1.0)

st.subheader("Tariff Inputs")

rate_H1, rate_H2, rate_H3 = st.columns(3)
subrate_col, fcrate_col, load_col = st.columns(3)

rate_H1 = rate_H1.number_input("Rate H1", 0.0)
rate_H2 = rate_H2.number_input("Rate H2", 0.0)
rate_H3 = rate_H3.number_input("Rate H3", 0.0)
subsidy_rate = subrate_col.number_input("Subsidy Rate", 0.0)
fc_rate = fcrate_col.number_input("FC Rate", 0.0)
load = load_col.number_input("Contract Load (kW/kVA)", 0.0)

st.subheader("Date Inputs")

dc_date = st.date_input("Disconnection Date")
agr_date = st.date_input("Agreement Date")
bill_prev = st.date_input("Previous Bill Date")
bill_curr = st.date_input("Current Bill Date")

if st.button("Calculate Bill"):
    inputs = {
        "current": {
            "H1": curr_H1, "H2": curr_H2, "H3": curr_H3,
            "kVAh": curr_kvah
        },
        "previous": {
            "H1": prev_H1, "H2": prev_H2, "H3": prev_H3,
            "kVAh": prev_kvah
        },
        "mf": mf,
        "load": load,
        "rates": {
            "H1": rate_H1, "H2": rate_H2, "H3": rate_H3,
            "subsidy": subsidy_rate,
            "FC": fc_rate,
        },
        "disconnection_date": dc_date,
        "agreement_date": agr_date,
        "bill_prev_date": bill_prev,
        "bill_curr_date": bill_curr,
    }

    df = calculate_ht_bill(inputs)
    st.success("✔ Bill Calculated")

    st.table(df.style.format({"Amount": "{:,.2f}"}))
