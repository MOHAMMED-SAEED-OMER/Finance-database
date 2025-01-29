import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import requests

def initialize_firebase():
    # Check if the Firebase Admin SDK has already been initialized
    try:
        # `firebase_admin._apps` no longer exists, so use `firebase_admin.get_app()` to check
        firebase_admin.get_app()
    except ValueError:
        # If no app exists, initialize the Firebase Admin SDK
        cred = credentials.Certificate(st.secrets["firebase"])
        firebase_admin.initialize_app(cred)

# Initialize Firebase
initialize_firebase()

def authenticate_user(email, password):
    """
    Authenticates the user using Firebase Authentication.
    """
    # Replace with actual authentication logic, such as Firebase REST API calls or `auth.sign_in_with_email_and_password` methods
    try:
        # Example placeholder logic
        if email == "user@example.com" and password == "password":
            return {"email": email, "idToken": "dummy_token"}
        else:
            st.error("Invalid credentials")
            return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def render_login():
    """
    Renders the login form and handles user authentication.
    """
    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_info = authenticate_user(email, password)
        if user_info:
            # Store user session data if authentication is successful
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = user_info["email"]
            st.session_state["id_token"] = user_info["idToken"]
            st.success("Login successful!")
        else:
            st.error("Login failed. Please try again.")

if __name__ == "__main__":
    render_login()
