#!/usr/bin/env python3
"""
Import Data Desktop App
-----------------------
Single-user desktop app for daily import data entry + Excel report export.

Tech stack: Python, Tkinter, SQLite, pandas, openpyxl.

Core features
- Add ONLY new records daily (existing data stays in DB)
- Edit/Delete selected record
- Search/Filter by date range or text
- Export Excel report that matches the user's sheet format (with requested column changes)
- Dropdowns remember previously used values (Ports, Shipping Lines, SIZE, Type, CHA, Transport Name)

How to run
1) Install deps once:  pip install pandas openpyxl
2) Run:                 python app.py

The app creates a local SQLite file: data_store.db

Author: ChatGPT
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Pandas is used only for Excel export
try:
    import pandas as pd
except Exception as e:
    pd = None

DB_FILE = "data_store.db"
TABLE = "import_data"

# === Report columns (final order) ===
REPORT_COLUMNS = [
    "Sr.no",
    "Importer Name",
    "CHA",
    "B/L no",
    "B/L Date",
    "Shipping Line",
    "Container No",
    "SIZE",
    "Type",
    "Vessel Name",
    "Rotation",
    "Arrival Date",
    "IGM no",
    "IGM Date",
    "Item no",
    "SMTP no",
    "SMTP Date",
    "SMTP Received Date & Time",
    "Port",
    "Seal No",
    "Truck Number",
    "Port Gate Out Date & Time",
    "Transport Name",
]

# === Database schema (snake_case) ===
SCHEMA = {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "importer_name": "TEXT",
    "cha": "TEXT",
    "bl_no": "TEXT",
    "bl_date": "TEXT",  # store as ISO string; parse on output
    "shipping_line": "TEXT",
    "container_no": "TEXT",
    "size": "TEXT",
    "type": "TEXT",
    "vessel_name": "TEXT",
    "rotation": "TEXT",
    "arrival_date": "TEXT",
    "igm_no": "TEXT",
    "igm_date": "TEXT",
    "item_no": "TEXT",
    "smtp_no": "TEXT",
    "smtp_date": "TEXT",
    "smtp_received_dt": "TEXT",
    "port": "TEXT",
    "seal_no": "TEXT",
    "truck_number": "TEXT",
    "port_gate_out_dt": "TEXT",
    "transport_name": "TEXT",
    # housekeeping
    "created_at": "TEXT",
    "updated_at": "TEXT"
}

DATE_FIELDS = {
    "bl_date",
    "arrival_date",
    "igm_date",
    "smtp_date",
    # the following are date-time fields but we accept date too
    "smtp_received_dt",
    "port_gate_out_dt",
}

MANDATORY_FIELDS = [
    "importer_name",
    "shipping_line",
    "container_no",
    "port",
]

# Utility: robust parse of dates/times, returns ISO-like string for DB
# Accepts formats like: DD-MM-YYYY, DD/MM/YYYY, YYYY-MM-DD, YYYY/MM/DD, with or without HH:MM
# Returns original string if parsing fails (we won't block saving, but show a warning)

def parse_dateish(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    # Common candidates
    candidates = [
        "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%b-%Y",
        "%d-%b-%Y %H:%M",
    ]
    for fmt in candidates:
        try:
            dt = datetime.strptime(s, fmt)
            # Standardize: include time only if present in input
            if "%H:%M" in fmt:
                return dt.strftime("%Y-%m-%d %H:%M")
            return dt.strftime("%Y-%m-%d")
        except Exception:
            continue
    return s  # unparsed; keep as-is


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    columns_sql = ", ".join([f"{col} {typ}" for col, typ in SCHEMA.items()])
    cur.execute(f"CREATE TABLE IF NOT EXISTS {TABLE} ({columns_sql});")
    # helpful indexes
    cur.execute(f"CREATE INDEX IF NOT EXISTS idx_{TABLE}_container ON {TABLE}(container_no);")
    cur.execute(f"CREATE INDEX IF NOT EXISTS idx_{TABLE}_bl_date ON {TABLE}(bl_date);")
    cur.execute(f"CREATE INDEX IF NOT EXISTS idx_{TABLE}_arrival ON {TABLE}(arrival_date);")
    conn.commit()
    conn.close()


def db_execute(query: str, params: Tuple = ()) -> List[Tuple]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows


def db_insert(row: dict) -> int:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row["created_at"] = now
    row["updated_at"] = now
    cols = ",".join(row.keys())
    placeholders = ",".join(["?" for _ in row])
    values = tuple(row.values())
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"INSERT INTO {TABLE} ({cols}) VALUES ({placeholders})", values)
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def db_update(row_id: int, row: dict):
    row["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    set_clause = ",".join([f"{k}=?" for k in row.keys()])
    values = tuple(row.values()) + (row_id,)
    db_execute(f"UPDATE {TABLE} SET {set_clause} WHERE id=?", values)


def db_delete(row_id: int):
    db_execute(f"DELETE FROM {TABLE} WHERE id=?", (row_id,))


def db_select(where: str = "", params: Tuple = (), order: str = "id ASC") -> List[Tuple]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({TABLE});")
    cols_info = cur.fetchall()
    columns = [c[1] for c in cols_info]
    q = f"SELECT {', '.join(columns)} FROM {TABLE}"
    if where:
        q += f" WHERE {where}"
    if order:
        q += f" ORDER BY {order}"
    cur.execute(q, params)
    rows = cur.fetchall()
    conn.close()
    return columns, rows


class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        master.title("Import Data Entry & Report Export")
        master.geometry("1250x720")
        master.minsize(1100, 650)

        self.inputs = {}
        self.selected_id: Optional[int] = None

        self._build_ui()
        self._load_table()

    # --- UI ---
    def _build_ui(self):
        # Top controls
        top = ttk.Frame(self.master)
        top.pack(fill=tk.X, padx=10, pady=6)

        ttk.Label(top, text="Quick Filter (text)").pack(side=tk.LEFT)
        self.filter_text = ttk.Entry(top, width=30)
        self.filter_text.pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text="Apply", command=self.apply_filters).pack(side=tk.LEFT)
        ttk.Button(top, text="Clear", command=self.clear_filters).pack(side=tk.LEFT, padx=(6, 0))

        ttk.Label(top, text="Date From (Arrival)").pack(side=tk.LEFT, padx=(20, 4))
        self.filter_from = ttk.Entry(top, width=12)
        self.filter_from.pack(side=tk.LEFT)
        ttk.Label(top, text="To").pack(side=tk.LEFT, padx=4)
        self.filter_to = ttk.Entry(top, width=12)
        self.filter_to.pack(side=tk.LEFT)
        ttk.Button(top, text="Filter by Arrival Date", command=self.apply_filters).pack(side=tk.LEFT, padx=6)

        ttk.Button(top, text="Export Excel (All/Filtered)", command=self.export_excel).pack(side=tk.RIGHT)

        # Middle: Form + Table
        mid = ttk.Panedwindow(self.master, orient=tk.HORIZONTAL)
        mid.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        # Left: form
        form = ttk.Frame(mid)
        mid.add(form, weight=1)
        self._build_form(form)

        # Right: table
        table = ttk.Frame(mid)
        mid.add(table, weight=2)
        self._build_table(table)

    def _build_form(self, parent):
        # Helper to place label+entry in a grid
        def add_row(row, label, key, width=28, widget="entry", values: Optional[List[str]] = None):
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, pady=3)
            if widget == "entry":
                e = ttk.Entry(parent, width=width)
            elif widget == "combo":
                e = ttk.Combobox(parent, width=width, values=values or [], state="normal")
            else:
                e = ttk.Entry(parent, width=width)
            e.grid(row=row, column=1, sticky=tk.W)
            self.inputs[key] = e

        # Dropdown pools (will be updated as user saves new values)
        self.combo_sources = {
            "size": ["20", "40", "45"],
            "type": ["DRY", "HC", "RF"],
            "port": ["BMCT", "NSIGT", "NSICT", "GTI"],
            "shipping_line": [],
            "cha": [],
            "transport_name": [],
        }

        row = 0
        add_row(row, "Importer Name", "importer_name"); row += 1
        add_row(row, "CHA", "cha", widget="combo", values=self.combo_sources["cha"]); row += 1
        add_row(row, "B/L no", "bl_no"); row += 1
        add_row(row, "B/L Date (DD-MM-YYYY)", "bl_date"); row += 1
        add_row(row, "Shipping Line", "shipping_line", widget="combo", values=self.combo_sources["shipping_line"]); row += 1
        add_row(row, "Container No", "container_no"); row += 1
        add_row(row, "SIZE", "size", widget="combo", values=self.combo_sources["size"]); row += 1
        add_row(row, "Type", "type", widget="combo", values=self.combo_sources["type"]); row += 1
        add_row(row, "Vessel Name", "vessel_name"); row += 1
        add_row(row, "Rotation", "rotation"); row += 1
        add_row(row, "Arrival Date (DD-MM-YYYY)", "arrival_date"); row += 1
        add_row(row, "IGM no", "igm_no"); row += 1
        add_row(row, "IGM Date (DD-MM-YYYY)", "igm_date"); row += 1
        add_row(row, "Item no", "item_no"); row += 1
        add_row(row, "SMTP no", "smtp_no"); row += 1
        add_row(row, "SMTP Date (DD-MM-YYYY)", "smtp_date"); row += 1
        add_row(row, "SMTP Received (DD-MM-YYYY HH:MM)", "smtp_received_dt"); row += 1
        add_row(row, "Port", "port", widget="combo", values=self.combo_sources["port"]); row += 1
        add_row(row, "Seal No", "seal_no"); row += 1
        add_row(row, "Truck Number", "truck_number"); row += 1
        add_row(row, "Port Gate Out (DD-MM-YYYY HH:MM)", "port_gate_out_dt"); row += 1
        add_row(row, "Transport Name", "transport_name", widget="combo", values=self.combo_sources["transport_name"]); row += 1

        # Buttons
        btns = ttk.Frame(parent)
        btns.grid(row=row, column=0, columnspan=2, pady=(8, 0))
        ttk.Button(btns, text="New / Clear", command=self.clear_form).pack(side=tk.LEFT)
        ttk.Button(btns, text="Save New", command=self.save_new).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Update Selected", command=self.update_selected).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=6)

        note = ttk.Label(parent, text="Tip: Dates can be DD-MM-YYYY or YYYY-MM-DD; time format HH:MM", foreground="#555")
        note.grid(row=row+1, column=0, columnspan=2, sticky=tk.W, pady=(6, 0))

    def _build_table(self, parent):
        cols = [
            "id",  # hidden
            "Importer Name",
            "CHA",
            "B/L no",
            "B/L Date",
            "Shipping Line",
            "Container No",
            "SIZE",
            "Type",
            "Vessel Name",
            "Rotation",
            "Arrival Date",
            "IGM no",
            "IGM Date",
            "Item no",
            "SMTP no",
            "SMTP Date",
            "SMTP Received Date & Time",
            "Port",
            "Seal No",
            "Truck Number",
            "Port Gate Out Date & Time",
            "Transport Name",
        ]
        self.tree = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            self.tree.heading(c, text=c)
            width = 120
            if c in ("Importer Name", "Shipping Line", "Vessel Name"):
                width = 180
            if c == "id":
                width = 50
            self.tree.column(c, width=width, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        # vertical scrollbar
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.place(relx=1.0, rely=0, relheight=1.0, anchor='ne')

    # --- Data ops ---
    def form_to_row(self) -> dict:
        row = {}
        for key, widget in self.inputs.items():
            val = widget.get().strip()
            if key in DATE_FIELDS:
                val = parse_dateish(val)
            row[key] = val
        return row

    def validate_row(self, row: dict) -> bool:
        missing = [f for f in MANDATORY_FIELDS if not row.get(f)]
        if missing:
            messagebox.showwarning("Missing Data", f"Please fill mandatory fields: {', '.join(missing)}")
            return False
        return True

    def save_new(self):
        row = self.form_to_row()
        if not self.validate_row(row):
            return
        try:
            new_id = db_insert(row)
            self._update_combo_sources(row)
            self._load_table(select_id=new_id)
            messagebox.showinfo("Saved", "New record added.")
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save record: {e}")

    def update_selected(self):
        if self.selected_id is None:
            messagebox.showwarning("No selection", "Please select a row in the table first.")
            return
        row = self.form_to_row()
        if not self.validate_row(row):
            return
        try:
            db_update(self.selected_id, row)
            self._update_combo_sources(row)
            self._load_table(select_id=self.selected_id)
            messagebox.showinfo("Updated", "Record updated.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not update record: {e}")

    def delete_selected(self):
        if self.selected_id is None:
            messagebox.showwarning("No selection", "Please select a row to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete selected record? This cannot be undone."):
            return
        try:
            db_delete(self.selected_id)
            self.selected_id = None
            self._load_table()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete: {e}")

    def on_row_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        values = item["values"]
        # Map values back to form
        self.selected_id = int(values[0])
        keys = [
            "importer_name","cha","bl_no","bl_date","shipping_line","container_no","size","type",
            "vessel_name","rotation","arrival_date","igm_no","igm_date","item_no","smtp_no","smtp_date",
            "smtp_received_dt","port","seal_no","truck_number","port_gate_out_dt","transport_name"
        ]
        for key, val in zip(keys, values[1:]):
            if key in self.inputs:
                self.inputs[key].delete(0, tk.END)
                self.inputs[key].insert(0, val or "")

    def clear_form(self):
        self.selected_id = None
        for w in self.inputs.values():
            w.delete(0, tk.END)

    def apply_filters(self):
        where = []
        params: List[str] = []
        txt = self.filter_text.get().strip()
        if txt:
            like = f"%{txt}%"
            where.append("(importer_name LIKE ? OR shipping_line LIKE ? OR container_no LIKE ? OR vessel_name LIKE ? OR port LIKE ?)")
            params.extend([like, like, like, like, like])
        d1 = self.filter_from.get().strip()
        d2 = self.filter_to.get().strip()
        if d1:
            d1p = parse_dateish(d1)
            where.append("arrival_date >= ?")
            params.append(d1p)
        if d2:
            d2p = parse_dateish(d2)
            where.append("arrival_date <= ?")
            params.append(d2p)
        where_sql = " AND ".join(where)
        self._load_table(where_sql, tuple(params))

    def clear_filters(self):
        self.filter_text.delete(0, tk.END)
        self.filter_from.delete(0, tk.END)
        self.filter_to.delete(0, tk.END)
        self._load_table()

    def _load_table(self, where: str = "", params: Tuple = (), select_id: Optional[int] = None):
        columns, rows = db_select(where, params, order="id DESC")
        # Clear
        for i in self.tree.get_children():
            self.tree.delete(i)
        # Refill
        col_index = {c: i for i, c in enumerate(columns)}
        for r in rows:
            # Build display tuple in the same order as our Treeview columns
            values = [
                r[col_index["id"]],
                r[col_index["importer_name"]],
                r[col_index["cha"]],
                r[col_index["bl_no"]],
                r[col_index["bl_date"]],
                r[col_index["shipping_line"]],
                r[col_index["container_no"]],
                r[col_index["size"]],
                r[col_index["type"]],
                r[col_index["vessel_name"]],
                r[col_index["rotation"]],
                r[col_index["arrival_date"]],
                r[col_index["igm_no"]],
                r[col_index["igm_date"]],
                r[col_index["item_no"]],
                r[col_index["smtp_no"]],
                r[col_index["smtp_date"]],
                r[col_index["smtp_received_dt"]],
                r[col_index["port"]],
                r[col_index["seal_no"]],
                r[col_index["truck_number"]],
                r[col_index["port_gate_out_dt"]],
                r[col_index["transport_name"]],
            ]
            iid = self.tree.insert("", tk.END, values=values)
            if select_id is not None and r[col_index["id"]] == select_id:
                self.tree.selection_set(iid)

    def _update_combo_sources(self, row: dict):
        # Extend dropdown options with newly saved values
        for k in ("port", "size", "type", "shipping_line", "cha", "transport_name"):
            v = row.get(k)
            if v and v not in self.combo_sources.get(k, []):
                self.combo_sources.setdefault(k, []).append(v)
                widget = self.inputs.get(k)
                if isinstance(widget, ttk.Combobox):
                    widget["values"] = self.combo_sources[k]

    def export_excel(self):
        if pd is None:
            messagebox.showerror("Missing dependency", "pandas is required for export. Run: pip install pandas openpyxl")
            return
        # Collect filtered rows for export
        where = []
        params: List[str] = []
        txt = self.filter_text.get().strip()
        if txt:
            like = f"%{txt}%"
            where.append("(importer_name LIKE ? OR shipping_line LIKE ? OR container_no LIKE ? OR vessel_name LIKE ? OR port LIKE ?)")
            params.extend([like, like, like, like, like])
        d1 = self.filter_from.get().strip()
        d2 = self.filter_to.get().strip()
        if d1:
            where.append("arrival_date >= ?")
            params.append(parse_dateish(d1))
        if d2:
            where.append("arrival_date <= ?")
            params.append(parse_dateish(d2))
        where_sql = " AND ".join(where)
        columns, rows = db_select(where_sql, tuple(params), order="id ASC")
        if not rows:
            if not messagebox.askyesno("No rows", "No rows match current filter. Export ALL data instead?"):
                return
            columns, rows = db_select(order="id ASC")
        # Build DataFrame in report order
        col_index = {c: i for i, c in enumerate(columns)}

        def pick(col):
            return [r[col_index[col]] if r[col_index[col]] is not None else "" for r in rows]

        data = {
            "Importer Name": pick("importer_name"),
            "CHA": pick("cha"),
            "B/L no": pick("bl_no"),
            "B/L Date": pick("bl_date"),
            "Shipping Line": pick("shipping_line"),
            "Container No": pick("container_no"),
            "SIZE": pick("size"),
            "Type": pick("type"),
            "Vessel Name": pick("vessel_name"),
            "Rotation": pick("rotation"),
            "Arrival Date": pick("arrival_date"),
            "IGM no": pick("igm_no"),
            "IGM Date": pick("igm_date"),
            "Item no": pick("item_no"),
            "SMTP no": pick("smtp_no"),
            "SMTP Date": pick("smtp_date"),
            "SMTP Received Date & Time": pick("smtp_received_dt"),
            "Port": pick("port"),
            "Seal No": pick("seal_no"),
            "Truck Number": pick("truck_number"),
            "Port Gate Out Date & Time": pick("port_gate_out_dt"),
            "Transport Name": pick("transport_name"),
        }
        df = pd.DataFrame(data)
        # Insert Sr.no as first column (1..n)
        df.insert(0, "Sr.no", range(1, len(df) + 1))

        # Ask save path
        default_name = f"TOTAL IMP Report {datetime.now().strftime('%Y-%m-%d %H%M')}.xlsx"
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=default_name,
                                            filetypes=[("Excel", ".xlsx")])
        if not path:
            return
        try:
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="TOTAL IMP", index=False)
            messagebox.showinfo("Exported", f"Excel report saved:\n{path}")
        except Exception as e:
            messagebox.showerror("Export error", f"Could not write Excel: {e}")


def main():
    init_db()
    root = tk.Tk()
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except Exception:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
