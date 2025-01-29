import streamlit as st
import requests

# Define the Firebase API key (replace this with your actual key)
FIREBASE_API_KEY = st.secrets["FIREBASE_API_KEY"]

# Firebase Authentication endpoint
FIREBASE_AUTH_ENDPOINT = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"

def verify_credentials(email, password):
    """
    Verify user credentials using Firebase Authentication.
    """
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(FIREBASE_AUTH_ENDPOINT, json=payload)

    if response.status_code == 200:
        # Authentication successful
        return response.json()  # This contains user info like idToken
    else:
        # Authentication failed
        return None

def render_login():
    """
    Render the login interface.
    """
    st.title("Login Page")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_info = verify_credentials(email, password)
        if user_info:
            st.success("Login successful!")
            # Store session state
            st.session_state["logged_in"] = True
            st.session_state["user_info"] = user_info
        else:
            st.error("Invalid credentials. Please try again.")
