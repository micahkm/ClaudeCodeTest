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
