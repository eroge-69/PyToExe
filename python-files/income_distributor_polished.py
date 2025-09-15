#!/usr/bin/env python3
"""Income Distributor - Polished UI Version
Reads percentage structure from 'INCOME EXPENSE PERCENTAGE STRUCTURE.xlsx' (Sheet1)
and distributes an entered income amount across categories, showing Category, %,
Amount, and Bank Account. Allows exporting results to Excel. Includes improved UI
and uses a provided PNG icon if available.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import pandas as pd
import os
import locale

# Set locale for number formatting (uses user's default locale)
try:
    locale.setlocale(locale.LC_ALL, '')
except Exception:
    # fallback - some environments may not support locale setting
    pass

BASE_DIR = os.path.dirname(__file__)
DEFAULT_DATA_FILE = os.path.join(BASE_DIR, "INCOME EXPENSE PERCENTAGE STRUCTURE.xlsx")
DEFAULT_ICON = os.path.join(BASE_DIR, "A_flat-design_vector_graphic_icon_features_a_finan.png")

def format_currency(value):
    try:
        # Use locale if possible
        v = float(value)
        s = locale.format_string("%0.2f", v, grouping=True)
    except Exception:
        s = f"{float(value):,.2f}"
    return s

def read_structure_from_excel(path=DEFAULT_DATA_FILE):
    try:
        df = pd.read_excel(path, sheet_name=0, header=None, dtype=str)
    except Exception as e:
        raise RuntimeError(f"Failed to read Excel file: {e}")
    flat = df.fillna("").astype(str)
    # Heuristic: header-like row at index 2, values at index 3 (based on your sheet)
    header_row_index = 2 if len(flat) > 3 else 0
    value_row_index = header_row_index + 1 if len(flat) > header_row_index+1 else header_row_index
    header_row = flat.iloc[header_row_index].tolist()
    value_row = flat.iloc[value_row_index].tolist()
    categories = []
    import re
    keywords = {
        "TITHE": "Tithe",
        "SEED": "Seed",
        "JOSEPH": "Joseph Account",
        "HOME RUNNING": "Home Running",
        "UTILITY": "Utility",
        "SAVINGS": "Savings"
    }
    for idx, label in enumerate(header_row):
        lbl = label.strip().upper()
        val = value_row[idx].strip() if idx < len(value_row) else ""
        if not lbl:
            continue
        # If header contains a percentage in parentheses e.g. "TITHE (10%)", parse it
        m = re.match(r'(.+?)\\s*\\((\\d+)%\\)', lbl)
        if m:
            cat = m.group(1).strip().title()
            pct = int(m.group(2))
            bank = ""
            for up in range(header_row_index-1, -1, -1):
                candidate = flat.iloc[up, idx].strip()
                if candidate:
                    bank = candidate
                    break
            categories.append({"Category": cat, "Percentage": pct, "Bank": bank})
            continue
        # fallback: find known keywords
        for k, name in keywords.items():
            if k in lbl:
                # try parse percentage from value cell or from label digits
                pct = None
                vr = val.upper().replace('%','').strip()
                try:
                    pct = int(vr)
                except:
                    dig = re.search(r'(\\d+)', lbl)
                    if dig:
                        pct = int(dig.group(1))
                if pct is None:
                    pct = 0
                bank = ""
                for up in range(header_row_index-1, -1, -1):
                    candidate = flat.iloc[up, idx].strip()
                    if candidate:
                        bank = candidate
                        break
                categories.append({"Category": name, "Percentage": pct, "Bank": bank})
                break
    if not categories:
        # fallback static structure
        categories = [
            {"Category":"Tithe","Percentage":10,"Bank":"Access Bank 0028577498"},
            {"Category":"Seed","Percentage":5,"Bank":"GTBANK 0049508405"},
            {"Category":"Joseph Account","Percentage":20,"Bank":"Sterling Bank 0073672307"},
            {"Category":"Home Running","Percentage":40,"Bank":"Opay 8060779227"},
            {"Category":"Utility","Percentage":15,"Bank":"Fairmoney 8060779227"},
            {"Category":"Savings","Percentage":10,"Bank":"FBN 3192545360"},
        ]
    for c in categories:
        c["Percentage"] = int(c["Percentage"])
    return categories

class IncomeDistributorApp(tk.Tk):
    def __init__(self, data_file=DEFAULT_DATA_FILE, icon_file=DEFAULT_ICON):
        super().__init__()
        self.title("Income Distributor")
        self.geometry("820x560")
        self.minsize(760, 480)
        self.configure(bg="#f4f7fb")
        self.data_file = data_file
        self.icon_file = icon_file
        try:
            self.categories = read_structure_from_excel(data_file)
        except Exception as e:
            messagebox.showwarning("Data File", f"Couldn't read the Excel file automatically: {e}\\nUsing fallback structure.")
            self.categories = read_structure_from_excel.__wrapped__() if hasattr(read_structure_from_excel, '__wrapped__') else []
        self._setup_style()
        self.create_widgets()
        self._set_icon()

    def _set_icon(self):
        # Use iconphoto if PNG exists; otherwise ignore
        try:
            if os.path.exists(self.icon_file):
                img = tk.PhotoImage(file=self.icon_file)
                self.iconphoto(True, img)
        except Exception:
            pass

    def _setup_style(self):
        style = ttk.Style(self)
        # Use clam theme if available for better visuals
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), background='#0b3d91', foreground='white', padding=10)
        style.configure('TFrame', background='#f4f7fb')
        style.configure('Card.TFrame', background='white', relief='flat')
        style.configure('Info.TLabel', font=('Segoe UI', 10), background='#f4f7fb')
        style.configure('Small.TButton', font=('Segoe UI', 9))

    def create_widgets(self):
        # Top bar
        top = ttk.Frame(self, style='TFrame', padding=(12,12))
        top.pack(fill='x', padx=12, pady=(12,6))
        header = ttk.Label(top, text='Income Distributor', style='Header.TLabel', anchor='w')
        header.pack(fill='x')

        body = ttk.Frame(self, style='TFrame', padding=(12,8))
        body.pack(fill='both', expand=True, padx=12, pady=(6,12))

        # Input card
        card = ttk.Frame(body, style='Card.TFrame', padding=12)
        card.pack(fill='x', padx=6, pady=(0,12))

        lbl = ttk.Label(card, text='Enter Income Amount:', style='Info.TLabel')
        lbl.grid(row=0, column=0, sticky='w')
        self.income_var = tk.StringVar(value='0.00')
        self.entry_income = ttk.Entry(card, textvariable=self.income_var, width=24, font=('Segoe UI', 11))
self.entry_income.config(state="normal")

        self.entry_income.grid(row=0, column=1, padx=(8,8))
        btn_calc = ttk.Button(card, text='Calculate', command=self.calculate, style='Small.TButton')
        btn_calc.grid(row=0, column=2, padx=6)
        btn_export = ttk.Button(card, text='Export to Excel', command=self.export_to_excel, style='Small.TButton')
        btn_export.grid(row=0, column=3, padx=6)
        btn_load = ttk.Button(card, text='Load Excel...', command=self.load_excel, style='Small.TButton')
        btn_load.grid(row=0, column=4, padx=6)

        # Results area
        cols = ('Category','Percentage','Amount','Bank Account')
        self.tree = ttk.Treeview(body, columns=cols, show='headings', height=14)
        for c in cols:
            self.tree.heading(c, text=c)
            if c == 'Category':
                self.tree.column(c, width=240, anchor='w')
            elif c == 'Bank Account':
                self.tree.column(c, width=300, anchor='w')
            else:
                self.tree.column(c, width=120, anchor='e')

        # Add striped row tags
        self.tree.tag_configure('oddrow', background='#ffffff')
        self.tree.tag_configure('evenrow', background='#f7fbff')

        # Add a vertical scrollbar
        vsb = ttk.Scrollbar(body, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side='right', fill='y', padx=(0,12), pady=(0,12))
        self.tree.pack(fill='both', expand=True, padx=(6,0), pady=(6,0))

        # Info footer card
        footer = ttk.Frame(self, style='Card.TFrame', padding=8)
        footer.pack(fill='x', side='bottom', padx=12, pady=12)
        self.status = tk.StringVar(value=f"Loaded categories: {len(self.categories)} | File: {os.path.basename(self.data_file)}")
        ttk.Label(footer, textvariable=self.status, style='Info.TLabel').pack(side='left')

    def load_excel(self):
        p = filedialog.askopenfilename(title='Select Excel file', filetypes=[('Excel files','*.xlsx;*.xls')])
        if not p:
            return
        try:
            self.categories = read_structure_from_excel(p)
            self.status.set(f"Loaded categories: {len(self.categories)} | File: {os.path.basename(p)}")
            messagebox.showinfo('Loaded', f'Loaded {len(self.categories)} categories from the file.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load: {e}')

    def calculate(self):
        income_text = self.income_var.get().strip().replace(',','')
        try:
            income = Decimal(income_text)
        except InvalidOperation:
            messagebox.showerror('Invalid Input', 'Please enter a valid numeric income amount.')
            return
        # Clear tree
        for row in self.tree.get_children():
            self.tree.delete(row)
        allocated_total = Decimal('0.00')
        rows = []
        # compute using quantize for 2 decimal places rounding half up
        for cat in self.categories:
            pct = Decimal(cat['Percentage'])
            amt = (income * pct / Decimal(100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            allocated_total += amt
            rows.append((cat['Category'], f"{int(pct)}%", amt, cat.get('Bank','')))
        # handle rounding remainder
        remainder = income - allocated_total
        if remainder != Decimal('0.00') and rows:
            # add remainder to largest percentage category
            max_idx = max(range(len(self.categories)), key=lambda i: self.categories[i]['Percentage'])
            cat, pct, amt, bank = rows[max_idx]
            new_amt = (amt + remainder).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            rows[max_idx] = (cat, pct, new_amt, bank)
            allocated_total += remainder
        # insert into tree with formatting and striped rows
        for i, r in enumerate(rows):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            cat, pct, amt, bank = r
            amt_str = format_currency(str(amt))
            self.tree.insert('', 'end', values=(cat, pct, amt_str, bank), tags=(tag,))
        self.status.set(f"Income: {format_currency(income)}  |  Allocated: {format_currency(allocated_total)}")


    def export_to_excel(self):
        rows = [self.tree.item(i)['values'] for i in self.tree.get_children()]
        if not rows:
            messagebox.showwarning('No Data', 'Please calculate distribution before exporting.')
            return
        df = pd.DataFrame(rows, columns=['Category','Percentage','Amount','Bank Account'])
        p = filedialog.asksaveasfilename(title='Save as Excel', defaultextension='.xlsx', filetypes=[('Excel files','*.xlsx')])
        if not p:
            return
        try:
            # remove grouping separators from Amount before saving numeric
            df['Amount'] = df['Amount'].astype(str).str.replace(',','').astype(float)
            df.to_excel(p, index=False)
            messagebox.showinfo('Saved', f'Exported results to {p}')
        except Exception as e:
            messagebox.showerror('Save Error', f'Failed to save: {e}')


if __name__ == '__main__':
    app = IncomeDistributorApp()
    app.mainloop()
