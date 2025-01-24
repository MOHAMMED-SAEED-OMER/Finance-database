import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from google.oauth2.service_account import Credentials

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch finance data from Google Sheets
@st.cache_data(ttl=300)
def fetch_finance_data():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # Convert necessary columns to numeric
        df["Liquidated amount"] = pd.to_numeric(df["Liquidated amount"], errors="coerce").fillna(0)
        df["Requested Amount"] = pd.to_numeric(df["Requested Amount"], errors="coerce").fillna(0)

        return df
    except Exception as e:
        st.error(f"Error loading the finance data: {e}")
        return pd.DataFrame()

# Render Finance Dashboard
def render_finance_dashboard():
    df = fetch_finance_data()
    if df.empty:
        st.warning("No financial data available.")
        return

    # Calculate financial metrics
    total_income = df[df["TRX type"].str.lower() == "income"]["Liquidated amount"].sum()
    total_expense = df[df["TRX type"].str.lower() == "expense"]["Liquidated amount"].sum()
    issued_funds = df[df["Liquidation status"].str.lower() == "to be liquidated"]["Requested Amount"].sum()
    available_funds = df["Liquidated amount"].sum() - issued_funds

    # Prepare data for graphs with reduced complexity
    df["Liquidation date"] = pd.to_datetime(df["Liquidation date"], errors='coerce')
    df["Payment date"] = pd.to_datetime(df["Payment date"], errors='coerce')

    # Aggregate data by month to reduce clutter
    df["Liquidation Month"] = df["Liquidation date"].dt.to_period("M").astype(str)
    df["Payment Day"] = df["Payment date"].dt.strftime("%Y-%m-%d")

    # Income trend (monthly aggregation, reduced data points)
    income_data = df[df["TRX type"].str.lower() == "income"].groupby("Liquidation Month")["Liquidated amount"].sum().reset_index()
    income_chart = px.bar(
        income_data.tail(6),  # Show only the last 6 months
        x="Liquidation Month",
        y="Liquidated amount",
        title="Income Trend",
        height=250,
        color_discrete_sequence=["#1E3A8A"],
    )

    # Expense trend (monthly aggregation, reduced data points)
    expense_data = df[df["TRX type"].str.lower() == "expense"].groupby("Liquidation Month")["Liquidated amount"].sum().reset_index()
    expense_chart = px.bar(
        expense_data.tail(6),  # Show only the last 6 months
        x="Liquidation Month",
        y="Liquidated amount",
        title="Expense Trend",
        height=250,
        color_discrete_sequence=["#D32F2F"],
    )

    # Issued funds trend (recent transactions only)
    issued_funds_data = df[df["Liquidation status"].str.lower() == "to be liquidated"].groupby("Payment Day")["Requested Amount"].sum().reset_index()
    issued_chart = px.bar(
        issued_funds_data.tail(7),  # Show only the last 7 days
        x="Payment Day",
        y="Requested Amount",
        title="Issued Funds Trend",
        height=250,
        color_discrete_sequence=["#F59E0B"],
    )

    # Available funds breakdown by payment method
    funds_distribution = df[df["Liquidation status"].str.lower() == "liquidated"].groupby("Payment method")["Liquidated amount"].sum().reset_index()
    available_funds_chart = px.pie(
        funds_distribution,
        names="Payment method",
        values="Liquidated amount",
        title="Available Funds Distribution",
        hole=0.4,  # Make it a donut chart
    )

    # Custom CSS for enhanced UI
    st.markdown("""
        <style>
            .finance-header {
                font-size: 22px;
                font-weight: bold;
                color: #1E3A8A;
                margin-bottom: 10px;
                border-bottom: 2px solid #1E3A8A;
                padding-bottom: 5px;
            }
            .finance-box {
                background-color: #F3F4F6;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 10px;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
                font-size: 24px;
                font-weight: bold;
                text-align: center;
                color: #1E3A8A;
            }
            .metric-value {
                font-size: 30px;
                font-weight: bold;
                color: #1E3A8A;
            }
        </style>
    """, unsafe_allow_html=True)

    # Layout with columns for the finance overview
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='finance-header'>Total Income</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='finance-box'>{total_income:,.0f} IQD</div>", unsafe_allow_html=True)
        st.plotly_chart(income_chart, use_container_width=True)

    with col2:
        st.markdown("<div class='finance-header'>Total Expense</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='finance-box'>({abs(total_expense):,.0f}) IQD</div>", unsafe_allow_html=True)
        st.plotly_chart(expense_chart, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
    st.markdown("<div class='finance-header'>Issued Funds</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='finance-box'>({issued_funds:,.0f} IQD)</div>", unsafe_allow_html=True)
    st.plotly_chart(issued_chart, use_container_width=True)


    with col4:
        st.markdown("<div class='finance-header'>Available Funds</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='finance-box'>{available_funds:,.0f} IQD</div>", unsafe_allow_html=True)
        st.plotly_chart(available_funds_chart, use_container_width=True)

if __name__ == "__main__":
    render_finance_dashboard()
