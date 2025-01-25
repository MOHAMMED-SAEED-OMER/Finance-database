import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch dropdown options from Helper tab (vertical structure with categories as columns)
@st.cache_data(ttl=60)
def fetch_dropdown_options_vertical():
    try:
        client = load_credentials()
        helper_sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("Helper")
        helper_data = helper_sheet.get_all_records()  # Read all rows as dictionaries
        
        dropdown_options = {}
        for key in helper_data[0].keys():  # Iterate over column headers
            dropdown_options[key] = [row[key] for row in helper_data if row[key]]  # Collect non-empty values
        return dropdown_options
    except Exception as e:
        st.error(f"Error fetching dropdown options: {e}")
        return {}

# Render the Add New Data Page
def render_add_data():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>📋 Add New Data</h2>", unsafe_allow_html=True)
    st.write("Use this page to add new data to the database dynamically.")

    try:
        # Authenticate and open the Google Sheet
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1

        # Fetch dropdown options
        dropdown_options = fetch_dropdown_options_vertical()

        # Fetch headers dynamically
        headers = sheet.row_values(1)  # Fetch the first row as headers

        # Custom CSS for better styling
        st.markdown("""
            <style>
                .stTextInput, .stSelectbox, .stDateInput {
                    border-radius: 10px;
                    border: 2px solid #1E3A8A;
                    padding: 10px;
                }
                .submit-btn {
                    background-color: #1E3A8A;
                    color: white;
                    font-size: 18px;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                }
                .submit-btn:hover {
                    background-color: #3B82F6;
                }
            </style>
        """, unsafe_allow_html=True)

        # Create form to prevent multiple submissions
        with st.form("data_entry_form"):
            data_to_add = []
            for header in headers:
                if header in dropdown_options:
                    value = st.selectbox(f"Select {header}:", options=[""] + dropdown_options[header])
                elif header.lower() == "date":
                    value = st.date_input(f"Enter {header}:", value=datetime.today())
                else:
                    value = st.text_input(f"Enter {header}:", placeholder=f"Type {header} here...")
                data_to_add.append(value)

            # Submit button to add data
            submit_button = st.form_submit_button("Submit Data", use_container_width=True)

            if submit_button:
                if any(data_to_add):  # Ensure at least one field is filled
                    sheet.append_row(data_to_add)  # Append data to Google Sheet
                    st.success("✅ Data added successfully!")
                    st.write("**Submitted Data:**")
                    st.write(dict(zip(headers, data_to_add)))
                else:
                    st.warning("⚠️ Please fill at least one field.")

    except Exception as e:
        st.error(f"Error adding data to Google Sheets: {e}")

if __name__ == "__main__":
    render_add_data()
