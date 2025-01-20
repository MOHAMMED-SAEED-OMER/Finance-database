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
    st.experimental_rerun()

if not st.session_state["logged_in"]:
    from login import render_login
    render_login()
else:
    # Custom styling for navigation bar with welcome message and logout button
    st.markdown("""
        <style>
            .nav-container {
                display: flex;
                justify-content: space-between;
                align-items: center;
                background-color: #1E3A8A;
                padding: 15px 30px;
                border-radius: 10px;
                color: white;
            }
            .nav-title {
                font-size: 1.5rem;
                font-weight: bold;
            }
            .nav-user {
                font-size: 1.1rem;
                margin-right: 20px;
            }
            .logout-btn {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1rem;
            }
            .logout-btn:hover {
                background-color: #d32f2f;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="nav-container">
            <div class="nav-title">Finance Management System</div>
            <div class="nav-user">👋 Welcome, {st.session_state["user_email"]}</div>
            <form action="" method="POST">
                <button class="logout-btn" type="submit" name="logout">Log Out</button>
            </form>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Log out functionality (checks if the logout button is clicked)
    if st.query_params.get("logout"):
        logout()

    # Horizontal navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Submit a Request", 
        "Approver", 
        "Payment", 
        "Liquidation", 
        "Database", 
        "Add Data", 
        "User Profiles"
    ])

    with tab1:
        if st.session_state["user_role"] in ["Admin", "Requester"]:
            from submit_request import render_request_form
            render_request_form()
        else:
            st.warning("You do not have permission to access this page.")

    with tab2:
        if st.session_state["user_role"] in ["Admin", "Approver"]:
            from approver_page import render_approver_page
            render_approver_page()
        else:
            st.warning("You do not have permission to access this page.")

    with tab3:
        if st.session_state["user_role"] in ["Admin", "Approver"]:
            from payment_page import render_payment_page
            render_payment_page()
        else:
            st.warning("You do not have permission to access this page.")

    with tab4:
        if st.session_state["user_role"] in ["Admin"]:
            from liquidation_page import render_liquidation_page
            render_liquidation_page()
        else:
            st.warning("You do not have permission to access this page.")

    with tab5:
        from database import render_database
        render_database()

    with tab6:
        if st.session_state["user_role"] in ["Admin", "Requester"]:
            from add_data import render_add_data
            render_add_data()
        else:
            st.warning("You do not have permission to access this page.")

    with tab7:
        if st.session_state["user_role"] == "Admin":
            from user_profiles import render_user_profiles
            render_user_profiles()
        else:
            st.warning("You do not have permission to access this page.")
