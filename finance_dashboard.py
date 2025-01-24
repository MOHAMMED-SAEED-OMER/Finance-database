import streamlit as st
import pandas as pd
import plotly.express as px
from google.oauth2.service_account import Credentials
import gspread

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch and process financial data
@st.cache_data(ttl=300)
def fetch_financial_data():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()

        df = pd.DataFrame(data)

        # Convert columns to numeric where applicable
        df["Liquidated amount"] = pd.to_numeric(df["Liquidated amount"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"Error loading financial data: {e}")
        return pd.DataFrame()

# Render the Finance Dashboard
def render_finance_dashboard():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Finance Dashboard</h2>", unsafe_allow_html=True)
    st.write("Gain insights into your financial data through interactive charts and statistics.")

    df = fetch_financial_data()

    if df.empty:
        st.warning("No financial data available.")
        return

    # Total Income & Expenses Calculation
    total_income = df[df["TRX type"].str.lower() == "income"]["Liquidated amount"].sum()
    total_expenses = df[df["TRX type"].str.lower() == "expense"]["Liquidated amount"].sum()
    net_funds = total_income + total_expenses  # Expenses are negative

    # Calculate fund allocation
    bank_funds = df[df["Payment method"].str.lower() == "bank"]["Liquidated amount"].sum()
    cash_funds = df[df["Payment method"].str.lower() == "cash"]["Liquidated amount"].sum()

    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"{total_income:,} IQD")
    col2.metric("Total Expenses", f"{total_expenses:,} IQD")
    col3.metric("Available Funds", f"{net_funds:,} IQD")

    col1, col2 = st.columns(2)
    col1.metric("Cash in Safe", f"{cash_funds:,} IQD")
    col2.metric("Bank Balance", f"{bank_funds:,} IQD")

    # Income Source Breakdown
    st.markdown("### Income Sources Breakdown")
    income_by_source = df[df["TRX type"].str.lower() == "income"].groupby("Project name")["Liquidated amount"].sum().reset_index()
    fig_income = px.pie(income_by_source, values="Liquidated amount", names="Project name", title="Income by Project")
    st.plotly_chart(fig_income, use_container_width=True)

    # Expense Breakdown by Category
    st.markdown("### Expense Breakdown")
    expense_by_category = df[df["TRX type"].str.lower() == "expense"].groupby("Budget line")["Liquidated amount"].sum().reset_index()
    fig_expense = px.bar(expense_by_category, x="Budget line", y="Liquidated amount", title="Expenses by Budget Line", color="Liquidated amount")
    st.plotly_chart(fig_expense, use_container_width=True)

    # Income vs. Expenses Trend Over Time
    st.markdown("### Income vs. Expense Trends")
    df["Liquidation date"] = pd.to_datetime(df["Liquidation date"], errors="coerce")
    df["Month"] = df["Liquidation date"].dt.strftime("%Y-%m")

    trend_df = df.groupby(["Month", "TRX type"])["Liquidated amount"].sum().reset_index()
    fig_trend = px.line(trend_df, x="Month", y="Liquidated amount", color="TRX type", title="Monthly Income vs Expenses Trend")
    st.plotly_chart(fig_trend, use_container_width=True)

    # Add date range filter
    st.markdown("### Filter Data by Date Range")
    date_col1, date_col2 = st.columns(2)
    start_date = date_col1.date_input("Start Date", df["Liquidation date"].min())
    end_date = date_col2.date_input("End Date", df["Liquidation date"].max())

    # Apply date filter
    if start_date and end_date:
        filtered_df = df[(df["Liquidation date"] >= pd.Timestamp(start_date)) & (df["Liquidation date"] <= pd.Timestamp(end_date))]
        st.write("Filtered Data", filtered_df)

if __name__ == "__main__":
    render_finance_dashboard()
