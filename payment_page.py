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
        pending_payments = df[df["Payment status"].str.lower() == "pending"]

        return pending_payments
    except Exception as e:
        st.error(f"Error fetching pending payments: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Update payment status and date
def issue_payment(sheet, trx_id):
    try:
        baghdad_tz = pytz.timezone("Asia/Baghdad")
        payment_date = datetime.now(baghdad_tz).strftime("%Y-%m-%d %H:%M:%S")

        data = sheet.get_all_values()
        headers = data[0]
        trx_id_col = headers.index("TRX ID") + 1

        for i, row in enumerate(data):
            if row[trx_id_col - 1] == trx_id:
                row_index = i + 1
                payment_status_col = headers.index("Payment status") + 1
                payment_date_col = headers.index("Payment date") + 1
                liquidation_status_col = headers.index("Liquidation status") + 1

                # Update the sheet with payment details
                sheet.update_cell(row_index, payment_status_col, "Issued")
                sheet.update_cell(row_index, payment_date_col, payment_date)
                sheet.update_cell(row_index, liquidation_status_col, "To be liquidated")

                return True
        st.error("TRX ID not found in the database.")
        return False
    except Exception as e:
        st.error(f"Error issuing payment: {e}")
        return False

# Render Payment Page
def render_payment_page():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>💵 Payment Processing</h2>", unsafe_allow_html=True)
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

        st.markdown("<div class='sub-text'>Review the following pending payments:</div>", unsafe_allow_html=True)

        # Apply CSS for better styling
        st.markdown("""
            <style>
                .card {
                    background-color: #f9f9f9;
                    padding: 15px;
                    border-radius: 10px;
                    box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1);
                    margin-bottom: 15px;
                }
                .card-header {
                    font-size: 18px;
                    font-weight: bold;
                    color: #1E3A8A;
                }
                .card-body {
                    font-size: 16px;
                    color: #333;
                }
                .btn-approve {
                    background-color: #28a745;
                    color: white;
                    padding: 8px 16px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }
                .btn-approve:hover {
                    background-color: #218838;
                }
            </style>
        """, unsafe_allow_html=True)

        # Loop through each pending payment and display in card format
        for _, request in pending_payments.iterrows():
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='card-header'>Request ID: {request['TRX ID']} - {request['Project name']}</div>", unsafe_allow_html=True)
                st.markdown("<div class='card-body'>", unsafe_allow_html=True)
                st.write(f"**Budget Line:** {request['Budget line']}")
                st.write(f"**Purpose:** {request['Purpose']}")
                st.write(f"**Requested Amount:** {int(request['Requested Amount']):,} IQD")
                st.write(f"**Submission Date:** {request['Request submission date']}")
                st.markdown("</div>", unsafe_allow_html=True)

                # Approve Button
                if st.button(f"Issue Payment for {request['TRX ID']}", key=f"pay_{request['TRX ID']}"):
                    if issue_payment(sheet, request["TRX ID"]):
                        st.success(f"Payment issued for request {request['TRX ID']}.")
                        st.session_state["issued_payment"] = request["TRX ID"]
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

        # Display a message if a payment was recently issued
        if st.session_state["issued_payment"]:
            st.info(f"Recently issued payment for TRX ID: {st.session_state['issued_payment']}")

    except Exception as e:
        st.error(f"Error loading payment page: {e}")

if __name__ == "__main__":
    render_payment_page()
