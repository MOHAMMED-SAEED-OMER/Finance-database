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

# Fetch dropdown options from Helper tab (vertical structure with categories as columns)
@st.cache_data(ttl=60)  # Cache for 60 seconds
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

# Render the Add New Data Page
def render_add_data():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Add New Data</h2>", unsafe_allow_html=True)
    st.write("Use this page to add new financial records to the database dynamically.")

    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1

        # Fetch dropdown options
        dropdown_options = fetch_dropdown_options_vertical()

        # Form layout
        with st.form("data_entry_form"):
            trx_type = st.selectbox("Transaction Type:", options=[""] + dropdown_options.get("TRX type", []), help="Select the transaction type.")
            trx_category = st.selectbox("Transaction Category:", options=[""] + dropdown_options.get("TRX category", []), help="Select the transaction category.")
            project_name = st.selectbox("Project Name:", options=[""] + dropdown_options.get("Project name", []), help="Select the project name.")
            budget_line = st.text_input("Budget Line:", help="Enter the budget line item.")
            purpose = st.text_area("Purpose:", help="Explain the purpose of the transaction.")
            detail = st.text_area("Details:", help="Provide additional details about the transaction.")
            payment_method = st.selectbox("Payment Method:", options=[""] + dropdown_options.get("Payment method", []), help="Select the payment method.")
            liquidated_amount = st.number_input("Liquidated Amount (IQD):", min_value=0, help="Enter the liquidated amount in IQD.")
            supplier_donor = st.text_input("Supplier/Donor:", help="Enter the supplier or donor name.")
            contribution = st.text_input("Contribution:", help="Enter any contribution details.")
            liquidated_invoices = st.text_input("Liquidated Invoices (Optional):", help="Provide invoice links if available.")
            remarks = st.text_area("Remarks (Optional):", help="Any additional remarks.")

            # Submit button to add data
            submit_button = st.form_submit_button("Submit Data")

            if submit_button:
                # Check required fields
                if not trx_type or not trx_category or not project_name or not budget_line or not purpose or not detail or not payment_method or not liquidated_amount or not supplier_donor or not contribution:
                    st.warning("Please fill in all required fields.")
                else:
                    # Prepare the final row for Google Sheet
                    data_to_add = [
                        "",  # TRX ID (auto)
                        trx_type,
                        trx_category,
                        "Direct payment",  # Auto-filled value
                        "",  # Requester name (blank)
                        project_name,
                        budget_line,
                        purpose,
                        detail,
                        "",  # Requested Amount (blank)
                        "",  # Request submission date (blank)
                        "",  # Approval status (blank)
                        "",  # Approval date (blank)
                        "Issued",  # Auto-filled value
                        datetime.today().strftime("%Y-%m-%d"),  # Auto-filled payment date
                        payment_method,
                        "Liquidated",  # Auto-filled value
                        liquidated_amount,
                        datetime.today().strftime("%Y-%m-%d"),  # Auto-filled liquidation date
                        liquidated_invoices,  # Optional field
                        "",  # Returned amount (blank)
                        "",  # Related request ID (blank)
                        supplier_donor,
                        contribution,
                        remarks
                    ]

                    # Append data to Google Sheet
                    sheet.append_row(data_to_add)
                    st.success("Data added successfully!")

    except Exception as e:
        st.error(f"Error adding data to Google Sheets: {e}")

if __name__ == "__main__":
    render_add_data()
