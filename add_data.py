import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from datetime import datetime

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Render the Add New Data Page
def render_add_data():
    st.title("➕ Add New Data")
    st.write("Use this page to add new data to the database dynamically.")

    try:
        # Authenticate and open the Google Sheet
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1

        # Fetch headers dynamically
        headers = sheet.row_values(1)  # Fetch the first row as headers

        # Input fields for each header
        data_to_add = []
        for header in headers:
            value = st.text_input(f"Enter {header}:")
            data_to_add.append(value)

        # Submit button to add data
        if st.button("Submit Data"):
            if any(data_to_add):  # Ensure at least one field is filled
                sheet.append_row(data_to_add)  # Append data to Google Sheet
                st.success("Data added successfully!")
            else:
                st.warning("Please fill at least one field.")

    except Exception as e:
        st.error(f"Error adding data to Google Sheets: {e}")
