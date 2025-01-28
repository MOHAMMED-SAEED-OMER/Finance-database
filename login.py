import requests
import firebase_admin
from firebase_admin import credentials
import streamlit as st

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["firebase"])
    firebase_admin.initialize_app(cred)

# Firebase REST API Login
def verify_user(email, password):
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={st.secrets['FIREBASE_API_KEY']}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()  # Returns user info like idToken, email, etc.
        else:
            st.error("Invalid credentials or error occurred.")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None
