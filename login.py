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

# Custom Styling for Framed UI
def set_custom_css():
    st.markdown(
        """
        <style>
            /* Page Frame */
            .frame {
                display: flex;
                height: 80vh;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.2);
            }

            /* Sidebar */
            .sidebar {
                width: 40%;
                background: linear-gradient(135deg, #184E77, #1E3A8A);
                color: white;
                display: flex;
                flex-direction: column;
                justify-content: center;
                padding: 30px;
                text-align: center;
            }

            .sidebar-title {
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 20px;
            }

            .sidebar-quote {
                font-size: 1.2rem;
                font-weight: bold;
                font-style: italic;
                opacity: 0.9;
            }

            /* Login Box */
            .login-box {
                width: 60%;
                background: white;
                padding: 40px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                text-align: center;
            }

            .login-title {
                font-size: 2rem;
                font-weight: bold;
                color: #1E3A8A;
                margin-bottom: 20px;
            }

            /* Input Fields */
            .login-input {
                border: 2px solid #88C1D0;
                border-radius: 10px;
                padding: 14px;
                width: 80%;
                font-size: 1rem;
                margin-bottom: 10px;
                transition: all 0.2s ease-in-out;
                background: rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(10px);
            }

            .login-input:focus {
                border-color: #184E77;
                box-shadow: 0px 0px 12px rgba(24, 78, 119, 0.3);
                outline: none;
            }

            /* Button */
            .btn-login {
                background: linear-gradient(135deg, #1E3A8A, #3B82F6);
                color: white;
                border-radius: 12px;
                padding: 14px;
                font-size: 1.2rem;
                width: 80%;
                border: none;
                font-weight: bold;
                transition: all 0.3s ease-in-out;
            }

            .btn-login:hover {
                transform: scale(1.05);
                box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
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

    # Page Frame
    st.markdown('<div class="frame">', unsafe_allow_html=True)

    # Sidebar - Information Panel
    random_quote = random.choice(motivation_quotes)
    st.markdown(
        f"""
        <div class="sidebar">
            <div class="sidebar-title">🌍 Climate Action Portal</div>
            <div class="sidebar-quote">{random_quote}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Login Box
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="login-title">{get_greeting()}<br>Sign in to Your Account</div>', unsafe_allow_html=True)

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

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # Close frame div

    # Footer
    st.markdown("<div class='footer'>© 2025 Hasar Organization for Climate Action</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    render_login()
