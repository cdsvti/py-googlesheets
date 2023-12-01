import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json. readonly,
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "1j1eh_8ndygSwEa4Q4qa0dLGwXXlH1ODwC4uTMppZdc4"
RANGE_NAME = "Página1!A1:F"

def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use the headless mode for authentication
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0, authorization_prompt_message="")
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])
        print(values)
        return sheet

    except HttpError as err:
        print(err)

def get_units(sheet):
    try:
        # Call the Sheets API
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return []

        header = values[0]
        units = [row for row in values[1:] if row and len(row) >= 2 and row[header.index("Status")].lower() == "livre"]
        return units

    except HttpError as err:
        print(err)
        return []

def update_status(sheet, unit, new_status):
    try:
        # Call the Sheets API
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        header = values[0]
        unit_index = header.index("Unit")

        # Find the row with the specified unit
        for row in values[1:]:
            if row and len(row) >= unit_index + 1 and row[unit_index] == unit:
                # Update the status in the corresponding row
                status_index = header.index("Status")
                row[status_index] = new_status

                # Update the sheet with the modified values
                sheet.values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=RANGE_NAME,
                    body={"values": values},
                    valueInputOption="RAW"
                ).execute()

                print(f"Status for Unit {unit} updated to {new_status}.")
                return

        print(f"Unit {unit} not found.")

    except HttpError as err:
        print(err)

if __name__ == "__main__":
    # Run the main function and obtain the sheet object
    sheet = main()

    # Run the get_units function using the obtained sheet object
    units = get_units(sheet)
    print("Filtered Rows: Unit,Status,Price,Sqt,Room,Bd")
    print(units)
    #
    # Convert units to JSON format
    json_units = json.dumps(units)
    print("JSON Format:")
    print(json_units)

    # Example: Update status for Unit 101 to "Ocupado"
    #update_status(sheet, "118", "Ocupado")
