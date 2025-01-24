import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import pandas as pd

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch and process database
@st.cache_data(ttl=300)
def fetch_database():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1

        # Fetch data and convert to DataFrame
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # Convert 'Requested Amount' to formatted numbers
        df["Requested Amount"] = df["Requested Amount"].apply(lambda x: f"{int(x):,} IQD")

        return df
    except Exception as e:
        st.error(f"Error loading the database: {e}")
        return pd.DataFrame()

# Render the Database Page
def render_database():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>📊 Database Viewer</h2>", unsafe_allow_html=True)
    st.write("Monitor all requests and their statuses in real-time.")

    df = fetch_database()

    if df.empty:
        st.warning("No data available in the database.")
        return

    # Sidebar filters
    st.sidebar.markdown("### 🔍 Filter Requests")
    requester_filter = st.sidebar.text_input("Search by Requester Name:")
    project_filter = st.sidebar.text_input("Search by Project Name:")
    status_filter = st.sidebar.selectbox("Filter by Status:", ["All"] + df["Approval Status"].unique().tolist())

    # Apply filters
    if requester_filter:
        df = df[df["Requester name"].str.contains(requester_filter, case=False, na=False)]
    if project_filter:
        df = df[df["Project name"].str.contains(project_filter, case=False, na=False)]
    if status_filter != "All":
        df = df[df["Approval Status"] == status_filter]

    # Display summary stats
    st.markdown("### 📈 Summary Overview")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Requests", len(df))
    col2.metric("Pending Approvals", len(df[df["Approval Status"] == "Pending"]))
    col3.metric("Approved Requests", len(df[df["Approval Status"] == "Approved"]))
    col4.metric("Declined Requests", len(df[df["Approval Status"] == "Declined"]))

    # Display the database with improved styling
    st.markdown("### 📋 Request Data")

    st.dataframe(
        df.style.set_table_styles([
            {'selector': 'thead', 'props': [('background-color', '#1E3A8A'), ('color', 'white')]},
            {'selector': 'tbody tr:nth-child(odd)', 'props': [('background-color', '#f0f0f0')]},
            {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#ffffff')]}
        ]),
        height=500,
        use_container_width=True
    )

    # Export data section
    st.markdown("### 📤 Export Data")
    export_format = st.radio("Choose Export Format:", ["Excel", "CSV"])
    if st.button("Download"):
        if export_format == "Excel":
            df.to_excel("database_export.xlsx", index=False)
            with open("database_export.xlsx", "rb") as file:
                st.download_button("Download Excel", file, file_name="database_export.xlsx", mime="application/vnd.ms-excel")
        elif export_format == "CSV":
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, file_name="database_export.csv", mime="text/csv")

if __name__ == "__main__":
    render_database()
