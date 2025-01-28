import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from google.oauth2.service_account import Credentials
from database_analyze import render_database_analysis  # Import Trends Analysis (Tab 2)

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
    # Tabs with new placements
    tab1, tab2 = st.tabs(["Overview", "Analysis"])

    with tab1:
        df = fetch_finance_data()
        if df.empty:
            st.warning("No financial data available.")
            return

        # Calculate financial metrics
        total_income = df[df["TRX type"].str.lower() == "income"]["Liquidated amount"].sum()
        total_expense = df[df["TRX type"].str.lower() == "expense"]["Liquidated amount"].sum()
        issued_funds = df[df["Liquidation status"].str.lower() == "to be liquidated"]["Requested Amount"].sum()
        available_funds = df["Liquidated amount"].sum() + issued_funds

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

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(income_chart, use_container_width=True, key="income_chart")

        with col2:
            st.plotly_chart(expense_chart, use_container_width=True, key="expense_chart")

    with tab2:
        render_database_analysis()  # Call the separate database_analyze module to render the second tab

if __name__ == "__main__":
    render_finance_dashboard()
