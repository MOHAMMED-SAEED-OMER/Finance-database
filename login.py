import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import pandas as pd
import hashlib
import datetime
import random
from streamlit_lottie import st_lottie
import requests

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

# Climate Facts
climate_facts = [
    "🌍 The Earth's temperature has risen by 1.1°C since 1880.",
    "🌿 Trees can absorb up to 48 pounds of CO₂ per year.",
    "💧 Only 3% of the Earth's water is fresh, and two-thirds of it is frozen.",
    "🔥 The last decade was the hottest ever recorded.",
    "🌱 Plant-based diets can reduce carbon footprints by 50%.",
    "🚲 Switching to cycling for short trips can reduce CO₂ emissions by 67%."
]

# Load Lottie animation from URL
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Animation URL (replace with any Lottie animation URL you prefer)
LOTTIE_URL = "https://assets1.lottiefiles.com/packages/lf20_hs1shz7u.json"

# Custom Styling for Modern UI
def set_custom_css():
    st.markdown(
        """
        <style>
            /* Center the entire login box */
            .login-container {
                max-width: 420px;
                margin: auto;
                padding: 30px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                backdrop-filter: blur(12px);
                box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.2);
                text-align: center;
                transition: all 0.3s ease-in-out;
            }
            .login-container:hover {
                transform: scale(1.02);
                box-shadow: 0px 10px 25px rgba(0, 0, 0, 0.3);
            }
            .header {
                font-size: 2.8rem;
                font-weight: bold;
                color: #1E3A8A;
                text-align: center;
                margin-bottom: 20px;
                font-family: 'Arial', sans-serif;
            }
            .climate-card {
                background: linear-gradient(135deg, #3B82F6, #6DD5FA);
                border-radius: 12px;
                padding: 18px;
                text-align: center;
                font-size: 1.2rem;
                color: white;
                font-weight: bold;
                box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.15);
                max-width: 380px;
                margin: auto;
                margin-bottom: 20px;
                transition: all 0.3s ease-in-out;
            }
            .climate-card:hover {
                transform: scale(1.03);
                box-shadow: 0px 6px 18px rgba(0, 0, 0, 0.2);
            }
            .login-title {
                font-size: 1.5rem;
                font-weight: bold;
                color: #1E3A8A;
                margin-bottom: 10px;
                font-family: 'Arial', sans-serif;
            }
            .login-input {
                border-radius: 10px;
                padding: 12px;
                width: 100%;
                border: 1px solid #ccc;
                font-size: 1rem;
                margin-bottom: 12px;
                text-align: center;
            }
            .btn-login {
                background-color: #1E3A8A;
                color: #ffffff;
                border-radius: 8px;
                padding: 12px;
                font-size: 1.1rem;
                width: 100%;
                border: none;
                font-family: 'Arial', sans-serif;
                transition: all 0.3s ease-in-out;
            }
            .btn-login:hover {
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
        unsafe_allow_html=True
    )

def render_login():
    set_custom_css()

    # Display Lottie animation at the top
    lottie_animation = load_lottieurl(LOTTIE_URL)
    if lottie_animation:
        st_lottie(lottie_animation, height=200, key="login_animation")

    st.markdown("<div class='header'>Hasar Organization</div>", unsafe_allow_html=True)

    # Climate Fact Card (New Feature)
    random_fact = random.choice(climate_facts)
    st.markdown(
        f"""
        <div class="climate-card">
            🌍 {random_fact}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Login Box
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown(f"<div class='login-title'>{get_greeting()}<br>Welcome to the Climate Action Portal</div>", unsafe_allow_html=True)

    # Login form
    email = st.text_input("📧 Email", placeholder="Enter your email", key="email")
    password = st.text_input("🔑 Password", placeholder="Enter your password", type="password", key="password")
    remember_me = st.checkbox("Keep me signed in")

    if st.button("Sign In", use_container_width=True, key="login_btn"):
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
