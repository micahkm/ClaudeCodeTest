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

# ── Cell position constants (verified against Invoice U015) ──────────────────
SUBMITTED_DATE_CELL  = 'A7'
CLIENT_NAME_CELL     = 'A9'
INVOICE_NUM_CELL     = 'E9'
PROJECT_CELL         = 'A11'
DUE_DATE_CELL        = 'C11'
LINE_ITEMS_START_ROW = 13
LINE_ITEM_DESC_COL   = 'A'
LINE_ITEM_QTY_COL    = 'D'
LINE_ITEM_PRICE_COL  = 'E'
LINE_ITEM_TOTAL_COL  = 'F'
SUBTOTAL_LABEL_COL   = 'E'
SUBTOTAL_VALUE_COL   = 'F'
NOTES_COL            = 'A'
CLEAR_RANGE          = 'A7:F50'


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


def create_invoice_sheet(drive, gc, form_data: dict) -> str:
    """Copy source invoice, write form data into it, return new spreadsheet ID.

    form_data keys:
        company_name  str
        prefix        str
        project       str
        due_date      str  (M/D/YYYY)
        items         list of {'description': str, 'qty': float,
                               'unit_price': float, 'total': float}
        adjustments   float
        notes         str
        invoice_number str  (e.g. 'U016')
    """
    prefix         = form_data['prefix']
    invoice_number = form_data['invoice_number']

    source_id, parent_id = find_source_file(drive, prefix)

    copy_body = {'name': f'Invoice {invoice_number}'}
    if parent_id:
        copy_body['parents'] = [parent_id]
    new_file = drive.files().copy(fileId=source_id, body=copy_body).execute()
    new_id   = new_file['id']

    sh = gc.open_by_key(new_id)
    ws = sh.sheet1

    ws.batch_clear([CLEAR_RANGE])

    today   = datetime.date.today().strftime('%-m/%-d/%Y')
    items   = form_data['items']
    subtotal = round(sum(item['total'] for item in items), 2)
    adj      = form_data['adjustments']
    total    = round(subtotal + adj, 2)

    updates = [
        {'range': SUBMITTED_DATE_CELL, 'values': [[f"Submitted on {today}"]]},
        {'range': CLIENT_NAME_CELL,    'values': [[form_data['company_name']]]},
        {'range': INVOICE_NUM_CELL,    'values': [[invoice_number]]},
        {'range': PROJECT_CELL,        'values': [[form_data['project']]]},
        {'range': DUE_DATE_CELL,       'values': [[form_data['due_date']]]},
    ]

    for i, item in enumerate(items):
        r = LINE_ITEMS_START_ROW + i
        updates += [
            {'range': f'{LINE_ITEM_DESC_COL}{r}',  'values': [[item['description']]]},
            {'range': f'{LINE_ITEM_QTY_COL}{r}',   'values': [[item['qty']]]},
            {'range': f'{LINE_ITEM_PRICE_COL}{r}', 'values': [[item['unit_price']]]},
            {'range': f'{LINE_ITEM_TOTAL_COL}{r}', 'values': [[item['total']]]},
        ]

    sr = LINE_ITEMS_START_ROW + len(items)
    updates += [
        {'range': f'{SUBTOTAL_LABEL_COL}{sr}',     'values': [['Subtotal']]},
        {'range': f'{SUBTOTAL_VALUE_COL}{sr}',     'values': [[f'${subtotal:,.2f}']]},
        {'range': f'{SUBTOTAL_LABEL_COL}{sr + 1}', 'values': [['Adjustments']]},
        {'range': f'{SUBTOTAL_VALUE_COL}{sr + 1}', 'values': [[f'${adj:,.2f}']]},
        {'range': f'{SUBTOTAL_VALUE_COL}{sr + 2}', 'values': [[f'${total:,.2f}']]},
    ]

    note_lines = (form_data['notes'] or '').strip().split('\n')[:3]
    for j, line in enumerate(note_lines):
        updates.append({'range': f'{NOTES_COL}{sr + j}', 'values': [[line]]})

    ws.batch_update(updates, value_input_option='USER_ENTERED')
    return new_id


def export_to_pdf(creds: Credentials, spreadsheet_id: str, invoice_number: str) -> str:
    """Export spreadsheet as PDF to ~/Desktop; return the saved file path."""
    desktop  = os.path.expanduser('~/Desktop')
    pdf_path = os.path.join(desktop, f'Invoice {invoice_number}.pdf')

    url = (
        f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export'
        f'?format=pdf&size=letter&portrait=true&fitw=true&gridlines=false'
    )
    session  = AuthorizedSession(creds)
    response = session.get(url)
    response.raise_for_status()

    with open(pdf_path, 'wb') as f:
        f.write(response.content)

    return pdf_path
