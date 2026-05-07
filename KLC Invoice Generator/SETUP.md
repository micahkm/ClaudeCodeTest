# KLC Invoice Generator — Setup

## 1. Python dependencies

    pip install -r requirements.txt

## 2. Google Cloud project

1. Go to https://console.cloud.google.com
2. Create a new project (or select an existing one)
3. Enable both of these APIs:
   - Google Sheets API
   - Google Drive API

## 3. OAuth2 credentials

1. In the Cloud Console, go to APIs & Services → Credentials
2. Click Create Credentials → OAuth client ID
3. Application type: Desktop app
4. Download the JSON and save it as credentials.json in this folder

On first run, a browser window opens asking you to sign in with
koolaulasercreations@gmail.com and grant access. After approving,
token.json is saved and all future runs are silent.

## 4. Create Invoice TEMPLATE in Drive (for new clients only)

When you invoice a brand-new company for the first time, the app
needs a blank template to copy.

1. Open Invoice U015 (or any recent invoice) in Google Drive
2. File → Make a copy
3. Name the copy exactly: Invoice TEMPLATE
4. Clear all the dynamic cells (submitted date, client name,
   invoice number, project, due date, line items, subtotal, total,
   notes) but leave all header rows and formatting intact
5. Leave at least 20 blank rows below the column-header row

## 5. Run the app

    python app.py
