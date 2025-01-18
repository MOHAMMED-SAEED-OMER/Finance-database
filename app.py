import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Finance Database",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar Navigation with Buttons
st.sidebar.title("Navigation")
st.sidebar.markdown("Click a button below to navigate:")

# Define buttons for page navigation
if st.sidebar.button("View Database"):
    st.session_state["page"] = "Database"
elif st.sidebar.button("Add New Data"):
    st.session_state["page"] = "Add New Data"

# Initialize the session state if not set
if "page" not in st.session_state:
    st.session_state["page"] = "Database"

# Dynamically load pages
if st.session_state["page"] == "Database":
    from database import render_database
    render_database()
elif st.session_state["page"] == "Add New Data":
    from add_data import render_add_data
    render_add_data()
