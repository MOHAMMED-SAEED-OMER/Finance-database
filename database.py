import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch finance data from Google Sheets
@st.cache_data(ttl=300)
def fetch_database():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # Ensure numeric conversion for necessary columns
        df["Liquidated amount"] = pd.to_numeric(df["Liquidated amount"], errors="coerce").fillna(0)
        return df
    except Exception as e:
        st.error(f"Error loading the database: {e}")
        return pd.DataFrame()

# Render the Database Page
def render_database():
    st.markdown("<div class='page-title'>Database</div>", unsafe_allow_html=True)

    # Fetch database data
    df = fetch_database()
    if df.empty:
        st.warning("No data available in the database.")
        return

    # Display the database in a styled table
    st.markdown("<h3 style='color: #1E3A8A;'>Full Database Overview</h3>", unsafe_allow_html=True)
    st.dataframe(
        df.style.set_properties(
            **{
                "background-color": "#F3F4F6",
                "color": "#1E3A8A",
                "border-color": "#D1D5DB",
            }
        ).set_table_styles(
            [{"selector": "th", "props": [("background-color", "#1E3A8A"), ("color", "white")]}]
        ),
        height=600,
        use_container_width=True,
    )

    # Add a summary of key statistics
    st.markdown("<h3 style='color: #1E3A8A;'>Key Statistics</h3>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Entries", len(df))
    with col2:
        st.metric("Total Income", f"{df[df['TRX type'] == 'Income']['Liquidated amount'].sum():,.0f} IQD")
    with col3:
        st.metric("Total Expenses", f"{df[df['TRX type'] == 'Expense']['Liquidated amount'].sum():,.0f} IQD")
    with col4:
        st.metric("Pending Requests", len(df[df["Approval Status"] == "Pending"]))

    # Add a data visualization section
    st.markdown("<h3 style='color: #1E3A8A;'>Visualization</h3>", unsafe_allow_html=True)
    trx_type_count = df["TRX type"].value_counts()
    trx_type_chart = trx_type_count.plot(kind="bar", color=["#3B82F6", "#EF4444", "#F59E0B"], figsize=(8, 4))
    st.pyplot(trx_type_chart.figure)

if __name__ == "__main__":
    render_database()
