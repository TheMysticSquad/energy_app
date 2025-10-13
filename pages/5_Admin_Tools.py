import streamlit as st

st.set_page_config(page_title="Admin Tools", page_icon="🛠️", layout="wide")

st.title("🛠️ Admin Panel")

st.sidebar.header("Admin Navigation")
admin_options = st.sidebar.radio(
    "Select Tool",
    ("User Management", "System Settings", "Logs", "Data Backup")
)

if admin_options == "User Management":
    st.subheader("User Management")
    st.write("Add, remove, or update users.")
    st.text_input("Search user by name or email")
    st.button("Add New User")
    st.button("Remove Selected User")
    st.button("Update User Info")

elif admin_options == "System Settings":
    st.subheader("System Settings")
    st.write("Configure application settings.")
    st.checkbox("Enable Maintenance Mode")
    st.selectbox("Default Language", ["English", "Spanish", "French"])
    st.button("Save Settings")

elif admin_options == "Logs":
    st.subheader("System Logs")
    st.write("View recent activity and error logs.")
    st.button("Refresh Logs")
    st.text_area("Logs Output", "No logs to display.", height=200)

elif admin_options == "Data Backup":
    st.subheader("Data Backup & Restore")
    st.write("Backup or restore application data.")
    st.button("Backup Now")
    st.file_uploader("Restore from backup file", type=["zip", "tar"])
    st.button("Restore Data")