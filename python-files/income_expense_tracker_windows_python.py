#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Income & Expense Tracker — Windows-friendly Python app (Tkinter + SQLite)
----------------------------------------------------------------------------
NEW (Oct 2025)
- CSV Export/Import for transactions (date,type,category,amount,note)
- Configurable currency: RON or EUR (affects UI formatting)

Core Features
- Overview tab: shows balances for current month and current year, plus quick stats
- Transactions tab: add/edit/delete incomes & expenses with categories and notes
- Calendar tab: month view with per-day totals (income, expense, balance)
- Categories tab: manage income/expense categories (add/delete)
- Data stored locally in SQLite (DB auto-created). Safe paths & schema migration.
- Single-file app; no external packages required (uses Python stdlib + Tkinter)

Build to .exe (PyInstaller)
- pip install pyinstaller
- pyinstaller --noconsole --onefile --name IncomeExpenseTracker income_expense_tracker.py
  -> dist/IncomeExpenseTracker.exe

Optional installer (Inno Setup)
- Use Inno Setup to wrap the EXE into a proper Windows installer.

Author: ChatGPT (for Iulian M.)
License: MIT
"""

import calendar
import csv
import datetime as dt
import os
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

APP_NAME = "Income & Expense Tracker"
DB_FILENAME = "income_expense_tracker.db"

CURRENCIES = {
    "RON": {"symbol": "RON", "fmt": "{:,.2f} RON"},
    "EUR": {"symbol": "€",   "fmt": "{:,.2f} €"},
}
DEFAULT_CURRENCY = "RON"

# --------------------------- Utilities & Persistence ---------------------------

def app_data_dir() -> Path:
    """Return a writable app data directory per-OS."""
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        p = Path(base) / "IulianM" / "IncomeExpenseTracker"
    else:
        p = Path.home() / ".income_expense_tracker"
    p.mkdir(parents=True, exist_ok=True)
    return p

DB_PATH = app_data_dir() / DB_FILENAME

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income','expense')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(name, type)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_date TEXT NOT NULL,                 -- YYYY-MM-DD
    amount REAL NOT NULL,                  -- positive number
    type TEXT NOT NULL CHECK(type IN ('income','expense')),
    category_id INTEGER NOT NULL,
    note TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT,
    FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE RESTRICT
);
"""

DEFAULT_CATEGORIES = {
    "income": ["Salary","Bonus","Business","Dividends","Gifts","Other"],
    "expense": ["Food","Rent","Utilities","Transport","Health","Education","Entertainment","Clothing","Savings","Other"]
}


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA_SQL)
        # Seed default categories if table empty
        cur = conn.execute("SELECT COUNT(*) AS c FROM categories")
        if cur.fetchone()[0] == 0:
            for t, names in DEFAULT_CATEGORIES.items():
                for n in names:
                    try:
                        conn.execute("INSERT INTO categories(name, type) VALUES (?,?)", (n, t))
                    except sqlite3.IntegrityError:
                        pass
        # Seed default currency if not set
        cur = conn.execute("SELECT value FROM settings WHERE key='currency'")
        row = cur.fetchone()
        if not row:
            conn.execute("INSERT INTO settings(key,value) VALUES ('currency', ?)", (DEFAULT_CURRENCY,))
        conn.commit()

# Settings helpers

def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    with get_conn() as conn:
        cur = conn.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cur.fetchone()
        return row[0] if row else default


def set_setting(key: str, value: str) -> None:
    with get_conn() as conn:
        conn.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
        conn.commit()

# --------------------------- Domain Logic ---------------------------

@dataclass
class Category:
    id: int
    name: str
    type: str  # income|expense

@dataclass
class Transaction:
    id: int
    tx_date: str
    amount: float
    type: str
    category_id: int
    note: str


def list_categories(cat_type: Optional[str] = None) -> List[Category]:
    with get_conn() as conn:
        if cat_type:
            cur = conn.execute("SELECT id,name,type FROM categories WHERE type=? ORDER BY name", (cat_type,))
        else:
            cur = conn.execute("SELECT id,name,type FROM categories ORDER BY type,name")
        return [Category(*row) for row in cur.fetchall()]


def ensure_category(name: str, cat_type: str) -> int:
    name = name.strip()
    if not name:
        raise ValueError("Category name cannot be empty")
    with get_conn() as conn:
        # try fetch
        cur = conn.execute("SELECT id FROM categories WHERE name=? AND type=?", (name, cat_type))
        r = cur.fetchone()
        if r:
            return int(r[0])
        # insert
        conn.execute("INSERT INTO categories(name, type) VALUES (?,?)", (name, cat_type))
        conn.commit()
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def add_category(name: str, cat_type: str):
    ensure_category(name, cat_type)


def delete_category(cat_id: int) -> bool:
    """Return True if deleted, False if constrained by existing transactions."""
    with get_conn() as conn:
        cur = conn.execute("SELECT COUNT(*) FROM transactions WHERE category_id=?", (cat_id,))
        if cur.fetchone()[0] > 0:
            return False
        conn.execute("DELETE FROM categories WHERE id=?", (cat_id,))
        conn.commit()
        return True


def add_transaction(tx_date: str, amount: float, tx_type: str, category_id: int, note: str = ""):
    if amount <= 0:
        raise ValueError("Amount must be positive")
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO transactions(tx_date, amount, type, category_id, note) VALUES (?,?,?,?,?)",
            (tx_date, amount, tx_type, category_id, note),
        )
        conn.commit()


def update_transaction(tx_id: int, tx_date: str, amount: float, tx_type: str, category_id: int, note: str = ""):
    if amount <= 0:
        raise ValueError("Amount must be positive")
    with get_conn() as conn:
        conn.execute(
            "UPDATE transactions SET tx_date=?, amount=?, type=?, category_id=?, note=?, updated_at=datetime('now') WHERE id=?",
            (tx_date, amount, tx_type, category_id, note, tx_id),
        )
        conn.commit()


def delete_transaction(tx_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM transactions WHERE id=?", (tx_id,))
        conn.commit()


def totals_for_range(start_date: str, end_date: str) -> Tuple[float, float, float]:
    """Return (income, expense, balance) for date range inclusive."""
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT type, SUM(amount) AS s FROM transactions WHERE tx_date BETWEEN ? AND ? GROUP BY type",
            (start_date, end_date),
        )
        inc = exp = 0.0
        for row in cur.fetchall():
            if row[0] == "income":
                inc = row[1] or 0.0
            else:
                exp = row[1] or 0.0
        return inc, exp, inc - exp


def daily_totals_for_month(year: int, month: int) -> List[Tuple[int, float, float, float]]:
    """Return list of (day, income, expense, balance)."""
    _, last_day = calendar.monthrange(year, month)
    results = [(d, 0.0, 0.0, 0.0) for d in range(1, last_day + 1)]
    start = dt.date(year, month, 1).isoformat()
    end = dt.date(year, month, last_day).isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT tx_date, type, SUM(amount) AS s FROM transactions WHERE tx_date BETWEEN ? AND ? GROUP BY tx_date, type",
            (start, end),
        )
        day_map = {d: [0.0, 0.0] for d in range(1, last_day + 1)}
        for tx_date, ttype, s in cur.fetchall():
            d = int(tx_date.split("-")[-1])
            if ttype == "income":
                day_map[d][0] = s or 0.0
            else:
                day_map[d][1] = s or 0.0
        for d in range(1, last_day + 1):
            inc, exp = day_map[d]
            results[d - 1] = (d, inc, exp, inc - exp)
    return results

# --------------------------- UI ---------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1040x700")
        self.minsize(940, 640)
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # Currency state
        self.currency_code = get_setting("currency", DEFAULT_CURRENCY)
        self.currency_fmt = CURRENCIES.get(self.currency_code, CURRENCIES[DEFAULT_CURRENCY])["fmt"]

        self._make_menu()
        self._build()
        self._refresh_all()

    # ---------------- Menu ----------------
    def _make_menu(self):
        menubar = tk.Menu(self)
        filem = tk.Menu(menubar, tearoff=0)
        filem.add_command(label="Export CSV…", command=self._export_csv)
        filem.add_command(label="Import CSV…", command=self._import_csv)
        filem.add_separator()
        filem.add_command(label="Backup DB", command=self._backup_db)
        filem.add_separator()
        filem.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=filem)

        settingsm = tk.Menu(menubar, tearoff=0)
        currm = tk.Menu(settingsm, tearoff=0)
        currm.add_command(label="Set Currency: RON", command=lambda: self._set_currency("RON"))
        currm.add_command(label="Set Currency: EUR", command=lambda: self._set_currency("EUR"))
        settingsm.add_cascade(label=f"Currency (current: {self.currency_code})", menu=currm)
        menubar.add_cascade(label="Settings", menu=settingsm)

        helpm = tk.Menu(menubar, tearoff=0)
        helpm.add_command(label="About", command=self._about)
        menubar.add_cascade(label="Help", menu=helpm)
        self.config(menu=menubar)
        self._menubar = menubar
        self._settings_menu = settingsm

    def _backup_db(self):
        try:
            ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = DB_PATH.with_name(DB_PATH.stem + f"-backup-{ts}" + DB_PATH.suffix)
            with open(DB_PATH, "rb") as src, open(backup, "wb") as dst:
                dst.write(src.read())
            messagebox.showinfo("Backup created", f"Backup saved to:
{backup}")
        except Exception as e:
            messagebox.showerror("Backup failed", str(e))

    def _about(self):
        messagebox.showinfo(
            "About",
            f"{APP_NAME}
Simple personal finance tracker (Tkinter + SQLite).
Database: {DB_PATH}
Currency: {self.currency_code}",
        )

    # ---------------- Layout ----------------
    def _build(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Overview Tab
        self.tab_overview = ttk.Frame(notebook, padding=12)
        notebook.add(self.tab_overview, text="Overview")
        self._build_overview(self.tab_overview)

        # Transactions Tab
        self.tab_tx = ttk.Frame(notebook, padding=12)
        notebook.add(self.tab_tx, text="Transactions")
        self._build_transactions(self.tab_tx)

        # Calendar Tab
        self.tab_calendar = ttk.Frame(notebook, padding=12)
        notebook.add(self.tab_calendar, text="Calendar")
        self._build_calendar(self.tab_calendar)

        # Categories Tab
        self.tab_categories = ttk.Frame(notebook, padding=12)
        notebook.add(self.tab_categories, text="Categories")
        self._build_categories(self.tab_categories)

    # ---------------- Utility (format amounts) ----------------
    def _fmt(self, value: float) -> str:
        try:
            return self.currency_fmt.format(value)
        except Exception:
            return f"{value:,.2f} {self.currency_code}"

    def _refresh_all(self):
        self._refresh_overview()
        self._refresh_tx_list()
        self._refresh_calendar()
        self._refresh_categories()

    # ---------------- Overview ----------------
    def _build_overview(self, parent):
        self.ov_month_val = tk.StringVar()
        self.ov_year_val = tk.StringVar()
        self.ov_totals_val = tk.StringVar()

        frm = ttk.Frame(parent)
        frm.pack(fill=tk.X)

        # Current month stats
        card1 = ttk.Labelframe(frm, text="Current Month", padding=12)
        card1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        ttk.Label(card1, textvariable=self.ov_month_val, font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)

        # Current year stats
        card2 = ttk.Labelframe(frm, text="Current Year", padding=12)
        card2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 6))
        ttk.Label(card2, textvariable=self.ov_year_val, font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)

        # Totals all time
        card3 = ttk.Labelframe(frm, text="All Time", padding=12)
        card3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))
        ttk.Label(card3, textvariable=self.ov_totals_val, font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)

    def _refresh_overview(self):
        today = dt.date.today()
        start_m = today.replace(day=1).isoformat()
        last_day = calendar.monthrange(today.year, today.month)[1]
        end_m = today.replace(day=last_day).isoformat()
        inc, exp, bal = totals_for_range(start_m, end_m)
        self.ov_month_val.set(f"Income: {self._fmt(inc)} | Expense: {self._fmt(exp)} | Balance: {self._fmt(bal)}")

        start_y = dt.date(today.year, 1, 1).isoformat()
        end_y = dt.date(today.year, 12, 31).isoformat()
        incy, expy, baly = totals_for_range(start_y, end_y)
        self.ov_year_val.set(f"Income: {self._fmt(incy)} | Expense: {self._fmt(expy)} | Balance: {self._fmt(baly)}")

        # all time
        with get_conn() as conn:
            cur = conn.execute("SELECT type, SUM(amount) FROM transactions GROUP BY type")
            inca = expa = 0.0
            for t, s in cur.fetchall():
                if t == "income": inca = s or 0.0
                else: expa = s or 0.0
        self.ov_totals_val.set(f"Income: {self._fmt(inca)} | Expense: {self._fmt(expa)} | Balance: {self._fmt(inca-expa)}")

    # ---------------- Transactions ----------------
    def _build_transactions(self, parent):
        # Top form
        form = ttk.Labelframe(parent, text="Add / Edit Transaction", padding=10)
        form.pack(fill=tk.X)

        self.tx_id_editing: Optional[int] = None

        ttk.Label(form, text="Date (YYYY-MM-DD)").grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        self.ent_tx_date = ttk.Entry(form, width=14)
        self.ent_tx_date.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        self.ent_tx_date.insert(0, dt.date.today().isoformat())

        ttk.Label(form, text="Type").grid(row=0, column=2, sticky=tk.W, padx=4, pady=4)
        self.cmb_tx_type = ttk.Combobox(form, values=["income","expense"], state="readonly", width=10)
        self.cmb_tx_type.grid(row=0, column=3, sticky=tk.W, padx=4, pady=4)
        self.cmb_tx_type.set("expense")

        ttk.Label(form, text="Category").grid(row=0, column=4, sticky=tk.W, padx=4, pady=4)
        self.cmb_tx_category = ttk.Combobox(form, values=[], state="readonly", width=18)
        self.cmb_tx_category.grid(row=0, column=5, sticky=tk.W, padx=4, pady=4)

        ttk.Label(form, text="Amount").grid(row=0, column=6, sticky=tk.W, padx=4, pady=4)
        self.ent_tx_amount = ttk.Entry(form, width=12)
        self.ent_tx_amount.grid(row=0, column=7, sticky=tk.W, padx=4, pady=4)

        ttk.Label(form, text="Note").grid(row=0, column=8, sticky=tk.W, padx=4, pady=4)
        self.ent_tx_note = ttk.Entry(form, width=30)
        self.ent_tx_note.grid(row=0, column=9, sticky=tk.W, padx=4, pady=4)

        self.btn_save_tx = ttk.Button(form, text="Save", command=self._on_save_tx)
        self.btn_save_tx.grid(row=0, column=10, padx=4, pady=4)
        self.btn_clear_tx = ttk.Button(form, text="Clear", command=self._clear_tx_form)
        self.btn_clear_tx.grid(row=0, column=11, padx=4, pady=4)

        # Filters
        flt = ttk.Labelframe(parent, text="Filter", padding=10)
        flt.pack(fill=tk.X, pady=(8, 4))
        ttk.Label(flt, text="From").grid(row=0, column=0, padx=4, pady=4)
        self.ent_from = ttk.Entry(flt, width=14)
        self.ent_from.grid(row=0, column=1)
        ttk.Label(flt, text="To").grid(row=0, column=2, padx=4)
        self.ent_to = ttk.Entry(flt, width=14)
        self.ent_to.grid(row=0, column=3)
        ttk.Button(flt, text="Apply", command=self._refresh_tx_list).grid(row=0, column=4, padx=6)
        ttk.Button(flt, text="This Month", command=self._set_this_month_filter).grid(row=0, column=5, padx=6)

        # Table
        self.tree = ttk.Treeview(parent, columns=("id","date","type","category","amount","note"), show="headings", height=16)
        self.tree.pack(fill=tk.BOTH, expand=True)
        for c, w in zip(["id","date","type","category","amount","note"],[60,110,80,180,140,400]):
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=w, anchor=tk.W if c!="amount" else tk.E)
        self.tree.bind("<Double-1>", self._on_tree_double)

        # Buttons
        btns = ttk.Frame(parent)
        btns.pack(fill=tk.X, pady=6)
        ttk.Button(btns, text="Edit Selected", command=self._edit_selected).pack(side=tk.LEFT)
        ttk.Button(btns, text="Delete Selected", command=self._delete_selected).pack(side=tk.LEFT, padx=8)

        self.cmb_tx_type.bind("<<ComboboxSelected>>", lambda e: self._load_categories_for_type())
        self._load_categories_for_type()

    def _set_this_month_filter(self):
        today = dt.date.today()
        start = today.replace(day=1)
        last_day = calendar.monthrange(today.year, today.month)[1]
        end = today.replace(day=last_day)
        self.ent_from.delete(0, tk.END); self.ent_from.insert(0, start.isoformat())
        self.ent_to.delete(0, tk.END); self.ent_to.insert(0, end.isoformat())
        self._refresh_tx_list()

    def _load_categories_for_type(self):
        t = self.cmb_tx_type.get()
        cats = list_categories(t)
        self._cat_map = {f"{c.name}": c.id for c in cats}
        self.cmb_tx_category["values"] = list(self._cat_map.keys())
        if cats:
            self.cmb_tx_category.set(cats[0].name)

    def _on_save_tx(self):
        try:
            date = self.ent_tx_date.get().strip()
            amount = float(self.ent_tx_amount.get().strip())
            ttype = self.cmb_tx_type.get()
            cat_name = self.cmb_tx_category.get()
            if cat_name not in self._cat_map:
                raise ValueError("Select a valid category")
            cat_id = self._cat_map[cat_name]
            note = self.ent_tx_note.get().strip()
            # validate date
            dt.date.fromisoformat(date)

            if self.tx_id_editing is None:
                add_transaction(date, amount, ttype, cat_id, note)
            else:
                update_transaction(self.tx_id_editing, date, amount, ttype, cat_id, note)
            self._clear_tx_form()
            self._refresh_all()
        except Exception as e:
            messagebox.showerror("Invalid data", str(e))

    def _clear_tx_form(self):
        self.tx_id_editing = None
        self.ent_tx_date.delete(0, tk.END); self.ent_tx_date.insert(0, dt.date.today().isoformat())
        self.cmb_tx_type.set("expense"); self._load_categories_for_type()
        self.ent_tx_amount.delete(0, tk.END)
        self.ent_tx_note.delete(0, tk.END)

    def _refresh_tx_list(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        f = self.ent_from.get().strip() or "0001-01-01"
        t = self.ent_to.get().strip() or "9999-12-31"
        try:
            # validate dates if provided
            if f != "0001-01-01": dt.date.fromisoformat(f)
            if t != "9999-12-31": dt.date.fromisoformat(t)
        except Exception as e:
            messagebox.showerror("Invalid filter dates", str(e))
            return
        rows = []
        with get_conn() as conn:
            cur = conn.execute(
                """
                SELECT tx.id, tx.tx_date, tx.type, c.name as cat, tx.amount, COALESCE(tx.note,'')
                FROM transactions tx
                JOIN categories c ON c.id = tx.category_id
                WHERE tx.tx_date BETWEEN ? AND ?
                ORDER BY tx.tx_date DESC, tx.id DESC
                """,
                (f, t),
            )
            rows = cur.fetchall()
        for row in rows:
            self.tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], self._fmt(row[4]), row[5]))

    def _on_tree_double(self, _event):
        self._edit_selected()

    def _edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        id_, date, ttype, cat, amount, note = item["values"]
        self.tx_id_editing = int(id_)
        self.ent_tx_date.delete(0, tk.END); self.ent_tx_date.insert(0, date)
        self.cmb_tx_type.set(ttype); self._load_categories_for_type()
        self.cmb_tx_category.set(cat)
        # strip currency from displayed amount
        try:
            amt_clean = str(amount).replace("€"," ").replace("RON"," ").replace(",", "").strip()
            self.ent_tx_amount.delete(0, tk.END); self.ent_tx_amount.insert(0, amt_clean)
        except Exception:
            self.ent_tx_amount.delete(0, tk.END); self.ent_tx_amount.insert(0, "0")
        self.ent_tx_note.delete(0, tk.END); self.ent_tx_note.insert(0, note)

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        id_ = int(item["values"][0])
        if messagebox.askyesno("Confirm delete", "Delete selected transaction?"):
            delete_transaction(id_)
            self._refresh_all()

    # ---------------- CSV Export/Import ----------------
    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            title="Export Transactions to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files","*.csv"), ("All files","*.*")],
            initialfile=f"transactions-{dt.date.today().isoformat()}.csv",
        )
        if not path:
            return
        try:
            with get_conn() as conn:
                cur = conn.execute(
                    """
                    SELECT tx.tx_date, tx.type, c.name as category, tx.amount, COALESCE(tx.note,'')
                    FROM transactions tx
                    JOIN categories c ON c.id = tx.category_id
                    ORDER BY tx.tx_date ASC, tx.id ASC
                    """
                )
                rows = cur.fetchall()
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["date","type","category","amount","note"])  # header
                for r in rows:
                    w.writerow([r[0], r[1], r[2], f"{r[3]:.2f}", r[4]])
            messagebox.showinfo("Export complete", f"Saved to:
{path}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def _import_csv(self):
        path = filedialog.askopenfilename(
            title="Import Transactions from CSV",
            filetypes=[("CSV files","*.csv"), ("All files","*.*")],
        )
        if not path:
            return
        added = skipped = 0
        try:
            with open(path, "r", newline="", encoding="utf-8") as f:
                rdr = csv.DictReader(f)
                required = {"date","type","category","amount","note"}
                if not required.issubset({c.lower() for c in rdr.fieldnames or []}):
                    raise ValueError("CSV must have headers: date,type,category,amount,note")
                for row in rdr:
                    try:
                        date = (row.get("date") or row.get("Date") or "").strip()
                        ttype = (row.get("type") or row.get("Type") or "").strip().lower()
                        category = (row.get("category") or row.get("Category") or "").strip()
                        amount_str = (row.get("amount") or row.get("Amount") or "0").strip()
                        note = (row.get("note") or row.get("Note") or "").strip()

                        # validate
                        dt.date.fromisoformat(date)
                        if ttype not in ("income","expense"):
                            raise ValueError("type must be income or expense")
                        # parse amount (strip symbols)
                        amount_str = amount_str.replace("€"," ").replace("RON"," ")
                        amount = float(amount_str.replace(",","."))
                        if amount <= 0:
                            raise ValueError("amount must be > 0")
                        cat_id = ensure_category(category, ttype)
                        add_transaction(date, amount, ttype, cat_id, note)
                        added += 1
                    except Exception:
                        skipped += 1
                        continue
            self._refresh_all()
            messagebox.showinfo("Import result", f"Imported: {added}
Skipped: {skipped}")
        except Exception as e:
            messagebox.showerror("Import failed", str(e))

    # ---------------- Calendar ----------------
    def _build_calendar(self, parent):
        top = ttk.Frame(parent)
        top.pack(fill=tk.X)
        self.spin_year = tk.Spinbox(top, from_=2000, to=2100, width=6, command=self._refresh_calendar)
        self.spin_month = tk.Spinbox(top, from_=1, to=12, width=4, command=self._refresh_calendar)
        today = dt.date.today()
        self.spin_year.delete(0, tk.END); self.spin_year.insert(0, today.year)
        self.spin_month.delete(0, tk.END); self.spin_month.insert(0, today.month)
        ttk.Label(top, text="Year").pack(side=tk.LEFT, padx=6)
        self.spin_year.pack(side=tk.LEFT)
        ttk.Label(top, text="Month").pack(side=tk.LEFT, padx=6)
        self.spin_month.pack(side=tk.LEFT)
        ttk.Button(top, text="Today", command=self._calendar_to_today).pack(side=tk.LEFT, padx=8)

        self.calendar_table = ttk.Treeview(parent, columns=("day","income","expense","balance"), show="headings", height=20)
        self.calendar_table.pack(fill=tk.BOTH, expand=True, pady=8)
        for c, w, anchor in [("day",70, tk.CENTER), ("income",180, tk.E), ("expense",180, tk.E), ("balance",180, tk.E)]:
            self.calendar_table.heading(c, text=c.title())
            self.calendar_table.column(c, width=w, anchor=anchor)

    def _calendar_to_today(self):
        today = dt.date.today()
        self.spin_year.delete(0, tk.END); self.spin_year.insert(0, today.year)
        self.spin_month.delete(0, tk.END); self.spin_month.insert(0, today.month)
        self._refresh_calendar()

    def _refresh_calendar(self):
        for r in self.calendar_table.get_children():
            self.calendar_table.delete(r)
        try:
            year = int(self.spin_year.get())
            month = int(self.spin_month.get())
        except ValueError:
            return
        data = daily_totals_for_month(year, month)
        for day, inc, exp, bal in data:
            self.calendar_table.insert("", tk.END, values=(day, self._fmt(inc), self._fmt(exp), self._fmt(bal)))

    # ---------------- Categories ----------------
    def _build_categories(self, parent):
        frm = ttk.Frame(parent)
        frm.pack(fill=tk.BOTH, expand=True)

        # Income categories
        inc_frame = ttk.Labelframe(frm, text="Income Categories", padding=10)
        inc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,6))
        self.lst_inc = tk.Listbox(inc_frame, height=14)
        self.lst_inc.pack(fill=tk.BOTH, expand=True)
        inc_add = ttk.Frame(inc_frame)
        inc_add.pack(fill=tk.X, pady=6)
        self.ent_inc_cat = ttk.Entry(inc_add)
        self.ent_inc_cat.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(inc_add, text="Add", command=lambda: self._add_cat("income")).pack(side=tk.LEFT, padx=6)
        ttk.Button(inc_add, text="Delete Selected", command=lambda: self._del_cat("income")).pack(side=tk.LEFT)

        # Expense categories
        exp_frame = ttk.Labelframe(frm, text="Expense Categories", padding=10)
        exp_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6,0))
        self.lst_exp = tk.Listbox(exp_frame, height=14)
        self.lst_exp.pack(fill=tk.BOTH, expand=True)
        exp_add = ttk.Frame(exp_frame)
        exp_add.pack(fill=tk.X, pady=6)
        self.ent_exp_cat = ttk.Entry(exp_add)
        self.ent_exp_cat.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(exp_add, text="Add", command=lambda: self._add_cat("expense")).pack(side=tk.LEFT, padx=6)
        ttk.Button(exp_add, text="Delete Selected", command=lambda: self._del_cat("expense")).pack(side=tk.LEFT)

    def _refresh_categories(self):
        self.lst_inc.delete(0, tk.END)
        self.lst_exp.delete(0, tk.END)
        for c in list_categories("income"):
            self.lst_inc.insert(tk.END, f"{c.id}: {c.name}")
        for c in list_categories("expense"):
            self.lst_exp.insert(tk.END, f"{c.id}: {c.name}")
        # also update combo in transactions
        self._load_categories_for_type()

    def _add_cat(self, t: str):
        name = (self.ent_inc_cat.get() if t=="income" else self.ent_exp_cat.get()).strip()
        if not name:
            return
        try:
            add_category(name, t)
            if t == "income":
                self.ent_inc_cat.delete(0, tk.END)
            else:
                self.ent_exp_cat.delete(0, tk.END)
            self._refresh_categories()
        except sqlite3.IntegrityError:
            messagebox.showwarning("Duplicate", f"Category '{name}' already exists in {t}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _del_cat(self, t: str):
        lst = self.lst_inc if t=="income" else self.lst_exp
        sel = lst.curselection()
        if not sel:
            return
        txt = lst.get(sel[0])
        try:
            cat_id = int(txt.split(":")[0])
        except Exception:
            return
        if not messagebox.askyesno("Confirm", "Delete selected category? (Only if unused)"):
            return
        ok = delete_category(cat_id)
        if not ok:
            messagebox.showinfo("In use", "Cannot delete category with existing transactions.")
        self._refresh_categories()

    # ---------------- Currency ----------------
    def _set_currency(self, code: str):
        if code not in CURRENCIES:
            return
        set_setting("currency", code)
        self.currency_code = code
        self.currency_fmt = CURRENCIES[code]["fmt"]
        # update menu label
        self._settings_menu.entryconfig(0, label=f"Currency (current: {self.currency_code})")
        self._refresh_all()


# --------------------------- Main ---------------------------

def main():
    init_db()
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
