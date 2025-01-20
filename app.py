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

if not st.session_state["logged_in"]:
    from login import render_login
    render_login()
else:
    # Sidebar with user info and logout button
    st.sidebar.title("Welcome")
    st.sidebar.write(f"👤 **User:** {st.session_state['user_email']}")
    st.sidebar.write(f"🔑 **Role:** {st.session_state['user_role']}")

    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["user_email"] = None
        st.session_state["user_role"] = None
        st.experimental_rerun()

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to:",
        options=["Submit a Request", "Approver", "Payment", "Liquidation", "Database", "Add Data", "User Profiles"]
    )

    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>Finance Management System</h1>", unsafe_allow_html=True)

    if page == "Submit a Request":
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

    elif page == "Liquidation":
        if st.session_state["user_role"] in ["Admin"]:
            from liquidation_page import render_liquidation_page
            render_liquidation_page()
        else:
            st.warning("You do not have permission to access this page.")

    elif page == "Database":
        from database import render_database
        render_database()

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
