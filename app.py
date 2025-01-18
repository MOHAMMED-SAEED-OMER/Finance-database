import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Finance Database",
    layout="wide",
)

# Logo or header at the top
st.markdown(
    """
    <style>
        .header-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px;
            background-color: #f5f5f5;
            border-bottom: 1px solid #ddd;
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        }
    </style>
    <div class="header-container">
        <div class="logo">Finance Database</div>
        <!-- Add a logo or any other navigation items here -->
    </div>
    """,
    unsafe_allow_html=True,
)

# Tab-based navigation
tabs = st.tabs(["Database", "Add New Data"])

with tabs[0]:
    from database import render_database
    render_database()

with tabs[1]:
    from add_data import render_add_data
    render_add_data()
