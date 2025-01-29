import streamlit as st

# Define the known correct credentials
CORRECT_EMAIL = "your_correct_email@example.com"
CORRECT_PASSWORD = "your_secure_password"

# Define a function to verify user credentials
def verify_credentials(email, password):
    return email == CORRECT_EMAIL and password == CORRECT_PASSWORD

# Render the login interface
def render_login():
    st.title("Login Page")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify_credentials(email, password):
            st.success("Login successful!")
            # Perform post-login actions, such as setting session state
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = email
        else:
            st.error("Invalid credentials. Please try again.")
