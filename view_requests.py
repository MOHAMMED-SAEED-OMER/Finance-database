import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch user requests
@st.cache_data(ttl=60)
def fetch_user_requests(email):
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()

        df = pd.DataFrame(data)
        user_requests = df[df["Requester name"] == email]
        return user_requests
    except Exception as e:
        st.error(f"Error fetching user requests: {e}")
        return pd.DataFrame()

# Render User Requests Page
def render_user_requests():
    st.title("My Requests")
    st.write("View all requests you have submitted.")

    email = st.session_state.get("user_email", "Unknown")
    user_requests = fetch_user_requests(email)

    if user_requests.empty:
        st.info("No requests found for your account.")
        return

    st.dataframe(
        user_requests[["TRX ID", "Project name", "Approval Status", "Requested Amount", "Request submission date"]],
        use_container_width=True,
    )

if __name__ == "__main__":
    render_user_requests()
