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
        self._prefix_user_edited = False
        self._prefix_auto_set = False
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
        self.prefix_var.trace_add("write", self._on_prefix_change)

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

    def _on_prefix_change(self, *_):
        if not self._prefix_auto_set:
            self._prefix_user_edited = True

    def _on_company_change(self, *_):
        if self._prefix_user_edited:
            return
        name = self.company_var.get().strip()
        self._prefix_auto_set = True
        if not name:
            self.prefix_var.set("")
        else:
            self.prefix_var.set(name.split()[0].upper()[:4])
        self._prefix_auto_set = False

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
        self._prefix_user_edited = False
        self._prefix_auto_set = False
        self.company_var.set("")
        self.project_var.set("")
        d = date.today() + timedelta(days=30)
        self.due_var.set(f"{d.month}/{d.day}/{d.year}")
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
            desc = item["desc"].get().strip()
            try:
                qty = float(item["qty"].get())
                price = float(item["price"].get())
            except ValueError:
                messagebox.showerror("Invalid Input",
                                      "Qty and Unit Price must be numbers.")
                return None
            if not desc:
                continue
            items.append({
                "desc": desc,
                "qty": qty,
                "price": price,
                "total": round(qty * price, 2),
            })
        if not items:
            messagebox.showerror("Missing Items",
                                  "At least one line item with a description is required.")
            return None

        try:
            adj = float(self.adj_var.get())
        except ValueError:
            adj = 0.0

        notes_raw = self.notes_text.get("1.0", "end-1c")
        notes = [line for line in notes_raw.split("\n") if line.strip()][:3]

        d = date.today()
        return {
            "client_name": company,
            "prefix": prefix,
            "project": project,
            "due_date": due,
            "date_submitted": f"{d.month}/{d.day}/{d.year}",
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
