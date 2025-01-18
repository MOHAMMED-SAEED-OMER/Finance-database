import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

# Load credentials from Streamlit secrets
def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch dropdown options from the Helper tab
@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_dropdown_options():
    try:
        client = load_credentials()
        helper_sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("Helper")
        helper_data = helper_sheet.get_all_records()

        # Extract project names and payment methods, ignoring blanks
        dropdown_options = {
            "Project Name": [row["Project name"] for row in helper_data if "Project name" in row and row["Project name"].strip()],
            "Payment Method": [row["Payment method"] for row in helper_data if "Payment method" in row and row["Payment method"].strip()],
        }
        return dropdown_options
    except Exception as e:
        st.error(f"Error fetching dropdown options: {e}")
        return {"Project Name": [], "Payment Method": []}

# Generate the next TRX ID
def generate_trx_id(sheet):
    try:
        all_rows = sheet.get_all_records()
        if all_rows:
            last_trx_id = all_rows[-1].get("TRX ID", "TRX-0000")  # Default if no TRX ID exists
            next_id_number = int(last_trx_id.split("-")[1]) + 1
            return f"TRX-{next_id_number:04d}"
        else:
            return "TRX-0001"
    except Exception as e:
        st.error(f"Error generating TRX ID: {e}")
        return "TRX-0001"

# Render the Request Submission Page
def render_request_form():
    st.title("📝 Submit a Request")
    st.write("Request funds for a project by filling out the form below.")

    # Fetch dropdown options
    dropdown_options = fetch_dropdown_options()

    # Validate dropdown options
    if not dropdown_options["Project Name"]:
        st.warning("No projects found in the Helper tab. Please add project names.")
        return
    if not dropdown_options["Payment Method"]:
        st.warning("No payment methods found in the Helper tab. Please add payment methods.")
        return

    # Form fields
    project = st.selectbox("Choose a Project:", options=[""] + dropdown_options["Project Name"])
    payment_method = st.selectbox("Choose Payment Method:", options=[""] + dropdown_options["Payment Method"])
    budget_line = st.text_input("Write the Budget Line:")
    purpose = st.text_area("Explain the Purpose of Your Request:")
    request_details = st.text_area("Request Details (e.g., cost breakdown):")
    total_amount = st.number_input("Total Amount Requested (negative for expense):", value=0.0, step=0.01)
    notes = st.text_area("Additional Notes or Remarks:")

    # Get the requester name from session state
    requester_name = st.session_state.get("user_email", "Unknown")

    # Submit button
    if st.button("Submit Request"):
        if not project:
            st.warning("Please choose a project.")
            return
        if not payment_method:
            st.warning("Please choose a payment method.")
            return
        if total_amount >= 0:
            st.warning("The total amount requested must be negative.")
            return

        try:
            client = load_credentials()
            sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1

            # Generate TRX ID
            trx_id = generate_trx_id(sheet)

            # Get the current date and time in Baghdad timezone
            baghdad_tz = pytz.timezone("Asia/Baghdad")
            submission_date = datetime.now(baghdad_tz).strftime("%Y-%m-%d %H:%M:%S")

            # Prepare the data to append
            new_row = [
                trx_id,  # TRX ID
                "Expense",  # TRX Type
                "Project expense",  # TRX Category
                "Request based",  # Request/Direct
                requester_name,  # Requester Name
                project,  # Project Name
                budget_line,  # Budget Line
                purpose,  # Purpose
                request_details,  # Detail
                total_amount,  # Requested Amount
                submission_date,  # Request Submission Date
                "Pending",  # Approval Status (default to Pending)
                "",  # Approval Date
                "",  # Payment Status
                "",  # Payment Date
                payment_method,  # Payment Method
                "",  # Liquidation Status
                "",  # Liquidated Amount
                "",  # Liquidation Date
                "",  # Liquidated Invoices
                "",  # Returned Amount
                "",  # Related Request ID
                "",  # Supplier/Donor
                "",  # Contribution
                notes,  # Remarks
            ]

            # Append the data to the Google Sheet
            sheet.append_row(new_row)
            st.success(f"Request submitted successfully! TRX ID: {trx_id}")
        except Exception as e:
            st.error(f"Error submitting request: {e}")
