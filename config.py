import gspread
import os

# Add your Google API credentials here
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "your_credentials.json"
gc = gspread.service_account(filename='creds/credentials.json')

sa = gspread.service_account(filename='creds/credentials.json')
sh = sa.open('Google Sheet Name')
sheet1 = sh.worksheet('Name of specific sheet within sheet')
sheet2 = sh.worksheet('Name of specific sheet within sheet')