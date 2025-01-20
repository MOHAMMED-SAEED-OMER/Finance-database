import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import hashlib
import time

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

# Function to display a random image from Lorem Picsum
def display_random_image():
    width = 400
    height = 500
    image_url = f"https://picsum.photos/{width}/{height}?random={time.time()}"  # Unique image every refresh
    st.image(image_url, use_container_width=True)

# Render the Login Page
def render_login():
    st.set_page_config(page_title="Hasar Organization", layout="wide")

    # Split the screen into two columns
    col1, col2 = st.columns([1, 1])

    # Left column for dynamic images and social media links
    with col1:
        st.markdown("<h2 style='text-align: center;'>Welcome to Hasar Organization</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: gray;'>Inspiring Change Through Climate Action</h4>", unsafe_allow_html=True)
        
        # Display dynamic images
        display_random_image()

        # Add social media links
        st.markdown("### Connect with Us")
        st.markdown("[🌐 Website](https://www.hasar.org)")
        st.markdown("[📘 Facebook](https://www.facebook.com/HasarOrganization)")
        st.markdown("[📷 Instagram](https://www.instagram.com/HasarOrg)")
        st.markdown("[🐦 Twitter](https://twitter.com/HasarOrg)")
        st.markdown("[💼 LinkedIn](https://www.linkedin.com/company/hasarorg)")

    # Right column for login form
    with col2:
        st.markdown("<h2 style='text-align: center;'>🔐 Secure Login</h2>", unsafe_allow_html=True)
        st.write("Please enter your credentials to access the finance management system.")

        # Store login inputs in session state
        if "saved_email" not in st.session_state:
            st.session_state.saved_email = ""
        if "saved_password" not in st.session_state:
            st.session_state.saved_password = ""

        # Login form inputs
        email = st.text_input("Email:", value=st.session_state.saved_email, placeholder="Enter your email")
        password = st.text_input("Password:", value=st.session_state.saved_password, type="password", placeholder="Enter your password")
        keep_signed_in = st.checkbox("Keep me signed in")

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

                # Save email and password in session state if "Keep me signed in" is checked
                if keep_signed_in:
                    st.session_state.saved_email = email
                    st.session_state.saved_password = password
                else:
                    st.session_state.saved_email = ""
                    st.session_state.saved_password = ""

                st.success("Login successful! Redirecting...")

                # Redirect to the database page after successful login
                st.session_state["page"] = "Database"

            except Exception as e:
                st.error(f"Error during login: {e}")

if __name__ == "__main__":
    render_login()
