import gspread
from flask import Flask, request, jsonify
from oauth2client.service_account import ServiceAccountCredentials

# Initialize Flask app
app = Flask(__name__)

# Google Sheets setup
SERVICE_ACCOUNT_FILE = 'clever-bee-442514-j7-ed066186e963.json'
SPREADSHEET_NAME = 'https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0'
TAB_NAME = 'database'

# Authenticate and access Google Sheet
def get_google_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
    client = gspread.authorize(credentials)
    sheet = client.open_by_url(SPREADSHEET_NAME).worksheet(TAB_NAME)
    return sheet

# Route to fetch all data
@app.route('/data', methods=['GET'])
def get_data():
    try:
        sheet = get_google_sheet()
        records = sheet.get_all_records()
        return jsonify({"status": "success", "data": records}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Route to add a new record
@app.route('/data', methods=['POST'])
def add_data():
    try:
        data = request.json
        sheet = get_google_sheet()
        sheet.append_row(list(data.values()))
        return jsonify({"status": "success", "message": "Data added successfully"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Route to update a record
@app.route('/data/<int:row>', methods=['PUT'])
def update_data(row):
    try:
        data = request.json
        sheet = get_google_sheet()
        cell_list = sheet.range(row, 1, row, len(data))
        for i, key in enumerate(data):
            cell_list[i].value = data[key]
        sheet.update_cells(cell_list)
        return jsonify({"status": "success", "message": f"Row {row} updated successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
