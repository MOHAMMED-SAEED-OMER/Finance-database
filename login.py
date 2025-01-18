import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import hashlib

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Hash a password for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Authenticate user
def authenticate_user(email, password):
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("Users")  # Use a "Users" tab
        users = sheet.get_all_records()

        hashed_password = hash_password(password)
        for user in users:
            if user["Email"] == email and user["Password"] == hashed_password:
                return user["Role"]  # Return the user's role if credentials match
        return None  # Return None if authentication fails
    except Exception as e:
        st.error(f"Error during authentication: {e}")
        return None

# Render the login page
def render_login():
    st.title("🔐 Login")
    st.write("Please enter your credentials to log in.")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        role = authenticate_user(email, password)
        if role:
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = email
            st.session_state["user_role"] = role
            st.success("Login successful!")
            st.experimental_rerun()  # Refresh to load the app
        else:
            st.error("Invalid email or password.")
