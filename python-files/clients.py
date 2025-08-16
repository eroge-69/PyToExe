#!/usr/bin/env python3
"""
Client Balance Manager — Fixed column-order (explicit SELECT) + Payment Received Date + Exact-Match Overdue

Save as: client_balance_manager_final.py
DB file: client_balances.db
"""
import os
import sys
import sqlite3
import tempfile
import platform
from datetime import datetime
import subprocess
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DB_FILE = "client_balances.db"
DATE_FMT = "%Y-%m-%d"
OVERDUE_DAYS = 30
EPS = 1e-6

# ----------------------------- Database Layer ----------------------------- #

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            work_location TEXT,
            contact_no TEXT,
            invoice_no TEXT NOT NULL,
            invoice_month TEXT,
            invoice_submission_date TEXT NOT NULL,
            payment_received_date TEXT,
            debit REAL DEFAULT 0,
            credit REAL DEFAULT 0,
            address TEXT,
            remarks TEXT,
            other_details TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    ensure_column(conn, "payment_received_date", "TEXT")
    return conn

def ensure_column(conn, column_name, column_type):
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(records)")
    cols = [r[1] for r in cur.fetchall()]
    if column_name not in cols:
        try:
            cur.execute(f"ALTER TABLE records ADD COLUMN {column_name} {column_type}")
            conn.commit()
        except Exception as e:
            print(f"[WARN] Could not add column {column_name}: {e}", file=sys.stderr)

# ------------------------- Utility / Validation --------------------------- #

def safe_float(value, default=0.0):
    try:
        if value is None or str(value).strip() == "":
            return default
        return float(str(value).replace(",", "").strip())
    except Exception:
        return default

def parse_date(s):
    try:
        return datetime.strptime(s, DATE_FMT)
    except Exception:
        return None

def format_date(dt):
    return dt.strftime(DATE_FMT)

# ------------------------------- Main App -------------------------------- #

class ClientBalanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Volcano General Transporation LLC-OPC (Client Balance Manager)")
        self.geometry("1320x880")

        self.minsize(1150, 740)

        self.conn = init_db()

        self.alerted_overdue_companies = set()

        self._build_styles()
        self._build_toolbar()
        self._build_stats()
        self._build_form()
        self._build_table()
        self._bind_events()

        self.load_records()

    def _build_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TButton", padding=6)
        style.configure("TEntry", padding=4)
        style.configure("TLabel", padding=2)
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#cde3ff")])
        style.configure("oddrow", background="#f8f8fc")
        style.configure("evenrow", background="#ffffff")
        style.configure("overdue", background="#fff0f0")

    def _build_toolbar(self):
        bar = ttk.Frame(self)
        bar.pack(fill=tk.X, padx=10, pady=(10, 6))

        ttk.Label(bar, text="🔎 Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(bar, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=(6, 12))

        btns = [
            ("Add", self.add_record),
            ("Update", self.update_record),
            ("Delete", self.delete_record),
            ("Clear Form", self.clear_form),
            ("Export Excel", self.export_excel),
            ("Export PDF", self.export_pdf),
            ("Print", self.print_records),
            ("Refresh", self.load_records),
            ("Export Due PDF", self.export_due_pdf),
            ("Print Due Report", self.print_due_report),

        ]
        for text, cmd in btns:
            ttk.Button(bar, text=text, command=cmd).pack(side=tk.LEFT, padx=4)

        self.status_var = tk.StringVar(value="Ready")
        self.status = ttk.Label(self, textvariable=self.status_var, anchor="w")
        self.status.pack(fill=tk.X, padx=10, pady=(0, 2))

    def _build_stats(self):
        self.stats_view = {k: tk.StringVar(value="0") for k in ("clients", "records")}
        self.stats_view.update({"debit": tk.StringVar(value="0.00"), "credit": tk.StringVar(value="0.00"), "balance": tk.StringVar(value="0.00")})
        self.stats_all = {k: tk.StringVar(value="0") for k in ("clients", "records")}
        self.stats_all.update({"debit": tk.StringVar(value="0.00"), "credit": tk.StringVar(value="0.00"), "balance": tk.StringVar(value="0.00")})

        wrap = ttk.Frame(self)
        wrap.pack(fill=tk.X, padx=10, pady=(0, 8))

        def row(parent, title, vars_):
            f = ttk.Frame(parent)
            f.pack(fill=tk.X, pady=2)
            ttk.Label(f, text=title, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0,12))
            for lab, key in [("Total Clients:", "clients"), ("Total Records:", "records"), ("Total Debit:", "debit"), ("Total Credit:", "credit"), ("Balance:", "balance")]:
                ttk.Label(f, text=lab).pack(side=tk.LEFT)
                ttk.Label(f, textvariable=vars_[key], foreground="#1f5c1f").pack(side=tk.LEFT, padx=(2,12))
        row(wrap, "Totals (View)", self.stats_view)
        row(wrap, "Totals (All)", self.stats_all)

    def _build_form(self):
        box = ttk.LabelFrame(self, text="Record Details")
        box.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.vars = {
            "id": tk.StringVar(),
            "company_name": tk.StringVar(),
            "work_location": tk.StringVar(),
            "contact_no": tk.StringVar(),
            "invoice_no": tk.StringVar(),
            "invoice_month": tk.StringVar(),
            "invoice_submission_date": tk.StringVar(value=format_date(datetime.today())),
            "payment_received_date": tk.StringVar(value=format_date(datetime.today())),
            "debit": tk.StringVar(value="0"),
            "credit": tk.StringVar(value="0"),
            "address": tk.StringVar(),
            "remarks": tk.StringVar(),
            "other_details": tk.StringVar(),
        }

        labels = [
            ("Company Name*", "company_name"),
            ("Work Location", "work_location"),
            ("Contact No", "contact_no"),
            ("Invoice No*", "invoice_no"),
            ("Invoice Month", "invoice_month"),
            ("Invoice Submission (YYYY-MM-DD)*", "invoice_submission_date"),
            ("Payment Received Date (YYYY-MM-DD)", "payment_received_date"),
            ("Debit", "debit"),
            ("Credit", "credit"),
            ("Address", "address"),
            ("Remarks", "remarks"),
            ("Other Details", "other_details"),
        ]

        for i, (lbl, key) in enumerate(labels):
            r, c = divmod(i, 4)
            ttk.Label(box, text=lbl).grid(row=r, column=c*2, sticky="e", padx=6, pady=4)
            ttk.Entry(box, textvariable=self.vars[key], width=30).grid(row=r, column=c*2 + 1, sticky="we", padx=6, pady=4)

        ttk.Label(box, textvariable=self.vars["id"], foreground="#666").grid(row=3, column=0, columnspan=2, sticky="w", padx=6)
        for i in range(8):
            box.grid_columnconfigure(i, weight=1)

    def _build_table(self):
        wrap = ttk.Frame(self)
        wrap.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        columns = (
            "id","company_name","work_location","contact_no",
            "invoice_no","invoice_month","invoice_submission_date","payment_received_date",
            "debit","credit","balance","address","remarks","other_details"
        )
        self.tree = ttk.Treeview(wrap, columns=columns, show="headings", selectmode="browse")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        headings = {
            "id":"ID","company_name":"Company","work_location":"Work Location","contact_no":"Contact No",
            "invoice_no":"Invoice No","invoice_month":"Invoice Month",
            "invoice_submission_date":"Submission Date","payment_received_date":"Payment Received Date",
            "debit":"Debit","credit":"Credit","balance":"Balance",
            "address":"Address","remarks":"Remarks","other_details":"Other Details"
        }
        widths = {
            "id":60,"company_name":180,"work_location":140,"contact_no":120,
            "invoice_no":120,"invoice_month":120,"invoice_submission_date":130,"payment_received_date":150,
            "debit":100,"credit":100,"balance":110,"address":200,"remarks":200,"other_details":200
        }

        for k in columns:
            self.tree.heading(k, text=headings[k], command=lambda kk=k: self._sort_by(kk, False))
            self.tree.column(k, width=widths.get(k,120), anchor=tk.W)

        sb = ttk.Scrollbar(wrap, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

    def _bind_events(self):
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.search_var.trace_add("write", lambda *a: self.on_search_change())

    # ---------------------------- Payment/Overdue -------------------------- #

    def _has_exact_matching_payment(self, company, invoice_no, invoice_month, amount):
        try:
            c = self.conn.cursor()
            c.execute("""
                SELECT credit FROM records
                WHERE company_name = ?
                  AND invoice_no = ?
                  AND IFNULL(invoice_month,'') = IFNULL(?, '')
                  AND credit IS NOT NULL
            """, (company, invoice_no, invoice_month))
            for (credit_val,) in c.fetchall():
                if abs(safe_float(credit_val) - safe_float(amount)) <= EPS:
                    return True
            return False
        except Exception:
            return False

    def _is_exact_overdue(self, date_str, company, invoice_no, invoice_month, amount):
        dt = parse_date(date_str)
        if dt is None:
            return False
        days = (datetime.today() - dt).days
        if days < OVERDUE_DAYS:
            return False
        return not self._has_exact_matching_payment(company, invoice_no, invoice_month, amount)

    # ------------------------------- Actions ------------------------------- #

    def _validate_form(self):
        for key, msg in [
            ("company_name","Company Name is required."),
            ("invoice_no","Invoice No is required."),
            ("invoice_submission_date","Submission Date is required (YYYY-MM-DD)."),
        ]:
            if not self.vars[key].get().strip():
                messagebox.showerror("Missing Field", msg)
                return False

        if parse_date(self.vars["invoice_submission_date"].get().strip()) is None:
            messagebox.showerror("Invalid Date", "Submission Date must be YYYY-MM-DD.")
            return False

        prd = self.vars["payment_received_date"].get().strip()
        if prd and parse_date(prd) is None:
            messagebox.showerror("Invalid Date", "Payment Received Date must be YYYY-MM-DD or empty.")
            return False

        for key in ("debit","credit"):
            try:
                _ = safe_float(self.vars[key].get())
            except Exception:
                messagebox.showerror("Invalid Number", f"{key.title()} must be a number.")
                return False
        return True

    def add_record(self):
        if not self._validate_form():
            return
        try:
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO records (
                    company_name, work_location, contact_no, invoice_no, invoice_month,
                    invoice_submission_date, payment_received_date, debit, credit,
                    address, remarks, other_details
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                self.vars["company_name"].get().strip(),
                self.vars["work_location"].get().strip(),
                self.vars["contact_no"].get().strip(),
                self.vars["invoice_no"].get().strip(),
                self.vars["invoice_month"].get().strip(),
                self.vars["invoice_submission_date"].get().strip(),
                self.vars["payment_received_date"].get().strip() or None,
                safe_float(self.vars["debit"].get()),
                safe_float(self.vars["credit"].get()),
                self.vars["address"].get().strip(),
                self.vars["remarks"].get().strip(),
                self.vars["other_details"].get().strip()
            ))
            self.conn.commit()
            self.status_var.set("Record added.")
            self.clear_form()
            self.load_records()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add record: {e}")

    def update_record(self):
        rid = self.vars["id"].get().strip()
        if not rid:
            messagebox.showwarning("No Selection", "Select a record to update.")
            return
        if not self._validate_form():
            return
        try:
            c = self.conn.cursor()
            c.execute("""
                UPDATE records
                SET company_name=?, work_location=?, contact_no=?, invoice_no=?, invoice_month=?,
                    invoice_submission_date=?, payment_received_date=?, debit=?, credit=?,
                    address=?, remarks=?, other_details=?
                WHERE id=?
            """, (
                self.vars["company_name"].get().strip(),
                self.vars["work_location"].get().strip(),
                self.vars["contact_no"].get().strip(),
                self.vars["invoice_no"].get().strip(),
                self.vars["invoice_month"].get().strip(),
                self.vars["invoice_submission_date"].get().strip(),
                self.vars["payment_received_date"].get().strip() or None,
                safe_float(self.vars["debit"].get()),
                safe_float(self.vars["credit"].get()),
                self.vars["address"].get().strip(),
                self.vars["remarks"].get().strip(),
                self.vars["other_details"].get().strip(),
                int(rid)
            ))
            self.conn.commit()
            self.status_var.set("Record updated.")
            self.load_records(preserve_selection=int(rid))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update record: {e}")

    def delete_record(self):
        rid = self.vars["id"].get().strip()
        if not rid:
            messagebox.showwarning("No Selection", "Select a record to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", "Delete the selected record? This cannot be undone."):
            return
        try:
            c = self.conn.cursor()
            c.execute("DELETE FROM records WHERE id=?", (int(rid),))
            self.conn.commit()
            self.status_var.set("Record deleted.")
            self.clear_form()
            self.load_records()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete record: {e}")

    def clear_form(self):
        for k, var in self.vars.items():
            if k in ("invoice_submission_date", "payment_received_date"):
                var.set(format_date(datetime.today()))
            elif k in ("debit","credit"):
                var.set("0")
            else:
                var.set("")

    def on_tree_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        vals = item["values"]
        keys = [
            "id","company_name","work_location","contact_no","invoice_no","invoice_month",
            "invoice_submission_date","payment_received_date","debit","credit","balance",
            "address","remarks","other_details"
        ]
        data = dict(zip(keys, vals))
        for k in self.vars:
            if k in data:
                self.vars[k].set("" if data[k] is None else str(data[k]))

        company = data.get("company_name")
        inv_no = data.get("invoice_no")
        inv_mo = data.get("invoice_month")
        inv_date = data.get("invoice_submission_date")
        debit_amt = safe_float(data.get("debit"))

        if company and inv_no and inv_date and debit_amt > 0 and company not in self.alerted_overdue_companies:
            if self._is_exact_overdue(inv_date, company, inv_no, inv_mo, debit_amt):
                days = (datetime.today() - parse_date(inv_date)).days
                messagebox.showwarning(
                    "Overdue Notice",
                    f"{company} invoice {inv_no} ({inv_mo or 'N/A'}) is overdue by {days} days.\n"
                    f"No exact matching payment (amount {debit_amt:.2f}) was found."
                )
                self.alerted_overdue_companies.add(company)

    def on_search_change(self):
        self.load_records()
        for iid in self.tree.get_children():
            vals = self.tree.item(iid, "values")
            company = vals[1]
            inv_no = vals[4]
            inv_mo = vals[5]
            date_str = vals[6]
            debit_amt = safe_float(vals[8])
            if company and inv_no and company not in self.alerted_overdue_companies and debit_amt > 0:
                if self._is_exact_overdue(date_str, company, inv_no, inv_mo, debit_amt):
                    days = (datetime.today() - parse_date(date_str)).days
                    messagebox.showwarning(
                        "Overdue Records Present",
                        f"{company} has an overdue invoice {inv_no} ({inv_mo or 'N/A'}) by {days} days.\n"
                        f"No exact matching payment (amount {debit_amt:.2f}) was found."
                    )
                    self.alerted_overdue_companies.add(company)

    def load_records(self, preserve_selection=None):
        try:
            q = self.search_var.get().strip()
        except Exception:
            q = ""
        try:
            c = self.conn.cursor()
            # EXPLICIT column list to guarantee ordering even if DB schema changed
            cols = (
                "id","company_name","work_location","contact_no","invoice_no","invoice_month",
                "invoice_submission_date","payment_received_date","debit","credit",
                "address","remarks","other_details","created_at"
            )
            if q:
                like = f"%{q}%"
                sql = f"""
                    SELECT {', '.join(cols)} FROM records
                    WHERE company_name LIKE ? OR work_location LIKE ? OR contact_no LIKE ?
                       OR invoice_no LIKE ? OR invoice_month LIKE ?
                       OR invoice_submission_date LIKE ? OR IFNULL(payment_received_date,'') LIKE ?
                       OR address LIKE ? OR remarks LIKE ? OR other_details LIKE ?
                    ORDER BY company_name ASC, invoice_submission_date ASC, id ASC
                """
                c.execute(sql, (like,like,like,like,like,like,like,like,like,like))
            else:
                sql = f"SELECT {', '.join(cols)} FROM records ORDER BY company_name ASC, invoice_submission_date ASC, id ASC"
                c.execute(sql)
            rows = c.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load records: {e}")
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        balances = {}
        view_companies = set()
        view_records = 0
        view_debit = 0.0
        view_credit = 0.0

        for idx, r in enumerate(rows):
            (rid, company_name, work_location, contact_no, invoice_no, invoice_month,
             invoice_submission_date, payment_received_date, debit, credit,
             address, remarks, other_details, created_at) = r

            view_records += 1
            view_companies.add(company_name)
            d = safe_float(debit)
            cval = safe_float(credit)
            view_debit += d
            view_credit += cval

            bal = balances.get(company_name, 0.0) + d - cval
            balances[company_name] = bal

            vals = (
                rid, company_name, work_location, contact_no, invoice_no, invoice_month,
                invoice_submission_date, payment_received_date or "",
                float(d), float(cval), round(bal, 2),
                address, remarks, other_details
            )

            tags = ["evenrow" if idx % 2 == 0 else "oddrow"]
            if d > 0 and self._is_exact_overdue(invoice_submission_date, company_name, invoice_no, invoice_month, d):
                tags.append("overdue")

            self.tree.insert("", tk.END, iid=str(rid), values=vals, tags=tags)

        self.stats_view["clients"].set(str(len(view_companies)))
        self.stats_view["records"].set(str(view_records))
        self.stats_view["debit"].set(f"{view_debit:.2f}")
        self.stats_view["credit"].set(f"{view_credit:.2f}")
        self.stats_view["balance"].set(f"{(view_debit - view_credit):.2f}")

        try:
            c = self.conn.cursor()
            c.execute("SELECT COUNT(DISTINCT company_name), COUNT(*), IFNULL(SUM(debit),0), IFNULL(SUM(credit),0) FROM records")
            clients, recs, deb_sum, cred_sum = c.fetchone()
            self.stats_all["clients"].set(str(clients))
            self.stats_all["records"].set(str(recs))
            self.stats_all["debit"].set(f"{float(deb_sum):.2f}")
            self.stats_all["credit"].set(f"{float(cred_sum):.2f}")
            self.stats_all["balance"].set(f"{(float(deb_sum) - float(cred_sum)):.2f}")
        except Exception:
            pass

        if preserve_selection and self.tree.exists(str(preserve_selection)):
            self.tree.selection_set(str(preserve_selection))
            self.tree.see(str(preserve_selection))

        self.status_var.set(f"Loaded {view_records} records.")

    def _ask_savepath(self, title, defaultextension, filetypes):
        return filedialog.asksaveasfilename(title=title, defaultextension=defaultextension, filetypes=filetypes, confirmoverwrite=True)

    def export_excel(self):
        path = self._ask_savepath("Save Excel File", ".xlsx", [("Excel Workbook","*.xlsx")])
        if not path:
            return
        try:
            import pandas as pd
            c = self.conn.cursor()
            cols = (
                "id","company_name","work_location","contact_no","invoice_no","invoice_month",
                "invoice_submission_date","payment_received_date","debit","credit",
                "address","remarks","other_details","created_at"
            )
            sql = f"SELECT {', '.join(cols)} FROM records ORDER BY company_name, invoice_submission_date, id"
            c.execute(sql)
            data = c.fetchall()
            df = pd.DataFrame(data, columns=cols)
            df["debit"] = pd.to_numeric(df["debit"]).fillna(0.0)
            df["credit"] = pd.to_numeric(df["credit"]).fillna(0.0)
            df["_order"] = pd.to_datetime(df["invoice_submission_date"], errors="coerce")
            df.sort_values(["company_name", "_order", "id"], inplace=True)
            df["balance"] = df.groupby("company_name")["debit"].cumsum() - df.groupby("company_name")["credit"].cumsum()
            df.drop(columns=["_order"], inplace=True)
            cols_out = [
                "id","company_name","work_location","contact_no","invoice_no","invoice_month",
                "invoice_submission_date","payment_received_date","debit","credit","balance",
                "address","remarks","other_details","created_at"
            ]
            df = df[cols_out]
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="ClientBalances")
            self.status_var.set(f"Excel saved: {os.path.basename(path)}")
            messagebox.showinfo("Export Complete", f"Excel saved to: {path}")
        except ImportError:
            messagebox.showerror("Missing Dependency", "Install pandas and openpyxl to export Excel:\npip install pandas openpyxl")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not save Excel file: {e}")

    def export_pdf(self):
        path = self._ask_savepath("Save PDF File", ".pdf", [("PDF", "*.pdf")])
        if not path:
            return
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import mm

            rows = [self.tree.item(iid, "values") for iid in self.tree.get_children()]

            # Correct totals
            total_debit = sum(safe_float(r[8]) for r in rows)  # Debit column
            total_credit = sum(safe_float(r[9]) for r in rows)  # Credit column
            total_balance = total_debit - total_credit

            c = canvas.Canvas(path, pagesize=landscape(A4))
            width, height = landscape(A4)
            margin = 12 * mm
            x = margin
            y = height - margin

            title = f"Client Invoice & Balance Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            c.setFont("Helvetica-Bold", 14)
            c.drawString(x, y, title)
            y -= 10 * mm

            # Only these headers
            headers = ["ID", "Company", "Invoice No", "Invoice Mo", "Submit Date",
                       "Received Date", "Debit", "Credit", "Balance", "Remarks"]
            col_w = [25, 120, 70, 60, 70, 70, 45, 45, 55, 120]

            # Draw headers
            c.setFont("Helvetica-Bold", 9)
            cx = x
            for h, w in zip(headers, col_w):
                c.drawString(cx, y, h)
                cx += w
            y -= 6 * mm

            # Draw rows (only selected columns)
            c.setFont("Helvetica", 8)
            for row in rows:
                selected_values = [row[0], row[1], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[12]]
                cx = x
                for text, w in zip(selected_values, col_w):
                    s = str(text)
                    max_chars = int(w / 4.5)
                    if len(s) > max_chars:
                        s = s[: max_chars - 1] + "…"
                    c.drawString(cx, y, s)
                    cx += w
                y -= 6 * mm
                if y < margin + 20:
                    c.showPage()
                    c.setFont("Helvetica", 8)
                    y = height - margin

            # Totals row
            y -= 8 * mm
            c.setFont("Helvetica-Bold", 10)
            c.drawString(x, y, f"TOTAL DEBIT: {total_debit:.2f}")
            c.drawString(x + 150, y, f"TOTAL CREDIT: {total_credit:.2f}")
            c.drawString(x + 300, y, f"TOTAL BALANCE: {total_balance:.2f}")

            c.save()
            self.status_var.set(f"PDF saved: {os.path.basename(path)}")
            messagebox.showinfo("Export Complete", f"PDF saved to: {path}")
        except ImportError:
            messagebox.showerror("Missing Dependency", "Install reportlab to export/print PDF:\npip install reportlab")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not save PDF file: {e}")

    def print_records(self):
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import mm
        except ImportError:
            messagebox.showerror("Missing Dependency", "Install reportlab to enable printing:\npip install reportlab")
            return

        tmpdir = tempfile.gettempdir()
        path = os.path.join(tmpdir, f"client_invoices_{int(datetime.now().timestamp())}.pdf")

        try:
            rows = [self.tree.item(iid, "values") for iid in self.tree.get_children()]

            # Correct totals
            total_debit = sum(safe_float(r[8]) for r in rows)  # Debit column
            total_credit = sum(safe_float(r[9]) for r in rows)  # Credit column
            total_balance = total_debit - total_credit

            c = canvas.Canvas(path, pagesize=landscape(A4))
            width, height = landscape(A4)
            margin = 12 * mm
            x = margin
            y = height - margin

            title = f"Client Invoice Print — {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            c.setFont("Helvetica-Bold", 14)
            c.drawString(x, y, title)
            y -= 10 * mm

            # Only these headers
            headers = ["ID", "Company", "Invoice No", "Invoice Mo", "Submit Date",
                       "Received Date", "Debit", "Credit", "Balance", "Remarks"]
            col_w = [25, 120, 70, 60, 70, 70, 45, 45, 55, 120]

            # Draw headers
            c.setFont("Helvetica-Bold", 9)
            cx = x
            for h, w in zip(headers, col_w):
                c.drawString(cx, y, h)
                cx += w
            y -= 6 * mm

            # Draw rows (only selected columns)
            c.setFont("Helvetica", 8)
            for row in rows:
                selected_values = [row[0], row[1], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[12]]
                cx = x
                for text, w in zip(selected_values, col_w):
                    s = str(text)
                    max_chars = int(w / 4.5)
                    if len(s) > max_chars:
                        s = s[: max_chars - 1] + "…"
                    c.drawString(cx, y, s)
                    cx += w
                y -= 6 * mm
                if y < margin + 20:
                    c.showPage()
                    c.setFont("Helvetica", 8)
                    y = height - margin

            # Totals row
            y -= 8 * mm
            c.setFont("Helvetica-Bold", 10)
            c.drawString(x, y, f"TOTAL DEBIT: {total_debit:.2f}")
            c.drawString(x + 150, y, f"TOTAL CREDIT: {total_credit:.2f}")
            c.drawString(x + 300, y, f"TOTAL BALANCE: {total_balance:.2f}")

            c.save()
        except Exception as e:
            messagebox.showerror("Print Failed", f"Could not prepare PDF: {e}")
            return

        try:
            sysname = platform.system().lower()
            if sysname == "windows":
                os.startfile(path, "print")  # type: ignore[attr-defined]
            elif sysname == "darwin":
                os.system(f"lp '{path}'")
            else:
                os.system(f"lp '{path}' || lpr '{path}'")
            self.status_var.set("Sent to printer.")
        except Exception as e:
            messagebox.showerror("Print Failed", f"Could not send to printer: {e}")

    # -------------------- PDF / Print Due Report -------------------- #

    # -------------------- PDF / Print Due Report -------------------- #

    # -------------------- PDF / Print Overdue (30+ days) Report -------------------- #

    # -------------------- PDF / Print Overdue (30+ days) Report -------------------- #
    # -------------------- PDF / Print Overdue (30+ days) Report -------------------- #

    def _generate_due_report_pdf(self, path):
        """
        Overdue report (30+ days after invoice_submission_date).
        Groups by Company + Invoice Month.
        - Total Debit: only debits whose invoice_submission_date is > OVERDUE_DAYS days old
        - Total Credit: all credits for that company + month
        - Balance = Overdue Debit - Total Credit
        Only rows with Balance > 0 are shown.
        """
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm

        c = self.conn.cursor()
        c.execute("""
            SELECT
                company_name,
                COALESCE(invoice_month, 'N/A') AS inv_month,
                COALESCE(SUM(
                    CASE
                        WHEN invoice_submission_date IS NOT NULL
                             AND invoice_submission_date <> ''
                             AND (julianday('now') - julianday(invoice_submission_date)) > ?
                        THEN debit
                        ELSE 0
                    END
                ), 0) AS overdue_debit,
                COALESCE(SUM(credit), 0) AS total_credit
            FROM records
            GROUP BY company_name, inv_month
            HAVING overdue_debit > total_credit
            ORDER BY company_name, inv_month;
        """, (OVERDUE_DAYS,))

        rows = c.fetchall()

        # Totals
        total_overdue_debit = sum(r[2] for r in rows)
        total_credit = sum(r[3] for r in rows)
        total_balance = total_overdue_debit - total_credit

        # --- Build PDF ---
        canv = canvas.Canvas(path, pagesize=landscape(A4))
        width, height = landscape(A4)
        margin = 12 * mm
        x = margin
        y = height - margin

        title = f"Clients Overdue Report (>{OVERDUE_DAYS} days after submission) — {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        canv.setFont("Helvetica-Bold", 14)
        canv.drawString(x, y, title)
        y -= 10 * mm

        headers = ["Company", "Invoice Month", "Total Debit", "Total Credit", "Balance"]
        col_w = [220, 120, 90, 90, 90]

        def draw_header(ypos):
            canv.setFont("Helvetica-Bold", 10)
            cx = x
            for h, w in zip(headers, col_w):
                canv.drawString(cx, ypos, h)
                cx += w
            return ypos - 6 * mm

        # draw header first
        y = draw_header(y)
        canv.setFont("Helvetica", 9)

        for company, inv_month, overdue_debit, credits in rows:
            balance = overdue_debit - credits
            values = [company, inv_month, f"{overdue_debit:.2f}", f"{credits:.2f}", f"{balance:.2f}"]
            cx = x
            for val, w in zip(values, col_w):
                s = str(val)
                max_chars = int(w / 4.5)
                if len(s) > max_chars:
                    s = s[: max_chars - 1] + "…"
                canv.drawString(cx, y, s)
                cx += w
            y -= 6 * mm

            if y < margin + 20:
                canv.showPage()
                y = height - margin
                y = draw_header(y)
                canv.setFont("Helvetica", 9)

        # Totals row
        y -= 8 * mm
        canv.setFont("Helvetica-Bold", 10)
        canv.drawString(x, y, f"TOTAL DEBIT: {total_overdue_debit:.2f}")
        canv.drawString(x + 260, y, f"TOTAL CREDIT: {total_credit:.2f}")
        canv.drawString(x + 400, y, f"TOTAL BALANCE: {total_balance:.2f}")

        canv.save()

    def export_due_pdf(self):
        path = self._ask_savepath("Save Overdue Report PDF", ".pdf", [("PDF", "*.pdf")])
        if not path:
            return
        try:
            self._generate_due_report_pdf(path)
            self.status_var.set(f"Overdue Report PDF saved: {os.path.basename(path)}")
            messagebox.showinfo("Export Complete", f"Overdue Report PDF saved to: {path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not save Overdue Report PDF: {e}")

    def print_due_report(self):
        try:
            tmpdir = tempfile.gettempdir()
            path = os.path.join(tmpdir, f"client_overdue_{int(datetime.now().timestamp())}.pdf")
            self._generate_due_report_pdf(path)

            sysname = platform.system().lower()
            if sysname == "windows":
                os.startfile(path, "print")  # type: ignore[attr-defined]
            elif sysname == "darwin":
                os.system(f"lp '{path}'")
            else:
                os.system(f"lp '{path}' || lpr '{path}'")
            self.status_var.set("Overdue report sent to printer.")
        except Exception as e:
            messagebox.showerror("Print Failed", f"Could not print overdue report: {e}")

    def _sort_by(self, col, descending):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children("")]
        def coerce(v):
            try:
                return float(v)
            except Exception:
                dt = parse_date(v)
                return dt or v
        data.sort(key=lambda t: coerce(t[0]), reverse=descending)
        for idx, item in enumerate(data):
            self.tree.move(item[1], "", idx)
            current = self.tree.item(item[1], "tags")
            base = ["evenrow" if idx % 2 == 0 else "oddrow"]
            if "overdue" in current:
                base.append("overdue")
            self.tree.item(item[1], tags=base)
        self.tree.heading(col, command=lambda: self._sort_by(col, not descending))

if __name__ == "__main__":
    app = ClientBalanceApp()
    app.mainloop()
