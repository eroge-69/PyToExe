# crime_system.py (INSECURE - with Improved UI Colors, No Case Notes)
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import csv
from datetime import datetime
from ttkthemes import ThemedTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Tejas@32',
    'database': 'crime_db'
}

class AuditLogger:
    @staticmethod
    def log(username, action):
        sql = "INSERT INTO audit_log (username, action) VALUES (%s, %s)"
        try:
            with mysql.connector.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (username, action))
                conn.commit()
        except mysql.connector.Error as err:
            print(f"Audit Log Failed: {err}")

class CrimeDAO:
    @staticmethod
    def get_connection():
        return mysql.connector.connect(**DB_CONFIG)
    @staticmethod
    def insert(crime_record):
        sql = "INSERT INTO crimes (id, crimeType, location, accusedName, officer, status) VALUES (%s, %s, %s, %s, %s, %s)"
        with CrimeDAO.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (crime_record['id'], crime_record['crimeType'], crime_record['location'],
                                     crime_record['accusedName'], crime_record['officer'], crime_record['status']))
            conn.commit()
    @staticmethod
    def update(crime_record):
        sql = "UPDATE crimes SET crimeType=%s, location=%s, accusedName=%s, officer=%s, status=%s WHERE id=%s"
        with CrimeDAO.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (crime_record['crimeType'], crime_record['location'],
                                     crime_record['accusedName'], crime_record['officer'],
                                     crime_record['status'], crime_record['id']))
            conn.commit()
    @staticmethod
    def delete(crime_id):
        sql = "DELETE FROM crimes WHERE id=%s"
        with CrimeDAO.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (crime_id,))
            conn.commit()
    @staticmethod
    def fetch_all(offset, limit):
        sql = "SELECT * FROM crimes ORDER BY created_at DESC LIMIT %s OFFSET %s"
        with CrimeDAO.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql, (limit, offset))
                return cursor.fetchall()
    @staticmethod
    def count_all():
        sql = "SELECT COUNT(*) as count FROM crimes"
        with CrimeDAO.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql)
                result = cursor.fetchone()
                return result['count'] if result else 0
    @staticmethod
    def advanced_search(params):
        sql = "SELECT * FROM crimes WHERE 1=1"
        args = []
        for key, value in params.items():
            if value:
                sql += f" AND LOWER({key}) LIKE LOWER(%s)"
                args.append(f"%{value}%")
        sql += " ORDER BY created_at DESC"
        with CrimeDAO.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql, tuple(args))
                return cursor.fetchall()
    @staticmethod
    def get_crimes_by_type():
        sql = "SELECT crimeType, COUNT(*) as count FROM crimes GROUP BY crimeType ORDER BY count DESC"
        with CrimeDAO.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
    @staticmethod
    def get_crimes_by_status():
        sql = "SELECT status, COUNT(*) as count FROM crimes GROUP BY status"
        with CrimeDAO.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql)
                return cursor.fetchall()

class UserDAO:
    @staticmethod
    def get_role_if_valid(username, password):
        sql = "SELECT role FROM users WHERE username = %s AND password = %s"
        with CrimeDAO.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql, (username, password))
                user = cursor.fetchone()
                if user:
                    return user['role']
        return None
    @staticmethod
    def get_all_users():
        sql = "SELECT id, username, role FROM users ORDER BY username"
        with CrimeDAO.get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
    @staticmethod
    def insert_user(username, role, password):
        sql = "INSERT INTO users (username, role, password) VALUES (%s, %s, %s)"
        with CrimeDAO.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (username, role, password))
            conn.commit()
    @staticmethod
    def update_user_role(username, role):
        sql = "UPDATE users SET role = %s WHERE username = %s"
        with CrimeDAO.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (role, username))
            conn.commit()
    @staticmethod
    def reset_user_password(username, password):
        sql = "UPDATE users SET password = %s WHERE username = %s"
        with CrimeDAO.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (password, username))
            conn.commit()
    @staticmethod
    def delete_user(username):
        sql = "DELETE FROM users WHERE username = %s"
        with CrimeDAO.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (username,))
            conn.commit()

class LoginFrame(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Login - Crime System (INSECURE)")
        self.geometry("380x220")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.parent.destroy)
        parent.withdraw()
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        main_frame = ttk.Frame(self, padding="20 20 20 20")
        main_frame.pack(expand=True, fill=tk.BOTH)
        ttk.Label(main_frame, text="Username:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.tf_user = ttk.Entry(main_frame, width=30)
        self.tf_user.grid(row=0, column=1, padx=5, pady=10)
        ttk.Label(main_frame, text="Password:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.pf_pass = ttk.Entry(main_frame, show="*", width=30)
        self.pf_pass.grid(row=1, column=1, padx=5, pady=10)
        self.pf_pass.bind("<Return>", lambda e: self.do_login())
        btn_login = ttk.Button(main_frame, text="Login", command=self.do_login)
        btn_login.grid(row=2, column=1, pady=20, sticky="e")
        self.tf_user.focus()
    def do_login(self):
        username = self.tf_user.get().strip()
        password = self.pf_pass.get()
        if not username or not password:
            messagebox.showwarning("Input Error", "Enter username & password.")
            return
        try:
            role = UserDAO.get_role_if_valid(username, password)
            if role:
                AuditLogger.log(username, "User logged in successfully.")
                self.destroy()
                self.parent.deiconify()
                self.parent.start_app(role, username)
            else:
                AuditLogger.log(username, "Failed login attempt.")
                messagebox.showerror("Login Failed", "Invalid username/password.")
        except mysql.connector.Error as err:
            messagebox.showerror("DB Error", f"Database error: {err}")

class CrimeRecordSystem(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc")
        self.withdraw()
        LoginFrame(self)
    def start_app(self, role, username):
        for widget in self.winfo_children():
            widget.destroy()
        self.current_role = role
        self.current_username = username
        self.init_ui()
    def init_ui(self):
        self.title(f"Crime Records - Logged in as: {self.current_username.upper()} ({self.current_role})")
        self.geometry("1366x768")
        
        style = ttk.Style(self)
        style.configure("Header.TLabel", font=("Segoe UI", 24, "bold"), foreground="#2c3e50")
        style.map("Treeview", background=[('selected', '#2980b9')], foreground=[('selected', 'white')])

        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        header = ttk.Label(main_frame, text="Crime Record Management System", style="Header.TLabel")
        header.pack(pady=10)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        records_tab = ttk.Frame(notebook)
        dashboard_tab = ttk.Frame(notebook)
        notebook.add(records_tab, text="Crime Records")
        notebook.add(dashboard_tab, text="Dashboard")
        if self.current_role == 'admin':
            user_management_tab = ttk.Frame(notebook)
            notebook.add(user_management_tab, text="User Management")
            self.setup_user_management_tab(user_management_tab)
        self.setup_records_tab(records_tab)
        self.setup_dashboard_tab(dashboard_tab)
        self.load_page(1)

    def setup_records_tab(self, parent_tab):
        top_container = ttk.Frame(parent_tab)
        top_container.pack(fill=tk.BOTH, expand=True, pady=10)
        left_frame = ttk.LabelFrame(top_container, text="Record Details", padding=15)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        form_fields = ["Crime ID:", "Crime Type:", "Location:", "Accused Name:", "Officer In Charge:", "Status:"]
        self.form_entries = {}
        for i, field in enumerate(form_fields):
            label = ttk.Label(left_frame, text=field)
            label.grid(row=i, column=0, sticky="w", pady=5)
            if field == "Crime Type:":
                self.cb_crime_type = ttk.Combobox(left_frame, values=["Theft","Murder","Fraud","Assault","Cybercrime","Other"], state="readonly")
                self.cb_crime_type.grid(row=i, column=1, sticky="ew", padx=5); self.form_entries[field] = self.cb_crime_type
            elif field == "Status:":
                self.cb_status = ttk.Combobox(left_frame, values=["Open", "Under Investigation", "Closed"], state="readonly")
                self.cb_status.grid(row=i, column=1, sticky="ew", padx=5); self.form_entries[field] = self.cb_status
            else:
                entry = ttk.Entry(left_frame, width=30)
                entry.grid(row=i, column=1, sticky="ew", padx=5); self.form_entries[field] = entry
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=len(form_fields), column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="Add", command=self.do_add).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Update", command=self.do_update).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        
        table_frame = ttk.Frame(top_container)
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        columns = ("ID", "Crime Type", "Location", "Accused", "Officer", "Status", "Created At")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns: self.table.heading(col, text=col)
        self.table.column("ID", width=80); self.table.column("Status", width=120)
        
        self.table.tag_configure('Open', background='#f8d7da', foreground='#721c24')
        self.table.tag_configure('UnderInvestigation', background='#fff3cd', foreground='#856404')
        self.table.tag_configure('Closed', background='#d4edda', foreground='#155724')
        self.table.tag_configure('oddrow', background='#ffffff')
        self.table.tag_configure('evenrow', background='#f2f2f2')

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.table.bind("<<TreeviewSelect>>", self.on_row_select)
        
        bottom_frame = ttk.LabelFrame(parent_tab, text="Search & Actions", padding=15)
        bottom_frame.pack(fill=tk.X, pady=10)
        search_frame = ttk.Frame(bottom_frame)
        search_frame.pack(fill=tk.X, expand=True, side=tk.LEFT)
        ttk.Label(search_frame, text="Location:").grid(row=0, column=0, padx=5, pady=2)
        self.search_location = ttk.Entry(search_frame); self.search_location.grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(search_frame, text="Accused:").grid(row=0, column=2, padx=5, pady=2)
        self.search_accused = ttk.Entry(search_frame); self.search_accused.grid(row=0, column=3, padx=5, pady=2)
        ttk.Label(search_frame, text="Status:").grid(row=0, column=4, padx=5, pady=2)
        self.search_status = ttk.Combobox(search_frame, values=["", "Open", "Under Investigation", "Closed"], state="readonly")
        self.search_status.grid(row=0, column=5, padx=5, pady=2); self.search_status.current(0)
        actions_frame = ttk.Frame(bottom_frame)
        actions_frame.pack(side=tk.RIGHT)
        ttk.Button(actions_frame, text="Search", command=self.do_advanced_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Refresh", command=lambda: self.load_page(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Log Out", command=self.do_logout).pack(side=tk.LEFT, padx=2)
        if self.current_role == 'admin': ttk.Button(actions_frame, text="Delete", command=self.do_delete).pack(side=tk.LEFT, padx=2)
        pagination_frame = ttk.Frame(actions_frame)
        pagination_frame.pack(side=tk.LEFT, padx=(20, 0))
        self.btn_prev = ttk.Button(pagination_frame, text="Prev", command=lambda: self.load_page(self.current_page - 1)); self.btn_prev.pack(side=tk.LEFT)
        self.lbl_page = ttk.Label(pagination_frame, text="Page 1 / 1"); self.lbl_page.pack(side=tk.LEFT, padx=5)
        self.btn_next = ttk.Button(pagination_frame, text="Next", command=lambda: self.load_page(self.current_page + 1)); self.btn_next.pack(side=tk.LEFT)

    def refresh_table(self, records):
        for row in self.table.get_children():
            self.table.delete(row)
        for i, record in enumerate(records):
            created_at = record['created_at'].strftime('%Y-%m-%d %H:%M:%S') if record.get('created_at') else ''
            
            status = record['status']
            status_tag = status.replace(' ', '')
            row_tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            self.table.insert("", tk.END, values=(record['id'], record['crimeType'], record['location'],
                                                  record['accusedName'], record['officer'], status, created_at),
                              tags=(row_tag, status_tag))

    def setup_dashboard_tab(self, parent_tab):
        self.dashboard_frame = ttk.Frame(parent_tab, padding=10)
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)
        self.refresh_dashboard()

    def refresh_dashboard(self):
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()
        try:
            data1 = CrimeDAO.get_crimes_by_type()
            if not data1: raise ValueError("No crime data to display.")
            fig1 = Figure(figsize=(7, 5), dpi=100, facecolor='#f0f0f0')
            ax1 = fig1.add_subplot(111)
            ax1.set_facecolor('#f0f0f0')
            types = [row['crimeType'] for row in data1]
            counts = [row['count'] for row in data1]
            ax1.bar(types, counts, color='cornflowerblue')
            ax1.set_title("Crimes by Type", color='#2c3e50')
            ax1.set_ylabel("Number of Cases", color='#2c3e50')
            ax1.tick_params(axis='x', rotation=45, colors='#2c3e50')
            ax1.tick_params(axis='y', colors='#2c3e50')
            fig1.tight_layout()
            canvas1 = FigureCanvasTkAgg(fig1, master=self.dashboard_frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        except Exception as e:
            ttk.Label(self.dashboard_frame, text=f"Could not load Crime Type chart:\n{e}").pack(side=tk.LEFT, padx=10)
        try:
            data2 = CrimeDAO.get_crimes_by_status()
            if not data2: raise ValueError("No crime data to display.")
            fig2 = Figure(figsize=(5, 5), dpi=100, facecolor='#f0f0f0')
            ax2 = fig2.add_subplot(111)
            ax2.set_facecolor('#f0f0f0')
            statuses = [row['status'] for row in data2]
            counts = [row['count'] for row in data2]
            ax2.pie(counts, labels=statuses, autopct='%1.1f%%', startangle=140, colors=['#f8d7da','#fff3cd','#d4edda'],
                    textprops={'color': '#2c3e50'})
            ax2.set_title("Case Status Overview", color='#2c3e50')
            fig2.tight_layout()
            canvas2 = FigureCanvasTkAgg(fig2, master=self.dashboard_frame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        except Exception as e:
            ttk.Label(self.dashboard_frame, text=f"Could not load Case Status chart:\n{e}").pack(side=tk.RIGHT, padx=10)

    def load_page(self, page):
        self.page_size = 10
        self.current_page = 1
        try:
            self.total_rows = CrimeDAO.count_all()
            total_pages = max(1, (self.total_rows + self.page_size - 1) // self.page_size)
            if page < 1: page = 1
            if page > total_pages: page = total_pages
            self.current_page = page
            offset = (self.current_page - 1) * self.page_size
            records = CrimeDAO.fetch_all(offset, self.page_size)
            self.refresh_table(records)
            self.lbl_page.config(text=f"Page {self.current_page} / {total_pages} (Total: {self.total_rows})")
            self.btn_prev.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
            self.btn_next.config(state=tk.NORMAL if self.current_page < total_pages else tk.DISABLED)
            self.search_location.delete(0, tk.END); self.search_accused.delete(0, tk.END); self.search_status.set("")
        except mysql.connector.Error as err:
            messagebox.showerror("DB Error", f"Failed to load records: {err}")

    def on_row_select(self, event):
        selected_item = self.table.focus()
        if not selected_item: return
        values = self.table.item(selected_item, 'values')
        self.clear_form()
        self.form_entries["Crime ID:"].insert(0, values[0])
        self.form_entries["Crime Type:"].set(values[1])
        self.form_entries["Location:"].insert(0, values[2])
        self.form_entries["Accused Name:"].insert(0, values[3])
        self.form_entries["Officer In Charge:"].insert(0, values[4])
        self.form_entries["Status:"].set(values[5])

    def get_form_data(self):
        return { 'id': self.form_entries["Crime ID:"].get().strip(), 'crimeType': self.form_entries["Crime Type:"].get(),
                 'location': self.form_entries["Location:"].get().strip(), 'accusedName': self.form_entries["Accused Name:"].get().strip(),
                 'officer': self.form_entries["Officer In Charge:"].get().strip(), 'status': self.form_entries["Status:"].get() }

    def do_add(self):
        data = self.get_form_data()
        if not data['id']: messagebox.showwarning("Input Error", "Crime ID is required."); return
        try:
            CrimeDAO.insert(data)
            AuditLogger.log(self.current_username, f"Added record with ID: {data['id']}")
            messagebox.showinfo("Success", "Record inserted successfully.")
            self.clear_form(); self.load_page(1)
            self.refresh_dashboard()
        except mysql.connector.Error as err: messagebox.showerror("Insert Failed", f"Failed to insert record: {err}")

    def do_update(self):
        data = self.get_form_data()
        if not data['id']: messagebox.showwarning("Input Error", "Select a record to update."); return
        try:
            CrimeDAO.update(data)
            AuditLogger.log(self.current_username, f"Updated record with ID: {data['id']}")
            messagebox.showinfo("Success", "Record updated successfully.")
            self.clear_form(); self.load_page(self.current_page)
            self.refresh_dashboard()
        except mysql.connector.Error as err: messagebox.showerror("Update Failed", f"Failed to update record: {err}")

    def do_delete(self):
        selected_item = self.table.focus()
        if not selected_item: messagebox.showwarning("Selection Error", "Select a row to delete."); return
        crime_id = self.table.item(selected_item, 'values')[0]
        if messagebox.askyesno("Confirm Delete", f"Delete record {crime_id}?"):
            try:
                CrimeDAO.delete(crime_id)
                AuditLogger.log(self.current_username, f"Deleted record with ID: {crime_id}")
                messagebox.showinfo("Success", "Record deleted.")
                self.load_page(1)
                self.refresh_dashboard()
            except mysql.connector.Error as err: messagebox.showerror("Delete Failed", f"Failed to delete record: {err}")

    def do_logout(self):
        self.withdraw()
        LoginFrame(self)

    def do_advanced_search(self):
        params = { 'location': self.search_location.get().strip(), 'accusedName': self.search_accused.get().strip(),
                   'status': self.search_status.get() }
        try:
            records = CrimeDAO.advanced_search(params)
            self.refresh_table(records)
            self.lbl_page.config(text=f"Search results ({len(records)} found)")
            self.btn_prev.config(state=tk.DISABLED); self.btn_next.config(state=tk.DISABLED)
        except mysql.connector.Error as err: messagebox.showerror("Search Failed", f"Failed to search records: {err}")
        
    def clear_form(self):
        for widget in self.form_entries.values():
            if isinstance(widget, ttk.Entry): widget.delete(0, tk.END)
            elif isinstance(widget, ttk.Combobox): widget.set("")
        self.table.selection_remove(self.table.focus())

    def setup_user_management_tab(self, parent_tab):
        main_container = ttk.Frame(parent_tab, padding=10)
        main_container.pack(fill=tk.BOTH, expand=True)
        form_frame = ttk.LabelFrame(main_container, text="User Details", padding=15)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), anchor='n')
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        self.user_username_entry = ttk.Entry(form_frame, width=30)
        self.user_username_entry.grid(row=0, column=1, padx=5)
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.user_password_entry = ttk.Entry(form_frame, width=30)
        self.user_password_entry.grid(row=1, column=1, padx=5)
        ttk.Label(form_frame, text="(for new users or reset)").grid(row=2, column=1, sticky="w", padx=5)
        ttk.Label(form_frame, text="Role:").grid(row=3, column=0, sticky="w", pady=5)
        self.user_role_combo = ttk.Combobox(form_frame, values=["officer", "admin"], state="readonly")
        self.user_role_combo.grid(row=3, column=1, sticky="ew", padx=5)
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="Add User", command=self.do_add_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Update Role", command=self.do_update_user_role).pack(side=tk.LEFT, padx=5)
        reset_btn_frame = ttk.Frame(form_frame)
        reset_btn_frame.grid(row=5, column=0, columnspan=2, pady=5)
        ttk.Button(reset_btn_frame, text="Reset Password", command=self.do_reset_user_password).pack()
        delete_btn_frame = ttk.Frame(form_frame)
        delete_btn_frame.grid(row=6, column=0, columnspan=2, pady=(20,5))
        ttk.Button(delete_btn_frame, text="Delete User", command=self.do_delete_user).pack()
        table_frame = ttk.Frame(main_container)
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        user_columns = ("ID", "Username", "Role")
        self.user_table = ttk.Treeview(table_frame, columns=user_columns, show="headings")
        for col in user_columns: self.user_table.heading(col, text=col)
        self.user_table.column("ID", width=50)
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.user_table.yview)
        self.user_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.user_table.pack(fill=tk.BOTH, expand=True)
        self.user_table.bind("<<TreeviewSelect>>", self.on_user_select)
        self.refresh_user_table()
    def refresh_user_table(self):
        self.user_username_entry.delete(0, tk.END)
        self.user_password_entry.delete(0, tk.END)
        self.user_role_combo.set('')
        for row in self.user_table.get_children(): self.user_table.delete(row)
        try:
            users = UserDAO.get_all_users()
            for user in users:
                self.user_table.insert("", tk.END, values=(user['id'], user['username'], user['role']))
        except mysql.connector.Error as err:
            messagebox.showerror("DB Error", f"Could not load users: {err}")
    def on_user_select(self, event):
        selected_item = self.user_table.focus()
        if not selected_item: return
        values = self.user_table.item(selected_item, 'values')
        self.user_username_entry.delete(0, tk.END)
        self.user_username_entry.insert(0, values[1])
        self.user_role_combo.set(values[2])
        self.user_password_entry.delete(0, tk.END)
    def do_add_user(self):
        username = self.user_username_entry.get().strip()
        password = self.user_password_entry.get().strip()
        role = self.user_role_combo.get()
        if not all([username, password, role]):
            messagebox.showwarning("Input Error", "All fields are required to add a new user.")
            return
        try:
            UserDAO.insert_user(username, role, password)
            AuditLogger.log(self.current_username, f"Added new user: {username}")
            messagebox.showinfo("Success", f"User '{username}' created successfully.")
            self.refresh_user_table()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to add user. Is the username unique?\n{err}")
    def do_update_user_role(self):
        username = self.user_username_entry.get().strip()
        role = self.user_role_combo.get()
        if not all([username, role]):
            messagebox.showwarning("Input Error", "Select a user from the table and a new role to update.")
            return
        if username == self.current_username and role != 'admin':
            messagebox.showerror("Error", "You cannot remove your own admin role.")
            return
        try:
            UserDAO.update_user_role(username, role)
            AuditLogger.log(self.current_username, f"Updated role for user: {username} to {role}")
            messagebox.showinfo("Success", f"Role for '{username}' updated successfully.")
            self.refresh_user_table()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to update user role.\n{err}")
    def do_reset_user_password(self):
        username = self.user_username_entry.get().strip()
        password = self.user_password_entry.get().strip()
        if not all([username, password]):
            messagebox.showwarning("Input Error", "Select a user from the table and enter a new password to reset.")
            return
        if messagebox.askyesno("Confirm Reset", f"Are you sure you want to reset the password for '{username}'?"):
            try:
                UserDAO.reset_user_password(username, password)
                AuditLogger.log(self.current_username, f"Reset password for user: {username}")
                messagebox.showinfo("Success", f"Password for '{username}' has been reset.")
                self.user_password_entry.delete(0, tk.END)
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to reset password.\n{err}")
    def do_delete_user(self):
        username = self.user_username_entry.get().strip()
        if not username:
            messagebox.showwarning("Input Error", "Select a user from the table to delete.")
            return
        if username == self.current_username:
            messagebox.showerror("Error", "You cannot delete your own account while logged in.")
            return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete user '{username}'?"):
            try:
                UserDAO.delete_user(username)
                AuditLogger.log(self.current_username, f"Deleted user: {username}")
                messagebox.showinfo("Success", f"User '{username}' has been deleted.")
                self.refresh_user_table()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to delete user.\n{err}")

if __name__ == "__main__":
    app = CrimeRecordSystem()
    app.mainloop()