import streamlit as st

def apply_styling():
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

def render_sidebar():
    with st.sidebar:
        st.markdown("<div class='sidebar-text'>Finance Management System</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sidebar-text'>Welcome, {st.session_state.get('user_email', 'Guest')}</div>", unsafe_allow_html=True)

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

        selected_page = st.radio("Navigation", pages, index=0 if pages else None)
        return selected_page

def display_page_title(page):
    st.markdown(f"<div class='page-title'>{page}</div>", unsafe_allow_html=True)

# Logout function
def logout():
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.session_state["user_role"] = None
    st.rerun()
