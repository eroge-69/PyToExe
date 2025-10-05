# -*- coding: utf-8 -*-
"""
ActivationApp.py

یک نمونه اپ دسکتاپ ساده با PyQt5 که صفحه‌ای مدرن باز می‌کند و از کاربر
می‌خواهد کد فعال‌سازی وارد کند. هر ورودی - حتی اگر صحیح باشد - همواره
خطا نشان داده و پیغام می‌دهد که "کد معتبر وارد کنید".

ساخت exe (نمونه):
1. نصب پیش‌نیازها:
   pip install pyqt5
2. ساخت فایل تک اجرایی (ویندوز):
   pip install pyinstaller
   pyinstaller --onefile --windowed ActivationApp.py
   (بعد از اجرا پوشه dist/ActivationApp.exe ساخته می‌شود)

توضیحات: برای تغییر متن‌ها، استایل یا منطق پاسخ‌دهی، کافی‌ست در کد
تعدیل کنید. در حال حاضر منطق بررسی کد به‌صورت "همیشه نامعتبر" عمل می‌کند.
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt


class ActivationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Activation — Demo")
        self.setFixedSize(420, 240)
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        # Header
        header = QLabel("فعالسازی نرم‌افزار")
        header.setAlignment(Qt.AlignCenter)
        header.setObjectName("header")

        # Instruction
        instr = QLabel("لطفاً کد فعال‌سازی خود را وارد کنید:")
        instr.setAlignment(Qt.AlignLeft)
        instr.setObjectName("instr")

        # Input + button
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("کد فعال‌سازی را وارد کنید")
        self.code_input.setObjectName("code_input")
        self.code_input.returnPressed.connect(self.on_submit)

        submit_btn = QPushButton("فعال‌سازی")
        submit_btn.clicked.connect(self.on_submit)
        submit_btn.setObjectName("submit_btn")

        # Layouts
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.code_input)
        h_layout.addWidget(submit_btn)

        v_layout = QVBoxLayout(central)
        v_layout.addStretch(1)
        v_layout.addWidget(header)
        v_layout.addSpacing(8)
        v_layout.addWidget(instr)
        v_layout.addLayout(h_layout)
        v_layout.addStretch(2)

        # Apply stylesheet for modern look
        self.setStyleSheet(r'''
            QWidget { background: qlineargradient(x1:0 y1:0, x2:1 y2:1,
                        stop:0 #f7f9fc, stop:1 #ffffff); font-family: "Segoe UI", Tahoma, Arial; }
            #header { font-size: 20px; font-weight: 600; color: #222; }
            #instr { font-size: 12px; color: #444; }
            QLineEdit#code_input { padding: 10px; border-radius: 8px; border: 1px solid #d0d7de; min-width: 220px; }
            QPushButton#submit_btn { padding: 10px 16px; border-radius: 8px; border: none; background: qlineargradient(x1:0 y1:0, x2:0 y2:1, stop:0 #3b82f6, stop:1 #2563eb); color: white; font-weight: 600; }
            QPushButton#submit_btn:hover { background: qlineargradient(x1:0 y1:0, x2:0 y2:1, stop:0 #60a5fa, stop:1 #3b82f6); }
        ''')

    def on_submit(self):
        entered = self.code_input.text().strip()
        # منطق: هر چیزی وارد شود، خطا نشان داده شده و درخواست کد معتبر می‌شود
        self.show_invalid(entered)

    def show_invalid(self, value):
        msg = QMessageBox(self)
        msg.setWindowTitle("خطا در فعال‌سازی")
        # پیام می‌تواند فارسی یا انگلیسی باشد — اینجا فارسی است
        msg.setText("کد وارد شده معتبر نیست.")
        msg.setInformativeText("لطفاً از یک کد فعال‌سازی معتبر استفاده کنید.")
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        # پس از بستن پیام، می‌توان ورودی را خالی کرد یا انتخاب‌شده نگه داشت
        self.code_input.selectAll()
        self.code_input.setFocus()


def main():
    app = QApplication(sys.argv)
    win = ActivationWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
