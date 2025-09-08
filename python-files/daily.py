"""
Daily Cash Book — simple desktop app
Tracks: Date, Particulars, Received, Paid, and auto-calculated running Balance.

• Windows-friendly (pure Tkinter + sqlite3)
• One-file app; creates 'cashbook.db' next to the script
• Add, edit, delete rows; export CSV
• Auto-today date; running totals (Received, Paid, Closing Balance)

Simple interface - no search or filters
"""
from __future__ import annotations
import os
import csv
import sqlite3
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Optional: ttkbootstrap theme (nice dark mode). Falls back to ttk if not installed.
USE_TTKBOOTSTRAP = False
try:
    if USE_TTKBOOTSTRAP:
        import ttkbootstrap as tb  # type: ignore
except Exception:
    USE_TTKBOOTSTRAP = False

# Optional: tkcalendar for date picker
HAS_TKCALENDAR = False
try:
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
except ImportError:
    pass

DB_FILE = "cashbook.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dt TEXT NOT NULL,              -- ISO datetime string (YYYY-MM-DD)
    particulars TEXT NOT NULL,
    received REAL NOT NULL DEFAULT 0,
    paid REAL NOT NULL DEFAULT 0,
    balance REAL NOT NULL DEFAULT 0
);
"""

class CashBookApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Daily Cash Book - Simple")
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.execute(SCHEMA)
        self.conn.commit()

        # Main style
        if USE_TTKBOOTSTRAP:
            style = tb.Style("darkly")
            self.root = style.master  # type: ignore
        else:
            style = ttk.Style()
            if os.name == "nt":
                style.theme_use("vista") if "vista" in style.theme_names() else None
            
            # Configure larger button style
            style.configure("Large.TButton", font=("Arial", 10))
            style.configure("Treeview", font=("Arial", 10))
            style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
            style.configure("Title.TLabel", font=("Arial", 12, "bold"))
            style.configure("Negative.Treeview", background="#ffdddd")  # Light red for negative
            style.configure("Positive.Treeview", background="#ddffdd")  # Light green for positive

        self._build_ui()
        self._load_rows()
        self._update_totals()

    # ---------------- UI ----------------
    def _build_ui(self):
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Top heading
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, pady=(10, 5))
        title_label = ttk.Label(title_frame, text="DAILY CASH BOOK", style="Title.TLabel")
        title_label.pack()
        
        # Main content area
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel for controls
        left_panel = ttk.Frame(content_frame, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)  # Keep fixed width
        
        # Right panel for table
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Build left panel controls
        self._build_left_panel(left_panel)
        
        # Build right panel table
        self._build_right_panel(right_panel)
        
        # Status bar at the bottom
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _build_left_panel(self, parent):
        # Form frame
        form = ttk.LabelFrame(parent, text="Add / Edit Entry", padding=10)
        form.pack(fill=tk.X, pady=(0, 10))
        
        # Date
        ttk.Label(form, text="Date", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 2))
        
        if HAS_TKCALENDAR:
            self.ent_date = DateEntry(form, width=24, font=("Arial", 10), 
                                     date_pattern='yyyy-mm-dd')
            self.ent_date.set_date(date.today())
        else:
            self.var_date = tk.StringVar(value=date.today().isoformat())
            self.ent_date = ttk.Entry(form, textvariable=self.var_date, width=25, font=("Arial", 10))
            
        self.ent_date.pack(fill=tk.X, pady=(0, 10))
        
        # Particulars
        ttk.Label(form, text="Particulars", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 2))
        self.var_part = tk.StringVar()
        self.ent_part = ttk.Entry(form, textvariable=self.var_part, width=25, font=("Arial", 10))
        self.ent_part.pack(fill=tk.X, pady=(0, 10))
        # Bind to convert to uppercase
        self.ent_part.bind('<KeyRelease>', self._to_uppercase)
        
        # Received
        ttk.Label(form, text="Received", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 2))
        self.var_recv = tk.StringVar(value="0.00")
        vcmd = (self.root.register(self._validate_money_input), '%d', '%P')
        self.ent_recv = ttk.Entry(form, textvariable=self.var_recv, width=25, justify="right", 
                                 font=("Arial", 10), validate="key", validatecommand=vcmd)
        self.ent_recv.pack(fill=tk.X, pady=(0, 10))
        
        # Paid
        ttk.Label(form, text="Paid", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 2))
        self.var_paid = tk.StringVar(value="0.00")
        self.ent_paid = ttk.Entry(form, textvariable=self.var_paid, width=25, justify="right", 
                                 font=("Arial", 10), validate="key", validatecommand=vcmd)
        self.ent_paid.pack(fill=tk.X, pady=(0, 15))
        
        # Buttons frame
        btn_frame = ttk.Frame(form)
        btn_frame.pack(fill=tk.X)
        
        self.btn_add = ttk.Button(btn_frame, text="Add (Enter)", command=self.add_entry, style="Large.TButton")
        self.btn_add.pack(fill=tk.X, pady=2)
        
        self.btn_update = ttk.Button(btn_frame, text="Update", command=self.update_selected, style="Large.TButton")
        self.btn_update.pack(fill=tk.X, pady=2)
        
        self.btn_clear = ttk.Button(btn_frame, text="Clear (Esc)", command=self.clear_form, style="Large.TButton")
        self.btn_clear.pack(fill=tk.X, pady=2)
        
        # Action buttons frame
        action_frame = ttk.LabelFrame(parent, text="Actions", padding=10)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(action_frame, text="Select All (Ctrl+A)", command=self.select_all, style="Large.TButton").pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Delete Selected (Del)", command=self.delete_selected, style="Large.TButton").pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Export CSV (Ctrl+E)", command=self.export_csv, style="Large.TButton").pack(fill=tk.X, pady=2)
        
        # Totals frame
        totals_frame = ttk.LabelFrame(parent, text="Totals", padding=10)
        totals_frame.pack(fill=tk.X)
        
        self.lbl_total_recv = ttk.Label(totals_frame, text="Total Received: 0.00", font=("Arial", 10, "bold"))
        self.lbl_total_recv.pack(anchor="w", pady=2)
        
        self.lbl_total_paid = ttk.Label(totals_frame, text="Total Paid: 0.00", font=("Arial", 10, "bold"))
        self.lbl_total_paid.pack(anchor="w", pady=2)
        
        self.lbl_closing = ttk.Label(totals_frame, text="Closing Balance: 0.00", font=("Arial", 10, "bold"))
        self.lbl_closing.pack(anchor="w", pady=2)

    def _build_right_panel(self, parent):
        # Table frame
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Table with serial number column
        cols = ("sno", "dt", "particulars", "received", "paid", "balance")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="extended")
        self.tree.heading("sno", text="S.No")
        self.tree.heading("dt", text="Date")
        self.tree.heading("particulars", text="Particulars")
        self.tree.heading("received", text="Received")
        self.tree.heading("paid", text="Paid")
        self.tree.heading("balance", text="Balance")
        
        self.tree.column("sno", width=50, anchor="center")
        self.tree.column("dt", width=100, anchor="w")
        self.tree.column("particulars", width=250, anchor="w")
        self.tree.column("received", width=100, anchor="e")
        self.tree.column("paid", width=100, anchor="e")
        self.tree.column("balance", width=100, anchor="e")
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_frame.rowconfigure(0, weight=4)
        table_frame.columnconfigure(0, weight=4)
        
        self.tree.bind("<ButtonRelease-1>", self.on_row_click)
        self.tree.bind("<Double-1>", self.on_row_double_click)
        
        # Key bindings for speed
        self.root.bind("<Return>", lambda e: self.add_entry())
        self.root.bind("<Escape>", lambda e: self.clear_form())
        self.root.bind("<Delete>", lambda e: self.delete_selected())
        self.root.bind("<Control-a>", lambda e: self.select_all())
        self.root.bind("<Control-A>", lambda e: self.select_all())
        self.root.bind("<Control-e>", lambda e: self.export_csv())
        self.root.bind("<Control-E>", lambda e: self.export_csv())

    # ------------- Helpers -------------
    def _to_uppercase(self, event=None):
        """Convert text to uppercase"""
        current_text = self.var_part.get()
        if current_text != current_text.upper():
            self.var_part.set(current_text.upper())
    
    def _validate_money_input(self, action, value_if_allowed):
        """Validate money input fields"""
        if action == '0':  # This is a delete action
            return True
        try:
            # Allow empty string (will be treated as 0)
            if not value_if_allowed:
                return True
            # Try to convert to float
            float(value_if_allowed.replace(',', ''))
            return True
        except ValueError:
            return False

    @staticmethod
    def _parse_money(value: str) -> Decimal:
        v = value.strip().replace(",", "") or "0"
        try:
            return Decimal(v)
        except InvalidOperation:
            raise ValueError("Please enter a valid number (use digits and optional decimal point)")

    @staticmethod
    def _fmt_money(d: Decimal | float) -> str:
        try:
            return f"{Decimal(d):,.2f}"
        except Exception:
            return f"{d:.2f}" if isinstance(d, (int, float)) else str(d)

    def _selected_row_ids(self) -> list[int]:
        """Get all selected row IDs"""
        sel = self.tree.selection()
        if not sel:
            return []
        
        row_ids = []
        for item in sel:
            values = self.tree.item(item)["values"]
            if values:
                # Get the date and particulars to find the matching row in database
                dt_s, particulars = values[1], values[2]  # Skip S.No column
                cur = self.conn.cursor()
                cur.execute("SELECT id FROM entries WHERE dt=? AND particulars=? LIMIT 1", (dt_s, particulars))
                row = cur.fetchone()
                if row:
                    row_ids.append(row[0])
        return row_ids

    def _selected_row_id(self) -> int | None:
        """Get single selected row ID"""
        ids = self._selected_row_ids()
        return ids[0] if ids else None

    # ------------- Data Ops -------------
    def _row_iter(self, where_clause: str = "", params: tuple = ()):  # yields rows dict
        cur = self.conn.cursor()
        sql = "SELECT id, dt, particulars, received, paid, balance FROM entries"
        if where_clause:
            sql += f" WHERE {where_clause}"
        sql += " ORDER BY dt ASC, id ASC"
        for r in cur.execute(sql, params):
            yield {
                "id": r[0],
                "dt": r[1],
                "particulars": r[2],
                "received": Decimal(str(r[3])),
                "paid": Decimal(str(r[4])),
                "balance": Decimal(str(r[5])),
            }

    def _last_balance(self) -> Decimal:
        cur = self.conn.cursor()
        cur.execute("SELECT balance FROM entries ORDER BY dt DESC, id DESC LIMIT 1")
        row = cur.fetchone()
        return Decimal(str(row[0])) if row else Decimal("0")

    def _insert_entry(self, dt_str: str, particulars: str, received: Decimal, paid: Decimal):
        # Insert with a temporary balance, then recalc all balances to keep running balance correct
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO entries (dt, particulars, received, paid, balance) VALUES (?,?,?,?,0)",
            (dt_str, particulars, float(received), float(paid),),
        )
        self.conn.commit()
        self._recalc_all_balances()

    def _update_entry(self, row_id: int, dt_str: str, particulars: str, received: Decimal, paid: Decimal):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE entries SET dt=?, particulars=?, received=?, paid=? WHERE id=?",
            (dt_str, particulars, float(received), float(paid), row_id),
        )
        self.conn.commit()
        self._recalc_all_balances()

    def _delete_entry(self, row_id: int):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM entries WHERE id=?", (row_id,))
        self.conn.commit()
        self._recalc_all_balances()

    def _delete_multiple_entries(self, row_ids: list[int]):
        cur = self.conn.cursor()
        for row_id in row_ids:
            cur.execute("DELETE FROM entries WHERE id=?", (row_id,))
        self.conn.commit()
        self._recalc_all_balances()

    def _recalc_all_balances(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, dt, received, paid FROM entries ORDER BY dt ASC, id ASC")
        rows = cur.fetchall()
        running = Decimal("0")
        for rid, dt_s, recv, paid in rows:
            running += Decimal(str(recv)) - Decimal(str(paid))
            cur.execute("UPDATE entries SET balance=? WHERE id=?", (float(running), rid))
        self.conn.commit()
        self._load_rows()
        self._update_totals()

    # ------------- UI Actions -------------
    def add_entry(self):
        try:
            if HAS_TKCALENDAR:
                d = self.ent_date.get_date().isoformat()
            else:
                d = self.var_date.get().strip() or date.today().isoformat()
                
            # Accept just date; store noon time to keep order when multiple rows same day
            datetime.strptime(d, "%Y-%m-%d")
            dt_str = f"{d} {datetime.now().strftime('%H:%M:%S')}"

            particulars = self.var_part.get().strip() or "—"
            received = self._parse_money(self.var_recv.get())
            paid = self._parse_money(self.var_paid.get())
            
            if received < 0 or paid < 0:
                raise ValueError("Amounts cannot be negative")
                
            self._insert_entry(dt_str, particulars, received, paid)
            self.clear_form()
            self.status_var.set("Entry added successfully")
        except Exception as e:
            messagebox.showerror("Invalid Input", str(e))
            self.status_var.set(f"Error: {str(e)}")

    def on_row_click(self, _evt=None):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        values = item["values"]
        # values order: sno, dt, particulars, rec, paid, bal
        dt_s, particulars, rec, paid, bal = values[1], values[2], values[3], values[4], values[5]
        
        if HAS_TKCALENDAR:
            try:
                self.ent_date.set_date(datetime.strptime(dt_s.split(" ")[0], "%Y-%m-%d"))
            except:
                pass
        else:
            self.var_date.set(dt_s.split(" ")[0])
            
        self.var_part.set(particulars)
        self.var_recv.set(self._fmt_money(rec))
        self.var_paid.set(self._fmt_money(paid))
        self.status_var.set("Row selected for editing")

    def on_row_double_click(self, _evt=None):
        # Shortcut: load into form ready to update
        self.on_row_click()

    def update_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Update", "Please select a row to update.")
            self.status_var.set("Please select a row to update")
            return
        row_id = self._selected_row_id()
        if row_id is None:
            messagebox.showerror("Error", "Could not find the selected row in database.")
            self.status_var.set("Error: Could not find selected row")
            return
        try:
            if HAS_TKCALENDAR:
                d = self.ent_date.get_date().isoformat()
            else:
                d = self.var_date.get().strip()
                
            datetime.strptime(d, "%Y-%m-%d")
            dt_str = f"{d} {datetime.now().strftime('%H:%M:%S')}"
            particulars = self.var_part.get().strip() or "—"
            received = self._parse_money(self.var_recv.get())
            paid = self._parse_money(self.var_paid.get())
            
            if received < 0 or paid < 0:
                raise ValueError("Amounts cannot be negative")
                
            self._update_entry(row_id, dt_str, particulars, received, paid)
            self.clear_form()
            self.status_var.set("Entry updated successfully")
        except Exception as e:
            messagebox.showerror("Update Failed", str(e))
            self.status_var.set(f"Error: {str(e)}")

    def select_all(self):
        """Select all rows in the table"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)
        self.status_var.set("All rows selected")

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Please select rows to delete.")
            self.status_var.set("Please select rows to delete")
            return
        
        row_ids = self._selected_row_ids()
        if not row_ids:
            messagebox.showerror("Error", "Could not find the selected rows in database.")
            self.status_var.set("Error: Could not find selected rows")
            return
        
        count = len(row_ids)
        
        # Special warning if trying to delete all records
        if count == len(self.tree.get_children()):
            msg = "You are about to delete ALL records. This cannot be undone. Continue?"
        else:
            msg = f"Delete {count} selected entries?"
            
        if messagebox.askyesno("Confirm", msg):
            self._delete_multiple_entries(row_ids)
            self.status_var.set(f"Deleted {count} entries")

    def clear_form(self):
        if HAS_TKCALENDAR:
            self.ent_date.set_date(date.today())
        else:
            self.var_date.set(date.today().isoformat())
            
        self.var_part.set("")
        self.var_recv.set("0.00")
        self.var_paid.set("0.00")
        self.tree.selection_remove(self.tree.selection())
        self.ent_part.focus_set()  # Auto-focus on particulars field
        self.status_var.set("Form cleared")

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"cashbook_export_{date.today().isoformat()}.csv",
        )
        if not path:
            return
            
        # Export all data from database, not just what's visible
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["S.No", "Date", "Particulars", "Received", "Paid", "Balance"])
            
            # Get all data from database
            cur = self.conn.cursor()
            cur.execute("SELECT dt, particulars, received, paid, balance FROM entries ORDER BY dt ASC, id ASC")
            
            sno = 1
            for row in cur.fetchall():
                # Format the date to remove time component if present
                dt = row[0].split(' ')[0] if ' ' in row[0] else row[0]
                writer.writerow([sno, dt, row[1], row[2], row[3], row[4]])
                sno += 1
                
        messagebox.showinfo("Export", f"Exported to\n{path}")
        self.status_var.set(f"Data exported to {path}")

    # ------------- Loading & Totals -------------
    def _load_rows(self, where_clause: str = "", params: tuple = ()):  # refresh table
        # Clear
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        cur = self.conn.cursor()
        sql = "SELECT id, dt, particulars, received, paid, balance FROM entries"
        if where_clause:
            sql += f" WHERE {where_clause}"
        sql += " ORDER BY dt ASC, id ASC"
        
        sno = 1
        for r in cur.execute(sql, params):
            # Format amounts with 2 decimal places
            received_fmt = self._fmt_money(r[3])
            paid_fmt = self._fmt_money(r[4])
            balance_fmt = self._fmt_money(r[5])
            
            item_id = self.tree.insert("", tk.END, values=(sno, r[1], r[2], received_fmt, paid_fmt, balance_fmt))
            
            # Color code based on balance
            balance_val = Decimal(str(r[5]))
            if balance_val < 0:
                self.tree.item(item_id, tags=('negative',))
            elif balance_val > 0:
                self.tree.item(item_id, tags=('positive',))
                
            sno += 1

    def _update_totals(self):
        # Totals based on current view
        total_recv = Decimal("0")
        total_paid = Decimal("0")
        closing = Decimal("0")
        for iid in self.tree.get_children():
            values = self.tree.item(iid)["values"]
            # values: sno, dt, part, rec, paid, bal
            rec_str = values[3].replace(",", "")
            paid_str = values[4].replace(",", "")
            bal_str = values[5].replace(",", "")
            
            total_recv += Decimal(rec_str)
            total_paid += Decimal(paid_str)
            closing = Decimal(bal_str)  # last row's balance (ordered ascending)
        
        self.lbl_total_recv.config(text=f"Total Received: {self._fmt_money(total_recv)}")
        self.lbl_total_paid.config(text=f"Total Paid: {self._fmt_money(total_paid)}")
        self.lbl_closing.config(text=f"Closing Balance: {self._fmt_money(closing)}")


def main():
    root = tk.Tk()
    app = CashBookApp(root)
    root.geometry("1100x650")
    root.minsize(1000, 550)
    root.mainloop()


if __name__ == "__main__":
    main()