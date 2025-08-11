# Email Validator Pro — Py2Exe.com Safe Version
# All imports and resources are self-contained for online exe building.
# No external file dependencies, all data is inline.

import sys
import socket
import threading
import re
from queue import Queue
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog, QProgressBar, QLabel
from PySide6.QtCore import Qt, QThread, Signal
import dns.resolver
import smtplib

# Worker thread for checking emails
class EmailCheckerThread(QThread):
    progress = Signal(int)
    result = Signal(str, str)

    def __init__(self, emails):
        super().__init__()
        self.emails = emails

    def run(self):
        total = len(self.emails)
        for i, email in enumerate(self.emails):
            status = self.check_email(email)
            self.result.emit(email, status)
            self.progress.emit(int(((i+1)/total)*100))

    def check_email(self, email):
        domain = email.split('@')[-1]
        try:
            dns.resolver.resolve(domain, 'MX')
            return "Valid domain"
        except:
            return "Invalid domain"

# Main GUI Application
class EmailValidatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Email Validator Pro")
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Email", "Status"])
        layout.addWidget(self.table)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.label = QLabel("Load a CSV/TXT file with emails to start")
        layout.addWidget(self.label)

        self.btn_load = QPushButton("Load Email List")
        self.btn_load.clicked.connect(self.load_file)
        layout.addWidget(self.btn_load)

        self.btn_start = QPushButton("Start Validation")
        self.btn_start.clicked.connect(self.start_validation)
        layout.addWidget(self.btn_start)

        self.emails = []

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Email File", "", "Text Files (*.txt *.csv)")
        if path:
            with open(path, 'r') as f:
                self.emails = [line.strip() for line in f if line.strip()]
            self.table.setRowCount(0)
            for email in self.emails:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(email))
                self.table.setItem(row, 1, QTableWidgetItem("Pending"))

    def start_validation(self):
        if not self.emails:
            return
        self.thread = EmailCheckerThread(self.emails)
        self.thread.result.connect(self.update_status)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.start()

    def update_status(self, email, status):
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == email:
                self.table.setItem(row, 1, QTableWidgetItem(status))
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmailValidatorApp()
    window.show()
    sys.exit(app.exec())
