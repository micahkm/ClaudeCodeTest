"""Google Drive/Sheets API logic for KLC Invoice Generator."""
import os
import re
import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request, AuthorizedSession
from googleapiclient.discovery import build
import gspread

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
TOKEN_FILE       = os.path.join(os.path.dirname(__file__), 'token.json')


def suggest_prefix(company_name: str) -> str:
    """Return first word of company name, uppercased, max 4 chars."""
    if not company_name.strip():
        return ''
    first_word = company_name.strip().split()[0]
    return first_word.upper()[:4]


def next_invoice_number(titles: list, prefix: str) -> str:
    """Scan Drive file title list and return the next invoice number for prefix."""
    pattern = re.compile(rf'^Invoice {re.escape(prefix)}(\d+)$', re.IGNORECASE)
    numbers = [int(m.group(1)) for t in titles if (m := pattern.match(t.strip()))]
    next_num = (max(numbers) + 1) if numbers else 1
    return f'{prefix}{next_num:03d}'


def get_credentials() -> Credentials:
    """Load or refresh OAuth2 credentials; opens browser on first run."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f'credentials.json not found at {CREDENTIALS_FILE}\n'
                    'See SETUP.md for instructions.'
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return creds


def get_clients(creds: Credentials):
    """Return (gspread_client, drive_service) built from credentials."""
    gc    = gspread.authorize(creds)
    drive = build('drive', 'v3', credentials=creds)
    return gc, drive


def get_all_invoice_titles(drive) -> list:
    """Return all Google Sheet titles that contain 'Invoice' (for numbering lookup)."""
    resp = drive.files().list(
        q="name contains 'Invoice' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false",
        fields='files(name)',
        pageSize=200,
    ).execute()
    return [f['name'] for f in resp.get('files', [])]


def find_source_file(drive, prefix: str):
    """Return (file_id, parent_folder_id) of highest-numbered invoice for prefix.
    Falls back to 'Invoice TEMPLATE' if no prior invoices exist for this prefix."""
    resp = drive.files().list(
        q=f"name contains 'Invoice {prefix}' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false",
        fields='files(id, name, parents)',
        pageSize=200,
    ).execute()
    files = resp.get('files', [])

    pattern = re.compile(rf'^Invoice {re.escape(prefix)}(\d+)$', re.IGNORECASE)
    numbered = []
    for f in files:
        m = pattern.match(f['name'].strip())
        if m:
            numbered.append((int(m.group(1)), f['id'], (f.get('parents') or [None])[0]))

    if numbered:
        numbered.sort(reverse=True)
        _, file_id, parent_id = numbered[0]
        return file_id, parent_id

    # No prior invoices for this prefix — fall back to master template
    tmpl = drive.files().list(
        q="name = 'Invoice TEMPLATE' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false",
        fields='files(id, parents)',
    ).execute().get('files', [])
    if not tmpl:
        raise FileNotFoundError(
            "No existing invoices found for this prefix and no 'Invoice TEMPLATE' found in Drive.\n"
            "See SETUP.md for template setup instructions."
        )
    return tmpl[0]['id'], (tmpl[0].get('parents') or [None])[0]
