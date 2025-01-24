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
 

    df = fetch_finance_data()
    if df.empty:
        st.warning("No financial data available.")
        return

    # Calculate financial metrics
    total_income = df[df["TRX type"].str.lower() == "income"]["Liquidated amount"].sum()
    total_expense = df[df["TRX type"].str.lower() == "expense"]["Liquidated amount"].sum()
    issued_funds = df[df["Liquidation status"].str.lower() == "to be liquidated"]["Requested Amount"].sum()
    available_funds = (total_income - abs(total_expense)) - issued_funds

    # Custom CSS for pivot table style layout
    st.markdown("""
        <style>
            .pivot-container {
                background-color: #F3F4F6;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 10px;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            }
            .pivot-title {
                font-size: 22px;
                font-weight: bold;
                color: #1E3A8A;
                cursor: pointer;
            }
            .pivot-content {
                margin-top: 15px;
                font-size: 18px;
                padding-left: 15px;
                background-color: #E3F2FD;
                border-radius: 10px;
                padding: 10px;
            }
            .pivot-metric {
                font-size: 24px;
                font-weight: bold;
                color: #4CAF50;
                text-align: right;
            }
        </style>
    """, unsafe_allow_html=True)

    # Income Section
    with st.container():
        with st.expander(f"💰 Total Income: {total_income:,.0f} IQD", expanded=False):
            income_breakdown = df[df["TRX type"].str.lower() == "income"].groupby("TRX category")["Liquidated amount"].sum().reset_index()
            st.dataframe(income_breakdown.style.format({"Liquidated amount": "{:,.0f} IQD"}), use_container_width=True)

    # Expense Section
    with st.container():
        with st.expander(f"💸 Total Expense: {abs(total_expense):,.0f} IQD", expanded=False):
            expense_breakdown = df[df["TRX type"].str.lower() == "expense"].groupby("TRX category")["Liquidated amount"].sum().reset_index()
            st.dataframe(expense_breakdown.style.format({"Liquidated amount": "{:,.0f} IQD"}), use_container_width=True)

    # Issued Funds Section (Pending Liquidation)
    with st.container():
        with st.expander(f"🏦 Issued Funds (Pending Liquidation): {issued_funds:,.0f} IQD", expanded=False):
            issued_funds_details = df[df["Liquidation status"].str.lower() == "to be liquidated"][["TRX ID", "Requested Amount"]]
            st.dataframe(issued_funds_details.style.format({"Requested Amount": "{:,.0f} IQD"}), use_container_width=True)

    # Available Funds Section
    with st.container():
        with st.expander(f"💵 Available Funds Now: {available_funds:,.0f} IQD", expanded=False):
            funds_distribution = df[df["Liquidation status"].str.lower() == "liquidated"].groupby("Payment method")["Liquidated amount"].sum().reset_index()
            st.dataframe(funds_distribution.style.format({"Liquidated amount": "{:,.0f} IQD"}), use_container_width=True)

if __name__ == "__main__":
    render_finance_dashboard()
