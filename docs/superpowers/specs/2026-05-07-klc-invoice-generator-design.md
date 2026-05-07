# KLC Invoice Generator — Design Spec
_Date: 2026-05-07_

## Overview

A Python/tkinter desktop app that fills out an invoice form, creates a new Google Sheets invoice in Drive (matching the existing U010–U015 format), exports it as a PDF to `~/Desktop`, and auto-opens the PDF for review.

---

## File Structure

```
KLC Invoice Generator/
├── app.py                  # Main tkinter GUI + orchestration
├── sheets.py               # All Google Drive/Sheets API logic
├── credentials.json        # OAuth2 client credentials (not committed to git)
└── token.json              # Auto-saved OAuth token after first login (not committed to git)
```

**Dependencies:** `gspread`, `google-auth-oauthlib`

---

## Authentication

- OAuth2 Desktop App flow via `google-auth-oauthlib`
- First run: browser opens Google consent screen for `koolaulasercreations@gmail.com`
- Token saved to `token.json`; all subsequent runs are silent
- Required scopes: `https://www.googleapis.com/auth/spreadsheets`, `https://www.googleapis.com/auth/drive`
- `credentials.json` must be placed in the app folder by the user (downloaded from Google Cloud Console)
- A `SETUP.md` file in the app folder walks through the one-time Google Cloud + credentials setup

---

## Form UI

Styled to match the Quote Calculator: dark green (`#2D5016`) banner, cream (`#F5F0E8`) background.

### Client Info Section
| Field | Default | Notes |
|---|---|---|
| Company Name | (blank) | Triggers prefix auto-suggestion on change |
| Invoice Prefix | Auto-suggested | First word of company name, uppercased, max 4 chars; editable |
| Project / Description | (blank) | Single line |
| Due Date | Today + 30 days | Editable (MM/DD/YYYY) |

### Line Items Section
Dynamic table. Each row has: Description (wide) | Qty | Unit Price | Total (read-only, auto-calculated).

- **`+ Add Item`** — appends a blank row
- **`+ Add Discount`** — appends a row with a negative unit price pre-filled as `$0.00` and label `"Discount"`
- Each row has an **`✕`** button to delete it
- At least one item row always present

### Adjustments & Notes Section
| Field | Default |
|---|---|
| Adjustments ($) | 0.00 |
| Notes | (blank, multiline) |

### Bottom Bar
- Live-updating **Subtotal** and **Total** (`Total = Subtotal + Adjustments`)
- **`Generate Invoice`** button (dark green, full width)
- **`Clear`** button (resets form to defaults)

---

## Invoice Numbering Logic

1. Read the Invoice Prefix from the form (e.g. `U`)
2. Search Drive for files titled `Invoice <PREFIX>\d+` (case-insensitive)
3. Parse all numeric suffixes, find the maximum (e.g. `015` from `U015`)
4. Next invoice number = max + 1, zero-padded to 3 digits (e.g. `U016`)
5. If no existing files found for that prefix → start at `001`

**Prefix auto-suggestion:** `first_word(company_name).upper()[:4]`
- `"Ukey Creation"` → `UKEY`
- `"PEWA by Pono Potions"` → `PEWA`
- Always editable by the user before generating

---

## Sheet Creation & PDF Export Flow

### For a known company (prefix exists in Drive)
1. Find the highest-numbered `Invoice <PREFIX>NNN` file in Drive (by parsing the numeric suffix, not by creation date)
2. Copy it using the Drive `files.copy` API (preserves all formatting)
3. Save the copy to the same Drive folder as the source file
4. Clear the data cells (submitted date, client, invoice #, project, due date, line items, notes, subtotal, adjustments, total)
5. Write new values to the appropriate cells
6. Rename the file to `Invoice <PREFIX>NNN` (e.g. `Invoice U016`)

### For a new company (no prior invoices)
1. Find the master template file titled `Invoice TEMPLATE` in Drive (searched by exact title)
2. Copy it to the same folder as the template file and fill it the same way
3. The `Invoice TEMPLATE` file is created once during initial setup and lives in the invoices Drive folder

### Cell mapping (based on existing invoice structure)
The invoice layout occupies a single sheet with this row structure:
- Rows 1–7: KLC header + "INVOICE" + submitted date (static / date-updated)
- Rows 8–11: Invoice for / Payable to / Invoice # / Project / Due date (client-specific)
- Row 12: Column headers (Description, Qty, Unit price, Total price)
- Rows 13–N: Line items (variable length)
- Rows N+1–N+3: Notes + Subtotal / Adjustments / Total block

Because line item count varies, the app clears rows 13 onward before writing new data rather than trying to insert/delete rows. The `Invoice TEMPLATE` must have enough blank rows buffered below row 12 to accommodate any number of items (20 blank rows is sufficient).

### PDF Export & Desktop Save
1. Use the Drive export endpoint: `GET /drive/v3/files/{id}/export?mimeType=application/pdf`
2. Stream response to `~/Desktop/Invoice <PREFIX><NNN>.pdf` (matching the Sheet title format)
3. Call `os.system(f'open "{pdf_path}"')` to auto-open in the default PDF viewer

---

## Error Handling

- **Missing `credentials.json`**: Show a dialog pointing to `SETUP.md`
- **Drive API failure**: Show error dialog with the API message; do not create a partial invoice
- **No `Invoice TEMPLATE` for new company**: Show a dialog explaining the user must create the template file in Drive
- **Invalid form input** (non-numeric qty/price, empty company name): Highlight the offending field and show an inline error before any API calls

---

## Setup Artifacts

A `SETUP.md` file in the app folder covers:
1. Creating a Google Cloud project
2. Enabling Sheets API + Drive API
3. Creating OAuth2 Desktop App credentials and downloading `credentials.json`
4. Creating the `Invoice TEMPLATE` spreadsheet in Drive
5. Running `pip install gspread google-auth-oauthlib` and launching with `python app.py`

---

## Out of Scope

- Email sending
- Multi-sheet invoices
- Payment tracking
- Integration with the Quote Calculator
