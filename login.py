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

# Log login attempts to Google Sheets
def log_login_attempt(email, success):
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("LoginLogs")
        sheet.append_row([email, str(success), str(pd.Timestamp.now())])
    except Exception as e:
        st.warning(f"Failed to log login attempt: {e}")

# Hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Custom CSS for styling improvements
def set_custom_css():
    st.markdown(
        """
        <style>
            body {
                font-family: 'Arial', sans-serif;
            }
            .header {
                font-size: 3rem;
                font-weight: bold;
                color: #0D3B66;
                text-align: center;
                margin-bottom: 20px;
            }
            .login-container {
                max-width: 450px;
                margin: auto;
                padding: 2rem;
                background: #F9FAFB;
                border: 2px solid #D1D5DB;
                border-radius: 15px;
                box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            .login-title {
                font-size: 1.8rem;
                font-weight: bold;
                color: #0D3B66;
                margin-bottom: 20px;
            }
            .login-input {
                margin-bottom: 15px;
            }
            .btn-login {
                background-color: #0D3B66;
                color: #ffffff;
                border-radius: 8px;
                padding: 10px;
                font-size: 1.2rem;
                width: 100%;
                border: none;
                font-family: 'Arial', sans-serif;
            }
            .btn-login:hover {
                background-color: #2563EB;
            }
            .footer {
                font-size: 0.9rem;
                color: #6B7280;
                text-align: center;
                margin-top: 20px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def logout():
    st.session_state.clear()
    st.success("Logged out successfully!")
    st.experimental_rerun()

def render_login():
    set_custom_css()
    st.markdown("<div class='header'>Hasar Organization</div>", unsafe_allow_html=True)

    # Login box container
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<div class='login-title'>Sign in to Your Account</div>", unsafe_allow_html=True)

    # Check if the user is already logged in
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.success("You are already logged in.")
        return

    # Use session state to store login inputs
    if "email" not in st.session_state:
        st.session_state.email = ""
    if "password" not in st.session_state:
        st.session_state.password = ""

    # Login form
    email = st.text_input("📧 Email", value=st.session_state.email, placeholder="Enter your email", key="email_input", help="Your registered email")
    password = st.text_input("🔑 Password", value=st.session_state.password, placeholder="Enter your password", type="password", key="password_input", help="Your account password")
    remember_me = st.checkbox("Keep me signed in", key="remember_me")

    if st.button("Sign In", use_container_width=True, key="login_button"):
        if not email or not password:
            st.warning("Please fill out all fields.")
            return

        try:
            # Fetch users from Google Sheets
            users = fetch_user_data()
            if users.empty:
                st.info("No users found. Please contact your administrator.")
                return

            user = users[users["Email"].str.lower() == email.lower()]

            if user.empty:
                st.error("❌ User not found. Please check your email or contact your administrator.")
                log_login_attempt(email, success=False)
                return

            # Get the first matching user
            user = user.iloc[0]
            hashed_password = user["Password"]
            role = user["Role"]

            # Validate password
            password_hash = hash_password(password)
            if password_hash != hashed_password:
                log_login_attempt(email, success=False)
                st.error("❌ Incorrect password. Please try again.")
                return

            # Successful login
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = email
            st.session_state["user_name"] = user.get("Name", "User")  # Use user name if available
            st.session_state["user_role"] = role

            # Save session state if "Remember Me" is checked
            if remember_me:
                st.session_state["keep_signed_in"] = True
                st.session_state.email = email
                st.session_state.password = password
            else:
                st.session_state.email = ""
                st.session_state.password = ""

            st.success("✅ Login successful! Redirecting...")
            log_login_attempt(email, success=True)

            # Redirect to the main app page
            st.session_state["page"] = "database"
            st.experimental_rerun()

        except Exception as e:
            st.error(f"Error during login: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='footer'>© 2025 Hasar Organization for Climate Action</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    render_login()
