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

# Custom CSS for styling
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
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #ffffff;
            text-align: center;
            margin-bottom: 20px;
        }
        .login-container {
            max-width: 450px;
            margin: auto;
            padding: 2rem;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.2);
            text-align: center;
        }
        .login-title {
            font-size: 1.8rem;
            font-weight: bold;
            color: #1E3A8A;
            margin-bottom: 10px;
        }
        .instructions {
            font-size: 1rem;
            color: #374151;
            margin-bottom: 20px;
            text-align: left;
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
        .footer {
            font-size: 0.9rem;
            color: #E5E7EB;
            text-align: center;
            margin-top: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

def render_login():
    st.markdown("<div class='header'>Hasar Organization</div>", unsafe_allow_html=True)
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<div class='login-title'>Sign in to Your Account</div>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class='instructions'>
            <ul>
                <li>Use your registered email and password to log in.</li>
                <li>Click 'Keep me signed in' to stay logged in for your session.</li>
                <li>Contact the admin if you encounter login issues.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Check if the user is already logged in
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.success("You are already logged in.")
        st.query_params.update({"page": "database"})
        return

    # Login form
    email = st.text_input("Email:", placeholder="Enter your email")
    password = st.text_input("Password:", placeholder="Enter your password", type="password")
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
                st.session_state["keep_signed_in"] = True
            else:
                st.session_state["keep_signed_in"] = False

            st.success("Login successful! Redirecting...")

            # Redirect to database page after login
            st.query_params.update({"page": "database"})

        except Exception as e:
            st.error(f"Error during login: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='footer'>© 2025 Hasar Organization for Climate Action</div>", unsafe_allow_html=True)
