import streamlit as st

# Apply new styling
def apply_styling():
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                background-color: #1E293B; /* Darker shade for better visibility */
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
            }
            .sidebar-text {
                font-size: 26px;
                font-weight: bold;
                color: #E2E8F0; /* Light grayish text */
                text-align: center;
                margin-bottom: 20px;
            }
            .sidebar-subtext {
                font-size: 18px;
                color: #94A3B8; /* Subtle text color */
                text-align: center;
                margin-bottom: 30px;
            }
            .nav-btn {
                background-color: #475569; /* New dark theme button color */
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                width: 100%;
                text-align: center;
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
                box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
            }
            .nav-btn:hover {
                background-color: #64748B;
                transform: scale(1.05);
                transition: 0.2s;
            }
            .logout-btn {
                background-color: #D32F2F;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                width: 100%;
                font-size: 18px;
                font-weight: bold;
                margin-top: 20px;
                box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
            }
            .logout-btn:hover {
                background-color: #B71C1C;
                transform: scale(1.05);
                transition: 0.2s;
            }
            .page-title {
                font-size: 2.5rem;
                font-weight: bold;
                color: #334155; /* Dark blue-gray for better visibility */
                text-align: center;
                margin-bottom: 20px;
                text-transform: uppercase;
            }
            .profile-section {
                background-color: #475569;
                color: #E2E8F0;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
                box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
            }
            .profile-header {
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .profile-details {
                font-size: 16px;
                margin-bottom: 5px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_sidebar():
    with st.sidebar:
        st.markdown("<div class='sidebar-text'>Finance Management System</div>", unsafe_allow_html=True)

        # Fetch user details
        user_name = st.session_state.get('user_name', 'Guest')
        user_email = st.session_state.get('user_email', 'Not Provided')
        user_role = st.session_state.get('user_role', 'Unknown')

        # User profile section
        st.markdown(
            f"""
            <div class='profile-section'>
                <div class='profile-header'>User Profile</div>
                <div class='profile-details'><strong>Name:</strong> {user_name}</div>
                <div class='profile-details'><strong>Email:</strong> {user_email}</div>
                <div class='profile-details'><strong>Role:</strong> {user_role}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Role-based navigation
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

        selected_page = st.session_state.get("selected_page", pages[0] if pages else None)

        for page in pages:
            if st.button(page, key=page, help=f"Navigate to {page}", use_container_width=True):
                st.session_state["selected_page"] = page
                st.rerun()

        if st.button("Log Out", key="logout_btn", help="Click to log out", use_container_width=True):
            logout()

        return st.session_state.get("selected_page", pages[0] if pages else None)

def display_page_title(page):
    if page != st.session_state.get("last_page"):
        st.markdown(f"<div class='page-title'>{page}</div>", unsafe_allow_html=True)
        st.session_state["last_page"] = page

# Logout function
def logout():
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.session_state["user_name"] = None
    st.session_state["user_role"] = None
    st.rerun()
