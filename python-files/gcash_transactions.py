
"""
gcash_transactions.py
Simple offline app to save GCash Cash In / Cash Out transactions into local SQLite DB.
Run with: python gcash_transactions.py
Convert to exe: see instructions below (PyInstaller).
"""

import sqlite3
import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DB_FILE = "transactions.db"

# ---- Database helpers ----
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id TEXT,
        full_name TEXT,
        contact TEXT,
        address TEXT,
        txn_type TEXT,
        amount REAL,
        reference TEXT,
        datetime TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_transaction(data):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO transactions (client_id, full_name, contact, address, txn_type, amount, reference, datetime)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

def query_transactions(filter_sql="", params=()):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    q = "SELECT id, client_id, full_name, contact, address, txn_type, amount, reference, datetime FROM transactions"
    if filter_sql:
        q += " WHERE " + filter_sql
    q += " ORDER BY id DESC LIMIT 500"
    cur.execute(q, params)
    rows = cur.fetchall()
    conn.close()
    return rows

# ---- UI ----
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GCash Transactions - Offline")
        self.geometry("980x640")
        self.resizable(True, True)
        self.create_widgets()
        init_db()
        self.load_transactions()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        # --- Left: form ---
        left = ttk.Frame(frm)
        left.pack(side="left", fill="y", padx=(0,10))

        ttk.Label(left, text="Client ID:").grid(row=0, column=0, sticky="w")
        self.e_client_id = ttk.Entry(left, width=30)
        self.e_client_id.grid(row=0, column=1, pady=3)

        ttk.Label(left, text="Full Name:").grid(row=1, column=0, sticky="w")
        self.e_full_name = ttk.Entry(left, width=30)
        self.e_full_name.grid(row=1, column=1, pady=3)

        ttk.Label(left, text="Contact #:").grid(row=2, column=0, sticky="w")
        self.e_contact = ttk.Entry(left, width=30)
        self.e_contact.grid(row=2, column=1, pady=3)

        ttk.Label(left, text="Address:").grid(row=3, column=0, sticky="nw")
        self.t_address = tk.Text(left, width=22, height=4)
        self.t_address.grid(row=3, column=1, pady=3)

        ttk.Label(left, text="Transaction Type:").grid(row=4, column=0, sticky="w")
        self.txn_type = ttk.Combobox(left, values=["Cash In", "Cash Out"], state="readonly", width=28)
        self.txn_type.current(0)
        self.txn_type.grid(row=4, column=1, pady=3)

        ttk.Label(left, text="Amount (PHP):").grid(row=5, column=0, sticky="w")
        self.e_amount = ttk.Entry(left, width=30)
        self.e_amount.grid(row=5, column=1, pady=3)

        ttk.Label(left, text="Reference #:").grid(row=6, column=0, sticky="w")
        self.e_reference = ttk.Entry(left, width=30)
        self.e_reference.grid(row=6, column=1, pady=3)

        btn_save = ttk.Button(left, text="Save Transaction", command=self.on_save)
        btn_save.grid(row=7, column=0, columnspan=2, pady=(10, 5), sticky="ew")

        ttk.Separator(left, orient="horizontal").grid(row=8, column=0, columnspan=2, sticky="ew", pady=8)

        # Quick export
        btn_export = ttk.Button(left, text="Export Visible to CSV", command=self.on_export)
        btn_export.grid(row=9, column=0, columnspan=2, sticky="ew")

        # --- Right: list & search ---
        right = ttk.Frame(frm)
        right.pack(side="left", fill="both", expand=True)

        # Search bar
        search_frame = ttk.Frame(right)
        search_frame.pack(fill="x", pady=(0,6))
        ttk.Label(search_frame, text="Search (Client ID / Name / Reference):").pack(side="left")
        self.e_search = ttk.Entry(search_frame, width=40)
        self.e_search.pack(side="left", padx=6)
        btn_search = ttk.Button(search_frame, text="Search", command=self.on_search)
        btn_search.pack(side="left", padx=(0,6))
        btn_clear = ttk.Button(search_frame, text="Clear", command=self.on_clear_search)
        btn_clear.pack(side="left")

        # Treeview
        columns = ("id","client_id","full_name","contact","address","txn_type","amount","reference","datetime")
        self.tree = ttk.Treeview(right, columns=columns, show="headings", height=20)
        for col in columns:
            self.tree.heading(col, text=col.replace("_"," ").title())
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("client_id", width=100)
        self.tree.column("full_name", width=160)
        self.tree.column("contact", width=110)
        self.tree.column("address", width=180)
        self.tree.column("txn_type", width=80, anchor="center")
        self.tree.column("amount", width=90, anchor="e")
        self.tree.column("reference", width=110)
        self.tree.column("datetime", width=140)

        self.tree.pack(fill="both", expand=True)

        # Bottom info
        bottom = ttk.Frame(right)
        bottom.pack(fill="x", pady=(6,0))
        self.lbl_status = ttk.Label(bottom, text="Ready")
        self.lbl_status.pack(side="left")

    def on_save(self):
        cid = self.e_client_id.get().strip()
        name = self.e_full_name.get().strip()
        contact = self.e_contact.get().strip()
        address = self.t_address.get("1.0", "end").strip()
        txn = self.txn_type.get()
        amt = self.e_amount.get().strip()
        ref = self.e_reference.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Full Name is required.")
            return
        try:
            amount_val = float(amt)
        except:
            messagebox.showwarning("Validation", "Enter a valid numeric amount.")
            return
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_transaction((cid, name, contact, address, txn, amount_val, ref, dt))
        self.lbl_status.config(text=f"Saved transaction for {name} at {dt}")
        self.clear_form()
        self.load_transactions()

    def clear_form(self):
        self.e_client_id.delete(0, "end")
        self.e_full_name.delete(0, "end")
        self.e_contact.delete(0, "end")
        self.t_address.delete("1.0", "end")
        self.txn_type.current(0)
        self.e_amount.delete(0, "end")
        self.e_reference.delete(0, "end")

    def load_transactions(self, filter_sql="", params=()):
        rows = query_transactions(filter_sql, params)
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            # Format amount to 2 decimal places
            r_list = list(r)
            r_list[6] = f"{r_list[6]:.2f}"
            self.tree.insert("", "end", values=r_list)
        self.lbl_status.config(text=f"Loaded {len(rows)} records (most recent 500)")

    def on_search(self):
        term = self.e_search.get().strip()
        if not term:
            self.load_transactions()
            return
        # search in client_id, full_name, reference
        filter_sql = "(client_id LIKE ? OR full_name LIKE ? OR reference LIKE ?)"
        like = f"%{term}%"
        self.load_transactions(filter_sql, (like, like, like))

    def on_clear_search(self):
        self.e_search.delete(0, "end")
        self.load_transactions()

    def on_export(self):
        # Export currently visible rows in treeview
        items = self.tree.get_children()
        if not items:
            messagebox.showinfo("Export", "No records to export.")
            return
        default_name = f"transactions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=default_name, filetypes=[("CSV files","*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id","client_id","full_name","contact","address","txn_type","amount","reference","datetime"])
            for iid in items:
                row = self.tree.item(iid, "values")
                writer.writerow(row)
        messagebox.showinfo("Export", f"Exported {len(items)} rows to:\n{path}")
        self.lbl_status.config(text=f"Exported {len(items)} rows to {path}")

if __name__ == "__main__":
    init_db()
    app = App()
    app.mainloop()
