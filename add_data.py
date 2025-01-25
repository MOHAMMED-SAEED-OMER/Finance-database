import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from datetime import datetime

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

# Render the Add New Data Page
def render_add_data():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>📋 Add New Transaction</h2>", unsafe_allow_html=True)
    st.write("Fill out the form below to add a new transaction directly to the database.")

    try:
        # Authenticate and open the Google Sheet
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1

        # Fetch dropdown options
        dropdown_options = fetch_dropdown_options_vertical()

        # Define necessary headers for required fields
        headers = [
            "TRX type", "TRX category", "Project name", "Budget line", "Purpose", 
            "Detail", "Payment method", "Liquidated amount", "Supplier/Donor", "Contribution"
        ]

        # Auto-filled values
        auto_values = {
            "Request/Direct": "Direct payment",
            "Payment status": "Issued",
            "Payment date": datetime.today().strftime("%Y-%m-%d"),
            "Liquidation status": "Liquidated",
            "Liquidation date": datetime.today().strftime("%Y-%m-%d"),
            "Requester name": "",
            "Requested Amount": "",
            "Request submission date": "",
            "Approval Status": "",
            "Approval date": "",
            "Returned amount": "",
            "Related request ID": "",
        }

        # Custom CSS for better styling
        st.markdown("""
            <style>
                .stTextInput, .stSelectbox, .stDateInput, .stNumberInput {
                    border-radius: 10px;
                    border: 2px solid #1E3A8A;
                    padding: 10px;
                }
                .submit-btn {
                    background-color: #1E3A8A;
                    color: white;
                    font-size: 18px;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                }
                .submit-btn:hover {
                    background-color: #3B82F6;
                }
            </style>
        """, unsafe_allow_html=True)

        # Create form to prevent multiple submissions
        with st.form("data_entry_form"):
            data_to_add = []

            # Required fields
            trx_type = st.selectbox("Select TRX Type:", options=[""] + dropdown_options.get("TRX type", []))
            trx_category = st.selectbox("Select TRX Category:", options=[""] + dropdown_options.get("TRX category", []))
            project_name = st.selectbox("Select Project Name:", options=[""] + dropdown_options.get("Project name", []))
            budget_line = st.text_input("Enter Budget Line:")
            purpose = st.text_input("Enter Purpose:")
            detail = st.text_area("Enter Detail:")
            payment_method = st.selectbox("Select Payment Method:", options=[""] + dropdown_options.get("Payment method", []))
            liquidated_amount = st.number_input("Enter Liquidated Amount:", min_value=0, step=1000)
            supplier_donor = st.text_input("Enter Supplier/Donor:")
            contribution = st.text_input("Enter Contribution:")

            # Optional fields
            liquidated_invoices = st.text_input("Enter Liquidated Invoices (Optional):", placeholder="Add invoice links if applicable")
            remarks = st.text_area("Additional Remarks (Optional):", placeholder="Any additional comments")

            # Prepare the final row for Google Sheet
            data_to_add = [
                "", trx_type, trx_category, auto_values["Request/Direct"], auto_values["Requester name"],
                project_name, budget_line, purpose, detail, auto_values["Requested Amount"],
                auto_values["Request submission date"], auto_values["Approval Status"], auto_values["Approval date"],
                auto_values["Payment status"], auto_values["Payment date"], payment_method,
                auto_values["Liquidation status"], liquidated_amount, auto_values["Liquidation date"],
                liquidated_invoices, auto_values["Returned amount"], auto_values["Related request ID"],
                supplier_donor, contribution, remarks
            ]

            # Submit button to add data
            submit_button = st.form_submit_button("Submit Data", use_container_width=True)

            # Validate form before submission
            if submit_button:
                if not all([trx_type, trx_category, project_name, budget_line, purpose, detail, payment_method, liquidated_amount, supplier_donor, contribution]):
                    st.warning("⚠️ Please fill in all required fields.")
                else:
                    sheet.append_row(data_to_add)  # Append data to Google Sheet
                    st.success("✅ Data added successfully!")
                    st.write("**Submitted Data:**")
                    st.write(dict(zip(headers + ["Liquidated invoices", "Remarks"], data_to_add)))

    except Exception as e:
        st.error(f"Error adding data to Google Sheets: {e}")

if __name__ == "__main__":
    render_add_data()
