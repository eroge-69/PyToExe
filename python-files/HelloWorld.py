import os
import sys
import csv
import sqlite3
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from typing import Optional, List, Tuple

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QAction, QColor, QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QGridLayout, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QLineEdit,
    QDateEdit, QComboBox, QMessageBox, QFileDialog, QSplitter, QFrame, QGroupBox
)

DB_FILE = "seat_manager.db"
SEAT_COUNT = 30
SEAT_ROWS = 6
SEAT_COLS = 5

# ---------------------- Data Layer (SQLite) ----------------------

class DB:
    def __init__(self, path: str = DB_FILE):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.ensure_schema()

    def ensure_schema(self):
        cur = self.conn.cursor()
        # Students
        cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            monthly_fee INTEGER NOT NULL DEFAULT 1500,
            assigned_seat INTEGER UNIQUE, -- 1..30, unique if assigned
            start_date TEXT,              -- ISO date
            next_due_date TEXT            -- ISO date
        );
        """)
        # Seats
        cur.execute("""
        CREATE TABLE IF NOT EXISTS seats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seat_number INTEGER UNIQUE NOT NULL,  -- 1..30
            notes TEXT
        );
        """)
        # Transactions
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dt TEXT NOT NULL,                 -- ISO datetime
            type TEXT NOT NULL,               -- Income | Expense
            category TEXT NOT NULL,           -- Membership Fee, Utilities, Rent, Supplies, Maintenance, Other
            amount INTEGER NOT NULL,          -- store in INR
            description TEXT,
            student_id INTEGER,
            FOREIGN KEY(student_id) REFERENCES students(id)
        );
        """)
        self.conn.commit()
        # Seed seats if empty
        cur.execute("SELECT COUNT(*) AS c FROM seats;")
        if cur.fetchone()["c"] == 0:
            cur.executemany("INSERT INTO seats(seat_number, notes) VALUES(?, ?);",
                            [(i, "") for i in range(1, SEAT_COUNT + 1)])
            self.conn.commit()

    # --------- Seats ---------
    def list_seats(self) -> List[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM seats ORDER BY seat_number;").fetchall()

    def seat_occupant(self, seat_number: int) -> Optional[sqlite3.Row]:
        return self.conn.execute("SELECT * FROM students WHERE assigned_seat = ?;", (seat_number,)).fetchone()

    def update_seat_notes(self, seat_number: int, notes: str):
        self.conn.execute("UPDATE seats SET notes = ? WHERE seat_number = ?;", (notes, seat_number))
        self.conn.commit()

    # --------- Students ---------
    def list_students(self) -> List[sqlite3.Row]:
        return self.conn.execute("""
            SELECT s.*, 
                CASE 
                  WHEN next_due_date IS NULL THEN 'Unknown'
                  WHEN date(next_due_date) < date('now','localtime') THEN 'Overdue'
                  ELSE 'Paid'
                END AS payment_status
            FROM students s
            ORDER BY name COLLATE NOCASE;
        """).fetchall()

    def add_student(self, name: str, phone: str, monthly_fee: int,
                    assigned_seat: Optional[int], start_date: Optional[str], next_due_date: Optional[str]):
        self.conn.execute("""
            INSERT INTO students(name, phone, monthly_fee, assigned_seat, start_date, next_due_date)
            VALUES(?,?,?,?,?,?);
        """, (name, phone, monthly_fee, assigned_seat, start_date, next_due_date))
        self.conn.commit()

    def update_student(self, student_id: int, name: str, phone: str, monthly_fee: int,
                       assigned_seat: Optional[int], start_date: Optional[str], next_due_date: Optional[str]):
        self.conn.execute("""
            UPDATE students SET name=?, phone=?, monthly_fee=?, assigned_seat=?, start_date=?, next_due_date=?
            WHERE id = ?;
        """, (name, phone, monthly_fee, assigned_seat, start_date, next_due_date, student_id))
        self.conn.commit()

    def delete_student(self, student_id: int):
        # Free seat
        self.conn.execute("UPDATE students SET assigned_seat=NULL WHERE id=?;", (student_id,))
        self.conn.execute("DELETE FROM students WHERE id=?;", (student_id,))
        self.conn.commit()

    def students_payment_due_within_days(self, days: int) -> List[sqlite3.Row]:
        return self.conn.execute("""
            SELECT * FROM students 
            WHERE next_due_date IS NOT NULL 
              AND date(next_due_date) BETWEEN date('now','localtime') AND date('now','+{} day','localtime')
            ORDER BY date(next_due_date);
        """.format(days)).fetchall()

    def students_overdue(self) -> List[sqlite3.Row]:
        return self.conn.execute("""
            SELECT * FROM students 
            WHERE next_due_date IS NOT NULL AND date(next_due_date) < date('now','localtime')
            ORDER BY date(next_due_date);
        """).fetchall()

    # --------- Transactions ---------
    def add_transaction(self, dt_iso: str, type_: str, category: str,
                        amount: int, description: str, student_id: Optional[int]):
        self.conn.execute("""
            INSERT INTO transactions(dt, type, category, amount, description, student_id)
            VALUES(?,?,?,?,?,?);
        """, (dt_iso, type_, category, amount, description, student_id))
        self.conn.commit()

    def month_summary(self, year: int, month: int) -> Tuple[int, int, int]:
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)
        rows = self.conn.execute("""
            SELECT type, SUM(amount) AS total FROM transactions
            WHERE date(dt) >= ? AND date(dt) < ?
            GROUP BY type;
        """, (start.isoformat(), end.isoformat())).fetchall()
        income = sum(r["total"] for r in rows if r["type"] == "Income") if rows else 0
        expense = sum(r["total"] for r in rows if r["type"] == "Expense") if rows else 0
        return income, expense, income - expense

# ---------------------- UI Helpers ----------------------

GREEN = QColor("#22c55e")
BLUE  = QColor("#3b82f6")
RED   = QColor("#ef4444")
GREY  = QColor("#9ca3af")
CARD_BG = "#0b1220"
CARD_ACCENT = "#1f2a44"
FG = "#e5e7eb"

def fmt_money(n: int) -> str:
    return f"₹{n:,}"

def to_iso(qdate: QDate) -> Optional[str]:
    if not qdate or not qdate.isValid():
        return None
    return date(qdate.year(), qdate.month(), qdate.day()).isoformat()

def from_iso(s: Optional[str]) -> Optional[QDate]:
    if not s:
        return None
    y, m, d = map(int, s.split("-"))
    return QDate(y, m, d)

def bump_one_month(d: date) -> date:
    y, m = d.year, d.month
    if m == 12:
        return date(y+1, 1, min(d.day, 28))
    return date(y, m+1, min(d.day, 28))

# ---------------------- Dialogs ----------------------

class StudentDialog(QDialog):
    def __init__(self, db: DB, student: Optional[sqlite3.Row] = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.student = student
        self.setWindowTitle("Student" + (" (Edit)" if student else " (New)"))
        self.setMinimumWidth(420)
        form = QFormLayout(self)

        self.name = QLineEdit()
        self.phone = QLineEdit()
        self.fee = QLineEdit()
        self.fee.setText("1500")
        self.seat = QComboBox()
        self.seat.addItem("— None —", userData=None)
        # seats 1..30 and show occupied
        for seat in self.db.list_seats():
            occ = self.db.seat_occupant(seat["seat_number"])
            label = f"Seat {seat['seat_number']}" + (f" (Occupied by {occ['name']})" if occ else "")
            self.seat.addItem(label, userData=seat["seat_number"])
            if occ:
                idx = self.seat.count() - 1
                self.seat.model().item(idx).setEnabled(False)

        self.start = QDateEdit()
        self.start.setCalendarPopup(True)
        self.start.setDate(QDate.currentDate())

        self.due = QDateEdit()
        self.due.setCalendarPopup(True)
        self.due.setDate(QDate.currentDate().addMonths(1))

        if student:
            self.name.setText(student["name"])
            self.phone.setText(student["phone"] or "")
            self.fee.setText(str(student["monthly_fee"]))
            if student["assigned_seat"]:
                # set combobox to that seat
                for i in range(self.seat.count()):
                    if self.seat.itemData(i) == student["assigned_seat"]:
                        self.seat.setCurrentIndex(i)
                        break
            if student["start_date"]:
                self.start.setDate(from_iso(student["start_date"]))
            if student["next_due_date"]:
                self.due.setDate(from_iso(student["next_due_date"]))

        form.addRow("Name", self.name)
        form.addRow("Phone", self.phone)
        form.addRow("Monthly Fee (₹)", self.fee)
        form.addRow("Assigned Seat", self.seat)
        form.addRow("Start Date", self.start)
        form.addRow("Next Due Date", self.due)

        btns = QHBoxLayout()
        save = QPushButton("Save")
        save.clicked.connect(self.on_save)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        btns.addWidget(save)
        btns.addWidget(cancel)
        form.addRow(btns)

    def on_save(self):
        try:
            monthly_fee = int(self.fee.text().strip() or "1500")
        except ValueError:
            QMessageBox.warning(self, "Invalid", "Monthly fee must be a number.")
            return
        name = self.name.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid", "Name is required.")
            return
        phone = self.phone.text().strip()
        assigned = self.seat.currentData()
        start_iso = to_iso(self.start.date())
        due_iso = to_iso(self.due.date())
        if self.student:
            self.db.update_student(self.student["id"], name, phone, monthly_fee,
                                   assigned, start_iso, due_iso)
        else:
            self.db.add_student(name, phone, monthly_fee, assigned, start_iso, due_iso)
        self.accept()

class PaymentDialog(QDialog):
    def __init__(self, db: DB, student: sqlite3.Row, parent=None):
        super().__init__(parent)
        self.db = db
        self.st = student
        self.setWindowTitle(f"Log Payment - {student['name']}")
        form = QFormLayout(self)
        self.amount = QLineEdit(str(student["monthly_fee"]))
        self.desc = QLineEdit(f"{student['name']} - Monthly Fee")
        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.currentDate())
        self.category = QComboBox()
        self.category.addItems(["Membership Fee"])
        form.addRow("Amount (₹)", self.amount)
        form.addRow("Description", self.desc)
        form.addRow("Date", self.date)
        form.addRow("Category", self.category)
        btns = QHBoxLayout()
        pay = QPushButton("Record Payment")
        pay.clicked.connect(self.on_pay)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        btns.addWidget(pay)
        btns.addWidget(cancel)
        form.addRow(btns)

    def on_pay(self):
        try:
            amt = int(self.amount.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Invalid", "Amount must be a number.")
            return
        dt_iso = date(self.date.date().year(), self.date.date().month(), self.date.date().day()).isoformat()
        self.db.add_transaction(dt_iso, "Income", self.category.currentText(), amt, self.desc.text().strip(), self.st["id"])
        # bump next due date by a month (from current next_due_date if present else today)
        current_due = self.st["next_due_date"]
        base = date.fromisoformat(current_due) if current_due else date.today()
        new_due = bump_one_month(base)
        self.db.update_student(self.st["id"], self.st["name"], self.st["phone"] or "", self.st["monthly_fee"],
                               self.st["assigned_seat"], self.st["start_date"], new_due.isoformat())
        self.accept()

class ExpenseDialog(QDialog):
    def __init__(self, db: DB, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Log Expense")
        form = QFormLayout(self)
        self.amount = QLineEdit()
        self.desc = QLineEdit()
        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.currentDate())
        self.category = QComboBox()
        self.category.addItems(["Utilities", "Rent", "Supplies", "Maintenance", "Other"])
        form.addRow("Amount (₹)", self.amount)
        form.addRow("Description", self.desc)
        form.addRow("Date", self.date)
        form.addRow("Category", self.category)
        btns = QHBoxLayout()
        add = QPushButton("Record Expense")
        add.clicked.connect(self.on_add)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        btns.addWidget(add)
        btns.addWidget(cancel)
        form.addRow(btns)

    def on_add(self):
        try:
            amt = int(self.amount.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Invalid", "Amount must be a number.")
            return
        if amt <= 0:
            QMessageBox.warning(self, "Invalid", "Amount must be > 0.")
            return
        dt_iso = date(self.date.date().year(), self.date.date().month(), self.date.date().day()).isoformat()
        self.db.add_transaction(dt_iso, "Expense", self.category.currentText(), amt, self.desc.text().strip(), None)
        self.accept()

# ---------------------- Main Window ----------------------

class SeatManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DB()
        self.setWindowTitle("Seat Manager 🪑")
        self.setMinimumSize(1180, 720)
        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        # Menu
        menubar = self.menuBar()
        filem = menubar.addMenu("&File")
        act_export = QAction("Export CSV (Students)", self)
        act_export.triggered.connect(self.export_students)
        act_import = QAction("Import CSV (Students)", self)
        act_import.triggered.connect(self.import_students)
        filem.addAction(act_export)
        filem.addAction(act_import)

        trans = menubar.addMenu("&Transactions")
        act_exp = QAction("Log Expense…", self)
        act_exp.triggered.connect(self.log_expense)
        trans.addAction(act_exp)

        # Top: Dashboard
        dash = QHBoxLayout()
        self.card_occupied = self._stat_card("Occupied", "0 / 30")
        self.card_vacant   = self._stat_card("Vacant", "0")
        self.card_due      = self._stat_card("Due This Week", "0")
        self.card_overdue  = self._stat_card("Overdue", "0")
        self.card_income   = self._stat_card("MTD Income", "₹0")
        self.card_expense  = self._stat_card("MTD Expense", "₹0")
        self.card_net      = self._stat_card("MTD Net", "₹0")
        for c in [self.card_occupied, self.card_vacant, self.card_due, self.card_overdue,
                  self.card_income, self.card_expense, self.card_net]:
            dash.addWidget(c)

        dash_wrap = QFrame()
        dash_wrap.setStyleSheet(f"QFrame{{background:{CARD_BG};border-radius:12px;padding:10px;}}")
        dash_wrap.setLayout(dash)

        # Middle: Seat map + Students table
        mid = QSplitter()
        mid.setOrientation(Qt.Orientation.Horizontal)

        # Seat map
        seat_box = QGroupBox("Seat Map")
        seat_layout = QGridLayout()
        seat_layout.setSpacing(8)
        self.seat_buttons: List[QPushButton] = []
        for i in range(SEAT_COUNT):
            btn = QPushButton(f"{i+1}")
            btn.setMinimumHeight(48)
            btn.setCheckable(False)
            btn.clicked.connect(lambda _, s=i+1: self.on_seat_clicked(s))
            btn.setStyleSheet("QPushButton{border-radius:8px;font-weight:600;}")
            self.seat_buttons.append(btn)
            seat_layout.addWidget(btn, i // SEAT_COLS, i % SEAT_COLS)
        seat_box.setLayout(seat_layout)

        # Students table
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Name", "Phone", "Seat", "Monthly Fee", "Start Date", "Next Due", "Status"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_edit_student)

        # Buttons under table
        tb_buttons = QHBoxLayout()
        add_btn = QPushButton("Add Student")
        add_btn.clicked.connect(self.on_add_student)
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.on_edit_student)
        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self.on_delete_student)
        pay_btn = QPushButton("Log Payment")
        pay_btn.clicked.connect(self.on_log_payment)
        tb_buttons.addWidget(add_btn)
        tb_buttons.addWidget(edit_btn)
        tb_buttons.addWidget(del_btn)
        tb_buttons.addStretch(1)
        tb_buttons.addWidget(pay_btn)

        right = QVBoxLayout()
        right.addWidget(self.table)
        tb_wrap = QFrame()
        tb_wrap.setLayout(tb_buttons)
        right.addWidget(tb_wrap)

        right_box = QWidget()
        right_box.setLayout(right)

        mid.addWidget(seat_box)
        mid.addWidget(right_box)
        mid.setSizes([420, 760])

        # Root layout
        root = QVBoxLayout()
        root.addWidget(dash_wrap)
        root.addWidget(mid)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

        # Dark-ish theme
        self.setStyleSheet(f"""
        QMainWindow{{background:#0a0f1a;color:{FG};}}
        QLabel, QTableWidget, QGroupBox {{color:{FG};}}
        QGroupBox{{border:1px solid {CARD_ACCENT}; border-radius:10px; margin-top:12px; padding:10px;}}
        QTableWidget::item{{padding:6px;}}
        QPushButton{{background:{CARD_ACCENT}; color:{FG}; padding:8px 12px; border:1px solid #2b3758; border-radius:8px;}}
        QPushButton:hover{{background:#2b3758;}}
        QHeaderView::section{{background:#121a2b; color:{FG}; padding:6px; border:0;}}
        """)

    def _stat_card(self, title: str, value: str) -> QFrame:
        box = QFrame()
        box.setStyleSheet(f"QFrame{{background:{CARD_ACCENT}; border-radius:12px;}}")
        v = QVBoxLayout()
        t = QLabel(title)
        t.setStyleSheet("QLabel{font-size:12px; color:#93a2bf;}")
        val = QLabel(value)
        val.setStyleSheet("QLabel{font-size:20px; font-weight:700;}")
        v.addWidget(t)
        v.addWidget(val)
        v.setContentsMargins(12,10,12,10)
        box.setLayout(v)
        box.value_label = val
        return box

    # ----------------- Actions -----------------

    def refresh_all(self):
        self.refresh_seat_map()
        self.refresh_students_table()
        self.refresh_dashboard()

    def refresh_seat_map(self):
        for i, btn in enumerate(self.seat_buttons, start=1):
            st = self.db.seat_occupant(i)
            if not st:
                self._color_btn(btn, "Vacant")
                btn.setToolTip(f"Seat {i}: Vacant")
            else:
                # Status: Blue if paid, Red if overdue
                paid = "next_due_date" in st.keys() and st["next_due_date"] and date.fromisoformat(st["next_due_date"]) >= date.today()
                color = "Paid" if paid else "Overdue"
                self._color_btn(btn, color)
                nd = st["next_due_date"] or "—"
                btn.setToolTip(f"Seat {i}: {st['name']} • Due: {nd}")

    def _color_btn(self, btn: QPushButton, status: str):
        if status == "Vacant":
            bg = GREEN.name()
        elif status == "Paid":
            bg = BLUE.name()
        else:
            bg = RED.name()
        btn.setStyleSheet(f"QPushButton{{background:{bg}; color:white; border:0; border-radius:10px; font-weight:700;}}")

    def refresh_students_table(self):
        rows = self.db.list_students()
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            vals = [
                row["name"],
                row["phone"] or "",
                str(row["assigned_seat"] or "—"),
                fmt_money(row["monthly_fee"]),
                row["start_date"] or "—",
                row["next_due_date"] or "—",
                row["payment_status"]
            ]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(str(v))
                if c == 6:
                    if v == "Overdue":
                        item.setForeground(RED)
                    elif v == "Paid":
                        item.setForeground(BLUE)
                    else:
                        item.setForeground(GREY)
                self.table.setItem(r, c, item)

    def refresh_dashboard(self):
        seats = self.db.list_seats()
        occupied = sum(1 for s in seats if self.db.seat_occupant(s["seat_number"]))
        vacant = SEAT_COUNT - occupied
        due_week = len(self.db.students_payment_due_within_days(7))
        overdue = len(self.db.students_overdue())

        today = date.today()
        inc, exp, net = self.db.month_summary(today.year, today.month)

        self.card_occupied.value_label.setText(f"{occupied} / {SEAT_COUNT}")
        self.card_vacant.value_label.setText(str(vacant))
        self.card_due.value_label.setText(str(due_week))
        self.card_overdue.value_label.setText(str(overdue))
        self.card_income.value_label.setText(fmt_money(inc))
        self.card_expense.value_label.setText(fmt_money(exp))
        self.card_net.value_label.setText(fmt_money(net))

    def on_seat_clicked(self, seat_number: int):
        st = self.db.seat_occupant(seat_number)
        if st:
            # open payment or edit prompt
            m = QMessageBox(self)
            m.setWindowTitle(f"Seat {seat_number}")
            m.setText(f"{st['name']} (Seat {seat_number})")
            m.addButton("Log Payment", QMessageBox.ButtonRole.AcceptRole)
            m.addButton("Edit Student", QMessageBox.ButtonRole.ActionRole)
            m.addButton("Unassign Seat", QMessageBox.ButtonRole.DestructiveRole)
            m.addButton("Close", QMessageBox.ButtonRole.RejectRole)
            ret = m.exec()
            if ret == 0:  # Log Payment
                dlg = PaymentDialog(self.db, st, self)
                if dlg.exec():
                    self.refresh_all()
            elif ret == 1:  # Edit
                dlg = StudentDialog(self.db, st, self)
                if dlg.exec():
                    self.refresh_all()
            elif ret == 2:  # Unassign
                self.db.update_student(st["id"], st["name"], st["phone"] or "", st["monthly_fee"],
                                       None, st["start_date"], st["next_due_date"])
                self.refresh_all()
        else:
            # assign student
            # open new-student dialog with seat preselected (and disabled others)
            dlg = StudentDialog(self.db, None, self)
            # preselect this seat
            for i in range(dlg.seat.count()):
                if dlg.seat.itemData(i) == seat_number and dlg.seat.model().item(i).isEnabled():
                    dlg.seat.setCurrentIndex(i)
                    break
            if dlg.exec():
                self.refresh_all()

    def current_selected_student(self) -> Optional[sqlite3.Row]:
        r = self.table.currentRow()
        if r < 0:
            return None
        name = self.table.item(r, 0).text()
        seat_val = self.table.item(r, 2).text()
        st = self.db.conn.execute("SELECT * FROM students WHERE name=?;", (name,)).fetchone()
        return st

    def on_add_student(self):
        dlg = StudentDialog(self.db, None, self)
        if dlg.exec():
            self.refresh_all()

    def on_edit_student(self):
        st = self.current_selected_student()
        if not st:
            return
        dlg = StudentDialog(self.db, st, self)
        if dlg.exec():
            self.refresh_all()

    def on_delete_student(self):
        st = self.current_selected_student()
        if not st:
            return
        if QMessageBox.question(self, "Delete", f"Delete {st['name']}?") == QMessageBox.StandardButton.Yes:
            self.db.delete_student(st["id"])
            self.refresh_all()

    def on_log_payment(self):
        st = self.current_selected_student()
        if not st:
            return
        dlg = PaymentDialog(self.db, st, self)
        if dlg.exec():
            self.refresh_all()

    def log_expense(self):
        dlg = ExpenseDialog(self.db, self)
        if dlg.exec():
            self.refresh_all()

    def export_students(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Students", "students_export.csv", "CSV Files (*.csv)")
        if not path:
            return
        rows = self.db.list_students()
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["name","phone","monthly_fee","assigned_seat","start_date","next_due_date"])
            for r in rows:
                w.writerow([r["name"], r["phone"] or "", r["monthly_fee"], r["assigned_seat"] or "",
                            r["start_date"] or "", r["next_due_date"] or ""])
        QMessageBox.information(self, "Exported", f"Saved to {path}")

    def import_students(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Students", "", "CSV Files (*.csv)")
        if not path:
            return
        count = 0
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                name = row.get("name","").strip()
                if not name:
                    continue
                phone = row.get("phone","").strip()
                fee = int(row.get("monthly_fee","1500") or "1500")
                seat = row.get("assigned_seat","").strip()
                seat_num = int(seat) if seat else None
                start = row.get("start_date","").strip() or None
                due = row.get("next_due_date","").strip() or None
                try:
                    self.db.add_student(name, phone, fee, seat_num, start, due)
                    count += 1
                except sqlite3.IntegrityError:
                    pass
        QMessageBox.information(self, "Imported", f"Imported {count} students.")
        self.refresh_all()


def main():
    app = QApplication(sys.argv)
    w = SeatManager()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
