import json
import subprocess
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, black

_DIR = Path(__file__).parent
INVOICES_DB = _DIR / "invoices.json"
LOGO_PATH = _DIR / "logo.png"

PRIMARY    = HexColor("#2D5016")
ACCENT     = HexColor("#6B4226")
LIGHT_GRAY = HexColor("#EDEAE4")
ROW_ALT    = HexColor("#F7F5F1")
MID_GRAY   = HexColor("#888888")

BUSINESS_NAME = "Ko'olau Laser Creations"
BUSINESS_INFO = [
    "47-148 Lile Place",
    "Kaneohe, HI 96744",
    "(808) 782-2479",
    "koolaulasercreations@gmail.com",
]
PAYABLE_TO = "Ko'olau Laser Creations"

PAGE_W, PAGE_H = letter   # 612 x 792
L_MARGIN = 50
R_MARGIN = PAGE_W - 50
CONTENT_W = R_MARGIN - L_MARGIN


def _load_db() -> dict:
    if INVOICES_DB.exists():
        try:
            return json.loads(INVOICES_DB.read_text())
        except Exception:
            pass
    return {}


def _next_invoice_number(prefix: str) -> tuple[str, int]:
    db = _load_db()
    num = db.get(prefix.upper(), 0) + 1
    return f"{prefix.upper()}{num:03d}", num


def _record_invoice(prefix: str, num: int) -> None:
    db = _load_db()
    db[prefix.upper()] = num
    INVOICES_DB.write_text(json.dumps(db, indent=2))


def _draw_invoice(c: canvas.Canvas, data: dict, invoice_num: str) -> None:
    # ── Top green bar ──
    c.setFillColor(PRIMARY)
    c.rect(0, PAGE_H - 6, PAGE_W, 6, fill=1, stroke=0)

    # ── Logo ──
    if LOGO_PATH.exists():
        logo_size = 80
        c.drawImage(
            str(LOGO_PATH),
            R_MARGIN - logo_size, PAGE_H - 6 - logo_size - 8,
            width=logo_size, height=logo_size,
            preserveAspectRatio=True, mask="auto",
        )

    # ── Business name ──
    y = PAGE_H - 30
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(PRIMARY)
    c.drawString(L_MARGIN, y, BUSINESS_NAME)

    # ── Address ──
    c.setFont("Helvetica", 9)
    c.setFillColor(MID_GRAY)
    for line in BUSINESS_INFO:
        y -= 13
        c.drawString(L_MARGIN, y, line)

    # ── "INVOICE" ──
    y -= 40
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(PRIMARY)
    c.drawString(L_MARGIN, y, "INVOICE")

    # ── Submitted date ──
    y -= 22
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(ACCENT)
    c.drawString(L_MARGIN, y, f"Submitted on {data['date_submitted']}")

    # ── Info grid ──
    y -= 30
    col1_x = L_MARGIN
    col2_x = L_MARGIN + 160
    col3_x = L_MARGIN + 360

    def bold_label(x, yy, text):
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(PRIMARY)
        c.drawString(x, yy, text)

    def regular_val(x, yy, text):
        c.setFont("Helvetica", 10)
        c.setFillColor(black)
        c.drawString(x, yy, str(text))

    bold_label(col1_x, y, "Invoice for")
    bold_label(col2_x, y, "Payable to")
    bold_label(col3_x, y, "Invoice #")

    y -= 15
    regular_val(col1_x, y, data["client_name"])
    regular_val(col2_x, y, PAYABLE_TO)
    regular_val(col3_x, y, invoice_num)

    y -= 20
    bold_label(col2_x, y, "Project")
    bold_label(col3_x, y, "Due date")

    y -= 15
    regular_val(col2_x, y, data["project"])
    regular_val(col3_x, y, data["due_date"])

    # ── Divider ──
    y -= 20
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(1.5)
    c.line(L_MARGIN, y, R_MARGIN, y)

    # ── Table header ──
    y -= 20
    COL_QTY_RX    = L_MARGIN + 330
    COL_UPRICE_RX = L_MARGIN + 420
    COL_TOTAL_RX  = R_MARGIN

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(PRIMARY)
    c.drawString(L_MARGIN, y, "Description")
    c.drawRightString(COL_QTY_RX,    y, "Qty")
    c.drawRightString(COL_UPRICE_RX, y, "Unit price")
    c.drawRightString(COL_TOTAL_RX,  y, "Total price")

    # ── Line items ──
    ROW_H = 18
    for i, item in enumerate(data["line_items"]):
        y -= ROW_H
        if i % 2 == 1:
            c.setFillColor(ROW_ALT)
            c.rect(L_MARGIN, y - 4, CONTENT_W, ROW_H, fill=1, stroke=0)

        c.setFont("Helvetica", 10)
        c.setFillColor(black)
        c.drawString(L_MARGIN, y, str(item["desc"]))

        qty = item["qty"]
        qty_str = f"{int(qty)}" if qty == int(qty) else f"{qty:.2f}"
        c.setFillColor(MID_GRAY)
        c.drawRightString(COL_QTY_RX, y, qty_str)

        price = item["price"]
        price_str = f"${abs(price):.2f}" if price >= 0 else f"-${abs(price):.2f}"
        c.drawRightString(COL_UPRICE_RX, y, price_str)

        c.setFillColor(black)
        total = item["total"]
        total_str = f"${abs(total):.2f}" if total >= 0 else f"-${abs(total):.2f}"
        c.drawRightString(COL_TOTAL_RX, y, total_str)

    # ── Footer: notes left, totals right ──
    y -= 28
    subtotal = sum(item["total"] for item in data["line_items"])
    adj = data.get("adjustments", 0.0)
    grand_total = subtotal + adj

    notes = [ln for ln in data.get("notes", []) if ln.strip()]

    # Notes
    c.setFont("Helvetica", 9)
    c.setFillColor(MID_GRAY)
    c.drawString(L_MARGIN, y, "Notes:")
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    note_y = y - 14
    for line in notes:
        c.drawString(L_MARGIN, note_y, line)
        note_y -= 14

    # Totals (aligned right)
    tot_label_x = COL_UPRICE_RX - 60

    c.setFont("Helvetica", 10)
    c.setFillColor(MID_GRAY)
    c.drawString(tot_label_x, y, "Subtotal")
    c.setFillColor(black)
    c.drawRightString(COL_TOTAL_RX, y, f"${subtotal:.2f}")

    y -= 16
    c.setFillColor(MID_GRAY)
    c.drawString(tot_label_x, y, "Adjustments")
    c.setFillColor(black)
    c.drawRightString(COL_TOTAL_RX, y, f"${adj:.2f}")

    y -= 22
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(PRIMARY)
    c.drawRightString(COL_TOTAL_RX, y, f"${grand_total:.2f}")


def create_invoice(data: dict) -> tuple[None, str]:
    """Main entry point called by app.py. Returns (None, pdf_path)."""
    prefix = data["prefix"].upper()
    invoice_num, raw_num = _next_invoice_number(prefix)

    pdf_path = str(Path.home() / "Desktop" / f"Invoice {invoice_num}.pdf")

    c = canvas.Canvas(pdf_path, pagesize=letter)
    _draw_invoice(c, data, invoice_num)
    c.save()

    _record_invoice(prefix, raw_num)
    subprocess.run(["open", pdf_path], check=True)

    return None, pdf_path
