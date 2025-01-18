import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

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

        # Prepare the data to append
        new_row = [
            "Expense",  # TRX Type
            "Request based",  # TRX Category
            budget_line,  # Budget Line
            project,  # Project Name
            payment_method,  # Payment Method
            "To be liquidated",  # Default Liquidation Status
            purpose,  # Purpose
            request_details,  # Request Details
            total_amount,  # Amount
            notes,  # Notes/Remarks
        ]

        # Debug log to verify the data
        st.write("Data to append:", new_row)

        # Append the data to the Google Sheet
        sheet.append_row(new_row)
        st.success("Request submitted successfully!")
    except Exception as e:
        st.error(f"Error submitting request: {e}")
