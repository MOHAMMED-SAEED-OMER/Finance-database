import json
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

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

# Fetch data from Google Sheets
def fetch_data():
    try:
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        records = sheet.get_all_records()
        return records
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Add data to Google Sheets
def add_data(name, amount):
    try:
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        sheet.append_row([name, amount])
        st.success(f"Added record: {name}, {amount}")
    except Exception as e:
        st.error(f"Error adding data to Google Sheets: {e}")

# Streamlit Interface
st.title("Google Sheets Integration")

st.header("Fetch Data")
if st.button("Fetch Data"):
    data = fetch_data()
    if data:
        st.table(data)

st.header("Add Data")
name = st.text_input("Name")
amount = st.number_input("Amount", min_value=0.0, step=0.01)

if st.button("Add Data"):
    if name and amount:
        add_data(name, amount)
    else:
        st.warning("Please provide both Name and Amount.")
