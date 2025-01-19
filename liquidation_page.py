import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import pytz

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch all pending liquidations
@st.cache_data(ttl=60)
def fetch_pending_liquidations():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
        data = sheet.get_all_records()

        # Convert data to DataFrame and filter for "To be liquidated" status
        df = pd.DataFrame(data)
        pending_liquidations = df[df["Liquidation status"].str.lower() == "to be liquidated"]
        return pending_liquidations
    except Exception as e:
        st.error(f"Error fetching pending liquidations: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Update liquidation status, amount, invoices, and returned amount
def process_liquidation(sheet, row_index, liquidated_amount, invoices_link, requested_amount):
    try:
        baghdad_tz = pytz.timezone("Asia/Baghdad")
        liquidation_date = datetime.now(baghdad_tz).strftime("%Y-%m-%d %H:%M:%S")

        # Calculate returned amount (Liquidated amount - Requested amount)
        returned_amount = liquidated_amount - requested_amount

        # Update Liquidation Status
        sheet.update_cell(row_index, 17, "Liquidated")  # Column 17: Liquidation Status
        # Update Liquidated Amount
        sheet.update_cell(row_index, 18, liquidated_amount)  # Column 18: Liquidated Amount
        # Update Liquidation Date
        sheet.update_cell(row_index, 19, liquidation_date)  # Column 19: Liquidation Date
        # Update Liquidated Invoices
        sheet.update_cell(row_index, 20, invoices_link)  # Column 20: Liquidated Invoices
        # Update Returned Amount
        sheet.update_cell(row_index, 21, returned_amount)  # Column 21: Returned Amount

        return True
    except Exception as e:
        st.error(f"Error processing liquidation: {e}")
        return False

# Render Liquidation Page
def render_liquidation_page():
    st.title("🏦 Liquidation Processing")
    st.write("View and process liquidations.")

    # Session state to track processed liquidations
    if "processed_liquidation" not in st.session_state:
        st.session_state["processed_liquidation"] = None

    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1

        # Fetch pending liquidations
        pending_liquidations = fetch_pending_liquidations()

        if pending_liquidations.empty:
            st.info("No pending liquidations to process.")
            return

        # Display pending liquidations
        st.write("### Pending Liquidations")
        st.dataframe(pending_liquidations)

        # Select a request to process liquidation
        trx_id = st.selectbox(
            "Select a Request by TRX ID:",
            options=pending_liquidations["TRX ID"].tolist(),
        )

        # Find requested amount for the selected TRX ID
        selected_row = pending_liquidations[pending_liquidations["TRX ID"] == trx_id]
        requested_amount = selected_row["Requested Amount"].values[0]

        # User inputs
        liquidated_amount = st.number_input(
            "Enter Liquidated Amount (negative value):", value=0.0, step=0.01
        )
        invoices_link = st.text_input("Enter Invoice Link:")

        if st.button("Process Liquidation"):
            # Find the row index of the selected TRX ID
            row_index = pending_liquidations[pending_liquidations["TRX ID"] == trx_id].index[0] + 2  # +2 for header and 1-based indexing

            success = process_liquidation(sheet, row_index, liquidated_amount, invoices_link, requested_amount)
            if success:
                st.session_state["processed_liquidation"] = trx_id
                st.success(f"Liquidation completed for request {trx_id}.")
                st.rerun()  # Refresh page correctly

        # Display a message if a liquidation was recently processed
        if st.session_state["processed_liquidation"]:
            st.info(f"Recently processed liquidation for TRX ID: {st.session_state['processed_liquidation']}")

    except Exception as e:
        st.error(f"Error loading liquidation page: {e}")
