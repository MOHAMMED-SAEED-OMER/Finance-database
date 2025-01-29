import streamlit as st

def apply_styling():
    # Custom styling for the app
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                background-color: #1E3A8A;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
            }
            .sidebar-text {
                font-size: 24px;
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
            .nav-btn {
                background-color: #3B82F6;
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
                background-color: #2563EB;
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
                color: #1E3A8A;
                text-align: center;
                margin-bottom: 20px;
                text-transform: uppercase;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_sidebar():
    # Create sidebar content
    with st.sidebar:
        st.markdown("<div class='sidebar-text'>Finance Management System</div>", unsafe_allow_html=True)

        # User details display
        user_name = st.session_state.get("user_name", "Guest")
        st.markdown(f"<div class='sidebar-subtext'>Welcome, {user_name}</div>", unsafe_allow_html=True)

        # Navigation buttons
        pages = ["Requests", "Approver", "Payment", "Liquidation", "Database", "Finance Dashboard", "Add Data", "User Profiles"]
        selected_page = st.session_state.get("selected_page", pages[0])

        for page in pages:
            if st.button(page, key=page, help=f"Go to {page}", use_container_width=True):
                st.session_state["selected_page"] = page
                st.experimental_rerun()

        if st.button("Log Out", key="logout_btn", help="Log out of the application", use_container_width=True):
            logout()

def display_page_title(page):
    # Display the page title at the top
    st.markdown(f"<div class='page-title'>{page}</div>", unsafe_allow_html=True)

def logout():
    # Clear session state on logout
    st.session_state.clear()
    st.experimental_rerun()
