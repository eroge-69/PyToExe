"""
TECHWIZ Tuition Fees Manager - Single-file (IDLE-ready)

Features:
 - Student DB with separate Sat/Sun batch fields (batch_no + timing)
 - Batches table with 'day' (Saturday/Sunday), batch_no, batch_time, total_seats, seats_taken
 - When adding/updating/deleting students, seats_taken updates automatically per day/batch
 - Batches tab shows students holding seats for selected batch
 - Payments, PDF receipts, exports to XLSX/PDF, charts (optional libs)
 - Uses SQLite: fees_manager.db (same folder)
 - Optional libraries: pillow, tkcalendar, pandas, openpyxl, reportlab, matplotlib
 - Save as TECHWIZ_fees_manager.py and run in IDLE
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, date
import calendar
import os
from collections import defaultdict

# Optional libs
try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

try:
    from tkcalendar import DateEntry
except Exception:
    DateEntry = None

try:
    import pandas as pd
except Exception:
    pd = None

try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
except Exception:
    pdf_canvas = None

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.cm as cm
except Exception:
    Figure = None
    FigureCanvasTkAgg = None
    cm = None

# Basic center info
DB_FILE = "fees_manager.db"
CENTER_NAME = "TECHWIZ Tuition Fees Manager"
CENTER_CONTACT = "8961312523"
CENTER_ADDRESS = "3/31 Parui Das Para Road, Kolkata - 700061"
SOFTWARE_DEV = "Software Developer: Surajit Ghosh"
# NOTE: Class footer removed as per user request

# ---------------- DB helpers ----------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Students: separate Sat and Sun batch fields + admission_date stored ISO
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sat_batch_no TEXT,
            sat_batch_time TEXT,
            sun_batch_no TEXT,
            sun_batch_time TEXT,
            contact TEXT,
            address TEXT,
            admission_date TEXT,
            photo_path TEXT
        )
    """)
    # Payments
    c.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            month INTEGER,
            year INTEGER,
            amount REAL,
            date_received TEXT,
            note TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)
    # Batches: day = 'Saturday' or 'Sunday'
    c.execute("""
        CREATE TABLE IF NOT EXISTS batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            batch_no TEXT NOT NULL,
            batch_time TEXT,
            total_seats INTEGER DEFAULT 0,
            seats_taken INTEGER DEFAULT 0,
            UNIQUE(day, batch_no)
        )
    """)
    conn.commit()
    conn.close()

def query_db(query, params=(), fetch=False):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(query, params)
    if fetch:
        rows = c.fetchall()
        conn.close()
        return rows
    conn.commit()
    conn.close()

# ---------------- App ----------------
class FeesManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(CENTER_NAME)
        self.geometry("1200x760")
        self.configure(bg="white")
        self.style = ttk.Style(self)
        try:
            self.style.theme_use('clam')
        except Exception:
            pass
        # some style hints
        try:
            self.style.configure('Accent.TButton', background='#4CAF50', foreground='white')
            self.style.configure('Danger.TButton', background='#E53935', foreground='white')
        except Exception:
            pass

        # Header
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", padx=10, pady=(10,0))
        tk.Label(header, text=CENTER_NAME, font=("Segoe UI", 18, "bold"), bg="white").pack(side="left")
        info = tk.Label(header, text=f"Contact: {CENTER_CONTACT}    {CENTER_ADDRESS}", bg="white", anchor="e")
        info.pack(side="right")

        # Search
        search_frame = tk.Frame(self, bg="white")
        search_frame.pack(fill="x", padx=10, pady=(6,0))
        tk.Label(search_frame, text="Search:", bg="white").pack(side="left")
        self.search_var = tk.StringVar()
        se = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        se.pack(side="left", padx=6)
        se.bind("<KeyRelease>", lambda e: self.perform_search())
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side="left", padx=4)

        # Notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)
        self.nb = nb

        # Tabs
        self.tab_students = ttk.Frame(nb)
        self.tab_payments = ttk.Frame(nb)
        self.tab_batches = ttk.Frame(nb)
        self.tab_reports = ttk.Frame(nb)

        nb.add(self.tab_students, text="Student Database")
        nb.add(self.tab_payments, text="Payments")
        nb.add(self.tab_batches, text="Batches")
        nb.add(self.tab_reports, text="Reports")

        # Build each tab
        self.build_students_tab()
        self.build_payments_tab()
        self.build_batches_tab()
        self.build_reports_tab()

        # initial loads
        self.refresh_students_tree()
        self.refresh_payments_tree()
        self.refresh_batches_tree()
        self.refresh_student_combobox()

    # ---------------- Students Tab ----------------
    def build_students_tab(self):
        frame = self.tab_students
        form = tk.Frame(frame, bg="white", pady=6)
        form.pack(fill="x", padx=10)

        # Fields: name, sat_batch_no, sat_batch_time, sun_batch_no, sun_batch_time, contact, address, admission_date
        labels = ["Student Name:", "Sat Batch No:", "Sat Batch Timing:", "Sun Batch No:", "Sun Batch Timing:", "Contact No:", "Address:", "Admission Date:"]
        self.student_vars = [tk.StringVar() for _ in labels]
        for i, lbl in enumerate(labels):
            row = tk.Frame(form, bg="white")
            row.pack(fill="x", pady=2)
            tk.Label(row, text=lbl, width=18, anchor="w", bg="white").pack(side="left")
            if lbl == "Admission Date:":
                if DateEntry:
                    de = DateEntry(row, date_pattern='dd/mm/yyyy', textvariable=self.student_vars[i], width=20)
                    de.pack(side="left", padx=5)
                else:
                    ent = ttk.Entry(row, textvariable=self.student_vars[i], width=20)
                    ent.pack(side="left", padx=5)
                    ent.insert(0, date.today().strftime('%d/%m/%Y'))
            else:
                ent = ttk.Entry(row, textvariable=self.student_vars[i], width=50)
                ent.pack(side="left", padx=5)

        # Photo
        photo_row = tk.Frame(form, bg="white")
        photo_row.pack(fill="x", pady=2)
        tk.Label(photo_row, text="Photo:", width=18, anchor="w", bg="white").pack(side="left")
        self.photo_path_var = tk.StringVar()
        ttk.Button(photo_row, text="Upload Photo", command=self.upload_photo).pack(side="left")
        self.photo_thumb_lbl = tk.Label(photo_row, bg="white")
        self.photo_thumb_lbl.pack(side="left", padx=8)

        # Buttons
        btn_frame = tk.Frame(form, bg="white")
        btn_frame.pack(fill="x", pady=(6,0))
        ttk.Button(btn_frame, text="Add Student", style='Accent.TButton', command=self.add_student).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Update Selected", command=self.update_student).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Delete Selected", style='Danger.TButton', command=self.delete_student).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_student_form).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Export Students", command=self.export_students).pack(side="left", padx=6)

        # Treeview for students
        list_frame = tk.Frame(frame, bg="white")
        list_frame.pack(fill="both", expand=True, padx=10, pady=6)
        columns = ("id", "name", "sat_batch_no", "sat_batch_time", "sun_batch_no", "sun_batch_time", "contact", "address", "admission_date")
        self.students_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        headings = ["ID","Name","Sat Batch No","Sat Timing","Sun Batch No","Sun Timing","Contact","Address","Admission Date"]
        widths = [50,180,100,100,100,100,100,180,100]
        for col, h, w in zip(columns, headings, widths):
            self.students_tree.heading(col, text=h)
            self.students_tree.column(col, width=w, anchor="w")
        self.students_tree.pack(side="left", fill="both", expand=True)
        self.students_tree.bind("<<TreeviewSelect>>", lambda e: self.load_student_from_selection())

        vs = ttk.Scrollbar(list_frame, orient="vertical", command=self.students_tree.yview)
        vs.pack(side="right", fill="y")
        self.students_tree.configure(yscrollcommand=vs.set)

    def upload_photo(self):
        path = filedialog.askopenfilename(title="Select Photo", filetypes=[("Image files","*.png;*.jpg;*.jpeg;*.bmp")])
        if path:
            self.photo_path_var.set(path)
            self.show_thumbnail(path)

    def show_thumbnail(self, path):
        if Image is None or ImageTk is None:
            return
        try:
            im = Image.open(path)
            im.thumbnail((64,64))
            self.photo_thumb = ImageTk.PhotoImage(im)
            self.photo_thumb_lbl.config(image=self.photo_thumb)
        except Exception as e:
            messagebox.showwarning("Photo", f"Could not open image: {e}")

    def add_student(self):
        vals = [v.get().strip() for v in self.student_vars]
        if not vals[0]:
            messagebox.showwarning("Missing", "Student name required")
            return
        # admission date parse
        adm = vals[7]
        try:
            if adm:
                dt = datetime.strptime(adm, '%d/%m/%Y')
                adm_iso = dt.date().isoformat()
            else:
                adm_iso = date.today().isoformat()
        except Exception:
            messagebox.showwarning("Date", "Admission date must be DD/MM/YYYY")
            return
        photo = self.photo_path_var.get().strip() or None
        query_db("""
            INSERT INTO students (name, sat_batch_no, sat_batch_time, sun_batch_no, sun_batch_time, contact, address, admission_date, photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (vals[0], vals[1] or None, vals[2] or None, vals[3] or None, vals[4] or None, vals[5] or None, vals[6] or None, adm_iso, photo))
        # update batch seat counts for provided sat/sun batches
        if vals[1]:
            self.ensure_batch_exists_and_increment('Saturday', vals[1], vals[2])
        if vals[3]:
            self.ensure_batch_exists_and_increment('Sunday', vals[3], vals[4])
        messagebox.showinfo("Added", "Student added successfully")
        self.clear_student_form()
        self.refresh_students_tree()
        self.refresh_student_combobox()
        self.refresh_batches_tree()

    def update_student(self):
        sel = self.get_selected_student_id()
        if not sel:
            messagebox.showwarning("Select", "Select a student to update")
            return
        vals = [v.get().strip() for v in self.student_vars]
        adm = vals[7]
        try:
            if adm:
                dt = datetime.strptime(adm, '%d/%m/%Y')
                adm_iso = dt.date().isoformat()
            else:
                adm_iso = date.today().isoformat()
        except Exception:
            messagebox.showwarning("Date", "Admission date must be DD/MM/YYYY")
            return
        photo = self.photo_path_var.get().strip() or None
        # get old sat/sun batch assignments
        old = query_db("SELECT sat_batch_no, sun_batch_no FROM students WHERE id=?", (sel,), fetch=True)
        old_sat, old_sun = (None, None)
        if old and old[0]:
            old_sat = old[0][0]
            old_sun = old[0][1]
        query_db("""
            UPDATE students SET name=?, sat_batch_no=?, sat_batch_time=?, sun_batch_no=?, sun_batch_time=?, contact=?, address=?, admission_date=?, photo_path=? WHERE id=?
        """, (vals[0], vals[1] or None, vals[2] or None, vals[3] or None, vals[4] or None, vals[5] or None, vals[6] or None, adm_iso, photo, sel))
        # adjust counts if batches changed
        new_sat = vals[1] or None
        new_sun = vals[3] or None
        if old_sat != new_sat:
            if old_sat:
                self.decrement_batch_taken('Saturday', old_sat)
            if new_sat:
                self.ensure_batch_exists_and_increment('Saturday', new_sat, vals[2])
        if old_sun != new_sun:
            if old_sun:
                self.decrement_batch_taken('Sunday', old_sun)
            if new_sun:
                self.ensure_batch_exists_and_increment('Sunday', new_sun, vals[4])
        messagebox.showinfo("Updated", "Student updated")
        self.refresh_students_tree()
        self.refresh_student_combobox()
        self.refresh_batches_tree()

    def delete_student(self):
        sel = self.get_selected_student_id()
        if not sel:
            messagebox.showwarning("Select", "Select a student to delete")
            return
        if not messagebox.askyesno("Confirm", "Delete student and all their payments?"):
            return
        # decrement sat/sun batches if assigned
        row = query_db("SELECT sat_batch_no, sun_batch_no FROM students WHERE id=?", (sel,), fetch=True)
        if row and row[0]:
            sat, sun = row[0][0], row[0][1]
            if sat:
                self.decrement_batch_taken('Saturday', sat)
            if sun:
                self.decrement_batch_taken('Sunday', sun)
        # delete payments and student
        query_db("DELETE FROM payments WHERE student_id=?", (sel,))
        query_db("DELETE FROM students WHERE id=?", (sel,))
        messagebox.showinfo("Deleted", "Student deleted")
        self.refresh_students_tree()
        self.refresh_payments_tree()
        self.refresh_student_combobox()
        self.refresh_batches_tree()
        self.clear_student_form()

    def clear_student_form(self):
        for v in self.student_vars:
            v.set("")
        self.photo_path_var.set("")
        if ImageTk:
            self.photo_thumb_lbl.config(image="")

    def refresh_students_tree(self):
        for row in self.students_tree.get_children():
            self.students_tree.delete(row)
        rows = query_db("""
            SELECT id, name, sat_batch_no, sat_batch_time, sun_batch_no, sun_batch_time, contact, address, admission_date
            FROM students ORDER BY name
        """, fetch=True)
        for r in rows:
            adm = r[8]
            display_date = adm
            try:
                display_date = datetime.strptime(adm, '%Y-%m-%d').strftime('%d/%m/%Y')
            except Exception:
                pass
            self.students_tree.insert("", "end", values=(r[0], r[1], r[2] or "", r[3] or "", r[4] or "", r[5] or "", r[6] or "", r[7] or "", display_date))

    def load_student_from_selection(self):
        sel = self.students_tree.selection()
        if not sel:
            return
        data = self.students_tree.item(sel[0])['values']
        if not data:
            return
        sid = data[0]
        row = query_db("SELECT name, sat_batch_no, sat_batch_time, sun_batch_no, sun_batch_time, contact, address, admission_date, photo_path FROM students WHERE id=?", (sid,), fetch=True)
        if not row:
            return
        name, sat_no, sat_time, sun_no, sun_time, contact, address, adm_iso, photo_path = row[0]
        self.student_vars[0].set(name or "")
        self.student_vars[1].set(sat_no or "")
        self.student_vars[2].set(sat_time or "")
        self.student_vars[3].set(sun_no or "")
        self.student_vars[4].set(sun_time or "")
        self.student_vars[5].set(contact or "")
        self.student_vars[6].set(address or "")
        adm_display = ""
        try:
            if adm_iso:
                adm_display = datetime.strptime(adm_iso, '%Y-%m-%d').strftime('%d/%m/%Y')
        except Exception:
            adm_display = adm_iso or ""
        self.student_vars[7].set(adm_display)
        if photo_path:
            self.photo_path_var.set(photo_path)
            self.show_thumbnail(photo_path)
        else:
            self.photo_path_var.set("")
            if ImageTk:
                self.photo_thumb_lbl.config(image="")

    def get_selected_student_id(self):
        sel = self.students_tree.selection()
        if not sel:
            return None
        return self.students_tree.item(sel[0])['values'][0]

    # ---------------- Payments Tab ----------------
    def build_payments_tab(self):
        frame = self.tab_payments
        top = tk.Frame(frame, bg="white", pady=8)
        top.pack(fill="x", padx=10)

        tk.Label(top, text="Student:", bg="white", width=12, anchor="w").grid(row=0, column=0, sticky="w")
        self.payment_student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(top, textvariable=self.payment_student_var, width=50)
        self.student_combo.grid(row=0, column=1, sticky="w", padx=4)

        tk.Label(top, text="Month:", bg="white", width=12, anchor="w").grid(row=1, column=0, sticky="w")
        months = [calendar.month_name[i] for i in range(1,13)]
        self.payment_month_var = tk.StringVar(value=months[date.today().month-1])
        self.month_combo = ttk.Combobox(top, values=months, textvariable=self.payment_month_var, width=20)
        self.month_combo.grid(row=1, column=1, sticky="w", padx=4)

        tk.Label(top, text="Year:", bg="white", width=12, anchor="w").grid(row=2, column=0, sticky="w")
        years = [str(y) for y in range(date.today().year-5, date.today().year+6)]
        self.payment_year_var = tk.StringVar(value=str(date.today().year))
        self.year_combo = ttk.Combobox(top, values=years, textvariable=self.payment_year_var, width=20)
        self.year_combo.grid(row=2, column=1, sticky="w", padx=4)

        tk.Label(top, text="Amount:", bg="white", width=12, anchor="w").grid(row=0, column=2, sticky="w")
        self.payment_amount_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.payment_amount_var, width=20).grid(row=0, column=3, sticky="w", padx=4)

        tk.Label(top, text="Date (DD/MM/YYYY):", bg="white", width=16, anchor="w").grid(row=1, column=2, sticky="w")
        self.payment_date_var = tk.StringVar()
        if DateEntry:
            de = DateEntry(top, date_pattern='dd/mm/yyyy', textvariable=self.payment_date_var, width=18)
            de.grid(row=1, column=3, sticky="w", padx=4)
        else:
            ent = ttk.Entry(top, textvariable=self.payment_date_var, width=20)
            ent.grid(row=1, column=3, sticky="w", padx=4)
            ent.insert(0, date.today().strftime('%d/%m/%Y'))

        tk.Label(top, text="Note:", bg="white", width=12, anchor="w").grid(row=2, column=2, sticky="w")
        self.payment_note_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.payment_note_var, width=40).grid(row=2, column=3, sticky="w", padx=4)

        btn_frame = tk.Frame(top, bg="white")
        btn_frame.grid(row=3, column=0, columnspan=4, pady=(8,0))
        ttk.Button(btn_frame, text="Receive Payment", style='Accent.TButton', command=self.receive_payment).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Generate Receipt (PDF)", command=self.generate_receipt_pdf).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Delete Selected Payment", style='Danger.TButton', command=self.delete_payment).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Clear Fields", command=self.clear_payment_fields).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_payments_tree).pack(side="left", padx=4)

        # payments list
        list_frame = tk.Frame(frame, bg="white")
        list_frame.pack(fill="both", expand=True, padx=10, pady=8)
        cols = ("id","student","month","year","amount","date_received","note")
        self.payments_tree = ttk.Treeview(list_frame, columns=cols, show="headings", selectmode="browse")
        headings = ["ID","Student","Month","Year","Amount","Date Received","Note"]
        widths = [40,240,80,60,80,120,200]
        for c,h,w in zip(cols, headings, widths):
            self.payments_tree.heading(c, text=h)
            self.payments_tree.column(c, width=w, anchor="w")
        self.payments_tree.pack(side="left", fill="both", expand=True)
        vs2 = ttk.Scrollbar(list_frame, orient="vertical", command=self.payments_tree.yview)
        vs2.pack(side="right", fill="y")
        self.payments_tree.configure(yscrollcommand=vs2.set)
        self.payments_tree.bind("<<TreeviewSelect>>", lambda e: self.load_payment_selection())

    def refresh_student_combobox(self):
        rows = query_db("SELECT id, name FROM students ORDER BY name", fetch=True)
        display = [f"{r[0]} - {r[1]}" for r in rows]
        self.student_combo['values'] = display

    def clear_payment_fields(self):
        self.payment_student_var.set("")
        self.payment_amount_var.set("")
        self.payment_note_var.set("")
        self.payment_month_var.set(calendar.month_name[date.today().month])
        self.payment_year_var.set(str(date.today().year))
        self.payment_date_var.set(date.today().strftime('%d/%m/%Y'))

    def receive_payment(self):
        stud = self.payment_student_var.get().strip()
        if not stud:
            messagebox.showwarning("Missing", "Select a student")
            return
        try:
            student_id = int(stud.split("-",1)[0].strip())
        except Exception:
            messagebox.showwarning("Invalid", "Select a valid student from drop-down (format: id - name)")
            return
        month = list(calendar.month_name).index(self.payment_month_var.get())
        year = int(self.payment_year_var.get())
        try:
            amount = float(self.payment_amount_var.get())
        except Exception:
            messagebox.showwarning("Invalid", "Enter a numeric amount")
            return
        try:
            dt = datetime.strptime(self.payment_date_var.get(), '%d/%m/%Y')
            date_received = dt.date().isoformat()
        except Exception:
            messagebox.showwarning("Date", "Payment date must be DD/MM/YYYY")
            return
        note = self.payment_note_var.get().strip()
        query_db("""
            INSERT INTO payments (student_id, month, year, amount, date_received, note) VALUES (?, ?, ?, ?, ?, ?)
        """, (student_id, month, year, amount, date_received, note))
        messagebox.showinfo("Received", f"Payment recorded for {self.payment_student_var.get()}")
        self.clear_payment_fields()
        self.refresh_payments_tree()

    def refresh_payments_tree(self):
        for r in self.payments_tree.get_children():
            self.payments_tree.delete(r)
        rows = query_db("""
            SELECT p.id, s.name, p.month, p.year, p.amount, p.date_received, p.note
            FROM payments p
            LEFT JOIN students s ON p.student_id = s.id
            ORDER BY p.year DESC, p.month DESC, p.date_received DESC
        """, fetch=True)
        for r in rows:
            month_name = calendar.month_name[r[2]] if r[2] and r[2] > 0 else ""
            dr = r[5]
            try:
                dr = datetime.strptime(dr, '%Y-%m-%d').strftime('%d/%m/%Y')
            except Exception:
                pass
            self.payments_tree.insert("", "end", values=(r[0], r[1] or "Unknown", month_name, r[3], f"{r[4]:.2f}", dr, r[6] or ""))

    def load_payment_selection(self):
        sel = self.payments_tree.selection()
        if not sel:
            return
        vals = self.payments_tree.item(sel[0])['values']
        pid, name, month_name, year, amount, date_received, note = vals
        for v in self.student_combo['values']:
            if v.strip().endswith(f"- {name}"):
                self.payment_student_var.set(v)
                break
        self.payment_month_var.set(month_name)
        self.payment_year_var.set(str(year))
        self.payment_amount_var.set(str(amount))
        self.payment_date_var.set(date_received)
        self.payment_note_var.set(note)

    def delete_payment(self):
        sel = self.payments_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a payment to delete")
            return
        pid = self.payments_tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", "Delete selected payment?"):
            query_db("DELETE FROM payments WHERE id=?", (pid,))
            self.refresh_payments_tree()

    def generate_receipt_pdf(self):
        if pdf_canvas is None:
            messagebox.showwarning("Missing library", "reportlab is required to generate PDF receipts. Please pip install reportlab")
            return
        sel = self.payments_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a payment to generate receipt")
            return
        vals = self.payments_tree.item(sel[0])['values']
        pid, name, month_name, year, amount, date_received, note = vals
        filename = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=[('PDF','*.pdf')], title='Save Receipt As')
        if not filename:
            return
        c = pdf_canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width/2, height-40, CENTER_NAME)
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, height-56, CENTER_ADDRESS + " | Contact: " + CENTER_CONTACT)
        c.line(30, height-70, width-30, height-70)
        x = 40
        y = height - 110
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y, "Payment Receipt")
        c.setFont("Helvetica", 10)
        y -= 20
        c.drawString(x, y, f"Receipt ID: {pid}")
        y -= 16
        c.drawString(x, y, f"Student: {name}")
        y -= 16
        c.drawString(x, y, f"Month/Year: {month_name} {year}")
        y -= 16
        c.drawString(x, y, f"Amount Received: ₹ {amount}")
        y -= 16
        c.drawString(x, y, f"Date Received: {date_received}")
        y -= 16
        c.drawString(x, y, f"Note: {note}")
        y -= 40
        c.drawString(x, y, "Thank you for your payment.")
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(width/2, 30, SOFTWARE_DEV)
        c.save()
        messagebox.showinfo("Saved", f"Receipt saved to {filename}")

    # ---------------- Batches Tab ----------------
    def build_batches_tab(self):
        frame = self.tab_batches
        top = tk.Frame(frame, bg="white", pady=8)
        top.pack(fill="x", padx=10)

        tk.Label(top, text="Day:", bg="white", width=8, anchor="w").grid(row=0, column=0, sticky="w")
        self.batch_day_var = tk.StringVar(value="Saturday")
        ttk.Combobox(top, values=["Saturday", "Sunday"], textvariable=self.batch_day_var, width=12).grid(row=0, column=1, sticky="w", padx=4)

        tk.Label(top, text="Batch No:", bg="white", width=10, anchor="w").grid(row=0, column=2, sticky="w")
        self.batch_no_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.batch_no_var, width=16).grid(row=0, column=3, sticky="w", padx=4)

        tk.Label(top, text="Batch Time:", bg="white", width=10, anchor="w").grid(row=0, column=4, sticky="w")
        self.batch_time_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.batch_time_var, width=16).grid(row=0, column=5, sticky="w", padx=4)

        tk.Label(top, text="Total Seats:", bg="white", width=10, anchor="w").grid(row=0, column=6, sticky="w")
        self.batch_total_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.batch_total_var, width=8).grid(row=0, column=7, sticky="w", padx=4)

        btn_frame = tk.Frame(top, bg="white")
        btn_frame.grid(row=1, column=0, columnspan=8, pady=(6,0))
        ttk.Button(btn_frame, text="Add Batch", style='Accent.TButton', command=self.add_batch).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Update Selected", command=self.update_selected_batch).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Delete Selected", style='Danger.TButton', command=self.delete_selected_batch).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Clear", command=self.clear_batch_form).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_batches_tree).pack(side="left", padx=4)

        content = tk.Frame(frame, bg="white")
        content.pack(fill="both", expand=True, padx=10, pady=8)

        left = tk.Frame(content, bg="white")
        left.pack(side="left", fill="both", expand=True)

        self.batches_tree = ttk.Treeview(left, columns=("id","day","batch_no","batch_time","total","taken","vacant"), show='headings', selectmode="browse")
        headers = ["ID","Day","Batch No","Batch Time","Total Seats","Seats Taken","Vacant"]
        widths = [50,90,120,120,100,100,100]
        for c,h,w in zip(("id","day","batch_no","batch_time","total","taken","vacant"), headers, widths):
            self.batches_tree.heading(c, text=h)
            self.batches_tree.column(c, width=w)
        self.batches_tree.pack(fill="both", expand=True, side="left")
        self.batches_tree.bind("<<TreeviewSelect>>", lambda e: self.load_batch_selection())
        vs = ttk.Scrollbar(left, orient="vertical", command=self.batches_tree.yview)
        vs.pack(side="right", fill="y")
        self.batches_tree.configure(yscrollcommand=vs.set)

        right = tk.Frame(content, bg="white")
        right.pack(side="left", fill="both", expand=True)

        # Top of right side: filter by day + show students list
        filter_row = tk.Frame(right, bg="white")
        filter_row.pack(fill="x", pady=(0,6))
        tk.Label(filter_row, text="Show Day:", bg="white").pack(side="left")
        self.batch_filter_day = tk.StringVar(value="All")
        ttk.Combobox(filter_row, values=["All", "Saturday", "Sunday"], textvariable=self.batch_filter_day, width=10).pack(side="left", padx=6)
        ttk.Button(filter_row, text="Apply Filter", command=self.refresh_batches_tree).pack(side="left", padx=6)

        # Students in selected batch
        tk.Label(right, text="Students in Selected Batch:", bg="white", anchor="w").pack(fill="x")
        self.batch_students_list = tk.Listbox(right)
        self.batch_students_list.pack(fill="both", expand=True, pady=(4,0))

        # Chart area (matplotlib) showing vacant seats per batch for current filter
        chart_frame = tk.Frame(right, bg="white")
        chart_frame.pack(fill="both", expand=True, pady=(6,0))
        if Figure is not None:
            self.fig_batches = Figure(figsize=(5,3), dpi=100)
            self.ax_batches = self.fig_batches.add_subplot(111)
            self.canvas_batches = FigureCanvasTkAgg(self.fig_batches, master=chart_frame)
            self.canvas_batches.get_tk_widget().pack(fill="both", expand=True)
        else:
            tk.Label(chart_frame, text="matplotlib not installed\nCharts disabled", bg="white").pack()

    def add_batch(self):
        day = self.batch_day_var.get().strip()
        batch_no = self.batch_no_var.get().strip()
        batch_time = self.batch_time_var.get().strip()
        try:
            total = int(self.batch_total_var.get())
        except Exception:
            messagebox.showwarning("Invalid", "Total seats must be an integer")
            return
        if not day or not batch_no:
            messagebox.showwarning("Missing", "Day and Batch No required")
            return
        # unique (day, batch_no)
        rows = query_db("SELECT id FROM batches WHERE day=? AND batch_no=?", (day, batch_no), fetch=True)
        if rows:
            messagebox.showwarning("Exists", "Batch already exists for that day&no")
            return
        query_db("INSERT INTO batches (day, batch_no, batch_time, total_seats, seats_taken) VALUES (?, ?, ?, ?, 0)", (day, batch_no, batch_time, total))
        messagebox.showinfo("Saved", "Batch added")
        self.clear_batch_form()
        self.refresh_batches_tree()

    def load_batch_selection(self):
        sel = self.batches_tree.selection()
        if not sel:
            return
        vals = self.batches_tree.item(sel[0])['values']
        bid, day, batch_no, batch_time, total, taken, vacant = vals
        self.batch_day_var.set(day)
        self.batch_no_var.set(batch_no)
        self.batch_time_var.set(batch_time)
        self.batch_total_var.set(str(total))
        # populate students list for this batch
        self.populate_students_for_batch(day, batch_no)

    def update_selected_batch(self):
        sel = self.batches_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a batch to update")
            return
        bid = self.batches_tree.item(sel[0])['values'][0]
        day = self.batch_day_var.get().strip()
        batch_no = self.batch_no_var.get().strip()
        batch_time = self.batch_time_var.get().strip()
        try:
            total = int(self.batch_total_var.get())
        except Exception:
            messagebox.showwarning("Invalid", "Total seats must be an integer")
            return
        if not day or not batch_no:
            messagebox.showwarning("Missing", "Day & Batch No required")
            return
        # conflict check
        rows = query_db("SELECT id FROM batches WHERE day=? AND batch_no=? AND id<>?", (day, batch_no, bid), fetch=True)
        if rows:
            messagebox.showwarning("Conflict", "Another batch with same day & no exists")
            return
        query_db("UPDATE batches SET day=?, batch_no=?, batch_time=?, total_seats=? WHERE id=?", (day, batch_no, batch_time, total, bid))
        messagebox.showinfo("Updated", "Batch updated")
        self.refresh_batches_tree()

    def delete_selected_batch(self):
        sel = self.batches_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a batch to delete")
            return
        bid = self.batches_tree.item(sel[0])['values'][0]
        day = self.batches_tree.item(sel[0])['values'][1]
        batch_no = self.batches_tree.item(sel[0])['values'][2]
        confirm = messagebox.askyesno("Confirm Delete", f"Delete batch {batch_no} ({day})?\nThis will remove assignments for students in this batch.")
        if not confirm:
            return
        # Clear students assigned to this batch (only the matching day column)
        if day == 'Saturday':
            query_db("UPDATE students SET sat_batch_no=NULL, sat_batch_time=NULL WHERE sat_batch_no=?", (batch_no,))
        else:
            query_db("UPDATE students SET sun_batch_no=NULL, sun_batch_time=NULL WHERE sun_batch_no=?", (batch_no,))
        query_db("DELETE FROM batches WHERE id=?", (bid,))
        messagebox.showinfo("Deleted", "Batch deleted and student assignments cleared")
        self.refresh_batches_tree()
        self.refresh_students_tree()
        self.refresh_student_combobox()

    def clear_batch_form(self):
        self.batch_day_var.set("Saturday")
        self.batch_no_var.set("")
        self.batch_time_var.set("")
        self.batch_total_var.set("")

    def refresh_batches_tree(self):
        for r in self.batches_tree.get_children():
            self.batches_tree.delete(r)
        # filter by day if set
        filter_day = self.batch_filter_day.get()
        if filter_day == "All":
            rows = query_db("SELECT id, day, batch_no, batch_time, total_seats, seats_taken FROM batches ORDER BY day, batch_no", fetch=True)
        else:
            rows = query_db("SELECT id, day, batch_no, batch_time, total_seats, seats_taken FROM batches WHERE day=? ORDER BY batch_no", (filter_day,), fetch=True)
        names = []
        vacants = []
        for r in rows:
            vacant = (r[4] or 0) - (r[5] or 0)
            vacant = vacant if vacant >= 0 else 0
            self.batches_tree.insert("", "end", values=(r[0], r[1], r[2], r[3] or "", r[4] or 0, r[5] or 0, vacant))
            names.append(f"{r[1]} {r[2]}")
            vacants.append(vacant)
        # draw chart
        if Figure is not None:
            self.ax_batches.clear()
            if names:
                colors = None
                try:
                    cmap = cm.get_cmap('tab20')
                    colors = [cmap(i / max(1, len(names)-1)) for i in range(len(names))]
                except Exception:
                    colors = None
                self.ax_batches.bar(names, vacants, color=colors)
                self.ax_batches.set_title('Vacant Seats (filtered)')
                self.ax_batches.set_ylabel('Vacant Seats')
                self.ax_batches.set_xticklabels(names, rotation=45, ha='right')
            self.fig_batches.tight_layout()
            self.canvas_batches.draw()
        # clear students list when refreshing
        self.batch_students_list.delete(0, tk.END)

    def ensure_batch_exists_and_increment(self, day, batch_no, batch_time=None):
        # ensure batch row exists; if not create with total_seats=0
        rows = query_db("SELECT id FROM batches WHERE day=? AND batch_no=?", (day, batch_no), fetch=True)
        if not rows:
            query_db("INSERT INTO batches (day, batch_no, batch_time, total_seats, seats_taken) VALUES (?, ?, ?, 0, 0)", (day, batch_no, batch_time or "",))
        # increment seats_taken if seats allow (we don't enforce here beyond not going negative)
        query_db("UPDATE batches SET seats_taken = seats_taken + 1 WHERE day=? AND batch_no=?", (day, batch_no))

    def decrement_batch_taken(self, day, batch_no):
        rows = query_db("SELECT id, seats_taken FROM batches WHERE day=? AND batch_no=?", (day, batch_no), fetch=True)
        if rows:
            try:
                query_db("UPDATE batches SET seats_taken = CASE WHEN seats_taken>0 THEN seats_taken-1 ELSE 0 END WHERE day=? AND batch_no=?", (day, batch_no))
            except Exception:
                pass

    def populate_students_for_batch(self, day, batch_no):
        self.batch_students_list.delete(0, tk.END)
        if day == 'Saturday':
            rows = query_db("SELECT id, name FROM students WHERE sat_batch_no=? ORDER BY name", (batch_no,), fetch=True)
        else:
            rows = query_db("SELECT id, name FROM students WHERE sun_batch_no=? ORDER BY name", (batch_no,), fetch=True)
        for r in rows:
            self.batch_students_list.insert(tk.END, f"{r[0]} - {r[1]}")

    # ---------------- Reports Tab ----------------
    def build_reports_tab(self):
        frame = self.tab_reports
        top = tk.Frame(frame, bg="white", pady=8)
        top.pack(fill="x", padx=10)

        tk.Label(top, text="Report Type:", bg="white").grid(row=0, column=0, sticky="w")
        self.report_type_var = tk.StringVar(value="Yearly")
        type_combo = ttk.Combobox(top, values=["Yearly","Monthly"], textvariable=self.report_type_var, width=12)
        type_combo.grid(row=0, column=1, sticky="w", padx=4)
        type_combo.bind("<<ComboboxSelected>>", lambda e: self.update_report_controls())

        tk.Label(top, text="Year:", bg="white").grid(row=0, column=2, sticky="w")
        years = [str(y) for y in range(date.today().year-5, date.today().year+6)]
        self.report_year_var = tk.StringVar(value=str(date.today().year))
        ttk.Combobox(top, values=years, textvariable=self.report_year_var, width=10).grid(row=0, column=3, sticky="w", padx=4)

        tk.Label(top, text="Month (for Monthly):", bg="white").grid(row=0, column=4, sticky="w")
        months = [calendar.month_name[i] for i in range(1,13)]
        self.report_month_var = tk.StringVar(value=months[date.today().month-1])
        self.report_month_cb = ttk.Combobox(top, values=months, textvariable=self.report_month_var, width=12)
        self.report_month_cb.grid(row=0, column=5, sticky="w", padx=4)

        ttk.Button(top, text="Generate Report", command=self.generate_report, style='Accent.TButton').grid(row=0, column=6, padx=8)
        ttk.Button(top, text="Export Report (.xlsx/.pdf)", command=self.export_report_options).grid(row=0, column=7, padx=8)

        content = tk.Frame(frame, bg="white")
        content.pack(fill="both", expand=True, padx=10, pady=8)

        left = tk.Frame(content, bg="white")
        left.pack(side="left", fill="both", expand=True)
        self.report_tree = ttk.Treeview(left, columns=("student","month","year","amount","date","note"), show="headings")
        for c,h in zip(("student","month","year","amount","date","note"),("Student","Month","Year","Amount","Date","Note")):
            self.report_tree.heading(c, text=h)
            self.report_tree.column(c, width=140, anchor="w")
        self.report_tree.pack(fill="both", expand=True, side="left")
        vs = ttk.Scrollbar(left, orient="vertical", command=self.report_tree.yview)
        vs.pack(side="right", fill="y")
        self.report_tree.configure(yscrollcommand=vs.set)

        right = tk.Frame(content, bg="white")
        right.pack(side="left", fill="both", expand=True)
        if Figure is not None:
            self.fig = Figure(figsize=(5,4), dpi=100)
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=right)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            tk.Label(right, text="matplotlib not installed\nCharts disabled", bg="white").pack()

        self.update_report_controls()

    def update_report_controls(self):
        t = self.report_type_var.get()
        if t == "Yearly":
            self.report_month_cb.config(state="disabled")
        else:
            self.report_month_cb.config(state="readonly")

    def generate_report(self):
        rtype = self.report_type_var.get()
        year = int(self.report_year_var.get())
        if rtype == "Yearly":
            rows = query_db("SELECT s.name, p.month, p.year, p.amount, p.date_received, p.note FROM payments p LEFT JOIN students s ON p.student_id=s.id WHERE p.year=?", (year,), fetch=True)
            if not rows:
                messagebox.showinfo("No Data", f"No payments found for year {year}")
                self.clear_report_display()
                return
            for r in self.report_tree.get_children():
                self.report_tree.delete(r)
            monthly = defaultdict(float)
            for name, month, yr, amount, date_received, note in rows:
                month_name = calendar.month_name[month] if month>0 else ""
                try:
                    dr = datetime.strptime(date_received, '%Y-%m-%d').strftime('%d/%m/%Y')
                except Exception:
                    dr = date_received
                self.report_tree.insert("", "end", values=(name or "Unknown", month_name, yr, f"{amount:.2f}", dr, note or ""))
                monthly[month] += amount
            if Figure is not None:
                labels = [calendar.month_name[m] for m in sorted([m for m in monthly if m>0])]
                vals = [monthly[m] for m in sorted([m for m in monthly if m>0])]
                self.ax.clear()
                if vals:
                    colors = None
                    try:
                        cmap = cm.get_cmap('tab20')
                        colors = [cmap(i / max(1, len(vals)-1)) for i in range(len(vals))]
                    except Exception:
                        colors = None
                    total = sum(vals)
                    def make_autopct(values):
                        def my_autopct(pct):
                            val = pct * total / 100.0
                            return f"\u20B9{val:.2f}"
                        return my_autopct
                    self.ax.pie(vals, labels=labels, autopct=make_autopct(vals), startangle=140, colors=colors)
                    self.ax.set_title(f"Fees Collected in {year} — Total: \u20B9{total:.2f}")
                self.fig.tight_layout()
                self.canvas.draw()
        else:
            month = list(calendar.month_name).index(self.report_month_var.get())
            rows = query_db("SELECT s.name, p.month, p.year, p.amount, p.date_received, p.note FROM payments p LEFT JOIN students s ON p.student_id=s.id WHERE p.year=? AND p.month=?", (year, month), fetch=True)
            if not rows:
                messagebox.showinfo("No Data", f"No payments found for {self.report_month_var.get()} {year}")
                self.clear_report_display()
                return
            for r in self.report_tree.get_children():
                self.report_tree.delete(r)
            total = 0.0
            breakdown = defaultdict(float)
            for name, m, yr, amount, date_received, note in rows:
                try:
                    dr = datetime.strptime(date_received, '%Y-%m-%d').strftime('%d/%m/%Y')
                except Exception:
                    dr = date_received
                self.report_tree.insert("", "end", values=(name or "Unknown", calendar.month_name[m], yr, f"{amount:.2f}", dr, note or ""))
                total += amount
                breakdown[name or "Unknown"] += amount
            if Figure is not None:
                labels = list(breakdown.keys())
                vals = list(breakdown.values())
                self.ax.clear()
                if vals:
                    colors = None
                    try:
                        cmap = cm.get_cmap('tab20')
                        colors = [cmap(i / max(1, len(vals)-1)) for i in range(len(vals))]
                    except Exception:
                        colors = None
                    def make_autopct(values):
                        def my_autopct(pct):
                            val = pct * sum(values) / 100.0
                            return f"\u20B9{val:.2f}"
                        return my_autopct
                    self.ax.pie(vals, labels=labels, autopct=make_autopct(vals), startangle=140, colors=colors)
                    self.ax.set_title(f"Payments in {self.report_month_var.get()} {year} — Total: \u20B9{total:.2f}")
                self.fig.tight_layout()
                self.canvas.draw()

    def clear_report_display(self):
        for r in self.report_tree.get_children():
            self.report_tree.delete(r)
        if Figure is not None:
            self.ax.clear()
            self.canvas.draw()

    # ---------------- Export ----------------
    def export_students(self):
        if pd is None:
            messagebox.showwarning("Missing library", "pandas & openpyxl required for XLSX export. Please pip install pandas openpyxl")
            return
        rows = query_db("SELECT id, name, sat_batch_no, sat_batch_time, sun_batch_no, sun_batch_time, contact, address, admission_date FROM students ORDER BY name", fetch=True)
        if not rows:
            messagebox.showinfo("No Data", "No student data to export")
            return
        data = []
        for r in rows:
            adm = r[8]
            try:
                adm_fmt = datetime.strptime(adm, '%Y-%m-%d').strftime('%d/%m/%Y')
            except Exception:
                adm_fmt = adm
            data.append({
                'ID': r[0], 'Name': r[1], 'Sat Batch': r[2], 'Sat Timing': r[3],
                'Sun Batch': r[4], 'Sun Timing': r[5], 'Contact': r[6], 'Address': r[7],
                'Admission Date': adm_fmt
            })
        df = pd.DataFrame(data)
        xlsx_path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel Workbook','*.xlsx')], title='Save Students as')
        if not xlsx_path:
            return
        try:
            df.to_excel(xlsx_path, index=False)
        except Exception as e:
            messagebox.showwarning("Export", f"Failed to save XLSX: {e}")
            return
        pdf_path = os.path.splitext(xlsx_path)[0] + '.pdf'
        if pdf_canvas is None:
            messagebox.showinfo("Saved", f"Students exported to {xlsx_path}. (Install reportlab to also export PDF)")
            return
        doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        elems = [Paragraph(CENTER_NAME, styles['Title']), Paragraph(CENTER_ADDRESS + ' | Contact: ' + CENTER_CONTACT, styles['Normal']), Spacer(1,6)]
        table_data = [list(df.columns)] + df.values.tolist()
        t = Table(table_data, repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0), colors.HexColor('#f2f2f2')), ('GRID',(0,0),(-1,-1),0.5, colors.black), ('FONT',(0,0),(-1,0),'Helvetica-Bold')]))
        elems.append(t)
        doc.build(elems)
        messagebox.showinfo("Saved", f"Students exported to {xlsx_path} and {pdf_path}")

    def export_report_options(self):
        if pd is None:
            messagebox.showwarning("Missing library", "pandas & openpyxl required for XLSX export. Please pip install pandas openpyxl")
            return
        rows = [self.report_tree.item(i)['values'] for i in self.report_tree.get_children()]
        if not rows:
            messagebox.showinfo("No Data", "Generate the report first")
            return
        cols = ['Student','Month','Year','Amount','Date','Note']
        df = pd.DataFrame(rows, columns=cols)
        xlsx_path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel Workbook','*.xlsx')], title='Save Report as')
        if not xlsx_path:
            return
        try:
            df.to_excel(xlsx_path, index=False)
        except Exception as e:
            messagebox.showwarning("Export", f"Failed to save XLSX: {e}")
            return
        pdf_path = os.path.splitext(xlsx_path)[0] + '.pdf'
        if pdf_canvas is None:
            messagebox.showinfo("Saved", f"Report exported to {xlsx_path}. (Install reportlab to also export PDF)")
            return
        doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        elems = [Paragraph(CENTER_NAME, styles['Title']), Paragraph(CENTER_ADDRESS+' | Contact: '+CENTER_CONTACT, styles['Normal']), Spacer(1,6)]
        table_data = [cols] + df.values.tolist()
        t = Table(table_data, repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0), colors.HexColor('#f2f2f2')), ('GRID',(0,0),(-1,-1),0.5, colors.black), ('FONT',(0,0),(-1,0),'Helvetica-Bold')]))
        elems.append(t)
        doc.build(elems)
        messagebox.showinfo("Saved", f"Report exported to {xlsx_path} and {pdf_path}")

    # ---------------- Search ----------------
    def perform_search(self):
        text = self.search_var.get().strip().lower()
        current_tab = self.nb.index(self.nb.select())
        def filter_tree(tree):
            for iid in tree.get_children():
                vals = [str(x).lower() for x in tree.item(iid)['values']]
                visible = (text in " ".join(vals)) if text else True
                if not visible:
                    try:
                        tree.detach(iid)
                    except Exception:
                        pass
                else:
                    try:
                        tree.reattach(iid, '', 'end')
                    except Exception:
                        pass
        if current_tab == 0:
            filter_tree(self.students_tree)
        elif current_tab == 1:
            filter_tree(self.payments_tree)
        elif current_tab == 2:
            filter_tree(self.batches_tree)
        elif current_tab == 3:
            filter_tree(self.report_tree)

    def clear_search(self):
        self.search_var.set("")
        self.perform_search()

# ---------------- Run ----------------
if __name__ == "__main__":
    init_db()
    # warn about optional libs
    missing = []
    if Image is None or ImageTk is None:
        missing.append("Pillow (image thumbnails)")
    if DateEntry is None:
        missing.append("tkcalendar (date picker)")
    if pd is None:
        missing.append("pandas & openpyxl (XLSX export)")
    if pdf_canvas is None:
        missing.append("reportlab (PDF export)")
    if Figure is None:
        missing.append("matplotlib (charts)")
    if missing:
        print("Optional libraries missing: " + ", ".join(missing))
        print("Install recommended libs with:\n    pip install matplotlib pillow tkcalendar pandas openpyxl reportlab\n(Some features will be disabled if not installed.)")
    app = FeesManagerApp()
    app.mainloop()
