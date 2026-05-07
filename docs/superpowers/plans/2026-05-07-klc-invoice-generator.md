# KLC Invoice Generator — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python/tkinter desktop app that fills an invoice form, creates a new Google Sheets invoice in Drive (matching the existing U010–U015 format), exports it as a PDF to `~/Desktop`, and auto-opens it.

**Architecture:** Pure-logic functions (prefix suggestion, invoice numbering) are unit-tested independently. A `sheets.py` module owns all Google API calls (auth, Drive search, sheet copy, cell write, PDF export). `app.py` contains only the tkinter UI and wires it to `sheets.py` on form submit.

**Tech Stack:** Python 3, tkinter (stdlib), gspread 6.x, google-auth-oauthlib, google-api-python-client

---

## File Map

| File | Responsibility |
|---|---|
| `KLC Invoice Generator/app.py` | tkinter GUI, form state, calls `sheets.py` on Generate |
| `KLC Invoice Generator/sheets.py` | All Google API logic: auth, Drive search, copy, write, PDF export |
| `KLC Invoice Generator/tests/test_logic.py` | Unit tests for pure logic functions |
| `KLC Invoice Generator/requirements.txt` | Python dependencies |
| `KLC Invoice Generator/SETUP.md` | One-time OAuth2 + template setup guide |
| `KLC Invoice Generator/.gitignore` | Ignores `credentials.json` and `token.json` |

---

### Task 1: Scaffold the project

**Files:**
- Create: `KLC Invoice Generator/requirements.txt`
- Create: `KLC Invoice Generator/.gitignore`
- Create: `KLC Invoice Generator/sheets.py` (stub)
- Create: `KLC Invoice Generator/app.py` (stub)
- Create: `KLC Invoice Generator/tests/__init__.py`

- [ ] **Step 1: Create requirements.txt**

Create `KLC Invoice Generator/requirements.txt`:
```
gspread>=6.0.0
google-auth-oauthlib>=1.2.0
google-api-python-client>=2.100.0
```

- [ ] **Step 2: Create .gitignore**

Create `KLC Invoice Generator/.gitignore`:
```
credentials.json
token.json
__pycache__/
*.pyc
.DS_Store
```

- [ ] **Step 3: Create stub sheets.py**

Create `KLC Invoice Generator/sheets.py`:
```python
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
```

- [ ] **Step 4: Create stub app.py**

Create `KLC Invoice Generator/app.py`:
```python
"""KLC Invoice Generator — tkinter UI."""
import tkinter as tk

if __name__ == '__main__':
    root = tk.Tk()
    root.title('KLC Invoice Generator')
    root.mainloop()
```

- [ ] **Step 5: Create tests directory**

Create `KLC Invoice Generator/tests/__init__.py` as an empty file.

- [ ] **Step 6: Install dependencies**

```bash
cd "KLC Invoice Generator" && pip install -r requirements.txt
```

Expected: all packages install without errors.

- [ ] **Step 7: Commit**

```bash
git add "KLC Invoice Generator/"
git commit -m "feat: scaffold KLC Invoice Generator"
```

---

### Task 2: Pure logic — prefix suggestion and invoice numbering (TDD)

**Files:**
- Modify: `KLC Invoice Generator/sheets.py`
- Create: `KLC Invoice Generator/tests/test_logic.py`

- [ ] **Step 1: Write failing tests**

Create `KLC Invoice Generator/tests/test_logic.py`:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from sheets import suggest_prefix, next_invoice_number


class TestSuggestPrefix:
    def test_single_word(self):
        assert suggest_prefix('Ukey') == 'UKEY'

    def test_first_word_only(self):
        assert suggest_prefix('Ukey Creation') == 'UKEY'

    def test_max_four_chars(self):
        assert suggest_prefix('Aloha Prints') == 'ALOH'

    def test_pewa(self):
        assert suggest_prefix('PEWA by Pono Potions') == 'PEWA'

    def test_empty_string(self):
        assert suggest_prefix('') == ''

    def test_three_char_word(self):
        assert suggest_prefix('KLC Hawaii') == 'KLC'


class TestNextInvoiceNumber:
    def test_increments_from_existing(self):
        titles = ['Invoice U013', 'Invoice U014', 'Invoice U015']
        assert next_invoice_number(titles, 'U') == 'U016'

    def test_starts_at_001_for_new_prefix(self):
        assert next_invoice_number([], 'X') == 'X001'

    def test_finds_max_not_last(self):
        titles = ['Invoice U015', 'Invoice U012', 'Invoice U009']
        assert next_invoice_number(titles, 'U') == 'U016'

    def test_multi_char_prefix(self):
        titles = ['Invoice PEWA001', 'Invoice PEWA002']
        assert next_invoice_number(titles, 'PEWA') == 'PEWA003'

    def test_ignores_other_prefixes(self):
        titles = ['Invoice U015', 'Invoice PEWA002']
        assert next_invoice_number(titles, 'U') == 'U016'

    def test_zero_pads_to_three_digits(self):
        assert next_invoice_number([], 'ABC') == 'ABC001'
```

- [ ] **Step 2: Run tests — expect failures**

```bash
cd "KLC Invoice Generator" && python -m pytest tests/test_logic.py -v
```

Expected: `AttributeError: module 'sheets' has no attribute 'suggest_prefix'`

- [ ] **Step 3: Implement the two functions in sheets.py**

Add after the constants in `KLC Invoice Generator/sheets.py`:
```python
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
```

- [ ] **Step 4: Run tests — expect all pass**

```bash
cd "KLC Invoice Generator" && python -m pytest tests/test_logic.py -v
```

Expected: all 12 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add "KLC Invoice Generator/sheets.py" "KLC Invoice Generator/tests/test_logic.py"
git commit -m "feat: add invoice numbering and prefix suggestion logic"
```

---

### Task 3: Google Auth

**Files:**
- Modify: `KLC Invoice Generator/sheets.py`

- [ ] **Step 1: Add get_credentials() and get_clients() to sheets.py**

Add after `next_invoice_number()` in `KLC Invoice Generator/sheets.py`:
```python
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
```

- [ ] **Step 2: Smoke-test auth manually**

Add a temporary block at the bottom of `sheets.py` to verify auth works, then remove it after confirming:
```python
if __name__ == '__main__':
    creds = get_credentials()
    gc, drive = get_clients(creds)
    print('Auth OK:', creds.valid)
```

Run: `cd "KLC Invoice Generator" && python sheets.py`

Expected: browser opens for Google consent on first run (sign in as koolaulasercreations@gmail.com, grant access), then prints `Auth OK: True`. `token.json` appears in the folder.

Remove the `if __name__ == '__main__':` block after confirming.

- [ ] **Step 3: Commit**

```bash
git add "KLC Invoice Generator/sheets.py"
git commit -m "feat: add OAuth2 auth flow"
```

---

### Task 4: Drive search — find existing invoices and source file

**Files:**
- Modify: `KLC Invoice Generator/sheets.py`

- [ ] **Step 1: Add Drive search functions to sheets.py**

Add after `get_clients()` in `KLC Invoice Generator/sheets.py`:
```python
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
```

- [ ] **Step 2: Smoke-test Drive search**

Add temporary `__main__` block:
```python
if __name__ == '__main__':
    creds = get_credentials()
    gc, drive = get_clients(creds)
    titles = get_all_invoice_titles(drive)
    print('All invoice titles:', titles)
    fid, parent = find_source_file(drive, 'U')
    print(f'Source for U: file_id={fid}  parent={parent}')
```

Run: `cd "KLC Invoice Generator" && python sheets.py`

Expected: prints list of invoice titles including `Invoice U015`, followed by the file ID and parent folder ID for U. Remove `__main__` block after confirming.

- [ ] **Step 3: Commit**

```bash
git add "KLC Invoice Generator/sheets.py"
git commit -m "feat: add Drive search for invoice source files"
```

---

### Task 5: Map cell positions in the invoice template

Before writing cell data we need to confirm the exact row/column positions of the dynamic fields. This is a one-time discovery step — no permanent code output, just constants to record.

**Files:**
- Modify: `KLC Invoice Generator/sheets.py` (add constants)

- [ ] **Step 1: Run cell inspection script**

Add temporary `__main__` block:
```python
if __name__ == '__main__':
    creds = get_credentials()
    gc, drive = get_clients(creds)
    # Invoice U015 — most recent known-good invoice
    sh = gc.open_by_key('1AK_9hCRRZC16GfZPOG4mZP-hmEbW0rRMh06bxKX3zt0')
    ws = sh.sheet1
    for i, row in enumerate(ws.get_all_values(), start=1):
        if any(c.strip() for c in row):
            print(f'Row {i:02d}: {row}')
```

Run: `cd "KLC Invoice Generator" && python sheets.py`

Read the output carefully. You need the row numbers for:
- Submitted date line (e.g. "Submitted on 4/20/2026")
- Client name (e.g. "Ukey Creation")
- Invoice number (e.g. "U015")
- Project name
- Due date
- First line item row
- Column index (0-based from the list, A=0, B=1, C=2, D=3, E=4, F=5) for Qty, Unit Price, Total, Subtotal label/value

Remove `__main__` block after recording.

- [ ] **Step 2: Add cell constants to sheets.py**

Add after the `SCOPES` / `TOKEN_FILE` constants block, adjusting any addresses that differ from the inspection output:
```python
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
```

- [ ] **Step 3: Commit**

```bash
git add "KLC Invoice Generator/sheets.py"
git commit -m "feat: add verified cell position constants"
```

---

### Task 6: Sheet copy and cell write

**Files:**
- Modify: `KLC Invoice Generator/sheets.py`

- [ ] **Step 1: Add create_invoice_sheet() to sheets.py**

Add after `find_source_file()`:
```python
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
```

- [ ] **Step 2: Smoke-test with a real invoice**

Add temporary `__main__` block:
```python
if __name__ == '__main__':
    creds  = get_credentials()
    gc, drive = get_clients(creds)
    titles = get_all_invoice_titles(drive)
    inv_num = next_invoice_number(titles, 'U')
    form_data = {
        'company_name':   'Ukey Creation',
        'prefix':         'U',
        'project':        'Test Invoice — delete me',
        'due_date':       '6/6/2026',
        'items': [
            {'description': 'Test Item', 'qty': 2, 'unit_price': 5.00, 'total': 10.00},
            {'description': 'Discount',  'qty': 2, 'unit_price': -1.00, 'total': -2.00},
        ],
        'adjustments':    0.0,
        'notes':          'This is a smoke test.',
        'invoice_number': inv_num,
    }
    new_id = create_invoice_sheet(drive, gc, form_data)
    print(f'Created: https://docs.google.com/spreadsheets/d/{new_id}')
```

Run: `cd "KLC Invoice Generator" && python sheets.py`

Open the printed URL. Verify: invoice number, client name, project, line items, subtotal, and total are correct. **Delete the test file from Drive after confirming.** Remove `__main__` block.

- [ ] **Step 3: Commit**

```bash
git add "KLC Invoice Generator/sheets.py"
git commit -m "feat: add create_invoice_sheet with cell write"
```

---

### Task 7: PDF export to Desktop

**Files:**
- Modify: `KLC Invoice Generator/sheets.py`

- [ ] **Step 1: Add export_to_pdf() to sheets.py**

Add after `create_invoice_sheet()`:
```python
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
```

- [ ] **Step 2: Smoke-test PDF export**

Create a fresh test invoice using the smoke test from Task 6, note its spreadsheet ID, then add:
```python
if __name__ == '__main__':
    creds = get_credentials()
    # Replace with the ID of a test invoice you just created
    test_id = 'PASTE_SPREADSHEET_ID_HERE'
    path = export_to_pdf(creds, test_id, 'UTEST')
    print(f'PDF saved to: {path}')
    import os; os.system(f'open "{path}"')
```

Run: `cd "KLC Invoice Generator" && python sheets.py`

Expected: PDF opens on Desktop. Verify it looks like a clean invoice. Delete the test PDF and test Sheet from Drive. Remove `__main__` block.

- [ ] **Step 3: Commit**

```bash
git add "KLC Invoice Generator/sheets.py"
git commit -m "feat: add PDF export to Desktop"
```

---

### Task 8: Full tkinter UI

**Files:**
- Modify: `KLC Invoice Generator/app.py`

- [ ] **Step 1: Replace app.py with the full UI**

Replace the entire contents of `KLC Invoice Generator/app.py` with:
```python
"""KLC Invoice Generator — tkinter UI."""
import tkinter as tk
from tkinter import messagebox
import datetime
import os

import sheets

BG    = '#F5F0E8'
GREEN = '#2D5016'
BROWN = '#6B4226'
RED   = '#CC3333'
WHITE = '#FFFFFF'
LIGHT = '#E8E0D0'


class LineItemRow:
    def __init__(self, frame, on_change, on_delete):
        self.frame = tk.Frame(frame, bg=BG)
        self.frame.pack(fill='x', pady=1)

        self.desc_var  = tk.StringVar()
        self.qty_var   = tk.StringVar(value='1')
        self.price_var = tk.StringVar(value='0.00')
        self.total_var = tk.StringVar(value='$0.00')

        for v in (self.desc_var, self.qty_var, self.price_var):
            v.trace_add('write', lambda *_: on_change())

        tk.Entry(self.frame, textvariable=self.desc_var,  width=32,
                 font=('Helvetica', 10)).pack(side='left', padx=(0, 4))
        tk.Entry(self.frame, textvariable=self.qty_var,   width=6,
                 font=('Helvetica', 10)).pack(side='left', padx=(0, 4))
        tk.Entry(self.frame, textvariable=self.price_var, width=9,
                 font=('Helvetica', 10)).pack(side='left', padx=(0, 4))
        tk.Label(self.frame, textvariable=self.total_var, width=10,
                 bg=LIGHT, font=('Helvetica', 10), anchor='e').pack(side='left', padx=(0, 4))
        tk.Button(self.frame, text='✕', bg=BG, fg=RED, font=('Helvetica', 9),
                  relief='flat', cursor='hand2',
                  command=on_delete).pack(side='left')

    def get_item(self):
        try:
            qty   = float(self.qty_var.get())
            price = float(self.price_var.get())
        except ValueError:
            qty, price = 0.0, 0.0
        total = round(qty * price, 2)
        self.total_var.set(f'${total:,.2f}')
        return {
            'description': self.desc_var.get().strip(),
            'qty':         qty,
            'unit_price':  price,
            'total':       total,
        }

    def destroy(self):
        self.frame.destroy()


class InvoiceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('KLC Invoice Generator')
        self.configure(bg=BG)
        self.resizable(False, False)
        self._item_rows: list = []
        self._creds = None
        self._build_ui()
        self._add_item_row()

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        banner = tk.Frame(self, bg=GREEN, pady=10)
        banner.pack(fill='x')
        tk.Label(banner, text="Ko'olau Laser Creations",
                 font=('Helvetica', 18, 'bold'), bg=GREEN, fg=WHITE).pack()
        tk.Label(banner, text='Invoice Generator',
                 font=('Helvetica', 11), bg=GREEN, fg='#A8C97A').pack()

        main = tk.Frame(self, bg=BG, padx=20, pady=12)
        main.pack(fill='both')

        # Client Info
        self._section(main, 'Client Info')

        r = tk.Frame(main, bg=BG); r.pack(fill='x', pady=2)
        tk.Label(r, text='Company Name:', width=18, anchor='w', bg=BG).pack(side='left')
        self.company_var = tk.StringVar()
        self.company_var.trace_add('write', self._on_company_change)
        tk.Entry(r, textvariable=self.company_var, width=32,
                 font=('Helvetica', 10)).pack(side='left')

        r = tk.Frame(main, bg=BG); r.pack(fill='x', pady=2)
        tk.Label(r, text='Invoice Prefix:', width=18, anchor='w', bg=BG).pack(side='left')
        self.prefix_var = tk.StringVar()
        tk.Entry(r, textvariable=self.prefix_var, width=10,
                 font=('Helvetica', 10)).pack(side='left')

        r = tk.Frame(main, bg=BG); r.pack(fill='x', pady=2)
        tk.Label(r, text='Project:', width=18, anchor='w', bg=BG).pack(side='left')
        self.project_var = tk.StringVar()
        tk.Entry(r, textvariable=self.project_var, width=42,
                 font=('Helvetica', 10)).pack(side='left')

        r = tk.Frame(main, bg=BG); r.pack(fill='x', pady=2)
        tk.Label(r, text='Due Date:', width=18, anchor='w', bg=BG).pack(side='left')
        default_due = (datetime.date.today() + datetime.timedelta(days=30)).strftime('%-m/%-d/%Y')
        self.due_var = tk.StringVar(value=default_due)
        tk.Entry(r, textvariable=self.due_var, width=14,
                 font=('Helvetica', 10)).pack(side='left')

        # Line Items
        self._section(main, 'Line Items')

        hdr = tk.Frame(main, bg=BG); hdr.pack(fill='x')
        for text, w in [('Description', 32), ('Qty', 6), ('Unit Price', 9), ('Total', 10)]:
            tk.Label(hdr, text=text, width=w, anchor='w', bg=BG,
                     font=('Helvetica', 9, 'bold'), fg='#555555').pack(side='left', padx=(0, 4))

        self.items_frame = tk.Frame(main, bg=BG)
        self.items_frame.pack(fill='x')

        btns = tk.Frame(main, bg=BG); btns.pack(fill='x', pady=(4, 0))
        tk.Button(btns, text='+ Add Item', bg=GREEN, fg=WHITE, font=('Helvetica', 9),
                  relief='flat', cursor='hand2', padx=8, pady=3,
                  command=self._add_item_row).pack(side='left', padx=(0, 6))
        tk.Button(btns, text='+ Add Discount', bg=BROWN, fg=WHITE, font=('Helvetica', 9),
                  relief='flat', cursor='hand2', padx=8, pady=3,
                  command=self._add_discount_row).pack(side='left')

        # Adjustments & Notes
        self._section(main, 'Adjustments & Notes')

        r = tk.Frame(main, bg=BG); r.pack(fill='x', pady=2)
        tk.Label(r, text='Adjustments ($):', width=18, anchor='w', bg=BG).pack(side='left')
        self.adj_var = tk.StringVar(value='0.00')
        self.adj_var.trace_add('write', lambda *_: self._update_totals())
        tk.Entry(r, textvariable=self.adj_var, width=10,
                 font=('Helvetica', 10)).pack(side='left')

        tk.Label(main, text='Notes:', anchor='w', bg=BG,
                 font=('Helvetica', 10)).pack(anchor='w', pady=(4, 0))
        self.notes_text = tk.Text(main, width=60, height=3, font=('Helvetica', 10))
        self.notes_text.pack(fill='x', pady=(2, 8))

        # Bottom bar
        bar = tk.Frame(self, bg=GREEN, padx=20, pady=10)
        bar.pack(fill='x')
        self.totals_var = tk.StringVar(value='Subtotal: $0.00   Total: $0.00')
        tk.Label(bar, textvariable=self.totals_var, bg=GREEN, fg=WHITE,
                 font=('Helvetica', 11)).pack(side='left')
        btn_f = tk.Frame(bar, bg=GREEN); btn_f.pack(side='right')
        tk.Button(btn_f, text='Clear', bg='#CCCCCC', fg='#333333',
                  font=('Helvetica', 10), relief='flat', cursor='hand2',
                  padx=10, pady=6, command=self._clear).pack(side='left', padx=(0, 8))
        tk.Button(btn_f, text='Generate Invoice', bg=BROWN, fg=WHITE,
                  font=('Helvetica', 11, 'bold'), relief='flat', cursor='hand2',
                  padx=16, pady=6, command=self._generate).pack(side='left')

    def _section(self, parent, title):
        tk.Label(parent, text=title, font=('Helvetica', 11, 'bold'),
                 bg=BG, fg='#1A1A1A').pack(anchor='w', pady=(12, 2))

    # ── Line Items ────────────────────────────────────────────────────────────

    def _add_item_row(self, description='', unit_price='0.00'):
        row = LineItemRow(
            self.items_frame,
            on_change=self._update_totals,
            on_delete=lambda r=None: self._delete_row(row),
        )
        if description:
            row.desc_var.set(description)
        if unit_price != '0.00':
            row.price_var.set(unit_price)
        self._item_rows.append(row)
        self._update_totals()

    def _add_discount_row(self):
        self._add_item_row(description='Discount', unit_price='-0.00')

    def _delete_row(self, row):
        if len(self._item_rows) <= 1:
            return
        self._item_rows.remove(row)
        row.destroy()
        self._update_totals()

    # ── Live Totals ───────────────────────────────────────────────────────────

    def _update_totals(self):
        subtotal = sum(r.get_item()['total'] for r in self._item_rows)
        try:
            adj = float(self.adj_var.get())
        except ValueError:
            adj = 0.0
        self.totals_var.set(
            f'Subtotal: ${subtotal:,.2f}   Total: ${subtotal + adj:,.2f}'
        )

    # ── Prefix Auto-Suggest ───────────────────────────────────────────────────

    def _on_company_change(self, *_):
        self.prefix_var.set(sheets.suggest_prefix(self.company_var.get()))

    # ── Generate Invoice ──────────────────────────────────────────────────────

    def _generate(self):
        company = self.company_var.get().strip()
        prefix  = self.prefix_var.get().strip().upper()
        project = self.project_var.get().strip()
        due     = self.due_var.get().strip()

        if not company:
            messagebox.showerror('Missing Field', 'Company Name is required.'); return
        if not prefix:
            messagebox.showerror('Missing Field', 'Invoice Prefix is required.'); return
        if not project:
            messagebox.showerror('Missing Field', 'Project is required.'); return

        items = [r.get_item() for r in self._item_rows]
        if not any(item['description'] for item in items):
            messagebox.showerror('Missing Items', 'Add at least one line item.'); return

        try:
            adj = float(self.adj_var.get())
        except ValueError:
            messagebox.showerror('Invalid Input', 'Adjustments must be a number.'); return

        notes = self.notes_text.get('1.0', 'end').strip()

        try:
            if not self._creds or not self._creds.valid:
                self._creds = sheets.get_credentials()
            gc, drive = sheets.get_clients(self._creds)
        except FileNotFoundError as e:
            messagebox.showerror('Setup Required', str(e)); return

        try:
            all_titles     = sheets.get_all_invoice_titles(drive)
            invoice_number = sheets.next_invoice_number(all_titles, prefix)
        except Exception as e:
            messagebox.showerror('Drive Error', f'Could not scan Drive:\n{e}'); return

        subtotal = sum(item['total'] for item in items)
        if not messagebox.askyesno(
            'Confirm Invoice',
            f'Generate Invoice {invoice_number}?\n\n'
            f'Client:  {company}\n'
            f'Project: {project}\n'
            f'Total:   ${subtotal + adj:,.2f}\n\n'
            'PDF will be saved to your Desktop.',
        ):
            return

        form_data = {
            'company_name':   company,
            'prefix':         prefix,
            'project':        project,
            'due_date':       due,
            'items':          items,
            'adjustments':    adj,
            'notes':          notes,
            'invoice_number': invoice_number,
        }
        try:
            sheet_id = sheets.create_invoice_sheet(drive, gc, form_data)
            pdf_path = sheets.export_to_pdf(self._creds, sheet_id, invoice_number)
        except FileNotFoundError as e:
            messagebox.showerror('Template Missing', str(e)); return
        except Exception as e:
            messagebox.showerror('Error', f'Failed to generate invoice:\n{e}'); return

        os.system(f'open "{pdf_path}"')
        messagebox.showinfo('Done', f'Invoice {invoice_number} created!\nPDF saved to Desktop.')

    # ── Clear ─────────────────────────────────────────────────────────────────

    def _clear(self):
        self.company_var.set('')
        self.prefix_var.set('')
        self.project_var.set('')
        self.due_var.set(
            (datetime.date.today() + datetime.timedelta(days=30)).strftime('%-m/%-d/%Y')
        )
        self.adj_var.set('0.00')
        self.notes_text.delete('1.0', 'end')
        for row in list(self._item_rows):
            row.destroy()
        self._item_rows.clear()
        self._add_item_row()


if __name__ == '__main__':
    app = InvoiceApp()
    app.mainloop()
```

- [ ] **Step 2: Launch and verify the UI**

```bash
cd "KLC Invoice Generator" && python app.py
```

Check each of the following manually:
- App opens with the green KLC banner
- Typing in Company Name auto-fills the Prefix field
- `+ Add Item` appends a new blank row
- `+ Add Discount` appends a row with description "Discount" and price "-0.00"
- `✕` removes a row (cannot remove the last remaining row)
- Editing Qty or Unit Price updates Total column and the bottom bar live
- `Clear` resets all fields and leaves one blank item row
- Do NOT click Generate yet (save that for Task 9)

- [ ] **Step 3: Commit**

```bash
git add "KLC Invoice Generator/app.py"
git commit -m "feat: build full tkinter invoice form UI"
```

---

### Task 9: End-to-end test and SETUP.md

**Files:**
- Create: `KLC Invoice Generator/SETUP.md`

- [ ] **Step 1: Full end-to-end test**

Run `python app.py`. Fill in a real invoice:
- Company Name: Ukey Creation  → Prefix auto-fills to UKEY, change it to U
- Project: E2E test run
- Due Date: leave default
- Add one item: description "Test cut", qty 1, unit price 10.00
- Click **Generate Invoice**

Verify all of the following:
1. Confirmation dialog shows the correct next invoice number (e.g. U016)
2. Google Sheet appears in Drive named `Invoice U016`
3. PDF lands on Desktop named `Invoice U016.pdf`
4. PDF opens automatically
5. PDF shows correct client name, project, item, subtotal and total

Delete the test Sheet from Drive and the test PDF from Desktop after confirming.

- [ ] **Step 2: Write SETUP.md**

Create `KLC Invoice Generator/SETUP.md` with the following content (use plain indented blocks instead of fenced code inside this file):

```
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
```

- [ ] **Step 3: Final commit and push**

```bash
git add "KLC Invoice Generator/SETUP.md"
git commit -m "docs: add SETUP.md for KLC Invoice Generator"
git push
```
