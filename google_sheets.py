import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Define the scope of access (we need both read and write capabilities)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'google_credentials.json'

def get_sheets_service():
    """Authenticates using the JSON key and returns the Sheets service object."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def get_tracker_data(spreadsheet_id, range_name="Sheet1!A1:L"):
    """
    Fetches the data from your specified sheet.
    Range A1:L covers columns from 'Order Date' to 'Calendar Reminder'.
    """
    service = get_sheets_service()
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    
    # Return the raw list of lists
    return result.get('values', [])
