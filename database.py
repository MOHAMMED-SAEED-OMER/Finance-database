from st_aggrid import AgGrid, GridOptionsBuilder
import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import pandas as pd
# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"
# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)
# Fetch database
@st.cache_data(ttl=300)
def fetch_database():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"Error loading the database: {e}")
        return pd.DataFrame()
# Render the Database Page
def render_database():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Database Viewer</h2>", unsafe_allow_html=True)
    st.write("Monitor all requests and their statuses in real-time.")
    df = fetch_database()
    if df.empty:
        st.warning("No data available in the database.")
        return
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(enabled=True)
    gb.configure_side_bar()
    gb.configure_default_column(filterable=True, editable=True, resizable=True, sortable=True)
    grid_options = gb.build()
    st.markdown("### Interactive Data Table")
    AgGrid(df, gridOptions=grid_options, height=500, fit_columns_on_grid_load=True)
if __name__ == "__main__":
    render_database()
