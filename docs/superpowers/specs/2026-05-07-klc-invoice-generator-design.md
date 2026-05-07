# KLC Invoice Generator — Design Spec

## Overview

A Python desktop application (tkinter) that lets the user fill in invoice details, then automatically:
1. Copies an existing Google Sheets invoice from Drive (preserving formatting)
2. Writes the new invoice data into the correct cells
3. Exports a PDF to `~/Desktop/` and auto-opens it

---

## Architecture

Three source files with clean boundaries:

| File | Responsibility |
|---|---|
| `app.py` | tkinter UI only — reads form input, calls `sheets.create_invoice(data)` |
| `sheets.py` | All Google API logic — auth, Drive search/copy, Sheets write, PDF export |
| `logic.py` | Pure functions — `suggest_prefix`, `next_invoice_number` — no I/O, unit-tested |

---

## UI Form (tkinter)

**Color scheme:** Background `#F5F0E8`, Primary `#2D5016`, Accent `#6B4226`, Error `#CC3333`

### Sections

**1. Client Info**
| Field | Default | Notes |
|---|---|---|
| Company Name | blank | Auto-suggests Invoice Prefix on keystroke |
| Invoice Prefix | auto-filled | First word uppercased, max 4 chars; fully editable |
| Project | blank | Single line |
| Due Date | Today + 30 days | M/D/YYYY format |

**2. Line Items** — dynamic table
- Columns: Description (wide) | Qty | Unit Price | Total (read-only)
- `+ Add Item` — appends blank row
- `+ Add Discount` — appends row with "Discount" label and `-0.00` price
- `✕` per row — deletes row (cannot delete last row)
- Live total recalculates on every keystroke

**3. Adjustments & Notes**
- Adjustments ($) — added to subtotal for grand total
- Notes — multiline text, up to 3 lines written to sheet

**4. Footer bar** (green)
- Left: live Subtotal + Total
- Right: `Clear` (resets form) + `Generate Invoice` (primary action, disabled during generation)

---

## Invoice Generation Flow

1. **Authenticate** — OAuth2 desktop flow; browser opens once, token cached in `token.json`
2. **Find source file** — Drive search for `Invoice <PREFIX>NNN` files; falls back to `Invoice TEMPLATE` for new clients
3. **Determine invoice number** — parse numeric suffixes from matching filenames, increment max, zero-pad to 3 digits (e.g., U016)
4. **Copy file** — `Drive.files().copy()` preserves all formatting, borders, logos
5. **Write cells** — batch-clear `A7:F50`, then batch-write all fields atomically
6. **Export PDF** — Drive export endpoint → `~/Desktop/Invoice <PREFIX><NNN>.pdf` → auto-opened

### Cell Mapping

| Cell | Field |
|---|---|
| A7 | Date submitted |
| A9 | Client name |
| E9 | Invoice number |
| A11 | Project |
| C11 | Due date |
| A13+ | Line item description (one per row) |
| D13+ | Line item qty |
| E13+ | Line item unit price |
| F13+ | Line item total |
| A(13+N+2)+ | Notes lines |
| Clear range | A7:F50 |

---

## Dependencies

```
gspread>=6.0.0
google-auth-oauthlib>=1.2.0
google-api-python-client>=2.100.0
```

---

## Prefix / Numbering Logic

- **suggest_prefix(company_name):** `company_name.strip().split()[0].upper()[:4]`
- **next_invoice_number(filenames, prefix):** regex `^Invoice <PREFIX>(\d+)$` (case-insensitive), find max numeric suffix, return `<PREFIX><max+1:03d>`. Returns `<PREFIX>001` if no matches.

---

## One-Time Setup (user)

1. Enable Google Sheets API + Google Drive API in Google Cloud Console
2. Create OAuth2 Desktop App credentials, download `credentials.json` into `KLC Invoice Generator/`
3. Create an `Invoice TEMPLATE` spreadsheet in Google Drive (copy of a blank invoice)
4. `pip install -r requirements.txt`
5. `python app.py` — browser opens for auth on first run only
