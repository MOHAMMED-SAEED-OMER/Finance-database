import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import pytz  # Ensure pytz is imported for timezone handling

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch all pending requests
@st.cache_data(ttl=60)
def fetch_pending_requests():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()

        # Convert data to DataFrame and filter for pending requests
        df = pd.DataFrame(data)
        pending_requests = df[df["Approval Status"] == "Pending"]
        return pending_requests
    except Exception as e:
        st.error(f"Error fetching pending requests: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Update approval status and date
def update_approval(sheet, row_index, status):
    try:
        baghdad_tz = pytz.timezone("Asia/Baghdad")
        approval_date = datetime.now(baghdad_tz).strftime("%Y-%m-%d %H:%M:%S")

        # Update Approval Status
        sheet.update_cell(row_index, 12, status)  # Column 12: Approval Status
        # Update Approval Date
        sheet.update_cell(row_index, 13, approval_date)  # Column 13: Approval Date

        return True
    except Exception as e:
        st.error(f"Error updating approval status: {e}")
        return False

# Render Approver Page
def render_approver_page():
    st.title("🔎 Approver Page")
    st.write("Review pending requests and approve or decline them.")

    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1

        # Fetch pending requests
        pending_requests = fetch_pending_requests()

        if pending_requests.empty:
            st.info("No pending requests to review.")
            return

        # Display pending requests
        st.write("### Pending Requests")
        st.dataframe(pending_requests)

        # Select a request to approve or decline
        trx_id = st.selectbox(
            "Select a Request by TRX ID:",
            options=pending_requests["TRX ID"].tolist(),
        )

        # Action buttons
        col1, col2 = st.columns(2)

        if col1.button("Approve"):
            # Find the row index of the selected TRX ID
            row_index = pending_requests[pending_requests["TRX ID"] == trx_id].index[0] + 2  # +2 for header and 1-based indexing
            success = update_approval(sheet, row_index, "Approved")
            if success:
                st.success(f"Request {trx_id} has been approved.")
                st.experimental_rerun()

        if col2.button("Decline"):
            # Find the row index of the selected TRX ID
            row_index = pending_requests[pending_requests["TRX ID"] == trx_id].index[0] + 2  # +2 for header and 1-based indexing
            success = update_approval(sheet, row_index, "Declined")
            if success:
                st.warning(f"Request {trx_id} has been declined.")
                st.experimental_rerun()

    except Exception as e:
        st.error(f"Error loading approver page: {e}")
