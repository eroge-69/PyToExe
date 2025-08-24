# -*- coding: utf-8 -*-
# Code from: Raibod 
# Name: Professional personnel management platform for Keshavarzi Bank (پلتفرم حرفه‌ای مدیریت پرسنل بانک کشاورزی)
# Run: python PPMPKB.py

import os, sys
from PySide6.QtCore import Qt, QSortFilterProxyModel, QRegularExpression, QDate, QSize
from PySide6.QtGui import QAction, QPixmap, QKeySequence
from PySide6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QTextEdit, QPushButton, QLabel, QDateEdit, QComboBox, QFileDialog, QMessageBox,
    QTableView, QSplitter, QFrame, QToolBar, QStatusBar, QMenu, QDialog, QGridLayout
)
import pandas as pd

APP_TITLE = "پلتفرم حرفه‌ای مدیریت پرسنل بانک کشاورزی"
DB_FILE   = "PPMPKB.db"
TABLE     = "employees"

# رنگ‌های سازمانی
GREEN   = "#0b7d3a"
GREEN_D = "#075e2b"
GOLD    = "#d9a400"

# ========== Database ==========
def ensure_db():
    first_time = not os.path.exists(DB_FILE)
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(DB_FILE)
    if not db.open():
        raise RuntimeError("خطا در باز کردن دیتابیس")
    if first_time:
        q = QSqlQuery()
        q.exec(f"""
        CREATE TABLE IF NOT EXISTS {TABLE}(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name  TEXT NOT NULL,
            national_id TEXT NOT NULL UNIQUE,
            personnel_code TEXT NOT NULL UNIQUE,
            mobile TEXT,
            phone TEXT,
            email TEXT,
            unit TEXT,
            role TEXT,
            hire_date TEXT,
            status TEXT,
            address TEXT,
            photo_path TEXT
        );
        """)
        # ایندکس برای جستجوی سریع‌تر
        q.exec(f"CREATE INDEX IF NOT EXISTS idx_emp_name ON {TABLE}(first_name,last_name);")
        q.exec(f"CREATE INDEX IF NOT EXISTS idx_emp_unit ON {TABLE}(unit);")
    return db

# ========== Filter Dialog (optional advanced filters) ==========
class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("فیلتر پیشرفته")
        self.resize(500, 200)
        lay = QGridLayout(self)
        self.name = QLineEdit(); self.name.setPlaceholderText("نام/نام خانوادگی")
        self.unit = QLineEdit(); self.unit.setPlaceholderText("واحد (مثلاً اعتبارات)")
        self.role = QLineEdit(); self.role.setPlaceholderText("سمت (مثلاً کارشناس)")
        self.status = QComboBox(); self.status.addItems(["-", "شاغل", "مرخصی", "بازنشسته", "سایر"])
        self.btn_ok = QPushButton("اعمال فیلتر ✅")
        self.btn_cl = QPushButton("پاک‌کردن ❌")
        lay.addWidget(QLabel("نام/خانوادگی:"), 0, 0); lay.addWidget(self.name, 0, 1, 1, 3)
        lay.addWidget(QLabel("واحد:"),        1, 0); lay.addWidget(self.unit, 1, 1)
        lay.addWidget(QLabel("سمت:"),        1, 2); lay.addWidget(self.role, 1, 3)
        lay.addWidget(QLabel("وضعیت:"),      2, 0); lay.addWidget(self.status, 2, 1)
        btns = QHBoxLayout(); btns.addWidget(self.btn_ok); btns.addWidget(self.btn_cl)
        lay.addLayout(btns, 3, 0, 1, 4)
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cl.clicked.connect(self.clear_fields)

    def clear_fields(self):
        self.name.clear(); self.unit.clear(); self.role.clear(); self.status.setCurrentIndex(0)

# ========== Main Window ==========
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1360, 820)
        self.db = ensure_db()

        # Model
        self.model = QSqlTableModel(self, self.db)
        self.model.setTable(TABLE)
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model.select()
        headers = [
            "شناسه","نام","نام خانوادگی","کد ملی","کد پرسنلی","موبایل","تلفن","ایمیل",
            "واحد","سمت","تاریخ استخدام","وضعیت","آدرس","مسیر عکس"
        ]
        for i, h in enumerate(headers):
            self.model.setHeaderData(i, Qt.Orientation.Horizontal, h)

        # Proxy for filter/search
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)  # همه ستون‌ها

        # UI
        self._build_ui()
        self._wire_signals()
        self.apply_styles(dark=True)
        self.statusBar().showMessage("✅ آماده به کار")

    # ----- UI Build -----
    def _build_ui(self):
        # Toolbar
        tb = QToolBar("ابزار")
        tb.setIconSize(QSize(22, 22))
        self.addToolBar(tb)

        # Actions
        self.act_new   = QAction("🆕 جدید", self); self.act_new.setToolTip("فرم جدید (Ctrl+N)")
        self.act_save  = QAction("💾 ذخیره", self); self.act_save.setToolTip("افزودن رکورد (Ctrl+S)")
        self.act_update= QAction("🛠️ بروزرسانی", self); self.act_update.setToolTip("بروزرسانی رکورد انتخابی (Ctrl+U)")
        self.act_delete= QAction("🗑️ حذف", self); self.act_delete.setToolTip("حذف رکورد انتخابی (Del)")
        self.act_import= QAction("📥 ورود Excel", self); self.act_import.setToolTip("Import از اکسل")
        self.act_export= QAction("📤 خروجی Excel", self); self.act_export.setToolTip("Export به اکسل (فیلتر فعلی)")
        self.act_theme = QAction("🌓 تم تیره/روشن", self)
        self.act_filter= QAction("🧰 فیلتر پیشرفته", self)
        self.act_refresh= QAction("🔁 تازه‌سازی", self)
        self.act_about = QAction("ℹ️ درباره", self)

        for a in [self.act_new,self.act_save,self.act_update,self.act_delete,self.act_import,self.act_export,self.act_filter,self.act_refresh,self.act_theme,self.act_about]:
            tb.addAction(a)

        # Shortcuts
        self.act_new.setShortcut(QKeySequence("Ctrl+N"))
        self.act_save.setShortcut(QKeySequence("Ctrl+S"))
        self.act_update.setShortcut(QKeySequence("Ctrl+U"))
        self.act_delete.setShortcut(QKeySequence(Qt.Key.Key_Delete))
        self.act_refresh.setShortcut(QKeySequence("F5"))

        # Search bar
        tb.addSeparator()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔎 جست‌وجو در همهٔ فیلدها (نام، کدملی، کدپرسنلی، واحد، سمت، تلفن، ایمیل...)")
        self.search_edit.setFixedWidth(480)
        tb.addWidget(self.search_edit)

        # Central
        central = QWidget(); self.setCentralWidget(central)
        v = QVBoxLayout(central)
        split = QSplitter(); split.setOrientation(Qt.Orientation.Horizontal); v.addWidget(split)

        # Left: Form
        form_frame = QFrame(); form_frame.setObjectName("formFrame")
        f = QFormLayout(form_frame)
        self.first_name = QLineEdit(); self.first_name.setPlaceholderText("نام 👤")
        self.last_name  = QLineEdit(); self.last_name.setPlaceholderText("نام خانوادگی 🧑‍💼")

        self.national_id = QLineEdit(); self.national_id.setPlaceholderText("کد ملی 🆔"); self.national_id.setMaxLength(10)
        regex_validator = QRegularExpressionValidator(QRegularExpression("^[0-9]{0,10}$"))
        self.national_id.setValidator(regex_validator)


        self.personnel_code = QLineEdit(); self.personnel_code.setPlaceholderText("کد پرسنلی 🧾"); self.personnel_code.setMaxLength(12)
        self.mobile = QLineEdit(); self.mobile.setPlaceholderText("موبایل 📱")
        self.phone  = QLineEdit(); self.phone.setPlaceholderText("تلفن ثابت ☎️")
        self.email  = QLineEdit(); self.email.setPlaceholderText("ایمیل ✉️")

        self.unit   = QComboBox(); self.unit.addItems(["-", "اعتبارات", "مالی", "فناوری اطلاعات", "اداری", "بازاریابی", "صندوق", "حراست", "سایر"])
        self.role   = QLineEdit(); self.role.setPlaceholderText("سمت 🏷️")
        self.hire_date = QDateEdit(); self.hire_date.setCalendarPopup(True); self.hire_date.setDisplayFormat("yyyy/MM/dd"); self.hire_date.setDate(QDate.currentDate())
        self.status = QComboBox(); self.status.addItems(["شاغل","مرخصی","بازنشسته","سایر"])

        self.address = QTextEdit(); self.address.setPlaceholderText("آدرس 🏠")
        self.photo_path = QLineEdit(); self.photo_path.setPlaceholderText("مسیر عکس پرسنلی 🖼️")
        self.btn_browse = QPushButton("📁 انتخاب عکس")
        self.preview = QLabel("پیش‌نمایش عکس"); self.preview.setAlignment(Qt.AlignCenter); self.preview.setFixedHeight(180); self.preview.setFrameShape(QFrame.Shape.StyledPanel)

        ph = QHBoxLayout(); ph.addWidget(self.photo_path, 2); ph.addWidget(self.btn_browse, 1)

        f.addRow("نام:", self.first_name)
        f.addRow("نام خانوادگی:", self.last_name)
        f.addRow("کد ملی:", self.national_id)
        f.addRow("کد پرسنلی:", self.personnel_code)
        f.addRow("موبایل:", self.mobile)
        f.addRow("تلفن:", self.phone)
        f.addRow("ایمیل:", self.email)
        f.addRow("واحد:", self.unit)
        f.addRow("سمت:", self.role)
        f.addRow("تاریخ استخدام:", self.hire_date)
        f.addRow("وضعیت:", self.status)
        f.addRow("آدرس:", self.address)
        f.addRow("عکس:", ph)
        f.addRow(self.preview)

        # Form buttons row
        fb = QHBoxLayout()
        self.btn_add = QPushButton("➕ افزودن")
        self.btn_update = QPushButton("✏️ بروزرسانی")
        self.btn_delete = QPushButton("🗑️ حذف")
        self.btn_clear = QPushButton("🧹 پاک‌سازی فرم")
        for b in [self.btn_add, self.btn_update, self.btn_delete, self.btn_clear]:
            fb.addWidget(b)
        x = QVBoxLayout(); x.addLayout(f); x.addLayout(fb)
        form_frame.setLayout(x)

        # Right: Table
        table_frame = QFrame()
        table_layout = QVBoxLayout(table_frame)
        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        table_layout.addWidget(self.table)

        # footer filter chips
        chip = QHBoxLayout()
        self.cmb_unit_filter = QComboBox(); self.cmb_unit_filter.addItems(["همه واحدها"] + [self.unit.itemText(i) for i in range(self.unit.count()) if self.unit.itemText(i) != "-"])
        self.cmb_status_filter = QComboBox(); self.cmb_status_filter.addItems(["همه وضعیت‌ها","شاغل","مرخصی","بازنشسته","سایر"])
        self.le_role_filter = QLineEdit(); self.le_role_filter.setPlaceholderText("فیلتر سمت…")
        chip.addWidget(QLabel("فیلتر سریع:"))
        chip.addWidget(self.cmb_unit_filter)
        chip.addWidget(self.cmb_status_filter)
        chip.addWidget(self.le_role_filter)
        table_layout.addLayout(chip)

        split.addWidget(form_frame)
        split.addWidget(table_frame)
        split.setStretchFactor(0,1)
        split.setStretchFactor(1,2)

        # Status bar
        self.setStatusBar(QStatusBar())
        # Menus
        mb = self.menuBar()
        m_file = mb.addMenu("📂 فایل")
        m_tools= mb.addMenu("🧰 ابزار")
        m_help = mb.addMenu("❓ راهنما")
        for a in [self.act_import, self.act_export, self.act_refresh]:
            m_file.addAction(a)
        m_file.addSeparator(); m_file.addAction(self.act_theme)
        m_file.addSeparator(); close_a = QAction("🚪 خروج", self); close_a.triggered.connect(self.close); m_file.addAction(close_a)
        for a in [self.act_filter]:
            m_tools.addAction(a)
        m_help.addAction(self.act_about)

        # Tooltips
        self.btn_add.setToolTip("افزودن پرسنل جدید")
        self.btn_update.setToolTip("ویرایش/بروزرسانی رکورد انتخاب‌شده")
        self.btn_delete.setToolTip("حذف رکورد انتخاب‌شده")
        self.btn_clear.setToolTip("پاک‌سازی فرم")
        self.btn_browse.setToolTip("انتخاب فایل عکس (PNG/JPG/WebP)")
        self.search_edit.setToolTip("جست‌وجوی زنده روی تمام ستون‌ها")

    # ----- Wiring -----
    def _wire_signals(self):
        self.search_edit.textChanged.connect(self.apply_search)
        self.cmb_unit_filter.currentTextChanged.connect(self.apply_quick_filters)
        self.cmb_status_filter.currentTextChanged.connect(self.apply_quick_filters)
        self.le_role_filter.textChanged.connect(self.apply_quick_filters)

        self.table.selectionModel().selectionChanged.connect(self.load_selected_to_form)
        self.btn_browse.clicked.connect(self.pick_photo)

        self.btn_add.clicked.connect(self.save_record)
        self.btn_update.clicked.connect(self.update_record)
        self.btn_delete.clicked.connect(self.delete_record)
        self.btn_clear.clicked.connect(self.clear_form)

        self.act_new.triggered.connect(self.clear_form)
        self.act_save.triggered.connect(self.save_record)
        self.act_update.triggered.connect(self.update_record)
        self.act_delete.triggered.connect(self.delete_record)
        self.act_import.triggered.connect(self.import_excel)
        self.act_export.triggered.connect(self.export_excel)
        self.act_refresh.triggered.connect(lambda: self.model.select())
        self.act_theme.triggered.connect(self.toggle_theme)
        self.act_filter.triggered.connect(self.open_filter_dialog)
        self.act_about.triggered.connect(self.show_about)

    # ----- Search & Filters -----
    def apply_search(self, text):
        self.proxy.setFilterRegularExpression(QRegularExpression(text))

    def apply_quick_filters(self):
        unit = self.cmb_unit_filter.currentText()
        status = self.cmb_status_filter.currentText()
        role = self.le_role_filter.text().strip()

        # میکس فیلتر‌ها: با regex روی کل جدول
        parts = []
        if unit and unit != "همه واحدها":
            parts.append(f"(?i){unit}")
        if status and status != "همه وضعیت‌ها":
            parts.append(f"(?i){status}")
        if role:
            parts.append(f"(?i){role}")
        rx = ".*".join(parts) if parts else ""
        self.proxy.setFilterRegularExpression(QRegularExpression(rx))

    def open_filter_dialog(self):
        dlg = FilterDialog(self)
        if dlg.exec():
            terms = []
            if dlg.name.text().strip():
                terms.append(f"(?i){dlg.name.text().strip()}")
            if dlg.unit.text().strip():
                terms.append(f"(?i){dlg.unit.text().strip()}")
            if dlg.role.text().strip():
                terms.append(f"(?i){dlg.role.text().strip()}")
            if dlg.status.currentText() != "-":
                terms.append(f"(?i){dlg.status.currentText()}")
            rx = ".*".join(terms) if terms else ""
            self.proxy.setFilterRegularExpression(QRegularExpression(rx))

    # ----- Helpers -----
    def current_row_id(self):
        idx = self.table.currentIndex()
        if not idx.isValid(): return None
        src = self.proxy.mapToSource(idx)
        return self.model.record(src.row()).value("id")

    def load_selected_to_form(self):
        rid = self.current_row_id()
        if rid is None: return
        q = QSqlQuery()
        q.prepare(f"SELECT * FROM {TABLE} WHERE id=?")
        q.addBindValue(rid); q.exec()
        if q.next():
            self.first_name.setText(q.value("first_name") or "")
            self.last_name.setText(q.value("last_name") or "")
            self.national_id.setText(q.value("national_id") or "")
            self.personnel_code.setText(q.value("personnel_code") or "")
            self.mobile.setText(q.value("mobile") or "")
            self.phone.setText(q.value("phone") or "")
            self.email.setText(q.value("email") or "")
            self.role.setText(q.value("role") or "")
            unit = q.value("unit") or "-"
            ix = self.unit.findText(unit); self.unit.setCurrentIndex(ix if ix >=0 else 0)
            hd = q.value("hire_date") or QDate.currentDate().toString("yyyy/MM/dd")
            try:
                y,m,d = [int(x) for x in hd.split("/")]
                self.hire_date.setDate(QDate(y,m,d))
            except: self.hire_date.setDate(QDate.currentDate())
            st = q.value("status") or "شاغل"
            ix = self.status.findText(st); self.status.setCurrentIndex(ix if ix >=0 else 0)
            self.address.setPlainText(q.value("address") or "")
            self.photo_path.setText(q.value("photo_path") or "")
            self.update_photo_preview(self.photo_path.text())

    def pick_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "انتخاب عکس", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if path:
            self.photo_path.setText(path)
            self.update_photo_preview(path)

    def update_photo_preview(self, path):
        if path and os.path.exists(path):
            pix = QPixmap(path)
            if not pix.isNull():
                self.preview.setPixmap(pix.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return
        self.preview.setText("پیش‌نمایش عکس")

    def clear_form(self):
        for w in [self.first_name,self.last_name,self.national_id,self.personnel_code,self.mobile,self.phone,self.email,self.role,self.photo_path]:
            w.clear()
        self.unit.setCurrentIndex(0)
        self.status.setCurrentIndex(0)
        self.address.clear()
        self.hire_date.setDate(QDate.currentDate())
        self.preview.setText("پیش‌نمایش عکس")
        self.table.clearSelection()
        self.statusBar().showMessage("🧹 فرم پاک شد")

    # ----- Validation -----
    def validate(self, for_update=False):
        fn = self.first_name.text().strip()
        ln = self.last_name.text().strip()
        nid= self.national_id.text().strip()
        pid= self.personnel_code.text().strip()
        if not fn: return "نام را وارد کنید."
        if not ln: return "نام خانوادگی را وارد کنید."
        if not nid or len(nid)!=10: return "کد ملی 10 رقمی معتبر وارد کنید."
        if not pid: return "کد پرسنلی را وارد کنید."
        # uniqueness
        q = QSqlQuery()
        def exists(field, value, ignore_id=None):
            q.prepare(f"SELECT id FROM {TABLE} WHERE {field}=?")
            q.addBindValue(value); q.exec()
            while q.next():
                if ignore_id and q.value(0)==ignore_id: continue
                return True
            return False
        rid = self.current_row_id() if for_update else None
        if exists("national_id", nid, rid): return "این کد ملی قبلاً ثبت شده است."
        if exists("personnel_code", pid, rid): return "این کد پرسنلی قبلاً ثبت شده است."
        return None

    # ----- CRUD -----
    def save_record(self):
        err = self.validate(False)
        if err: QMessageBox.warning(self, "خطا", err); return
        q = QSqlQuery()
        q.prepare(f"""
        INSERT INTO {TABLE}
        (first_name,last_name,national_id,personnel_code,mobile,phone,email,unit,role,hire_date,status,address,photo_path)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """)
        vals = [
            self.first_name.text().strip(),
            self.last_name.text().strip(),
            self.national_id.text().strip(),
            self.personnel_code.text().strip(),
            self.mobile.text().strip(),
            self.phone.text().strip(),
            self.email.text().strip(),
            self.unit.currentText(),
            self.role.text().strip(),
            self.hire_date.text(),
            self.status.currentText(),
            self.address.toPlainText().strip(),
            self.photo_path.text().strip()
        ]
        for v in vals: q.addBindValue(v)
        if not q.exec():
            QMessageBox.critical(self, "خطا", "ثبت اطلاعات ناموفق بود."); return
        self.model.select()
        self.statusBar().showMessage("✅ رکورد ذخیره شد")
        self.clear_form()

    def update_record(self):
        rid = self.current_row_id()
        if rid is None:
            QMessageBox.warning(self, "خطا", "ردیفی انتخاب نشده است."); return
        err = self.validate(True)
        if err: QMessageBox.warning(self, "خطا", err); return
        q = QSqlQuery()
        q.prepare(f"""
        UPDATE {TABLE} SET
        first_name=?, last_name=?, national_id=?, personnel_code=?, mobile=?, phone=?, email=?,
        unit=?, role=?, hire_date=?, status=?, address=?, photo_path=?
        WHERE id=?
        """)
        vals = [
            self.first_name.text().strip(),
            self.last_name.text().strip(),
            self.national_id.text().strip(),
            self.personnel_code.text().strip(),
            self.mobile.text().strip(),
            self.phone.text().strip(),
            self.email.text().strip(),
            self.unit.currentText(),
            self.role.text().strip(),
            self.hire_date.text(),
            self.status.currentText(),
            self.address.toPlainText().strip(),
            self.photo_path.text().strip(),
            rid
        ]
        for v in vals: q.addBindValue(v)
        if not q.exec():
            QMessageBox.critical(self, "خطا", "بروزرسانی ناموفق بود."); return
        self.model.select()
        self.statusBar().showMessage("✏️ بروزرسانی شد")

    def delete_record(self):
        rid = self.current_row_id()
        if rid is None:
            QMessageBox.warning(self, "خطا", "ردیفی انتخاب نشده است."); return
        if QMessageBox.question(self, "حذف", "از حذف این رکورد مطمئن هستید؟") != QMessageBox.Yes:
            return
        q = QSqlQuery()
        q.prepare(f"DELETE FROM {TABLE} WHERE id=?")
        q.addBindValue(rid)
        if not q.exec():
            QMessageBox.critical(self, "خطا", "حذف ناموفق بود."); return
        self.model.select()
        self.clear_form()
        self.statusBar().showMessage("🗑️ حذف شد")

    # ----- Excel I/O -----
    def import_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, "ورود از Excel", "", "Excel Files (*.xlsx *.xls)")
        if not path: return
        try:
            df = pd.read_excel(path)
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خواندن اکسل ناموفق بود:\n{e}")
            return

        # mapping منعطف (ستون‌های فارسی/انگلیسی)
        mapping = {
            'first_name': ['نام','first','first_name','fname'],
            'last_name' : ['نام خانوادگی','family','last','last_name','lname'],
            'national_id':['کد ملی','national_id','nid'],
            'personnel_code':['کد پرسنلی','personnel_code','pid','code'],
            'mobile':['موبایل','شماره همراه','mobile','cell'],
            'phone':['تلفن ثابت','phone','tel'],
            'email':['ایمیل','email'],
            'unit':['واحد','unit','dept','department'],
            'role':['سمت','role','position','title'],
            'hire_date':['تاریخ استخدام','hire','hire_date','start_date'],
            'status':['وضعیت','status'],
            'address':['آدرس','address','addr'],
            'photo_path':['مسیر عکس','photo','photo_path']
        }
        # normalize
        norm = {}
        for std, aliases in mapping.items():
            found = None
            for c in df.columns:
                if str(c).strip().lower() in [a.lower() for a in aliases]:
                    found = c; break
            norm[std] = found

        # build safe rows
        added, skipped = 0, 0
        for _, r in df.iterrows():
            fn = str(r[norm['first_name']]) if norm['first_name'] else ""
            ln = str(r[norm['last_name']]) if norm['last_name'] else ""
            nid= str(r[norm['national_id']]) if norm['national_id'] else ""
            pid= str(r[norm['personnel_code']]) if norm['personnel_code'] else ""
            if not (fn and ln and nid and pid):
                skipped += 1; continue
            vals = [
                fn, ln, nid, pid,
                str(r[norm['mobile']]) if norm['mobile'] else "",
                str(r[norm['phone']]) if norm['phone'] else "",
                str(r[norm['email']]) if norm['email'] else "",
                str(r[norm['unit']]) if norm['unit'] else "",
                str(r[norm['role']]) if norm['role'] else "",
                str(r[norm['hire_date']]) if norm['hire_date'] else "",
                str(r[norm['status']]) if norm['status'] else "شاغل",
                str(r[norm['address']]) if norm['address'] else "",
                str(r[norm['photo_path']]) if norm['photo_path'] else ""
            ]
            q = QSqlQuery()
            q.prepare(f"""INSERT OR IGNORE INTO {TABLE}
            (first_name,last_name,national_id,personnel_code,mobile,phone,email,unit,role,hire_date,status,address,photo_path)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""")
            for v in vals: q.addBindValue(v)
            if q.exec(): added += 1
            else: skipped += 1

        self.model.select()
        QMessageBox.information(self, "ورود از اکسل", f"✅ ثبت جدید: {added}\n❗ رد/تکراری: {skipped}")

    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "خروجی Excel", "employees.xlsx", "Excel Files (*.xlsx)")
        if not path: return
        rows = self.proxy.rowCount()
        cols = self.proxy.columnCount()
        data = []
        headers = [self.model.headerData(i, Qt.Orientation.Horizontal) for i in range(cols)]
        for r in range(rows):
            row = []
            for c in range(cols):
                idx = self.proxy.index(r, c)
                row.append(self.proxy.data(idx))
            data.append(row)
        try:
            pd.DataFrame(data, columns=headers).to_excel(path, index=False)
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"ذخیره اکسل ناموفق بود:\n{e}"); return
        QMessageBox.information(self, "خروجی اکسل", "📤 فایل با موفقیت ذخیره شد.")

    # ----- About & Theme -----
    def show_about(self):
        QMessageBox.information(self, "درباره", "پلتفرم حرفه‌ای مدیریت پرسنل بانک کشاورزی\nPySide6 + SQLite + Excel\n© 2025")

    def toggle_theme(self):
        # ساده: سوییچ بین تیره/روشن با CSS سفارشی
        current_dark = self.palette().window().color().value() < 128
        self.apply_styles(dark=not current_dark)

    def apply_styles(self, dark=True):
        if dark:
            self.setStyleSheet(f"""
                QMainWindow {{ background: #1d2020; color: #e6ece9; }}
                QToolBar {{ background: {GREEN_D}; padding:6px; }}
                QToolBar QToolButton {{
                    background: {GREEN}; color: white; border-radius: 8px; padding:6px 10px; margin:3px;
                }}
                QToolBar QToolButton:hover {{ background: {GOLD}; color: black; }}
                #formFrame {{ background:#232726; border-radius:12px; padding:14px; }}
                QLineEdit, QTextEdit, QComboBox, QDateEdit {{
                    background:#2b2f2d; color:#e9ecea; border:1px solid #3a3f3d; border-radius:8px; padding:6px;
                }}
                QPushButton {{
                    background:{GREEN}; color:white; border-radius:10px; padding:8px 12px; font-weight:600;
                }}
                QPushButton:hover {{ background:{GOLD}; color:black; }}
                QTableView {{
                    background:#202322; alternate-background-color:#242827; gridline-color:#404645;
                    selection-background-color:{GOLD}; selection-color:black;
                }}
                QHeaderView::section {{
                    background:#2b2f2d; color:#e6ece9; padding:6px; border:0; border-bottom:1px solid #3a3f3d;
                }}
                QStatusBar {{ background:#1a1d1c; color:#dfe5e2; }}
                QMenuBar {{ background:#1a1d1c; color:#dfe5e2; }}
                QMenu {{ background:#222524; color:#e6ece9; }}
                QMenu::item:selected {{ background:{GOLD}; color:black; }}
            """)
        else:
            self.setStyleSheet(f"""
                QMainWindow {{ background: #f6f8f7; color:#222; }}
                QToolBar {{ background: #e9f2ec; padding:6px; border-bottom:1px solid #cfe6d8; }}
                QToolBar QToolButton {{
                    background: {GREEN}; color: white; border-radius: 8px; padding:6px 10px; margin:3px;
                }}
                QToolBar QToolButton:hover {{ background: {GOLD}; color:black; }}
                #formFrame {{ background:#ffffff; border-radius:12px; padding:14px; border:1px solid #e6ece9; }}
                QLineEdit, QTextEdit, QComboBox, QDateEdit {{
                    background:#ffffff; color:#222; border:1px solid #d6dbda; border-radius:8px; padding:6px;
                }}
                QPushButton {{
                    background:{GREEN}; color:white; border-radius:10px; padding:8px 12px; font-weight:600;
                }}
                QPushButton:hover {{ background:{GOLD}; color:black; }}
                QTableView {{
                    background:#ffffff; alternate-background-color:#f4f6f5; gridline-color:#d6dbda;
                    selection-background-color:{GOLD}; selection-color:black;
                }}
                QHeaderView::section {{
                    background:#f0f5f3; color:#222; padding:6px; border:0; border-bottom:1px solid #d6dbda;
                }}
                QStatusBar {{ background:#eef5f1; color:#333; }}
                QMenuBar {{ background:#eef5f1; color:#333; }}
                QMenu {{ background:#ffffff; color:#222; }}
                QMenu::item:selected {{ background:{GOLD}; color:black; }}
            """)

# ========== Run ==========
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)
    win = Main()
    win.show()
    sys.exit(app.exec())