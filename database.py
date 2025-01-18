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

# Render the Database Page
def render_database():
    st.title("📊 Database Viewer")
    st.write("This page shows the current database in real-time.")

    try:
        # Authenticate and open the Google Sheet
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1

        # Fetch data
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # Show the data
        st.dataframe(df, height=400)

        # Full-screen option
        if st.button("View Full Screen"):
            st.write("Full Database:")
            st.dataframe(df)

    except Exception as e:
        st.error(f"Error loading the database: {e}")
