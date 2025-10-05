# -*- coding: utf-8 -*-
import sys
import cv2
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSlider, QVBoxLayout, QHBoxLayout, QPushButton, QSplitter, QFileDialog, QLineEdit, QCheckBox, QMessageBox, QTabWidget, QDialog, QMenuBar, QAction, QAbstractButton, QOpenGLWidget, QComboBox, QSpinBox, QMainWindow, QToolBar, QSizePolicy, QStyle, QTextEdit, QScrollArea, QMenu
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QProcess, qInstallMessageHandler, QtMsgType
from PyQt5.QtGui import QImage, QPixmap, QIcon, QColor
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import QSize, QRect
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
import json
import logging
import os
import subprocess
# Windows webcam support - removed picamera2
import pydicom
from pydicom.dataset import Dataset, FileDataset
import tempfile
import shutil
import sysconfig
import re
from PIL import Image, TiffImagePlugin

APP_VERSION = "1.0.5" 

# Resolve resource paths reliably when compiled (Nuitka/PyInstaller) or running from source
try:
    # When compiled, some launchers set sys.frozen and use sys.executable directory
    if getattr(sys, "frozen", False):
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        # Fallback to the directory of this file (when running from source)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except Exception:
    # Ultimate fallback to argv[0]
    BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

ASSETS_DIR = os.path.join(BASE_DIR, "assests")

def resource_path(*relative_parts):
    return os.path.join(BASE_DIR, *relative_parts)

# Logging setup to capture issues in compiled builds
LOG_FILE = os.path.join(BASE_DIR, "IMATT_Camera.log")
logger = logging.getLogger("IMATT")
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    try:
        _fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    except Exception:
        # Fallback: write next to executable with a generic name
        _fh = logging.FileHandler(os.path.join(BASE_DIR, "app.log"), encoding="utf-8")
    _fh.setLevel(logging.DEBUG)
    _fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(_fh)
    logging.captureWarnings(True)
    try:
        logger.debug(f"BASE_DIR={BASE_DIR}")
    except Exception:
        pass

# Hint Qt where to find its plugins in standalone build
try:
    qt_plugins_root = os.path.join(BASE_DIR, 'PyQt5', 'qt-plugins')
    if os.path.isdir(qt_plugins_root):
        os.environ.setdefault('QT_PLUGIN_PATH', qt_plugins_root)
        os.environ.setdefault('QT_QPA_PLATFORM_PLUGIN_PATH', os.path.join(qt_plugins_root, 'platforms'))
        logger.debug(f"QT_PLUGIN_PATH set to {os.environ.get('QT_PLUGIN_PATH')}")
        logger.debug(f"QT_QPA_PLATFORM_PLUGIN_PATH set to {os.environ.get('QT_QPA_PLATFORM_PLUGIN_PATH')}")
except Exception:
    pass

def _qt_message_handler(mode, context, message):
    try:
        if mode == QtMsgType.QtDebugMsg:
            logger.debug(f"Qt: {message}")
        elif mode == QtMsgType.QtInfoMsg:
            logger.info(f"Qt: {message}")
        elif mode == QtMsgType.QtWarningMsg:
            logger.warning(f"Qt: {message}")
        elif mode == QtMsgType.QtCriticalMsg:
            logger.error(f"Qt: {message}")
        elif mode == QtMsgType.QtFatalMsg:
            logger.critical(f"Qt: {message}")
    except Exception:
        pass

try:
    qInstallMessageHandler(_qt_message_handler)
except Exception:
    pass


INFO_FIELDS_PATH = resource_path('info_fields.json')

# Create IMATT folder on desktop
def get_imatt_folder():
    # For this specific user, use the correct OneDrive Desktop path
    desktop_path = r"C:\Users\alixa\OneDrive\Desktop"
    
    # Verify the path exists
    if not os.path.exists(desktop_path):
        # Fallback to other possible paths
        possible_desktop_paths = [
            os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop"),
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.environ.get('USERPROFILE', ''), "OneDrive", "Desktop"),
            os.path.join(os.environ.get('USERPROFILE', ''), "Desktop")
        ]
        
        for path in possible_desktop_paths:
            if os.path.exists(path):
                desktop_path = path
                break
        
        # If still no desktop found, use user's home directory
        if not os.path.exists(desktop_path):
            desktop_path = os.path.expanduser("~")
    
    imatt_folder = os.path.join(desktop_path, "IMATT")
    if not os.path.exists(imatt_folder):
        try:
            os.makedirs(imatt_folder)
            print(f"Created IMATT folder at: {imatt_folder}")
        except Exception as e:
            print(f"Error creating IMATT folder: {e}")
            # Fallback to current directory
            imatt_folder = os.path.join(os.getcwd(), "IMATT")
            if not os.path.exists(imatt_folder):
                os.makedirs(imatt_folder)
    
    print(f"Using IMATT folder: {imatt_folder}")
    return imatt_folder

class ToggleSwitch(QAbstractButton):
    def __init__(self, parent=None, checked=False):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(48, 28)
        self._margin = 3
        self._bg_off = Qt.gray
        self._bg_on = QColor("#E89B4C")
        self._circle_off = Qt.white
        self._circle_on = Qt.white
        self._anim = 1.0 if self.isChecked() else 0.0  # Always jump instantly

    def sizeHint(self):
        return QSize(48, 28)

    # Remove animation: set _anim instantly
    def setChecked(self, checked):
        super().setChecked(checked)
        self._anim = 1.0 if checked else 0.0
        self.update()

    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QBrush, QPen
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        margin = self._margin
        bg_rect = rect.adjusted(margin, margin, -margin, -margin)
        # Draw background
        bg_color = QColor(self._bg_off) if self._anim < 0.5 else QColor(self._bg_on)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bg_rect, bg_rect.height()/2, bg_rect.height()/2)
        # Draw circle
        x = margin + self._anim * (bg_rect.width() - bg_rect.height())
        circle_rect = QRect(int(x), margin, bg_rect.height(), bg_rect.height())
        painter.setBrush(QBrush(QColor(self._circle_on)))
        painter.setPen(QPen(Qt.gray, 1))
        painter.drawEllipse(circle_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setChecked(not self.isChecked())
            self.clicked.emit(self.isChecked())
            self.toggled.emit(self.isChecked())

class CameraControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load camera settings first to avoid AttributeError
        self.settings_file_camera = resource_path('settings_camera.json')
        self.camera_settings = self.load_camera_settings()
        # Now safe to use self.camera_settings everywhere below

        self.setWindowTitle("IMATT")
        self.setStyleSheet("background-color: #f0f0f0;")

        # Main layout setup
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Create a menu bar at the top
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setStyleSheet("""
            QMenuBar {
                background: #e0e0e0;
                color: black;
                font-size: 18px;
                padding: 8px 8px;
                min-height: 8px;
            }
            QMenuBar::item {
                background: #f5f5f5;
                color: black;
                padding: 6px 18px;
                margin: 2px 6px;
                border-radius: 6px;
                border: 1.5px solid #b0b0b0;
                transition: background 0.2s, color 0.2s;
            }
            QMenuBar::item:selected {
                background: #bdbdbd;
                color: black;
                border-radius: 6px;
                border: 1.5px solid #b0b0b0;
            }
            QMenuBar::item:pressed {
                background: #9e9e9e;
                color: black;
            }
            QMenu {
                background: #e0e0e0;
                color: black;
                font-size: 16px;
                border: 1px solid #b0b0b0;
            }
            QMenu::item:selected {
                background: #bdbdbd;
                color: black;
                border-radius: 6px;
            }
        """)
        # File menu (first menu)
        file_menu = self.menu_bar.addMenu('File')
        
        # Mode menu (second menu)
        mode_menu = self.menu_bar.addMenu('Mode')
        
        # Create mode submenu actions with proper styling
        general_mode_action = QAction('General', self)
        general_mode_action.setCheckable(True)
        general_mode_action.setChecked(True)  # Default mode
        general_mode_action.triggered.connect(lambda: self.set_mode("General"))
        
        ivf_mode_action = QAction('IVF', self)
        ivf_mode_action.setCheckable(True)
        ivf_mode_action.triggered.connect(lambda: self.set_mode("IVF"))
        
        # Add actions to mode menu
        mode_menu.addAction(general_mode_action)
        mode_menu.addAction(ivf_mode_action)
        
        # Apply the same styling as File menu (inherits from QMenuBar stylesheet)
        
        # Store mode actions for later use
        self.mode_actions = [general_mode_action, ivf_mode_action]
        
        # Camera menu (third menu)
        camera_menu = self.menu_bar.addMenu('Camera')
        
        # Detect available cameras and create menu actions
        self.available_cameras = self.detect_available_cameras()
        self.camera_actions = []
        
        for camera_info in self.available_cameras:
            camera_action = QAction(camera_info['name'], self)
            camera_action.setCheckable(True)
            camera_action.triggered.connect(lambda checked, idx=camera_info['index']: self.set_camera(idx))
            camera_menu.addAction(camera_action)
            self.camera_actions.append(camera_action)
        
        # Set default camera as checked
        selected_camera = self.camera_settings.get("selected_camera", 0)
        for i, camera_info in enumerate(self.available_cameras):
            if camera_info['index'] == selected_camera:
                self.camera_actions[i].setChecked(True)
                break
        else:
            # If selected camera not found, check the first available camera
            if self.camera_actions:
                self.camera_actions[0].setChecked(True)
        
        # Settings action
        settings_action = QAction('Settings', self)
        def show_settings():
            dlg = SettingsDialog(self, self.camera_settings)
            dlg.rotation_changed.connect(self.set_rotation_angle)
            if dlg.exec_() == QDialog.Accepted:
                self.camera_settings = dlg.get_settings()
                self.save_camera_settings()
                self.mode = self.camera_settings.get("mode", "General")
                self.update_mode_ui()
                # Enable/disable mag_combo based on show_scale_bar
                show_bar = self.camera_settings.get('show_scale_bar', True)
                self.mag_combo.setEnabled(show_bar)
                self.eyepiece_combo.setEnabled(show_bar)
        def set_rotation_angle(angle):
            self.rotation_angle = angle
            self.update_frame()
        settings_action.triggered.connect(show_settings)
        file_menu.addAction(settings_action)
        # Print action
        print_action = QAction("Print", self)
        print_action.triggered.connect(self.handle_menu_print)
        file_menu.addAction(print_action)
        # Check Update action
        check_update_action = QAction('Check Update', self)
        check_update_action.triggered.connect(self.check_update)
        file_menu.addAction(check_update_action)
        # About action
        about_action = QAction('About', self)
        def show_about():
            dlg = QDialog(self)
            dlg.setWindowTitle("About")
            dlg.setFixedSize(480, 260)
            main_layout = QVBoxLayout(dlg)
            main_layout.setContentsMargins(24, 18, 24, 12)
            main_layout.setSpacing(10)

            # Logo and text in one row
            row_layout = QHBoxLayout()
            row_layout.setSpacing(18)

            # Logo
            logo_label = QLabel()
            logo_pixmap = QPixmap(os.path.join(ASSETS_DIR, "IMATT.png"))
            scaled_logo = logo_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
            logo_label.setAlignment(Qt.AlignVCenter)
            row_layout.addWidget(logo_label, alignment=Qt.AlignVCenter)

            # Info text
            info_html = f"""
            <div style='font-family:Tahoma,Arial,sans-serif;'>
                <div style='font-size:18px; font-weight:bold; margin-bottom:8px;'>IMATT Camera Software</div>
                <div style='font-size:14px; margin-bottom:6px;'>Version: {APP_VERSION}</div>
                <div style='font-size:13px; color:#444; margin-bottom:2px;'>info@imattco.com</div>
                <div style='font-size:13px; color:#444; margin-bottom:6px;'>+989379412699</div>
                <div style='font-size:12px; color:#444;'>Copyright (c) 2022 IMATT</div>
            </div>
            """
            info_label = QLabel(info_html)
            info_label.setTextFormat(Qt.RichText)
            info_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            row_layout.addWidget(info_label, alignment=Qt.AlignVCenter)

            main_layout.addLayout(row_layout)

            # OK button at the bottom center
            btn_layout = QHBoxLayout()
            btn_layout.addStretch(1)
            ok_btn = QPushButton("OK")
            ok_btn.setFixedWidth(80)
            ok_btn.clicked.connect(dlg.accept)
            btn_layout.addWidget(ok_btn)
            btn_layout.addStretch(1)
            main_layout.addLayout(btn_layout)

            dlg.exec_()
        about_action.triggered.connect(show_about)
        file_menu.addAction(about_action)
        # Set the menu bar as the main window's menu
        self.setMenuBar(self.menu_bar)

        # Set the main widget as the central widget
        self.setCentralWidget(main_widget)

        splitter = QSplitter(Qt.Horizontal)

        control_widget = QWidget()
        self.control_layout = QVBoxLayout(control_widget)

        self.control_layout.setContentsMargins(5, 5, 5, 5)  
        self.control_layout.setSpacing(30)

        # Add company logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("margin: 0px;")  # Optional styling
        logo_pixmap = QPixmap(os.path.join(ASSETS_DIR, "IMATT.png"))  # Replace with your logo path
        scaled_logo = logo_pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(scaled_logo)
        main_layout.addWidget(self.logo_label)

        # Default color for record button
        self.record_button_default_color = "background-color:rgb(206, 204, 204); border-radius: 10px;"

        # Set application icon - Windows path
        icon_path = os.path.join(ASSETS_DIR, "IMATT.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Add logo to the top of the control layout
        self.control_layout.addWidget(self.logo_label)

        # Objective Magnification Selector
        mag_layout = QHBoxLayout()
        mag_label = QLabel("Objective Magnification:")
        self.mag_combo = QComboBox()
        self.mag_combo.addItems(["4X", "10X", "20X", "40X", "100X"])
        self.mag_combo.setCurrentText("40X")
        self.objective_magnification = 40
        def on_mag_change():
            self.objective_magnification = int(self.mag_combo.currentText().replace("X", ""))
        self.mag_combo.currentIndexChanged.connect(on_mag_change)
        mag_layout.addWidget(mag_label)
        mag_layout.addWidget(self.mag_combo)
        self.control_layout.addLayout(mag_layout)

        # C-Mount Lens Adapter Selector
        eyepiece_layout = QHBoxLayout()
        eyepiece_label = QLabel("C-Mount Lens Adapter:")
        self.eyepiece_combo = QComboBox()
        self.eyepiece_combo.addItems(["0.35X", "0.5X", "0.75X", "1.0X"])
        self.eyepiece_combo.setCurrentText("0.5X")
        self.eyepiece_magnification = 0.5
        def on_eyepiece_change():
            self.eyepiece_magnification = float(self.eyepiece_combo.currentText().replace("X", ""))
            self.update_frame()
        self.eyepiece_combo.currentIndexChanged.connect(on_eyepiece_change)
        eyepiece_layout.addWidget(eyepiece_label)
        eyepiece_layout.addWidget(self.eyepiece_combo)
        self.control_layout.addLayout(eyepiece_layout)
        
        # Enable/disable mag_combo based on show_scale_bar
        show_bar = self.camera_settings.get('show_scale_bar', True)
        self.mag_combo.setEnabled(show_bar)
        self.eyepiece_combo.setEnabled(show_bar)

        # Set window flags for Windows - allow normal window behavior
        self.setWindowFlags(Qt.Window)

        # --- Add QTabWidget for sliders ---
        self.tabs = QTabWidget()
        # Make the tab widget expand vertically to fill available space
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setVerticalStretch(20) # Give it priority to expand over the bottom spacer
        self.tabs.setSizePolicy(sizePolicy)
        self.tabs.tabBar().setExpanding(True)
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                height: 40px;
                min-width: 100px;
                font-size: 18px;
                padding: 10px 4px;
                background: #e0e0e0;
                color: #333;
                border: 1px solid #b0b0b0;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #0c838c;
                color: white;
                border: 2px solid #0c838c;
                border-bottom: 2px solid white; /* Blend with pane background */
            }
            QTabBar::tab:!selected {
                background: #e0e0e0;
                color: #333;
            }
            QTabWidget::pane {
                border: 1px solid #b0b0b0;
                top: -2px;
                background: white;
                border-radius: 0 0 8px 8px;
            }
        """)

        # Basic tab (analog filters)
        self.basic_tab = QWidget()
        self.basic_layout = QVBoxLayout(self.basic_tab)
        self.basic_layout.setContentsMargins(5, 5, 5, 5)
        self.basic_layout.addStretch(1)
        # Add analog sliders to basic tab
        # --- iOS-style switch for filter ---
        filter_row = QHBoxLayout()
        self.filter_switch = ToggleSwitch()
        self.filter_switch.setChecked(False)  # Default: OFF for natural colors
        filter_label = QLabel("Enable Filter")
        filter_label.setStyleSheet("font-size: 14px; color: #333;")
        filter_row.addWidget(self.filter_switch)
        filter_row.addWidget(filter_label)
        filter_row.addStretch(1)
        self.basic_layout.addLayout(filter_row)
        self.basic_layout.addStretch(1)
        self.gain_slider = self.add_slider_with_label_tab(self.basic_layout, "Gain", 0, 100, 100, 14)
        self.basic_layout.addStretch(1)
        self.black_level_slider = self.add_slider_with_label_tab(self.basic_layout, "Black Level", 0, 100, 0, 1)
        self.basic_layout.addStretch(1)
        self.gamma_slider = self.add_slider_with_label_tab(self.basic_layout, "Gamma", 10, 300, 100, 1)
        self.basic_layout.addStretch(1)
        self.saturation_slider = self.add_slider_with_label_tab(self.basic_layout, "Saturation", 0, 100, 50, 1)
        self.basic_layout.addStretch(1)
        self.sharpness_slider = self.add_slider_with_label_tab(self.basic_layout, "Sharpness", -200, 200, 1, 5)
        self.basic_layout.addStretch(1)

        # Advance tab (RGB + Hue)
        self.advance_tab = QWidget()
        self.advance_layout = QVBoxLayout(self.advance_tab)
        self.advance_layout.setContentsMargins(5, 5, 5, 5)
        self.advance_layout.addStretch(1)
        # --- Add Enable Filter checkbox to the Advance tab ---
        self.filter_switch_advance = ToggleSwitch()
        self.filter_switch_advance.setChecked(False)  # Default: OFF for natural colors
        filter_label_advance = QLabel("Enable Filter")
        filter_label_advance.setStyleSheet("font-size: 14px; color: #333;")
        filter_row_advance = QHBoxLayout()
        filter_row_advance.addWidget(self.filter_switch_advance)
        filter_row_advance.addWidget(filter_label_advance)
        filter_row_advance.addStretch(1)
        self.advance_layout.addLayout(filter_row_advance)
        self.advance_layout.addStretch(1)
        # --- End of adding checkbox ---
        self.red_slider = self.add_slider_with_label_tab(self.advance_layout, "Red", 0, 255, 255, 1)
        self.advance_layout.addStretch(1)
        self.green_slider = self.add_slider_with_label_tab(self.advance_layout, "Green", 0, 255, 255, 1)
        self.advance_layout.addStretch(1)
        self.blue_slider = self.add_slider_with_label_tab(self.advance_layout, "Blue", 0, 255, 255, 1)
        self.advance_layout.addStretch(1)
        self.hue_switch = ToggleSwitch()
        self.hue_switch.setChecked(False)  # Default: OFF for natural colors
        hue_label = QLabel("Enable Hue Filter")
        hue_label.setStyleSheet("font-size: 14px; color: #333;")
        hue_row = QHBoxLayout()
        hue_row.addWidget(self.hue_switch)
        hue_row.addWidget(hue_label)
        hue_row.addStretch(1)
        self.advance_layout.addLayout(hue_row)
        self.advance_layout.addStretch(1)
        self.hue_slider = self.add_slider_with_label_tab(self.advance_layout, "Hue", 0, 180, 100, 1)
        self.advance_layout.addStretch(1)

        # --- First tab: Info ---
        self.info_tab = QWidget()
        self.info_layout = QVBoxLayout(self.info_tab)
        self.info_layout.setContentsMargins(5, 5, 5, 5)
        self.info_layout.setSpacing(15)
        self.tabs.addTab(self.info_tab, "Info")
        
        self.tabs.addTab(self.basic_tab, "basic")
        self.tabs.addTab(self.advance_tab, "advance")
        self.control_layout.addWidget(self.tabs)

        # Buttons for reset and save actions
        self.reset_button = QPushButton("Reset Sliders")
        self.reset_button.setStyleSheet("background-color: Gray; font-size: 16px; padding: 10px;")
        self.reset_button.clicked.connect(self.reset_values)
        self.control_layout.addWidget(self.reset_button)

        button_layout = QHBoxLayout()
       
        self.save_button = QPushButton()
        self.save_button.setIcon(QIcon(os.path.join(ASSETS_DIR, "takepic.png")))
        self.save_button.setIconSize(QSize(60, 60))
        self.save_button.setFixedSize(150, 70)
        self.save_button.setStyleSheet("background-color:rgb(206, 204, 204); border-radius: 10px;") 
        self.save_button.clicked.connect(lambda _=False: self.take_picture(high_res=True))
        button_layout.addWidget(self.save_button)


        button_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Minimum))


        self.record_button = QPushButton()
        self.record_button.setIcon(QIcon(os.path.join(ASSETS_DIR, "video.png")))
        self.record_button.setIconSize(QSize(60, 60))
        self.record_button.setFixedSize(150, 70)
        self.record_button.setStyleSheet(self.record_button_default_color)
        self.record_button.clicked.connect(self.toggle_recording)
        button_layout.addWidget(self.record_button)


        self.control_layout.addLayout(button_layout)

        # Add control widget to the splitter
        control_widget.setMinimumWidth(350)
        control_widget.setMaximumWidth(350)
        # Prevent resizing of control panel in splitter
        splitter.setCollapsible(0, False)
        splitter.setStretchFactor(0, 0)
        splitter.setSizes([350, 1000])
        splitter.addWidget(control_widget)

        # Label to display the video feed
        self.video_widget = CameraGLWidget()
        self.video_widget.setStyleSheet("background-color: black;")
        splitter.addWidget(self.video_widget)

        # Ensure video expands fully when panel is hidden
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

        # --- Floating arrow button on the image ---
        self.toggle_panel_button = QPushButton()
        self.toggle_panel_button.setFixedWidth(18)
        self.toggle_panel_button.setFixedHeight(60)
        self.toggle_panel_button.setCheckable(True)
        self.toggle_panel_button.setChecked(False)
        self.toggle_panel_button.setText('◀')
        self.toggle_panel_button.setStyleSheet('''
            QPushButton {
                font-size: 18px;
                background: rgba(255,255,255,80);
                border: 1px solid #bbb;
                border-radius: 5px;
                color: #0c838c;
                padding: 0;
                margin: 0;
            }
            QPushButton:hover {
                background: rgba(33,150,243,0.18);
                color: #0d47a1;
                border: 1.5px solid #0c838c;
            }
        ''')
        self.toggle_panel_button.clicked.connect(self.toggle_control_panel)

        # A layout to place the button on the image
        self.video_label_layout = QVBoxLayout(self.video_widget)
        self.video_label_layout.setContentsMargins(0, 0, 0, 0)
        self.video_label_layout.addWidget(self.toggle_panel_button, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        self.control_widget = control_widget
        self.splitter = splitter

        # Initialize Windows webcam with selected camera
        selected_camera = self.camera_settings.get("selected_camera", 0)
        self.cap = cv2.VideoCapture(selected_camera, cv2.CAP_DSHOW)  # Use DirectShow backend for lower latency
        if not self.cap.isOpened():
            # Try other camera indices if selected camera fails
            for i in range(0, 5):
                if i != selected_camera:  # Skip the already tried camera
                    self.cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                    if self.cap.isOpened():
                        # Update settings to the working camera
                        self.camera_settings["selected_camera"] = i
                        self.save_camera_settings()
                        break
            if not self.cap.isOpened():
                QMessageBox.critical(self, "Camera Error", "No webcam found. Please connect a webcam and restart the application.")
                return
        
        # Fix color issues by setting camera properties
        try:
            # Set auto white balance to ON to fix blue tint
            self.cap.set(cv2.CAP_PROP_AUTO_WB, 1)
            # Set brightness to normal
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 128)
            # Set contrast to normal
            self.cap.set(cv2.CAP_PROP_CONTRAST, 128)
            # Set fixed optimal exposure
            self.set_fixed_exposure()
            print("Camera color settings applied successfully")
        except Exception as e:
            print(f"Could not set camera properties: {e}")
        
        # Set webcam properties for better performance
        try:
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        except Exception:
            pass
        # Prefer 1280x720@30; adjust if camera can't keep up
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for lower latency
        
        # Default zoom factor (1x)
        self.zoom_factor = 1  

        # Timer to periodically capture frames - optimized for Windows
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        # Set timer to 30 FPS (33ms interval) to match camera and recording FPS
        self.timer.start(33)  # 1000ms / 30fps = 33ms interval

        self.is_recording = False
        self.video_writer = None
        # Preallocate a reusable buffer for frame conversions to reduce allocations
        self._tmp_frame_bgr = None

        # Set window size for Windows - not full maximized
        self.resize(1400, 900)
        self.move(100, 100)

        # Debounced settings saver to reduce disk I/O while sliding
        self.settings_save_timer = QTimer(self)
        self.settings_save_timer.setSingleShot(True)
        self.settings_save_timer.setInterval(400)
        self.settings_save_timer.timeout.connect(self.save_settings)

        # Load previously saved settings if they exist
        self.settings_file = resource_path('settings.json')
        self.load_settings()



        self.fullscreen_window = None

        # Add a spacer to push the following widgets to the bottom.
        self.control_layout.addStretch(1)

        # Add version label.
        self.version_label = QLabel(f"Version {APP_VERSION}")
        self.version_label.setStyleSheet("font-size: 20px; color: #888; border: none; padding-bottom: 5px; font-weight: bold;")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.control_layout.addWidget(self.version_label)

        # --- Apply iPhone-style switch to filter checkboxes ---
        switch_style = '''
        QCheckBox::indicator {
            width: 40px;
            height: 22px;
            border-radius: 11px;
            background: #ccc;
            border: 1px solid #aaa;
            position: relative;
        }
        QCheckBox::indicator:checked {
            background: #E89B4C;
            border: 1px solid #E89B4C;
        }
        QCheckBox::indicator:unchecked {
            background: #ccc;
            border: 1px solid #aaa;
        }
        QCheckBox::indicator {
            margin: 0 6px 0 0;
        }
        QCheckBox::indicator:checked {
            box-shadow: 0 0 2px #E89B4C;
        }
        QCheckBox::indicator:before {
            content: '';
            position: absolute;
            left: 2px;
            top: 2px;
            width: 18px;
            height: 18px;
            border-radius: 9px;
            background: white;
            transition: left 0.2s;
        }
        QCheckBox::indicator:checked:before {
            left: 20px;
        }
        '''
        self.filter_switch.setStyleSheet(switch_style)
        self.filter_switch_advance.setStyleSheet(switch_style)
        self.hue_switch.setStyleSheet(switch_style)

        # Camera settings load/save
        self.mode = self.camera_settings.get("mode", "General")
        self.rotation_angle = self.camera_settings.get("rotation_angle", 0)
        self.apply_camera_settings()
        self.update_mode_ui()  # Set UI based on mode
        
        # Update mode menu to reflect current mode
        if hasattr(self, 'mode_actions'):
            for action in self.mode_actions:
                action.setChecked(action.text() == self.mode)

        # After creating each slider, connect its valueChanged to self.update_frame
        # Keep live preview smooth; apply on change without forcing immediate re-render
        self.gain_slider.valueChanged.connect(self.update_frame)
        self.black_level_slider.valueChanged.connect(self.update_frame)
        self.gamma_slider.valueChanged.connect(self.update_frame)
        self.saturation_slider.valueChanged.connect(self.update_frame)
        self.sharpness_slider.valueChanged.connect(self.update_frame)
        # Redraw only on release/toggle to reduce refresh storms
        self.red_slider.sliderReleased.connect(self.update_frame)
        self.green_slider.sliderReleased.connect(self.update_frame)
        self.blue_slider.sliderReleased.connect(self.update_frame)
        self.hue_slider.sliderReleased.connect(self.update_frame)
        self.filter_switch.toggled.connect(self.update_frame)
        self.filter_switch_advance.toggled.connect(self.update_frame)
        self.hue_switch.toggled.connect(self.update_frame)

        # Ensure Info fields are saved on app close
        QApplication.instance().aboutToQuit.connect(self.save_info_fields)

    def add_slider_with_label_tab(self, layout, label_text, min_value, max_value, initial_value, TickInterval):
        slider_layout = QHBoxLayout()
        slider_layout.setContentsMargins(2, 0, 2, 0)

        # Text Label
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 14px; color: #333; margin-left: 1px;")
        slider_layout.addWidget(label, alignment=Qt.AlignLeft)

        # Small space between label and slider
        slider_layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Minimum))

        # Slider
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(initial_value)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(TickInterval)
        slider.setFixedWidth(90)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #ddd;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0c838c;
                border: 2px solid #0c838c;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #0c838c;
                border-radius: 4px;
            }
            QSlider::add-page:horizontal {
                background: #ddd;
                border-radius: 4px;
            }
        """)
        slider_layout.addWidget(slider, alignment=Qt.AlignRight)

        # Very small space between slider and value box
        slider_layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Minimum))

        # Value Input
        value_input = QLineEdit()
        value_input.setText(str(initial_value))
        value_input.setFixedWidth(55)
        value_input.setStyleSheet("font-size: 14px; color: #333; margin-left: 0px;")
        slider_layout.addWidget(value_input, alignment=Qt.AlignRight)

        slider.valueChanged.connect(lambda value: self.update_value(value, value_input))
        value_input.returnPressed.connect(lambda: self.set_slider_value(value_input, slider, min_value, max_value))
        layout.addLayout(slider_layout)
        slider_layout.setContentsMargins(0, 5, 0, 5)
        # Debounce settings save to avoid heavy I/O while dragging
        slider.valueChanged.connect(lambda _: self.settings_save_timer.start())
        return slider

    def update_value(self, value, value_input, *args):
        # Update the value input field when slider value changes
        value_input.setText(str(value))

    def set_slider_value(self, value_input, slider, min_value, max_value, *args):
        # Set the slider value based on the input field
        try:
            value = int(value_input.text())
            if min_value <= value <= max_value:
                slider.setValue(value)
            else:
                value_input.setText(str(slider.value()))
        except ValueError:
            value_input.setText(str(slider.value()))

    def reset_values(self, *args):
        # Reset all sliders to default values
        self.gain_slider.setValue(100)
        self.black_level_slider.setValue(0)
        self.gamma_slider.setValue(100)
        self.saturation_slider.setValue(50)
        self.red_slider.setValue(255)
        self.blue_slider.setValue(255)
        self.sharpness_slider.setValue(1)
        self.hue_slider.setValue(100)
        
        # Turn off ALL filter switches to ensure natural colors
        self.hue_switch.setChecked(False)
        self.filter_switch.setChecked(False)
        self.filter_switch_advance.setChecked(False)
        
        # Force update to apply changes immediately
        self.update_frame()
    


    def change_video_quality(self, *args):
        quality = self.quality_combo.currentText()
        self.set_video_quality(quality)

    def set_video_quality(self, quality, *args):
        # Set webcam resolution based on selected quality
        if quality == "1456x1088":
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1456)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1088)
        else:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
    def change_zoom_level(self, *args):
        zoom = self.zoom_combo.currentText()
        if zoom == "1x":
            self.zoom_factor = 1
        elif zoom == "2x":
            self.zoom_factor = 2
        elif zoom == "4x":
            self.zoom_factor = 4

    def show_format_dialog(self, info_fields_filled):
        # Step 1: Ask for Photo or Report
        type_dialog = QDialog(self)
        type_dialog.setWindowTitle("Select Output Type")
        layout = QVBoxLayout(type_dialog)
        label = QLabel("Select output type:")
        layout.addWidget(label)
        btn_layout = QHBoxLayout()
        photo_btn = QPushButton("Photo")
        report_btn = QPushButton("Report")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(photo_btn)
        btn_layout.addWidget(report_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        output_type = {"value": None}
        def set_output_type(t):
            output_type["value"] = t
            type_dialog.accept()
        photo_btn.clicked.connect(lambda: set_output_type("Photo"))
        report_btn.clicked.connect(lambda: set_output_type("Report"))
        cancel_btn.clicked.connect(type_dialog.reject)
        if not type_dialog.exec_():
            return None, None, None

        # Step 2: Show options based on selection
        if output_type["value"] == "Photo":
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Photo Format")
            layout = QVBoxLayout(dialog)
            label = QLabel("Select image format to save:")
            layout.addWidget(label)
            btn_layout = QHBoxLayout()
            png_btn = QPushButton("PNG")
            tiff_btn = QPushButton("TIFF")
            dicom_btn = QPushButton("DICOM")
            cancel_btn = QPushButton("Cancel")
            btn_layout.addWidget(png_btn)
            btn_layout.addWidget(tiff_btn)
            btn_layout.addWidget(dicom_btn)
            btn_layout.addWidget(cancel_btn)
            layout.addLayout(btn_layout)
            selected = {"format": None, "action": None}
            def choose(fmt):
                if fmt == "DICOM" and not info_fields_filled:
                    QMessageBox.warning(self, "Missing Information", "Please fill at least one field in the Info tab to enable DICOM format.")
                    return
                selected["format"] = fmt
                selected["action"] = "save"
                dialog.accept()
            png_btn.clicked.connect(lambda: choose("PNG"))
            tiff_btn.clicked.connect(lambda: choose("TIFF"))
            dicom_btn.clicked.connect(lambda: choose("DICOM"))
            cancel_btn.clicked.connect(dialog.reject)
            if not dialog.exec_():
                return None, None, None
            return selected["format"], selected["action"], None
        elif output_type["value"] == "Report":
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Report Action")
            layout = QVBoxLayout(dialog)
            label = QLabel("What would you like to do with the report?")
            layout.addWidget(label)
            btn_layout = QHBoxLayout()
            pdf_btn = QPushButton("PDF")
            print_btn = QPushButton("Print")
            cancel_btn = QPushButton("Cancel")
            btn_layout.addWidget(pdf_btn)
            btn_layout.addWidget(print_btn)
            btn_layout.addWidget(cancel_btn)
            layout.addLayout(btn_layout)
            selected = {"format": None, "action": None}
            def choose(fmt, action):
                if (fmt == "PDF" or action == "print") and not info_fields_filled:
                    QMessageBox.warning(self, "Missing Information", "Please fill at least one field in the Info tab to enable PDF or Print report.")
                    return
                selected["format"] = fmt
                selected["action"] = action
                dialog.accept()
            pdf_btn.clicked.connect(lambda: choose("PDF", "save"))
            print_btn.clicked.connect(lambda: choose("PDF", "print"))
            cancel_btn.clicked.connect(dialog.reject)
            if not dialog.exec_():
                return None, None, None
            return selected["format"], selected["action"], None
        else:
            return None, None, None

    def take_picture(self, high_res: bool = False) -> None:
        """
        Save the image to the IMATT folder on desktop or print it.
        - high_res=False -> Saves the same frame you see on the display (fast, same color).
        - high_res=True  -> Captures a new 1456x1088 frame from the sensor, then applies the same filters.
        """
        # Debug: Test simple capture first
        print("=== DEBUG: Testing simple capture ===")
        ret, test_frame = self.cap.read()
        if ret:
            print(f"Test frame from camera - First pixel BGR: {test_frame[0, 0]}")
            test_rgb = cv2.cvtColor(test_frame, cv2.COLOR_BGR2RGB)
            print(f"Test frame converted to RGB - First pixel RGB: {test_rgb[0, 0]}")
            
            # Save test image directly (BGR is correct for cv2.imwrite)
            test_path = "test_direct_bgr.png"
            cv2.imwrite(test_path, test_frame)
            print(f"Saved test image as BGR: {test_path}")
            
            # Save RGB using PIL (correct way)
            test_path_rgb = "test_direct_rgb.png"
            from PIL import Image
            pil_img = Image.fromarray(test_rgb)
            pil_img.save(test_path_rgb)
            print(f"Saved test image as RGB using PIL: {test_path_rgb}")
        print("=== END DEBUG ===")
        # Get IMATT folder on desktop
        imatt_folder = get_imatt_folder()

        # Check if at least one field is filled (new logic)
        if self.mode == "IVF":
            info_fields_filled = any([
                self.patient_name_input.text().strip() if hasattr(self, 'patient_name_input') else '',
                self.patient_ref_input.text().strip() if hasattr(self, 'patient_ref_input') else '',
                self.cycle_input.text().strip() if hasattr(self, 'cycle_input') else '',
                self.oocyte_embryo_input.text().strip() if hasattr(self, 'oocyte_embryo_input') else '',
                self.comments_input.toPlainText().strip() if hasattr(self, 'comments_input') else ''
            ])
        else:
            info_fields_filled = any([
                self.name_input.text().strip() if hasattr(self, 'name_input') else '',
                self.id_input.text().strip() if hasattr(self, 'id_input') else '',
                self.case_number_input.text().strip() if hasattr(self, 'case_number_input') else '',
                self.institution_input.text().strip() if hasattr(self, 'institution_input') else '',
                self.doctor_input.text().strip() if hasattr(self, 'doctor_input') else '',
                self.date_input.text().strip() if hasattr(self, 'date_input') else '',
                self.sex_input.currentText() != "Undefined" if hasattr(self, 'sex_input') else False,
                self.age_input.text().strip() if hasattr(self, 'age_input') else '',
                self.procedure_input.text().strip() if hasattr(self, 'procedure_input') else '',
                self.description_input.toPlainText().strip() if hasattr(self, 'description_input') else ''
            ])

        selected_format, action, _ = self.show_format_dialog(info_fields_filled)

        if not selected_format or not action:
            return

        if self.mode == "General" and selected_format == "DICOM" and not info_fields_filled:
            QMessageBox.warning(self, "Missing Information", "Please fill at least one Info field to enable DICOM format")
            return

        waiting_dialog = QMessageBox(self)
        waiting_dialog.setWindowTitle("Processing")
        processing_text = "Printing document..." if action == "print" else "Saving file..."
        waiting_dialog.setText(f"Please wait... {processing_text}")
        waiting_dialog.setStandardButtons(QMessageBox.NoButton)
        waiting_dialog.show()
        QApplication.processEvents()

        if high_res:
            # For high res, capture at maximum available resolution
            self.set_video_quality('1456x1088')
            ret, img_to_process = self.cap.read()
            if not ret:
                img_to_process = self.frame.copy()
            else:
                # Convert BGR to RGB immediately after capture (same as in update_frame)
                img_to_process = cv2.cvtColor(img_to_process, cv2.COLOR_BGR2RGB)
            self.set_video_quality('1280x720')
            
            # Apply filters to high-res image if any are active
            if (
                (hasattr(self, 'filter_switch') and self.filter_switch.isChecked()) or
                (hasattr(self, 'filter_switch_advance') and self.filter_switch_advance.isChecked()) or
                (hasattr(self, 'hue_switch') and self.hue_switch.isChecked())
            ):
                img_to_process = self.apply_filters(img_to_process)
        else:
            # For normal resolution, use the exact frame that's currently displayed
            # This ensures the saved image matches what the user sees EXACTLY
            # No need to apply filters again since self.frame already has them applied
            if hasattr(self, 'frame') and self.frame is not None:
                img_to_process = self.frame.copy()
                print(f"Using displayed frame for saving - Size: {img_to_process.shape}")
            else:
                # Fallback: capture new frame and apply filters
                ret, img_to_process = self.cap.read()
                if ret:
                    img_to_process = cv2.cvtColor(img_to_process, cv2.COLOR_BGR2RGB)
                    if (
                        (hasattr(self, 'filter_switch') and self.filter_switch.isChecked()) or
                        (hasattr(self, 'filter_switch_advance') and self.filter_switch_advance.isChecked()) or
                        (hasattr(self, 'hue_switch') and self.hue_switch.isChecked())
                    ):
                        img_to_process = self.apply_filters(img_to_process)
                else:
                    QMessageBox.warning(self, "Error", "Could not capture frame for saving")
                    return
        
        if self.rotation_angle != 0:
            if self.rotation_angle == 90:
                img_to_process = cv2.rotate(img_to_process, cv2.ROTATE_90_CLOCKWISE)
            elif self.rotation_angle == 180:
                img_to_process = cv2.rotate(img_to_process, cv2.ROTATE_180)
            elif self.rotation_angle == 270:
                img_to_process = cv2.rotate(img_to_process, cv2.ROTATE_90_COUNTERCLOCKWISE)
        
        show_bar = self.camera_settings.get('show_scale_bar', True)
        if action == "print":
            reply = QMessageBox.question(self, 'Confirm Print', 'Are you sure you want to print this report?', QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                # Convert RGB to BGR for printing
                img_to_print_bgr = cv2.cvtColor(img_to_process, cv2.COLOR_RGB2BGR)
                if show_bar:
                    img_to_print_bgr = self.draw_scale_bar(img_to_print_bgr, photo_resolution_for_calc=img_to_process.shape[1::-1])
                self.print_document(img_to_print_bgr)
            waiting_dialog.accept()
            return

        if action == "save":
            file_path = ""
            if self.mode == "IVF":
                from PyQt5.QtWidgets import QInputDialog
                if selected_format == "PDF":
                    ext = ".pdf"
                elif selected_format == "DICOM":
                    ext = ".dcm"
                elif selected_format == "TIFF":
                    ext = ".tiff"
                else:
                    ext = ".png"
                while True:
                    fname, ok = QInputDialog.getText(self, "File Name", f"Enter file name (without extension):")
                    if not ok:
                        waiting_dialog.accept()
                        return
                    fname = fname.strip()
                    if fname:
                        file_path = os.path.join(imatt_folder, fname + ext)
                        break
            else:
                current_time = datetime.now().strftime("%m-%d-%y-%H-%M-%S")
                if selected_format == "PNG":
                    file_name = f"image_{current_time}.png"
                elif selected_format == "TIFF":
                    file_name = f"image_{current_time}.tiff"
                elif selected_format == "PDF":
                    file_name = f"image_{current_time}.pdf"
                else:
                    file_name = f"image_{current_time}.dcm"
                file_path = os.path.join(imatt_folder, file_name)

            # img_to_process is already in RGB format from display
            # Keep it in RGB format for proper colors
            img_to_save = img_to_process.copy()

            if selected_format == "PDF":
                if show_bar:
                    # Convert RGB to BGR for draw_scale_bar, then back to RGB
                    img_bgr_temp = cv2.cvtColor(img_to_save, cv2.COLOR_RGB2BGR)
                    img_bgr_temp = self.draw_scale_bar(img_bgr_temp, photo_resolution_for_calc=img_to_process.shape[1::-1])
                    img_to_save = cv2.cvtColor(img_bgr_temp, cv2.COLOR_BGR2RGB)
                self.save_as_pdf(img_to_save, file_path)
            elif selected_format == "TIFF":
                if show_bar:
                    # Convert RGB to BGR for draw_scale_bar, then back to RGB
                    img_bgr_temp = cv2.cvtColor(img_to_save, cv2.COLOR_RGB2BGR)
                    img_bgr_temp = self.draw_scale_bar(img_bgr_temp, photo_resolution_for_calc=img_to_process.shape[1::-1])
                    img_with_bar = cv2.cvtColor(img_bgr_temp, cv2.COLOR_BGR2RGB)
                else:
                    img_with_bar = img_to_save
                self.save_as_tiff(img_with_bar, file_path)
            elif selected_format == "PNG":
                if show_bar:
                    # Convert RGB to BGR for draw_scale_bar, then back to RGB
                    img_bgr_temp = cv2.cvtColor(img_to_save, cv2.COLOR_RGB2BGR)
                    img_bgr_temp = self.draw_scale_bar(img_bgr_temp, photo_resolution_for_calc=img_to_process.shape[1::-1])
                    img_with_bar = cv2.cvtColor(img_bgr_temp, cv2.COLOR_BGR2RGB)
                else:
                    img_with_bar = img_to_save
                # Use PIL to save RGB image properly
                from PIL import Image
                pil_img = Image.fromarray(img_with_bar)
                pil_img.save(file_path)
                print(f"Saved RGB image using PIL: {file_path}")
            elif selected_format == "DICOM":
                if show_bar:
                    # Convert RGB to BGR for draw_scale_bar, then back to RGB
                    img_bgr_temp = cv2.cvtColor(img_to_save, cv2.COLOR_RGB2BGR)
                    img_bgr_temp = self.draw_scale_bar(img_bgr_temp, photo_resolution_for_calc=img_to_process.shape[1::-1])
                    img_with_bar = cv2.cvtColor(img_bgr_temp, cv2.COLOR_BGR2RGB)
                else:
                    img_with_bar = img_to_save
                self.save_as_dicom(img_with_bar, file_path)
            
            waiting_dialog.accept()
            base_name = os.path.basename(file_path)
            folder_path = os.path.dirname(file_path)
            
            # Show additional info about the saved image
            if not high_res:
                QMessageBox.information(self, "Save Successful", 
                                      f"File saved successfully!\n\n"
                                      f"File name: {base_name}\n"
                                      f"Location: {folder_path}\n\n"
                                      f"✅ This image is EXACTLY what you see on screen!")
            else:
                QMessageBox.information(self, "Save Successful", 
                                      f"File saved successfully!\n\n"
                                      f"File name: {base_name}\n"
                                      f"Location: {folder_path}\n\n"
                                      f"📸 High-resolution image captured from camera")

    def handle_menu_print(self, *args):
        """
        Handles the Print action from the File menu.
        """
        # Check if at least one field is filled (new logic)
        if self.mode == "IVF":
            info_fields_filled = any([
                self.patient_name_input.text().strip() if hasattr(self, 'patient_name_input') else '',
                self.patient_ref_input.text().strip() if hasattr(self, 'patient_ref_input') else '',
                self.cycle_input.text().strip() if hasattr(self, 'cycle_input') else '',
                self.oocyte_embryo_input.text().strip() if hasattr(self, 'oocyte_embryo_input') else '',
                self.comments_input.toPlainText().strip() if hasattr(self, 'comments_input') else ''
            ])
        else:
            info_fields_filled = any([
                self.name_input.text().strip() if hasattr(self, 'name_input') else '',
                self.id_input.text().strip() if hasattr(self, 'id_input') else '',
                self.case_number_input.text().strip() if hasattr(self, 'case_number_input') else '',
                self.institution_input.text().strip() if hasattr(self, 'institution_input') else '',
                self.doctor_input.text().strip() if hasattr(self, 'doctor_input') else '',
                self.date_input.text().strip() if hasattr(self, 'date_input') else '',
                self.sex_input.currentText() != "Undefined" if hasattr(self, 'sex_input') else False,
                self.age_input.text().strip() if hasattr(self, 'age_input') else '',
                self.procedure_input.text().strip() if hasattr(self, 'procedure_input') else '',
                self.description_input.toPlainText().strip() if hasattr(self, 'description_input') else ''
            ])
        if not info_fields_filled:
            QMessageBox.warning(self, "Missing Information", "Please fill at least one field in the Info tab to print a report.")
            return

        reply = QMessageBox.question(self, 'Confirm Print', 'Are you sure you want to print this report?', QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        waiting_dialog = QMessageBox(self)
        waiting_dialog.setWindowTitle("Processing")
        waiting_dialog.setText("Please wait... Printing document...")
        waiting_dialog.setStandardButtons(QMessageBox.NoButton)
        waiting_dialog.show()
        QApplication.processEvents()

        try:
            self.set_video_quality('1456x1088')
            ret, img_to_process = self.cap.read()
            if not ret:
                img_to_process = self.frame.copy()
            else:
                # Convert BGR to RGB immediately after capture (same as in update_frame)
                img_to_process = cv2.cvtColor(img_to_process, cv2.COLOR_BGR2RGB)
            self.set_video_quality('1280x720')

            if ((hasattr(self, 'filter_switch') and self.filter_switch.isChecked()) or
                (hasattr(self, 'filter_switch_advance') and self.filter_switch_advance.isChecked()) or
                (hasattr(self, 'hue_switch') and self.hue_switch.isChecked())):
                img_to_process = self.apply_filters(img_to_process)
            
            if self.rotation_angle != 0:
                if self.rotation_angle == 90:
                    img_to_process = cv2.rotate(img_to_process, cv2.ROTATE_90_CLOCKWISE)
                elif self.rotation_angle == 180:
                    img_to_process = cv2.rotate(img_to_process, cv2.ROTATE_180)
                elif self.rotation_angle == 270:
                    img_to_process = cv2.rotate(img_to_process, cv2.ROTATE_90_COUNTERCLOCKWISE)

            # Convert RGB to BGR for printing
            img_to_print_bgr = cv2.cvtColor(img_to_process, cv2.COLOR_RGB2BGR)
            show_bar = self.camera_settings.get('show_scale_bar', True)
            if show_bar:
                img_to_print_bgr = self.draw_scale_bar(img_to_print_bgr, photo_resolution_for_calc=img_to_process.shape[1::-1])
                
            self.print_document(img_to_print_bgr)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred during printing: {e}")
        
        finally:
            waiting_dialog.accept()

    def print_document(self, image_to_print_bgr):
        """
        Generates a temporary PDF and sends it to the printer.
        The image is passed as an argument.
        """
        temp_pdf_path = None
        try:
            # --- Resize image for better printer compatibility ---
            PRINT_WIDTH_PX = 2000
            original_h, original_w = image_to_print_bgr.shape[:2]
            aspect_ratio = original_h / original_w
            new_h = int(PRINT_WIDTH_PX * aspect_ratio)
            img_resized_for_print = cv2.resize(image_to_print_bgr, (PRINT_WIDTH_PX, new_h), interpolation=cv2.INTER_AREA)

            # Create and print temporary PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
                temp_pdf_path = tmp_pdf.name
            
            self.save_as_pdf(img_resized_for_print, temp_pdf_path)

            if not shutil.which("lp"):
                 QMessageBox.critical(self, "Print Error", "Printing command 'lp' not found. Is CUPS installed and configured?")
                 return

            # Specify printer and PDF format explicitly
            printer_name = "HP-LaserJet-Professional-P-1102w"
            cmd = [
                "lp",
                "-d", printer_name,
                "-o", "document-format=application/pdf",
                "-o", "media=A4",            # or media=iso_a4_210x297mm
                temp_pdf_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

            # Display error or success
            if result.returncode != 0:
                QMessageBox.critical(
                    self,
                    "Print Error",
                    f"Failed to send document to printer:\n{result.stderr or 'Unknown error'}"
                )
            else:
                QMessageBox.information(
                    self,
                    "Print Successful",
                    "The document was sent to the printer successfully."
                )
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred during printing: {e}")
        
        finally:
            if temp_pdf_path and os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

    def save_as_pdf(self, img, file_path):
        """
        Save image and Info as PDF using reportlab
        """
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        import tempfile
        import cv2

        if self.mode == "IVF":
            # IVF mode fields
            patient_name = self.patient_name_input.text() if hasattr(self, 'patient_name_input') else ''
            patient_ref = self.patient_ref_input.text() if hasattr(self, 'patient_ref_input') else ''
            cycle = self.cycle_input.text() if hasattr(self, 'cycle_input') else ''
            oocyte_embryo = self.oocyte_embryo_input.text() if hasattr(self, 'oocyte_embryo_input') else ''
            comments = self.comments_input.toPlainText() if hasattr(self, 'comments_input') else ''
        else:
            # General mode fields
            institution = self.institution_input.text() if hasattr(self, 'institution_input') else ''
            case_number = self.case_number_input.text() if hasattr(self, 'case_number_input') else ''
            name = self.name_input.text() if hasattr(self, 'name_input') else ''
            patient_id = self.id_input.text() if hasattr(self, 'id_input') else ''
            doctor = self.doctor_input.text() if hasattr(self, 'doctor_input') else ''
            date = self.date_input.text() if hasattr(self, 'date_input') else ''
            sex = self.sex_input.currentText() if hasattr(self, 'sex_input') else ''
            age = self.age_input.text() if hasattr(self, 'age_input') else ''
            procedure = self.procedure_input.text() if hasattr(self, 'procedure_input') else ''
            description = self.description_input.toPlainText() if hasattr(self, 'description_input') else ''

        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4
        margin = 40
        y = height - margin

        if self.mode == "IVF":
            # IVF mode PDF layout
            # Header: IVF Report
            header_box_height = 54
            c.setLineWidth(1)
            c.roundRect(margin, y - header_box_height, width - 2*margin, header_box_height, 14, stroke=1, fill=0)
            c.setFont("Helvetica", 18)
            c.drawCentredString(width / 2, y - header_box_height / 2 + 2, "IVF Report")
            y -= (header_box_height + 28)

            # IVF Info in two columns
            c.setFont("Helvetica", 13)
            col1_x = margin
            col2_x = width / 2 + 10
            col_y = y
            line_gap = 18
            # Left column
            left_lines = [
                f"Patient Name: {patient_name}",
                f"Patient Ref: {patient_ref}",
                f"Cycle: {cycle}"
            ]
            for line in left_lines:
                c.drawString(col1_x, col_y, line)
                col_y -= line_gap
            # Right column
            col_y2 = y
            right_lines = [
                f"Oocyte / Embryo: {oocyte_embryo}"
            ]
            for line in right_lines:
                if line:
                    c.drawString(col2_x, col_y2, line)
                    col_y2 -= line_gap
            # Find lower y for next section
            y = min(col_y, col_y2) - 10

            # Comments below both columns, full width
            if comments:
                c.setFont("Helvetica", 13)
                desc_label_y = y
                c.drawString(margin, desc_label_y, "Comments:")
                from reportlab.platypus import Paragraph
                from reportlab.lib.styles import getSampleStyleSheet
                styles = getSampleStyleSheet()
                styleN = styles["Normal"]
                styleN.fontName = "Helvetica"
                styleN.fontSize = 12
                styleN.leading = 15
                desc_para = Paragraph(comments.replace("\n", "<br/>"), styleN)
                w, h = desc_para.wrap(width - 2*margin, 300)
                desc_para.drawOn(c, margin, desc_label_y - h - 4)
                y = desc_label_y - h - 18
            else:
                y -= 16
        else:
            # General mode PDF layout
            # Header: Institution Name in a larger rounded box, centered vertically
            header_box_height = 54
            c.setLineWidth(1)
            c.roundRect(margin, y - header_box_height, width - 2*margin, header_box_height, 14, stroke=1, fill=0)
            c.setFont("Helvetica", 18)
            c.drawCentredString(width / 2, y - header_box_height / 2 + 2, institution)
            y -= (header_box_height + 28)

            # Patient Info in two columns
            c.setFont("Helvetica", 13)
            col1_x = margin
            col2_x = width / 2 + 10
            col_y = y
            line_gap = 18
            # Left column
            left_lines = [
                f"Case Number: {case_number}",
                f"Name: {name}",
                f"ID: {patient_id}",
                f"Sex: {sex}"
            ]
            for line in left_lines:
                c.drawString(col1_x, col_y, line)
                col_y -= line_gap
            # Right column
            col_y2 = y
            right_lines = [
                f"Age: {age}",
                f"Date: {date}",
                f"Procedure: {procedure}" if procedure else ""
            ]
            for line in right_lines:
                if line:
                    c.drawString(col2_x, col_y2, line)
                    col_y2 -= line_gap
            # Find lower y for next section
            y = min(col_y, col_y2) - 10

            # Description below both columns, full width
            if description:
                c.setFont("Helvetica", 13)
                desc_label_y = y
                c.drawString(margin, desc_label_y, "Description:")
                from reportlab.platypus import Paragraph
                from reportlab.lib.styles import getSampleStyleSheet
                styles = getSampleStyleSheet()
                styleN = styles["Normal"]
                styleN.fontName = "Helvetica"
                styleN.fontSize = 12
                styleN.leading = 15
                desc_para = Paragraph(description.replace("\n", "<br/>"), styleN)
                w, h = desc_para.wrap(width - 2*margin, 300)
                desc_para.drawOn(c, margin, desc_label_y - h - 4)
                y = desc_label_y - h - 18
            else:
                y -= 16

        # Image (centered, with large vertical margins)
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_img:
            # Use PIL to save RGB image properly
            from PIL import Image
            pil_img = Image.fromarray(img)
            pil_img.save(tmp_img.name, 'JPEG')
            tmp_img_path = tmp_img.name
        img_max_width = width - 2*margin
        img_max_height = 260
        img_reader = ImageReader(tmp_img_path)
        iw, ih = img_reader.getSize()
        aspect = ih / iw
        img_width = img_max_width
        img_height = img_width * aspect
        if img_height > img_max_height:
            img_height = img_max_height
            img_width = img_height / aspect
        img_x = (width - img_width) / 2
        img_y = y - img_height
        c.drawImage(tmp_img_path, img_x, img_y, width=img_width, height=img_height)
        import os
        os.remove(tmp_img_path)
        y = img_y - 40  # large space below image

        # Doctor Name and Signature (centered, with large spacing, no line)
        if self.mode != "IVF":
            c.setFont("Helvetica", 13)
            c.drawCentredString(width / 2, y, f"Doctor: {doctor}")
            y -= 36
            c.setFont("Helvetica", 11)
            c.drawCentredString(width / 2, y, "Signature:")
            y -= 30

        # Footer (centered, small font)
        c.setFont("Helvetica-Oblique", 9)
        footer_text = "This report was generated by IMATT Imaging Software. For more information, visit www.imattco.com."
        c.drawCentredString(width / 2, 30, footer_text)

        c.showPage()
        c.save()

    def save_as_dicom(self, img, file_path):
        # The input 'img' is already in RGB format from take_picture.
        # DICOM Photometric Interpretation is set to RGB, so no conversion needed.

        # Read info from the Info tab based on mode
        if self.mode == "IVF":
            # IVF mode fields
            patient_name = self.patient_name_input.text() if hasattr(self, 'patient_name_input') else ''
            patient_id = self.patient_ref_input.text() if hasattr(self, 'patient_ref_input') else ''
            case_number = self.cycle_input.text() if hasattr(self, 'cycle_input') else ''
            study_date = datetime.now().strftime('%Y%m%d')  # Use current date for IVF
            modality = "IVF"  # Set modality to IVF
            institution = "IVF Laboratory"  # Default institution for IVF
        else:
            # General mode fields
            patient_name = self.name_input.text() if hasattr(self, 'name_input') else ''
            patient_id = self.id_input.text() if hasattr(self, 'id_input') else ''
            case_number = self.case_number_input.text() if hasattr(self, 'case_number_input') else ''
            study_date = self.date_input.text() if hasattr(self, 'date_input') else ''
            modality = self.modality_input.text() if hasattr(self, 'modality_input') else ''
            institution = self.institution_input.text() if hasattr(self, 'institution_input') else ''

        # Create DICOM dataset
        file_meta = pydicom.Dataset()
        file_meta.MediaStorageSOPClassUID = pydicom.uid.generate_uid()
        file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
        file_meta.ImplementationClassUID = pydicom.uid.generate_uid()

        ds = FileDataset(file_path, {}, file_meta=file_meta, preamble=b"\0" * 128)
        ds.PatientName = patient_name
        ds.PatientID = patient_id
        ds.StudyDate = study_date
        ds.Modality = modality
        ds.InstitutionName = institution
        ds.ContentDate = datetime.now().strftime('%Y%m%d')
        ds.ContentTime = datetime.now().strftime('%H%M%S')

        # Convert image to grayscale or RGB based on shape
        if len(img.shape) == 2:
            ds.SamplesPerPixel = 1
            ds.PhotometricInterpretation = "MONOCHROME2"
        else:
            ds.SamplesPerPixel = 3
            ds.PhotometricInterpretation = "RGB"
        ds.Rows, ds.Columns = img.shape[0], img.shape[1]
        ds.BitsAllocated = 8
        ds.BitsStored = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.PixelData = img.tobytes()

        # --- Set Pixel Spacing (scale) ---
        h, w = img.shape[:2]
        # Determine sensor type by resolution
        if (w, h) == (4056, 3040):
            pixel_size_um = 1.55
        elif (w, h) == (1456, 1088):
            pixel_size_um = 3.45
        else:
            pixel_size_um = 1.55
        objective_mag = getattr(self, 'objective_magnification', 40)
        eyepiece_mag = getattr(self, 'eyepiece_magnification', 0.5)
        mag = objective_mag * eyepiece_mag
        pixel_size_mm = (pixel_size_um / mag) / 1000.0  # mm per pixel
        ds.PixelSpacing = [str(pixel_size_mm), str(pixel_size_mm)]

        ds.save_as(file_path)

    def save_as_tiff(self, img, file_path):
        # Save TIFF with XResolution/YResolution tags for scale
        h, w = img.shape[:2]
        # Determine sensor type by resolution
        if (w, h) == (4056, 3040):
            pixel_size_um = 1.55
        elif (w, h) == (1456, 1088):
            pixel_size_um = 3.45
        else:
            pixel_size_um = 1.55
        objective_mag = getattr(self, 'objective_magnification', 40)
        eyepiece_mag = getattr(self, 'eyepiece_magnification', 0.5)
        mag = objective_mag * eyepiece_mag
        pixel_size_mm = (pixel_size_um / mag) / 1000.0  # mm per pixel
        # Calculate DPI (dots per inch) for scale
        dpi = int(25.4 / pixel_size_mm)
        # Image is already in RGB format, no conversion needed
        pil_img = Image.fromarray(img)
        pil_img.save(file_path, format='TIFF', dpi=(dpi, dpi))

    def toggle_recording(self, checked=False, *args):
        # Get IMATT folder on desktop
        imatt_folder = get_imatt_folder()
        current_time = datetime.now().strftime("%m-%d-%y-%H-%M-%S")
        file_name = f"video_{current_time}.mp4" 
        file_path = os.path.join(imatt_folder, file_name)

        if not self.is_recording:
            # Ensure frame is initialized
            if not hasattr(self, 'frame') or self.frame is None:
                QMessageBox.warning(self, "Error", "No video frame available to record.")
                return
            
            print(f"Starting video recording to: {file_path}")
            
            # Get current frame dimensions
            frame_height, frame_width = self.frame.shape[:2]
            
            # Use 30 FPS to match camera FPS for proper timing
            fps = 30
            
            # Try multiple codecs in order of preference
            codecs_to_try = [
                ('H264', cv2.VideoWriter_fourcc(*'H264')),
                ('XVID', cv2.VideoWriter_fourcc(*'XVID')),
                ('MJPG', cv2.VideoWriter_fourcc(*'MJPG')),
                ('mp4v', cv2.VideoWriter_fourcc(*'mp4v'))
            ]
            
            self.video_writer = None
            for codec_name, fourcc in codecs_to_try:
                self.video_writer = cv2.VideoWriter(
                    file_path,
                    fourcc,
                    fps,
                    (frame_width, frame_height)
                )
                if self.video_writer.isOpened():
                    print(f"Using {codec_name} codec for recording")
                    break
                else:
                    self.video_writer.release()
                    self.video_writer = None
            
            if not self.video_writer or not self.video_writer.isOpened():
                QMessageBox.warning(self, "Error", "Could not initialize video recording. No suitable codec found.")
                return
            
            # Initialize recording variables
            self.is_recording = True
            self.recording_start_time = datetime.now()
            self.record_button.setStyleSheet("background-color: Red; border-radius: 10px;")
            print("Video recording started")
            
        else:
            # Stop recording
            self.is_recording = False
            if self.video_writer:
                self.video_writer.release()
            self.video_writer = None
            self.record_button.setStyleSheet(self.record_button_default_color)
            
            # Calculate actual recording duration
            if hasattr(self, 'recording_start_time'):
                duration = datetime.now() - self.recording_start_time
                duration_str = f"{duration.total_seconds():.1f} seconds"
            else:
                duration_str = "Unknown duration"
            
            folder_path = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            QMessageBox.information(self, "Recording Stopped", 
                                  f"Recording saved successfully!\n\n"
                                  f"File name: {base_name}\n"
                                  f"Duration: {duration_str}\n"
                                  f"Location: {folder_path}")
            print(f"Video recording stopped. Duration: {duration_str}")

    def set_fixed_exposure(self):
        """Set optimal fixed exposure for cameras"""
        try:
            # Enable auto exposure for better image quality
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)  # 0.75 means auto exposure mode
        except Exception:
            pass

    def apply_sharpness(self, frame, sharpness_value):
        if sharpness_value == 0:
            return frame

        # Convert to float for precision
        frame_float = frame.astype(np.float32)
        
        # Enhanced sharpening algorithm with multiple techniques
        if sharpness_value > 0:
            # Positive values: sharpen
            # Method 1: Unsharp mask
            kernel_size = max(3, min(21, 3 + abs(sharpness_value) // 10))
            # Ensure kernel size is odd
            if kernel_size % 2 == 0:
                kernel_size += 1
            blurred = cv2.GaussianBlur(frame_float, (kernel_size, kernel_size), 0)
            detail_layer = frame_float - blurred
            
            # Stronger scaling for more visible effect
            scale_factor = (sharpness_value / 100.0) * 3.0  # Triple the effect
            result = frame_float + (detail_layer * scale_factor)
            
            # Method 2: Laplacian sharpening for high values
            if sharpness_value > 50:
                # Convert to grayscale for Laplacian
                gray = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_RGB2GRAY)
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                laplacian = np.uint8(np.absolute(laplacian))
                
                # Apply Laplacian enhancement
                laplacian_factor = (sharpness_value - 50) / 150.0  # 0 to 1 for values 50-200
                for i in range(3):  # Apply to all channels
                    result[:, :, i] = result[:, :, i] + (laplacian * laplacian_factor)
            
        else:
            # Negative values: blur
            kernel_size = max(3, min(21, 3 + abs(sharpness_value) // 10))
            # Ensure kernel size is odd
            if kernel_size % 2 == 0:
                kernel_size += 1
            blurred = cv2.GaussianBlur(frame_float, (kernel_size, kernel_size), 0)
            detail_layer = frame_float - blurred
            
            scale_factor = abs(sharpness_value) / 100.0
            result = frame_float - (detail_layer * scale_factor)
        
        # Clip values to the valid range [0, 255] and convert back to uint8
        result = np.clip(result, 0, 255).astype(np.uint8)
        return result

    def apply_filters(self, frame):
        # If hue switch is on, only apply hue
        if hasattr(self, 'hue_switch') and self.hue_switch.isChecked():
            hue_value = self.hue_slider.value()
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
            hsv_frame[:, :, 0] = hue_value  # Set Hue channel to the selected value
            frame = cv2.cvtColor(hsv_frame, cv2.COLOR_HSV2RGB)

        # If RGB filter switch (advance) is on, only apply RGB
        if hasattr(self, 'filter_switch_advance') and self.filter_switch_advance.isChecked():
            frame[:, :, 0] = frame[:, :, 0] * (self.red_slider.value() / 255)
            frame[:, :, 1] = frame[:, :, 1] * (self.green_slider.value() / 255)
            frame[:, :, 2] = frame[:, :, 2] * (self.blue_slider.value() / 255)

        # If basic filter switch is on, only apply basic filters
        if hasattr(self, 'filter_switch') and self.filter_switch.isChecked():
            # Apply Gain filter (adjust brightness)
            gain = self.gain_slider.value() / 100
            frame = cv2.convertScaleAbs(frame, alpha=gain, beta=0)
            # Apply Black Level filter
            black_level = self.black_level_slider.value()
            frame = np.clip(frame - black_level, 0, 255)
            # Apply Gamma correction
            gamma_value = self.gamma_slider.value() / 100
            gamma_lookup_table = np.array([(i / 255) ** gamma_value * 255 for i in range(256)], dtype=np.uint8)
            frame = cv2.LUT(frame, gamma_lookup_table)
            # Apply Saturation filter
            saturation = self.saturation_slider.value() / 100
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
            hsv_frame[:, :, 1] = hsv_frame[:, :, 1] * saturation  # Saturation channel
            frame = cv2.cvtColor(hsv_frame, cv2.COLOR_HSV2RGB)
            # Apply Sharpness filter
            frame = self.apply_sharpness(frame, self.sharpness_slider.value())
        return frame

    def update_frame(self, *args):
        # Capture frame from webcam
        ret, frame = self.cap.read()
        if not ret:
            # If frame capture fails, return early
            return
        
        # Convert BGR to RGB for processing
        # Use faster color conversion if available
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # If any filter switches are on, apply filters
        if (
            (hasattr(self, 'filter_switch') and self.filter_switch.isChecked()) or
            (hasattr(self, 'filter_switch_advance') and self.filter_switch_advance.isChecked()) or
            (hasattr(self, 'hue_switch') and self.hue_switch.isChecked())
        ):
            # Downscale for processing to reduce CPU, then upscale for view
            original_size = (frame.shape[1], frame.shape[0])
            proc_size = (max(640, original_size[0] // 2), max(360, original_size[1] // 2))
            frame_small = cv2.resize(frame, proc_size, interpolation=cv2.INTER_LINEAR)
            frame_small = self.apply_filters(frame_small)
            frame = cv2.resize(frame_small, original_size, interpolation=cv2.INTER_LINEAR)

        # Rotate image (e.g., 180 degrees)
        if hasattr(self, 'rotation_angle') and self.rotation_angle:
            if self.rotation_angle == 90:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            elif self.rotation_angle == 180:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            elif self.rotation_angle == 270:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Draw scale bar in lower right corner if enabled
        if self.camera_settings.get('show_scale_bar', True):
            # Get photo resolution from settings to calculate the scale correctly for the preview
            photo_res_str = self.camera_settings.get("photo_res", "1456x1088")
            w_str, h_str = photo_res_str.split('x')
            photo_resolution_for_calc = (int(w_str), int(h_str))
            # Convert RGB to BGR for draw_scale_bar, then back to RGB
            frame_bgr_temp = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame_bgr_temp = self.draw_scale_bar(frame_bgr_temp, photo_resolution_for_calc=photo_resolution_for_calc)
            frame = cv2.cvtColor(frame_bgr_temp, cv2.COLOR_BGR2RGB)

        # Convert to BGR for display (reuse buffer when possible)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        height, width, channel = frame_bgr.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame_bgr.data, width, height, bytes_per_line, QImage.Format_BGR888)
        self.video_widget.set_image(q_img)
        self.frame = frame  # Store in RGB format
        # Save frame if recording
        if hasattr(self, 'is_recording') and self.is_recording and hasattr(self, 'video_writer') and self.video_writer is not None:
            # Convert to BGR for saving
            self.video_writer.write(frame_bgr)
        return

    def _get_rounded_scale(self, num):
        if num >= 100:
            return int(round(num / 10.0)) * 10
        if num >= 10:
            return int(round(num))
        if num >= 1:
            return round(num, 1)
        return round(num, 2)

    def draw_scale_bar(self, frame, photo_resolution_for_calc=None):
        """
        Draws a scale bar on the `frame`.
        The physical length of the bar is fixed relative to the frame's width.
        The value of the bar is calculated based on the frame's own resolution for consistent display.
        """
        import cv2
        import numpy as np
        
        # Dimensions of the frame we are drawing on
        h_prev, w_prev = frame.shape[:2]

        # Use the frame's own resolution for calculation to maintain consistent scale bar size
        w_photo, h_photo = w_prev, h_prev

        # Determine sensor pixel size based on the frame's resolution
        if (w_photo, h_photo) == (4056, 3040):
            pixel_size_um_photo = 1.55
        elif (w_photo, h_photo) == (1456, 1088):
            pixel_size_um_photo = 3.45
        else: # Default for other/preview resolutions
            pixel_size_um_photo = 1.55

        # Get magnification
        objective_mag = getattr(self, 'objective_magnification', 40)
        eyepiece_mag = getattr(self, 'eyepiece_magnification', 0.5)
        mag = objective_mag * eyepiece_mag

        # Length of the bar to draw (1/8th of frame width)
        px_len_on_frame = w_prev // 8
        
        # Calculate the real-world length of that bar
        scale_um = px_len_on_frame * (pixel_size_um_photo / mag)
        scale_um_rounded = self._get_rounded_scale(scale_um)

        # Draw the bar on the frame
        bar_height = max(4, h_prev // 120)
        bar_color = (255, 255, 255) # White
        margin = 30
        x1 = w_prev - margin - px_len_on_frame
        x2 = w_prev - margin
        y1 = h_prev - margin
        y2 = y1 - bar_height
        
        frame = frame.copy()
        cv2.rectangle(frame, (x1, y2), (x2, y1), bar_color, -1)
        # Draw black border for contrast
        cv2.rectangle(frame, (x1, y2), (x2, y1), (0, 0, 0), 1)
        # Draw label
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        text = f"{scale_um_rounded} um"
        (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
        tx = x1 + (px_len_on_frame - tw) // 2
        ty = y2 - 8
        # Draw text with a black outline for visibility
        cv2.putText(frame, text, (tx, ty), font, font_scale, (0,0,0), thickness+1, cv2.LINE_AA)
        cv2.putText(frame, text, (tx, ty), font, font_scale, (255,255,255), thickness, cv2.LINE_AA)
        return frame

    def load_settings(self):
        # Load settings from file
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                # Apply saved settings if any
                for slider_name, value in settings.items():
                    slider = getattr(self, slider_name, None)
                    if slider:
                        if isinstance(slider, ToggleSwitch):
                            slider.setChecked(value)  # Set checkbox state
                        else:
                            slider.setValue(value)  # Set slider value

    def save_settings(self, *args):
        # Save current settings to a file
        settings = {
            'gain_slider': self.gain_slider.value(),
            'black_level_slider': self.black_level_slider.value(),
            'gamma_slider': self.gamma_slider.value(),
            'saturation_slider': self.saturation_slider.value(),
            'sharpness_slider': self.sharpness_slider.value(),
            'red_slider': self.red_slider.value(),
            'green_slider': self.green_slider.value(),
            'blue_slider': self.blue_slider.value(),
            'hue_slider': self.hue_slider.value(),
            'hue_switch': self.hue_switch.isChecked(),
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)



    def toggle_control_panel(self, checked=False, *args):
        if self.toggle_panel_button.isChecked():
            self.control_widget.hide()
            self.toggle_panel_button.setText('▶')
            # Expand video to full width
            self.splitter.setSizes([0, 1])
        else:
            self.control_widget.show()
            self.toggle_panel_button.setText('◀')
            # Restore original sizes
            self.splitter.setSizes([350, 1000])

    def check_update(self, checked=False, *args):
        """Open the IMATT website for updates and information"""
        import webbrowser
        try:
            webbrowser.open("http://imattco.ir")
            print("Opening IMATT website: http://imattco.ir")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open website: {e}")
            print(f"Error opening website: {e}")

    def detect_available_cameras(self):
        """Detect all available cameras and return a list of camera info"""
        available_cameras = []
        for i in range(10):  # Check up to 10 camera indices
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                # Try to get camera name if possible
                try:
                    # Some cameras support getting the name
                    camera_name = f"Camera {i}"
                    # Try to get more info about the camera
                    ret, frame = cap.read()
                    if ret:
                        height, width = frame.shape[:2]
                        camera_name = f"Camera {i} ({width}x{height})"
                except:
                    camera_name = f"Camera {i}"
                
                available_cameras.append({
                    'index': i,
                    'name': camera_name,
                    'cap': cap
                })
            else:
                cap.release()
        return available_cameras

    def load_camera_settings(self):
        try:
            with open(self.settings_file_camera, 'r') as f:
                return json.load(f)
        except Exception:
            return {"photo_res": "1456x1088", "video_res": "1456x1088", "preview_res": "1280x720", "fps": 30, "selected_camera": 0}

    def save_camera_settings(self):
        self.camera_settings["rotation_angle"] = self.rotation_angle
        with open(self.settings_file_camera, 'w') as f:
            json.dump(self.camera_settings, f)

    def apply_camera_settings(self):
        # Set preview resolution and FPS
        preview_res = self.camera_settings.get("preview_res", "1280x720")
        fps = self.camera_settings.get("fps", 30)
        self.rotation_angle = self.camera_settings.get("rotation_angle", 0)
        # Set preview config
        self.set_video_quality(preview_res)
        self.timer.setInterval(int(1000 / fps))
        try:
            self.cap.set(cv2.CAP_PROP_FPS, fps)
        except Exception:
            pass

    def set_rotation_angle(self, angle):
        self.rotation_angle = angle
        self.update_frame()

    def set_mode(self, mode):
        """Set the current mode and update UI accordingly"""
        self.mode = mode
        self.camera_settings["mode"] = mode
        self.save_camera_settings()
        self.update_mode_ui()
        
        # Update menu actions
        for action in self.mode_actions:
            action.setChecked(action.text() == mode)
        
        print(f"Mode changed to: {mode}")

    def set_camera(self, camera_index):
        """Switch to the selected camera"""
        # Release current camera
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()
        
        # Initialize new camera
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            QMessageBox.warning(self, "Camera Error", f"Could not open camera {camera_index}")
            return
        
        # Apply camera settings
        try:
            # Set auto white balance to ON to fix blue tint
            self.cap.set(cv2.CAP_PROP_AUTO_WB, 1)
            # Set brightness to normal
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 128)
            # Set contrast to normal
            self.cap.set(cv2.CAP_PROP_CONTRAST, 128)
            # Set fixed optimal exposure
            self.set_fixed_exposure()
            print(f"Camera {camera_index} color settings applied successfully")
        except Exception as e:
            print(f"Could not set camera properties: {e}")
        
        # Set webcam properties for better performance
        try:
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        except Exception:
            pass
        
        # Set resolution and FPS
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for lower latency
        
        # Save selected camera to settings
        self.camera_settings["selected_camera"] = camera_index
        self.save_camera_settings()
        
        # Update menu actions
        for i, camera_info in enumerate(self.available_cameras):
            if camera_info['index'] == camera_index:
                self.camera_actions[i].setChecked(True)
            else:
                self.camera_actions[i].setChecked(False)
        
        print(f"Switched to camera {camera_index}")

    def update_mode_ui(self):
        # Remove all widgets from the current info_tab
        for i in reversed(range(self.info_layout.count())):
            widget = self.info_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        # Add a scroll area for the info fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        self.info_layout.addWidget(scroll)
        def simple_label(text):
            return QLabel(f'<span style="color:black;">{text}</span>')
        
        if self.mode == "IVF":
            # IVF fields only
            self.patient_name_label = simple_label("Patient Name")
            self.patient_name_input = QLineEdit()
            scroll_layout.addWidget(self.patient_name_label)
            scroll_layout.addWidget(self.patient_name_input)
            
            self.patient_ref_label = simple_label("Patient Ref")
            self.patient_ref_input = QLineEdit()
            scroll_layout.addWidget(self.patient_ref_label)
            scroll_layout.addWidget(self.patient_ref_input)
            
            self.cycle_label = simple_label("Cycle")
            self.cycle_input = QLineEdit()
            scroll_layout.addWidget(self.cycle_label)
            scroll_layout.addWidget(self.cycle_input)
            
            self.oocyte_embryo_label = simple_label("Oocyte / Embryo")
            self.oocyte_embryo_input = QLineEdit()
            scroll_layout.addWidget(self.oocyte_embryo_label)
            scroll_layout.addWidget(self.oocyte_embryo_input)
            
            self.comments_label = simple_label("Comments")
            self.comments_input = QTextEdit()
            self.comments_input.setFixedHeight(80)
            scroll_layout.addWidget(self.comments_label)
            scroll_layout.addWidget(self.comments_input)
        else:
            # General mode fields
            self.name_label = simple_label("Name")
            self.name_input = QLineEdit()
            scroll_layout.addWidget(self.name_label)
            scroll_layout.addWidget(self.name_input)
            self.id_label = simple_label("ID")
            self.id_input = QLineEdit()
            scroll_layout.addWidget(self.id_label)
            scroll_layout.addWidget(self.id_input)
            self.case_label = simple_label("Case Number")
            self.case_number_input = QLineEdit()
            scroll_layout.addWidget(self.case_label)
            scroll_layout.addWidget(self.case_number_input)
            self.institution_label = simple_label("Institution Name")
            self.institution_input = QLineEdit()
            scroll_layout.addWidget(self.institution_label)
            scroll_layout.addWidget(self.institution_input)
            self.doctor_label = simple_label("Doctor Name")
            self.doctor_input = QLineEdit()
            scroll_layout.addWidget(self.doctor_label)
            scroll_layout.addWidget(self.doctor_input)
            self.date_label = simple_label("Date")
            self.date_input = QLineEdit()
            scroll_layout.addWidget(self.date_label)
            scroll_layout.addWidget(self.date_input)
            self.sex_label = simple_label("Sex")
            self.sex_input = QComboBox()
            self.sex_input.addItems(["Undefined", "Male", "Female"])
            scroll_layout.addWidget(self.sex_label)
            scroll_layout.addWidget(self.sex_input)
            self.age_label = simple_label("Age")
            self.age_input = QLineEdit()
            scroll_layout.addWidget(self.age_label)
            scroll_layout.addWidget(self.age_input)
            self.procedure_label = simple_label("Procedure")
            self.procedure_input = QLineEdit()
            scroll_layout.addWidget(self.procedure_label)
            scroll_layout.addWidget(self.procedure_input)
            self.description_label = simple_label("Description")
            self.description_input = QTextEdit()
            self.description_input.setFixedHeight(80)
            scroll_layout.addWidget(self.description_label)
            scroll_layout.addWidget(self.description_input)
        
        self.connect_info_field_signals()
        self.load_info_fields()

    def do_power_off(self, *args):
        reply = QMessageBox.question(self, 'Exit Application', 'Are you sure you want to exit the application?', QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.release()
            QApplication.instance().quit()

    def load_info_fields(self):
        try:
            with open(INFO_FIELDS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if self.mode == "IVF":
                # Load IVF fields
                ivf_data = data.get("ivf", {})
                if hasattr(self, 'patient_name_input'):
                    self.patient_name_input.setText(ivf_data.get("patient_name", ""))
                if hasattr(self, 'patient_ref_input'):
                    self.patient_ref_input.setText(ivf_data.get("patient_ref", ""))
                if hasattr(self, 'cycle_input'):
                    self.cycle_input.setText(ivf_data.get("cycle", ""))
                if hasattr(self, 'oocyte_embryo_input'):
                    self.oocyte_embryo_input.setText(ivf_data.get("oocyte_embryo", ""))
                if hasattr(self, 'comments_input'):
                    self.comments_input.setPlainText(ivf_data.get("comments", ""))
            else:
                # Load General fields
                general_data = data.get("general", {})
                if hasattr(self, 'name_input'):
                    self.name_input.setText(general_data.get("name", ""))
                if hasattr(self, 'id_input'):
                    self.id_input.setText(general_data.get("id", ""))
                if hasattr(self, 'case_number_input'):
                    self.case_number_input.setText(general_data.get("case_number", ""))
                if hasattr(self, 'institution_input'):
                    self.institution_input.setText(general_data.get("institution", ""))
                if hasattr(self, 'doctor_input'):
                    self.doctor_input.setText(general_data.get("doctor", ""))
                if hasattr(self, 'date_input'):
                    self.date_input.setText(general_data.get("date", ""))
                if hasattr(self, 'sex_input'):
                    idx = self.sex_input.findText(general_data.get("sex", "Undefined"))
                    self.sex_input.setCurrentIndex(idx if idx >= 0 else 0)
                if hasattr(self, 'age_input'):
                    self.age_input.setText(general_data.get("age", ""))
                if hasattr(self, 'procedure_input'):
                    self.procedure_input.setText(general_data.get("procedure", ""))
                if hasattr(self, 'description_input'):
                    self.description_input.setPlainText(general_data.get("description", ""))
        except Exception as e:
            print(f"Error loading info fields: {e}")

    def save_info_fields(self, *args):
        try:
            # Load existing data first
            try:
                with open(INFO_FIELDS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except:
                data = {"general": {}, "ivf": {}}
            
            if self.mode == "IVF":
                # Save IVF fields
                data["ivf"] = {
                    "patient_name": self.patient_name_input.text() if hasattr(self, 'patient_name_input') else "",
                    "patient_ref": self.patient_ref_input.text() if hasattr(self, 'patient_ref_input') else "",
                    "cycle": self.cycle_input.text() if hasattr(self, 'cycle_input') else "",
                    "oocyte_embryo": self.oocyte_embryo_input.text() if hasattr(self, 'oocyte_embryo_input') else "",
                    "comments": self.comments_input.toPlainText() if hasattr(self, 'comments_input') else ""
                }
            else:
                # Save General fields
                data["general"] = {
                    "name": self.name_input.text() if hasattr(self, 'name_input') else "",
                    "id": self.id_input.text() if hasattr(self, 'id_input') else "",
                    "case_number": self.case_number_input.text() if hasattr(self, 'case_number_input') else "",
                    "institution": self.institution_input.text() if hasattr(self, 'institution_input') else "",
                    "doctor": self.doctor_input.text() if hasattr(self, 'doctor_input') else "",
                    "date": self.date_input.text() if hasattr(self, 'date_input') else "",
                    "sex": self.sex_input.currentText() if hasattr(self, 'sex_input') else "Undefined",
                    "age": self.age_input.text() if hasattr(self, 'age_input') else "",
                    "procedure": self.procedure_input.text() if hasattr(self, 'procedure_input') else "",
                    "description": self.description_input.toPlainText() if hasattr(self, 'description_input') else ""
                }
            
            with open(INFO_FIELDS_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving info fields: {e}")

    def connect_info_field_signals(self):
        if self.mode == "IVF":
            # Connect IVF field signals
            if hasattr(self, 'patient_name_input'):
                self.patient_name_input.textChanged.connect(self.save_info_fields)
            if hasattr(self, 'patient_ref_input'):
                self.patient_ref_input.textChanged.connect(self.save_info_fields)
            if hasattr(self, 'cycle_input'):
                self.cycle_input.textChanged.connect(self.save_info_fields)
            if hasattr(self, 'oocyte_embryo_input'):
                self.oocyte_embryo_input.textChanged.connect(self.save_info_fields)
            if hasattr(self, 'comments_input'):
                self.comments_input.textChanged.connect(self.save_info_fields)
        else:
            # Connect General field signals
            if hasattr(self, 'name_input'):
                self.name_input.textChanged.connect(self.save_info_fields)
            if hasattr(self, 'id_input'):
                self.id_input.textChanged.connect(self.save_info_fields)
            if hasattr(self, 'case_number_input'):
                self.case_number_input.textChanged.connect(self.save_info_fields)
            if hasattr(self, 'institution_input'):
                self.institution_input.textChanged.connect(self.save_info_fields)
            if hasattr(self, 'doctor_input'):
                self.doctor_input.textChanged.connect(self.save_info_fields)
            if hasattr(self, 'date_input'):
                self.date_input.textChanged.connect(self.save_info_fields)
            if hasattr(self, 'sex_input'):
                self.sex_input.currentIndexChanged.connect(self.save_info_fields)
            if hasattr(self, 'age_input'):
                self.age_input.textChanged.connect(self.save_info_fields)
            if hasattr(self, 'procedure_input'):
                self.procedure_input.textChanged.connect(self.save_info_fields)
            if hasattr(self, 'description_input'):
                self.description_input.textChanged.connect(self.save_info_fields)

class FullScreenVideoWindow(QWidget):
    def __init__(self, pixmap):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setWindowState(Qt.WindowFullScreen)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setPixmap(pixmap)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def set_pixmap(self, pixmap):
        self.label.setPixmap(pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def mousePressEvent(self, event):
        self.close()


def get_windows_mac_address():
    try:
        import subprocess
        # Try getmac command first
        result = subprocess.check_output("getmac /fo csv /nh", shell=True).decode().strip()
        mac_addresses = result.split('\n')
        for mac in mac_addresses:
            if mac and ',' in mac:
                parts = mac.split(',')
                if len(parts) >= 2:
                    # The first column contains the MAC address, second contains the device name
                    mac_addr = parts[0].strip().strip('"').replace('-', ':').upper()
                    if mac_addr and mac_addr != '00:00:00:00:00:00' and mac_addr != 'N/A' and len(mac_addr) == 17:
                        return mac_addr
        
        # Fallback: try ipconfig method
        try:
            result = subprocess.check_output("ipconfig /all", shell=True).decode('cp850', errors='ignore')
            lines = result.split('\n')
            for line in lines:
                if 'Physical Address' in line or 'MAC Address' in line:
                    mac_addr = line.split(':')[-1].strip().replace('-', ':').upper()
                    if mac_addr and mac_addr != '00:00:00:00:00:00' and len(mac_addr) == 17:
                        return mac_addr
        except:
            pass
            
        return "unknown"
    except Exception as e:
        print(f"Error getting MAC address: {e}")
        return "unknown"


class CameraGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._qimage = None

    def set_image(self, qimage):
        self._qimage = qimage
        self.update()

    def paintGL(self):
        if self._qimage is not None:
            from PyQt5.QtGui import QPainter
            painter = QPainter(self)
            # Widget and image dimensions
            widget_w, widget_h = self.width(), self.height()
            img_w, img_h = self._qimage.width(), self._qimage.height()
            # Calculate aspect ratios
            aspect_img = img_w / img_h
            aspect_widget = widget_w / widget_h
            # Determine final size to preserve aspect ratio
            if aspect_img > aspect_widget:
                draw_w = widget_w
                draw_h = int(widget_w / aspect_img)
            else:
                draw_h = widget_h
                draw_w = int(widget_h * aspect_img)
            # Center the image
            x = (widget_w - draw_w) // 2
            y = (widget_h - draw_h) // 2
            painter.drawImage(QRect(x, y, draw_w, draw_h), self._qimage)
            painter.end()

    def resizeGL(self, w, h):
        pass

    def initializeGL(self):
        pass

class SettingsDialog(QDialog):
    rotation_changed = pyqtSignal(int)
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # --- General Tab ---
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        general_layout.setSpacing(16)
        # Show scale bar
        scale_bar_row = QHBoxLayout()
        self.scale_bar_toggle = ToggleSwitch()
        scale_bar_label = QLabel("Show scale bar on saved images")
        scale_bar_row.addWidget(self.scale_bar_toggle)
        scale_bar_row.addWidget(scale_bar_label)
        scale_bar_row.addStretch(1)
        general_layout.addLayout(scale_bar_row)
        general_layout.addSpacing(10)
        # Rotation
        rot_layout = QHBoxLayout()
        self.rotation_angle = 0
        self.rotation_label = QLabel("Rotation: 0°")
        self.rotation_label.setFixedWidth(120)  # Enough for 'Rotation: 180°'
        self.rotate_button = QPushButton("↻")
        self.rotate_button.setFixedSize(40, 40)
        self.rotate_button.setStyleSheet("background-color: #888; color: white; font-size: 22px; border-radius: 20px;")
        self.rotate_button.clicked.connect(self.rotate_image)
        rot_layout.addWidget(self.rotation_label)
        rot_layout.addWidget(self.rotate_button)
        rot_layout.addStretch(1)
        general_layout.addLayout(rot_layout)
        general_layout.addSpacing(10)
        general_layout.addStretch(1)
        self.tabs.addTab(general_tab, "General")

        # --- Camera Tab ---
        camera_tab = QWidget()
        camera_layout = QVBoxLayout(camera_tab)
        camera_layout.setSpacing(16)
        # Preview resolution
        preview_row = QHBoxLayout()
        preview_row.addWidget(QLabel("Preview Resolution:"))
        self.preview_res_combo = QComboBox()
        self.preview_res_combo.addItems(["1280x720", "1456x1088"])
        preview_row.addWidget(self.preview_res_combo)
        preview_row.addStretch(1)
        camera_layout.addLayout(preview_row)
        camera_layout.addSpacing(10)
        # Photo resolution
        photo_row = QHBoxLayout()
        photo_row.addWidget(QLabel("Photo Resolution:"))
        self.photo_res_combo = QComboBox()
        self.photo_res_combo.addItems(["1456x1088", "1280x720"])
        photo_row.addWidget(self.photo_res_combo)
        photo_row.addStretch(1)
        camera_layout.addLayout(photo_row)
        camera_layout.addSpacing(10)
        # Video resolution
        video_row = QHBoxLayout()
        video_row.addWidget(QLabel("Video Resolution:"))
        self.video_res_combo = QComboBox()
        self.video_res_combo.addItems(["1456x1088", "1280x720"])
        video_row.addWidget(self.video_res_combo)
        video_row.addStretch(1)
        camera_layout.addLayout(video_row)
        camera_layout.addSpacing(10)
        # FPS
        fps_row = QHBoxLayout()
        fps_row.addWidget(QLabel("FPS:"))
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setFixedHeight(32)
        self.fps_spin.setStyleSheet('''
            QSpinBox {
                font-size: 16px;
                padding: 2px 8px;
                background: white;
                border: 0.5px solid #ccc;
                border-radius: 6px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 18px;
                height: 16px;
                subcontrol-origin: border;
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        ''')
        fps_row.addWidget(self.fps_spin)
        fps_row.addStretch(1)
        camera_layout.addLayout(fps_row)
        camera_layout.addSpacing(10)
        camera_layout.addStretch(1)
        self.tabs.addTab(camera_tab, "Camera")

        # Buttons
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        # Load current settings
        if settings:
            self.preview_res_combo.setCurrentText(settings.get("preview_res", "1280x720"))
            self.photo_res_combo.setCurrentText(settings.get("photo_res", "1456x1088"))
            self.video_res_combo.setCurrentText(settings.get("video_res", "1456x1088"))
            self.fps_spin.setValue(settings.get("fps", 30))
            self.rotation_angle = settings.get("rotation_angle", 0)
            self.rotation_label.setText(f"Rotation: {self.rotation_angle}°")
            self.scale_bar_toggle.setChecked(settings.get("show_scale_bar", True))
        combo_style = """
QComboBox QAbstractItemView {
    selection-background-color: #fff;
    selection-color: #000;
}
QComboBox QAbstractItemView::item:hover {
    background: #fff;
    color: #000;
}
"""
        self.preview_res_combo.setStyleSheet(combo_style)
        self.photo_res_combo.setStyleSheet(combo_style)
        self.video_res_combo.setStyleSheet(combo_style)

    def rotate_image(self, *args):
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.rotation_label.setText(f"Rotation: {self.rotation_angle}°")
        self.rotation_changed.emit(self.rotation_angle)

    def get_settings(self):
        return {
            "photo_res": self.photo_res_combo.currentText(),
            "video_res": self.video_res_combo.currentText(),
            "preview_res": self.preview_res_combo.currentText(),
            "fps": self.fps_spin.value(),
            "rotation_angle": self.rotation_angle,
            "show_scale_bar": self.scale_bar_toggle.isChecked(),
        }

if __name__ == "__main__":
    try:
        logger.info("Application starting...")
        app = QApplication(sys.argv)
        window = CameraControlPanel()
        # Ensure Info fields are saved on app close
        app.aboutToQuit.connect(window.save_info_fields)
        window.show()
        rc = app.exec_()
        logger.info(f"Application exited with code {rc}")
        sys.exit(rc)
    except Exception as e:
        try:
            logger.exception("Fatal error during startup")
        except Exception:
            pass
        # Also print to stderr for debug exe
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)