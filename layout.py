import streamlit as st

def render_top_navbar():
    """
    Render the top navigation bar with tabs and dropdowns.
    """
    # Define the main tabs and their submenus
    tabs = {
        "Requests": ["Submit a Request", "View My Requests"],
        "Approver": [],
        "Payment": [],
        "Liquidation": [],
        "Database": [],
        "Finance Dashboard": ["Overview", "Analysis"],
        "Add Data": [],
        "User Profiles": ["User Overview", "Add New User"]
    }

    # Keep track of the current main tab and active page
    st.session_state["current_tab"] = st.session_state.get("current_tab", list(tabs.keys())[0])
    st.session_state["current_page"] = st.session_state.get("current_page", None)

    # Create horizontal tab layout
    cols = st.columns(len(tabs))
    for i, (tab, subpages) in enumerate(tabs.items()):
        with cols[i]:
            if subpages:  # If there are subpages, create a dropdown
                with st.expander(tab):
                    for subpage in subpages:
                        if st.button(subpage, key=subpage):
                            st.session_state["current_tab"] = tab
                            st.session_state["current_page"] = subpage
            else:  # If no subpages, it's a direct tab
                if st.button(tab, key=tab):
                    st.session_state["current_tab"] = tab
                    st.session_state["current_page"] = tab

def display_page_content():
    """
    Display the content of the currently selected page.
    """
    current_page = st.session_state.get("current_page", "Requests")
    st.write(f"## {current_page} Content")
    # Add custom content for each page if needed
    # For example:
    if current_page == "Submit a Request":
        st.write("Here you can submit a new request.")
    elif current_page == "View My Requests":
        st.write("Here you can view your submitted requests.")
    elif current_page == "Overview":
        st.write("This is the overview section of the Finance Dashboard.")
    elif current_page == "Analysis":
        st.write("This is the analysis section of the Finance Dashboard.")
    # ... Add more content for other pages ...

# Main app logic
st.set_page_config(page_title="Finance Management System", layout="wide")
render_top_navbar()
display_page_content()
