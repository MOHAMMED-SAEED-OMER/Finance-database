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

# Fetch database from Google Sheet
@st.cache_data(ttl=300)
def fetch_finance_data():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # Convert Liquidated amount to numeric
        df["Liquidated amount"] = pd.to_numeric(df["Liquidated amount"], errors="coerce").fillna(0)
        return df
    except Exception as e:
        st.error(f"Error loading the finance data: {e}")
        return pd.DataFrame()

# Render Finance Dashboard
def render_finance_dashboard():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Finance Dashboard</h2>", unsafe_allow_html=True)

    df = fetch_finance_data()
    if df.empty:
        st.warning("No financial data available.")
        return

    # Calculate totals
    total_income = df[df["TRX type"].str.lower() == "income"]["Liquidated amount"].sum()
    total_expenses = df[df["TRX type"].str.lower() == "expense"]["Liquidated amount"].sum()
    available_funds = total_income + total_expenses  # Expenses are negative values

    # Display Key Metrics
    st.markdown("### Financial Overview")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(f"💰 Total Income: {total_income:,.0f} IQD"):
            st.markdown("### Income Categories")
            income_categories = df[df["TRX type"].str.lower() == "income"].groupby("TRX category")["Liquidated amount"].sum().reset_index()
            st.table(income_categories)

    with col2:
        if st.button(f"💸 Total Expenses: {total_expenses:,.0f} IQD"):
            st.markdown("### Expense Categories")
            expense_categories = df[df["TRX type"].str.lower() == "expense"].groupby("TRX category")["Liquidated amount"].sum().reset_index()
            st.table(expense_categories)

    with col3:
        st.metric(label="🏦 Available Funds", value=f"{available_funds:,.0f} IQD")

if __name__ == "__main__":
    render_finance_dashboard()
