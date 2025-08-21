import sys, csv, json
from datetime import date, datetime
from typing import Dict, Optional
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QBrush, QColor, QAction
import pyqtgraph as pg

# ----------------------------
# Storage
# ----------------------------
class Storage:
    def __init__(self):
        self.data = {}  # { "YYYY-MM": [rows] }
        self.categories = {"income": ["Salary"], "expense": ["Food", "Rent", "Misc"]}
        self.budgets = {}  # { "YYYY-MM": amount }

    def load_month(self, ym):
        return self.data.get(ym, [])

    def save_month(self, ym, rows):
        self.data[ym] = rows

    def next_id(self, ym):
        rows = self.load_month(ym)
        if not rows:
            return 1
        return max(r.get("id",0) for r in rows)+1

    def export_transactions_csv(self, path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["month","id","type","category","amount","date","notes"])
            for month, rows in self.data.items():
                for r in rows:
                    w.writerow([month, r.get("id",""), r.get("type",""), r.get("category",""),
                                r.get("amount",""), r.get("date",""), r.get("notes","")])

    def import_transactions_csv(self, path):
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                ym = row["month"]
                obj = {"id": int(row["id"]), "type": row["type"], "category": row["category"],
                       "amount": float(row["amount"]), "date": row["date"], "notes": row["notes"]}
                self.data.setdefault(ym, []).append(obj)

    def export_data_json(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"budgets": self.budgets, "categories": self.categories, "data": self.data}, f, indent=2)

    def import_data_json(self, path):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
            self.budgets = d.get("budgets", {})
            self.categories = d.get("categories", {})
            self.data = d.get("data", {})


# ----------------------------
# Pie Chart Widget
# ----------------------------
class PieChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setAspectLocked(True)
        self.plot_widget.setBackground(QColor(240,240,240))
        self.layout.addWidget(self.plot_widget)

    def plot_pie(self, data: dict, title: str = ""):
        self.plot_widget.clear()
        if not data:
            return
        total = sum(data.values())
        if total == 0:  # <--- skip if no data
            self.plot_widget.setTitle(title + " (No data)")
            return
        start_angle = 90
        for cat, val in data.items():
            span = 360 * val / total
            item = pg.QtWidgets.QGraphicsEllipseItem(-100, -100, 200, 200)
            item.setStartAngle(int(start_angle * 16))
            item.setSpanAngle(int(-span * 16))
            color = QColor.fromHsv(hash(cat)%360, 255, 200)
            brush = QBrush(color)
            item.setBrush(brush)
            self.plot_widget.addItem(item)
            start_angle -= span
        self.plot_widget.setTitle(title)

# ----------------------------
# Dashboard
# ----------------------------
class Dashboard(QWidget):
    def __init__(self, storage: Storage, month_selector: QComboBox):
        super().__init__()
        self.storage = storage
        self.month_selector = month_selector
        layout = QVBoxLayout(self)

        self.summary_lbl = QLabel()
        self.pie_chart = PieChartWidget()
        self.budget_edit = QDoubleSpinBox()
        self.budget_edit.setPrefix("Budget: ₹")
        self.budget_edit.setDecimals(2)
        self.budget_edit.setMaximum(1e9)
        layout.addWidget(self.summary_lbl)
        layout.addWidget(self.pie_chart)
        layout.addWidget(self.budget_edit)

        self.budget_edit.valueChanged.connect(self.on_budget_change)
        self.setLayout(layout)

    def refresh(self):
        ym = self.month_selector.currentText()
        rows = self.storage.load_month(ym)
        inc = sum(r["amount"] for r in rows if r["type"] == "income")
        exp = sum(r["amount"] for r in rows if r["type"] == "expense")
        bal = inc - exp
        budget = self.storage.budgets.get(ym, 0)
        over = budget and exp > budget
        note = f"Budget: ₹{budget:,.2f} | {'Over Budget!' if over else 'Within Budget'}" if budget else "No budget set"
        self.summary_lbl.setText(
            f"<b>Month:</b> {ym}<br>"
            f"<b>Income:</b> ₹{inc:,.2f}<br>"
            f"<b>Expense:</b> ₹{exp:,.2f}<br>"
            f"<b>Balance:</b> ₹{bal:,.2f}<br>"
            f"{note}"
        )

        # Plot income vs expense pie chart
        self.pie_chart.plot_pie({"Income": inc, "Expense": exp}, "Income vs Expense")

        self.budget_edit.blockSignals(True)
        self.budget_edit.setValue(budget)
        self.budget_edit.blockSignals(False)

    def on_budget_change(self, value):
        ym = self.month_selector.currentText()
        self.storage.budgets[ym] = value
        self.refresh()


# ----------------------------
# Tracker
# ----------------------------
class Tracker(QWidget):
    def __init__(self, storage: Storage, month_selector: QComboBox):
        super().__init__()
        self.storage = storage
        self.month_selector = month_selector
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID","Type","Category","Amount","Date","Notes"])
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

        form_box = QGroupBox("New/Edit Transaction")
        form_layout = QHBoxLayout(form_box)
        self.type_cb = QComboBox(); self.type_cb.addItems(["income","expense"])
        self.category_cb = QComboBox()
        self.amount_sp = QDoubleSpinBox(); self.amount_sp.setPrefix("₹ "); self.amount_sp.setDecimals(2); self.amount_sp.setMaximum(1e9)
        self.date_edit = QDateEdit(); self.date_edit.setCalendarPopup(True)
        self.notes_le = QLineEdit(); self.notes_le.setMaximumWidth(200)
        self.btn_add = QPushButton("Add"); self.btn_update = QPushButton("Update"); self.btn_delete = QPushButton("Delete")
        for w in [self.type_cb,self.category_cb,self.amount_sp,self.date_edit,self.notes_le,self.btn_add,self.btn_update,self.btn_delete]: form_layout.addWidget(w)
        layout.addWidget(form_box)

        self.pie_chart = PieChartWidget()
        layout.addWidget(self.pie_chart)

        self.setLayout(layout)

        # Connections
        self.btn_add.clicked.connect(self.on_add)
        self.btn_update.clicked.connect(self.on_update)
        self.btn_delete.clicked.connect(self.on_delete)
        self.table.itemSelectionChanged.connect(self.on_table_select)
        self.type_cb.currentTextChanged.connect(lambda _: self._reload_categories(self.type_cb.currentText()))
        self.month_selector.currentTextChanged.connect(lambda _: self.update_view())

        self._reload_categories("expense")

    def _reload_categories(self, ttype):
        self.category_cb.blockSignals(True)
        self.category_cb.clear()
        self.category_cb.addItems(sorted(self.storage.categories.get(ttype,[])))
        self.category_cb.blockSignals(False)

    def _selected_id(self) -> Optional[int]:
        row = self.table.currentRow()
        if row<0: return None
        try: return int(self.table.item(row,0).text())
        except: return None

    def _get_form(self):
        ttype = self.type_cb.currentText()
        category = self.category_cb.currentText()
        amount = float(self.amount_sp.value())
        qd = self.date_edit.date()
        tdate = date(qd.year(),qd.month(),qd.day()).isoformat()
        notes = self.notes_le.text().strip()
        return ttype, category, amount, tdate, notes

    def update_view(self):
        ym = self.month_selector.currentText()
        rows = self.storage.load_month(ym)
        self.table.setRowCount(len(rows))
        by_cat = {}
        for i,r in enumerate(rows):
            self.table.setItem(i,0,QTableWidgetItem(str(r["id"])))
            self.table.setItem(i,1,QTableWidgetItem(r["type"]))
            self.table.setItem(i,2,QTableWidgetItem(r["category"]))
            self.table.setItem(i,3,QTableWidgetItem(f"₹ {r['amount']:,.2f}"))
            self.table.setItem(i,4,QTableWidgetItem(r["date"]))
            self.table.setItem(i,5,QTableWidgetItem(r.get("notes","")))
            if r["type"]=="expense": by_cat[r["category"]] = by_cat.get(r["category"],0)+r["amount"]
        self.table.hideColumn(0)
        self.pie_chart.plot_pie(by_cat,"Expenses by Category")
        self._reset_form()
        self.btn_add.setEnabled(True); self.btn_update.setEnabled(False); self.btn_delete.setEnabled(False)

    def _reset_form(self):
        self.amount_sp.setValue(0)
        self.date_edit.setDate(QDate.currentDate())
        self.notes_le.setText("")

    def on_add(self):
        ttype,category,amount,tdate,notes=self._get_form()
        if amount<=0: return
        ym=self.month_selector.currentText()
        nid=self.storage.next_id(ym)
        rows=self.storage.load_month(ym)
        rows.append({"id":nid,"type":ttype,"category":category,"amount":amount,"date":tdate,"notes":notes})
        self.storage.save_month(ym,rows)
        self.update_view()

    def on_update(self):
        sel=self._selected_id(); 
        if sel is None: return
        ttype,category,amount,tdate,notes=self._get_form()
        ym=self.month_selector.currentText()
        rows=self.storage.load_month(ym)
        for r in rows:
            if r["id"]==sel: r.update({"type":ttype,"category":category,"amount":amount,"date":tdate,"notes":notes}); break
        self.storage.save_month(ym,rows)
        self.update_view()

    def on_delete(self):
        sel=self._selected_id()
        if sel is None: return
        ym=self.month_selector.currentText()
        rows=[r for r in self.storage.load_month(ym) if r["id"]!=sel]
        self.storage.save_month(ym,rows)
        self.update_view()

    def on_table_select(self):
        sel=self._selected_id(); has=sel is not None
        self.btn_add.setEnabled(not has)
        self.btn_update.setEnabled(has)
        self.btn_delete.setEnabled(has)
        if not has: return
        row=self.table.currentRow()
        self.type_cb.setCurrentText(self.table.item(row,1).text())
        self._reload_categories(self.type_cb.currentText())
        self.category_cb.setCurrentText(self.table.item(row,2).text())
        self.amount_sp.setValue(float(self.table.item(row,3).text().replace("₹","").replace(",","")))
        y,m,d=map(int,self.table.item(row,4).text().split("-"))
        self.date_edit.setDate(QDate(y,m,d))
        self.notes_le.setText(self.table.item(row,5).text() or "")


# ----------------------------
# Main Window
# ----------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Budget Tracker")
        self.resize(1200,800)
        self.storage=Storage()
        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        container = QWidget()
        v=QVBoxLayout(container)

        menubar=QMenuBar(self)
        file_menu=menubar.addMenu("File")
        export_csv=QAction("Export CSV",self)
        import_csv=QAction("Import CSV",self)
        export_json=QAction("Export JSON",self)
        import_json=QAction("Import JSON",self)
        file_menu.addAction(export_csv); file_menu.addAction(import_csv)
        file_menu.addAction(export_json); file_menu.addAction(import_json)
        v.setMenuBar(menubar)

        export_csv.triggered.connect(self.export_csv)
        import_csv.triggered.connect(self.import_csv)
        export_json.triggered.connect(self.export_json)
        import_json.triggered.connect(self.import_json)

        toolbar=QHBoxLayout()
        self.month_selector=QComboBox()
        toolbar.addWidget(QLabel("Month:")); toolbar.addWidget(self.month_selector)
        v.addLayout(toolbar)

        self.tabs=QTabWidget()
        self.dashboard=Dashboard(self.storage,self.month_selector)
        self.tracker=Tracker(self.storage,self.month_selector)
        self.tabs.addTab(self.dashboard,"Dashboard")
        self.tabs.addTab(self.tracker,"Tracker")
        v.addWidget(self.tabs)

        self.setCentralWidget(container)
        self._populate_months()
        self.month_selector.currentTextChanged.connect(lambda _: self.refresh_all())

    def _populate_months(self):
        today=date.today()
        months=[]
        for offset in range(-24,25):
            yy=today.year; mm=today.month+offset
            while mm<=0: mm+=12; yy-=1
            while mm>12: mm-=12; yy+=1
            months.append(f"{yy:04d}-{mm:02d}")
        uniq=[]
        for m in months:
            if m not in uniq: uniq.append(m)
        self.month_selector.addItems(uniq)
        self.month_selector.setCurrentText(f"{today.year:04d}-{today.month:02d}")

    def refresh_all(self):
        self.dashboard.refresh()
        self.tracker.update_view()

    # Import/Export
    def export_csv(self):
        path,_=QFileDialog.getSaveFileName(self,"Export CSV","","CSV Files (*.csv)")
        if path: self.storage.export_transactions_csv(path)

    def import_csv(self):
        path,_=QFileDialog.getOpenFileName(self,"Import CSV","","CSV Files (*.csv)")
        if path:
            self.storage.import_transactions_csv(path)
            self.refresh_all()

    def export_json(self):
        path,_=QFileDialog.getSaveFileName(self,"Export JSON","","JSON Files (*.json)")
        if path: self.storage.export_data_json(path)

    def import_json(self):
        path,_=QFileDialog.getOpenFileName(self,"Import JSON","","JSON Files (*.json)")
        if path:
            self.storage.import_data_json(path)
            self.refresh_all()


# ----------------------------
# Entrypoint
# ----------------------------
def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__=="__main__":
    main()