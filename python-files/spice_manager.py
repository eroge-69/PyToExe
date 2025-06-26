import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QCheckBox, QScrollArea, QStyledItemDelegate, QTabWidget, QComboBox,
    QDialog, QFontComboBox, QColorDialog
)

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QFontDialog




DB_PATH = 'spices.db'

class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute('PRAGMA foreign_keys = ON')
        self.create_tables()

    def create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS raw_ingredients (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                price_per_kg REAL
            );
            CREATE TABLE IF NOT EXISTS composites (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            );
            CREATE TABLE IF NOT EXISTS composite_items (
                composite_id INTEGER,
                raw_id INTEGER,
                grams REAL,
                PRIMARY KEY (composite_id, raw_id),
                FOREIGN KEY(composite_id) REFERENCES composites(id) ON DELETE CASCADE,
                FOREIGN KEY(raw_id) REFERENCES raw_ingredients(id) ON DELETE CASCADE
            );
        """)
             # اگر ستون profit_percent وجود ندارد، اضافه‌ش کن
        try:
            self.conn.execute("ALTER TABLE composites ADD COLUMN profit_percent REAL DEFAULT 0;")
        except sqlite3.OperationalError:
            # اگر ستون از قبل هست، هیچ کاری انجام نده
            pass

        self.conn.commit()

    # ---------- RAW CRUD ----------
    def add_raw(self, name, price):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO raw_ingredients (name, price_per_kg) VALUES (?, ?) "
            "ON CONFLICT(name) DO UPDATE SET price_per_kg=excluded.price_per_kg",
            (name, price)
        )
        self.conn.commit()

    def update_raw_name(self, raw_id, new_name):
        self.conn.execute("UPDATE raw_ingredients SET name=? WHERE id=?", (new_name, raw_id))
        self.conn.commit()

    def delete_raw(self, raw_id):
        self.conn.execute("DELETE FROM raw_ingredients WHERE id=?", (raw_id,))
        self.conn.commit()

    def get_raw(self):
        return self.conn.execute(
            "SELECT id, name, price_per_kg FROM raw_ingredients ORDER BY name"
        ).fetchall()

    # ------- COMPOSITE CRUD -------
    def add_composite(self, id_, name, profit, items):
        cur = self.conn.cursor()
        # اگر رکورد جدید باشد، INSERT کن با ستون profit_percent
        cur.execute(
            "INSERT OR IGNORE INTO composites (id, name, profit_percent) VALUES (?, ?, ?)",
            (id_, name, profit)
        )
        # اگر رکورد وجود داشت یا بعد از INSERT اولیه، همیشه name و profit را UPDATE کن
        cur.execute(
            "UPDATE composites SET name=?, profit_percent=? WHERE id=?",
            (name, profit, id_)
        )
        self.conn.commit()

        # سپس آیتم‌های قدیمی را پاک کن و موارد جدید را وارد کن
        cur.execute("DELETE FROM composite_items WHERE composite_id=?", (id_,))
        for raw_id, grams in items.items():
            cur.execute(
                "INSERT INTO composite_items (composite_id, raw_id, grams) VALUES (?, ?, ?)",
                (id_, raw_id, grams)
            )
        self.conn.commit()


    def update_composite(self, old_id, new_id, new_name, profit, items):
        if old_id == new_id:
            # اینجا profit را هم پاس بده
            self.add_composite(new_id, new_name, profit, items)
        else:
            # اگر ID عوض شده، اول رکورد جدید را با profit درج کن و بعد رکورد قدیمی را حذف کن
            self.add_composite(new_id, new_name, profit, items)
            self.delete_composite(old_id)


    def delete_composite(self, comp_id):
        self.conn.execute("DELETE FROM composites WHERE id=?", (comp_id,))
        self.conn.commit()

    def get_composites(self, filter_raw_ids=None):
        if filter_raw_ids:
            ph = ','.join('?' for _ in filter_raw_ids)
            query = (
                f"SELECT DISTINCT c.id, c.name FROM composites c "
                f"JOIN composite_items ci ON c.id=ci.composite_id "
                f"WHERE ci.raw_id IN ({ph}) ORDER BY c.id"
            )
            comps = self.conn.execute(query, filter_raw_ids).fetchall()
        else:
            comps = self.conn.execute("SELECT id, name, profit_percent FROM composites ORDER BY id").fetchall()

        result = []
        for cid, name, profit in comps:
            items = self.conn.execute(
                "SELECT r.name, r.price_per_kg, ci.grams, r.id "
                "FROM composite_items ci JOIN raw_ingredients r ON ci.raw_id=r.id "
                "WHERE ci.composite_id=?", (cid,)
            ).fetchall()
            total_price = sum(price * grams / 1000 for _, price, grams, _ in items)
            total_grams = sum(grams for _, _, grams, _ in items)

            # ← اینجا اضافه کن
            sell_price = total_price * (1 + profit/100)

            result.append((cid, name, total_price, sell_price, total_grams, items, profit))

        return result

class PriceDelegate(QStyledItemDelegate):
    def __init__(self, window):
        super().__init__(window)
        self.window = window

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        # فرمت کردن خودکار اعداد با کاما
        editor.textChanged.connect(lambda t: self.format_text(editor, t))
        # وقتی اینتر زدن، مقدار رو اعمال کن و ادیتور رو ببند
        editor.returnPressed.connect(
            lambda: (
                self.commitData.emit(editor),
                self.closeEditor.emit(editor, QStyledItemDelegate.NoHint)
            )
        )
        # حتماً installEventFilter رو پس از ساخت editor فراخوانی کن
        editor.installEventFilter(self)
        return editor

    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent, Qt
        # فقط برای ادیتور قیمت
        if isinstance(obj, QLineEdit) and event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
            # اعمال تغییر
            self.commitData.emit(obj)
            self.closeEditor.emit(obj, QStyledItemDelegate.NoHint)
            # حرکت به سلول بعدی در ستون قیمت
            table = self.window.raw_table
            cur = table.currentIndex()
            next_row = cur.row() + 1
            if next_row < table.rowCount():
                next_idx = table.model().index(next_row, 1)  # ستون قیمت = ستون 1
                table.setCurrentIndex(next_idx)
                table.edit(next_idx)
            return True
        return super().eventFilter(obj, event)

    # بقیه متدها بدون تغییر
    def format_text(self, editor, text):
        clean = text.replace(',', '')
        if clean.isdigit():
            editor.blockSignals(True)
            editor.setText(f"{int(clean):,d}")
            editor.blockSignals(False)

    def setEditorData(self, editor, index):
        editor.setText(index.data())

    def setModelData(self, editor, model, index):
        txt = editor.text().replace(',', '')
        try:
            price = float(txt)
        except ValueError:
            return
        model.setData(index, f"{price:,.0f}")
        row = index.row()
        rid = model.index(row, 0).data(Qt.UserRole)
        name = model.index(row, 0).data()
        self.window.db.add_raw(name, price)
        self.window.refresh_tables()


class EditDialog(QDialog):
    def __init__(self, title, fields, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)
        self.edits = {}
        for label, value in fields.items():
            h = QHBoxLayout()
            h.addWidget(QLabel(label))
            le = QLineEdit(str(value))
            h.addWidget(le)
            layout.addLayout(h)
            self.edits[label] = le
        btns = QHBoxLayout()
        btns.addWidget(QPushButton("ذخیره", clicked=self.accept))
        btns.addWidget(QPushButton("لغو", clicked=self.reject))
        layout.addLayout(btns)

    def get_values(self):
        return {label: edit.text().strip() for label, edit in self.edits.items()}

class RequestDialog(QDialog):
    def __init__(self, raw_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("درخواست مواد")
        self.resize(300, 400)
        layout = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        container = QWidget(); scroll_layout = QVBoxLayout(container)
        self.checks = []
        for rid, name, _ in raw_list:
            cb = QCheckBox(name)
            cb.raw_id = rid
            scroll_layout.addWidget(cb)
            self.checks.append(cb)
        scroll_layout.addStretch()
        container.setLayout(scroll_layout)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        btns = QHBoxLayout()
        btns.addWidget(QPushButton("تأیید", clicked=self.accept))
        btns.addWidget(QPushButton("لغو", clicked=self.reject))
        layout.addLayout(btns)

    def get_selected(self):
        return [cb.raw_id for cb in self.checks if cb.isChecked()]

class CompositeDialog(QDialog):
    def __init__(self, db, comp_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.comp_id = comp_id
        self.setWindowTitle("تعریف ترکیب" if comp_id is None else "ویرایش ترکیب")
        self.resize(600, 400)

        layout = QVBoxLayout(self)
        # ID + Name
        h = QHBoxLayout()
        h.addWidget(QLabel("شناسه:"))
        self.id_edit = QLineEdit()
        h.addWidget(self.id_edit)
        h.addWidget(QLabel("نام ترکیب:"))
        self.name_edit = QLineEdit()
        h.addWidget(self.name_edit)
        h.addWidget(QLabel("درصد سود:"))
        self.profit_edit = QLineEdit("0")          # مقدار پیش‌فرض
        self.profit_edit.setMaximumWidth(60)
        h.addWidget(self.profit_edit)
        layout.addLayout(h)

        # Request raw
        btn_req = QPushButton("درخواست مواد")
        btn_req.clicked.connect(self.open_request_dialog)
        layout.addWidget(btn_req)

        # Table
        self.raw_table = QTableWidget(0, 2)
        self.raw_table.setHorizontalHeaderLabels(["نام", "گرم"])
        layout.addWidget(self.raw_table)

        # Save/Cancel
        btns = QHBoxLayout()
        btns.addWidget(QPushButton("تأیید", clicked=self.accept))
        btns.addWidget(QPushButton("لغو", clicked=self.reject))
        layout.addLayout(btns)

        self.raw_rows = []

        # preload existing composite
        if comp_id is not None:
            for cid2, name2, prod_price, sell_price, grams2, items2, profit2 in self.db.get_composites():
                if cid2 == comp_id:
                    # شناسه و نام
                    self.id_edit.setText(str(cid2))
                    self.name_edit.setText(name2)
                    # درصد سود
                    self.profit_edit.setText(str(profit2))
                   # لیست اولیه‌ی جدول
                    rl = [(rid, rname, price) for rname, price, g, rid in items2]
                    self.populate_table(rl)
                    # پر کردن ستون گرم بر اساس مقادیر قبلی
                    for idx, (_, _, _) in enumerate(rl):
                        self.raw_rows[idx][1].setText(str(items2[idx][2]))
                    break

    def populate_table(self, raw_list):
        self.raw_table.setRowCount(len(raw_list))
        self.raw_rows = []
        for i, (rid, name, _) in enumerate(raw_list):
            it = QTableWidgetItem(name)
            it.setData(Qt.UserRole, rid)
            self.raw_table.setItem(i, 0, it)
            ln = QLineEdit("0")
            ln.setMaximumWidth(80)
            self.raw_table.setCellWidget(i, 1, ln)
            self.raw_rows.append((rid, ln))

    def open_request_dialog(self):
        rd = RequestDialog(self.db.get_raw(), self)
        if rd.exec_():
            sel = rd.get_selected()
            rl = [(rid, name, price) for rid, name, price in self.db.get_raw() if rid in sel]
            self.populate_table(rl)

    def get_data(self):
        id_ = int(self.id_edit.text().strip())
        name = self.name_edit.text().strip()
        items = {}
        for rid, ln in self.raw_rows:
            grams = float(ln.text().replace(',', '')) if ln.text() else 0
            if grams > 0:
                items[rid] = grams
        profit = float(self.profit_edit.text().replace(',', '').replace('%',''))
        return id_, name, profit, items


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("SpiceApp", "Manager")
        self.load_user_settings()
        self.db = DatabaseManager()
        self.setWindowTitle("مدیر ادویه")
        self.setLayoutDirection(Qt.RightToLeft)
        self.resize(900, 650)
        self._build_ui()
        self.refresh_tables()
        self.custom_weights = []  # لیست وزن‌های فعال فعلی


    def confirm_delete_raw(self, rid):
        reply = QMessageBox.question(
            self, 'تأیید حذف',
            'آیا مطمئنید می‌خواهید این ماده را حذف کنید؟',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete_raw(rid)
            self.refresh_tables()

    def confirm_delete_composite(self, cid):
        reply = QMessageBox.question(
            self, 'تأیید حذف',
            'آیا مطمئنید می‌خواهید این ترکیب را حذف کنید؟',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete_composite(cid)
            self.refresh_tables()


    def _build_ui(self):
        self.tabs = QTabWidget()
        self.main_tab = QWidget(); self._init_main_tab(); self.tabs.addTab(self.main_tab, 'مدیریت')
        self.pack_tab = QWidget(); self._init_pack_tab(); self.tabs.addTab(self.pack_tab, 'بسته بندی')
        self.setCentralWidget(self.tabs)
        self.settings_tab = QWidget()
        self._init_settings_tab()
        self.tabs.addTab(self.settings_tab, 'تنظیمات')


    def _init_main_tab(self):
        l = QVBoxLayout(self.main_tab)


                # درصد سود
        # h_profit = QHBoxLayout()
        # h_profit.addWidget(QLabel("درصد سود:"))
        # self.profit_margin_input = QLineEdit("20")  # مقدار پیش‌فرض مثلاً ۲۰٪
        # self.profit_margin_input.setMaximumWidth(60)
        # self.profit_margin_input.textChanged.connect(lambda: self.refresh_comp_table())
        # h_profit.addWidget(self.profit_margin_input)
        # h_profit.addStretch()
        # l.addLayout(h_profit)


        # raw
        self.raw_search = QLineEdit(); self.raw_search.setPlaceholderText("جست‌وجوی ماده…")
        self.raw_search.textChanged.connect(self._filter_raw_table); l.addWidget(self.raw_search)
        h = QHBoxLayout()
        h.addWidget(QLabel("ماده:")); self.raw_name = QLineEdit(); h.addWidget(self.raw_name)
        h.addWidget(QLabel("قیمت (ت/کیلو):")); self.raw_price = QLineEdit()
        self.raw_price.textChanged.connect(lambda t: PriceDelegate(self).format_text(self.raw_price, t))
        h.addWidget(self.raw_price)
        btn = QPushButton("افزودن"); btn.clicked.connect(self.add_raw); h.addWidget(btn)
        l.addLayout(h)
        self.raw_table = QTableWidget(0,4)
        self.raw_table.setHorizontalHeaderLabels(["نام","قیمت","حذف","ویرایش"])
        self.raw_table.setItemDelegateForColumn(1, PriceDelegate(self))
        l.addWidget(self.raw_table)

        # filter composites by raw
        l.addWidget(QLabel("فیلتر ترکیبات بر اساس مواد اولیه:"))
        self.filter_scroll = QScrollArea(); self.filter_scroll.setWidgetResizable(True)
        self.filter_widget = QWidget(); self.filter_layout = QVBoxLayout(self.filter_widget)
        self.filter_layout.addStretch(); self.filter_scroll.setWidget(self.filter_widget); l.addWidget(self.filter_scroll)

        # composites
        self.comp_search = QLineEdit(); self.comp_search.setPlaceholderText("جست‌وجوی ترکیب…")
        self.comp_search.textChanged.connect(self._filter_comp_table); l.addWidget(self.comp_search)
        ch = QHBoxLayout(); ch.addWidget(QLabel("ترکیب:")); self.comp_name = QLineEdit(); ch.addWidget(self.comp_name)
        btn = QPushButton("تعریف"); btn.clicked.connect(self.define_composite); ch.addWidget(btn); l.addLayout(ch)
        self.comp_table = QTableWidget(0, 8)
        self.comp_table.setHorizontalHeaderLabels(["شناسه","نام","قیمت تولید","قیمت فروش","کل گرم (g)","حذف","ویرایش نام","ویرایش ترکیبات"])

        l.addWidget(self.comp_table)


    def _init_main_tab(self):
        l = QVBoxLayout(self.main_tab)

        # raw
        self.raw_search = QLineEdit()
        self.raw_search.setPlaceholderText("جست‌وجوی ماده…")
        self.raw_search.textChanged.connect(self._filter_raw_table)
        l.addWidget(self.raw_search)

        h = QHBoxLayout()
        h.addWidget(QLabel("ماده:"))
        self.raw_name = QLineEdit()
        h.addWidget(self.raw_name)

        h.addWidget(QLabel("قیمت (ت/کیلو):"))
        self.raw_price = QLineEdit()
        self.raw_price.textChanged.connect(lambda t: PriceDelegate(self).format_text(self.raw_price, t))
        self.raw_price.returnPressed.connect(self.add_raw)  # Connect the returnPressed signal to add_raw
        h.addWidget(self.raw_price)

        btn = QPushButton("افزودن")
        btn.clicked.connect(self.add_raw)
        h.addWidget(btn)

        l.addLayout(h)
        self.raw_table = QTableWidget(0, 4)
        self.raw_table.setHorizontalHeaderLabels(["نام", "قیمت", "حذف", "ویرایش"])
        self.raw_table.setItemDelegateForColumn(1, PriceDelegate(self))
        l.addWidget(self.raw_table)

        # filter composites by raw
        l.addWidget(QLabel("فیلتر ترکیبات بر اساس مواد اولیه:"))
        self.filter_scroll = QScrollArea()
        self.filter_scroll.setWidgetResizable(True)
        self.filter_widget = QWidget()
        self.filter_layout = QVBoxLayout(self.filter_widget)
        self.filter_layout.addStretch()
        self.filter_scroll.setWidget(self.filter_widget)
        l.addWidget(self.filter_scroll)

        # composites
        self.comp_search = QLineEdit()
                # درصد سود
        # h_profit = QHBoxLayout()
        # h_profit.addWidget(QLabel("درصد سود:"))
        # self.profit_margin_input = QLineEdit("20")  # پیش‌فرض ۲۰٪
        # self.profit_margin_input.setMaximumWidth(60)
        # self.profit_margin_input.textChanged.connect(lambda: self.refresh_comp_table())
        # h_profit.addWidget(self.profit_margin_input)
        # h_profit.addStretch()
        # l.addLayout(h_profit)

        self.comp_search.setPlaceholderText("جست‌وجوی ترکیب…")
        self.comp_search.textChanged.connect(self._filter_comp_table)
        l.addWidget(self.comp_search)

        ch = QHBoxLayout()
        ch.addWidget(QLabel("ترکیب:"))
        self.comp_name = QLineEdit()
        ch.addWidget(self.comp_name)

        btn = QPushButton("تعریف")
        btn.clicked.connect(self.define_composite)
        ch.addWidget(btn)
        l.addLayout(ch)

        self.comp_table = QTableWidget(0, 8)
        self.comp_table.setHorizontalHeaderLabels(["شناسه", "نام", "قیمت تولید", "قیمت فروش", "کل گرم (g)", "حذف", "ویرایش نام", "ویرایش ترکیبات"])
        l.addWidget(self.comp_table)


    def _init_pack_tab(self):
        l = QVBoxLayout(self.pack_tab)

        self.pack_table = QTableWidget()
        self.pack_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        l.addWidget(self.pack_table)

        control = QHBoxLayout()
        control.addWidget(QLabel("وزن دلخواه (g):"))
        self.custom_weight = QLineEdit()
        control.addWidget(self.custom_weight)

        btn_add_weight = QPushButton("افزودن وزن")
        btn_add_weight.clicked.connect(self.add_custom_weight_column)
        control.addWidget(btn_add_weight)

        l.addLayout(control)

        # ستون اول همیشه نام ترکیب است
        self.pack_table.setColumnCount(1)
        self.pack_table.setHorizontalHeaderLabels(["نام ترکیب"])
        self.refresh_pack_rows()


    

    def _init_settings_tab(self):
        layout = QVBoxLayout(self.settings_tab)

        # Font selector
        layout.addWidget(QLabel("فونت برنامه:"))
        self.font_button = QPushButton("انتخاب فونت")
        self.font_button.clicked.connect(self.open_font_dialog)
        layout.addWidget(self.font_button)

        self.preview_label = QLabel("نمونه پیش‌نمایش فونت")
        layout.addWidget(self.preview_label)



        # Color selector
        layout.addWidget(QLabel("انتخاب رنگ پس‌زمینه:"))
        self.color_btn = QPushButton("انتخاب رنگ")
        self.color_btn.clicked.connect(self.open_color_dialog)
        layout.addWidget(self.color_btn)

        layout.addStretch()

    def change_app_font(self, font):
        QApplication.setFont(font)
        self.preview_label.setFont(font)
        self.save_user_settings(font=font)

    def open_color_dialog(self):
        color = QColorDialog.getColor(QColor("white"), self, "انتخاب رنگ پس‌زمینه")
        if color.isValid():
            self.setStyleSheet(f"QWidget {{ background-color: {color.name()}; }}")
            self.save_user_settings(color=color)



    def add_raw(self):
        name = self.raw_name.text().strip()
        txt = self.raw_price.text().replace(',','')
        try:
            price = float(txt)
        except:
            QMessageBox.warning(self,'خطا','قیمت نامعتبر'); return
        self.db.add_raw(name, price)
        self.raw_name.clear(); self.raw_price.clear(); self.refresh_tables()

    def _filter_raw_table(self):
        kw = self.raw_search.text().strip()
        for i in range(self.raw_table.rowCount()):
            self.raw_table.setRowHidden(i, kw not in self.raw_table.item(i,0).text())

    def refresh_raw_table(self):
        raws = self.db.get_raw()
        self.raw_table.setRowCount(len(raws))
        for i,(rid,name,price) in enumerate(raws):
            # ستون نام: غیرقابل ویرایش
            it = QTableWidgetItem(name)
            it.setData(Qt.UserRole, rid)
            it.setFlags(it.flags() & ~Qt.ItemIsEditable)  # <--- اضافه کنید
            self.raw_table.setItem(i, 0, it)

            # ستون قیمت: با قابلیت ویرایش
            price_item = QTableWidgetItem(f"{price:,.0f}")
            self.raw_table.setItem(i, 1, price_item)

            # دکمه حذف
            btn = QPushButton("حذف")
            btn.clicked.connect(lambda _, r=rid: self.confirm_delete_raw(r))
            self.raw_table.setCellWidget(i,2,btn)


            # دکمه ویرایش (نام)
            btn2 = QPushButton("ویرایش")
            btn2.clicked.connect(lambda _,r=rid:self.edit_raw(r))
            self.raw_table.setCellWidget(i,3,btn2)

    def edit_raw(self, rid):
        cur = next(r for r in self.db.get_raw() if r[0]==rid)[1]
        dlg = EditDialog("ویرایش ماده",{"نام":cur},self)
        if dlg.exec_():
            self.db.update_raw_name(rid, dlg.get_values()["نام"]); self.refresh_tables()

    def refresh_filter_list(self):
        for cb in getattr(self,'raw_checkboxes',[]): cb.deleteLater()
        self.raw_checkboxes=[]
        for rid,name,_ in self.db.get_raw():
            cb=QCheckBox(name); cb.raw_id=rid; cb.stateChanged.connect(self.refresh_comp_table)
            self.filter_layout.insertWidget(self.filter_layout.count()-1,cb); self.raw_checkboxes.append(cb)

    def define_composite(self):
        dlg=CompositeDialog(self.db,parent=self)
        if dlg.exec_():
            cid,name,profit,items=dlg.get_data()
            self.db.add_composite(cid, name, profit, items)
            self.refresh_tables()

    def _filter_comp_table(self):
        kw=self.comp_search.text().strip()
        for i in range(self.comp_table.rowCount()):
            self.comp_table.setRowHidden(i,kw not in self.comp_table.item(i,1).text())

    def refresh_comp_table(self):
        comps = self.db.get_composites([cb.raw_id for cb in self.raw_checkboxes if cb.isChecked()] or None)
        try:
            profit_percent = float(self.profit_margin_input.text().replace('%', '').replace(',', ''))
        except:
            profit_percent = 0

        self.comp_table.setRowCount(len(comps))
        for i, (cid, name, prod_price, sell_price, grams, items, profit) in enumerate(comps):
            # شناسه
            id_item = QTableWidgetItem(str(cid))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.comp_table.setItem(i, 0, id_item)

            # نام ترکیب
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.comp_table.setItem(i, 1, name_item)

            # قیمت تولید
            price_item = QTableWidgetItem(f"{prod_price:,.0f}")
            price_item.setFlags(price_item.flags() & ~Qt.ItemIsEditable)
            self.comp_table.setItem(i, 2, price_item)

            # قیمت فروش = قیمت تولید + سود
            sell_item = QTableWidgetItem(f"{sell_price:,.0f}")
            sell_item.setFlags(sell_item.flags() & ~Qt.ItemIsEditable)
            self.comp_table.setItem(i, 3, sell_item)

            # کل گرم
            grams_item = QTableWidgetItem(f"{grams:,.0f}")
            grams_item.setFlags(grams_item.flags() & ~Qt.ItemIsEditable)
            self.comp_table.setItem(i, 4, grams_item)

            # حذف
            btn_del = QPushButton("حذف")
            btn_del.clicked.connect(lambda _, c=cid: self.confirm_delete_composite(c))
            self.comp_table.setCellWidget(i, 5, btn_del)

            # ویرایش نام
            btn_edit_name = QPushButton("ویرایش نام")
            btn_edit_name.clicked.connect(lambda _, c=cid: self._edit_comp_name(c))
            self.comp_table.setCellWidget(i, 6, btn_edit_name)

            # ویرایش ترکیبات
            btn_edit_items = QPushButton("ویرایش ترکیبات")
            btn_edit_items.clicked.connect(lambda _, c=cid: self._edit_comp_items(c))
            self.comp_table.setCellWidget(i, 7, btn_edit_items)



    def _edit_comp_name(self, cid):
        cur = next(c for c in self.db.get_composites() if c[0] == cid)
        old_id, old_name, _, _, items,profit = cur
        items_dict = {rid: grams for _, _, grams, rid in items}
        dlg = EditDialog("ویرایش ترکیب", {"شناسه": old_id, "نام": old_name}, self)
        
        if dlg.exec_():
            vals = dlg.get_values()
            try:
                new_id = int(vals["شناسه"])
            except ValueError:
                QMessageBox.warning(self, 'خطا', 'شناسه نامعتبر')
                return
            
            new_name = vals["نام"]
            
            # Check if the new ID already exists
            existing_ids = [c[0] for c in self.db.get_composites()]
            if new_id != old_id and new_id in existing_ids:
                QMessageBox.warning(self, 'خطا', 'شناسه تکراری است')
                return
            
            try:
                self.db.update_composite(old_id, new_id, new_name, items_dict,profit)
                self.refresh_tables()
            except sqlite3.IntegrityError as e:
                QMessageBox.warning(self, 'خطا', f'خطا در به‌روزرسانی: {str(e)}')


    def _edit_comp_items(self, cid):
        dlg=CompositeDialog(self.db,comp_id=cid,parent=self)
        if dlg.exec_():
            new_id,new_name,profit,new_items=dlg.get_data()
            self.db.update_composite(cid,new_id,new_name,profit,new_items)
            self.refresh_tables()

    def refresh_pack_tab(self):
        self.pack_table.setRowCount(0)
        for cid, name, prod_price, sell_price, grams, items, profit in self.db.get_composites():
            unit = prod_price / grams if grams else 0
            r = self.pack_table.rowCount()
            self.pack_table.insertRow(r)
            self.pack_table.setItem(r, 0, QTableWidgetItem(name))
            # نمونه برای ستون‌های 100g, 250g, 500g:
            self.pack_table.setItem(r, 1, QTableWidgetItem(f"{unit*100:,.0f}"))
            self.pack_table.setItem(r, 2, QTableWidgetItem(f"{unit*250:,.0f}"))
            self.pack_table.setItem(r, 3, QTableWidgetItem(f"{unit*500:,.0f}"))


    def calculate_custom_price(self):
        try:
            w=float(self.custom_weight.text().replace(',', ''))
        except:
            QMessageBox.warning(self,'خطا','وزن نامعتبر');return
        cid=self.comp_select.currentData()
        for cid2,name,price,grams,_ in self.db.get_composites():
            if cid2==cid:
                self.custom_result.setText(f"{name}: {price/grams*w:,.0f} تومان")
                break
    def load_user_settings(self):
        font_family = self.settings.value("font_family", "")
        if font_family:
            app_font = QFont(font_family)
            QApplication.setFont(app_font)
            if hasattr(self, 'font_combo'):
                self.font_combo.setCurrentFont(app_font)

        bg_color = self.settings.value("bg_color", "")
        if bg_color:
            self.setStyleSheet(f"QWidget {{ background-color: {bg_color}; }}")


    def save_user_settings(self, font=None, color=None):
        if font:
            self.settings.setValue("font_family", font.family())
        if color:
            self.settings.setValue("bg_color", color.name())


    def open_font_dialog(self):
        from PyQt5.QtWidgets import QFontDialog
        font, ok = QFontDialog.getFont(QApplication.font(), self, "انتخاب فونت")
        if ok:
            QApplication.setFont(font)
            self.preview_label.setFont(font)
            self.apply_font_to_all_widgets(font=font)
            self.save_user_settings(font=font)

    def apply_font_to_all_widgets(self, widget=None, font=None):
        if widget is None:
            widget = self
        if font is None:
            font = QApplication.font()

        widget.setFont(font)
        for child in widget.findChildren(QWidget):
            child.setFont(font)


    def add_custom_weight_column(self):
        try:
            weight = int(self.custom_weight.text().replace(',', ''))
            if weight <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "خطا", "وزن نامعتبر است")
            return

        if weight in self.custom_weights:
            QMessageBox.information(self, "اطلاع", "این وزن قبلاً اضافه شده")
            return

        self.custom_weights.append(weight)
        self.refresh_pack_columns()
        self.custom_weight.clear()


    def remove_weight_column(self, weight):
            if weight in self.custom_weights:
                self.custom_weights.remove(weight)
                self.refresh_pack_columns()


    def refresh_pack_rows(self):
        self.composites_for_pack = self.db.get_composites()
        self.pack_table.setRowCount(len(self.composites_for_pack))
        for i, (cid, name, prod_price, sell_price, grams, items, profit) in enumerate(self.composites_for_pack):
            item = QTableWidgetItem(name)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.pack_table.setItem(i, 0, item)


    def refresh_pack_columns(self):
        self.pack_table.setColumnCount(1 + len(self.custom_weights))  # ستون نام + وزن‌ها
        headers = ["نام ترکیب"] + [f"{w}g" for w in self.custom_weights]
        self.pack_table.setHorizontalHeaderLabels(headers)

        self.refresh_pack_rows()

        for col, weight in enumerate(self.custom_weights, start=1):
            for row, (_, _, prod_price, sell_price, grams, items, profit) in enumerate(self.composites_for_pack):
                if grams == 0:
                    self.pack_table.setItem(row, col, QTableWidgetItem("0"))
                    continue
                unit_price = prod_price / grams   # یا sell_price / grams اگر بر اساس قیمت فروش می‌خواهید
                total = unit_price * weight
                self.pack_table.setItem(row, col, QTableWidgetItem(f"{total:,.0f}"))


        # دکمه حذف ستون
        btn = QPushButton("❌")
        btn.setToolTip("حذف وزن")
        btn.clicked.connect(lambda _, w=weight: self.remove_weight_column(w))
        self.pack_table.setCellWidget(-1, col, btn)  # نمایش در هدر ممکن نیست، به‌صورت معمول می‌ذاریم







    def refresh_tables(self):
        self.refresh_raw_table()
        self.refresh_filter_list()
        self.refresh_comp_table()
        self.refresh_pack_tab()

if __name__=='__main__':
    app=QApplication(sys.argv)
    w=MainWindow()
    w.show()
    sys.exit(app.exec_())