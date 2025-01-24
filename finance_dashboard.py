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

    # Custom CSS for enhanced UI
    st.markdown("""
        <style>
            .finance-box {
                background-color: #F3F4F6;
                border-radius: 10px;
                padding: 30px;
                margin-bottom: 10px;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
                font-size: 26px;
                font-weight: bold;
                text-align: center;
                color: #1E3A8A;
                transition: 0.3s ease-in-out;
            }
            .finance-box:hover {
                transform: scale(1.05);
            }
            .finance-header {
                font-size: 22px;
                font-weight: bold;
                color: #1E3A8A;
                margin-bottom: 20px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Create four columns layout
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        if st.button(f"Total Income: {total_income:,.0f} IQD", key="income"):
            with st.expander("Income Breakdown"):
                income_breakdown = df[df["TRX type"].str.lower() == "income"].groupby("TRX category")["Liquidated amount"].sum().reset_index()
                income_breakdown["Liquidated amount"] = income_breakdown["Liquidated amount"].apply(lambda x: f"{x:,.0f} IQD")
                st.dataframe(income_breakdown)

    with col2:
        if st.button(f"Total Expenses: ({abs(total_expense):,.0f}) IQD", key="expense"):
            with st.expander("Expense Breakdown"):
                expense_breakdown = df[df["TRX type"].str.lower() == "expense"].groupby("TRX category")["Liquidated amount"].sum().reset_index()
                expense_breakdown["Liquidated amount"] = expense_breakdown["Liquidated amount"].apply(lambda x: f"({abs(x):,.0f}) IQD")
                st.dataframe(expense_breakdown)

    with col3:
        if st.button(f"Issued Funds (Pending): ({issued_funds:,.0f}) IQD", key="issued"):
            with st.expander("Issued Funds Details"):
                issued_funds_details = df[df["Liquidation status"].str.lower() == "to be liquidated"][["TRX ID", "Requested Amount"]]
                issued_funds_details["Requested Amount"] = issued_funds_details["Requested Amount"].apply(lambda x: f"({x:,.0f}) IQD")
                st.dataframe(issued_funds_details)

    with col4:
        if st.button(f"Available Funds Now: {available_funds:,.0f} IQD", key="available"):
            with st.expander("Funds Distribution"):
                funds_distribution = df[df["Liquidation status"].str.lower() == "liquidated"].groupby("Payment method")["Liquidated amount"].sum().reset_index()
                funds_distribution["Liquidated amount"] = funds_distribution["Liquidated amount"].apply(lambda x: f"{x:,.0f} IQD")
                st.dataframe(funds_distribution)

if __name__ == "__main__":
    render_finance_dashboard()
