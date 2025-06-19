import psycopg2
from datetime import datetime
import threading
import csv
import pandas as pd
from fpdf import FPDF
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from psycopg2 import sql, errors

class AccountingSystem:
    def __init__(self, db_name='accounting', user='postgres', password='qwe123!@#', host='localhost', port='5432'):
        self.db_params = {
            'dbname': db_name,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
        self.lock = threading.Lock()
        self._initialize_database()

    def _get_connection(self):
        """Επιστρέφει μια νέα σύνδεση με τη βάση δεδομένων"""
        return psycopg2.connect(**self.db_params)

    def _initialize_database(self):
        with self.lock, self._get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    # Δημιουργία πίνακα προμηθευτών
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS suppliers (
                            id SERIAL PRIMARY KEY,
                            vat_number TEXT UNIQUE,
                            name TEXT NOT NULL,
                            address TEXT,
                            phone TEXT,
                            email TEXT
                        )
                    ''')
                    
                    # Δημιουργία πίνακα συμβάσεων
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS contracts (
                            id SERIAL PRIMARY KEY,
                            supplier_id INTEGER NOT NULL,
                            amount NUMERIC(12, 2) NOT NULL,
                            start_date DATE NOT NULL,
                            end_date DATE NOT NULL,
                            payment_terms TEXT,
                            remaining_amount NUMERIC(12, 2) NOT NULL,
                            FOREIGN KEY (supplier_id) REFERENCES suppliers (id) ON DELETE CASCADE
                        )
                    ''')
                    
                    # Δημιουργία πίνακα κινήσεων
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS transactions (
                            id SERIAL PRIMARY KEY,
                            date DATE NOT NULL,
                            amount NUMERIC(12, 2) NOT NULL,
                            transaction_type TEXT NOT NULL,
                            description TEXT,
                            contract_id INTEGER,
                            FOREIGN KEY (contract_id) REFERENCES contracts (id) ON DELETE SET NULL
                        )
                    ''')
                    
                    # Δημιουργία πίνακα υπολοίπων
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS balances (
                            id SERIAL PRIMARY KEY,
                            date DATE NOT NULL,
                            balance NUMERIC(12, 2) NOT NULL
                        )
                    ''')
                    
                    conn.commit()
                except errors.DuplicateTable:
                    conn.rollback()
                except Exception as e:
                    conn.rollback()
                    raise e

    # ========== Διαχείριση Προμηθευτών ==========
    def add_supplier(self, vat_number, name, address=None, phone=None, email=None):
        with self.lock, self._get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute('''
                        INSERT INTO suppliers (vat_number, name, address, phone, email)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    ''', (vat_number, name, address, phone, email))
                    conn.commit()
                    return cursor.fetchone()[0]
                except errors.UniqueViolation:
                    conn.rollback()
                    print("Προμηθευτής με αυτό το ΑΦΜ υπάρχει ήδη.")
                    return False
                except Exception as e:
                    conn.rollback()
                    print(f"Σφάλμα κατά την προσθήκη προμηθευτή: {e}")
                    return False

    def get_supplier_by_vat(self, vat_number):
        with self.lock, self._get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute('''
                        SELECT * FROM suppliers WHERE vat_number=%s
                    ''', (vat_number,))
                    supplier = cursor.fetchone()
                    
                    if supplier:
                        # Λήψη συμβάσεων για τον προμηθευτή
                        cursor.execute('''
                            SELECT * FROM contracts WHERE supplier_id=%s
                        ''', (supplier[0],))
                        contracts = cursor.fetchall()
                        
                        supplier_data = {
                            'id': supplier[0],
                            'vat_number': supplier[1],
                            'name': supplier[2],
                            'address': supplier[3],
                            'phone': supplier[4],
                            'email': supplier[5],
                            'contracts': contracts
                        }
                        return supplier_data
                    return None
                except Exception as e:
                    print(f"Σφάλμα κατά την ανάκτηση προμηθευτή: {e}")
                    return None

    # ========== Διαχείριση Συμβάσεων ==========
    def add_contract(self, supplier_id, amount, start_date, end_date, payment_terms=None):
        with self.lock, self._get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute('''
                        INSERT INTO contracts 
                        (supplier_id, amount, start_date, end_date, payment_terms, remaining_amount)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                    ''', (supplier_id, amount, start_date, end_date, payment_terms, amount))
                    conn.commit()
                    return cursor.fetchone()[0]
                except Exception as e:
                    conn.rollback()
                    print(f"Σφάλμα κατά την προσθήκη σύμβασης: {e}")
                    return False

    def get_active_contracts(self):
        with self.lock, self._get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    today = datetime.now().strftime('%Y-%m-%d')
                    cursor.execute('''
                        SELECT c.*, s.name, s.vat_number 
                        FROM contracts c
                        JOIN suppliers s ON c.supplier_id = s.id
                        WHERE c.end_date >= %s
                    ''', (today,))
                    return cursor.fetchall()
                except Exception as e:
                    print(f"Σφάλμα κατά την ανάκτηση συμβάσεων: {e}")
                    return []

    # ========== Διαχείριση Κινήσεων ==========
    def add_transaction(self, amount, transaction_type, description=None, contract_id=None):
        with self.lock, self._get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    # Καταχώρηση κίνησης
                    date = datetime.now().strftime('%Y-%m-%d')
                    cursor.execute('''
                        INSERT INTO transactions 
                        (date, amount, transaction_type, description, contract_id)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    ''', (date, amount, transaction_type, description, contract_id))
                    transaction_id = cursor.fetchone()[0]
                    
                    # Ενημέρωση υπολοίπου σύμβασης (αν υπάρχει contract_id)
                    if contract_id:
                        cursor.execute('''
                            UPDATE contracts 
                            SET remaining_amount = remaining_amount - %s
                            WHERE id = %s
                        ''', (amount, contract_id))
                    
                    # Ενημέρωση γενικού υπολοίπου
                    self._update_balance(conn, cursor, amount, transaction_type)
                    
                    conn.commit()
                    return transaction_id
                except Exception as e:
                    conn.rollback()
                    print(f"Σφάλμα κατά την προσθήκη συναλλαγής: {e}")
                    return False

    def _update_balance(self, conn, cursor, amount, transaction_type):
        try:
            # Λήψη τελευταίου υπολοίπου
            cursor.execute('''
                SELECT balance FROM balances 
                ORDER BY date DESC LIMIT 1
            ''')
            last_balance = cursor.fetchone()
            
            current_balance = last_balance[0] if last_balance else 0.0
            
            # Υπολογισμός νέου υπολοίπου
            if transaction_type in ('ΠΛΗΡΩΜΗ', 'ΕΞΟΔΟ'):
                new_balance = current_balance - amount
            else:  # Είσοδος
                new_balance = current_balance + amount
            
            # Καταχώρηση νέου υπολοίπου
            date = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                INSERT INTO balances (date, balance)
                VALUES (%s, %s)
            ''', (date, new_balance))
        except Exception as e:
            print(f"Σφάλμα κατά την ενημέρωση υπολοίπου: {e}")
            raise

    def get_transactions(self, start_date=None, end_date=None, transaction_type=None):
        with self.lock, self._get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    query = '''
                        SELECT t.*, s.name as supplier_name, c.amount as contract_amount
                        FROM transactions t
                        LEFT JOIN contracts c ON t.contract_id = c.id
                        LEFT JOIN suppliers s ON c.supplier_id = s.id
                        WHERE 1=1
                    '''
                    params = []
                    
                    if start_date:
                        query += ' AND t.date >= %s'
                        params.append(start_date)
                    
                    if end_date:
                        query += ' AND t.date <= %s'
                        params.append(end_date)
                    
                    if transaction_type:
                        query += ' AND t.transaction_type = %s'
                        params.append(transaction_type)
                    
                    query += ' ORDER BY t.date DESC'
                    
                    cursor.execute(query, params)
                    return cursor.fetchall()
                except Exception as e:
                    print(f"Σφάλμα κατά την ανάκτηση συναλλαγών: {e}")
                    return []

    # ========== Αναφορές ==========
    def get_balance_report(self):
        with self.lock, self._get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute('''
                        SELECT balance FROM balances 
                        ORDER BY date DESC LIMIT 1
                    ''')
                    current_balance = cursor.fetchone()
                    
                    cursor.execute('''
                        SELECT c.id, s.name, c.amount, c.remaining_amount, 
                               (c.amount - c.remaining_amount) as paid_amount
                        FROM contracts c
                        JOIN suppliers s ON c.supplier_id = s.id
                        WHERE c.end_date >= CURRENT_DATE
                    ''')
                    contracts = cursor.fetchall()
                    
                    return {
                        'current_balance': current_balance[0] if current_balance else 0.0,
                        'contracts': contracts
                    }
                except Exception as e:
                    print(f"Σφάλμα κατά την ανάκτηση αναφοράς υπολοίπου: {e}")
                    return {
                        'current_balance': 0.0,
                        'contracts': []
                    }

class EnhancedAccountingSystem(AccountingSystem):
    def __init__(self, db_name='accounting', user='postgres', password='qwe123!@#', host='localhost', port='5432'):
        super().__init__(db_name, user, password, host, port)
    
    # ========== Εισαγωγή από CSV ==========
    def import_from_csv(self, file_path, import_type):
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                if import_type == 'suppliers':
                    for row in reader:
                        self.add_supplier(
                            vat_number=row.get('ΑΦΜ'),
                            name=row.get('Ονομασία'),
                            address=row.get('Διεύθυνση'),
                            phone=row.get('Τηλέφωνο'),
                            email=row.get('Email')
                        )
                elif import_type == 'transactions':
                    for row in reader:
                        self.add_transaction(
                            amount=float(row.get('Ποσό', 0)),
                            transaction_type=row.get('Τύπος'),
                            description=row.get('Περιγραφή'),
                            contract_id=int(row.get('ID Σύμβασης', 0)) if row.get('ID Σύμβασης') else None
                        )
                
                return True
        except Exception as e:
            print(f"Σφάλμα κατά την εισαγωγή: {str(e)}")
            return False

    # ========== Εξαγωγή σε Excel ==========
    def export_to_excel(self, file_path, export_type):
        try:
            with self.lock, self._get_connection() as conn:
                if export_type == 'transactions':
                    query = '''
                        SELECT t.date, t.amount, t.transaction_type, t.description, 
                               s.name as supplier_name, c.amount as contract_amount
                        FROM transactions t
                        LEFT JOIN contracts c ON t.contract_id = c.id
                        LEFT JOIN suppliers s ON c.supplier_id = s.id
                        ORDER BY t.date DESC
                    '''
                elif export_type == 'suppliers':
                    query = 'SELECT * FROM suppliers'
                elif export_type == 'contracts':
                    query = '''
                        SELECT c.*, s.name as supplier_name 
                        FROM contracts c
                        JOIN suppliers s ON c.supplier_id = s.id
                    '''
                
                df = pd.read_sql_query(query, conn)
                df.to_excel(file_path, index=False)
                return True
        except Exception as e:
            print(f"Σφάλμα κατά την εξαγωγή: {str(e)}")
            return False

    # ========== Εξαγωγή σε PDF ==========
    def export_to_pdf(self, file_path, report_type):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            if report_type == 'balance':
                report = self.get_balance_report()
                
                pdf.cell(200, 10, txt="Αναφορά Υπολοίπων", ln=1, align='C')
                pdf.cell(200, 10, txt=f"Ημερομηνία: {datetime.now().strftime('%Y-%m-%d')}", ln=1)
                pdf.cell(200, 10, txt=f"Τρέχον υπόλοιπο: {report['current_balance']:.2f}€", ln=1)
                
                pdf.ln(10)
                pdf.cell(200, 10, txt="Συμβάσεις Προμηθευτών", ln=1)
                
                # Πίνακας συμβάσεων
                pdf.set_font("Arial", size=10)
                col_widths = [40, 50, 30, 30, 30]
                headers = ["Προμηθευτής", "Συνολικό Ποσό", "Πληρωμένο", "Υπόλοιπο", "Ποσοστό"]
                
                # Κεφαλίδες
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 10, txt=header, border=1)
                pdf.ln()
                
                # Δεδομένα
                for contract in report['contracts']:
                    paid = contract[2] - contract[3]
                    percentage = (paid / contract[2]) * 100 if contract[2] > 0 else 0
                    
                    data = [
                        contract[1],
                        f"{contract[2]:.2f}€",
                        f"{paid:.2f}€",
                        f"{contract[3]:.2f}€",
                        f"{percentage:.1f}%"
                    ]
                    
                    for i, item in enumerate(data):
                        pdf.cell(col_widths[i], 10, txt=item, border=1)
                    pdf.ln()
            
            pdf.output(file_path)
            return True
        except Exception as e:
            print(f"Σφάλμα κατά τη δημιουργία PDF: {str(e)}")
            return False

class AccountingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Λογιστικό Πρόγραμμα")
        self.root.geometry("1000x700")
        
        self.system = EnhancedAccountingSystem()
        
        self.create_widgets()
        self.show_main_frame()
        self.setup_context_menus()  # Προσθήκη αυτής της γραμμής

    def setup_context_menus(self):
        # Δημιουργία βασικού μενού
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Αντιγραφή", command=self.copy_to_clipboard)
        
        # Σύνδεση με widgets
        self.suppliers_tree.bind("<Button-3>", self.show_context_menu)
        # Προσθέστε και άλλα widgets αν χρειάζεται

    def show_context_menu(self, event):
        """Εμφανίζει το μενού δεξιού κλικ"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def copy_to_clipboard(self):
        """Αντιγραφή επιλεγμένου κειμένου"""
        widget = self.root.focus_get()
        
        # Για TreeView
        if widget == self.suppliers_tree:
            selected_item = widget.focus()
            if selected_item:
                values = widget.item(selected_item)['values']
                self.root.clipboard_clear()
                self.root.clipboard_append(" ".join(str(x) for x in values))
        
        # Για Entry/Text widgets
        elif isinstance(widget, (tk.Entry, tk.Text)):
            widget.event_generate("<<Copy>>")
    
    def create_widgets(self):
        # Κύριο Frame
        self.main_frame = ttk.Frame(self.root)
        
        # Κουμπιά κύριας οθόνης
        ttk.Button(self.main_frame, text="Διαχείριση Προμηθευτών", 
                  command=self.show_suppliers_frame).pack(pady=5, fill=tk.X)
        ttk.Button(self.main_frame, text="Διαχείριση Συμβάσεων", 
                  command=self.show_contracts_frame).pack(pady=5, fill=tk.X)
        ttk.Button(self.main_frame, text="Κινήσεις & Πληρωμές", 
                  command=self.show_transactions_frame).pack(pady=5, fill=tk.X)
        ttk.Button(self.main_frame, text="Αναφορά Υπολοίπων", 
                  command=self.show_reports_frame).pack(pady=5, fill=tk.X)
        ttk.Button(self.main_frame, text="Εισαγωγή/Εξαγωγή", 
                  command=self.show_import_export_frame).pack(pady=5, fill=tk.X)
        
        # Frame Προμηθευτών
        self.suppliers_frame = ttk.Frame(self.root)
        self.setup_suppliers_frame()
        
        # Frame Συμβάσεων
        self.contracts_frame = ttk.Frame(self.root)
        self.setup_contracts_frame()
        
        # Frame Κινήσεων
        self.transactions_frame = ttk.Frame(self.root)
        self.setup_transactions_frame()
        
        # Frame Αναφορών
        self.reports_frame = ttk.Frame(self.root)
        self.setup_reports_frame()
        
        # Frame Εισαγωγής/Εξαγωγής
        self.import_export_frame = ttk.Frame(self.root)
        self.setup_import_export_frame()
    
    def show_main_frame(self):
        self.hide_all_frames()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_suppliers_frame(self):
        self.hide_all_frames()
        self.suppliers_frame.pack(fill=tk.BOTH, expand=True)
        self.refresh_suppliers_list()
    
    def show_contracts_frame(self):
        self.hide_all_frames()
        self.contracts_frame.pack(fill=tk.BOTH, expand=True)
        self.refresh_contracts_list()
    
    def show_transactions_frame(self):
        self.hide_all_frames()
        self.transactions_frame.pack(fill=tk.BOTH, expand=True)
        self.refresh_transactions_list()
    
    def show_reports_frame(self):
        self.hide_all_frames()
        self.reports_frame.pack(fill=tk.BOTH, expand=True)
    
    def show_import_export_frame(self):
        self.hide_all_frames()
        self.import_export_frame.pack(fill=tk.BOTH, expand=True)
    
    def hide_all_frames(self):
        for frame in [self.main_frame, self.suppliers_frame, self.contracts_frame,
                     self.transactions_frame, self.reports_frame, self.import_export_frame]:
            frame.pack_forget()
    
    def setup_suppliers_frame(self):
        ttk.Label(self.suppliers_frame, text="Διαχείριση Προμηθευτών", font=('Arial', 14)).pack(pady=10)
        
        # Πίνακας προμηθευτών
        self.suppliers_tree = ttk.Treeview(self.suppliers_frame, columns=('vat', 'name', 'address', 'phone', 'email'), show='headings')
        self.suppliers_tree.heading('vat', text='ΑΦΜ')
        self.suppliers_tree.heading('name', text='Ονομασία')
        self.suppliers_tree.heading('address', text='Διεύθυνση')
        self.suppliers_tree.heading('phone', text='Τηλέφωνο')
        self.suppliers_tree.heading('email', text='Email')
        self.suppliers_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Φόρμα προσθήκης προμηθευτή
        form_frame = ttk.Frame(self.suppliers_frame)
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(form_frame, text="ΑΦΜ:").grid(row=0, column=0, sticky=tk.W)
        self.vat_entry = ttk.Entry(form_frame)
        self.vat_entry.grid(row=0, column=1, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Ονομασία:").grid(row=1, column=0, sticky=tk.W)
        self.name_entry = ttk.Entry(form_frame)
        self.name_entry.grid(row=1, column=1, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Διεύθυνση:").grid(row=2, column=0, sticky=tk.W)
        self.address_entry = ttk.Entry(form_frame)
        self.address_entry.grid(row=2, column=1, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Τηλέφωνο:").grid(row=3, column=0, sticky=tk.W)
        self.phone_entry = ttk.Entry(form_frame)
        self.phone_entry.grid(row=3, column=1, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Email:").grid(row=4, column=0, sticky=tk.W)
        self.email_entry = ttk.Entry(form_frame)
        self.email_entry.grid(row=4, column=1, sticky=tk.EW)
        
        button_frame = ttk.Frame(self.suppliers_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Προσθήκη", command=self.add_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Αναζήτηση με ΑΦΜ", command=self.search_supplier).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Επιστροφή", command=self.show_main_frame).pack(side=tk.RIGHT)

        # Προσθήκη μενού δεξιού κλικ
        self.suppliers_menu = tk.Menu(self.root, tearoff=0)
        self.suppliers_menu.add_command(label="Αντιγραφή", command=lambda: self.copy_from_treeview(self.suppliers_tree))
        
        # Σύνδεση μενού με treeview
        self.suppliers_tree.bind("<Button-3>", lambda e: self.show_context_menu(e, self.suppliers_menu))

    def copy_from_treeview(self, tree):
        selected_item = tree.focus()
        if selected_item:
            values = tree.item(selected_item)['values']
            if values:
                self.root.clipboard_clear()
                self.root.clipboard_append("\t".join(str(x) for x in values))

    
    def refresh_suppliers_list(self):
        for item in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(item)
        
        with self.system.lock:
            conn = self.system._get_connection()  # Χρήση της μεθόδου σύνδεσης του AccountingSystem
            cursor = conn.cursor()
            cursor.execute('SELECT vat_number, name, address, phone, email FROM suppliers')
            for row in cursor.fetchall():
                self.suppliers_tree.insert('', tk.END, values=row)
            conn.close()  # ή χρήση context manager (with)
    
    def add_supplier(self):
        vat = self.vat_entry.get()
        name = self.name_entry.get()
        address = self.address_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        
        if not vat or not name:
            messagebox.showerror("Σφάλμα", "Τα πεδία ΑΦΜ και Ονομασία είναι υποχρεωτικά")
            return
        
        if self.system.add_supplier(vat, name, address, phone, email):
            messagebox.showinfo("Επιτυχία", "Ο προμηθευτής προστέθηκε με επιτυχία")
            self.refresh_suppliers_list()
            self.vat_entry.delete(0, tk.END)
            self.name_entry.delete(0, tk.END)
            self.address_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
    
    def search_supplier(self):
        vat = self.vat_entry.get()
        if not vat:
            messagebox.showerror("Σφάλμα", "Παρακαλώ εισάγετε ΑΦΜ για αναζήτηση")
            return
        
        supplier = self.system.get_supplier_by_vat(vat)
        if supplier:
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, supplier['name'])
            self.address_entry.delete(0, tk.END)
            self.address_entry.insert(0, supplier.get('address', ''))
            self.phone_entry.delete(0, tk.END)
            self.phone_entry.insert(0, supplier.get('phone', ''))
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, supplier.get('email', ''))
        else:
            messagebox.showinfo("Πληροφορία", "Δεν βρέθηκε προμηθευτής με αυτό το ΑΦΜ")
    
    def setup_contracts_frame(self):
        ttk.Label(self.contracts_frame, text="Διαχείριση Συμβάσεων", font=('Arial', 14)).pack(pady=10)
        
        # Πίνακας συμβάσεων
        self.contracts_tree = ttk.Treeview(self.contracts_frame, columns=('id', 'supplier', 'amount', 'start', 'end', 'remaining'), show='headings')
        self.contracts_tree.heading('id', text='ID')
        self.contracts_tree.heading('supplier', text='Προμηθευτής')
        self.contracts_tree.heading('amount', text='Ποσό')
        self.contracts_tree.heading('start', text='Έναρξη')
        self.contracts_tree.heading('end', text='Λήξη')
        self.contracts_tree.heading('remaining', text='Υπόλοιπο')
        self.contracts_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Φόρμα προσθήκης σύμβασης
        form_frame = ttk.Frame(self.contracts_frame)
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(form_frame, text="ΑΦΜ Προμηθευτή:").grid(row=0, column=0, sticky=tk.W)
        self.contract_vat_entry = ttk.Entry(form_frame)
        self.contract_vat_entry.grid(row=0, column=1, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Ποσό:").grid(row=1, column=0, sticky=tk.W)
        self.contract_amount_entry = ttk.Entry(form_frame)
        self.contract_amount_entry.grid(row=1, column=1, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Ημ/νία Έναρξης:").grid(row=2, column=0, sticky=tk.W)
        self.contract_start_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
        self.contract_start_entry.grid(row=2, column=1, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Ημ/νία Λήξης:").grid(row=3, column=0, sticky=tk.W)
        self.contract_end_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
        self.contract_end_entry.grid(row=3, column=1, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Όροι Πληρωμής:").grid(row=4, column=0, sticky=tk.W)
        self.contract_terms_entry = ttk.Entry(form_frame)
        self.contract_terms_entry.grid(row=4, column=1, sticky=tk.EW)
        
        button_frame = ttk.Frame(self.contracts_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Προσθήκη", command=self.add_contract).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Επιστροφή", command=self.show_main_frame).pack(side=tk.RIGHT)
    
    def refresh_contracts_list(self):
        for item in self.contracts_tree.get_children():
            self.contracts_tree.delete(item)
        
        contracts = self.system.get_active_contracts()
        for contract in contracts:
            self.contracts_tree.insert('', tk.END, values=(
                contract[0],  # ID
                contract[8],  # Όνομα προμηθευτή
                f"{contract[2]:.2f}€",  # Ποσό
                contract[3],  # Έναρξη
                contract[4],  # Λήξη
                f"{contract[6]:.2f}€"   # Υπόλοιπο
            ))
    
    def add_contract(self):
        vat = self.contract_vat_entry.get()
        amount = self.contract_amount_entry.get()
        start_date = self.contract_start_entry.get()
        end_date = self.contract_end_entry.get()
        terms = self.contract_terms_entry.get()
        
        if not vat or not amount or not start_date or not end_date:
            messagebox.showerror("Σφάλμα", "Τα πεδία ΑΦΜ, Ποσό και Ημερομηνίες είναι υποχρεωτικά")
            return
        
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Σφάλμα", "Το ποσό πρέπει να είναι αριθμός")
            return
        
        supplier = self.system.get_supplier_by_vat(vat)
        if not supplier:
            messagebox.showerror("Σφάλμα", "Δεν βρέθηκε προμηθευτής με αυτό το ΑΦΜ")
            return
        
        contract_id = self.system.add_contract(
            supplier_id=supplier['id'],
            amount=amount,
            start_date=start_date,
            end_date=end_date,
            payment_terms=terms
        )
        
        if contract_id:
            messagebox.showinfo("Επιτυχία", "Η σύμβαση προστέθηκε με επιτυχία")
            self.refresh_contracts_list()
            self.contract_vat_entry.delete(0, tk.END)
            self.contract_amount_entry.delete(0, tk.END)
            self.contract_terms_entry.delete(0, tk.END)
    
    def setup_transactions_frame(self):
        ttk.Label(self.transactions_frame, text="Κινήσεις & Πληρωμές", font=('Arial', 14)).pack(pady=10)
        # Πίνακας κινήσεων
        self.transactions_tree = ttk.Treeview(self.transactions_frame, 
                                           columns=('date', 'amount', 'type', 'description', 'supplier'), 
                                           show='headings')
        self.transactions_tree.heading('date', text='Ημερομηνία')
        self.transactions_tree.heading('amount', text='Ποσό')
        self.transactions_tree.heading('type', text='Τύπος')
        self.transactions_tree.heading('description', text='Περιγραφή')
        self.transactions_tree.heading('supplier', text='Προμηθευτής')
        self.transactions_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Φίλτρα
        filter_frame = ttk.Frame(self.transactions_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Από:").grid(row=0, column=0)
        self.filter_start_entry = DateEntry(filter_frame, date_pattern='yyyy-mm-dd')
        self.filter_start_entry.grid(row=0, column=1)
        
        ttk.Label(filter_frame, text="Έως:").grid(row=0, column=2)
        self.filter_end_entry = DateEntry(filter_frame, date_pattern='yyyy-mm-dd')
        self.filter_end_entry.grid(row=0, column=3)
        
        ttk.Label(filter_frame, text="Τύπος:").grid(row=0, column=4)
        self.filter_type_combobox = ttk.Combobox(filter_frame, values=['', 'ΠΛΗΡΩΜΗ', 'ΕΞΟΔΟ', 'ΕΣΟΔΟ'])
        self.filter_type_combobox.grid(row=0, column=5)
        
        ttk.Button(filter_frame, text="Εφαρμογή Φίλτρων", command=self.apply_filters).grid(row=0, column=6, padx=5)
        
        # Φόρμα προσθήκης κίνησης
        form_frame = ttk.Frame(self.transactions_frame)
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Ποσό:").grid(row=0, column=0, sticky=tk.W)
        self.transaction_amount_entry = ttk.Entry(form_frame)
        self.transaction_amount_entry.grid(row=0, column=1, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Τύπος:").grid(row=1, column=0, sticky=tk.W)
        self.transaction_type_combobox = ttk.Combobox(form_frame, values=['ΠΛΗΡΩΜΗ', 'ΕΞΟΔΟ', 'ΕΙΣΟΔΟΣ'])
        self.transaction_type_combobox.grid(row=1, column=1, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Περιγραφή:").grid(row=2, column=0, sticky=tk.W)
        self.transaction_desc_entry = ttk.Entry(form_frame)
        self.transaction_desc_entry.grid(row=2, column=1, sticky=tk.EW)
        
        ttk.Label(form_frame, text="ΑΦΜ Προμηθευτή (προαιρετικό):").grid(row=3, column=0, sticky=tk.W)
        self.transaction_vat_entry = ttk.Entry(form_frame)
        self.transaction_vat_entry.grid(row=3, column=1, sticky=tk.EW)
        
        button_frame = ttk.Frame(self.transactions_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Προσθήκη", command=self.add_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Επιστροφή", command=self.show_main_frame).pack(side=tk.RIGHT)
    
    def refresh_transactions_list(self, start_date=None, end_date=None, transaction_type=None):
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        transactions = self.system.get_transactions(start_date, end_date, transaction_type)
        for t in transactions:
            self.transactions_tree.insert('', tk.END, values=(
                t[1],  # Date
                f"{t[2]:.2f}€",  # Amount
                t[3],  # Type
                t[4],  # Description
                t[5]   # Supplier name
            ))

    def apply_filters(self):
        start_date = self.filter_start_entry.get()
        end_date = self.filter_end_entry.get()
        trans_type = self.filter_type_combobox.get()
        
        if not start_date: start_date = None
        if not end_date: end_date = None
        if not trans_type: trans_type = None
        
        self.refresh_transactions_list(start_date, end_date, trans_type)
    
    def add_transaction(self):
        amount = self.transaction_amount_entry.get()
        trans_type = self.transaction_type_combobox.get()
        description = self.transaction_desc_entry.get()
        vat = self.transaction_vat_entry.get()

        if not amount or not trans_type:
            messagebox.showerror("Σφάλμα", "Τα πεδία Ποσό και Τύπος είναι υποχρεωτικά")
            return
        
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Σφάλμα", "Το ποσό πρέπει να είναι αριθμός")
            return
        
        contract_id = None
        if vat:
            supplier = self.system.get_supplier_by_vat(vat)
            if supplier and supplier.get('contracts'):
                # Για απλότητα, παίρνουμε την πρώτη ενεργή σύμβαση
                contract = supplier['contracts'][0]
                contract_id = contract[0]
        
        if self.system.add_transaction(
            amount=amount,
            transaction_type=trans_type,
            description=description,
            contract_id=contract_id
        ):
            messagebox.showinfo("Επιτυχία", "Η κίνηση καταχωρήθηκε με επιτυχία")
            self.refresh_transactions_list()
            self.transaction_amount_entry.delete(0, tk.END)
            self.transaction_desc_entry.delete(0, tk.END)
            self.transaction_vat_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Σφάλμα", "Προέκυψε σφάλμα κατά την καταχώρηση")
    
    def setup_reports_frame(self):
        # Αναφορά υπολοίπων
        report_frame = ttk.Frame(self.reports_frame)
        report_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(report_frame, text="Αναφορά Υπολοίπων", font=('Arial', 14)).pack(pady=10)
        
        # Τρέχον υπόλοιπο
        self.balance_label = ttk.Label(report_frame, text="Τρέχον υπόλοιπο: ...")
        self.balance_label.pack()
        
        # Πίνακας συμβάσεων
        columns = ('supplier', 'total', 'paid', 'remaining', 'percentage')
        self.report_tree = ttk.Treeview(report_frame, columns=columns, show='headings')
        self.report_tree.heading('supplier', text='Προμηθευτής')
        self.report_tree.heading('total', text='Συνολικό Ποσό')
        self.report_tree.heading('paid', text='Πληρωμένο')
        self.report_tree.heading('remaining', text='Υπόλοιπο')
        self.report_tree.heading('percentage', text='Ποσοστό')
        self.report_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Κουμπιά
        button_frame = ttk.Frame(report_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Ανανέωση", command=self.refresh_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Εξαγωγή σε PDF", command=self.export_report_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Επιστροφή", command=self.show_main_frame).pack(side=tk.RIGHT)
        
        # Αρχική φόρτωση αναφοράς
        self.refresh_report()
    
    def refresh_report(self):
        report = self.system.get_balance_report()
        self.balance_label.config(text=f"Τρέχον υπόλοιπο: {report['current_balance']}€")
        
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        for contract in report['contracts']:
            paid = contract[2] - contract[3]
            percentage = (paid / contract[2]) * 100 if contract[2] > 0 else 0
            self.report_tree.insert('', tk.END, values=(
                contract[1],
                f"{contract[2]:.2f}€",
                f"{paid:.2f}€",
                f"{contract[3]:.2f}€",
                f"{percentage:.1f}%"
            ))
    
    def export_report_pdf(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if file_path:
            if self.system.export_to_pdf(file_path, 'balance'):
                messagebox.showinfo("Επιτυχία", f"Η αναφορά εξήχθη σε PDF: {file_path}")
            else:
                messagebox.showerror("Σφάλμα", "Προέκυψε σφάλμα κατά την εξαγωγή")
    
    def setup_import_export_frame(self):
        # Εισαγωγή
        import_frame = ttk.LabelFrame(self.import_export_frame, text="Εισαγωγή από CSV")
        import_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(import_frame, text="Τύπος δεδομένων:").grid(row=0, column=0, padx=5, pady=5)
        self.import_type = tk.StringVar(value='suppliers')
        ttk.Radiobutton(import_frame, text="Προμηθευτές", variable=self.import_type, value='suppliers').grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(import_frame, text="Κινήσεις", variable=self.import_type, value='transactions').grid(row=0, column=2, sticky=tk.W)
        
        ttk.Button(import_frame, text="Επιλογή Αρχείου", command=self.select_import_file).grid(row=1, column=0, columnspan=3, pady=5)
        self.import_file_label = ttk.Label(import_frame, text="Δεν έχει επιλεγεί αρχείο")
        self.import_file_label.grid(row=2, column=0, columnspan=3)
        
        ttk.Button(import_frame, text="Εισαγωγή", command=self.execute_import).grid(row=3, column=0, columnspan=3, pady=5)
        
        # Εξαγωγή
        export_frame = ttk.LabelFrame(self.import_export_frame, text="Εξαγωγή")
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(export_frame, text="Τύπος δεδομένων:").grid(row=0, column=0, padx=5, pady=5)
        self.export_type = tk.StringVar(value='transactions')
        ttk.Radiobutton(export_frame, text="Κινήσεις", variable=self.export_type, value='transactions').grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(export_frame, text="Προμηθευτές", variable=self.export_type, value='suppliers').grid(row=0, column=2, sticky=tk.W)
        ttk.Radiobutton(export_frame, text="Συμβάσεις", variable=self.export_type, value='contracts').grid(row=0, column=3, sticky=tk.W)
        
        ttk.Button(export_frame, text="Εξαγωγή σε Excel", command=self.export_to_excel).grid(row=1, column=0, columnspan=4, pady=5)
        ttk.Button(export_frame, text="Εξαγωγή σε PDF", command=self.export_report_pdf).grid(row=2, column=0, columnspan=4, pady=5)
        
        # Κουμπί επιστροφής
        bottom_frame = ttk.Frame(self.import_export_frame)
        bottom_frame.pack(fill=tk.X, pady=(5, 10))  # Μικρότερο padding κάτω
    
        ttk.Button(bottom_frame, text="Επιστροφή", command=self.show_main_frame).pack(side=tk.RIGHT, padx=10)
    
    def select_import_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.import_file_label.config(text=file_path)
            self.selected_import_file = file_path
    
    def execute_import(self):
        if not hasattr(self, 'selected_import_file'):
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε πρώτα αρχείο")
            return
        
        if self.system.import_from_csv(self.selected_import_file, self.import_type.get()):
            messagebox.showinfo("Επιτυχία", "Η εισαγωγή ολοκληρώθηκε με επιτυχία")
            # Ανανέωση των αντίστοιχων λιστών
            if self.import_type.get() == 'suppliers':
                self.refresh_suppliers_list()
            elif self.import_type.get() == 'transactions':
                self.refresh_transactions_list()
        else:
            messagebox.showerror("Σφάλμα", "Προέκυψε σφάλμα κατά την εισαγωγή")
    
    def export_to_excel(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        if file_path:
            if self.system.export_to_excel(file_path, self.export_type.get()):
                messagebox.showinfo("Επιτυχία", f"Η εξαγωγή σε Excel ολοκληρώθηκε: {file_path}")
            else:
                messagebox.showerror("Σφάλμα", "Προέκυψε σφάλμα κατά την εξαγωγή")

if __name__ == "__main__":
    root = tk.Tk()
    app = AccountingApp(root)
    root.mainloop()
