#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Imports to access gdocs
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Imports for parsing yaml
import argparse
import os
import typing as t
from robust import yaml

DESCRIPTION = 'Reads fault and failure codes and updates the bug files'

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of robust spreadsheet.
SPREADSHEET_ID = '1WMnp8a2I79aVBS4x_vjAkxFzzELsBpmjYgMEuytZOhg'
RANGE_NAME = 'Coding!A2:F'

COLUMN_BUG = 0
COLUMN_FAULT = 4
COLUMN_FAILURE = 5

dir_here = os.path.dirname(__file__)
token_path = os.path.join(dir_here, 'token.pickle')
credentials_path = os.path.join(dir_here, 'credentials.json')

def get_credentials():
    creds = None
    # If there are no (valid) credentials available, let the user log in.
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_gsheets_data() -> t.Iterator[t.List[str]]:
    creds = get_credentials()

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('Error: No data found.')
        return

    for row in values:
        # return columns 'Bug', 'Fault labels' and 'Failure labels'
        try:
            yield [row[COLUMN_BUG], row[COLUMN_FAULT], row[COLUMN_FAILURE]]
        except:
            print(f"ERROR: Empty fields encountered for {row[COLUMN_BUG]} in 'ROBUST coding'")
            yield [row[COLUMN_BUG], "", ""]

def refactor_fault_failure(description: t.List[str], faults: t.List[str], failures: t.List[str], update: bool = True) -> None:
    if 'failure-codes' and 'fault-codes' in description:
        if not update:
            return
        else:
            del description['fault-codes']
            del description['failure-codes']

    description['fault-codes'] = failures
    description['failure-codes'] = faults

def refactor_file(filename: str, faults: str, failures: str, update: bool = True) -> None:
    robust_dir = os.path.dirname(dir_here)
    bug_path = os.path.join(robust_dir, filename)

    try:
        with open(bug_path, 'r') as f:
            description = yaml.load(f)
    except (FileNotFoundError, IOError) as err:
        print(f"{err}")
        return

    try:
        faults_ = faults.upper().splitlines()
        failures_ = failures.upper().splitlines()
        refactor_fault_failure(description, faults_, failures_)
    except ValueError as err:
        print(f"ERROR [{filename}]: {err}")

    with open(bug_path, 'w') as f:
        yaml.dump(description, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--update',
                        nargs='?',
                        type=bool,
                        default=True,
                        help='Update fault-codes and failure-codes even if the fields exist in the bug files.')
    args = parser.parse_args()
    for row in get_gsheets_data():
        refactor_file(row[0], row[1], row[2], args.update)

