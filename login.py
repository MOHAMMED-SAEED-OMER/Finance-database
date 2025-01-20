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

# Fetch user data from Google Sheets
def fetch_user_data():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("Users")
        data = sheet.get_all_records()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Ensure expected columns exist
        required_columns = {"Email", "Password", "Role"}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"The Users sheet must include the following columns: {required_columns}")

        return df
    except Exception as e:
        st.error(f"Error fetching user data: {e}")
        return pd.DataFrame()

# Hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Render the Login Page
def render_login():
    st.markdown(
        """
        <style>
            body {
                background-color: #1E3A8A;
                color: #ffffff;
                font-family: 'Arial', sans-serif;
            }
            .stApp {
                background-color: #1E3A8A;
            }
            .login-container {
                max-width: 450px;
                margin: 5% auto;
                padding: 2rem;
                background: #ffffff;
                border-radius: 12px;
                box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.2);
                text-align: center;
            }
            .login-title {
                font-size: 2rem;
                font-weight: bold;
                color: #1E3A8A;
                margin-bottom: 10px;
            }
            .login-subtitle {
                font-size: 1.2rem;
                font-weight: normal;
                color: #374151;
                margin-bottom: 20px;
            }
            .stTextInput>div>div>input {
                text-align: center;
            }
            .btn-login {
                background-color: #1E3A8A;
                color: #ffffff;
                border-radius: 5px;
                padding: 10px;
                font-size: 1.1rem;
                width: 100%;
                border: none;
            }
            .btn-login:hover {
                background-color: #3B82F6;
            }
            .checkbox-label {
                color: #000000;
                font-size: 1rem;
            }
            .footer {
                font-size: 0.9rem;
                color: #E5E7EB;
                text-align: center;
                margin-top: 20px;
            }
            .st-emotion-cache-1kyxreq {
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<div class='login-title'>Welcome Back!</div>", unsafe_allow_html=True)
    st.markdown("<div class='login-subtitle'>Secure access to your finance dashboard</div>", unsafe_allow_html=True)

    # Use session state to persist credentials
    if "saved_email" not in st.session_state:
        st.session_state.saved_email = ""
    if "saved_password" not in st.session_state:
        st.session_state.saved_password = ""

    with st.form("login_form"):
        email = st.text_input("Email:", value=st.session_state.saved_email, placeholder="Enter your email")
        password = st.text_input("Password:", value=st.session_state.saved_password, placeholder="Enter your password", type="password")
        remember_me = st.checkbox("Keep me signed in", key="remember_me")
        submit_button = st.form_submit_button("Sign In", use_container_width=True)

    if submit_button:
        if not email or not password:
            st.warning("Please fill out all fields.")
            return

        try:
            # Fetch users from Google Sheets
            users = fetch_user_data()
            user = users[users["Email"].str.lower() == email.lower()]

            if user.empty:
                st.error("User not found.")
                return

            # Get the first matching user
            user = user.iloc[0]
            hashed_password = user["Password"]
            role = user["Role"]

            # Validate password
            password_hash = hash_password(password)
            if password_hash != hashed_password:
                st.error("Incorrect password.")
                return

            # Successful login
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = email
            st.session_state["user_role"] = role

            # Save session state if "Remember Me" is checked
            if remember_me:
                st.session_state.saved_email = email
                st.session_state.saved_password = password
            else:
                st.session_state.saved_email = ""
                st.session_state.saved_password = ""

            st.success("Login successful! Redirecting...")

            # Redirect to database page after login
            st.query_params.update({"page": "database"})

        except Exception as e:
            st.error(f"Error during login: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='footer'>© 2025 Hasar Organization for Climate Action</div>", unsafe_allow_html=True)
