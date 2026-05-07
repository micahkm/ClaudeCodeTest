import os
import re
import subprocess
from pathlib import Path

import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

_DIR = Path(__file__).parent
TOKEN_PATH = _DIR / "token.json"
CREDS_PATH = _DIR / "credentials.json"

# Cell positions — verified against actual invoice template
CELL_DATE_SUBMITTED = "A7"
CELL_CLIENT_NAME = "A9"
CELL_INVOICE_NUMBER = "E9"
CELL_PROJECT = "A11"
CELL_DUE_DATE = "C11"
LINE_ITEM_START_ROW = 13
LINE_ITEM_COL_DESC = "A"
LINE_ITEM_COL_QTY = "D"
LINE_ITEM_COL_UNIT_PRICE = "E"
LINE_ITEM_COL_TOTAL = "F"
CLEAR_RANGE = "A7:F50"
CELL_ADJUSTMENTS = "E40"


def authenticate():
    """Returns (gspread.Client, drive_service, creds). Opens browser on first run."""
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())
    gc = gspread.authorize(creds)
    drive = build("drive", "v3", credentials=creds)
    return gc, drive, creds


def search_invoices(drive, prefix: str) -> list[dict]:
    """Returns Drive file dicts matching 'Invoice <PREFIX>NNN', ordered name desc."""
    query = (
        f"name contains 'Invoice {prefix}' "
        "and mimeType='application/vnd.google-apps.spreadsheet' "
        "and trashed=false"
    )
    result = drive.files().list(
        q=query,
        fields="files(id, name, parents)",
        orderBy="name desc",
    ).execute()
    files = result.get("files", [])
    pattern = re.compile(rf'^Invoice {re.escape(prefix)}\d+$', re.IGNORECASE)
    return [f for f in files if pattern.match(f["name"].strip())]


def search_template(drive) -> dict | None:
    """Returns the 'Invoice TEMPLATE' Drive file dict, or None if not found."""
    query = (
        "name = 'Invoice TEMPLATE' "
        "and mimeType='application/vnd.google-apps.spreadsheet' "
        "and trashed=false"
    )
    result = drive.files().list(q=query, fields="files(id, name, parents)").execute()
    files = result.get("files", [])
    return files[0] if files else None


def copy_invoice(drive, source_id: str, new_name: str, folder_id: str) -> str:
    """Copies a Drive file into the same folder. Returns the new file's ID."""
    body = {"name": new_name, "parents": [folder_id]}
    new_file = drive.files().copy(fileId=source_id, body=body).execute()
    return new_file["id"]


def write_invoice_cells(gc, sheet_id: str, data: dict) -> None:
    """Batch-clears data range and writes all invoice fields.

    data keys: client_name (str), invoice_number (str), project (str),
               due_date (str), date_submitted (str),
               line_items (list of {desc: str, qty: float, price: float, total: float}),
               notes (list[str], up to 3 elements), adjustments (float)
    """
    ws = gc.open_by_key(sheet_id).sheet1
    ws.batch_clear([CLEAR_RANGE])

    updates = [
        {"range": CELL_DATE_SUBMITTED, "values": [[data["date_submitted"]]]},
        {"range": CELL_CLIENT_NAME,    "values": [[data["client_name"]]]},
        {"range": CELL_INVOICE_NUMBER, "values": [[data["invoice_number"]]]},
        {"range": CELL_PROJECT,        "values": [[data["project"]]]},
        {"range": CELL_DUE_DATE,       "values": [[data["due_date"]]]},
    ]

    for i, item in enumerate(data["line_items"]):
        row = LINE_ITEM_START_ROW + i
        updates += [
            {"range": f"{LINE_ITEM_COL_DESC}{row}",       "values": [[item["desc"]]]},
            {"range": f"{LINE_ITEM_COL_QTY}{row}",        "values": [[item["qty"]]]},
            {"range": f"{LINE_ITEM_COL_UNIT_PRICE}{row}", "values": [[item["price"]]]},
            {"range": f"{LINE_ITEM_COL_TOTAL}{row}",      "values": [[item["total"]]]},
        ]

    note_start = LINE_ITEM_START_ROW + len(data["line_items"]) + 2
    for j, line in enumerate(data.get("notes", [])[:3]):
        if line.strip():
            updates.append({"range": f"A{note_start + j}", "values": [[line]]})

    if data.get("adjustments", 0) != 0:
        updates.append({"range": CELL_ADJUSTMENTS, "values": [[data["adjustments"]]]})

    ws.batch_update(updates, value_input_option="USER_ENTERED")


def export_pdf(creds, file_id: str, dest_path: str) -> None:
    """Exports a Google Sheet as PDF, saves to dest_path, and opens it."""
    from google.auth.transport.requests import AuthorizedSession
    url = (
        f"https://docs.google.com/spreadsheets/d/{file_id}/export"
        "?format=pdf&size=letter&portrait=true&fitw=true&gridlines=false"
    )
    session = AuthorizedSession(creds)
    r = session.get(url)
    r.raise_for_status()
    Path(dest_path).write_bytes(r.content)
    subprocess.run(["open", dest_path], check=True)


def create_invoice(data: dict) -> tuple[str, str]:
    """Main entry point called by app.py.

    Returns (sheet_url, pdf_path).
    Raises RuntimeError with a user-readable message on failure.
    """
    from logic import next_invoice_number

    gc, drive, creds = authenticate()
    prefix = data["prefix"]

    existing = search_invoices(drive, prefix)
    if existing:
        source = existing[0]           # ordered name desc → highest number first
        folder_id = source["parents"][0]
    else:
        template = search_template(drive)
        if not template:
            raise RuntimeError(
                "No existing invoices found for this prefix and no "
                "'Invoice TEMPLATE' found in Drive.\n\n"
                "Create an 'Invoice TEMPLATE' spreadsheet in Drive first."
            )
        source = template
        folder_id = template["parents"][0]

    filenames = [f["name"] for f in existing]
    invoice_num = next_invoice_number(filenames, prefix)
    new_name = f"Invoice {invoice_num}"

    new_id = copy_invoice(drive, source["id"], new_name, folder_id)
    write_invoice_cells(gc, new_id, {**data, "invoice_number": invoice_num})

    pdf_path = str(Path.home() / "Desktop" / f"{new_name}.pdf")
    export_pdf(creds, new_id, pdf_path)

    sheet_url = f"https://docs.google.com/spreadsheets/d/{new_id}"
    return sheet_url, pdf_path
