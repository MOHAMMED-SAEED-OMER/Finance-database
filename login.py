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
    st.title("🔐 Login")
    st.write("Please enter your credentials to log in.")

    # Initialize cookies for "Remember Me" functionality
    if "user_email" not in st.session_state:
        st.session_state.user_email = st.experimental_get_query_params().get("email", [""])[0]
    if "user_password" not in st.session_state:
        st.session_state.user_password = ""

    # Login form
    email = st.text_input("Email:", value=st.session_state.user_email)
    password = st.text_input("Password:", value=st.session_state.user_password, type="password")
    remember_me = st.checkbox("Remember Me")

    if st.button("Login"):
        if not email or not password:
            st.warning("Please fill out all fields.")
            return

        try:
            # Fetch users from Google Sheets
            users = fetch_user_data()
            user = users[users["Email"] == email]

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

            # Save email and password for "Remember Me"
            if remember_me:
                st.experimental_set_query_params(email=email)

            st.success("Login successful!")

            # Redirect to the main app
            st.experimental_set_query_params(page="database")

        except Exception as e:
            st.error(f"Error during login: {e}")
