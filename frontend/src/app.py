import streamlit as st
import requests
import time

# Base URL for NSC API
NSC_API = "http://localhost:8000"

st.set_page_config(page_title="Disconnection-Reconnection Dashboard", layout="wide")
st.title("⚡ Disconnection & Reconnection Simulation Dashboard")

# Session state
if "tickets" not in st.session_state:
    st.session_state.tickets = {}

# Sidebar form for creating new request
st.sidebar.header("🔌 Create New Request")
consumer_id = st.sidebar.text_input("Consumer ID", "C12345")
request_id = st.sidebar.text_input("Request ID", f"REQ{int(time.time())}")
action = st.sidebar.selectbox("Action", ["DISCONNECT", "RECONNECT"])

if st.sidebar.button("Submit Request"):
    payload = {"consumer_id": consumer_id, "request_id": request_id, "action": action}
    try:
        res = requests.post(f"{NSC_API}/nsc/disconnect", json=payload, timeout=5)
        if res.status_code == 200:
            st.session_state.tickets[request_id] = {
                "consumer_id": consumer_id,
                "action": action,
                "status": "PENDING",
                "last_update": time.strftime("%H:%M:%S"),
            }
            st.sidebar.success("Request submitted successfully!")
        else:
            st.sidebar.error("Failed to submit request.")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# Refresh button
if st.button("🔄 Refresh Status"):
    try:
        # Fetch callback-updated statuses from NSC memory (simulate API)
        # Note: For production, NSC should expose /nsc/status endpoint
        res = requests.get(f"{NSC_API}/nsc/callback")  # Placeholder
    except Exception:
        pass  # For now, we'll rely on manual refreshes

# Display all tickets
st.subheader("📋 Ticket Status Overview")
if not st.session_state.tickets:
    st.info("No tickets yet. Use the sidebar to create one.")
else:
    for tid, ticket in st.session_state.tickets.items():
        with st.expander(f"Ticket {tid}"):
            st.write(f"**Consumer:** {ticket['consumer_id']}")
            st.write(f"**Action:** {ticket['action']}")
            st.write(f"**Status:** {ticket['status']}")
            st.write(f"**Last Updated:** {ticket['last_update']}")

            # Option to simulate status update from callback
            if st.button(f"Check Status ({tid})"):
                try:
                    # For simplicity, we'll assume callback already updated in NSC
                    # In production, call a GET endpoint here
                    ticket["status"] = "SUCCESS"
                    ticket["last_update"] = time.strftime("%H:%M:%S")
                    st.success(f"Ticket {tid} completed successfully.")
                except Exception as e:
                    st.error(str(e))

# Footer
st.markdown("---")
st.caption("Developed for NIS ↔ AMISP Integration Simulation • Streamlit Frontend")
