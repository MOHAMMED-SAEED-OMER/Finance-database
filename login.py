import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import pandas as pd
import hashlib
import datetime

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
        sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("Users")
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching user data: {e}")
        return pd.DataFrame()

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Determine greeting based on time
def get_greeting():
    now = datetime.datetime.now()
    hour = now.hour
    if 5 <= hour < 12:
        return "🌅 Good Morning!"
    elif 12 <= hour < 18:
        return "☀️ Good Afternoon!"
    else:
        return "🌙 Good Evening!"

# Custom CSS for styling
def set_custom_css():
    st.markdown(
        """
        <style>
            .header {
                font-size: 3rem;
                font-weight: bold;
                color: #1E3A8A;
                text-align: center;
                margin-bottom: 30px;
                font-family: 'Arial', sans-serif;
            }
            .login-container {
                max-width: 450px;
                margin: auto;
                padding: 2rem;
                background: linear-gradient(to bottom, #f0f4ff, #ffffff);
                border-radius: 15px;
                box-shadow: 0px 8px 30px rgba(0, 0, 0, 0.2);
                text-align: center;
            }
            .login-title {
                font-size: 1.8rem;
                font-weight: bold;
                color: #1E3A8A;
                margin-bottom: 10px;
                font-family: 'Arial', sans-serif;
            }
            .btn-login {
                background-color: #1E3A8A;
                color: #ffffff;
                border-radius: 8px;
                padding: 12px;
                font-size: 1.2rem;
                width: 100%;
                border: none;
                font-family: 'Arial', sans-serif;
            }
            .btn-login:hover {
                background-color: #3B82F6;
            }
            .animation-card {
                background-color: white;
                border-radius: 15px;
                box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.15);
                padding: 20px;
                text-align: center;
                max-width: 350px;
                margin: auto;
                margin-bottom: 20px;
            }
            .footer {
                font-size: 0.9rem;
                color: #374151;
                text-align: center;
                margin-top: 20px;
                font-family: 'Arial', sans-serif;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_login():
    set_custom_css()
    st.markdown("<div class='header'>Hasar Organization</div>", unsafe_allow_html=True)

    # Animated Climate GIF inside a card
    st.markdown(
        """
        <div class="animation-card">
            <img src="https://media.giphy.com/media/d31vTpVi1LAcDvdm/giphy.gif" width="150">
            <h4>🌍 Climate Action Portal</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown(f"<div class='login-title'>{get_greeting()}<br>Welcome to the Climate Action Portal</div>", unsafe_allow_html=True)

    # Login form
    email = st.text_input("📧 Email", placeholder="Enter your email")
    password = st.text_input("🔑 Password", placeholder="Enter your password", type="password")
    remember_me = st.checkbox("Keep me signed in")

    if st.button("Sign In", use_container_width=True):
        if not email or not password:
            st.warning("Please fill out all fields.")
            return

        try:
            # Fetch users from Google Sheets
            users = fetch_user_data()
            user = users[users["Email"].str.lower() == email.lower()]

            if user.empty:
                st.error("❌ User not found.")
                return

            user = user.iloc[0]
            hashed_password = user["Password"]
            role = user["Role"]

            if hash_password(password) != hashed_password:
                st.error("❌ Incorrect password.")
                return

            st.session_state["logged_in"] = True
            st.session_state["user_email"] = email
            st.session_state["user_role"] = role

            if remember_me:
                st.session_state["keep_signed_in"] = True
            else:
                st.session_state.pop("keep_signed_in", None)

            st.success("✅ Login successful! Redirecting...")

        except Exception as e:
            st.error(f"Error during login: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='footer'>© 2025 Hasar Organization for Climate Action</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    render_login()
