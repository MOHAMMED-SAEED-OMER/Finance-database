import gspread
import streamlit as st
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

        df = pd.DataFrame(data)
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

# Social Media Links
social_links = {
    "🌐 Website": "https://www.hasar.org",
    "📘 Facebook": "https://www.facebook.com/HasarOrganization",
    "📷 Instagram": "https://www.instagram.com/HasarOrg",
    "🐦 Twitter": "https://twitter.com/HasarOrg",
    "🔗 LinkedIn": "https://www.linkedin.com/company/hasarorg"
}

# List of image URLs for slideshow (replace with actual URLs or local paths)
image_urls = [
    "https://www.hasar.org/images/project1.jpg",
    "https://www.hasar.org/images/project2.jpg",
    "https://www.hasar.org/images/project3.jpg"
]

def render_login():
    st.markdown(
        """
        <style>
            .header { 
                font-size: 2.5rem; 
                font-weight: bold; 
                color: #1E3A8A; 
                text-align: center; 
                margin-bottom: 20px; 
            }
            .instructions { 
                font-size: 1rem; 
                color: #374151; 
                margin-bottom: 20px; 
                text-align: left; 
            }
            .footer { 
                font-size: 0.9rem; 
                color: #374151; 
                text-align: center; 
                margin-top: 20px; 
            }
            .social-links a { 
                text-decoration: none; 
                color: #1E3A8A; 
                font-size: 1.2rem; 
                margin-right: 20px; 
            }
        </style>
        """, 
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1.5, 1])  # Left and right sections

    # Left Side - Image Slideshow and Social Media Links
    with col1:
        st.markdown("<div class='header'>Welcome to Hasar Organization</div>", unsafe_allow_html=True)

        # Image slideshow (cycling through images every 5 seconds)
        placeholder = st.empty()
        for img_url in image_urls:
            placeholder.image(img_url, use_container_width=True)
            time.sleep(5)

        # Social Media Links
        st.markdown("<div class='social-links'><strong>Follow us:</strong></div>", unsafe_allow_html=True)
        for name, url in social_links.items():
            st.markdown(f"[{name}]({url})")

    # Right Side - Login Form
    with col2:
        st.markdown("<div class='header'>Login</div>", unsafe_allow_html=True)

        # Login form fields
        email = st.text_input("Email:", placeholder="Enter your email")
        password = st.text_input("Password:", placeholder="Enter your password", type="password")
        remember_me = st.checkbox("Keep me signed in")

        if st.button("Sign In"):
            if not email or not password:
                st.warning("Please fill out all fields.")
                return

            try:
                users = fetch_user_data()
                user = users[users["Email"].str.lower() == email.lower()]

                if user.empty:
                    st.error("User not found.")
                    return

                user = user.iloc[0]
                hashed_password = user["Password"]
                role = user["Role"]

                if hash_password(password) != hashed_password:
                    st.error("Incorrect password.")
                    return

                # Successful login
                st.session_state["logged_in"] = True
                st.session_state["user_email"] = email
                st.session_state["user_role"] = role

                # Keep session state
                if remember_me:
                    st.session_state["keep_signed_in"] = True
                else:
                    st.session_state["keep_signed_in"] = False

                st.success("Login successful! Redirecting...")
                st.query_params.update({"page": "database"})

            except Exception as e:
                st.error(f"Error during login: {e}")

        st.markdown("<div class='footer'>© 2025 Hasar Organization</div>", unsafe_allow_html=True)
