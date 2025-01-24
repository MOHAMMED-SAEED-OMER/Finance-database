import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import pandas as pd
import io
from fpdf import FPDF

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

        # Convert columns to numeric where applicable
        df["Liquidated amount"] = pd.to_numeric(df["Liquidated amount"], errors="coerce").fillna(0).astype(int)

        return df
    except Exception as e:
        st.error(f"Error loading the database: {e}")
        return pd.DataFrame()

# Generate PDF file
def generate_pdf(dataframe):
    output = io.BytesIO()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, "Finance Database Export", ln=True, align='C')

    # Adding table headers
    pdf.set_font("Arial", style="B", size=10)
    for col in dataframe.columns:
        pdf.cell(40, 10, col, border=1)

    pdf.ln()

    # Adding table rows
    pdf.set_font("Arial", size=10)
    for index, row in dataframe.iterrows():
        for col in dataframe.columns:
            pdf.cell(40, 10, str(row[col]), border=1)
        pdf.ln()

    # Save the PDF to the buffer
    pdf.output(output)
    pdf_data = output.getvalue()
    output.close()
    return pdf_data


# Render the Database Page
def render_database():
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>Database Viewer</h2>", unsafe_allow_html=True)
    st.write("Monitor all requests and their statuses in real-time.")

    df = fetch_database()

    if df.empty:
        st.warning("No data available in the database.")
        return

    # Filter section inside the page
    st.markdown("### Filter Requests")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        filter_column = st.selectbox("Select Column to Filter", ["None"] + list(df.columns))

    filtered_df = df.copy()
    if filter_column != "None":
        with col2:
            filter_value = st.text_input(f"Enter value for {filter_column}:")
        
        if filter_value:
            filtered_df = filtered_df[filtered_df[filter_column].astype(str).str.contains(filter_value, case=False, na=False)]

    # Calculate financial metrics
    total_income = filtered_df[filtered_df["TRX type"].str.lower() == "income"]["Liquidated amount"].sum()
    total_expenses = filtered_df[filtered_df["TRX type"].str.lower() == "expense"]["Liquidated amount"].sum()
    net_funds = total_income + total_expenses  # Expenses are negative

    # Display summary stats
    st.markdown("### Summary Overview")
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Income", f"{total_income:,} IQD")
    col2.metric("Total Expenses", f"{total_expenses:,} IQD")
    col3.metric("Remaining Funds", f"{net_funds:,} IQD")

    # Display the database with improved styling
    st.markdown("### Request Data")

    st.dataframe(
        filtered_df.style.set_table_styles([
            {'selector': 'thead', 'props': [('background-color', '#1E3A8A'), ('color', 'white')]},
            {'selector': 'tbody tr:nth-child(odd)', 'props': [('background-color', '#f0f0f0')]},
            {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#ffffff')]}
        ]),
        height=500,
        use_container_width=True
    )

  # Export data section at the top
st.markdown("### Export Data")
col1, col2 = st.columns(2)

with col1:
    export_format = st.radio("Choose Export Format:", ["Excel", "CSV", "PDF"], horizontal=True)

with col2:
    if st.button("Download"):
        if export_format == "Excel":
            try:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    filtered_df.to_excel(writer, index=False, sheet_name="Database")
                    writer.close()
                st.download_button(
                    "Download Excel", 
                    output.getvalue(), 
                    file_name="database_export.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Excel export failed: {e}")

        elif export_format == "CSV":
            csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV", 
                csv, 
                file_name="database_export.csv", 
                mime="text/csv"
            )

        elif export_format == "PDF":
            try:
                pdf_data = generate_pdf(filtered_df)
                st.download_button(
                    label="Download PDF",
                    data=pdf_data,
                    file_name="database_export.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"PDF export failed: {e}")

if __name__ == "__main__":
    render_database()
