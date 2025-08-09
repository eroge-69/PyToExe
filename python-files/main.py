#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
برنامج إدارة تأجير الشقق
نظام شامل لإدارة العقود والإيجارات والفواتير
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QMessageBox, QDialog
from PyQt5.QtWidgets import QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtWidgets import QComboBox, QDateEdit, QSpinBox, QTextEdit, QGroupBox
from PyQt5.QtWidgets import QFormLayout, QGridLayout, QFrame, QSplitter
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap

from config import APP_CONFIG, ensure_directories
from database import DatabaseManager
from auth import AuthManager
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow

class ApartmentRentalApp:
    def __init__(self):
        # التأكد من وجود المجلدات المطلوبة
        ensure_directories()
        
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_CONFIG['name'])
        self.app.setApplicationVersion(APP_CONFIG['version'])
        
        # تطبيق الثيم العربي
        self.setup_arabic_theme()
        
        # إنشاء مدير قاعدة البيانات
        self.db_manager = DatabaseManager()
        
        # إنشاء مدير المصادقة
        self.auth_manager = AuthManager(self.db_manager)
        
        # متغير لحفظ النافذة الرئيسية
        self.main_window = None
        
    def setup_arabic_theme(self):
        """إعداد الثيم العربي للتطبيق"""
        # تحديد الخط العربي
        font = QFont("Tahoma", 10)
        font.setStyleHint(QFont.SansSerif)
        self.app.setFont(font)
        
        # تطبيق ستايل شيت عربي
        style = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            background-color: white;
        }
        
        QTabBar::tab {
            background-color: #e1e1e1;
            border: 1px solid #c0c0c0;
            padding: 8px 16px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: white;
            border-bottom-color: white;
        }
        
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #106ebe;
        }
        
        QPushButton:pressed {
            background-color: #005a9e;
        }
        
        QLineEdit, QComboBox, QDateEdit, QSpinBox {
            border: 1px solid #c0c0c0;
            padding: 6px;
            border-radius: 3px;
            background-color: white;
        }
        
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {
            border: 2px solid #0078d4;
        }
        
        QTableWidget {
            gridline-color: #d0d0d0;
            background-color: white;
            alternate-background-color: #f9f9f9;
        }
        
        QTableWidget::item {
            padding: 8px;
        }
        
        QTableWidget::item:selected {
            background-color: #0078d4;
            color: white;
        }
        
        QHeaderView::section {
            background-color: #e1e1e1;
            padding: 8px;
            border: 1px solid #c0c0c0;
            font-weight: bold;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #c0c0c0;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        """
        
        self.app.setStyleSheet(style)
        
        # تحديد اتجاه النص من اليمين لليسار
        self.app.setLayoutDirection(Qt.RightToLeft)
    
    def run(self):
        """تشغيل التطبيق"""
        try:
            # إنشاء قاعدة البيانات إذا لم تكن موجودة
            self.db_manager.create_tables()
            
            # عرض نافذة تسجيل الدخول
            login_dialog = LoginDialog(self.auth_manager)
            
            if login_dialog.exec_() == QDialog.Accepted:
                # إنشاء النافذة الرئيسية
                self.main_window = MainWindow(self.db_manager, self.auth_manager)
                self.main_window.show()
                
                # تشغيل حلقة الأحداث
                return self.app.exec_()
            else:
                return 0
                
        except Exception as e:
            QMessageBox.critical(None, "خطأ", f"حدث خطأ في تشغيل التطبيق:\n{str(e)}")
            return 1

def main():
    """النقطة الرئيسية لتشغيل التطبيق"""
    app = ApartmentRentalApp()
    sys.exit(app.run())

if __name__ == "__main__":
    main()