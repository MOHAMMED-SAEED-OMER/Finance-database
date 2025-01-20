import streamlit as st
from login import render_login

# Set page configuration at the very top
st.set_page_config(page_title="Hasar Organization", layout="wide")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.session_state["user_role"] = None

if not st.session_state["logged_in"]:
    render_login()
else:
    # Sidebar Navigation with Pages
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to:",
        options=["Database", "Add New Data", "Submit a Request", "Approver", "Payment", "User Profiles"]
    )

    if page == "Database":
        from database import render_database
        render_database()

    elif page == "Add New Data":
        if st.session_state["user_role"] in ["Admin", "Requester"]:
            from add_data import render_add_data
            render_add_data()
        else:
            st.warning("You do not have permission to access this page.")

    elif page == "Submit a Request":
        if st.session_state["user_role"] in ["Admin", "Requester"]:
            from submit_request import render_request_form
            render_request_form()
        else:
            st.warning("You do not have permission to access this page.")

    elif page == "Approver":
        if st.session_state["user_role"] in ["Admin", "Approver"]:
            from approver_page import render_approver_page
            render_approver_page()
        else:
            st.warning("You do not have permission to access this page.")

    elif page == "Payment":
        if st.session_state["user_role"] in ["Admin", "Approver"]:
            from payment_page import render_payment_page
            render_payment_page()
        else:
            st.warning("You do not have permission to access this page.")

    elif page == "User Profiles":
        if st.session_state["user_role"] == "Admin":
            from user_profiles import render_user_profiles
            render_user_profiles()
        else:
            st.warning("You do not have permission to access this page.")
