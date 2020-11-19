#!/usr/bin/env python3
# Copyright (c) Ryax Technologies

from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
import json
import numpy
from sheets import GoogleSpreadsheet, get_credentials

def save_object(d, where):
    with open(where, 'wb') as f:
        pickle.dump(d, f, pickle.HIGHEST_PROTOCOL)

def load_object(where):
    with open(where, 'rb') as f:
        return pickle.load(f)

def json_from_file(where):
    with open(where, "r") as f:
        ret = json.load(f)
    return ret

def json_to_file(d, where):
    with open(where,'w') as f:
        json.dump(d,f)

def handle(req):
    try:
        spreadsheet_id = req.get('spreadsheet_id') 
        data_file = req.get('data')
        if not os.path.isfile(data_file):
            raise Exception(f"File {data_file} does not exist")
        data = load_object(data_file)

        print("Found data\nHandling google credentials locally")
        creds_string = req.get('credentials')
        creds_dict = json.loads(creds_string.replace("'", "\""))
        saved_creds = '/tmp/google_sheet_credentials.json'
        json_to_file(creds_dict, saved_creds)
        
        
        api_token = req.get('token_file')
        print("Launching google agent...")
        google_auth = get_credentials(
                secret_file = saved_creds,
                token_file = api_token
                )
        if not google_auth:
            raise Exception("Timed out after error: could not retrieve google token.")

        sheet = GoogleSpreadsheet().from_list_of_dicts(
                data,
                id = spreadsheet_id,
                credential = google_auth)
        print("Sending data to server")
        resp = sheet.append()
        print(f"Response: {resp}")

    except Exception as e:
        print(e)

if __name__ == '__main__':
    print("Running locally in order to fetch token.")
    print("Finding credentials in ./credentials.json")
    assert os.path.isfile('credentials.json'), "Credentials file not found in this directory!"
    print("Credentials found!")
    from sheets import get_token_first_time
    print("Contacting the google API to fetch a valid token")
    get_token_first_time('credentials.json')
    print("Done")







