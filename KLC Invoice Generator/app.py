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
