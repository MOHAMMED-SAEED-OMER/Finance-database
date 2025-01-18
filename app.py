import json
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

# Title of the Streamlit App
st.title("Google Sheets Integration with Dynamic Headers")

# Load credentials from Streamlit Secrets
try:
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    client = gspread.authorize(credentials)
except Exception as e:
    st.error(f"Error loading credentials: {e}")
    st.stop()

# Google Sheets URL
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Function to fetch data and headers from Google Sheets
def fetch_headers():
    try:
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        headers = sheet.row_values(1)  # Fetch the first row as headers
        return headers
    except Exception as e:
        st.error(f"Error fetching headers from Google Sheets: {e}")
        return None

# Add new data dynamically based on headers
def add_data_dynamic(data):
    try:
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        sheet.append_row(data)  # Append the data as a new row
        st.success("Data added successfully!")
    except Exception as e:
        st.error(f"Error adding data to Google Sheets: {e}")

# Fetch headers dynamically
headers = fetch_headers()
if headers:
    st.write("Recognized Headers from Google Sheets:")
    st.write(headers)

    st.header("Add Data")
    data_to_add = []
    for header in headers:
        value = st.text_input(f"Enter {header}:")
        data_to_add.append(value)

    if st.button("Submit Data"):
        if any(data_to_add):  # Ensure at least one value is provided
            add_data_dynamic(data_to_add)
        else:
            st.warning("Please fill at least one field.")
