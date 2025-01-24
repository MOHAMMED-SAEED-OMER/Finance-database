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

# Fetch and process database
@st.cache_data(ttl=300)
def fetch_database():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1

        # Fetch data and convert to DataFrame
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        return df
    except Exception as e:
        st.error(f"Error loading the database: {e}")
        return pd.DataFrame()

# Render the Database Page
def render_database():
    st.write("View and manage all financial records efficiently.")

    df = fetch_database()

    if df.empty:
        st.warning("No data available in the database.")
        return

    # Enhanced filter section inside the page
    st.markdown("<h3 style='color: #1E3A8A;'>🔍 Filter Records</h3>", unsafe_allow_html=True)

    filter_col, filter_value = st.columns([1, 3])

    with filter_col:
        selected_column = st.selectbox(
            "Choose Column to Filter", 
            ["None"] + list(df.columns), 
            index=0
        )

    filtered_df = df.copy()

    if selected_column != "None":
        with filter_value:
            value_input = st.text_input(f"Enter value for {selected_column}:")

        if value_input:
            filtered_df = filtered_df[
                filtered_df[selected_column].astype(str).str.contains(value_input, case=False, na=False)
            ]

    # Stylish table visualization
    st.markdown("<h3 style='color: #1E3A8A;'>📋 Request Data</h3>", unsafe_allow_html=True)

    st.dataframe(
        filtered_df.style.set_table_styles([
            {'selector': 'thead', 'props': [('background-color', '#1E3A8A'), ('color', 'white'), ('font-size', '16px')]},
            {'selector': 'tbody tr:nth-child(odd)', 'props': [('background-color', '#f0f0f0')]},
            {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#ffffff')]},
            {'selector': 'td', 'props': [('padding', '8px'), ('border', '1px solid #ddd')]},
        ]),
        height=600,
        use_container_width=True
    )

    # Custom CSS styling for enhanced UI
    st.markdown("""
        <style>
            .stDataFrame { border-radius: 10px; }
            .stSelectbox, .stTextInput {
                border: 2px solid #1E3A8A; 
                border-radius: 5px; 
                padding: 8px;
            }
            .stButton button {
                background-color: #1E3A8A;
                color: white;
                border-radius: 5px;
                padding: 8px 20px;
                border: none;
            }
            .stButton button:hover {
                background-color: #3B82F6;
            }
        </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    render_database()
