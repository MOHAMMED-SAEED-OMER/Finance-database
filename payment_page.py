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

# Fetch all pending payments
@st.cache_data(ttl=60)
def fetch_pending_payments():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()

        # Convert data to DataFrame and filter for pending payments
        df = pd.DataFrame(data)
        pending_payments = df[df["Payment status"] == "Pending"]
        return pending_payments
    except Exception as e:
        st.error(f"Error fetching pending payments: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Update payment status and date
def issue_payment(sheet, row_index):
    try:
        baghdad_tz = pytz.timezone("Asia/Baghdad")
        payment_date = datetime.now(baghdad_tz).strftime("%Y-%m-%d %H:%M:%S")

        # Update Payment Status (Column 14)
        sheet.update_cell(row_index, 14, "Issued")
        # Update Payment Date (Column 15)
        sheet.update_cell(row_index, 15, payment_date)
        # Update Liquidation Status (Column 17 - FIXED)
        sheet.update_cell(row_index, 17, "To be liquidated")

        return True
    except Exception as e:
        st.error(f"Error issuing payment: {e}")
        return False

# Render Payment Page
def render_payment_page():
    st.title("💵 Payment Processing")
    st.write("View and process pending payments.")

    # Session state to track issued payments
    if "issued_payment" not in st.session_state:
        st.session_state["issued_payment"] = None

    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1

        # Fetch pending payments
        pending_payments = fetch_pending_payments()

        if pending_payments.empty:
            st.info("No pending payments to process.")
            return

        # Display pending payments
        st.write("### Pending Payments")
        st.dataframe(pending_payments)

        # Select a request to process payment
        trx_id = st.selectbox(
            "Select a Request by TRX ID:",
            options=pending_payments["TRX ID"].tolist(),
        )

        # Action button
        if st.button("Issue Payment"):
            # Find the row index of the selected TRX ID
            row_index = pending_payments[pending_payments["TRX ID"] == trx_id].index[0] + 2  # +2 for header and 1-based indexing
            success = issue_payment(sheet, row_index)
            if success:
                st.session_state["issued_payment"] = trx_id
                st.success(f"Payment issued for request {trx_id}.")

        # Display a message if a payment was recently issued
        if st.session_state["issued_payment"]:
            st.info(f"Recently issued payment for TRX ID: {st.session_state['issued_payment']}")

    except Exception as e:
        st.error(f"Error loading payment page: {e}")
