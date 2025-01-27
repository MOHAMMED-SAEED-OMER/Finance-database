import gspread
import streamlit as st
import pandas as pd
import hashlib
from google.oauth2.service_account import Credentials
import plotly.express as px

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Hash password function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Fetch user data
@st.cache_data(ttl=300)
def fetch_user_data():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("Users")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"Error fetching user data: {e}")
        return pd.DataFrame()

# Delete a user from the sheet
def delete_user(email):
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("Users")
        records = sheet.get_all_records()

        for idx, record in enumerate(records, start=2):  # Skip header row
            if record["Email"] == email:
                sheet.delete_rows(idx)
                st.success("User deleted successfully!")
                st.experimental_rerun()
                return
        st.warning("User not found.")
    except Exception as e:
        st.error(f"Error deleting user: {e}")

# Render the User Profiles Page
def render_user_profiles():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>User Management</h2>", unsafe_allow_html=True)

    # Create tabbed interface
    tab1, tab2 = st.tabs(["User Overview", "Add New User"])

    # User Overview Tab
    with tab1:
        df = fetch_user_data()
        if df.empty:
            st.warning("No user data available.")
            return
        
        # Calculate user statistics
        total_users = df.shape[0]
        role_counts = df["Role"].value_counts().to_dict()

        # Layout for statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div class='user-box'>Total Users</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='user-count'>{total_users}</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='user-box'>Admins</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='user-count'>{role_counts.get('Admin', 0)}</div>", unsafe_allow_html=True)

        with col3:
            st.markdown("<div class='user-box'>Requesters</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='user-count'>{role_counts.get('Requester', 0)}</div>", unsafe_allow_html=True)

        # User data visualization
        role_chart = px.pie(df, names="Role", title="User Role Distribution", hole=0.4)
        st.plotly_chart(role_chart, use_container_width=True)

        # Display user list in card format with delete button
        for index, row in df.iterrows():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(
                    f"""
                    <div class='user-card'>
                        <strong>Name:</strong> {row['Name']}<br>
                        <strong>Email:</strong> {row['Email']}<br>
                        <strong>Role:</strong> {row['Role']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col2:
                if st.button("Delete", key=f"delete_{index}"):
                    delete_user(row["Email"])

    # Add New User Tab
    with tab2:
        st.subheader("Add a New User")
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone_number = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", options=["Admin", "Approver", "Requester"])

        if st.button("Add User"):
            if name and email and phone_number and password and role:
                hashed_password = hash_password(password)
                client = load_credentials()
                sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("Users")
                sheet.append_row([name, email, phone_number, hashed_password, role])
                st.success(f"User {name} added successfully with role {role}.")
            else:
                st.warning("Please fill in all required fields.")

    # Custom CSS for styling
    st.markdown("""
        <style>
            .user-box {
                font-size: 20px;
                font-weight: bold;
                background-color: #1E3A8A;
                color: white;
                text-align: center;
                padding: 15px;
                border-radius: 10px;
            }
            .user-count {
                font-size: 26px;
                font-weight: bold;
                color: #1E3A8A;
                text-align: center;
            }
            .user-card {
                background-color: #F3F4F6;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 10px;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            }
            .stButton>button {
                background-color: #D32F2F;
                color: white;
                border-radius: 10px;
                padding: 8px 16px;
                border: none;
            }
            .stButton>button:hover {
                background-color: #B71C1C;
            }
        </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    render_user_profiles()
