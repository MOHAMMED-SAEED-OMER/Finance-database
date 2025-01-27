import streamlit as st
from layout import apply_styling, render_sidebar, display_page_title

# Set page configuration
st.set_page_config(
    page_title="Finance Database",
    layout="wide",
)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.session_state["user_role"] = None

# Apply styling to the app
apply_styling()

if not st.session_state["logged_in"]:
    from login import render_login
    render_login()
else:
    # Render the sidebar and get the selected page
    page = render_sidebar()

    # Display title based on the selected page
    if page:
        display_page_title(page)

    # Load pages based on selected option
    if page == "Requests":
        from submit_request import render_request_form
        render_request_form()

    elif page == "Approver":
        from approver_page import render_approver_page
        render_approver_page()

    elif page == "Payment":
        from payment_page import render_payment_page
        render_payment_page()

    elif page == "Liquidation":
        from liquidation_page import render_liquidation_page
        render_liquidation_page()

    elif page == "Database":
        from database import render_database
        render_database()

    elif page == "Finance Dashboard":
        from finance_dashboard import render_finance_dashboard
        render_finance_dashboard()

    elif page == "Add Data":
        from add_data import render_add_data
        render_add_data()

    elif page == "User Profiles":
        from user_profiles import render_user_profiles
        render_user_profiles()
