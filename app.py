import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from datetime import datetime

# Title of the Streamlit App
st.title("Enhanced Google Sheets Integration")

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

# Fetch headers dynamically
@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_headers():
    try:
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        headers = sheet.row_values(1)  # Fetch the first row as headers
        return headers
    except Exception as e:
        st.error(f"Error fetching headers from Google Sheets: {e}")
        return None

# Fetch data dynamically
@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_data():
    try:
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        records = sheet.get_all_records()  # Fetch all rows
        return records
    except Exception as e:
        st.error(f"Error fetching data from Google Sheets: {e}")
        return None

# Add new data dynamically
def add_data_dynamic(data):
    try:
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        sheet.append_row(data)  # Append the data as a new row
        st.success("Data added successfully!")
    except Exception as e:
        st.error(f"Error adding data to Google Sheets: {e}")

# Recognize headers
headers = fetch_headers()

if headers:
    st.write("Recognized Headers from Google Sheets:")
    st.write(headers)

    # Display the current data in the Google Sheet
    st.header("Current Data")
    data = fetch_data()
    if data:
        st.table(data)

    # Add New Data
    st.header("Add New Data")
    data_to_add = []

    # Define validation rules (example: numeric, text, dropdowns)
    validation_rules = {
        "Expense Type": ["Income", "Expense"],  # Dropdown options
        "Amount": "numeric",
        "Date": "date",
    }

    # Generate dynamic input fields with validation
    for header in headers:
        if header in validation_rules:
            if isinstance(validation_rules[header], list):  # Dropdown
                value = st.selectbox(f"Enter {header}:", options=[""] + validation_rules[header])
            elif validation_rules[header] == "numeric":  # Numeric input
                value = st.number_input(f"Enter {header}:", step=0.01)
            elif validation_rules[header] == "date":  # Date input
                value = st.date_input(f"Enter {header}:", value=datetime.today())
            else:
                value = st.text_input(f"Enter {header}:")
        else:
            value = st.text_input(f"Enter {header}:")
        data_to_add.append(value)

    # Submit button to add data
    if st.button("Submit Data"):
        if any(data_to_add):  # Ensure at least one field is filled
            add_data_dynamic(data_to_add)
        else:
            st.warning("Please fill at least one field.")

