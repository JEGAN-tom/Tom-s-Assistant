from __future__ import print_function

from auth import spreadsheet_service

from auth import drive_service

def create():
    spreadsheet_details = {
                            'properties':{
                                            'title': 'TomTestGoogleSheet'
                                         }
                          }

    sheet = spreadsheet_service.spreadsheets().create(body=spreadsheet_details,fields='spreadsheetId').execute()
    sheetId = sheet.get('spreadsheetId')

    print('Spreadsheet ID: {0}'.format(sheetId))

    permission1 = {
                    'type': 'user',
                    'role': 'writer',
                    'emailAddress': 'jegan007.jr@gmail.com'

                  }
    drive_service.permissions().create(fileId=sheetId, body=permission1).execute()

    return sheetId

#create()