import streamlit as st

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
    st.session_state["request_tab"] = "Submit a Request"  # Default to request submission

# Logout function
def logout():
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.session_state["user_role"] = None
    st.rerun()

if not st.session_state["logged_in"]:
    from login import render_login
    render_login()
else:
    with st.sidebar:
        st.write(f"👋 Welcome, {st.session_state['user_email']}")
        if st.button("Log Out"):
            logout()

    # Dropdown for Request Pages
    request_page = st.sidebar.selectbox(
        "📝 Requests",
        ["Submit a Request", "View My Requests"],
        index=0  # Default to 'Submit a Request'
    )

    # Handle the selected page for requests
    if request_page == "Submit a Request":
        from submit_request import render_request_form
        render_request_form()

    elif request_page == "View My Requests":
        from view_requests import render_user_requests
        render_user_requests()

    # Other navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Approver",
        "Payment",
        "Liquidation",
        "Database",
        "Add Data",
        "User Profiles"
    ])

    with tab1:
        if st.session_state["user_role"] in ["Admin", "Approver"]:
            from approver_page import render_approver_page
            render_approver_page()
        else:
            st.warning("You do not have permission to access this page.")

    with tab2:
        if st.session_state["user_role"] in ["Admin", "Approver"]:
            from payment_page import render_payment_page
            render_payment_page()
        else:
            st.warning("You do not have permission to access this page.")

    with tab3:
        if st.session_state["user_role"] in ["Admin"]:
            from liquidation_page import render_liquidation_page
            render_liquidation_page()
        else:
            st.warning("You do not have permission to access this page.")

    with tab4:
        from database import render_database
        render_database()

    with tab5:
        if st.session_state["user_role"] in ["Admin", "Requester"]:
            from add_data import render_add_data
            render_add_data()
        else:
            st.warning("You do not have permission to access this page.")

    with tab6:
        if st.session_state["user_role"] == "Admin":
            from user_profiles import render_user_profiles
            render_user_profiles()
        else:
            st.warning("You do not have permission to access this page.")
