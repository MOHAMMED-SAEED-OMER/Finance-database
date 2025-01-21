import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch user's past requests
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
        st.error(f"Error fetching requests: {e}")
        return pd.DataFrame()

# Render the View Requests Page
def render_user_requests():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>📂 My Requests</h2>", unsafe_allow_html=True)
    st.write("Here you can view all your submitted requests.")

    user_email = st.session_state.get("user_email", "Unknown")
    requests_df = fetch_user_requests(user_email)

    if requests_df.empty:
        st.info("You have no submitted requests.")
    else:
        st.dataframe(requests_df, use_container_width=True)
