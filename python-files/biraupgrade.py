import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import pandas as pd
from tkcalendar import DateEntry

class ServiceTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Laptop Service Tracker")
        self.root.state('zoomed')
        
        # Configure root to resize properly
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Set style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TButton", padding=6, relief="flat", background="#4CAF50", 
                            foreground="white", font=('Arial', 10))
        self.style.map("TButton", background=[('active', '#45a049')])
        self.style.configure("TLabel", padding=3, background="#f0f0f0", font=('Arial', 9))
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabelframe", background="#f0f0f0", font=('Arial', 10, 'bold'))
        self.style.configure("TLabelframe.Label", background="#f0f0f0", font=('Arial', 10, 'bold'))
        self.style.configure("Custom.TButton", foreground="#ffffff", background="#4CAF50", 
                            font=('Arial', 10, 'bold'))
        self.style.configure("Treeview", font=('Arial', 9))
        self.style.configure("Treeview.Heading", font=('Arial', 9, 'bold'))
        
        # Database initialization
        self.create_database()
        
        # Main container
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main_frame to resize properly
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Create tabs
        self.tab_control = ttk.Notebook(self.main_frame)
        self.tab_control.grid(row=0, column=0, sticky='nsew')

        # Input Tab
        self.input_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.input_tab, text='Input Data')
        self.setup_input_tab()

        # View Tab
        self.view_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.view_tab, text='View Data')
        
        # Configure view_tab to resize properly
        self.view_tab.columnconfigure(0, weight=1)
        self.view_tab.rowconfigure(1, weight=1)  # The row with the Treeview should expand
        
        self.setup_view_tab()

    def create_database(self):
        conn = sqlite3.connect('service_tracker.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT,
                unit_type TEXT,
                unit_series TEXT,
                phone_number TEXT,
                damage_type TEXT,
                repair_type TEXT,
                cost REAL,
                price REAL,
                profit REAL,
                received_date DATE,
                completed_date DATE,
                pickup_date DATE,
                warranty_period INTEGER,
                warranty_status TEXT,
                service_status TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def setup_input_tab(self):
        # Main container for input tab
        input_main_frame = ttk.Frame(self.input_tab)
        input_main_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Configure grid weights
        input_main_frame.columnconfigure(0, weight=1)
        input_main_frame.columnconfigure(1, weight=1)
        input_main_frame.rowconfigure(0, weight=1)

        # Left side - Input Form
        input_frame = ttk.LabelFrame(input_main_frame, text="Service Information", padding="10")
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)

        # Customer Information
        ttk.Label(input_frame, text="Customer Name:").grid(row=0, column=0, sticky='w', pady=3)
        self.customer_name = ttk.Entry(input_frame, width=30)
        self.customer_name.grid(row=0, column=1, padx=5, pady=3, sticky='ew')

        ttk.Label(input_frame, text="Phone Number:").grid(row=1, column=0, sticky='w', pady=3)
        self.phone_number = ttk.Entry(input_frame, width=30)
        self.phone_number.grid(row=1, column=1, padx=5, pady=3, sticky='ew')

        # Unit Information
        ttk.Label(input_frame, text="Unit Type:").grid(row=2, column=0, sticky='w', pady=3)
        self.unit_type = ttk.Combobox(input_frame, values=['Laptop', 'PC', 'Printer'], width=27)
        self.unit_type.grid(row=2, column=1, padx=5, pady=3, sticky='ew')

        ttk.Label(input_frame, text="Unit Series:").grid(row=3, column=0, sticky='w', pady=3)
        self.unit_series = ttk.Entry(input_frame, width=30)
        self.unit_series.grid(row=3, column=1, padx=5, pady=3, sticky='ew')

        # Service Details
        ttk.Label(input_frame, text="Damage Type:").grid(row=4, column=0, sticky='w', pady=3)
        self.damage_type = ttk.Entry(input_frame, width=30)
        self.damage_type.grid(row=4, column=1, padx=5, pady=3, sticky='ew')

        ttk.Label(input_frame, text="Repair Type:").grid(row=5, column=0, sticky='w', pady=3)
        self.repair_type = ttk.Entry(input_frame, width=30)
        self.repair_type.grid(row=5, column=1, padx=5, pady=3, sticky='ew')

        # Financial Information
        ttk.Label(input_frame, text="Cost (Rp):").grid(row=0, column=2, sticky='w', padx=(20,0), pady=3)
        self.cost = ttk.Entry(input_frame, width=30)
        self.cost.grid(row=0, column=3, padx=5, pady=3, sticky='ew')

        ttk.Label(input_frame, text="Price (Rp):").grid(row=1, column=2, sticky='w', padx=(20,0), pady=3)
        self.price = ttk.Entry(input_frame, width=30)
        self.price.grid(row=1, column=3, padx=5, pady=3, sticky='ew')

        # Service Dates
        dates_frame = ttk.LabelFrame(input_frame, text="Service Dates", padding="5")
        dates_frame.grid(row=6, column=0, columnspan=4, sticky='ew', pady=10)
        dates_frame.columnconfigure(1, weight=1)
        dates_frame.columnconfigure(3, weight=1)

        ttk.Label(dates_frame, text="Received Date:").grid(row=0, column=0, sticky='w', padx=5, pady=3)
        self.received_date = DateEntry(dates_frame, width=27, date_pattern='yyyy-mm-dd')
        self.received_date.grid(row=0, column=1, padx=5, pady=3, sticky='ew')

        ttk.Label(dates_frame, text="Completion Date:").grid(row=0, column=2, sticky='w', padx=20, pady=3)
        self.completed_date = DateEntry(dates_frame, width=27, date_pattern='yyyy-mm-dd')
        self.completed_date.grid(row=0, column=3, padx=5, pady=3, sticky='ew')

        ttk.Label(dates_frame, text="Pickup Date:").grid(row=1, column=0, sticky='w', padx=5, pady=3)
        self.pickup_date = DateEntry(dates_frame, width=27, date_pattern='yyyy-mm-dd')
        self.pickup_date.grid(row=1, column=1, padx=5, pady=3, sticky='ew')

        # Additional Information
        ttk.Label(input_frame, text="Warranty Period (days):").grid(row=2, column=2, sticky='w', padx=(20,0), pady=3)
        self.warranty_period = ttk.Entry(input_frame, width=30)
        self.warranty_period.grid(row=2, column=3, padx=5, pady=3, sticky='ew')

        ttk.Label(input_frame, text="Service Status:").grid(row=3, column=2, sticky='w', padx=(20,0), pady=3)
        self.service_status = ttk.Combobox(input_frame, 
            values=['Pending', 'In Progress', 'Completed', 'Picked Up', 'Failed'], width=27)
        self.service_status.grid(row=3, column=3, padx=5, pady=3, sticky='ew')

        # Submit Button
        self.submit_btn = ttk.Button(input_frame, text="Submit", command=self.save_record, style="Custom.TButton")
        self.submit_btn.grid(row=7, column=1, columnspan=2, pady=20)

        # Right side - SOP
        sop_frame = ttk.LabelFrame(input_main_frame, text="Standard Operating Procedure", padding="10")
        sop_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        sop_frame.columnconfigure(0, weight=1)
        sop_frame.rowconfigure(0, weight=1)

        sop_text = """
        STANDARD OPERATING PROCEDURE (SOP) SERVIS LAPTOP, PC & PRINTER

        A. PENERIMAAN UNIT
        1. Periksa kondisi fisik unit dengan teliti
        2. Dokumentasikan kerusakan yang terlihat
        3. Catat semua keluhan pelanggan dengan detail
        4. Berikan tanda terima dengan nomor servis unik

        B. DIAGNOSA
        1. Lakukan pengujian awal untuk identifikasi masalah
        2. Dokumentasikan hasil temuan
        3. Informasikan estimasi biaya dan waktu pengerjaan
        4. Dapatkan persetujuan pelanggan sebelum pengerjaan

        C. PENGERJAAN SERVIS
        1. Gunakan peralatan yang sesuai dan berkualitas
        2. Dokumentasikan setiap langkah pengerjaan
        3. Lakukan backup data jika diperlukan
        4. Gunakan spare part original/berkualitas

        D. QUALITY CONTROL
        1. Lakukan pengujian menyeluruh setelah perbaikan
        2. Pastikan semua fungsi berjalan normal
        3. Dokumentasikan hasil pengujian
        4. Bersihkan unit sebelum diserahkan

        E. PENYERAHAN UNIT
        1. Demonstrasikan hasil perbaikan ke pelanggan
        2. Jelaskan garansi dan batasan-batasannya
        3. Berikan tips perawatan unit
        4. Dokumentasikan serah terima unit

        F. GARANSI
        1. Berlaku sesuai periode yang ditentukan
        2. Catat detail garansi pada kartu garansi
        3. Simpan salinan kartu garansi
        4. Jelaskan syarat dan ketentuan garansi
        """

        sop_display = tk.Text(sop_frame, height=30, width=60, wrap=tk.WORD, font=('Arial', 9))
        sop_display.insert(tk.END, sop_text)
        sop_display.config(state='disabled')
        sop_display.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        sop_scrollbar = ttk.Scrollbar(sop_frame, orient='vertical', command=sop_display.yview)
        sop_scrollbar.grid(row=0, column=1, sticky='ns')
        sop_display.config(yscrollcommand=sop_scrollbar.set)

    def setup_view_tab(self):
        # Search Frame
        search_frame = ttk.Frame(self.view_tab, padding="5")
        search_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        search_frame.columnconfigure(1, weight=1)

        # Customer ID Search
        ttk.Label(search_frame, text="Search Customer ID:").grid(row=0, column=0, padx=5, sticky='w')
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, sticky='ew')

        search_btn = ttk.Button(search_frame, text="Search", command=self.search_records, style="Custom.TButton")
        search_btn.grid(row=0, column=2, padx=5)
        
        export_btn = ttk.Button(search_frame, text="Export to Excel", command=self.export_to_excel, style="Custom.TButton")
        export_btn.grid(row=0, column=3, padx=5)
        
        # Date Range Filter - NEW FEATURE
        date_filter_frame = ttk.LabelFrame(self.view_tab, text="Date Range Filter", padding="5")
        date_filter_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        date_filter_frame.columnconfigure(1, weight=1)
        date_filter_frame.columnconfigure(3, weight=1)
        
        ttk.Label(date_filter_frame, text="Start Date:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.start_date = DateEntry(date_filter_frame, width=20, date_pattern='yyyy-mm-dd')
        self.start_date.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(date_filter_frame, text="End Date:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.end_date = DateEntry(date_filter_frame, width=20, date_pattern='yyyy-mm-dd')
        self.end_date.grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        
        filter_btn = ttk.Button(date_filter_frame, text="Filter by Date Range", 
                            command=self.filter_by_date_range, style="Custom.TButton")
        filter_btn.grid(row=0, column=4, padx=10, pady=5)
        
        reset_btn = ttk.Button(date_filter_frame, text="Reset Filter", 
                           command=self.load_records, style="Custom.TButton")
        reset_btn.grid(row=0, column=5, padx=10, pady=5)

        # Create a frame to contain the treeview and scrollbars
        tree_frame = ttk.Frame(self.view_tab)
        tree_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        
        # Configure tree_frame to resize properly
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Treeview
        self.tree = ttk.Treeview(tree_frame, columns=(
            'id', 'customer_name', 'unit_type', 'unit_series', 'phone_number',
            'damage_type', 'repair_type', 'cost', 'price', 'profit',
            'received_date', 'completed_date', 'pickup_date',
            'warranty_period', 'warranty_status', 'service_status'
        ), show='headings', height=15)

        # Configure columns
        columns = [
            ('id', 'ID', 50),
            ('customer_name', 'Customer Name', 120),
            ('unit_type', 'Unit Type', 80),
            ('unit_series', 'Unit Series', 100),
            ('phone_number', 'Phone Number', 100),
            ('damage_type', 'Damage Type', 120),
            ('repair_type', 'Repair Type', 120),
            ('cost', 'Cost (Rp)', 100),
            ('price', 'Price (Rp)', 100),
            ('profit', 'Profit (Rp)', 100),
            ('received_date', 'Received Date', 100),
            ('completed_date', 'Completed Date', 100),
            ('pickup_date', 'Pickup Date', 100),
            ('warranty_period', 'Warranty (days)', 100),
            ('warranty_status', 'Warranty Status', 100),
            ('service_status', 'Service Status', 100)
        ]

        for col, heading, width in columns:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, minwidth=width)

        # Vertical Scrollbar
        y_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        y_scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Horizontal Scrollbar
        x_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        x_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure the treeview to use both scrollbars
        self.tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.tree.grid(row=0, column=0, sticky='nsew')

        # Update Button
        update_btn = ttk.Button(self.view_tab, text="Update Selected Record", 
                                command=self.load_selected_record, style="Custom.TButton")
        update_btn.grid(row=3, column=0, pady=10)

        # Financial Summary Frame - Modified for Date Range
        summary_frame = ttk.LabelFrame(self.view_tab, text="Financial Summary", padding="10")
        summary_frame.grid(row=4, column=0, sticky='ew', padx=5, pady=10)
        summary_frame.columnconfigure(1, weight=1)
        summary_frame.columnconfigure(3, weight=1)
        
        # Date Range for Financial Summary - NEW FEATURE
        summary_date_frame = ttk.Frame(summary_frame)
        summary_date_frame.grid(row=0, column=0, columnspan=4, sticky='ew', padx=5, pady=5)
        summary_date_frame.columnconfigure(1, weight=1)
        summary_date_frame.columnconfigure(3, weight=1)
        
        ttk.Label(summary_date_frame, text="From:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.summary_start_date = DateEntry(summary_date_frame, width=15, date_pattern='yyyy-mm-dd')
        self.summary_start_date.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(summary_date_frame, text="To:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.summary_end_date = DateEntry(summary_date_frame, width=15, date_pattern='yyyy-mm-dd')
        self.summary_end_date.grid(row=0, column=3, padx=5, pady=5, sticky='ew')
        
        calculate_btn = ttk.Button(summary_date_frame, text="Calculate Summary", 
                               command=self.calculate_financial_summary, style="Custom.TButton")
        calculate_btn.grid(row=0, column=4, padx=10, pady=5)

        # Total Revenue and Profit
        self.total_revenue_var = tk.StringVar()
        self.total_profit_var = tk.StringVar()
        
        ttk.Label(summary_frame, text="Total Revenue:", font=('Arial', 12, 'bold')).grid(row=1, column=0, padx=20, pady=5, sticky='w')
        ttk.Label(summary_frame, textvariable=self.total_revenue_var, font=('Arial', 12)).grid(row=1, column=1, padx=20, pady=5, sticky='w')
        
        ttk.Label(summary_frame, text="Total Profit:", font=('Arial', 12, 'bold')).grid(row=1, column=2, padx=20, pady=5, sticky='w')
        ttk.Label(summary_frame, textvariable=self.total_profit_var, font=('Arial', 12)).grid(row=1, column=3, padx=20, pady=5, sticky='w')

        # Monthly Statistics
        self.month_revenue_var = tk.StringVar()
        self.month_profit_var = tk.StringVar()
        
        ttk.Label(summary_frame, text="This Month Revenue:", font=('Arial', 10)).grid(row=2, column=0, padx=20, pady=5, sticky='w')
        ttk.Label(summary_frame, textvariable=self.month_revenue_var, font=('Arial', 10)).grid(row=2, column=1, padx=20, pady=5, sticky='w')
        
        ttk.Label(summary_frame, text="This Month Profit:", font=('Arial', 10)).grid(row=2, column=2, padx=20, pady=5, sticky='w')
        ttk.Label(summary_frame, textvariable=self.month_profit_var, font=('Arial', 10)).grid(row=2, column=3, padx=20, pady=5, sticky='w')

        # Load initial data
        self.load_records()
    
    def calculate_financial_summary(self):
        """Calculate financial summary based on selected date range"""
        start_date = self.summary_start_date.get()
        end_date = self.summary_end_date.get()
        
        try:
            conn = sqlite3.connect('service_tracker.db')
            cursor = conn.cursor()
            
            # Calculate totals within date range
            cursor.execute('''
                SELECT SUM(price), SUM(profit) 
                FROM service_records 
                WHERE received_date BETWEEN ? AND ?
            ''', (start_date, end_date))
            
            total_revenue, total_profit = cursor.fetchone()
            
            # Calculate monthly totals (current month)
            first_of_month = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT SUM(price), SUM(profit) 
                FROM service_records 
                WHERE received_date >= ?
            ''', (first_of_month,))
            
            month_revenue, month_profit = cursor.fetchone()
            
            conn.close()
            
            # Update financial summary
            self.total_revenue_var.set(f"Rp {total_revenue:,.2f}" if total_revenue else "Rp 0")
            self.total_profit_var.set(f"Rp {total_profit:,.2f}" if total_profit else "Rp 0")
            self.month_revenue_var.set(f"Rp {month_revenue:,.2f}" if month_revenue else "Rp 0")
            self.month_profit_var.set(f"Rp {month_profit:,.2f}" if month_profit else "Rp 0")
            
            messagebox.showinfo("Financial Summary", 
                             f"Summary calculated for period:\n{start_date} to {end_date}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating summary: {str(e)}")

    def save_record(self):
        try:
            cost = float(self.cost.get())
            price = float(self.price.get())
            profit = price - cost
            warranty_period = int(self.warranty_period.get())

            conn = sqlite3.connect('service_tracker.db')
            cursor = conn.cursor()
            
            if hasattr(self, 'selected_record_id'):  # Update record
                cursor.execute('''
                    UPDATE service_records
                    SET customer_name = ?, unit_type = ?, unit_series = ?, phone_number = ?,
                        damage_type = ?, repair_type = ?, cost = ?, price = ?, profit = ?,
                        received_date = ?, completed_date = ?, pickup_date = ?,
                        warranty_period = ?, warranty_status = ?, service_status = ?
                    WHERE id = ?
                ''', (
                    self.customer_name.get(), self.unit_type.get(), self.unit_series.get(),
                    self.phone_number.get(), self.damage_type.get(), self.repair_type.get(),
                    cost, price, profit, self.received_date.get(),
                    self.completed_date.get(), self.pickup_date.get(),
                    warranty_period, 'Active', self.service_status.get(),
                    self.selected_record_id
                ))
                del self.selected_record_id
                self.submit_btn.config(text="Submit")
            else:  # New record
                cursor.execute('''
                    INSERT INTO service_records (
                        customer_name, unit_type, unit_series, phone_number,
                        damage_type, repair_type, cost, price, profit,
                        received_date, completed_date, pickup_date,
                        warranty_period, warranty_status, service_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.customer_name.get(), self.unit_type.get(), self.unit_series.get(),
                    self.phone_number.get(), self.damage_type.get(), self.repair_type.get(),
                    cost, price, profit, self.received_date.get(),
                    self.completed_date.get(), self.pickup_date.get(),
                    warranty_period, 'Active', self.service_status.get()
                ))
            
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Record saved successfully!")
            self.clear_form()
            self.load_records()

        except Exception as e:
            messagebox.showerror("Error", f"Error saving record: {str(e)}")

    def load_records(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load from database
        conn = sqlite3.connect('service_tracker.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM service_records')
        records = cursor.fetchall()

        # Calculate totals
        cursor.execute('SELECT SUM(price), SUM(profit) FROM service_records')
        total_revenue, total_profit = cursor.fetchone()

        # Calculate monthly totals
        first_of_month = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT SUM(price), SUM(profit) 
            FROM service_records 
            WHERE received_date >= ?
        ''', (first_of_month,))
        month_revenue, month_profit = cursor.fetchone()

        conn.close()

        # Update financial summary
        self.total_revenue_var.set(f"Rp {total_revenue:,.2f}" if total_revenue else "Rp 0")
        self.total_profit_var.set(f"Rp {total_profit:,.2f}" if total_profit else "Rp 0")
        self.month_revenue_var.set(f"Rp {month_revenue:,.2f}" if month_revenue else "Rp 0")
        self.month_profit_var.set(f"Rp {month_profit:,.2f}" if month_profit else "Rp 0")

        # Insert records into treeview
        for record in records:
            values = list(record)
            # Format currency values
            values[7] = f"Rp {values[7]:,.2f}"  # Cost
            values[8] = f"Rp {values[8]:,.2f}"  # Price
            values[9] = f"Rp {values[9]:,.2f}"  # Profit
            self.tree.insert('', 'end', values=values)

    def search_records(self):
        search_term = self.search_entry.get()
        
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect('service_tracker.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM service_records WHERE id LIKE ?', (f"%{search_term}%",))
        records = cursor.fetchall()
        conn.close()

        for record in records:
            values = list(record)
            values[7] = f"Rp {values[7]:,.2f}"
            values[8] = f"Rp {values[8]:,.2f}"
            values[9] = f"Rp {values[9]:,.2f}"
            self.tree.insert('', 'end', values=values)
    
    def filter_by_date_range(self):
        """Filter records by date range"""
        start_date = self.start_date.get()
        end_date = self.end_date.get()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = sqlite3.connect('service_tracker.db')
            cursor = conn.cursor()
            
            # Get records within the specified date range
            cursor.execute('''
                SELECT * FROM service_records 
                WHERE received_date BETWEEN ? AND ?
            ''', (start_date, end_date))
            
            records = cursor.fetchall()
            conn.close()
            
            # Calculate totals for this range
            total_revenue = sum(record[8] for record in records) if records else 0
            total_profit = sum(record[9] for record in records) if records else 0
            
            # Update summary for this range
            self.total_revenue_var.set(f"Rp {total_revenue:,.2f}")
            self.total_profit_var.set(f"Rp {total_profit:,.2f}")
            
            # Insert filtered records into treeview
            for record in records:
                values = list(record)
                values[7] = f"Rp {values[7]:,.2f}"  # Cost
                values[8] = f"Rp {values[8]:,.2f}"  # Price
                values[9] = f"Rp {values[9]:,.2f}"  # Profit
                self.tree.insert('', 'end', values=values)
                
            messagebox.showinfo("Filter Applied", 
                             f"Showing {len(records)} records between {start_date} and {end_date}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error filtering records: {str(e)}")

    def export_to_excel(self):
        start_date = self.start_date.get()
        end_date = self.end_date.get()
        
        try:
            conn = sqlite3.connect('service_tracker.db')
            
            # If date filter is active, export only filtered data
            if hasattr(self, 'date_filter_active') and self.date_filter_active:
                query = """
                    SELECT * FROM service_records 
                    WHERE received_date BETWEEN ? AND ?
                """
                df = pd.read_sql_query(query, conn, params=(start_date, end_date))
                filename = f"service_records_{start_date}_to_{end_date}.xlsx"
            else:
                # Export all data
                df = pd.read_sql_query("SELECT * FROM service_records", conn)
                filename = f"service_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
            conn.close()

            # Format currency columns
            for col in ['cost', 'price', 'profit']:
                df[col] = df[col].apply(lambda x: f"Rp {x:,.2f}")

            df.to_excel(filename, index=False)
            messagebox.showinfo("Success", f"Data exported successfully to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting data: {str(e)}")

    def clear_form(self):
        self.customer_name.delete(0, tk.END)
        self.phone_number.delete(0, tk.END)
        self.unit_type.set('')
        self.unit_series.delete(0, tk.END)
        self.damage_type.delete(0, tk.END)
        self.repair_type.delete(0, tk.END)
        self.cost.delete(0, tk.END)
        self.price.delete(0, tk.END)
        self.warranty_period.delete(0, tk.END)
        self.service_status.set('')
        if hasattr(self, 'selected_record_id'):
            del self.selected_record_id
            self.submit_btn.config(text="Submit")

    def load_selected_record(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a record to update")
            return
        
        record_id = self.tree.item(selected_item, 'values')[0]
        
        conn = sqlite3.connect('service_tracker.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM service_records WHERE id = ?', (record_id,))
        record = cursor.fetchone()
        conn.close()
        
        if record:
            # Load data into input fields
            self.selected_record_id = record_id
            self.customer_name.delete(0, tk.END)
            self.customer_name.insert(0, record[1])
            self.unit_type.set(record[2])
            self.unit_series.delete(0, tk.END)
            self.unit_series.insert(0, record[3])
            self.phone_number.delete(0, tk.END)
            self.phone_number.insert(0, record[4])
            self.damage_type.delete(0, tk.END)
            self.damage_type.insert(0, record[5])
            self.repair_type.delete(0, tk.END)
            self.repair_type.insert(0, record[6])
            self.cost.delete(0, tk.END)
            self.cost.insert(0, str(record[7]))
            self.price.delete(0, tk.END)
            self.price.insert(0, str(record[8]))
            self.received_date.set_date(record[10])
            self.completed_date.set_date(record[11])
            self.pickup_date.set_date(record[12])
            self.warranty_period.delete(0, tk.END)
            self.warranty_period.insert(0, str(record[13]))
            self.service_status.set(record[15])
            self.submit_btn.config(text="Update Record")
            self.tab_control.select(self.input_tab)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServiceTrackerApp(root)
    root.mainloop()