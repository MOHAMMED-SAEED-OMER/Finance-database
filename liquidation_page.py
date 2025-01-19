import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import pytz

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch liquidation requests
@st.cache_data(ttl=60)
def fetch_liquidation_requests():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()

        # Convert data to DataFrame and filter for "To be liquidated"
        df = pd.DataFrame(data)
        liquidation_requests = df[df["Liquidation status"] == "To be liquidated"]
        return liquidation_requests
    except Exception as e:
        st.error(f"Error fetching liquidation requests: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Update liquidation details in the database
def process_liquidation(sheet, row_index, liquidated_amount, invoice_link):
    try:
        baghdad_tz = pytz.timezone("Asia/Baghdad")
        liquidation_date = datetime.now(baghdad_tz).strftime("%Y-%m-%d %H:%M:%S")

        # Retrieve the requested amount from the sheet
        requested_amount = float(sheet.cell(row_index, 10).value)

        # Calculate returned amount (requested - liquidated)
        returned_amount = requested_amount - liquidated_amount

        # Update liquidation details in Google Sheet
        sheet.update_cell(row_index, 17, "Liquidated")  # Column 17: Liquidation Status
        sheet.update_cell(row_index, 18, liquidated_amount)  # Column 18: Liquidated Amount
        sheet.update_cell(row_index, 19, liquidation_date)  # Column 19: Liquidation Date
        sheet.update_cell(row_index, 20, invoice_link)  # Column 20: Liquidated Invoices
        sheet.update_cell(row_index, 21, returned_amount)  # Column 21: Returned Amount

        return True
    except Exception as e:
        st.error(f"Error processing liquidation: {e}")
        return False

# Render Liquidation Page
def render_liquidation_page():
    st.title("💰 Liquidation Page")
    st.write("View and process pending liquidations.")

    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1

        # Fetch liquidation requests
        liquidation_requests = fetch_liquidation_requests()

        if liquidation_requests.empty:
            st.info("No pending liquidations to process.")
            return

        # Display pending liquidation requests
        st.write("### Requests Pending Liquidation")
        st.dataframe(liquidation_requests)

        # Select a request for liquidation
        trx_id = st.selectbox(
            "Select a Request by TRX ID:",
            options=liquidation_requests["TRX ID"].tolist(),
        )

        # Get the row index of the selected TRX ID
        row_index = liquidation_requests[liquidation_requests["TRX ID"] == trx_id].index[0] + 2  # +2 for header and 1-based indexing

        # Input fields for liquidation processing
        liquidated_amount = st.number_input("Enter Liquidated Amount (negative value):", value=0.0, step=0.01)
        invoice_link = st.text_input("Enter Liquidated Invoice Link:")

        if st.button("Submit Liquidation"):
            if liquidated_amount >= 0:
                st.warning("Liquidated amount must be negative.")
                return
            if not invoice_link:
                st.warning("Please enter an invoice link.")
                return
            
            success = process_liquidation(sheet, row_index, liquidated_amount, invoice_link)
            if success:
                st.success(f"Liquidation processed for request {trx_id}.")
                st.experimental_rerun()

    except Exception as e:
        st.error(f"Error loading liquidation page: {e}")
