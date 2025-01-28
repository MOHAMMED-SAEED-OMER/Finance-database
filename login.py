import requests
import streamlit as st
import firebase_admin
from firebase_admin import credentials

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["FIREBASE_KEY"])
    firebase_admin.initialize_app(cred)

# Firebase REST API Key (Add to secrets.toml)
FIREBASE_API_KEY = st.secrets["FIREBASE_API_KEY"]

# Firebase REST API Login Function
def verify_user(email, password):
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            user_data = response.json()
            return {
                "email": user_data["email"],
                "idToken": user_data["idToken"],
                "localId": user_data["localId"]
            }
        else:
            error_message = response.json().get("error", {}).get("message", "Unknown error occurred.")
            st.error(f"Error: {error_message}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Custom CSS for Styling
def set_custom_css():
    st.markdown(
        """
        <style>
            body {
                background: linear-gradient(135deg, #1E3A8A, #3B82F6);
                font-family: 'Arial', sans-serif;
            }
            .login-container {
                max-width: 400px;
                margin: auto;
                padding: 2rem;
                background: white;
                border-radius: 15px;
                box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.2);
                text-align: center;
            }
            .login-title {
                font-size: 1.8rem;
                font-weight: bold;
                color: #1E3A8A;
                margin-bottom: 1rem;
            }
            .form-control {
                margin-bottom: 1rem;
                padding: 10px;
                font-size: 1rem;
                border-radius: 8px;
                border: 1px solid #ccc;
                width: 100%;
            }
            .btn-login {
                background-color: #1E3A8A;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: bold;
                width: 100%;
                border: none;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            .btn-login:hover {
                background-color: #3B82F6;
            }
            .footer {
                margin-top: 1rem;
                font-size: 0.9rem;
                color: #555;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

# Render Login Page
def render_login():
    set_custom_css()

    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<div class='login-title'>Welcome to Hasar Organization</div>", unsafe_allow_html=True)

    email = st.text_input("Email", placeholder="Enter your email", key="email_input")
    password = st.text_input("Password", placeholder="Enter your password", type="password", key="password_input")
    login_button = st.button("Sign In", key="login_button", help="Click to log in")

    if login_button:
        if not email or not password:
            st.warning("Please enter both email and password.")
            return

        # Authenticate with Firebase
        user_data = verify_user(email, password)
        if user_data:
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = user_data["email"]
            st.session_state["idToken"] = user_data["idToken"]
            st.session_state["user_id"] = user_data["localId"]
            st.success("✅ Login successful!")
            st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='footer'>© 2025 Hasar Organization</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    render_login()
