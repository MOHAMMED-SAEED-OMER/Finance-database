import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials
import gspread

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch and process database
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
        monthly_summary = df.groupby(["Month", "TRX type"])["Liquidated amount"].sum().reset_index()

        return monthly_summary
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Render database analysis page
def render_database_analysis():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Funds Flow Analysis</h2>", unsafe_allow_html=True)
    st.write("Analyze the monthly income and expenses trends using a waterfall chart.")

    df = fetch_data()

    if df.empty:
        st.warning("No data available for analysis.")
        return

    # Prepare data for waterfall chart (monthly net income = income - expense)
    income_df = df[df["TRX type"] == "Income"].groupby("Month")["Liquidated amount"].sum().reset_index()
    expense_df = df[df["TRX type"] == "Expense"].groupby("Month")["Liquidated amount"].sum().reset_index()

    # Merge income and expense to calculate monthly net change
    summary_df = pd.merge(income_df, expense_df, on="Month", how="outer", suffixes=("_income", "_expense")).fillna(0)
    summary_df["Net Change"] = summary_df["Liquidated amount_income"] - summary_df["Liquidated amount_expense"]

    # Create waterfall chart data
    waterfall_chart_data = pd.DataFrame({
        "Month": summary_df["Month"],
        "Net Change": summary_df["Net Change"]
    })

    # Plotly Waterfall Chart
    waterfall_fig = go.Figure(go.Waterfall(
        name="Funds Flow",
        orientation="v",
        measure=["relative"] * len(waterfall_chart_data),
        x=waterfall_chart_data["Month"],
        y=waterfall_chart_data["Net Change"],
        text=waterfall_chart_data["Net Change"].apply(lambda x: f"{x:,.0f} IQD"),
        textposition="outside",
        connector=dict(line=dict(color="rgb(63, 63, 63)")),
    ))

    waterfall_fig.update_layout(
        title="Monthly Funds Flow Waterfall Chart",
        xaxis_title="Month",
        yaxis_title="Net Income (IQD)",
        showlegend=False
    )

    st.plotly_chart(waterfall_fig, use_container_width=True)

if __name__ == "__main__":
    render_database_analysis()
