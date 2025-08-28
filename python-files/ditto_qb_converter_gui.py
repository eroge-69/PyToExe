#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ditto QuickBooks Converter - GUI
--------------------------------
A small Tkinter app to convert a "job log" Excel workbook into a QuickBooks-ready
"After_Generated" sheet with:
- Grouping lines per (TAT, Speakers bucket, Verbatim/Timestamps)
- Item(Product/Service) category mapping (Category + " Transcription", Spanish -> "Spanish Translation")
- ItemQuantity = Minutes (already decimal minutes)
- InvoiceDate, DueDate from UI (MM/DD/YYYY)
- InvoiceNo applied per client: starts from user-provided number (first client), then increments for each new client

Dependencies:
    pip install pandas openpyxl xlsxwriter

Run:
    python ditto_qb_converter_gui.py
"""

import os
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    # Optional drag-and-drop support: pip install tkinterdnd2
    from tkinterdnd2 import DND_FILES, TkinterDnD
    _DND_AVAILABLE = True
except Exception:
    _DND_AVAILABLE = False

import pandas as pd


def _normalize_columns(df: pd.DataFrame):
    """Return (df, colmap) where colmap maps canonical keys -> actual column names in df."""
    norm = {}
    for col in df.columns:
        key = str(col).strip().lower().replace("\n", " ")
        key = re.sub(r"\s+", " ", key)
        norm[col] = key

    def pick(*cands):
        # exact first
        for real, k in norm.items():
            for c in cands:
                if k == c:
                    return real
        # contains fallback
        for real, k in norm.items():
            for c in cands:
                if c in k:
                    return real
        return None

    colmap = {
        "client":   pick("client"),
        "category": pick("category"),
        "file_name":pick("file name", "filename"),
        "minutes":  pick("minutes"),
        "rate":     pick("rate"),
        "tat":      pick("tat"),
        "speakers": pick("number of speakers", "num of speakers", "speakers"),
        "vt":       pick("verbatim or timestamps", "verbatim & timestamps", "verbatim / timestamps"),
    }
    missing = [k for k,v in colmap.items() if v is None]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}. Found columns: {list(df.columns)}")
    return df, colmap


def _tat_label_key(v):
    s = str(v).strip().lower()
    if "rush" in s or "1-2" in s:
        return ("1-2 Business Day Turnaround", 0)
    if "standard" in s or "3-5" in s:
        return ("3-5 Business Day Turnaround", 1)
    if "extended" in s or "6-10" in s:
        return ("6-10 Business Day Turnaround", 2)
    return (s.title() if s else "Other Turnaround", 99)


def _speakers_bucket_key(v):
    s = str(v).strip()
    if s == "" or s.lower() == "nan":
        return ("1-2 Speakers", 0)
    try:
        n = int(float(s))
        return ("1-2 Speakers" if n <= 2 else "3+ Speakers", 0 if n <= 2 else 1)
    except Exception:
        pass
    s2 = s.lower()
    if ("1" in s2 and "2" in s2):
        return ("1-2 Speakers", 0)
    if any(ch in s2 for ch in ["3", "+", "4", "5"]):
        return ("3+ Speakers", 1)
    return ("1-2 Speakers", 0)


def _vt_label_key(v):
    s = str(v).strip().lower()
    if s in ("", "none", "nan"):
        label = "Cleaned-Up Verbatim"
    elif s == "verbatim":
        label = "Verbatim"
    elif s == "timestamps":
        label = "Timestamps"
    elif ("verbatim" in s and "timestamp" in s):
        label = "Verbatim & Timestamps"
    elif s == "cleaned-up verbatim":
        label = "Cleaned-Up Verbatim"
    else:
        label = str(v).strip().title()
    order = {"Cleaned-Up Verbatim":0, "Verbatim":1, "Timestamps":2, "Verbatim & Timestamps":3}
    return (label, order.get(label, 9))


def _category_map(cat):
    s = str(cat).strip()
    if s.lower() == "spanish":
        return "Spanish Translation"
    if s == "" or s.lower() == "nan":
        return "Transcription"
    return f"{s} Transcription"


def transform_to_after(before_df: pd.DataFrame, invoice_date: str, due_date: str, first_invoice_no: int) -> pd.DataFrame:
    """Convert Before-style DataFrame to QuickBooks After format."""
    bdf, cols = _normalize_columns(before_df)

    # client order by first appearance
    order = []
    seen = set()
    for c in bdf[cols["client"]].astype(str).fillna(""):
        if c not in seen:
            seen.add(c)
            order.append(c)

    bdf = bdf.copy()
    bdf["tat_label"], bdf["tat_key"] = zip(*bdf[cols["tat"]].map(_tat_label_key))
    bdf["spk_label"], bdf["spk_key"] = zip(*bdf[cols["speakers"]].map(_speakers_bucket_key))
    bdf["vt_label"], bdf["vt_key"] = zip(*bdf[cols["vt"]].map(_vt_label_key))
    bdf["QBCategory"] = bdf[cols["category"]].map(_category_map)

    rows = []
    inv_no = int(first_invoice_no)

    for client in order:
        sub = bdf[bdf[cols["client"]].astype(str) == str(client)].copy()
        if sub.empty:
            continue
        sub = sub.sort_values(by=["tat_key","spk_key","vt_key", cols["file_name"]], kind="mergesort")
        # group lines
        for (tat_label, spk_label, vt_label), grp in sub.groupby(["tat_label","spk_label","vt_label"], sort=False):
            rows.append({
                "*InvoiceNo": inv_no,
                "*Customer": client,
                "*InvoiceDate": invoice_date,
                "*DueDate": due_date,
                "Item(Product/Service)": None,
                "ItemDescription": f"{tat_label} | {spk_label} | {vt_label}",
                "ItemQuantity": 0.0,
                "ItemRate": 0.00,
                "*ItemAmount": 0.00
            })
            for _, r in grp.iterrows():
                try:
                    qty = float(r.get(cols["minutes"])) if pd.notna(r.get(cols["minutes"])) else 0.0
                except Exception:
                    qty = 0.0
                try:
                    rate = float(r.get(cols["rate"])) if pd.notna(r.get(cols["rate"])) else 0.0
                except Exception:
                    rate = 0.0
                amt = round(qty * rate, 2)
                rows.append({
                    "*InvoiceNo": inv_no,
                    "*Customer": client,
                    "*InvoiceDate": invoice_date,
                    "*DueDate": due_date,
                    "Item(Product/Service)": r.get("QBCategory"),
                    "ItemDescription": r.get(cols["file_name"]),
                    "ItemQuantity": qty,
                    "ItemRate": rate,
                    "*ItemAmount": amt
                })
        inv_no += 1  # next client gets next invoice number

    after = pd.DataFrame(rows, columns=[
        "*InvoiceNo","*Customer","*InvoiceDate","*DueDate",
        "Item(Product/Service)","ItemDescription","ItemQuantity","ItemRate","*ItemAmount"
    ])
    return after


def parse_mmddyyyy(s: str) -> str:
    """Return date string normalized to MM/DD/YYYY, raising ValueError if invalid."""
    s = (s or "").strip()
    try:
        dt = datetime.strptime(s, "%m/%d/%Y")
        return dt.strftime("%m/%d/%Y")
    except Exception:
        # try lenient split
        parts = s.split("/")
        if len(parts) == 3 and all(p.strip().isdigit() for p in parts):
            m, d, y = [p.strip() for p in parts]
            if len(y) == 2:
                y = "20" + y  # naive century
            dt = datetime(int(y), int(m), int(d))
            return dt.strftime("%m/%d/%Y")
        raise ValueError("Date must be in MM/DD/YYYY format")


class App(tk.Tk if not _DND_AVAILABLE else TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ditto QuickBooks Converter")
        self.geometry("600x340")
        self.minsize(560, 320)

        self.var_path = tk.StringVar()
        self.var_inv_date = tk.StringVar()
        self.var_due_date = tk.StringVar()
        self.var_first_inv = tk.StringVar()

        self._build_ui()

    def _build_ui(self):
        pad = {'padx': 10, 'pady': 8}

        outer = ttk.Frame(self)
        outer.pack(fill='both', expand=True, **pad)

        # File row
        row_file = ttk.Frame(outer)
        row_file.pack(fill='x', **pad)
        ttk.Label(row_file, text="Excel file:").pack(side='left')
        ent = ttk.Entry(row_file, textvariable=self.var_path)
        ent.pack(side='left', fill='x', expand=True, padx=(8,8))
        ttk.Button(row_file, text="Browse…", command=self.on_browse).pack(side='left')

        if _DND_AVAILABLE:
            ent.drop_target_register(DND_FILES)
            ent.dnd_bind('<<Drop>>', self.on_drop)

        # Form
        form = ttk.Frame(outer)
        form.pack(fill='x', **pad)

        ttk.Label(form, text="Invoice Date (MM/DD/YYYY):").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.var_inv_date, width=18).grid(row=0, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(form, text="Due Date (MM/DD/YYYY):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.var_due_date, width=18).grid(row=1, column=1, sticky='w', padx=5, pady=5)

        ttk.Label(form, text="First Invoice No:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        ttk.Entry(form, textvariable=self.var_first_inv, width=18).grid(row=2, column=1, sticky='w', padx=5, pady=5)

        # Buttons
        btns = ttk.Frame(outer)
        btns.pack(fill='x', **pad)
        ttk.Button(btns, text="Convert", command=self.on_convert).pack(side='right')
        ttk.Button(btns, text="Quit", command=self.destroy).pack(side='right', padx=(0,8))

        ttk.Label(outer, text="Tip: If drag-and-drop isn't available, click Browse to pick a file.",
                  foreground="#666").pack(anchor='w', padx=4)

    def on_browse(self):
        path = filedialog.askopenfilename(
            title="Select job log Excel",
            filetypes=[("Excel", "*.xlsx;*.xlsm;*.xls")],
        )
        if path:
            self.var_path.set(path)

    def on_drop(self, event):
        raw = event.data
        # tkdnd provides a brace-wrapped list when spaces are in paths
        if raw.startswith("{") and raw.endswith("}"):
            raw = raw[1:-1]
        # naive split; good enough for typical single-file drops
        self.var_path.set(raw)

    def on_convert(self):
        try:
            path = self.var_path.get().strip()
            if not path or not os.path.exists(path):
                messagebox.showerror("Error", "Please select a valid Excel file.")
                return
            try:
                inv_date = parse_mmddyyyy(self.var_inv_date.get())
                due_date = parse_mmddyyyy(self.var_due_date.get())
            except Exception as e:
                messagebox.showerror("Invalid date", str(e))
                return
            try:
                first_inv = int(self.var_first_inv.get().strip())
            except Exception:
                messagebox.showerror("Invalid invoice number", "First Invoice No must be an integer (e.g., 1001).")
                return

            xls = pd.ExcelFile(path)
            sheet = "Before" if "Before" in xls.sheet_names else xls.sheet_names[0]
            before_df = pd.read_excel(path, sheet_name=sheet)

            after_df = transform_to_after(before_df, inv_date, due_date, first_inv)

            base_dir = os.path.dirname(path) or os.getcwd()
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_path = os.path.join(base_dir, f"Billing_After_Generated_{ts}.xlsx")

            with pd.ExcelWriter(out_path, engine="xlsxwriter") as writer:
                before_df.to_excel(writer, sheet_name="Before", index=False)
                after_df.to_excel(writer, sheet_name="After_Generated", index=False)
                wb = writer.book
                ws = writer.sheets["After_Generated"]
                # format numeric cols
                cols = list(after_df.columns)
                if "ItemQuantity" in cols:
                    qx = cols.index("ItemQuantity"); ws.set_column(qx, qx, 12, wb.add_format({'num_format':'0.0###'}))
                if "ItemRate" in cols:
                    rx = cols.index("ItemRate"); ws.set_column(rx, rx, 12, wb.add_format({'num_format':'0.00'}))
                if "*ItemAmount" in cols:
                    ax = cols.index("*ItemAmount"); ws.set_column(ax, ax, 12, wb.add_format({'num_format':'0.00'}))
                ws.autofilter(0, 0, len(after_df), len(after_df.columns)-1)

            messagebox.showinfo("Done", f"Saved:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Conversion failed", f"{e}")
            raise

def main():
    root_cls = TkinterDnD.Tk if _DND_AVAILABLE else tk.Tk
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
