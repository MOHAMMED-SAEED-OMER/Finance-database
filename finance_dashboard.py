import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch dropdown options from Helper tab
@st.cache_data(ttl=60)
def fetch_dropdown_options_vertical():
    try:
        client = load_credentials()
        helper_sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("Helper")
        helper_data = helper_sheet.get_all_records()
        
        dropdown_options = {}
        for key in helper_data[0].keys():
            dropdown_options[key] = [row[key] for row in helper_data if row[key]]
        return dropdown_options
    except Exception as e:
        st.error(f"Error fetching dropdown options: {e}")
        return {}

# Generate the next TRX ID
def generate_trx_id(sheet):
    try:
        all_rows = sheet.get_all_records()
        if all_rows:
            last_trx_id = all_rows[-1].get("TRX ID", "TRX-0000")
            next_id_number = int(last_trx_id.split("-")[1]) + 1
            return f"TRX-{next_id_number:04d}"
        else:
            return "TRX-0001"
    except Exception as e:
        st.error(f"Error generating TRX ID: {e}")
        return "TRX-0001"

# Render the Add New Data Page
def render_add_data():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Add New Data</h2>", unsafe_allow_html=True)
    st.write("Use this page to add new data to the database dynamically.")

    try:
        # Authenticate and open the Google Sheet
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1

        # Fetch dropdown options
        dropdown_options = fetch_dropdown_options_vertical()

        # User input fields
        trx_type = st.selectbox("Select TRX Type:", options=[""] + dropdown_options.get("TRX type", []), help="Select the type of transaction.")
        trx_category = st.selectbox("Select TRX Category:", options=[""] + dropdown_options.get("TRX category", []), help="Select the category.")
        project_name = st.text_input("Enter Project Name (Optional):", help="Optional field for the project name.")
        budget_line = st.text_input("Enter Budget Line (Optional):", help="Optional field for the budget line.")
        purpose = st.text_area("Enter Purpose:", help="Explain the purpose of the transaction.")
        detail = st.text_area("Enter Detail:", help="Provide transaction details.")
        payment_method = st.selectbox("Select Payment Method:", options=[""] + dropdown_options.get("Payment method", []), help="Select payment method.")
        liquidated_amount = st.number_input("Enter Liquidated Amount (IQD):", value=0, help="Enter the amount to be liquidated.")
        liquidated_invoices = st.text_input("Enter Invoice Links (Optional):", help="Provide invoice links if available.")
        supplier_donor = st.text_input("Enter Supplier/Donor Name:", help="Provide the supplier or donor name.")
        contribution = st.text_input("Enter Contribution:", help="Enter any contributions received.")
        remarks = st.text_area("Additional Remarks (Optional):", help="Add any remarks if necessary.")

        # Form submission
        if st.button("Submit Data"):
            if not trx_type or not trx_category or not purpose or not detail or not payment_method or not supplier_donor or not contribution:
                st.warning("Please fill in all required fields.")
                return

            # Auto-generated and default values
            trx_id = generate_trx_id(sheet)
            request_direct = "Direct payment"
            approval_status = "Issued"
            liquidation_status = "Liquidated"
            payment_date = datetime.today().strftime("%Y-%m-%d")
            liquidation_date = datetime.today().strftime("%Y-%m-%d")

            # Adjust liquidated amount based on TRX Type
            if trx_type.lower() == "expense":
                liquidated_amount = -abs(liquidated_amount)  # Ensure negative for expense
            elif trx_type.lower() == "income":
                liquidated_amount = abs(liquidated_amount)   # Ensure positive for income

            # Prepare the final row for Google Sheet
            data_to_add = [
                trx_id,  # Automatically generated TRX ID
                trx_type,
                trx_category,
                request_direct,  # Auto-filled value
                "",  # Requester name (blank)
                project_name if project_name else "",  # Optional project name
                budget_line if budget_line else "",  # Optional budget line
                purpose,
                detail,
                "",  # Requested Amount (blank)
                "",  # Request submission date (blank)
                "",  # Approval status (blank)
                "",  # Approval date (blank)
                approval_status,  # Auto-filled value
                payment_date,  # Auto-filled payment date
                payment_method,
                liquidation_status,  # Auto-filled value
                liquidated_amount,  # Final adjusted liquidated amount
                liquidation_date,  # Auto-filled liquidation date
                liquidated_invoices,  # Optional field
                "",  # Returned amount (blank)
                "",  # Related request ID (blank)
                supplier_donor,
                contribution,
                remarks
            ]

            # Append data to Google Sheet
            sheet.append_row(data_to_add)
            st.success(f"Data added successfully! TRX ID: {trx_id}")

    except Exception as e:
        st.error(f"Error adding data to Google Sheets: {e}")

if __name__ == "__main__":
    render_add_data()
