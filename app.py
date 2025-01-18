import json
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

# Title of the Streamlit App
st.title("Google Sheets Integration")

# Load credentials from Streamlit Secrets
try:
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    credentials = Credentials.from_service_account_info(key_data)
    client = gspread.authorize(credentials)
except Exception as e:
    st.error(f"Error loading credentials: {e}")
    st.stop()

# Google Sheet URL
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Function to fetch data from Google Sheets
def fetch_data():
    try:
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        records = sheet.get_all_records()  # Fetch all rows as a list of dictionaries
        return records
    except Exception as e:
        st.error(f"Error fetching data from Google Sheets: {e}")
        return None

# Function to add data to Google Sheets
def add_data(name, amount):
    try:
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        sheet.append_row([name, amount])  # Append a new row
        st.success(f"Added record: {name}, {amount}")
    except Exception as e:
        st.error(f"Error adding data to Google Sheets: {e}")

# Streamlit Buttons for Interaction
st.header("Fetch Data from Google Sheets")
if st.button("Fetch Data"):
    records = fetch_data()
    if records:
        st.write("Data from Google Sheets:")
        st.table(records)

st.header("Add Data to Google Sheets")
name = st.text_input("Name")
amount = st.number_input("Amount", min_value=0.0, step=0.01)

if st.button("Add Data"):
    if name and amount:
        add_data(name, amount)
    else:
        st.warning("Please provide both Name and Amount.")
