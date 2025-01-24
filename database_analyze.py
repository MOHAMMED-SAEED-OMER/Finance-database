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

        # Convert liquidation date column to datetime and extract month-year
        df["Liquidation date"] = pd.to_datetime(df["Liquidation date"], errors='coerce')
        df["Month"] = df["Liquidation date"].dt.strftime('%Y-%m')

        # Convert liquidated amount to numeric and handle errors
        df["Liquidated amount"] = pd.to_numeric(df["Liquidated amount"], errors='coerce').fillna(0)

        # Filter relevant rows (exclude rows with 0 liquidated amount)
        df = df[df["Liquidated amount"] != 0]

        return df
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

    # Calculate monthly total income and expenses
    income_df = df[df["TRX type"].str.lower() == "income"].groupby("Month")["Liquidated amount"].sum().reset_index()
    expense_df = df[df["TRX type"].str.lower() == "expense"].groupby("Month")["Liquidated amount"].sum().reset_index()

    # Merge income and expenses to calculate net changes
    summary_df = pd.merge(income_df, expense_df, on="Month", how="outer", suffixes=("_income", "_expense")).fillna(0)
    summary_df["Net Change"] = summary_df["Liquidated amount_income"] - summary_df["Liquidated amount_expense"]

    # Sort the months in chronological order
    summary_df = summary_df.sort_values(by="Month")

    # Waterfall chart values
    months = summary_df["Month"].tolist()
    changes = summary_df["Net Change"].tolist()

    # Create waterfall chart with cumulative changes
    waterfall_fig = go.Figure(go.Waterfall(
        name="Funds Flow",
        orientation="v",
        measure=["relative"] * len(changes) + ["total"],
        x=months + ["Total"],
        y=changes + [sum(changes)],
        text=[f"{val:,.0f} IQD" for val in changes] + [f"{sum(changes):,.0f} IQD"],
        textposition="outside",
        decreasing=dict(marker=dict(color="red")),
        increasing=dict(marker=dict(color="green")),
        totals=dict(marker=dict(color="blue")),
        connector=dict(line=dict(color="rgb(63, 63, 63)")),
    ))

    waterfall_fig.update_layout(
        title="Monthly Funds Flow",
        xaxis_title="Month",
        yaxis_title="Net Income (IQD)",
        showlegend=False
    )

    st.plotly_chart(waterfall_fig, use_container_width=True)

if __name__ == "__main__":
    render_database_analysis()
