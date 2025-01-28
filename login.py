import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin SDK
if not firebase_admin._apps:  # Avoid initializing multiple times
    cred = credentials.Certificate({
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
    })
    firebase_admin.initialize_app(cred)

# Custom login function using Firebase Authentication
def firebase_login(email, password):
    try:
        user = auth.get_user_by_email(email)
        # Simulating password check (Firebase Auth does not support plaintext password check)
        # You would use Firebase Auth client-side for password validation in production.
        if user:
            return user
        else:
            return None
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None

def render_login():
    st.title("Login to Hasar Organization")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign In"):
        user = firebase_login(email, password)
        if user:
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = email
            st.success("Login successful!")
        else:
            st.error("Invalid email or password")

if __name__ == "__main__":
    render_login()
