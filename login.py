import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import pandas as pd
import hashlib
import datetime
import random

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

# Generate dynamic greeting
def get_greeting():
    now = datetime.datetime.now()
    hour = now.hour
    if 5 <= hour < 12:
        return "☀️ Good Morning!"
    elif 12 <= hour < 18:
        return "🌤️ Good Afternoon!"
    else:
        return "🌙 Good Evening!"

# Motivational Messages
motivation_quotes = [
    "🌱 Every small action matters in the fight against climate change.",
    "🌍 Your journey towards a greener future starts today!",
    "🚀 Innovation and sustainability go hand in hand.",
    "🌿 A single tree can make a difference, so can you!",
    "💡 Climate action starts with knowledge and commitment."
]

# Custom Styling for Compact UI
def set_custom_css():
    st.markdown(
        """
        <style>
            body {
                margin: 0;
                padding: 0;
                background-color: #F3F4F6;
            }
            
            /* Centered Container */
            .login-container {
                width: 600px;
                margin: 40px auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0px 5px 20px rgba(0, 0, 0, 0.15);
                padding: 30px;
                text-align: center;
            }

            /* Header */
            .header-title {
                font-size: 2rem;
                font-weight: bold;
                color: #1E3A8A;
                margin-bottom: 10px;
            }

            /* Quote Box */
            .quote-box {
                background: #E3F2FD;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                font-size: 1.1rem;
                font-style: italic;
                font-weight: bold;
                color: #1E3A8A;
                box-shadow: 0px 3px 10px rgba(0, 0, 0, 0.1);
            }

            /* Input Fields */
            .login-input {
                width: 90%;
                padding: 12px;
                border-radius: 8px;
                border: 1px solid #A7B3C3;
                font-size: 1rem;
                margin-bottom: 15px;
                text-align: center;
                background: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(5px);
            }

            .login-input:focus {
                border-color: #1E3A8A;
                box-shadow: 0px 0px 8px rgba(30, 58, 138, 0.2);
                outline: none;
            }

            /* Button */
            .btn-login {
                background: linear-gradient(135deg, #1E3A8A, #3B82F6);
                color: white;
                font-weight: bold;
                padding: 12px;
                font-size: 1.1rem;
                width: 90%;
                border-radius: 8px;
                border: none;
                transition: 0.3s;
            }

            .btn-login:hover {
                transform: scale(1.03);
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2);
            }

            /* Footer */
            .footer {
                font-size: 0.9rem;
                color: #374151;
                text-align: center;
                margin-top: 20px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_login():
    set_custom_css()

    # Get random motivational message
    random_quote = random.choice(motivation_quotes)

    # Login Page Container
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    # Header
    st.markdown(f'<div class="header-title">{get_greeting()}</div>', unsafe_allow_html=True)
    
    # Quote Box
    st.markdown(f'<div class="quote-box">{random_quote}</div>', unsafe_allow_html=True)

    # Login Form
    email = st.text_input("📧 Email", placeholder="Enter your email", key="email")
    password = st.text_input("🔑 Password", placeholder="Enter your password", type="password", key="password")
    remember_me = st.checkbox("Keep me signed in")

    if st.button("Sign In", use_container_width=True, key="login_btn"):
        if not email or not password:
            st.warning("Please fill out all fields.")
            return

        try:
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

            st.success("✅ Login successful! Redirecting...")

        except Exception as e:
            st.error(f"Error during login: {e}")

    st.markdown("</div>", unsafe_allow_html=True)  # Close login-container

    # Footer
    st.markdown("<div class='footer'>© 2025 Hasar Organization for Climate Action</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    render_login()
