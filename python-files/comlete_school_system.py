import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import hashlib
import os
import json
import datetime
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io
import base64
import shutil
from datetime import datetime, date

class SchoolManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Complete School Management System")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e3a5f')
        
        # Current user
        self.current_user = None
        self.user_role = None
        
        # Create database directory
        self.create_directories()
        
        # Initialize database
        self.init_database()
        
        # Show login screen first
        self.show_login_screen()

    def create_directories(self):
        directories = [
            'school_data',
            'school_data/student_photos',
            'school_data/id_cards', 
            'school_data/reports',
            'school_data/backups',
            'school_data/exports'
        ]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def init_database(self):
        self.conn = sqlite3.connect('school_data/school_management.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Enable foreign keys
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create all tables
        self.create_tables()
        self.insert_default_data()
        self.conn.commit()

    def create_tables(self):
        tables = [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                role TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_date TEXT,
                last_login TEXT
            )
            """,
            
            # Guardians table
            """
            CREATE TABLE IF NOT EXISTS guardians (
                guardian_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                relationship TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                occupation TEXT,
                created_date TEXT
            )
            """,
            
            # Teachers table
            """
            CREATE TABLE IF NOT EXISTS teachers (
                teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                gender TEXT,
                date_of_birth TEXT,
                hire_date TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                qualification TEXT,
                subject_specialization TEXT,
                role TEXT DEFAULT 'teacher',
                salary REAL DEFAULT 0,
                photo BLOB,
                status TEXT DEFAULT 'active',
                created_date TEXT
            )
            """,
            
            # Classes table
            """
            CREATE TABLE IF NOT EXISTS classes (
                class_id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT NOT NULL,
                section TEXT,
                teacher_id INTEGER,
                capacity INTEGER,
                room_number TEXT,
                created_date TEXT
            )
            """,
            
            # Subjects table
            """
            CREATE TABLE IF NOT EXISTS subjects (
                subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT NOT NULL,
                subject_code TEXT UNIQUE,
                description TEXT,
                teacher_id INTEGER,
                class_id INTEGER,
                created_date TEXT
            )
            """,
            
            # Students table
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                gender TEXT,
                date_of_birth TEXT,
                admission_no TEXT UNIQUE,
                class_id INTEGER,
                address TEXT,
                phone TEXT,
                email TEXT,
                guardian_id INTEGER,
                enrollment_date TEXT,
                status TEXT DEFAULT 'active',
                photo BLOB,
                blood_group TEXT,
                medical_info TEXT,
                created_date TEXT
            )
            """,
            
            # Exams table
            """
            CREATE TABLE IF NOT EXISTS exams (
                exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_name TEXT NOT NULL,
                term TEXT,
                academic_year TEXT,
                start_date TEXT,
                end_date TEXT,
                total_marks REAL,
                passing_marks REAL,
                description TEXT,
                created_date TEXT
            )
            """,
            
            # Results table
            """
            CREATE TABLE IF NOT EXISTS results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                subject_id INTEGER,
                exam_id INTEGER,
                marks_obtained REAL,
                grade TEXT,
                remarks TEXT,
                created_date TEXT
            )
            """,
            
            # Attendance table
            """
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                class_id INTEGER,
                date TEXT,
                status TEXT,
                remarks TEXT,
                created_date TEXT
            )
            """,
            
            # Fees table
            """
            CREATE TABLE IF NOT EXISTS fees (
                fee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                amount REAL,
                fee_type TEXT,
                due_date TEXT,
                payment_status TEXT DEFAULT 'Pending',
                payment_date TEXT,
                receipt_no TEXT,
                academic_year TEXT,
                term TEXT,
                created_date TEXT
            )
            """,
            
            # Library books table
            """
            CREATE TABLE IF NOT EXISTS library_books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                isbn TEXT UNIQUE,
                publisher TEXT,
                category TEXT,
                quantity INTEGER DEFAULT 1,
                available_copies INTEGER DEFAULT 1,
                price REAL,
                location TEXT,
                description TEXT,
                created_date TEXT
            )
            """,
            
            # Library transactions table
            """
            CREATE TABLE IF NOT EXISTS library_transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                student_id INTEGER,
                teacher_id INTEGER,
                issue_date TEXT,
                due_date TEXT,
                return_date TEXT,
                status TEXT DEFAULT 'issued',
                fine_amount REAL DEFAULT 0,
                remarks TEXT,
                created_date TEXT
            )
            """,
            
            # Timetable table
            """
            CREATE TABLE IF NOT EXISTS timetable (
                timetable_id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER,
                subject_id INTEGER,
                teacher_id INTEGER,
                day_of_week TEXT,
                start_time TEXT,
                end_time TEXT,
                room TEXT,
                created_date TEXT
            )
            """,
            
            # Events table
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                description TEXT,
                event_date TEXT,
                venue TEXT,
                organizer TEXT,
                event_type TEXT,
                created_date TEXT
            )
            """,
            
            # Hostels table
            """
            CREATE TABLE IF NOT EXISTS hostels (
                hostel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostel_name TEXT NOT NULL,
                capacity INTEGER,
                warden_id INTEGER,
                address TEXT,
                phone TEXT,
                created_date TEXT
            )
            """,
            
            # Hostel allocations table
            """
            CREATE TABLE IF NOT EXISTS hostel_allocations (
                allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostel_id INTEGER,
                student_id INTEGER,
                room_no TEXT,
                bed_no TEXT,
                date_allocated TEXT,
                date_vacated TEXT,
                status TEXT DEFAULT 'active',
                created_date TEXT
            )
            """,
            
            # Transport table
            """
            CREATE TABLE IF NOT EXISTS transport (
                bus_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bus_number TEXT UNIQUE,
                driver_name TEXT,
                driver_phone TEXT,
                route TEXT,
                capacity INTEGER,
                fare REAL,
                created_date TEXT
            )
            """,
            
            # Transport allocations table
            """
            CREATE TABLE IF NOT EXISTS transport_allocations (
                allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                bus_id INTEGER,
                pickup_point TEXT,
                drop_point TEXT,
                pickup_time TEXT,
                status TEXT DEFAULT 'active',
                created_date TEXT
            )
            """,
            
            # Inventory table
            """
            CREATE TABLE IF NOT EXISTS inventory (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER,
                unit_price REAL,
                total_value REAL,
                supplier TEXT,
                purchase_date TEXT,
                location TEXT,
                description TEXT,
                created_date TEXT
            )
            """,
            
            # Notices table
            """
            CREATE TABLE IF NOT EXISTS notices (
                notice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                target_audience TEXT,
                publish_date TEXT,
                expiry_date TEXT,
                priority TEXT DEFAULT 'normal',
                created_date TEXT
            )
            """,
            
            # Settings table
            """
            CREATE TABLE IF NOT EXISTS settings (
                setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE,
                setting_value TEXT,
                description TEXT,
                updated_date TEXT
            )
            """
        ]
        
        for table in tables:
            try:
                self.cursor.execute(table)
            except Exception as e:
                print(f"Error creating table: {e}")

    def insert_default_data(self):
        # Insert default admin user
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if self.cursor.fetchone()[0] == 0:
            hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
            current_date = datetime.now().isoformat()
            self.cursor.execute(
                """INSERT INTO users (username, password, email, role, created_date) 
                VALUES (?, ?, ?, ?, ?)""",
                ('admin', hashed_password, 'admin@school.com', 'admin', current_date)
            )
        
        # Insert sample teachers
        self.cursor.execute("SELECT COUNT(*) FROM teachers")
        if self.cursor.fetchone()[0] == 0:
            current_date = datetime.now().isoformat()
            teachers = [
                ('John', 'Smith', 'Male', '1980-05-15', '2015-08-01', 
                 '555-0101', 'john.smith@school.com', '123 Main St', 'M.Ed', 
                 'Mathematics', 'teacher', 50000, None, 'active', current_date),
                ('Sarah', 'Johnson', 'Female', '1985-08-20', '2018-03-15',
                 '555-0102', 'sarah.johnson@school.com', '456 Oak Ave', 'Ph.D',
                 'Science', 'teacher', 55000, None, 'active', current_date),
                ('Michael', 'Brown', 'Male', '1975-12-10', '2010-01-15',
                 '555-0103', 'michael.brown@school.com', '789 Pine St', 'M.A',
                 'English', 'teacher', 52000, None, 'active', current_date)
            ]
            self.cursor.executemany(
                """INSERT INTO teachers (first_name, last_name, gender, date_of_birth, 
                hire_date, phone, email, address, qualification, subject_specialization, 
                role, salary, photo, status, created_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                teachers
            )
        
        # Insert sample classes
        self.cursor.execute("SELECT COUNT(*) FROM classes")
        if self.cursor.fetchone()[0] == 0:
            current_date = datetime.now().isoformat()
            classes = [
                ('JSS1', 'A', 1, 30, 'Room 101', current_date),
                ('JSS1', 'B', 2, 30, 'Room 102', current_date),
                ('JSS2', 'A', 1, 30, 'Room 201', current_date),
                ('JSS2', 'B', 3, 30, 'Room 202', current_date),
                ('SS1', 'Science', 2, 25, 'Room 301', current_date),
                ('SS1', 'Arts', 1, 25, 'Room 302', current_date),
                ('SS2', 'Science', 2, 25, 'Room 401', current_date),
                ('SS2', 'Arts', 3, 25, 'Room 402', current_date)
            ]
            self.cursor.executemany(
                """INSERT INTO classes (class_name, section, teacher_id, capacity, 
                room_number, created_date) VALUES (?, ?, ?, ?, ?, ?)""",
                classes
            )
        
        # Insert sample subjects
        self.cursor.execute("SELECT COUNT(*) FROM subjects")
        if self.cursor.fetchone()[0] == 0:
            current_date = datetime.now().isoformat()
            subjects = [
                ('Mathematics', 'MATH01', 'Core mathematics curriculum', 1, 1, current_date),
                ('English Language', 'ENG01', 'English language and literature', 3, 1, current_date),
                ('Basic Science', 'SCI01', 'Fundamental science concepts', 2, 1, current_date),
                ('Social Studies', 'SOC01', 'History and social sciences', 1, 2, current_date),
                ('Physics', 'PHY01', 'Advanced physics', 2, 5, current_date),
                ('Chemistry', 'CHEM01', 'Advanced chemistry', 2, 5, current_date),
                ('Biology', 'BIO01', 'Advanced biology', 2, 5, current_date),
                ('Literature', 'LIT01', 'English literature', 3, 6, current_date)
            ]
            self.cursor.executemany(
                """INSERT INTO subjects (subject_name, subject_code, description, teacher_id, class_id, created_date) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                subjects
            )
        
        # Insert default settings
        self.cursor.execute("SELECT COUNT(*) FROM settings")
        if self.cursor.fetchone()[0] == 0:
            current_date = datetime.now().isoformat()
            settings = [
                ('school_name', 'Excel Academy', 'School Name', current_date),
                ('school_address', '123 Education Street, City', 'School Address', current_date),
                ('school_phone', '+1-555-0123', 'School Phone', current_date),
                ('school_email', 'info@excelacademy.edu', 'School Email', current_date),
                ('academic_year', '2024-2025', 'Current Academic Year', current_date),
                ('currency', '$', 'Currency Symbol', current_date)
            ]
            self.cursor.executemany(
                """INSERT INTO settings (setting_key, setting_value, description, updated_date) 
                VALUES (?, ?, ?, ?)""",
                settings
            )

    def show_login_screen(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Login frame
        login_frame = tk.Frame(self.root, bg='#1e3a5f')
        login_frame.pack(expand=True, fill='both')
        
        # Login form
        form_frame = tk.Frame(login_frame, bg='white', padx=40, pady=40, relief='raised', bd=2)
        form_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title
        title_label = tk.Label(form_frame, text="🎓 School Management System", 
                              font=('Arial', 20, 'bold'), bg='white', fg='#1e3a5f')
        title_label.pack(pady=20)
        
        # Username
        tk.Label(form_frame, text="Username:", font=('Arial', 12), bg='white').pack(anchor='w', pady=(20,5))
        username_entry = tk.Entry(form_frame, font=('Arial', 12), width=25)
        username_entry.pack(pady=5)
        username_entry.focus()
        
        # Password
        tk.Label(form_frame, text="Password:", font=('Arial', 12), bg='white').pack(anchor='w', pady=(10,5))
        password_entry = tk.Entry(form_frame, font=('Arial', 12), width=25, show='*')
        password_entry.pack(pady=5)
        
        # Login button
        def login():
            username = username_entry.get()
            password = password_entry.get()
            if self.authenticate_user(username, password):
                self.current_user = username
                self.user_role = self.get_user_role(username)
                self.show_main_interface()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
        
        login_btn = tk.Button(form_frame, text="Login", font=('Arial', 12, 'bold'),
                             bg='#1e3a5f', fg='white', padx=30, pady=10, command=login)
        login_btn.pack(pady=20)
        
        # Default credentials
        default_label = tk.Label(form_frame, text="Default: admin / admin123", 
                                font=('Arial', 10), bg='white', fg='gray')
        default_label.pack(pady=10)
        
        # Bind Enter key to login
        password_entry.bind('<Return>', lambda e: login())

    def authenticate_user(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute(
            "SELECT user_id FROM users WHERE username = ? AND password = ? AND status = 'active'",
            (username, hashed_password)
        )
        result = self.cursor.fetchone()
        if result:
            # Update last login
            self.cursor.execute(
                "UPDATE users SET last_login = ? WHERE username = ?",
                (datetime.now().isoformat(), username)
            )
            self.conn.commit()
            return True
        return False

    def get_user_role(self, username):
        self.cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def show_main_interface(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Configure styles
        self.setup_styles()
        
        # Header
        header_frame = tk.Frame(self.root, bg='#1e3a5f', height=80)
        header_frame.pack(fill='x', padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        # Header content
        header_left = tk.Frame(header_frame, bg='#1e3a5f')
        header_left.pack(side='left', padx=20)
        
        title_label = tk.Label(header_left, 
                              text="🎓 Complete School Management System",
                              font=('Arial', 20, 'bold'),
                              fg='white',
                              bg='#1e3a5f')
        title_label.pack(pady=20)
        
        # User info
        header_right = tk.Frame(header_frame, bg='#1e3a5f')
        header_right.pack(side='right', padx=20)
        
        user_label = tk.Label(header_right,
                             text=f"Welcome, {self.current_user} ({self.user_role})",
                             font=('Arial', 12),
                             fg='white',
                             bg='#1e3a5f')
        user_label.pack(pady=5)
        
        logout_btn = tk.Button(header_right,
                              text="Logout",
                              font=('Arial', 10),
                              bg='#e74c3c',
                              fg='white',
                              command=self.logout)
        logout_btn.pack(pady=5)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#ecf0f1')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Navigation frame
        self.nav_frame = tk.Frame(main_container, bg='#2c3e50', width=250)
        self.nav_frame.pack(side='left', fill='y', padx=(0, 10))
        self.nav_frame.pack_propagate(False)
        
        # Content frame
        self.content_frame = tk.Frame(main_container, bg='white')
        self.content_frame.pack(side='left', fill='both', expand=True)
        
        # Create navigation
        self.create_navigation()
        
        # Show dashboard
        self.show_dashboard()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.colors = {
            'primary': '#3498db',
            'secondary': '#2c3e50',
            'success': '#27ae60',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'info': '#1abc9c',
            'light': '#ecf0f1',
            'dark': '#34495e'
        }

    def create_navigation(self):
        # Navigation menu items based on user role
        nav_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("👨‍🎓 Students", self.show_students),
            ("👨‍🏫 Teachers", self.show_teachers),
            ("🏫 Classes", self.show_classes),
            ("📖 Subjects", self.show_subjects),
            ("📝 Exams", self.show_exams),
            ("📈 Results", self.show_results),
            ("📅 Attendance", self.show_attendance),
            ("💰 Fees", self.show_fees),
            ("📚 Library", self.show_library),
            ("🕒 Timetable", self.show_timetable),
            ("🎯 Events", self.show_events),
            ("🏠 Hostel", self.show_hostel),
            ("🚌 Transport", self.show_transport),
            ("📦 Inventory", self.show_inventory),
            ("📢 Notices", self.show_notices),
            ("🆔 ID Cards", self.show_id_cards),
            ("📋 Reports", self.show_reports),
            ("⚙️ Settings", self.show_settings),
            ("💾 Backup", self.show_backup)
        ]
        
        # Add admin-only items
        if self.user_role in ['admin']:
            nav_items.append(("👥 User Management", self.show_user_management))
        
        for text, command in nav_items:
            btn = tk.Button(self.nav_frame,
                          text=text,
                          font=('Arial', 11),
                          bg='#34495e',
                          fg='white',
                          relief='flat',
                          padx=20,
                          pady=15,
                          anchor='w',
                          command=command)
            btn.pack(fill='x', padx=5, pady=2)
            
            # Hover effects
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg='#3498db'))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg='#34495e'))

    def logout(self):
        self.current_user = None
        self.user_role = None
        self.show_login_screen()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def center_window(self, window, width, height):
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    # ========== DASHBOARD ==========
    def show_dashboard(self):
        self.clear_content()
        
        header = tk.Label(self.content_frame,
                         text="📊 Dashboard",
                         font=('Arial', 24, 'bold'),
                         bg='white',
                         fg='#2c3e50')
        header.pack(pady=20)
        
        # Statistics frame
        stats_frame = tk.Frame(self.content_frame, bg='white')
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        stats = self.get_dashboard_stats()
        stat_cards = [
            ("Total Students", stats['students'], '#3498db', '👨‍🎓'),
            ("Total Teachers", stats['teachers'], '#27ae60', '👨‍🏫'),
            ("Total Classes", stats['classes'], '#e74c3c', '🏫'),
            ("Pending Fees", f"${stats['pending_fees']}", '#f39c12', '💰'),
            ("Library Books", stats['books'], '#9b59b6', '📚'),
            ("Today's Attendance", f"{stats['attendance_today']}%", '#1abc9c', '📅')
        ]
        
        for i, (title, value, color, icon) in enumerate(stat_cards):
            card = self.create_dashboard_card(stats_frame, title, value, color, icon)
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky='nsew')
        
        for i in range(3):
            stats_frame.grid_columnconfigure(i, weight=1)
        
        # Recent activities
        self.show_recent_activities()

    def get_dashboard_stats(self):
        stats = {}
        try:
            # Total students
            self.cursor.execute("SELECT COUNT(*) FROM students WHERE status='active'")
            stats['students'] = self.cursor.fetchone()[0]
            
            # Total teachers
            self.cursor.execute("SELECT COUNT(*) FROM teachers WHERE status='active'")
            stats['teachers'] = self.cursor.fetchone()[0]
            
            # Total classes
            self.cursor.execute("SELECT COUNT(*) FROM classes")
            stats['classes'] = self.cursor.fetchone()[0]
            
            # Pending fees
            self.cursor.execute("SELECT SUM(amount) FROM fees WHERE payment_status='Pending'")
            result = self.cursor.fetchone()[0]
            stats['pending_fees'] = result if result else 0
            
            # Library books
            self.cursor.execute("SELECT COUNT(*) FROM library_books")
            stats['books'] = self.cursor.fetchone()[0]
            
            # Today's attendance
            today = datetime.now().strftime('%Y-%m-%d')
            self.cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = ? AND status = 'Present'", (today,))
            present = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM students WHERE status='active'")
            total = self.cursor.fetchone()[0]
            
            stats['attendance_today'] = round((present / total * 100) if total > 0 else 0, 1)
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            stats = {k: 0 for k in ['students', 'teachers', 'classes', 'pending_fees', 'books', 'attendance_today']}
        
        return stats

    def create_dashboard_card(self, parent, title, value, color, icon):
        card = tk.Frame(parent, bg='white', relief='raised', borderwidth=1)
        
        # Card content
        content_frame = tk.Frame(card, bg='white', padx=20, pady=15)
        content_frame.pack(fill='both', expand=True)
        
        # Icon and value
        top_frame = tk.Frame(content_frame, bg='white')
        top_frame.pack(fill='x')
        
        icon_label = tk.Label(top_frame, text=icon, font=('Arial', 24), bg='white')
        icon_label.pack(side='left')
        
        value_label = tk.Label(top_frame, text=str(value), font=('Arial', 24, 'bold'), 
                              bg='white', fg=color)
        value_label.pack(side='right')
        
        # Title
        title_label = tk.Label(content_frame, text=title, font=('Arial', 12), 
                              bg='white', fg='#7f8c8d')
        title_label.pack(anchor='w', pady=(10, 0))
        
        return card

    def show_recent_activities(self):
        activities_frame = tk.LabelFrame(self.content_frame,
                                       text="Recent Activities",
                                       font=('Arial', 14, 'bold'),
                                       bg='white',
                                       padx=10,
                                       pady=10)
        activities_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create treeview for recent activities
        columns = ('Date', 'Activity', 'User', 'Details')
        tree = ttk.Treeview(activities_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(activities_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        # Sample activities
        sample_activities = [
            (datetime.now().strftime('%Y-%m-%d'), 'New Student Added', 'admin', 'John Doe - JSS1A'),
            (datetime.now().strftime('%Y-%m-%d'), 'Fee Payment', 'accountant', 'Receipt #001 - $500'),
            (datetime.now().strftime('%Y-%m-%d'), 'Book Issued', 'librarian', 'Mathematics Basics to Student #1')
        ]
        
        for activity in sample_activities:
            tree.insert('', tk.END, values=activity)

    # ========== STUDENTS MANAGEMENT ==========
    def show_students(self):
        self.clear_content()
        
        header = tk.Label(self.content_frame,
                         text="👨‍🎓 Student Management",
                         font=('Arial', 24, 'bold'),
                         bg='white',
                         fg='#2c3e50')
        header.pack(pady=20)
        
        # Control frame
        control_frame = tk.Frame(self.content_frame, bg='white')
        control_frame.pack(fill='x', padx=20, pady=10)
        
        # Search
        search_frame = tk.Frame(control_frame, bg='white')
        search_frame.pack(side='left')
        
        tk.Label(search_frame, text="Search:", bg='white').pack(side='left')
        self.student_search_entry = tk.Entry(search_frame, width=30)
        self.student_search_entry.pack(side='left', padx=5)
        tk.Button(search_frame, text="🔍 Search", command=self.search_students).pack(side='left', padx=5)
        
        # Buttons
        btn_frame = tk.Frame(control_frame, bg='white')
        btn_frame.pack(side='right')
        
        buttons = [
            ("➕ Add Student", self.add_student),
            ("✏️ Edit", self.edit_student),
            ("🗑️ Delete", self.delete_student),
            ("🔄 Refresh", self.load_students)
        ]
        
        for text, command in buttons:
            tk.Button(btn_frame, text=text, bg='#3498db', fg='white',
                     font=('Arial', 10), padx=10, pady=5, command=command).pack(side='left', padx=5)
        
        # Students table
        table_frame = tk.Frame(self.content_frame, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Name', 'Admission No', 'Class', 'Gender', 'Phone', 'Status')
        self.students_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.students_tree.heading(col, text=col)
            self.students_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.students_tree.yview)
        self.students_tree.configure(yscrollcommand=scrollbar.set)
        
        self.students_tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        self.load_students()
        self.students_tree.bind('<Double-1>', lambda e: self.edit_student())

    def load_students(self):
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        try:
            self.cursor.execute("""
                SELECT s.student_id, s.first_name || ' ' || s.last_name, s.admission_no,
                       c.class_name || ' ' || c.section, s.gender, s.phone, s.status
                FROM students s
                LEFT JOIN classes c ON s.class_id = c.class_id
                ORDER BY s.student_id
            """)
            
            for row in self.cursor.fetchall():
                self.students_tree.insert('', tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students: {str(e)}")

    def search_students(self):
        search_term = self.student_search_entry.get()
        if not search_term:
            self.load_students()
            return
        
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        try:
            self.cursor.execute("""
                SELECT s.student_id, s.first_name || ' ' || s.last_name, s.admission_no,
                       c.class_name || ' ' || c.section, s.gender, s.phone, s.status
                FROM students s
                LEFT JOIN classes c ON s.class_id = c.class_id
                WHERE s.first_name LIKE ? OR s.last_name LIKE ? OR s.admission_no LIKE ?
            """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            
            for row in self.cursor.fetchall():
                self.students_tree.insert('', tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search students: {str(e)}")

    def add_student(self):
        self.show_student_form()

    def edit_student(self):
        selected = self.students_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a student to edit")
            return
        
        student_id = self.students_tree.item(selected[0])['values'][0]
        self.show_student_form(student_id)

    def show_student_form(self, student_id=None):
        form_window = tk.Toplevel(self.root)
        form_window.title("Student Form" if not student_id else "Edit Student")
        form_window.geometry("500x600")
        form_window.configure(bg='white')
        form_window.transient(self.root)
        form_window.grab_set()
        
        self.center_window(form_window, 500, 600)
        
        # Form content
        header_text = "➕ Add Student" if not student_id else "✏️ Edit Student"
        header = tk.Label(form_window, text=header_text, font=('Arial', 18, 'bold'), bg='white', fg='#2c3e50')
        header.pack(pady=20)
        
        # Form frame
        form_frame = tk.Frame(form_window, bg='white')
        form_frame.pack(fill='both', expand=True, padx=40)
        
        # Form fields
        fields = [
            ("First Name", "entry"),
            ("Last Name", "entry"),
            ("Gender", "combobox", ["Male", "Female", "Other"]),
            ("Date of Birth", "entry"),
            ("Admission No", "entry"),
            ("Class", "combobox", self.get_classes()),
            ("Phone", "entry"),
            ("Email", "entry"),
            ("Address", "text"),
            ("Status", "combobox", ["active", "graduated", "withdrawn"])
        ]
        
        self.student_form_entries = {}
        row = 0
        
        for field in fields:
            label = tk.Label(form_frame, text=field[0] + ":", bg='white', anchor='w')
            label.grid(row=row, column=0, sticky='w', pady=5)
            
            if field[1] == "entry":
                entry = tk.Entry(form_frame, width=30)
                entry.grid(row=row, column=1, sticky='w', pady=5, padx=10)
                self.student_form_entries[field[0].lower().replace(" ", "_")] = entry
                
            elif field[1] == "combobox":
                combo = ttk.Combobox(form_frame, values=field[2], width=27)
                combo.grid(row=row, column=1, sticky='w', pady=5, padx=10)
                self.student_form_entries[field[0].lower().replace(" ", "_")] = combo
                
            elif field[1] == "text":
                text_widget = tk.Text(form_frame, width=30, height=3)
                text_widget.grid(row=row, column=1, sticky='w', pady=5, padx=10)
                self.student_form_entries[field[0].lower().replace(" ", "_")] = text_widget
            
            row += 1
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="💾 Save", bg='#27ae60', fg='white',
                 font=('Arial', 12), padx=20, pady=10,
                 command=lambda: self.save_student(student_id, form_window)).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="❌ Cancel", bg='#e74c3c', fg='white',
                 font=('Arial', 12), padx=20, pady=10,
                 command=form_window.destroy).pack(side='left', padx=10)
        
        # Load data if editing
        if student_id:
            self.load_student_data(student_id)

    def get_classes(self):
        try:
            self.cursor.execute("SELECT class_id, class_name, section FROM classes")
            classes = self.cursor.fetchall()
            return [f"{row[0]} - {row[1]} {row[2]}" for row in classes]
        except:
            return []

    def load_student_data(self, student_id):
        try:
            self.cursor.execute("""
                SELECT first_name, last_name, gender, date_of_birth, admission_no,
                       class_id, phone, email, address, status
                FROM students WHERE student_id = ?
            """, (student_id,))
            
            student_data = self.cursor.fetchone()
            
            if student_data:
                fields = ['first_name', 'last_name', 'gender', 'date_of_birth', 'admission_no',
                         'class', 'phone', 'email', 'address', 'status']
                
                for i, field in enumerate(fields):
                    if field in self.student_form_entries:
                        if field == 'class':
                            value = f"{student_data[5]}" if student_data[5] else ""
                        else:
                            value = student_data[i] if student_data[i] else ""
                        
                        if isinstance(self.student_form_entries[field], tk.Text):
                            self.student_form_entries[field].delete('1.0', tk.END)
                            self.student_form_entries[field].insert('1.0', value)
                        else:
                            self.student_form_entries[field].delete(0, tk.END)
                            self.student_form_entries[field].insert(0, value)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load student data: {str(e)}")

    def save_student(self, student_id, form_window):
        try:
            # Get form data
            data = {}
            for field, widget in self.student_form_entries.items():
                if isinstance(widget, tk.Text):
                    data[field] = widget.get('1.0', tk.END).strip()
                else:
                    data[field] = widget.get().strip()
            
            # Validate required fields
            if not data.get('first_name') or not data.get('last_name'):
                messagebox.showerror("Error", "First name and last name are required")
                return
            
            # Prepare database data
            class_id = data['class'].split(' - ')[0] if data.get('class') else None
            
            student_data = (
                data.get('first_name', ''),
                data.get('last_name', ''),
                data.get('gender', ''),
                data.get('date_of_birth', ''),
                data.get('admission_no', ''),
                class_id,
                data.get('phone', ''),
                data.get('email', ''),
                data.get('address', ''),
                data.get('status', 'active')
            )
            
            if student_id:
                # Update existing student
                self.cursor.execute("""
                    UPDATE students SET first_name=?, last_name=?, gender=?, date_of_birth=?,
                    admission_no=?, class_id=?, phone=?, email=?, address=?, status=?
                    WHERE student_id=?
                """, (*student_data, student_id))
            else:
                # Insert new student
                enrollment_date = datetime.now().strftime("%Y-%m-%d")
                created_date = datetime.now().isoformat()
                self.cursor.execute("""
                    INSERT INTO students (first_name, last_name, gender, date_of_birth,
                    admission_no, class_id, phone, email, address, enrollment_date, status, created_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (*student_data, enrollment_date, created_date))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Student saved successfully!")
            self.load_students()
            form_window.destroy()
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save student: {str(e)}")

    def delete_student(self):
        selected = self.students_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a student to delete")
            return
        
        student_id = self.students_tree.item(selected[0])['values'][0]
        student_name = self.students_tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Confirm", f"Delete {student_name}?"):
            try:
                self.cursor.execute("DELETE FROM students WHERE student_id=?", (student_id,))
                self.conn.commit()
                self.load_students()
                messagebox.showinfo("Success", "Student deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete student: {str(e)}")

    # ========== CLASSES MANAGEMENT ==========
    def show_classes(self):
        self.clear_content()
        
        header = tk.Label(self.content_frame,
                         text="🏫 Class Management",
                         font=('Arial', 24, 'bold'),
                         bg='white',
                         fg='#2c3e50')
        header.pack(pady=20)
        
        # Control frame
        control_frame = tk.Frame(self.content_frame, bg='white')
        control_frame.pack(fill='x', padx=20, pady=10)
        
        # Buttons
        btn_frame = tk.Frame(control_frame, bg='white')
        btn_frame.pack(side='right')
        
        tk.Button(btn_frame, text="➕ Add Class", bg='#3498db', fg='white',
                 font=('Arial', 10), padx=10, pady=5, command=self.add_class).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🔄 Refresh", bg='#27ae60', fg='white',
                 font=('Arial', 10), padx=10, pady=5, command=self.load_classes).pack(side='left', padx=5)
        
        # Classes table
        table_frame = tk.Frame(self.content_frame, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Class Name', 'Section', 'Teacher', 'Capacity', 'Room')
        self.classes_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.classes_tree.heading(col, text=col)
            self.classes_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.classes_tree.yview)
        self.classes_tree.configure(yscrollcommand=scrollbar.set)
        
        self.classes_tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        self.load_classes()
        self.classes_tree.bind('<Double-1>', lambda e: self.edit_class())

    def load_classes(self):
        for item in self.classes_tree.get_children():
            self.classes_tree.delete(item)
        
        try:
            self.cursor.execute("""
                SELECT c.class_id, c.class_name, c.section, 
                       t.first_name || ' ' || t.last_name, c.capacity, c.room_number
                FROM classes c
                LEFT JOIN teachers t ON c.teacher_id = t.teacher_id
                ORDER BY c.class_id
            """)
            
            for row in self.cursor.fetchall():
                self.classes_tree.insert('', tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load classes: {str(e)}")

    def add_class(self):
        self.show_class_form()

    def edit_class(self):
        selected = self.classes_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a class to edit")
            return
        
        class_id = self.classes_tree.item(selected[0])['values'][0]
        self.show_class_form(class_id)

    def show_class_form(self, class_id=None):
        form_window = tk.Toplevel(self.root)
        form_window.title("Class Form" if not class_id else "Edit Class")
        form_window.geometry("400x400")
        form_window.configure(bg='white')
        form_window.transient(self.root)
        form_window.grab_set()
        
        self.center_window(form_window, 400, 400)
        
        header_text = "➕ Add Class" if not class_id else "✏️ Edit Class"
        header = tk.Label(form_window, text=header_text, font=('Arial', 18, 'bold'), bg='white', fg='#2c3e50')
        header.pack(pady=20)
        
        form_frame = tk.Frame(form_window, bg='white')
        form_frame.pack(fill='both', expand=True, padx=40)
        
        # Form fields
        fields = [
            ("Class Name", "entry"),
            ("Section", "entry"),
            ("Teacher", "combobox", self.get_teachers()),
            ("Capacity", "entry"),
            ("Room Number", "entry")
        ]
        
        self.class_form_entries = {}
        row = 0
        
        for field in fields:
            label = tk.Label(form_frame, text=field[0] + ":", bg='white', anchor='w')
            label.grid(row=row, column=0, sticky='w', pady=5)
            
            if field[1] == "entry":
                entry = tk.Entry(form_frame, width=30)
                entry.grid(row=row, column=1, sticky='w', pady=5, padx=10)
                self.class_form_entries[field[0].lower().replace(" ", "_")] = entry
                
            elif field[1] == "combobox":
                combo = ttk.Combobox(form_frame, values=field[2], width=27)
                combo.grid(row=row, column=1, sticky='w', pady=5, padx=10)
                self.class_form_entries[field[0].lower().replace(" ", "_")] = combo
            
            row += 1
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="💾 Save", bg='#27ae60', fg='white',
                 font=('Arial', 12), padx=20, pady=10,
                 command=lambda: self.save_class(class_id, form_window)).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="❌ Cancel", bg='#e74c3c', fg='white',
                 font=('Arial', 12), padx=20, pady=10,
                 command=form_window.destroy).pack(side='left', padx=10)
        
        # Load data if editing
        if class_id:
            self.load_class_data(class_id)

    def get_teachers(self):
        try:
            self.cursor.execute("SELECT teacher_id, first_name, last_name FROM teachers")
            teachers = self.cursor.fetchall()
            return [f"{row[0]} - {row[1]} {row[2]}" for row in teachers]
        except:
            return []

    def load_class_data(self, class_id):
        try:
            self.cursor.execute("""
                SELECT class_name, section, teacher_id, capacity, room_number
                FROM classes WHERE class_id = ?
            """, (class_id,))
            
            class_data = self.cursor.fetchone()
            
            if class_data:
                fields = ['class_name', 'section', 'teacher', 'capacity', 'room_number']
                
                for i, field in enumerate(fields):
                    if field in self.class_form_entries:
                        if field == 'teacher':
                            value = f"{class_data[2]}" if class_data[2] else ""
                        else:
                            value = class_data[i] if class_data[i] else ""
                        
                        self.class_form_entries[field].delete(0, tk.END)
                        self.class_form_entries[field].insert(0, value)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load class data: {str(e)}")

    def save_class(self, class_id, form_window):
        try:
            # Get form data
            data = {}
            for field, widget in self.class_form_entries.items():
                data[field] = widget.get().strip()
            
            # Validate required fields
            if not data.get('class_name'):
                messagebox.showerror("Error", "Class name is required")
                return
            
            # Prepare database data
            teacher_id = data['teacher'].split(' - ')[0] if data.get('teacher') else None
            
            class_data = (
                data.get('class_name', ''),
                data.get('section', ''),
                teacher_id,
                data.get('capacity', ''),
                data.get('room_number', '')
            )
            
            if class_id:
                # Update existing class
                self.cursor.execute("""
                    UPDATE classes SET class_name=?, section=?, teacher_id=?, capacity=?, room_number=?
                    WHERE class_id=?
                """, (*class_data, class_id))
            else:
                # Insert new class
                created_date = datetime.now().isoformat()
                self.cursor.execute("""
                    INSERT INTO classes (class_name, section, teacher_id, capacity, room_number, created_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (*class_data, created_date))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Class saved successfully!")
            self.load_classes()
            form_window.destroy()
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save class: {str(e)}")

    # ========== TIMETABLE MANAGEMENT ==========
    def show_timetable(self):
        self.clear_content()
        
        header = tk.Label(self.content_frame,
                         text="🕒 Timetable Management",
                         font=('Arial', 24, 'bold'),
                         bg='white',
                         fg='#2c3e50')
        header.pack(pady=20)
        
        # Control frame
        control_frame = tk.Frame(self.content_frame, bg='white')
        control_frame.pack(fill='x', padx=20, pady=10)
        
        # Buttons
        btn_frame = tk.Frame(control_frame, bg='white')
        btn_frame.pack(side='right')
        
        tk.Button(btn_frame, text="➕ Add Timetable", bg='#3498db', fg='white',
                 font=('Arial', 10), padx=10, pady=5, command=self.add_timetable).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🔄 Refresh", bg='#27ae60', fg='white',
                 font=('Arial', 10), padx=10, pady=5, command=self.load_timetable).pack(side='left', padx=5)
        
        # Timetable table
        table_frame = tk.Frame(self.content_frame, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('ID', 'Class', 'Subject', 'Teacher', 'Day', 'Start Time', 'End Time', 'Room')
        self.timetable_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.timetable_tree.heading(col, text=col)
            self.timetable_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.timetable_tree.yview)
        self.timetable_tree.configure(yscrollcommand=scrollbar.set)
        
        self.timetable_tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        self.load_timetable()
        self.timetable_tree.bind('<Double-1>', lambda e: self.edit_timetable())

    def load_timetable(self):
        for item in self.timetable_tree.get_children():
            self.timetable_tree.delete(item)
        
        try:
            self.cursor.execute("""
                SELECT t.timetable_id, c.class_name || ' ' || c.section, 
                       s.subject_name, te.first_name || ' ' || te.last_name,
                       t.day_of_week, t.start_time, t.end_time, t.room
                FROM timetable t
                LEFT JOIN classes c ON t.class_id = c.class_id
                LEFT JOIN subjects s ON t.subject_id = s.subject_id
                LEFT JOIN teachers te ON t.teacher_id = te.teacher_id
                ORDER BY t.day_of_week, t.start_time
            """)
            
            for row in self.cursor.fetchall():
                self.timetable_tree.insert('', tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load timetable: {str(e)}")

    def add_timetable(self):
        self.show_timetable_form()

    def edit_timetable(self):
        selected = self.timetable_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a timetable entry to edit")
            return
        
        timetable_id = self.timetable_tree.item(selected[0])['values'][0]
        self.show_timetable_form(timetable_id)

    def show_timetable_form(self, timetable_id=None):
        form_window = tk.Toplevel(self.root)
        form_window.title("Timetable Form" if not timetable_id else "Edit Timetable")
        form_window.geometry("400x500")
        form_window.configure(bg='white')
        form_window.transient(self.root)
        form_window.grab_set()
        
        self.center_window(form_window, 400, 500)
        
        header_text = "➕ Add Timetable" if not timetable_id else "✏️ Edit Timetable"
        header = tk.Label(form_window, text=header_text, font=('Arial', 18, 'bold'), bg='white', fg='#2c3e50')
        header.pack(pady=20)
        
        form_frame = tk.Frame(form_window, bg='white')
        form_frame.pack(fill='both', expand=True, padx=40)
        
        # Form fields
        fields = [
            ("Class", "combobox", self.get_classes()),
            ("Subject", "combobox", self.get_subjects()),
            ("Teacher", "combobox", self.get_teachers()),
            ("Day of Week", "combobox", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]),
            ("Start Time", "entry"),
            ("End Time", "entry"),
            ("Room", "entry")
        ]
        
        self.timetable_form_entries = {}
        row = 0
        
        for field in fields:
            label = tk.Label(form_frame, text=field[0] + ":", bg='white', anchor='w')
            label.grid(row=row, column=0, sticky='w', pady=5)
            
            if field[1] == "entry":
                entry = tk.Entry(form_frame, width=30)
                entry.grid(row=row, column=1, sticky='w', pady=5, padx=10)
                self.timetable_form_entries[field[0].lower().replace(" ", "_")] = entry
                
            elif field[1] == "combobox":
                combo = ttk.Combobox(form_frame, values=field[2], width=27)
                combo.grid(row=row, column=1, sticky='w', pady=5, padx=10)
                self.timetable_form_entries[field[0].lower().replace(" ", "_")] = combo
            
            row += 1
        
        # Buttons
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="💾 Save", bg='#27ae60', fg='white',
                 font=('Arial', 12), padx=20, pady=10,
                 command=lambda: self.save_timetable(timetable_id, form_window)).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="❌ Cancel", bg='#e74c3c', fg='white',
                 font=('Arial', 12), padx=20, pady=10,
                 command=form_window.destroy).pack(side='left', padx=10)
        
        # Load data if editing
        if timetable_id:
            self.load_timetable_data(timetable_id)

    def get_subjects(self):
        try:
            self.cursor.execute("SELECT subject_id, subject_name FROM subjects")
            subjects = self.cursor.fetchall()
            return [f"{row[0]} - {row[1]}" for row in subjects]
        except:
            return []

    def load_timetable_data(self, timetable_id):
        try:
            self.cursor.execute("""
                SELECT class_id, subject_id, teacher_id, day_of_week, start_time, end_time, room
                FROM timetable WHERE timetable_id = ?
            """, (timetable_id,))
            
            timetable_data = self.cursor.fetchone()
            
            if timetable_data:
                fields = ['class', 'subject', 'teacher', 'day_of_week', 'start_time', 'end_time', 'room']
                
                for i, field in enumerate(fields):
                    if field in self.timetable_form_entries:
                        if field in ['class', 'subject', 'teacher']:
                            value = f"{timetable_data[i]}" if timetable_data[i] else ""
                        else:
                            value = timetable_data[i] if timetable_data[i] else ""
                        
                        self.timetable_form_entries[field].delete(0, tk.END)
                        self.timetable_form_entries[field].insert(0, value)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load timetable data: {str(e)}")

    def save_timetable(self, timetable_id, form_window):
        try:
            # Get form data
            data = {}
            for field, widget in self.timetable_form_entries.items():
                data[field] = widget.get().strip()
            
            # Validate required fields
            if not data.get('class') or not data.get('subject'):
                messagebox.showerror("Error", "Class and Subject are required")
                return
            
            # Prepare database data
            class_id = data['class'].split(' - ')[0] if data.get('class') else None
            subject_id = data['subject'].split(' - ')[0] if data.get('subject') else None
            teacher_id = data['teacher'].split(' - ')[0] if data.get('teacher') else None
            
            timetable_data = (
                class_id,
                subject_id,
                teacher_id,
                data.get('day_of_week', ''),
                data.get('start_time', ''),
                data.get('end_time', ''),
                data.get('room', '')
            )
            
            if timetable_id:
                # Update existing timetable
                self.cursor.execute("""
                    UPDATE timetable SET class_id=?, subject_id=?, teacher_id=?, day_of_week=?, 
                    start_time=?, end_time=?, room=? WHERE timetable_id=?
                """, (*timetable_data, timetable_id))
            else:
                # Insert new timetable
                created_date = datetime.now().isoformat()
                self.cursor.execute("""
                    INSERT INTO timetable (class_id, subject_id, teacher_id, day_of_week, 
                    start_time, end_time, room, created_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (*timetable_data, created_date))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Timetable saved successfully!")
            self.load_timetable()
            form_window.destroy()
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save timetable: {str(e)}")

    # ========== OTHER MODULES (SIMPLIFIED FOR BREVITY) ==========
    def show_teachers(self):
        self.clear_content()
        self.show_management_module("Teachers", "teachers", 
                                   ['ID', 'Name', 'Gender', 'Phone', 'Email', 'Qualification', 'Salary'])

    def show_subjects(self):
        self.clear_content()
        self.show_management_module("Subjects", "subjects",
                                   ['ID', 'Subject Name', 'Code', 'Teacher', 'Class'])

    def show_exams(self):
        self.clear_content()
        self.show_management_module("Exams", "exams",
                                   ['ID', 'Exam Name', 'Term', 'Academic Year', 'Start Date', 'End Date'])

    def show_results(self):
        self.clear_content()
        self.show_management_module("Results", "results",
                                   ['ID', 'Student', 'Subject', 'Exam', 'Marks', 'Grade'])

    def show_attendance(self):
        self.clear_content()
        self.show_management_module("Attendance", "attendance",
                                   ['ID', 'Student', 'Class', 'Date', 'Status'])

    def show_fees(self):
        self.clear_content()
        self.show_management_module("Fees", "fees",
                                   ['ID', 'Student', 'Amount', 'Fee Type', 'Due Date', 'Status'])

    def show_library(self):
        self.clear_content()
        self.show_management_module("Library", "library_books",
                                   ['ID', 'Title', 'Author', 'ISBN', 'Category', 'Available'])

    def show_events(self):
        self.clear_content()
        self.show_management_module("Events", "events",
                                   ['ID', 'Event Name', 'Date', 'Venue', 'Organizer'])

    def show_hostel(self):
        self.clear_content()
        self.show_management_module("Hostel", "hostels",
                                   ['ID', 'Hostel Name', 'Capacity', 'Warden'])

    def show_transport(self):
        self.clear_content()
        self.show_management_module("Transport", "transport",
                                   ['ID', 'Bus Number', 'Driver', 'Route', 'Capacity'])

    def show_inventory(self):
        self.clear_content()
        self.show_management_module("Inventory", "inventory",
                                   ['ID', 'Item Name', 'Category', 'Quantity', 'Unit Price'])

    def show_notices(self):
        self.clear_content()
        self.show_management_module("Notices", "notices",
                                   ['ID', 'Title', 'Publish Date', 'Expiry Date', 'Priority'])

    def show_management_module(self, title, table, columns):
        header = tk.Label(self.content_frame,
                         text=f"{title} Management",
                         font=('Arial', 24, 'bold'),
                         bg='white',
                         fg='#2c3e50')
        header.pack(pady=20)
        
        # Control frame
        control_frame = tk.Frame(self.content_frame, bg='white')
        control_frame.pack(fill='x', padx=20, pady=10)
        
        # Buttons
        btn_frame = tk.Frame(control_frame, bg='white')
        btn_frame.pack(side='right')
        
        tk.Button(btn_frame, text=f"➕ Add {title[:-1]}", bg='#3498db', fg='white',
                 font=('Arial', 10), padx=10, pady=5).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🔄 Refresh", bg='#27ae60', fg='white',
                 font=('Arial', 10), padx=10, pady=5).pack(side='left', padx=5)
        
        # Table
        table_frame = tk.Frame(self.content_frame, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        # Load data
        self.load_table_data(tree, table)

    def load_table_data(self, tree, table):
        try:
            self.cursor.execute(f"SELECT * FROM {table} LIMIT 50")
            for row in self.cursor.fetchall():
                tree.insert('', tk.END, values=row)
        except Exception as e:
            print(f"Error loading {table}: {e}")

    def show_id_cards(self):
        self.clear_content()
        header = tk.Label(self.content_frame,
                         text="🆔 ID Card Generator",
                         font=('Arial', 24, 'bold'),
                         bg='white',
                         fg='#2c3e50')
        header.pack(pady=20)
        
        tk.Button(self.content_frame, text="🎫 Generate All ID Cards", bg='#3498db', fg='white',
                 font=('Arial', 12), padx=20, pady=10).pack(pady=10)

    def show_reports(self):
        self.clear_content()
        header = tk.Label(self.content_frame,
                         text="📋 Reports & Analytics",
                         font=('Arial', 24, 'bold'),
                         bg='white',
                         fg='#2c3e50')
        header.pack(pady=20)
        
        reports = [
            "Student Performance Report",
            "Attendance Summary Report", 
            "Fee Collection Report",
            "Library Usage Report"
        ]
        
        for report in reports:
            tk.Button(self.content_frame, text=f"📊 {report}", bg='#9b59b6', fg='white',
                     font=('Arial', 11), padx=20, pady=8, width=25).pack(pady=5)

    def show_settings(self):
        self.clear_content()
        header = tk.Label(self.content_frame,
                         text="⚙️ System Settings",
                         font=('Arial', 24, 'bold'),
                         bg='white',
                         fg='#2c3e50')
        header.pack(pady=20)
        
        settings = [
            "School Information",
            "Academic Settings", 
            "Fee Structure",
            "System Preferences"
        ]
        
        for setting in settings:
            tk.Button(self.content_frame, text=f"⚙️ {setting}", bg='#f39c12', fg='white',
                     font=('Arial', 11), padx=20, pady=8, width=25).pack(pady=5)

    def show_backup(self):
        self.clear_content()
        header = tk.Label(self.content_frame,
                         text="💾 Backup & Restore",
                         font=('Arial', 24, 'bold'),
                         bg='white',
                         fg='#2c3e50')
        header.pack(pady=20)
        
        tk.Button(self.content_frame, text="💾 Create Backup", bg='#3498db', fg='white',
                 font=('Arial', 12), padx=20, pady=10, command=self.create_backup).pack(pady=10)
        
        tk.Button(self.content_frame, text="🔄 Restore Backup", bg='#27ae60', fg='white',
                 font=('Arial', 12), padx=20, pady=10, command=self.restore_backup).pack(pady=10)

    def show_user_management(self):
        self.clear_content()
        header = tk.Label(self.content_frame,
                         text="👥 User Management",
                         font=('Arial', 24, 'bold'),
                         bg='white',
                         fg='#2c3e50')
        header.pack(pady=20)
        
        content = tk.Label(self.content_frame,
                          text="User Management Module\n\n"
                               "Features:\n"
                               "✅ Add/Edit/Delete users\n"
                               "✅ Role-based permissions\n"
                               "✅ User activity logs\n"
                               "✅ Password reset\n"
                               "✅ Bulk user operations",
                          font=('Arial', 12),
                          bg='white',
                          justify='left')
        content.pack(pady=20)

    def create_backup(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"school_data/backups/backup_{timestamp}.db"
            shutil.copy2('school_data/school_management.db', backup_file)
            messagebox.showinfo("Success", f"Backup created successfully!\n{backup_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create backup: {str(e)}")

    def restore_backup(self):
        file_path = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                shutil.copy2(file_path, 'school_data/school_management.db')
                messagebox.showinfo("Success", "Backup restored successfully!\nPlease restart the application.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restore backup: {str(e)}")

def main():
    try:
        root = tk.Tk()
        app = SchoolManagementSystem(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()