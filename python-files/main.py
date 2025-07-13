import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import sqlite3
import pandas as pd
import sys

# Matplotlib imports for charting
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt
except ImportError:
    messagebox.showerror("Missing Library", "matplotlib is required for charting. Please install it with:\npip install matplotlib")
    sys.exit(1)

# GPA Grade Points mapping
grade_points = {
    "A+": 4.0, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "D-": 0.7, "F": 0.0
}

# Icons using Unicode
ICON_ADD = "\u2795"      # Heavy plus sign
ICON_DELETE = "\U0001F5D1"  # Wastebasket
ICON_EDIT = "\u270D"     # Writing hand
ICON_SAVE = "\u2714"     # Heavy check mark
ICON_EXPORT = "\U0001F4E4" # Outbox tray
ICON_IMPORT = "\U0001F4E5" # Inbox tray
ICON_CALC = "\u03C3"     # Sigma

def load_inter_font(root):
    available = font.families()
    if "Inter" in available:
        return "Inter"
    elif "Segoe UI" in available:
        return "Segoe UI"
    elif "Arial" in available:
        return "Arial"
    else:
        return "TkDefaultFont"

class GPAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GPA Calculator & Student Management")
        self.root.geometry("1140x860")
        self.root.minsize(950, 800)

        self.app_font = load_inter_font(root)

        self.root.configure(bg="#f4f6fb")
        self.database = 'data.db'
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()
        self.init_db()

        self.current_student = None  # (name, index_number)
        self.current_year = 'Year 1'
        self.current_semester = 'Semester 1'

        self.entries = []

        self.style = ttk.Style(self.root)
        self.configure_style()
        self.build_ui()

    def init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                index_number TEXT UNIQUE NOT NULL,
                UNIQUE(name, index_number)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                year TEXT, semester TEXT,
                course_name TEXT, grade TEXT, credits REAL,
                FOREIGN KEY(student_id) REFERENCES students(id)
            )
        """)
        self.conn.commit()

    def configure_style(self):
        self.style.theme_use('clam')
        primary = "#1e40af"
        primary_hover = "#1e3a8a"
        secondary = "#f59e0b"
        secondary_hover = "#d97706"
        bg = "#f4f6fb"
        card_bg = "#ffffff"
        header_bg = "#e0e7ff"
        text = "#1e293b"
        accent = "#2563eb"
        error = "#dc2626"
        border = "#d1d5db"
        highlight = "#93c5fd"

        base_font = (self.app_font, 11)
        header_font = (self.app_font, 14, "bold")
        title_font = (self.app_font, 18, "bold")

        self.style.configure("TFrame", background=bg)
        self.style.configure("Card.TFrame", background=card_bg, relief="raised", borderwidth=1)
        self.style.configure("Header.TFrame", background=header_bg)

        self.style.configure("TLabel", background=bg, foreground=text, font=base_font)
        self.style.configure("Header.TLabel", background=header_bg, foreground=primary, font=header_font)
        self.style.configure("Title.TLabel", background=bg, foreground=primary, font=title_font)

        self.style.configure("TButton",
                             font=base_font,
                             padding=8,
                             background=primary,
                             foreground="white",
                             borderwidth=0,
                             relief="flat")
        self.style.map("TButton",
                       foreground=[('disabled', '#9ca3af')],
                       background=[('pressed', primary_hover), ('active', primary_hover)])

        self.style.configure("Primary.TButton",
                             font=base_font,
                             padding=10,
                             background=primary,
                             foreground="white",
                             relief="flat",
                             borderwidth=0)
        self.style.map("Primary.TButton",
                       background=[('pressed', primary_hover), ('active', primary_hover)])

        self.style.configure("Secondary.TButton",
                             font=base_font,
                             padding=10,
                             background=secondary,
                             foreground="white",
                             relief="flat",
                             borderwidth=0)
        self.style.map("Secondary.TButton",
                       background=[('pressed', secondary_hover), ('active', secondary_hover)])

        self.style.configure("Danger.TButton",
                             font=base_font,
                             padding=10,
                             background=error,
                             foreground="white",
                             relief="flat",
                             borderwidth=0)
        self.style.map("Danger.TButton",
                       background=[('pressed', "#b91c1c"), ('active', "#b91c1c")])

        self.style.configure("TCombobox",
                             padding=6,
                             relief="flat",
                             selectbackground=accent,
                             fieldbackground=card_bg,
                             background=bg,
                             foreground=text)
        self.style.map("TCombobox",
                       fieldbackground=[('readonly', card_bg)],
                       selectbackground=[('readonly', accent)])

        self.style.configure("Vertical.TScrollbar",
                             gripcount=0,
                             background=primary,
                             darkcolor=primary,
                             lightcolor=primary,
                             troughcolor=bg,
                             bordercolor=bg,
                             arrowcolor=primary,
                             relief="flat")

        self.style.configure("Treeview",
                             background=card_bg,
                             foreground=text,
                             rowheight=28,
                             fieldbackground=card_bg,
                             bordercolor=border,
                             lightcolor=border,
                             darkcolor=border,
                             font=base_font)
        self.style.map("Treeview",
                       background=[('selected', highlight)],
                       foreground=[('selected', '#000000')])
        self.style.configure("Treeview.Heading",
                             font=header_font,
                             background=header_bg,
                             foreground=primary,
                             relief="flat")
        self.style.map("Treeview.Heading",
                       background=[('active', primary_hover)])

        self.style.configure("Dialog.TFrame", background=bg)

    def build_ui(self):
        header_bar = ttk.Frame(self.root, style="Header.TFrame", padding=10)
        header_bar.pack(fill='x')

        header_label = ttk.Label(header_bar, text="GPA Calculator & Student Management", style="Title.TLabel")
        header_label.pack(side="left", padx=20)

        container = ttk.Frame(self.root, padding=20, style="TFrame")
        container.pack(fill="both", expand=True)

        # Student management frame
        student_frame = ttk.Frame(container, style="Card.TFrame", padding=16)
        student_frame.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        student_frame.columnconfigure(1, weight=1)
        student_frame.columnconfigure(3, weight=1)
        student_frame.columnconfigure(4, weight=1)

        lbl_select = ttk.Label(student_frame, text="Select Student:", style="Header.TLabel")
        lbl_select.grid(row=0, column=0, sticky="w", pady=4)

        self.student_combo = ttk.Combobox(student_frame, state="normal", width=40, font=(self.app_font, 11))
        self.student_combo.grid(row=0, column=1, sticky="ew", padx=(4, 12), pady=6)
        self.student_combo.bind('<KeyRelease>', self.filter_students)

        btn_select = ttk.Button(student_frame, text="Select", command=self.select_student, style="Primary.TButton")
        btn_select.grid(row=0, column=2, padx=4, pady=6)

        # Add/edit student fields
        ttk.Label(student_frame, text="Student Name:", style="Header.TLabel").grid(row=1, column=0, sticky="w", pady=4)
        self.name_entry = ttk.Entry(student_frame, font=(self.app_font, 11))
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=(4, 12), pady=6)

        ttk.Label(student_frame, text="Index Number:", style="Header.TLabel").grid(row=2, column=0, sticky="w", pady=4)
        self.index_entry = ttk.Entry(student_frame, font=(self.app_font, 11))
        self.index_entry.grid(row=2, column=1, sticky="ew", padx=(4, 12), pady=6)

        btn_add = ttk.Button(student_frame, text=f"{ICON_ADD} Add Student", command=self.add_student, style="Primary.TButton")
        btn_add.grid(row=1, column=2, padx=4, pady=6)

        btn_update = ttk.Button(student_frame, text=f"{ICON_EDIT} Update Student", command=self.update_student, style="Primary.TButton")
        btn_update.grid(row=2, column=2, padx=4, pady=6)

        btn_delete = ttk.Button(student_frame, text=f"{ICON_DELETE} Delete Student", command=self.delete_student, style="Danger.TButton")
        btn_delete.grid(row=1, column=3, padx=4, pady=6)

        # Year & semester selection frame
        sem_frame = ttk.Frame(container, style="Card.TFrame", padding=16)
        sem_frame.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        sem_frame.columnconfigure(1, weight=1)
        sem_frame.columnconfigure(3, weight=1)

        lbl_year = ttk.Label(sem_frame, text="Year:", style="Header.TLabel")
        lbl_year.grid(row=0, column=0, sticky="w", pady=4, padx=(0, 8))
        self.year_var = tk.StringVar(value=self.current_year)
        year_combo = ttk.Combobox(sem_frame, textvariable=self.year_var,
                                  values=[f'Year {i}' for i in range(1, 6)],
                                  width=12, state="readonly", style="TCombobox")
        year_combo.grid(row=0, column=1, sticky="w", pady=4, padx=(0, 16))

        lbl_sem = ttk.Label(sem_frame, text="Semester:", style="Header.TLabel")
        lbl_sem.grid(row=0, column=2, sticky="w", pady=4, padx=(0, 8))
        self.semester_var = tk.StringVar(value=self.current_semester)
        semester_combo = ttk.Combobox(sem_frame, textvariable=self.semester_var,
                                      values=["Semester 1", "Semester 2", "Summer"],
                                      width=12, state="readonly", style="TCombobox")
        semester_combo.grid(row=0, column=3, sticky="w", pady=4, padx=(0, 16))

        btn_load_courses = ttk.Button(sem_frame, text="Load Courses", command=self.load_courses, style="Primary.TButton")
        btn_load_courses.grid(row=0, column=4, padx=4, pady=4)

        # Courses frame
        courses_container = ttk.Frame(container, style="Card.TFrame", padding=16)
        courses_container.grid(row=2, column=0, sticky="nsew", pady=(0, 16))
        container.rowconfigure(2, weight=1)
        container.columnconfigure(0, weight=1)

        self.course_canvas = tk.Canvas(courses_container, borderwidth=0, highlightthickness=0, background="#fefefe")
        self.course_canvas.pack(side="left", fill="both", expand=True)

        self.course_scroll = ttk.Scrollbar(courses_container, orient="vertical", command=self.course_canvas.yview, style="Vertical.TScrollbar")
        self.course_scroll.pack(side="right", fill="y")

        self.course_canvas.configure(yscrollcommand=self.course_scroll.set)

        self.course_inner = ttk.Frame(self.course_canvas, style="Card.TFrame")
        self.course_canvas.create_window((0, 0), window=self.course_inner, anchor="nw")

        self.course_inner.bind("<Configure>", lambda e: self.course_canvas.configure(scrollregion=self.course_canvas.bbox("all")))

        header_bg = "#cde0ff"
        header_text = "#10357a"
        header = ['Course Name', 'Grade', 'Credits', 'Action']
        for idx, text in enumerate(header):
            lbl = ttk.Label(self.course_inner, text=text,
                            background=header_bg, foreground=header_text,
                            font=(self.app_font, 11, "bold"),
                            padding=6, borderwidth=1, relief="ridge")
            lbl.grid(row=0, column=idx, sticky="ew", padx=2, pady=2)
            self.course_inner.grid_columnconfigure(idx, weight=1)

        self.add_course_row()

        bottom_frame = ttk.Frame(container, style="TFrame")
        bottom_frame.grid(row=3, column=0, sticky="ew")
        bottom_frame.columnconfigure(tuple(range(7)), weight=1)

        ttk.Button(bottom_frame, text=f"{ICON_ADD} Add Course", command=self.add_course_row, style="Primary.TButton").grid(row=0, column=0, padx=4, pady=12, sticky="ew")
        ttk.Button(bottom_frame, text=f"{ICON_SAVE} Save Courses", command=self.save_courses, style="Primary.TButton").grid(row=0, column=1, padx=4, pady=12, sticky="ew")
        ttk.Button(bottom_frame, text="Clear Courses", command=self.clear_course_rows, style="Secondary.TButton").grid(row=0, column=2, padx=4, pady=12, sticky="ew")
        ttk.Button(bottom_frame, text=f"{ICON_EXPORT} Export Excel", command=self.export_excel, style="Primary.TButton").grid(row=0, column=3, padx=4, pady=12, sticky="ew")
        ttk.Button(bottom_frame, text=f"{ICON_IMPORT} Import Excel", command=self.import_excel, style="Primary.TButton").grid(row=0, column=4, padx=4, pady=12, sticky="ew")
        ttk.Button(bottom_frame, text=f"{ICON_CALC} Calculate GPA", command=self.calculate_gpa, style="Primary.TButton").grid(row=0, column=5, padx=4, pady=12, sticky="ew")
        ttk.Button(bottom_frame, text="Export All GPA Summary", command=self.export_all_gpa_summary, style="Secondary.TButton").grid(row=0, column=6, padx=4, pady=12, sticky="ew")

        gpa_frame = ttk.Frame(container, style="TFrame")
        gpa_frame.grid(row=4, column=0, sticky="w", pady=12)
        self.gpa_label = ttk.Label(gpa_frame, text="", font=(self.app_font, 16, "bold"), foreground="#1e40af", background="#f4f6fb")
        self.gpa_label.grid(row=0, column=0, sticky="w", padx=(0, 48))
        self.sem_gpa_label = ttk.Label(gpa_frame, text="", font=(self.app_font, 16, "bold"), foreground="#2563eb", background="#f4f6fb")
        self.sem_gpa_label.grid(row=0, column=1, sticky="w")

        self.chart_frame = ttk.Frame(container, style="Card.TFrame", padding=12)
        self.chart_frame.grid(row=5, column=0, sticky="nsew")
        container.rowconfigure(5, weight=0)

        self.figure = plt.Figure(figsize=(10, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Academic Progress (GPA and Credits per Semester)")
        self.ax.set_xlabel("Semester (Year-Semester)")
        self.ax.set_ylabel("GPA / Credits")
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        self.student_combo.focus_set()
        self.load_students()

    # Student Methods
    def add_student(self):
        name = self.name_entry.get().strip()
        index_number = self.index_entry.get().strip()
        if not name or not index_number:
            messagebox.showwarning("Input Error", "Both Name and Index Number are required.", parent=self.root)
            return
        try:
            self.cursor.execute("INSERT INTO students (name, index_number) VALUES (?, ?)", (name, index_number))
            self.conn.commit()
            self.load_students()
            messagebox.showinfo("Success", f"Student '{name}' (Index: {index_number}) added.", parent=self.root)
            self.name_entry.delete(0, tk.END)
            self.index_entry.delete(0, tk.END)
        except sqlite3.IntegrityError as e:
            if "UNIQUE" in str(e).upper():
                messagebox.showwarning("Exists", "Student name or index number already exists! Use unique index numbers.", parent=self.root)
            else:
                messagebox.showerror("Error", "Database error: " + str(e), parent=self.root)

    def update_student(self):
        selected = self.student_combo.get()
        if not selected:
            messagebox.showwarning("Warning", "Select a student first.", parent=self.root)
            return
        student = self.parse_student(selected)
        if not student:
            messagebox.showerror("Error", "Selected student format invalid.", parent=self.root)
            return
        old_name, old_index = student

        new_name = self.name_entry.get().strip()
        new_index = self.index_entry.get().strip()
        if not new_name or not new_index:
            messagebox.showwarning("Input Error", "Both Name and Index Number are required.", parent=self.root)
            return
        if (new_name, new_index) == (old_name, old_index):
            messagebox.showinfo("No Changes", "No changes detected to update.", parent=self.root)
            return
        try:
            self.cursor.execute("UPDATE students SET name=?, index_number=? WHERE name=? AND index_number=?",
                                (new_name, new_index, old_name, old_index))
            self.conn.commit()
            self.load_students()
            self.gpa_label.config(text="")
            self.sem_gpa_label.config(text="")
            messagebox.showinfo("Updated", f"Student updated to '{new_name}' (Index: {new_index}).", parent=self.root)
            display_val = f"{new_index} - {new_name}"
            self.student_combo.set(display_val)
            self.current_student = (new_name, new_index)
            self.load_courses()
            self.update_progress_chart()
        except sqlite3.IntegrityError as e:
            if "UNIQUE" in str(e).upper():
                messagebox.showwarning("Exists", "New student name or index number conflicts with existing record.", parent=self.root)
            else:
                messagebox.showerror("Error", "Database error: " + str(e), parent=self.root)

    def delete_student(self):
        selected = self.student_combo.get()
        if not selected:
            messagebox.showwarning("Warning", "No student selected.", parent=self.root)
            return
        student = self.parse_student(selected)
        if not student:
            messagebox.showerror("Error", "Selected student format invalid.", parent=self.root)
            return
        name, index_number = student
        confirm = messagebox.askyesno("Confirm", f"Delete student '{name}' with Index Number '{index_number}' and all related data?", parent=self.root)
        if confirm:
            self.cursor.execute("SELECT id FROM students WHERE name=? AND index_number=?", (name, index_number))
            res = self.cursor.fetchone()
            if not res:
                messagebox.showerror("Error", "Student not found in the database.", parent=self.root)
                return
            student_id = res[0]
            self.cursor.execute("DELETE FROM courses WHERE student_id=?", (student_id,))
            self.cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
            self.conn.commit()
            self.load_students()
            self.clear_entries()
            self.current_student = None
            self.gpa_label.config(text="")
            self.sem_gpa_label.config(text="")
            self.update_progress_chart()
            messagebox.showinfo("Deleted", f"Student '{name}' (Index: {index_number}) and all data deleted.", parent=self.root)

    def select_student(self):
        selected = self.student_combo.get()
        if not selected:
            messagebox.showwarning("Warning", "Select a student first.", parent=self.root)
            return
        student = self.parse_student(selected)
        if not student:
            messagebox.showerror("Error", "Selected student format invalid.", parent=self.root)
            return
        self.current_student = student  
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, student[0])
        self.index_entry.delete(0, tk.END)
        self.index_entry.insert(0, student[1])
        self.load_courses()
        self.update_progress_chart()

    def filter_students(self, event):
        pattern = self.student_combo.get().lower()
        self.cursor.execute("SELECT name, index_number FROM students ORDER BY name")
        students = self.cursor.fetchall()
        filtered = [f"{idx} - {name}" for name, idx in students if pattern in name.lower() or pattern in idx.lower()]
        self.student_combo['values'] = filtered

    def load_students(self):
        self.cursor.execute("SELECT name, index_number FROM students ORDER BY name")
        students = self.cursor.fetchall()
        display_values = [f"{idx} - {name}" for name, idx in students]
        self.student_combo['values'] = display_values
        if students:
            first = students[0]
            display_val = f"{first[1]} - {first[0]}"
            self.student_combo.set(display_val)
            self.current_student = (first[0], first[1])
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, first[0])
            self.index_entry.delete(0, tk.END)
            self.index_entry.insert(0, first[1])
            self.load_courses()
            self.update_progress_chart()
        else:
            self.student_combo.set('')
            self.current_student = None
            self.clear_entries()
            self.gpa_label.config(text="")
            self.sem_gpa_label.config(text="")
            self.update_progress_chart()

    def parse_student(self, display_text):
        try:
            parts = display_text.split(" - ", 1)
            if len(parts) == 2:
                index_number = parts[0].strip()
                name = parts[1].strip()
                return (name, index_number)
        except Exception:
            pass
        return None

    # Course Methods (unchanged from original)

    def add_course_row(self, cname='', grade='A', credits=''):
        row = len(self.entries) + 1

        name_entry = ttk.Entry(self.course_inner, width=30, font=(self.app_font, 11))
        name_entry.grid(row=row, column=0, padx=8, pady=4, sticky="ew", ipadx=3, ipady=3)
        name_entry.insert(0, cname)

        grade_var = tk.StringVar(value=grade)
        grade_combo = ttk.Combobox(self.course_inner,
                                   textvariable=grade_var,
                                   values=list(grade_points.keys()),
                                   width=5,
                                   state="readonly",
                                   font=(self.app_font, 11))
        grade_combo.grid(row=row, column=1, padx=8, pady=4, sticky="ew", ipadx=3, ipady=3)

        credits_entry = ttk.Entry(self.course_inner, width=10, font=(self.app_font, 11))
        credits_entry.grid(row=row, column=2, padx=8, pady=4, sticky="ew", ipadx=3, ipady=3)
        credits_entry.insert(0, credits)

        del_button = ttk.Button(self.course_inner, text="Delete", command=lambda: self.confirm_delete_row(row - 1), width=8, style="Danger.TButton")
        del_button.grid(row=row, column=3, padx=8, pady=4)

        credits_entry.bind("<FocusOut>", lambda e, ent=credits_entry, cname=name_entry: self.validate_credits(ent, cname))
        grade_combo.bind("<<ComboboxSelected>>", lambda e, var=grade_var, cname=name_entry: self.validate_grade(var, cname))

        self.entries.append((name_entry, grade_var, credits_entry, del_button))

    def confirm_delete_row(self, idx):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this course?"):
            self.delete_row(idx)

    def validate_credits(self, entry_widget, cname_widget):
        val = entry_widget.get().strip()
        if val == '':
            entry_widget.configure(foreground='black')
            return True
        try:
            val_f = float(val)
            if val_f <= 0:
                raise ValueError
            entry_widget.configure(foreground='black')
            return True
        except ValueError:
            messagebox.showwarning("Invalid Input", f"Invalid credits value '{val}' for course '{cname_widget.get()}'. Enter positive number.", parent=self.root)
            entry_widget.focus_set()
            entry_widget.configure(foreground='red')
            return False

    def validate_grade(self, var, cname_widget):
        val = var.get()
        if val not in grade_points:
            messagebox.showwarning("Invalid Grade", f"Invalid grade '{val}' for course '{cname_widget.get()}'. Please select a valid grade.", parent=self.root)
            return False
        return True

    def delete_row(self, idx):
        for widget in self.entries[idx]:
            widget.destroy()
        self.entries.pop(idx)
        self.reorder_entries()

    def reorder_entries(self):
        data = [(e[0].get(), e[1].get(), e[2].get()) for e in self.entries]
        for widget in self.course_inner.winfo_children():
            widget.destroy()
        self.entries.clear()

        header_bg = "#cde0ff"
        header_text = "#10357a"
        header = ['Course Name', 'Grade', 'Credits', 'Action']
        for idx, text in enumerate(header):
            lbl = ttk.Label(self.course_inner, text=text,
                            background=header_bg, foreground=header_text,
                            font=(self.app_font, 11, "bold"),
                            padding=6, borderwidth=1, relief="ridge")
            lbl.grid(row=0, column=idx, sticky="ew", padx=2, pady=2)
            self.course_inner.grid_columnconfigure(idx, weight=1)
        for d in data:
            self.add_course_row(*d)

    def clear_entries(self):
        for widget in self.course_inner.winfo_children():
            widget.destroy()
        self.entries.clear()
        header_bg = "#cde0ff"
        header_text = "#10357a"
        header = ['Course Name', 'Grade', 'Credits', 'Action']
        for idx, text in enumerate(header):
            lbl = ttk.Label(self.course_inner, text=text,
                            background=header_bg, foreground=header_text,
                            font=(self.app_font, 11, "bold"),
                            padding=6, borderwidth=1, relief="ridge")
            lbl.grid(row=0, column=idx, sticky="ew", padx=2, pady=2)
            self.course_inner.grid_columnconfigure(idx, weight=1)

    def clear_course_rows(self):
        if messagebox.askyesno("Clear Courses", "Are you sure you want to clear all course entries for this year and semester?"):
            self.clear_entries()
            self.add_course_row()

    def save_courses(self):
        if not self.current_student:
            messagebox.showwarning("Warning", "Please select a student first.", parent=self.root)
            return
        name, index_number = self.current_student
        self.cursor.execute("SELECT id FROM students WHERE name=? AND index_number=?", (name, index_number))
        student_id_res = self.cursor.fetchone()
        if not student_id_res:
            messagebox.showerror("Error", "Selected student does not exist in database.", parent=self.root)
            return
        student_id = student_id_res[0]
        self.cursor.execute("DELETE FROM courses WHERE student_id=? AND year=? AND semester=?",
                            (student_id, self.year_var.get(), self.semester_var.get()))
        for name_entry, grade_var, credits_entry, _ in self.entries:
            cname, grade, credits = name_entry.get().strip(), grade_var.get().strip(), credits_entry.get().strip()
            if cname and credits:
                if not self.validate_credits(credits_entry, name_entry):
                    return
                if not self.validate_grade(grade_var, name_entry):
                    return
                try:
                    credits_val = float(credits)
                    self.cursor.execute("INSERT INTO courses (student_id, year, semester, course_name, grade, credits) VALUES (?,?,?,?,?,?)",
                                        (student_id, self.year_var.get(), self.semester_var.get(), cname, grade, credits_val))
                except ValueError:
                    messagebox.showwarning("Invalid Input", f"Invalid credits value for course '{cname}'. Please enter a valid number.", parent=self.root)
                    return
        self.conn.commit()
        messagebox.showinfo("Saved", "Courses saved successfully.", parent=self.root)

    def load_courses(self):
        if not self.current_student:
            messagebox.showwarning("Warning", "Please select a student first.", parent=self.root)
            return
        self.clear_entries()
        self.gpa_label.config(text="")
        self.sem_gpa_label.config(text="")
        name, index_number = self.current_student
        self.cursor.execute("""
            SELECT id FROM students WHERE name=? AND index_number=?
        """, (name, index_number))
        student_id_res = self.cursor.fetchone()
        if not student_id_res:
            messagebox.showerror("Error", "Selected student does not exist in database.", parent=self.root)
            return
        student_id = student_id_res[0]
        self.cursor.execute("""
            SELECT course_name, grade, credits FROM courses 
            WHERE student_id=? AND year=? AND semester=?
        """, (student_id, self.year_var.get(), self.semester_var.get()))
        rows = self.cursor.fetchall()
        if rows:
            for row in rows:
                self.add_course_row(*row)
        else:
            self.add_course_row()

    def calculate_gpa(self):
        if not self.current_student:
            messagebox.showwarning("Warning", "Please select a student first.", parent=self.root)
            return
        name, index_number = self.current_student
        self.cursor.execute("SELECT id FROM students WHERE name=? AND index_number=?", (name, index_number))
        student_id_res = self.cursor.fetchone()
        if not student_id_res:
            messagebox.showerror("Error", "Selected student does not exist in database.", parent=self.root)
            return
        student_id = student_id_res[0]

        self.cursor.execute("SELECT grade, credits FROM courses WHERE student_id=?", (student_id,))
        data = self.cursor.fetchall()
        total_points, total_credits = 0, 0
        for grade, credits in data:
            total_points += grade_points.get(grade, 0) * credits
            total_credits += credits
        cum_gpa = total_points / total_credits if total_credits else 0
        self.gpa_label.config(text=f"Cumulative GPA: {cum_gpa:.2f} (Credits: {total_credits})")

        self.cursor.execute("""
            SELECT grade, credits FROM courses WHERE student_id=? AND year=? AND semester=?
        """, (student_id, self.year_var.get(), self.semester_var.get()))
        sem_data = self.cursor.fetchall()
        sem_points, sem_credits = 0, 0
        for grade, credits in sem_data:
            sem_points += grade_points.get(grade, 0) * credits
            sem_credits += credits
        sem_gpa = sem_points / sem_credits if sem_credits else 0
        self.sem_gpa_label.config(text=f"{self.year_var.get()} {self.semester_var.get()} GPA: {sem_gpa:.2f} (Credits: {sem_credits})")

        self.update_progress_chart()

    def update_progress_chart(self):
        if not self.current_student:
            self.ax.clear()
            self.ax.set_title("Academic Progress (GPA and Credits per Semester)")
            self.ax.set_xlabel("Semester (Year-Semester)")
            self.ax.set_ylabel("GPA / Credits")
            self.canvas.draw()
            return

        name, index_number = self.current_student
        self.cursor.execute("SELECT id FROM students WHERE name=? AND index_number=?", (name, index_number))
        student_id_res = self.cursor.fetchone()
        if not student_id_res:
            return
        student_id = student_id_res[0]

        self.cursor.execute("""
            SELECT year, semester FROM courses WHERE student_id=? GROUP BY year, semester
        """, (student_id,))
        semesters = self.cursor.fetchall()

        labels = []
        gpa_values = []
        credits_values = []
        total_earned_credits = 0
        cumulative_credits = []
        DEGREE_TOTAL_CREDITS = 120.0  

        sem_order = {"Semester 1":1, "Semester 2":2, "Summer":3}
        def semester_sort_key(t):
            year_str, sem_str = t
            try:
                year_num = int(year_str.replace("Year ", ""))
            except:
                year_num = 0
            sem_num = sem_order.get(sem_str, 0)
            return (year_num, sem_num)
        semesters = sorted(semesters, key=semester_sort_key)

        for (year, semester) in semesters:
            label = f"{year} {semester}"
            labels.append(label)
            self.cursor.execute("""
                SELECT grade, credits FROM courses WHERE student_id=? AND year=? AND semester=?
            """, (student_id, year, semester))
            data = self.cursor.fetchall()
            points = 0
            credits = 0
            for grade, cred in data:
                points += grade_points.get(grade,0) * cred
                credits += cred
            gpa = points / credits if credits else 0
            gpa_values.append(gpa)
            credits_values.append(credits)
            total_earned_credits += credits
            cumulative_credits.append(total_earned_credits)

        self.ax.clear()
        if not labels:
            self.ax.text(0.5, 0.5, "No course data available for progress chart.", ha='center', va='center')
            self.ax.set_title("Academic Progress (GPA and Credits per Semester)")
            self.ax.set_xlabel("Semester (Year-Semester)")
            self.ax.set_ylabel("GPA / Credits")
            self.canvas.draw()
            return

        self.ax.plot(labels, gpa_values, color="#1e40af", marker='o', label="GPA")

        ax2 = self.ax.twinx()
        ax2.bar(labels, credits_values, alpha=0.35, color="#f59e0b", label="Credits in Semester")
        ax2.plot(labels, cumulative_credits, linestyle='--', color="#2563eb", label="Cumulative Credits")

        ax2.set_ylabel("Credits")
        ax2.set_ylim(0, max(DEGREE_TOTAL_CREDITS, max(cumulative_credits) if cumulative_credits else 0)*1.1)

        ax2.axhline(y=DEGREE_TOTAL_CREDITS, color="red", linestyle=":", linewidth=1.5, label=f"Degree Requirement ({int(DEGREE_TOTAL_CREDITS)})")

        self.ax.set_ylim(0, 4.25)
        self.ax.set_xlabel("Semester")
        self.ax.set_ylabel("GPA")
        self.ax.set_title(f"{self.current_student[0]}'s Academic Progress")

        # Fix: set ticks before setting tick labels
        self.ax.set_xticks(range(len(labels)))
        self.ax.set_xticklabels(labels, rotation=45, ha='right')

        lines_1, labels_1 = self.ax.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        self.ax.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")

        self.figure.tight_layout()
        self.canvas.draw()

    def export_excel(self):
        if not self.current_student:
            messagebox.showwarning("Warning", "Select a student first.", parent=self.root)
            return
        name, index_number = self.current_student
        self.cursor.execute("SELECT id FROM students WHERE name=? AND index_number=?", (name, index_number))
        student_id_res = self.cursor.fetchone()
        if not student_id_res:
            messagebox.showerror("Error", "Selected student does not exist in database.", parent=self.root)
            return
        student_id = student_id_res[0]
        df = pd.read_sql_query("SELECT year, semester, course_name, grade, credits FROM courses WHERE student_id=?", self.conn, params=(student_id,))
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file:
            try:
                df.to_excel(file, index=False)
                messagebox.showinfo("Exported", "Data exported successfully.", parent=self.root)
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data. Error: {str(e)}", parent=self.root)

    def export_all_gpa_summary(self):
        self.cursor.execute("SELECT id, name, index_number FROM students ORDER BY name")
        students = self.cursor.fetchall()
        records = []
        for student_id, name, idx in students:
            self.cursor.execute("SELECT DISTINCT year, semester FROM courses WHERE student_id=?", (student_id,))
            ys = self.cursor.fetchall()
            for year, semester in ys:
                self.cursor.execute("SELECT grade, credits FROM courses WHERE student_id=? AND year=? AND semester=?", (student_id, year, semester))
                data = self.cursor.fetchall()
                points = 0
                credits = 0
                for grade, cred in data:
                    points += grade_points.get(grade,0) * cred
                    credits += cred
                gpa = points / credits if credits else 0
                records.append({
                    'Name': name,
                    'Index Number': idx,
                    'Year': year,
                    'Semester': semester,
                    'GPA': round(gpa, 3),
                    'Credits': credits
                })
        if not records:
            messagebox.showinfo("No Data", "No GPA records to export.", parent=self.root)
            return
        df = pd.DataFrame(records)
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file:
            try:
                df.to_excel(file, index=False)
                messagebox.showinfo("Exported", "GPA summary exported successfully.", parent=self.root)
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export GPA summary. Error: {str(e)}", parent=self.root)

    def import_excel(self):
        if not self.current_student:
            messagebox.showwarning("Warning", "Select a student first.", parent=self.root)
            return
        file = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if file:
            try:
                df = pd.read_excel(file)
            except Exception as e:
                messagebox.showerror("Import Error", f"Could not read the Excel file. Error: {str(e)}", parent=self.root)
                return
            required_cols = {"year", "semester", "course_name", "grade", "credits"}
            if not required_cols.issubset(df.columns):
                messagebox.showerror("Error", "Invalid file format. Missing required columns.", parent=self.root)
                return
            name, index_number = self.current_student
            self.cursor.execute("SELECT id FROM students WHERE name=? AND index_number=?", (name, index_number))
            student_id_res = self.cursor.fetchone()
            if not student_id_res:
                messagebox.showerror("Error", "Selected student does not exist in database.", parent=self.root)
                return
            student_id = student_id_res[0]
            errors = []
            for idx, row in df.iterrows():
                try:
                    g = row['grade']
                    c = float(row['credits'])
                    if g not in grade_points or c <= 0:
                        raise ValueError("Invalid grade or credits.")
                    self.cursor.execute("INSERT INTO courses (student_id, year, semester, course_name, grade, credits) VALUES (?,?,?,?,?,?)",
                        (student_id, row['year'], row['semester'], row['course_name'], g, c))
                except Exception as e:
                    errors.append(f"Row {idx+2}: {row.to_dict()} Error: {str(e)}")
            self.conn.commit()
            if errors:
                err_msg = "\n".join(errors)
                messagebox.showwarning("Import Errors", f"Some rows failed to import:\n{err_msg}", parent=self.root)
            else:
                messagebox.showinfo("Imported", "Data imported successfully.", parent=self.root)
            self.load_courses()


if __name__ == '__main__':
    root = tk.Tk()
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = GPAApp(root)
    root.mainloop()

