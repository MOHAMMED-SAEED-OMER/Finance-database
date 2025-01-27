import streamlit as st

def apply_styling():
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                background-color: #1E3A8A;
                padding: 30px 20px;
                border-radius: 10px;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
            }
            .sidebar-text {
                font-size: 22px;
                font-weight: bold;
                color: white;
                text-align: center;
                margin-bottom: 20px;
            }
            .sidebar-subtext {
                font-size: 18px;
                color: #BBDEFB;
                text-align: center;
                margin-bottom: 30px;
            }
            .sidebar-btn {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                width: 100%;
                text-align: center;
                font-size: 18px;
                font-weight: bold;
                box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
            }
            .sidebar-btn:hover {
                background-color: #2563EB;
                transform: scale(1.05);
                transition: 0.2s;
            }
            .sidebar-logout {
                background-color: #D32F2F;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                width: 100%;
                font-size: 18px;
                margin-top: 20px;
                font-weight: bold;
                box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
            }
            .sidebar-logout:hover {
                background-color: #B71C1C;
                transform: scale(1.05);
                transition: 0.2s;
            }
            .page-title {
                font-size: 2.5rem;
                font-weight: bold;
                color: #1E3A8A;
                text-align: center;
                margin-bottom: 20px;
                text-transform: uppercase;
            }
            .select-style select {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 18px;
                font-weight: bold;
                width: 100%;
                box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
            }
            .select-style select:hover {
                background-color: #2563EB;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_sidebar():
    with st.sidebar:
        st.markdown("<div class='sidebar-text'>Finance Management System</div>", unsafe_allow_html=True)
        
        # Show welcome message with user name
        user_name = st.session_state.get('user_name', 'Guest')
        st.markdown(f"<div class='sidebar-subtext'>Welcome, {user_name}</div>", unsafe_allow_html=True)

        # Role-based navigation options with a stylish selectbox
        role = st.session_state.get("user_role", "Guest")
        pages = []

        if role == "Admin":
            pages = [
                "Requests", "Approver", "Payment", "Liquidation",
                "Database", "Finance Dashboard", "Add Data", "User Profiles"
            ]
        elif role == "Approver":
            pages = ["Approver", "Database"]
        elif role == "Requester":
            pages = ["Requests"]

        selected_page = None
        if pages:
            st.markdown("<div class='select-style'>", unsafe_allow_html=True)
            selected_page = st.selectbox("Navigate to:", pages)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("You do not have access to any pages.")

        # Logout button
        if st.button("Log Out", key="logout_btn", help="Click to log out", use_container_width=True, args=("logout",)):
            logout()

        return selected_page

def display_page_title(page):
    st.markdown(f"<div class='page-title'>{page}</div>", unsafe_allow_html=True)

# Logout function
def logout():
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.session_state["user_name"] = None
    st.session_state["user_role"] = None
    st.rerun()
