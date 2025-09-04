import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem,
                             QComboBox, QTextEdit, QDialog, QFormLayout, QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt

class ContactManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление контактами")
        self.setGeometry(100, 100, 900, 600)
        self.init_ui()
        self.init_db()
        self.load_groups()
        self.load_contacts()

    def init_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        # Фильтр по группе и поиск
        filter_layout = QHBoxLayout()
        self.group_filter = QComboBox()
        self.group_filter.addItem("Все группы")
        self.group_filter.currentTextChanged.connect(self.load_contacts)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по ФИО, телефону, email")
        self.search_input.textChanged.connect(self.load_contacts)
        filter_layout.addWidget(QLabel("Группа:"))
        filter_layout.addWidget(self.group_filter)
        filter_layout.addWidget(QLabel("Поиск:"))
        filter_layout.addWidget(self.search_input)
        layout.addLayout(filter_layout)

        # Таблица контактов
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Телефон", "Email", "Группа"])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        layout.addWidget(self.table)

        # Кнопки действий
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить контакт")
        add_btn.clicked.connect(self.add_contact)
        edit_btn = QPushButton("Редактировать контакт")
        edit_btn.clicked.connect(self.edit_contact)
        del_btn = QPushButton("Удалить контакт")
        del_btn.clicked.connect(self.delete_contact)
        manage_groups_btn = QPushButton("Управление группами")
        manage_groups_btn.clicked.connect(self.manage_groups)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(manage_groups_btn)
        layout.addLayout(btn_layout)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def init_db(self):
        conn = sqlite3.connect("contacts.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                group_name TEXT,
                notes TEXT,
                FOREIGN KEY(group_name) REFERENCES groups(name)
            )
        ''')
        # Тестовые данные
        cursor.execute("SELECT COUNT(*) FROM groups")
        if cursor.fetchone()[0] == 0:
            groups = [("Семья",), ("Работа",), ("Друзья",)]
            cursor.executemany("INSERT INTO groups(name) VALUES(?)", groups)
        cursor.execute("SELECT COUNT(*) FROM contacts")
        if cursor.fetchone()[0] == 0:
            contacts = [
                ("Иванов И.И.", "+79161234567", "ivanov@example.com", "Работа", "Менеджер"),
                ("Петров П.П.", "+79261234567", "petrov@example.com", "Друзья", "Школьный друг"),
                ("Сидорова С.С.", "+79361234567", "sidorova@example.com", "Семья", "Сестра")
            ]
            cursor.executemany(
                "INSERT INTO contacts(full_name, phone, email, group_name, notes) VALUES(?,?,?,?,?)",
                contacts
            )
        conn.commit()
        conn.close()

    def load_groups(self):
        conn = sqlite3.connect("contacts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM groups ORDER BY name")
        self.group_filter.blockSignals(True)
        for name, in cursor.fetchall():
            self.group_filter.addItem(name)
        self.group_filter.blockSignals(False)
        conn.close()

    def load_contacts(self):
        self.table.setRowCount(0)
        search = self.search_input.text().strip().lower()
        group = self.group_filter.currentText()
        conn = sqlite3.connect("contacts.db")
        cursor = conn.cursor()
        query = "SELECT id, full_name, phone, email, group_name FROM contacts"
        conditions, params = [], []
        if group != "Все группы":
            conditions.append("group_name = ?")
            params.append(group)
        if search:
            conditions.append("(LOWER(full_name) LIKE ? OR phone LIKE ? OR LOWER(email) LIKE ?)")
            w = f"%{search}%"
            params.extend([w, w, w])
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY full_name"
        cursor.execute(query, params)
        for i, row in enumerate(cursor.fetchall()):
            self.table.insertRow(i)
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))
        conn.close()
        # Растягиваем все колонки по ширине таблицы
        from PyQt5.QtWidgets import QHeaderView
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

    def add_contact(self):
        dlg = ContactDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.load_groups(); self.load_contacts()

    def edit_contact(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите контакт для редактирования")
            return
        contact_id = int(self.table.item(row, 0).text())
        dlg = ContactDialog(self, contact_id)
        if dlg.exec_() == QDialog.Accepted:
            self.load_contacts()

    def delete_contact(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите контакт для удаления")
            return
        contact_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(self, "Удаление", "Удалить контакт?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect("contacts.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            conn.commit(); conn.close()
            self.load_contacts()

    def manage_groups(self):
        dlg = GroupDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.group_filter.clear(); self.group_filter.addItem("Все группы"); self.load_groups(); self.load_contacts()

class ContactDialog(QDialog):
    def __init__(self, parent=None, contact_id=None):
        super().__init__(parent)
        self.contact_id = contact_id
        self.setWindowTitle("Контакт")
        self.init_ui()
        if contact_id:
            self.load_data()

    def init_ui(self):
        form = QFormLayout(self)
        self.name = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.group = QComboBox()
        conn = sqlite3.connect("contacts.db")
        cursor = conn.cursor(); cursor.execute("SELECT name FROM groups ORDER BY name")
        for name, in cursor.fetchall(): self.group.addItem(name)
        conn.close()
        self.notes = QTextEdit()
        form.addRow("ФИО:", self.name)
        form.addRow("Телефон:", self.phone)
        form.addRow("Email:", self.email)
        form.addRow("Группа:", self.group)
        form.addRow("Заметки:", self.notes)
        btns = QHBoxLayout()
        save = QPushButton("Сохранить"); save.clicked.connect(self.save)
        cancel = QPushButton("Отмена"); cancel.clicked.connect(self.reject)
        btns.addWidget(save); btns.addWidget(cancel)
        form.addRow(btns)

    def load_data(self):
        conn = sqlite3.connect("contacts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, phone, email, group_name, notes FROM contacts WHERE id = ?", (self.contact_id,))
        full, ph, em, grp, notes = cursor.fetchone(); conn.close()
        self.name.setText(full); self.phone.setText(ph); self.email.setText(em);
        idx = self.group.findText(grp); self.group.setCurrentIndex(idx if idx>=0 else 0)
        self.notes.setPlainText(notes)

    def save(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Ошибка", "ФИО обязательно")
            return
        conn = sqlite3.connect("contacts.db")
        cursor = conn.cursor()
        data = (self.name.text().strip(), self.phone.text().strip(), self.email.text().strip(),
                self.group.currentText(), self.notes.toPlainText())
        if self.contact_id:
            cursor.execute("UPDATE contacts SET full_name=?, phone=?, email=?, group_name=?, notes=? WHERE id=?", (*data, self.contact_id))
        else:
            cursor.execute("INSERT INTO contacts(full_name, phone, email, group_name, notes) VALUES(?,?,?,?,?)", data)
        conn.commit(); conn.close()
        self.accept()

class GroupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Группы контактов")
        self.init_ui()
        self.load_groups()

    def init_ui(self):
        self.setMinimumWidth(300)
        form = QVBoxLayout(self)
        self.list = QTableWidget(); self.list.setColumnCount(1); self.list.setHorizontalHeaderLabels(["Группа"])
        form.addWidget(self.list)
        btns = QHBoxLayout()
        add = QPushButton("Добавить"); add.clicked.connect(self.add_group)
        edit = QPushButton("Переименовать"); edit.clicked.connect(self.rename_group)
        delete = QPushButton("Удалить"); delete.clicked.connect(self.delete_group)
        close = QPushButton("Закрыть"); close.clicked.connect(self.accept)
        for w in (add, edit, delete, close): btns.addWidget(w);
        form.addLayout(btns)

    def load_groups(self):
        self.list.setRowCount(0)
        conn = sqlite3.connect("contacts.db")
        cursor = conn.cursor(); cursor.execute("SELECT name FROM groups ORDER BY name")
        for i, (name,) in enumerate(cursor.fetchall()):
            self.list.insertRow(i); self.list.setItem(i,0,QTableWidgetItem(name))
        conn.close()

    def add_group(self):
        text, ok = QInputDialog.getText(self, "Новая группа", "Введите название группы:")
        if ok and text.strip():
            conn = sqlite3.connect("contacts.db")
            try:
                conn.execute("INSERT INTO groups(name) VALUES(?)", (text.strip(),))
                conn.commit()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Ошибка", "Группа уже существует")
            conn.close(); self.load_groups()

    def rename_group(self):
        row = self.list.currentRow()
        if row<0: return
        old = self.list.item(row,0).text()
        new, ok = QInputDialog.getText(self, "Переименовать", "Новое название:", text=old)
        if ok and new.strip():
            conn = sqlite3.connect("contacts.db")
            conn.execute("UPDATE groups SET name=? WHERE name=?", (new.strip(), old))
            conn.execute("UPDATE contacts SET group_name=? WHERE group_name=?", (new.strip(), old))
            conn.commit(); conn.close(); self.load_groups()

    def delete_group(self):
        row = self.list.currentRow()
        if row<0: return
        name = self.list.item(row,0).text()
        reply = QMessageBox.question(self, "Удалить группу", f"Удалить группу '{name}'?", QMessageBox.Yes|QMessageBox.No)
        if reply==QMessageBox.Yes:
            conn = sqlite3.connect("contacts.db")
            conn.execute("DELETE FROM groups WHERE name=?", (name,))
            conn.execute("UPDATE contacts SET group_name=NULL WHERE group_name=?", (name,))
            conn.commit(); conn.close(); self.load_groups()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget { background-color:#f0f0f0; font-size:14px; }
        QLineEdit, QComboBox, QDateEdit, QTextEdit { border:1px solid #ccc; border-radius:4px; padding:6px; }
        QPushButton { background-color:#28a745; color:white; padding:6px 12px; border:none; border-radius:4px; }
        QPushButton:hover { background-color:#218838; }
        QTableWidget { background:white; border:1px solid #ccc; gridline-color:#eee; }
        QHeaderView::section { background-color:#28a745; color:white; padding:4px; border:none; }
    """)
    window = ContactManager()
    window.show()
    sys.exit(app.exec_())
