# KLC Invoice Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python/tkinter desktop app that fills in a Google Sheets invoice from a form, saves it to Drive, and exports a PDF to the Desktop.

**Architecture:** `logic.py` holds pure functions (prefix suggestion, invoice numbering) that are unit-tested before anything else. `sheets.py` holds all Google API logic (auth, Drive copy, Sheets write, PDF export). `app.py` is the tkinter UI that calls `sheets.create_invoice(data)` on submit — it never touches Google APIs directly.

**Tech Stack:** Python 3.11+, tkinter (stdlib), gspread 6.x, google-auth-oauthlib, google-api-python-client

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `KLC Invoice Generator/logic.py` | Create | Pure functions: suggest_prefix, next_invoice_number |
| `KLC Invoice Generator/sheets.py` | Create | All Google API logic |
| `KLC Invoice Generator/app.py` | Create | tkinter UI |
| `KLC Invoice Generator/tests/__init__.py` | Create | Empty, marks tests as package |
| `KLC Invoice Generator/tests/test_logic.py` | Create | Unit tests for logic.py |
| `KLC Invoice Generator/requirements.txt` | Create | Python dependencies |
| `KLC Invoice Generator/.gitignore` | Create | Ignore token.json, credentials.json, __pycache__ |
| `KLC Invoice Generator/SETUP.md` | Create | One-time user setup guide |

---

## Task 0: Git Cleanup

**Files:** none (git operations only)

- [ ] **Stage all pending deletes and commit**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest"
git add -A
git commit -m "chore: remove old KLC Invoice Generator implementation"
```

Expected output: commit hash with summary of deleted files.

> Note: This removes files from the working tree. Old commits still exist in git history. If the user wants full history rewrite (`git filter-repo`), that requires a separate explicit request.

---

## Task 1: Scaffold

**Files:**
- Create: `KLC Invoice Generator/requirements.txt`
- Create: `KLC Invoice Generator/.gitignore`
- Create: `KLC Invoice Generator/logic.py` (stub)
- Create: `KLC Invoice Generator/sheets.py` (stub)
- Create: `KLC Invoice Generator/app.py` (stub)
- Create: `KLC Invoice Generator/tests/__init__.py`
- Create: `KLC Invoice Generator/tests/test_logic.py` (stub)

- [ ] **Create the directory structure**

```bash
mkdir -p "/Users/micahmiyashiro/Desktop/ClaudeCodeTest/KLC Invoice Generator/tests"
```

- [ ] **Write `requirements.txt`**

```
gspread>=6.0.0
google-auth-oauthlib>=1.2.0
google-api-python-client>=2.100.0
```

Save to: `KLC Invoice Generator/requirements.txt`

- [ ] **Write `.gitignore`**

```
token.json
credentials.json
__pycache__/
*.pyc
*.pyo
.DS_Store
```

Save to: `KLC Invoice Generator/.gitignore`

- [ ] **Write stub `logic.py`**

```python
def suggest_prefix(company_name: str) -> str:
    raise NotImplementedError

def next_invoice_number(filenames: list[str], prefix: str) -> str:
    raise NotImplementedError
```

Save to: `KLC Invoice Generator/logic.py`

- [ ] **Write stub `sheets.py`**

```python
def authenticate():
    raise NotImplementedError

def search_invoices(drive, prefix: str) -> list[dict]:
    raise NotImplementedError

def search_template(drive) -> dict | None:
    raise NotImplementedError

def copy_invoice(drive, source_id: str, new_name: str, folder_id: str) -> str:
    raise NotImplementedError

def write_invoice_cells(gc, sheet_id: str, data: dict) -> None:
    raise NotImplementedError

def export_pdf(creds, file_id: str, dest_path: str) -> None:
    raise NotImplementedError

def create_invoice(data: dict) -> tuple[str, str]:
    raise NotImplementedError
```

Save to: `KLC Invoice Generator/sheets.py`

- [ ] **Write stub `app.py`**

```python
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    root.title("KLC Invoice Generator")
    root.mainloop()
```

Save to: `KLC Invoice Generator/app.py`

- [ ] **Create empty `tests/__init__.py`**

Empty file at: `KLC Invoice Generator/tests/__init__.py`

- [ ] **Write stub `tests/test_logic.py`**

```python
# tests filled in during Task 2 and Task 3
```

Save to: `KLC Invoice Generator/tests/test_logic.py`

- [ ] **Install dependencies**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest/KLC Invoice Generator"
pip install -r requirements.txt
```

- [ ] **Commit scaffold**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest"
git add "KLC Invoice Generator/"
git commit -m "chore: scaffold KLC Invoice Generator"
```

---

## Task 2: suggest_prefix — TDD

**Files:**
- Modify: `KLC Invoice Generator/tests/test_logic.py`
- Modify: `KLC Invoice Generator/logic.py`

- [ ] **Write the failing tests for suggest_prefix**

Replace `KLC Invoice Generator/tests/test_logic.py` with:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from logic import suggest_prefix, next_invoice_number


class TestSuggestPrefix:
    def test_single_word_truncates_to_four(self):
        assert suggest_prefix("Umauma") == "UMAU"

    def test_multi_word_uses_first_word(self):
        assert suggest_prefix("Koolau Laser Creations") == "KOOL"

    def test_short_name_no_padding(self):
        assert suggest_prefix("AB") == "AB"

    def test_empty_string_returns_empty(self):
        assert suggest_prefix("") == ""

    def test_already_uppercase(self):
        assert suggest_prefix("ACME Corp") == "ACME"

    def test_leading_whitespace_stripped(self):
        assert suggest_prefix("  Umauma") == "UMAU"

    def test_exactly_four_chars(self):
        assert suggest_prefix("ABCD Extra") == "ABCD"
```

- [ ] **Run tests and confirm they fail**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest"
python -m pytest "KLC Invoice Generator/tests/test_logic.py::TestSuggestPrefix" -v
```

Expected: `NotImplementedError` on all 7 tests — FAILED.

- [ ] **Implement suggest_prefix in logic.py**

```python
import re


def suggest_prefix(company_name: str) -> str:
    words = company_name.strip().split()
    if not words:
        return ""
    return words[0].upper()[:4]


def next_invoice_number(filenames: list[str], prefix: str) -> str:
    raise NotImplementedError
```

- [ ] **Run tests and confirm they pass**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest"
python -m pytest "KLC Invoice Generator/tests/test_logic.py::TestSuggestPrefix" -v
```

Expected: 7 PASSED.

- [ ] **Commit**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest"
git add "KLC Invoice Generator/logic.py" "KLC Invoice Generator/tests/test_logic.py"
git commit -m "feat: implement suggest_prefix with tests"
```

---

## Task 3: next_invoice_number — TDD

**Files:**
- Modify: `KLC Invoice Generator/tests/test_logic.py`
- Modify: `KLC Invoice Generator/logic.py`

- [ ] **Append the failing tests for next_invoice_number**

Add to `KLC Invoice Generator/tests/test_logic.py` (after `TestSuggestPrefix`):

```python
class TestNextInvoiceNumber:
    def test_no_prior_invoices_starts_at_001(self):
        assert next_invoice_number([], "U") == "U001"

    def test_single_prior_invoice_increments(self):
        assert next_invoice_number(["Invoice U015"], "U") == "U016"

    def test_multiple_picks_max(self):
        files = ["Invoice U010", "Invoice U015", "Invoice U012"]
        assert next_invoice_number(files, "U") == "U016"

    def test_ignores_other_prefixes(self):
        files = ["Invoice U015", "Invoice K003"]
        assert next_invoice_number(files, "U") == "U016"

    def test_case_insensitive_match(self):
        assert next_invoice_number(["invoice u015"], "U") == "U016"

    def test_pads_to_three_digits(self):
        assert next_invoice_number(["Invoice U099"], "U") == "U100"

    def test_prefix_in_number_part_not_matched(self):
        # "Invoice UA001" should not match prefix "U"
        assert next_invoice_number(["Invoice UA001"], "U") == "U001"

    def test_four_char_prefix(self):
        assert next_invoice_number(["Invoice KOOL003"], "KOOL") == "KOOL004"
```

- [ ] **Run tests and confirm new ones fail**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest"
python -m pytest "KLC Invoice Generator/tests/test_logic.py::TestNextInvoiceNumber" -v
```

Expected: `NotImplementedError` — all 8 FAILED.

- [ ] **Implement next_invoice_number in logic.py**

Replace `KLC Invoice Generator/logic.py` with:

```python
import re


def suggest_prefix(company_name: str) -> str:
    words = company_name.strip().split()
    if not words:
        return ""
    return words[0].upper()[:4]


def next_invoice_number(filenames: list[str], prefix: str) -> str:
    pattern = re.compile(
        rf'^Invoice {re.escape(prefix)}(\d+)$', re.IGNORECASE
    )
    numbers = []
    for name in filenames:
        m = pattern.match(name.strip())
        if m:
            numbers.append(int(m.group(1)))
    next_num = (max(numbers) + 1) if numbers else 1
    return f"{prefix}{next_num:03d}"
```

- [ ] **Run all logic tests and confirm all pass**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest"
python -m pytest "KLC Invoice Generator/tests/" -v
```

Expected: 15 PASSED (7 + 8).

- [ ] **Commit**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest"
git add "KLC Invoice Generator/logic.py" "KLC Invoice Generator/tests/test_logic.py"
git commit -m "feat: implement next_invoice_number with tests"
```

---

## Task 4: Google Auth + Drive Search

**Files:**
- Modify: `KLC Invoice Generator/sheets.py`

> **Prerequisite:** `credentials.json` must be in `KLC Invoice Generator/` before manual testing. See `SETUP.md` (written in Task 9) for how to obtain it.

- [ ] **Replace sheets.py with auth + search implementation**

```python
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
    raise NotImplementedError


def write_invoice_cells(gc, sheet_id: str, data: dict) -> None:
    raise NotImplementedError


def export_pdf(creds, file_id: str, dest_path: str) -> None:
    raise NotImplementedError


def create_invoice(data: dict) -> tuple[str, str]:
    raise NotImplementedError
```

- [ ] **Manual smoke test (requires credentials.json)**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest/KLC Invoice Generator"
python - <<'EOF'
import sheets
gc, drive, creds = sheets.authenticate()
print("Auth OK")
results = sheets.search_invoices(drive, "U")
print(f"Found {len(results)} invoices matching prefix U:")
for f in results:
    print(f"  {f['name']} ({f['id']})")
template = sheets.search_template(drive)
print(f"Template: {template['name'] if template else 'NOT FOUND'}")
EOF
```

Expected: "Auth OK", list of matching Drive files, and template found.

- [ ] **Commit**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest"
git add "KLC Invoice Generator/sheets.py"
git commit -m "feat: add Google auth and Drive search"
```

---

## Task 5: Sheet Copy + Cell Write

**Files:**
- Modify: `KLC Invoice Generator/sheets.py`

- [ ] **Replace copy_invoice and write_invoice_cells stubs with implementations**

In `KLC Invoice Generator/sheets.py`, replace the two `raise NotImplementedError` stubs for `copy_invoice` and `write_invoice_cells`:

```python
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

    ws.batch_update(updates, value_input_option="USER_ENTERED")
```

- [ ] **Manual test: copy + write (requires credentials.json and a real invoice in Drive)**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest/KLC Invoice Generator"
python - <<'EOF'
import sheets

gc, drive, creds = sheets.authenticate()
existing = sheets.search_invoices(drive, "U")
if not existing:
    print("No existing U-prefix invoices found — run this after Task 4 smoke test passes")
else:
    source = existing[0]
    folder_id = source["parents"][0]
    new_id = sheets.copy_invoice(drive, source["id"], "Invoice TEST_DELETE_ME", folder_id)
    print(f"Copied to: https://docs.google.com/spreadsheets/d/{new_id}")

    test_data = {
        "client_name": "Test Client",
        "invoice_number": "TEST001",
        "project": "Test Project",
        "due_date": "6/6/2026",
        "date_submitted": "5/7/2026",
        "line_items": [
            {"desc": "Design Work", "qty": 2, "price": 150.0, "total": 300.0},
            {"desc": "Revisions",   "qty": 1, "price": 50.0,  "total": 50.0},
        ],
        "notes": ["Thank you for your business!"],
        "adjustments": 0.0,
    }
    sheets.write_invoice_cells(gc, new_id, test_data)
    print("Cells written. Open the sheet above to verify layout.")
    print("Delete 'Invoice TEST_DELETE_ME' from Drive when done.")
EOF
```

Expected: URL printed. Open it and confirm all cells are in the right positions.

> **If cell positions are wrong:** Update the constants at the top of `sheets.py` (`CELL_DATE_SUBMITTED`, `LINE_ITEM_START_ROW`, etc.) to match the actual template layout, then re-run.

- [ ] **Commit**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest"
git add "KLC Invoice Generator/sheets.py"
git commit -m "feat: add sheet copy and cell write"
```

---

## Task 6: PDF Export

**Files:**
- Modify: `KLC Invoice Generator/sheets.py`

- [ ] **Replace export_pdf stub with implementation**

In `KLC Invoice Generator/sheets.py`, replace the `export_pdf` stub:

```python
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
```

- [ ] **Manual test: export PDF (requires a test sheet ID from Task 5)**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest/KLC Invoice Generator"
python - <<'EOF'
import sheets
from pathlib import Path

gc, drive, creds = sheets.authenticate()
# Replace with the sheet ID from the TEST_DELETE_ME copy made in Task 5
TEST_SHEET_ID = "PASTE_SHEET_ID_HERE"
dest = str(Path.home() / "Desktop" / "Invoice_TEST.pdf")
sheets.export_pdf(creds, TEST_SHEET_ID, dest)
print(f"PDF exported to: {dest}")
EOF
```

Expected: PDF appears on Desktop and opens automatically in Preview.

- [ ] **Commit**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest"
git add "KLC Invoice Generator/sheets.py"
git commit -m "feat: add PDF export to Desktop"
```

---

## Task 7: create_invoice Orchestrator

**Files:**
- Modify: `KLC Invoice Generator/sheets.py`

- [ ] **Replace create_invoice stub with full orchestration**

In `KLC Invoice Generator/sheets.py`, replace the `create_invoice` stub:

```python
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
```

- [ ] **Run all unit tests to confirm no regressions**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest"
python -m pytest "KLC Invoice Generator/tests/" -v
```

Expected: 15 PASSED.

- [ ] **Commit**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest"
git add "KLC Invoice Generator/sheets.py"
git commit -m "feat: add create_invoice orchestrator"
```

---

## Task 8: Full tkinter UI

**Files:**
- Modify: `KLC Invoice Generator/app.py`

- [ ] **Replace app.py with full implementation**

```python
import tkinter as tk
from tkinter import messagebox
from datetime import date, timedelta
import threading

BG = "#F5F0E8"
PRIMARY = "#2D5016"
ACCENT = "#6B4226"
ERROR_COLOR = "#CC3333"
WHITE = "#FFFFFF"
LIGHT_BG = "#E8E0D0"
FONT_LABEL = ("Helvetica", 11)
FONT_ENTRY = ("Helvetica", 11)
FONT_BOLD = ("Helvetica", 12, "bold")
FONT_FOOTER = ("Helvetica", 12)


class InvoiceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KLC Invoice Generator")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.line_items: list[dict] = []
        self._build_ui()
        self._reset_form()

    # ------------------------------------------------------------------ build

    def _build_ui(self):
        outer = tk.Frame(self, bg=BG, padx=20, pady=20)
        outer.pack(fill="both", expand=True)

        # Client Info
        self._section_label(outer, "Client Info")
        info = tk.Frame(outer, bg=BG)
        info.pack(fill="x", pady=(4, 12))
        self.company_var = tk.StringVar()
        self.prefix_var = tk.StringVar()
        self.project_var = tk.StringVar()
        self.due_var = tk.StringVar()
        self._field(info, "Company Name", self.company_var, 0)
        self._field(info, "Invoice Prefix", self.prefix_var, 1)
        self._field(info, "Project", self.project_var, 2)
        self._field(info, "Due Date (M/D/YYYY)", self.due_var, 3)
        self.company_var.trace_add("write", self._on_company_change)

        # Line Items
        self._section_label(outer, "Line Items")
        header = tk.Frame(outer, bg=BG)
        header.pack(fill="x")
        for text, width in [("Description", 28), ("Qty", 5), ("Unit Price", 8), ("Total", 8)]:
            tk.Label(header, text=text, font=("Helvetica", 10, "bold"), bg=BG,
                     fg=PRIMARY, width=width, anchor="w").pack(side="left", padx=(0, 4))

        self.items_frame = tk.Frame(outer, bg=BG)
        self.items_frame.pack(fill="x")

        btn_row = tk.Frame(outer, bg=BG)
        btn_row.pack(fill="x", pady=(4, 12))
        tk.Button(btn_row, text="+ Add Item", bg=LIGHT_BG, fg=PRIMARY,
                  font=FONT_LABEL, bd=0, padx=10, pady=4,
                  command=self._add_item).pack(side="left", padx=(0, 8))
        tk.Button(btn_row, text="+ Add Discount", bg=LIGHT_BG, fg=ACCENT,
                  font=FONT_LABEL, bd=0, padx=10, pady=4,
                  command=self._add_discount).pack(side="left")

        # Adjustments & Notes
        self._section_label(outer, "Adjustments & Notes")
        adj_frame = tk.Frame(outer, bg=BG)
        adj_frame.pack(fill="x", pady=(4, 12))
        self.adj_var = tk.StringVar(value="0.00")
        self._field(adj_frame, "Adjustments ($)", self.adj_var, 0)
        self.adj_var.trace_add("write", lambda *_: self._update_totals())
        tk.Label(adj_frame, text="Notes", font=FONT_LABEL, bg=BG,
                 fg=PRIMARY).grid(row=1, column=0, sticky="nw", pady=(4, 0))
        self.notes_text = tk.Text(adj_frame, height=3, width=50, font=FONT_ENTRY,
                                   bg=WHITE, relief="solid", bd=1)
        self.notes_text.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(4, 0))

        # Footer bar
        footer = tk.Frame(self, bg=PRIMARY, pady=12, padx=20)
        footer.pack(fill="x", side="bottom")
        self.subtotal_label = tk.Label(footer, text="Subtotal: $0.00",
                                        fg=WHITE, bg=PRIMARY, font=FONT_FOOTER)
        self.subtotal_label.pack(side="left", padx=(0, 20))
        self.total_label = tk.Label(footer, text="Total: $0.00",
                                     fg=WHITE, bg=PRIMARY, font=FONT_FOOTER)
        self.total_label.pack(side="left")
        tk.Button(footer, text="Clear", bg=LIGHT_BG, fg=PRIMARY, font=FONT_BOLD,
                  bd=0, padx=14, pady=6,
                  command=self._reset_form).pack(side="right", padx=(8, 0))
        self.gen_btn = tk.Button(footer, text="Generate Invoice", bg=ACCENT, fg=WHITE,
                                  font=FONT_BOLD, bd=0, padx=14, pady=6,
                                  command=self._generate)
        self.gen_btn.pack(side="right")

    def _section_label(self, parent, text: str):
        tk.Label(parent, text=text, font=FONT_BOLD, bg=BG,
                 fg=PRIMARY).pack(anchor="w", pady=(8, 2))

    def _field(self, parent, label: str, var: tk.StringVar, row: int):
        tk.Label(parent, text=label, font=FONT_LABEL, bg=BG,
                 fg=PRIMARY).grid(row=row, column=0, sticky="w", pady=2)
        tk.Entry(parent, textvariable=var, font=FONT_ENTRY, bg=WHITE,
                 relief="solid", bd=1, width=30).grid(
            row=row, column=1, sticky="w", padx=(8, 0), pady=2)

    # --------------------------------------------------------------- behavior

    def _on_company_change(self, *_):
        name = self.company_var.get().strip()
        if not name:
            return
        first = name.split()[0].upper()[:4]
        self.prefix_var.set(first)

    def _add_item(self, desc: str = "", qty: str = "1",
                  price: str = "0.00", discount: bool = False):
        row_frame = tk.Frame(self.items_frame, bg=BG)
        row_frame.pack(fill="x", pady=2)

        desc_var = tk.StringVar(value="Discount" if discount else desc)
        qty_var = tk.StringVar(value=qty)
        price_var = tk.StringVar(value="-0.00" if discount else price)
        total_var = tk.StringVar(value="$0.00")

        tk.Entry(row_frame, textvariable=desc_var, font=FONT_ENTRY, bg=WHITE,
                 relief="solid", bd=1, width=28).pack(side="left", padx=(0, 4))
        tk.Entry(row_frame, textvariable=qty_var, font=FONT_ENTRY, bg=WHITE,
                 relief="solid", bd=1, width=5).pack(side="left", padx=(0, 4))
        tk.Entry(row_frame, textvariable=price_var, font=FONT_ENTRY, bg=WHITE,
                 relief="solid", bd=1, width=8).pack(side="left", padx=(0, 4))
        tk.Label(row_frame, textvariable=total_var, font=FONT_ENTRY, bg=BG,
                 fg=PRIMARY, width=8, anchor="w").pack(side="left", padx=(0, 4))

        item = {
            "frame": row_frame,
            "desc": desc_var,
            "qty": qty_var,
            "price": price_var,
            "total": total_var,
        }
        self.line_items.append(item)

        def delete_row():
            if len(self.line_items) <= 1:
                return
            row_frame.destroy()
            self.line_items.remove(item)
            self._update_totals()

        tk.Button(row_frame, text="✕", bg=BG, fg=ERROR_COLOR, font=FONT_LABEL,
                  bd=0, command=delete_row).pack(side="left")

        for v in (desc_var, qty_var, price_var):
            v.trace_add("write", lambda *_: self._update_totals())
        self._update_totals()

    def _add_discount(self):
        self._add_item(discount=True)

    def _update_totals(self):
        subtotal = 0.0
        for item in self.line_items:
            try:
                total = float(item["qty"].get()) * float(item["price"].get())
            except ValueError:
                total = 0.0
            item["total"].set(f"${total:.2f}")
            subtotal += total
        try:
            adj = float(self.adj_var.get())
        except ValueError:
            adj = 0.0
        grand_total = subtotal + adj
        self.subtotal_label.config(text=f"Subtotal: ${subtotal:.2f}")
        self.total_label.config(text=f"Total: ${grand_total:.2f}")

    def _reset_form(self):
        self.company_var.set("")
        self.prefix_var.set("")
        self.project_var.set("")
        self.due_var.set(
            (date.today() + timedelta(days=30)).strftime("%-m/%-d/%Y")
        )
        self.adj_var.set("0.00")
        for item in list(self.line_items):
            item["frame"].destroy()
        self.line_items.clear()
        if hasattr(self, "notes_text"):
            self.notes_text.delete("1.0", "end")
        self._add_item()

    def _collect_data(self) -> dict | None:
        company = self.company_var.get().strip()
        prefix = self.prefix_var.get().strip().upper()
        project = self.project_var.get().strip()
        due = self.due_var.get().strip()

        if not all([company, prefix, project, due]):
            messagebox.showerror(
                "Missing Fields",
                "Company Name, Invoice Prefix, Project, and Due Date are required."
            )
            return None

        items = []
        for item in self.line_items:
            try:
                qty = float(item["qty"].get())
                price = float(item["price"].get())
            except ValueError:
                messagebox.showerror("Invalid Input",
                                      "Qty and Unit Price must be numbers.")
                return None
            items.append({
                "desc": item["desc"].get(),
                "qty": qty,
                "price": price,
                "total": round(qty * price, 2),
            })

        try:
            adj = float(self.adj_var.get())
        except ValueError:
            adj = 0.0

        notes_raw = self.notes_text.get("1.0", "end-1c")
        notes = [line for line in notes_raw.split("\n")[:3]]

        return {
            "client_name": company,
            "prefix": prefix,
            "project": project,
            "due_date": due,
            "date_submitted": date.today().strftime("%-m/%-d/%Y"),
            "line_items": items,
            "adjustments": adj,
            "notes": notes,
        }

    def _generate(self):
        data = self._collect_data()
        if data is None:
            return
        self.gen_btn.config(state="disabled", text="Generating…")

        def run():
            try:
                import sheets
                url, pdf = sheets.create_invoice(data)
                self.after(0, lambda: self._on_success(url, pdf))
            except Exception as exc:
                self.after(0, lambda: self._on_error(str(exc)))

        threading.Thread(target=run, daemon=True).start()

    def _on_success(self, url: str, pdf: str):
        self.gen_btn.config(state="normal", text="Generate Invoice")
        messagebox.showinfo(
            "Invoice Created",
            f"Google Sheet:\n{url}\n\nPDF saved to:\n{pdf}"
        )

    def _on_error(self, msg: str):
        self.gen_btn.config(state="normal", text="Generate Invoice")
        messagebox.showerror("Error", msg)


if __name__ == "__main__":
    InvoiceApp().mainloop()
```

- [ ] **Launch the app and verify it renders correctly**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest/KLC Invoice Generator"
python app.py
```

Manual checks:
- All four sections visible (Client Info, Line Items, Adjustments & Notes, footer)
- Typing a company name auto-fills the prefix field
- `+ Add Item` appends a row; `✕` removes it (cannot remove last row)
- `+ Add Discount` appends a row with "Discount" and "-0.00"
- Editing qty/price updates the Total column and footer totals live
- `Clear` resets the form

- [ ] **Run unit tests to confirm no regressions**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest"
python -m pytest "KLC Invoice Generator/tests/" -v
```

Expected: 15 PASSED.

- [ ] **Commit**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest"
git add "KLC Invoice Generator/app.py"
git commit -m "feat: build full tkinter invoice form UI"
```

---

## Task 9: SETUP.md + End-to-End Test

**Files:**
- Create: `KLC Invoice Generator/SETUP.md`

- [ ] **Write SETUP.md**

```markdown
# KLC Invoice Generator — Setup

Follow these steps once before using the app for the first time.

## 1. Enable Google APIs

1. Go to https://console.cloud.google.com/
2. Create a new project (or select an existing one)
3. In the left menu: **APIs & Services → Library**
4. Search for and enable **Google Sheets API**
5. Search for and enable **Google Drive API**

## 2. Create OAuth2 Credentials

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth client ID**
3. Application type: **Desktop app**
4. Name it anything (e.g., "KLC Invoice Generator")
5. Click **Create**, then **Download JSON**
6. Rename the downloaded file to `credentials.json`
7. Move it into this folder (`KLC Invoice Generator/`)

> `credentials.json` is in `.gitignore` — it will not be committed.

## 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 4. Create the Invoice Template in Google Drive

1. Open Google Drive
2. Create a new Google Sheet named exactly: `Invoice TEMPLATE`
3. Copy your existing invoice layout into it (or design from scratch)
4. Leave data cells blank — the app will fill them in

The template must be in a Google Drive folder (not "My Drive" root if possible).
The app will copy this template for any client that has no prior invoices.

## 5. Run the App

```bash
python app.py
```

On first run, a browser window will open asking you to authorize the app.
After authorizing, a `token.json` file is saved locally — future runs skip the browser.

> `token.json` is in `.gitignore` — it will not be committed.

## Troubleshooting

**"No 'Invoice TEMPLATE' found"** — Check that you created a sheet named exactly `Invoice TEMPLATE` in Drive and it is not in the Trash.

**"credentials.json not found"** — Make sure you downloaded and renamed the file correctly, and placed it in the `KLC Invoice Generator/` folder.

**Wrong cells filled** — The cell positions in `sheets.py` (constants at the top) were set based on the original invoice layout. If your template uses different rows/columns, update those constants.
```

- [ ] **End-to-end test (requires credentials.json and Invoice TEMPLATE in Drive)**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest/KLC Invoice Generator"
python app.py
```

Fill in the form:
- Company: `Umauma` (prefix should auto-fill as `UMAU`)
- Project: `E2E Test`
- Due Date: leave default
- Add 2 line items with prices
- Click **Generate Invoice**

Verify:
1. A progress indicator appears on the button during generation
2. A success dialog shows the Google Sheet URL and PDF path
3. New file appears in Google Drive: `Invoice UMAU001` (or next number)
4. PDF appears on Desktop and auto-opens
5. Open the Google Sheet — all fields should be in the correct cells

- [ ] **Commit**

```bash
cd "/Users/micahmiyashiro/Desktop/ClaudeCodeTest"
git add "KLC Invoice Generator/SETUP.md"
git commit -m "docs: add SETUP.md for KLC Invoice Generator"
```

- [ ] **Final: push to GitHub**

```bash
git push origin master
```
