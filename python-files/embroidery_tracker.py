#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Embroidery Work Tracker — Desktop App (Tkinter + SQLite)
Author: ChatGPT for Muhammad Sufyan

Features
- Workers & Designs master lists
- Assign Work (auto Work ID)
- Track status: Pending / In Progress / Done
- Search & Filter by Worker, Status, Work ID/Design Code
- Edit remarks, update status, delete assignment
- Basic reports (counts per status, per worker)
- Export assignments to CSV

How to run
1) Install Python 3.10+ from https://python.org
2) Save this file as embroidery_tracker.py
3) Run:  python embroidery_tracker.py

Make a Windows .exe (optional)
- Install:  pip install pyinstaller
- Build:    pyinstaller --onefile --noconsole embroidery_tracker.py
  The EXE will be in the "dist" folder.

Database: embroidery.db (auto-created in same folder)
"""

import os
import sqlite3
import csv
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

APP_TITLE = "Embroidery Work Tracker"
DB_FILE = "embroidery.db"
DATE_FMT = "%Y-%m-%d"

STATUS_CHOICES = ["Pending", "In Progress", "Done"]

# ------------------------- Database Layer ------------------------- #

def get_conn():
    return sqlite3.connect(DB_FILE)


def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS designs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                fabric TEXT
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_id TEXT NOT NULL UNIQUE,
                worker_id INTEGER NOT NULL,
                design_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                given_date TEXT NOT NULL,
                due_date TEXT,
                status TEXT NOT NULL DEFAULT 'Pending',
                remarks TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(worker_id) REFERENCES workers(id),
                FOREIGN KEY(design_id) REFERENCES designs(id)
            );
            """
        )
        conn.commit()


def add_worker(name: str, phone: str = ""):
    if not name.strip():
        raise ValueError("Worker name required")
    with get_conn() as conn:
        conn.execute("INSERT INTO workers(name, phone) VALUES(?, ?)", (name.strip(), phone.strip()))
        conn.commit()


def get_workers():
    with get_conn() as conn:
        return conn.execute("SELECT id, name, phone FROM workers ORDER BY name").fetchall()


def delete_worker(worker_id: int):
    with get_conn() as conn:
        # Prevent delete if assignments exist
        cnt = conn.execute("SELECT COUNT(*) FROM assignments WHERE worker_id=?", (worker_id,)).fetchone()[0]
        if cnt:
            raise RuntimeError("Cannot delete: Worker has assignments.")
        conn.execute("DELETE FROM workers WHERE id=?", (worker_id,))
        conn.commit()


def add_design(code: str, fabric: str = ""):
    if not code.strip():
        raise ValueError("Design code required")
    with get_conn() as conn:
        conn.execute("INSERT INTO designs(code, fabric) VALUES(?, ?)", (code.strip(), fabric.strip()))
        conn.commit()


def get_designs():
    with get_conn() as conn:
        return conn.execute("SELECT id, code, fabric FROM designs ORDER BY code").fetchall()


def delete_design(design_id: int):
    with get_conn() as conn:
        cnt = conn.execute("SELECT COUNT(*) FROM assignments WHERE design_id=?", (design_id,)).fetchone()[0]
        if cnt:
            raise RuntimeError("Cannot delete: Design has assignments.")
        conn.execute("DELETE FROM designs WHERE id=?", (design_id,))
        conn.commit()


def next_work_id(today=None) -> str:
    # Format: W-YYYYMMDD-#### (sequence per day)
    if today is None:
        today = date.today()
    day = today.strftime("%Y%m%d")
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT COUNT(*) FROM assignments WHERE work_id LIKE ?",
            (f"W-{day}-%",),
        )
        count_today = cur.fetchone()[0]
    return f"W-{day}-{count_today + 1:04d}"


def add_assignment(worker_id: int, design_id: int, quantity: int, given_date: str, due_date: str, remarks: str):
    wid = next_work_id()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO assignments(work_id, worker_id, design_id, quantity, given_date, due_date, status, remarks, created_at)
            VALUES(?, ?, ?, ?, ?, ?, 'Pending', ?, ?)
            """,
            (wid, worker_id, design_id, quantity, given_date, due_date, remarks, now),
        )
        conn.commit()
    return wid


def fetch_assignments(worker_id=None, status=None, search_text=""):
    q = [
        "SELECT a.id, a.work_id, w.name, d.code, a.quantity, a.given_date, a.due_date, a.status, a.remarks",
        "FROM assignments a",
        "JOIN workers w ON w.id=a.worker_id",
        "JOIN designs d ON d.id=a.design_id",
        "WHERE 1=1",
    ]
    params = []
    if worker_id:
        q.append("AND a.worker_id=?")
        params.append(worker_id)
    if status and status != "All":
        q.append("AND a.status=?")
        params.append(status)
    if search_text:
        q.append("AND (a.work_id LIKE ? OR d.code LIKE ?)")
        like = f"%{search_text}%"
        params.extend([like, like])
    q.append("ORDER BY a.id DESC")
    sql = " ".join(q)

    with get_conn() as conn:
        return conn.execute(sql, params).fetchall()


def update_assignment_status(assignment_id: int, new_status: str):
    if new_status not in STATUS_CHOICES:
        raise ValueError("Invalid status")
    with get_conn() as conn:
        conn.execute("UPDATE assignments SET status=? WHERE id=?", (new_status, assignment_id))
        conn.commit()


def update_assignment_remarks(assignment_id: int, remarks: str):
    with get_conn() as conn:
        conn.execute("UPDATE assignments SET remarks=? WHERE id=?", (remarks, assignment_id))
        conn.commit()


def delete_assignment(assignment_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM assignments WHERE id=?", (assignment_id,))
        conn.commit()


def report_counts_by_status():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) FROM assignments GROUP BY status"
        ).fetchall()
    return rows


def report_counts_by_worker():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT w.name, 
                   SUM(a.status='Pending') as pending,
                   SUM(a.status='In Progress') as inprog,
                   SUM(a.status='Done') as done,
                   COUNT(*) as total
            FROM assignments a JOIN workers w ON w.id=a.worker_id
            GROUP BY w.name
            ORDER BY w.name
            """
        ).fetchall()
    return rows

# ------------------------- UI Layer ------------------------- #

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1100x700")
        self.minsize(1000, 650)

        self.style = ttk.Style(self)
        try:
            self.style.theme_use('clam')
        except tk.TclError:
            pass

        self.create_widgets()
        self.refresh_all()

    # --- UI Construction --- #
    def create_widgets(self):
        # Top bar
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=8)
        ttk.Label(top, text=APP_TITLE, font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT)
        ttk.Button(top, text="Export CSV", command=self.export_csv).pack(side=tk.RIGHT, padx=5)
        ttk.Button(top, text="Reports", command=self.show_reports).pack(side=tk.RIGHT, padx=5)

        # Main panes
        main = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

        # Left: Masters & New Assignment form (Notebook)
        left = ttk.Notebook(main)
        main.add(left, weight=1)

        # Workers Tab
        self.tab_workers = ttk.Frame(left)
        left.add(self.tab_workers, text="Workers")
        self.build_workers_tab()

        # Designs Tab
        self.tab_designs = ttk.Frame(left)
        left.add(self.tab_designs, text="Designs")
        self.build_designs_tab()

        # Assign Tab (create new)
        self.tab_assign = ttk.Frame(left)
        left.add(self.tab_assign, text="Assign Work")
        self.build_assign_tab()

        # Right: Assignments list & filters
        right = ttk.Frame(main)
        main.add(right, weight=3)
        self.build_assignments_list(right)

    def build_workers_tab(self):
        frm = self.tab_workers
        # Add worker form
        f1 = ttk.LabelFrame(frm, text="Add Worker")
        f1.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(f1, text="Name").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.worker_name_var = tk.StringVar()
        ttk.Entry(f1, textvariable=self.worker_name_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(f1, text="Phone").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.worker_phone_var = tk.StringVar()
        ttk.Entry(f1, textvariable=self.worker_phone_var).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        f1.columnconfigure(1, weight=1)
        ttk.Button(f1, text="Add Worker", command=self.on_add_worker).grid(row=2, column=0, columnspan=2, pady=8)

        # Worker list
        f2 = ttk.LabelFrame(frm, text="Workers")
        f2.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        self.tv_workers = ttk.Treeview(f2, columns=("id", "name", "phone"), show="headings", height=8)
        for c, w in [("id", 60), ("name", 180), ("phone", 140)]:
            self.tv_workers.heading(c, text=c.title())
            self.tv_workers.column(c, width=w, anchor="w")
        self.tv_workers.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        sb = ttk.Scrollbar(f2, orient=tk.VERTICAL, command=self.tv_workers.yview)
        self.tv_workers.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        btns = ttk.Frame(frm)
        btns.pack(fill=tk.X, padx=10, pady=(0,10))
        ttk.Button(btns, text="Delete Selected Worker", command=self.on_delete_worker).pack(side=tk.LEFT)

    def build_designs_tab(self):
        frm = self.tab_designs
        f1 = ttk.LabelFrame(frm, text="Add Design")
        f1.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(f1, text="Design Code").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.design_code_var = tk.StringVar()
        ttk.Entry(f1, textvariable=self.design_code_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(f1, text="Fabric/Type").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.design_fabric_var = tk.StringVar()
        ttk.Entry(f1, textvariable=self.design_fabric_var).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        f1.columnconfigure(1, weight=1)
        ttk.Button(f1, text="Add Design", command=self.on_add_design).grid(row=2, column=0, columnspan=2, pady=8)

        f2 = ttk.LabelFrame(frm, text="Designs")
        f2.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        self.tv_designs = ttk.Treeview(f2, columns=("id", "code", "fabric"), show="headings", height=8)
        for c, w in [("id", 60), ("code", 160), ("fabric", 180)]:
            self.tv_designs.heading(c, text=c.title())
            self.tv_designs.column(c, width=w, anchor="w")
        self.tv_designs.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        sb = ttk.Scrollbar(f2, orient=tk.VERTICAL, command=self.tv_designs.yview)
        self.tv_designs.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        btns = ttk.Frame(frm)
        btns.pack(fill=tk.X, padx=10, pady=(0,10))
        ttk.Button(btns, text="Delete Selected Design", command=self.on_delete_design).pack(side=tk.LEFT)

    def build_assign_tab(self):
        frm = self.tab_assign
        f = ttk.LabelFrame(frm, text="Create New Assignment")
        f.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(f, text="Worker").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.cmb_worker = ttk.Combobox(f, state="readonly")
        self.cmb_worker.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(f, text="Design").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.cmb_design = ttk.Combobox(f, state="readonly")
        self.cmb_design.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(f, text="Quantity").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.qty_var = tk.IntVar(value=1)
        ttk.Entry(f, textvariable=self.qty_var).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(f, text="Given Date (YYYY-MM-DD)").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.given_var = tk.StringVar(value=date.today().strftime(DATE_FMT))
        ttk.Entry(f, textvariable=self.given_var).grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(f, text="Due Date (YYYY-MM-DD)").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.due_var = tk.StringVar(value="")
        ttk.Entry(f, textvariable=self.due_var).grid(row=4, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(f, text="Remarks").grid(row=5, column=0, sticky="nw", padx=5, pady=5)
        self.remarks_text = tk.Text(f, height=4)
        self.remarks_text.grid(row=5, column=1, sticky="ew", padx=5, pady=5)

        f.columnconfigure(1, weight=1)
        ttk.Button(f, text="Assign Work", command=self.on_assign).grid(row=6, column=0, columnspan=2, pady=10)

    def build_assignments_list(self, parent):
        # Filters
        top = ttk.LabelFrame(parent, text="Filters")
        top.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(top, text="Worker").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.filter_worker = ttk.Combobox(top, state="readonly")
        self.filter_worker.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(top, text="Status").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.filter_status = ttk.Combobox(top, state="readonly", values=["All"] + STATUS_CHOICES)
        self.filter_status.set("All")
        self.filter_status.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        ttk.Label(top, text="Search (Work ID / Design)").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.filter_search = ttk.Entry(top)
        self.filter_search.grid(row=0, column=5, sticky="ew", padx=5, pady=5)

        ttk.Button(top, text="Apply", command=self.refresh_assignments).grid(row=0, column=6, padx=5)
        ttk.Button(top, text="Clear", command=self.clear_filters).grid(row=0, column=7, padx=5)
        top.columnconfigure(5, weight=1)

        # Treeview
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        cols = ("id","work_id","worker","design","qty","given","due","status","remarks")
        self.tv_assign = ttk.Treeview(frame, columns=cols, show="headings")
        headings = [
            ("id", 60), ("work_id", 140), ("worker", 160), ("design", 120),
            ("qty", 60), ("given", 100), ("due", 100), ("status", 110), ("remarks", 260)
        ]
        for c, w in headings:
            self.tv_assign.heading(c, text=c.upper())
            self.tv_assign.column(c, width=w, anchor="w")
        self.tv_assign.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        sb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tv_assign.yview)
        self.tv_assign.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # Action buttons
        btns = ttk.Frame(parent)
        btns.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btns, text="Mark In Progress", command=lambda: self.bulk_update_status("In Progress")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Mark Done", command=lambda: self.bulk_update_status("Done")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Edit Remarks", command=self.on_edit_remarks).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Delete", command=self.on_delete_assignment).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Refresh", command=self.refresh_assignments).pack(side=tk.RIGHT)

    # --- Event Handlers --- #
    def on_add_worker(self):
        name = self.worker_name_var.get().strip()
        phone = self.worker_phone_var.get().strip()
        try:
            add_worker(name, phone)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self.worker_name_var.set("")
        self.worker_phone_var.set("")
        self.refresh_workers()
        self.refresh_worker_comboboxes()

    def on_delete_worker(self):
        sel = self.tv_workers.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a worker to delete.")
            return
        item = self.tv_workers.item(sel[0])
        worker_id = int(item['values'][0])
        if not messagebox.askyesno("Confirm", "Delete selected worker? This cannot be undone."):
            return
        try:
            delete_worker(worker_id)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self.refresh_workers()
        self.refresh_worker_comboboxes()

    def on_add_design(self):
        code = self.design_code_var.get().strip()
        fabric = self.design_fabric_var.get().strip()
        try:
            add_design(code, fabric)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Design code must be unique.")
            return
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self.design_code_var.set("")
        self.design_fabric_var.set("")
        self.refresh_designs()
        self.refresh_design_comboboxes()

    def on_delete_design(self):
        sel = self.tv_designs.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a design to delete.")
            return
        item = self.tv_designs.item(sel[0])
        design_id = int(item['values'][0])
        if not messagebox.askyesno("Confirm", "Delete selected design? This cannot be undone."):
            return
        try:
            delete_design(design_id)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self.refresh_designs()
        self.refresh_design_comboboxes()

    def on_assign(self):
        w_idx = self.cmb_worker.current()
        d_idx = self.cmb_design.current()
        if w_idx == -1 or d_idx == -1:
            messagebox.showerror("Error", "Select Worker and Design")
            return
        worker_id = self.cmb_worker_ids[w_idx]
        design_id = self.cmb_design_ids[d_idx]

        try:
            qty = int(self.qty_var.get())
            if qty <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Quantity must be a positive integer")
            return

        given = self.given_var.get().strip()
        due = self.due_var.get().strip()
        # Basic date sanity
        try:
            datetime.strptime(given, DATE_FMT)
            if due:
                datetime.strptime(due, DATE_FMT)
        except Exception:
            messagebox.showerror("Error", "Dates must be in YYYY-MM-DD format")
            return

        remarks = self.remarks_text.get("1.0", tk.END).strip()
        try:
            wid = add_assignment(worker_id, design_id, qty, given, due, remarks)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        messagebox.showinfo("Assigned", f"Work assigned with ID: {wid}")
        self.remarks_text.delete("1.0", tk.END)
        self.qty_var.set(1)
        self.refresh_assignments()

    def bulk_update_status(self, new_status: str):
        sels = self.tv_assign.selection()
        if not sels:
            messagebox.showinfo("Info", "Select one or more rows.")
            return
        for s in sels:
            aid = int(self.tv_assign.item(s)['values'][0])
            try:
                update_assignment_status(aid, new_status)
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
        self.refresh_assignments()

    def on_edit_remarks(self):
        sel = self.tv_assign.selection()
        if not sel:
            messagebox.showinfo("Info", "Select one row.")
            return
        aid = int(self.tv_assign.item(sel[0])['values'][0])
        current = self.tv_assign.item(sel[0])['values'][8]
        new_text = simpledialog.askstring("Edit Remarks", "Remarks:", initialvalue=current)
        if new_text is None:
            return
        update_assignment_remarks(aid, new_text.strip())
        self.refresh_assignments()

    def on_delete_assignment(self):
        sels = self.tv_assign.selection()
        if not sels:
            messagebox.showinfo("Info", "Select one or more rows.")
            return
        if not messagebox.askyesno("Confirm", "Delete selected assignment(s)?"):
            return
        for s in sels:
            aid = int(self.tv_assign.item(s)['values'][0])
            delete_assignment(aid)
        self.refresh_assignments()

    def clear_filters(self):
        self.filter_search.delete(0, tk.END)
        self.filter_status.set("All")
        if self.filter_worker['values']:
            self.filter_worker.current(0)
        self.refresh_assignments()

    def show_reports(self):
        win = tk.Toplevel(self)
        win.title("Reports")
        win.geometry("600x400")

        frame = ttk.Frame(win)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Status Summary
        ttk.Label(frame, text="Counts by Status", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tv1 = ttk.Treeview(frame, columns=("status","count"), show="headings", height=4)
        tv1.heading("status", text="STATUS")
        tv1.heading("count", text="COUNT")
        tv1.column("status", width=160)
        tv1.column("count", width=100)
        tv1.pack(fill=tk.X, pady=(5,10))

        for status, cnt in report_counts_by_status():
            tv1.insert('', tk.END, values=(status, cnt))

        # Worker Summary
        ttk.Label(frame, text="Per Worker Summary", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10,0))
        tv2 = ttk.Treeview(frame, columns=("worker","pending","inprog","done","total"), show="headings", height=8)
        for c, w in [("worker", 180), ("pending", 90), ("inprog", 90), ("done", 90), ("total", 90)]:
            tv2.heading(c, text=c.upper())
            tv2.column(c, width=w, anchor="w")
        tv2.pack(fill=tk.BOTH, expand=True, pady=(5,0))

        for row in report_counts_by_worker():
            tv2.insert('', tk.END, values=row)

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], initialfile="assignments_export.csv"
        )
        if not path:
            return
        rows = fetch_assignments()
        headers = ["ID","WorkID","Worker","Design","Quantity","Given","Due","Status","Remarks"]
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            messagebox.showinfo("Exported", f"Saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # --- Data refresh helpers --- #
    def refresh_all(self):
        self.refresh_workers()
        self.refresh_worker_comboboxes()
        self.refresh_designs()
        self.refresh_design_comboboxes()
        self.refresh_filter_workers()
        self.refresh_assignments()

    def refresh_workers(self):
        for i in self.tv_workers.get_children():
            self.tv_workers.delete(i)
        for row in get_workers():
            self.tv_workers.insert('', tk.END, values=row)

    def refresh_designs(self):
        for i in self.tv_designs.get_children():
            self.tv_designs.delete(i)
        for row in get_designs():
            self.tv_designs.insert('', tk.END, values=row)

    def refresh_worker_comboboxes(self):
        workers = get_workers()
        names = [w[1] for w in workers]
        self.cmb_worker_ids = [w[0] for w in workers]
        self.cmb_worker['values'] = names
        if names:
            self.cmb_worker.current(0)

    def refresh_design_comboboxes(self):
        designs = get_designs()
        codes = [d[1] for d in designs]
        self.cmb_design_ids = [d[0] for d in designs]
        self.cmb_design['values'] = codes
        if codes:
            self.cmb_design.current(0)

    def refresh_filter_workers(self):
        workers = get_workers()
        vals = ["All"] + [w[1] for w in workers]
        self.filter_worker['values'] = vals
        if vals:
            self.filter_worker.current(0)
        # Map name -> id for filtering
        self.worker_name_to_id = {w[1]: w[0] for w in workers}

    def refresh_assignments(self):
        # Determine filters
        wname = self.filter_worker.get().strip()
        worker_id = None
        if wname and wname != "All":
            worker_id = self.worker_name_to_id.get(wname)
        status = self.filter_status.get().strip() or "All"
        search = self.filter_search.get().strip()

        # Get rows and fill
        rows = fetch_assignments(worker_id=worker_id, status=status, search_text=search)
        for i in self.tv_assign.get_children():
            self.tv_assign.delete(i)
        for row in rows:
            self.tv_assign.insert('', tk.END, values=row)


# ------------------------- Main ------------------------- #

def main():
    init_db()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
