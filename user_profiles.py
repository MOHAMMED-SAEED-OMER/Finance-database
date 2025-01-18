import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import pandas as pd
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

# Render the User Profiles Page
def render_user_profiles():
    st.title("👤 User Profiles")
    st.write("Manage user accounts, roles, and passwords.")

    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("Users")

        # Fetch user data
        user_data = sheet.get_all_records()
        df = pd.DataFrame(user_data)

        # Display current users
        st.subheader("Current Users")
        st.dataframe(df, height=300)

        # Add new user form
        st.subheader("Add New User")
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone_number = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", options=["Admin", "Approver", "Requester"])

        if st.button("Add User"):
            if name and email and phone_number and password and role:
                hashed_password = hash_password(password)
                sheet.append_row([name, email, phone_number, hashed_password, role])
                st.success(f"User {name} added with role {role}.")
            else:
                st.warning("Please fill out all fields.")

        # Delete or modify user logic here (to be implemented)

    except Exception as e:
        st.error(f"Error loading user profiles: {e}")
