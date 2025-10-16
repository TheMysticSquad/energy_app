import streamlit as st
from datetime import datetime
from billing_engine import BillingEngine
from random import uniform
import time

st.set_page_config(page_title="Admin Tools", page_icon="🛠️", layout="wide")

st.title("🛠️ Admin Panel")

# Sidebar Navigation
st.sidebar.header("Admin Navigation")
admin_options = st.sidebar.radio(
    "Select Tool",
    (
        "User Management",
        "System Settings",
        "Logs",
        "Data Backup",
        "Billing Scheduler",  # ✅ New Section
    )
)

# -----------------------------------------
# 1️⃣ User Management
# -----------------------------------------
if admin_options == "User Management":
    st.subheader("User Management")
    st.write("Add, remove, or update users.")
    st.text_input("Search user by name or email")
    st.button("Add New User")
    st.button("Remove Selected User")
    st.button("Update User Info")

# -----------------------------------------
# 2️⃣ System Settings
# -----------------------------------------
elif admin_options == "System Settings":
    st.subheader("System Settings")
    st.write("Configure application settings.")
    st.checkbox("Enable Maintenance Mode")
    st.selectbox("Default Language", ["English", "Spanish", "French"])
    st.button("Save Settings")

# -----------------------------------------
# 3️⃣ Logs
# -----------------------------------------
elif admin_options == "Logs":
    st.subheader("System Logs")
    st.write("View recent activity and error logs.")
    st.button("Refresh Logs")
    st.text_area("Logs Output", "No logs to display.", height=200)

# -----------------------------------------
# 4️⃣ Data Backup
# -----------------------------------------
elif admin_options == "Data Backup":
    st.subheader("Data Backup & Restore")
    st.write("Backup or restore application data.")
    st.button("Backup Now")
    st.file_uploader("Restore from backup file", type=["zip", "tar"])
    st.button("Restore Data")

# -----------------------------------------
# 5️⃣ Billing Scheduler (New)
# -----------------------------------------
elif admin_options == "Billing Scheduler":
    st.subheader("⚡ Daily Billing Scheduler")
    st.write("Run or schedule automated daily billing for prepaid consumers.")

    # Simulated daily consumption generator
    def simulate_consumption(consumer):
        return round(uniform(1.5, 6.0), 2)

    # Create instance of BillingEngine
    billing_engine = BillingEngine()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Run Daily Billing Now"):
            with st.spinner("Processing daily billing..."):
                billing_engine.process_daily_billing(simulated_consumption_fn=simulate_consumption)
                st.success(f"✅ Daily Billing Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    with col2:
        if st.button("🧾 Generate Monthly Invoice"):
            with st.spinner("Generating monthly invoices..."):
                billing_engine.generate_monthly_invoices()
                st.success("✅ Monthly Invoice Generation Completed.")

    # Auto-Scheduler simulation (for cron job or background service)
    st.markdown("---")
    st.markdown("### 🕓 Auto Scheduler (Simulated)")
    auto_enabled = st.toggle("Enable Auto Daily Billing Scheduler", value=False)

    if auto_enabled:
        interval = st.slider("Run every (minutes)", min_value=1, max_value=60, value=5)
        st.info(f"Auto Scheduler Active — will run every {interval} minute(s) in background.")
        st.caption("💡 In production, use system cron or Celery instead of this simulation.")

        if st.button("Simulate Auto Run"):
            for i in range(3):  # Run a few simulated cycles
                billing_engine.process_daily_billing(simulated_consumption_fn=simulate_consumption)
                st.write(f"✅ Cycle {i+1} completed.")
                time.sleep(interval)

    # Display last billing log / timestamp
    st.markdown("---")
    st.write(f"🧩 Last Billing Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
