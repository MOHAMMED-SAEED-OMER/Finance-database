import streamlit as st
from layout import apply_styling, render_sidebar, display_page_title
from firebase_admin import auth

# Set page configuration
st.set_page_config(
    page_title="Finance Database",
    layout="wide",
)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.session_state["user_name"] = None  # Added user_name
    st.session_state["user_role"] = None

# Apply new styling
apply_styling()

# Logout function
def logout():
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.session_state["user_name"] = None
    st.session_state["user_role"] = None
    st.experimental_rerun()

if not st.session_state["logged_in"]:
    from login import render_login
    render_login()
else:
    # Render the sidebar and get the selected page
    page = render_sidebar()

    # Display page title dynamically
    if page:
        display_page_title(page)

    # Load pages dynamically
    if page == "Requests":
        if st.session_state["user_role"] in ["Admin", "Requester"]:
            st.markdown("<div class='page-title'>Requests</div>", unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["Submit a Request", "View My Requests"])

            with tab1:
                from submit_request import render_request_form
                render_request_form()

            with tab2:
                from view_requests import render_user_requests
                render_user_requests()
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

    elif page == "Liquidation":
        if st.session_state["user_role"] == "Admin":
            from liquidation_page import render_liquidation_page
            render_liquidation_page()
        else:
            st.warning("You do not have permission to access this page.")

    elif page == "Database":
        if st.session_state["user_role"] in ["Admin", "Approver"]:
            from database import render_database
            render_database()
        else:
            st.warning("You do not have permission to access this page.")

    elif page == "Finance Dashboard":
        if st.session_state["user_role"] in ["Admin", "Approver"]:
            from finance_dashboard import render_finance_dashboard
            render_finance_dashboard()
        else:
            st.warning("You do not have permission to access this page.")

    elif page == "Add Data":
        if st.session_state["user_role"] in ["Admin", "Requester"]:
            from add_data import render_add_data
            render_add_data()
        else:
            st.warning("You do not have permission to access this page.")

    elif page == "User Profiles":
        if st.session_state["user_role"] == "Admin":
            from user_profiles import render_user_profiles
            render_user_profiles()
        else:
            st.warning("You do not have permission to access this page.")

    elif page == "Role Management":
        if st.session_state["user_role"] == "Admin":
            from role_management import render_role_management
            render_role_management()
        else:
            st.warning("You do not have permission to access this page.")

    else:
        st.warning("Page not found. Please use the navigation menu.")
