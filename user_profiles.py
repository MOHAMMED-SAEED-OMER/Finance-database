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

        # Calculate statistics
        total_users = len(df)
        admin_count = df[df["Role"] == "Admin"].shape[0]
        approver_count = df[df["Role"] == "Approver"].shape[0]
        requester_count = df[df["Role"] == "Requester"].shape[0]

        # Custom CSS for styling
        st.markdown("""
            <style>
                .stat-card {
                    background-color: #1E3A8A;
                    padding: 20px;
                    border-radius: 10px;
                    color: white;
                    text-align: center;
                    font-size: 24px;
                    box-shadow: 2px 2px 12px rgba(0,0,0,0.1);
                }
                .profile-card {
                    background-color: #F3F4F6;
                    padding: 15px;
                    border-radius: 10px;
                    margin-bottom: 10px;
                    box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
                    font-size: 18px;
                    color: #333;
                }
                .delete-btn {
                    background-color: #D32F2F;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                }
                .delete-btn:hover {
                    background-color: #B71C1C;
                }
            </style>
        """, unsafe_allow_html=True)

        # Display key statistics in cards
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<div class='stat-card'>Total Users<br><b>{total_users}</b></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='stat-card'>Admins<br><b>{admin_count}</b></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='stat-card'>Approvers<br><b>{approver_count}</b></div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='stat-card'>Requesters<br><b>{requester_count}</b></div>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("👥 User Profiles")

        # Display users as profile cards
        for index, row in df.iterrows():
            col1, col2 = st.columns([4, 1])
            col1.markdown(
                f"""
                <div class='profile-card'>
                    <b>Name:</b> {row['Name']}<br>
                    <b>Email:</b> {row['Email']}<br>
                    <b>Phone:</b> {row['Phone Number']}<br>
                    <b>Role:</b> {row['Role']}
                </div>
                """, unsafe_allow_html=True
            )
            if col2.button("❌ Delete", key=f"delete_{index}"):
                delete_user(row["Email"])
                st.experimental_rerun()

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

    except Exception as e:
        st.error(f"Error loading user profiles: {e}")

# Delete user function
def delete_user(email):
    try:
        df = fetch_user_data()
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("Users")

        row_index = df[df["Email"] == email].index[0] + 2  # Account for header row
        sheet.delete_rows(row_index)
        st.success(f"User {email} deleted.")
    except Exception as e:
        st.error(f"Error deleting user: {e}")

if __name__ == "__main__":
    render_user_profiles()
