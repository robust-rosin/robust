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
from bug_validator import BugValidator
from collections import OrderedDict

DESCRIPTION = 'Reads fault and failure codes and updates the bug files'

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of robust spreadsheet.
SPREADSHEET_ID = '167XH2qjA6Zrt5xDwxP999BejnLn3KeFQK1DesM7H3wA'
RANGE_NAME = 'Coding!A2:J'

COLUMN_BUG = 0
COLUMN_FAULT = 5
COLUMN_FAILURE_SW = 8
COLUMN_FAILURE_SYS = 9

dir_here = os.path.dirname(__file__)
token_path = os.path.join(dir_here, 'token.pickle')
credentials_path = os.path.join(dir_here, 'credentials.json')

bug_validator = BugValidator()

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
            yield [row[COLUMN_BUG], row[COLUMN_FAULT], row[COLUMN_FAILURE_SW], row[COLUMN_FAILURE_SYS]]
        except:
            print(f"ERROR: Empty fields encountered for {row[COLUMN_BUG]} in 'ROBUST coding'")
            yield [row[COLUMN_BUG], None, None, None]

def refactor_fault_failure(description: t.List[str], faults: t.List[str], failures: t.List[str], update: bool = True) -> None:
    if 'failure-codes' in description and 'fault-codes' in description and not update:
            return

    description['fault-codes'] = faults
    description['failure-codes'] = failures

def refactor_file(filename: str,
                  faults: t.Optional[str],
                  failure_sw: t.Optional[str],
                  failure_sys: t.Optional[str],
                  update: bool = True) -> None:
    robust_dir = os.path.dirname(dir_here)
    bug_path = os.path.join(robust_dir, filename)

    try:
        with open(bug_path, 'r') as f:
            description = yaml.load(f)
    except (FileNotFoundError, IOError) as err:
        print(f"{err}")
        return

    fault_list: t.Optional[t.List[str]]
    fault_list = None
    if not faults:
        print(f"{filename}: No fault codes assigned to the bug")
    else:
        fault_list = faults.upper().splitlines()

    failure_sw_list: t.Optional[t.List[str]]
    failure_sw_list = None
    if not failure_sw:
        print(f"{filename}: No software failure codes assigned to the bug")
    else:
        failure_sw_list = failure_sw.upper().splitlines()
    if failure_sw_list != None and len(failure_sw_list) != 1:
        raise ValueError(filename, "There should be exactly one software failure code assigned for each bug.")

    failure_sys_list: t.Optional[t.List[str]]
    failure_sys_list = None
    if not failure_sys:
        print(f"{filename}: No system failure codes assigned to the bug")
    else:
        failure_sys_list = failure_sys.upper().splitlines()

    failure_list: t.Optional[t.List[str]]
    failure_list = None
    if failure_sw_list != None and failure_sys_list != None:
        failure_list = failure_sw_list + failure_sys_list

    if fault_list == None and failure_list == None:
        return

    refactor_fault_failure(description, fault_list, failure_list)

    if not bug_validator.validate(OrderedDict(description.items())):
        raise ValueError(filename, "Invalid fault-failure codes assigned to the bug.")

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

    bug_validator.make_schema('fault-codes', 'failure-codes')

    for row in get_gsheets_data():
        refactor_file(row[0], row[1], row[2], row[3], args.update)


