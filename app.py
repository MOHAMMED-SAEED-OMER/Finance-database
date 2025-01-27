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
    # Custom sidebar design
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                background-color: #1E3A8A;
                padding: 30px 15px;
                border-radius: 10px;
            }
            .sidebar-text {
                font-size: 20px;
                font-weight: bold;
                color: white;
                margin-bottom: 20px;
                text-align: center;
            }
            .sidebar-btn {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                width: 100%;
                text-align: center;
                font-size: 16px;
            }
            .sidebar-btn:hover {
                background-color: #2563EB;
            }
            .sidebar-logout {
                background-color: #D32F2F;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                width: 100%;
                font-size: 16px;
                margin-top: 20px;
            }
            .sidebar-logout:hover {
                background-color: #B71C1C;
            }
            .page-title {
                font-size: 2.5rem;
                font-weight: bold;
                color: #1E3A8A;
                text-align: center;
                margin-bottom: 20px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.markdown("<div class='sidebar-text'>Finance Management System</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sidebar-text'>Welcome, {st.session_state['user_email']}</div>", unsafe_allow_html=True)
        
        if st.button("Log Out", key="logout_btn", help="Click to log out", use_container_width=True):
            logout()

        st.markdown("<hr style='border: 1px solid white;'>", unsafe_allow_html=True)

        # Role-based navigation
        if st.session_state["user_role"] == "Admin":
            pages = [
                "Requests", "Approver", "Payment", "Liquidation",
                "Database", "Finance Dashboard", "Add Data", "User Profiles"
            ]
        elif st.session_state["user_role"] == "Approver":
            pages = ["Approver", "Database"]
        elif st.session_state["user_role"] == "Requester":
            pages = ["Requests"]
        else:
            pages = []

        page = st.radio("Navigation", pages, index=0 if pages else None)

    # Display title above tabs based on selected page
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
        st.markdown("<div class='page-title'>Approver</div>", unsafe_allow_html=True)
        from approver_page import render_approver_page
        render_approver_page()

    elif page == "Payment":
        st.markdown("<div class='page-title'>Payment</div>", unsafe_allow_html=True)
        from payment_page import render_payment_page
        render_payment_page()

    elif page == "Liquidation":
        st.markdown("<div class='page-title'>Liquidation</div>", unsafe_allow_html=True)
        from liquidation_page import render_liquidation_page
        render_liquidation_page()

    elif page == "Database":
        st.markdown("<div class='page-title'>Database</div>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["View Database", "Analysis & Charts"])

        with tab1:
            from database import render_database
            render_database()

        with tab2:
            from database_analyze import render_database_analysis
            render_database_analysis()

    elif page == "Finance Dashboard":
        st.markdown("<div class='page-title'>Finance Dashboard</div>", unsafe_allow_html=True)
        from finance_dashboard import render_finance_dashboard
        render_finance_dashboard()

    elif page == "Add Data":
        st.markdown("<div class='page-title'>Add Data</div>", unsafe_allow_html=True)
        from add_data import render_add_data
        render_add_data()

    elif page == "User Profiles":
        st.markdown("<div class='page-title'>User Management</div>", unsafe_allow_html=True)
        from user_profiles import render_user_profiles
        render_user_profiles()
