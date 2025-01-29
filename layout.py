import streamlit as st

def apply_styling():
    st.markdown(
        """
        <style>
            /* Custom styling for the layout */
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
            .nav-btn {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                width: 100%;
                text-align: center;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
                box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
            }
            .nav-btn:hover {
                background-color: #2563EB;
                transform: scale(1.05);
                transition: 0.2s;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_sidebar():
    st.sidebar.markdown("<div class='sidebar-text'>Finance Management System</div>", unsafe_allow_html=True)

    main_tabs = {
        "Requests": ["Submit a Request", "View My Requests"],
        "Approver": [],
        "Payment": [],
        "Liquidation": [],
        "Database": [],
        "Finance Dashboard": ["Overview", "Analysis"],
        "Add Data": [],
        "User Profiles": ["User Overview", "Add New User"]
    }

    selected_tab = st.session_state.get("selected_tab", "Requests")
    selected_subtab = st.session_state.get("selected_subtab", "")

    for tab, subtabs in main_tabs.items():
        if subtabs:
            # Create a button that reveals a dropdown if there are subtabs
            if st.sidebar.button(tab, key=tab):
                st.session_state["selected_tab"] = tab
                st.session_state["selected_subtab"] = ""
                selected_tab = tab

            if selected_tab == tab:
                # Show the subtabs as buttons
                for subtab in subtabs:
                    if st.sidebar.button(f"   {subtab}", key=subtab):
                        st.session_state["selected_subtab"] = subtab
                        selected_subtab = subtab
        else:
            # If no subtabs, just a single button
            if st.sidebar.button(tab, key=tab):
                st.session_state["selected_tab"] = tab
                st.session_state["selected_subtab"] = ""
                selected_tab = tab
                selected_subtab = ""

    return selected_tab, selected_subtab

def display_page_title(page_title):
    st.markdown(f"<h1 style='text-align: center; color: #1E3A8A;'>{page_title}</h1>", unsafe_allow_html=True)
