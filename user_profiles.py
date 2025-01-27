import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import pandas as pd
import hashlib
import re

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

# Validate email format
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# Fetch user data with caching
@st.cache_data(ttl=300)
def fetch_user_data():
    client = load_credentials()
    sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("Users")
    user_data = sheet.get_all_records()
    return pd.DataFrame(user_data)

# Render the User Profiles Page
def render_user_profiles():
    st.title("🔑 User Profile Management")

    try:
        df = fetch_user_data()

        # Display current users with filtering option
        st.subheader("👥 Current Users")
        selected_role = st.selectbox("Filter by Role", ["All"] + df["Role"].unique().tolist())
        filtered_df = df if selected_role == "All" else df[df["Role"] == selected_role]
        st.data_editor(filtered_df, num_rows="dynamic", height=300)

        st.markdown("---")
        st.subheader("➕ Add New User")

        with st.form("add_user_form"):
            name = st.text_input("Name", placeholder="Enter full name")
            email = st.text_input("Email", placeholder="Enter email address")
            phone_number = st.text_input("Phone Number", placeholder="Enter phone number")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
            role = st.selectbox("Role", options=["Admin", "Approver", "Requester"])
            submit_button = st.form_submit_button("Add User")

        if submit_button:
            if not name or not email or not phone_number or not password or not confirm_password or not role:
                st.warning("Please fill out all required fields.")
            elif password != confirm_password:
                st.warning("Passwords do not match.")
            elif not is_valid_email(email):
                st.warning("Invalid email format.")
            else:
                try:
                    client = load_credentials()
                    sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("Users")

                    hashed_password = hash_password(password)
                    sheet.append_row([name, email, phone_number, hashed_password, role])
                    st.success(f"User {name} added successfully with role {role}.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error adding user: {e}")

        st.markdown("---")
        st.subheader("🗑️ Delete User")

        user_to_delete = st.selectbox("Select User to Delete", df["Email"])
        if st.button("Delete User"):
            try:
                client = load_credentials()
                sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("Users")
                row_index = df[df["Email"] == user_to_delete].index[0] + 2  # Account for header row in Google Sheets
                sheet.delete_rows(row_index)
                st.success(f"User {user_to_delete} deleted.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error deleting user: {e}")

    except Exception as e:
        st.error(f"Error loading user profiles: {e}")

if __name__ == "__main__":
    render_user_profiles()
