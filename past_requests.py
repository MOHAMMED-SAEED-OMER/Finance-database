import gspread
import streamlit as st
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

# Fetch past (approved/declined) requests
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
        return pd.DataFrame()

# Render Past Requests Page
def render_past_requests():
    st.title("Past Requests")
    st.write("View approved and declined requests.")

    past_requests = fetch_past_requests()

    if past_requests.empty:
        st.info("No past requests found.")
        return

    # Display past requests in a table
    st.dataframe(
        past_requests[["TRX ID", "Project name", "Approval Status", "Requested Amount", "Approval date"]],
        use_container_width=True,
    )

if __name__ == "__main__":
    render_past_requests()
