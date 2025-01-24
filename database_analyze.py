import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from google.oauth2.service_account import Credentials

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch and process database
@st.cache_data(ttl=300)
def fetch_database():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1

        # Fetch data and convert to DataFrame
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # Convert relevant columns to appropriate data types
        df["Liquidated amount"] = pd.to_numeric(df["Liquidated amount"], errors="coerce").fillna(0)
        df["Liquidation date"] = pd.to_datetime(df["Liquidation date"], errors="coerce")

        return df
    except Exception as e:
        st.error(f"Error loading the database: {e}")
        return pd.DataFrame()

# Render the Database Analysis Page
def render_database_analysis():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Funds Analysis & Charts</h2>", unsafe_allow_html=True)
    st.write("Analyze the flow of funds over time.")

    df = fetch_database()

    if df.empty:
        st.warning("No data available for analysis.")
        return

    # Processing data for analysis
    df["Month"] = df["Liquidation date"].dt.to_period("M")  # Convert to monthly periods

    # Grouping data by month and calculating net funds (income minus expense)
    monthly_data = df.groupby(["Month", "TRX type"])["Liquidated amount"].sum().unstack(fill_value=0)
    monthly_data["Net Funds"] = monthly_data.get("income", 0) + monthly_data.get("expense", 0)  # Expenses are negative

    # Resetting index for plotting
    monthly_data = monthly_data.reset_index()
    monthly_data["Month"] = monthly_data["Month"].astype(str)  # Convert to string for plotting

    # Plot financial trend
    st.markdown("### 📈 Financial Trend Over Time")
    fig = px.line(
        monthly_data,
        x="Month",
        y="Net Funds",
        markers=True,
        title="Monthly Net Funds Flow",
        labels={"Net Funds": "Net Amount (IQD)", "Month": "Month"},
        line_shape="linear",
    )

    fig.update_traces(line=dict(color="#1E3A8A", width=2), marker=dict(size=8))
    fig.update_layout(xaxis_title="Month", yaxis_title="Net Funds (IQD)", template="plotly_white")

    st.plotly_chart(fig, use_container_width=True)

    # Breakdown of income and expenses
    st.markdown("### 📊 Monthly Income vs Expenses Breakdown")
    bar_fig = px.bar(
        monthly_data,
        x="Month",
        y=["income", "expense"],
        title="Monthly Income & Expenses",
        labels={"value": "Amount (IQD)", "Month": "Month"},
        barmode="group",
    )

    bar_fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Amount (IQD)",
        legend_title="Transaction Type",
        template="plotly_white",
    )

    st.plotly_chart(bar_fig, use_container_width=True)

if __name__ == "__main__":
    render_database_analysis()
