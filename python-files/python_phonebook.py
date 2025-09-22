import sys
import json
import os
from uuid import uuid4
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, 
                QMessageBox, QDialog, QFormLayout, QComboBox, QTextEdit, QHeaderView,
                QToolBar, QStatusBar, QAction, QFileDialog, QInputDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
import pandas as pd

class Contact:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid4()))
        self.first_name = kwargs.get('first_name', '')
        self.last_name = kwargs.get('last_name', '')
        self.national_code = kwargs.get('national_code', '')
        self.mobile = kwargs.get('mobile', '')
        self.phone = kwargs.get('phone', '')
        self.job = kwargs.get('job', '')
        self.work_history = kwargs.get('work_history', '')
        self.start_date = kwargs.get('start_date', '')
        self.job_title = kwargs.get('job_title', '')
        self.organizational_post = kwargs.get('organizational_post', '')
        self.work_address = kwargs.get('work_address', '')
        self.home_address = kwargs.get('home_address', '')
        self.marital_status = kwargs.get('marital_status', '')
        self.blood_type = kwargs.get('blood_type', '')
        self.birth_date_solar = kwargs.get('birth_date_solar', '')
        self.birth_date_gregorian = kwargs.get('birth_date_gregorian', '')
        self.profile_image = kwargs.get('profile_image', '')
        self.documents = kwargs.get('documents', [])

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        return self.__dict__

    def is_duplicate(self, other_contact):
        return (self.mobile and self.mobile == other_contact.mobile) or \
                (self.national_code and self.national_code == other_contact.national_code)

class ContactManager:
    def __init__(self):
        self.contacts = []
        self.load_data()

    def load_data(self):
        try:
            if os.path.exists('contacts.json'):
                with open('contacts.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.contacts = [Contact(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.contacts = []

    def save_data(self):
        with open('contacts.json', 'w', encoding='utf-8') as f:
            json.dump([c.to_dict() for c in self.contacts], f, ensure_ascii=False, indent=2)

    def add_contact(self, contact):
        for existing_contact in self.contacts:
            if contact.is_duplicate(existing_contact):
                return False, "مخاطب تکراری است"
        
        self.contacts.append(contact)
        self.save_data()
        return True, "مخاطب با موفقیت افزوده شد"

    def update_contact(self, contact_id, new_data):
        contact = self.get_contact_by_id(contact_id)
        if contact:
            for key, value in new_data.items():
                if hasattr(contact, key):
                    setattr(contact, key, value)
            self.save_data()
            return True, "مخاطب با موفقیت به‌روزرسانی شد"
        return False, "مخاطب یافت نشد"

    def get_contact_by_id(self, contact_id):
        for contact in self.contacts:
            if contact.id == contact_id:
                return contact
        return None

    def delete_contact(self, contact_id):
        contact = self.get_contact_by_id(contact_id)
        if contact:
            self.contacts.remove(contact)
            self.save_data()
            return True, "مخاطب با موفقیت حذف شد"
        return False, "مخاطب یافت نشد"

    def search_contacts(self, query):
        results = []
        query = query.lower()
        for contact in self.contacts:
            if (query in contact.first_name.lower() or 
                query in contact.last_name.lower() or 
                query in contact.mobile or 
                query in contact.national_code or 
                query in contact.job.lower() or 
                query in contact.organizational_post.lower()):
                results.append(contact)
        return results

class ContactDialog(QDialog):
    def __init__(self, contact_manager, contact=None, parent=None):
        super().__init__(parent)
        self.contact_manager = contact_manager
        self.contact = contact
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("ویرایش مخاطب" if self.contact else "افزودن مخاطب جدید")
        self.setMinimumWidth(500)
        self.setLayoutDirection(Qt.RightToLeft)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignRight)
        
        form_layout = QFormLayout()
        form_layout.setFormAlignment(Qt.AlignRight)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setAlignment(Qt.AlignRight)
        self.last_name_edit = QLineEdit()
        self.last_name_edit.setAlignment(Qt.AlignRight)
        self.national_code_edit = QLineEdit()
        self.national_code_edit.setAlignment(Qt.AlignRight)
        self.mobile_edit = QLineEdit()
        self.mobile_edit.setAlignment(Qt.AlignRight)
        self.phone_edit = QLineEdit()
        self.phone_edit.setAlignment(Qt.AlignRight)
        self.job_edit = QLineEdit()
        self.job_edit.setAlignment(Qt.AlignRight)
        self.organizational_post_edit = QLineEdit()
        self.organizational_post_edit.setAlignment(Qt.AlignRight)
        self.work_address_edit = QTextEdit()
        self.work_address_edit.setAlignment(Qt.AlignRight)
        self.home_address_edit = QTextEdit()
        self.home_address_edit.setAlignment(Qt.AlignRight)
        
        self.marital_status_combo = QComboBox()
        self.marital_status_combo.addItems(["", "متأهل", "مجرد"])
        self.blood_type_combo = QComboBox()
        self.blood_type_combo.addItems(["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        
        self.birth_date_solar_edit = QLineEdit()
        self.birth_date_solar_edit.setAlignment(Qt.AlignRight)
        self.birth_date_gregorian_edit = QLineEdit()
        self.birth_date_gregorian_edit.setAlignment(Qt.AlignRight)
        
        form_layout.addRow(QLabel("نام:"), self.first_name_edit)
        form_layout.addRow(QLabel("نام خانوادگی:"), self.last_name_edit)
        form_layout.addRow(QLabel("کد ملی:"), self.national_code_edit)
        form_layout.addRow(QLabel("شماره موبایل:"), self.mobile_edit)
        form_layout.addRow(QLabel("شماره تلفن:"), self.phone_edit)
        form_layout.addRow(QLabel("شغل:"), self.job_edit)
        form_layout.addRow(QLabel("پست سازمانی:"), self.organizational_post_edit)
        form_layout.addRow(QLabel("آدرس محل کار:"), self.work_address_edit)
        form_layout.addRow(QLabel("آدرس منزل:"), self.home_address_edit)
        form_layout.addRow(QLabel("وضعیت تأهل:"), self.marital_status_combo)
        form_layout.addRow(QLabel("گروه خونی:"), self.blood_type_combo)
        form_layout.addRow(QLabel("تاریخ تولد شمسی:"), self.birth_date_solar_edit)
        form_layout.addRow(QLabel("تاریخ تولد میلادی:"), self.birth_date_gregorian_edit)
        
        if self.contact:
            self.first_name_edit.setText(self.contact.first_name)
            self.last_name_edit.setText(self.contact.last_name)
            self.national_code_edit.setText(self.contact.national_code)
            self.mobile_edit.setText(self.contact.mobile)
            self.phone_edit.setText(self.contact.phone)
            self.job_edit.setText(self.contact.job)
            self.organizational_post_edit.setText(self.contact.organizational_post)
            self.work_address_edit.setPlainText(self.contact.work_address)
            self.home_address_edit.setPlainText(self.contact.home_address)
            self.marital_status_combo.setCurrentText(self.contact.marital_status or "")
            self.blood_type_combo.setCurrentText(self.contact.blood_type or "")
            self.birth_date_solar_edit.setText(self.contact.birth_date_solar or "")
            self.birth_date_gregorian_edit.setText(self.contact.birth_date_gregorian or "")
        
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignRight)
        
        save_button = QPushButton("ذخیره")
        save_button.clicked.connect(self.save_contact)
        cancel_button = QPushButton("انصراف")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def save_contact(self):
        contact_data = {
            'first_name': self.first_name_edit.text(),
            'last_name': self.last_name_edit.text(),
            'mobile': self.mobile_edit.text(),
            'national_code': self.national_code_edit.text(),
            'phone': self.phone_edit.text(),
            'job': self.job_edit.text(),
            'organizational_post': self.organizational_post_edit.text(),
            'work_address': self.work_address_edit.toPlainText(),
            'home_address': self.home_address_edit.toPlainText(),
            'marital_status': self.marital_status_combo.currentText(),
            'blood_type': self.blood_type_combo.currentText(),
            'birth_date_solar': self.birth_date_solar_edit.text(),
            'birth_date_gregorian': self.birth_date_gregorian_edit.text()
        }
        
        if self.contact:
            success, message = self.contact_manager.update_contact(self.contact.id, contact_data)
        else:
            new_contact = Contact(**contact_data)
            success, message = self.contact_manager.add_contact(new_contact)
        
        if success:
            QMessageBox.information(self, "موفقیت", message)
            self.accept()
        else:
            QMessageBox.warning(self, "خطا", message)

class PhoneBookApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.contact_manager = ContactManager()
        self.setup_ui()
        self.load_contacts()
        
    def setup_ui(self):
        self.setWindowTitle("دفرچه تلفن سازمانی (برنامه نویس و توسعه دهنده : مهندس محمدباقر احمدی - 09194615118)")
        self.setGeometry(100, 100, 1200, 800)
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.apply_styles()
        
        central_widget = QWidget()
        central_widget.setLayoutDirection(Qt.RightToLeft)
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignRight)
        central_widget.setLayout(main_layout)
        
        # ایجاد نوار ابزار
        toolbar = QToolBar()
        toolbar.setLayoutDirection(Qt.RightToLeft)
        self.addToolBar(toolbar)
        
        # افزودن دکمه‌ها به نوار ابزار
        actions = [
            ("افزودن مخاطب", "list-add", self.add_contact),
            ("ویرایش مخاطب", "document-edit", self.edit_contact),
            ("حذف مخاطب", "edit-delete", self.delete_contact),
            ("کپی مخاطب", "edit-copy", self.copy_contact),
            ("وارد کردن", "document-import", self.import_contacts),
            ("خروجی", "document-export", self.export_contacts),
            ("جستجو", "edit-find", self.search_contacts)
        ]
        
        for text, icon_name, callback in actions:
            action = QAction(QIcon.fromTheme(icon_name), text, self)
            action.triggered.connect(callback)
            toolbar.addAction(action)
            toolbar.addSeparator()
        
        # نوار جستجو
        search_layout = QHBoxLayout()
        search_layout.setAlignment(Qt.AlignRight)
        
        search_label = QLabel("جستجو:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("جستجو...")
        self.search_edit.setAlignment(Qt.AlignRight)
        self.search_edit.textChanged.connect(self.filter_contacts)
        
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_label)
        
        # جدول مخاطبین
        self.contacts_table = QTableWidget()
        self.contacts_table.setColumnCount(6)
        self.contacts_table.setHorizontalHeaderLabels([
            "نام", "نام خانوادگی", "شماره موبایل", "پست سازمانی", "شغل", "کد ملی"
        ])
        
        # تنظیمات جدول
        self.contacts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.contacts_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.contacts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.contacts_table.doubleClicked.connect(self.edit_contact)
        self.contacts_table.setLayoutDirection(Qt.RightToLeft)
        
        # تنظیم تراز سرستون‌ها به راست
        for i in range(self.contacts_table.columnCount()):
            item = self.contacts_table.horizontalHeaderItem(i)
            if item:
                item.setTextAlignment(Qt.AlignRight)
        
        # افزودن ویجت‌ها به لایه اصلی
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.contacts_table)
        
        # نوار وضعیت
        self.statusBar().showMessage("آماده")
        
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QToolBar {
                background-color: #e0e0e0;
                border: none;
                padding: 5px;
                spacing: 5px;
            }
            QToolButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #45a049;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #f2f2f2;
                selection-background-color: #bbdefb;
                gridline-color: #e0e0e0;
                font-family: B Nazanin;
                font-size: 18;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 5px;
                border: none;
                font-family: B Nazanin;
                font-size: 18;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-family: B Nazanin;
                font-size: 18;
            }
            QTextEdit {
                font-family: B Nazanin;
                font-size: 18;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-family: B Nazanin;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-family: B Nazanin;
                font-size: 18px;
            }
            QComboBox {
                font-family: B Nazanin;
                font-size: 18px;
            }
        """)
        
    def load_contacts(self):
        self.contacts_table.setRowCount(len(self.contact_manager.contacts))
        
        for row, contact in enumerate(self.contact_manager.contacts):
            items = [
                QTableWidgetItem(contact.first_name),
                QTableWidgetItem(contact.last_name),
                QTableWidgetItem(contact.mobile),
                QTableWidgetItem(contact.organizational_post),
                QTableWidgetItem(contact.job),
                QTableWidgetItem(contact.national_code)
            ]
            
            for i, item in enumerate(items):
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.contacts_table.setItem(row, i, item)
        
        self.statusBar().showMessage(f"تعداد مخاطبین: {len(self.contact_manager.contacts)}")
    
    def filter_contacts(self):
        query = self.search_edit.text().lower()
        for row in range(self.contacts_table.rowCount()):
            match = False
            for col in range(self.contacts_table.columnCount()):
                item = self.contacts_table.item(row, col)
                if item and query in item.text().lower():
                    match = True
                    break
            self.contacts_table.setRowHidden(row, not match)
    
    def add_contact(self):
        dialog = ContactDialog(self.contact_manager)
        if dialog.exec_() == QDialog.Accepted:
            self.load_contacts()
    
    def edit_contact(self):
        selected_row = self.contacts_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "اخطار", "لطفاً یک مخاطب را انتخاب کنید")
            return
        
        contact_id = self.contact_manager.contacts[selected_row].id
        contact = self.contact_manager.get_contact_by_id(contact_id)
        
        if contact:
            dialog = ContactDialog(self.contact_manager, contact, self)
            if dialog.exec_() == QDialog.Accepted:
                self.load_contacts()
    
    def delete_contact(self):
        selected_row = self.contacts_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "اخطار", "لطفاً یک مخاطب را انتخاب کنید")
            return
        
        contact_id = self.contact_manager.contacts[selected_row].id
        
        reply = QMessageBox.question(
            self, "تأیید حذف", 
            "آیا از حذف این مخاطب اطمینان دارید؟",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.contact_manager.delete_contact(contact_id)
            if success:
                self.load_contacts()
                QMessageBox.information(self, "موفقیت", message)
            else:
                QMessageBox.warning(self, "خطا", message)
    
    def copy_contact(self):
        selected_row = self.contacts_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "اخطار", "لطفاً یک مخاطب را انتخاب کنید")
            return
        
        contact = self.contact_manager.contacts[selected_row]
        
        contact_data = contact.to_dict()
        contact_data['id'] = str(uuid4())
        contact_data['first_name'] = f"{contact_data['first_name']} (کپی)"
        
        new_contact = Contact(**contact_data)
        success, message = self.contact_manager.add_contact(new_contact)
        
        if success:
            self.load_contacts()
            QMessageBox.information(self, "موفقیت", message)
        else:
            QMessageBox.warning(self, "خطا", message)
    
    def import_contacts(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "وارد کردن مخاطبین", "", 
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                
                imported_count = 0
                duplicate_count = 0
                
                for _, row in df.iterrows():
                    contact_data = {
                        'first_name': row.get('نام', ''),
                        'last_name': row.get('نام خانوادگی', ''),
                        'mobile': str(row.get('شماره موبایل', '')),
                        'national_code': str(row.get('کد ملی', '')),
                        'phone': str(row.get('شماره تلفن', '')),
                        'job': row.get('شغل', ''),
                        'organizational_post': row.get('پست سازمانی', ''),
                        'work_address': row.get('آدرس محل کار', ''),
                        'home_address': row.get('آدرس منزل', ''),
                        'marital_status': row.get('وضعیت تأهل', ''),
                        'blood_type': row.get('گروه خونی', ''),
                        'birth_date_solar': str(row.get('تاریخ تولد شمسی', '')),
                        'birth_date_gregorian': str(row.get('تاریخ تولد میلادی', ''))
                    }
                    
                    new_contact = Contact(**contact_data)
                    success, _ = self.contact_manager.add_contact(new_contact)
                    
                    if success:
                        imported_count += 1
                    else:
                        duplicate_count += 1
                
                self.load_contacts()
                QMessageBox.information(
                    self, "وارد کردن", 
                    f"تعداد {imported_count} مخاطب وارد شد.\n"
                    f"تعداد {duplicate_count} مخاطب تکراری نادیده گرفته شد."
                )
                
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در وارد کردن فایل: {str(e)}")
    
    def export_contacts(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "ذخیره مخاطبین", "", 
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                contacts_data = []
                for contact in self.contact_manager.contacts:
                    contacts_data.append({
                        'نام': contact.first_name,
                        'نام خانوادگی': contact.last_name,
                        'شماره موبایل': contact.mobile,
                        'کد ملی': contact.national_code,
                        'شماره تلفن': contact.phone,
                        'شغل': contact.job,
                        'پست سازمانی': contact.organizational_post,
                        'آدرس محل کار': contact.work_address,
                        'آدرس منزل': contact.home_address,
                        'وضعیت تأهل': contact.marital_status,
                        'گروه خونی': contact.blood_type,
                        'تاریخ تولد شمسی': contact.birth_date_solar,
                        'تاریخ تولد میلادی': contact.birth_date_gregorian
                    })
                
                df = pd.DataFrame(contacts_data)
                
                if file_path.endswith('.csv'):
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                else:
                    df.to_excel(file_path, index=False)
                
                QMessageBox.information(self, "موفقیت", "مخاطبین با موفقیت ذخیره شدند")
                
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ذخیره فایل: {str(e)}")
    
    def search_contacts(self):
        query, ok = QInputDialog.getText(self, "جستجو", "عبارت جستجو را وارد کنید:")
        if ok and query:
            results = self.contact_manager.search_contacts(query)
            
            if results:
                self.search_edit.setText(query)
                self.statusBar().showMessage(f"تعداد نتایج جستجو: {len(results)}")
            else:
                QMessageBox.information(self, "جستجو", "هیچ نتیجه‌ای یافت نشد")

def main():
    app = QApplication(sys.argv)
    
    # تنظیم فونت برای پشتیبانی از فارسی
    font = QFont("B Nazanin", 16)
    app.setFont(font)
    
    window = PhoneBookApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()