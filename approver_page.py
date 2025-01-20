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

# Fetch all pending requests
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
        return pd.DataFrame()  # Return empty DataFrame on error

# Update approval status
def update_approval(sheet, trx_id, status):
    try:
        baghdad_tz = pytz.timezone("Asia/Baghdad")
        current_date = datetime.now(baghdad_tz).strftime("%Y-%m-%d %H:%M:%S")

        # Get all data to find the row index
        data = sheet.get_all_values()
        headers = data[0]
        trx_id_col = headers.index("TRX ID") + 1

        for i, row in enumerate(data):
            if row[trx_id_col - 1] == trx_id:
                row_index = i + 1  # Google Sheets row is 1-based index

                approval_status_col = headers.index("Approval Status") + 1
                approval_date_col = headers.index("Approval date") + 1
                payment_status_col = headers.index("Payment status") + 1

                sheet.update_cell(row_index, approval_status_col, status)
                sheet.update_cell(row_index, approval_date_col, current_date)

                if status == "Approved":
                    sheet.update_cell(row_index, payment_status_col, "Pending")

                return True
        st.error("TRX ID not found in the database.")
        return False
    except Exception as e:
        st.error(f"Error updating approval status: {e}")
        return False

# Render the Approver Page
def render_approver_page():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Approver Panel</h2>", unsafe_allow_html=True)
    st.write("Review and approve or decline funding requests.")

    # Custom CSS for styling
    st.markdown("""
        <style>
            .request-card {
                border: 2px solid #1E3A8A;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                background-color: #F8F9FA;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            }
            .request-header {
                font-size: 1.4rem;
                font-weight: bold;
                color: #1E3A8A;
                margin-bottom: 5px;
            }
            .request-detail {
                font-size: 1rem;
                color: #333333;
                margin-bottom: 10px;
            }
            .amount {
                font-size: 1.2rem;
                font-weight: bold;
                color: #D32F2F;
            }
            .approve-btn {
                background-color: #1E3A8A;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                border: none;
                font-size: 16px;
                cursor: pointer;
            }
            .approve-btn:hover {
                background-color: #3B82F6;
            }
            .decline-btn {
                background-color: #D32F2F;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                border: none;
                font-size: 16px;
                cursor: pointer;
            }
            .decline-btn:hover {
                background-color: #B71C1C;
            }
        </style>
    """, unsafe_allow_html=True)

    # Tabs for Pending and Past Requests
    tab1, tab2 = st.tabs(["Pending Requests", "Past Requests"])

    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1

        # Pending Requests Tab
        with tab1:
            pending_requests = fetch_pending_requests()

            if pending_requests.empty:
                st.info("No pending requests to review.")
                return

            for index, request in pending_requests.iterrows():
                st.markdown("<div class='request-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='request-header'>Project: {request['Project name']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='request-detail'><b>TRX ID:</b> {request['TRX ID']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='request-detail'><b>Budget Line:</b> {request['Budget line']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='request-detail'><b>Purpose:</b> {request['Purpose']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='request-detail'><b>Details:</b> {request['Detail']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='amount'>Requested Amount: {int(request['Requested Amount']):,} IQD</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='request-detail'><b>Submission Date:</b> {request['Request submission date']}</div>", unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                if col1.button("Approve", key=f"approve_{request['TRX ID']}"):
                    success = update_approval(sheet, request["TRX ID"], "Approved")
                    if success:
                        st.success(f"Request {request['TRX ID']} approved.")
                        st.rerun()

                if col2.button("Decline", key=f"decline_{request['TRX ID']}"):
                    success = update_approval(sheet, request["TRX ID"], "Declined")
                    if success:
                        st.warning(f"Request {request['TRX ID']} declined.")
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

        # Past Requests Tab (existing design retained)
        with tab2:
            past_requests = fetch_pending_requests()
            if past_requests.empty:
                st.info("No past requests available.")
                return

            st.write("### Approved and Declined Requests")
            st.dataframe(past_requests)

    except Exception as e:
        st.error(f"Error loading approver page: {e}")

if __name__ == "__main__":
    render_approver_page()
