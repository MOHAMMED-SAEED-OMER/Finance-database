import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Finance Database",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar Navigation
st.sidebar.title("Navigation")
st.sidebar.markdown("Use the menu below to navigate:")
page = st.sidebar.selectbox(
    "Select a page:",
    ["Database", "Add New Data"]  # Add more pages as needed
)

# Dynamically load pages
if page == "Database":
    from database import render_database
    render_database()
elif page == "Add New Data":
    from add_data import render_add_data
    render_add_data()
