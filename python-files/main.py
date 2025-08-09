
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
برنامج إدارة تأجير الشقق والفواتير
نظام شامل لإدارة العقارات والمستأجرين والفواتير
مع نظام تسجيل دخول آمن
"""

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database import DatabaseManager
from ui.main_window import MainWindow
from ui.login_dialog import LoginDialog

class RentalManagementApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        
        # إعداد الخط العربي
        self.setup_arabic_font()
        
        # متغيرات المستخدم الحالي
        self.current_user = None
        self.db_manager = None
        self.main_window = None
        
        # بدء عملية تسجيل الدخول
        self.start_login_process()
    
    def setup_arabic_font(self):
        """إعداد الخط العربي للتطبيق"""
        # تحديد خط عربي مناسب
        arabic_font = QFont("Arial Unicode MS", 10)
        arabic_font.setStyleHint(QFont.System)
        self.setFont(arabic_font)
        
        # إعداد اتجاه النص من اليمين لليسار
        self.setLayoutDirection(Qt.RightToLeft)
    
    def start_login_process(self):
        """بدء عملية تسجيل الدخول"""
        login_dialog = LoginDialog()
        
        # عرض نافذة تسجيل الدخول
        if login_dialog.exec_() == QDialog.Accepted and login_dialog.login_successful:
            self.current_user = login_dialog.current_user
            self.start_main_application()
        else:
            # إذا تم إلغاء تسجيل الدخول، إغلاق التطبيق
            self.quit()
    
    def start_main_application(self):
        """بدء التطبيق الرئيسي بعد تسجيل الدخول بنجاح"""
        try:
            # إنشاء قاعدة البيانات
            self.db_manager = DatabaseManager()
            
            # إنشاء النافذة الرئيسية مع معلومات المستخدم
            self.main_window = MainWindow(self.db_manager, self.current_user)
            self.main_window.show()
            
            # عرض رسالة ترحيب
            self.show_welcome_message()
            
        except Exception as e:
            QMessageBox.critical(None, "خطأ", f"فشل في تشغيل التطبيق:\n{str(e)}")
            self.quit()
    
    def show_welcome_message(self):
        """عرض رسالة ترحيب"""
        user_name = self.current_user.get('full_name', self.current_user.get('username', 'المستخدم'))
        role_text = "المدير" if self.current_user.get('role') == 'admin' else "المستخدم"
        
        welcome_msg = f"مرحباً {user_name}\nتم تسجيل الدخول بصفة {role_text}"
        
        # عرض الرسالة في شريط الحالة
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(f"مرحباً {user_name} - {role_text}", 5000)

class SplashScreen(QSplashScreen):
    """شاشة البداية"""
    def __init__(self):
        # إنشاء صورة بسيطة للشاشة
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor(52, 73, 94))
        
        super().__init__(pixmap)
        
        # إعداد النص
        self.setStyleSheet("""
            QSplashScreen {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        # عرض رسالة التحميل
        self.showMessage("جاري تحميل نظام إدارة تأجير الشقق...", 
                        Qt.AlignCenter | Qt.AlignBottom, Qt.white)

def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    app = RentalManagementApp(sys.argv)
    
    # إعداد معلومات التطبيق
    app.setApplicationName("نظام إدارة تأجير الشقق")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("نظام إدارة العقارات")
    
    # إعداد أيقونة التطبيق
    if os.path.exists('assets/icon.png'):
        app.setWindowIcon(QIcon('assets/icon.png'))
    elif os.path.exists('assets/icon.ico'):
        app.setWindowIcon(QIcon('assets/icon.ico'))
    
    # تشغيل التطبيق
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()