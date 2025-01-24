import streamlit as st
import pandas as pd
import plotly.express as px
from google.oauth2.service_account import Credentials
import gspread

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch data and process
@st.cache_data(ttl=300)
def fetch_data():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # Convert date column to datetime format and extract the month
        df["Liquidation date"] = pd.to_datetime(df["Liquidation date"], errors='coerce')
        df["Month"] = df["Liquidation date"].dt.strftime('%Y-%m')

        # Convert liquidated amount to numeric and handle errors
        df["Liquidated amount"] = pd.to_numeric(df["Liquidated amount"], errors='coerce').fillna(0)

        # Filter non-zero values
        df = df[df["Liquidated amount"] != 0]

        # Group by month and transaction type
        monthly_summary = df.groupby(["Month", "TRX type"])["Liquidated amount"].sum().unstack(fill_value=0).reset_index()

        return monthly_summary
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Render database analysis page
def render_database_analysis():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Funds Flow Analysis</h2>", unsafe_allow_html=True)
    st.write("Analyze the monthly income and expenses trends.")

    df = fetch_data()

    if df.empty:
        st.warning("No data available for analysis.")
        return

    # Ensure the columns exist in the dataframe
    if 'Income' not in df.columns:
        df['Income'] = 0
    if 'Expense' not in df.columns:
        df['Expense'] = 0

    # Plotly visualization
    line_fig = px.line(
        df,
        x="Month",
        y=["Income", "Expense"],
        labels={"value": "Amount (IQD)", "Month": "Month"},
        title="Monthly Income vs Expenses",
        markers=True
    )
    st.plotly_chart(line_fig, use_container_width=True)

    # Bar chart visualization
    bar_fig = px.bar(
        df,
        x="Month",
        y=["Income", "Expense"],
        title="Income and Expenses Breakdown",
        barmode="group",
        labels={"value": "Amount (IQD)", "Month": "Month"},
    )
    st.plotly_chart(bar_fig, use_container_width=True)

if __name__ == "__main__":
    render_database_analysis()
