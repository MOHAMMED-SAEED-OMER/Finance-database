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
    st.session_state["user_name"] = None  # Added user_name
    st.session_state["user_role"] = None

# Apply new styling
apply_styling()

if not st.session_state["logged_in"]:
    from login import render_login  # Ensure `render_login` is defined properly
    render_login()  # Call the function to render the login page
else:
    # Render the sidebar and get the selected page
    page = render_sidebar()

    # Display page title dynamically
    if page:
        display_page_title(page)

    # Load pages dynamically
    if page == "Requests":
        st.markdown("<div class='page-title'>Requests</div>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Submit a Request", "View My Requests"])

        with tab1:
            from submit_request import render_request_form
            render_request_form()

        with tab2:
            from view_requests import render_user_requests
            render_user_requests()

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
