import sys
import json
import os
import subprocess
import ctypes
import socket
import logging
import re
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton, 
                             QLineEdit, QVBoxLayout, QHBoxLayout, QMessageBox, QFrame,
                             QProgressBar, QGroupBox)
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QLinearGradient, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal

# مسیر فایل JSON و لاگ
JSON_PATH = "C:/Program Files/syxtools/syxip.json"
LOG_FILE = "C:/Program Files/syxtools/syxip.log"

# تنظیمات لاگ
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger()

# تابع برای اجرای برنامه با دسترسی Administrator
def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            return False
        except Exception as e:
            logger.error(f"Failed to run as admin: {str(e)}")
            return False

# تابع برای خواندن فایل JSON
def read_json_file():
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {JSON_PATH}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error reading JSON: {str(e)}")
        return None

# کلاس کارگر برای تغییر تنظیمات شبکه در پس زمینه
class NetworkWorker(QThread):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)
    
    def __init__(self, profile, interface_name):
        super().__init__()
        self.profile = profile
        self.interface_name = interface_name
    
    def run(self):
        try:
            success, message = self.apply_network_settings()
            self.finished.emit(success, message)
        except Exception as e:
            logger.error(f"Network worker error: {str(e)}")
            self.finished.emit(False, f"خطای داخلی: {str(e)}")
    
    def apply_network_settings(self):
        # روش 1: استفاده از netsh (روش اصلی)
        self.progress.emit(20)
        if self.method_netsh():
            logger.info(f"Successfully applied settings using netsh for {self.profile['name']}")
            return True, f"تنظیمات با موفقیت اعمال شد"
        
        # روش 2: استفاده از PowerShell
        self.progress.emit(40)
        if self.method_powershell():
            logger.info(f"Successfully applied settings using PowerShell for {self.profile['name']}")
            return True, f"تنظیمات با موفقیت اعمال شد"
        
        logger.error(f"All methods failed for {self.profile['name']}")
        return False, "تمام روش‌ها برای تغییر تنظیمات شبکه با شکست مواجه شدند"
    
    def method_netsh(self):
        try:
            # تنظیم آدرس IP
            cmd_set_ip = f'netsh interface ip set address name="{self.interface_name}" static {self.profile["ip"]} {self.profile["subnet"]} {self.profile["gateway"]}'
            result = subprocess.run(cmd_set_ip, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.returncode != 0:
                logger.warning(f"netsh IP setting failed: {result.stderr}")
                return False
            
            # تنظیم DNS
            if self.profile["dns1"]:
                cmd_set_dns1 = f'netsh interface ip set dns name="{self.interface_name}" static {self.profile["dns1"]}'
                result_dns1 = subprocess.run(cmd_set_dns1, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                if result_dns1.returncode != 0:
                    logger.warning(f"netsh DNS1 setting failed: {result_dns1.stderr}")
            
            if self.profile["dns2"]:
                cmd_set_dns2 = f'netsh interface ip add dns name="{self.interface_name}" {self.profile["dns2"]} index=2'
                result_dns2 = subprocess.run(cmd_set_dns2, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                if result_dns2.returncode != 0:
                    logger.warning(f"netsh DNS2 setting failed: {result_dns2.stderr}")
            
            return True
        except Exception as e:
            logger.error(f"Error in method_netsh: {str(e)}")
            return False
    
    def method_powershell(self):
        try:
            # تنظیم IP با PowerShell
            ps_script = f'''
                $interface = Get-NetAdapter -Name "{self.interface_name}" -ErrorAction SilentlyContinue
                if (-not $interface) {{ $interface = Get-NetAdapter | Where-Object {{ $_.Status -eq 'Up' }} | Select-Object -First 1 }}
                $interface | Set-NetIPInterface -Dhcp Disabled
                $interface | New-NetIPAddress -IPAddress {self.profile["ip"]} -PrefixLength 24 -DefaultGateway {self.profile["gateway"]} -ErrorAction Stop | Out-Null
                Set-DnsClientServerAddress -InterfaceIndex $interface.ifIndex -ServerAddresses {self.profile["dns1"]},{self.profile["dns2"]} -ErrorAction Stop
            '''
            result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True, encoding='utf-8', errors='ignore')
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error in method_powershell: {str(e)}")
            return False

# تابع برای تشخیص رابط شبکه فعال
def get_active_network_interface():
    try:
        result = subprocess.run("netsh interface show interface", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        lines = result.stdout.split('\n')
        
        # جستجوی رابط فعال (فارسی و انگلیسی)
        for line in lines:
            if ("Connected" in line or "متصل" in line) and ("Dedicated" in line or "اختصاصی" in line):
                parts = line.split()
                if len(parts) > 3:
                    return parts[-1]
        
        # جستجوی جایگزین
        for line in lines:
            if ("Connected" in line or "متصل" in line):
                parts = line.split()
                if len(parts) > 3:
                    return parts[-1]
        
        return "Ethernet"  # Fallback
    except Exception as e:
        logger.error(f"Error detecting network interface: {str(e)}")
        return "Ethernet"

# تابع برای پینگ گرفتن
def ping_ip(ip, timeout=3):
    try:
        subprocess.check_output(f"ping -n 1 -w {timeout*1000} {ip}", shell=True, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False
    except Exception:
        return False

# تابع برای دریافت تنظیمات IP فعلی
def get_current_ip_config():
    try:
        result = subprocess.run("ipconfig /all", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        return result.stdout
    except Exception as e:
        logger.error(f"Error getting IP config: {str(e)}")
        return ""

# تابع بهبود یافته برای استخراج IP فعلی
def get_current_ip(interface_name):
    try:
        result = subprocess.run("ipconfig", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        output = result.stdout

        # حالت‌های مختلف نام رابط در ipconfig
        possible_titles = [
            f"adapter {interface_name}:",           # انگلیسی
            f"آداپتور {interface_name}:",           # فارسی
            f"Adapter {interface_name}:",           # برخی ویندوزها
            f"{interface_name}:"                    # حالت ساده
        ]

        lines = output.splitlines()
        in_section = False
        for i, line in enumerate(lines):
            # شروع بخش رابط شبکه
            if any(title.lower() in line.lower() for title in possible_titles):
                in_section = True
                continue
            if in_section:
                # پایان بخش رابط با خط خالی
                if line.strip() == "":
                    break
                # جستجوی آدرس IPv4
                if ("IPv4" in line or "آدرس IPv4" in line or "IP Address" in line or "آدرس آی‌پی" in line):
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        return match.group(1)
        return "یافت نشد"
    except Exception as e:
        logger.error(f"Error extracting IP: {str(e)}")
        return "خطا در استخراج"

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ورود به سیستم")
        self.setWindowIcon(QIcon("icon.ico"))
        self.setFixedSize(500, 400)
        self.json_data = None
        
        # خواندن فایل JSON
        self.load_json_data()
        
        self.init_ui()
        self.center()
    
    def center(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)
    
    def load_json_data(self):
        self.json_data = read_json_file()
        if not self.json_data:
            QMessageBox.critical(self, "خطای بحرانی", 
                "خطا در خواندن فایل پیکربندی!\n\n"
                "لطفاً از موارد زیر اطمینان حاصل کنید:\n"
                "1. فایل در مسیر C:/Program Files/syxtools/syxip.json وجود دارد\n"
                "2. فرمت فایل JSON صحیح است\n"
                "3. برنامه با دسترسی Administrator اجرا شده است\n\n"
                "جزئیات خطا در فایل لاگ ثبت شده است.")
            sys.exit(1)
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setAlignment(Qt.AlignCenter)
        
        # لوگو
        logo_label = QLabel()
        if hasattr(sys, '_MEIPASS'):
            logo_path = os.path.join(sys._MEIPASS, 'logo.png')
        else:
            logo_path = 'logo.png'
        
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("لوگو")
        logo_label.setAlignment(Qt.AlignCenter)
        
        # عنوان
        title = QLabel("سوئیچر شبکه")
        title.setFont(QFont("B Nazanin", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #3498db; margin-bottom: 10px;")
        
        # دستورالعمل
        instruction = QLabel("لطفاً کد ملی خود را وارد کنید:")
        instruction.setFont(QFont("B Nazanin", 14))
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setStyleSheet("color: #ecf0f1;")
        
        # فیلد ورود کد ملی
        self.national_id_input = QLineEdit()
        self.national_id_input.setFont(QFont("B Nazanin", 16))
        self.national_id_input.setPlaceholderText("کد ملی")
        self.national_id_input.setEchoMode(QLineEdit.Password)
        self.national_id_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 12px;
                min-height: 40px;
            }
            QLineEdit:focus {
                border-color: #1abc9c;
            }
        """)
        
        # دکمه ورود
        login_btn = QPushButton("ورود به سیستم")
        login_btn.setFont(QFont("B Nazanin", 14, QFont.Bold))
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
                margin-top: 10px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1d6fa5;
            }
        """)
        login_btn.clicked.connect(self.check_login)
        
        # نسخه برنامه
        version = QLabel("نسخه 4.0 - رفع مشکلات استخراج IP")
        version.setFont(QFont("B Nazanin", 10))
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("color: #7f8c8d; margin-top: 20px;")
        
        # افزودن ویجت‌ها به لایه
        layout.addWidget(logo_label)
        layout.addWidget(title)
        layout.addWidget(instruction)
        layout.addWidget(self.national_id_input)
        layout.addWidget(login_btn)
        layout.addWidget(version)
        
        # تنظیم تم تاریک
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0, QColor(30, 39, 46))
        gradient.setColorAt(1, QColor(44, 62, 80))
        
        palette.setBrush(QPalette.Window, gradient)
        palette.setColor(QPalette.WindowText, QColor(236, 240, 241))
        palette.setColor(QPalette.Button, QColor(52, 152, 219))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Base, QColor(52, 73, 94))
        palette.setColor(QPalette.AlternateBase, QColor(44, 62, 80))
        self.setPalette(palette)
        
        self.setLayoutDirection(Qt.RightToLeft)
        self.setLayout(layout)
    
    def check_login(self):
        national_id = self.national_id_input.text()
        if national_id == self.json_data.get("national_id", ""):
            self.main_window = MainWindow(self.json_data)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "خطای احراز هویت", 
                "کد ملی وارد شده صحیح نیست!\n\n"
                "لطفاً دقت کنید:\n"
                "1. کد ملی باید دقیقاً مطابق فایل پیکربندی باشد\n"
                "2. در صورت فراموشی کد ملی با مدیر سیستم تماس بگیرید")

class MainWindow(QMainWindow):
    def __init__(self, json_data):
        super().__init__()
        self.json_data = json_data
        self.interface_name = get_active_network_interface()
        self.current_profile = None
        self.setWindowTitle("سوئیچر شبکه syxtools")
        self.setWindowIcon(QIcon("icon.ico"))
        self.setMinimumSize(900, 700)
        
        # ایجاد ویجت مرکزی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # لایه اصلی
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # ایجاد استایل برای برنامه
        self.apply_style()
        self.init_ui(main_layout)
        
        # تایمر برای بررسی وضعیت شبکه
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_network_info)
        self.status_timer.start(10000)  # هر 10 ثانیه
        
        # بررسی اولیه وضعیت شبکه
        self.update_network_info()
    
    def apply_style(self):
        # ایجاد یک پالت برای تم تاریک
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 800)
        gradient.setColorAt(0, QColor(30, 39, 46))
        gradient.setColorAt(1, QColor(44, 62, 80))
        
        palette.setBrush(QPalette.Window, gradient)
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Button, QColor(52, 152, 219))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Base, QColor(52, 73, 94, 200))
        palette.setColor(QPalette.AlternateBase, QColor(44, 62, 80))
        
        self.setPalette(palette)
        self.setLayoutDirection(Qt.RightToLeft)
    
    def init_ui(self, main_layout):
        # هدر برنامه
        header = QLabel(f"خوش آمدید {self.json_data['username']}")
        header.setFont(QFont("B Nazanin", 28, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #3498db; margin-bottom: 20px;")
        
        # نمایش نام کاربری
        username_label = QLabel(f"کاربر جاری: {self.json_data['username']} | رابط شبکه: {self.interface_name}")
        username_label.setFont(QFont("B Nazanin", 14))
        username_label.setAlignment(Qt.AlignCenter)
        username_label.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                background-color: rgba(44, 62, 80, 150);
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 20px;
            }
        """)
        
        # عنوان پروفایل‌ها
        profiles_title = QLabel("پروفایل‌های شبکه")
        profiles_title.setFont(QFont("B Nazanin", 18, QFont.Bold))
        profiles_title.setStyleSheet("color: #1abc9c; margin-bottom: 15px;")
        profiles_title.setAlignment(Qt.AlignCenter)
        
        # لایه دکمه‌ها
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(40)
        buttons_layout.setAlignment(Qt.AlignCenter)
        
        # ایجاد دکمه‌ها برای پروفایل‌ها
        self.profile_buttons = []
        for i, profile in enumerate(self.json_data["profiles"], start=1):
            btn = self.create_profile_button(profile, i)
            buttons_layout.addWidget(btn)
            self.profile_buttons.append(btn)
        
        # نوار پیشرفت
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498db;
                border-radius: 5px;
                background-color: #2c3e50;
                height: 20px;
                margin: 15px 0;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                width: 10px;
            }
        """)
        self.progress_bar.hide()
        
        # گروه وضعیت شبکه
        status_group = QGroupBox("مراحل تأیید شبکه")
        status_group.setFont(QFont("B Nazanin", 14, QFont.Bold))
        status_group.setStyleSheet("""
            QGroupBox {
                color: #1abc9c;
                background-color: rgba(44, 62, 80, 180);
                border-radius: 15px;
                padding: 20px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        
        status_layout = QVBoxLayout(status_group)
        
        # گزارش وضعیت سه مرحله‌ای
        self.ip_status = QLabel("◻️ مرحله 1: وضعیت IP - در انتظار تغییر پروفایل")
        self.ip_status.setFont(QFont("B Nazanin", 12))
        self.ip_status.setStyleSheet("color: #f1c40f; margin-bottom: 8px;")
        
        self.network_status = QLabel("◻️ مرحله 2: اتصال به شبکه - در انتظار تغییر پروفایل")
        self.network_status.setFont(QFont("B Nazanin", 12))
        self.network_status.setStyleSheet("color: #f1c40f; margin-bottom: 8px;")
        
        self.internet_status = QLabel("◻️ مرحله 3: اتصال به اینترنت - در انتظار تغییر پروفایل")
        self.internet_status.setFont(QFont("B Nazanin", 12))
        self.internet_status.setStyleSheet("color: #f1c40f;")
        
        status_layout.addWidget(self.ip_status)
        status_layout.addWidget(self.network_status)
        status_layout.addWidget(self.internet_status)
        
        # بخش اطلاعات شبکه فعلی
        ip_group = QGroupBox("اطلاعات شبکه فعلی")
        ip_group.setFont(QFont("B Nazanin", 14, QFont.Bold))
        ip_group.setStyleSheet("""
            QGroupBox {
                color: #3498db;
                background-color: rgba(44, 62, 80, 180);
                border-radius: 15px;
                padding: 20px;
                margin-top: 20px;
            }
        """)
        
        ip_layout = QVBoxLayout(ip_group)
        
        self.ip_info = QLabel("در حال دریافت اطلاعات شبکه...")
        self.ip_info.setFont(QFont("B Nazanin", 12))
        self.ip_info.setAlignment(Qt.AlignCenter)
        self.ip_info.setStyleSheet("color: #bdc3c7;")
        
        ip_layout.addWidget(self.ip_info)
        
        # بخش گزارش خطا
        error_frame = QFrame()
        error_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(192, 57, 43, 100);
                border-radius: 15px;
                padding: 20px;
                margin-top: 20px;
            }
        """)
        
        error_layout = QVBoxLayout(error_frame)
        
        error_title = QLabel("سیستم گزارش خطا")
        error_title.setFont(QFont("B Nazanin", 16, QFont.Bold))
        error_title.setStyleSheet("color: #ecf0f1; margin-bottom: 10px;")
        error_title.setAlignment(Qt.AlignCenter)
        
        self.error_label = QLabel("آخرین خطا: سیستم بدون خطا فعالیت می‌کند")
        self.error_label.setFont(QFont("B Nazanin", 11))
        self.error_label.setStyleSheet("color: #ecf0f1;")
        self.error_label.setWordWrap(True)
        
        contact_label = QLabel("در صورت بروز خطای مکرر با مدیر سیستم تماس بگیرید: پشتیبانی@syxtools.com")
        contact_label.setFont(QFont("B Nazanin", 10))
        contact_label.setStyleSheet("color: #f1c40f; margin-top: 15px;")
        contact_label.setAlignment(Qt.AlignCenter)
        
        error_layout.addWidget(error_title)
        error_layout.addWidget(self.error_label)
        error_layout.addWidget(contact_label)
        
        # افزودن ویجت‌ها به لایه اصلی
        main_layout.addWidget(header)
        main_layout.addWidget(username_label)
        main_layout.addWidget(profiles_title)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(status_group)
        main_layout.addWidget(ip_group)
        main_layout.addWidget(error_frame)
    
    def create_profile_button(self, profile, index):
        btn = QPushButton()
        btn.setMinimumSize(300, 150)
        
        layout = QVBoxLayout(btn)
        layout.setAlignment(Qt.AlignCenter)
        
        # آیکون پروفایل
        icon_label = QLabel()
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, f'profile_{index}.png')
        else:
            icon_path = f'profile_{index}.png'
        
        if os.path.exists(icon_path):
            icon_pixmap = QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(icon_pixmap)
        else:
            icon_label.setText(profile['name'][0])
        icon_label.setAlignment(Qt.AlignCenter)
        
        # نام پروفایل
        name_label = QLabel(profile['name'])
        name_label.setFont(QFont("B Nazanin", 18, QFont.Bold))
        name_label.setStyleSheet("color: #ecf0f1;")
        name_label.setAlignment(Qt.AlignCenter)
        
        # اطلاعات IP
        ip_label = QLabel(f"IP: {profile['ip']}")
        ip_label.setFont(QFont("B Nazanin", 12))
        ip_label.setStyleSheet("color: #bdc3c7;")
        ip_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(icon_label)
        layout.addWidget(name_label)
        layout.addWidget(ip_label)
        
        # استایل دکمه
        btn.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                border: 2px solid #3498db;
                border-radius: 15px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #34495e;
                border-color: #1abc9c;
            }
        """)
        
        btn.clicked.connect(lambda _, p=profile: self.apply_profile(p))
        return btn
    
    def apply_profile(self, profile):
        # بازنشانی وضعیت‌ها
        self.reset_status_labels()
        
        self.current_profile = profile
        
        # غیرفعال کردن دکمه‌ها هنگام اعمال تغییرات
        for btn in self.profile_buttons:
            btn.setEnabled(False)
        
        # نمایش نوار پیشرفت
        self.progress_bar.show()
        self.ip_status.setText("🔄 مرحله 1: در حال اعمال تنظیمات شبکه...")
        self.ip_status.setStyleSheet("color: #f39c12;")
        
        # ایجاد کارگر شبکه
        self.worker = NetworkWorker(profile, self.interface_name)
        self.worker.finished.connect(self.on_network_settings_applied)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.start()
    
    def reset_status_labels(self):
        self.ip_status.setText("◻️ مرحله 1: وضعیت IP - در انتظار تغییر پروفایل")
        self.ip_status.setStyleSheet("color: #f1c40f;")
        
        self.network_status.setText("◻️ مرحله 2: اتصال به شبکه - در انتظار تغییر پروفایل")
        self.network_status.setStyleSheet("color: #f1c40f;")
        
        self.internet_status.setText("◻️ مرحله 3: اتصال به اینترنت - در انتظار تغییر پروفایل")
        self.internet_status.setStyleSheet("color: #f1c40f;")
    
    def on_network_settings_applied(self, success, message):
        # فعال کردن مجدد دکمه‌ها
        for btn in self.profile_buttons:
            btn.setEnabled(True)
        
        # مخفی کردن نوار پیشرفت
        self.progress_bar.hide()
        
        if success:
            # تأخیر برای اطمینان از اعمال تنظیمات
            QTimer.singleShot(5000, self.verify_ip_settings)
        else:
            error_msg = f"خطا در اعمال تنظیمات: {message}\n\nاین نسخه از نرم افزار قادر به اعمال تنظیمات نیست.\nلطفاً با مدیر سیستم تماس بگیرید."
            self.error_label.setText(f"آخرین خطا: {error_msg}")
            self.ip_status.setText("❌ مرحله 1: خطا در اعمال تنظیمات شبکه")
            self.ip_status.setStyleSheet("color: #e74c3c;")
            logger.error(error_msg)
            
            # نمایش پیام خطا به کاربر
            QMessageBox.critical(self, "خطای فنی", error_msg)
    
    def verify_ip_settings(self):
        try:
            # دریافت IP فعلی
            current_ip = get_current_ip(self.interface_name)
            
            if current_ip == self.current_profile["ip"]:
                self.ip_status.setText("✅ مرحله 1: IP دستگاه با پروفایل مطابقت دارد")
                self.ip_status.setStyleSheet("color: #2ecc71;")
                
                # بررسی اتصال به شبکه
                self.network_status.setText("🔄 مرحله 2: در حال بررسی اتصال به شبکه...")
                self.network_status.setStyleSheet("color: #f39c12;")
                QTimer.singleShot(3000, self.check_network_connection)
            else:
                self.ip_status.setText(f"❌ مرحله 1: IP فعلی ({current_ip}) با پروفایل ({self.current_profile['ip']}) مطابقت ندارد")
                self.ip_status.setStyleSheet("color: #e74c3c;")
                self.error_label.setText(f"آخرین خطا: IP فعلی ({current_ip}) با پروفایل ({self.current_profile['ip']}) مطابقت ندارد")
        except Exception as e:
            self.ip_status.setText("❌ مرحله 1: خطا در بررسی تطابق IP")
            self.ip_status.setStyleSheet("color: #e74c3c;")
            logger.error(f"Error verifying IP settings: {str(e)}")
    
    def check_network_connection(self):
        try:
            # بررسی اتصال به گیتوی پروفایل
            gateway = self.current_profile["gateway"]
            if gateway and ping_ip(gateway):
                self.network_status.setText(f"✅ مرحله 2: اتصال به شبکه {self.current_profile['name']} برقرار است")
                self.network_status.setStyleSheet("color: #2ecc71;")
                
                # بررسی اتصال به اینترنت
                self.internet_status.setText("🔄 مرحله 3: در حال بررسی اتصال به اینترنت...")
                self.internet_status.setStyleSheet("color: #f39c12;")
                QTimer.singleShot(3000, self.check_internet_connection)
            else:
                self.network_status.setText(f"❌ مرحله 2: اتصال به شبکه {self.current_profile['name']} برقرار نیست")
                self.network_status.setStyleSheet("color: #e74c3c;")
                self.error_label.setText(f"آخرین خطا: اتصال به شبکه {self.current_profile['name']} برقرار نیست")
        except Exception as e:
            self.network_status.setText("❌ مرحله 2: خطا در بررسی اتصال شبکه")
            self.network_status.setStyleSheet("color: #e74c3c;")
            logger.error(f"Error checking network connection: {str(e)}")
    
    def check_internet_connection(self):
        try:
            # بررسی اتصال به اینترنت از طریق DNS پروفایل
            dns_server = self.current_profile["dns1"] or "8.8.8.8"
            if ping_ip(dns_server):
                self.internet_status.setText("✅ مرحله 3: اتصال به اینترنت برقرار است")
                self.internet_status.setStyleSheet("color: #2ecc71;")
                
                # نمایش پیام موفقیت
                QMessageBox.information(self, "تغییر موفق", 
                    f"پروفایل {self.current_profile['name']} با موفقیت اعمال شد\n\n"
                    f"• IP فعلی: {self.current_profile['ip']}\n"
                    f"• اتصال به شبکه: برقرار\n"
                    f"• اتصال به اینترنت: برقرار")
            else:
                self.internet_status.setText("❌ مرحله 3: اتصال به اینترنت برقرار نیست")
                self.internet_status.setStyleSheet("color: #e74c3c;")
                self.error_label.setText("آخرین خطا: اتصال به اینترنت برقرار نیست")
                
                # نمایش پیام هشدار
                QMessageBox.warning(self, "تغییر با هشدار", 
                    f"پروفایل {self.current_profile['name']} اعمال شد اما:\n\n"
                    f"• اتصال به شبکه: برقرار\n"
                    f"• اتصال به اینترنت: برقرار نیست\n\n"
                    f"لطفاً تنظیمات DNS را بررسی کنید")
        except Exception as e:
            self.internet_status.setText("❌ مرحله 3: خطا در بررسی اتصال اینترنت")
            self.internet_status.setStyleSheet("color: #e74c3c;")
            logger.error(f"Error checking internet connection: {str(e)}")
    
    def update_network_info(self):
        try:
            # دریافت IP فعلی
            current_ip = get_current_ip(self.interface_name)
            
            # نمایش اطلاعات
            self.ip_info.setText(f"IP فعلی: {current_ip}")
            
            # به‌روزرسانی خودکار وضعیت اینترنت
            if ping_ip("8.8.8.8"):
                self.internet_status.setText("✅ مرحله 3: اتصال به اینترنت برقرار است (بروزرسانی خودکار)")
                self.internet_status.setStyleSheet("color: #2ecc71;")
            else:
                self.internet_status.setText("❌ مرحله 3: اتصال به اینترنت برقرار نیست (بروزرسانی خودکار)")
                self.internet_status.setStyleSheet("color: #e74c3c;")
            
        except Exception as e:
            logger.error(f"Error in network status update: {str(e)}")

if __name__ == "__main__":
    # درخواست دسترسی Administrator
    if not run_as_admin():
        sys.exit(0)
    
    app = QApplication(sys.argv)
    
    # تنظیم فونت پیشفرض برای برنامه
    try:
        font = QFont("B Nazanin", 12)
        app.setFont(font)
    except:
        # فونت جایگزین برای ویندوزهایی که فونت فارسی ندارند
        font = QFont("Arial", 10)
        app.setFont(font)
    
    # بررسی وجود فایل JSON
    if not os.path.exists(JSON_PATH):
        error_msg = f"فایل پیکربندی در مسیر {JSON_PATH} یافت نشد!\nبرنامه نمی‌تواند ادامه دهد."
        logger.critical(error_msg)
        QMessageBox.critical(None, "خطای بحرانی", error_msg)
        sys.exit(1)
    
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())