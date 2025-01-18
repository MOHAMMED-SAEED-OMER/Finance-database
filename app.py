import json
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

# Load the credentials from Streamlit Secrets
key_data = st.secrets["GOOGLE_CREDENTIALS"]
credentials = Credentials.from_service_account_info(key_data)

# Authenticate with Google Sheets
client = gspread.authorize(credentials)

# Open the Google Sheet by URL
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/YOUR-SPREADSHEET-ID/edit").sheet1

# Streamlit App Interface
st.title("Google Sheets Integration")

# Fetch and Display Data from Google Sheets
if st.button("Fetch Data"):
    try:
        # Get all records from the sheet
        data = sheet.get_all_records()  # List of dictionaries
        if data:
            st.write("Data from Google Sheets:")
            st.table(data)  # Display as a table
        else:
            st.info("No data found in the Google Sheet.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")

# Add a new record to the Google Sheet
st.header("Add Data to Google Sheets")
name = st.text_input("Name")
amount = st.number_input("Amount", min_value=0.0, step=1.0)

if st.button("Add Data"):
    try:
        if name and amount:
            # Append a new row to the Google Sheet
            sheet.append_row([name, amount])
            st.success(f"Added record: {name}, {amount}")
        else:
            st.warning("Please provide both Name and Amount.")
    except Exception as e:
        st.error(f"Error adding data: {e}")
