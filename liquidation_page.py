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
def process_liquidation(sheet, trx_id, liquidated_amount, invoices_link):
    try:
        baghdad_tz = pytz.timezone("Asia/Baghdad")
        liquidation_date = datetime.now(baghdad_tz).strftime("%Y-%m-%d %H:%M:%S")

        # Get all data to find the row index
        data = sheet.get_all_values()
        headers = data[0]  
        trx_id_col = headers.index("TRX ID") + 1  

        for i, row in enumerate(data):
            if row[trx_id_col - 1] == trx_id:
                row_index = i + 1  
                requested_amount = int(row[headers.index("Requested Amount")])

                # Calculate returned amount
                returned_amount = liquidated_amount - requested_amount

                # Update cells in the sheet
                sheet.update_cell(row_index, headers.index("Liquidation status") + 1, "Liquidated")
                sheet.update_cell(row_index, headers.index("Liquidated amount") + 1, liquidated_amount)
                sheet.update_cell(row_index, headers.index("Liquidation date") + 1, liquidation_date)
                sheet.update_cell(row_index, headers.index("Liquidated invoices") + 1, invoices_link)
                sheet.update_cell(row_index, headers.index("Returned amount") + 1, returned_amount)

                return True
        return False
    except Exception as e:
        st.error(f"Error processing liquidation: {e}")
        return False

# Render Liquidation Page
def render_liquidation_page():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Liquidation Processing</h2>", unsafe_allow_html=True)
    st.write("Review and process pending liquidations.")

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

        # Create a list to track processed requests
        processed_requests = []

        # Accordion style expander for pending liquidations
        for index, request in pending_liquidations.iterrows():
            if st.session_state.get("processed_liquidation") == request["TRX ID"]:
                continue  # Skip already processed items

            with st.expander(f"Request ID: {request['TRX ID']} - {request['Project name']}"):
                st.write(f"**Budget Line:** {request['Budget line']}")
                st.write(f"**Purpose:** {request['Purpose']}")
                st.write(f"**Requested Amount:** {int(request['Requested Amount']):,} IQD")
                st.write(f"**Payment Date:** {request['Payment date']}")
                st.write(f"**Payment Method:** {request['Payment method']}")

                # Liquidation input fields
                liquidated_amount = st.text_input(
                    f"Enter Liquidated Amount (IQD) for {request['TRX ID']}",
                    placeholder="e.g., 1,000,000"
                )

                invoices_link = st.text_input(
                    f"Enter Invoice Link for {request['TRX ID']}",
                    placeholder="Paste invoice link here"
                )

                # Action button
                col1, col2 = st.columns(2)
                if col1.button("Confirm Liquidation", key=f"confirm_{request['TRX ID']}"):
                    if not liquidated_amount.isdigit():
                        st.warning("Please enter a valid amount.")
                    elif not invoices_link.strip():
                        st.warning("Please provide an invoice link.")
                    else:
                        # Ensure liquidated amount is stored as negative
                        liquidated_amount = -abs(int(liquidated_amount.replace(",", "")))

                        success = process_liquidation(sheet, request["TRX ID"], liquidated_amount, invoices_link)
                        if success:
                            st.session_state["processed_liquidation"] = request["TRX ID"]
                            processed_requests.append(request["TRX ID"])
                            st.success(f"Liquidation completed for TRX ID: {request['TRX ID']}")
                            st.rerun()

        # Remove processed requests from pending list
        if processed_requests:
            pending_liquidations = pending_liquidations[~pending_liquidations["TRX ID"].isin(processed_requests)]

        # Display message for recent liquidation
        if st.session_state["processed_liquidation"]:
            st.info(f"Recently processed liquidation for TRX ID: {st.session_state['processed_liquidation']}")

    except Exception as e:
        st.error(f"Error loading liquidation page: {e}")

if __name__ == "__main__":
    render_liquidation_page()
