"""
PCB Component Inventory Manager - Single-file PyQt6 desktop app

Features:
- SQLite-backed CRUD for components (name, value, footprint, manufacturer, quantity, location, notes)
- Search / filter
- Import / export CSV
- Simple statistics (total parts, distinct types)
- Single-file for easy running and packaging with PyInstaller

Run: python pcb_inventory_manager_app.py
Dependencies: PyQt6 (pip install PyQt6)

"""
import sys
import sqlite3
import csv
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QDialog, QFormLayout, QSpinBox, QTextEdit, QFileDialog
)
from PyQt6.QtCore import Qt

DB_FILE = Path.home() / ".pcb_inventory.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    value TEXT,
    footprint TEXT,
    manufacturer TEXT,
    quantity INTEGER DEFAULT 0,
    location TEXT,
    notes TEXT
);
"""

class Database:
    def __init__(self, path=DB_FILE):
        self.path = path
        self.conn = sqlite3.connect(str(self.path))
        self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()
        cur.executescript(SCHEMA)
        self.conn.commit()

    def add_component(self, data):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO components (name, value, footprint, manufacturer, quantity, location, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (data['name'], data.get('value'), data.get('footprint'), data.get('manufacturer'), data.get('quantity',0), data.get('location'), data.get('notes'))
        )
        self.conn.commit()
        return cur.lastrowid

    def update_component(self, comp_id, data):
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE components
            SET name=?, value=?, footprint=?, manufacturer=?, quantity=?, location=?, notes=?
            WHERE id=?
            """,
            (data['name'], data.get('value'), data.get('footprint'), data.get('manufacturer'), data.get('quantity',0), data.get('location'), data.get('notes'), comp_id)
        )
        self.conn.commit()

    def delete_component(self, comp_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM components WHERE id=?", (comp_id,))
        self.conn.commit()

    def list_components(self, search=None):
        cur = self.conn.cursor()
        if search:
            q = f"%{search}%"
            cur.execute("SELECT * FROM components WHERE name LIKE ? OR value LIKE ? OR footprint LIKE ? OR manufacturer LIKE ? OR location LIKE ? OR notes LIKE ? ORDER BY name", (q, q, q, q, q, q))
        else:
            cur.execute("SELECT * FROM components ORDER BY name")
        return cur.fetchall()

    def get_component(self, comp_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM components WHERE id=?", (comp_id,))
        return cur.fetchone()

    def import_csv(self, filepath):
        with open(filepath, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data = {
                    'name': row.get('name') or row.get('Name') or '',
                    'value': row.get('value') or row.get('Value'),
                    'footprint': row.get('footprint') or row.get('Footprint'),
                    'manufacturer': row.get('manufacturer') or row.get('Manufacturer'),
                    'quantity': int(row.get('quantity') or row.get('Quantity') or 0),
                    'location': row.get('location') or row.get('Location'),
                    'notes': row.get('notes') or row.get('Notes'),
                }
                if data['name']:
                    self.add_component(data)

    def export_csv(self, filepath):
        rows = self.list_components()
        headers = ['id','name','value','footprint','manufacturer','quantity','location','notes']
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(headers)
            for r in rows:
                w.writerow(r)

    def stats(self):
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*), SUM(quantity) FROM components")
        cnt, total_q = cur.fetchone()
        cur.execute("SELECT COUNT(DISTINCT name) FROM components")
        distinct = cur.fetchone()[0]
        return {'rows': cnt or 0, 'total_quantity': total_q or 0, 'distinct_names': distinct or 0}

class ComponentDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Add / Edit Component")
        self.resize(400,300)
        layout = QFormLayout()
        self.name = QLineEdit()
        self.value = QLineEdit()
        self.footprint = QLineEdit()
        self.manufacturer = QLineEdit()
        self.quantity = QSpinBox()
        self.quantity.setMaximum(1000000)
        self.location = QLineEdit()
        self.notes = QTextEdit()
        layout.addRow("Name:", self.name)
        layout.addRow("Value:", self.value)
        layout.addRow("Footprint:", self.footprint)
        layout.addRow("Manufacturer:", self.manufacturer)
        layout.addRow("Quantity:", self.quantity)
        layout.addRow("Location:", self.location)
        layout.addRow("Notes:", self.notes)
        btns = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        main = QVBoxLayout()
        main.addLayout(layout)
        main.addLayout(btns)
        self.setLayout(main)
        if data:
            self.name.setText(data.get('name',''))
            self.value.setText(data.get('value',''))
            self.footprint.setText(data.get('footprint',''))
            self.manufacturer.setText(data.get('manufacturer',''))
            self.quantity.setValue(int(data.get('quantity',0)))
            self.location.setText(data.get('location',''))
            self.notes.setPlainText(data.get('notes',''))

    def get_data(self):
        return {
            'name': self.name.text().strip(),
            'value': self.value.text().strip(),
            'footprint': self.footprint.text().strip(),
            'manufacturer': self.manufacturer.text().strip(),
            'quantity': int(self.quantity.value()),
            'location': self.location.text().strip(),
            'notes': self.notes.toPlainText().strip(),
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCB Component Inventory")
        self.resize(900, 600)
        self.db = Database()
        self._build_ui()
        self.reload_table()

    def _build_ui(self):
        central = QWidget()
        v = QVBoxLayout()

        # Top controls
        top = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, value, footprint, manufacturer, location or notes...")
        self.search_input.returnPressed.connect(self.on_search)
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.on_search)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.on_clear)
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.on_add)
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.on_edit)
        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self.on_delete)
        import_btn = QPushButton("Import CSV")
        import_btn.clicked.connect(self.on_import)
        export_btn = QPushButton("Export CSV")
        export_btn.clicked.connect(self.on_export)
        stats_btn = QPushButton("Stats")
        stats_btn.clicked.connect(self.on_stats)
        top.addWidget(self.search_input)
        top.addWidget(search_btn)
        top.addWidget(clear_btn)
        top.addWidget(add_btn)
        top.addWidget(edit_btn)
        top.addWidget(del_btn)
        top.addWidget(import_btn)
        top.addWidget(export_btn)
        top.addWidget(stats_btn)
        v.addLayout(top)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(['ID','Name','Value','Footprint','Manufacturer','Quantity','Location','Notes'])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        v.addWidget(self.table)

        central.setLayout(v)
        self.setCentralWidget(central)

    def reload_table(self, search=None):
        rows = self.db.list_components(search)
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val) if val is not None else '')
                if c == 0:
                    item.setData(Qt.ItemDataRole.UserRole, row[0])
                self.table.setItem(r, c, item)
        self.table.resizeColumnsToContents()

    def get_selected_id(self):
        sel = self.table.selectedItems()
        if not sel:
            return None
        row = sel[0].row()
        id_item = self.table.item(row, 0)
        try:
            return int(id_item.text())
        except Exception:
            return None

    def on_search(self):
        term = self.search_input.text().strip()
        self.reload_table(term if term else None)

    def on_clear(self):
        self.search_input.clear()
        self.reload_table()

    def on_add(self):
        dlg = ComponentDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Missing name", "Component must have a name")
                return
            self.db.add_component(data)
            self.reload_table()

    def on_edit(self):
        comp_id = self.get_selected_id()
        if not comp_id:
            QMessageBox.information(self, "Select row", "Please select a component to edit")
            return
        rec = self.db.get_component(comp_id)
        data = {
            'name': rec[1], 'value': rec[2], 'footprint': rec[3], 'manufacturer': rec[4], 'quantity': rec[5], 'location': rec[6], 'notes': rec[7]
        }
        dlg = ComponentDialog(self, data)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new = dlg.get_data()
            if not new['name']:
                QMessageBox.warning(self, "Missing name", "Component must have a name")
                return
            self.db.update_component(comp_id, new)
            self.reload_table()

    def on_delete(self):
        comp_id = self.get_selected_id()
        if not comp_id:
            QMessageBox.information(self, "Select row", "Please select a component to delete")
            return
        reply = QMessageBox.question(self, "Confirm delete", "Delete selected component?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_component(comp_id)
            self.reload_table()

    def on_import(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import CSV", str(Path.home()), "CSV Files (*.csv);;All Files (*)")
        if path:
            try:
                self.db.import_csv(path)
                QMessageBox.information(self, "Import complete", "CSV import finished")
                self.reload_table()
            except Exception as e:
                QMessageBox.critical(self, "Import failed", str(e))

    def on_export(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", str(Path.home() / "components_export.csv"), "CSV Files (*.csv);;All Files (*)")
        if path:
            try:
                self.db.export_csv(path)
                QMessageBox.information(self, "Export complete", "CSV exported")
            except Exception as e:
                QMessageBox.critical(self, "Export failed", str(e))

    def on_stats(self):
        s = self.db.stats()
        QMessageBox.information(self, "Stats", f"Rows: {s['rows']}\nDistinct names: {s['distinct_names']}\nTotal quantity: {s['total_quantity']}")

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
