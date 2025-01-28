import streamlit as st
import pandas as pd
import hashlib
import gspread
from google.oauth2.service_account import Credentials

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

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

# Hash the password for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Render login page
def render_login():
    st.markdown(
        """
        <style>
            body {
                background: linear-gradient(135deg, #1E3A8A, #3B82F6);
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Arial', sans-serif;
            }
            .login-container {
                background: #fff;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.2);
                text-align: center;
                width: 100%;
                max-width: 400px;
                margin: auto;
            }
            .login-title {
                font-size: 24px;
                font-weight: bold;
                color: #1E3A8A;
                margin-bottom: 15px;
            }
            .greeting {
                font-size: 18px;
                color: #555;
                margin-bottom: 10px;
            }
            .form-control {
                border-radius: 8px;
                padding: 12px;
                width: 100%;
                margin-bottom: 15px;
                font-size: 14px;
            }
            .login-btn {
                background-color: #1E3A8A;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                transition: 0.3s;
                width: 100%;
                border: none;
            }
            .login-btn:hover {
                background-color: #3B82F6;
                transform: scale(1.05);
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
        unsafe_allow_html=True,
    )

    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>Hasar Organization</h2>", unsafe_allow_html=True)

    # Dynamic greeting
    hour = pd.Timestamp.now().hour
    if hour < 12:
        greeting = "🌅 Good Morning!"
    elif hour < 18:
        greeting = "☀️ Good Afternoon!"
    else:
        greeting = "🌙 Good Evening!"
    st.markdown(f"<p class='greeting'>{greeting}</p>", unsafe_allow_html=True)

    # Login form
    email = st.text_input("📧 Email", placeholder="Enter your email")
    password = st.text_input("🔑 Password", placeholder="Enter your password", type="password")

    if st.button("Sign In"):
        if not email or not password:
            st.warning("⚠️ Please fill out all fields.")
        else:
            # Fetch user data
            users = fetch_user_data()

            # Check if email exists
            user = users[users["Email"].str.lower() == email.lower()]
            if user.empty:
                st.error("❌ User not found.")
            else:
                # Validate password
                user = user.iloc[0]
                if hash_password(password) != user["Password"]:
                    st.error("❌ Incorrect password.")
                else:
                    # Login successful
                    st.session_state["logged_in"] = True
                    st.session_state["user_email"] = email
                    st.session_state["user_name"] = user.get("Name", "User")
                    st.session_state["user_role"] = user["Role"]
                    st.success("✅ Login successful! Redirecting...")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='footer'>© 2025 Hasar Organization for Climate Action</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    render_login()
