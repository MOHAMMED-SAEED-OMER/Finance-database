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

# Fetch all approved and declined requests
@st.cache_data(ttl=60)
def fetch_past_requests():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()
        
        df = pd.DataFrame(data)
        past_requests = df[df["Approval Status"].str.lower().isin(["approved", "declined"])]
        return past_requests
    except Exception as e:
        st.error(f"Error fetching past requests: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Update approval status, payment status, and dates
def update_approval(sheet, trx_id, status):
    try:
        baghdad_tz = pytz.timezone("Asia/Baghdad")
        current_date = datetime.now(baghdad_tz).strftime("%Y-%m-%d %H:%M:%S")

        # Get all data to find the row index
        data = sheet.get_all_values()
        headers = data[0]  # Get headers to identify column positions
        trx_id_col = headers.index("TRX ID") + 1  # Get TRX ID column position

        for i, row in enumerate(data):
            if row[trx_id_col - 1] == trx_id:
                row_index = i + 1  # Google Sheets row is 1-based index

                approval_status_col = headers.index("Approval Status") + 1
                approval_date_col = headers.index("Approval date") + 1
                payment_status_col = headers.index("Payment status") + 1

                sheet.update_cell(row_index, approval_status_col, status)
                sheet.update_cell(row_index, approval_date_col, current_date)

                if status == "Approved":
                    sheet.update_cell(row_index, payment_status_col, "Pending")  # Set payment to pending

                return True
        st.error("TRX ID not found in the database.")
        return False
    except Exception as e:
        st.error(f"Error updating approval status: {e}")
        return False

# Render the Approver Page
def render_approver_page():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Approver Panel</h2>", unsafe_allow_html=True)
    st.write("Manage and review project funding requests.")

    # Tabs for Pending and Past Requests
    tab1, tab2 = st.tabs(["Pending Requests", "Past Requests"])

    # Custom CSS for design
    st.markdown("""
        <style>
            .stSelectbox, .stButton {
                border-radius: 10px;
                border: 2px solid #1E3A8A;
                padding: 10px;
            }
            .stDataFrame {
                border: 2px solid #1E3A8A;
                border-radius: 10px;
            }
            .approve-btn {
                background-color: #1E3A8A;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }
            .approve-btn:hover {
                background-color: #3B82F6;
            }
            .decline-btn {
                background-color: #D32F2F;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }
            .decline-btn:hover {
                background-color: #B71C1C;
            }
        </style>
    """, unsafe_allow_html=True)

    # Session state for tracking processed requests
    if "processed_request" not in st.session_state:
        st.session_state["processed_request"] = None

    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1

        # Pending Requests Tab
        with tab1:
            pending_requests = fetch_pending_requests()

            if pending_requests.empty:
                st.info("No pending requests to review.")
                return

            st.write("### Pending Requests")
            st.dataframe(pending_requests)

            trx_id = st.selectbox(
                "Select a Request by TRX ID:",
                options=pending_requests["TRX ID"].tolist(),
            )

            col1, col2 = st.columns(2)

            if col1.button("Approve", key="approve_btn"):
                success = update_approval(sheet, trx_id, "Approved")
                if success:
                    st.session_state["processed_request"] = trx_id
                    st.success(f"Request {trx_id} has been approved.")
                    st.rerun()

            if col2.button("Decline", key="decline_btn"):
                success = update_approval(sheet, trx_id, "Declined")
                if success:
                    st.session_state["processed_request"] = trx_id
                    st.warning(f"Request {trx_id} has been declined.")
                    st.rerun()

            if st.session_state["processed_request"]:
                st.info(f"Recently processed request: {st.session_state['processed_request']}")

        # Past Requests Tab
        with tab2:
            past_requests = fetch_past_requests()

            if past_requests.empty:
                st.info("No past requests available.")
                return

            st.write("### Approved and Declined Requests")
            st.dataframe(past_requests)

    except Exception as e:
        st.error(f"Error loading approver page: {e}")

if __name__ == "__main__":
    render_approver_page()
