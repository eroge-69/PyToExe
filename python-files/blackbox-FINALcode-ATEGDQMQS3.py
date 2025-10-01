import sys  
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QMessageBox, QDateEdit,
    QStackedWidget, QHeaderView, QTabWidget, QComboBox, QSizePolicy, QFrame,
    QAbstractItemView, QSpacerItem, QProgressDialog
)
from PyQt5.QtCore import Qt, QDate, QRectF, QTimer, QSettings
from PyQt5.QtGui import QColor, QFont, QPainter, QBrush, QPen, QIcon, QDoubleValidator
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog # تم تصحيح هذا السطر
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
from playsound import playsound # لتشغيل الأصوات

# ----- الإعدادات العامة -----
EXCEL_FILE = "balance_sheet.xlsx"
COLUMNS = ["التاريخ", "النوع", "المبلغ", "الرصيد الحالي", "وصف العملية"]
USERNAME = "MD.ELAMROSY"
PASSWORD = "65868978"
COPYRIGHT_TEXT = "© MOHAMED ELAMROSY"
APP_NAME = "BalanceSheetApp"
ORG_NAME = "MohamedElAmrosy"

# مسارات ملفات الصوت (تأكد من وجودها أو قم بتغيير المسارات)
SOUND_PATHS = {
    "login_success": "sounds/login_success.wav",
    "add_entry": "sounds/add_entry.wav",
    "delete_entry": "sounds/delete_entry.wav",
    "negative_balance": "sounds/negative_balance.wav",
    "logout": "sounds/logout.wav",
    "error": "sounds/error.wav",
    "save_success": "sounds/save_success.wav"
}

def play_sound(sound_key):
    """تشغيل ملف صوتي إذا كان موجودًا."""
    path = SOUND_PATHS.get(sound_key)
    if path and os.path.exists(path):
        try:
            playsound(path, block=False)
        except Exception as e:
            print(f"Error playing sound {path}: {e}")

# نصوص متعددة اللغات
TEXTS = {
    "app_title": {"العربية": "شيت الرصيد - MOHAMED ELAMROSY", "English": "Balance Sheet - MOHAMED ELAMROSY"},
    "login_title": {"العربية": "تسجيل الدخول", "English": "Login"},
    "username_placeholder": {"العربية": "اسم المستخدم", "English": "Username"},
    "password_placeholder": {"العربية": "كلمة المرور", "English": "Password"},
    "login_btn": {"العربية": "دخول", "English": "Login"},
    "login_success_msg": {"العربية": "السلام عليكم … أهلا ومرحبا بكم", "English": "Hello and Welcome!"},
    "login_error_msg": {"العربية": "اسم المستخدم أو كلمة المرور غير صحيحة", "English": "Wrong username or password"},
    "add_btn": {"العربية": "إضافة", "English": "Add"},
    "delete_btn": {"العربية": "حذف", "English": "Delete"},
    "refresh_btn": {"العربية": "تحديث", "English": "Refresh"},
    "save_btn": {"العربية": "حفظ", "English": "Save"},
    "logout_btn": {"العربية": "تسجيل خروج", "English": "Logout"},
    "print_btn": {"العربية": "طباعة", "English": "Print"},
    "date_label": {"العربية": "التاريخ:", "English": "Date:"},
    "amount_label": {"العربية": "المبلغ:", "English": "Amount:"},
    "desc_label": {"العربية": "وصف العملية:", "English": "Description:"},
    "invalid_amount": {"العربية": "المبلغ غير صحيح. يرجى إدخال رقم موجب.", "English": "Invalid amount. Please enter a positive number."},
    "select_row_delete": {"العربية": "اختر صفًا للحذف أولاً.", "English": "Select a row to delete first."},
    "confirm_delete": {"العربية": "هل أنت متأكد من حذف هذا الصف؟", "English": "Are you sure you want to delete this row?"},
    "negative_balance_warning": {"العربية": "⚠️ تنبيه: الرصيد أصبح بالسالب! يرجى مراجعة حساباتك.", "English": "⚠️ Warning: Balance is negative! Please review your accounts."},
    "logout_confirm": {"العربية": "هل تريد تسجيل الخروج؟", "English": "Do you want to logout?"},
    "exit_confirm": {"العربية": "هل أنت متأكد من الخروج من التطبيق؟", "English": "Are you sure you want to exit the application?"},
    "error_title": {"العربية": "خطأ", "English": "Error"},
    "warning_title": {"العربية": "تنبيه", "English": "Warning"},
    "confirm_title": {"العربية": "تأكيد", "English": "Confirm"},
    "balance_summary": {"العربية": "💰 الرصيد الكلي:", "English": "💰 Total Balance:"},
    "deposit_summary": {"العربية": "📥 إجمالي الإيداعات:", "English": "📥 Total Deposits:"},
    "expense_summary": {"العربية": "📤 إجمالي المصروفات:", "English": "📤 Total Expenses:"},
    "net_summary": {"العربية": "📊 الصافي:", "English": "📊 Net:"},
    "balance_chart_title": {"العربية": "تطور الرصيد عبر الزمن", "English": "Balance Evolution Over Time"},
    "date_chart_label": {"العربية": "التاريخ", "English": "Date"},
    "balance_chart_label": {"العربية": "الرصيد", "English": "Balance"},
    "main_tab": {"العربية": "الرئيسية", "English": "Main"},
    "deposit_tab": {"العربية": "الإيداع", "English": "Deposit"},
    "expense_tab": {"العربية": "المصروفات", "English": "Expense"},
    "print_header": {"العربية": "تقرير كشف الحساب", "English": "Account Statement Report"},
    "print_footer": {"العربية": f"تقرير تم إنشاؤه بواسطة {COPYRIGHT_TEXT}", "English": f"Report generated by {COPYRIGHT_TEXT}"},
    "save_success": {"العربية": "تم حفظ البيانات بنجاح في ملف Excel.", "English": "Data successfully saved to Excel file."},
    "save_error": {"العربية": "حدث خطأ أثناء حفظ البيانات: ", "English": "Error saving data: "},
    "loading_data": {"العربية": "جاري تحميل البيانات...", "English": "Loading data..."},
    "saving_data": {"العربية": "جاري حفظ البيانات...", "English": "Saving data..."},
}

# ----- تحميل البيانات -----
df = pd.DataFrame(columns=COLUMNS) # تعريف df كمتغير عام مبدئيًا

def load_initial_data():
    """تحميل البيانات من ملف Excel مع التحقق من الأعمدة."""
    global df
    if os.path.exists(EXCEL_FILE):
        try:
            temp_df = pd.read_excel(EXCEL_FILE)
            # التأكد من وجود جميع الأعمدة الأساسية
            missing_cols = [col for col in COLUMNS if col not in temp_df.columns]
            if missing_cols:
                QMessageBox.warning(None, TEXTS["warning_title"]["العربية"], 
                                    f"ملف Excel يفتقد للأعمدة التالية: {', '.join(missing_cols)}. سيتم إضافتها.")
                for col in missing_cols:
                    temp_df[col] = 0 if col in ["المبلغ", "الرصيد الحالي"] else ""
            df = temp_df[COLUMNS] # التأكد من ترتيب الأعمدة
        except Exception as e:
            QMessageBox.critical(None, TEXTS["error_title"]["العربية"], 
                                 f"خطأ في تحميل ملف Excel: {e}\nسيتم إنشاء ملف جديد.")
            df = pd.DataFrame(columns=COLUMNS)
    else:
        df = pd.DataFrame(columns=COLUMNS)
    
    df = update_balance(df)

def update_balance(df_local):
    """تحديث عمود الرصيد الحالي بناءً على العمليات."""
    if df_local.empty:
        return pd.DataFrame(columns=COLUMNS)
    
    # تحويل عمود التاريخ إلى datetime لفرز صحيح
    # التعامل مع الأخطاء في التحويل
    df_local["التاريخ"] = pd.to_datetime(df_local["التاريخ"], errors='coerce')
    df_local = df_local.dropna(subset=["التاريخ"]) # حذف الصفوف التي فشل تحويل تاريخها
    df_local = df_local.sort_values(by="التاريخ").reset_index(drop=True)
    
    balance = 0
    balances = []
    for _, row in df_local.iterrows():
        # التأكد من أن المبلغ رقمي
        try:
            amount = float(str(row["المبلغ"]).replace(',', '')) # إزالة فواصل الآلاف قبل التحويل
        except ValueError:
            amount = 0.0 # تجاهل القيم غير الرقمية أو التعامل معها كصفر
            
        if str(row["النوع"]).lower() in ["رصيد", "deposit"]:
            balance += amount
        else:
            balance -= amount
        balances.append(balance)
    df_local["الرصيد الحالي"] = balances
    return df_local

# ----- Toast Notification Widget -----
class ToastNotification(QWidget):
    def __init__(self, message, parent=None, duration=3000, bg_color="#333", text_color="white"):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.layout = QVBoxLayout(self)
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 12pt;
                font-weight: bold;
            }}
        """)
        self.layout.addWidget(self.label)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hide_toast)
        self.duration = duration
        self.setFixedSize(self.label.sizeHint().width() + 40, self.label.sizeHint().height() + 20)

    def show_toast(self):
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + parent_rect.height() - self.height() - 50 # أسفل الشاشة
            self.move(x, y)
        self.show()
        self.timer.start(self.duration)

    def hide_toast(self):
        self.timer.stop()
        self.close()

# ----- واجهة تسجيل الدخول -----
class LoginWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.settings = QSettings(ORG_NAME, APP_NAME)
        self.lang = self.settings.value("language", "العربية")
        self.setup_ui()
        self.update_language(self.lang)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Title
        self.title_lbl = QLabel()
        self.title_lbl.setFont(QFont("Arial", 36, QFont.Bold))
        self.title_lbl.setAlignment(Qt.AlignCenter)
        self.title_lbl.setStyleSheet("color: #0056b3;") # لون أزرق داكن
        layout.addWidget(self.title_lbl)

        # Input fields frame
        input_frame = QFrame()
        input_frame.setFrameShape(QFrame.StyledPanel)
        input_frame.setFrameShadow(QFrame.Raised)
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 10px;
                padding: 20px;
            }
            QLineEdit {
                border: 1px solid #a0a0a0;
                border-radius: 5px;
                padding: 8px;
                font-size: 14pt;
            }
            QLineEdit:focus {
                border: 2px solid #007bff;
            }
        """)
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(15)

        self.user_edit = QLineEdit()
        self.user_edit.setFixedWidth(400)
        input_layout.addWidget(self.user_edit, alignment=Qt.AlignCenter)

        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.Password)
        self.pass_edit.setFixedWidth(400)
        input_layout.addWidget(self.pass_edit, alignment=Qt.AlignCenter)

        layout.addWidget(input_frame, alignment=Qt.AlignCenter)

        # Login button
        self.login_btn = QPushButton()
        self.login_btn.setFixedWidth(250)
        self.login_btn.setFixedHeight(50)
        self.login_btn.setFont(QFont("Arial", 16, QFont.Bold))
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745; /* أخضر */
                color: white;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.login_btn.clicked.connect(self.try_login)
        layout.addWidget(self.login_btn, alignment=Qt.AlignCenter)

        # Language selection
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["العربية", "English"])
        self.lang_combo.setFixedWidth(150)
        self.lang_combo.setFont(QFont("Arial", 12))
        self.lang_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #a0a0a0;
                border-radius: 5px;
                padding: 5px;
                background-color: #f0f0f0;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down.png); /* يمكنك إضافة أيقونة سهم */
                width: 15px;
                height: 15px;
            }
        """)
        self.lang_combo.currentTextChanged.connect(self.update_language)
        self.lang_combo.setCurrentText(self.lang) # تعيين اللغة المحفوظة
        layout.addWidget(self.lang_combo, alignment=Qt.AlignCenter)

        # Copyright
        self.copyright_lbl = QLabel(COPYRIGHT_TEXT)
        self.copyright_lbl.setAlignment(Qt.AlignCenter)
        self.copyright_lbl.setStyleSheet("color: #6c757d; font-size: 10pt;") # لون رمادي
        layout.addWidget(self.copyright_lbl)

    def update_language(self, lang):
        self.lang = lang
        self.settings.setValue("language", lang) # حفظ اللغة
        self.title_lbl.setText(TEXTS["login_title"][lang])
        self.user_edit.setPlaceholderText(TEXTS["username_placeholder"][lang])
        self.pass_edit.setPlaceholderText(TEXTS["password_placeholder"][lang])
        self.login_btn.setText(TEXTS["login_btn"][lang])
        # تحديث اتجاه الواجهة
        if lang == "العربية":
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)
        
        # تحديث عنوان النافذة الرئيسية
        if self.parent:
            self.parent.setWindowTitle(TEXTS["app_title"][lang])

    def try_login(self):
        if self.user_edit.text() == USERNAME and self.pass_edit.text() == PASSWORD:
            play_sound("login_success")
            QMessageBox.information(self, TEXTS["login_title"][self.lang], TEXTS["login_success_msg"][self.lang])
            self.parent.stack.setCurrentIndex(1)
            self.parent.dashboard_page.set_language(self.lang) # تحديث لغة لوحة التحكم
        else:
            play_sound("error")
            QMessageBox.warning(self, TEXTS["error_title"][self.lang], TEXTS["login_error_msg"][self.lang])

# ----- تبويب العمليات (TabWidget) -----
class TabWidget(QWidget):
    def __init__(self, tab_type, main_window):
        super().__init__()
        self.tab_type = tab_type
        self.main_window = main_window
        self.lang = "العربية" # سيتم تحديثها بواسطة Dashboard
        self.setup_ui()
        # لا نستدعي update_language و load_data هنا مباشرة، بل من Dashboard
        # لضمان تزامن اللغة والبيانات بعد التهيئة الكاملة.

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)

        # ---- Table ----
        self.table = QTableWidget()
        self.table.setColumnCount(len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setFont(QFont("Arial", 11))
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #f8f9fa;
                alternate-background-color: #e9ecef;
                gridline-color: #dee2e6;
                border: 1px solid #ced4da;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #007bff; /* أزرق أساسي */
                color: white;
                font-weight: bold;
                font-size: 12pt;
                padding: 6px;
                border-right: 1px solid #0056b3;
            }
            QHeaderView::section:last {
                border-right: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #6c757d; /* رمادي داكن عند التحديد */
                color: white;
            }
        """)
        self.table.itemChanged.connect(self.handle_item_changed) # ربط لتعديل الخلايا
        self.layout.addWidget(self.table)

        # ---- Inputs Frame ----
        input_frame = QFrame()
        input_frame.setFrameShape(QFrame.StyledPanel)
        input_frame.setFrameShadow(QFrame.Sunken)
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
            }
            QLabel {
                font-size: 11pt;
                font-weight: bold;
                color: #343a40;
            }
            QLineEdit, QDateEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px;
                font-size: 11pt;
            }
            QLineEdit:focus, QDateEdit:focus {
                border: 2px solid #007bff;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setSpacing(15)

        self.date_label = QLabel()
        input_layout.addWidget(self.date_label)
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setFixedWidth(130)
        input_layout.addWidget(self.date_edit)

        self.amount_label = QLabel()
        input_layout.addWidget(self.amount_label)
        self.amount_input = QLineEdit()
        self.amount_input.setFixedWidth(150)
        self.amount_input.setValidator(QDoubleValidator(0.0, 999999999.99, 2)) # للسماح بالأرقام فقط
        input_layout.addWidget(self.amount_input)

        self.desc_label = QLabel()
        input_layout.addWidget(self.desc_label)
        self.desc_input = QLineEdit()
        self.desc_input.setFixedWidth(250)
        input_layout.addWidget(self.desc_input)

        input_layout.addStretch()
        self.layout.addWidget(input_frame)

        # ---- Buttons Frame ----
        btn_frame = QFrame()
        btn_frame.setFrameShape(QFrame.NoFrame)
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setSpacing(10)
        btn_layout.addStretch(1)

        button_style = """
            QPushButton {
                background-color: #007bff; /* أزرق */
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """
        delete_button_style = """
            QPushButton {
                background-color: #dc3545; /* أحمر */
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """
        logout_button_style = """
            QPushButton {
                background-color: #6c757d; /* رمادي */
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """

        self.add_btn = QPushButton()
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setStyleSheet(button_style)
        self.add_btn.setIcon(QIcon("icons/add.png")) # أيقونة إضافة
        self.add_btn.clicked.connect(self.add_entry)
        btn_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton()
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.setStyleSheet(delete_button_style)
        self.delete_btn.setIcon(QIcon("icons/delete.png")) # أيقونة حذف
        self.delete_btn.clicked.connect(self.delete_entry)
        btn_layout.addWidget(self.delete_btn)

        self.refresh_btn = QPushButton()
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setStyleSheet(button_style)
        self.refresh_btn.setIcon(QIcon("icons/refresh.png")) # أيقونة تحديث
        self.refresh_btn.clicked.connect(self.load_data)
        btn_layout.addWidget(self.refresh_btn)

        self.save_btn = QPushButton()
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setStyleSheet(button_style)
        self.save_btn.setIcon(QIcon("icons/save.png")) # أيقونة حفظ
        self.save_btn.clicked.connect(self.save)
        btn_layout.addWidget(self.save_btn)

        self.print_btn = QPushButton()
        self.print_btn.setCursor(Qt.PointingHandCursor)
        self.print_btn.setStyleSheet(button_style)
        self.print_btn.setIcon(QIcon("icons/print.png")) # أيقونة طباعة
        self.print_btn.clicked.connect(self.print_table)
        btn_layout.addWidget(self.print_btn)

        self.logout_btn = QPushButton()
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet(logout_button_style)
        self.logout_btn.setIcon(QIcon("icons/logout.png")) # أيقونة تسجيل خروج
        self.logout_btn.clicked.connect(self.logout)
        btn_layout.addWidget(self.logout_btn)

        btn_layout.addStretch(1)
        self.layout.addWidget(btn_frame)

        # ---- Chart ----
        self.figure = Figure(figsize=(6, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("border: 1px solid #ced4da; border-radius: 8px; background-color: white;")
        self.layout.addWidget(self.canvas)

    def update_language(self, lang):
        self.lang = lang
        if lang == "العربية":
            labels = ["التاريخ", "النوع", "المبلغ", "الرصيد الحالي", "وصف العملية"]
            self.setLayoutDirection(Qt.RightToLeft)
            self.table.horizontalHeader().setLayoutDirection(Qt.RightToLeft)
        else:
            labels = ["Date", "Type", "Amount", "Balance", "Description"]
            self.setLayoutDirection(Qt.LeftToRight)
            self.table.horizontalHeader().setLayoutDirection(Qt.LeftToRight)
        self.table.setHorizontalHeaderLabels(labels)

        self.add_btn.setText(TEXTS["add_btn"][lang])
        self.delete_btn.setText(TEXTS["delete_btn"][lang])
        self.refresh_btn.setText(TEXTS["refresh_btn"][lang])
        self.save_btn.setText(TEXTS["save_btn"][lang])
        self.logout_btn.setText(TEXTS["logout_btn"][lang])
        self.print_btn.setText(TEXTS["print_btn"][lang])

        self.date_label.setText(TEXTS["date_label"][lang])
        self.amount_label.setText(TEXTS["amount_label"][lang])
        self.desc_label.setText(TEXTS["desc_label"][lang])

    def set_language(self, lang):
        self.update_language(lang)
        self.load_data() # إعادة تحميل البيانات لتحديث الرسوم البيانية والنصوص

    def get_filtered_df(self):
        """يحصل على DataFrame المفلتر بناءً على نوع التبويب الحالي."""
        global df
        filtered = df.copy()
        
        current_tab_type_ar = self.tab_type
        current_tab_type_en = ""

        if self.tab_type == TEXTS["deposit_tab"]["العربية"]:
            current_tab_type_en = TEXTS["deposit_tab"]["English"]
        elif self.tab_type == TEXTS["expense_tab"]["العربية"]:
            current_tab_type_en = TEXTS["expense_tab"]["English"]
        elif self.tab_type == TEXTS["main_tab"]["العربية"]:
            current_tab_type_en = TEXTS["main_tab"]["English"]

        if self.tab_type != TEXTS["main_tab"]["العربية"]:
            filtered = filtered[filtered["النوع"].str.lower().isin([current_tab_type_ar.lower(), current_tab_type_en.lower()])]
        return filtered

    def load_data(self):
        global df
        self.table.itemChanged.disconnect(self.handle_item_changed) # تعطيل الإشارة مؤقتًا
        
        filtered = self.get_filtered_df()
        
        self.table.setRowCount(len(filtered))
        for i, row in filtered.iterrows():
            for j, col in enumerate(COLUMNS):
                item = QTableWidgetItem()
                
                # تنسيق الأرقام
                if col in ["المبلغ", "الرصيد الحالي"]:
                    try:
                        value = float(str(row[col]).replace(',', ''))
                        item.setText(f"{value:,.2f}") 
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    except ValueError:
                        item.setText(str(row[col]))
                        item.setTextAlignment(Qt.AlignCenter)
                else:
                    item.setText(str(row[col]))
                    item.setTextAlignment(Qt.AlignCenter)
                
                # تلوين الصفوف بناءً على نوع العملية
                if row["النوع"].lower() in ["رصيد", "deposit"]:
                    item.setForeground(QColor("#28a745"))  # أخضر للإيداع
                    item.setFont(QFont("Arial", 11, QFont.Bold))
                elif row["النوع"].lower() in ["مصروف", "expense"]:
                    item.setForeground(QColor("#dc3545"))  # أحمر للمصروف
                    item.setFont(QFont("Arial", 11, QFont.Bold))
                else:
                    item.setForeground(QColor("#343a40")) # لون نص عادي
                    item.setFont(QFont("Arial", 11))
                self.table.setItem(i, j, item)
        
        self.table.itemChanged.connect(self.handle_item_changed) # إعادة تفعيل الإشارة
        self.update_chart(filtered)

    def handle_item_changed(self, item):
        global df
        # تجنب التكرار اللانهائي عند تحديث الخلايا برمجياً
        if not self.table.signalsBlocked():
            self.table.blockSignals(True) # منع إشارات أخرى أثناء التحديث

            row_in_table = item.row()
            col_in_table = item.column()
            new_value = item.text()

            filtered_df = self.get_filtered_df()
            if row_in_table >= len(filtered_df):
                self.table.blockSignals(False)
                return

            real_index_in_df = filtered_df.index[row_in_table]
            column_name = COLUMNS[col_in_table]

            # التحقق من صحة البيانات قبل التحديث
            if column_name in ["المبلغ", "الرصيد الحالي"]:
                try:
                    # إزالة فواصل الآلاف قبل التحويل
                    new_value_float = float(new_value.replace(',', '')) 
                    if new_value_float < 0 and column_name == "المبلغ":
                        QMessageBox.warning(self, TEXTS["warning_title"][self.lang], "المبلغ لا يمكن أن يكون سالبًا." if self.lang == "العربية" else "Amount cannot be negative.")
                        self.load_data() # إعادة تحميل البيانات الأصلية للخلية
                        self.table.blockSignals(False)
                        return
                    df.loc[real_index_in_df, column_name] = new_value_float
                except ValueError:
                    QMessageBox.warning(self, TEXTS["warning_title"][self.lang], TEXTS["invalid_amount"][self.lang])
                    self.load_data() # إعادة تحميل البيانات الأصلية للخلية
                    self.table.blockSignals(False)
                    return
            else:
                df.loc[real_index_in_df, column_name] = new_value
            
            df = update_balance(df) # إعادة حساب الرصيد بعد التعديل
            self.load_data() # إعادة تحميل الجدول لتحديث الرصيد الحالي
            self.main_window.update_dashboard()
            self.save() # حفظ التغييرات تلقائياً

            self.table.blockSignals(False) # إعادة تفعيل الإشارة

    def add_entry(self):
        global df
        try:
            amount = float(self.amount_input.text().replace(',', ''))
            if amount <= 0:
                QMessageBox.warning(self, TEXTS["warning_title"][self.lang], "المبلغ يجب أن يكون أكبر من صفر." if self.lang == "العربية" else "Amount must be greater than zero.")
                play_sound("error")
                return
        except ValueError:
            QMessageBox.warning(self, TEXTS["warning_title"][self.lang], TEXTS["invalid_amount"][self.lang])
            play_sound("error")
            return

        new_entry = {
            "التاريخ": self.date_edit.date().toString("yyyy-MM-dd"),
            "النوع": self.tab_type if self.tab_type != TEXTS["main_tab"]["العربية"] else "رصيد",
            "المبلغ": amount,
            "وصف العملية": self.desc_input.text(),
            "الرصيد الحالي": 0
        }
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df = update_balance(df)

        if df["الرصيد الحالي"].iloc[-1] < 0:
            play_sound("negative_balance")
            QMessageBox.warning(self, TEXTS["warning_title"][self.lang], TEXTS["negative_balance_warning"][self.lang])
        else:
            play_sound("add_entry")

        self.load_data()
        self.amount_input.clear()
        self.desc_input.clear()
        self.main_window.update_dashboard()
        self.save()

    def delete_entry(self):
        global df
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, TEXTS["warning_title"][self.lang], TEXTS["select_row_delete"][self.lang])
            play_sound("error")
            return
        
        confirm = QMessageBox.question(self, TEXTS["confirm_title"][self.lang], TEXTS["confirm_delete"][self.lang],
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            indices_to_drop = []
            filtered_df = self.get_filtered_df()

            for model_index in selected_rows:
                table_row = model_index.row()
                if table_row < len(filtered_df):
                    real_index = filtered_df.index[table_row]
                    indices_to_drop.append(real_index)
            
            if indices_to_drop:
                df = df.drop(indices_to_drop).reset_index(drop=True)
                df = update_balance(df)
                self.load_data()
                self.main_window.update_dashboard()
                self.save()
                play_sound("delete_entry")
            else:
                QMessageBox.warning(self, TEXTS["warning_title"][self.lang], "لم يتم العثور على الصفوف المحددة للحذف." if self.lang == "العربية" else "Selected rows not found for deletion.")

    def save(self):
        global df
        try:
            # عرض مؤشر حفظ
            toast = ToastNotification(TEXTS["saving_data"][self.lang], self.main_window, bg_color="#007bff")
            toast.show_toast()
            QApplication.processEvents() # تحديث الواجهة

            df.to_excel(EXCEL_FILE, index=False)
            play_sound("save_success")
            toast.hide_toast() # إخفاء مؤشر الحفظ
            ToastNotification(TEXTS["save_success"][self.lang], self.main_window, bg_color="#28a745").show_toast()
        except Exception as e:
            toast.hide_toast()
            QMessageBox.critical(self, TEXTS["error_title"][self.lang], TEXTS["save_error"][self.lang] + str(e))
            play_sound("error")

    def logout(self):
        confirm = QMessageBox.question(self, TEXTS["confirm_title"][self.lang], TEXTS["logout_confirm"][self.lang],
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            play_sound("logout")
            self.main_window.stack.setCurrentIndex(0)

    def update_chart(self, data):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if not data.empty:
            # تحويل التاريخ إلى صيغة مناسبة للرسم البياني
            data_sorted = data.sort_values(by="التاريخ")
            ax.plot(pd.to_datetime(data_sorted["التاريخ"]), data_sorted["الرصيد الحالي"], 
                    marker='o', linestyle='-', color='#007bff', linewidth=2, markersize=6)
        
        ax.set_title(TEXTS["balance_chart_title"][self.lang], fontsize=14, fontweight='bold', color='#343a40')
        ax.set_xlabel(TEXTS["date_chart_label"][self.lang], fontsize=12, color='#495057')
        ax.set_ylabel(TEXTS["balance_chart_label"][self.lang], fontsize=12, color='#495057')
        ax.grid(True, linestyle='--', alpha=0.6, color='#adb5bd')
        ax.tick_params(axis='x', rotation=45)
        self.figure.tight_layout() # لضبط الهوامش
        self.canvas.draw()

    def print_table(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)
            painter.begin(printer)

            # إعداد الخطوط والألوان
            header_font = QFont("Arial", 12, QFont.Bold)
            table_font = QFont("Arial", 10)
            title_font = QFont("Arial", 16, QFont.Bold)
            footer_font = QFont("Arial", 8)

            # حساب عرض وارتفاع الصفحة
            page_rect = printer.pageRect()
            margin = 50 # هامش من كل جانب
            printable_rect = QRectF(page_rect.x() + margin, page_rect.y() + margin,
                                    page_rect.width() - 2 * margin, page_rect.height() - 2 * margin)
            
            current_y = printable_rect.y()

            # طباعة العنوان
            painter.setFont(title_font)
            painter.drawText(printable_rect, Qt.AlignHCenter | Qt.AlignTop, TEXTS["print_header"][self.lang])
            current_y += title_font.pointSize() * 2

            # طباعة رؤوس الأعمدة
            painter.setFont(header_font)
            painter.setPen(QPen(QColor(0, 0, 0))) # لون أسود للحدود
            painter.setBrush(QBrush(QColor(220, 220, 220))) # لون خلفية خفيف للرؤوس

            col_widths = []
            total_table_width = 0
            for col in range(self.table.columnCount()):
                # تقدير عرض العمود بناءً على محتواه وعرض الجدول
                header_text = self.table.horizontalHeaderItem(col).text()
                metrics = painter.fontMetrics()
                width = max(metrics.width(header_text) + 20, self.table.columnWidth(col))
                col_widths.append(width)
                total_table_width += width
            
            # ضبط مقياس الجدول ليناسب عرض الصفحة
            scale_factor = printable_rect.width() / total_table_width
            col_widths = [w * scale_factor for w in col_widths]
            row_height = header_font.pointSize() * 2

            x_offset = printable_rect.x()

            for col in range(self.table.columnCount()):
                rect = QRectF(x_offset, current_y, col_widths[col], row_height)
                painter.drawRect(rect)
                painter.drawText(rect, Qt.AlignCenter, self.table.horizontalHeaderItem(col).text())
                x_offset += col_widths[col]
            current_y += row_height

            # طباعة محتوى الجدول
            painter.setFont(table_font)
            painter.setBrush(QBrush(QColor(255, 255, 255))) # خلفية بيضاء للصفوف

            for row in range(self.table.rowCount()):
                x_offset = printable_rect.x()
                # التحقق من تجاوز الصفحة قبل طباعة الصف
                if current_y + row_height > printable_rect.bottom() - footer_font.pointSize() * 3:
                    printer.newPage()
                    current_y = printable_rect.y() + title_font.pointSize() * 2 # إعادة تعيين Y بعد العنوان
                    # إعادة طباعة رؤوس الأعمدة في الصفحة الجديدة
                    x_offset_new_page = printable_rect.x()
                    painter.setFont(header_font)
                    painter.setBrush(QBrush(QColor(220, 220, 220)))
                    for col in range(self.table.columnCount()):
                        rect = QRectF(x_offset_new_page, current_y, col_widths[col], row_height)
                        painter.drawRect(rect)
                        painter.drawText(rect, Qt.AlignCenter, self.table.horizontalHeaderItem(col).text())
                        x_offset_new_page += col_widths[col]
                    current_y += row_height
                    painter.setFont(table_font)
                    painter.setBrush(QBrush(QColor(255, 255, 255)))

                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    text = item.text() if item else ""
                    rect = QRectF(x_offset, current_y, col_widths[col], row_height)
                    painter.drawRect(rect)
                    painter.drawText(rect, Qt.AlignCenter, text)
                    x_offset += col_widths[col]
                current_y += row_height

            # طباعة التذييل
            painter.setFont(footer_font)
            painter.setPen(QPen(QColor(100, 100, 100)))
            footer_y = printable_rect.bottom() - footer_font.pointSize() * 1.5
            painter.drawText(printable_rect, Qt.AlignHCenter | Qt.AlignBottom, TEXTS["print_footer"][self.lang])

            painter.end()

# ----- Dashboard -----
class Dashboard(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings = QSettings(ORG_NAME, APP_NAME)
        self.lang = self.settings.value("language", "العربية")
        self.setup_ui()
        self.set_language(self.lang) # تحديث اللغة والملخص عند التهيئة

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # 🔹 الملخص أعلى الصفحة
        self.summary_frame = QFrame()
        self.summary_frame.setFrameShape(QFrame.StyledPanel)
        self.summary_frame.setFrameShadow(QFrame.Raised)
        self.summary_frame.setStyleSheet("""
            QFrame {
                background-color: #e9f5ff; /* لون خلفية فاتح للملخص */
                border: 1px solid #a0d9ff;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                font-size: 15pt;
                font-weight: bold;
                color: #0056b3; /* لون أزرق داكن للنصوص */
            }
        """)
        self.summary_layout = QHBoxLayout(self.summary_frame)
        self.summary_layout.setSpacing(20)
        self.summary_labels = {
            "balance": QLabel(),
            "deposit": QLabel(),
            "expense": QLabel(),
            "net": QLabel()
        }
        for lbl in self.summary_labels.values():
            lbl.setAlignment(Qt.AlignCenter)
            self.summary_layout.addWidget(lbl)
        layout.addWidget(self.summary_frame)

        # 🔹 التبويبات
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Arial", 12, QFont.Bold))
        self.tabs.setStyleSheet("""
            QTabWidget::pane { /* The tab widget frame */
                border: 1px solid #ced4da;
                border-top: none;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
            QTabBar::tab {
                background: #e9ecef; /* لون خلفية التبويب غير النشط */
                border: 1px solid #ced4da;
                border-bottom-color: #ced4da; /* same as pane color */
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 15px;
                margin-right: 2px;
                color: #495057;
            }
            QTabBar::tab:selected {
                background: #007bff; /* لون خلفية التبويب النشط */
                color: white;
                border-color: #007bff;
                border-bottom-color: #007bff; /* same as pane color */
            }
            QTabBar::tab:hover {
                background: #d0d9e0;
            }
        """)
        self.tab_pages = [
            TabWidget(TEXTS["main_tab"]["العربية"], self.main_window),
            TabWidget(TEXTS["deposit_tab"]["العربية"], self.main_window),
            TabWidget(TEXTS["expense_tab"]["العربية"], self.main_window)
        ]
        self.tabs.addTab(self.tab_pages[0], TEXTS["main_tab"]["العربية"])
        self.tabs.addTab(self.tab_pages[1], TEXTS["deposit_tab"]["العربية"])
        self.tabs.addTab(self.tab_pages[2], TEXTS["expense_tab"]["العربية"])
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.tabs)

        # 🔹 اختيار اللغة
        lang_layout = QHBoxLayout()
        lang_layout.addStretch()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["العربية", "English"])
        self.lang_combo.setFixedWidth(150)
        self.lang_combo.setFont(QFont("Arial", 12))
        self.lang_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px;
                background-color: #ffffff;
                selection-background-color: #007bff;
                selection-color: white;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #ced4da;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down.png); /* يمكنك إضافة أيقونة سهم */
                width: 12px;
                height: 12px;
            }
        """)
        self.lang_combo.currentTextChanged.connect(self.set_language)
        self.lang_combo.setCurrentText(self.lang) # تعيين اللغة المحفوظة
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)

    def set_language(self, lang):
        self.lang = lang
        self.settings.setValue("language", lang) # حفظ اللغة
        # تحديث اتجاه الواجهة
        if lang == "العربية":
            self.setLayoutDirection(Qt.RightToLeft)
            self.tabs.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)
            self.tabs.setLayoutDirection(Qt.LeftToRight)

        # تحديث نصوص التبويبات
        self.tabs.setTabText(0, TEXTS["main_tab"][lang])
        self.tabs.setTabText(1, TEXTS["deposit_tab"][lang])
        self.tabs.setTabText(2, TEXTS["expense_tab"][lang])

        # تحديث لغة كل تبويب فرعي
        for tab_page in self.tab_pages:
            tab_page.set_language(lang)
        
        self.update_dashboard() # تحديث الملخص بعد تغيير اللغة
        self.main_window.setWindowTitle(TEXTS["app_title"][lang]) # تحديث عنوان النافذة الرئيسية

    def update_dashboard(self):
        global df
        total_balance = df["الرصيد الحالي"].iloc[-1] if not df.empty else 0
        deposits = df[df["النوع"].str.lower().isin(["رصيد", "deposit"])]["المبلغ"].sum()
        expenses = df[df["النوع"].str.lower().isin(["مصروف", "expense"])]["المبلغ"].sum()
        net = deposits - expenses

        # تلوين الرصيد الكلي بناءً على قيمته
        balance_color = "#28a745" if total_balance >= 0 else "#dc3545" # أخضر أو أحمر
        net_color = "#28a745" if net >= 0 else "#dc3545"

        self.summary_labels["balance"].setText(f"{TEXTS['balance_summary'][self.lang]} <span style='color: {balance_color};'>{total_balance:,.2f}</span>")
        self.summary_labels["deposit"].setText(f"{TEXTS['deposit_summary'][self.lang]} <span style='color: #28a745;'>{deposits:,.2f}</span>")
        self.summary_labels["expense"].setText(f"{TEXTS['expense_summary'][self.lang]} <span style='color: #dc3545;'>{expenses:,.2f}</span>")
        self.summary_labels["net"].setText(f"{TEXTS['net_summary'][self.lang]} <span style='color: {net_color};'>{net:,.2f}</span>")

        # تحديث بيانات كل تبويب (الجداول والرسوم البيانية)
        for tab in self.tab_pages:
            tab.load_data()

# ----- MainWindow -----
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings(ORG_NAME, APP_NAME)
        self.setWindowTitle(TEXTS["app_title"][self.settings.value("language", "العربية")])
        self.setWindowIcon(QIcon("icons/app_icon.png")) # يمكنك إضافة أيقونة للتطبيق

        self.stack = QStackedWidget()
        layout = QVBoxLayout(self)
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.login_page = LoginWidget(self)
        self.dashboard_page = Dashboard(self)

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.dashboard_page)

        # استعادة حالة النافذة
        self.restore_geometry()

    def update_dashboard(self):
        self.dashboard_page.update_dashboard()
        self.setWindowTitle(TEXTS["app_title"][self.dashboard_page.lang]) # تحديث عنوان النافذة

    def closeEvent(self, event):
        """تأكيد الخروج من التطبيق وحفظ حالة النافذة."""
        confirm = QMessageBox.question(self, TEXTS["confirm_title"][self.dashboard_page.lang],
                                       TEXTS["exit_confirm"][self.dashboard_page.lang],
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.save_geometry()
            event.accept()
        else:
            event.ignore()

    def save_geometry(self):
        """حفظ حجم وموقع النافذة."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

    def restore_geometry(self):
        """استعادة حجم وموقع النافذة."""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.showMaximized() # إذا لم تكن هناك إعدادات محفوظة، افتحها مكبرة

# ----- تشغيل التطبيق -----
if __name__ == "__main__":
    # إنشاء مجلد الأصوات إذا لم يكن موجودًا
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
    # إنشاء مجلد الأيقونات إذا لم يكن موجودًا
    if not os.path.exists("icons"):
        os.makedirs("icons")
    
    # تحميل البيانات الأولية
    load_initial_data()

    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 12))
    
    # تطبيق نمط عام على التطبيق
    app.setStyleSheet("""
        QWidget {
            background-color: #f0f2f5; /* لون خلفية فاتح للتطبيق */
            color: #343a40; /* لون نص افتراضي */
        }
        QPushButton {
            border: none;
            border-radius: 5px;
            padding: 8px 15px;
            font-size: 11pt;
            font-weight: bold;
            transition: background-color 0.3s ease; /* تأثير انتقال للألوان */
        }
        QPushButton:hover {
            opacity: 0.9;
        }
        QMessageBox {
            background-color: #ffffff;
            font-size: 12pt;
        }
        QMessageBox QPushButton {
            background-color: #007bff;
            color: white;
            border-radius: 5px;
            padding: 5px 10px;
        }
        QMessageBox QPushButton:hover {
            background-color: #0056b3;
        }
        QComboBox {
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 5px;
            background-color: #ffffff;
            selection-background-color: #007bff;
            selection-color: white;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: #ced4da;
            border-left-style: solid;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
        }
        QComboBox::down-arrow {
            image: url(icons/arrow_down.png); /* يمكنك إضافة أيقونة سهم */
            width: 12px;
            height: 12px;
        }
    """)

    window = MainWindow()
    window.show() # استخدام show() بدلاً من showMaximized() للسماح باستعادة الحالة
    sys.exit(app.exec_())
