#!/usr/bin/env python3
"""
Student Management System
A complete offline desktop application for managing students, teachers, classes, attendance, and fees.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, date
import calendar
import os
from decimal import Decimal
import webbrowser
from tkinter import font

class DatabaseManager:
    def __init__(self, db_path="student_management.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.executescript("""
        -- Students Table
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            student_name TEXT NOT NULL,
            is_free_participant INTEGER DEFAULT 0,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Teachers Table
        CREATE TABLE IF NOT EXISTS teachers (
            teacher_id TEXT PRIMARY KEY,
            teacher_name TEXT NOT NULL,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Classes Table
        CREATE TABLE IF NOT EXISTS classes (
            class_id TEXT PRIMARY KEY,
            class_name TEXT NOT NULL,
            teacher_id TEXT NOT NULL,
            monthly_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
        );

        -- Student-Class Assignments
        CREATE TABLE IF NOT EXISTS student_classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            class_id TEXT NOT NULL,
            assigned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
            UNIQUE(student_id, class_id)
        );

        -- Attendance Table
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            class_id TEXT NOT NULL,
            attendance_date DATE NOT NULL,
            month_year TEXT NOT NULL,
            week_number INTEGER NOT NULL,
            present INTEGER DEFAULT 1,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
            UNIQUE(student_id, class_id, attendance_date)
        );

        -- Fee Collections Table
        CREATE TABLE IF NOT EXISTS fee_collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            class_id TEXT NOT NULL,
            month_year TEXT NOT NULL,
            fee_amount DECIMAL(10,2) NOT NULL,
            attendance_count INTEGER NOT NULL,
            collection_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
            UNIQUE(student_id, class_id, month_year)
        );

        -- Teacher Payments Table
        CREATE TABLE IF NOT EXISTS teacher_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id TEXT NOT NULL,
            payment_amount DECIMAL(10,2) NOT NULL,
            payment_date DATE NOT NULL,
            month_year TEXT,
            notes TEXT,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
        );

        -- System Settings Table
        CREATE TABLE IF NOT EXISTS system_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT NOT NULL,
            updated_date DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Insert default settings if they don't exist
        cursor.execute("SELECT COUNT(*) FROM system_settings")
        if cursor.fetchone()[0] == 0:
            cursor.executescript("""
            INSERT INTO system_settings (setting_key, setting_value) VALUES 
            ('teacher_share_percentage', '80'),
            ('institute_share_percentage', '20'),
            ('minimum_attendance_for_fees', '2');
            """)
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            conn.close()
            return results
        else:
            conn.commit()
            conn.close()
            return cursor.rowcount

class StudentManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Create main interface
        self.create_main_interface()
        
        # Load dashboard on startup
        self.show_dashboard()
    
    def create_main_interface(self):
        """Create the main application interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.students_frame = ttk.Frame(self.notebook)
        self.teachers_frame = ttk.Frame(self.notebook)
        self.classes_frame = ttk.Frame(self.notebook)
        self.attendance_frame = ttk.Frame(self.notebook)
        self.fees_frame = ttk.Frame(self.notebook)
        self.payments_frame = ttk.Frame(self.notebook)
        self.reports_frame = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_frame, text="📊 Dashboard")
        self.notebook.add(self.students_frame, text="👥 Students")
        self.notebook.add(self.teachers_frame, text="👨‍🏫 Teachers")
        self.notebook.add(self.classes_frame, text="📚 Classes")
        self.notebook.add(self.attendance_frame, text="✅ Attendance")
        self.notebook.add(self.fees_frame, text="💰 Fees")
        self.notebook.add(self.payments_frame, text="💳 Teacher Payments")
        self.notebook.add(self.reports_frame, text="📄 Reports")
        
        # Setup each tab
        self.setup_dashboard_tab()
        self.setup_students_tab()
        self.setup_teachers_tab()
        self.setup_classes_tab()
        self.setup_attendance_tab()
        self.setup_fees_tab()
        self.setup_payments_tab()
        self.setup_reports_tab()
    
    def setup_dashboard_tab(self):
        """Setup dashboard tab"""
        # Create scrollable frame
        canvas = tk.Canvas(self.dashboard_frame)
        scrollbar = ttk.Scrollbar(self.dashboard_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.dashboard_content = scrollable_frame
    
    def setup_students_tab(self):
        """Setup students management tab"""
        # Left panel for form
        left_panel = ttk.LabelFrame(self.students_frame, text="Add/Edit Student", padding="10")
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        
        # Student form fields
        ttk.Label(left_panel, text="Student ID:").pack(anchor='w')
        self.student_id_var = tk.StringVar()
        ttk.Entry(left_panel, textvariable=self.student_id_var, width=30).pack(fill='x', pady=(0, 10))
        
        ttk.Label(left_panel, text="Student Name:").pack(anchor='w')
        self.student_name_var = tk.StringVar()
        ttk.Entry(left_panel, textvariable=self.student_name_var, width=30).pack(fill='x', pady=(0, 10))
        
        self.student_free_var = tk.BooleanVar()
        ttk.Checkbutton(left_panel, text="Free Participant", variable=self.student_free_var).pack(anchor='w', pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="Add Student", command=self.add_student).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="Update", command=self.update_student).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_student).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_student_form).pack(side='left', padx=5)
        
        # Class assignment section
        ttk.Separator(left_panel, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(left_panel, text="Assign to Class:").pack(anchor='w')
        
        self.student_class_var = tk.StringVar()
        self.student_class_combo = ttk.Combobox(left_panel, textvariable=self.student_class_var, state='readonly')
        self.student_class_combo.pack(fill='x', pady=(0, 10))
        
        ttk.Button(left_panel, text="Assign Class", command=self.assign_student_to_class).pack(fill='x')
        
        # Right panel for list
        right_panel = ttk.LabelFrame(self.students_frame, text="Students List", padding="10")
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Students treeview
        self.students_tree = ttk.Treeview(right_panel, columns=('ID', 'Name', 'Free', 'Classes'), show='headings')
        self.students_tree.heading('ID', text='Student ID')
        self.students_tree.heading('Name', text='Name')
        self.students_tree.heading('Free', text='Free Participant')
        self.students_tree.heading('Classes', text='Classes')
        
        self.students_tree.column('ID', width=100)
        self.students_tree.column('Name', width=150)
        self.students_tree.column('Free', width=100)
        self.students_tree.column('Classes', width=200)
        
        self.students_tree.pack(fill='both', expand=True)
        self.students_tree.bind('<<TreeviewSelect>>', self.on_student_select)
        
        # Load students
        self.load_students()
        self.load_classes_combo()
    
    def setup_teachers_tab(self):
        """Setup teachers management tab"""
        # Left panel for form
        left_panel = ttk.LabelFrame(self.teachers_frame, text="Add/Edit Teacher", padding="10")
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        
        # Teacher form fields
        ttk.Label(left_panel, text="Teacher ID:").pack(anchor='w')
        self.teacher_id_var = tk.StringVar()
        ttk.Entry(left_panel, textvariable=self.teacher_id_var, width=30).pack(fill='x', pady=(0, 10))
        
        ttk.Label(left_panel, text="Teacher Name:").pack(anchor='w')
        self.teacher_name_var = tk.StringVar()
        ttk.Entry(left_panel, textvariable=self.teacher_name_var, width=30).pack(fill='x', pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="Add Teacher", command=self.add_teacher).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="Update", command=self.update_teacher).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_teacher).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_teacher_form).pack(side='left', padx=5)
        
        # Right panel for list
        right_panel = ttk.LabelFrame(self.teachers_frame, text="Teachers List", padding="10")
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Teachers treeview
        self.teachers_tree = ttk.Treeview(right_panel, columns=('ID', 'Name', 'Classes'), show='headings')
        self.teachers_tree.heading('ID', text='Teacher ID')
        self.teachers_tree.heading('Name', text='Name')
        self.teachers_tree.heading('Classes', text='Classes')
        
        self.teachers_tree.column('ID', width=100)
        self.teachers_tree.column('Name', width=150)
        self.teachers_tree.column('Classes', width=200)
        
        self.teachers_tree.pack(fill='both', expand=True)
        self.teachers_tree.bind('<<TreeviewSelect>>', self.on_teacher_select)
        
        # Load teachers
        self.load_teachers()
    
    def setup_classes_tab(self):
        """Setup classes management tab"""
        # Left panel for form
        left_panel = ttk.LabelFrame(self.classes_frame, text="Add/Edit Class", padding="10")
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        
        # Class form fields
        ttk.Label(left_panel, text="Class ID:").pack(anchor='w')
        self.class_id_var = tk.StringVar()
        ttk.Entry(left_panel, textvariable=self.class_id_var, width=30).pack(fill='x', pady=(0, 10))
        
        ttk.Label(left_panel, text="Class Name:").pack(anchor='w')
        self.class_name_var = tk.StringVar()
        ttk.Entry(left_panel, textvariable=self.class_name_var, width=30).pack(fill='x', pady=(0, 10))
        
        ttk.Label(left_panel, text="Teacher:").pack(anchor='w')
        self.class_teacher_var = tk.StringVar()
        self.class_teacher_combo = ttk.Combobox(left_panel, textvariable=self.class_teacher_var, state='readonly')
        self.class_teacher_combo.pack(fill='x', pady=(0, 10))
        
        ttk.Label(left_panel, text="Monthly Fee:").pack(anchor='w')
        self.class_fee_var = tk.StringVar()
        ttk.Entry(left_panel, textvariable=self.class_fee_var, width=30).pack(fill='x', pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="Add Class", command=self.add_class).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="Update", command=self.update_class).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_class).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_class_form).pack(side='left', padx=5)
        
        # Right panel for list
        right_panel = ttk.LabelFrame(self.classes_frame, text="Classes List", padding="10")
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Classes treeview
        self.classes_tree = ttk.Treeview(right_panel, columns=('ID', 'Name', 'Teacher', 'Fee', 'Students'), show='headings')
        self.classes_tree.heading('ID', text='Class ID')
        self.classes_tree.heading('Name', text='Class Name')
        self.classes_tree.heading('Teacher', text='Teacher')
        self.classes_tree.heading('Fee', text='Monthly Fee')
        self.classes_tree.heading('Students', text='Students')
        
        self.classes_tree.column('ID', width=100)
        self.classes_tree.column('Name', width=150)
        self.classes_tree.column('Teacher', width=150)
        self.classes_tree.column('Fee', width=100)
        self.classes_tree.column('Students', width=80)
        
        self.classes_tree.pack(fill='both', expand=True)
        self.classes_tree.bind('<<TreeviewSelect>>', self.on_class_select)
        
        # Load classes and teachers
        self.load_classes()
        self.load_teachers_combo()
    
    def setup_attendance_tab(self):
        """Setup attendance management tab"""
        # Top frame for controls
        top_frame = ttk.Frame(self.attendance_frame)
        top_frame.pack(fill='x', padx=10, pady=10)
        
        # Month/Year selection
        ttk.Label(top_frame, text="Month/Year:").pack(side='left')
        self.attendance_month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        ttk.Entry(top_frame, textvariable=self.attendance_month_var, width=10).pack(side='left', padx=5)
        
        # Class selection
        ttk.Label(top_frame, text="Class:").pack(side='left', padx=(20, 0))
        self.attendance_class_var = tk.StringVar()
        self.attendance_class_combo = ttk.Combobox(top_frame, textvariable=self.attendance_class_var, state='readonly', width=20)
        self.attendance_class_combo.pack(side='left', padx=5)
        
        # Load attendance button
        ttk.Button(top_frame, text="Load Attendance", command=self.load_attendance).pack(side='left', padx=20)
        
        # Save attendance button
        ttk.Button(top_frame, text="Save Attendance", command=self.save_attendance).pack(side='left', padx=5)
        
        # Attendance grid frame
        grid_frame = ttk.LabelFrame(self.attendance_frame, text="Attendance Grid", padding="10")
        grid_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Create canvas for scrollable attendance grid
        self.attendance_canvas = tk.Canvas(grid_frame)
        attendance_scrollbar = ttk.Scrollbar(grid_frame, orient="vertical", command=self.attendance_canvas.yview)
        self.attendance_scrollable_frame = ttk.Frame(self.attendance_canvas)
        
        self.attendance_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.attendance_canvas.configure(scrollregion=self.attendance_canvas.bbox("all"))
        )
        
        self.attendance_canvas.create_window((0, 0), window=self.attendance_scrollable_frame, anchor="nw")
        self.attendance_canvas.configure(yscrollcommand=attendance_scrollbar.set)
        
        self.attendance_canvas.pack(side="left", fill="both", expand=True)
        attendance_scrollbar.pack(side="right", fill="y")
        
        # Load classes for attendance
        self.load_classes_for_attendance()
    
    def setup_fees_tab(self):
        """Setup fees management tab"""
        # Top frame for controls
        top_frame = ttk.Frame(self.fees_frame)
        top_frame.pack(fill='x', padx=10, pady=10)
        
        # Month/Year selection
        ttk.Label(top_frame, text="Month/Year:").pack(side='left')
        self.fees_month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        ttk.Entry(top_frame, textvariable=self.fees_month_var, width=10).pack(side='left', padx=5)
        
        # Load eligible fees button
        ttk.Button(top_frame, text="Load Eligible Students", command=self.load_eligible_fees).pack(side='left', padx=20)
        
        # Collect all fees button
        ttk.Button(top_frame, text="Collect All Eligible Fees", command=self.collect_all_fees).pack(side='left', padx=5)
        
        # Fees list frame
        fees_frame = ttk.LabelFrame(self.fees_frame, text="Fee Collection", padding="10")
        fees_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Fees treeview
        self.fees_tree = ttk.Treeview(fees_frame, columns=('Student', 'Class', 'Attendance', 'Fee', 'Status'), show='headings')
        self.fees_tree.heading('Student', text='Student')
        self.fees_tree.heading('Class', text='Class')
        self.fees_tree.heading('Attendance', text='Attendance')
        self.fees_tree.heading('Fee', text='Fee Amount')
        self.fees_tree.heading('Status', text='Status')
        
        self.fees_tree.column('Student', width=150)
        self.fees_tree.column('Class', width=150)
        self.fees_tree.column('Attendance', width=100)
        self.fees_tree.column('Fee', width=100)
        self.fees_tree.column('Status', width=100)
        
        self.fees_tree.pack(fill='both', expand=True)
        self.fees_tree.bind('<Double-1>', self.collect_individual_fee)
    
    def setup_payments_tab(self):
        """Setup teacher payments management tab"""
        # Left panel for payment form
        left_panel = ttk.LabelFrame(self.payments_frame, text="Record Payment", padding="10")
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        
        # Payment form fields
        ttk.Label(left_panel, text="Teacher:").pack(anchor='w')
        self.payment_teacher_var = tk.StringVar()
        self.payment_teacher_combo = ttk.Combobox(left_panel, textvariable=self.payment_teacher_var, state='readonly')
        self.payment_teacher_combo.pack(fill='x', pady=(0, 10))
        
        ttk.Label(left_panel, text="Payment Amount:").pack(anchor='w')
        self.payment_amount_var = tk.StringVar()
        ttk.Entry(left_panel, textvariable=self.payment_amount_var, width=30).pack(fill='x', pady=(0, 10))
        
        ttk.Label(left_panel, text="Payment Date:").pack(anchor='w')
        self.payment_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(left_panel, textvariable=self.payment_date_var, width=30).pack(fill='x', pady=(0, 10))
        
        ttk.Label(left_panel, text="Month/Year (optional):").pack(anchor='w')
        self.payment_month_var = tk.StringVar()
        ttk.Entry(left_panel, textvariable=self.payment_month_var, width=30).pack(fill='x', pady=(0, 10))
        
        ttk.Label(left_panel, text="Notes:").pack(anchor='w')
        self.payment_notes_var = tk.StringVar()
        ttk.Entry(left_panel, textvariable=self.payment_notes_var, width=30).pack(fill='x', pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="Record Payment", command=self.record_payment).pack(fill='x', pady=(0, 5))
        ttk.Button(button_frame, text="Clear", command=self.clear_payment_form).pack(fill='x')
        
        # Teacher balance summary
        ttk.Separator(left_panel, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(left_panel, text="Teacher Balance Summary:", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w')
        
        self.balance_text = tk.Text(left_panel, height=10, width=30, state='disabled')
        self.balance_text.pack(fill='both', expand=True, pady=10)
        
        # Right panel for payments list
        right_panel = ttk.LabelFrame(self.payments_frame, text="Payment History", padding="10")
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Payments treeview
        self.payments_tree = ttk.Treeview(right_panel, columns=('Date', 'Teacher', 'Amount', 'Month', 'Notes'), show='headings')
        self.payments_tree.heading('Date', text='Payment Date')
        self.payments_tree.heading('Teacher', text='Teacher')
        self.payments_tree.heading('Amount', text='Amount')
        self.payments_tree.heading('Month', text='For Month')
        self.payments_tree.heading('Notes', text='Notes')
        
        self.payments_tree.column('Date', width=100)
        self.payments_tree.column('Teacher', width=150)
        self.payments_tree.column('Amount', width=100)
        self.payments_tree.column('Month', width=100)
        self.payments_tree.column('Notes', width=200)
        
        self.payments_tree.pack(fill='both', expand=True)
        
        # Load payments
        self.load_payments()
        self.load_teachers_for_payment()
        self.update_balance_summary()
    
    def setup_reports_tab(self):
        """Setup reports tab"""
        # Reports control frame
        control_frame = ttk.LabelFrame(self.reports_frame, text="Generate Reports", padding="10")
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # Month selection
        ttk.Label(control_frame, text="Month/Year:").pack(side='left')
        self.report_month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        ttk.Entry(control_frame, textvariable=self.report_month_var, width=10).pack(side='left', padx=5)
        
        # Report buttons
        ttk.Button(control_frame, text="Monthly Summary", command=self.generate_monthly_summary).pack(side='left', padx=10)
        ttk.Button(control_frame, text="Teacher Financial Report", command=self.generate_teacher_report).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Export to CSV", command=self.export_to_csv).pack(side='left', padx=5)
        
        # Reports display frame
        reports_display_frame = ttk.LabelFrame(self.reports_frame, text="Report Output", padding="10")
        reports_display_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Text widget for report display
        self.reports_text = tk.Text(reports_display_frame, wrap='word', state='disabled')
        reports_scrollbar = ttk.Scrollbar(reports_display_frame, orient="vertical", command=self.reports_text.yview)
        self.reports_text.configure(yscrollcommand=reports_scrollbar.set)
        
        self.reports_text.pack(side="left", fill="both", expand=True)
        reports_scrollbar.pack(side="right", fill="y")
    
    # Student Management Methods
    def add_student(self):
        """Add a new student"""
        student_id = self.student_id_var.get().strip()
        student_name = self.student_name_var.get().strip()
        is_free = 1 if self.student_free_var.get() else 0
        
        if not student_id or not student_name:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        try:
            self.db.execute_query(
                "INSERT INTO students (student_id, student_name, is_free_participant) VALUES (?, ?, ?)",
                (student_id, student_name, is_free)
            )
            messagebox.showinfo("Success", "Student added successfully")
            self.clear_student_form()
            self.load_students()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Student ID already exists")
    
    def update_student(self):
        """Update selected student"""
        selected = self.students_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a student to update")
            return
        
        student_id = self.student_id_var.get().strip()
        student_name = self.student_name_var.get().strip()
        is_free = 1 if self.student_free_var.get() else 0
        
        if not student_id or not student_name:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        # Get original student ID from selection
        original_id = self.students_tree.item(selected[0])['values'][0]
        
        try:
            self.db.execute_query(
                "UPDATE students SET student_id = ?, student_name = ?, is_free_participant = ? WHERE student_id = ?",
                (student_id, student_name, is_free, original_id)
            )
            messagebox.showinfo("Success", "Student updated successfully")
            self.load_students()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Student ID already exists")
    
    def delete_student(self):
        """Delete selected student"""
        selected = self.students_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a student to delete")
            return
        
        student_id = self.students_tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete student {student_id}?"):
            self.db.execute_query("DELETE FROM students WHERE student_id = ?", (student_id,))
            messagebox.showinfo("Success", "Student deleted successfully")
            self.clear_student_form()
            self.load_students()
    
    def clear_student_form(self):
        """Clear student form"""
        self.student_id_var.set("")
        self.student_name_var.set("")
        self.student_free_var.set(False)
        self.student_class_var.set("")
    
    def on_student_select(self, event):
        """Handle student selection"""
        selected = self.students_tree.selection()
        if selected:
            values = self.students_tree.item(selected[0])['values']
            self.student_id_var.set(values[0])
            self.student_name_var.set(values[1])
            self.student_free_var.set(values[2] == 'Yes')
    
    def load_students(self):
        """Load students into treeview"""
        # Clear existing items
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        # Load students with their classes
        query = """
        SELECT s.student_id, s.student_name, 
               CASE WHEN s.is_free_participant = 1 THEN 'Yes' ELSE 'No' END,
               GROUP_CONCAT(c.class_name, ', ') as classes
        FROM students s
        LEFT JOIN student_classes sc ON s.student_id = sc.student_id
        LEFT JOIN classes c ON sc.class_id = c.class_id
        GROUP BY s.student_id, s.student_name, s.is_free_participant
        ORDER BY s.student_name
        """
        
        students = self.db.execute_query(query)
        for student in students:
            classes = student[3] if student[3] else "No classes assigned"
            self.students_tree.insert('', 'end', values=student[:3] + (classes,))
    
    def assign_student_to_class(self):
        """Assign student to selected class"""
        student_id = self.student_id_var.get().strip()
        class_id = self.student_class_var.get()
        
        if not student_id or not class_id:
            messagebox.showerror("Error", "Please select student and class")
            return
        
        try:
            self.db.execute_query(
                "INSERT INTO student_classes (student_id, class_id) VALUES (?, ?)",
                (student_id, class_id)
            )
            messagebox.showinfo("Success", "Student assigned to class successfully")
            self.load_students()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Student is already assigned to this class")
    
    def load_classes_combo(self):
        """Load classes into combobox"""
        classes = self.db.execute_query("SELECT class_id, class_name FROM classes ORDER BY class_name")
        class_list = [f"{cls[0]} - {cls[1]}" for cls in classes]
        self.student_class_combo['values'] = class_list
    
    # Teacher Management Methods
    def add_teacher(self):
        """Add a new teacher"""
        teacher_id = self.teacher_id_var.get().strip()
        teacher_name = self.teacher_name_var.get().strip()
        
        if not teacher_id or not teacher_name:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        try:
            self.db.execute_query(
                "INSERT INTO teachers (teacher_id, teacher_name) VALUES (?, ?)",
                (teacher_id, teacher_name)
            )
            messagebox.showinfo("Success", "Teacher added successfully")
            self.clear_teacher_form()
            self.load_teachers()
            self.load_teachers_combo()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Teacher ID already exists")
    
    def update_teacher(self):
        """Update selected teacher"""
        selected = self.teachers_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a teacher to update")
            return
        
        teacher_id = self.teacher_id_var.get().strip()
        teacher_name = self.teacher_name_var.get().strip()
        
        if not teacher_id or not teacher_name:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        original_id = self.teachers_tree.item(selected[0])['values'][0]
        
        try:
            self.db.execute_query(
                "UPDATE teachers SET teacher_id = ?, teacher_name = ? WHERE teacher_id = ?",
                (teacher_id, teacher_name, original_id)
            )
            messagebox.showinfo("Success", "Teacher updated successfully")
            self.load_teachers()
            self.load_teachers_combo()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Teacher ID already exists")
    
    def delete_teacher(self):
        """Delete selected teacher"""
        selected = self.teachers_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a teacher to delete")
            return
        
        teacher_id = self.teachers_tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete teacher {teacher_id}?"):
            self.db.execute_query("DELETE FROM teachers WHERE teacher_id = ?", (teacher_id,))
            messagebox.showinfo("Success", "Teacher deleted successfully")
            self.clear_teacher_form()
            self.load_teachers()
            self.load_teachers_combo()
    
    def clear_teacher_form(self):
        """Clear teacher form"""
        self.teacher_id_var.set("")
        self.teacher_name_var.set("")
    
    def on_teacher_select(self, event):
        """Handle teacher selection"""
        selected = self.teachers_tree.selection()
        if selected:
            values = self.teachers_tree.item(selected[0])['values']
            self.teacher_id_var.set(values[0])
            self.teacher_name_var.set(values[1])
    
    def load_teachers(self):
        """Load teachers into treeview"""
        for item in self.teachers_tree.get_children():
            self.teachers_tree.delete(item)
        
        query = """
        SELECT t.teacher_id, t.teacher_name, 
               GROUP_CONCAT(c.class_name, ', ') as classes
        FROM teachers t
        LEFT JOIN classes c ON t.teacher_id = c.teacher_id
        GROUP BY t.teacher_id, t.teacher_name
        ORDER BY t.teacher_name
        """
        
        teachers = self.db.execute_query(query)
        for teacher in teachers:
            classes = teacher[2] if teacher[2] else "No classes assigned"
            self.teachers_tree.insert('', 'end', values=teacher[:2] + (classes,))
    
    def load_teachers_combo(self):
        """Load teachers into combobox"""
        teachers = self.db.execute_query("SELECT teacher_id, teacher_name FROM teachers ORDER BY teacher_name")
        teacher_list = [f"{teacher[0]} - {teacher[1]}" for teacher in teachers]
        if hasattr(self, 'class_teacher_combo'):
            self.class_teacher_combo['values'] = teacher_list
    
    def load_teachers_for_payment(self):
        """Load teachers for payment combobox"""
        teachers = self.db.execute_query("SELECT teacher_id, teacher_name FROM teachers ORDER BY teacher_name")
        teacher_list = [f"{teacher[0]} - {teacher[1]}" for teacher in teachers]
        self.payment_teacher_combo['values'] = teacher_list
    
    # Class Management Methods
    def add_class(self):
        """Add a new class"""
        class_id = self.class_id_var.get().strip()
        class_name = self.class_name_var.get().strip()
        teacher_selection = self.class_teacher_var.get()
        fee = self.class_fee_var.get().strip()
        
        if not class_id or not class_name or not teacher_selection or not fee:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        try:
            fee_amount = float(fee)
            teacher_id = teacher_selection.split(' - ')[0]
            
            self.db.execute_query(
                "INSERT INTO classes (class_id, class_name, teacher_id, monthly_fee) VALUES (?, ?, ?, ?)",
                (class_id, class_name, teacher_id, fee_amount)
            )
            messagebox.showinfo("Success", "Class added successfully")
            self.clear_class_form()
            self.load_classes()
            self.load_classes_combo()
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Please enter a valid fee amount and select a teacher")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Class ID already exists")
    
    def update_class(self):
        """Update selected class"""
        selected = self.classes_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a class to update")
            return
        
        class_id = self.class_id_var.get().strip()
        class_name = self.class_name_var.get().strip()
        teacher_selection = self.class_teacher_var.get()
        fee = self.class_fee_var.get().strip()
        
        if not class_id or not class_name or not teacher_selection or not fee:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        try:
            fee_amount = float(fee)
            teacher_id = teacher_selection.split(' - ')[0]
            original_id = self.classes_tree.item(selected[0])['values'][0]
            
            self.db.execute_query(
                "UPDATE classes SET class_id = ?, class_name = ?, teacher_id = ?, monthly_fee = ? WHERE class_id = ?",
                (class_id, class_name, teacher_id, fee_amount, original_id)
            )
            messagebox.showinfo("Success", "Class updated successfully")
            self.load_classes()
            self.load_classes_combo()
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Please enter a valid fee amount and select a teacher")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Class ID already exists")
    
    def delete_class(self):
        """Delete selected class"""
        selected = self.classes_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a class to delete")
            return
        
        class_id = self.classes_tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete class {class_id}?"):
            self.db.execute_query("DELETE FROM classes WHERE class_id = ?", (class_id,))
            messagebox.showinfo("Success", "Class deleted successfully")
            self.clear_class_form()
            self.load_classes()
            self.load_classes_combo()
    
    def clear_class_form(self):
        """Clear class form"""
        self.class_id_var.set("")
        self.class_name_var.set("")
        self.class_teacher_var.set("")
        self.class_fee_var.set("")
    
    def on_class_select(self, event):
        """Handle class selection"""
        selected = self.classes_tree.selection()
        if selected:
            values = self.classes_tree.item(selected[0])['values']
            self.class_id_var.set(values[0])
            self.class_name_var.set(values[1])
            
            # Find and set teacher
            teacher_name = values[2]
            for teacher_option in self.class_teacher_combo['values']:
                if teacher_name in teacher_option:
                    self.class_teacher_var.set(teacher_option)
                    break
            
            self.class_fee_var.set(values[3])
    
    def load_classes(self):
        """Load classes into treeview"""
        for item in self.classes_tree.get_children():
            self.classes_tree.delete(item)
        
        query = """
        SELECT c.class_id, c.class_name, t.teacher_name, c.monthly_fee,
               COUNT(sc.student_id) as student_count
        FROM classes c
        JOIN teachers t ON c.teacher_id = t.teacher_id
        LEFT JOIN student_classes sc ON c.class_id = sc.class_id
        GROUP BY c.class_id, c.class_name, t.teacher_name, c.monthly_fee
        ORDER BY c.class_name
        """
        
        classes = self.db.execute_query(query)
        for cls in classes:
            self.classes_tree.insert('', 'end', values=cls)
    
    def load_classes_for_attendance(self):
        """Load classes for attendance combobox"""
        classes = self.db.execute_query("SELECT class_id, class_name FROM classes ORDER BY class_name")
        class_list = [f"{cls[0]} - {cls[1]}" for cls in classes]
        self.attendance_class_combo['values'] = class_list
    
    # Attendance Management Methods
    def load_attendance(self):
        """Load attendance grid for selected month and class"""
        month_year = self.attendance_month_var.get().strip()
        class_selection = self.attendance_class_var.get()
        
        if not month_year or not class_selection:
            messagebox.showerror("Error", "Please select month/year and class")
            return
        
        class_id = class_selection.split(' - ')[0]
        
        # Clear existing grid
        for widget in self.attendance_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get students in this class
        students = self.db.execute_query("""
            SELECT s.student_id, s.student_name 
            FROM students s
            JOIN student_classes sc ON s.student_id = sc.student_id
            WHERE sc.class_id = ?
            ORDER BY s.student_name
        """, (class_id,))
        
        if not students:
            ttk.Label(self.attendance_scrollable_frame, text="No students in this class").pack()
            return
        
        # Create grid headers
        header_frame = ttk.Frame(self.attendance_scrollable_frame)
        header_frame.pack(fill='x', pady=5)
        
        ttk.Label(header_frame, text="Student", width=20).grid(row=0, column=0, padx=5)
        for week in range(1, 6):  # Week 1-5
            ttk.Label(header_frame, text=f"Week {week}", width=10).grid(row=0, column=week, padx=5)
        
        # Create attendance checkboxes
        self.attendance_vars = {}
        
        for i, student in enumerate(students):
            student_id, student_name = student
            row_frame = ttk.Frame(self.attendance_scrollable_frame)
            row_frame.pack(fill='x', pady=2)
            
            ttk.Label(row_frame, text=student_name, width=20).grid(row=0, column=0, padx=5, sticky='w')
            
            self.attendance_vars[student_id] = {}
            
            for week in range(1, 6):
                var = tk.BooleanVar()
                self.attendance_vars[student_id][week] = var
                
                # Check if attendance already exists
                existing = self.db.execute_query("""
                    SELECT present FROM attendance 
                    WHERE student_id = ? AND class_id = ? AND month_year = ? AND week_number = ?
                """, (student_id, class_id, month_year, week))
                
                if existing:
                    var.set(existing[0][0] == 1)
                
                ttk.Checkbutton(row_frame, variable=var).grid(row=0, column=week, padx=5)
    
    def save_attendance(self):
        """Save attendance data"""
        month_year = self.attendance_month_var.get().strip()
        class_selection = self.attendance_class_var.get()
        
        if not month_year or not class_selection:
            messagebox.showerror("Error", "Please select month/year and class")
            return
        
        if not hasattr(self, 'attendance_vars'):
            messagebox.showerror("Error", "Please load attendance first")
            return
        
        class_id = class_selection.split(' - ')[0]
        
        try:
            # Get year and month for date calculations
            year, month = map(int, month_year.split('-'))
            
            for student_id, weeks in self.attendance_vars.items():
                for week_num, var in weeks.items():
                    present = 1 if var.get() else 0
                    
                    # Calculate attendance date (first day of week)
                    # Simple calculation: week 1 = 1st, week 2 = 8th, etc.
                    day = (week_num - 1) * 7 + 1
                    
                    # Ensure day doesn't exceed month days
                    max_days = calendar.monthrange(year, month)[1]
                    if day > max_days:
                        continue
                    
                    attendance_date = f"{year}-{month:02d}-{day:02d}"
                    
                    # Insert or update attendance
                    self.db.execute_query("""
                        INSERT OR REPLACE INTO attendance 
                        (student_id, class_id, attendance_date, month_year, week_number, present)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (student_id, class_id, attendance_date, month_year, week_num, present))
            
            messagebox.showinfo("Success", "Attendance saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save attendance: {str(e)}")
    
    # Fee Management Methods
    def load_eligible_fees(self):
        """Load eligible students for fee collection"""
        month_year = self.fees_month_var.get().strip()
        
        if not month_year:
            messagebox.showerror("Error", "Please enter month/year")
            return
        
        # Clear existing items
        for item in self.fees_tree.get_children():
            self.fees_tree.delete(item)
        
        # Get eligible students (attendance >= 2 and not free participants)
        query = """
        SELECT s.student_id, s.student_name, c.class_id, c.class_name, c.monthly_fee,
               COUNT(a.id) as attendance_count,
               CASE WHEN fc.id IS NOT NULL THEN 'Collected' ELSE 'Pending' END as status
        FROM students s
        JOIN student_classes sc ON s.student_id = sc.student_id
        JOIN classes c ON sc.class_id = c.class_id
        LEFT JOIN attendance a ON s.student_id = a.student_id AND c.class_id = a.class_id 
                                 AND a.month_year = ? AND a.present = 1
        LEFT JOIN fee_collections fc ON s.student_id = fc.student_id AND c.class_id = fc.class_id 
                                       AND fc.month_year = ?
        WHERE s.is_free_participant = 0
        GROUP BY s.student_id, s.student_name, c.class_id, c.class_name, c.monthly_fee
        HAVING attendance_count >= 2
        ORDER BY s.student_name, c.class_name
        """
        
        eligible = self.db.execute_query(query, (month_year, month_year))
        
        for record in eligible:
            student_name = record[1]
            class_name = record[3]
            attendance_count = record[5]
            fee_amount = f"${record[4]:.2f}"
            status = record[6]
            
            self.fees_tree.insert('', 'end', values=(
                student_name, class_name, attendance_count, fee_amount, status
            ), tags=(record[0], record[2]))  # Store IDs in tags
    
    def collect_individual_fee(self, event):
        """Collect fee for double-clicked student"""
        selected = self.fees_tree.selection()
        if not selected:
            return
        
        item = self.fees_tree.item(selected[0])
        values = item['values']
        tags = item['tags']
        
        if values[4] == 'Collected':
            messagebox.showinfo("Info", "Fee already collected for this student")
            return
        
        student_id = tags[0]
        class_id = tags[1]
        month_year = self.fees_month_var.get().strip()
        fee_amount = float(values[3].replace(', ''))
        attendance_count = values[2]
        
        if messagebox.askyesno("Confirm", f"Collect fee of ${fee_amount:.2f} from {values[0]}?"):
            try:
                self.db.execute_query("""
                    INSERT INTO fee_collections (student_id, class_id, month_year, fee_amount, attendance_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (student_id, class_id, month_year, fee_amount, attendance_count))
                
                messagebox.showinfo("Success", "Fee collected successfully")
                self.load_eligible_fees()  # Refresh the list
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Fee already collected for this student")
    
    def collect_all_fees(self):
        """Collect all eligible fees"""
        month_year = self.fees_month_var.get().strip()
        
        if not month_year:
            messagebox.showerror("Error", "Please enter month/year")
            return
        
        # Get all pending eligible fees
        query = """
        SELECT s.student_id, c.class_id, c.monthly_fee, COUNT(a.id) as attendance_count
        FROM students s
        JOIN student_classes sc ON s.student_id = sc.student_id
        JOIN classes c ON sc.class_id = c.class_id
        LEFT JOIN attendance a ON s.student_id = a.student_id AND c.class_id = a.class_id 
                                 AND a.month_year = ? AND a.present = 1
        LEFT JOIN fee_collections fc ON s.student_id = fc.student_id AND c.class_id = fc.class_id 
                                       AND fc.month_year = ?
        WHERE s.is_free_participant = 0 AND fc.id IS NULL
        GROUP BY s.student_id, c.class_id, c.monthly_fee
        HAVING attendance_count >= 2
        """
        
        eligible = self.db.execute_query(query, (month_year, month_year))
        
        if not eligible:
            messagebox.showinfo("Info", "No pending fees to collect")
            return
        
        if messagebox.askyesno("Confirm", f"Collect fees for {len(eligible)} eligible students?"):
            try:
                for record in eligible:
                    student_id, class_id, fee_amount, attendance_count = record
                    self.db.execute_query("""
                        INSERT INTO fee_collections (student_id, class_id, month_year, fee_amount, attendance_count)
                        VALUES (?, ?, ?, ?, ?)
                    """, (student_id, class_id, month_year, fee_amount, attendance_count))
                
                messagebox.showinfo("Success", f"Collected fees for {len(eligible)} students")
                self.load_eligible_fees()  # Refresh the list
            except Exception as e:
                messagebox.showerror("Error", f"Failed to collect fees: {str(e)}")
    
    # Payment Management Methods
    def record_payment(self):
        """Record a payment to teacher"""
        teacher_selection = self.payment_teacher_var.get()
        amount = self.payment_amount_var.get().strip()
        payment_date = self.payment_date_var.get().strip()
        month_year = self.payment_month_var.get().strip()
        notes = self.payment_notes_var.get().strip()
        
        if not teacher_selection or not amount or not payment_date:
            messagebox.showerror("Error", "Please fill in required fields")
            return
        
        try:
            teacher_id = teacher_selection.split(' - ')[0]
            payment_amount = float(amount)
            
            self.db.execute_query("""
                INSERT INTO teacher_payments (teacher_id, payment_amount, payment_date, month_year, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (teacher_id, payment_amount, payment_date, month_year or None, notes or None))
            
            messagebox.showinfo("Success", "Payment recorded successfully")
            self.clear_payment_form()
            self.load_payments()
            self.update_balance_summary()
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Please enter valid amount and select teacher")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record payment: {str(e)}")
    
    def clear_payment_form(self):
        """Clear payment form"""
        self.payment_teacher_var.set("")
        self.payment_amount_var.set("")
        self.payment_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.payment_month_var.set("")
        self.payment_notes_var.set("")
    
    def load_payments(self):
        """Load payment history"""
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)
        
        query = """
        SELECT tp.payment_date, t.teacher_name, tp.payment_amount, tp.month_year, tp.notes
        FROM teacher_payments tp
        JOIN teachers t ON tp.teacher_id = t.teacher_id
        ORDER BY tp.payment_date DESC
        """
        
        payments = self.db.execute_query(query)
        for payment in payments:
            month_year = payment[3] if payment[3] else "-"
            notes = payment[4] if payment[4] else "-"
            self.payments_tree.insert('', 'end', values=(
                payment[0], payment[1], f"${payment[2]:.2f}", month_year, notes
            ))
    
    def update_balance_summary(self):
        """Update teacher balance summary"""
        self.balance_text.config(state='normal')
        self.balance_text.delete(1.0, tk.END)
        
        # Get teacher balances
        query = """
        SELECT t.teacher_id, t.teacher_name,
               COALESCE(SUM(fc.fee_amount * 0.8), 0) as total_earned,
               COALESCE(SUM(tp.payment_amount), 0) as total_paid,
               COALESCE(SUM(fc.fee_amount * 0.8), 0) - COALESCE(SUM(tp.payment_amount), 0) as balance
        FROM teachers t
        LEFT JOIN classes c ON t.teacher_id = c.teacher_id
        LEFT JOIN fee_collections fc ON c.class_id = fc.class_id
        LEFT JOIN teacher_payments tp ON t.teacher_id = tp.teacher_id
        GROUP BY t.teacher_id, t.teacher_name
        ORDER BY t.teacher_name
        """
        
        balances = self.db.execute_query(query)
        
        self.balance_text.insert(tk.END, "Teacher Balance Summary\n")
        self.balance_text.insert(tk.END, "=" * 30 + "\n\n")
        
        for balance in balances:
            teacher_name = balance[1]
            earned = balance[2]
            paid = balance[3]
            balance_amount = balance[4]
            
            status = "BALANCE DUE" if balance_amount > 0 else "OVERPAID" if balance_amount < 0 else "SETTLED"
            
            self.balance_text.insert(tk.END, f"{teacher_name}:\n")
            self.balance_text.insert(tk.END, f"  Earned: ${earned:.2f}\n")
            self.balance_text.insert(tk.END, f"  Paid: ${paid:.2f}\n")
            self.balance_text.insert(tk.END, f"  Balance: ${balance_amount:.2f} ({status})\n\n")
        
        self.balance_text.config(state='disabled')
    
    # Dashboard Methods
    def show_dashboard(self):
        """Show dashboard with summary statistics"""
        # Clear existing dashboard
        for widget in self.dashboard_content.winfo_children():
            widget.destroy()
        
        # Title
        title_label = ttk.Label(self.dashboard_content, text="Student Management System Dashboard", 
                               font=('TkDefaultFont', 16, 'bold'))
        title_label.pack(pady=20)
        
        # Current month stats
        current_month = datetime.now().strftime("%Y-%m")
        self.create_monthly_dashboard(current_month)
    
    def create_monthly_dashboard(self, month_year):
        """Create dashboard for specific month"""
        # Month header
        month_frame = ttk.LabelFrame(self.dashboard_content, text=f"Summary for {month_year}", padding="10")
        month_frame.pack(fill='x', padx=20, pady=10)
        
        # Get statistics
        stats = self.get_monthly_statistics(month_year)
        
        # Create stats grid
        stats_frame = ttk.Frame(month_frame)
        stats_frame.pack(fill='x')
        
        # Row 1: Basic counts
        ttk.Label(stats_frame, text="Total Students:", font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Label(stats_frame, text=str(stats['total_students'])).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(stats_frame, text="Total Classes:", font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=2, sticky='w', padx=5, pady=5)
        ttk.Label(stats_frame, text=str(stats['total_classes'])).grid(row=0, column=3, sticky='w', padx=5, pady=5)
        
        # Row 2: Financial summary
        ttk.Label(stats_frame, text="Total Fees Collected:", font=('TkDefaultFont', 10, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        ttk.Label(stats_frame, text=f"${stats['total_fees']:.2f}").grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(stats_frame, text="Institute Share (20%):", font=('TkDefaultFont', 10, 'bold')).grid(row=1, column=2, sticky='w', padx=5, pady=5)
        ttk.Label(stats_frame, text=f"${stats['institute_share']:.2f}").grid(row=1, column=3, sticky='w', padx=5, pady=5)
        
        # Row 3: Teacher payments
        ttk.Label(stats_frame, text="Teacher Share (80%):", font=('TkDefaultFont', 10, 'bold')).grid(row=2, column=0, sticky='w', padx=5, pady=5)
        ttk.Label(stats_frame, text=f"${stats['teacher_share']:.2f}").grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(stats_frame, text="Payments Made:", font=('TkDefaultFont', 10, 'bold')).grid(row=2, column=2, sticky='w', padx=5, pady=5)
        ttk.Label(stats_frame, text=f"${stats['payments_made']:.2f}").grid(row=2, column=3, sticky='w', padx=5, pady=5)
        
        # Teacher breakdown
        teacher_frame = ttk.LabelFrame(self.dashboard_content, text="Teacher Summary", padding="10")
        teacher_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Teacher summary treeview
        teacher_tree = ttk.Treeview(teacher_frame, columns=('Teacher', 'Classes', 'Earned', 'Paid', 'Balance'), show='headings', height=8)
        teacher_tree.heading('Teacher', text='Teacher')
        teacher_tree.heading('Classes', text='Classes')
        teacher_tree.heading('Earned', text='Earned (80%)')
        teacher_tree.heading('Paid', text='Paid')
        teacher_tree.heading('Balance', text='Balance')
        
        teacher_tree.column('Teacher', width=150)
        teacher_tree.column('Classes', width=100)
        teacher_tree.column('Earned', width=100)
        teacher_tree.column('Paid', width=100)
        teacher_tree.column('Balance', width=100)
        
        teacher_tree.pack(fill='both', expand=True)
        
        # Load teacher data
        teacher_data = self.get_teacher_summary(month_year)
        for teacher in teacher_data:
            balance = teacher[4]
            # Color code based on balance
            tags = ('positive',) if balance > 0 else ('negative',) if balance < 0 else ('zero',)
            teacher_tree.insert('', 'end', values=teacher, tags=tags)
        
        # Configure tags for colors
        teacher_tree.tag_configure('positive', background='#ffcccc')  # Light red for money owed
        teacher_tree.tag_configure('negative', background='#ccffcc')  # Light green for overpaid
        teacher_tree.tag_configure('zero', background='white')       # White for settled
    
    def get_monthly_statistics(self, month_year):
        """Get monthly statistics"""
        stats = {}
        
        # Total students and classes
        stats['total_students'] = self.db.execute_query("SELECT COUNT(*) FROM students")[0][0]
        stats['total_classes'] = self.db.execute_query("SELECT COUNT(*) FROM classes")[0][0]
        
        # Financial data for the month
        financial_data = self.db.execute_query("""
            SELECT COALESCE(SUM(fee_amount), 0) as total_fees
            FROM fee_collections 
            WHERE month_year = ?
        """, (month_year,))
        
        total_fees = financial_data[0][0] if financial_data else 0
        stats['total_fees'] = total_fees
        stats['teacher_share'] = total_fees * 0.8
        stats['institute_share'] = total_fees * 0.2
        
        # Payments made in the month
        payments_data = self.db.execute_query("""
            SELECT COALESCE(SUM(payment_amount), 0) 
            FROM teacher_payments 
            WHERE payment_date LIKE ?
        """, (f"{month_year}%",))
        
        stats['payments_made'] = payments_data[0][0] if payments_data else 0
        
        return stats
    
    def get_teacher_summary(self, month_year=None):
        """Get teacher summary data"""
        if month_year:
            query = """
            SELECT t.teacher_name,
                   COUNT(DISTINCT c.class_id) as class_count,
                   COALESCE(SUM(fc.fee_amount * 0.8), 0) as earned,
                   COALESCE(SUM(tp.payment_amount), 0) as paid,
                   COALESCE(SUM(fc.fee_amount * 0.8), 0) - COALESCE(SUM(tp.payment_amount), 0) as balance
            FROM teachers t
            LEFT JOIN classes c ON t.teacher_id = c.teacher_id
            LEFT JOIN fee_collections fc ON c.class_id = fc.class_id AND fc.month_year = ?
            LEFT JOIN teacher_payments tp ON t.teacher_id = tp.teacher_id AND tp.month_year = ?
            GROUP BY t.teacher_id, t.teacher_name
            ORDER BY t.teacher_name
            """
            return self.db.execute_query(query, (month_year, month_year))
        else:
            query = """
            SELECT t.teacher_name,
                   COUNT(DISTINCT c.class_id) as class_count,
                   COALESCE(SUM(fc.fee_amount * 0.8), 0) as earned,
                   COALESCE(SUM(tp.payment_amount), 0) as paid,
                   COALESCE(SUM(fc.fee_amount * 0.8), 0) - COALESCE(SUM(tp.payment_amount), 0) as balance
            FROM teachers t
            LEFT JOIN classes c ON t.teacher_id = c.teacher_id
            LEFT JOIN fee_collections fc ON c.class_id = fc.class_id
            LEFT JOIN teacher_payments tp ON t.teacher_id = tp.teacher_id
            GROUP BY t.teacher_id, t.teacher_name
            ORDER BY t.teacher_name
            """
            return self.db.execute_query(query)
    
    # Reports Methods
    def generate_monthly_summary(self):
        """Generate monthly summary report"""
        month_year = self.report_month_var.get().strip()
        
        if not month_year:
            messagebox.showerror("Error", "Please enter month/year")
            return
        
        self.reports_text.config(state='normal')
        self.reports_text.delete(1.0, tk.END)
        
        # Header
        self.reports_text.insert(tk.END, f"MONTHLY SUMMARY REPORT - {month_year}\n")
        self.reports_text.insert(tk.END, "=" * 50 + "\n\n")
        
        # Get statistics
        stats = self.get_monthly_statistics(month_year)
        
        # Basic statistics
        self.reports_text.insert(tk.END, "OVERVIEW\n")
        self.reports_text.insert(tk.END, "-" * 20 + "\n")
        self.reports_text.insert(tk.END, f"Total Students: {stats['total_students']}\n")
        self.reports_text.insert(tk.END, f"Total Classes: {stats['total_classes']}\n")
        self.reports_text.insert(tk.END, f"Total Fees Collected: ${stats['total_fees']:.2f}\n")
        self.reports_text.insert(tk.END, f"Institute Share (20%): ${stats['institute_share']:.2f}\n")
        self.reports_text.insert(tk.END, f"Teacher Share (80%): ${stats['teacher_share']:.2f}\n")
        self.reports_text.insert(tk.END, f"Payments Made: ${stats['payments_made']:.2f}\n\n")
        
        # Teacher breakdown
        self.reports_text.insert(tk.END, "TEACHER BREAKDOWN\n")
        self.reports_text.insert(tk.END, "-" * 20 + "\n")
        
        teacher_data = self.get_teacher_summary(month_year)
        for teacher in teacher_data:
            name, classes, earned, paid, balance = teacher
            self.reports_text.insert(tk.END, f"Teacher: {name}\n")
            self.reports_text.insert(tk.END, f"  Classes: {classes}\n")
            self.reports_text.insert(tk.END, f"  Earned: ${earned:.2f}\n")
            self.reports_text.insert(tk.END, f"  Paid: ${paid:.2f}\n")
            self.reports_text.insert(tk.END, f"  Balance: ${balance:.2f}\n\n")
        
        self.reports_text.config(state='disabled')
    
    def generate_teacher_report(self):
        """Generate detailed teacher financial report"""
        month_year = self.report_month_var.get().strip()
        
        if not month_year:
            messagebox.showerror("Error", "Please enter month/year")
            return
        
        self.reports_text.config(state='normal')
        self.reports_text.delete(1.0, tk.END)
        
        # Header
        self.reports_text.insert(tk.END, f"TEACHER FINANCIAL REPORT - {month_year}\n")
        self.reports_text.insert(tk.END, "=" * 60 + "\n\n")
        
        # Detailed teacher report
        query = """
        SELECT t.teacher_name, c.class_name,
               COUNT(fc.student_id) as paying_students,
               SUM(fc.fee_amount) as total_collected,
               SUM(fc.fee_amount * 0.8) as teacher_share,
               SUM(fc.fee_amount * 0.2) as institute_share
        FROM teachers t
        JOIN classes c ON t.teacher_id = c.teacher_id
        LEFT JOIN fee_collections fc ON c.class_id = fc.class_id AND fc.month_year = ?
        GROUP BY t.teacher_id, t.teacher_name, c.class_id, c.class_name
        ORDER BY t.teacher_name, c.class_name
        """
        
        report_data = self.db.execute_query(query, (month_year,))
        
        current_teacher = None
        teacher_total = 0
        
        for record in report_data:
            teacher_name, class_name, students, total, teacher_share, institute_share = record
            
            if current_teacher != teacher_name:
                if current_teacher is not None:
                    self.reports_text.insert(tk.END, f"  TEACHER TOTAL: ${teacher_total:.2f}\n\n")
                
                current_teacher = teacher_name
                teacher_total = 0
                self.reports_text.insert(tk.END, f"TEACHER: {teacher_name}\n")
                self.reports_text.insert(tk.END, "-" * 40 + "\n")
            
            teacher_total += teacher_share or 0
            
            self.reports_text.insert(tk.END, f"  Class: {class_name}\n")
            self.reports_text.insert(tk.END, f"    Paying Students: {students or 0}\n")
            self.reports_text.insert(tk.END, f"    Total Collected: ${total or 0:.2f}\n")
            self.reports_text.insert(tk.END, f"    Teacher Share (80%): ${teacher_share or 0:.2f}\n")
            self.reports_text.insert(tk.END, f"    Institute Share (20%): ${institute_share or 0:.2f}\n\n")
        
        if current_teacher is not None:
            self.reports_text.insert(tk.END, f"  TEACHER TOTAL: ${teacher_total:.2f}\n\n")
        
        self.reports_text.config(state='disabled')
    
    def export_to_csv(self):
        """Export current report to CSV"""
        content = self.reports_text.get(1.0, tk.END).strip()
        
        if not content:
            messagebox.showerror("Error", "Please generate a report first")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Report As"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Report exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {str(e)}")

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = StudentManagementApp(root)
    
    # Set window icon and properties
    try:
        root.iconbitmap('school.ico')  # Add if you have an icon file
    except:
        pass  # Ignore if icon file doesn't exist
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()