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
@st.cache_data(ttl=60)
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
            last_trx_id = all_rows[-1].get("TRX ID", "TRX-0000")
            next_id_number = int(last_trx_id.split("-")[1]) + 1
            return f"TRX-{next_id_number:04d}"
        else:
            return "TRX-0001"
    except Exception as e:
        st.error(f"Error generating TRX ID: {e}")
        return "TRX-0001"

# Render the Request Submission Page
def render_request_form():
    st.markdown(
        """
        <style>
            .request-header {
                font-size: 2.5rem;
                font-weight: bold;
                color: #1E3A8A;
                text-align: center;
                margin-bottom: 20px;
            }
            .request-container {
                max-width: 800px;
                margin: auto;
                padding: 2rem;
                background: #ffffff;
                border-radius: 12px;
                box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.2);
            }
            .request-subtitle {
                font-size: 1.2rem;
                color: #374151;
                text-align: center;
                margin-bottom: 30px;
            }
            .submit-btn {
                background-color: #1E3A8A;
                color: white;
                border-radius: 5px;
                padding: 12px;
                font-size: 1.2rem;
                width: 100%;
                border: none;
                cursor: pointer;
            }
            .submit-btn:hover {
                background-color: #3B82F6;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='request-header'>Requests</div>", unsafe_allow_html=True)
    st.markdown("<div class='request-container'>", unsafe_allow_html=True)
    st.markdown("<div class='request-subtitle'>Request funds here</div>", unsafe_allow_html=True)

    # Fetch dropdown options
    dropdown_options = fetch_dropdown_options()

    # Validate dropdown options
    if not dropdown_options["Project Name"]:
        st.warning("No projects found in the Helper tab. Please add project names.")
        return
    if not dropdown_options["Payment Method"]:
        st.warning("No payment methods found in the Helper tab. Please add payment methods.")
        return

    # Form fields with tooltips
    project = st.selectbox(
        "Choose a Project:",
        options=[""] + dropdown_options["Project Name"],
        help="Select the project you are requesting funds for."
    )
    payment_method = st.selectbox(
        "Choose Payment Method:",
        options=[""] + dropdown_options["Payment Method"],
        help="Select the payment method you prefer (e.g., cash, bank transfer)."
    )
    budget_line = st.text_input(
        "Budget Line:",
        placeholder="Enter the budget line number",
        help="Provide the budget line number related to this request."
    )
    purpose = st.text_area(
        "Purpose of Request:",
        placeholder="Describe the purpose of the request",
        help="Provide a brief description of the reason for requesting funds."
    )
    request_details = st.text_area(
        "Request Details:",
        placeholder="Provide a cost breakdown (e.g., item1: $50, item2: $30)",
        help="Include detailed breakdown of items and costs."
    )
    total_amount = st.number_input(
        "Total Amount Requested (negative for expense):",
        value=0.0,
        step=0.01,
        help="Enter the total requested amount as a negative number (e.g., -1000 for expenses)."
    )
    notes = st.text_area(
        "Additional Notes or Remarks:",
        placeholder="Enter any additional information (optional)",
        help="Include any additional details or remarks about your request."
    )

    # Get the requester name from session state
    requester_name = st.session_state.get("user_email", "Unknown")

    # Submit button
    if st.button("Submit Request", key="submit_request", use_container_width=True):
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
                trx_id, "Expense", "Project expense", "Request based", requester_name,
                project, budget_line, purpose, request_details, total_amount,
                submission_date, "Pending", "", "", "", payment_method,
                "", "", "", "", "", "", "", "", notes
            ]

            # Append the data to the Google Sheet
            sheet.append_row(new_row)

            st.success(f"Request submitted successfully! TRX ID: {trx_id}")
        except Exception as e:
            st.error(f"Error submitting request: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
