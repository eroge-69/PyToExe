import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLineEdit, QTextEdit, QLabel, 
                             QDateEdit, QComboBox, QMessageBox, QFileDialog,
                             QGroupBox, QFormLayout, QTimeEdit, QHeaderView)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QIcon
import os
import shutil

class LawFirmApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initDB()
        
    def initUI(self):
        self.setWindowTitle('Law Firm Management System')
        self.setGeometry(100, 100, 1000, 700)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.client_tab = QWidget()
        self.case_tab = QWidget()
        self.time_tab = QWidget()
        self.document_tab = QWidget()
        self.calendar_tab = QWidget()
        
        self.tabs.addTab(self.client_tab, "Clients")
        self.tabs.addTab(self.case_tab, "Cases")
        self.tabs.addTab(self.time_tab, "Time Tracking")
        self.tabs.addTab(self.document_tab, "Documents")
        self.tabs.addTab(self.calendar_tab, "Calendar")
        
        # Setup each tab
        self.setupClientTab()
        self.setupCaseTab()
        self.setupTimeTab()
        self.setupDocumentTab()
        self.setupCalendarTab()
        
        # Status bar
        self.statusBar().showMessage('Ready')
        
    def initDB(self):
        self.conn = sqlite3.connect('law_firm.db')
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                company TEXT,
                address TEXT,
                phone TEXT,
                email TEXT,
                retainer REAL,
                date_added TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                case_number TEXT NOT NULL,
                case_type TEXT,
                description TEXT,
                status TEXT,
                open_date TEXT,
                close_date TEXT,
                assigned_attorney TEXT,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER,
                attorney TEXT,
                description TEXT,
                date_worked TEXT,
                start_time TEXT,
                end_time TEXT,
                duration REAL,
                billed_amount REAL,
                FOREIGN KEY (case_id) REFERENCES cases (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER,
                document_name TEXT,
                document_path TEXT,
                upload_date TEXT,
                FOREIGN KEY (case_id) REFERENCES cases (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER,
                event_date TEXT,
                event_time TEXT,
                description TEXT,
                FOREIGN KEY (case_id) REFERENCES cases (id)
            )
        ''')
        
        self.conn.commit()
        
    def setupClientTab(self):
        layout = QVBoxLayout(self.client_tab)
        
        # Form for adding new clients
        form_group = QGroupBox("Add New Client")
        form_layout = QFormLayout()
        
        self.client_first_name = QLineEdit()
        self.client_last_name = QLineEdit()
        self.client_company = QLineEdit()
        self.client_address = QTextEdit()
        self.client_phone = QLineEdit()
        self.client_email = QLineEdit()
        self.client_retainer = QLineEdit()
        
        form_layout.addRow("First Name:", self.client_first_name)
        form_layout.addRow("Last Name:", self.client_last_name)
        form_layout.addRow("Company:", self.client_company)
        form_layout.addRow("Address:", self.client_address)
        form_layout.addRow("Phone:", self.client_phone)
        form_layout.addRow("Email:", self.client_email)
        form_layout.addRow("Retainer:", self.client_retainer)
        
        add_client_btn = QPushButton("Add Client")
        add_client_btn.clicked.connect(self.addClient)
        form_layout.addRow("", add_client_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Table for displaying clients
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(8)
        self.clients_table.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Company", "Phone", "Email", "Retainer", "Date Added"])
        self.clients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.clients_table)
        
        # Load clients into table
        self.loadClients()
        
    def setupCaseTab(self):
        layout = QVBoxLayout(self.case_tab)
        
        # Form for adding new cases
        form_group = QGroupBox("Add New Case")
        form_layout = QFormLayout()
        
        self.case_client = QComboBox()
        self.loadClientsToComboBox()
        self.case_number = QLineEdit()
        self.case_type = QComboBox()
        self.case_type.addItems(["Civil", "Criminal", "Family", "Corporate", "Real Estate", "Other"])
        self.case_description = QTextEdit()
        self.case_status = QComboBox()
        self.case_status.addItems(["Open", "Closed", "Pending", "Active"])
        self.case_open_date = QDateEdit()
        self.case_open_date.setDate(QDate.currentDate())
        self.case_close_date = QDateEdit()
        self.case_assigned_attorney = QLineEdit()
        
        form_layout.addRow("Client:", self.case_client)
        form_layout.addRow("Case Number:", self.case_number)
        form_layout.addRow("Case Type:", self.case_type)
        form_layout.addRow("Description:", self.case_description)
        form_layout.addRow("Status:", self.case_status)
        form_layout.addRow("Open Date:", self.case_open_date)
        form_layout.addRow("Close Date:", self.case_close_date)
        form_layout.addRow("Assigned Attorney:", self.case_assigned_attorney)
        
        add_case_btn = QPushButton("Add Case")
        add_case_btn.clicked.connect(self.addCase)
        form_layout.addRow("", add_case_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Table for displaying cases
        self.cases_table = QTableWidget()
        self.cases_table.setColumnCount(9)
        self.cases_table.setHorizontalHeaderLabels(["ID", "Client", "Case Number", "Type", "Status", "Open Date", "Close Date", "Attorney", "Description"])
        self.cases_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.cases_table)
        
        # Load cases into table
        self.loadCases()
        
    def setupTimeTab(self):
        layout = QVBoxLayout(self.time_tab)
        
        # Form for adding time entries
        form_group = QGroupBox("Add Time Entry")
        form_layout = QFormLayout()
        
        self.time_case = QComboBox()
        self.loadCasesToComboBox()
        self.time_attorney = QLineEdit()
        self.time_description = QTextEdit()
        self.time_date = QDateEdit()
        self.time_date.setDate(QDate.currentDate())
        self.time_start = QTimeEdit()
        self.time_start.setTime(QApplication.instance().currentTime())
        self.time_end = QTimeEdit()
        self.time_end.setTime(QApplication.instance().currentTime())
        
        form_layout.addRow("Case:", self.time_case)
        form_layout.addRow("Attorney:", self.time_attorney)
        form_layout.addRow("Description:", self.time_description)
        form_layout.addRow("Date:", self.time_date)
        form_layout.addRow("Start Time:", self.time_start)
        form_layout.addRow("End Time:", self.time_end)
        
        add_time_btn = QPushButton("Add Time Entry")
        add_time_btn.clicked.connect(self.addTimeEntry)
        form_layout.addRow("", add_time_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Table for displaying time entries
        self.time_table = QTableWidget()
        self.time_table.setColumnCount(7)
        self.time_table.setHorizontalHeaderLabels(["ID", "Case", "Attorney", "Date", "Duration", "Billed Amount", "Description"])
        self.time_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.time_table)
        
        # Load time entries into table
        self.loadTimeEntries()
        
    def setupDocumentTab(self):
        layout = QVBoxLayout(self.document_tab)
        
        # Form for adding documents
        form_group = QGroupBox("Add Document")
        form_layout = QFormLayout()
        
        self.doc_case = QComboBox()
        self.loadCasesToComboBox()
        self.doc_name = QLineEdit()
        self.doc_path = QLineEdit()
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browseDocument)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.doc_path)
        path_layout.addWidget(browse_btn)
        
        form_layout.addRow("Case:", self.doc_case)
        form_layout.addRow("Document Name:", self.doc_name)
        form_layout.addRow("Document Path:", path_layout)
        
        add_doc_btn = QPushButton("Add Document")
        add_doc_btn.clicked.connect(self.addDocument)
        form_layout.addRow("", add_doc_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Table for displaying documents
        self.doc_table = QTableWidget()
        self.doc_table.setColumnCount(5)
        self.doc_table.setHorizontalHeaderLabels(["ID", "Case", "Document Name", "Upload Date", "Path"])
        self.doc_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.doc_table)
        
        # Load documents into table
        self.loadDocuments()
        
    def setupCalendarTab(self):
        layout = QVBoxLayout(self.calendar_tab)
        
        # Form for adding calendar events
        form_group = QGroupBox("Add Calendar Event")
        form_layout = QFormLayout()
        
        self.cal_case = QComboBox()
        self.loadCasesToComboBox()
        self.cal_date = QDateEdit()
        self.cal_date.setDate(QDate.currentDate())
        self.cal_time = QTimeEdit()
        self.cal_time.setTime(QApplication.instance().currentTime())
        self.cal_description = QTextEdit()
        
        form_layout.addRow("Case:", self.cal_case)
        form_layout.addRow("Date:", self.cal_date)
        form_layout.addRow("Time:", self.cal_time)
        form_layout.addRow("Description:", self.cal_description)
        
        add_cal_btn = QPushButton("Add Event")
        add_cal_btn.clicked.connect(self.addCalendarEvent)
        form_layout.addRow("", add_cal_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Table for displaying calendar events
        self.cal_table = QTableWidget()
        self.cal_table.setColumnCount(5)
        self.cal_table.setHorizontalHeaderLabels(["ID", "Case", "Date", "Time", "Description"])
        self.cal_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.cal_table)
        
        # Load calendar events into table
        self.loadCalendarEvents()
        
    def loadClientsToComboBox(self):
        self.cursor.execute("SELECT id, first_name, last_name FROM clients")
        clients = self.cursor.fetchall()
        self.case_client.clear()
        self.time_case.clear()
        self.doc_case.clear()
        self.cal_case.clear()
        
        for client in clients:
            self.case_client.addItem(f"{client[1]} {client[2]}", client[0])
            self.time_case.addItem(f"{client[1]} {client[2]}", client[0])
            self.doc_case.addItem(f"{client[1]} {client[2]}", client[0])
            self.cal_case.addItem(f"{client[1]} {client[2]}", client[0])
            
    def loadCasesToComboBox(self):
        self.cursor.execute("SELECT cases.id, cases.case_number, clients.first_name, clients.last_name FROM cases JOIN clients ON cases.client_id = clients.id")
        cases = self.cursor.fetchall()
        self.time_case.clear()
        self.doc_case.clear()
        self.cal_case.clear()
        
        for case in cases:
            self.time_case.addItem(f"{case[1]} - {case[2]} {case[3]}", case[0])
            self.doc_case.addItem(f"{case[1]} - {case[2]} {case[3]}", case[0])
            self.cal_case.addItem(f"{case[1]} - {case[2]} {case[3]}", case[0])
            
    def addClient(self):
        first_name = self.client_first_name.text()
        last_name = self.client_last_name.text()
        company = self.client_company.text()
        address = self.client_address.toPlainText()
        phone = self.client_phone.text()
        email = self.client_email.text()
        retainer = self.client_retainer.text()
        date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not first_name or not last_name:
            QMessageBox.warning(self, "Input Error", "First name and last name are required!")
            return
            
        try:
            self.cursor.execute(
                "INSERT INTO clients (first_name, last_name, company, address, phone, email, retainer, date_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (first_name, last_name, company, address, phone, email, retainer, date_added)
            )
            self.conn.commit()
            
            # Clear form fields
            self.client_first_name.clear()
            self.client_last_name.clear()
            self.client_company.clear()
            self.client_address.clear()
            self.client_phone.clear()
            self.client_email.clear()
            self.client_retainer.clear()
            
            # Refresh clients table and combobox
            self.loadClients()
            self.loadClientsToComboBox()
            
            self.statusBar().showMessage('Client added successfully')
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add client: {str(e)}")
            
    def addCase(self):
        client_id = self.case_client.currentData()
        case_number = self.case_number.text()
        case_type = self.case_type.currentText()
        description = self.case_description.toPlainText()
        status = self.case_status.currentText()
        open_date = self.case_open_date.date().toString("yyyy-MM-dd")
        close_date = self.case_close_date.date().toString("yyyy-MM-dd") if self.case_close_date.date() > QDate(2000, 1, 1) else None
        assigned_attorney = self.case_assigned_attorney.text()
        
        if not case_number:
            QMessageBox.warning(self, "Input Error", "Case number is required!")
            return
            
        try:
            self.cursor.execute(
                "INSERT INTO cases (client_id, case_number, case_type, description, status, open_date, close_date, assigned_attorney) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (client_id, case_number, case_type, description, status, open_date, close_date, assigned_attorney)
            )
            self.conn.commit()
            
            # Clear form fields
            self.case_number.clear()
            self.case_description.clear()
            self.case_assigned_attorney.clear()
            
            # Refresh cases table and combobox
            self.loadCases()
            self.loadCasesToComboBox()
            
            self.statusBar().showMessage('Case added successfully')
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add case: {str(e)}")
            
    def addTimeEntry(self):
        case_id = self.time_case.currentData()
        attorney = self.time_attorney.text()
        description = self.time_description.toPlainText()
        date_worked = self.time_date.date().toString("yyyy-MM-dd")
        start_time = self.time_start.time().toString("HH:mm")
        end_time = self.time_end.time().toString("HH:mm")
        
        # Calculate duration in hours
        start_dt = datetime.strptime(start_time, "%H:%M")
        end_dt = datetime.strptime(end_time, "%H:%M")
        duration = (end_dt - start_dt).seconds / 3600.0
        
        # Simple billing calculation ($200/hour)
        billed_amount = duration * 200
        
        try:
            self.cursor.execute(
                "INSERT INTO time_entries (case_id, attorney, description, date_worked, start_time, end_time, duration, billed_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (case_id, attorney, description, date_worked, start_time, end_time, duration, billed_amount)
            )
            self.conn.commit()
            
            # Clear form fields
            self.time_attorney.clear()
            self.time_description.clear()
            
            # Refresh time entries table
            self.loadTimeEntries()
            
            self.statusBar().showMessage('Time entry added successfully')
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add time entry: {str(e)}")
            
    def browseDocument(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Document", "", "All Files (*);;PDF Files (*.pdf);;Word Documents (*.doc *.docx);;Text Files (*.txt)")
        if file_path:
            self.doc_path.setText(file_path)
            
    def addDocument(self):
        case_id = self.doc_case.currentData()
        document_name = self.doc_name.text()
        document_path = self.doc_path.text()
        upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not document_name or not document_path:
            QMessageBox.warning(self, "Input Error", "Document name and path are required!")
            return
            
        try:
            # Copy document to a documents folder
            docs_dir = "documents"
            if not os.path.exists(docs_dir):
                os.makedirs(docs_dir)
                
            file_ext = os.path.splitext(document_path)[1]
            new_filename = f"{document_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
            new_path = os.path.join(docs_dir, new_filename)
            
            shutil.copy2(document_path, new_path)
            
            self.cursor.execute(
                "INSERT INTO documents (case_id, document_name, document_path, upload_date) VALUES (?, ?, ?, ?)",
                (case_id, document_name, new_path, upload_date)
            )
            self.conn.commit()
            
            # Clear form fields
            self.doc_name.clear()
            self.doc_path.clear()
            
            # Refresh documents table
            self.loadDocuments()
            
            self.statusBar().showMessage('Document added successfully')
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add document: {str(e)}")
            
    def addCalendarEvent(self):
        case_id = self.cal_case.currentData()
        event_date = self.cal_date.date().toString("yyyy-MM-dd")
        event_time = self.cal_time.time().toString("HH:mm")
        description = self.cal_description.toPlainText()
        
        try:
            self.cursor.execute(
                "INSERT INTO calendar (case_id, event_date, event_time, description) VALUES (?, ?, ?, ?)",
                (case_id, event_date, event_time, description)
            )
            self.conn.commit()
            
            # Clear form fields
            self.cal_description.clear()
            
            # Refresh calendar events table
            self.loadCalendarEvents()
            
            self.statusBar().showMessage('Calendar event added successfully')
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add calendar event: {str(e)}")
            
    def loadClients(self):
        self.cursor.execute("SELECT * FROM clients")
        clients = self.cursor.fetchall()
        
        self.clients_table.setRowCount(len(clients))
        for row, client in enumerate(clients):
            for col, data in enumerate(client):
                self.clients_table.setItem(row, col, QTableWidgetItem(str(data)))
                
    def loadCases(self):
        self.cursor.execute("""
            SELECT cases.*, clients.first_name, clients.last_name 
            FROM cases 
            JOIN clients ON cases.client_id = clients.id
        """)
        cases = self.cursor.fetchall()
        
        self.cases_table.setRowCount(len(cases))
        for row, case in enumerate(cases):
            for col, data in enumerate(case):
                if col == 1:  # Client ID column, show client name instead
                    client_name = f"{case[9]} {case[10]}"
                    self.cases_table.setItem(row, col, QTableWidgetItem(client_name))
                else:
                    self.cases_table.setItem(row, col, QTableWidgetItem(str(data)))
                    
    def loadTimeEntries(self):
        self.cursor.execute("""
            SELECT time_entries.*, cases.case_number, clients.first_name, clients.last_name 
            FROM time_entries 
            JOIN cases ON time_entries.case_id = cases.id
            JOIN clients ON cases.client_id = clients.id
        """)
        time_entries = self.cursor.fetchall()
        
        self.time_table.setRowCount(len(time_entries))
        for row, entry in enumerate(time_entries):
            for col, data in enumerate(entry):
                if col == 1:  # Case ID column, show case number and client name
                    case_info = f"{entry[9]} - {entry[10]} {entry[11]}"
                    self.time_table.setItem(row, col, QTableWidgetItem(case_info))
                else:
                    self.time_table.setItem(row, col, QTableWidgetItem(str(data)))
                    
    def loadDocuments(self):
        self.cursor.execute("""
            SELECT documents.*, cases.case_number, clients.first_name, clients.last_name 
            FROM documents 
            JOIN cases ON documents.case_id = cases.id
            JOIN clients ON cases.client_id = clients.id
        """)
        documents = self.cursor.fetchall()
        
        self.doc_table.setRowCount(len(documents))
        for row, doc in enumerate(documents):
            for col, data in enumerate(doc):
                if col == 1:  # Case ID column, show case number and client name
                    case_info = f"{doc[6]} - {doc[7]} {doc[8]}"
                    self.doc_table.setItem(row, col, QTableWidgetItem(case_info))
                else:
                    self.doc_table.setItem(row, col, QTableWidgetItem(str(data)))
                    
    def loadCalendarEvents(self):
        self.cursor.execute(""'
            SELECT calendar.*, cases.case_number, clients.first_name, clients.last_name 
            FROM calendar 
            JOIN cases ON calendar.case_id = cases.id
            JOIN clients ON cases.client_id = clients.id
        """)
        events = self.cursor.fetchall()
        
        self.cal_table.setRowCount(len(events))
        for row, event in enumerate(events):
            for col, data in enumerate(event):
                if col == 1:  # Case ID column, show case number and client name
                    case_info = f"{event[5]} - {event[6]} {event[7]}"
                    self.cal_table.setItem(row, col, QTableWidgetItem(case_info))
                else:
                    self.cal_table.setItem(row, col, QTableWidgetItem(str(data)))
                    
    def closeEvent(self, event):
        # Close database connection when application closes
        self.conn.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = LawFirmApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()