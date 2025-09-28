#!/usr/bin/env python3
"""
School Management System (All-in-one, Python + SQLite + Tkinter, no external deps)

Save as: school_system.py
Run: python school_system.py

Features:
- Creates SQLite DB (school.db) with all requested tables.
- Tkinter UI to manage tables: Students, Guardians, Teachers, Classes, Subjects,
  Exams, Results, Attendance, Fees, Library, Timetable, Events, Hostel, Transport, Users.
- Photo upload for students (stored as BLOB).
- ID card & report generation opens HTML in default browser (printable).
- Search, Add, Edit, Delete, Refresh.
- Centered forms, confirmation dialogs.
"""

import os
import sqlite3
import base64
import tempfile
import webbrowser
from datetime import datetime
from tkinter import (
    Tk, Toplevel, StringVar, IntVar, Label, Entry, Button, LEFT, RIGHT, BOTH, X, Y, END, filedialog, messagebox, PhotoImage
)
from tkinter import ttk

DB_FILE = "school.db"

# -----------------------
# Database Initialization
# -----------------------
def init_db():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    # Enable foreign keys
    cur.execute("PRAGMA foreign_keys = ON;")

    # Core tables
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS Guardians (
        guardian_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        relationship TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        occupation TEXT
    );

    CREATE TABLE IF NOT EXISTS Classes (
        class_id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_name TEXT,
        section TEXT,
        teacher_id INTEGER,
        capacity INTEGER,
        FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS Teachers (
        teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        gender TEXT,
        date_of_birth TEXT,
        hire_date TEXT,
        subject_id INTEGER,
        phone TEXT,
        email TEXT,
        address TEXT,
        role TEXT,
        salary REAL
    );

    CREATE TABLE IF NOT EXISTS Subjects (
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_name TEXT,
        subject_code TEXT,
        teacher_id INTEGER,
        FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS Students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        gender TEXT,
        date_of_birth TEXT,
        admission_no TEXT,
        class_id INTEGER,
        address TEXT,
        phone TEXT,
        email TEXT,
        guardian_id INTEGER,
        enrollment_date TEXT,
        status TEXT,
        photo BLOB,
        FOREIGN KEY (class_id) REFERENCES Classes(class_id) ON DELETE SET NULL,
        FOREIGN KEY (guardian_id) REFERENCES Guardians(guardian_id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS Exams (
        exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_name TEXT,
        term TEXT,
        academic_year TEXT,
        start_date TEXT,
        end_date TEXT
    );

    CREATE TABLE IF NOT EXISTS Results (
        result_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject_id INTEGER,
        exam_id INTEGER,
        marks_obtained REAL,
        grade TEXT,
        remarks TEXT,
        FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES Subjects(subject_id) ON DELETE SET NULL,
        FOREIGN KEY (exam_id) REFERENCES Exams(exam_id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS Attendance (
        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        class_id INTEGER,
        date TEXT,
        status TEXT,
        FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
        FOREIGN KEY (class_id) REFERENCES Classes(class_id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS Fees (
        fee_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        amount REAL,
        fee_type TEXT,
        due_date TEXT,
        payment_status TEXT,
        payment_date TEXT,
        receipt_no TEXT,
        FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        isbn TEXT,
        category TEXT,
        quantity INTEGER,
        available_copies INTEGER
    );

    CREATE TABLE IF NOT EXISTS BookTransactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER,
        student_id INTEGER,
        issue_date TEXT,
        return_date TEXT,
        status TEXT,
        FOREIGN KEY (book_id) REFERENCES Books(book_id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Timetable (
        timetable_id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER,
        subject_id INTEGER,
        teacher_id INTEGER,
        day_of_week TEXT,
        start_time TEXT,
        end_time TEXT,
        FOREIGN KEY (class_id) REFERENCES Classes(class_id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES Subjects(subject_id) ON DELETE SET NULL,
        FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS Events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_name TEXT,
        description TEXT,
        date TEXT,
        venue TEXT
    );

    CREATE TABLE IF NOT EXISTS Hostels (
        hostel_id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostel_name TEXT,
        capacity INTEGER,
        warden_id INTEGER
    );

    CREATE TABLE IF NOT EXISTS HostelAllocations (
        allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostel_id INTEGER,
        student_id INTEGER,
        room_no TEXT,
        date_allocated TEXT,
        FOREIGN KEY (hostel_id) REFERENCES Hostels(hostel_id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Buses (
        bus_id INTEGER PRIMARY KEY AUTOINCREMENT,
        driver_name TEXT,
        route TEXT,
        capacity INTEGER
    );

    CREATE TABLE IF NOT EXISTS TransportAllocations (
        allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        bus_id INTEGER,
        pickup_point TEXT,
        drop_point TEXT,
        FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
        FOREIGN KEY (bus_id) REFERENCES Buses(bus_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        status TEXT
    );

    -- Additional helpful tables
    CREATE TABLE IF NOT EXISTS Inventory (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        quantity INTEGER,
        location TEXT
    );

    CREATE TABLE IF NOT EXISTS HealthRecords (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        notes TEXT,
        allergies TEXT,
        last_checkup TEXT,
        FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Discipline (
        discipline_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        incident_date TEXT,
        notes TEXT,
        action_taken TEXT,
        FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Assignments (
        assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        due_date TEXT,
        subject_id INTEGER
    );

    CREATE TABLE IF NOT EXISTS Submissions (
        submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER,
        student_id INTEGER,
        submitted_on TEXT,
        file_name TEXT
    );
    """)

    con.commit()
    con.close()

# -----------------------
# Utility functions
# -----------------------
def center_window(win, width=None, height=None):
    win.update_idletasks()
    w = width if width else win.winfo_reqwidth()
    h = height if height else win.winfo_reqheight()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

def query_db(sql, params=(), fetch=False):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute(sql, params)
    if fetch:
        rows = cur.fetchall()
        con.close()
        return rows
    else:
        con.commit()
        con.close()
        return None

def detect_mime_from_filename(filename):
    # basic inference
    ext = filename.lower().split('.')[-1]
    if ext in ('jpg', 'jpeg'):
        return 'image/jpeg'
    if ext in ('png',):
        return 'image/png'
    if ext in ('gif',):
        return 'image/gif'
    return 'application/octet-stream'

def blob_to_data_uri(blob, filename_hint='image'):
    if not blob:
        return ''
    mime = detect_mime_from_filename(filename_hint)
    b64 = base64.b64encode(blob).decode('ascii')
    return f"data:{mime};base64,{b64}"

# -----------------------
# GUI: Generic Table Manager
# -----------------------
class TableManager:
    def __init__(self, master, table_name, columns, pk, custom_columns=[]):
        """
        table_name: str (e.g., "Students")
        columns: list of (db_column, display_name)
        pk: primary key column
        custom_columns: additional non-db columns to include in Treeview
        """
        self.master = master
        self.table_name = table_name
        self.columns = columns
        self.pk = pk
        self.custom_columns = custom_columns

        self.window = Toplevel(master)
        self.window.title(f"Manage — {table_name}")
        self.window.minsize(900, 500)
        center_window(self.window, 1000, 600)

        # Top control bar
        topframe = ttk.Frame(self.window)
        topframe.pack(fill=X, padx=8, pady=6)

        # Search
        self.search_var = StringVar()
        ttk.Label(topframe, text=f"🔎 Search {table_name}:").pack(side=LEFT, padx=(4,2))
        self.search_entry = ttk.Entry(topframe, textvariable=self.search_var)
        self.search_entry.pack(side=LEFT, padx=(0,6))
        ttk.Button(topframe, text="Search", command=self.search).pack(side=LEFT, padx=4)
        ttk.Button(topframe, text="Refresh", command=self.refresh).pack(side=LEFT, padx=4)

        # CRUD Buttons
        ttk.Button(topframe, text="➕ Add", command=self.add).pack(side=RIGHT, padx=4)
        ttk.Button(topframe, text="✏️ Edit", command=self.edit).pack(side=RIGHT, padx=4)
        ttk.Button(topframe, text="🗑️ Delete", command=self.delete).pack(side=RIGHT, padx=4)
        ttk.Button(topframe, text="🔍 View", command=self.view).pack(side=RIGHT, padx=4)

        # Treeview for listing
        cols = [c[0] for c in columns] + custom_columns
        display_cols = [c[1] for c in columns] + custom_columns
        self.tree = ttk.Treeview(self.window, columns=cols, show='headings', selectmode='browse')
        for col, dcol in zip(cols, display_cols):
            self.tree.heading(col, text=dcol)
            self.tree.column(col, width=120, anchor='w')
        self.tree.pack(fill=BOTH, expand=True, padx=8, pady=8)

        # Bind double-click to view
        self.tree.bind("<Double-1>", lambda e: self.view())

        self.refresh()

    def refresh(self):
        # Default: select all
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Build simple SELECT * (better to customize per table)
        try:
            sql = f"SELECT {', '.join([c[0] for c in self.columns])} FROM {self.table_name}"
            rows = query_db(sql, fetch=True)
            for r in rows:
                # convert None to ''
                display = [ (i if i is not None else '') for i in r ]
                self.tree.insert('', END, values=display)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load {self.table_name}: {e}")

    def search(self):
        term = self.search_var.get().strip()
        if not term:
            self.refresh()
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            # naive search across text columns
            text_cols = [c[0] for c in self.columns if c[0] not in (self.pk,)]
            conds = " OR ".join([f"{col} LIKE ?" for col in text_cols])
            params = tuple([f"%{term}%"] * len(text_cols))
            sql = f"SELECT {', '.join([c[0] for c in self.columns])} FROM {self.table_name} WHERE {conds}"
            rows = query_db(sql, params, fetch=True)
            for r in rows:
                display = [ (i if i is not None else '') for i in r ]
                self.tree.insert('', END, values=display)
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {e}")

    def get_selected_pk(self):
        sel = self.tree.selection()
        if not sel:
            return None
        vals = self.tree.item(sel[0], 'values')
        # assume pk is first column in the columns list
        pk_index = 0
        try:
            return vals[pk_index]
        except:
            return None

    # The following methods are meant to be overridden for custom behavior
    def add(self):
        messagebox.showinfo("Add", f"Add new record to {self.table_name} - Not implemented here.")

    def edit(self):
        messagebox.showinfo("Edit", f"Edit selected record in {self.table_name} - Not implemented here.")

    def delete(self):
        pk = self.get_selected_pk()
        if not pk:
            messagebox.showwarning("Delete", "Select a row to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete selected record ({pk}) from {self.table_name}?"):
            return
        try:
            sql = f"DELETE FROM {self.table_name} WHERE {self.columns[0][0]} = ?"
            query_db(sql, (pk,))
            messagebox.showinfo("Deleted", "Record deleted.")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Delete failed: {e}")

    def view(self):
        pk = self.get_selected_pk()
        if not pk:
            messagebox.showwarning("View", "Select a row to view.")
            return
        # Default: show details in a dialog
        sql = f"SELECT * FROM {self.table_name} WHERE {self.columns[0][0]} = ?"
        rows = query_db(sql, (pk,), fetch=True)
        if not rows:
            messagebox.showinfo("View", "No data found.")
            return
        row = rows[0]
        keys = [d[0] for d in self.get_table_info()]
        detail = "\n".join([f"{k}: {v}" for k, v in zip(keys, row)])
        messagebox.showinfo(f"{self.table_name} — Details", detail)

    def get_table_info(self):
        # Return sqlite PRAGMA table_info for the table
        return query_db(f"PRAGMA table_info({self.table_name})", fetch=True)


# -----------------------
# Students Manager (custom)
# -----------------------
class StudentsManager(TableManager):
    def __init__(self, master):
        columns = [
            ("student_id", "ID"),
            ("first_name", "First Name"),
            ("last_name", "Last Name"),
            ("gender", "Gender"),
            ("date_of_birth", "DOB"),
            ("admission_no", "Admission No"),
            ("class_id", "Class ID"),
            ("phone", "Phone"),
            ("email", "Email"),
            ("guardian_id", "Guardian ID"),
            ("enrollment_date", "Enrollment"),
            ("status", "Status"),
        ]
        super().__init__(master, "Students", columns, pk="student_id")

    def add(self):
        StudentForm(self.window, mode="add", refresh_callback=self.refresh)

    def edit(self):
        pk = self.get_selected_pk()
        if not pk:
            messagebox.showwarning("Edit", "Select a student to edit.")
            return
        StudentForm(self.window, mode="edit", student_id=pk, refresh_callback=self.refresh)

    def view(self):
        pk = self.get_selected_pk()
        if not pk:
            messagebox.showwarning("View", "Select a student.")
            return
        # show detailed view with photo and options (ID card, report)
        rows = query_db("SELECT * FROM Students WHERE student_id = ?", (pk,), fetch=True)
        if not rows:
            messagebox.showinfo("View", "Student not found.")
            return
        row = rows[0]
        keys = [d[0] for d in query_db("PRAGMA table_info(Students)", fetch=True)]
        # create a centered popup with details
        top = Toplevel(self.window)
        top.title(f"Student — {row[1]} {row[2]}")
        top.minsize(500, 400)
        center_window(top, 700, 500)
        frm = ttk.Frame(top, padding=10)
        frm.pack(fill=BOTH, expand=True)
        # left: image if exists
        photo_blob = row[keys.index('photo') - 0] if 'photo' in keys else None
        if row[keys.index('photo')]:
            blob = row[keys.index('photo')]
            mime = detect_mime_from_filename(row[keys.index('admission_no')] or 'photo.png')
            data_uri = blob_to_data_uri(blob, filename_hint='student_image')
            # embed image in HTML? For display in Tk we can write to temp file and load PhotoImage if Tk supports it.
            try:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".img")
                tmp.write(blob)
                tmp.flush()
                tmp.close()
                # attempt to create PhotoImage
                img = PhotoImage(file=tmp.name)
                lbl_img = Label(frm, image=img)
                lbl_img.image = img
                lbl_img.pack(side=LEFT, padx=8, pady=8)
            except Exception:
                # can't render image with tk; ignore visual
                pass

        # right: key-value pairs and buttons
        info_frame = ttk.Frame(frm)
        info_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10)
        for i, col in enumerate(keys):
            if col == 'photo':
                continue
            Label(info_frame, text=f"{col}: ", font=("Segoe UI", 9, "bold")).grid(row=i, column=0, sticky='nw', padx=3, pady=2)
            Label(info_frame, text=str(row[i] or "")).grid(row=i, column=1, sticky='nw', padx=3, pady=2)

        btns = ttk.Frame(top, padding=8)
        btns.pack(fill=X)
        ttk.Button(btns, text="🆔 Generate ID Card", command=lambda: generate_student_id_html(row)).pack(side=LEFT, padx=6)
        ttk.Button(btns, text="📄 Generate Report", command=lambda: generate_student_report_html(row)).pack(side=LEFT, padx=6)
        ttk.Button(btns, text="Close", command=top.destroy).pack(side=RIGHT, padx=6)


# -----------------------
# Student Form (Add/Edit)
# -----------------------
class StudentForm:
    def __init__(self, master, mode="add", student_id=None, refresh_callback=None):
        self.master = master
        self.mode = mode
        self.student_id = student_id
        self.refresh_callback = refresh_callback

        self.top = Toplevel(master)
        self.top.title("Add Student" if mode == "add" else "Edit Student")
        center_window(self.top, 700, 520)

        frm = ttk.Frame(self.top, padding=12)
        frm.pack(fill=BOTH, expand=True)

        # Input fields
        self.vars = {}
        labels = [
            ("first_name", "First Name"),
            ("last_name", "Last Name"),
            ("gender", "Gender"),
            ("date_of_birth", "Date of Birth (YYYY-MM-DD)"),
            ("admission_no", "Admission No"),
            ("class_id", "Class ID"),
            ("address", "Address"),
            ("phone", "Phone"),
            ("email", "Email"),
            ("guardian_id", "Guardian ID"),
            ("enrollment_date", "Enrollment Date (YYYY-MM-DD)"),
            ("status", "Status (active/graduated/withdrawn)")
        ]
        r = 0
        for key, lbl in labels:
            ttk.Label(frm, text=lbl).grid(row=r, column=0, sticky='w', pady=6, padx=6)
            v = StringVar()
            self.vars[key] = v
            ttk.Entry(frm, textvariable=v, width=40).grid(row=r, column=1, sticky='w', pady=6)
            r += 1

        # Photo upload
        ttk.Label(frm, text="Photo (PNG/JPG)").grid(row=r, column=0, sticky='w', pady=6, padx=6)
        self.photo_label = ttk.Label(frm, text="No file")
        self.photo_label.grid(row=r, column=1, sticky='w')
        ttk.Button(frm, text="Upload Photo", command=self.upload_photo).grid(row=r, column=2, padx=6)
        self.photo_blob = None
        r += 1

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=r, column=0, columnspan=3, pady=12)
        ttk.Button(btn_frame, text="Save", command=self.save).pack(side=LEFT, padx=6)
        ttk.Button(btn_frame, text="Cancel", command=self.top.destroy).pack(side=LEFT, padx=6)

        # If edit mode, load existing data
        if self.mode == "edit" and self.student_id:
            self.load_student()

    def upload_photo(self):
        f = filedialog.askopenfilename(title="Select photo", filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif"), ("All files", "*.*")])
        if not f:
            return
        with open(f, "rb") as fh:
            self.photo_blob = fh.read()
        self.photo_label.config(text=os.path.basename(f))

    def load_student(self):
        rows = query_db("SELECT * FROM Students WHERE student_id = ?", (self.student_id,), fetch=True)
        if not rows:
            messagebox.showerror("Error", "Student not found.")
            self.top.destroy()
            return
        row = rows[0]
        # map columns
        cols = [c[0] for c in query_db("PRAGMA table_info(Students)", fetch=True)]
        # set vars
        for i, col in enumerate(cols):
            if col == 'photo':
                self.photo_blob = row[i]
                continue
            if col in self.vars:
                self.vars[col].set("" if row[i] is None else str(row[i]))

    def save(self):
        # simple validation
        first = self.vars["first_name"].get().strip()
        last = self.vars["last_name"].get().strip()
        if not first or not last:
            messagebox.showwarning("Validation", "First and last names are required.")
            return
        # collect values
        vals = {k: v.get().strip() or None for k, v in self.vars.items()}
        # set defaults
        if not vals.get("enrollment_date"):
            vals["enrollment_date"] = datetime.now().strftime("%Y-%m-%d")
        if not vals.get("status"):
            vals["status"] = "active"
        try:
            if self.mode == "add":
                sql = """INSERT INTO Students
                (first_name, last_name, gender, date_of_birth, admission_no, class_id, address, phone, email, guardian_id, enrollment_date, status, photo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                params = (
                    vals.get("first_name"), vals.get("last_name"), vals.get("gender"),
                    vals.get("date_of_birth"), vals.get("admission_no"),
                    int(vals["class_id"]) if vals.get("class_id") else None,
                    vals.get("address"), vals.get("phone"), vals.get("email"),
                    int(vals["guardian_id"]) if vals.get("guardian_id") else None,
                    vals.get("enrollment_date"), vals.get("status"),
                    self.photo_blob
                )
                query_db(sql, params)
                messagebox.showinfo("Saved", "Student added.")
            else:
                sql = """UPDATE Students SET first_name=?, last_name=?, gender=?, date_of_birth=?, admission_no=?, class_id=?, address=?, phone=?, email=?, guardian_id=?, enrollment_date=?, status=?, photo=? WHERE student_id=?"""
                params = (
                    vals.get("first_name"), vals.get("last_name"), vals.get("gender"),
                    vals.get("date_of_birth"), vals.get("admission_no"),
                    int(vals["class_id"]) if vals.get("class_id") else None,
                    vals.get("address"), vals.get("phone"), vals.get("email"),
                    int(vals["guardian_id"]) if vals.get("guardian_id") else None,
                    vals.get("enrollment_date"), vals.get("status"),
                    self.photo_blob, int(self.student_id)
                )
                query_db(sql, params)
                messagebox.showinfo("Saved", "Student updated.")
            if self.refresh_callback:
                self.refresh_callback()
            self.top.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")

# -----------------------
# ID Card & Report generation
# -----------------------
def generate_student_id_html(student_row):
    """
    student_row: the row tuple from Students SELECT *
    We'll generate a simple HTML card with embedded photo as base64.
    """
    # get column ordering
    cols = [c[0] for c in query_db("PRAGMA table_info(Students)", fetch=True)]
    mapping = dict(zip(cols, student_row))
    # decide image mime
    blob = mapping.get('photo')
    image_html = ""
    if blob:
        data_uri = blob_to_data_uri(blob, filename_hint=mapping.get('admission_no') or 'photo.png')
        image_html = f'<img src="{data_uri}" alt="photo" style="width:120px;height:140px;border-radius:6px;object-fit:cover;" />'
    else:
        image_html = '<div style="width:120px;height:140px;background:#ddd;display:flex;align-items:center;justify-content:center;">No Photo</div>'

    html = f"""
    <html>
    <head><meta charset="utf-8"><title>ID Card - {mapping.get('first_name')} {mapping.get('last_name')}</title></head>
    <body style="font-family: Arial, Helvetica, sans-serif; background:#f8f9fb; padding:40px;">
      <div style="width:420px;margin:0 auto;background:white;border-radius:8px;padding:18px;box-shadow:0 6px 18px rgba(0,0,0,0.08);">
        <div style="display:flex;align-items:center;">
          <div style="flex:0 0 140px;">{image_html}</div>
          <div style="flex:1;padding-left:18px;">
            <h2 style="margin:0;padding:0;">{mapping.get('first_name') or ''} {mapping.get('last_name') or ''}</h2>
            <p style="margin:6px 0 0 0;"><strong>Admission No:</strong> {mapping.get('admission_no') or ''}</p>
            <p style="margin:6px 0 0 0;"><strong>Class ID:</strong> {mapping.get('class_id') or ''}</p>
            <p style="margin:6px 0 0 0;"><strong>Guardian ID:</strong> {mapping.get('guardian_id') or ''}</p>
            <p style="margin:12px 0 0 0;color:#666;">Issued: {datetime.now().strftime('%Y-%m-%d')}</p>
          </div>
        </div>
        <hr style="margin:14px 0;">
        <div style="display:flex;justify-content:space-between;">
          <div><small>School: Your School Name</small></div>
          <div><small>Signature: __________________</small></div>
        </div>
      </div>
      <p style="text-align:center;margin-top:16px;"><button onclick="window.print()">Print ID Card</button></p>
    </body>
    </html>
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8')
    tmp.write(html)
    tmp.close()
    webbrowser.open('file://' + tmp.name)

def generate_student_report_html(student_row):
    cols = [c[0] for c in query_db("PRAGMA table_info(Students)", fetch=True)]
    mapping = dict(zip(cols, student_row))
    student_id = mapping.get('student_id')
    # gather results
    result_rows = query_db("SELECT Results.result_id, Subjects.subject_name, Results.marks_obtained, Results.grade, Results.remarks, Exams.exam_name FROM Results LEFT JOIN Subjects ON Results.subject_id=Subjects.subject_id LEFT JOIN Exams ON Results.exam_id=Exams.exam_id WHERE Results.student_id = ?", (student_id,), fetch=True)
    # build HTML
    blob = mapping.get('photo')
    if blob:
        data_uri = blob_to_data_uri(blob, filename_hint=mapping.get('admission_no') or 'photo.png')
        img_html = f'<img src="{data_uri}" style="width:100px;height:120px;object-fit:cover;border-radius:6px;">'
    else:
        img_html = '<div style="width:100px;height:120px;background:#eee;display:inline-block;"></div>'

    rows_html = ""
    if result_rows:
        rows_html += "<table border='1' cellpadding='6' cellspacing='0' style='border-collapse:collapse;width:100%'><tr><th>Subject</th><th>Exam</th><th>Marks</th><th>Grade</th><th>Remarks</th></tr>"
        for rr in result_rows:
            _, subj, marks, grade, remarks, examname = rr
            rows_html += f"<tr><td>{subj or ''}</td><td>{examname or ''}</td><td>{marks or ''}</td><td>{grade or ''}</td><td>{remarks or ''}</td></tr>"
        rows_html += "</table>"
    else:
        rows_html = "<p>No results yet.</p>"

    html = f"""
    <html><head><meta charset="utf-8"><title>Report - {mapping.get('first_name')} {mapping.get('last_name')}</title></head>
    <body style="font-family:Arial,Helvetica,sans-serif;padding:20px;background:#f6f7fb;">
    <div style="max-width:900px;margin:0 auto;background:white;padding:18px;border-radius:8px;box-shadow:0 6px 18px rgba(0,0,0,0.06);">
      <div style="display:flex;gap:18px;">
        <div>{img_html}</div>
        <div style="flex:1;">
          <h2 style="margin:0">{mapping.get('first_name') or ''} {mapping.get('last_name') or ''}</h2>
          <p style="margin:4px 0;"><strong>Admission No:</strong> {mapping.get('admission_no') or ''}</p>
          <p style="margin:4px 0;"><strong>Class ID:</strong> {mapping.get('class_id') or ''}</p>
          <p style="margin:4px 0;"><strong>Enrollment:</strong> {mapping.get('enrollment_date') or ''}</p>
        </div>
      </div>
      <hr style="margin:12px 0;">
      <h3>Results</h3>
      {rows_html}
      <hr>
      <p><small>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
      <p style="text-align:center"><button onclick="window.print()">Print / Save as PDF</button></p>
    </div>
    </body></html>
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8')
    tmp.write(html)
    tmp.close()
    webbrowser.open('file://' + tmp.name)

# -----------------------
# Application Main Window
# -----------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("Ilimin Fasahar Dijital - School Management System")
        root.geometry("1200x700")
        # center
        center_window(root, 1200, 700)

        # left pane navigation
        nav = ttk.Frame(root, width=260, padding=8)
        nav.pack(side=LEFT, fill=Y)

        ttk.Label(nav, text="📚 School System", font=("Segoe UI", 14, "bold")).pack(pady=(6,12))
        # nice list of buttons
        buttons = [
            ("Students", self.open_students),
            ("Guardians", lambda: self.open_table("Guardians", [("guardian_id","ID"),("first_name","First"),("last_name","Last"),("relationship","Rel"),("phone","Phone")], "guardian_id")),
            ("Teachers", lambda: self.open_table("Teachers", [("teacher_id","ID"),("first_name","First"),("last_name","Last"),("subject_id","Subject ID"),("phone","Phone")], "teacher_id")),
            ("Classes", lambda: self.open_table("Classes", [("class_id","ID"),("class_name","Name"),("section","Section"),("teacher_id","Teacher ID")], "class_id")),
            ("Subjects", lambda: self.open_table("Subjects", [("subject_id","ID"),("subject_name","Name"),("subject_code","Code"),("teacher_id","Teacher ID")], "subject_id")),
            ("Exams", lambda: self.open_table("Exams", [("exam_id","ID"),("exam_name","Exam"),("term","Term"),("academic_year","Year")], "exam_id")),
            ("Results", lambda: self.open_table("Results", [("result_id","ID"),("student_id","Student ID"),("subject_id","Subject ID"),("exam_id","Exam ID"),("marks_obtained","Marks")], "result_id")),
            ("Attendance", lambda: self.open_table("Attendance", [("attendance_id","ID"),("student_id","Student"),("class_id","Class"),("date","Date"),("status","Status")], "attendance_id")),
            ("Fees", lambda: self.open_table("Fees", [("fee_id","ID"),("student_id","Student"),("amount","Amount"),("payment_status","Status")], "fee_id")),
            ("Library", lambda: self.open_table("Books", [("book_id","ID"),("title","Title"),("author","Author"),("available_copies","Available")], "book_id")),
            ("Timetable", lambda: self.open_table("Timetable", [("timetable_id","ID"),("class_id","Class"),("subject_id","Subject"),("teacher_id","Teacher")], "timetable_id")),
            ("Events", lambda: self.open_table("Events", [("event_id","ID"),("event_name","Event"),("date","Date"),("venue","Venue")], "event_id")),
            ("Hostel", lambda: self.open_table("Hostels", [("hostel_id","ID"),("hostel_name","Name"),("capacity","Capacity")], "hostel_id")),
            ("Hostel Allocations", lambda: self.open_table("HostelAllocations", [("allocation_id","ID"),("hostel_id","Hostel"),("student_id","Student"),("room_no","Room")], "allocation_id")),
            ("Transport", lambda: self.open_table("Buses", [("bus_id","ID"),("driver_name","Driver"),("route","Route"),("capacity","Capacity")], "bus_id")),
            ("Transport Alloc", lambda: self.open_table("TransportAllocations", [("allocation_id","ID"),("student_id","Student"),("bus_id","Bus"),("pickup_point","Pick")], "allocation_id")),
            ("Users", lambda: self.open_table("Users", [("user_id","ID"),("username","Username"),("role","Role"),("status","Status")], "user_id")),
            ("Inventory", lambda: self.open_table("Inventory", [("item_id","ID"),("name","Name"),("category","Cat"),("quantity","Qty")], "item_id")),
            ("Health Records", lambda: self.open_table("HealthRecords", [("record_id","ID"),("student_id","Student"),("allergies","Allergies")], "record_id")),
            ("Discipline", lambda: self.open_table("Discipline", [("discipline_id","ID"),("student_id","Student"),("incident_date","Date")], "discipline_id")),
            ("Assignments", lambda: self.open_table("Assignments", [("assignment_id","ID"),("title","Title"),("due_date","Due")], "assignment_id")),
            ("Submissions", lambda: self.open_table("Submissions", [("submission_id","ID"),("assignment_id","Assignment"),("student_id","Student"),("submitted_on","Date")], "submission_id")),
        ]
        for (label, cmd) in buttons:
            ttk.Button(nav, text=label, command=cmd).pack(fill=X, pady=4)

        # main area - welcome / instructions
        main = ttk.Frame(root, padding=16)
        main.pack(fill=BOTH, expand=True)
        ttk.Label(main, text="Welcome to the School Management System", font=("Segoe UI", 18, "bold")).pack(pady=(10,6))
        ttk.Label(main, text="Use the left menu to manage students, teachers, classes and other modules.\nSelect a module, then add/edit/delete records. For students: view to generate ID card or report.", justify=LEFT).pack(pady=(6,12))

        # quick shortcuts
        quick = ttk.Frame(main)
        quick.pack(pady=6, fill=X)
        ttk.Button(quick, text="Open Students", command=self.open_students).pack(side=LEFT, padx=6)
        ttk.Button(quick, text="Open Teachers", command=lambda: self.open_table("Teachers", [("teacher_id","ID"),("first_name","First"),("last_name","Last"),("subject_id","Subject ID")], "teacher_id")).pack(side=LEFT, padx=6)
        ttk.Button(quick, text="Open Guardians", command=lambda: self.open_table("Guardians", [("guardian_id","ID"),("first_name","First"),("last_name","Last")], "guardian_id")).pack(side=LEFT, padx=6)

    def open_students(self):
        StudentsManager(self.root)

    def open_table(self, table_name, columns, pk):
        TableManager(self.root, table_name, columns, pk)

# -----------------------
# Run the application
# -----------------------
def main():
    init_db()
    root = Tk()
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except:
        pass
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
