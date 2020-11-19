#!/usr/bin/env python3
# Copyright (c) Ryax Technologies

from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
import numpy
from typing import List


def get_credentials(
        secret_file = 'credentials.json',
        token_file = '/tmp/token.pickle',
        scopes =['https://www.googleapis.com/auth/spreadsheets']):
    cred = None
    token_save_location = '/tmp/token.pickle'
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            cred = pickle.load(token)
            print(f'Found token at {token_file}')
    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            print("WARNING: attempting to refresh token")
            cred.refresh(Request())
        else:
            print(f"WARNING: token was either not found or was invalid")
            flow = InstalledAppFlow.from_client_secrets_file(secret_file, scopes)
            print(f"You must access the following URL to gain a google access token: {flow.authorization_url()[0]}\nUpload this token in the same directory as your handler.py to Ryax in order to use it.") 
            return None
            # cred = flow.run_local_server()
    print(f"Valid token obtained, saving it to {token_save_location}")
    with open(token_save_location, 'wb') as token:
        pickle.dump(cred, token)
    return cred

class GoogleSpreadsheet:
    def __init__(self, id = None, credential = None, title = None, data = []):
        self.cred = credential
        self.id = id 
        self.data = data 
        self.service = None

    def __str__(self):
        return str([str(x)+'\n' for x in self.data])

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, data={self.data})>"

    def create_new_sheet(self, title):
        assert title is not None, "Spreadsheet needs a title"
        service = self.get_service()
        blank_sheet = {"properties": {"title":title}}
        spreadsheet = (
                service.spreadsheets().create(body=blank_sheet, fields='spreadsheetId').execute()
                )
        self.id = spreadsheet.get("spreadsheetId")
        return self.id

    @classmethod
    def from_list_of_dicts(
            cls, 
            d: List[dict],
            id = None, 
            title = None,
            credential = None):
        assert all(x.keys() == d[0].keys() for x in d)
        values = [[x for x in d[0].keys()]]
        for row in d:
            values.append([row.get(val) for val in values[0]])
        return cls(id = id, credential = credential, title = title, data = values)

    @classmethod
    def from_nested_list(
            cls,
            d: List[list],
            id = None,
            title = None,
            credential = None):
        assert all(len(x)==len(d[0]) for x in d)
        return cls(id = id, credential = credential, title = title, data = d)
 
    def update_credential(self, cred):
        self.cred = cred

    def get_service(self,
            api_name: str = 'sheets',
            api_version: str = 'v4'):
        return build(api_name, api_version, credentials=self.cred)

    def update(self, majorDimension = 'ROWS', start_cell = 'A1'):
        service = self.get_service()
        value_body = {'majorDimension': majorDimension,'values': self.data}
        request = service.spreadsheets().values().update(
                spreadsheetId = self.id,
                valueInputOption = 'USER_ENTERED',
                range = 'A1',
                body = value_body
                )
        response = request.execute()
        return response

    def append(self, majorDimension = 'ROWS', start_cell = 'A1'):
        service = self.get_service()
        value_body = {'majorDimension': majorDimension,'values': self.data}
        request = service.spreadsheets().values().append(
                spreadsheetId = self.id,
                valueInputOption = 'USER_ENTERED',
                range = 'A1',
                body = value_body
                )
        response = request.execute()
        return response
