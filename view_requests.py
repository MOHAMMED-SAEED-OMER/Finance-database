import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch user's request data
@st.cache_data(ttl=60)
def fetch_user_requests(user_email):
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()

        df = pd.DataFrame(data)

        # Filter data for the logged-in user
        user_requests = df[df["Requester name"].str.lower() == user_email.lower()]
        return user_requests
    except Exception as e:
        st.error(f"Error fetching user requests: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Render User Requests Page
def render_user_requests():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>📊 My Requests Dashboard</h2>", unsafe_allow_html=True)
    
    user_email = st.session_state.get("user_email", "Unknown")
    requests_df = fetch_user_requests(user_email)

    if requests_df.empty:
        st.warning("No requests found for your account.")
        return

    # Summary cards
    total_requests = len(requests_df)
    pending_count = (requests_df["Approval Status"].str.lower() == "pending").sum()
    approved_count = (requests_df["Approval Status"].str.lower() == "approved").sum()
    declined_count = (requests_df["Approval Status"].str.lower() == "declined").sum()
    liquidated_count = (requests_df["Liquidation status"].str.lower() == "liquidated").sum()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Requests", total_requests)
    with col2:
        st.metric("Pending", pending_count)
    with col3:
        st.metric("Approved", approved_count)
    with col4:
        st.metric("Declined", declined_count)
    with col5:
        st.metric("Liquidated", liquidated_count)

    st.markdown("---")

    # Visualization Section
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # Pie Chart for request statuses
        status_counts = requests_df["Approval Status"].value_counts()
        fig_pie = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Request Status Distribution",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        # Bar Chart for monthly trends
        requests_df["Request submission date"] = pd.to_datetime(requests_df["Request submission date"])
        requests_df["Month"] = requests_df["Request submission date"].dt.strftime('%Y-%m')
        monthly_counts = requests_df["Month"].value_counts().sort_index()
        fig_bar = px.bar(
            x=monthly_counts.index,
            y=monthly_counts.values,
            labels={'x': 'Month', 'y': 'Number of Requests'},
            title="Monthly Requests Trend",
            color_discrete_sequence=['#1E3A8A']
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # Filters for searching requests
    st.subheader("🔍 Search & Filter Requests")
    project_filter = st.selectbox("Filter by Project", options=["All"] + list(requests_df["Project name"].unique()))
    status_filter = st.selectbox("Filter by Status", options=["All", "Pending", "Approved", "Declined", "Liquidated"])

    filtered_df = requests_df.copy()
    if project_filter != "All":
        filtered_df = filtered_df[filtered_df["Project name"] == project_filter]
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["Approval Status"] == status_filter]

    # Expandable section to display request table
    with st.expander("📋 View Full Request List"):
        st.write("Below is the list of your submitted requests:")
        st.dataframe(filtered_df)

    # Summary of selected requests
    total_selected_requests = len(filtered_df)
    total_amount = filtered_df["Requested Amount"].sum()

    st.success(f"📊 You have {total_selected_requests} selected requests totaling {total_amount:,.0f} IQD.")

if __name__ == "__main__":
    render_past_requests()
