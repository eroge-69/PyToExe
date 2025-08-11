"""
Raktárkészlet nyilvántartó (MVP) - egy fájl
Technológiák: Python 3.9+, PyQt6, sqlite3
Használat:
 1) Telepítsd a függőségeket:
    pip install PyQt6
 2) Futtatás fejlesztés módban:
    python raktar_keszlet.py
 3) EXE készítése (PyInstaller-rel):
    pip install pyinstaller
    pyinstaller --onefile --add-data "raktar.db;." raktar_keszlet.py

Funkciók (MVP):
 - SQLite adatbázis (raktar.db)
 - Tétel lista / hozzáadás / szerkesztés / törlés
 - Bevét / Kiadás tranzakciók (mozgás naplózása)
 - Helyszínek (raktár polc) és beszállítók alapok
 - Keresés / szűrés / CSV export-import
 - Audit (módosítások naplója)

Ez egy működő, egyszerű, de bővíthető alap — igény szerint hozzáadok:
 - felhasználókezelés / jelszó
 - barcode/​scanner integráció
 - PDF riportok, nyomtatás
 - REST API / hálózati többfelhasználós mód

Kérlek írd meg, ha ezt a Python+PyQt megoldást akarod, vagy inkább C# / WPF-t.
"""

import sys
import sqlite3
import csv
from datetime import datetime
from pathlib import Path

from PyQt6 import QtWidgets, QtGui, QtCore

DB_PATH = Path("raktar.db")

# ---------- DB inicializálás ----------

def init_db():
    first = not DB_PATH.exists()
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        sku TEXT UNIQUE,
        name TEXT,
        description TEXT,
        location TEXT,
        supplier TEXT,
        quantity REAL DEFAULT 0
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        item_id INTEGER,
        delta REAL,
        type TEXT,
        note TEXT,
        timestamp TEXT,
        user TEXT,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS audit (
        id INTEGER PRIMARY KEY,
        action TEXT,
        detail TEXT,
        timestamp TEXT,
        user TEXT
    )
    ''')

    conn.commit()
    if first:
        seed_example(conn)
    return conn


def seed_example(conn):
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    items = [
        ("SKU-0001", "Csavar M4 20mm", "Rozsdamentes", "Polc A1", "Beszallito Kft.", 120),
        ("SKU-0002", "Anyacsavar M4", "", "Polc A1", "Beszallito Kft.", 200),
    ]
    for sku, name, desc, loc, sup, q in items:
        cur.execute('INSERT OR IGNORE INTO items (sku,name,description,location,supplier,quantity) VALUES (?,?,?,?,?,?)',
                    (sku, name, desc, loc, sup, q))
    cur.execute('INSERT INTO audit (action,detail,timestamp,user) VALUES (?,?,?,?)', ("seed","példa adatok", now, "system"))
    conn.commit()

# ---------- Adatelérés helperek ----------

class DB:
    def __init__(self, conn):
        self.conn = conn

    def get_items(self, search=None):
        cur = self.conn.cursor()
        if search:
            q = f"%{search}%"
            cur.execute("SELECT id,sku,name,description,location,supplier,quantity FROM items WHERE sku LIKE ? OR name LIKE ? OR description LIKE ? OR location LIKE ? OR supplier LIKE ? ORDER BY name",
                        (q,q,q,q,q))
        else:
            cur.execute("SELECT id,sku,name,description,location,supplier,quantity FROM items ORDER BY name")
        return cur.fetchall()

    def add_item(self, sku, name, description, location, supplier, quantity):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO items (sku,name,description,location,supplier,quantity) VALUES (?,?,?,?,?,?)',
                    (sku,name,description,location,supplier,quantity))
        self.conn.commit()
        self._audit('add_item', f'sku={sku} name={name}')

    def update_item(self, item_id, **kwargs):
        cur = self.conn.cursor()
        fields = []
        vals = []
        for k,v in kwargs.items():
            fields.append(f"{k}=?")
            vals.append(v)
        vals.append(item_id)
        cur.execute(f"UPDATE items SET {','.join(fields)} WHERE id=?", vals)
        self.conn.commit()
        self._audit('update_item', f'id={item_id} changed={kwargs}')

    def delete_item(self, item_id):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM items WHERE id=?', (item_id,))
        self.conn.commit()
        self._audit('delete_item', f'id={item_id}')

    def transact(self, item_id, delta, type_, note='', user='local'):
        cur = self.conn.cursor()
        now = datetime.utcnow().isoformat()
        cur.execute('INSERT INTO transactions (item_id,delta,type,note,timestamp,user) VALUES (?,?,?,?,?,?)',
                    (item_id, delta, type_, note, now, user))
        cur.execute('UPDATE items SET quantity = quantity + ? WHERE id=?', (delta, item_id))
        self.conn.commit()
        self._audit('transact', f'id={item_id} delta={delta} type={type_} note={note}')

    def get_transactions(self, item_id=None, limit=200):
        cur = self.conn.cursor()
        if item_id:
            cur.execute('SELECT id,item_id,delta,type,note,timestamp,user FROM transactions WHERE item_id=? ORDER BY timestamp DESC LIMIT ?', (item_id, limit))
        else:
            cur.execute('SELECT id,item_id,delta,type,note,timestamp,user FROM transactions ORDER BY timestamp DESC LIMIT ?', (limit,))
        return cur.fetchall()

    def export_csv(self, filepath):
        rows = self.get_items()
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['id','sku','name','description','location','supplier','quantity'])
            for r in rows:
                w.writerow(r)
        self._audit('export_csv', f'file={filepath}')

    def import_csv(self, filepath):
        with open(filepath, newline='', encoding='utf-8') as f:
            r = csv.DictReader(f)
            cur = self.conn.cursor()
            for row in r:
                # upsert by sku
                sku = row.get('sku')
                name = row.get('name','')
                desc = row.get('description','')
                loc = row.get('location','')
                sup = row.get('supplier','')
                qty = float(row.get('quantity') or 0)
                cur.execute('SELECT id FROM items WHERE sku=?', (sku,))
                found = cur.fetchone()
                if found:
                    cur.execute('UPDATE items SET name=?,description=?,location=?,supplier=?,quantity=? WHERE sku=?', (name,desc,loc,sup,qty,sku))
                else:
                    cur.execute('INSERT INTO items (sku,name,description,location,supplier,quantity) VALUES (?,?,?,?,?,?)', (sku,name,desc,loc,sup,qty))
            self.conn.commit()
        self._audit('import_csv', f'file={filepath}')

    def _audit(self, action, detail, user='local'):
        cur = self.conn.cursor()
        now = datetime.utcnow().isoformat()
        cur.execute('INSERT INTO audit (action,detail,timestamp,user) VALUES (?,?,?,?)', (action,detail,now,user))
        self.conn.commit()

# ---------- GUI ----------

class ItemDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.setWindowTitle('Tétel')
        self.resize(400,300)
        layout = QtWidgets.QFormLayout(self)
        self.sku = QtWidgets.QLineEdit()
        self.name = QtWidgets.QLineEdit()
        self.desc = QtWidgets.QTextEdit()
        self.location = QtWidgets.QLineEdit()
        self.supplier = QtWidgets.QLineEdit()
        self.quantity = QtWidgets.QDoubleSpinBox()
        self.quantity.setMaximum(1_000_000)
        self.quantity.setDecimals(3)
        layout.addRow('SKU', self.sku)
        layout.addRow('Név', self.name)
        layout.addRow('Leírás', self.desc)
        layout.addRow('Hely', self.location)
        layout.addRow('Szállító', self.supplier)
        layout.addRow('Mennyiség', self.quantity)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

        if item:
            self.sku.setText(item[1])
            self.name.setText(item[2])
            self.desc.setPlainText(item[3] or '')
            self.location.setText(item[4] or '')
            self.supplier.setText(item[5] or '')
            self.quantity.setValue(item[6] or 0)

    def values(self):
        return {
            'sku': self.sku.text().strip(),
            'name': self.name.text().strip(),
            'description': self.desc.toPlainText().strip(),
            'location': self.location.text().strip(),
            'supplier': self.supplier.text().strip(),
            'quantity': self.quantity.value()
        }

class TransactDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.setWindowTitle('Tranzakció')
        layout = QtWidgets.QFormLayout(self)
        self.item = item
        self.delta = QtWidgets.QDoubleSpinBox()
        self.delta.setDecimals(3)
        self.delta.setMaximum(1_000_000)
        self.type = QtWidgets.QComboBox()
        self.type.addItems(['BEVETEL','KIADAS','Áthelyezés','KORRIGALAS'])
        self.note = QtWidgets.QLineEdit()
        layout.addRow('Tétel', QtWidgets.QLabel(item[2] if item else ''))
        layout.addRow('Mennyiség (+/-)', self.delta)
        layout.addRow('Típus', self.type)
        layout.addRow('Megjegyzés', self.note)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

    def values(self):
        return self.delta.value(), self.type.currentText(), self.note.text().strip()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, db:DB):
        super().__init__()
        self.db = db
        self.setWindowTitle('Raktár készlet nyilvántartó')
        self.resize(900,600)

        central = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(central)

        # Toolbar
        toolbar = QtWidgets.QHBoxLayout()
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText('Keresés SKU/név/leírás/hely...')
        btn_search = QtWidgets.QPushButton('Keres')
        btn_search.clicked.connect(self.reload)
        btn_add = QtWidgets.QPushButton('Új tétel')
        btn_add.clicked.connect(self.add_item)
        btn_edit = QtWidgets.QPushButton('Szerkeszt')
        btn_edit.clicked.connect(self.edit_item)
        btn_delete = QtWidgets.QPushButton('Töröl')
        btn_delete.clicked.connect(self.delete_item)
        btn_trans = QtWidgets.QPushButton('Tranzakció')
        btn_trans.clicked.connect(self.transact_item)
        btn_export = QtWidgets.QPushButton('Export CSV')
        btn_export.clicked.connect(self.export_csv)
        btn_import = QtWidgets.QPushButton('Import CSV')
        btn_import.clicked.connect(self.import_csv)
        toolbar.addWidget(self.search)
        toolbar.addWidget(btn_search)
        toolbar.addWidget(btn_add)
        toolbar.addWidget(btn_edit)
        toolbar.addWidget(btn_delete)
        toolbar.addWidget(btn_trans)
        toolbar.addWidget(btn_export)
        toolbar.addWidget(btn_import)

        v.addLayout(toolbar)

        # Table
        self.table = QtWidgets.QTableWidget(0,7)
        self.table.setHorizontalHeaderLabels(['ID','SKU','Név','Leírás','Hely','Szállító','Mennyiség'])
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        v.addWidget(self.table)

        # Bottom: transactions preview
        h = QtWidgets.QHBoxLayout()
        self.tx_list = QtWidgets.QListWidget()
        h.addWidget(QtWidgets.QLabel('Utolsó tranzakciók'))
        h.addWidget(self.tx_list)
        v.addLayout(h)

        self.setCentralWidget(central)
        self.reload()
        self.table.itemSelectionChanged.connect(self.on_select)

    def reload(self):
        search = self.search.text().strip()
        rows = self.db.get_items(search if search else None)
        self.table.setRowCount(0)
        for r in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for c, val in enumerate(r):
                it = QtWidgets.QTableWidgetItem(str(val))
                if c==6: # quantity numeric
                    it.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row, c, it)
        self.tx_list.clear()
        txs = self.db.get_transactions(limit=20)
        for t in txs:
            self.tx_list.addItem(f"{t[5]} | id:{t[0]} item:{t[1]} {t[2]} ({t[3]}) @ {t[4]}")

    def get_selected_item(self):
        sel = self.table.selectedItems()
        if not sel:
            return None
        row = sel[0].row()
        vals = [self.table.item(row,c).text() for c in range(self.table.columnCount())]
        # cast id and quantity
        try:
            vals[0] = int(vals[0])
            vals[6] = float(vals[6])
        except:
            pass
        return vals

    def add_item(self):
        d = ItemDialog(self)
        if d.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            v = d.values()
            try:
                self.db.add_item(v['sku'], v['name'], v['description'], v['location'], v['supplier'], v['quantity'])
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Hiba', str(e))
            self.reload()

    def edit_item(self):
        sel = self.get_selected_item()
        if not sel:
            QtWidgets.QMessageBox.information(self, 'Info', 'Válassz ki egy tételt a szerkesztéshez')
            return
        # build item tuple consistent with DB rows
        item = (sel[0], sel[1], sel[2], sel[3], sel[4], sel[5], sel[6])
        d = ItemDialog(self, item)
        if d.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            v = d.values()
            try:
                self.db.update_item(item[0], sku=v['sku'], name=v['name'], description=v['description'], location=v['location'], supplier=v['supplier'], quantity=v['quantity'])
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Hiba', str(e))
            self.reload()

    def delete_item(self):
        sel = self.get_selected_item()
        if not sel:
            QtWidgets.QMessageBox.information(self, 'Info', 'Válassz ki egy tételt a törléshez')
            return
        ret = QtWidgets.QMessageBox.question(self, 'Törlés', f"Tényleg törlöd a tételt: {sel[2]} ?")
        if ret == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_item(sel[0])
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Hiba', str(e))
            self.reload()

    def transact_item(self):
        sel = self.get_selected_item()
        if not sel:
            QtWidgets.QMessageBox.information(self, 'Info', 'Válassz ki egy tételt a tranzakcióhoz')
            return
        item = (sel[0], sel[1], sel[2], sel[3], sel[4], sel[5], sel[6])
        d = TransactDialog(self, item)
        if d.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            delta, type_, note = d.values()
            if delta == 0:
                QtWidgets.QMessageBox.information(self, 'Info', 'A mennyiség nem lehet 0')
                return
            # sign for BEVETEL positive, KIADAS negative
            if type_ == 'KIADAS' and delta>0:
                delta = -abs(delta)
            if type_ == 'BEVETEL' and delta<0:
                delta = abs(delta)
            try:
                self.db.transact(item[0], delta, type_, note)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, 'Hiba', str(e))
            self.reload()

    def on_select(self):
        sel = self.get_selected_item()
        if not sel:
            return
        txs = self.db.get_transactions(item_id=sel[0], limit=50)
        self.tx_list.clear()
        for t in txs:
            self.tx_list.addItem(f"{t[5]} | {t[2]} ({t[3]}) @ {t[4]}")

    def export_csv(self):
        fn, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Export CSV', filter='CSV Files (*.csv)')
        if not fn:
            return
        try:
            self.db.export_csv(fn)
            QtWidgets.QMessageBox.information(self, 'Kész', 'Exportálás sikeres')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Hiba', str(e))

    def import_csv(self):
        fn, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Import CSV', filter='CSV Files (*.csv)')
        if not fn:
            return
        try:
            self.db.import_csv(fn)
            QtWidgets.QMessageBox.information(self, 'Kész', 'Import sikeres')
            self.reload()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Hiba', str(e))


# ---------- Indítás ----------

def main():
    conn = init_db()
    db = DB(conn)
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow(db)
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
