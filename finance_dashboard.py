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

        # Convert Liquidated amount to numeric
        df["Liquidated amount"] = pd.to_numeric(df["Liquidated amount"], errors="coerce").fillna(0)
        return df
    except Exception as e:
        st.error(f"Error loading the finance data: {e}")
        return pd.DataFrame()

# Render Finance Dashboard with improved UI
def render_finance_dashboard():
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>💰 Finance Dashboard</h1>", unsafe_allow_html=True)

    df = fetch_finance_data()
    if df.empty:
        st.warning("No financial data available.")
        return

    # Calculate totals
    total_income = df[df["TRX type"].str.lower() == "income"]["Liquidated amount"].sum()
    total_expenses = df[df["TRX type"].str.lower() == "expense"]["Liquidated amount"].sum()
    available_funds = total_income + total_expenses  # Expenses are negative values

    # Custom CSS for styling
    st.markdown("""
        <style>
            .metric-card {
                border-radius: 10px;
                padding: 20px;
                background-color: #F3F4F6;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            }
            .metric-title {
                color: #1E3A8A;
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .metric-value {
                color: #4CAF50;
                font-size: 36px;
                font-weight: bold;
            }
            .expand-section {
                background-color: #E3F2FD;
                border-radius: 10px;
                padding: 15px;
                margin-top: 15px;
                font-size: 18px;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            }
        </style>
    """, unsafe_allow_html=True)

    # Layout for the three key metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<div class='metric-card'><div class='metric-title'>Total Income</div><div class='metric-value'>"
                    f"{total_income:,.0f} IQD</div></div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='metric-card'><div class='metric-title'>Total Expenses</div><div class='metric-value' style='color: #E53935;'>"
                    f"{total_expenses:,.0f} IQD</div></div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='metric-card'><div class='metric-title'>Available Funds</div><div class='metric-value' style='color: #FB8C00;'>"
                    f"{available_funds:,.0f} IQD</div></div>", unsafe_allow_html=True)

    # Expandable sections for category breakdown
    with st.expander("🔍 View Income Breakdown"):
        income_categories = df[df["TRX type"].str.lower() == "income"].groupby("TRX category")["Liquidated amount"].sum().reset_index()
        st.markdown("<div class='expand-section'>", unsafe_allow_html=True)
        st.write(income_categories)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("🔍 View Expense Breakdown"):
        expense_categories = df[df["TRX type"].str.lower() == "expense"].groupby("TRX category")["Liquidated amount"].sum().reset_index()
        st.markdown("<div class='expand-section'>", unsafe_allow_html=True)
        st.write(expense_categories)
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    render_finance_dashboard()
