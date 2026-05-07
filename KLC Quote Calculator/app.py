"""
KLC Quote Calculator
Ko'olau Laser Creations — quote generation tool with PDF export.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import datetime
import os


# ─── QUOTE LOGIC ─────────────────────────────────────────────────────────────

def calculate_quote(material_cost, machine_hours, machine_rate,
                    labor_hours, labor_rate, setup_fee,
                    margin_pct, discount_pct):
    """Return a dict of all line items and the final total."""
    machine_cost = machine_hours * machine_rate
    labor_cost = labor_hours * labor_rate
    subtotal = material_cost + machine_cost + labor_cost + setup_fee
    margin_amount = subtotal * (margin_pct / 100)
    pre_discount = subtotal + margin_amount
    discount_amount = pre_discount * (discount_pct / 100)
    total = pre_discount - discount_amount

    return {
        "material_cost": material_cost,
        "machine_cost": machine_cost,
        "labor_cost": labor_cost,
        "setup_fee": setup_fee,
        "subtotal": subtotal,
        "margin_pct": margin_pct,
        "margin_amount": margin_amount,
        "pre_discount": pre_discount,
        "discount_pct": discount_pct,
        "discount_amount": discount_amount,
        "total": total,
    }


# ─── PDF EXPORT ───────────────────────────────────────────────────────────────

LOGO_PATH = "/Users/micahmiyashiro/Desktop/KLC Logo V2 copy.png"


def export_pdf(filepath, customer_name, customer_email, job_description,
               quote_number, breakdown):
    """Generate a branded PDF quote and save to filepath."""
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    # Brand colors (Ko'olau dark green + brown)
    KLC_GREEN = colors.HexColor("#2D5016")
    KLC_BROWN = colors.HexColor("#6B4226")
    KLC_LIGHT = colors.HexColor("#F5F0E8")

    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        "Header",
        fontSize=22,
        textColor=KLC_GREEN,
        fontName="Helvetica-Bold",
        spaceAfter=36,
    )
    subheader_style = ParagraphStyle(
        "SubHeader",
        fontSize=11,
        textColor=KLC_BROWN,
        fontName="Helvetica",
        spaceAfter=2,
    )
    label_style = ParagraphStyle(
        "Label",
        fontSize=10,
        textColor=colors.HexColor("#555555"),
        fontName="Helvetica-Bold",
    )
    value_style = ParagraphStyle(
        "Value",
        fontSize=10,
        fontName="Helvetica",
    )
    total_style = ParagraphStyle(
        "Total",
        fontSize=13,
        textColor=KLC_GREEN,
        fontName="Helvetica-Bold",
        alignment=TA_RIGHT,
    )
    footer_style = ParagraphStyle(
        "Footer",
        fontSize=8,
        textColor=colors.HexColor("#888888"),
        fontName="Helvetica",
        alignment=TA_CENTER,
    )

    story = []

    # Header — logo left, business info right
    logo_cell = ""
    if os.path.exists(LOGO_PATH):
        logo = Image(LOGO_PATH)
        logo._restrictSize(1.6 * inch, 1.6 * inch)
        logo_cell = logo

    header_text = [
        Paragraph("Ko'olau Laser Creations", header_style),
        Paragraph("3D Printing · Laser Cutting · Engraving · Design", subheader_style),
        Paragraph("Kaneohe, Oahu, Hawaii", subheader_style),
        Paragraph("koolaulasercreations@gmail.com", subheader_style),
    ]

    header_table = Table(
        [[logo_cell, header_text]],
        colWidths=[1.8 * inch, 5.2 * inch],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 12),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=2, color=KLC_GREEN, spaceBefore=10, spaceAfter=12))

    # Quote meta
    today = datetime.date.today().strftime("%B %d, %Y")
    meta_data = [
        ["Quote Number:", quote_number, "Date:", today],
        ["Customer:", customer_name, "Email:", customer_email],
    ]
    meta_table = Table(meta_data, colWidths=[1.2 * inch, 2.5 * inch, 0.8 * inch, 2.5 * inch])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#555555")),
        ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#555555")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Job description
    story.append(Paragraph("Job Description", label_style))
    story.append(Paragraph(job_description or "—", value_style))
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CCCCCC"), spaceAfter=10))

    # Line items table
    line_items = [
        ["Description", "Amount"],
        ["Material Cost", f"${breakdown['material_cost']:,.2f}"],
        ["Machine Time", f"${breakdown['machine_cost']:,.2f}"],
        ["Labor", f"${breakdown['labor_cost']:,.2f}"],
        ["Setup Fee", f"${breakdown['setup_fee']:,.2f}"],
        ["Subtotal", f"${breakdown['subtotal']:,.2f}"],
        [f"Profit Margin ({breakdown['margin_pct']:.1f}%)", f"${breakdown['margin_amount']:,.2f}"],
    ]
    if breakdown["discount_pct"] > 0:
        line_items.append([
            f"Bulk Discount ({breakdown['discount_pct']:.1f}%)",
            f"-${breakdown['discount_amount']:,.2f}",
        ])

    col_widths = [4.5 * inch, 2.5 * inch]
    items_table = Table(line_items, colWidths=col_widths)
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), KLC_GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, KLC_LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (0, -1), 8),
        ("RIGHTPADDING", (1, 0), (1, -1), 8),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 10))

    # Total
    story.append(Paragraph(f"TOTAL:  ${breakdown['total']:,.2f}", total_style))
    story.append(Spacer(1, 30))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CCCCCC"), spaceAfter=8))
    story.append(Paragraph(
        "This quote is valid for 30 days. Prices are estimates and may vary based on final design requirements. "
        "Thank you for choosing Ko'olau Laser Creations!",
        footer_style,
    ))

    doc.build(story)


# ─── GUI ─────────────────────────────────────────────────────────────────────

class QuoteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KLC Quote Calculator")
        self.resizable(False, False)
        self._quote_counter = 1
        self._build_ui()

    def _build_ui(self):
        # Brand colors
        BG = "#F5F0E8"
        GREEN = "#2D5016"
        BROWN = "#6B4226"

        self.configure(bg=BG)

        # Header banner
        banner = tk.Frame(self, bg=GREEN, pady=10)
        banner.pack(fill="x")
        tk.Label(banner, text="Ko'olau Laser Creations",
                 font=("Helvetica", 18, "bold"), bg=GREEN, fg="white").pack()
        tk.Label(banner, text="Quote Calculator",
                 font=("Helvetica", 11), bg=GREEN, fg="#A8C97A").pack()

        main = tk.Frame(self, bg=BG, padx=20, pady=16)
        main.pack(fill="both")

        def section(parent, title):
            tk.Label(parent, text=title, font=("Helvetica", 11, "bold"),
                     bg=BG, fg="#1A1A1A").grid(row=section.row, column=0, columnspan=2,
                                               sticky="w", pady=(12, 2))
            section.row += 1
        section.row = 0

        def row(parent, label, default="0"):
            tk.Label(parent, text=label, bg=BG, fg="#1A1A1A", anchor="w",
                     width=26).grid(row=section.row, column=0, sticky="w", pady=2)
            var = tk.StringVar(value=default)
            tk.Entry(parent, textvariable=var, width=18).grid(
                row=section.row, column=1, sticky="w", padx=(8, 0))
            section.row += 1
            return var

        def text_row(parent, label):
            tk.Label(parent, text=label, bg=BG, fg="#1A1A1A", anchor="w",
                     width=26).grid(row=section.row, column=0, sticky="nw", pady=2)
            t = tk.Text(parent, width=30, height=3, font=("Helvetica", 10))
            t.grid(row=section.row, column=1, sticky="w", padx=(8, 0))
            section.row += 1
            return t

        # Customer info
        section(main, "Customer Info")
        self.customer_name = row(main, "Customer Name:", "")
        self.customer_email = row(main, "Customer Email:", "")
        self.job_desc = text_row(main, "Job Description:")

        # Costs
        section(main, "Costs")
        self.material_cost = row(main, "Material Cost ($):", "0.00")
        self.machine_hours = row(main, "Machine Hours:", "0")
        self.machine_rate = row(main, "Machine Rate ($/hr):", "30.00")
        self.labor_hours = row(main, "Labor Hours:", "0")
        self.labor_rate = row(main, "Labor Rate ($/hr):", "25.00")
        self.setup_fee = row(main, "Setup Fee ($):", "0.00")

        # Adjustments
        section(main, "Adjustments")
        self.margin_pct = row(main, "Profit Margin (%):", "30")
        self.discount_pct = row(main, "Bulk Discount (%):", "0")

        # Buttons
        btn_frame = tk.Frame(self, bg=BG, padx=20, pady=14)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Calculate", font=("Helvetica", 11, "bold"),
                  bg=GREEN, fg="white", padx=16, pady=6,
                  relief="flat", cursor="hand2",
                  command=self._calculate).pack(side="left", padx=(0, 10))

        tk.Button(btn_frame, text="Export PDF", font=("Helvetica", 11, "bold"),
                  bg=BROWN, fg="white", padx=16, pady=6,
                  relief="flat", cursor="hand2",
                  command=self._export_pdf).pack(side="left")

        tk.Button(btn_frame, text="Clear", font=("Helvetica", 10),
                  bg="#CCCCCC", fg="#333333", padx=12, pady=6,
                  relief="flat", cursor="hand2",
                  command=self._clear).pack(side="right")

        # Result panel
        result_frame = tk.Frame(self, bg=GREEN, padx=20, pady=12)
        result_frame.pack(fill="x")
        self.result_var = tk.StringVar(value="Fill in the fields above and click Calculate.")
        tk.Label(result_frame, textvariable=self.result_var, bg=GREEN, fg="white",
                 font=("Helvetica", 12), justify="left", anchor="w").pack(fill="x")

        self._last_breakdown = None

    def _get_float(self, var, name):
        try:
            return float(var.get())
        except ValueError:
            raise ValueError(f"'{name}' must be a number.")

    def _calculate(self):
        try:
            breakdown = calculate_quote(
                material_cost=self._get_float(self.material_cost, "Material Cost"),
                machine_hours=self._get_float(self.machine_hours, "Machine Hours"),
                machine_rate=self._get_float(self.machine_rate, "Machine Rate"),
                labor_hours=self._get_float(self.labor_hours, "Labor Hours"),
                labor_rate=self._get_float(self.labor_rate, "Labor Rate"),
                setup_fee=self._get_float(self.setup_fee, "Setup Fee"),
                margin_pct=self._get_float(self.margin_pct, "Profit Margin"),
                discount_pct=self._get_float(self.discount_pct, "Bulk Discount"),
            )
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return

        self._last_breakdown = breakdown
        discount_line = (f"  Discount ({breakdown['discount_pct']:.1f}%):  "
                         f"-${breakdown['discount_amount']:,.2f}\n"
                         if breakdown["discount_pct"] > 0 else "")
        self.result_var.set(
            f"  Material: ${breakdown['material_cost']:,.2f}   "
            f"Machine: ${breakdown['machine_cost']:,.2f}   "
            f"Labor: ${breakdown['labor_cost']:,.2f}   "
            f"Setup: ${breakdown['setup_fee']:,.2f}\n"
            f"  Subtotal: ${breakdown['subtotal']:,.2f}   "
            f"Margin ({breakdown['margin_pct']:.1f}%): +${breakdown['margin_amount']:,.2f}   "
            f"{discount_line}"
            f"TOTAL: ${breakdown['total']:,.2f}"
        )

    def _export_pdf(self):
        if not self._last_breakdown:
            self._calculate()
        if not self._last_breakdown:
            return

        default_name = f"KLC_Quote_{self._quote_counter:04d}.pdf"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=default_name,
        )
        if not filepath:
            return

        try:
            export_pdf(
                filepath=filepath,
                customer_name=self.customer_name.get(),
                customer_email=self.customer_email.get(),
                job_description=self.job_desc.get("1.0", "end").strip(),
                quote_number=f"KLC-{self._quote_counter:04d}",
                breakdown=self._last_breakdown,
            )
            self._quote_counter += 1
            messagebox.showinfo("Exported", f"Quote saved to:\n{filepath}")
            os.system(f'open "{filepath}"')
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _clear(self):
        for var in (self.customer_name, self.customer_email,
                    self.material_cost, self.machine_hours, self.machine_rate,
                    self.labor_hours, self.labor_rate, self.setup_fee,
                    self.margin_pct, self.discount_pct):
            var.set("")
        self.job_desc.delete("1.0", "end")
        self.machine_rate.set("30.00")
        self.labor_rate.set("25.00")
        self.margin_pct.set("30")
        self.discount_pct.set("0")
        self._last_breakdown = None
        self.result_var.set("Fill in the fields above and click Calculate.")


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QuoteApp()
    app.mainloop()
