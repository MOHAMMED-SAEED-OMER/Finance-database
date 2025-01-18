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

# Fetch user data from Google Sheets
def fetch_user_data():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("User Profiles")
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching user data: {e}")
        return pd.DataFrame()

# Render the Login Page
def render_login():
    st.title("🔐 Login")
    st.write("Please enter your credentials to log in.")

    # Login form
    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")

    if st.button("Login"):
        if not email or not password:
            st.warning("Please fill out all fields.")
            return

        try:
            users = fetch_user_data()
            user = users[users["Email"] == email]

            if user.empty:
                st.error("User not found.")
                return

            # Check password
            user = user.iloc[0]  # Get the first matching user
            hashed_password = user["Password"]
            role = user["Role"]

            # Validate password
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash != hashed_password:
                st.error("Incorrect password.")
                return

            # Successful login
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = email
            st.session_state["user_role"] = role

            st.success("Login successful!")
            st.experimental_set_query_params(page="database")  # Redirect to the main page
        except Exception as e:
            st.error(f"Error during login: {e}")
