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

    # Custom CSS for card design and styling
    st.markdown("""
        <style>
            .card-container {
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 20px;
            }
            .card {
                background-color: #1E3A8A;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
                text-align: center;
                transition: all 0.3s ease-in-out;
                width: 23%;
                color: #fff;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.2);
            }
            .card-title {
                font-size: 22px;
                font-weight: bold;
                color: #F3F4F6;
                margin-bottom: 10px;
            }
            .card-value {
                font-size: 28px;
                font-weight: bold;
            }
            .card-value-negative {
                font-size: 28px;
                font-weight: bold;
                color: #FF4C4C;
            }
            .stButton button {
                background-color: transparent;
                border: none;
                box-shadow: none;
                padding: 0;
                margin: 0;
                font-size: 22px;
                color: #ffffff;
                cursor: pointer;
            }
            .stButton button:hover {
                color: #F3F4F6;
                text-decoration: underline;
            }
        </style>
    """, unsafe_allow_html=True)

    # Display cards in a row
    st.markdown('<div class="card-container">', unsafe_allow_html=True)

    # Income Card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if st.button(f"Total Income"):
        with st.expander("Income Breakdown"):
            income_breakdown = df[df["TRX type"].str.lower() == "income"].groupby("TRX category")["Liquidated amount"].sum().reset_index()
            income_breakdown["Liquidated amount"] = income_breakdown["Liquidated amount"].apply(lambda x: f"{x:,.0f} IQD")
            st.dataframe(income_breakdown)
    st.markdown(f'<div class="card-title">Total Income</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card-value">{total_income:,.0f} IQD</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Expense Card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if st.button(f"Total Expenses"):
        with st.expander("Expense Breakdown"):
            expense_breakdown = df[df["TRX type"].str.lower() == "expense"].groupby("TRX category")["Liquidated amount"].sum().reset_index()
            expense_breakdown["Liquidated amount"] = expense_breakdown["Liquidated amount"].apply(lambda x: f"({abs(x):,.0f}) IQD")
            st.dataframe(expense_breakdown)
    st.markdown(f'<div class="card-title">Total Expenses</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card-value-negative">({abs(total_expense):,.0f}) IQD</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Issued Funds Card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if st.button(f"Issued Funds"):
        with st.expander("Issued Funds Details"):
            issued_funds_details = df[df["Liquidation status"].str.lower() == "to be liquidated"][["TRX ID", "Requested Amount"]]
            issued_funds_details["Requested Amount"] = issued_funds_details["Requested Amount"].apply(lambda x: f"({x:,.0f}) IQD")
            st.dataframe(issued_funds_details)
    st.markdown(f'<div class="card-title">Issued Funds</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card-value-negative">({issued_funds:,.0f}) IQD</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Available Funds Card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if st.button(f"Available Funds"):
        with st.expander("Funds Distribution"):
            funds_distribution = df[df["Liquidation status"].str.lower() == "liquidated"].groupby("Payment method")["Liquidated amount"].sum().reset_index()
            funds_distribution["Liquidated amount"] = funds_distribution["Liquidated amount"].apply(lambda x: f"{x:,.0f} IQD")
            st.dataframe(funds_distribution)
    st.markdown(f'<div class="card-title">Available Funds</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card-value">{available_funds:,.0f} IQD</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    render_finance_dashboard()
