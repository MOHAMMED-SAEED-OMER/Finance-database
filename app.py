import streamlit as st

# Set page configuration
st.set_page_config(page_title="Finance Database", layout="wide")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.session_state["user_role"] = None

# Function to handle logout
def logout():
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.session_state["user_role"] = None
    st.rerun()

# Custom CSS for navigation bar
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
            margin-bottom: 20px;
        }
        .nav-title {
            font-size: 1.8rem;
            font-weight: bold;
        }
        .nav-user {
            font-size: 1.2rem;
            margin-right: 20px;
        }
        .logout-btn {
            background-color: #f44336;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 1rem;
            cursor: pointer;
        }
        .logout-btn:hover {
            background-color: #d32f2f;
        }
    </style>
""", unsafe_allow_html=True)

# Display the navigation bar with welcome message and logout button
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.markdown("<div class='nav-title'>Finance Management System</div>", unsafe_allow_html=True)

with col2:
    if st.session_state["logged_in"]:
        st.markdown(f"<div class='nav-user'>👋 Welcome, {st.session_state['user_email']}</div>", unsafe_allow_html=True)

with col3:
    if st.session_state["logged_in"] and st.button("Log Out", key="logout_btn"):
        logout()

# Login Check
if not st.session_state["logged_in"]:
    from login import render_login
    render_login()
else:
    # Horizontal Navigation
    st.markdown("---")
    selected_page = st.radio(
        "Navigation",
        ["Submit a Request", "Approver", "Payment", "Liquidation", "Database", "Add Data", "User Profiles"],
        horizontal=True
    )

    if selected_page == "Submit a Request":
        if st.session_state["user_role"] in ["Admin", "Requester"]:
            from submit_request import render_request_form
            render_request_form()
        else:
            st.warning("You do not have permission to access this page.")

    elif selected_page == "Approver":
        if st.session_state["user_role"] in ["Admin", "Approver"]:
            from approver_page import render_approver_page
            render_approver_page()
        else:
            st.warning("You do not have permission to access this page.")

    elif selected_page == "Payment":
        if st.session_state["user_role"] in ["Admin", "Approver"]:
            from payment_page import render_payment_page
            render_payment_page()
        else:
            st.warning("You do not have permission to access this page.")

    elif selected_page == "Liquidation":
        if st.session_state["user_role"] in ["Admin"]:
            from liquidation_page import render_liquidation_page
            render_liquidation_page()
        else:
            st.warning("You do not have permission to access this page.")

    elif selected_page == "Database":
        from database import render_database
        render_database()

    elif selected_page == "Add Data":
        if st.session_state["user_role"] in ["Admin", "Requester"]:
            from add_data import render_add_data
            render_add_data()
        else:
            st.warning("You do not have permission to access this page.")

    elif selected_page == "User Profiles":
        if st.session_state["user_role"] == "Admin":
            from user_profiles import render_user_profiles
            render_user_profiles()
        else:
            st.warning("You do not have permission to access this page.")
