import json
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

# Load the credentials from Streamlit Secrets
key_data = st.secrets["GOOGLE_CREDENTIALS"]
credentials = Credentials.from_service_account_info(key_data)

# Authenticate with Google Sheets
client = gspread.authorize(credentials)

# Open a specific Google Sheet by URL
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/YOUR-SPREADSHEET-ID/edit").sheet1

st.title("Google Sheets Integration")

if st.button("Fetch Data"):
    try:
        records = sheet.get_all_records()
        st.table(records)
    except Exception as e:
        st.error(f"Error: {e}")
