import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from google.oauth2.service_account import Credentials
from database_analyze import render_database_analysis  # For the second tab

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
    # Tabs: Overview (first tab), Analysis (second tab)
    tab1, tab2 = st.tabs(["Overview", "Analysis"])

    # Tab 1: Overview
    with tab1:
        df = fetch_finance_data()
        if df.empty:
            st.warning("No financial data available.")
            return

        # Financial metrics
        total_income = df[df["TRX type"].str.lower() == "income"]["Liquidated amount"].sum()
        total_expense = df[df["TRX type"].str.lower() == "expense"]["Liquidated amount"].sum()
        available_funds = df["Liquidated amount"].sum()

        # Calculate Income vs. Expense trend for the last 6 months
        df["Liquidation date"] = pd.to_datetime(df["Liquidation date"], errors='coerce')
        df["Liquidation Month"] = df["Liquidation date"].dt.to_period("M").astype(str)

        income_data = df[df["TRX type"].str.lower() == "income"].groupby("Liquidation Month")["Liquidated amount"].sum().reset_index()
        expense_data = df[df["TRX type"].str.lower() == "expense"].groupby("Liquidation Month")["Liquidated amount"].sum().reset_index()

        # Charts
        income_chart = px.bar(
            income_data.tail(6),  # Last 6 months
            x="Liquidation Month",
            y="Liquidated amount",
            title="Income Trend (Last 6 Months)",
            height=300,
            color_discrete_sequence=["#3B82F6"]
        )

        expense_chart = px.bar(
            expense_data.tail(6),  # Last 6 months
            x="Liquidation Month",
            y="Liquidated amount",
            title="Expense Trend (Last 6 Months)",
            height=300,
            color_discrete_sequence=["#EF4444"]
        )

        # Layout for metrics and charts
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Income", f"{total_income:,.0f} IQD")
            st.plotly_chart(income_chart, use_container_width=True, key="income_chart")

        with col2:
            st.metric("Total Expense", f"({abs(total_expense):,.0f}) IQD")
            st.plotly_chart(expense_chart, use_container_width=True, key="expense_chart")

    # Tab 2: Analysis (Waterfall chart from database_analyze.py)
    with tab2:
        render_database_analysis()  # Call the analysis function from database_analyze.py

if __name__ == "__main__":
    render_finance_dashboard()
