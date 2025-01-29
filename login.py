import firebase_admin
from firebase_admin import credentials
import streamlit as st
import requests

# Debugging step: check if secrets are being read correctly
st.write("Firebase API Key:", st.secrets.get("FIREBASE_API_KEY"))
st.write("All Secrets:", st.secrets)

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"],
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
    })
    firebase_admin.initialize_app(cred)

# Firebase Authentication with REST API
def verify_user(email, password):
    """
    Verifies the user credentials with Firebase Authentication via REST API.
    """
    try:
        api_key = st.secrets["FIREBASE_API_KEY"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Authentication error: {e}")
        return None
    except KeyError:
        st.error("Missing Firebase API key in secrets.toml.")
        return None

# Custom Styling for the Login Page
def set_custom_styling():
    st.markdown(
        """
        <style>
            body {
                background: linear-gradient(135deg, #1E3A8A, #3B82F6);
            }
            .login-container {
                max-width: 400px;
                margin: auto;
                padding: 30px;
                background: #ffffff;
                border-radius: 10px;
                box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
            }
            .login-title {
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                color: #1E3A8A;
                margin-bottom: 20px;
            }
            .btn-login {
                background-color: #1E3A8A;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                padding: 10px;
                width: 100%;
                transition: 0.3s;
            }
            .btn-login:hover {
                background-color: #3B82F6;
                transform: scale(1.05);
            }
        </style>
        """,
        unsafe_allow_html=True
    )

# Render the Login Page
def render_login():
    set_custom_styling()

    # Login form container
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<div class='login-title'>Login to Hasar Organization</div>", unsafe_allow_html=True)

    # Input fields
    email = st.text_input("Email", placeholder="Enter your email")
    password = st.text_input("Password", placeholder="Enter your password", type="password")

    # Login button
    if st.button("Sign In", key="btn-login", help="Log in to your account"):
        if not email or not password:
            st.warning("Please provide both email and password.")
        else:
            user_info = verify_user(email, password)
            if user_info:
                # Save user session data
                st.session_state["logged_in"] = True
                st.session_state["user_email"] = user_info["email"]
                st.session_state["id_token"] = user_info["idToken"]

                st.success(f"Welcome, {user_info['email']}!")
                st.experimental_rerun()  # Reload the app to reflect logged-in state

    st.markdown("</div>", unsafe_allow_html=True)

# Run the Login Page
if __name__ == "__main__":
    render_login()
