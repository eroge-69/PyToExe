import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QLineEdit, QComboBox, QDateEdit, QTextEdit, QMessageBox, QHBoxLayout, QLabel, QFileDialog
from PyQt5.QtCore import Qt
import shutil
import csv

class CustomerManagerUI(QMainWindow):
    def __init__(self, db_path):
        super().__init__()

        self.db_path = db_path
        self.customer_manager = CustomerManager(db_path)

        self.setWindowTitle("Gestione Clienti")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.setup_ui()

    def setup_ui(self):
        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)

        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(["Nome", "Email", "Stato", "Scadenza", "Note", "Password"])

        self.input_layout = QHBoxLayout()

        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.status_input = QComboBox()
        self.status_input.addItems(["Attivo", "Sospeso", "Chiuso"])
        self.expiry_date_input = QDateEdit()
        self.notes_input = QTextEdit()

        self.input_layout.addWidget(QLabel("Nome:"))
        self.input_layout.addWidget(self.name_input)
        self.input_layout.addWidget(QLabel("Email:"))
        self.input_layout.addWidget(self.email_input)
        self.input_layout.addWidget(QLabel("Password:"))
        self.input_layout.addWidget(self.password_input)
        self.input_layout.addWidget(QLabel("Stato:"))
        self.input_layout.addWidget(self.status_input)
        self.input_layout.addWidget(QLabel("Scadenza:"))
        self.input_layout.addWidget(self.expiry_date_input)
        self.input_layout.addWidget(QLabel("Note:"))
        self.input_layout.addWidget(self.notes_input)

        self.layout.addLayout(self.input_layout)

        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Aggiungi")
        self.add_button.clicked.connect(self.add_customer)
        self.update_button = QPushButton("Modifica")
        self.update_button.clicked.connect(self.update_customer)
        self.delete_button = QPushButton("Elimina")
        self.delete_button.clicked.connect(self.delete_customer)
        self.search_button = QPushButton("Cerca")
        self.search_button.clicked.connect(self.search_customer)
        self.export_button = QPushButton("Esporta CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        self.backup_button = QPushButton("Backup")
        self.backup_button.clicked.connect(self.backup_database)
        self.restore_button = QPushButton("Ripristina")
        self.restore_button.clicked.connect(self.restore_database)

        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.update_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addWidget(self.search_button)
        self.button_layout.addWidget(self.export_button)
        self.button_layout.addWidget(self.backup_button)
        self.button_layout.addWidget(self.restore_button)

        self.layout.addLayout(self.button_layout)

        self.load_customers()

    def load_customers(self):
        try:
            customers = self.customer_manager.get_customers()
            self.table_widget.setRowCount(len(customers))
            for row, customer in enumerate(customers):
                for col, item in enumerate(customer[1:]):
                    self.table_widget.setItem(row, col, QTableWidgetItem(str(item)))
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il caricamento dei dati: {e}")

    def add_customer(self):
        name = self.name_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        status = self.status_input.currentText()
        expiry_date = self.expiry_date_input.text()
        notes = self.notes_input.toPlainText()

        try:
            self.customer_manager.add_customer(name, email, password, status, expiry_date, notes)
            QMessageBox.information(self, "Successo", "Cliente aggiunto con successo.")
            self.load_customers()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'aggiunta del cliente: {e}")

    def update_customer(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Avviso", "Seleziona un cliente da modificare.")
            return

        row = selected_items[0].row()
        name = self.name_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        status = self.status_input.currentText()
        expiry_date = self.expiry_date_input.text()
        notes = self.notes_input.toPlainText()

        try:
            self.customer_manager.update_customer(row + 1, name, email, password, status, expiry_date, notes)
            QMessageBox.information(self, "Successo", "Cliente aggiornato con successo.")
            self.load_customers()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'aggiornamento del cliente: {e}")

    def delete_customer(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Avviso", "Seleziona un cliente da eliminare.")
            return

        row = selected_items[0].row()
        try:
            self.customer_manager.delete_customer(row + 1)
            QMessageBox.information(self, "Successo", "Cliente eliminato con successo.")
            self.load_customers()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante l'eliminazione del cliente: {e}")

    def search_customer(self):
        search_text = self.name_input.text()
        try:
            customers = self.customer_manager.search_customers(search_text)
            self.table_widget.setRowCount(len(customers))
            for row, customer in enumerate(customers):
                for col, item in enumerate(customer[1:]):
                    self.table_widget.setItem(row, col, QTableWidgetItem(str(item)))
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la ricerca del cliente: {e}")

    def export_to_csv(self):
        customers = self.customer_manager.get_customers()
        filepath, _ = QFileDialog.getSaveFileName(self, "Esporta CSV", "", "CSV Files (*.csv)")
        if filepath:
            try:
                export_to_csv(customers, filepath)
                QMessageBox.information(self, "Successo", "Esportazione completata con successo.")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante l'esportazione dei dati: {e}")

    def backup_database(self):
        backup_path = "backup_customers.db"
        try:
            backup_database(self.db_path, backup_path)
            QMessageBox.information(self, "Successo", "Backup completato con successo.")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il backup del database: {e}")

    def restore_database(self):
        backup_path = "backup_customers.db"
        try:
            restore_database(backup_path, self.db_path)
            QMessageBox.information(self, "Successo", "Ripristino completato con successo.")
            self.load_customers()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante il ripristino del database: {e}")

class CustomerManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connect_db()

    def connect_db(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.create_table()
        except Exception as e:
            print(f"Errore durante la connessione al database: {e}")
            raise

    def create_table(self):
        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                status TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                notes TEXT
            )
            ''')
            self.conn.commit()
        except Exception as e:
            print(f"Errore durante la creazione della tabella: {e}")
            raise

    def add_customer(self, name, email, password, status, expiry_date, notes):
        try:
            self.cursor.execute('''
            INSERT INTO customers (name, email, password, status, expiry_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, email, password, status, expiry_date, notes))
            self.conn.commit()
        except Exception as e:
            print(f"Errore durante l'aggiunta del cliente: {e}")
            raise

    def update_customer(self, id, name, email, password, status, expiry_date, notes):
        try:
            self.cursor.execute('''
            UPDATE customers
            SET name = ?, email = ?, password = ?, status = ?, expiry_date = ?, notes = ?
            WHERE id = ?
            ''', (name, email, password, status, expiry_date, notes, id))
            self.conn.commit()
        except Exception as e:
            print(f"Errore durante l'aggiornamento del cliente: {e}")
            raise

    def delete_customer(self, id):
        try:
            self.cursor.execute('DELETE FROM customers WHERE id = ?', (id,))
            self.conn.commit()
        except Exception as e:
            print(f"Errore durante l'eliminazione del cliente: {e}")
            raise

    def search_customers(self, search_text):
        try:
            self.cursor.execute('''
            SELECT * FROM customers
            WHERE name LIKE ? OR email LIKE ? OR status LIKE ?
            ''', (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Errore durante la ricerca dei clienti: {e}")
            raise

    def get_customers(self):
        try:
            self.cursor.execute('SELECT * FROM customers')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Errore durante il recupero dei clienti: {e}")
            raise

def backup_database(db_path, backup_path):
    try:
        shutil.copyfile(db_path, backup_path)
    except Exception as e:
        print(f"Errore durante il backup del database: {e}")
        raise

def restore_database(backup_path, db_path):
    try:
        shutil.copyfile(backup_path, db_path)
    except Exception as e:
        print(f"Errore durante il ripristino del database: {e}")
        raise

def export_to_csv(customers, filepath):
    try:
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Nome", "Email", "Stato", "Scadenza", "Note"])
            for customer in customers:
                writer.writerow([customer[1], customer[2], customer[4], customer[5], customer[6]])
    except Exception as e:
        print(f"Errore durante l'esportazione in CSV: {e}")
        raise

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = CustomerManagerUI("customers.db")
    mainWindow.show()
    sys.exit(app.exec_())