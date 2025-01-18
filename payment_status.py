import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import pytz

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch approved and unissued requests
@st.cache_data(ttl=60)  # Cache data for 60 seconds
def fetch_pending_payments():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Filter for approved and unissued requests
        pending_payments = df[
            (df["Approval Status"] == "Approved") &
            (df["Payment Status"] != "Issued")
        ]
        return pending_payments
    except Exception as e:
        st.error(f"Error fetching pending payments: {e}")
        return pd.DataFrame()

# Update payment status in the database
def issue_payment(trx_id):
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()

        # Find the row to update
        for i, row in enumerate(data, start=2):  # Start from row 2 (excluding header)
            if row["TRX ID"] == trx_id:
                baghdad_tz = pytz.timezone("Asia/Baghdad")
                payment_date = datetime.now(baghdad_tz).strftime("%Y-%m-%d %H:%M:%S")

                # Update relevant columns
                sheet.update_cell(i, data[0].keys().index("Payment Status") + 1, "Issued")
                sheet.update_cell(i, data[0].keys().index("Payment Date") + 1, payment_date)
                sheet.update_cell(i, data[0].keys().index("Liquidation Status") + 1, "To be liquidated")

                st.success(f"Payment issued for TRX ID: {trx_id}")
                return

        st.warning(f"TRX ID {trx_id} not found.")
    except Exception as e:
        st.error(f"Error updating payment status: {e}")

# Render the Payment Status Page
def render_payment_status():
    st.title("💸 Payment Status")
    st.write("Issue payments for approved requests.")

    # Fetch approved and unissued requests
    pending_payments = fetch_pending_payments()

    if pending_payments.empty:
        st.info("No pending payments available.")
        return

    # Show pending payments in a table
    st.subheader("Pending Payments")
    st.dataframe(pending_payments)

    # Select a request to issue payment
    trx_id = st.selectbox("Select a TRX ID to issue payment:", options=[""] + list(pending_payments["TRX ID"]))

    if st.button("Issue Payment"):
        if not trx_id:
            st.warning("Please select a TRX ID.")
        else:
            issue_payment(trx_id)
