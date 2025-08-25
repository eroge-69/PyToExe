import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import sqlite3
import os
import random

class OPDManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("OPD Management System with Billing")
        self.root.geometry("1300x750")
        self.root.configure(bg='#f0f8ff')
        
        # Database setup
        self.setup_database()
        
        # Create main frames
        self.create_header()
        self.create_sidebar()
        self.create_main_area()
        self.create_status_bar()
        
        # Load initial data
        self.load_patients()
        
    def setup_database(self):
        # Create database directory if not exists
        if not os.path.exists('data'):
            os.makedirs('data')
            
        # Connect to SQLite database
        self.conn = sqlite3.connect('data/opd_management.db')
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                contact TEXT,
                address TEXT,
                registration_date TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                date TEXT,
                time TEXT,
                doctor_name TEXT,
                reason TEXT,
                status TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                bill_date TEXT,
                doctor_fee REAL,
                medicine_charges REAL,
                test_charges REAL,
                other_charges REAL,
                total_amount REAL,
                payment_status TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                charge REAL NOT NULL,
                category TEXT
            )
        ''')
        
        # Insert some sample services if table is empty
        self.cursor.execute("SELECT COUNT(*) FROM services")
        if self.cursor.fetchone()[0] == 0:
            sample_services = [
                ('Consultation', 500, 'Doctor Fee'),
                ('ECG', 300, 'Test'),
                ('Blood Test', 400, 'Test'),
                ('X-Ray', 600, 'Test'),
                ('Medicines', 0, 'Medicine'),
                ('Bandage', 50, 'Medicine'),
                ('Injection', 100, 'Medicine'),
                ('Room Charge', 1000, 'Other')
            ]
            
            self.cursor.executemany('''
                INSERT INTO services (name, charge, category) VALUES (?, ?, ?)
            ''', sample_services)
        
        self.conn.commit()
        
    def create_header(self):
        header = tk.Frame(self.root, bg='#2c3e50', height=80)
        header.pack(fill=tk.X)
        
        title = tk.Label(header, text="OPD Management System with Billing", font=("Arial", 20, "bold"), 
                        fg='white', bg='#2c3e50')
        title.pack(pady=20)
        
    def create_sidebar(self):
        sidebar = tk.Frame(self.root, width=250, bg='#34495e')
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Sidebar buttons
        buttons = [
            ("Dashboard", self.show_dashboard),
            ("New Patient", self.show_new_patient),
            ("Appointments", self.show_appointments),
            ("Billing", self.show_billing),
            ("Patient Search", self.show_search),
            ("Reports", self.show_reports)
        ]
        
        for text, command in buttons:
            btn = tk.Button(sidebar, text=text, font=("Arial", 12), 
                           bg='#3498db', fg='white', relief=tk.FLAT,
                           command=command, width=20, height=2)
            btn.pack(pady=10, padx=10)
            
        # Exit button
        exit_btn = tk.Button(sidebar, text="Exit", font=("Arial", 12), 
                            bg='#e74c3c', fg='white', relief=tk.FLAT,
                            command=self.exit_app, width=20, height=2)
        exit_btn.pack(side=tk.BOTTOM, pady=10, padx=10)
        
    def create_main_area(self):
        self.main_area = tk.Frame(self.root, bg='#ecf0f1')
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Default view
        self.show_dashboard()
        
    def create_status_bar(self):
        status_bar = tk.Frame(self.root, bg='#2c3e50', height=30)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_text = tk.StringVar()
        self.status_text.set("Ready | Total Patients: 0")
        
        status_label = tk.Label(status_bar, textvariable=self.status_text, 
                               fg='white', bg='#2c3e50', font=("Arial", 10))
        status_label.pack(side=tk.LEFT, padx=10)
        
        time_label = tk.Label(status_bar, text=datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 
                             fg='white', bg='#2c3e50', font=("Arial", 10))
        time_label.pack(side=tk.RIGHT, padx=10)
        
    def show_dashboard(self):
        self.clear_main_area()
        
        title = tk.Label(self.main_area, text="OPD Dashboard", font=("Arial", 20, "bold"), 
                        bg='#ecf0f1', fg='#2c3e50')
        title.pack(pady=20)
        
        # Dashboard widgets
        frame = tk.Frame(self.main_area, bg='#ecf0f1')
        frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Stats frame
        stats_frame = tk.Frame(frame, bg='#ecf0f1')
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Stats cards
        stats_data = [
            ("Total Patients", "125", "#3498db"),
            ("Today's Appointments", "15", "#2ecc71"),
            ("Pending Bills", "8", "#e74c3c"),
            ("Revenue Today", "₹12,500", "#f39c12")
        ]
        
        for i, (title, value, color) in enumerate(stats_data):
            card = tk.Frame(stats_frame, bg=color, relief=tk.RAISED, bd=2)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            title_label = tk.Label(card, text=title, font=("Arial", 12, "bold"), 
                                  bg=color, fg='white')
            title_label.pack(pady=(10, 5))
            
            value_label = tk.Label(card, text=value, font=("Arial", 16, "bold"), 
                                  bg=color, fg='white')
            value_label.pack(pady=(5, 10))
        
        # Today's appointments
        apt_frame = tk.LabelFrame(frame, text="Today's Appointments", font=("Arial", 14), 
                                 bg='#ecf0f1', fg='#2c3e50')
        apt_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create a treeview for appointments
        columns = ("ID", "Patient Name", "Time", "Doctor", "Status")
        self.apt_tree = ttk.Treeview(apt_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.apt_tree.heading(col, text=col)
            self.apt_tree.column(col, width=120)
            
        self.apt_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add some sample data
        sample_appointments = [
            (1, "Rahul Sharma", "10:00 AM", "Dr. Gupta", "Scheduled"),
            (2, "Priya Singh", "11:30 AM", "Dr. Kumar", "Completed"),
            (3, "Amit Patel", "02:00 PM", "Dr. Sharma", "Scheduled"),
            (4, "Sneha Desai", "03:30 PM", "Dr. Kapoor", "Pending"),
            (5, "Vikram Joshi", "05:00 PM", "Dr. Reddy", "Scheduled")
        ]
        
        for apt in sample_appointments:
            self.apt_tree.insert("", tk.END, values=apt)
            
        # Quick actions frame
        action_frame = tk.Frame(frame, bg='#ecf0f1')
        action_frame.pack(fill=tk.X, pady=10)
        
        new_apt_btn = tk.Button(action_frame, text="New Appointment", font=("Arial", 12), 
                               bg='#2ecc71', fg='white', width=15, height=2,
                               command=self.show_new_appointment)
        new_apt_btn.pack(side=tk.LEFT, padx=10)
        
        new_patient_btn = tk.Button(action_frame, text="New Patient", font=("Arial", 12), 
                                   bg='#3498db', fg='white', width=15, height=2,
                                   command=self.show_new_patient)
        new_patient_btn.pack(side=tk.LEFT, padx=10)
        
        billing_btn = tk.Button(action_frame, text="Generate Bill", font=("Arial", 12), 
                               bg='#f39c12', fg='white', width=15, height=2,
                               command=self.show_billing)
        billing_btn.pack(side=tk.LEFT, padx=10)
        
    def show_new_patient(self):
        self.clear_main_area()
        
        title = tk.Label(self.main_area, text="New Patient Registration", font=("Arial", 20, "bold"), 
                        bg='#ecf0f1', fg='#2c3e50')
        title.pack(pady=20)
        
        # Form frame
        form_frame = tk.Frame(self.main_area, bg='#ecf0f1')
        form_frame.pack(pady=20, padx=50, fill=tk.BOTH)
        
        # Form fields
        fields = [
            ("Name", "entry"),
            ("Age", "entry"),
            ("Gender", "combo", ["Male", "Female", "Other"]),
            ("Contact", "entry"),
            ("Address", "text")
        ]
        
        self.form_vars = {}
        row = 0
        
        for field in fields:
            label = tk.Label(form_frame, text=field[0] + ":", font=("Arial", 12), 
                            bg='#ecf0f1', fg='#2c3e50', anchor='w')
            label.grid(row=row, column=0, sticky='w', pady=10, padx=10)
            
            if field[1] == "entry":
                var = tk.StringVar()
                entry = tk.Entry(form_frame, textvariable=var, font=("Arial", 12), width=30)
                entry.grid(row=row, column=1, pady=10, padx=10, sticky='we')
                self.form_vars[field[0].lower()] = var
                
            elif field[1] == "combo":
                var = tk.StringVar()
                combo = ttk.Combobox(form_frame, textvariable=var, values=field[2], 
                                    font=("Arial", 12), width=28, state="readonly")
                combo.grid(row=row, column=1, pady=10, padx=10, sticky='we')
                self.form_vars[field[0].lower()] = var
                
            elif field[1] == "text":
                text_widget = tk.Text(form_frame, font=("Arial", 12), width=30, height=4)
                text_widget.grid(row=row, column=1, pady=10, padx=10, sticky='we')
                # For text widget, we'll store the widget itself
                self.form_vars[field[0].lower()] = text_widget
                
            row += 1
            
        # Button frame
        button_frame = tk.Frame(form_frame, bg='#ecf0f1')
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        submit_btn = tk.Button(button_frame, text="Register Patient", font=("Arial", 12), 
                              bg='#2ecc71', fg='white', width=15,
                              command=self.register_patient)
        submit_btn.pack(side=tk.LEFT, padx=10)
        
        clear_btn = tk.Button(button_frame, text="Clear Form", font=("Arial", 12), 
                             bg='#e74c3c', fg='white', width=15,
                             command=self.clear_form)
        clear_btn.pack(side=tk.LEFT, padx=10)
        
    def show_appointments(self):
        self.clear_main_area()
        
        title = tk.Label(self.main_area, text="Appointment Management", font=("Arial", 20, "bold"), 
                        bg='#ecf0f1', fg='#2c3e50')
        title.pack(pady=20)
        
        # Add appointment management content here
        content = tk.Label(self.main_area, text="Appointment management functionality will be implemented here", 
                          font=("Arial", 14), bg='#ecf0f1', fg='#7f8c8d')
        content.pack(pady=100)
        
    def show_billing(self):
        self.clear_main_area()
        
        title = tk.Label(self.main_area, text="Billing System", font=("Arial", 20, "bold"), 
                        bg='#ecf0f1', fg='#2c3e50')
        title.pack(pady=20)
        
        # Billing form frame
        billing_frame = tk.Frame(self.main_area, bg='#ecf0f1')
        billing_frame.pack(pady=20, padx=50, fill=tk.BOTH, expand=True)
        
        # Patient selection
        patient_frame = tk.Frame(billing_frame, bg='#ecf0f1')
        patient_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(patient_frame, text="Select Patient:", font=("Arial", 12), 
                bg='#ecf0f1', fg='#2c3e50').pack(side=tk.LEFT, padx=10)
        
        self.patient_var = tk.StringVar()
        patient_combo = ttk.Combobox(patient_frame, textvariable=self.patient_var, 
                                    values=["Rahul Sharma (ID: 1001)", "Priya Singh (ID: 1002)", 
                                            "Amit Patel (ID: 1003)", "Sneha Desai (ID: 1004)"],
                                    font=("Arial", 12), width=30, state="readonly")
        patient_combo.pack(side=tk.LEFT, padx=10)
        patient_combo.set("Select Patient")
        
        # Services frame
        services_frame = tk.LabelFrame(billing_frame, text="Services & Charges", font=("Arial", 14), 
                                      bg='#ecf0f1', fg='#2c3e50')
        services_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create a treeview for services
        columns = ("Service", "Charge", "Category")
        self.services_tree = ttk.Treeview(services_frame, columns=columns, show="headings", height=6)
        
        for col in columns:
            self.services_tree.heading(col, text=col)
            self.services_tree.column(col, width=150)
            
        self.services_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add sample services
        sample_services = [
            ("Consultation", "500", "Doctor Fee"),
            ("ECG", "300", "Test"),
            ("Blood Test", "400", "Test"),
            ("X-Ray", "600", "Test"),
            ("Medicines", "750", "Medicine"),
            ("Injection", "100", "Medicine")
        ]
        
        for service in sample_services:
            self.services_tree.insert("", tk.END, values=service)
        
        # Charges summary frame
        summary_frame = tk.Frame(billing_frame, bg='#ecf0f1')
        summary_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(summary_frame, text="Doctor Fee:", font=("Arial", 12), 
                bg='#ecf0f1', fg='#2c3e50').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        self.doc_fee_var = tk.StringVar()
        self.doc_fee_var.set("500")
        doc_fee_entry = tk.Entry(summary_frame, textvariable=self.doc_fee_var, 
                                font=("Arial", 12), width=15)
        doc_fee_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(summary_frame, text="Medicine Charges:", font=("Arial", 12), 
                bg='#ecf0f1', fg='#2c3e50').grid(row=0, column=2, sticky='w', padx=10, pady=5)
        
        self.med_charge_var = tk.StringVar()
        self.med_charge_var.set("850")
        med_charge_entry = tk.Entry(summary_frame, textvariable=self.med_charge_var, 
                                   font=("Arial", 12), width=15)
        med_charge_entry.grid(row=0, column=3, padx=10, pady=5)
        
        tk.Label(summary_frame, text="Test Charges:", font=("Arial", 12), 
                bg='#ecf0f1', fg='#2c3e50').grid(row=1, column=0, sticky='w', padx=10, pady=5)
        
        self.test_charge_var = tk.StringVar()
        self.test_charge_var.set("700")
        test_charge_entry = tk.Entry(summary_frame, textvariable=self.test_charge_var, 
                                    font=("Arial", 12), width=15)
        test_charge_entry.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(summary_frame, text="Other Charges:", font=("Arial", 12), 
                bg='#ecf0f1', fg='#2c3e50').grid(row=1, column=2, sticky='w', padx=10, pady=5)
        
        self.other_charge_var = tk.StringVar()
        self.other_charge_var.set("0")
        other_charge_entry = tk.Entry(summary_frame, textvariable=self.other_charge_var, 
                                     font=("Arial", 12), width=15)
        other_charge_entry.grid(row=1, column=3, padx=10, pady=5)
        
        tk.Label(summary_frame, text="Total Amount:", font=("Arial", 14, "bold"), 
                bg='#ecf0f1', fg='#2c3e50').grid(row=2, column=0, sticky='w', padx=10, pady=10)
        
        self.total_amount_var = tk.StringVar()
        self.total_amount_var.set("2050")
        total_amount_entry = tk.Entry(summary_frame, textvariable=self.total_amount_var, 
                                     font=("Arial", 14, "bold"), width=15, state='readonly',
                                     readonlybackground='#f0f0f0')
        total_amount_entry.grid(row=2, column=1, padx=10, pady=10)
        
        # Payment status
        tk.Label(summary_frame, text="Payment Status:", font=("Arial", 12), 
                bg='#ecf0f1', fg='#2c3e50').grid(row=2, column=2, sticky='w', padx=10, pady=10)
        
        self.payment_status_var = tk.StringVar()
        payment_combo = ttk.Combobox(summary_frame, textvariable=self.payment_status_var, 
                                    values=["Paid", "Pending", "Partial"],
                                    font=("Arial", 12), width=12, state="readonly")
        payment_combo.grid(row=2, column=3, padx=10, pady=10)
        payment_combo.set("Paid")
        
        # Button frame
        button_frame = tk.Frame(billing_frame, bg='#ecf0f1')
        button_frame.pack(pady=20)
        
        generate_btn = tk.Button(button_frame, text="Generate Bill", font=("Arial", 12), 
                                bg='#2ecc71', fg='white', width=15,
                                command=self.generate_bill)
        generate_btn.pack(side=tk.LEFT, padx=10)
        
        print_btn = tk.Button(button_frame, text="Print Bill", font=("Arial", 12), 
                             bg='#3498db', fg='white', width=15,
                             command=self.print_bill)
        print_btn.pack(side=tk.LEFT, padx=10)
        
        clear_btn = tk.Button(button_frame, text="Clear", font=("Arial", 12), 
                             bg='#e74c3c', fg='white', width=15,
                             command=self.clear_bill)
        clear_btn.pack(side=tk.LEFT, padx=10)
        
    def show_search(self):
        self.clear_main_area()
        
        title = tk.Label(self.main_area, text="Patient Search", font=("Arial", 20, "bold"), 
                        bg='#ecf0f1', fg='#2c3e50')
        title.pack(pady=20)
        
        # Add patient search content here
        content = tk.Label(self.main_area, text="Patient search functionality will be implemented here", 
                          font=("Arial", 14), bg='#ecf0f1', fg='#7f8c8d')
        content.pack(pady=100)
        
    def show_reports(self):
        self.clear_main_area()
        
        title = tk.Label(self.main_area, text="Reports", font=("Arial", 20, "bold"), 
                        bg='#ecf0f1', fg='#2c3e50')
        title.pack(pady=20)
        
        # Add reports content here
        content = tk.Label(self.main_area, text="Reporting functionality will be implemented here", 
                          font=("Arial", 14), bg='#ecf0f1', fg='#7f8c8d')
        content.pack(pady=100)
        
    def show_new_appointment(self):
        self.clear_main_area()
        
        title = tk.Label(self.main_area, text="New Appointment", font=("Arial", 20, "bold"), 
                        bg='#ecf0f1', fg='#2c3e50')
        title.pack(pady=20)
        
        # Add new appointment form here
        content = tk.Label(self.main_area, text="New appointment form will be implemented here", 
                          font=("Arial", 14), bg='#ecf0f1', fg='#7f8c8d')
        content.pack(pady=100)
        
    def clear_main_area(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
            
    def load_patients(self):
        # This would load patients from database
        # For now, we'll just set a dummy count
        self.status_text.set(f"Ready | Total Patients: 125")
        
    def register_patient(self):
        # Get form data
        name = self.form_vars['name'].get()
        age = self.form_vars['age'].get()
        gender = self.form_vars['gender'].get()
        contact = self.form_vars['contact'].get()
        address = self.form_vars['address'].get("1.0", tk.END).strip()
        
        # Validate form
        if not name or not age or not gender or not contact:
            messagebox.showerror("Error", "Please fill all required fields")
            return
            
        # Save to database (simplified)
        try:
            self.cursor.execute('''
                INSERT INTO patients (name, age, gender, contact, address, registration_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, age, gender, contact, address, datetime.now().strftime("%Y-%m-%d")))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Patient registered successfully!")
            self.clear_form()
            self.load_patients()  # Refresh patient count
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Error saving patient: {str(e)}")
            
    def generate_bill(self):
        patient = self.patient_var.get()
        if patient == "Select Patient":
            messagebox.showerror("Error", "Please select a patient")
            return
            
        # Calculate total
        try:
            doc_fee = float(self.doc_fee_var.get())
            med_charges = float(self.med_charge_var.get())
            test_charges = float(self.test_charge_var.get())
            other_charges = float(self.other_charge_var.get())
            
            total = doc_fee + med_charges + test_charges + other_charges
            self.total_amount_var.set(str(total))
            
            # Save to database (simplified)
            patient_id = patient.split("ID: ")[1].replace(")", "")
            
            self.cursor.execute('''
                INSERT INTO bills (patient_id, bill_date, doctor_fee, medicine_charges, 
                test_charges, other_charges, total_amount, payment_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (patient_id, datetime.now().strftime("%Y-%m-%d"), doc_fee, med_charges, 
                 test_charges, other_charges, total, self.payment_status_var.get()))
            
            self.conn.commit()
            
            # Show bill preview
            self.show_bill_preview(patient, doc_fee, med_charges, test_charges, other_charges, total)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for charges")
            
    def show_bill_preview(self, patient, doc_fee, med_charges, test_charges, other_charges, total):
        # Create a new window for bill preview
        preview = tk.Toplevel(self.root)
        preview.title("Bill Preview")
        preview.geometry("500x600")
        preview.configure(bg='white')
        
        # Bill header
        header = tk.Frame(preview, bg='#2c3e50', height=80)
        header.pack(fill=tk.X)
        
        title = tk.Label(header, text="MEDICAL BILL", font=("Arial", 20, "bold"), 
                        fg='white', bg='#2c3e50')
        title.pack(pady=20)
        
        # Bill details
        details_frame = tk.Frame(preview, bg='white')
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Hospital info
        tk.Label(details_frame, text="City Hospital", font=("Arial", 16, "bold"), 
                bg='white').pack(pady=(0, 10))
        tk.Label(details_frame, text="123 Medical Street, City", font=("Arial", 12), 
                bg='white').pack(pady=(0, 20))
        
        # Bill number and date
        bill_frame = tk.Frame(details_frame, bg='white')
        bill_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(bill_frame, text=f"Bill No: {random.randint(1000, 9999)}", 
                font=("Arial", 10), bg='white').pack(side=tk.LEFT)
        tk.Label(bill_frame, text=f"Date: {datetime.now().strftime('%d-%m-%Y')}", 
                font=("Arial", 10), bg='white').pack(side=tk.RIGHT)
        
        # Patient info
        tk.Label(details_frame, text=f"Patient: {patient}", font=("Arial", 12), 
                bg='white', anchor='w').pack(fill=tk.X, pady=10)
        
        # Charges breakdown
        charges_frame = tk.Frame(details_frame, bg='white')
        charges_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(charges_frame, text="Description", font=("Arial", 12, "bold"), 
                bg='white').grid(row=0, column=0, sticky='w')
        tk.Label(charges_frame, text="Amount (₹)", font=("Arial", 12, "bold"), 
                bg='white').grid(row=0, column=1, sticky='e')
        
        charges = [
            ("Doctor Consultation", doc_fee),
            ("Medicines", med_charges),
            ("Tests", test_charges),
            ("Other Charges", other_charges)
        ]
        
        for i, (desc, amount) in enumerate(charges, 1):
            tk.Label(charges_frame, text=desc, font=("Arial", 10), 
                    bg='white').grid(row=i, column=0, sticky='w', pady=2)
            tk.Label(charges_frame, text=f"₹{amount:.2f}", font=("Arial", 10), 
                    bg='white').grid(row=i, column=1, sticky='e', pady=2)
        
        # Total
        total_frame = tk.Frame(charges_frame, bg='white')
        total_frame.grid(row=5, column=0, columnspan=2, sticky='we', pady=(10, 0))
        
        tk.Label(total_frame, text="TOTAL", font=("Arial", 12, "bold"), 
                bg='white').pack(side=tk.LEFT)
        tk.Label(total_frame, text=f"₹{total:.2f}", font=("Arial", 12, "bold"), 
                bg='white').pack(side=tk.RIGHT)
        
        # Payment status
        tk.Label(details_frame, text=f"Payment Status: {self.payment_status_var.get()}", 
                font=("Arial", 12), bg='white').pack(pady=10)
        
        # Footer
        footer = tk.Frame(details_frame, bg='white')
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        tk.Label(footer, text="Thank you for visiting!", font=("Arial", 10, "italic"), 
                bg='white').pack()
        tk.Label(footer, text="For queries contact: 0123-456789", font=("Arial", 10), 
                bg='white').pack()
        
        # Close button
        close_btn = tk.Button(preview, text="Close", font=("Arial", 12), 
                             bg='#3498db', fg='white', width=15,
                             command=preview.destroy)
        close_btn.pack(pady=10)
        
    def print_bill(self):
        messagebox.showinfo("Print", "Bill sent to printer")
        
    def clear_bill(self):
        self.patient_var.set("Select Patient")
        self.doc_fee_var.set("500")
        self.med_charge_var.set("0")
        self.test_charge_var.set("0")
        self.other_charge_var.set("0")
        self.total_amount_var.set("0")
        self.payment_status_var.set("Paid")
            
    def clear_form(self):
        for key, var in self.form_vars.items():
            if isinstance(var, tk.StringVar):
                var.set("")
            elif isinstance(var, tk.Text):
                var.delete("1.0", tk.END)
                
    def exit_app(self):
        if messagebox.askokcancel("Exit", "Do you want to exit the application?"):
            self.conn.close()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = OPDManagementSystem(root)
    root.mainloop()