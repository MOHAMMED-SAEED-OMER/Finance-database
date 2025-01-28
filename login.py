import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["FIREBASE_CREDENTIALS"])
    firebase_admin.initialize_app(cred)

# Custom CSS for styling improvements
def set_custom_css():
    st.markdown(
        """
        <style>
            body {
                background-color: #f9f9f9;
                font-family: Arial, sans-serif;
            }
            .login-container {
                max-width: 400px;
                margin: auto;
                padding: 2rem;
                background: white;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.2);
                text-align: center;
            }
            .login-title {
                font-size: 1.8rem;
                font-weight: bold;
                color: #1E3A8A;
                margin-bottom: 20px;
            }
            .login-btn {
                background-color: #1E3A8A;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
            }
            .login-btn:hover {
                background-color: #3B82F6;
            }
            .error-message {
                color: red;
                font-size: 0.9rem;
                margin-top: 10px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_login():
    set_custom_css()

    # Login form
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<div class='login-title'>Sign in to Hasar Organization</div>", unsafe_allow_html=True)

    email = st.text_input("Email", placeholder="Enter your email")
    password = st.text_input("Password", placeholder="Enter your password", type="password")

    if st.button("Sign In", use_container_width=True):
        if not email or not password:
            st.warning("Please fill in both email and password.")
        else:
            try:
                # Verify user with Firebase
                user = auth.get_user_by_email(email)

                # Placeholder for password verification (Firebase Admin SDK doesn't handle passwords directly)
                if password == "user-password-placeholder":  # Replace this logic with secure password validation
                    st.success(f"Welcome back, {user.display_name}!")

                    # Update session state
                    st.session_state["logged_in"] = True
                    st.session_state["user_email"] = user.email
                    st.session_state["user_name"] = user.display_name
                    st.session_state["user_role"] = "Admin"  # Adjust as per Firebase role logic
                else:
                    st.error("Invalid email or password.")
            except firebase_admin.auth.AuthError:
                st.error("Authentication failed. Please check your credentials.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    render_login()
