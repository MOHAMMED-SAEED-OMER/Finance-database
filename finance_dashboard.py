import streamlit as st
import gspread
import pandas as pd
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
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>Finance Dashboard</h1>", unsafe_allow_html=True)

    df = fetch_finance_data()
    if df.empty:
        st.warning("No financial data available.")
        return

    # Calculate financial metrics
    total_income = df[df["TRX type"].str.lower() == "income"]["Liquidated amount"].sum()
    total_expense = df[df["TRX type"].str.lower() == "expense"]["Liquidated amount"].sum()
    issued_funds = df[df["Liquidation status"].str.lower() == "to be liquidated"]["Requested Amount"].sum()
    available_funds = (total_income - abs(total_expense)) - issued_funds

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
                text-align: right;
                color: #1E3A8A;
            }
            .expander-header {
                font-size: 20px;
                font-weight: bold;
                color: #333;
                padding: 10px 0;
            }
            .data-style {
                font-size: 18px;
                padding: 5px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Income Section
    with st.container():
        with st.expander(f"Total Income: {total_income:,.0f} IQD", expanded=False):
            st.markdown("<div class='expander-header'>Income Breakdown</div>", unsafe_allow_html=True)
            income_breakdown = df[df["TRX type"].str.lower() == "income"].groupby("TRX category")["Liquidated amount"].sum().reset_index()
            income_breakdown["Liquidated amount"] = income_breakdown["Liquidated amount"].apply(lambda x: f"{x:,.0f} IQD")
            st.dataframe(income_breakdown.style.set_table_styles([{"selector": "th", "props": [("text-align", "left")]}]), use_container_width=True)

    # Expense Section
    with st.container():
        with st.expander(f"Total Expense: {abs(total_expense):,.0f} IQD", expanded=False):
            st.markdown("<div class='expander-header'>Expense Breakdown</div>", unsafe_allow_html=True)
            expense_breakdown = df[df["TRX type"].str.lower() == "expense"].groupby("TRX category")["Liquidated amount"].sum().reset_index()
            expense_breakdown["Liquidated amount"] = expense_breakdown["Liquidated amount"].apply(lambda x: f"{abs(x):,.0f} IQD")
            st.dataframe(expense_breakdown.style.set_table_styles([{"selector": "th", "props": [("text-align", "left")]}]), use_container_width=True)

    # Issued Funds Section (Pending Liquidation)
    with st.container():
        with st.expander(f"Issued Funds (Pending Liquidation): {issued_funds:,.0f} IQD", expanded=False):
            st.markdown("<div class='expander-header'>Issued Fund Details</div>", unsafe_allow_html=True)
            issued_funds_details = df[df["Liquidation status"].str.lower() == "to be liquidated"][["TRX ID", "Requested Amount"]]
            issued_funds_details["Requested Amount"] = issued_funds_details["Requested Amount"].apply(lambda x: f"{x:,.0f} IQD")
            st.dataframe(issued_funds_details.style.set_table_styles([{"selector": "th", "props": [("text-align", "left")]}]), use_container_width=True)

    # Available Funds Section
    with st.container():
        with st.expander(f"Available Funds Now: {available_funds:,.0f} IQD", expanded=False):
            st.markdown("<div class='expander-header'>Funds Distribution</div>", unsafe_allow_html=True)
            funds_distribution = df[df["Liquidation status"].str.lower() == "liquidated"].groupby("Payment method")["Liquidated amount"].sum().reset_index()
            funds_distribution["Liquidated amount"] = funds_distribution["Liquidated amount"].apply(lambda x: f"{x:,.0f} IQD")
            st.dataframe(funds_distribution.style.set_table_styles([{"selector": "th", "props": [("text-align", "left")]}]), use_container_width=True)

if __name__ == "__main__":
    render_finance_dashboard()
