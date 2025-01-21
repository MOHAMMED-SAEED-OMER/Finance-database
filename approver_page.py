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

# Fetch pending requests
@st.cache_data(ttl=60)
def fetch_pending_requests():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()

        df = pd.DataFrame(data)
        pending_requests = df[df["Approval Status"].str.lower() == "pending"]
        return pending_requests
    except Exception as e:
        st.error(f"Error fetching pending requests: {e}")
        return pd.DataFrame()

# Update approval status
def update_approval(trx_id, status):
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_values()
        headers = data[0]
        trx_id_col = headers.index("TRX ID") + 1

        for i, row in enumerate(data):
            if row[trx_id_col - 1] == trx_id:
                row_index = i + 1
                approval_status_col = headers.index("Approval Status") + 1
                approval_date_col = headers.index("Approval date") + 1
                payment_status_col = headers.index("Payment status") + 1

                sheet.update_cell(row_index, approval_status_col, status)
                sheet.update_cell(row_index, approval_date_col, datetime.now(pytz.timezone("Asia/Baghdad")).strftime("%Y-%m-%d %H:%M:%S"))

                if status == "Approved":
                    sheet.update_cell(row_index, payment_status_col, "Pending")

                return True
        return False
    except Exception as e:
        st.error(f"Error updating approval status: {e}")
        return False

# Render Approver Page
def render_approver_page():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Approver Panel</h2>", unsafe_allow_html=True)
    st.write("Review and approve or decline funding requests.")

    try:
        pending_requests = fetch_pending_requests()

        if pending_requests.empty:
            st.info("No pending requests to review.")
            return

        for index, request in pending_requests.iterrows():
            with st.expander(f"Request ID: {request['TRX ID']} - {request['Project name']}"):
                st.write(f"**Budget Line:** {request['Budget line']}")
                st.write(f"**Purpose:** {request['Purpose']}")
                st.write(f"**Requested Amount:** {int(request['Requested Amount']):,} IQD")
                st.write(f"**Submission Date:** {request['Request submission date']}")

                col1, col2 = st.columns(2)

                approve_button = col1.button(f"Approve {request['TRX ID']}", key=f"approve_{request['TRX ID']}")
                decline_button = col2.button(f"Decline {request['TRX ID']}", key=f"decline_{request['TRX ID']}")

                if approve_button:
                    if update_approval(request["TRX ID"], "Approved"):
                        st.success(f"Request {request['TRX ID']} approved.")
                        st.rerun()

                if decline_button:
                    if update_approval(request["TRX ID"], "Declined"):
                        st.warning(f"Request {request['TRX ID']} declined.")
                        st.rerun()

    except Exception as e:
        st.error(f"Error loading approver page: {e}")

if __name__ == "__main__":
    render_approver_page()
