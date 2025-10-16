import streamlit as st
from datetime import datetime

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="Prepaid Electricity Management System",
    page_icon="⚡",
    layout="wide"
)
st.image("assets/logo.png", width=260, caption="Smart Energy Management")

# -----------------------------
# HEADER SECTION
# -----------------------------
st.title("⚡ Prepaid Electricity Management System")
st.markdown("#### Smart Monitoring • Daily Billing • Automated Disconnection")

st.markdown("---")

# -----------------------------
# INTRODUCTION
# -----------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### 🧭 Overview  
    The **Prepaid Electricity Management System** is designed to simplify billing, recharge,
    and consumption tracking for prepaid consumers.  

    #### 🔍 Key Features:
    - **Real-time Consumption Simulation**
    - **Automated Daily Billing**
    - **Recharge and Balance Management**
    - **Disconnection & Reconnection Automation**
    - **Admin Tools for Tariff Management**
    
    #### 📊 Upcoming Features:
    - Monthly analytics and insights dashboard  
    - Alerts via Email/SMS integration  
    - Smart prepaid meter sync (IoT Ready)
    """)
    st.markdown("---")

    st.markdown(f"📅 **Current System Date:** {datetime.now().strftime('%A, %d %B %Y')}")

with col2:
    st.image("assets/logo.png", width=260, caption="Smart Energy Management")

# -----------------------------
# NAVIGATION GUIDANCE
# -----------------------------
st.markdown("### 🧭 Quick Navigation")
cols = st.columns(3)
cols[0].page_link("pages/1_Dashboard.py", label="📋 Dashboard")
cols[1].page_link("pages/2_Daily_Billing_Sheet.py", label="📈 Daily Billing Sheet")
cols[2].page_link("pages/3_Monthly_Billing.py", label="📊 Monthly Billing")

cols = st.columns(3)
cols[0].page_link("pages/Disconnection_Management.py", label="🔌 Disconnection Management")
cols[1].page_link("pages/5_Admin_Tools.py", label="⚙️ Admin Tools")
cols[2].markdown("")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("""
<div style='text-align:center; font-size:13px; color:grey;'>
Developed as part of <b>Smart Prepaid Solution</b> — Version 2.0  
© 2025 SmartGrid Systems | Internal Prototype Build
</div>
""", unsafe_allow_html=True)
