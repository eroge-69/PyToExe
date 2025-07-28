import os
import sys
from datetime import datetime

from PyQt5.QtGui import QFont, QTextCursor, QTextDocument, QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget,
                             QTableWidget, QTableWidgetItem,
                             QCheckBox,
                             QTextEdit, QDialog,
                             QSpinBox, QHeaderView, QCompleter,
                             QFrame, QScrollArea, QSizePolicy, QFileDialog)
from PyQt5.QtCore import QStringListModel
from database import DatabaseHandler

from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QFormLayout,
                             QLabel, QComboBox, QLineEdit, QDateEdit,
                             QPushButton, QHBoxLayout, QMessageBox, QGridLayout)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class ModernCard(QFrame):
    """Modern card widget with shadow effect"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)


class ModernGroupBox(QGroupBox):
    """Modern styled group box"""

    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 20px;
                color: #2c3e50;
                border: 2px solid #e8f4f8;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 20px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 5px 15px;
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
        """)


class ModernButton(QPushButton):
    """Modern styled button with hover effects"""

    def __init__(self, text="", button_type="primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setMinimumHeight(40)
        self.setMinimumWidth(120)
        self.setCursor(Qt.PointingHandCursor)

        if button_type == "primary":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3498db, stop:1 #2980b9);
                    border: none;
                    color: white;
                    padding: 12px 24px;
                    font-size: 16px;
                    font-weight: 600;
                    border-radius: 8px;
                    text-align: center;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3cb0fd, stop:1 #3498db);
                    transform: translateY(-2px);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2980b9, stop:1 #21618c);
                }
                QPushButton:disabled {
                    background-color: #bdc3c7;
                    color: #7f8c8d;
                }
            """)
        elif button_type == "success":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #27ae60, stop:1 #229954);
                    border: none;
                    color: white;
                    padding: 12px 24px;
                    font-size: 16px;
                    font-weight: 600;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2ecc71, stop:1 #27ae60);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #229954, stop:1 #1e8449);
                }
            """)
        elif button_type == "danger":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e74c3c, stop:1 #c0392b);
                    border: none;
                    color: white;
                    padding: 12px 24px;
                    font-size: 16px;
                    font-weight: 600;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ec7063, stop:1 #e74c3c);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #c0392b, stop:1 #a93226);
                }
            """)
        elif button_type == "secondary":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #ecf0f1;
                    border: 2px solid #bdc3c7;
                    color: #2c3e50;
                    padding: 12px 24px;
                    font-size: 16px;
                    font-weight: 600;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #d5dbdb;
                    border-color: #95a5a6;
                }
                QPushButton:pressed {
                    background-color: #bdc3c7;
                }
            """)


class ModernLineEdit(QLineEdit):
    """Modern styled line edit with floating label effect"""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(45)
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e8f4f8;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 16px;
                background-color: white;
                selection-background-color: #3498db;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #f8fbff;
            }
            QLineEdit:hover {
                border-color: #5dade2;
            }
        """)


class ModernComboBox(QComboBox):
    """Modern styled combo box"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(45)
        self.setStyleSheet("""
            QComboBox {
                border: 2px solid #e8f4f8;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 16px;
                background-color: white;
                selection-background-color: #3498db;
            }
            QComboBox:focus {
                border-color: #3498db;
                background-color: #f8fbff;
            }
            QComboBox:hover {
                border-color: #5dade2;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 8px;
                selection-background-color: #3498db;
                selection-color: white;
            }
        """)


class ModernTextEdit(QTextEdit):
    """Modern styled text edit"""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e8f4f8;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 16px;
                background-color: white;
                selection-background-color: #3498db;
            }
            QTextEdit:focus {
                border-color: #3498db;
                background-color: #f8fbff;
            }
            QTextEdit:hover {
                border-color: #5dade2;
            }
        """)


class ModernDateEdit(QDateEdit):
    """Modern styled date edit"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(45)
        self.setCalendarPopup(True)
        self.setStyleSheet("""
            QDateEdit {
                border: 2px solid #e8f4f8;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 16px;
                background-color: white;
            }
            QDateEdit:focus {
                border-color: #3498db;
                background-color: #f8fbff;
            }
            QDateEdit:hover {
                border-color: #5dade2;
            }
            QDateEdit::drop-down {
                border: none;
                width: 30px;
            }
            QDateEdit::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)


class ModernSpinBox(QSpinBox):
    """Modern styled spin box"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(45)
        self.setStyleSheet("""
            QSpinBox {
                border: 2px solid #e8f4f8;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 16px;
                background-color: white;
            }
            QSpinBox:focus {
                border-color: #3498db;
                background-color: #f8fbff;
            }
            QSpinBox:hover {
                border-color: #5dade2;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                border: none;
                width: 20px;
                border-radius: 4px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #e8f4f8;
            }
        """)


class ModernCheckBox(QCheckBox):
    """Modern styled checkbox"""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QCheckBox {
                font-size: 16px;
                font-weight: 500;
                color: #2c3e50;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:hover {
                border-color: #3498db;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
                image: url(check.png);
            }
            QCheckBox::indicator:checked:hover {
                background-color: #2980b9;
            }
        """)


class ModernTable(QTableWidget):
    """Modern styled table widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.setStyleSheet("""
            QTableWidget {
                border: 2px solid #e8f4f8;
                border-radius: 10px;
                background-color: white;
                gridline-color: #ecf0f1;
                font-size: 15px;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                padding: 15px 8px;
                border: none;
                font-weight: bold;
                font-size: 16px;
            }
            QHeaderView::section:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QTableWidget::alternate-row-color {
                background-color: #f8f9fa;
            }
        """)


class OPDCareApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseHandler()
        self.initUI()
        self.apply_styles()

    def initUI(self):
        self.setWindowTitle("OPDCare 2.0")
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowIcon(QIcon('favicon.ico'))

        # Create main widget with modern styling
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header section
        header = self.create_header()
        main_layout.addWidget(header)

        # Create tab widget for different modules
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)

        # Add tabs with modern styling
        self.patient_tab = PatientTab(self.db)
        self.prescription_tab = PrescriptionTab(self.db)
        self.fitness_cert_tab = FitnessCertificateTab(self.db)
        self.medical_cert_tab = MedicalCertificateTab(self.db)
        self.billing_tab = BillingTab(self.db)
        self.master_tab = MasterTab(self.db)

        self.tabs.addTab(self.patient_tab, "👤 Patient")
        self.tabs.addTab(self.prescription_tab, "💊 Prescription")
        self.tabs.addTab(self.fitness_cert_tab, "🏃 Fitness Certificate")
        self.tabs.addTab(self.medical_cert_tab, "📋 Medical Certificate")
        self.tabs.addTab(self.billing_tab, "💰 Billing")
        self.tabs.addTab(self.master_tab, "⚙️ Master")

        main_layout.addWidget(self.tabs)

        # Status bar
        self.statusBar().showMessage("Ready - Welcome to OPDCare 2.0 | Made by Arham IT solution")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #34495e, stop:1 #2c3e50);
                color: white;
                border: none;
                padding: 5px;
                font-weight: 500;
            }
        """)

    def create_header(self):
        """Create modern header with gradient background"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:0.5 #2980b9, stop:1 #1abc9c);
                border: none;
            }
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 15, 30, 15)

        # Logo/Title section
        title_label = QLabel("OPDCare 2.0")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                background: transparent;
            }
        """)

        subtitle_label = QLabel("Modern Medical Management System")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 16px;
                font-weight: 500;
                background: transparent;
            }
        """)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        layout.addLayout(title_layout)
        layout.addStretch()

        # Current date/time
        current_date = QDate.currentDate().toString("dddd, MMMM dd, yyyy")
        date_label = QLabel(current_date)
        date_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: 500;
                background: transparent;
            }
        """)

        layout.addWidget(date_label)

        return header

    def apply_styles(self):
        """Apply modern application-wide styles"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }

            QTabWidget::pane {
                border: none;
                background: transparent;
                top: -1px;
            }

            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ecf0f1, stop:1 #d5dbdb);
                border: 2px solid #bdc3c7;
                border-bottom: none;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 15px 25px;
                margin-right: 3px;
                font-size: 16px;
                font-weight: 600;
                color: #2c3e50;
                min-width: 120px;
            }

            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 white, stop:1 #f8f9fa);
                border-color: #3498db;
                border-bottom: 3px solid #3498db;
                color: #2980b9;
            }

            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f1c40f, stop:1 #f39c12);
                color: white;
            }

            QScrollArea {
                border: none;
                background: transparent;
            }

            QScrollBar:vertical {
                background: #ecf0f1;
                width: 12px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 6px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background: #95a5a6;
            }

            QMessageBox {
                background-color: white;
                border-radius: 10px;
            }

            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 16px;
            }
        """)


class PatientTab(QWidget):
    def __init__(self, db_handler):
        super().__init__()
        self.db = db_handler
        self.initUI()

    def initUI(self):
        # Main scroll area with improved styling
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                width: 10px;
                background: #f0f0f0;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 4px;
            }
        """)

        main_widget = QWidget()
        scroll.setWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        # Patient form in modern card with enhanced styling
        card = ModernCard()
        card.setMinimumWidth(600)  # Ensure reasonable minimum width
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 25)

        form_group = ModernGroupBox("👨‍⚕️ Patient Information")
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # Enhanced form inputs with better placeholders and validation
        self.name_input = ModernLineEdit()
        self.name_input.setPlaceholderText("Full name")
        self.name_input.setToolTip("Enter patient's full name")

        self.age_input = ModernLineEdit()
        self.age_input.setPlaceholderText("Years")
        self.age_input.setValidator(QIntValidator(0, 120))

        self.weight_input = ModernLineEdit()
        self.weight_input.setPlaceholderText("Kilograms")
        self.weight_input.setValidator(QDoubleValidator(0, 300, 2))

        self.gender_combo = ModernComboBox()
        self.gender_combo.addItems(["Male", "Female", "Other"])
        self.gender_combo.setCurrentIndex(0)

        self.mobile_input = ModernLineEdit()
        self.mobile_input.setPlaceholderText("With country code")
        self.mobile_input.setInputMask("+99 99999 99999;_")

        self.address_input = ModernTextEdit()
        self.address_input.setPlaceholderText("Full address with PIN code")
        self.address_input.setMaximumHeight(100)

        # Enhanced date controls
        self.enable_reminder = ModernCheckBox("Set Follow-up Reminder")
        self.enable_reminder.setChecked(False)

        self.visit_date = ModernDateEdit()
        self.visit_date.setDate(QDate.currentDate())
        self.visit_date.setCalendarPopup(True)
        self.visit_date.setDisplayFormat("dd MMM yyyy")

        self.reminder_date = ModernDateEdit()
        self.reminder_date.setDate(QDate.currentDate().addDays(7))
        self.reminder_date.setCalendarPopup(True)
        self.reminder_date.setDisplayFormat("dd MMM yyyy")
        self.reminder_date.setEnabled(True)

        self.reminder_desc = ModernTextEdit()
        self.reminder_desc.setPlaceholderText("Follow-up reason or notes")
        self.reminder_desc.setMaximumHeight(80)
        self.reminder_desc.setEnabled(True)

        # Add form rows with improved organization
        form_layout.addRow(self.create_label("👤 Full Name:"), self.name_input)
        form_layout.addRow(self.create_label("📊 Basic Information:"), self.create_horizontal_group([
            (self.create_label("🎂 Age:"), self.age_input),
            (self.create_label("⚖️ Weight:"), self.weight_input),
            (self.create_label("⚧ Gender:"), self.gender_combo)
        ]))
        form_layout.addRow(self.create_label("📱 Contact:"), self.mobile_input)
        self.mobile_input.setFixedWidth(300)
        form_layout.addRow(self.create_label("🏠 Address:"), self.address_input)
        form_layout.addRow(self.create_label("📅 Visit Date:"), self.visit_date)
        self.visit_date.setFixedWidth(160)

        form_layout.addRow(self.create_label("🔔 Follow-up:"), self.enable_reminder)
        form_layout.addRow(self.create_label("⏰ Reminder Date:"), self.reminder_date)
        self.reminder_date.setFixedWidth(160)
        form_layout.addRow(self.create_label("📝 Follow-up Notes:"), self.reminder_desc)

        form_group.setLayout(form_layout)
        card_layout.addWidget(form_group)

        # Modern action buttons with better organization
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 10, 0, 0)
        btn_layout.setSpacing(15)

        self.save_btn = ModernButton("💾 Save Patient", "success")
        self.save_btn.setMinimumWidth(150)
        self.view_btn = ModernButton("👥 View Patients", "primary")
        self.view_btn.setMinimumWidth(150)
        self.clear_btn = ModernButton("🗑️ Clear Form", "secondary")
        self.clear_btn.setMinimumWidth(150)

        btn_layout.addStretch(1)
        btn_layout.addWidget(self.view_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.save_btn)

        card_layout.addWidget(btn_container)
        layout.addWidget(card)
        layout.addStretch()

        # Set main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Connect signals
        self.setup_connections()

    def create_label(self, text):
        """Create modern styled label with improved design"""
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: 600;
                color: #34495e;
                padding: 5px 0;
            }
        """)
        label.setAlignment(Qt.AlignVCenter)
        return label

    def create_horizontal_group(self, widgets):
        """Create a horizontal layout group for related fields"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        for widget in widgets:
            if isinstance(widget, tuple):
                for sub_widget in widget:
                    layout.addWidget(sub_widget)
            else:
                layout.addWidget(widget)

        return container

    def setup_connections(self):
        self.enable_reminder.stateChanged.connect(self.toggle_reminder_fields)
        self.save_btn.clicked.connect(self.save_patient)
        self.view_btn.clicked.connect(self.show_patients_modal)
        self.clear_btn.clicked.connect(self.clear_form)

    def toggle_reminder_fields(self, state):
        self.reminder_date.setVisible(state == Qt.Checked)
        self.reminder_desc.setVisible(state == Qt.Checked)

    def save_patient(self):
        # Validate inputs
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Patient name is required")
            return

        try:
            patient_data = {
                'name': self.name_input.text().strip(),
                'age': int(self.age_input.text()) if self.age_input.text() else None,
                'weight': float(self.weight_input.text()) if self.weight_input.text() else None,
                'gender': self.gender_combo.currentText(),
                'mobile': self.mobile_input.text().strip(),
                'address': self.address_input.toPlainText().strip(),
                'enable_reminder': self.enable_reminder.isChecked(),
                'reminder_date': self.reminder_date.date().toString(
                    "yyyy-MM-dd") if self.enable_reminder.isChecked() else None,
                'reminder_description': self.reminder_desc.toPlainText().strip() if self.enable_reminder.isChecked() else None,
                'visit_date': self.visit_date.date().toString("yyyy-MM-dd")
            }

            patient_id = self.db.add_patient(patient_data)

            # Success message with modern styling
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Success")
            msg.setText(f"Patient saved successfully!\nPatient ID: {patient_id}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

            self.clear_form()
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", "Please check your input values")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save patient: {str(e)}")

    def show_patients_modal(self, search_term=None):
        self.patients_modal = PatientsModal(self.db, search_term)
        self.patients_modal.exec_()

    def clear_form(self):
        self.name_input.clear()
        self.age_input.clear()
        self.weight_input.clear()
        self.gender_combo.setCurrentIndex(0)
        self.mobile_input.clear()
        self.address_input.clear()
        self.enable_reminder.setChecked(False)
        self.visit_date.setDate(QDate.currentDate())
        self.reminder_date.setDate(QDate.currentDate())
        self.reminder_desc.clear()


class PatientsModal(QDialog):
    def __init__(self, db_handler, search_term=None):
        super().__init__()
        self.db = db_handler
        self.search_term = search_term
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Patient Management")
        self.setGeometry(100, 50, 1800, 1000)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Search section in modern card
        search_card = ModernCard()
        search_layout = QVBoxLayout(search_card)
        search_layout.setContentsMargins(20, 20, 20, 20)

        search_group = ModernGroupBox("🔍 Search Patients")
        search_form = QHBoxLayout()

        self.patient_search = ModernLineEdit("Search by name, mobile, or ID...")
        if self.search_term:
            self.patient_search.setText(self.search_term)

        search_btn = ModernButton("🔍 Search", "primary")

        search_form.addWidget(self.patient_search)
        search_form.addWidget(search_btn)
        search_group.setLayout(search_form)
        search_layout.addWidget(search_group)

        # Patients table in modern style
        table_card = ModernCard()
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(20, 20, 20, 20)

        self.patients_table = ModernTable()
        self.patients_table.setColumnCount(8)
        self.patients_table.setHorizontalHeaderLabels([
            "ID", "Name", "Age", "Gender", "Mobile", "Address", "Visit Date", "Actions"
        ])

        self.load_patients()
        table_layout.addWidget(self.patients_table)

        layout.addWidget(search_card)
        layout.addWidget(table_card)
        self.setLayout(layout)

        search_btn.clicked.connect(self.load_patients)

    def load_patients(self):
        search_term = self.patient_search.text()
        if search_term:
            patients = self.db.search_patients(search_term)
        else:
            patients = self.db.get_all_patients()

        self.patients_table.setRowCount(len(patients))

        for row, patient in enumerate(patients):
            self.patients_table.setItem(row, 0, QTableWidgetItem(str(patient[0])))
            self.patients_table.setItem(row, 1, QTableWidgetItem(patient[1]))
            self.patients_table.setItem(row, 2, QTableWidgetItem(str(patient[2] if patient[2] else "")))
            self.patients_table.setItem(row, 3, QTableWidgetItem(patient[4] if patient[4] else ""))
            self.patients_table.setItem(row, 4, QTableWidgetItem(patient[5] if patient[5] else ""))
            self.patients_table.setItem(row, 5, QTableWidgetItem(patient[6] if patient[6] else ""))
            self.patients_table.setItem(row, 6, QTableWidgetItem(patient[10] if patient[10] else ""))

            # Modern action buttons
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(5, 5, 5, 5)
            btn_layout.setSpacing(5)

            prescription_btn = ModernButton("💊", "primary")
            prescription_btn.setMinimumWidth(60)
            prescription_btn.clicked.connect(lambda _, p=patient: self.open_prescription(p))

            edit_btn = ModernButton("✏️", "secondary")
            edit_btn.setMinimumWidth(60)
            edit_btn.clicked.connect(lambda _, p=patient: self.edit_patient(p))

            delete_btn = ModernButton("🗑️", "danger")
            delete_btn.setMinimumWidth(60)
            delete_btn.clicked.connect(lambda _, p=patient: self.delete_patient(p))

            btn_layout.addWidget(prescription_btn)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_widget.setLayout(btn_layout)

            self.patients_table.setCellWidget(row, 7, btn_widget)
            self.patients_table.setRowHeight(row, 60)



    def open_prescription(self, patient):
        """Show prescription creation dialog with modern styling"""
        try:
            self.prescription_dialog = QDialog(self)
            self.prescription_dialog.setWindowTitle(f"💊 Prescription for {patient[1]}")
            self.prescription_dialog.setMinimumSize(1000, 700)
            self.prescription_dialog.setStyleSheet("""
                QDialog {
                    background-color: #f8f9fa;
                }
            """)

            layout = QVBoxLayout()
            layout.setContentsMargins(25, 25, 25, 25)
            layout.setSpacing(20)

            # Patient info card
            patient_card = ModernCard()
            patient_layout = QVBoxLayout(patient_card)
            patient_layout.setContentsMargins(20, 20, 20, 20)

            patient_group = ModernGroupBox("👤 Patient Information")
            patient_form = QFormLayout()
            patient_form.addRow("Patient ID:", QLabel(str(patient[0])))
            patient_form.addRow("Name:", QLabel(patient[1]))
            patient_form.addRow("Age:", QLabel(str(patient[2]) if patient[2] else "N/A"))
            patient_form.addRow("Gender:", QLabel(patient[4] if patient[4] else "N/A"))
            patient_form.addRow("Mobile:", QLabel(patient[5] if patient[5] else "N/A"))
            patient_group.setLayout(patient_form)
            patient_layout.addWidget(patient_group)

            # Medicines section card
            med_card = ModernCard()
            med_layout = QVBoxLayout(med_card)
            med_layout.setContentsMargins(20, 20, 20, 20)

            rx_group = ModernGroupBox("💊 Prescription Medicines")
            rx_layout = QVBoxLayout()

            self.med_table = ModernTable()
            self.med_table.setColumnCount(6)
            self.med_table.setHorizontalHeaderLabels(["Type", "Medicine", "Dosage", "Days", "Qty", ""])

            add_btn = ModernButton("➕ Add Medicine", "success")
            add_btn.clicked.connect(self.add_medicine_row)

            rx_layout.addWidget(add_btn)
            rx_layout.addWidget(self.med_table)
            rx_group.setLayout(rx_layout)
            med_layout.addWidget(rx_group)

            # Action buttons
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(15)

            save_btn = ModernButton("💾 Save Prescription", "success")
            cancel_btn = ModernButton("❌ Cancel", "secondary")

            save_btn.clicked.connect(lambda: self.save_prescription(patient[0]))
            cancel_btn.clicked.connect(self.prescription_dialog.reject)

            btn_layout.addWidget(save_btn)
            btn_layout.addStretch()
            btn_layout.addWidget(cancel_btn)

            layout.addWidget(patient_card)
            layout.addWidget(med_card)
            layout.addLayout(btn_layout)
            self.prescription_dialog.setLayout(layout)

            # Add initial empty row
            self.add_medicine_row()

            self.prescription_dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open prescription dialog: {str(e)}")

    def add_medicine_row(self):
        """Add a new row to the medicine table"""
        row = self.med_table.rowCount()
        self.med_table.insertRow(row)

        # Medicine type combo
        type_combo = ModernComboBox()
        type_combo.addItems(["TAB", "SYP", "CAP", "INJ", "DPS", "OINT"])

        # Medicine name
        name_combo = ModernComboBox()
        self.update_medicine_names(name_combo, type_combo.currentText())
        type_combo.currentTextChanged.connect(lambda t: self.update_medicine_names(name_combo, t))

        # Dosage combo
        dose_combo = ModernComboBox()
        dose_combo.addItems(["1-0-0", "1-0-1", "0-0-1", "1-1-1", "SOS", "2-0-0"])

        # Days and Quantity
        days_spin = ModernSpinBox()
        days_spin.setRange(1, 30)
        days_spin.setValue(3)

        qty_spin = ModernSpinBox()
        qty_spin.setRange(1, 100)
        qty_spin.setValue(10)

        # Remove button
        remove_btn = ModernButton("❌", "danger")
        remove_btn.setMaximumWidth(40)
        remove_btn.clicked.connect(lambda: self.med_table.removeRow(row))

        # Add widgets to table
        self.med_table.setCellWidget(row, 0, type_combo)
        self.med_table.setCellWidget(row, 1, name_combo)
        self.med_table.setCellWidget(row, 2, dose_combo)
        self.med_table.setCellWidget(row, 3, days_spin)
        self.med_table.setCellWidget(row, 4, qty_spin)
        self.med_table.setCellWidget(row, 5, remove_btn)

    def update_medicine_names(self, name_combo, med_type):
        """Update medicine names based on selected type"""
        medicines = self.db.get_medicines_by_type(med_type)
        name_combo.clear()
        name_combo.addItems([m[2] for m in medicines])

    def save_prescription(self, patient_id):
        """Save prescription to database"""
        if self.med_table.rowCount() == 0:
            QMessageBox.warning(self, "Error", "Please add at least one medicine")
            return

        try:
            cursor = self.db.conn.cursor()
            cursor.execute("INSERT INTO Prescriptions (patient_id, date) VALUES (?, date('now'))",
                           (patient_id,))
            prescription_id = cursor.lastrowid

            for row in range(self.med_table.rowCount()):
                med_type = self.med_table.cellWidget(row, 0).currentText()
                med_name = self.med_table.cellWidget(row, 1).currentText()
                dose = self.med_table.cellWidget(row, 2).currentText()
                days = self.med_table.cellWidget(row, 3).value()
                qty = self.med_table.cellWidget(row, 4).value()

                cursor.execute('''
                    INSERT INTO Prescription_Medicines 
                    (prescription_id, medicine_type, medicine_name, dose, days, quantity)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (prescription_id, med_type, med_name, dose, days, qty))

            self.db.conn.commit()
            QMessageBox.information(self.prescription_dialog, "Success", "Prescription saved successfully!")
            self.prescription_dialog.accept()
        except Exception as e:
            QMessageBox.critical(self.prescription_dialog, "Error", f"Failed to save prescription: {str(e)}")

    def edit_patient(self, patient):
        edit_dialog = EditPatientDialog(self.db, patient)
        if edit_dialog.exec_():
            self.load_patients()

    def delete_patient(self, patient):
        """Delete patient with confirmation"""
        try:
            # Confirm deletion
            reply = QMessageBox.question(
                self,
                'Confirm Deletion',
                f'Are you sure you want to delete patient:\n\n{patient[1]} (ID: {patient[0]})?\n\nThis action cannot be undone!',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # First delete related records to maintain referential integrity
                cursor = self.db.conn.cursor()

                # Delete prescriptions and their medicines
                cursor.execute(
                    "DELETE FROM Prescription_Medicines WHERE prescription_id IN (SELECT prescription_id FROM Prescriptions WHERE patient_id = ?)",
                    (patient[0],))
                cursor.execute("DELETE FROM Prescriptions WHERE patient_id = ?", (patient[0],))

                # Delete certificates
                cursor.execute("DELETE FROM Fitness_Certificates WHERE patient_id = ?", (patient[0],))
                cursor.execute("DELETE FROM Medical_Certificates WHERE patient_id = ?", (patient[0],))

                # Finally delete the patient
                cursor.execute("DELETE FROM Patients WHERE patient_id = ?", (patient[0],))

                self.db.conn.commit()

                # Show success message
                QMessageBox.information(
                    self,
                    'Success',
                    f'Patient {patient[1]} (ID: {patient[0]}) has been deleted successfully.'
                )

                # Refresh the patient list
                self.load_patients()

        except Exception as e:
            QMessageBox.critical(
                self,
                'Error',
                f'Failed to delete patient:\n\n{str(e)}'
            )


class EditPatientDialog(QDialog):
    def __init__(self, db_handler, patient_data):
        super().__init__()
        self.db = db_handler
        self.patient_data = patient_data
        self.patient_id = patient_data[0]
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"✏️ Edit Patient - {self.patient_data[1]}")
        self.setGeometry(200, 200, 600, 700)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Form card
        card = ModernCard()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 25, 25, 25)

        form_group = ModernGroupBox("Patient Information")
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)

        self.name_input = ModernLineEdit()
        self.name_input.setText(self.patient_data[1])
        self.age_input = ModernLineEdit()
        self.age_input.setText(str(self.patient_data[2]) if self.patient_data[2] else "")
        self.weight_input = ModernLineEdit()
        self.weight_input.setText(str(self.patient_data[3]) if self.patient_data[3] else "")

        self.gender_combo = ModernComboBox()
        self.gender_combo.addItems(["Male", "Female", "Other"])
        if self.patient_data[4]:
            index = self.gender_combo.findText(self.patient_data[4])
            if index >= 0:
                self.gender_combo.setCurrentIndex(index)

        self.mobile_input = ModernLineEdit()
        self.mobile_input.setText(self.patient_data[5] if self.patient_data[5] else "")
        self.address_input = ModernTextEdit()
        self.address_input.setPlainText(self.patient_data[6] if self.patient_data[6] else "")
        self.address_input.setMaximumHeight(100)

        self.enable_reminder = ModernCheckBox("Enable Reminder")
        self.enable_reminder.setChecked(bool(self.patient_data[7]))
        self.enable_reminder.stateChanged.connect(self.toggle_reminder_fields)

        visit_date = QDate.fromString(self.patient_data[10], "yyyy-MM-dd") if self.patient_data[
            10] else QDate.currentDate()
        self.visit_date = ModernDateEdit()
        self.visit_date.setDate(visit_date)

        reminder_date = QDate.fromString(self.patient_data[8], "yyyy-MM-dd") if self.patient_data[
            8] else QDate.currentDate()
        self.reminder_date = ModernDateEdit()
        self.reminder_date.setDate(reminder_date)

        self.reminder_desc = ModernTextEdit()
        self.reminder_desc.setPlainText(self.patient_data[9] if self.patient_data[9] else "")
        self.reminder_desc.setMaximumHeight(80)

        # Set visibility based on current reminder status
        self.reminder_date.setVisible(self.enable_reminder.isChecked())
        self.reminder_desc.setVisible(self.enable_reminder.isChecked())

        form_layout.addRow("👤 Name:", self.name_input)
        form_layout.addRow("🎂 Age:", self.age_input)
        form_layout.addRow("⚖️ Weight:", self.weight_input)
        form_layout.addRow("⚧ Gender:", self.gender_combo)
        form_layout.addRow("📱 Mobile:", self.mobile_input)
        form_layout.addRow("🏠 Address:", self.address_input)
        form_layout.addRow("📅 Visit Date:", self.visit_date)
        form_layout.addRow("", self.enable_reminder)
        form_layout.addRow("⏰ Reminder Date:", self.reminder_date)
        form_layout.addRow("📝 Description:", self.reminder_desc)

        form_group.setLayout(form_layout)
        card_layout.addWidget(form_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        save_btn = ModernButton("💾 Save Changes", "success")
        save_btn.clicked.connect(self.save_patient)
        cancel_btn = ModernButton("❌ Cancel", "secondary")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)

        layout.addWidget(card)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def toggle_reminder_fields(self, state):
        self.reminder_date.setVisible(state == Qt.Checked)
        self.reminder_desc.setVisible(state == Qt.Checked)

    def save_patient(self):
        try:
            patient_data = {
                'name': self.name_input.text(),
                'age': int(self.age_input.text()) if self.age_input.text() else None,
                'weight': float(self.weight_input.text()) if self.weight_input.text() else None,
                'gender': self.gender_combo.currentText(),
                'mobile': self.mobile_input.text(),
                'address': self.address_input.toPlainText(),
                'enable_reminder': self.enable_reminder.isChecked(),
                'reminder_date': self.reminder_date.date().toString(
                    "yyyy-MM-dd") if self.enable_reminder.isChecked() else None,
                'reminder_description': self.reminder_desc.toPlainText() if self.enable_reminder.isChecked() else None,
                'visit_date': self.visit_date.date().toString("yyyy-MM-dd")
            }

            cursor = self.db.conn.cursor()
            cursor.execute('''
            UPDATE Patients SET 
                name = ?, age = ?, weight = ?, gender = ?, mobile = ?,
                address = ?, enable_reminder = ?, reminder_date = ?,
                reminder_description = ?, visit_date = ?
            WHERE patient_id = ?
            ''', (
                patient_data['name'], patient_data['age'], patient_data['weight'],
                patient_data['gender'], patient_data['mobile'], patient_data['address'],
                patient_data['enable_reminder'], patient_data['reminder_date'],
                patient_data['reminder_description'], patient_data['visit_date'],
                self.patient_id
            ))
            self.db.conn.commit()

            QMessageBox.information(self, "Success", "Patient updated successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update patient: {str(e)}")


class PrescriptionTab(QWidget):
    def __init__(self, db_handler):
        super().__init__()
        self.db = db_handler
        self.current_patient_id = None
        self._alive = True
        self.initUI()
        self.apply_styles()

    def initUI(self):
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        main_widget = QWidget()
        scroll.setWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        # Combined Patient Info Card
        combined_card = ModernCard()
        combined_layout = QVBoxLayout(combined_card)
        combined_layout.setContentsMargins(25, 25, 25, 25)
        combined_layout.setSpacing(20)

        # Patient Search Section
        search_group = ModernGroupBox("🔍 Patient Search & Details")
        search_layout = QVBoxLayout()

        # Search row
        search_row = QHBoxLayout()
        search_row.setContentsMargins(0, 0, 0, 0)
        self.patient_search = ModernLineEdit("Start typing patient name or mobile...")
        self.patient_search.setMinimumWidth(300)

        # Create completer
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer_model = QStringListModel()
        self.completer.setModel(self.completer_model)
        self.patient_search.setCompleter(self.completer)

        search_row.addWidget(self.patient_search)
        search_row.addStretch()

        # Details row - compact horizontal layout
        details_row = QHBoxLayout()
        details_row.setContentsMargins(0, 10, 0, 0)
        details_row.setSpacing(15)

        # Name section
        name_label = QLabel("Name:")
        self.patient_name = QLabel("Not selected")
        self.patient_name.setFixedWidth(200)

        # Info fields (age, gender, weight)
        self.patient_age = QLabel("")
        self.patient_gender = QLabel("")
        self.patient_weight = QLabel("")

        # Helper function to create compact info widgets
        def create_info_field(title, value_widget, width=60):
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(5)
            layout.addWidget(QLabel(title))
            value_widget.setFixedWidth(width)
            layout.addWidget(value_widget)
            return container

        details_row.addWidget(name_label)
        details_row.addWidget(self.patient_name)
        details_row.addWidget(create_info_field("Age:", self.patient_age, 50))
        details_row.addWidget(create_info_field("Gender:", self.patient_gender, 60))
        details_row.addWidget(create_info_field("Weight:", self.patient_weight, 60))
        details_row.addStretch()

        # Style all value labels
        for label in [self.patient_name, self.patient_age, self.patient_gender, self.patient_weight]:
            label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #2c3e50;
                    padding: 6px 8px;
                    background-color: #ecf0f1;
                    border-radius: 4px;
                    font-weight: 500;
                }
            """)

        # Reminder Section - integrated into the same card
        reminder_section = QWidget()
        reminder_layout = QHBoxLayout(reminder_section)
        reminder_layout.setContentsMargins(0, 10, 0, 0)
        reminder_layout.setSpacing(15)

        self.enable_reminder = ModernCheckBox("Enable Reminder")
        self.reminder_date = ModernDateEdit()
        self.reminder_date.setDate(QDate.currentDate())
        self.reminder_date.setFixedWidth(120)
        self.reminder_desc = ModernLineEdit("Reminder notes...")
        self.reminder_desc.setMinimumWidth(200)

        # Initially hide reminder fields
        self.reminder_date.setVisible(False)
        self.reminder_desc.setVisible(False)

        reminder_layout.addWidget(self.enable_reminder)
        reminder_layout.addWidget(self.reminder_date)
        reminder_layout.addWidget(self.reminder_desc)
        reminder_layout.addStretch()

        # Add all sections to search group
        search_layout.addLayout(search_row)
        search_layout.addLayout(details_row)
        search_layout.addWidget(reminder_section)
        search_group.setLayout(search_layout)

        # Add to combined card
        combined_layout.addWidget(search_group)

        # Medication card (unchanged)
        medication_card = ModernCard()
        med_layout = QVBoxLayout(medication_card)
        med_layout.setContentsMargins(25, 25, 25, 25)

        self.medication_group = ModernGroupBox("💊 Medication Management")
        med_content = QVBoxLayout()

        add_med_btn = ModernButton("➕ Add Medication", "success")

        self.medication_table = ModernTable()
        self.medication_table.setColumnCount(6)
        self.medication_table.setHorizontalHeaderLabels(["Type", "Medicine", "Dose", "Days", "Qty", ""])

        med_content.addWidget(add_med_btn)
        med_content.addWidget(self.medication_table)
        self.medication_group.setLayout(med_content)
        med_layout.addWidget(self.medication_group)

        self.medication_table.setMinimumHeight(250)
        self.medication_table.setMaximumHeight(400)

        # Action buttons card (unchanged)
        action_card = ModernCard()
        action_layout = QVBoxLayout(action_card)
        action_layout.setContentsMargins(25, 25, 25, 25)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        save_btn = ModernButton("💾 Save Prescription", "success")
        print_en_btn = ModernButton("🖨️ Print (English)", "primary")
        print_mr_btn = ModernButton("🖨️ Print (मराठी)", "primary")
        print_hi_btn = ModernButton("🖨️ Print (हिंदी)", "primary")
        new_btn = ModernButton("📄 New Entry", "secondary")

        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(print_en_btn)
        btn_layout.addWidget(print_mr_btn)
        btn_layout.addWidget(print_hi_btn)
        btn_layout.addWidget(new_btn)

        action_layout.addLayout(btn_layout)

        # Add all cards to main layout
        layout.addWidget(combined_card)  # Now using the combined card instead of separate ones
        layout.addWidget(medication_card)
        layout.addWidget(action_card)
        layout.addStretch()

        # Set main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Connect signals
        self.patient_search.textEdited.connect(self.update_search_suggestions)
        self.completer.activated.connect(self.on_completer_selected)
        self.enable_reminder.stateChanged.connect(self.toggle_reminder_fields)
        add_med_btn.clicked.connect(self.add_medication_row)
        save_btn.clicked.connect(self.save_prescription)
        new_btn.clicked.connect(self.clear_form)
        print_en_btn.clicked.connect(lambda: self.print_prescription('en'))
        print_mr_btn.clicked.connect(lambda: self.print_prescription('mr'))
        print_hi_btn.clicked.connect(lambda: self.print_prescription('hi'))

    def apply_styles(self):
        self.setStyleSheet("""
            QGroupBox {
                border: 1px solid #d3d3d3;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QTableWidget {
                border: 1px solid #d3d3d3;
                border-radius: 3px;
                background: white;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 5px;
                border: none;
            }
            QPushButton {
                padding: 5px 10px;
                min-width: 80px;
            }
        """)

    def toggle_reminder_fields(self, state):
        self.reminder_date.setVisible(state == Qt.Checked)
        self.reminder_desc.setVisible(state == Qt.Checked)

    def on_completer_selected(self, text):
        """Handle selection from the completer dropdown"""
        import re
        match = re.search(r'\((\d+)\)', text)
        if match:
            patient_id = int(match.group(1))
            self.load_patient_data(patient_id)
            self.patient_search.setText(text)

    def update_search_suggestions(self, text):
        """Update suggestions as user types"""
        if len(text) >= 2:
            patients = self.db.search_patients(text)
            suggestions = []
            for patient in patients:
                suggestion = f"{patient[1]} ({patient[0]})"
                if patient[5]:
                    suggestion += f" - {patient[5]}"
                suggestions.append(suggestion)
            self.completer_model.setStringList(suggestions)
        else:
            self.completer_model.setStringList([])

    def load_patient_data(self, patient_id):
        """Load patient data into form"""
        patient = self.db.get_patient_by_id(patient_id)
        if patient:
            self.current_patient_id = patient_id
            self.patient_name.setText(patient[1])
            self.patient_age.setText(str(patient[2]) if patient[2] else "")
            self.patient_gender.setText(patient[4] if patient[4] else "")
            self.patient_weight.setText(str(patient[3]) if patient[3] else "")

    def add_medication_row(self):
        if not self.current_patient_id:
            QMessageBox.warning(self, "Warning", "Please select a patient first")
            return

        row_pos = self.medication_table.rowCount()
        self.medication_table.insertRow(row_pos)

        # Medicine type combo
        type_combo = ModernComboBox()
        type_combo.addItems([
            "TAB", "SYP", "Drop", "Liquid", "Suspension", "Inhaler",
            "Capsule", "General", "Cream", "Ointment", "Powder"
        ])

        # Medicine name combo with search functionality
        name_combo = ModernComboBox()
        name_combo.setEditable(True)
        name_combo.setInsertPolicy(QComboBox.NoInsert)
        name_combo.lineEdit().setPlaceholderText("Search medicine...")

        # Create completer for search functionality
        self.med_completer = QCompleter()
        self.med_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.med_completer.setFilterMode(Qt.MatchContains)
        name_combo.setCompleter(self.med_completer)

        # Connect type change to update medicine names
        type_combo.currentTextChanged.connect(lambda t: self.update_medicine_names(name_combo, t))
        self.update_medicine_names(name_combo, type_combo.currentText())

        # Dose combo
        dose_combo = ModernComboBox()
        dose_combo.addItems(["1-0-0", "1-0-1", "0-0-1", "1-1-1", "SOS"])

        # Days and Qty
        days_spin = ModernSpinBox()
        days_spin.setRange(1, 30)
        days_spin.setValue(3)

        qty_spin = ModernSpinBox()
        qty_spin.setRange(1, 100)
        qty_spin.setValue(10)

        # Remove button
        remove_btn = ModernButton("❌", "danger")
        remove_btn.setMaximumWidth(50)
        remove_btn.clicked.connect(lambda: self.remove_medication_row(row_pos))

        self.medication_table.setCellWidget(row_pos, 0, type_combo)
        self.medication_table.setCellWidget(row_pos, 1, name_combo)
        self.medication_table.setCellWidget(row_pos, 2, dose_combo)
        self.medication_table.setCellWidget(row_pos, 3, days_spin)
        self.medication_table.setCellWidget(row_pos, 4, qty_spin)
        self.medication_table.setCellWidget(row_pos, 5, remove_btn)

    def update_medicine_names(self, name_combo, med_type):
        medicines = self.db.get_medicines_by_type(med_type)
        name_combo.clear()

        # Get medicine names
        medicine_names = [m[2] for m in medicines]  # Assuming index 2 is the name

        # Add items to combo
        name_combo.addItems(medicine_names)

        # Set completer model
        completer_model = QStringListModel(medicine_names)
        self.med_completer.setModel(completer_model)

        # Clear any previous search text
        name_combo.lineEdit().clear()

    def remove_medication_row(self, row):
        self.medication_table.removeRow(row)

    def get_prescription_data(self):
        if not self.current_patient_id:
            return None

        patient_data = {
            'name': self.patient_name.text(),
            'age': self.patient_age.text(),
            'gender': self.patient_gender.text(),
            'weight': self.patient_weight.text(),
            'cr_no': str(self.current_patient_id),
            'date': QDate.currentDate().toString("dd/MM/yyyy"),
            'revisit_date': self.reminder_date.date().toString(
                "dd/MM/yyyy") if self.enable_reminder.isChecked() else "",
            'medications': []
        }

        for row in range(self.medication_table.rowCount()):
            type_combo = self.medication_table.cellWidget(row, 0)
            name_combo = self.medication_table.cellWidget(row, 1)
            dose_combo = self.medication_table.cellWidget(row, 2)
            days_spin = self.medication_table.cellWidget(row, 3)
            qty_spin = self.medication_table.cellWidget(row, 4)

            medication = {
                'type': type_combo.currentText(),
                'name': name_combo.currentText(),
                'dose': dose_combo.currentText(),
                'days': days_spin.value(),
                'qty': qty_spin.value()
            }
            patient_data['medications'].append(medication)

        return patient_data

    def print_prescription(self, language='en'):
        if not self.current_patient_id:
            QMessageBox.warning(self, "Warning", "Please select a patient first")
            return

        data = self.get_prescription_data()
        if not data:
            return

        # Create a QTextDocument for printing
        doc = QTextDocument()
        cursor = QTextCursor(doc)

        # Build the prescription HTML content
        html = self.generate_prescription_html(data, language)
        doc.setHtml(html)

        # Setup printer
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)

        if dialog.exec_() == QPrintDialog.Accepted:
            # Print the document
            doc.print_(printer)

    def generate_prescription_html(self, data, language):
        # Unit mapping with translations
        unit_mapping = {
            'en': {
                "TAB": "tablet",
                "SYP": "bottle",
                "Drop": "bottle",
                "Liquid": "bottle",
                "Suspension": "bottle",
                "Inhaler": "inhaler",
                "Capsule": "capsule",
                "General": "unit",
                "Cream": "tube",
                "Ointment": "tube",
                "Powder": "packet"
            },
            'mr': {
                "TAB": "गोळी",
                "SYP": "बाटली",
                "Drop": "बाटली",
                "Liquid": "बाटली",
                "Suspension": "बाटली",
                "Inhaler": "इनहेलर",
                "Capsule": "कॅप्सूल",
                "General": "युनिट",
                "Cream": "ट्यूब",
                "Ointment": "ट्यूब",
                "Powder": "पाकीट"
            },
            'hi': {
                "TAB": "गोली",
                "SYP": "शीशी",
                "Drop": "शीशी",
                "Liquid": "शीशी",
                "Suspension": "शीशी",
                "Inhaler": "इनहेलर",
                "Capsule": "कैप्सूल",
                "General": "यूनिट",
                "Cream": "ट्यूब",
                "Ointment": "ट्यूब",
                "Powder": "पैकेट"
            }
        }

        # Language labels
        if language == 'en':
            labels = {
                "name": "Name",
                "date": "Date",
                "cr_no": "C.R.No",
                "age_sex": "Age/Sex",
                "weight": "Weight",
                "vitals": "Vitals:",
                "revisit": "Revisit on",
                "doctor": "Dr. Riyaj SAYYED",
                "reg": "Reg.No. A-1330062"
            }
        elif language == 'mr':
            labels = {
                "name": "नाव",
                "date": "तारीख",
                "cr_no": "क्र.नं.",
                "age_sex": "वय/लिंग",
                "weight": "वजन",
                "vitals": "व्हायटल्स:",
                "revisit": "पुन्हा दाखवण्याची तारीख",
                "doctor": "डॉ. रियाज सय्यद",
                "reg": "नोंदणी क्र. A-1330062"
            }
        elif language == 'hi':
            labels = {
                "name": "नाम",
                "date": "तिथि",
                "cr_no": "सी.आर.नं.",
                "age_sex": "आयु/लिंग",
                "weight": "वजन",
                "vitals": "वाइटल्स:",
                "revisit": "दुबारा दिखाने की तारीख",
                "doctor": "डॉ. रियाज सय्यद",
                "reg": "पंजी.सं. A-1330062"
            }

        html = f"""
              <html>
              <head>
              <style>
                  body {{
                       font-family: 'Times New Roman', serif;
                       margin: 30px;
                       font-size: 12pt;
                       line-height: 1.2;
                       background-color: #f8f8f8;
                       color: #333;
                   }}

                   .prescription-container {{
                       display: flex;
                       height: 100vh;
                       align-items: center;
                       justify-content: center;
                       background-color: white;
                       padding: 30px;
                       border: 2px solid #000;
                       max-width: 800px;
                       margin: 0 auto;
                       box-shadow: 0 0 10px rgba(0,0,0,0.1);
                   }}

                   .header-section {{
                       border-bottom: 2px solid #000;
                       padding-bottom: 15px;
                       margin-bottom: 20px;
                   }}

                   .patient-info {{
                       width: 100%;
                   }}

                   .info-row {{
                       display: flex;
                       justify-content: space-between;
                       margin-bottom: 8px;
                       border-bottom: 1px solid #000;
                       padding-bottom: 3px;
                   }}

                   .info-left, .info-right {{
                       display: flex;
                       align-items: center;
                   }}

                   .info-label {{
                       font-weight: bold;
                       margin-right: 8px;
                       min-width: 80px;
                   }}

                   .info-value {{
                       border-bottom: 1px dotted #666;
                       min-width: 150px;
                       padding-bottom: 2px;
                   }}

                   .vitals-row {{
                       display: flex;
                       align-items: center;
                       margin-bottom: 8px;
                       border-bottom: 1px solid #000;
                       padding-bottom: 3px;
                   }}

                   .rx-section {{
                       margin-top: 25px;
                       margin-bottom: 30px;
                   }}

                   .rx-title {{
                       font-weight: bold;
                       font-size: 18pt;
                       margin-bottom: 15px;
                       text-decoration: underline;
                   }}

                   .medications-table {{
                       width: 100%;
                       border-collapse: collapse;
                       margin-bottom: 20px;
                   }}

                   .med-row {{
                       border-bottom: 1px solid #ddd;
                   }}

                   .med-number {{
                       width: 30px;
                       padding: 8px 5px;
                       font-weight: bold;
                       vertical-align: top;
                       text-align: center;
                   }}

                   .med-details {{
                       padding: 8px 10px;
                       vertical-align: top;
                   }}

                   .med-name {{
                       font-weight: bold;
                       font-size: 13pt;
                       margin-bottom: 3px;
                   }}

                   .med-instruction {{
                       font-size: 11pt;
                       color: #555;
                       margin-bottom: 2px;
                   }}

                   .med-duration {{
                       padding: 8px 10px;
                       vertical-align: middle;
                       text-align: center;
                       font-weight: bold;
                   }}

                   .med-quantity {{
                       padding: 8px 10px;
                       vertical-align: middle;
                       text-align: center;
                       font-weight: bold;
                   }}

                   .revisit-section {{
                       margin-top: 40px;
                       padding-top: 15px;
                       border-top: 1px solid #000;
                       display: flex;
                       justify-content: space-between;
                       align-items: center;
                   }}

                   .revisit-info {{
                       font-weight: bold;
                       font-size: 13pt;
                   }}

                   .doctor-signature {{
                       text-align: center;
                       font-weight: bold;
                   }}

                   .doctor-name {{
                       font-size: 14pt;
                       margin-bottom: 5px;
                   }}

                   .doctor-reg {{
                       font-size: 12pt;
                       color: #666;
                   }}
              </style>
              </head>
              <body>

              <div class="prescription-container">
                  <!-- Header Section -->
                  <div class="header-section">
                      <div class="patient-info">
                          <div class="info-row">
                              <div class="info-left" style="display:flex;">
                                  <span class="info-label">{labels['name']}</span>
                                  <span>:</span>
                                  <span class="info-value" style="margin-left: 10px; padding-right: 50px;">{data['name']}</span>
                                  <span class="info-label" style="float: right;">‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ {labels['date']}</span>
                                  <span>:</span>
                                  <span class="info-value" style="margin-left: 10px;">{data['date']}</span>
                              </div>
                          </div>

                          <div class="info-row">
                              <div class="info-right">
                                  <span class="info-label">{labels['age_sex']}</span>
                                  <span>:</span>
                                  <span class="info-value" style="margin-left: 10px;">{data['age']}/{data['gender']}</span>
                                  <span class="info-label" style="margin-left: 20px;"> ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ {labels['weight']}:</span>
                                  <span class="info-value" style="margin-left: 10px;">{data['weight']} Kg</span>
                              </div>
                         <div>
                      </div>
                  </div>

                  <!-- Prescription Section -->
                  <div class="rx-section">
                      <div class="rx-title">Rx</div>

                      <table class="medications-table">
           """

        # Add medications
        for i, med in enumerate(data['medications'], 1):
            unit = unit_mapping[language].get(med['type'], "unit")
            quantity = f"{med['qty']} {unit}"

            html += f"""
                          <tr class="med-row">
                              <td class="med-number">{i}</td>
                              <td class="med-details">
                                  <div class="med-name">{med['type']}.. {med['name']}</div>
                                  <div class="med-instruction">{med['dose']}</div>
                              </td>
                              <td class="med-duration">{med['days']} दिन</td>
                              <td class="med-quantity">{quantity}</td>
                          </tr>
                  """

        html += """
                      </table>
                  </div>
           """

        # Revisit and Doctor signature section
        html += f"""
                  <div class="revisit-section">
                      <div class="revisit-info">
           """

        if data['revisit_date']:
            html += f"{labels['revisit']}: {data['revisit_date']}"

        html += f"""
                      </div>
                      <div class="doctor-signature">
                          <div class="doctor-name">{labels['doctor']}</div>
                          <div class="doctor-reg">{labels['reg']}</div>
                      </div>
                  </div>
              </div>

              </body>
              </html>
              """

        return html

    def save_prescription(self):
        """Fixed prescription saving with improved error handling"""
        try:
            # Validate inputs
            if not self.current_patient_id:
                QMessageBox.warning(self, "Error", "Please select a patient first")
                return False

            if self.medication_table.rowCount() == 0:
                QMessageBox.warning(self, "Error", "Please add at least one medication")
                return False

            # Prepare data
            prescription_data = {
                'patient_id': self.current_patient_id,
                'enable_reminder': self.enable_reminder.isChecked(),
                'reminder_date': self.reminder_date.date().toString("yyyy-MM-dd")
                if self.enable_reminder.isChecked() else None,
                'reminder_description': self.reminder_desc.toPlainText()
                if self.enable_reminder.isChecked() else None,
                'visit_date': QDate.currentDate().toString("yyyy-MM-dd")
            }

            # Get medication data
            medications = []
            for row in range(self.medication_table.rowCount()):
                type_combo = self.medication_table.cellWidget(row, 0)
                name_combo = self.medication_table.cellWidget(row, 1)
                dose_combo = self.medication_table.cellWidget(row, 2)
                days_spin = self.medication_table.cellWidget(row, 3)
                qty_spin = self.medication_table.cellWidget(row, 4)

                medications.append({
                    'type': type_combo.currentText(),
                    'name': name_combo.currentText(),
                    'dose': dose_combo.currentText(),
                    'days': days_spin.value(),
                    'quantity': qty_spin.value()
                })

            # Database operations
            try:
                # Add prescription and get ID
                prescription_id = self.db.add_prescription(prescription_data)
                if not prescription_id:
                    raise ValueError("Failed to get prescription ID")

                # Add medications
                for med in medications:
                    self.db.add_prescription_medicine(prescription_id, med)

                # Commit transaction
                print("Here....")
                self.db.conn.commit()

                QMessageBox.information(
                    self,
                    "Success",
                    f"Prescription saved successfully\nID: {prescription_id}"
                )

                self.clear_form()
                return True

            except Exception as e:
                # Rollback on error
                self.db.connection.rollback()
                QMessageBox.critical(
                    self,
                    "Database Error",
                    f"Failed to save prescription:\n{str(e)}"
                )
                return False

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred:\n{str(e)}"
            )
            return False

    def clear_form(self):
        self.current_patient_id = None
        self.patient_name.setText("Not selected")
        self.patient_age.clear()
        self.patient_gender.clear()
        self.patient_weight.clear()
        self.patient_search.clear()
        self.enable_reminder.setChecked(False)
        self.reminder_date.setDate(QDate.currentDate())
        self.reminder_desc.clear()
        self.medication_table.setRowCount(0)

    def closeEvent(self, event):
        """Clean up when window is closed"""
        self._alive = False
        if hasattr(self, 'db') and self.db:
            self.db.close()
        super().closeEvent(event)


class FitnessCertificateTab(QWidget):
    def __init__(self, db_handler):
        super().__init__()
        self.db = db_handler
        self.initUI()
        self.apply_styles()

    def initUI(self):
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        main_widget = QWidget()
        scroll.setWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        # Certificate details card
        details_card = ModernCard()
        details_layout = QVBoxLayout(details_card)
        details_layout.setContentsMargins(25, 25, 25, 25)

        details_group = ModernGroupBox("📝 Certificate Details")
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)

        self.title_combo = ModernComboBox()
        self.title_combo.addItems(["Mr.", "Miss", "Mrs.", "Dr."])
        self.name_input = ModernLineEdit()
        self.age_input = ModernLineEdit()
        self.certificate_date = ModernDateEdit(QDate.currentDate())
        self.certificate_date.setCalendarPopup(True)

        # Add doctor information fields

        form_layout.addRow("Title:", self.title_combo)
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Age:", self.age_input)
        form_layout.addRow("Date:", self.certificate_date)
        details_group.setLayout(form_layout)
        details_layout.addWidget(details_group)

        # Action buttons card
        action_card = ModernCard()
        action_layout = QVBoxLayout(action_card)
        action_layout.setContentsMargins(25, 25, 25, 25)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        generate_btn = ModernButton("🖨️ Generate Certificate", "primary")
        new_btn = ModernButton("📄 New Entry", "secondary")

        btn_layout.addWidget(generate_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(new_btn)

        action_layout.addLayout(btn_layout)

        # Add all to layout
        layout.addWidget(details_card)
        layout.addWidget(action_card)
        layout.addStretch()

        # Set main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Connect signals
        generate_btn.clicked.connect(self.generate_certificate)
        new_btn.clicked.connect(self.clear_form)

    def apply_styles(self):
        self.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #2c3e50;
                font-weight: 500;
            }
            QLineEdit, QComboBox, QDateEdit {
                padding: 8px;
                border: 1px solid #d3d3d3;
                border-radius: 4px;
                min-height: 30px;
            }
        """)

    def generate_certificate(self):
        if not self.name_input.text():
            QMessageBox.warning(self, "Warning", "Name is required")
            return

        try:
            # Get form values
            title = self.title_combo.currentText()
            name = f"{title} {self.name_input.text()}"
            age = self.age_input.text()
            doctor_name = "Riyaj Sayyed"
            reg_no = "A-1330062"
            date_str = self.certificate_date.date().toString("dd.MM.yyyy")

            # Generate default filename with person's name
            safe_name = "".join(c for c in name if c.isalnum() or c in " _-")
            default_filename = f"Fitness_Certificate_{safe_name}.pdf"

            # Let user choose save location
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(
                self,
                "Save Fitness Certificate",
                default_filename,
                "PDF Files (*.pdf)"
            )

            if not file_path:  # User cancelled the dialog
                return

            # Ensure the file has .pdf extension
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'

            # Generate the PDF
            self._generate_pdf_certificate(
                name=name,
                age=age,
                doctor_name=doctor_name,
                reg_no=reg_no,
                date_str=date_str,
                filename=file_path
            )

            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Fitness certificate generated successfully!\nSaved as: {file_path}"
            )
            self.clear_form()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate certificate: {str(e)}")

    def _generate_pdf_certificate(self, name, age, doctor_name, reg_no, date_str, filename):
        """Helper method to generate the PDF certificate using ReportLab"""
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 100, "FITNESS CERTIFICATE")
        c.line(width / 2 - 100, height - 105, width / 2 + 100, height - 105)

        # Body text
        c.setFont("Helvetica", 12)
        text = f"""This is to certify that {name} Age {age} yrs is examined 
                by me. He is physically and mentally fit & Does not 
                have any Disease."""

        text_object = c.beginText(100, height - 160)
        for line in text.split("\n"):
            text_object.textLine(line)
        c.drawText(text_object)

        # Signature line
        c.line(100, height - 240, 400, height - 240)

        # Doctor's details
        c.setFont("Helvetica", 12)
        c.drawString(100, height - 270, f"Dr. {doctor_name}")
        c.drawString(100, height - 285, f"Reg.No.{reg_no}")
        c.drawString(100, height - 300, f"Date: {date_str}")

        c.save()

    def clear_form(self):
        self.title_combo.setCurrentIndex(0)
        self.name_input.clear()
        self.age_input.clear()
        self.certificate_date.setDate(QDate.currentDate())


class MedicalCertificateTab(QWidget):
    def __init__(self, db_handler):
        super().__init__()
        self.db = db_handler
        self.initUI()
        self.apply_styles()

    def initUI(self):
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        main_widget = QWidget()
        scroll.setWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        # Certificate form card
        cert_card = ModernCard()
        cert_layout = QVBoxLayout(cert_card)
        cert_layout.setContentsMargins(25, 25, 25, 25)

        cert_group = ModernGroupBox("📋 Medical Certificate")
        cert_form = QFormLayout()
        cert_form.setVerticalSpacing(15)

        self.title_combo = ModernComboBox()
        self.title_combo.addItems(["Mr.", "Miss", "Mrs.", "Dr."])
        self.name_input = ModernLineEdit()
        self.illness_input = ModernTextEdit("Enter illness details...")
        self.illness_input.setMaximumHeight(80)
        self.from_date = ModernDateEdit(QDate.currentDate())
        self.to_date = ModernDateEdit(QDate.currentDate().addDays(7))

        # Doctor information fields

        cert_form.addRow("Title:", self.title_combo)
        cert_form.addRow("Name:", self.name_input)
        cert_form.addRow("Illness:", self.illness_input)
        cert_form.addRow("From Date:", self.from_date)
        cert_form.addRow("To Date:", self.to_date)
        cert_group.setLayout(cert_form)
        cert_layout.addWidget(cert_group)

        # Action buttons card
        action_card = ModernCard()
        action_layout = QVBoxLayout(action_card)
        action_layout.setContentsMargins(25, 25, 25, 25)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        generate_btn = ModernButton("🖨️ Generate Certificate", "primary")
        new_btn = ModernButton("📄 New Entry", "secondary")

        btn_layout.addWidget(generate_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(new_btn)

        action_layout.addLayout(btn_layout)

        # Add all to layout
        layout.addWidget(cert_card)
        layout.addWidget(action_card)
        layout.addStretch()

        # Set main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Connect signals
        generate_btn.clicked.connect(self.generate_certificate)
        new_btn.clicked.connect(self.clear_form)

    def apply_styles(self):
        self.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #2c3e50;
                font-weight: 500;
            }
            QLineEdit, QComboBox, QDateEdit {
                padding: 8px;
                border: 1px solid #d3d3d3;
                border-radius: 4px;
                min-height: 30px;
            }
            QTextEdit {
                padding: 8px;
                border: 1px solid #d3d3d3;
                border-radius: 4px;
            }
        """)

    def generate_certificate(self):
        if not self.name_input.text():
            QMessageBox.warning(self, "Warning", "Name is required")
            return

        if not self.illness_input.toPlainText():
            QMessageBox.warning(self, "Warning", "Illness description is required")
            return

        try:
            # Get form values
            title = self.title_combo.currentText()
            name = f"{title} {self.name_input.text()}"
            illness = self.illness_input.toPlainText()
            from_date = self.from_date.date().toString("dd.MM.yyyy")
            to_date = self.to_date.date().toString("dd.MM.yyyy")
            doctor_name = "Riyaj Sayyed"
            reg_no = "A-1330062"
            current_date = QDate.currentDate().toString("dd.MM.yyyy")

            # Generate default filename with person's name
            safe_name = "".join(c for c in name if c.isalnum() or c in " _-")
            default_filename = f"Medical_Certificate_{safe_name}.pdf"

            # Let user choose save location
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(
                self,
                "Save Medical Certificate",
                default_filename,
                "PDF Files (*.pdf)"
            )

            if not file_path:  # User cancelled the dialog
                return

            # Ensure the file has .pdf extension
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'

            # Generate the PDF
            self._generate_medical_certificate(
                name=name,
                illness=illness,
                from_date=from_date,
                to_date=to_date,
                doctor_name=doctor_name,
                reg_no=reg_no,
                current_date=current_date,
                filename=file_path
            )

            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Medical certificate generated successfully!\nSaved as: {file_path}"
            )
            self.clear_form()

            # Optional: Automatically open the generated file
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(file_path, "open")
                elif os.uname().sysname == 'Darwin':  # macOS
                    os.system(f"open '{file_path}'")
                else:  # Linux
                    os.system(f"xdg-open '{file_path}'")
            except:
                pass  # Silently fail if opening doesn't work

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate certificate: {str(e)}")

    def _generate_medical_certificate(self, name, illness, from_date, to_date,
                                    doctor_name, reg_no, current_date, filename):
        """Helper method to generate the PDF certificate using ReportLab"""
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 100, "MEDICAL CERTIFICATE")
        c.line(width / 2 - 100, height - 105, width / 2 + 100, height - 105)

        # Body text
        c.setFont("Helvetica", 12)
        text = c.beginText(70, height - 150)
        text.setLeading(20)
        text.textLine(f"This is to certify that {name} is/was advised rest from")
        text.textLine(f"{from_date} to {to_date} as, He is/was suffering from {illness}.")
        text.textLine(f"He is physically fit to resume after {to_date}.")
        c.drawText(text)

        # Not valid in court line
        c.line(70, height - 240, width - 70, height - 240)
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(75, height - 255, "[Not Valid in Court]")

        # Doctor details
        c.setFont("Helvetica", 12)
        c.drawString(70, height - 300, f"Dr. {doctor_name}")
        c.drawString(70, height - 320, f"Reg.No.{reg_no}")
        c.drawString(70, height - 340, f"Date: {current_date}")

        c.save()
    def clear_form(self):
        self.title_combo.setCurrentIndex(0)
        self.name_input.clear()
        self.illness_input.clear()
        self.from_date.setDate(QDate.currentDate())
        self.to_date.setDate(QDate.currentDate().addDays(7))


class BillingTab(QWidget):
    def __init__(self, db_handler):
        super().__init__()
        self.db = db_handler
        self.current_patient_id = None
        self.initUI()
        self.apply_styles()

    def initUI(self):
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        main_widget = QWidget()
        scroll.setWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        # Combined Patient Search & Details Card
        patient_card = ModernCard()
        patient_layout = QVBoxLayout(patient_card)
        patient_layout.setContentsMargins(25, 25, 25, 25)

        # Combined group box
        patient_group = ModernGroupBox("🔍 Patient Search & Details")
        patient_content = QVBoxLayout()
        patient_content.setSpacing(15)

        # Search row
        search_row = QHBoxLayout()
        search_row.setContentsMargins(0, 0, 0, 0)
        self.patient_search = ModernLineEdit("Search patient by name or mobile...")
        self.patient_search.setMinimumWidth(300)

        # Create completer
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer_model = QStringListModel()
        self.completer.setModel(self.completer_model)
        self.patient_search.setCompleter(self.completer)

        search_row.addWidget(self.patient_search)
        search_row.addStretch()

        # Details row - compact horizontal layout
        details_row = QHBoxLayout()
        details_row.setContentsMargins(0, 0, 0, 0)
        details_row.setSpacing(15)

        # Name section
        name_label = QLabel("Name:")
        self.patient_name = QLabel("Not selected")
        self.patient_name.setFixedWidth(200)

        # Info fields (age, gender, mobile)
        self.patient_age = QLabel("")
        self.patient_gender = QLabel("")
        self.patient_mobile = QLabel("")

        # Helper function to create compact info widgets
        def create_info_field(title, value_widget, width=80):
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(5)
            layout.addWidget(QLabel(title))
            value_widget.setFixedWidth(width)
            layout.addWidget(value_widget)
            return container

        details_row.addWidget(name_label)
        details_row.addWidget(self.patient_name)
        details_row.addWidget(create_info_field("Age:", self.patient_age, 60))
        details_row.addWidget(create_info_field("Gender:", self.patient_gender, 80))
        details_row.addWidget(create_info_field("Mobile:", self.patient_mobile, 120))
        details_row.addStretch()

        # Style all value labels
        for label in [self.patient_name, self.patient_age, self.patient_gender, self.patient_mobile]:
            label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #2c3e50;
                    padding: 6px 8px;
                    background-color: #ecf0f1;
                    border-radius: 4px;
                    font-weight: 500;
                }
            """)

        # Add sections to patient content
        patient_content.addLayout(search_row)
        patient_content.addLayout(details_row)
        patient_group.setLayout(patient_content)
        patient_layout.addWidget(patient_group)

        # Bill items card (unchanged)
        bill_card = ModernCard()
        bill_layout = QVBoxLayout(bill_card)
        bill_layout.setContentsMargins(25, 25, 25, 25)

        bill_group = ModernGroupBox("💰 Bill Items")
        bill_content = QVBoxLayout()

        add_item_btn = ModernButton("➕ Add Bill Item", "primary")

        self.bill_table = ModernTable()
        self.bill_table.setColumnCount(3)
        self.bill_table.setHorizontalHeaderLabels(["Description", "Amount (₹)", ""])
        self.bill_table.setMinimumHeight(200)

        bill_content.addWidget(add_item_btn)
        bill_content.addWidget(self.bill_table)
        bill_group.setLayout(bill_content)
        bill_layout.addWidget(bill_group)

        # Total amount display (unchanged)
        self.total_label = QLabel("Total: ₹0.00")
        self.total_label.setAlignment(Qt.AlignRight)
        self.total_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #27ae60;
                padding: 10px;
                background-color: #e8f5e8;
                border-radius: 8px;
                border: 2px solid #27ae60;
            }
        """)

        # Action buttons card (unchanged)
        action_card = ModernCard()
        action_layout = QVBoxLayout(action_card)
        action_layout.setContentsMargins(25, 25, 25, 25)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        generate_btn = ModernButton("💾 Generate Receipt", "success")
        new_btn = ModernButton("📄 New Entry", "secondary")

        btn_layout.addWidget(generate_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(new_btn)

        action_layout.addLayout(btn_layout)

        # Add all to layout
        layout.addWidget(patient_card)  # Combined patient card
        layout.addWidget(bill_card)
        layout.addWidget(self.total_label)
        layout.addWidget(action_card)
        layout.addStretch()

        # Set main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Connect signals
        self.patient_search.textEdited.connect(self.update_search_suggestions)
        self.completer.activated.connect(self.on_completer_selected)
        add_item_btn.clicked.connect(self.add_bill_item_row)
        generate_btn.clicked.connect(self.generate_bill)
        new_btn.clicked.connect(self.clear_form)

    def apply_styles(self):
        self.bill_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d3d3d3;
                border-radius: 3px;
                background: white;
                gridline-color: #e0e0e0;
            }

            QTableWidget QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 5px;
                border: none;
            }
        """)

    def update_search_suggestions(self, text):
        """Update suggestions as user types"""
        if len(text) >= 2:  # Only search when at least 2 characters are typed
            patients = self.db.search_patients(text)
            suggestions = []
            for patient in patients:
                # Format: "Name (ID) - Mobile"
                suggestion = f"{patient[1]} ({patient[0]})"
                if patient[5]:  # If mobile number exists
                    suggestion += f" - {patient[5]}"
                suggestions.append(suggestion)

            self.completer_model.setStringList(suggestions)
        else:
            self.completer_model.setStringList([])

    def on_completer_selected(self, text):
        """Handle selection from the completer dropdown"""
        import re
        match = re.search(r'\((\d+)\)', text)
        if match:
            patient_id = int(match.group(1))
            self.load_patient_data(patient_id)
            self.patient_search.setText(text)

    def load_patient_data(self, patient_id):
        """Load patient data into form"""
        patient = self.db.get_patient_by_id(patient_id)
        if patient:
            self.current_patient_id = patient_id
            self.patient_name.setText(patient[1])
            self.patient_age.setText(str(patient[2]) if patient[2] else "")
            self.patient_gender.setText(patient[4] if patient[4] else "")
            self.patient_mobile.setText(patient[5] if patient[5] else "")

    def add_bill_item_row(self):
        row_pos = self.bill_table.rowCount()
        self.bill_table.insertRow(row_pos)

        # Item description
        desc_input = QLineEdit()
        desc_input.setPlaceholderText("Consultation/Medicine/etc.")

        # Charges
        charges_input = QLineEdit()
        charges_input.setPlaceholderText("Amount")
        charges_input.setValidator(QDoubleValidator(0, 99999, 2))

        # Remove button
        remove_btn = QPushButton("X")
        remove_btn.setMaximumWidth(30)
        remove_btn.setStyleSheet("background-color: #ff4444; color: white;")
        remove_btn.clicked.connect(lambda: self.remove_bill_item_row(row_pos))

        self.bill_table.setCellWidget(row_pos, 0, desc_input)
        self.bill_table.setCellWidget(row_pos, 1, charges_input)
        self.bill_table.setCellWidget(row_pos, 2, remove_btn)

        # Connect charges change to update total
        charges_input.textChanged.connect(self.update_total)

    def remove_bill_item_row(self, row):
        self.bill_table.removeRow(row)
        self.update_total()

    def update_total(self):
        total = 0.0
        for row in range(self.bill_table.rowCount()):
            charges_input = self.bill_table.cellWidget(row, 1)
            try:
                total += float(charges_input.text())
            except ValueError:
                pass
        self.total_label.setText(f"Total: ₹{total:.2f}")

    def generate_bill(self):
        if not self.current_patient_id:
            QMessageBox.warning(self, "Warning", "Please select a patient first")
            return

        if self.bill_table.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "Please add at least one bill item")
            return

        try:
            # Get bill items
            bill_items = []
            for row in range(self.bill_table.rowCount()):
                desc_input = self.bill_table.cellWidget(row, 0)
                charges_input = self.bill_table.cellWidget(row, 1)

                description = desc_input.text()
                amount = float(charges_input.text())
                bill_items.append((description, amount))

            # Calculate total
            total = sum(item[1] for item in bill_items)

            # Save bill to database
            cursor = self.db.conn.cursor()
            cursor.execute('''
            INSERT INTO Bills (patient_id, name, age, mobile, total_amount)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                self.current_patient_id,
                self.patient_name.text(),
                int(self.patient_age.text()) if self.patient_age.text() else None,
                self.patient_mobile.text(),
                total
            ))
            bill_id = cursor.lastrowid

            # Save bill items
            for description, amount in bill_items:
                cursor.execute('''
                INSERT INTO Bill_Items (bill_id, item_type, charges)
                VALUES (?, ?, ?)
                ''', (bill_id, description, amount))

            self.db.conn.commit()

            # Generate receipt PDF
            patient_name = self.patient_name.text()
            patient_age = self.patient_age.text()
            patient_gender = self.patient_gender.text()
            doctor_name = "Riyaj Sayyed"
            reg_no = "A-1330062"

            # Create filename with patient name and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c for c in patient_name if c.isalnum() or c in " _-")
            filename = f"Receipt_{safe_name}_{timestamp}.pdf"

            self._generate_receipt_pdf(
                name=patient_name,
                age=patient_age,
                gender=patient_gender,
                items=bill_items,
                doctor_name=doctor_name,
                reg_no=reg_no,
                output_filename=filename
            )

            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Bill generated successfully!\nTotal: {total:.2f}\nReceipt saved as: {os.path.abspath(filename)}"
            )

            # Optionally open the PDF
            try:
                if os.name == 'nt':
                    os.startfile(filename, "open")
                elif os.uname().sysname == 'Darwin':
                    os.system(f"open {filename}")
                else:
                    os.system(f"xdg-open {filename}")
            except:
                pass  # Silently fail if opening doesn't work

            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate bill: {str(e)}")

    def _generate_receipt_pdf(self, name, age, gender, items, doctor_name, reg_no, output_filename):
        """Generate a PDF receipt for the bill"""
        c = canvas.Canvas(output_filename, pagesize=A4)
        width, height = A4

        # Header line
        c.drawString(50, height - 50, "-" * 90)

        # Patient Details
        c.drawString(60, height - 70, f"Name: {name}")
        c.drawString(300, height - 70, f"Date: {datetime.today().strftime('%d/%m/%Y')}")
        c.drawString(300, height - 90, f"Age/Gender: {age}/{gender}")

        # Item Header Line
        c.drawString(50, height - 110, "-" * 90)

        # Items
        y = height - 130
        total = 0
        for i, (item, price) in enumerate(items, 1):
            c.drawString(60, y, f"{i}.  {item}")
            c.drawString(300, y, f"{price:.2f}")
            total += price
            y -= 20

        # Total line
        c.drawString(50, y, "-" * 90)
        y -= 20
        c.drawString(250, y, f"Total: {total:.2f}")
        y -= 20
        c.drawString(50, y, "-" * 90)

        # Doctor signature
        y -= 60
        c.drawString(400, y, f"Dr.{doctor_name}")
        c.drawString(400, y - 15, f"Reg.No.{reg_no}")

        c.save()

    def clear_form(self):
        self.current_patient_id = None
        self.patient_name.setText("Not selected")
        self.patient_age.clear()
        self.patient_gender.clear()
        self.patient_mobile.clear()
        self.patient_search.clear()
        self.bill_table.setRowCount(0)
        self.total_label.setText("Total: ₹0.00")


class MasterTab(QWidget):
    def __init__(self, db_handler):
        super().__init__()
        self.db = db_handler
        self.initUI()
        self.apply_styles()

    def initUI(self):
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        main_widget = QWidget()
        scroll.setWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(25)

        # Medicine management card
        medicine_card = ModernCard()
        med_layout = QVBoxLayout(medicine_card)
        med_layout.setContentsMargins(25, 25, 25, 25)

        med_group = ModernGroupBox("💊 Medicine Management")
        med_form = QGridLayout()

        # Add medicine form
        self.medicine_type = ModernComboBox()
        self.medicine_type.addItems([
            "TAB", "SYP", "Drop", "Liquid", "Suspension", "Inhaler",
            "Injection", "Capsule", "General", "Cream", "Ointment",
            "Powder", "Applicator", "Mdi", "Gel", "Lotion", "Sachets"
        ])

        self.medicine_name = ModernLineEdit("Enter medicine name...")

        add_med_btn = ModernButton("➕ Add Medicine", "success")

        med_form.addWidget(QLabel("Type:"), 0, 0)
        med_form.addWidget(self.medicine_type, 0, 1)
        med_form.addWidget(QLabel("Name:"), 0, 2)
        med_form.addWidget(self.medicine_name, 0, 3)
        med_form.addWidget(add_med_btn, 1, 3)

        # Medicine list table
        self.medicines_table = ModernTable()
        self.medicines_table.setColumnCount(3)
        self.medicines_table.setHorizontalHeaderLabels(["ID", "Type", "Name"])
        self.medicines_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.medicines_table.setMinimumHeight(300)

        med_layout_inner = QVBoxLayout()
        med_layout_inner.addLayout(med_form)
        med_layout_inner.addWidget(self.medicines_table)
        med_group.setLayout(med_layout_inner)
        med_layout.addWidget(med_group)

        # System settings card
        # settings_card = ModernCard()
        # settings_layout = QVBoxLayout(settings_card)
        # settings_layout.setContentsMargins(25, 25, 25, 25)
        #
        # settings_group = ModernGroupBox("⚙️ System Settings")
        # settings_form = QFormLayout()
        #
        # self.doctor_name = ModernLineEdit("Dr. [Your Name]")
        # self.clinic_name = ModernLineEdit("Clinic Name")
        # self.clinic_address = ModernTextEdit("Clinic Address...")
        # self.clinic_address.setMaximumHeight(80)
        #
        # settings_form.addRow("Doctor Name:", self.doctor_name)
        # settings_form.addRow("Clinic Name:", self.clinic_name)
        # settings_form.addRow("Address:", self.clinic_address)
        #
        # save_settings_btn = ModernButton("💾 Save Settings", "success")
        # settings_form.addRow("", save_settings_btn)
        #
        # settings_group.setLayout(settings_form)
        # settings_layout.addWidget(settings_group)

        layout.addWidget(medicine_card)
        # layout.addWidget(settings_card)
        layout.addStretch()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Connect signals
        add_med_btn.clicked.connect(self.save_medicine)
        # save_settings_btn.clicked.connect(self.save_settings)

        # Load initial data
        self.load_medicines()

    def apply_styles(self):
        self.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #2c3e50;
                font-weight: 500;
            }
            QLineEdit, QComboBox, QTextEdit {
                padding: 8px;
                border: 1px solid #d3d3d3;
                border-radius: 4px;
                min-height: 30px;
            }
            QTableWidget {
                border: 1px solid #d3d3d3;
                border-radius: 3px;
                background: white;
                gridline-color: #e0e0e0;
            }
            QTableWidget QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 5px;
                border: none;
            }
        """)

    def save_medicine(self):
        if not self.medicine_name.text():
            QMessageBox.warning(self, "Warning", "Medicine name is required")
            return

        try:
            medicine_data = {
                'type': self.medicine_type.currentText(),
                'name': self.medicine_name.text()
            }

            self.db.add_medicine(medicine_data)
            QMessageBox.information(self, "Success", "Medicine saved successfully")
            self.clear_form()
            self.load_medicines()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save medicine: {str(e)}")

    def clear_form(self):
        self.medicine_name.clear()

    def load_medicines(self):
        try:
            medicines = self.db.get_all_medicines()
            self.medicines_table.setRowCount(len(medicines))

            for row, medicine in enumerate(medicines):
                self.medicines_table.setItem(row, 0, QTableWidgetItem(str(medicine[0])))
                self.medicines_table.setItem(row, 1, QTableWidgetItem(medicine[1]))
                self.medicines_table.setItem(row, 2, QTableWidgetItem(medicine[2]))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load medicines: {str(e)}")

    def save_settings(self):
        try:
            settings_data = {
                'doctor_name': self.doctor_name.text(),
                'clinic_name': self.clinic_name.text(),
                'clinic_address': self.clinic_address.toPlainText()
            }
            # Save settings to database or config file
            QMessageBox.information(self, "Success", "Settings saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

def main():
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("OPDCare 2.0")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Medical Solutions")

    # Apply modern application style
    app.setStyle('Fusion')

    # Set application font
    font = QFont("Segoe UI", 9)
    app.setFont(font)

    try:
        window = OPDCareApp()
        window.show()

        # Handle application exit
        sys.exit(app.exec_())

    except Exception as e:
        print(f"Application error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()