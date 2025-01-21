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

# Render the View Requests Page with Enhanced UI
def render_user_requests():
    # Page styling
    st.markdown("""
        <style>
            .title {
                text-align: center;
                color: #1E3A8A;
                font-size: 2.2rem;
                font-weight: bold;
            }
            .sub-text {
                text-align: center;
                color: #374151;
                font-size: 1.2rem;
                margin-bottom: 20px;
            }
            .card {
                padding: 20px;
                margin: 10px;
                border-radius: 10px;
                box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
                background-color: #F3F4F6;
            }
            .data-container {
                padding: 20px;
                border-radius: 10px;
                background-color: #FFFFFF;
                box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
            }
            .highlight {
                font-weight: bold;
                color: #2563EB;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='title'>📂 My Requests</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-text'>Track your submitted requests and check their status.</div>", unsafe_allow_html=True)

    # Fetching user's data
    user_email = st.session_state.get("user_email", "Unknown")
    requests_df = fetch_user_requests(user_email)

    # Filter options
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    status_filter = st.selectbox("Filter by Request Status:", ["All"] + requests_df["Approval Status"].unique().tolist())
    st.markdown("</div>", unsafe_allow_html=True)

    if not requests_df.empty:
        # Apply filters if selected
        if status_filter != "All":
            requests_df = requests_df[requests_df["Approval Status"] == status_filter]

        # Display request count summary
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Requests", len(requests_df))
        col2.metric("Approved", len(requests_df[requests_df["Approval Status"] == "Approved"]))
        col3.metric("Pending", len(requests_df[requests_df["Approval Status"] == "Pending"]))
        st.markdown("</div>", unsafe_allow_html=True)

        # Display requests in a styled dataframe
        st.markdown("<div class='data-container'>", unsafe_allow_html=True)
        st.dataframe(
            requests_df[["TRX ID", "Project name", "Requested Amount", "Approval Status", "Payment status", "Liquidation status"]],
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.warning("You have no submitted requests.")

if __name__ == "__main__":
    render_user_requests()
