import os
import glob
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DATE_FORMAT = '%d/%m/%Y'

def parse_file(path):
    """
    Read one guest file and return a flat dict of all fields.
    Sections like [Guest Services] become keys prefixed with the section name.
    """
    data = {}
    current_section = None

    with open(path, encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            # Section header
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                data[current_section] = {}
                continue

            # Key: Value lines
            if ':' in line:
                key, val = line.split(':', 1)
                key = key.strip()
                val = val.strip()
                if current_section:
                    data[current_section][key] = val
                else:
                    data[key] = val

    # Flatten nested sections into single-level dict
    flat = {}
    for k, v in data.items():
        if isinstance(v, dict):
            for subk, subv in v.items():
                flat[f"{k} - {subk}"] = subv
        else:
            flat[k] = v
    return flat

def load_all_records():
    """
    Parse every .txt file in DATA_DIR. Returns list of flat dicts.
    """
    files = glob.glob(os.path.join(DATA_DIR, '*.txt'))
    records = [parse_file(p) for p in files]
    return records

class GuestDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Guest Feedback Dashboard")
        self.geometry("1000x600")

        # Load data
        self.records = load_all_records()
        if not self.records:
            messagebox.showinfo("No Data", f"No .txt files found in {DATA_DIR}")
            self.destroy()
            return

        # Determine all column names from keys
        self.columns = list(self.records[0].keys())

        self._build_ui()
        self._populate_table(self.records)

    def _build_ui(self):
        # Date filter frame
        frm_filters = ttk.Frame(self)
        frm_filters.pack(fill='x', padx=10, pady=5)

        ttk.Label(frm_filters, text="Arrival From (dd/mm/yyyy):").pack(side='left')
        self.ent_from = ttk.Entry(frm_filters, width=12)
        self.ent_from.pack(side='left', padx=(5,15))

        ttk.Label(frm_filters, text="Arrival To (dd/mm/yyyy):").pack(side='left')
        self.ent_to = ttk.Entry(frm_filters, width=12)
        self.ent_to.pack(side='left', padx=(5,15))

        btn_filter = ttk.Button(frm_filters, text="Filter", command=self.apply_filter)
        btn_filter.pack(side='left', padx=5)

        btn_clear = ttk.Button(frm_filters, text="Clear Filter", command=self.clear_filter)
        btn_clear.pack(side='left', padx=5)

        # Table + scrollbars
        frm_table = ttk.Frame(self)
        frm_table.pack(fill='both', expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(frm_table, columns=self.columns, show='headings')
        vsb = ttk.Scrollbar(frm_table, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frm_table, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        frm_table.rowconfigure(0, weight=1)
        frm_table.columnconfigure(0, weight=1)

        # Set up column headings
        for col in self.columns:
            self.tree.heading(col, text=col)
            # Give some default width
            self.tree.column(col, width=120, anchor='w')

    def _populate_table(self, recs):
        # Clear existing
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insert each record
        for r in recs:
            vals = [r.get(c, "") for c in self.columns]
            self.tree.insert('', 'end', values=vals)

    def apply_filter(self):
        frm = self.ent_from.get().strip()
        to = self.ent_to.get().strip()

        try:
            dt_from = datetime.strptime(frm, DATE_FORMAT) if frm else None
            dt_to   = datetime.strptime(to,   DATE_FORMAT) if to  else None
        except ValueError:
            messagebox.showerror("Invalid Date", f"Please use format {DATE_FORMAT}")
            return

        filtered = []
        for r in self.records:
            adate_str = r.get("Arrival Date", "")
            try:
                adate = datetime.strptime(adate_str, DATE_FORMAT)
            except Exception:
                continue
            if dt_from and adate < dt_from:
                continue
            if dt_to   and adate > dt_to:
                continue
            filtered.append(r)

        self._populate_table(filtered)

    def clear_filter(self):
        self.ent_from.delete(0, 'end')
        self.ent_to.delete(0, 'end')
        self._populate_table(self.records)

if __name__ == "__main__":
    app = GuestDashboard()
    app.mainloop()
