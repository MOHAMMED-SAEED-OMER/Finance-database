import streamlit as st
from firebase_admin import credentials, initialize_app
import requests

# Initialize Firebase Admin SDK
if not len(initialize_app._apps):
    cred = credentials.Certificate(st.secrets["firebase"])
    initialize_app(cred)

# Firebase REST API login function
def verify_user(email, password):
    """
    Verifies the user credentials using Firebase Authentication REST API.
    """
    try:
        # Use the Firebase Web API key from secrets
        api_key = st.secrets.get("FIREBASE_API_KEY", None)
        if not api_key:
            st.error("Missing FIREBASE_API_KEY in secrets.")
            return None
        
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return response.json()  # Return authenticated user data
        else:
            error_msg = response.json().get("error", {}).get("message", "Unknown error")
            st.error(f"Authentication failed: {error_msg}")
            return None
    except Exception as e:
        st.error(f"Error verifying user: {e}")
        return None

# Function to render login page
def render_login():
    st.title("Login Page")

    email = st.text_input("Email", placeholder="Enter your email")
    password = st.text_input("Password", placeholder="Enter your password", type="password")

    if st.button("Login"):
        if email and password:
            user = verify_user(email, password)
            if user:
                st.success("Login successful!")
                st.write(user)  # Display user details for now
            else:
                st.error("Login failed.")
        else:
            st.warning("Please provide both email and password.")
