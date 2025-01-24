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
def fetch_pending_payments():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()

        df = pd.DataFrame(data)

        # Standardize column names to avoid case and spacing issues
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        # Define correct column keys in lowercase
        expected_columns = {
            "trx_id": "trx_id",
            "payment_status": "payment_status",
            "project_name": "project_name",
            "requested_amount": "requested_amount",
            "request_submission_date": "request_submission_date",
        }

        # Check if all expected columns exist
        missing_columns = [col for col in expected_columns.values() if col not in df.columns]
        if missing_columns:
            st.error(f"Missing columns in the Google Sheet: {', '.join(missing_columns)}")
            return pd.DataFrame()

        # Filter for pending payments
        pending_payments = df[df[expected_columns["payment_status"]].str.lower() == "pending"]

        # Return only relevant columns with corrected case
        return pending_payments[
            [expected_columns["trx_id"], expected_columns["project_name"], 
             expected_columns["requested_amount"], expected_columns["request_submission_date"]]
        ]
    except Exception as e:
        st.error(f"Error fetching pending payments: {e}")
        return pd.DataFrame()

# Update payment status and date
def issue_payment(trx_id):
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_values()
        headers = data[0]
        trx_id_col = headers.index("TRX ID") + 1

        for i, row in enumerate(data):
            if row[trx_id_col - 1] == trx_id:
                row_index = i + 1
                payment_status_col = headers.index("Payment Status") + 1
                payment_date_col = headers.index("Payment Date") + 1
                liquidation_status_col = headers.index("Liquidation Status") + 1

                baghdad_tz = pytz.timezone("Asia/Baghdad")
                payment_date = datetime.now(baghdad_tz).strftime("%Y-%m-%d %H:%M:%S")

                sheet.update_cell(row_index, payment_status_col, "Issued")
                sheet.update_cell(row_index, payment_date_col, payment_date)
                sheet.update_cell(row_index, liquidation_status_col, "To be liquidated")

                return True
        return False
    except Exception as e:
        st.error(f"Error issuing payment: {e}")
        return False

# Render Payment Page
def render_payment_page():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Payment Processing</h2>", unsafe_allow_html=True)
    st.write("View and process pending payments.")

    try:
        pending_payments = fetch_pending_payments()

        if pending_payments.empty:
            st.info("No pending payments to process.")
            return

        for index, payment in pending_payments.iterrows():
            with st.expander(f"Request ID: {payment['TRX ID']} - {payment['Project Name']}"):
                st.write(f"**Budget Line:** {payment['Budget Line']}")
                st.write(f"**Purpose:** {payment['Purpose']}")
                st.write(f"**Amount to be Paid:** {int(payment['Requested Amount']):,} IQD")
                st.write(f"**Approval Date:** {payment['Approval Date']}")

                if st.button(f"Issue Payment for {payment['TRX ID']}", key=f"issue_{payment['TRX ID']}"):
                    issue_payment(payment["TRX ID"])
                    st.success(f"Payment for {payment['TRX ID']} issued successfully.")
                    st.session_state["refresh_page"] = True

                if st.session_state.get("refresh_page", False):
                    st.session_state["refresh_page"] = False
                    st.rerun()

    except Exception as e:
        st.error(f"Error loading payment page: {e}")

if __name__ == "__main__":
    render_payment_page()
