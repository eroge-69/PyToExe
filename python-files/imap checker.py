import sys
import imaplib
import ssl
from typing import Tuple, Optional, List
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox,
                             QTableWidget, QTableWidgetItem, QTabWidget, QProgressBar,
                             QMessageBox, QFileDialog, QSplitter, QHeaderView, QComboBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QIcon
import csv
import os

class IMAPWorker(QThread):
    """Worker thread for IMAP operations to prevent GUI freezing"""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, server: str, port: int, username: str, password: str, use_ssl: bool = True):
        super().__init__()
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl

    def run(self):
        try:
            self.progress.emit("Connecting to server...")
            checker = IMAPAccountChecker(self.server, self.port, self.use_ssl)
            result = checker.check_account(self.username, self.password)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class BatchIMAPWorker(QThread):
    """Worker thread for batch IMAP operations"""
    finished = pyqtSignal(list)
    progress = pyqtSignal(str, bool)  # message, is_error
    item_processed = pyqtSignal(dict)

    def __init__(self, server: str, port: int, csv_file: str, use_ssl: bool = True):
        super().__init__()
        self.server = server
        self.port = port
        self.csv_file = csv_file
        self.use_ssl = use_ssl

    def run(self):
        results = []
        try:
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                accounts = list(reader)
                total = len(accounts)
                
                for i, row in enumerate(accounts):
                    username = row.get('username', '').strip()
                    password = row.get('password', '').strip()
                    
                    if username and password:
                        self.progress.emit(f"Checking {username} ({i+1}/{total})...", False)
                        
                        checker = IMAPAccountChecker(self.server, self.port, self.use_ssl)
                        result = checker.check_account(username, password)
                        results.append(result)
                        self.item_processed.emit(result)
                        
                        # Small delay to avoid overwhelming the server
                        self.msleep(100)
            
            self.finished.emit(results)
            
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}", True)

class IMAPAccountChecker:
    def __init__(self, server: str, port: int = 993, use_ssl: bool = True):
        self.server = server
        self.port = port
        self.use_ssl = use_ssl
        self.connection = None
    
    def connect(self) -> bool:
        try:
            if self.use_ssl:
                context = ssl.create_default_context()
                self.connection = imaplib.IMAP4_SSL(
                    self.server, 
                    self.port, 
                    ssl_context=context
                )
            else:
                self.connection = imaplib.IMAP4(self.server, self.port)
            return True
        except Exception as e:
            return False
    
    def login(self, username: str, password: str) -> Tuple[bool, Optional[str]]:
        if not self.connection:
            if not self.connect():
                return False, "Connection failed"
        
        try:
            result, data = self.connection.login(username, password)
            if result == 'OK':
                return True, "Login successful"
            else:
                return False, data[0].decode() if data else "Login failed"
        except imaplib.IMAP4.error as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error: {e}"
    
    def check_mailbox_info(self) -> dict:
        if not self.connection:
            return {}
        
        try:
            result, data = self.connection.select('INBOX')
            if result == 'OK':
                message_count = int(data[0])
            else:
                message_count = 0
            
            return {
                'inbox_message_count': message_count,
                'status': 'Connected'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def logout(self):
        if self.connection:
            try:
                self.connection.logout()
            except:
                pass
            self.connection = None
    
    def check_account(self, username: str, password: str) -> dict:
        result = {
            'username': username,
            'server': self.server,
            'connection_success': False,
            'login_success': False,
            'login_message': '',
            'mailbox_info': {}
        }
        
        if self.connect():
            result['connection_success'] = True
            login_success, login_message = self.login(username, password)
            result['login_success'] = login_success
            result['login_message'] = login_message
            
            if login_success:
                result['mailbox_info'] = self.check_mailbox_info()
        
        self.logout()
        return result

class IMAPCheckerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IMAP Account Checker")
        self.setGeometry(100, 100, 900, 700)
        self.setup_ui()
        
        # Common IMAP servers
        self.common_servers = {
            "Gmail": ("imap.gmail.com", 993),
            "Outlook": ("imap-mail.outlook.com", 993),
            "Yahoo": ("imap.mail.yahoo.com", 993),
            "AOL": ("imap.aol.com", 993),
            "iCloud": ("imap.mail.me.com", 993),
            "Custom": ("", 993)
        }
        
        self.batch_results = []

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_single_tab(), "Single Check")
        tabs.addTab(self.create_batch_tab(), "Batch Check")
        tabs.addTab(self.create_results_tab(), "Results")
        
        layout.addWidget(tabs)

    def create_single_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Server selection
        server_group = QGroupBox("Server Configuration")
        server_layout = QVBoxLayout(server_group)
        
        server_combo_layout = QHBoxLayout()
        server_combo_layout.addWidget(QLabel("Email Provider:"))
        
        self.server_combo = QComboBox()
        self.server_combo.addItems(list(self.common_servers.keys()))
        self.server_combo.currentTextChanged.connect(self.on_server_changed)
        server_combo_layout.addWidget(self.server_combo)
        server_combo_layout.addStretch()
        
        server_layout.addLayout(server_combo_layout)

        server_details_layout = QHBoxLayout()
        server_details_layout.addWidget(QLabel("IMAP Server:"))
        self.server_input = QLineEdit("imap.gmail.com")
        server_details_layout.addWidget(self.server_input)
        
        server_details_layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit("993")
        self.port_input.setFixedWidth(60)
        server_details_layout.addWidget(self.port_input)
        
        server_layout.addLayout(server_details_layout)

        # Credentials
        cred_group = QGroupBox("Account Credentials")
        cred_layout = QVBoxLayout(cred_group)
        
        cred_layout.addWidget(QLabel("Username/Email:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("your.email@example.com")
        cred_layout.addWidget(self.username_input)
        
        cred_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        cred_layout.addWidget(self.password_input)

        # Check button
        self.check_button = QPushButton("Check Account")
        self.check_button.clicked.connect(self.check_single_account)
        self.check_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        # Results area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Results will appear here...")

        # Add widgets to layout
        layout.addWidget(server_group)
        layout.addWidget(cred_group)
        layout.addWidget(self.check_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.results_text)

        return widget

    def create_batch_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Server configuration (same as single tab)
        server_group = QGroupBox("Server Configuration")
        server_layout = QVBoxLayout(server_group)
        
        server_combo_layout = QHBoxLayout()
        server_combo_layout.addWidget(QLabel("Email Provider:"))
        
        self.batch_server_combo = QComboBox()
        self.batch_server_combo.addItems(list(self.common_servers.keys()))
        self.batch_server_combo.currentTextChanged.connect(self.on_batch_server_changed)
        server_combo_layout.addWidget(self.batch_server_combo)
        server_combo_layout.addStretch()
        
        server_layout.addLayout(server_combo_layout)

        server_details_layout = QHBoxLayout()
        server_details_layout.addWidget(QLabel("IMAP Server:"))
        self.batch_server_input = QLineEdit("imap.gmail.com")
        server_details_layout.addWidget(self.batch_server_input)
        
        server_details_layout.addWidget(QLabel("Port:"))
        self.batch_port_input = QLineEdit("993")
        self.batch_port_input.setFixedWidth(60)
        server_details_layout.addWidget(self.batch_port_input)
        
        server_layout.addLayout(server_details_layout)

        # File selection
        file_group = QGroupBox("Batch File")
        file_layout = QVBoxLayout(file_group)
        
        file_select_layout = QHBoxLayout()
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Select CSV file with username,password columns")
        file_select_layout.addWidget(self.file_path_input)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_csv_file)
        file_select_layout.addWidget(self.browse_button)
        
        file_layout.addLayout(file_select_layout)
        
        file_info = QLabel("CSV format: username,password (one account per line)")
        file_info.setStyleSheet("color: #666; font-size: 10pt;")
        file_layout.addWidget(file_info)

        # Buttons
        button_layout = QHBoxLayout()
        self.start_batch_button = QPushButton("Start Batch Check")
        self.start_batch_button.clicked.connect(self.start_batch_check)
        self.start_batch_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; }")
        
        self.export_button = QPushButton("Export Results")
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)
        
        button_layout.addWidget(self.start_batch_button)
        button_layout.addWidget(self.export_button)
        button_layout.addStretch()

        # Progress
        self.batch_progress_bar = QProgressBar()
        self.batch_progress_text = QLabel()
        self.batch_progress_text.setAlignment(Qt.AlignCenter)

        # Add to layout
        layout.addWidget(server_group)
        layout.addWidget(file_group)
        layout.addLayout(button_layout)
        layout.addWidget(self.batch_progress_bar)
        layout.addWidget(self.batch_progress_text)
        layout.addStretch()

        return widget

    def create_results_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "Username", "Server", "Connection", "Login", "Messages"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.results_table)
        return widget

    def on_server_changed(self, provider):
        server, port = self.common_servers.get(provider, ("", 993))
        self.server_input.setText(server)
        self.port_input.setText(str(port))

    def on_batch_server_changed(self, provider):
        server, port = self.common_servers.get(provider, ("", 993))
        self.batch_server_input.setText(server)
        self.batch_port_input.setText(str(port))

    def browse_csv_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            self.file_path_input.setText(file_path)

    def check_single_account(self):
        server = self.server_input.text().strip()
        port = int(self.port_input.text().strip())
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not all([server, port, username, password]):
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return

        self.check_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.results_text.clear()

        self.worker = IMAPWorker(server, port, username, password)
        self.worker.finished.connect(self.on_single_check_finished)
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()

    def on_single_check_finished(self, result):
        self.check_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        output = f"""IMAP Account Check Results
{'='*50}
Username: {result['username']}
Server: {result['server']}
Connection: {'✅ SUCCESS' if result['connection_success'] else '❌ FAILED'}
Login: {'✅ SUCCESS' if result['login_success'] else '❌ FAILED'}

Message: {result['login_message']}
"""

        if result['login_success']:
            output += f"Messages in INBOX: {result['mailbox_info'].get('inbox_message_count', 0)}\n"

        self.results_text.setPlainText(output)

    def start_batch_check(self):
        server = self.batch_server_input.text().strip()
        port = int(self.batch_port_input.text().strip())
        csv_file = self.file_path_input.text().strip()

        if not all([server, csv_file]):
            QMessageBox.warning(self, "Error", "Please select a server and CSV file")
            return

        if not os.path.exists(csv_file):
            QMessageBox.warning(self, "Error", "CSV file does not exist")
            return

        self.start_batch_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.batch_progress_bar.setRange(0, 0)  # Indeterminate progress
        self.batch_progress_text.setText("Starting batch check...")

        self.batch_worker = BatchIMAPWorker(server, port, csv_file)
        self.batch_worker.progress.connect(self.on_batch_progress)
        self.batch_worker.item_processed.connect(self.on_item_processed)
        self.batch_worker.finished.connect(self.on_batch_finished)
        self.batch_worker.start()

    def on_batch_progress(self, message, is_error):
        if is_error:
            self.batch_progress_text.setStyleSheet("color: red;")
        else:
            self.batch_progress_text.setStyleSheet("")
        self.batch_progress_text.setText(message)

    def on_item_processed(self, result):
        self.batch_results.append(result)
        self.update_results_table()

    def on_batch_finished(self, results):
        self.start_batch_button.setEnabled(True)
        self.export_button.setEnabled(True)
        self.batch_progress_bar.setRange(0, 100)
        self.batch_progress_bar.setValue(100)
        self.batch_progress_text.setText(f"Batch check completed! Processed {len(results)} accounts.")

    def update_results_table(self):
        self.results_table.setRowCount(len(self.batch_results))
        
        for row, result in enumerate(self.batch_results):
            self.results_table.setItem(row, 0, QTableWidgetItem(result['username']))
            self.results_table.setItem(row, 1, QTableWidgetItem(result['server']))
            
            conn_item = QTableWidgetItem("✅ SUCCESS" if result['connection_success'] else "❌ FAILED")
            conn_item.setForeground(QColor('green') if result['connection_success'] else QColor('red'))
            self.results_table.setItem(row, 2, conn_item)
            
            login_item = QTableWidgetItem("✅ SUCCESS" if result['login_success'] else "❌ FAILED")
            login_item.setForeground(QColor('green') if result['login_success'] else QColor('red'))
            self.results_table.setItem(row, 3, login_item)
            
            messages = str(result['mailbox_info'].get('inbox_message_count', 0))
            self.results_table.setItem(row, 4, QTableWidgetItem(messages))

    def export_results(self):
        if not self.batch_results:
            QMessageBox.warning(self, "Error", "No results to export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "imap_check_results.csv", "CSV Files (*.csv)"
        )

        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Username', 'Server', 'Connection', 'Login', 'Messages', 'Message'])
                    
                    for result in self.batch_results:
                        writer.writerow([
                            result['username'],
                            result['server'],
                            'SUCCESS' if result['connection_success'] else 'FAILED',
                            'SUCCESS' if result['login_success'] else 'FAILED',
                            result['mailbox_info'].get('inbox_message_count', 0),
                            result['login_message']
                        ])
                
                QMessageBox.information(self, "Success", f"Results exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")

    def on_worker_error(self, error_message):
        self.check_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_message}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern style
    
    window = IMAPCheckerGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()