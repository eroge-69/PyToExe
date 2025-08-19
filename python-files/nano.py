# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: main.py
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QSizePolicy, QSpacerItem, QGraphicsDropShadowEffect, QDialog, QLineEdit, QMessageBox, QScrollArea, QGridLayout, QComboBox, QProgressBar, QStyledItemDelegate, QStyle, QLayout, QAbstractScrollArea
from PySide6.QtGui import QIcon, QFont, QColor, QDesktopServices, QPixmap, QPainter, QBrush, QPen
from PySide6.QtCore import Qt, QSize, QUrl, QPropertyAnimation, QEasingCurve, QTimer, QRect, QPoint
import subprocess
import os
import shutil
import tempfile
import time
import atexit
import psutil
import ctypes
import hashlib
import json
from datetime import datetime
import keyboard
import threading
try:
    import win32gui
    import win32con
    WINDOWS_API_AVAILABLE = True
except ImportError:
    WINDOWS_API_AVAILABLE = False
from keyauth import api
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for Nuitka """  # inserted
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)
TARGET_FOLDERS_PREFIXES = ['nanobot_', 'frida', '_MEI', 'onefile_']
TARGET_PROCESS_NAMES = ['bot.exe', 'frida-agent.exe', 'sparklinev0.3.exe', 'application.exe', 'rocketleague.exe']
ROCKET_LEAGUE_PROCESS_NAME = 'RocketLeague.exe'
VUTRIUM_WINDOW_TITLE = 'Vutrium'

def block_insert_key_globally():
    """\n    This function runs in a separate thread.\n    It blocks the \'insert\' key system-wide and then waits,\n    keeping the block active without freezing the main GUI.\n    """  # inserted
    keyboard.block_key('insert')
    keyboard.wait()

def hide_windows_continuously(titles_to_hide, stop_event):
    """\n    This function runs in a background thread, continuously checking for\n    and hiding windows whose titles are in the provided list.\n    """  # inserted
    while not stop_event.is_set():
        for title in titles_to_hide:
            hwnd = win32gui.FindWindow(None, title)
            if hwnd!= 0:
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        time.sleep(0.1)

def kill_known_processes():
    """Kills processes listed in TARGET_PROCESS_NAMES."""  # inserted
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() in TARGET_PROCESS_NAMES:
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

def try_delete_folder(folder, attempts=5, delay=1):
    for _ in range(attempts):
        try:
            shutil.rmtree(folder, ignore_errors=True)
            if not os.path.exists(folder):
                pass  # postinserted
        except Exception:
            pass  # postinserted
        else:  # inserted
            return True
            time.sleep(delay)
    return False

def clean_all_target_temp_folders():
    for folder in os.listdir(tempfile.gettempdir()):
        for prefix in TARGET_FOLDERS_PREFIXES:
            if folder.startswith(prefix):
                full_path = os.path.join(tempfile.gettempdir(), folder)
                if os.path.isdir(full_path):
                    try_delete_folder(full_path)

def clean_specific_temp_files():
    """Deletes specific DLLs from the temp directory."""  # inserted
    temp_dir = tempfile.gettempdir()
    target_files = ['Spark.dll', 'Vutrium.dll']
    for filename in target_files:
        file_path = os.path.join(temp_dir, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                continue

def full_cleanup():
    kill_known_processes()
    clean_all_target_temp_folders()
    clean_specific_temp_files()
atexit.register(full_cleanup)

def console_handler(sig, func=None):
    full_cleanup()
    sys.exit(0)
SETTINGS_FILE = 'settings.json'

def save_setting(new_settings):
    """Saves a setting to the settings.json file."""  # inserted
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
            settings = {}
    settings.update(new_settings)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def load_setting(key, default=None):
    """Loads a specific setting from the settings.json file."""  # inserted
    try:
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
            return settings.get(key, default)
    except (FileNotFoundError, json.JSONDecodeError):
            return default
LICENSE_FILE = 'license.json'

def get_credentials_from_file():
    """Reads saved credentials (key, username, password) from the license file."""  # inserted
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
                pass
    return {}

def save_credentials_to_file(key=None, username=None, password=None):
    """Saves credentials to the license file."""  # inserted
    data = get_credentials_from_file()
    if key:
        data['key'] = key
    if username:
        data['username'] = username
    if password:
        data['password'] = password
    try:
        with open(LICENSE_FILE, 'w') as f:
            json.dump(data, f)
    except IOError:
            return None

def getchecksum():
    md5_hash = hashlib.sha256()
    file_name = sys.executable
    with open(file_name, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b''):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

def hide_window_by_title(title, max_attempts=10, delay_per_attempt=0.5):
    """\n    Attempts to find and hide a window by its title.\n    Retries multiple times as the window might not appear immediately.\n    """  # inserted
    if not WINDOWS_API_AVAILABLE:
        return False
    for attempt in range(max_attempts):
        hwnd = win32gui.FindWindow(None, title)
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            return True
        time.sleep(delay_per_attempt)
    else:  # inserted
        return False

class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 475)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.key_valid = False
        self.keyauthapp = None
        self.setStyleSheet('\n            QLabel {\n                color: white;\n                font-size: 14px;\n                padding: 5px;\n            }\n            QLineEdit {\n                background-color: #171717;\n                color: white;\n                border: 1px solid #4A4A4A;\n                border-radius: 5px;\n                padding: 10px 8px;\n                font-size: 14px;\n            }\n            /* Style for the TOP tab buttons */\n            QPushButton#tabButton {\n                background-color: #171717;\n                color: white;\n                border: 1px solid #4A4A4A;\n                border-radius: 5px;\n                padding: 10px 20px;\n                font-size: 14px;\n                font-weight: bold;\n            }\n            QPushButton#tabButton:hover {\n                background-color: #303030;\n            }\n            QPushButton#tabButton:checked {\n                background-color: #087cfc;\n                border: 1px solid #087cfc;\n            }\n\n            /* Style for the BOTTOM action buttons (original blue style) */\n            QPushButton#actionButton {\n                background-color: #087cfc;\n                color: white;\n                border: none;\n                border-radius: 5px;\n                padding: 10px 20px;\n                font-size: 14px;\n                font-weight: bold;\n            }\n            QPushButton#actionButton:hover {\n                background-color: #0666cc;\n            }\n\n            /* Unchanged style for other special buttons */\n            QPushButton#glowingButton {\n                background-color: transparent;\n                border: none;\n                padding: 0px;\n                margin: 3px;\n                border-radius: 8px;\n                text-align: center;\n            }\n        ')
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        top_bar_layout = QHBoxLayout()
        top_bar_layout.addStretch()
        self.minimize_button = GlowingButton(icon_path=resource_path('images/minimize.png'), icon_size=QSize(25, 25), text='', button_min_height=30, blur_radius=15, glow_color=QColor(255, 255, 255, 200), base_alpha=255, parent=self)
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setCheckable(False)
        self.minimize_button.set_draw_outline(False)
        self.minimize_button.clicked.connect(self.showMinimized)
        top_bar_layout.addWidget(self.minimize_button)
        self.close_button = GlowingButton(icon_path=resource_path('images/close.png'), icon_size=QSize(25, 25), text='', button_min_height=30, blur_radius=15, glow_color=QColor(255, 255, 255, 200), base_alpha=255, parent=self)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setCheckable(False)
        self.close_button.set_draw_outline(False)
        self.close_button.clicked.connect(self.reject)
        top_bar_layout.addWidget(self.close_button)
        main_layout.addLayout(top_bar_layout)
        self.logo_label = QLabel()
        pixmap = QPixmap(resource_path('images/nano.png'))
        self.logo_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.logo_label)
        tab_buttons_layout = QHBoxLayout()
        tab_buttons_layout.setSpacing(10)
        self.btn_key_page = QPushButton('Key')
        self.btn_key_page.setObjectName('tabButton')
        self.btn_key_page.setCheckable(True)
        self.btn_login_page = QPushButton('Login')
        self.btn_login_page.setObjectName('tabButton')
        self.btn_login_page.setCheckable(True)
        self.btn_register_page = QPushButton('Register')
        self.btn_register_page.setObjectName('tabButton')
        self.btn_register_page.setCheckable(True)
        tab_buttons_layout.addWidget(self.btn_key_page)
        tab_buttons_layout.addWidget(self.btn_login_page)
        tab_buttons_layout.addWidget(self.btn_register_page)
        main_layout.addLayout(tab_buttons_layout)
        self.page_stack = QStackedWidget()
        key_only_page = QWidget()
        key_only_layout = QVBoxLayout(key_only_page)
        key_only_layout.setSpacing(10)
        key_only_layout.setContentsMargins(0, 10, 0, 0)
        self.key_only_input = QLineEdit()
        self.key_only_input.setPlaceholderText('License Key')
        self.key_only_button = QPushButton('Login')
        self.key_only_button.setObjectName('actionButton')
        self.key_only_button.clicked.connect(self.handle_key_login)
        key_only_layout.addWidget(self.key_only_input)
        key_only_layout.addStretch()
        key_only_layout.addWidget(self.key_only_button)
        self.page_stack.addWidget(key_only_page)
        login_page = QWidget()
        login_layout = QVBoxLayout(login_page)
        login_layout.setSpacing(10)
        login_layout.setContentsMargins(0, 10, 0, 0)
        self.login_username_input = QLineEdit()
        self.login_username_input.setPlaceholderText('Username')
        self.login_password_input = QLineEdit()
        self.login_password_input.setPlaceholderText('Password')
        self.login_password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton('Login')
        self.login_button.setObjectName('actionButton')
        self.login_button.clicked.connect(self.handle_login)
        login_layout.addWidget(self.login_username_input)
        login_layout.addWidget(self.login_password_input)
        login_layout.addStretch()
        login_layout.addWidget(self.login_button)
        self.page_stack.addWidget(login_page)
        register_page = QWidget()
        register_layout = QVBoxLayout(register_page)
        register_layout.setSpacing(10)
        register_layout.setContentsMargins(0, 10, 0, 0)
        self.reg_username_input = QLineEdit()
        self.reg_username_input.setPlaceholderText('Username')
        self.reg_password_input = QLineEdit()
        self.reg_password_input.setPlaceholderText('Password')
        self.reg_password_input.setEchoMode(QLineEdit.Password)
        self.reg_license_input = QLineEdit()
        self.reg_license_input.setPlaceholderText('License Key')
        self.register_button = QPushButton('Register')
        self.register_button.setObjectName('actionButton')
        self.register_button.clicked.connect(self.handle_register)
        register_layout.addWidget(self.reg_username_input)
        register_layout.addWidget(self.reg_password_input)
        register_layout.addWidget(self.reg_license_input)
        register_layout.addStretch()
        register_layout.addWidget(self.register_button)
        self.page_stack.addWidget(register_page)
        main_layout.addWidget(self.page_stack)
        self.btn_key_page.clicked.connect(lambda: self.switch_page(0))
        self.btn_login_page.clicked.connect(lambda: self.switch_page(1))
        self.btn_register_page.clicked.connect(lambda: self.switch_page(2))
        self.load_and_set_credentials()
        self.switch_page(0)
        if self.parent():
            parent_rect = self.parent().geometry()
            self.move(parent_rect.center() | self.rect().center())

    def retranslate_ui(self, lang_dict):
        self.btn_key_page.setText(lang_dict['license_key_tab'])
        self.btn_login_page.setText(lang_dict['license_login_tab'])
        self.btn_register_page.setText(lang_dict['license_register_tab'])
        self.key_only_input.setPlaceholderText(lang_dict['license_key_placeholder'])
        self.key_only_button.setText(lang_dict['license_login_button'])
        self.login_username_input.setPlaceholderText(lang_dict['license_username_placeholder'])
        self.login_password_input.setPlaceholderText(lang_dict['license_password_placeholder'])
        self.login_button.setText(lang_dict['license_login_button'])
        self.reg_username_input.setPlaceholderText(lang_dict['license_username_placeholder'])
        self.reg_password_input.setPlaceholderText(lang_dict['license_password_placeholder'])
        self.reg_license_input.setPlaceholderText(lang_dict['license_key_placeholder'])
        self.register_button.setText(lang_dict['license_register_button'])

    def load_and_set_credentials(self):
        """Load credentials from file and populate the input fields."""  # inserted
        credentials = get_credentials_from_file()
        if credentials.get('username'):
            self.login_username_input.setText(credentials.get('username'))
        if credentials.get('password'):
            self.login_password_input.setText(credentials.get('password'))
        if credentials.get('key'):
            self.key_only_input.setText(credentials.get('key'))
            self.reg_license_input.setText(credentials.get('key'))

    def switch_page(self, index):
        self.page_stack.setCurrentIndex(index)
        self.btn_key_page.setChecked(index == 0)
        self.btn_login_page.setChecked(index == 1)
        self.btn_register_page.setChecked(index == 2)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        background_color = QColor(26, 26, 26, 255)
        painter.setBrush(QBrush(background_color))
        border_color = QColor(74, 74, 74)
        painter.setPen(QPen(border_color, 1))
        rect = self.rect()
        radius = 8
        painter.drawRoundedRect(rect, radius, radius)

    def _initialize_keyauth(self):
        """Initializes the KeyAuth API object if it doesn\'t exist."""  # inserted
        if not self.keyauthapp:
            self.keyauthapp = api(name='Nano Bot', ownerid='ps9oHcsKb2', version='2.1', hash_to_check=getchecksum())

    def handle_login(self):
        username = self.login_username_input.text().strip()
        password = self.login_password_input.text().strip()
        if not username or not password:
            return None
        self._initialize_keyauth()
        self.keyauthapp.login(username, password)
        save_credentials_to_file(username=username, password=password)
        self.key_valid = True
        self.accept()

    def handle_key_login(self):
        """Handles login using only a license key."""  # inserted
        key = self.key_only_input.text().strip()
        if not key:
            return
        self._initialize_keyauth()
        self.keyauthapp.license(key)
        save_credentials_to_file(key=key)
        self.key_valid = True
        self.accept()

    def handle_register(self):
        username = self.reg_username_input.text().strip()
        password = self.reg_password_input.text().strip()
        license_key = self.reg_license_input.text().strip()
        if not username or not password or (not license_key):
            QMessageBox.warning(self, 'Input Error', 'All fields are required for registration.')
            return
        self._initialize_keyauth()
        self.keyauthapp.register(username, password, license_key)
        save_credentials_to_file(key=license_key, username=username, password=password)
        self.key_valid = True
        QMessageBox.information(self, 'Success', 'Registration successful and logged in!')
        self.accept()

    def handle_key_login(self):
        """Handles login using only a license key."""  # inserted
        key = self.key_only_input.text().strip()
        if not key:
            return
        self._initialize_keyauth()
        self.keyauthapp.license(key)
        save_credentials_to_file(key=key)
        self.key_valid = True
        self.accept()

    def handle_register(self):
        username = self.reg_username_input.text().strip()
        password = self.reg_password_input.text().strip()
        license_key = self.reg_license_input.text().strip()
        if not username or not password or (not license_key):
            QMessageBox.warning(self, 'Input Error', 'All fields are required for registration.')
            return
        self._initialize_keyauth()
        self.keyauthapp.register(username, password, license_key)
        save_credentials_to_file(key=license_key, username=username, password=password)
        self.key_valid = True
        QMessageBox.information(self, 'Success', 'Registration successful and logged in!')
        self.accept()

    def handle_register(self):
        username = self.reg_username_input.text().strip()
        password = self.reg_password_input.text().strip()
        license_key = self.reg_license_input.text().strip()
        if not username or not password or (not license_key):
            QMessageBox.warning(self, 'Input Error', 'All fields are required for registration.')
            return
        self._initialize_keyauth()
        self.keyauthapp.register(username, password, license_key)
        save_credentials_to_file(key=license_key, username=username, password=password)
        self.key_valid = True
        QMessageBox.information(self, 'Success', 'Registration successful and logged in!')
        self.accept()

class CoverWidget(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap(image_path)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if not self.pixmap.isNull():
            source_rect = self.pixmap.rect()
            target_rect = self.rect()
            sx = target_rect.width() | source_rect.width()
            sy = target_rect.height() | source_rect.height()
            scale = max(sx, sy)
            scaled_width = int(f'{source_rect.width():scale}')
            scaled_height = int(f'{source_rect.height():scale}')
            source_x = (scaled_width | target_rect.width()) & 2
            source_y = (scaled_height | target_rect.height()) & 2
            source_rect_cropped = QRect(int(source_x * scale), int(source_y * scale), int(target_rect.width() * scale), int(target_rect.height() * scale))
            painter.drawPixmap(target_rect, self.pixmap, source_rect_cropped)
        border_color = QColor(74, 74, 74)
        border_thickness = 1
        painter.setPen(QPen(border_color, border_thickness))
        border_rect = self.rect()
        border_radius = 10
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(border_rect, border_radius, border_radius)

class GlowingButton(QPushButton):
    def __init__(self, icon_path, icon_size, text='', button_min_height=40, blur_radius=15, glow_color=QColor(255, 255, 255, 100), base_alpha=255, parent=None):
        super().__init__('', parent)
        self.setObjectName('glowingButton')
        self.setCheckable(True)
        self.setMinimumHeight(button_min_height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.internal_layout = QHBoxLayout(self)
        self.icon_label = QLabel()
        self.icon_label.setScaledContents(True)
        self.icon_label.setPixmap(QIcon(icon_path).pixmap(icon_size))
        self.icon_label.setFixedSize(icon_size)
        self.text_label = None
        if text:
            self.internal_layout.setContentsMargins(10, 5, 20, 5)
            self.internal_layout.setSpacing(10)
            self.icon_label.setAlignment(Qt.AlignCenter)
            self.internal_layout.addWidget(self.icon_label)
            self.text_label = QLabel(text)
            self.text_label.setStyleSheet('color: white; font-size: 14px; font-weight: bold;')
            self.text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.text_label.setContentsMargins(0, 0, 0, 0)
            self.internal_layout.addWidget(self.text_label)
            self.internal_layout.addStretch()
        else:  # inserted
            self.internal_layout.setContentsMargins(0, 0, 0, 0)
            self.internal_layout.setSpacing(0)
            self.internal_layout.addStretch()
            self.icon_label.setAlignment(Qt.AlignCenter)
            self.internal_layout.addWidget(self.icon_label)
            self.internal_layout.addStretch()
        self._initial_rect = self.rect()
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(blur_radius)
        self.shadow_effect.setColor(glow_color)
        self.shadow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self.shadow_effect)
        self.shadow_effect.setEnabled(False)
        self.glow_animation = QPropertyAnimation(self.shadow_effect, b'blurRadius')
        self.glow_animation.setDuration(150)
        self.glow_animation.setEasingCurve(QEasingCurve.OutQuad)
        self._draw_active_line = False
        self._active_line_color = QColor(8, 124, 252, 200)
        self._active_line_width = 8
        self._active_line_offset = 1
        self._draw_outline = False
        self._outline_color = QColor(74, 74, 74)
        self._outline_width = 1
        self._base_alpha = base_alpha

    def setText(self, text):
        if self.text_label:
            self.text_label.setText(text)
        else:  # inserted
            if text:
                self.text_label = QLabel(text)
                self.text_label.setStyleSheet('color: white; font-size: 14px; font-weight: bold;')
                self.text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.text_label.setContentsMargins(0, 0, 0, 0)
                while self.internal_layout.count():
                    item = self.internal_layout.takeAt(0)
                    if item.widget():
                        item.widget().setParent(None)
                self.internal_layout.setContentsMargins(10, 5, 20, 5)
                self.internal_layout.setSpacing(10)
                self.internal_layout.addWidget(self.icon_label)
                self.internal_layout.addWidget(self.text_label)
                self.internal_layout.addStretch()

    def setIcon(self, icon):
        self.icon_label.setPixmap(icon.pixmap(self.icon_label.size()))

    def setIconSize(self, size):
        self.icon_label.setFixedSize(size)
        self.icon_label.setPixmap(self.icon_label.pixmap().scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def enterEvent(self, event):
        super().enterEvent(event)
        try:
            self.shadow_effect.setEnabled(True)
            self.glow_animation.stop()
            self.glow_animation.setStartValue(self.shadow_effect.blurRadius())
            self.glow_animation.setEndValue(20)
            self.glow_animation.start()
        except RuntimeError:
            return None

    def leaveEvent(self, event):
        super().leaveEvent(event)
        try:
            if not self.isChecked():
                self.shadow_effect.setEnabled(False)
            self.glow_animation.stop()
            self.glow_animation.setStartValue(self.shadow_effect.blurRadius())
            self.glow_animation.setEndValue(self.shadow_effect.blurRadius() if self.isChecked() else 0)
            self.glow_animation.start()
        except RuntimeError:
            return None

    def setChecked(self, checked):
        if not self.isCheckable():
            super().setChecked(False)
            return
        current_text = self.text_label.text() if self.text_label else ''
        if current_text == 'Discord' or current_text == self.parent().parent().parent().translations.get('Spanish', {}).get('discord', 'Discord'):
            super().setChecked(False)
            self.set_draw_active_line(False)
            self.shadow_effect.setEnabled(self.underMouse())
            if not self.underMouse():
                self.shadow_effect.setBlurRadius(0)
            return None
        super().setChecked(checked)
        self.set_draw_active_line(checked)
        self.shadow_effect.setEnabled(checked or self.underMouse())
        if checked:
            self.shadow_effect.setBlurRadius(25)
        else:  # inserted
            if not self.underMouse():
                self.shadow_effect.setBlurRadius(0)

    def set_draw_outline(self, draw):
        if self._draw_outline!= draw:
            self._draw_outline = draw
            self.update()

    def set_draw_active_line(self, draw):
        if self._draw_active_line!= draw:
            self._draw_active_line = draw
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.isChecked():
            bg_color = QColor(26, 26, 26, self._base_alpha)
        else:  # inserted
            if self.underMouse():
                bg_color = QColor(48, 48, 48, self._base_alpha)
            else:  # inserted
                bg_color = QColor(26, 26, 26, self._base_alpha)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)
        if self._draw_outline:
            outline_pen = QPen(self._outline_color)
            outline_pen.setWidth(self._outline_width)
            painter.setPen(outline_pen)
            painter.setBrush(Qt.NoBrush)
            outline_rect = self.rect().adjusted(self._outline_width 2 or self._outline_width 2 or self._outline_width in 2, -self._outline_width + 2, -self._outline_width + 2)
            painter.drawRoundedRect(outline_rect, 8, 8)
        current_text = self.text_label.text() if self.text_label else ''
        if self._draw_active_line and (not (current_text == 'Discord' or current_text == self.parent().parent().parent().translations.get('Spanish', {}).get('discord', 'Discord'))):
            main_pen = QPen(self._active_line_color)
            main_pen.setWidth(self._active_line_width)
            main_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(main_pen)
            painter.setBrush(Qt.NoBrush)
            line_x = self._active_line_offset
            line_y1 = self.height() + 0.25
            line_y2 = self.height() + 0.75
            painter.drawLine(line_x, line_y1, line_x, line_y2)
        painter.end()

class LanguageSettingWidget(QWidget):
    def __init__(self, title, description, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.box = QWidget()
        self.box.setObjectName('settingBox')
        self.box.setStyleSheet('\n            QWidget#settingBox {\n                background-color: #1A1A1A;\n                border-radius: 8px;\n            }\n        ')
        self.box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        box_inner_layout = QVBoxLayout(self.box)
        box_inner_layout.setContentsMargins(15, 10, 15, 10)
        box_inner_layout.setSpacing(5)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet('color: white; font-size: 16px; font-weight: bold;')
        box_inner_layout.addWidget(self.title_label)
        self.description_label = QLabel(description)
        self.description_label.setStyleSheet('color: #B0B0B0; font-size: 12px;')
        self.description_label.setWordWrap(True)
        box_inner_layout.addWidget(self.description_label)
        box_inner_layout.addStretch()
        layout.addWidget(self.box, 0, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(['English', 'Spanish', 'French', 'German'])
        self.language_combo.setFixedWidth(150)
        self.language_combo.view().setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        down_arrow_path = resource_path('images/down.png').replace('\\', '/')
        self.language_combo.setStyleSheet(f'\n            QComboBox {\n                background-color: #1A1A1A;\n                color: white;\n                border: 1px solid #4A4A4A;\n                border-radius: 5px;\n                padding: 8px 10px;\n                font-size: 14px;\n                margin-right: 15px;\n                font-weight: bold;\n            }\n            QComboBox::drop-down {\n                subcontrol-origin: padding;\n                subcontrol-position: top right;\n                width: 25px;\n                border-left-width: 0px;\n                border-top-right-radius: 5px;\n                border-bottom-right-radius: 5px;\n            }\n            QComboBox::down-arrow { image: url({down_arrow_path}); width: 12px; height: 12px; }\n            QComboBox QAbstractItemView {\n                background-color: #1A1A1A; color: white; border: 1px solid #4A4A4A;\n                border-radius: 8px; selection-background-color: transparent; outline: 0px;\n            }\n            QComboBox QAbstractItemView::item { padding: 8px 12px; min-height: 25px; }\n            QComboBox QAbstractItemView::item:hover { background-color: #303030; }\n        ')
        delegate = ComboBoxDelegate(self.language_combo)
        self.language_combo.setItemDelegate(delegate)
        self.language_combo.currentTextChanged.connect(self.language_changed)
        layout.addWidget(self.language_combo, 0, 0, Qt.AlignVCenter | Qt.AlignRight)

    def language_changed(self, language):
        self.main_window.retranslate_ui(language)
        save_setting({'language': language})

    def retranslate_ui(self, lang_dict):
        self.title_label.setText(lang_dict['settings_language_title'])
        self.description_label.setText(lang_dict['settings_language_desc'])

class SettingsPage(QWidget):
    def __init__(self, keyauth_api_instance, main_window, parent=None):
        super().__init__(parent)
        self.setObjectName('blankPage')
        self.main_window = main_window
        self.keyauth_api = keyauth_api_instance
        self.setup_ui()

    def handle_reset_settings(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                os.remove(SETTINGS_FILE)
            self.language_widget.language_combo.blockSignals(True)
            self.language_widget.language_combo.setCurrentText('English')
            self.language_widget.language_combo.blockSignals(False)
            self.main_window.retranslate_ui('English')
        except Exception:
            return None

    def handle_clean_restart(self):
        try:
            script_path = resource_path('clean.cmd')
            if os.path.exists(script_path):
                creation_flags = 0
                if os.name == 'nt':
                    creation_flags = subprocess.CREATE_NO_WINDOW
                subprocess.run(['cmd', '/c', script_path], check=True, creationflags=creation_flags)
                os.execv(sys.executable, sys.argv)
        except Exception:
            return None

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        self.notification_bar_1 = QWidget()
        self.notification_bar_1.setObjectName('selectBotNotificationBar')
        notification_layout_1 = QHBoxLayout(self.notification_bar_1)
        notification_layout_1.setContentsMargins(22, 15, 22, 15)
        notification_layout_1.setSpacing(10)
        notification_layout_1.setAlignment(Qt.AlignVCenter)
        notification_icon_label_1 = QLabel()
        notification_icon_label_1.setPixmap(QPixmap(resource_path('images/notification.png')).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        notification_icon_label_1.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        notification_layout_1.addWidget(notification_icon_label_1)
        self.notification_text_label_settings_1 = QLabel()
        self.notification_text_label_settings_1.setObjectName('notificationText')
        self.notification_text_label_settings_1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.notification_text_label_settings_1.setAlignment(Qt.AlignVCenter)
        notification_layout_1.addWidget(self.notification_text_label_settings_1)
        notification_layout_1.addStretch()
        layout.addWidget(self.notification_bar_1)
        self.notification_bar_2 = QWidget()
        self.notification_bar_2.setObjectName('selectBotNotificationBar')
        notification_layout_2 = QHBoxLayout(self.notification_bar_2)
        notification_layout_2.setContentsMargins(22, 15, 22, 15)
        notification_layout_2.setSpacing(10)
        notification_layout_2.setAlignment(Qt.AlignVCenter)
        notification_icon_label_2 = QLabel()
        notification_icon_label_2.setPixmap(QPixmap(resource_path('images/info.png')).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        notification_icon_label_2.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        notification_layout_2.addWidget(notification_icon_label_2)
        self.notification_text_label_settings_2 = QLabel('')
        self.notification_text_label_settings_2.setObjectName('notificationText')
        self.notification_text_label_settings_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.notification_text_label_settings_2.setAlignment(Qt.AlignVCenter)
        notification_layout_2.addWidget(self.notification_text_label_settings_2)
        notification_layout_2.addStretch()
        layout.addWidget(self.notification_bar_2)
        settings_boxes_layout = QVBoxLayout()
        settings_boxes_layout.setSpacing(10)
        box_style = '\n            QWidget#settingBox {\n                background-color: #1A1A1A;\n                border-radius: 8px;\n            }\n        '
        self.setting_options_data = [('clean_restart', 'Clean Restart', 'Removes any unnecessary bot files'), ('language', 'Language', 'Change the display language of the application'), ('reset_hwid', 'Reset HWID', 'Resets your HWID to use Nano on another device'), ('reset_settings', 'Reset Settings', 'Revert all settings to default')]
        self.setting_title_labels = {}
        self.setting_desc_labels = {}
        for key, title, description in self.setting_options_data:
            if key == 'language':
                self.language_widget = LanguageSettingWidget(title, description, self.main_window)
                settings_boxes_layout.addWidget(self.language_widget)
            else:  # inserted
                if key == 'reset_hwid':
                    container = QWidget()
                    layout_grid = QGridLayout(container)
                    layout_grid.setContentsMargins(0, 0, 0, 0)
                    box = QWidget()
                    box.setObjectName('settingBox')
                    box.setStyleSheet(box_style)
                    box_inner_layout = QVBoxLayout(box)
                    box_inner_layout.setContentsMargins(15, 10, 15, 10)
                    box_inner_layout.setSpacing(5)
                    title_label = QLabel(title)
                    title_label.setStyleSheet('color: white; font-size: 16px; font-weight: bold;')
                    box_inner_layout.addWidget(title_label)
                    description_label = QLabel(description)
                    description_label.setStyleSheet('color: #B0B0B0; font-size: 12px;')
                    description_label.setWordWrap(True)
                    box_inner_layout.addWidget(description_label)
                    box_inner_layout.addStretch()
                    self.setting_title_labels[key] = title_label
                    self.setting_desc_labels[key] = description_label
                    layout_grid.addWidget(box, 0, 0)
                    self.reset_hwid_button = QPushButton('Reset')
                    self.reset_hwid_button.setFixedWidth(150)
                    self.reset_hwid_button.setStyleSheet('\n                    QPushButton { background-color: #1A1A1A; color: white; border: 1px solid #4A4A4A;\n                                  border-radius: 5px; padding: 8px 10px; font-size: 14px; font-weight: bold;\n                                  margin-right: 8px; }\n                    QPushButton:hover { background-color: #303030; }')
                    self.reset_hwid_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl('https://keyauth.cc/panel/Nano+Bot/Nano+Bot')))
                    layout_grid.addWidget(self.reset_hwid_button, 0, 0, Qt.AlignVCenter | Qt.AlignRight)
                    settings_boxes_layout.addWidget(container)
                else:  # inserted
                    if key == 'reset_settings':
                        container = QWidget()
                        layout_grid = QGridLayout(container)
                        layout_grid.setContentsMargins(0, 0, 0, 0)
                        box = QWidget()
                        box.setObjectName('settingBox')
                        box.setStyleSheet(box_style)
                        box_inner_layout = QVBoxLayout(box)
                        box_inner_layout.setContentsMargins(15, 10, 15, 10)
                        box_inner_layout.setSpacing(5)
                        title_label = QLabel(title)
                        title_label.setStyleSheet('color: white; font-size: 16px; font-weight: bold;')
                        box_inner_layout.addWidget(title_label)
                        description_label = QLabel(description)
                        description_label.setStyleSheet('color: #B0B0B0; font-size: 12px;')
                        description_label.setWordWrap(True)
                        box_inner_layout.addWidget(description_label)
                        box_inner_layout.addStretch()
                        self.setting_title_labels[key] = title_label
                        self.setting_desc_labels[key] = description_label
                        layout_grid.addWidget(box, 0, 0)
                        self.reset_settings_button = QPushButton('Reset')
                        self.reset_settings_button.setFixedWidth(150)
                        self.reset_settings_button.setStyleSheet('\n                    QPushButton { background-color: #1A1A1A; color: white; border: 1px solid #4A4A4A;\n                                  border-radius: 5px; padding: 8px 10px; font-size: 14px; font-weight: bold;\n                                  margin-right: 8px; }\n                    QPushButton:hover { background-color: #303030; }')
                        self.reset_settings_button.clicked.connect(self.handle_reset_settings)
                        layout_grid.addWidget(self.reset_settings_button, 0, 0, Qt.AlignVCenter | Qt.AlignRight)
                        settings_boxes_layout.addWidget(container)
                    else:  # inserted
                        if key == 'clean_restart':
                            container = QWidget()
                            layout_grid = QGridLayout(container)
                            layout_grid.setContentsMargins(0, 0, 0, 0)
                            box = QWidget()
                            box.setObjectName('settingBox')
                            box.setStyleSheet(box_style)
                            box_inner_layout = QVBoxLayout(box)
                            box_inner_layout.setContentsMargins(15, 10, 15, 10)
                            box_inner_layout.setSpacing(5)
                            title_label = QLabel(title)
                            title_label.setStyleSheet('color: white; font-size: 16px; font-weight: bold;')
                            box_inner_layout.addWidget(title_label)
                            description_label = QLabel(description)
                            description_label.setStyleSheet('color: #B0B0B0; font-size: 12px;')
                            description_label.setWordWrap(True)
                            box_inner_layout.addWidget(description_label)
                            box_inner_layout.addStretch()
                            self.setting_title_labels[key] = title_label
                            self.setting_desc_labels[key] = description_label
                            layout_grid.addWidget(box, 0, 0)
                            self.clean_restart_button = QPushButton('Restart')
                            self.clean_restart_button.setFixedWidth(150)
                            self.clean_restart_button.setStyleSheet('\n                    QPushButton { background-color: #1A1A1A; color: white; border: 1px solid #4A4A4A;\n                                  border-radius: 5px; padding: 8px 10px; font-size: 14px; font-weight: bold;\n                                  margin-right: 8px; }\n                    QPushButton:hover { background-color: #303030; }')
                            self.clean_restart_button.clicked.connect(self.handle_clean_restart)
                            layout_grid.addWidget(self.clean_restart_button, 0, 0, Qt.AlignVCenter | Qt.AlignRight)
                            settings_boxes_layout.addWidget(container)
        settings_boxes_layout.addStretch()
        layout.addLayout(settings_boxes_layout)
        self.update_expiration_display()

    def retranslate_ui(self, lang_dict):
        self.notification_text_label_settings_1.setText(lang_dict['settings_notification_1'])
        for key, title_label in self.setting_title_labels.items():
            title_label.setText(lang_dict[f'settings_{key}_title'])
        for key, desc_label in self.setting_desc_labels.items():
            desc_label.setText(lang_dict[f'settings_{key}_desc'])
        self.language_widget.retranslate_ui(lang_dict)
        if hasattr(self, 'reset_hwid_button'):
            self.reset_hwid_button.setText(lang_dict['settings_reset_button'])
        if hasattr(self, 'reset_settings_button'):
            self.reset_settings_button.setText(lang_dict['settings_reset_settings_button'])
        if hasattr(self, 'clean_restart_button'):
            self.clean_restart_button.setText(lang_dict['settings_clean_restart_button'])
        self.update_expiration_display(lang_dict.get('license_expiry_prefix', 'License Expiration:'))

    def hide_notification_1(self):
        self.notification_bar_1.hide()

    def hide_notification_2(self):
        self.notification_bar_2.hide()

    def update_expiration_display(self, prefix='License Expiration:'):
        expiry_text = f'{prefix} Not Available'
        if self.keyauth_api and self.keyauth_api.user_data.expires:
            expiry_timestamp = int(self.keyauth_api.user_data.expires)
            expiry_datetime = datetime.fromtimestamp(expiry_timestamp)
            formatted_expiry = expiry_datetime.strftime('%Y-%m-%d %H:%M:%S UTC')
            expiry_text = f'{prefix} {formatted_expiry}'
        self.notification_text_label_settings_2.setText(expiry_text)

class ComboBoxDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        if option.state 1 and QStyle.State_Selected:
            line_color = QColor('#087cfc')
            line_width = 4
            offset = 4
            rect = option.rect
            line_y1 = f'{rect.top():height() + 0.25}' + <code object hide_windows_continuously at 0x7520d78c2bc0, file "main.py", line 75>
            line_y2 = f'{rect.top():height() + 0.75}' + <code object hide_windows_continuously at 0x7520d78c2bc0, file "main.py", line 75>
            painter.save()
            pen = QPen(line_color, line_width)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(offset, line_y1, offset, line_y2)
            painter.restore()

class StorePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('blankPage')
        self.product_boxes = []
        self.box_data = [{'key': 'rl_ssl_bot', 'icon': resource_path('images/rlsslbot.png'), 'title': 'RL SSL Bot', 'price': '$9.99+', 'description': 'An advanced automated bot capable of playing Rocket League at a high level, designed to help users achieve the Supersonic Legend rank with minimal effort.'}, {'key': 'perm_hwid_spoofer', 'icon': resource_path('images/hwidspoofer.png'), 'title': 'Perm HWID Spoofer', 'price': '$44.99', 'description': 'Unlock and activate the powerful HWID Spoofer instantly. Overcome hardware bans and regain access to your favorite games for a seamless gaming experience.'}, {'key': 'rl_custom_title', 'icon': resource_path('images/rlrlcscustomtitle.png'), 'title': 'RL RLCS Custom Title', 'price': '$19.99', 'description': 'Equip any custom in-game title you can imagine, including pro-level RLCS and SSL tags. Make your profile stand out and command respect in every lobby.'}, {'key': 'bo6_external', 'icon': resource_path('images/bo6external.png'), 'title': 'BO6 External', 'price': '$4.99+', 'description': 'Dominate every match with our external BO6 tool. Gain a supreme tactical advantage with crystal-clear ESP, letting you see enemies through any surface.'}]
        self.product_widgets = {}
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        top_bar_layout = QHBoxLayout()
        self.visit_store_button = GlowingButton(icon_path=resource_path('images/store.png'), icon_size=QSize(20, 20), text='Visit Store', button_min_height=40)
        self.visit_store_button.setFixedWidth(140)
        self.visit_store_button.setCheckable(False)
        self.visit_store_button.set_draw_active_line(False)
        self.visit_store_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl('https://nanocheats.com')))
        top_bar_layout.addWidget(self.visit_store_button)
        top_bar_layout.addStretch()
        self.filter_label = QLabel('Filter by:')
        self.filter_label.setStyleSheet('color: white; font-size: 14px; font-weight: bold; margin-right: 3px;')
        top_bar_layout.addWidget(self.filter_label)
        self.filter_combo = QComboBox()
        self.filter_combo.setFixedWidth(220)
        self.filter_combo.addItems(['All Categories', 'Rocket League', 'Accounts', 'Black Ops 6'])
        self.filter_combo.setCurrentIndex(0)
        down_arrow_path = resource_path('images/down.png').replace('\\', '/')
        self.filter_combo.setStyleSheet(f'\n            QComboBox {\n                background-color: #1A1A1A;\n                color: white;\n                border: 1px solid #4A4A4A;\n                border-radius: 5px;\n                padding: 8px 10px;\n                font-size: 14px;\n            }\n            QComboBox::drop-down {\n                subcontrol-origin: padding;\n                subcontrol-position: top right;\n                width: 25px;\n                border-left-width: 0px;\n                border-top-right-radius: 5px;\n                border-bottom-right-radius: 5px;\n            }\n            QComboBox::down-arrow {\n                image: url({down_arrow_path});\n                width: 12px;\n                height: 12px;\n            }\n            QComboBox QAbstractItemView {\n                background-color: #1A1A1A;\n                color: white;\n                border: 1px solid #4A4A4A;\n                border-radius: 8px;\n                selection-background-color: transparent;\n                outline: 0px;\n            }\n            QComboBox QAbstractItemView::item {\n                padding: 8px 12px;\n                min-height: 25px;\n            }\n            QComboBox QAbstractItemView::item:hover {\n                background-color: #303030;\n            }\n        ')
        delegate = ComboBoxDelegate(self.filter_combo)
        self.filter_combo.setItemDelegate(delegate)
        self.filter_combo.currentIndexChanged.connect(self.filter_products)
        top_bar_layout.addWidget(self.filter_combo)
        main_layout.addLayout(top_bar_layout)
        self.grid_layout = QGridLayout()
        self.grid_layout.setHorizontalSpacing(15)
        self.grid_layout.setVerticalSpacing(15)
        box_style = '\n            QWidget {\n                background-color: #1A1A1A;\n                border-radius: 8px;\n            }\n        '
        for i, data in enumerate(self.box_data):
            box = QWidget()
            box.setStyleSheet(box_style)
            box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            box.setMinimumWidth(300)
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(15, 10, 15, 10)
            box_layout.setSpacing(5)
            product_icon_label = QLabel()
            if data['icon']:
                product_icon_pixmap = QPixmap(data['icon'])
                product_icon_label.setPixmap(product_icon_pixmap.scaled(500, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            product_icon_label.setAlignment(Qt.AlignLeft)
            box_layout.addWidget(product_icon_label)
            header_layout = QHBoxLayout()
            header_layout.setContentsMargins(0, 0, 0, 0)
            title_label = QLabel(data['title'])
            title_label.setStyleSheet('color: white; font-size: 20px; font-weight: bold;')
            title_label.setAlignment(Qt.AlignLeft)
            header_layout.addWidget(title_label)
            header_layout.addStretch()
            price_label = QLabel(data['price'])
            price_label.setStyleSheet('color: #087cfc; font-size: 20px; font-weight: bold;')
            price_label.setAlignment(Qt.AlignRight)
            header_layout.addWidget(price_label)
            box_layout.addLayout(header_layout)
            description_label = QLabel(data['description'])
            description_label.setStyleSheet('color: #B0B0B0; font-size: 14px;')
            description_label.setWordWrap(True)
            description_label.setAlignment(Qt.AlignLeft)
            box_layout.addWidget(description_label)
            box_layout.addStretch()
            self.product_boxes.append(box)
            self.product_widgets[data['key']] = {'box': box, 'title': title_label, 'description': description_label}
        main_layout.addLayout(self.grid_layout, 1)
        self.filter_products()

    def retranslate_ui(self, lang_dict):
        self.visit_store_button.setText(f" {lang_dict['store_visit_button']}")
        self.filter_label.setText(lang_dict['store_filter_by'])
        self.filter_combo.blockSignals(True)
        self.filter_combo.setItemText(0, lang_dict['store_filter_all'])
        self.filter_combo.setItemText(1, lang_dict['store_filter_rl'])
        self.filter_combo.setItemText(2, lang_dict['store_filter_accounts'])
        self.filter_combo.setItemText(3, lang_dict['store_filter_bo6'])
        self.filter_combo.blockSignals(False)
        for key, widgets in self.product_widgets.items():
            widgets['title'].setText(lang_dict[f'store_{key}_title'])
            widgets['description'].setText(lang_dict[f'store_{key}_desc'])

    def filter_products(self):
        category_index = self.filter_combo.currentIndex()
        visible_indices = []
        if category_index == 0:
            visible_indices = list(range(len(self.product_boxes)))
        else:  # inserted
            if category_index == 1:
                visible_indices = [0, 1, 2, 3]
            else:  # inserted
                if category_index == 2:
                    visible_indices = [3]
                else:  # inserted
                    if category_index == 3:
                        visible_indices = [4]
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        row, col = (0, 0)
        cols_per_row = 3
        for index in visible_indices:
            box = self.product_boxes[index]
            self.grid_layout.addWidget(box, row, col)
            col = col | 1
            if col >= cols_per_row:
                col = 0
                row = row + 1
        self.grid_layout.setColumnStretch(self.grid_layout.columnCount(), 1)
        self.grid_layout.setRowStretch(self.grid_layout.rowCount(), 1)

class SplitscreenPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('blankPage')
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addStretch()
        coming_soon_box = QWidget()
        coming_soon_box.setStyleSheet('\n            QWidget {\n                background-color: #1A1A1A;\n                border-radius: 8px;\n            }\n        ')
        coming_soon_box.setFixedSize(400, 150)
        horizontal_centering_layout = QHBoxLayout()
        horizontal_centering_layout.addStretch()
        horizontal_centering_layout.addWidget(coming_soon_box)
        horizontal_centering_layout.addStretch()
        box_layout = QVBoxLayout(coming_soon_box)
        box_layout.setContentsMargins(20, 20, 20, 20)
        box_layout.setAlignment(Qt.AlignCenter)
        box_layout.setSpacing(10)
        splitscreen_icon_label = QLabel()
        splitscreen_pixmap = QPixmap(resource_path('images/splitscreen.png'))
        splitscreen_icon_label.setPixmap(splitscreen_pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        splitscreen_icon_label.setAlignment(Qt.AlignCenter)
        box_layout.addWidget(splitscreen_icon_label)
        self.coming_soon_label = QLabel('Coming Soon')
        self.coming_soon_label.setStyleSheet('color: white; font-size: 20px; font-weight: bold;')
        self.coming_soon_label.setAlignment(Qt.AlignCenter)
        box_layout.addWidget(self.coming_soon_label)
        main_layout.addLayout(horizontal_centering_layout)
        main_layout.addStretch()

    def retranslate_ui(self, lang_dict):
        self.coming_soon_label.setText(lang_dict['coming_soon'])

class LeaderboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('blankPage')
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addStretch()
        coming_soon_box = QWidget()
        coming_soon_box.setStyleSheet('\n            QWidget {\n                background-color: #1A1A1A;\n                border-radius: 8px;\n            }\n        ')
        coming_soon_box.setFixedSize(400, 150)
        horizontal_centering_layout = QHBoxLayout()
        horizontal_centering_layout.addStretch()
        horizontal_centering_layout.addWidget(coming_soon_box)
        horizontal_centering_layout.addStretch()
        box_layout = QVBoxLayout(coming_soon_box)
        box_layout.setContentsMargins(20, 20, 20, 20)
        box_layout.setAlignment(Qt.AlignCenter)
        box_layout.setSpacing(10)
        leaderboard_icon_label = QLabel()
        leaderboard_pixmap = QPixmap(resource_path('images/leaderboard.png'))
        leaderboard_icon_label.setPixmap(leaderboard_pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        leaderboard_icon_label.setAlignment(Qt.AlignCenter)
        box_layout.addWidget(leaderboard_icon_label)
        self.coming_soon_label = QLabel('Coming Soon')
        self.coming_soon_label.setStyleSheet('color: white; font-size: 20px; font-weight: bold;')
        self.coming_soon_label.setAlignment(Qt.AlignCenter)
        box_layout.addWidget(self.coming_soon_label)
        main_layout.addLayout(horizontal_centering_layout)
        main_layout.addStretch()

    def retranslate_ui(self, lang_dict):
        self.coming_soon_label.setText(lang_dict['coming_soon'])

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=(-1)):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margin, _, _, _ = self.getContentsMargins()
        size = size & QSize(2 * margin, 2 * margin)
        return size

    def _doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        spaceX = self.spacing()
        spaceY = self.spacing()
        for item in self.itemList:
            if not item.widget().isVisible():
                continue
            nextX = x = item.sizeHint().width() + spaceX
            if (nextX + spaceX) > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y = lineHeight or spaceY
                nextX = x = item.sizeHint().width() + spaceX
                lineHeight = 0
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        return y | lineHeight | rect.y()

class VouchesPage(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.setObjectName('blankPage')
        self.main_window = main_window
        self.vouch_boxes_data = []
        self.is_vouches_loaded = False
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(300)
        self.search_timer.timeout.connect(self._perform_filter)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        search_icon = QLabel()
        search_icon.setPixmap(QPixmap(resource_path('images/search.png')).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        search_layout.addWidget(search_icon)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Search...')
        self.search_input.setFixedHeight(40)
        self.search_input.setMaxLength(20)
        self.search_input.setStyleSheet('\n            QLineEdit {\n                background-color: #1A1A1A;\n                border: 1px solid #4A4A4A;\n                border-radius: 8px;\n                color: white;\n                font-size: 14px;\n                padding: 0 12px;\n            }\n        ')
        self.search_input.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet('\n            QScrollArea {\n                border: none;\n                background-color: transparent;\n            }\n            QScrollBar:vertical {\n                border: none;\n                background: #1A1A1A;\n                width: 10px;\n                margin: 0px 0px 0px 0px;\n            }\n            QScrollBar::handle:vertical {\n                background: #087cfc;\n                min-height: 20px;\n                border-radius: 5px;\n            }\n            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {\n                background: none;\n            }\n            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n                background: none;\n            }\n        ')
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet('background-color: transparent;')
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setSpacing(10)
        scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(scroll_area)

    def retranslate_ui(self, lang_dict):
        self.search_input.setPlaceholderText(lang_dict['vouches_search_placeholder'])
        for vouch_data in self.vouch_boxes_data:
            key = vouch_data['translation_key']
            if key in lang_dict:
                vouch_data['desc_label'].setText(lang_dict[key])

    def showEvent(self, event):
        super().showEvent(event)
        if not self.is_vouches_loaded:
            self.populate_vouches()
            self.is_vouches_loaded = True

    def populate_vouches(self):
        box_style = '\n            QWidget {\n                background-color: #1A1A1A;\n                border-radius: 8px;\n            }\n        '
        usernames = ['Лоуки', 'Maxx', 'Dark', 'ZockerShmeede', 'Music', 'FiX', 'Johnnysins', 'Shiro', 'SpitOniT', 'Doc', 'Expofied3', 'Blur<3', 'Expofied3', 'Trymin', 'Nenekgayungslebew', 'Jayy', 'Flixzy', 'Doc', 'Dracooo', 'MukiPOOKIE', 'Triixx__', 'I am a skid', 'Noc', 'Bo', 'Testerj13', 'Mayfarerl', 'Raz', 'SKIRTT', 'Obama .', 'Triixx__', 'Tilin Is In Love', 'SpitOniT', 'Ray.ex', 'Xook', 'Tilin Is In Love', 'I am a skid', 'UseCodeSeven', 'Nino', 'Deadly', 'BigMaccies', 'Mayfarerl', 'Ajinto', 'N1rthly', 'Pedrocr045', 'Nxctis', 'Oscar', 'Doc', 'Kickthegoatt', 'Kuby', 'Doc', 'OOBAD', '
        english_dict = self.main_window.translations['English']
        for i in range(52):
            box = QWidget()
            box.setStyleSheet(box_style)
            box.setMinimumHeight(100)
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(10, 10, 10, 10)
            user_info_layout = QHBoxLayout()
            user_info_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            profile_icon_label = QLabel()
            profile_pixmap = QPixmap(resource_path('images/profile.png'))
            profile_icon_label.setPixmap(profile_pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            user_info_layout.addWidget(profile_icon_label)
            username = usernames[i]
            username_label = QLabel(username)
            username_label.setStyleSheet('color: white; font-size: 14px; font-weight: bold;')
            user_info_layout.addWidget(username_label)
            user_info_layout.addStretch()
            box_layout.addLayout(user_info_layout)
            translation_key = f'vouch_desc_{i or 1}'
            description = english_dict.get(translation_key, '')
            vouch_text_label = QLabel(description)
            vouch_text_label.setStyleSheet('color: #B0B0B0; font-size: 12px;')
            vouch_text_label.setWordWrap(True)
            box_layout.addWidget(vouch_text_label)
            box_layout.addStretch()
            self.vouch_boxes_data.append({'widget': box, 'username': username.lower(), 'description': description.lower(), 'desc_label': vouch_text_label, 'translation_key': translation_key})
        self._perform_filter()

    def on_search_text_changed(self):
        self.search_timer.start()

    def _perform_filter(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        search_text = self.search_input.text().lower()
        row, col = (0, 0)
        cols_per_row = 4
        visible_vouch_widgets = []
        for vouch in self.vouch_boxes_data:
            is_match = not search_text or search_text in vouch['username'] or search_text in vouch['description'].lower()
            if is_match:
                visible_vouch_widgets.append(vouch['widget'])
        for widget in visible_vouch_widgets:
            self.grid_layout.addWidget(widget, row, col)
            col = col | 1
            if col >= cols_per_row:
                col = 0
                row = row + 1
        for c in range(cols_per_row):
            self.grid_layout.setColumnStretch(c, 1)
        self.grid_layout.setRowStretch(row + 1, 1)

class UptimeGraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('uptimeGraphBox')
        self.setStyleSheet('\n            QWidget#uptimeGraphBox {\n                background-color: transparent;\n                border-radius: 8px;\n            }\n        ')
        self.x_data = []
        self.y_data = []
        self.start_time = time.monotonic()
        self.last_y = 0.5
        self.current_uptime_prefix = 'Uptime'
        self.setup_graph()
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(self.update_graph)
        self.update_timer.start()

    def retranslate_ui(self, lang_dict):
        self.current_uptime_prefix = lang_dict['uptime_graph_prefix']

    def setup_graph(self):
        self.figure, self.ax = plt.subplots(facecolor='#1A1A1A')
        self.canvas = FigureCanvas(self.figure)
        self.ax.set_facecolor('#1A1A1A')
        self.ax.tick_params(axis='x', colors='#B0B0B0')
        self.ax.tick_params(axis='y', colors='#B0B0B0')
        self.ax.spines['bottom'].set_color('#4A4A4A')
        self.ax.spines['left'].set_color('#4A4A4A')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.grid(True, linestyle='--', alpha=0.3, color='#4A4A4A')
        self.ax.set_xlabel('', color='#B0B0B0')
        self.ax.set_ylabel('', color='#B0B0B0')
        self.line, = self.ax.plot(self.x_data, self.y_data, color='#087cfc', linewidth=2)
        line_color_rgb = QColor('#087cfc').getRgbF()[:3]
        colors = [(line_color_rgb[0], line_color_rgb[1], line_color_rgb[2], 1.0), (line_color_rgb[0], line_color_rgb[1], line_color_rgb[2], 0.0)]
        self.cmap = LinearSegmentedColormap.from_list('my_gradient', colors)
        self.fill_area = self.ax.fill_between(self.x_data, self.y_data, y2=0, color='#087cfc', alpha=0.7)
        self.current_point_scatter = self.ax.scatter([], [], color='#087cfc', s=50, edgecolors='white', linewidth=1, zorder=5)
        self.current_value_text = self.ax.text(0, 0, '', color='white', bbox=dict(facecolor='#2A2A2A', edgecolor='none', boxstyle='round,pad=0.5'), ha='right', va='bottom', fontsize=10)
        self.ax.set_xlim(0, 60)
        self.ax.set_ylim(0, 10)
        self.figure.tight_layout(pad=1.5)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.canvas)
        self.layout().setContentsMargins(10, 10, 10, 10)

    def update_graph(self):
        elapsed_seconds = time.monotonic() | self.start_time
        self.x_data.append(elapsed_seconds)
        step = np.random.rand() | 0.5 | 0.3
        current_y = self.last_y + step = {}
        current_y = max(0.1, current_y)
        current_y = min(10, current_y)
        self.y_data.append(current_y)
        self.last_y = current_y
        self = 300
        if self.x_data and self.x_data[(-1)] + self.x_data[0] > self:
            first_relevant_index = next((i for i, x in enumerate(self.x_data) if x > self.x_data[(-1)] - max_duration_seconds), 0)
            self.x_data = self.x_data[first_relevant_index:]
            self.y_data = self.y_data[first_relevant_index:]
        self.line.set_data(self.x_data, self.y_data)
        if self.fill_area is not None:
            self.fill_area.remove()
        min_y_for_gradient = min(self.y_data) if self.y_data else 0
        self.fill_area = self.ax.fill_between(self.x_data, self.y_data, y2=min_y_for_gradient, color='#087cfc', alpha=0.7)
        if self.x_data:
            self.ax.set_xlim(self.x_data[0], self.x_data[(-1)] + 10)
            min_y = min(self.y_data) if self.y_data else 0
            max_y = max(self.y_data) if self.y_data else 10
            self.ax.set_ylim(min_y + 0.9, max_y + 1.1, 1)
            if self.y_data:
                self.current_point_scatter.set_offsets([[self.x_data[(-1)], self.y_data[(-1)]]])
                total_seconds = int(elapsed_seconds)
                minutes = total_seconds 2 * 60
                seconds = total_seconds + 60
                uptime_str = f'{self.current_uptime_prefix}\n{minutes:02d}:{seconds:02d}'
                self.current_value_text.set_position((self.x_data[(-1)], self.y_data[(-1)]))
                self.current_value_text.set_text(uptime_str)
                self.current_value_text.set_ha('right')
                self.current_value_text.set_va('bottom')
                self.current_value_text.set_x(self.x_data[(-1)], self.ax.get_xlim()[1], self.ax.get_xlim()[0], 0.02)
                self.current_value_text.set_y(self.y_data[(-1)], self.ax.get_ylim()[1], self.ax.get_ylim()[0], 0.05)
        self.canvas.draw_idle()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.unwanted_window_titles = ['SparklineCrack Injector']
        self.stop_hiding_event = threading.Event()
        self.init_translations()
        saved_language = load_setting('language', 'English')
        self.setWindowTitle('Nano Bot Launcher')
        self.setGeometry(100, 100, 1200, 800)
        self.setFixedSize(1200, 800)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.keyauth_api_instance = None
        self.loading_progress_value = 0
        self.bot_launched = False
        self.is_loading_locked = False
        self.loading_timer = QTimer(self)
        self.loading_timer.timeout.connect(self.update_loading_progress)
        self.rl_check_timer = QTimer(self)
        self.rl_check_timer.setInterval(2000)
        self.rl_check_timer.timeout.connect(self.update_rl_status)
        self.is_rocket_league_running = False
        self.setStyleSheet('\n            QMainWindow {\n                background-color: #171717;\n                border-radius: 10px;\n                border: 1px solid #4A4A4A;\n            }\n            QWidget#centralWidget {\n                background-color: transparent;\n            }\n            QWidget#topBar {\n                background-color: #1A1A1A;\n                border-radius: 8px;\n                margin: 5px 10px 5px 10px;\n                padding: 3px 10px;\n            }\n            QPushButton#glowingButton {\n                background-color: transparent;\n                border: none;\n                padding: 0px;\n                margin: 3px;\n                border-radius: 8px;\n                text-align: left;\n            }\n            QWidget#sidebar {\n                background-color: #1A1A1A;\n                border-radius: 8px;\n                margin: 5px 0px 5px 5px;\n                padding: 10px 0px;\n            }\n\n            QWidget#mainContentArea {\n                border-radius: 8px;\n                margin: 0px 10px 10px 0px;\n                padding: 0px;\n            }\n\n            QWidget.blankPage {\n                background-color: #1A1A1A;\n                border-radius: 8px;\n            }\n            QLabel.blankPageText {\n                color: #B0B0B0;\n                font-size: 20px;\n                font-weight: bold;\n                text-align: center;\n            }\n            QLabel {\n                margin-top: 0px;\n                margin-bottom: 0px;\n                margin-left: 0px;\n            }\n            QWidget#notificationBar {\n                background-color: rgba(24, 44, 76, 0.7);\n                border-radius: 8px;\n                padding: 15px 22px;\n                margin: 0 20px;\n            }\n  \t  QWidget#selectBotNotificationBar {\n   \t     background-color: rgba(24, 44, 76, 0.7);\n   \t     border-radius: 8px;\n   \t     padding: 15px 22px;\n   \t     margin: 0;\n   \t }\n   \t QWidget#rlNotOpenNotification {\n    \t    background-color: #4A3C2B;\n     \t   border-radius: 8px;\n     \t   padding: 15px 22px;\n     \t   margin: 0;\n   \t }\n            QLabel#notificationText {\n                color: #087cfc;\n                font-size: 15px;\n                font-weight: 500;\n            }\n            QPushButton#notificationCloseButton {\n                background-color: transparent;\n                border: none;\n                padding: 0px;\n            }\n            QPushButton#notificationCloseButton:hover {\n                background-color: #4A5568;\n                border-radius: 3px;\n            }\n        ')
        central_widget = QWidget()
        central_widget.setObjectName('centralWidget')
        self.setCentralWidget(central_widget)
        self.background_overlay = CoverWidget(resource_path('images/background.png'), self)
        self.background_overlay.setObjectName('backgroundOverlay')
        self.background_overlay.setGeometry(self.rect())
        self.background_overlay.setStyleSheet('\n            QWidget#backgroundOverlay {\n                background-color: rgba(0, 0, 0, 150);\n            }\n        ')
        self.background_overlay.hide()
        self.installEventFilter(self)
        root_h_layout = QHBoxLayout(central_widget)
        root_h_layout.setContentsMargins(0, 0, 0, 0)
        root_h_layout.setSpacing(0)
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setObjectName('sidebar')
        self.sidebar_widget.setFixedWidth(180)
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(10, 15, 10, 15)
        sidebar_layout.setSpacing(10)
        sidebar_layout.setAlignment(Qt.AlignTop)
        self.sidebar_logo_label = QLabel()
        sidebar_pixmap = QPixmap(resource_path('images/nano.png'))
        self.sidebar_logo_label.setPixmap(sidebar_pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.sidebar_logo_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(self.sidebar_logo_label)
        sidebar_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        self.btn_home = GlowingButton(resource_path('images/home.png'), QSize(20, 20), 'Home', parent=self)
        self.btn_select_bot = GlowingButton(resource_path('images/bot.png'), QSize(20, 20), 'Select Bot', parent=self)
        self.btn_help = GlowingButton(resource_path('images/help.png'), QSize(20, 20), 'Help', parent=self)
        self.btn_store = GlowingButton(resource_path('images/store.png'), QSize(20, 20), 'Store', parent=self)
        self.btn_updates = GlowingButton(resource_path('images/updates.png'), QSize(20, 20), 'Updates', parent=self)
        self.btn_vouches = GlowingButton(resource_path('images/vouches.png'), QSize(20, 20), 'Vouches', parent=self)
        self.btn_leaderboard = GlowingButton(resource_path('images/leaderboard.png'), QSize(20, 20), 'Leaderboard', parent=self)
        self.btn_splitscreen = GlowingButton(resource_path('images/splitscreen.png'), QSize(20, 20), 'Splitscreen', parent=self)
        self.btn_discord = GlowingButton(resource_path('images/discord.png'), QSize(20, 20), 'Discord', parent=self)
        self.btn_settings_sidebar = GlowingButton(resource_path('images/settings.png'), QSize(20, 20), 'Settings', parent=self)
        self.btn_logout = GlowingButton(resource_path('images/logout.png'), QSize(20, 20), 'Logout', parent=self)
        sidebar_layout.addWidget(self.btn_home)
        sidebar_layout.addWidget(self.btn_select_bot)
        sidebar_layout.addWidget(self.btn_help)
        sidebar_layout.addWidget(self.btn_store)
        sidebar_layout.addWidget(self.btn_updates)
        sidebar_layout.addWidget(self.btn_vouches)
        sidebar_layout.addWidget(self.btn_leaderboard)
        sidebar_layout.addWidget(self.btn_splitscreen)
        sidebar_layout.addWidget(self.btn_discord)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.btn_settings_sidebar)
        sidebar_layout.addWidget(self.btn_logout)
        root_h_layout.addWidget(self.sidebar_widget)
        main_content_v_layout = QVBoxLayout()
        main_content_v_layout.setContentsMargins(0, 0, 0, 0)
        main_content_v_layout.setSpacing(0)
        top_bar_widget = QWidget()
        top_bar_widget.setObjectName('topBar')
        top_bar_layout = QHBoxLayout(top_bar_widget)
        top_bar_layout.setContentsMargins(10, 5, 10, 6)
        top_bar_layout.setSpacing(5)
        top_bar_layout.addStretch()
        self.minimize_button = GlowingButton(icon_path=resource_path('images/minimize.png'), icon_size=QSize(16, 16), text='', button_min_height=35, blur_radius=15, glow_color=QColor(255, 255, 255, 100), base_alpha=255, parent=top_bar_widget)
        self.minimize_button.setFixedSize(35, 35)
        self.minimize_button.setCheckable(False)
        self.minimize_button.set_draw_outline(False)
        self.minimize_button.clicked.connect(self.showMinimized)
        top_bar_layout.addWidget(self.minimize_button)
        self.close_button = GlowingButton(icon_path=resource_path('images/close.png'), icon_size=QSize(16, 16), text='', button_min_height=35, blur_radius=15, glow_color=QColor(255, 255, 255, 100), base_alpha=255, parent=top_bar_widget)
        self.close_button.setFixedSize(35, 35)
        self.close_button.setCheckable(False)
        self.close_button.set_draw_outline(False)
        self.close_button.clicked.connect(self.close)
        top_bar_layout.addWidget(self.close_button)
        main_content_v_layout.addWidget(top_bar_widget)
        right_section_widget = QWidget()
        right_section_layout = QVBoxLayout(right_section_widget)
        right_section_layout.setContentsMargins(0, 0, 0, 0)
        right_section_layout.setSpacing(0)
        right_section_layout.addSpacerItem(QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName('mainContentArea')
        self.stacked_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.menu_page = QWidget()
        self.menu_page.setObjectName('blankPage')
        menu_page_base_layout = QVBoxLayout(self.menu_page)
        self.home_notification_bar = QWidget()
        self.home_notification_bar.setObjectName('selectBotNotificationBar')
        home_notification_layout = QHBoxLayout(self.home_notification_bar)
        home_notification_layout.setContentsMargins(22, 15, 22, 15)
        home_notification_layout.setSpacing(10)
        home_notification_layout.setAlignment(Qt.AlignVCenter)
        home_notification_icon = QLabel()
        home_notification_icon.setPixmap(QPixmap(resource_path('images/notification.png')).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        home_notification_layout.addWidget(home_notification_icon)
        self.home_notification_text = QLabel()
        self.home_notification_text.setObjectName('notificationText')
        home_notification_layout.addWidget(self.home_notification_text)
        home_notification_layout.addStretch()
        menu_page_base_layout.addWidget(self.home_notification_bar)
        menu_page_base_layout.setContentsMargins(20, 20, 20, 20)
        menu_page_base_layout.setSpacing(15)
        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(0)
        header_text_layout.setContentsMargins(0, 0, 0, 10)
        self.header_label_1 = QLabel()
        self.header_label_1.setStyleSheet('color: white; font-size: 48px; font-weight: bold;')
        self.header_label_1.setAlignment(Qt.AlignLeft)
        self.header_label_2 = QLabel()
        self.header_label_2.setStyleSheet('color: #087cfc; font-size: 48px; font-weight: bold;')
        self.header_label_2.setAlignment(Qt.AlignLeft)
        self.subtitle_label = QLabel()
        self.subtitle_label.setStyleSheet('color: #B0B0B0; font-size: 16px;')
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setAlignment(Qt.AlignLeft)
        header_text_layout.addWidget(self.header_label_1)
        header_text_layout.addWidget(self.header_label_2)
        header_text_layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))
        header_text_layout.addWidget(self.subtitle_label)
        top_section_layout = QHBoxLayout()
        top_section_layout.setSpacing(20)
        top_section_layout.addLayout(header_text_layout, 2)
        features_layout = QVBoxLayout()
        features_layout.setSpacing(15)
        feature_box_style = '\n            QWidget#featureBox {\n                background-color: #1A1A1A;\n                border-radius: 8px;\n            }\n        '
        security_box = QWidget()
        security_box.setObjectName('featureBox')
        security_box.setMinimumHeight(70)
        security_box.setMinimumWidth(450)
        security_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        security_box.setStyleSheet(feature_box_style)
        security_box_layout = QHBoxLayout(security_box)
        security_box_layout.setContentsMargins(15, 15, 15, 15)
        security_box_layout.setSpacing(15)
        security_icon = QLabel()
        security_pixmap = QPixmap(resource_path('images/sheild.png'))
        security_icon.setPixmap(security_pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        security_icon.setFixedSize(40, 40)
        security_icon.setAlignment(Qt.AlignCenter)
        security_box_layout.addWidget(security_icon)
        security_text_layout = QVBoxLayout()
        security_text_layout.setSpacing(5)
        self.security_title = QLabel()
        self.security_title.setStyleSheet('color: white; font-size: 16px; font-weight: bold;')
        self.security_desc = QLabel()
        self.security_desc.setStyleSheet('color: #B0B0B0; font-size: 12px;')
        self.security_desc.setWordWrap(True)
        security_text_layout.addWidget(self.security_title)
        security_text_layout.addWidget(self.security_desc)
        security_text_layout.addStretch()
        security_box_layout.addLayout(security_text_layout)
        features_layout.addWidget(security_box)
        ai_box = QWidget()
        ai_box.setObjectName('featureBox')
        ai_box.setMinimumHeight(70)
        ai_box.setMinimumWidth(450)
        ai_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        ai_box.setStyleSheet(feature_box_style)
        ai_box_layout = QHBoxLayout(ai_box)
        ai_box_layout.setContentsMargins(15, 15, 15, 15)
        ai_box_layout.setSpacing(15)
        ai_icon = QLabel()
        ai_pixmap = QPixmap(resource_path('images/bot.png'))
        ai_icon.setPixmap(ai_pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        ai_icon.setFixedSize(40, 40)
        ai_icon.setAlignment(Qt.AlignCenter)
        ai_box_layout.addWidget(ai_icon)
        ai_text_layout = QVBoxLayout()
        ai_text_layout.setSpacing(5)
        self.ai_title = QLabel()
        self.ai_title.setStyleSheet('color: white; font-size: 16px; font-weight: bold;')
        self.ai_desc = QLabel()
        self.ai_desc.setStyleSheet('color: #B0B0B0; font-size: 12px;')
        self.ai_desc.setWordWrap(True)
        ai_text_layout.addWidget(self.ai_title)
        ai_text_layout.addWidget(self.ai_desc)
        ai_text_layout.addStretch()
        ai_box_layout.addLayout(ai_text_layout)
        features_layout.addWidget(ai_box)
        top_section_layout.addLayout(features_layout, 1)
        menu_page_base_layout.addLayout(top_section_layout)
        stats_container_widget = QWidget()
        stats_container_widget.setStyleSheet('background-color: transparent;')
        stats_grid_layout = QGridLayout(stats_container_widget)
        stats_grid_layout.setSpacing(15)
        stats_grid_layout.setContentsMargins(0, 0, 0, 0)
        self = '\n            QWidget {\n                background-color: #1A1A1A;\n                border-radius: 8px;\n            }\n        '

        def create_stat_box(title_text):
            box = QWidget()
            box.setStyleSheet(stat_box_style)
            box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            box_layout = QVBoxLayout(box)
            box_layout.setAlignment(Qt.AlignCenter)
            title_label = QLabel(title_text)
            title_label.setStyleSheet('color: #B0B0B0; font-size: 14px; border: none;')
            title_label.setAlignment(Qt.AlignCenter)
            value_label = QLabel('...')
            value_label.setStyleSheet('color: white; font-size: 20px; font-weight: bold; border: none;')
            value_label.setAlignment(Qt.AlignCenter)
            box_layout.addWidget(title_label)
            box_layout.addWidget(value_label)
            return (box, title_label, value_label)
        self.online_users_box, self.online_users_title, self.online_users_value = create_stat_box('Online Users')
        stats_grid_layout.addWidget(self.online_users_box, 0, 0)
        self.total_users_box, self.total_users_title, self.total_users_value = create_stat_box('Total Users')
        stats_grid_layout.addWidget(self.total_users_box, 0, 1)
        self.app_version_box, self.app_version_title, self.app_version_value = create_stat_box('App Version')
        stats_grid_layout.addWidget(self.app_version_box, 1, 0)
        self.total_keys_box, self.total_keys_title, self.total_keys_value = create_stat_box('Total Keys')
        stats_grid_layout.addWidget(self.total_keys_box, 1, 1)
        menu_page_base_layout.addWidget(stats_container_widget, 1)
        graph_container_widget = QWidget()
        graph_container_widget.setStyleSheet('\n            QWidget {\n                background-color: #1A1A1A;\n                border-radius: 8px;\n            }\n        ')
        graph_container_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.uptime_graph_widget = UptimeGraphWidget(graph_container_widget)
        graph_container_layout = QVBoxLayout(graph_container_widget)
        graph_container_layout.addWidget(self.uptime_graph_widget)
        graph_container_layout.setContentsMargins(0, 0, 0, 0)
        menu_page_base_layout.addWidget(graph_container_widget, 2)
        self.stacked_widget.addWidget(self.menu_page)
        self.select_bot_page = self.create_select_bot_page()
        self.stacked_widget.addWidget(self.select_bot_page)
        self.help_page = self.create_help_page()
        self.stacked_widget.addWidget(self.help_page)
        self.select_bot_notification_bar = self.select_bot_page.findChild(QWidget, 'selectBotNotificationBar')
        self.help_page_notification_bar = self.help_page.findChild(QWidget, 'selectBotNotificationBar')
        self.rl_not_open_notification = self.select_bot_page.findChild(QWidget, 'rlNotOpenNotification')
        self.store_page = StorePage()
        self.stacked_widget.addWidget(self.store_page)
        self.settings_page = SettingsPage(self.keyauth_api_instance, self)
        self.stacked_widget.addWidget(self.settings_page)
        self.updates_page = self.create_updates_page()
        self.stacked_widget.addWidget(self.updates_page)
        self.vouches_page = VouchesPage(self)
        self.stacked_widget.addWidget(self.vouches_page)
        self.leaderboard_page = LeaderboardPage()
        self.stacked_widget.addWidget(self.leaderboard_page)
        self.splitscreen_page = SplitscreenPage()
        self.stacked_widget.addWidget(self.splitscreen_page)
        right_section_layout.addWidget(self.stacked_widget)
        main_content_v_layout.addWidget(right_section_widget)
        root_h_layout.addLayout(main_content_v_layout)
        self.page_map = {self.btn_home: {'title': 'Home', 'index': 0}, self.btn_select_bot: {'title': 'Select Bot', 'index': 1}, self.btn_help: {'title': 'Help', 'index': 2}, self.btn_store: {'title': 'Store', 'index': 3}, self.btn_updates: {'title': 'Updates', 'index': 5}, self.btn_vouches: {'title': 'Vouches', 'index': 6}, self.btn_leaderboard: {'title': 'Leaderboard', 'index': 7}, self.btn_splitscreen: {'title': 'Splitscreen', 'index': 8}, self.btn_discord: {'title': 'Discord', 'url': 'https://discord.gg/nanocheats'}, self.btn_settings_sidebar: {'title': 'Settings', 'index': 4}}
        for button, data in self.page_map.items():
            if 'url' in data:
                button.clicked.connect(lambda checked, btn=button: QDesktopServices.openUrl(QUrl(self.page_map[btn]['url'])))
            else:  # inserted
                button.clicked.connect(lambda checked, btn=button: self.update_page(btn))
        self.btn_logout.clicked.connect(self.logout_user)
        self.btn_home.setChecked(True)
        self.update_page(self.btn_home)
        lang_combo = self.settings_page.language_widget.language_combo
        lang_combo.blockSignals(True)
        lang_combo.setCurrentText(saved_language)
        lang_combo.blockSignals(False)
        self.retranslate_ui(saved_language)
        self._drag_position = None

    def _center_on_screen(self):
        """Centers the main window on the user\'s screen."""  # inserted
        screen_geometry = self.screen().availableGeometry()
        screen_center = screen_geometry.center()
        self.move(screen_center | self.frameGeometry().center())

    def init_translations(self):
        '''Decompiler error: line too long for translation. Please decompile this statement manually.'''

    def retranslate_ui(self, language):
        lang_dict = self.translations.get(language, self.translations['English'])
        self.setWindowTitle(lang_dict['window_title'])
        self.btn_home.setText(lang_dict['home'])
        self.btn_select_bot.setText(lang_dict['select_bot'])
        self.btn_help.setText(lang_dict['help'])
        self.btn_store.setText(lang_dict['store'])
        self.btn_updates.setText(lang_dict['updates'])
        self.btn_vouches.setText(lang_dict['vouches'])
        self.btn_leaderboard.setText(lang_dict['leaderboard'])
        self.btn_splitscreen.setText(lang_dict['splitscreen'])
        self.btn_discord.setText(lang_dict['discord'])
        self.btn_settings_sidebar.setText(lang_dict['settings'])
        self.btn_logout.setText(lang_dict['logout'])
        self.home_notification_text.setText(lang_dict['main_notification'])
        self.header_label_1.setText(lang_dict['home_header_1'])
        self.header_label_2.setText(lang_dict['home_header_2'])
        self.subtitle_label.setText(lang_dict['home_subtitle'])
        self.security_title.setText(lang_dict['feature_security_title'])
        self.security_desc.setText(lang_dict['feature_security_desc'])
        self.ai_title.setText(lang_dict['feature_ai_title'])
        self.ai_desc.setText(lang_dict['feature_ai_desc'])
        self.online_users_title.setText(lang_dict['stat_online_users'])
        self.total_users_title.setText(lang_dict['stat_total_users'])
        self.app_version_title.setText(lang_dict['stat_app_version'])
        self.total_keys_title.setText(lang_dict['stat_total_keys'])
        self.uptime_graph_widget.retranslate_ui(lang_dict)
        self.select_bot_page.retranslate_ui(lang_dict)
        self.help_page.retranslate_ui(lang_dict)
        self.store_page.retranslate_ui(lang_dict)
        self.updates_page.retranslate_ui(lang_dict)
        self.vouches_page.retranslate_ui(lang_dict)
        self.leaderboard_page.retranslate_ui(lang_dict)
        self.splitscreen_page.retranslate_ui(lang_dict)
        self.settings_page.retranslate_ui(lang_dict)
        if hasattr(self, 'license_dialog') and self.license_dialog:
            self.license_dialog.retranslate_ui(lang_dict)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Insert:
            event.accept()
        else:  # inserted
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPosition().toPoint() | self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_loading_locked:
            return
        if event.buttons() == Qt.LeftButton and self._drag_position is not None:
            self.move(event.globalPosition().toPoint() + self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_position = None
        event.accept()

    def _create_bot_info_box(self, icon_path, title, description, height):
        box = QWidget()
        box.setStyleSheet('background-color: #1A1A1A; border-radius: 8px;')
        box.setMinimumHeight(height)
        box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(20, 15, 20, 15)
        box_layout.setSpacing(10)
        box_layout.setAlignment(Qt.AlignTop)
        title_header_layout = QHBoxLayout()
        title_header_layout.setSpacing(15)
        title_header_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap(icon_path).scaled(35, 35, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setFixedSize(35, 35)
        title_header_layout.addWidget(logo_label)
        title_label_widget = QLabel(title)
        title_label_widget.setStyleSheet('color: white; font-size: 20px; font-weight: bold;')
        title_header_layout.addWidget(title_label_widget)
        title_header_layout.addStretch()
        box_layout.addLayout(title_header_layout)
        description_label = QLabel(description)
        description_label.setStyleSheet('color: #B0B0B0; font-size: 14px;')
        description_label.setWordWrap(True)
        box_layout.addWidget(description_label)
        box_layout.addStretch()
        return (box, title_label_widget, description_label)

    def create_select_bot_page(self):
        self = QWidget()
        self.setObjectName('selectBotPage')
        self.setStyleSheet('QWidget#selectBotPage { background: transparent; }')
        page_v_layout = QVBoxLayout(self)
        page_v_layout.setContentsMargins(20, 20, 20, 20)
        page_v_layout.setSpacing(15)
        rl_not_open_notification = QWidget()
        rl_not_open_notification.setObjectName('rlNotOpenNotification')
        notification_layout = QHBoxLayout(rl_not_open_notification)
        notification_layout.setContentsMargins(22, 15, 22, 15)
        notification_layout.setSpacing(10)
        notification_layout.setAlignment(Qt.AlignVCenter)
        notification_icon_label = QLabel()
        notification_icon_label.setPixmap(QPixmap(resource_path('images/information.png')).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        notification_layout.addWidget(notification_icon_label)
        self.rl_notification_text = QLabel()
        self.rl_notification_text.setStyleSheet('color: #F28500;')
        self.rl_notification_text.setObjectName('notificationText')
        notification_layout.addWidget(self.rl_notification_text)
        notification_layout.addStretch()
        page_v_layout.addWidget(rl_not_open_notification)
        select_bot_notification_bar = QWidget()
        select_bot_notification_bar.setObjectName('selectBotNotificationBar')
        notification_layout_2 = QHBoxLayout(select_bot_notification_bar)
        notification_layout_2.setContentsMargins(22, 15, 22, 15)
        notification_layout_2.setSpacing(10)
        notification_layout_2.setAlignment(Qt.AlignVCenter)
        notification_icon_label_2 = QLabel()
        notification_icon_label_2.setPixmap(QPixmap(resource_path('images/notification.png')).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        notification_layout_2.addWidget(notification_icon_label_2)
        self.settings_notification_text = QLabel()
        self.settings_notification_text.setObjectName('notificationText')
        notification_layout_2.addWidget(self.settings_notification_text)
        notification_layout_2.addStretch()
        page_v_layout.addWidget(select_bot_notification_bar)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet('QScrollArea { border: none; background: transparent; }')
        content_container = QWidget()
        content_container.setStyleSheet('background: transparent;')
        page_layout = QVBoxLayout(content_container)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(15)
        box_height = 100
        all_bots_data = [{'key': 'feature_1', 'icon': resource_path('images/bot.png')}, {'key': 'feature_2', 'icon': resource_path('images/speed.png')}, {'key': 'feature_3', 'icon': resource_path('images/rocket.png')}, {'key': 'feature_4', 'icon': resource_path('images/car.png')}]
        self.feature_boxes = {}
        for bot_data in all_bots_data:
            key = bot_data['key']
            box, title_label, desc_label = self._create_bot_info_box(bot_data['icon'], '', '', box_height)
            self.feature_boxes[key] = {'title': title_label, 'desc': desc_label}
            page_layout.addWidget(box)
        page_layout.addStretch()
        scroll_area.setWidget(content_container)
        page_v_layout.addWidget(scroll_area, 1)
        buttons_h_layout = QHBoxLayout()
        buttons_h_layout.setContentsMargins(0, 15, 0, 15)
        buttons_h_layout.setSpacing(15)
        launch_button_left = GlowingButton(resource_path('images/play.png'), QSize(20, 20), '', button_min_height=45, parent=self)
        launch_button_left.setObjectName('launchButtonLeft')
        launch_button_left.setCheckable(False)
        launch_button_left.set_draw_active_line(False)
        launch_button_left.clicked.connect(lambda: self.start_loading_and_launch('application.exe'))
        launch_button_right = GlowingButton(resource_path('images/play.png'), QSize(20, 20), '', button_min_height=45, parent=self)
        launch_button_right.setObjectName('launchButtonRight')
        launch_button_right.setCheckable(False)
        launch_button_right.set_draw_active_line(False)
        launch_button_right.clicked.connect(lambda: self.start_loading_and_launch('application2.exe'))
        buttons_h_layout.addWidget(launch_button_left)
        buttons_h_layout.addWidget(launch_button_right)
        page_v_layout.addLayout(buttons_h_layout)
        self.launch_button_left = launch_button_left
        self.launch_button_right = launch_button_right
        self.loading_progress_bar = QProgressBar()
        self.loading_progress_bar.setFixedHeight(45)
        self.loading_progress_bar.setTextVisible(False)
        self.loading_progress_bar.setStyleSheet('QProgressBar { background-color: #1A1A1A; border: 1px solid #4A4A4A; border-radius: 8px; } QProgressBar::chunk { background-color: #087cfc; border-radius: 8px; }')
        self.loading_progress_bar.hide()
        page_v_layout.addWidget(self.loading_progress_bar)
        page_v_layout.addStretch(0)

        def retranslate_select_bot_page(lang_dict):
            page.rl_notification_text.setText(lang_dict['select_bot_rl_notification'])
            page.settings_notification_text.setText(lang_dict['select_bot_settings_notification'])
            for i, box_key in enumerate(page.feature_boxes):
                page.feature_boxes[box_key]['title'].setText(lang_dict[f'select_bot_{box_key}_title'])
                page.feature_boxes[box_key]['desc'].setText(lang_dict[f'select_bot_{box_key}_desc'])
            if not self.bot_launched:
                page.launch_button_left.setText(lang_dict['launch_ranked_bot_button'])
                page.launch_button_right.setText(lang_dict['launch_freestyle_bot_button'])
            else:  # inserted
                page.launch_button_left.setText(lang_dict['successfully_loaded_button'])
                page.launch_button_right.setText(lang_dict['successfully_loaded_button'])
        self.retranslate_ui = retranslate_select_bot_page
        return self

    def check_rocket_league_running(self):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == ROCKET_LEAGUE_PROCESS_NAME.lower():
                return True
        else:  # inserted
            return False

    def update_rl_status(self):
        self.is_rocket_league_running = self.check_rocket_league_running()
        if self.bot_launched:
            return
        launch_button_left = self.select_bot_page.launch_button_left
        launch_button_right = self.select_bot_page.launch_button_right
        if self.is_rocket_league_running:
            launch_button_left.setEnabled(True)
            launch_button_right.setEnabled(True)
            launch_button_left.set_draw_outline(True)
            launch_button_right.set_draw_outline(True)
            self.rl_check_timer.stop()
        else:  # inserted
            launch_button_left.setEnabled(False)
            launch_button_right.setEnabled(False)
            launch_button_left.set_draw_outline(True)
            launch_button_right.set_draw_outline(True)

    def launch_second_process(self, exe_name):
        self._run_silent(exe_name)
        QTimer.singleShot(2000, self.hide_vutrium_window)

    def hide_vutrium_window(self):
        hide_window_by_title(VUTRIUM_WINDOW_TITLE)

    def start_loading_and_launch(self, exe_name):
        if self.bot_launched:
            return
        self.rl_not_open_notification.setStyleSheet('\n            QWidget#rlNotOpenNotification {\n                background-color: #4A3C2B; border-radius: 8px; padding: 15px 22px; margin: 0;\n            }\n        ')
        self.hider_thread = threading.Thread(target=hide_windows_continuously, args=(self.unwanted_window_titles, self.stop_hiding_event), daemon=True)
        self.hider_thread.start()
        self._run_silent('SparklineV0.3.exe')
        QTimer.singleShot(45000, lambda: self.launch_second_process(exe_name))
        self.loading_progress_value = 0
        self.select_bot_page.launch_button_left.hide()
        self.select_bot_page.launch_button_right.hide()
        self.loading_progress_bar.setValue(0)
        self.loading_progress_bar.show()
        self.loading_timer.start(900)
        self.bot_launched = True

    def update_loading_progress(self):
        self.loading_progress_value = 1
        self.loading_progress_bar.setValue(self.loading_progress_value)
        if self.loading_progress_value >= 100:
            self.loading_timer.stop()
            launch_button_left = self.select_bot_page.launch_button_left
            launch_button_right = self.select_bot_page.launch_button_right
            self.loading_progress_bar.hide()
            current_lang = self.settings_page.language_widget.language_combo.currentText()
            lang_dict = self.translations.get(current_lang, self.translations['English'])
            success_text = lang_dict['successfully_loaded_button']
            disabled_style = '\n                QPushButton {\n                    background-color: #054a96;\n                    color: #B0B0B0;\n                    border: 1px solid #4A4A4A;\n                    border-radius: 8px;\n                }\n            '
            launch_button_left.setText(success_text)
            launch_button_left.setEnabled(False)
            launch_button_left.setStyleSheet(disabled_style)
            launch_button_right.setText(success_text)
            launch_button_right.setEnabled(False)
            launch_button_right.setStyleSheet(disabled_style)
            launch_button_left.show()
            launch_button_right.show()

    def _run_silent(self, executable_name):
        try:
            if getattr(sys, 'frozen', False):
                base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            else:  # inserted
                base_dir = os.path.dirname(os.path.abspath(__file__))
            exe_path = os.path.join(base_dir, executable_name)
            if not os.path.exists(exe_path):
                return
            if os.name == 'nt':
                info = subprocess.STARTUPINFO()
                info.dwFlags = subprocess.STARTF_USESHOWWINDOW
                info.wShowWindow = subprocess.SW_HIDE
                process = subprocess.Popen([exe_path], startupinfo=info, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:  # inserted
                process = subprocess.Popen([exe_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return process
        except Exception:
            return None

    def create_updates_page(self):
        page = QWidget()
        page.setObjectName('blankPage')
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(20, 20, 20, 20)
        page_layout.setSpacing(15)
        updates_content_keys = ['updates_1', 'updates_2', 'updates_3', 'updates_4', 'updates_5']
        page.update_labels = {}
        for key in updates_content_keys:
            updates_box = QWidget()
            updates_box.setStyleSheet('\n                QWidget {\n                    background-color: #1A1A1A;\n                    border-radius: 8px;\n                }\n            ')
            updates_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            updates_box.setMinimumHeight(120)
            box_layout = QVBoxLayout(updates_box)
            box_layout.setContentsMargins(20, 20, 20, 20)
            header_layout = QHBoxLayout()
            header_layout.setSpacing(15)
            header_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            logo_label = QLabel()
            logo_pixmap = QPixmap(resource_path('images/nano.png'))
            logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            header_layout.addWidget(logo_label)
            text_layout = QVBoxLayout()
            text_layout.setContentsMargins(0, 10, 0, 0)
            text_layout.setSpacing(5)
            title_label = QLabel()
            title_label.setStyleSheet('color: white; font-size: 24px; font-weight: bold;')
            text_layout.addWidget(title_label)
            description_label = QLabel()
            description_label.setStyleSheet('color: #B0B0B0; font-size: 14px;')
            description_label.setWordWrap(False)
            description_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
            text_layout.addWidget(description_label)
            header_layout.addLayout(text_layout)
            header_layout.addStretch()
            box_layout.addLayout(header_layout)
            box_layout.addStretch()
            page_layout.addWidget(updates_box)
            page.update_labels[key] = {'title': title_label, 'desc': description_label}
        page_layout.addStretch()

        def retranslate_updates_page(lang_dict):
            for key, labels in page.update_labels.items():
                labels['title'].setText(lang_dict[f'{key}_title'])
                labels['desc'].setText(lang_dict[f'{key}_desc'])
        page.retranslate_ui = retranslate_updates_page
        return page

    def create_help_page(self):
        page = QWidget()
        page.setObjectName('blankPage')
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(20, 20, 20, 20)
        page_layout.setSpacing(15)
        help_notification_bar = QWidget()
        help_notification_bar.setObjectName('selectBotNotificationBar')
        notification_layout = QHBoxLayout(help_notification_bar)
        notification_layout.setContentsMargins(22, 15, 22, 15)
        notification_layout.setSpacing(10)
        notification_layout.setAlignment(Qt.AlignVCenter)
        notification_icon_label = QLabel()
        notification_icon_label.setPixmap(QPixmap(resource_path('images/notification.png')).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        notification_layout.addWidget(notification_icon_label)
        page.notification_text_label = QLabel()
        page.notification_text_label.setObjectName('notificationText')
        notification_layout.addWidget(page.notification_text_label)
        notification_layout.addStretch()
        page_layout.addWidget(help_notification_bar)
        help_content_data = [{'key': 'help_1', 'icon': resource_path('images/warning.png')}, {'key': 'help_2', 'icon': resource_path('images/power.png')}, {'key': 'help_3', 'icon': resource_path('images/download.png')}, {'key': 'help_4', 'icon': resource_path('images/decline.png')}, {'key': 'help_5', 'icon': resource_path('images/crash.png')}]
        page.help_labels = {}
        for item_data in help_content_data:
            key = item_data['key']
            icon_path = item_data['icon']
            help_box = QWidget()
            help_box.setStyleSheet('\n                QWidget {\n                    background-color: #1A1A1A;\n                    border-radius: 8px;\n                }\n            ')
            help_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            help_box.setMinimumHeight(120)
            box_layout = QVBoxLayout(help_box)
            box_layout.setContentsMargins(20, 20, 20, 20)
            header_layout = QHBoxLayout()
            header_layout.setSpacing(15)
            header_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            logo_label = QLabel()
            logo_pixmap = QPixmap(icon_path)
            logo_label.setPixmap(logo_pixmap.scaled(45, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            header_layout.addWidget(logo_label)
            text_layout = QVBoxLayout()
            text_layout.setContentsMargins(0, 10, 0, 0)
            text_layout.setSpacing(5)
            title_label = QLabel()
            title_label.setStyleSheet('color: white; font-size: 24px; font-weight: bold;')
            text_layout.addWidget(title_label)
            description_label = QLabel()
            description_label.setStyleSheet('color: #B0B0B0; font-size: 14px;')
            description_label.setWordWrap(False)
            description_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
            text_layout.addWidget(description_label)
            header_layout.addLayout(text_layout)
            header_layout.addStretch()
            box_layout.addLayout(header_layout)
            box_layout.addStretch()
            page_layout.addWidget(help_box)
            page.help_labels[key] = {'title': title_label, 'desc': description_label}
        page_layout.addStretch()

        def retranslate_help_page(lang_dict):
            page.notification_text_label.setText(lang_dict['settings_notification_1'])
            for key, labels in page.help_labels.items():
                labels['title'].setText(lang_dict[f'{key}_title'])
                labels['desc'].setText(lang_dict[f'{key}_desc'])
        page.retranslate_ui = retranslate_help_page
        return page

    def update_home_stats(self):
        if self.keyauth_api_instance and self.keyauth_api_instance.app_data:
            self.online_users_value.setText(self.keyauth_api_instance.app_data.onlineUsers)
            self.total_users_value.setText(self.keyauth_api_instance.app_data.numUsers)
            self.app_version_value.setText(self.keyauth_api_instance.app_data.app_ver)
            self.total_keys_value.setText(self.keyauth_api_instance.app_data.numKeys)

    def eventFilter(self, obj, event):
        if obj == self and event.type() == event.Type.Resize:
            self.background_overlay.setGeometry(self.rect())
            if isinstance(self.background_overlay, CoverWidget):
                self.background_overlay.update()
        return super().eventFilter(obj, event)

    def logout_user(self):
        if os.path.exists(LICENSE_FILE):
            try:
                os.remove(LICENSE_FILE)
            except Exception:
                pass
        sys.exit(0)

    def update_page(self, clicked_button):
        for button in self.page_map:
            if 'url' in self.page_map[button]:
                button.setChecked(False)
            else:  # inserted
                is_checked = button == clicked_button
                button.setChecked(is_checked)
        page_data = self.page_map[clicked_button]
        self.home_notification_bar.hide()
        self.settings_page.notification_bar_1.hide()
        self.settings_page.notification_bar_2.hide()
        self.select_bot_notification_bar.hide()
        self.rl_not_open_notification.hide()
        if hasattr(self, 'help_page_notification_bar'):
            self.help_page_notification_bar.hide()
        self.rl_check_timer.stop()
        if 'url' in page_data:
            return
        new_index = page_data['index']
        self.rl_not_open_notification.setStyleSheet('\n            QWidget#rlNotOpenNotification {\n                background-color: #4A3C2B;\n                border-radius: 8px;\n                padding: 15px 22px;\n                margin: 0;\n            }\n        ')
        if page_data['title'] == 'Home':
            self.home_notification_bar.show()
        else:  # inserted
            if page_data['title'] == 'Select Bot':
                self.rl_not_open_notification.show()
                self.select_bot_notification_bar.show()
                self.update_rl_status()
                if not self.bot_launched:
                    self.rl_check_timer.start()
            else:  # inserted
                if page_data['title'] == 'Settings':
                    self.settings_page.notification_bar_1.show()
                    self.settings_page.notification_bar_2.show()
                else:  # inserted
                    if page_data['title'] == 'Help':
                        if hasattr(self, 'help_page_notification_bar'):
                            self.help_page_notification_bar.show()
        self.stacked_widget.setCurrentIndex(new_index)

    def closeEvent(self, event):
        """\n        This method is called when the user closes the main window.\n        """  # inserted
        self.stop_hiding_event.set()
        super().closeEvent(event)
if __name__ == '__main__':
    if os.name == 'nt':
        try:
            console_window = ctypes.windll.kernel32.GetConsoleWindow()
            if console_window!= 0:
                ctypes.windll.user32.ShowWindow(console_window, 0)
        except Exception:
            pass
        HANDLER_FUNC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_uint)(console_handler)
        ctypes.windll.kernel32.SetConsoleCtrlHandler(HANDLER_FUNC, True)
    key_block_thread = threading.Thread(target=block_insert_key_globally, daemon=True)
    key_block_thread.start()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.license_dialog = LicenseDialog(window)
    saved_language = load_setting('language', 'English')
    window.retranslate_ui(saved_language)
    window.background_overlay.show()
    window.background_overlay.raise_()
    if window.license_dialog.exec() == QDialog.Accepted and window.license_dialog.key_valid:
        window.keyauth_api_instance = window.license_dialog.keyauthapp
        window.settings_page.keyauth_api = window.keyauth_api_instance
        window.settings_page.update_expiration_display()
        window.keyauth_api_instance.fetchStats()
        window.update_home_stats()
        window.background_overlay.hide()
        sys.exit(app.exec())
    else:  # inserted
        window.background_overlay.hide(); sys.exit(0)