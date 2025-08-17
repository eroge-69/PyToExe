from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QFileSystemWatcher, QCoreApplication
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from qt_material import apply_stylesheet
import multiprocessing
import threading
import requests
import pymem
import pymem.process
import win32api
import win32con
import win32gui
from pynput.mouse import Controller, Button
from pynput import keyboard
import json
import os
import sys
import time
import math

# Константы
CONFIG_DIR = os.path.join(os.environ['LOCALAPPDATA'], 'temp', 'PyIt')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
DEFAULT_SETTINGS = {
    "esp_rendering": 1,
    "esp_mode": 1,
    "line_rendering": 1,
    "hp_bar_rendering": 1,
    "head_hitbox_rendering": 1,
    "bons": 1,
    "nickname": 1,
    "radius": 50,
    "keyboard": "ALT",
    "aim_active": 0,
    "aim_mode": 1,
    "aim_mode_distance": 1,
    "trigger_bot_active": 0,
    "keyboards": "X", 
    "weapon": 1,
    "bomb_esp": 1,
    "trigger_hit_chance": 100,
    "aim_fov": 50,
    "aim_smoothing": 0.3,
    
    # New targeting options
    "aim_target_mode": "head",  # head, neck, chest, legs, center, upper_body
    "head_offset": 3,  # pixels down from head
    "head_precision": 100,  # percentage for head precision
    "neck_offset": 8,  # pixels down from head for neck targeting
    
    # Recoil Control Settings
    "recoil_control_enabled": 1,  # Enable/disable recoil control
    "recoil_strength": 75,  # Recoil control strength (0-100)
    "recoil_smoothing": 0.8,  # Recoil smoothing factor (0.1-1.0)
    "ak47_recoil_pattern": 1,  # AK47 recoil pattern mode
    "m4_recoil_pattern": 1,  # M4 recoil pattern mode
    "m4a1_recoil_pattern": 1,  # M4A1 recoil pattern mode

    "esp_box_color_r": 255,
    "esp_box_color_g": 0,
    "esp_box_color_b": 0,
    "esp_bone_color_r": 0,
    "esp_bone_color_g": 255,
    "esp_bone_color_b": 0,
    "esp_health_color_r": 0,
    "esp_health_color_g": 0,
    "esp_health_color_b": 255,
    "esp_head_color_r": 255,
    "esp_head_color_g": 255,
    "esp_head_color_b": 0,
    "esp_name_color_r": 255,
    "esp_name_color_g": 255,
    "esp_name_color_b": 255,
    "esp_weapon_color_r": 255,
    "esp_weapon_color_g": 0,
    "esp_weapon_color_b": 255,
    "sniper_crosshair": 1,
    "silent_aim": 0,
    "silent_aim_key": "SHIFT",
    "silent_aim_fov": 30,
    "silent_aim_smoothing": 0.5
}
BombPlantedTime = 0
BombDefusedTime = 0
kill_switch_active = False
locked_target = None  # Track the currently locked target

# Функции утилиты
def load_settings():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
        return DEFAULT_SETTINGS
    
    try:
        with open(CONFIG_FILE, "r") as f:
            settings = json.load(f)
        
        # Validate and repair settings if needed
        repaired = False
        for key, default_value in DEFAULT_SETTINGS.items():
            if key not in settings:
                settings[key] = default_value
                repaired = True
        
        if repaired:
            print("Settings file was corrupted, repairing...")
            save_settings(settings)
        
        return settings
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Settings file corrupted: {e}. Creating new settings file...")
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
        return DEFAULT_SETTINGS

def save_settings(settings):
    with open(CONFIG_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def get_offsets_and_client_dll():
    try:
        # Updated to use the latest CS2 dumper repository
        offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json', timeout=10).json()
        client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json', timeout=10).json()
        return offsets, client_dll
    except Exception as e:
        print(f"Failed to fetch offsets: {e}")
        # Fallback to cached offsets if available
        return None, None

def get_window_size(window_title="Counter-Strike 2"):
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        rect = win32gui.GetClientRect(hwnd)
        return rect[2], rect[3]
    return None, None

def w2s(mtx, posx, posy, posz, width, height):
    screenW = (mtx[12] * posx) + (mtx[13] * posy) + (mtx[14] * posz) + mtx[15]
    if screenW > 0.001:
        screenX = (mtx[0] * posx) + (mtx[1] * posy) + (mtx[2] * posz) + mtx[3]
        screenY = (mtx[4] * posx) + (mtx[5] * posy) + (mtx[6] * posz) + mtx[7]
        camX = width / 2
        camY = height / 2
        x = camX + (camX * screenX / screenW)
        y = camY - (camY * screenY / screenW)
        return [int(x), int(y)]
    return [-999, -999]

# Kill Switch Functions
def on_kill_switch_press(key):
    global kill_switch_active
    try:
        if key.char == '=':
            print("Kill switch activated! Shutting down...")
            kill_switch_active = True
            os._exit(0)  # Force exit all processes
    except AttributeError:
        pass

def start_kill_switch_listener():
    """Start the kill switch keyboard listener"""
    with keyboard.Listener(on_press=on_kill_switch_press) as listener:
        listener.join()

# Recoil Control Functions
class RecoilControl:
    def __init__(self):
        self.shot_count = 0
        self.last_shot_time = 0
        self.current_weapon = None
        self.recoil_patterns = {
            'ak47': {
                'pattern': [
                    (0, 0), (0, 7), (-1, 7), (1, 7), (0, 7), (-1, 7), (1, 7), (0, 7),
                    (-1, 7), (1, 7), (0, 7), (-1, 7), (1, 7), (0, 7), (-1, 7), (1, 7),
                    (0, 7), (-1, 7), (1, 7), (0, 7), (-1, 7), (1, 7), (0, 7), (-1, 7),
                    (1, 7), (0, 7), (-1, 7), (1, 7), (0, 7), (-1, 7)
                ],
                'reset_time': 0.5  # Time to reset pattern
            },
            'm4': {
                'pattern': [
                    (0, 0), (0, 6), (0, 6), (0, 6), (0, 6), (0, 6), (0, 6), (0, 6),
                    (0, 6), (0, 6), (0, 6), (0, 6), (0, 6), (0, 6), (0, 6), (0, 6),
                    (0, 6), (0, 6), (0, 6), (0, 6), (0, 6), (0, 6), (0, 6), (0, 6),
                    (0, 6), (0, 6), (0, 6), (0, 6), (0, 6), (0, 6)
                ],
                'reset_time': 0.4
            },
            'm4a1': {
                'pattern': [
                    (0, 0), (0, 5), (0, 5), (0, 5), (0, 5), (0, 5), (0, 5), (0, 5),
                    (0, 5), (0, 5), (0, 5), (0, 5), (0, 5), (0, 5), (0, 5), (0, 5),
                    (0, 5), (0, 5), (0, 5), (0, 5), (0, 5), (0, 5), (0, 5), (0, 5),
                    (0, 5), (0, 5), (0, 5), (0, 5), (0, 5), (0, 5)
                ],
                'reset_time': 0.35
            }
        }
    
    def get_current_weapon(self, pm, client, offsets, client_dll):
        """Get the current weapon the player is holding"""
        try:
            dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
            m_hActiveWeapon = client_dll['client.dll']['classes']['C_BasePlayerPawn']['fields']['m_hActiveWeapon']
            m_szWeaponName = client_dll['client.dll']['classes']['C_EconEntity']['fields']['m_szWeaponName']
            
            local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
            if local_player_pawn_addr == 0:
                return None
            
            active_weapon_handle = pm.read_int(local_player_pawn_addr + m_hActiveWeapon)
            if active_weapon_handle == 0:
                return None
            
            # Get weapon entity
            dwEntityList = offsets['client.dll']['dwEntityList']
            entity_list = pm.read_longlong(client + dwEntityList)
            weapon_entity = pm.read_longlong(entity_list + 0x8 * ((active_weapon_handle & 0x7FFF) >> 0x9) + 0x10)
            if weapon_entity == 0:
                return None
            
            weapon_addr = pm.read_longlong(weapon_entity + 0x78 * (active_weapon_handle & 0x1FF))
            if weapon_addr == 0:
                return None
            
            # Read weapon name
            weapon_name = ""
            for i in range(32):
                char = pm.read_char(weapon_addr + m_szWeaponName + i)
                if char == 0:
                    break
                weapon_name += char
            
            return weapon_name.lower()
            
        except Exception as e:
            print(f"Error getting weapon: {e}")
            return None
    
    def reset_pattern(self):
        """Reset the recoil pattern"""
        self.shot_count = 0
        self.last_shot_time = 0
    
    def apply_recoil_control(self, settings):
        """Apply recoil control based on current weapon and settings"""
        if not settings.get('recoil_control_enabled', 1):
            return
        
        current_time = time.time()
        
        # Reset pattern if too much time has passed
        if current_time - self.last_shot_time > 1.0:
            self.reset_pattern()
            return
        
        # Get recoil strength and smoothing
        recoil_strength = settings.get('recoil_strength', 75) / 100.0
        recoil_smoothing = settings.get('recoil_smoothing', 0.8)
        
        # Get weapon-specific pattern
        weapon_pattern = None
        if self.current_weapon in ['weapon_ak47', 'ak47']:
            weapon_pattern = self.recoil_patterns['ak47']
        elif self.current_weapon in ['weapon_m4a1', 'm4a1']:
            weapon_pattern = self.recoil_patterns['m4a1']
        elif self.current_weapon in ['weapon_m4a1_silencer', 'm4a1_silencer']:
            weapon_pattern = self.recoil_patterns['m4a1']
        elif self.current_weapon in ['weapon_m4a4', 'm4a4', 'm4']:
            weapon_pattern = self.recoil_patterns['m4']
        
        if weapon_pattern and self.shot_count < len(weapon_pattern['pattern']):
            # Get recoil offset for current shot
            recoil_x, recoil_y = weapon_pattern['pattern'][self.shot_count]
            
            # Apply recoil strength
            move_x = int(-recoil_x * recoil_strength)
            move_y = int(-recoil_y * recoil_strength)
            
            # Apply smoothing
            if recoil_smoothing < 1.0:
                move_x = int(move_x * recoil_smoothing)
                move_y = int(move_y * recoil_smoothing)
            
            # Move mouse to compensate for recoil
            if move_x != 0 or move_y != 0:
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, move_x, move_y, 0, 0)
            
            self.shot_count += 1
            self.last_shot_time = current_time

# Global recoil control instance
recoil_control = RecoilControl()

# Конфигуратор
class ConfigWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.initUI()
        self.is_dragging = False
        self.drag_start_position = None
        self.setStyleSheet("background-color: #ffffff; border: 1px solid #bdc3c7;")

    def initUI(self):
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setFixedSize(1200, 800)
        self.setWindowTitle("Goon Ware - CS2 Cheat")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.menu_visible = True

        # Create title bar
        title_bar = QtWidgets.QWidget()
        title_bar.setFixedHeight(50)
        title_bar.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #1a1a1a, stop:1 #2d2d2d);
                border-bottom: 2px solid #ff69b4;
            }
        """)
        
        title_layout = QtWidgets.QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 0, 20, 0)
        
        # Title with gradient text effect
        title_label = QtWidgets.QLabel("GOON WARE")
        title_label.setStyleSheet("""
            QLabel {
                color: #ff69b4;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
        """)
        
        subtitle_label = QtWidgets.QLabel("CS2 CHEAT")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 12px;
                font-weight: normal;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin-left: 10px;
            }
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.addStretch()
        
        # Close button
        close_btn = QtWidgets.QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #ff4444;
                border: none;
                border-radius: 15px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #ff6666;
            }
            QPushButton:pressed {
                background: #cc3333;
            }
        """)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)

        # Main layout with modern styling
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add title bar
        main_layout.addWidget(title_bar)
        
        # Main content area with gradient background
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #1e1e1e, stop:0.5 #2a2a2a, stop:1 #1e1e1e);
            }
        """)
        content_layout = QtWidgets.QHBoxLayout(content_widget)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create sidebar with categories
        sidebar_widget = QtWidgets.QWidget()
        sidebar_widget.setFixedWidth(200)
        sidebar_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #1a1a1a, stop:1 #2d2d2d);
                border-right: 2px solid #ff69b4;
            }
        """)
        
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar_widget)
        sidebar_layout.setSpacing(10)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        
        # Sidebar title
        sidebar_title = QtWidgets.QLabel("CATEGORIES")
        sidebar_title.setStyleSheet("""
            QLabel {
                color: #ff69b4;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
                padding: 10px;
                border-bottom: 1px solid #333333;
                margin-bottom: 10px;
            }
        """)
        sidebar_title.setAlignment(QtCore.Qt.AlignCenter)
        sidebar_layout.addWidget(sidebar_title)
        
        # Category buttons
        self.esp_btn = QtWidgets.QPushButton("👁️ ESP")
        self.aimbot_btn = QtWidgets.QPushButton("🎯 AIMBOT")
        self.trigger_btn = QtWidgets.QPushButton("⚡ TRIGGERBOT")
        
        # Style for category buttons
        category_button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                border: 2px solid #333333;
                border-radius: 10px;
                color: #888888;
                font-size: 14px;
                font-weight: bold;
                padding: 15px 10px;
                text-align: left;
                margin: 5px 0px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #333333, stop:1 #2a2a2a);
                border: 2px solid #555555;
                color: #ffffff;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1e1e1e, stop:1 #2a2a2a);
            }
        """
        
        active_button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ff69b4, stop:1 #e91e63);
                border: 2px solid #ff69b4;
                border-radius: 10px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 15px 10px;
                text-align: left;
                margin: 5px 0px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ff8ac4, stop:1 #ff69b4);
            }
        """
        
        self.esp_btn.setStyleSheet(active_button_style)  # Start with ESP active
        self.aimbot_btn.setStyleSheet(category_button_style)
        self.trigger_btn.setStyleSheet(category_button_style)
        
        # Connect button clicks
        self.esp_btn.clicked.connect(lambda: self.show_category("esp"))
        self.aimbot_btn.clicked.connect(lambda: self.show_category("aimbot"))
        self.trigger_btn.clicked.connect(lambda: self.show_category("trigger"))
        
        sidebar_layout.addWidget(self.esp_btn)
        sidebar_layout.addWidget(self.aimbot_btn)
        sidebar_layout.addWidget(self.trigger_btn)
        sidebar_layout.addStretch()
        
        # Add sidebar to layout
        content_layout.addWidget(sidebar_widget)
        
        # Create content area
        self.content_area = QtWidgets.QStackedWidget()
        self.content_area.setStyleSheet("""
            QStackedWidget {
                background: transparent;
            }
        """)
        
        # Create scroll area for content
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #1e1e1e;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #ff69b4;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #ff8ac4;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create content pages
        self.esp_page = self.create_esp_content()
        self.aimbot_page = self.create_aimbot_content()
        self.trigger_page = self.create_trigger_content()
        
        # Add pages to stacked widget
        self.content_area.addWidget(self.esp_page)
        self.content_area.addWidget(self.aimbot_page)
        self.content_area.addWidget(self.trigger_page)
        
        # Set initial page
        self.content_area.setCurrentIndex(0)
        
        # Add content area to layout
        content_layout.addWidget(self.content_area)
        
        # Store button styles for category switching
        self.category_button_style = category_button_style
        self.active_button_style = active_button_style
        
        main_layout.addWidget(content_widget)
        
        self.setLayout(main_layout)
        self.setStyleSheet("""
            QWidget {
                background: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        # Initialize key binding timer
        self.key_binding_timer = QtCore.QTimer()
        self.key_binding_timer.timeout.connect(self.check_key_binding)
        self.key_binding_timer.start(50)
        
        # Update toggle styles
        self.update_toggle_style()
    
    def show_category(self, category):
        """Switch between different categories"""
        # Reset all button styles
        self.esp_btn.setStyleSheet(self.category_button_style)
        self.aimbot_btn.setStyleSheet(self.category_button_style)
        self.trigger_btn.setStyleSheet(self.category_button_style)
        
        # Set active button style and show corresponding content
        if category == "esp":
            self.esp_btn.setStyleSheet(self.active_button_style)
            self.content_area.setCurrentIndex(0)
        elif category == "aimbot":
            self.aimbot_btn.setStyleSheet(self.active_button_style)
            self.content_area.setCurrentIndex(1)
        elif category == "trigger":
            self.trigger_btn.setStyleSheet(self.active_button_style)
            self.content_area.setCurrentIndex(2)

    def create_esp_content(self):
        """Create the ESP content page"""
        page_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Create scroll area for this page
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #1e1e1e;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #ff69b4;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #ff8ac4;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create content container
        content_container = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_container)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # ESP Settings Section
        esp_group = QtWidgets.QGroupBox("ESP SETTINGS")
        esp_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #ffffff;
                border: 2px solid #ff69b4;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #ff69b4;
                background: #1e1e1e;
                border-radius: 6px;
                font-size: 14px;
                letter-spacing: 1px;
            }
        """)
        esp_layout = QtWidgets.QVBoxLayout(esp_group)
        
        # ESP toggles in a grid
        toggle_grid = QtWidgets.QGridLayout()
        
        self.esp_rendering_cb = QtWidgets.QCheckBox("Enable ESP")
        self.esp_rendering_cb.setChecked(self.settings["esp_rendering"] == 1)
        self.esp_rendering_cb.stateChanged.connect(self.save_settings)
        self.esp_rendering_cb.stateChanged.connect(self.update_toggle_style)
        toggle_grid.addWidget(self.esp_rendering_cb, 0, 0)
        
        self.line_rendering_cb = QtWidgets.QCheckBox("Draw Lines")
        self.line_rendering_cb.setChecked(self.settings["line_rendering"] == 1)
        self.line_rendering_cb.stateChanged.connect(self.save_settings)
        self.line_rendering_cb.stateChanged.connect(self.update_toggle_style)
        toggle_grid.addWidget(self.line_rendering_cb, 0, 1)
        
        self.hp_bar_rendering_cb = QtWidgets.QCheckBox("Health Bars")
        self.hp_bar_rendering_cb.setChecked(self.settings["hp_bar_rendering"] == 1)
        self.hp_bar_rendering_cb.stateChanged.connect(self.save_settings)
        self.hp_bar_rendering_cb.stateChanged.connect(self.update_toggle_style)
        toggle_grid.addWidget(self.hp_bar_rendering_cb, 1, 0)
        
        self.head_hitbox_rendering_cb = QtWidgets.QCheckBox("Head Hitboxes")
        self.head_hitbox_rendering_cb.setChecked(self.settings["head_hitbox_rendering"] == 1)
        self.head_hitbox_rendering_cb.stateChanged.connect(self.save_settings)
        self.head_hitbox_rendering_cb.stateChanged.connect(self.update_toggle_style)
        toggle_grid.addWidget(self.head_hitbox_rendering_cb, 1, 1)
        
        self.bons_cb = QtWidgets.QCheckBox("Skeleton ESP")
        self.bons_cb.setChecked(self.settings["bons"] == 1)
        self.bons_cb.stateChanged.connect(self.save_settings)
        self.bons_cb.stateChanged.connect(self.update_toggle_style)
        toggle_grid.addWidget(self.bons_cb, 2, 0)
        
        self.nickname_cb = QtWidgets.QCheckBox("Player Names")
        self.nickname_cb.setChecked(self.settings["nickname"] == 1)
        self.nickname_cb.stateChanged.connect(self.save_settings)
        self.nickname_cb.stateChanged.connect(self.update_toggle_style)
        toggle_grid.addWidget(self.nickname_cb, 2, 1)
        
        self.weapon_cb = QtWidgets.QCheckBox("Weapon Names")
        self.weapon_cb.setChecked(self.settings["weapon"] == 1)
        self.weapon_cb.stateChanged.connect(self.save_settings)
        self.weapon_cb.stateChanged.connect(self.update_toggle_style)
        toggle_grid.addWidget(self.weapon_cb, 3, 0)
        
        self.bomb_esp_cb = QtWidgets.QCheckBox("Bomb ESP")
        self.bomb_esp_cb.setChecked(self.settings["bomb_esp"] == 1)
        self.bomb_esp_cb.stateChanged.connect(self.save_settings)
        self.bomb_esp_cb.stateChanged.connect(self.update_toggle_style)
        toggle_grid.addWidget(self.bomb_esp_cb, 3, 1)
        
        self.sniper_crosshair_cb = QtWidgets.QCheckBox("Sniper Crosshair")
        self.sniper_crosshair_cb.setChecked(self.settings["sniper_crosshair"] == 1)
        self.sniper_crosshair_cb.stateChanged.connect(self.save_settings)
        self.sniper_crosshair_cb.stateChanged.connect(self.update_toggle_style)
        toggle_grid.addWidget(self.sniper_crosshair_cb, 4, 0)
        
        esp_layout.addLayout(toggle_grid)
        
        # ESP Mode
        mode_layout = QtWidgets.QHBoxLayout()
        esp_mode_label = QtWidgets.QLabel("ESP MODE:")
        esp_mode_label.setStyleSheet("""
            QLabel {
                color: #ff69b4;
                font-weight: bold;
                font-size: 13px;
                letter-spacing: 1px;
                padding: 5px 0px;
            }
        """)
        mode_layout.addWidget(esp_mode_label)
        self.esp_mode_cb = QtWidgets.QComboBox()
        self.esp_mode_cb.addItems(["Enemies Only", "All Players"])
        self.esp_mode_cb.setCurrentIndex(self.settings["esp_mode"])
        self.esp_mode_cb.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                border: 2px solid #ff69b4;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 13px;
                min-width: 140px;
                color: #ffffff;
                font-weight: bold;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #ff69b4;
                margin-right: 5px;
            }
            QComboBox:hover {
                border: 2px solid #ff8ac4;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #333333, stop:1 #2a2a2a);
            }
            QComboBox QAbstractItemView {
                background: #1e1e1e;
                color: #ffffff;
                border: 2px solid #ff69b4;
                border-radius: 8px;
                selection-background-color: #ff69b4;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 15px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #333333;
            }
        """)
        self.esp_mode_cb.currentIndexChanged.connect(self.save_settings)
        mode_layout.addWidget(self.esp_mode_cb)
        mode_layout.addStretch()
        esp_layout.addLayout(mode_layout)
        
        layout.addWidget(esp_group)
        
        # Color Settings Section
        color_group = QtWidgets.QGroupBox("COLOR CUSTOMIZATION")
        color_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #ffffff;
                border: 2px solid #ff69b4;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #ff69b4;
                background: #1e1e1e;
                border-radius: 6px;
                font-size: 14px;
                letter-spacing: 1px;
            }
        """)
        color_layout = QtWidgets.QVBoxLayout(color_group)
        
        # Color grid
        color_grid = QtWidgets.QGridLayout()
        
        # Box color
        box_color_label = QtWidgets.QLabel("BOX COLOR:")
        box_color_label.setStyleSheet("""
            QLabel {
                color: #ff69b4;
                font-weight: bold;
                font-size: 12px;
                letter-spacing: 0.5px;
                padding: 5px 0px;
            }
        """)
        color_grid.addWidget(box_color_label, 0, 0)
        self.box_color_r = QtWidgets.QSpinBox()
        self.box_color_r.setRange(0, 255)
        self.box_color_r.setValue(self.settings.get("esp_box_color_r", 255))
        self.box_color_r.valueChanged.connect(self.save_settings)
        self.box_color_r.setStyleSheet("""
            QSpinBox {
                padding: 8px 12px;
                border: 2px solid #ff69b4;
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
                min-width: 60px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background: #ff69b4;
                border: none;
                border-radius: 4px;
                width: 20px;
                margin: 2px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #ff8ac4;
            }
            QSpinBox::up-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid white;
            }
            QSpinBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid white;
            }
        """)
        color_grid.addWidget(self.box_color_r, 0, 1)
        
        self.box_color_g = QtWidgets.QSpinBox()
        self.box_color_g.setRange(0, 255)
        self.box_color_g.setValue(self.settings.get("esp_box_color_g", 0))
        self.box_color_g.valueChanged.connect(self.save_settings)
        self.box_color_g.setStyleSheet("""
            QSpinBox {
                padding: 8px 12px;
                border: 2px solid #ff69b4;
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
                min-width: 60px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background: #ff69b4;
                border: none;
                border-radius: 4px;
                width: 20px;
                margin: 2px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #ff8ac4;
            }
            QSpinBox::up-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid white;
            }
            QSpinBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid white;
            }
        """)
        color_grid.addWidget(self.box_color_g, 0, 2)
        
        self.box_color_b = QtWidgets.QSpinBox()
        self.box_color_b.setRange(0, 255)
        self.box_color_b.setValue(self.settings.get("esp_box_color_b", 0))
        self.box_color_b.valueChanged.connect(self.save_settings)
        self.box_color_b.setStyleSheet("""
            QSpinBox {
                padding: 8px 12px;
                border: 2px solid #ff69b4;
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
                min-width: 60px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background: #ff69b4;
                border: none;
                border-radius: 4px;
                width: 20px;
                margin: 2px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #ff8ac4;
            }
            QSpinBox::up-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid white;
            }
            QSpinBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid white;
            }
        """)
        color_grid.addWidget(self.box_color_b, 0, 3)
        
        # Bone color
        bone_color_label = QtWidgets.QLabel("BONE COLOR:")
        bone_color_label.setStyleSheet("""
            QLabel {
                color: #ff69b4;
                font-weight: bold;
                font-size: 12px;
                letter-spacing: 0.5px;
                padding: 5px 0px;
            }
        """)
        color_grid.addWidget(bone_color_label, 1, 0)
        self.bone_color_r = QtWidgets.QSpinBox()
        self.bone_color_r.setRange(0, 255)
        self.bone_color_r.setValue(self.settings.get("esp_bone_color_r", 0))
        self.bone_color_r.valueChanged.connect(self.save_settings)
        self.bone_color_r.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #ced4da; border-radius: 5px; }")
        color_grid.addWidget(self.bone_color_r, 1, 1)
        
        self.bone_color_g = QtWidgets.QSpinBox()
        self.bone_color_g.setRange(0, 255)
        self.bone_color_g.setValue(self.settings.get("esp_bone_color_g", 255))
        self.bone_color_g.valueChanged.connect(self.save_settings)
        self.bone_color_g.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #ced4da; border-radius: 5px; }")
        color_grid.addWidget(self.bone_color_g, 1, 2)
        
        self.bone_color_b = QtWidgets.QSpinBox()
        self.bone_color_b.setRange(0, 255)
        self.bone_color_b.setValue(self.settings.get("esp_bone_color_b", 0))
        self.bone_color_b.valueChanged.connect(self.save_settings)
        self.bone_color_b.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #ced4da; border-radius: 5px; }")
        color_grid.addWidget(self.bone_color_b, 1, 3)
        
        # Health color
        color_grid.addWidget(QtWidgets.QLabel("Health Color:"), 2, 0)
        self.health_color_r = QtWidgets.QSpinBox()
        self.health_color_r.setRange(0, 255)
        self.health_color_r.setValue(self.settings.get("esp_health_color_r", 0))
        self.health_color_r.valueChanged.connect(self.save_settings)
        self.health_color_r.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #ced4da; border-radius: 5px; }")
        color_grid.addWidget(self.health_color_r, 2, 1)
        
        self.health_color_g = QtWidgets.QSpinBox()
        self.health_color_g.setRange(0, 255)
        self.health_color_g.setValue(self.settings.get("esp_health_color_g", 0))
        self.health_color_g.valueChanged.connect(self.save_settings)
        self.health_color_g.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #ced4da; border-radius: 5px; }")
        color_grid.addWidget(self.health_color_g, 2, 2)
        
        self.health_color_b = QtWidgets.QSpinBox()
        self.health_color_b.setRange(0, 255)
        self.health_color_b.setValue(self.settings.get("esp_health_color_b", 255))
        self.health_color_b.valueChanged.connect(self.save_settings)
        self.health_color_b.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #ced4da; border-radius: 5px; }")
        color_grid.addWidget(self.health_color_b, 2, 3)
        
        # Head color
        color_grid.addWidget(QtWidgets.QLabel("Head Color:"), 3, 0)
        self.head_color_r = QtWidgets.QSpinBox()
        self.head_color_r.setRange(0, 255)
        self.head_color_r.setValue(self.settings.get("esp_head_color_r", 255))
        self.head_color_r.valueChanged.connect(self.save_settings)
        self.head_color_r.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #ced4da; border-radius: 5px; }")
        color_grid.addWidget(self.head_color_r, 3, 1)
        
        self.head_color_g = QtWidgets.QSpinBox()
        self.head_color_g.setRange(0, 255)
        self.head_color_g.setValue(self.settings.get("esp_head_color_g", 255))
        self.head_color_g.valueChanged.connect(self.save_settings)
        self.head_color_g.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #ced4da; border-radius: 5px; }")
        color_grid.addWidget(self.head_color_g, 3, 2)
        
        self.head_color_b = QtWidgets.QSpinBox()
        self.head_color_b.setRange(0, 255)
        self.head_color_b.setValue(self.settings.get("esp_head_color_b", 0))
        self.head_color_b.valueChanged.connect(self.save_settings)
        self.head_color_b.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #ced4da; border-radius: 5px; }")
        color_grid.addWidget(self.head_color_b, 3, 3)
        
        # Name color
        color_grid.addWidget(QtWidgets.QLabel("Name Color:"), 4, 0)
        self.name_color_r = QtWidgets.QSpinBox()
        self.name_color_r.setRange(0, 255)
        self.name_color_r.setValue(self.settings.get("esp_name_color_r", 255))
        self.name_color_r.valueChanged.connect(self.save_settings)
        self.name_color_r.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #ced4da; border-radius: 5px; }")
        color_grid.addWidget(self.name_color_r, 4, 1)
        
        self.name_color_g = QtWidgets.QSpinBox()
        self.name_color_g.setRange(0, 255)
        self.name_color_g.setValue(self.settings.get("esp_name_color_g", 255))
        self.name_color_g.valueChanged.connect(self.save_settings)
        self.name_color_g.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #ced4da; border-radius: 5px; }")
        color_grid.addWidget(self.name_color_g, 4, 2)
        
        self.name_color_b = QtWidgets.QSpinBox()
        self.name_color_b.setRange(0, 255)
        self.name_color_b.setValue(self.settings.get("esp_name_color_b", 255))
        self.name_color_b.valueChanged.connect(self.save_settings)
        self.name_color_b.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #ced4da; border-radius: 5px; }")
        color_grid.addWidget(self.name_color_b, 4, 3)
        
        # Weapon color
        color_grid.addWidget(QtWidgets.QLabel("Weapon Color:"), 5, 0)
        self.weapon_color_r = QtWidgets.QSpinBox()
        self.weapon_color_r.setRange(0, 255)
        self.weapon_color_r.setValue(self.settings.get("esp_weapon_color_r", 255))
        self.weapon_color_r.valueChanged.connect(self.save_settings)
        self.weapon_color_r.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #ced4da; border-radius: 5px; }")
        color_grid.addWidget(self.weapon_color_r, 5, 1)
        
        self.weapon_color_g = QtWidgets.QSpinBox()
        self.weapon_color_g.setRange(0, 255)
        self.weapon_color_g.setValue(self.settings.get("esp_weapon_color_g", 0))
        self.weapon_color_g.valueChanged.connect(self.save_settings)
        self.weapon_color_g.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #ced4da; border-radius: 5px; }")
        color_grid.addWidget(self.weapon_color_g, 5, 2)
        
        self.weapon_color_b = QtWidgets.QSpinBox()
        self.weapon_color_b.setRange(0, 255)
        self.weapon_color_b.setValue(self.settings.get("esp_weapon_color_b", 255))
        self.weapon_color_b.valueChanged.connect(self.save_settings)
        self.weapon_color_b.setStyleSheet("QSpinBox { padding: 5px; border: 1px solid #ced4da; border-radius: 5px; }")
        color_grid.addWidget(self.weapon_color_b, 5, 3)
        
        color_layout.addLayout(color_grid)
        content_layout.addWidget(color_group)
        
        # Set up scroll area
        scroll_area.setWidget(content_container)
        layout.addWidget(scroll_area)
        page_widget.setLayout(layout)
        return page_widget

    def create_aimbot_content(self):
        """Create the Aimbot content page"""
        page_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Create scroll area for this page
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #1e1e1e;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #ff69b4;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #ff8ac4;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create content container
        content_container = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_container)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Aimbot Settings
        aim_group = QtWidgets.QGroupBox("🎯 AIMBOT CONFIGURATION")
        aim_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #ffffff;
                border: 2px solid #ff69b4;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #ff69b4;
                background: #1e1e1e;
                border-radius: 6px;
                font-size: 14px;
                letter-spacing: 1px;
            }
        """)
        aim_layout = QtWidgets.QVBoxLayout(aim_group)
        
        # Enable Aimbot
        self.aim_active_cb = QtWidgets.QCheckBox("Enable Aimbot")
        self.aim_active_cb.setChecked(self.settings.get("aim_active", 0) == 1)
        self.aim_active_cb.stateChanged.connect(self.save_settings)
        self.aim_active_cb.stateChanged.connect(self.update_toggle_style)
        aim_layout.addWidget(self.aim_active_cb)
        
        # Key binding
        key_layout = QtWidgets.QHBoxLayout()
        key_layout.addWidget(QtWidgets.QLabel("Aimbot Key:"))
        self.keyboard_input = QtWidgets.QLineEdit()
        self.keyboard_input.setText(self.settings.get("keyboard", "ALT"))
        self.keyboard_input.setReadOnly(True)
        self.keyboard_input.mousePressEvent = lambda event: self.start_key_binding(self.keyboard_input, "keyboard")
        self.keyboard_input.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                border: 2px solid #ff69b4;
                border-radius: 8px;
                color: #ffffff;
                cursor: pointer;
                padding: 10px 15px;
                font-size: 13px;
                font-weight: bold;
            }
            QLineEdit:hover {
                border-color: #ff8ac4;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #333333, stop:1 #2a2a2a);
            }
        """)
        self.keyboard_input.setPlaceholderText("Click to set key...")
        key_layout.addWidget(self.keyboard_input)
        key_layout.addStretch()
        aim_layout.addLayout(key_layout)
        
        # Advanced Targeting Options
        target_group = QtWidgets.QGroupBox("🎯 TARGETING OPTIONS")
        target_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #ffffff;
                border: 2px solid #ff69b4;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #ff69b4;
                background: #1e1e1e;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        target_layout = QtWidgets.QVBoxLayout(target_group)
        
        # Target Mode Selection
        target_mode_layout = QtWidgets.QHBoxLayout()
        target_mode_layout.addWidget(QtWidgets.QLabel("Target Mode:"))
        self.aim_target_mode_cb = QtWidgets.QComboBox()
        self.aim_target_mode_cb.addItems(["Head", "Neck", "Chest", "Legs", "Center", "Upper Body"])
        
        # Set current value based on settings
        target_mode = self.settings.get("aim_target_mode", "head")
        target_mode_index = {"head": 0, "neck": 1, "chest": 2, "legs": 3, "center": 4, "upper_body": 5}.get(target_mode, 0)
        self.aim_target_mode_cb.setCurrentIndex(target_mode_index)
        
        self.aim_target_mode_cb.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                border: 2px solid #ff69b4;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 13px;
                min-width: 140px;
                color: #ffffff;
                font-weight: bold;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #ff69b4;
                margin-right: 5px;
            }
            QComboBox:hover {
                border: 2px solid #ff8ac4;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #333333, stop:1 #2a2a2a);
            }
            QComboBox QAbstractItemView {
                background: #1e1e1e;
                color: #ffffff;
                border: 2px solid #ff69b4;
                border-radius: 8px;
                selection-background-color: #ff69b4;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 15px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #333333;
            }
        """)
        self.aim_target_mode_cb.currentIndexChanged.connect(self.save_settings)
        target_mode_layout.addWidget(self.aim_target_mode_cb)
        target_mode_layout.addStretch()
        target_layout.addLayout(target_mode_layout)
        
        # Head Offset Slider
        head_offset_layout = QtWidgets.QVBoxLayout()
        head_offset_layout.addWidget(QtWidgets.QLabel("Head Offset (Pixels Down):"))
        self.head_offset_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.head_offset_slider.setMinimum(0)
        self.head_offset_slider.setMaximum(10)
        self.head_offset_slider.setValue(self.settings.get("head_offset", 3))
        self.head_offset_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #333333;
                background: #1e1e1e;
                height: 12px;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: #ff69b4;
                border: 2px solid #ff69b4;
                width: 20px;
                margin: -4px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #ff8ac4;
                border: 2px solid #ff8ac4;
            }
            QSlider::sub-page:horizontal {
                background: #ff69b4;
                border-radius: 6px;
            }
        """)
        self.head_offset_slider.valueChanged.connect(self.save_settings)
        head_offset_layout.addWidget(self.head_offset_slider)
        target_layout.addLayout(head_offset_layout)
        
        # Head Precision Slider
        head_precision_layout = QtWidgets.QVBoxLayout()
        head_precision_layout.addWidget(QtWidgets.QLabel("Head Precision (Center Alignment):"))
        self.head_precision_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.head_precision_slider.setMinimum(50)
        self.head_precision_slider.setMaximum(100)
        self.head_precision_slider.setValue(self.settings.get("head_precision", 100))
        self.head_precision_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #333333;
                background: #1e1e1e;
                height: 12px;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: #ff69b4;
                border: 2px solid #ff69b4;
                width: 20px;
                margin: -4px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #ff8ac4;
                border: 2px solid #ff8ac4;
            }
            QSlider::sub-page:horizontal {
                background: #ff69b4;
                border-radius: 6px;
            }
        """)
        self.head_precision_slider.valueChanged.connect(self.save_settings)
        head_precision_layout.addWidget(self.head_precision_slider)
        target_layout.addLayout(head_precision_layout)
        
        # Neck Offset Slider
        neck_offset_layout = QtWidgets.QVBoxLayout()
        neck_offset_layout.addWidget(QtWidgets.QLabel("Neck Offset (Pixels Down from Head):"))
        self.neck_offset_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.neck_offset_slider.setMinimum(5)
        self.neck_offset_slider.setMaximum(15)
        self.neck_offset_slider.setValue(self.settings.get("neck_offset", 8))
        self.neck_offset_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #333333;
                background: #1e1e1e;
                height: 12px;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: #ff69b4;
                border: 2px solid #ff69b4;
                width: 20px;
                margin: -4px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #ff8ac4;
                border: 2px solid #ff8ac4;
            }
            QSlider::sub-page:horizontal {
                background: #ff69b4;
                border-radius: 6px;
            }
        """)
        self.neck_offset_slider.valueChanged.connect(self.save_settings)
        neck_offset_layout.addWidget(self.neck_offset_slider)
        target_layout.addLayout(neck_offset_layout)
        
        aim_layout.addWidget(target_group)
        
        # Distance priority
        dist_layout = QtWidgets.QHBoxLayout()
        dist_layout.addWidget(QtWidgets.QLabel("Target Priority:"))
        self.aim_mode_distance_cb = QtWidgets.QComboBox()
        self.aim_mode_distance_cb.addItems(["Closest to Crosshair", "Largest Target"])
        self.aim_mode_distance_cb.setCurrentIndex(self.settings.get("aim_mode_distance", 1))
        self.aim_mode_distance_cb.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                border: 2px solid #ff69b4;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 13px;
                min-width: 140px;
                color: #ffffff;
                font-weight: bold;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #ff69b4;
                margin-right: 5px;
            }
            QComboBox:hover {
                border: 2px solid #ff8ac4;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #333333, stop:1 #2a2a2a);
            }
            QComboBox QAbstractItemView {
                background: #1e1e1e;
                color: #ffffff;
                border: 2px solid #ff69b4;
                border-radius: 8px;
                selection-background-color: #ff69b4;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 15px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #333333;
            }
        """)
        self.aim_mode_distance_cb.currentIndexChanged.connect(self.save_settings)
        dist_layout.addWidget(self.aim_mode_distance_cb)
        dist_layout.addStretch()
        aim_layout.addLayout(dist_layout)
        
        # FOV Slider
        fov_layout = QtWidgets.QVBoxLayout()
        fov_layout.addWidget(QtWidgets.QLabel("Aim FOV:"))
        self.fov_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.fov_slider.setMinimum(10)
        self.fov_slider.setMaximum(180)
        self.fov_slider.setValue(self.settings.get("aim_fov", 50))
        self.fov_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #333333;
                background: #1e1e1e;
                height: 12px;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: #ff69b4;
                border: 2px solid #ff69b4;
                width: 20px;
                margin: -4px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #ff8ac4;
                border: 2px solid #ff8ac4;
            }
            QSlider::sub-page:horizontal {
                background: #ff69b4;
                border-radius: 6px;
            }
        """)
        self.fov_slider.valueChanged.connect(self.save_settings)
        fov_layout.addWidget(self.fov_slider)
        aim_layout.addLayout(fov_layout)
        
        # Aimbot Smoothing Slider
        smoothing_layout = QtWidgets.QVBoxLayout()
        smoothing_layout.addWidget(QtWidgets.QLabel("Aimbot Smoothing:"))
        self.aim_smoothing_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.aim_smoothing_slider.setMinimum(1)
        self.aim_smoothing_slider.setMaximum(10)
        self.aim_smoothing_slider.setValue(int(self.settings.get("aim_smoothing", 0.3) * 10))
        self.aim_smoothing_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #333333;
                background: #1e1e1e;
                height: 12px;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: #ff69b4;
                border: 2px solid #ff69b4;
                width: 20px;
                margin: -4px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #ff8ac4;
                border: 2px solid #ff8ac4;
            }
            QSlider::sub-page:horizontal {
                background: #ff69b4;
                border-radius: 6px;
            }
        """)
        self.aim_smoothing_slider.valueChanged.connect(self.save_settings)
        smoothing_layout.addWidget(self.aim_smoothing_slider)
        aim_layout.addLayout(smoothing_layout)
        
        # Silent Aim Settings
        silent_group = QtWidgets.QGroupBox("🔇 SILENT AIM")
        silent_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #ffffff;
                border: 2px solid #ff69b4;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #ff69b4;
                background: #1e1e1e;
                border-radius: 6px;
                font-size: 14px;
                letter-spacing: 1px;
            }
        """)
        silent_layout = QtWidgets.QVBoxLayout(silent_group)
        
        # Enable Silent Aim
        self.silent_aim_cb = QtWidgets.QCheckBox("Enable Silent Aim")
        self.silent_aim_cb.setChecked(self.settings.get("silent_aim", 0) == 1)
        self.silent_aim_cb.stateChanged.connect(self.save_settings)
        self.silent_aim_cb.stateChanged.connect(self.update_toggle_style)
        silent_layout.addWidget(self.silent_aim_cb)
        
        # Silent Aim Key binding
        silent_key_layout = QtWidgets.QHBoxLayout()
        silent_key_layout.addWidget(QtWidgets.QLabel("Silent Aim Key:"))
        self.silent_aim_key_input = QtWidgets.QLineEdit()
        self.silent_aim_key_input.setText(self.settings.get("silent_aim_key", "SHIFT"))
        self.silent_aim_key_input.setReadOnly(True)
        self.silent_aim_key_input.mousePressEvent = lambda event: self.start_key_binding(self.silent_aim_key_input, "silent_aim_key")
        self.silent_aim_key_input.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                border: 2px solid #ff69b4;
                border-radius: 8px;
                color: #ffffff;
                cursor: pointer;
                padding: 10px 15px;
                font-size: 13px;
                font-weight: bold;
            }
            QLineEdit:hover {
                border-color: #ff8ac4;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #333333, stop:1 #2a2a2a);
            }
        """)
        self.silent_aim_key_input.setPlaceholderText("Click to set key...")
        silent_key_layout.addWidget(self.silent_aim_key_input)
        silent_key_layout.addStretch()
        silent_layout.addLayout(silent_key_layout)
        
        # Silent Aim FOV Slider
        silent_fov_layout = QtWidgets.QVBoxLayout()
        silent_fov_layout.addWidget(QtWidgets.QLabel("Silent Aim FOV:"))
        self.silent_aim_fov_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.silent_aim_fov_slider.setMinimum(10)
        self.silent_aim_fov_slider.setMaximum(90)
        self.silent_aim_fov_slider.setValue(self.settings.get("silent_aim_fov", 30))
        self.silent_aim_fov_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #333333;
                background: #1e1e1e;
                height: 12px;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: #ff69b4;
                border: 2px solid #ff69b4;
                width: 20px;
                margin: -4px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #ff8ac4;
                border: 2px solid #ff8ac4;
            }
            QSlider::sub-page:horizontal {
                background: #ff69b4;
                border-radius: 6px;
            }
        """)
        self.silent_aim_fov_slider.valueChanged.connect(self.save_settings)
        silent_fov_layout.addWidget(self.silent_aim_fov_slider)
        silent_layout.addLayout(silent_fov_layout)
        
        # Silent Aim Smoothing Slider
        silent_smooth_layout = QtWidgets.QVBoxLayout()
        silent_smooth_layout.addWidget(QtWidgets.QLabel("Silent Aim Smoothing:"))
        self.silent_aim_smoothing_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.silent_aim_smoothing_slider.setMinimum(1)
        self.silent_aim_smoothing_slider.setMaximum(10)
        self.silent_aim_smoothing_slider.setValue(int(self.settings.get("silent_aim_smoothing", 0.5) * 10))
        self.silent_aim_smoothing_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #333333;
                background: #1e1e1e;
                height: 12px;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: #ff69b4;
                border: 2px solid #ff69b4;
                width: 20px;
                margin: -4px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #ff8ac4;
                border: 2px solid #ff8ac4;
            }
            QSlider::sub-page:horizontal {
                background: #ff69b4;
                border-radius: 6px;
            }
        """)
        self.silent_aim_smoothing_slider.valueChanged.connect(self.save_settings)
        silent_smooth_layout.addWidget(self.silent_aim_smoothing_slider)
        silent_layout.addLayout(silent_smooth_layout)
        
        content_layout.addWidget(silent_group)
        
        # Recoil Control Settings
        recoil_group = QtWidgets.QGroupBox("🎯 RECOIL CONTROL")
        recoil_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #ffffff;
                border: 2px solid #ff69b4;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #ff69b4;
                background: #1e1e1e;
                border-radius: 6px;
                font-size: 14px;
                letter-spacing: 1px;
            }
        """)
        recoil_layout = QtWidgets.QVBoxLayout(recoil_group)
        
        # Enable Recoil Control
        self.recoil_control_cb = QtWidgets.QCheckBox("Enable Recoil Control")
        self.recoil_control_cb.setChecked(self.settings.get("recoil_control_enabled", 1) == 1)
        self.recoil_control_cb.stateChanged.connect(self.save_settings)
        self.recoil_control_cb.stateChanged.connect(self.update_toggle_style)
        recoil_layout.addWidget(self.recoil_control_cb)
        
        # Recoil Strength Slider
        recoil_strength_layout = QtWidgets.QVBoxLayout()
        recoil_strength_layout.addWidget(QtWidgets.QLabel("Recoil Control Strength:"))
        self.recoil_strength_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.recoil_strength_slider.setMinimum(0)
        self.recoil_strength_slider.setMaximum(100)
        self.recoil_strength_slider.setValue(self.settings.get("recoil_strength", 75))
        self.recoil_strength_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #333333;
                background: #1e1e1e;
                height: 12px;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: #ff69b4;
                border: 2px solid #ff69b4;
                width: 20px;
                margin: -4px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #ff8ac4;
                border: 2px solid #ff8ac4;
            }
            QSlider::sub-page:horizontal {
                background: #ff69b4;
                border-radius: 6px;
            }
        """)
        self.recoil_strength_slider.valueChanged.connect(self.save_settings)
        recoil_strength_layout.addWidget(self.recoil_strength_slider)
        recoil_layout.addLayout(recoil_strength_layout)
        
        # Recoil Smoothing Slider
        recoil_smoothing_layout = QtWidgets.QVBoxLayout()
        recoil_smoothing_layout.addWidget(QtWidgets.QLabel("Recoil Smoothing:"))
        self.recoil_smoothing_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.recoil_smoothing_slider.setMinimum(1)
        self.recoil_smoothing_slider.setMaximum(10)
        self.recoil_smoothing_slider.setValue(int(self.settings.get("recoil_smoothing", 0.8) * 10))
        self.recoil_smoothing_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #333333;
                background: #1e1e1e;
                height: 12px;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: #ff69b4;
                border: 2px solid #ff69b4;
                width: 20px;
                margin: -4px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #ff8ac4;
                border: 2px solid #ff8ac4;
            }
            QSlider::sub-page:horizontal {
                background: #ff69b4;
                border-radius: 6px;
            }
        """)
        self.recoil_smoothing_slider.valueChanged.connect(self.save_settings)
        recoil_smoothing_layout.addWidget(self.recoil_smoothing_slider)
        recoil_layout.addLayout(recoil_smoothing_layout)
        
        # Weapon-specific recoil patterns
        weapon_patterns_layout = QtWidgets.QVBoxLayout()
        weapon_patterns_layout.addWidget(QtWidgets.QLabel("Weapon Recoil Patterns:"))
        
        # AK47 Pattern
        ak47_layout = QtWidgets.QHBoxLayout()
        ak47_layout.addWidget(QtWidgets.QLabel("AK47:"))
        self.ak47_recoil_cb = QtWidgets.QComboBox()
        self.ak47_recoil_cb.addItems(["Pattern 1", "Pattern 2", "Pattern 3"])
        self.ak47_recoil_cb.setCurrentIndex(self.settings.get("ak47_recoil_pattern", 1) - 1)
        self.ak47_recoil_cb.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                border: 2px solid #ff69b4;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                min-width: 100px;
                color: #ffffff;
                font-weight: bold;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #ff69b4;
                margin-right: 5px;
            }
            QComboBox:hover {
                border: 2px solid #ff8ac4;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #333333, stop:1 #2a2a2a);
            }
            QComboBox QAbstractItemView {
                background: #1e1e1e;
                color: #ffffff;
                border: 2px solid #ff69b4;
                border-radius: 8px;
                selection-background-color: #ff69b4;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px 12px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #333333;
            }
        """)
        self.ak47_recoil_cb.currentIndexChanged.connect(self.save_settings)
        ak47_layout.addWidget(self.ak47_recoil_cb)
        ak47_layout.addStretch()
        weapon_patterns_layout.addLayout(ak47_layout)
        
        # M4 Pattern
        m4_layout = QtWidgets.QHBoxLayout()
        m4_layout.addWidget(QtWidgets.QLabel("M4:"))
        self.m4_recoil_cb = QtWidgets.QComboBox()
        self.m4_recoil_cb.addItems(["Pattern 1", "Pattern 2", "Pattern 3"])
        self.m4_recoil_cb.setCurrentIndex(self.settings.get("m4_recoil_pattern", 1) - 1)
        self.m4_recoil_cb.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                border: 2px solid #ff69b4;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                min-width: 100px;
                color: #ffffff;
                font-weight: bold;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #ff69b4;
                margin-right: 5px;
            }
            QComboBox:hover {
                border: 2px solid #ff8ac4;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #333333, stop:1 #2a2a2a);
            }
            QComboBox QAbstractItemView {
                background: #1e1e1e;
                color: #ffffff;
                border: 2px solid #ff69b4;
                border-radius: 8px;
                selection-background-color: #ff69b4;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px 12px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #333333;
            }
        """)
        self.m4_recoil_cb.currentIndexChanged.connect(self.save_settings)
        m4_layout.addWidget(self.m4_recoil_cb)
        m4_layout.addStretch()
        weapon_patterns_layout.addLayout(m4_layout)
        
        # M4A1 Pattern
        m4a1_layout = QtWidgets.QHBoxLayout()
        m4a1_layout.addWidget(QtWidgets.QLabel("M4A1:"))
        self.m4a1_recoil_cb = QtWidgets.QComboBox()
        self.m4a1_recoil_cb.addItems(["Pattern 1", "Pattern 2", "Pattern 3"])
        self.m4a1_recoil_cb.setCurrentIndex(self.settings.get("m4a1_recoil_pattern", 1) - 1)
        self.m4a1_recoil_cb.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                border: 2px solid #ff69b4;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                min-width: 100px;
                color: #ffffff;
                font-weight: bold;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #ff69b4;
                margin-right: 5px;
            }
            QComboBox:hover {
                border: 2px solid #ff8ac4;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #333333, stop:1 #2a2a2a);
            }
            QComboBox QAbstractItemView {
                background: #1e1e1e;
                color: #ffffff;
                border: 2px solid #ff69b4;
                border-radius: 8px;
                selection-background-color: #ff69b4;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px 12px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #333333;
            }
        """)
        self.m4a1_recoil_cb.currentIndexChanged.connect(self.save_settings)
        m4a1_layout.addWidget(self.m4a1_recoil_cb)
        m4a1_layout.addStretch()
        weapon_patterns_layout.addLayout(m4a1_layout)
        
        recoil_layout.addLayout(weapon_patterns_layout)
        content_layout.addWidget(recoil_group)
        
        content_layout.addWidget(aim_group)
        
        # Set up scroll area
        scroll_area.setWidget(content_container)
        layout.addWidget(scroll_area)
        page_widget.setLayout(layout)
        return page_widget

    def create_trigger_content(self):
        """Create the Triggerbot content page"""
        page_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Create scroll area for this page
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #1e1e1e;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #ff69b4;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #ff8ac4;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create content container
        content_container = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_container)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Triggerbot Settings
        trigger_group = QtWidgets.QGroupBox("⚡ TRIGGERBOT CONFIGURATION")
        trigger_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #ffffff;
                border: 2px solid #ff69b4;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #ff69b4;
                background: #1e1e1e;
                border-radius: 6px;
                font-size: 14px;
                letter-spacing: 1px;
            }
        """)
        trigger_layout = QtWidgets.QVBoxLayout(trigger_group)
        
        # Enable Triggerbot
        self.trigger_bot_active_cb = QtWidgets.QCheckBox("Enable Triggerbot")
        self.trigger_bot_active_cb.setChecked(self.settings.get("trigger_bot_active", 0) == 1)
        self.trigger_bot_active_cb.stateChanged.connect(self.save_settings)
        self.trigger_bot_active_cb.stateChanged.connect(self.update_toggle_style)
        trigger_layout.addWidget(self.trigger_bot_active_cb)
        
        # Key binding
        key_layout = QtWidgets.QHBoxLayout()
        key_layout.addWidget(QtWidgets.QLabel("Trigger Key:"))
        self.trigger_key_input = QtWidgets.QLineEdit()
        self.trigger_key_input.setText(self.settings.get("keyboards", "X"))
        self.trigger_key_input.setReadOnly(True)
        self.trigger_key_input.mousePressEvent = lambda event: self.start_key_binding(self.trigger_key_input, "keyboards")
        self.trigger_key_input.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2a2a2a, stop:1 #1e1e1e);
                border: 2px solid #ff69b4;
                border-radius: 8px;
                color: #ffffff;
                cursor: pointer;
                padding: 10px 15px;
                font-size: 13px;
                font-weight: bold;
            }
            QLineEdit:hover {
                border-color: #ff8ac4;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #333333, stop:1 #2a2a2a);
            }
        """)
        self.trigger_key_input.setPlaceholderText("Click to set key...")
        key_layout.addWidget(self.trigger_key_input)
        key_layout.addStretch()
        trigger_layout.addLayout(key_layout)
        
        # Hit chance slider
        hit_layout = QtWidgets.QVBoxLayout()
        hit_layout.addWidget(QtWidgets.QLabel("Hit Chance (%):"))
        self.hit_chance_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.hit_chance_slider.setMinimum(1)
        self.hit_chance_slider.setMaximum(100)
        self.hit_chance_slider.setValue(self.settings.get("trigger_hit_chance", 100))
        self.hit_chance_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #333333;
                background: #1e1e1e;
                height: 12px;
                border-radius: 6px;
            }
            QSlider::handle:horizontal {
                background: #ff69b4;
                border: 2px solid #ff69b4;
                width: 20px;
                margin: -4px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #ff8ac4;
                border: 2px solid #ff8ac4;
            }
            QSlider::sub-page:horizontal {
                background: #ff69b4;
                border-radius: 6px;
            }
        """)
        self.hit_chance_slider.valueChanged.connect(self.save_settings)
        hit_layout.addWidget(self.hit_chance_slider)
        trigger_layout.addLayout(hit_layout)
        
        content_layout.addWidget(trigger_group)
        
        # Set up scroll area
        scroll_area.setWidget(content_container)
        layout.addWidget(scroll_area)
        page_widget.setLayout(layout)
        return page_widget



    def create_left_container(self):
        left_container = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout()

        esp_container = self.create_esp_container()
        trigger_container = self.create_trigger_container()

        left_layout.addWidget(esp_container)
        left_layout.addItem(QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        left_layout.addWidget(trigger_container)

        left_container.setLayout(left_layout)
        return left_container

    def create_right_container(self):
        right_container = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout()

        aim_container = self.create_aim_container()
        right_layout.addWidget(aim_container)

        right_container.setLayout(right_layout)
        return right_container

    def create_esp_container(self):
        esp_container = QtWidgets.QWidget()
        esp_layout = QtWidgets.QVBoxLayout()

        esp_label = QtWidgets.QLabel("ESP Settings")
        esp_label.setAlignment(QtCore.Qt.AlignCenter)
        esp_layout.addWidget(esp_label)

        self.esp_rendering_cb = QtWidgets.QCheckBox("Enable ESP")
        self.esp_rendering_cb.setChecked(self.settings["esp_rendering"] == 1)
        self.esp_rendering_cb.stateChanged.connect(self.save_settings)
        self.esp_rendering_cb.stateChanged.connect(self.update_toggle_style)
        esp_layout.addWidget(self.esp_rendering_cb)

        self.esp_mode_cb = QtWidgets.QComboBox()
        self.esp_mode_cb.addItems(["Enemies Only", "All Players"])
        self.esp_mode_cb.setCurrentIndex(self.settings["esp_mode"])
        self.esp_mode_cb.setStyleSheet("background-color: #ffffff; border: 1px solid #ced4da; border-radius: 5px; color: #495057;")
        self.esp_mode_cb.currentIndexChanged.connect(self.save_settings)
        esp_layout.addWidget(self.esp_mode_cb)

        self.line_rendering_cb = QtWidgets.QCheckBox("Draw Lines")
        self.line_rendering_cb.setChecked(self.settings["line_rendering"] == 1)
        self.line_rendering_cb.stateChanged.connect(self.save_settings)
        self.line_rendering_cb.stateChanged.connect(self.update_toggle_style)
        esp_layout.addWidget(self.line_rendering_cb)

        self.hp_bar_rendering_cb = QtWidgets.QCheckBox("Draw HP Bars")
        self.hp_bar_rendering_cb.setChecked(self.settings["hp_bar_rendering"] == 1)
        self.hp_bar_rendering_cb.stateChanged.connect(self.save_settings)
        self.hp_bar_rendering_cb.stateChanged.connect(self.update_toggle_style)
        esp_layout.addWidget(self.hp_bar_rendering_cb)

        self.head_hitbox_rendering_cb = QtWidgets.QCheckBox("Draw Head Hitbox")
        self.head_hitbox_rendering_cb.setChecked(self.settings["head_hitbox_rendering"] == 1)
        self.head_hitbox_rendering_cb.stateChanged.connect(self.save_settings)
        self.head_hitbox_rendering_cb.stateChanged.connect(self.update_toggle_style)
        esp_layout.addWidget(self.head_hitbox_rendering_cb)

        self.bons_cb = QtWidgets.QCheckBox("Draw Bones")
        self.bons_cb.setChecked(self.settings["bons"] == 1)
        self.bons_cb.stateChanged.connect(self.save_settings)
        self.bons_cb.stateChanged.connect(self.update_toggle_style)
        esp_layout.addWidget(self.bons_cb)

        self.nickname_cb = QtWidgets.QCheckBox("Show Nickname")
        self.nickname_cb.setChecked(self.settings["nickname"] == 1)
        self.nickname_cb.stateChanged.connect(self.save_settings)
        self.nickname_cb.stateChanged.connect(self.update_toggle_style)
        esp_layout.addWidget(self.nickname_cb)

        self.weapon_cb = QtWidgets.QCheckBox("Show Weapon")
        self.weapon_cb.setChecked(self.settings["weapon"] == 1)
        self.weapon_cb.stateChanged.connect(self.save_settings)
        self.weapon_cb.stateChanged.connect(self.update_toggle_style)
        esp_layout.addWidget(self.weapon_cb)

        self.bomb_esp_cb = QtWidgets.QCheckBox("Bomb ESP")
        self.bomb_esp_cb.setChecked(self.settings["bomb_esp"] == 1)
        self.bomb_esp_cb.stateChanged.connect(self.save_settings)
        self.bomb_esp_cb.stateChanged.connect(self.update_toggle_style)
        esp_layout.addWidget(self.bomb_esp_cb)

        # Add color settings
        esp_layout.addWidget(QtWidgets.QLabel(""))
        color_label = QtWidgets.QLabel("ESP Color Settings")
        color_label.setAlignment(QtCore.Qt.AlignCenter)
        esp_layout.addWidget(color_label)

        # Box color
        esp_layout.addWidget(QtWidgets.QLabel("Box Color (R/G/B):"))
        box_color_layout = QtWidgets.QHBoxLayout()
        self.box_color_r = QtWidgets.QSpinBox()
        self.box_color_r.setRange(0, 255)
        self.box_color_r.setValue(self.settings.get("esp_box_color_r", 255))
        self.box_color_r.valueChanged.connect(self.save_settings)
        self.box_color_g = QtWidgets.QSpinBox()
        self.box_color_g.setRange(0, 255)
        self.box_color_g.setValue(self.settings.get("esp_box_color_g", 0))
        self.box_color_g.valueChanged.connect(self.save_settings)
        self.box_color_b = QtWidgets.QSpinBox()
        self.box_color_b.setRange(0, 255)
        self.box_color_b.setValue(self.settings.get("esp_box_color_b", 0))
        self.box_color_b.valueChanged.connect(self.save_settings)
        box_color_layout.addWidget(self.box_color_r)
        box_color_layout.addWidget(self.box_color_g)
        box_color_layout.addWidget(self.box_color_b)
        esp_layout.addLayout(box_color_layout)

        # Bone color
        esp_layout.addWidget(QtWidgets.QLabel("Bone Color (R/G/B):"))
        bone_color_layout = QtWidgets.QHBoxLayout()
        self.bone_color_r = QtWidgets.QSpinBox()
        self.bone_color_r.setRange(0, 255)
        self.bone_color_r.setValue(self.settings.get("esp_bone_color_r", 0))
        self.bone_color_r.valueChanged.connect(self.save_settings)
        self.bone_color_g = QtWidgets.QSpinBox()
        self.bone_color_g.setRange(0, 255)
        self.bone_color_g.setValue(self.settings.get("esp_bone_color_g", 255))
        self.bone_color_g.valueChanged.connect(self.save_settings)
        self.bone_color_b = QtWidgets.QSpinBox()
        self.bone_color_b.setRange(0, 255)
        self.bone_color_b.setValue(self.settings.get("esp_bone_color_b", 0))
        self.bone_color_b.valueChanged.connect(self.save_settings)
        bone_color_layout.addWidget(self.bone_color_r)
        bone_color_layout.addWidget(self.bone_color_g)
        bone_color_layout.addWidget(self.bone_color_b)
        esp_layout.addLayout(bone_color_layout)

        # Health color
        esp_layout.addWidget(QtWidgets.QLabel("Health Color (R/G/B):"))
        health_color_layout = QtWidgets.QHBoxLayout()
        self.health_color_r = QtWidgets.QSpinBox()
        self.health_color_r.setRange(0, 255)
        self.health_color_r.setValue(self.settings.get("esp_health_color_r", 0))
        self.health_color_r.valueChanged.connect(self.save_settings)
        self.health_color_g = QtWidgets.QSpinBox()
        self.health_color_g.setRange(0, 255)
        self.health_color_g.setValue(self.settings.get("esp_health_color_g", 0))
        self.health_color_g.valueChanged.connect(self.save_settings)
        self.health_color_b = QtWidgets.QSpinBox()
        self.health_color_b.setRange(0, 255)
        self.health_color_b.setValue(self.settings.get("esp_health_color_b", 255))
        self.health_color_b.valueChanged.connect(self.save_settings)
        health_color_layout.addWidget(self.health_color_r)
        health_color_layout.addWidget(self.health_color_g)
        health_color_layout.addWidget(self.health_color_b)
        esp_layout.addLayout(health_color_layout)

        # Head color
        esp_layout.addWidget(QtWidgets.QLabel("Head Color (R/G/B):"))
        head_color_layout = QtWidgets.QHBoxLayout()
        self.head_color_r = QtWidgets.QSpinBox()
        self.head_color_r.setRange(0, 255)
        self.head_color_r.setValue(self.settings.get("esp_head_color_r", 255))
        self.head_color_r.valueChanged.connect(self.save_settings)
        self.head_color_g = QtWidgets.QSpinBox()
        self.head_color_g.setRange(0, 255)
        self.head_color_g.setValue(self.settings.get("esp_head_color_g", 255))
        self.head_color_g.valueChanged.connect(self.save_settings)
        self.head_color_b = QtWidgets.QSpinBox()
        self.head_color_b.setRange(0, 255)
        self.head_color_b.setValue(self.settings.get("esp_head_color_b", 0))
        self.head_color_b.valueChanged.connect(self.save_settings)
        head_color_layout.addWidget(self.head_color_r)
        head_color_layout.addWidget(self.head_color_g)
        head_color_layout.addWidget(self.head_color_b)
        esp_layout.addLayout(head_color_layout)

        # Name color
        esp_layout.addWidget(QtWidgets.QLabel("Name Color (R/G/B):"))
        name_color_layout = QtWidgets.QHBoxLayout()
        self.name_color_r = QtWidgets.QSpinBox()
        self.name_color_r.setRange(0, 255)
        self.name_color_r.setValue(self.settings.get("esp_name_color_r", 255))
        self.name_color_r.valueChanged.connect(self.save_settings)
        self.name_color_g = QtWidgets.QSpinBox()
        self.name_color_g.setRange(0, 255)
        self.name_color_g.setValue(self.settings.get("esp_name_color_g", 255))
        self.name_color_g.valueChanged.connect(self.save_settings)
        self.name_color_b = QtWidgets.QSpinBox()
        self.name_color_b.setRange(0, 255)
        self.name_color_b.setValue(self.settings.get("esp_name_color_b", 255))
        self.name_color_b.valueChanged.connect(self.save_settings)
        name_color_layout.addWidget(self.name_color_r)
        name_color_layout.addWidget(self.name_color_g)
        name_color_layout.addWidget(self.name_color_b)
        esp_layout.addLayout(name_color_layout)

        # Weapon color
        esp_layout.addWidget(QtWidgets.QLabel("Weapon Color (R/G/B):"))
        weapon_color_layout = QtWidgets.QHBoxLayout()
        self.weapon_color_r = QtWidgets.QSpinBox()
        self.weapon_color_r.setRange(0, 255)
        self.weapon_color_r.setValue(self.settings.get("esp_weapon_color_r", 255))
        self.weapon_color_r.valueChanged.connect(self.save_settings)
        self.weapon_color_g = QtWidgets.QSpinBox()
        self.weapon_color_g.setRange(0, 255)
        self.weapon_color_g.setValue(self.settings.get("esp_weapon_color_g", 0))
        self.weapon_color_g.valueChanged.connect(self.save_settings)
        self.weapon_color_b = QtWidgets.QSpinBox()
        self.weapon_color_b.setRange(0, 255)
        self.weapon_color_b.setValue(self.settings.get("esp_weapon_color_b", 255))
        self.weapon_color_b.valueChanged.connect(self.save_settings)
        weapon_color_layout.addWidget(self.weapon_color_r)
        weapon_color_layout.addWidget(self.weapon_color_g)
        weapon_color_layout.addWidget(self.weapon_color_b)
        esp_layout.addLayout(weapon_color_layout)

        esp_container.setLayout(esp_layout)
        esp_container.setStyleSheet("background-color: #f8f9fa; border-radius: 10px; border: 1px solid #dee2e6;")
        return esp_container

    def create_trigger_container(self):
        trigger_container = QtWidgets.QWidget()
        trigger_layout = QtWidgets.QVBoxLayout()

        trigger_label = QtWidgets.QLabel("Trigger Bot Settings")
        trigger_label.setAlignment(QtCore.Qt.AlignCenter)
        trigger_layout.addWidget(trigger_label)

        self.trigger_bot_active_cb = QtWidgets.QCheckBox("Enable Trigger Bot")
        self.trigger_bot_active_cb.setChecked(self.settings["trigger_bot_active"] == 1)
        self.trigger_bot_active_cb.stateChanged.connect(self.save_settings)
        self.trigger_bot_active_cb.stateChanged.connect(self.update_toggle_style)
        trigger_layout.addWidget(self.trigger_bot_active_cb)

        self.trigger_key_input = QtWidgets.QLineEdit()
        self.trigger_key_input.setText(self.settings["keyboards"])
        self.trigger_key_input.setReadOnly(True)
        self.trigger_key_input.mousePressEvent = lambda event: self.start_key_binding(self.trigger_key_input, "keyboards")
        trigger_layout.addWidget(QtWidgets.QLabel("Trigger Key:"))
        trigger_layout.addWidget(self.trigger_key_input)
        self.trigger_key_input.setStyleSheet("background-color: #ffffff; border: 1px solid #ced4da; border-radius: 5px; color: #495057; cursor: pointer;")
        self.trigger_key_input.setPlaceholderText("Click to set key...")

        # Add hit chance slider
        trigger_layout.addWidget(QtWidgets.QLabel("Hit Chance (%):"))
        self.hit_chance_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.hit_chance_slider.setMinimum(1)
        self.hit_chance_slider.setMaximum(100)
        self.hit_chance_slider.setValue(self.settings.get("trigger_hit_chance", 100))
        self.hit_chance_slider.valueChanged.connect(self.save_settings)
        trigger_layout.addWidget(self.hit_chance_slider)

        # Add bhop section
        trigger_layout.addWidget(QtWidgets.QLabel(""))
        bhop_label = QtWidgets.QLabel("Bunny Hop Settings")
        bhop_label.setAlignment(QtCore.Qt.AlignCenter)
        trigger_layout.addWidget(bhop_label)

        self.bhop_active_cb = QtWidgets.QCheckBox("Enable Bunny Hop")
        self.bhop_active_cb.setChecked(self.settings.get("bhop_active", 0) == 1)
        self.bhop_active_cb.stateChanged.connect(self.save_settings)
        self.bhop_active_cb.stateChanged.connect(self.update_toggle_style)
        trigger_layout.addWidget(self.bhop_active_cb)

        self.bhop_key_input = QtWidgets.QLineEdit()
        self.bhop_key_input.setText(self.settings.get("bhop_key", "SPACE"))
        self.bhop_key_input.setReadOnly(True)
        self.bhop_key_input.mousePressEvent = lambda event: self.start_key_binding(self.bhop_key_input, "bhop_key")
        trigger_layout.addWidget(QtWidgets.QLabel("Bhop Key:"))
        trigger_layout.addWidget(self.bhop_key_input)
        self.bhop_key_input.setStyleSheet("background-color: #ffffff; border: 1px solid #ced4da; border-radius: 5px; color: #495057; cursor: pointer;")
        self.bhop_key_input.setPlaceholderText("Click to set key...")

        trigger_container.setLayout(trigger_layout)
        trigger_container.setStyleSheet("background-color: #f8f9fa; border-radius: 10px; border: 1px solid #dee2e6;")
        return trigger_container

    def create_aim_container(self):
        aim_container = QtWidgets.QWidget()
        aim_layout = QtWidgets.QVBoxLayout()

        aim_label = QtWidgets.QLabel("Aim Settings")
        aim_label.setAlignment(QtCore.Qt.AlignCenter)
        aim_layout.addWidget(aim_label)

        self.aim_active_cb = QtWidgets.QCheckBox("Enable Aim")
        self.aim_active_cb.setChecked(self.settings["aim_active"] == 1)
        self.aim_active_cb.stateChanged.connect(self.save_settings)
        self.aim_active_cb.stateChanged.connect(self.update_toggle_style)
        aim_layout.addWidget(self.aim_active_cb)

        self.radius_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.radius_slider.setMinimum(0)
        self.radius_slider.setMaximum(100)
        self.radius_slider.setValue(self.settings["radius"])
        self.radius_slider.valueChanged.connect(self.save_settings)
        aim_layout.addWidget(QtWidgets.QLabel("Aim Radius:"))
        aim_layout.addWidget(self.radius_slider)

        # Add FOV slider
        aim_layout.addWidget(QtWidgets.QLabel("Aim FOV:"))
        self.fov_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.fov_slider.setMinimum(10)
        self.fov_slider.setMaximum(180)
        self.fov_slider.setValue(self.settings.get("aim_fov", 50))
        self.fov_slider.valueChanged.connect(self.save_settings)
        aim_layout.addWidget(self.fov_slider)

        self.keyboard_input = QtWidgets.QLineEdit()
        self.keyboard_input.setText(self.settings["keyboard"])
        self.keyboard_input.setReadOnly(True)
        self.keyboard_input.mousePressEvent = lambda event: self.start_key_binding(self.keyboard_input, "keyboard")
        aim_layout.addWidget(QtWidgets.QLabel("Aim Key:"))
        aim_layout.addWidget(self.keyboard_input)
        self.keyboard_input.setStyleSheet("background-color: #ffffff; border: 1px solid #ced4da; border-radius: 5px; color: #495057; cursor: pointer;")
        self.keyboard_input.setPlaceholderText("Click to set key...")

        self.aim_mode_cb = QtWidgets.QComboBox()
        self.aim_mode_cb.addItems(["Body", "Head"])
        self.aim_mode_cb.setCurrentIndex(self.settings["aim_mode"])
        self.aim_mode_cb.setStyleSheet("background-color: #ffffff; border: 1px solid #ced4da; border-radius: 5px; color: #495057;")
        self.aim_mode_cb.currentIndexChanged.connect(self.save_settings)
        aim_layout.addWidget(QtWidgets.QLabel("Aim Mode:"))
        aim_layout.addWidget(self.aim_mode_cb)

        self.aim_mode_distance_cb = QtWidgets.QComboBox()
        self.aim_mode_distance_cb.addItems(["Closest to Crosshair", "Closest in 3D"])
        self.aim_mode_distance_cb.setCurrentIndex(self.settings["aim_mode_distance"])
        self.aim_mode_distance_cb.setStyleSheet("background-color: #ffffff; border: 1px solid #ced4da; border-radius: 5px; color: #495057;")
        self.aim_mode_distance_cb.currentIndexChanged.connect(self.save_settings)
        aim_layout.addWidget(QtWidgets.QLabel("Aim Distance Mode:"))
        aim_layout.addWidget(self.aim_mode_distance_cb)

        aim_container.setLayout(aim_layout)
        aim_container.setStyleSheet("background-color: #f8f9fa; border-radius: 10px; border: 1px solid #dee2e6;")
        return aim_container

    def save_settings(self):
        try:
            # ESP Settings
            if hasattr(self, 'esp_rendering_cb'):
                esp_state = 1 if self.esp_rendering_cb.isChecked() else 0
                self.settings["esp_rendering"] = esp_state
                print(f"ESP Rendering: {esp_state}")
            if hasattr(self, 'esp_mode_cb'):
                self.settings["esp_mode"] = self.esp_mode_cb.currentIndex()
            if hasattr(self, 'line_rendering_cb'):
                line_state = 1 if self.line_rendering_cb.isChecked() else 0
                self.settings["line_rendering"] = line_state
                print(f"Line Rendering: {line_state}")
            if hasattr(self, 'hp_bar_rendering_cb'):
                hp_state = 1 if self.hp_bar_rendering_cb.isChecked() else 0
                self.settings["hp_bar_rendering"] = hp_state
                print(f"HP Bar Rendering: {hp_state}")
            if hasattr(self, 'head_hitbox_rendering_cb'):
                head_state = 1 if self.head_hitbox_rendering_cb.isChecked() else 0
                self.settings["head_hitbox_rendering"] = head_state
                print(f"Head Hitbox Rendering: {head_state}")
            if hasattr(self, 'bons_cb'):
                bone_state = 1 if self.bons_cb.isChecked() else 0
                self.settings["bons"] = bone_state
                print(f"Bone ESP: {bone_state}")
            if hasattr(self, 'nickname_cb'):
                name_state = 1 if self.nickname_cb.isChecked() else 0
                self.settings["nickname"] = name_state
                print(f"Nickname: {name_state}")
            if hasattr(self, 'weapon_cb'):
                weapon_state = 1 if self.weapon_cb.isChecked() else 0
                self.settings["weapon"] = weapon_state
                print(f"Weapon: {weapon_state}")
            if hasattr(self, 'bomb_esp_cb'):
                bomb_state = 1 if self.bomb_esp_cb.isChecked() else 0
                self.settings["bomb_esp"] = bomb_state
                print(f"Bomb ESP: {bomb_state}")
            if hasattr(self, 'sniper_crosshair_cb'):
                crosshair_state = 1 if self.sniper_crosshair_cb.isChecked() else 0
                self.settings["sniper_crosshair"] = crosshair_state
                print(f"Sniper Crosshair: {crosshair_state}")
            
            # Aimbot Settings
            if hasattr(self, 'aim_active_cb'):
                self.settings["aim_active"] = 1 if self.aim_active_cb.isChecked() else 0
            if hasattr(self, 'fov_slider'):
                self.settings["aim_fov"] = self.fov_slider.value()
            if hasattr(self, 'keyboard_input'):
                self.settings["keyboard"] = self.keyboard_input.text()
            if hasattr(self, 'aim_mode_cb'):
                self.settings["aim_mode"] = self.aim_mode_cb.currentIndex()
            if hasattr(self, 'aim_mode_distance_cb'):
                self.settings["aim_mode_distance"] = self.aim_mode_distance_cb.currentIndex()
            if hasattr(self, 'aim_smoothing_slider'):
                self.settings["aim_smoothing"] = self.aim_smoothing_slider.value() / 10.0
            
            # New Targeting Settings
            if hasattr(self, 'aim_target_mode_cb'):
                target_modes = ["head", "neck", "chest", "legs", "center", "upper_body"]
                self.settings["aim_target_mode"] = target_modes[self.aim_target_mode_cb.currentIndex()]
            if hasattr(self, 'head_offset_slider'):
                self.settings["head_offset"] = self.head_offset_slider.value()
            if hasattr(self, 'head_precision_slider'):
                self.settings["head_precision"] = self.head_precision_slider.value()
            if hasattr(self, 'neck_offset_slider'):
                self.settings["neck_offset"] = self.neck_offset_slider.value()
            
            # Recoil Control Settings
            if hasattr(self, 'recoil_control_cb'):
                self.settings["recoil_control_enabled"] = 1 if self.recoil_control_cb.isChecked() else 0
            if hasattr(self, 'recoil_strength_slider'):
                self.settings["recoil_strength"] = self.recoil_strength_slider.value()
            if hasattr(self, 'recoil_smoothing_slider'):
                self.settings["recoil_smoothing"] = self.recoil_smoothing_slider.value() / 10.0
            if hasattr(self, 'ak47_recoil_cb'):
                self.settings["ak47_recoil_pattern"] = self.ak47_recoil_cb.currentIndex() + 1
            if hasattr(self, 'm4_recoil_cb'):
                self.settings["m4_recoil_pattern"] = self.m4_recoil_cb.currentIndex() + 1
            if hasattr(self, 'm4a1_recoil_cb'):
                self.settings["m4a1_recoil_pattern"] = self.m4a1_recoil_cb.currentIndex() + 1
            
            # Silent Aim Settings
            if hasattr(self, 'silent_aim_cb'):
                self.settings["silent_aim"] = 1 if self.silent_aim_cb.isChecked() else 0
            if hasattr(self, 'silent_aim_key_input'):
                self.settings["silent_aim_key"] = self.silent_aim_key_input.text()
            if hasattr(self, 'silent_aim_fov_slider'):
                self.settings["silent_aim_fov"] = self.silent_aim_fov_slider.value()
            if hasattr(self, 'silent_aim_smoothing_slider'):
                self.settings["silent_aim_smoothing"] = self.silent_aim_smoothing_slider.value() / 10.0
            
            # Triggerbot Settings
            if hasattr(self, 'trigger_bot_active_cb'):
                self.settings["trigger_bot_active"] = 1 if self.trigger_bot_active_cb.isChecked() else 0
            if hasattr(self, 'trigger_key_input'):
                self.settings["keyboards"] = self.trigger_key_input.text()
            if hasattr(self, 'hit_chance_slider'):
                self.settings["trigger_hit_chance"] = self.hit_chance_slider.value()
            
            # Color Settings
            if hasattr(self, 'box_color_r'):
                self.settings["esp_box_color_r"] = self.box_color_r.value()
            if hasattr(self, 'box_color_g'):
                self.settings["esp_box_color_g"] = self.box_color_g.value()
            if hasattr(self, 'box_color_b'):
                self.settings["esp_box_color_b"] = self.box_color_b.value()
            if hasattr(self, 'bone_color_r'):
                self.settings["esp_bone_color_r"] = self.bone_color_r.value()
            if hasattr(self, 'bone_color_g'):
                self.settings["esp_bone_color_g"] = self.bone_color_g.value()
            if hasattr(self, 'bone_color_b'):
                self.settings["esp_bone_color_b"] = self.bone_color_b.value()
            if hasattr(self, 'health_color_r'):
                self.settings["esp_health_color_r"] = self.health_color_r.value()
            if hasattr(self, 'health_color_g'):
                self.settings["esp_health_color_g"] = self.health_color_g.value()
            if hasattr(self, 'health_color_b'):
                self.settings["esp_health_color_b"] = self.health_color_b.value()
            if hasattr(self, 'head_color_r'):
                self.settings["esp_head_color_r"] = self.head_color_r.value()
            if hasattr(self, 'head_color_g'):
                self.settings["esp_head_color_g"] = self.head_color_g.value()
            if hasattr(self, 'head_color_b'):
                self.settings["esp_head_color_b"] = self.head_color_b.value()
            if hasattr(self, 'name_color_r'):
                self.settings["esp_name_color_r"] = self.name_color_r.value()
            if hasattr(self, 'name_color_g'):
                self.settings["esp_name_color_g"] = self.name_color_g.value()
            if hasattr(self, 'name_color_b'):
                self.settings["esp_name_color_b"] = self.name_color_b.value()
            if hasattr(self, 'weapon_color_r'):
                self.settings["esp_weapon_color_r"] = self.weapon_color_r.value()
            if hasattr(self, 'weapon_color_g'):
                self.settings["esp_weapon_color_g"] = self.weapon_color_g.value()
            if hasattr(self, 'weapon_color_b'):
                self.settings["esp_weapon_color_b"] = self.weapon_color_b.value()
            
            save_settings(self.settings)
            print("Settings saved successfully")
        except Exception as e:
            print(f"Error saving settings: {e}")

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = True
            self.drag_start_position = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self.is_dragging:
            delta = event.globalPosition().toPoint() - self.drag_start_position
            self.move(self.pos() + delta)
            self.drag_start_position = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_dragging = False

    def focusInEvent(self, event):
        """Handle focus in events"""
        super().focusInEvent(event)
        print("Window gained focus")

    def focusOutEvent(self, event):
        """Handle focus out events"""
        super().focusOutEvent(event)
        print("Window lost focus")

    def start_key_binding(self, input_field, setting_key):
        """Start listening for a key press to set as binding"""
        input_field.setText("Press any key...")
        input_field.setStyleSheet("background-color: #e3f2fd; border: 2px solid #2196f3; border-radius: 5px; color: #1976d2; cursor: pointer;")
        self.current_key_binding = (input_field, setting_key)
        self.setFocus()  # Ensure window has focus
        self.grabKeyboard()
        print(f"Waiting for key press for {setting_key}...")

    def check_key_binding(self):
        """Check for key presses using win32api as fallback"""
        if hasattr(self, 'current_key_binding') and self.current_key_binding:
            input_field, setting_key = self.current_key_binding
            
            # Check for common keys
            for key_code in range(65, 91):  # A-Z
                if win32api.GetAsyncKeyState(key_code) & 0x8000:
                    key_name = chr(key_code)
                    self.set_key_binding(input_field, setting_key, key_name)
                    return
            
            # Check for numbers
            for key_code in range(48, 58):  # 0-9
                if win32api.GetAsyncKeyState(key_code) & 0x8000:
                    key_name = chr(key_code)
                    self.set_key_binding(input_field, setting_key, key_name)
                    return
            
            # Check for special keys
            special_keys = {
                win32con.VK_SPACE: "SPACE",
                win32con.VK_TAB: "TAB",
                win32con.VK_RETURN: "ENTER",
                win32con.VK_SHIFT: "SHIFT",
                win32con.VK_CONTROL: "CTRL",
                win32con.VK_MENU: "ALT",
                win32con.VK_ESCAPE: "ESC",
                win32con.VK_BACK: "BACKSPACE",
                win32con.VK_DELETE: "DELETE",
                win32con.VK_INSERT: "INSERT",
                win32con.VK_HOME: "HOME",
                win32con.VK_END: "END",
                win32con.VK_PRIOR: "PAGEUP",
                win32con.VK_NEXT: "PAGEDOWN",
                win32con.VK_LEFT: "LEFT",
                win32con.VK_RIGHT: "RIGHT",
                win32con.VK_UP: "UP",
                win32con.VK_DOWN: "DOWN",
                win32con.VK_LBUTTON: "MOUSE1",
                win32con.VK_RBUTTON: "MOUSE2",
                win32con.VK_MBUTTON: "MOUSE3",
                win32con.VK_XBUTTON1: "MOUSE4",
                win32con.VK_XBUTTON2: "MOUSE5"
            }
            
            for key_code, key_name in special_keys.items():
                if win32api.GetAsyncKeyState(key_code) & 0x8000:
                    self.set_key_binding(input_field, setting_key, key_name)
                    return

    def set_key_binding(self, input_field, setting_key, key_name):
        """Set the key binding and update the UI"""
        print(f"Setting key binding: {setting_key} = {key_name}")
        input_field.setText(key_name)
        input_field.setStyleSheet("background-color: #ffffff; border: 1px solid #ced4da; border-radius: 5px; color: #495057; cursor: pointer;")
        
        # Update the setting
        self.settings[setting_key] = key_name
        save_settings(self.settings)
        
        # Clear the current binding
        self.current_key_binding = None
        self.releaseKeyboard()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        """Handle key press events for key binding"""
        print(f"Key pressed: {event.key()}")
        if hasattr(self, 'current_key_binding') and self.current_key_binding:
            input_field, setting_key = self.current_key_binding
            print(f"Processing key binding for {setting_key}")
            
            # Check for escape key to cancel
            if event.key() == QtCore.Qt.Key_Escape:
                print("Escape pressed, canceling key binding")
                input_field.setText(self.settings.get(setting_key, ""))
                input_field.setStyleSheet("background-color: #ffffff; border: 1px solid #ced4da; border-radius: 5px; color: #495057; cursor: pointer;")
                self.current_key_binding = None
                self.releaseKeyboard()
                return
            
            # Get the key name
            key_name = self.get_key_name(event.key())
            print(f"Key name: {key_name}")
            
            if key_name:
                # Update the input field
                input_field.setText(key_name)
                input_field.setStyleSheet("background-color: #ffffff; border: 1px solid #ced4da; border-radius: 5px; color: #495057; cursor: pointer;")
                
                # Update the setting
                self.settings[setting_key] = key_name
                save_settings(self.settings)
                print(f"Key binding set: {setting_key} = {key_name}")
                
                # Clear the current binding
                self.current_key_binding = None
                self.releaseKeyboard()
            else:
                # Invalid key, reset the field
                print("Invalid key pressed")
                input_field.setText(self.settings.get(setting_key, ""))
                input_field.setStyleSheet("background-color: #ffffff; border: 1px solid #ced4da; border-radius: 5px; color: #495057; cursor: pointer;")
                self.current_key_binding = None
                self.releaseKeyboard()
        else:
            print("No current key binding active")
            super().keyPressEvent(event)

    def get_key_name(self, key_code):
        """Convert key code to readable key name"""
        key_mapping = {
            QtCore.Qt.Key_A: "A", QtCore.Qt.Key_B: "B", QtCore.Qt.Key_C: "C", QtCore.Qt.Key_D: "D",
            QtCore.Qt.Key_E: "E", QtCore.Qt.Key_F: "F", QtCore.Qt.Key_G: "G", QtCore.Qt.Key_H: "H",
            QtCore.Qt.Key_I: "I", QtCore.Qt.Key_J: "J", QtCore.Qt.Key_K: "K", QtCore.Qt.Key_L: "L",
            QtCore.Qt.Key_M: "M", QtCore.Qt.Key_N: "N", QtCore.Qt.Key_O: "O", QtCore.Qt.Key_P: "P",
            QtCore.Qt.Key_Q: "Q", QtCore.Qt.Key_R: "R", QtCore.Qt.Key_S: "S", QtCore.Qt.Key_T: "T",
            QtCore.Qt.Key_U: "U", QtCore.Qt.Key_V: "V", QtCore.Qt.Key_W: "W", QtCore.Qt.Key_X: "X",
            QtCore.Qt.Key_Y: "Y", QtCore.Qt.Key_Z: "Z",
            QtCore.Qt.Key_0: "0", QtCore.Qt.Key_1: "1", QtCore.Qt.Key_2: "2", QtCore.Qt.Key_3: "3",
            QtCore.Qt.Key_4: "4", QtCore.Qt.Key_5: "5", QtCore.Qt.Key_6: "6", QtCore.Qt.Key_7: "7",
            QtCore.Qt.Key_8: "8", QtCore.Qt.Key_9: "9",
            QtCore.Qt.Key_F1: "F1", QtCore.Qt.Key_F2: "F2", QtCore.Qt.Key_F3: "F3", QtCore.Qt.Key_F4: "F4",
            QtCore.Qt.Key_F5: "F5", QtCore.Qt.Key_F6: "F6", QtCore.Qt.Key_F7: "F7", QtCore.Qt.Key_F8: "F8",
            QtCore.Qt.Key_F9: "F9", QtCore.Qt.Key_F10: "F10", QtCore.Qt.Key_F11: "F11", QtCore.Qt.Key_F12: "F12",
            QtCore.Qt.Key_Space: "SPACE", QtCore.Qt.Key_Tab: "TAB", QtCore.Qt.Key_Return: "ENTER",
            QtCore.Qt.Key_Shift: "SHIFT", QtCore.Qt.Key_Control: "CTRL", QtCore.Qt.Key_Alt: "ALT",
            QtCore.Qt.Key_Escape: "ESC", QtCore.Qt.Key_Backspace: "BACKSPACE", QtCore.Qt.Key_Delete: "DELETE",
            QtCore.Qt.Key_Insert: "INSERT", QtCore.Qt.Key_Home: "HOME", QtCore.Qt.Key_End: "END",
            QtCore.Qt.Key_PageUp: "PAGEUP", QtCore.Qt.Key_PageDown: "PAGEDOWN",
            QtCore.Qt.Key_Left: "LEFT", QtCore.Qt.Key_Right: "RIGHT", QtCore.Qt.Key_Up: "UP", QtCore.Qt.Key_Down: "DOWN",
            QtCore.Qt.Key_Minus: "-", QtCore.Qt.Key_Equal: "=", QtCore.Qt.Key_BracketLeft: "[", QtCore.Qt.Key_BracketRight: "]",
            QtCore.Qt.Key_Semicolon: ";", QtCore.Qt.Key_QuoteLeft: "'", QtCore.Qt.Key_Comma: ",", QtCore.Qt.Key_Period: ".",
            QtCore.Qt.Key_Slash: "/", QtCore.Qt.Key_Backslash: "\\", QtCore.Qt.Key_Backtick: "`",
            QtCore.Qt.Key_Button1: "MOUSE1", QtCore.Qt.Key_Button2: "MOUSE2", QtCore.Qt.Key_Button3: "MOUSE3",
            QtCore.Qt.Key_Button4: "MOUSE4", QtCore.Qt.Key_Button5: "MOUSE5"
        }
        
        return key_mapping.get(key_code, None)

    def update_toggle_style(self):
        """Update the visual style of all toggle buttons"""
        checkboxes = [
            self.esp_rendering_cb, self.line_rendering_cb, self.hp_bar_rendering_cb,
            self.head_hitbox_rendering_cb, self.bons_cb, self.nickname_cb, self.weapon_cb,
            self.bomb_esp_cb, self.sniper_crosshair_cb, self.trigger_bot_active_cb, self.aim_active_cb, self.silent_aim_cb
        ]
        
        for checkbox in checkboxes:
            if checkbox.isChecked():
                checkbox.setStyleSheet("""
                    QCheckBox {
                        color: #ffffff;
                        font-weight: bold;
                        padding: 8px 12px;
                        border-radius: 8px;
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #ff69b4, stop:1 #e91e63);
                        border: 1px solid #ff69b4;
                        margin: 3px;
                        font-size: 13px;
                        letter-spacing: 0.5px;
                    }
                    QCheckBox::indicator {
                        width: 16px;
                        height: 16px;
                        border-radius: 8px;
                        background-color: #ffffff;
                        border: 2px solid #ff69b4;
                        margin-right: 10px;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #ff69b4;
                        border: 2px solid #ffffff;
                        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTIgNkw1IDlMMTAgNCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
                    }
                """)
            else:
                checkbox.setStyleSheet("""
                    QCheckBox {
                        color: #888888;
                        font-weight: normal;
                        padding: 8px 12px;
                        border-radius: 8px;
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #2a2a2a, stop:1 #1e1e1e);
                        border: 1px solid #333333;
                        margin: 3px;
                        font-size: 13px;
                        letter-spacing: 0.5px;
                    }
                    QCheckBox::indicator {
                        width: 16px;
                        height: 16px;
                        border-radius: 8px;
                        background-color: #2a2a2a;
                        border: 2px solid #444444;
                        margin-right: 10px;
                    }
                    QCheckBox::indicator:unchecked {
                        background-color: #2a2a2a;
                        border: 2px solid #444444;
                    }
                    QCheckBox:hover {
                        color: #ffffff;
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #333333, stop:1 #2a2a2a);
                        border: 1px solid #555555;
                    }
                """)

def configurator():
    app = QtWidgets.QApplication(sys.argv)
    apply_stylesheet(app, theme='light_blue.xml')
    window = ConfigWindow()
    window.show()
    
    # Check for kill switch periodically
    def check_kill_switch():
        global kill_switch_active
        if kill_switch_active:
            app.quit()
            return
        QtCore.QTimer.singleShot(100, check_kill_switch)
    
    check_kill_switch()
    sys.exit(app.exec())

# ESP
class ESPWindow(QtWidgets.QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setWindowTitle('ESP Overlay')
        
        # Wait for CS2 window to be available
        while True:
            self.window_width, self.window_height = get_window_size("Counter-Strike 2")
            if self.window_width is not None and self.window_height is not None:
                break
            time.sleep(1)
            print("Waiting for CS2 window...")
        
        self.setGeometry(0, 0, self.window_width, self.window_height)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        hwnd = self.winId()
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

        self.file_watcher = QFileSystemWatcher([CONFIG_FILE])
        self.file_watcher.fileChanged.connect(self.reload_settings)

        # Initialize offsets and memory access
        self.offsets, self.client_dll = get_offsets_and_client_dll()
        if not self.offsets or not self.client_dll:
            print("Failed to get offsets, retrying...")
            time.sleep(2)
            self.offsets, self.client_dll = get_offsets_and_client_dll()
        
        # Wait for CS2 process
        while True:
            try:
                self.pm = pymem.Pymem("cs2.exe")
                self.client = pymem.process.module_from_name(self.pm.process_handle, "client.dll").lpBaseOfDll
                break
            except Exception as e:
                print(f"Waiting for CS2 process: {e}")
                time.sleep(1)

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(0, 0, self.window_width, self.window_height)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.view.setStyleSheet("background: transparent;")
        self.view.setSceneRect(0, 0, self.window_width, self.window_height)
        self.view.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(0)  # Update as fast as possible

        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0

    def reload_settings(self):
        self.settings = load_settings()
        self.window_width, self.window_height = get_window_size("Counter-Strike 2")
        if self.window_width is None or self.window_height is None:
            print("Ошибка: окно игры не найдено.")
            sys.exit(1)
        self.setGeometry(0, 0, self.window_width, self.window_height)
        self.update_scene()

    def update_scene(self):
        if not self.is_game_window_active():
            self.scene.clear()
            return

        self.scene.clear()
        try:
            # Check if offsets are still valid
            if not self.offsets or not self.client_dll:
                self.offsets, self.client_dll = get_offsets_and_client_dll()
                if not self.offsets or not self.client_dll:
                    status_text = self.scene.addText("Waiting for offsets...", QtGui.QFont('DejaVu Sans', 12, QtGui.QFont.Bold))
                    status_text.setPos(5, 5)
                    status_text.setDefaultTextColor(QtGui.QColor(255, 255, 0))
                    return
            
            esp(self.scene, self.pm, self.client, self.offsets, self.client_dll, self.window_width, self.window_height, self.settings)
            current_time = time.time()
            self.frame_count += 1
            if current_time - self.last_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_time = current_time
            fps_text = self.scene.addText(f"Goon Ware | FPS: {self.fps}", QtGui.QFont('DejaVu Sans', 12, QtGui.QFont.Bold))
            fps_text.setPos(5, 5)
            fps_text.setDefaultTextColor(QtGui.QColor(255, 255, 255))
            
            # Add kill switch indicator
            kill_switch_text = self.scene.addText("Kill Switch: =", QtGui.QFont('DejaVu Sans', 10, QtGui.QFont.Bold))
            kill_switch_text.setPos(5, 25)
            kill_switch_text.setDefaultTextColor(QtGui.QColor(255, 255, 0))
            
            # Add aimbot status indicator
            aim_key = self.settings.get('keyboard', 'ALT')
            aimbot_status_text = self.scene.addText(f"Aimbot: {aim_key}", QtGui.QFont('DejaVu Sans', 10, QtGui.QFont.Bold))
            aimbot_status_text.setPos(5, 45)
            aimbot_status_text.setDefaultTextColor(QtGui.QColor(0, 255, 0))
            
            # Add target lock indicator
            if locked_target:
                lock_text = self.scene.addText("TARGET LOCKED", QtGui.QFont('DejaVu Sans', 12, QtGui.QFont.Bold))
                lock_text.setPos(5, 65)
                lock_text.setDefaultTextColor(QtGui.QColor(255, 0, 0))
            
            # Add bhop status indicator
            bhop_key = self.settings.get('bhop_key', 'SPACE')
            bhop_status_text = self.scene.addText(f"Bhop: {bhop_key}", QtGui.QFont('DejaVu Sans', 10, QtGui.QFont.Bold))
            bhop_status_text.setPos(5, 85)
            bhop_status_text.setDefaultTextColor(QtGui.QColor(0, 255, 255))
        except Exception as e:
            print(f"Scene Update Error: {e}")
            # Don't quit immediately, just show error
            error_text = self.scene.addText(f"Error: {str(e)[:50]}...", QtGui.QFont('DejaVu Sans', 10, QtGui.QFont.Bold))
            error_text.setPos(5, 25)
            error_text.setDefaultTextColor(QtGui.QColor(255, 0, 0))

    def is_game_window_active(self):
        hwnd = win32gui.FindWindow(None, "Counter-Strike 2")
        if hwnd:
            foreground_hwnd = win32gui.GetForegroundWindow()
            return hwnd == foreground_hwnd
        return False

def esp(scene, pm, client, offsets, client_dll, window_width, window_height, settings):
    global BombPlantedTime, BombDefusedTime
    
    # Use get() method with default values to prevent KeyError
    if settings.get('esp_rendering', 0) == 0:
        return

    # Check if offsets are available
    if not offsets or not client_dll:
        print("Offsets not available, skipping ESP")
        return

    try:
        dwEntityList = offsets['client.dll']['dwEntityList']
        dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
        dwViewMatrix = offsets['client.dll']['dwViewMatrix']
        dwPlantedC4 = offsets['client.dll']['dwPlantedC4']
        m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
        m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
        m_pGameSceneNode = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode']
        m_modelState = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']
        m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
        m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']
        m_iszPlayerName = client_dll['client.dll']['classes']['CBasePlayerController']['fields']['m_iszPlayerName']
        m_pClippingWeapon = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_pClippingWeapon']
        m_AttributeManager = client_dll['client.dll']['classes']['C_EconEntity']['fields']['m_AttributeManager']
        m_Item = client_dll['client.dll']['classes']['C_AttributeContainer']['fields']['m_Item']
        m_iItemDefinitionIndex = client_dll['client.dll']['classes']['C_EconItemView']['fields']['m_iItemDefinitionIndex']
        m_ArmorValue = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_ArmorValue']
        m_vecAbsOrigin = client_dll['client.dll']['classes']['CGameSceneNode']['fields']['m_vecAbsOrigin']
        m_flTimerLength = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_flTimerLength']
        m_flDefuseLength = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_flDefuseLength']
        m_bBeingDefused = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_bBeingDefused']
    except KeyError as e:
        print(f"Missing offset: {e}")
        return

    try:
        view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]
    except Exception as e:
        print(f"Failed to read view matrix: {e}")
        return

    try:
        local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
        if local_player_pawn_addr == 0:
            return
        local_player_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
    except Exception as e:
        print(f"Failed to read local player data: {e}")
        return

    no_center_x = window_width / 2
    no_center_y = window_height * 0.9
    
    try:
        entity_list = pm.read_longlong(client + dwEntityList)
        if entity_list == 0:
            return
        entity_ptr = pm.read_longlong(entity_list + 0x10)
        if entity_ptr == 0:
            return
    except Exception as e:
        print(f"Failed to read entity list: {e}")
        return

    def bombisplant():
        global BombPlantedTime
        try:
            bombisplant = pm.read_bool(client + dwPlantedC4 - 0x8)
            if bombisplant:
                if (BombPlantedTime == 0):
                    BombPlantedTime = time.time()
            else:
                BombPlantedTime = 0
            return bombisplant
        except Exception as e:
            print(f"Failed to read bomb planted status: {e}")
            return False
    
    def getC4BaseClass():
        try:
            plantedc4 = pm.read_longlong(client + dwPlantedC4)
            if plantedc4 == 0:
                return 0
            plantedc4class = pm.read_longlong(plantedc4)
            return plantedc4class
        except Exception as e:
            print(f"Failed to get C4 base class: {e}")
            return 0
    
    def getPositionWTS():
        try:
            c4base = getC4BaseClass()
            if c4base == 0:
                return [-999, -999]
            c4node = pm.read_longlong(c4base + m_pGameSceneNode)
            if c4node == 0:
                return [-999, -999]
            c4posX = pm.read_float(c4node + m_vecAbsOrigin)
            c4posY = pm.read_float(c4node + m_vecAbsOrigin + 0x4)
            c4posZ = pm.read_float(c4node + m_vecAbsOrigin + 0x8)
            bomb_pos = w2s(view_matrix, c4posX, c4posY, c4posZ, window_width, window_height)
            return bomb_pos
        except Exception as e:
            print(f"Failed to get bomb position: {e}")  
            return [-999, -999]
    
    def getBombTime():
        try:
            c4base = getC4BaseClass()
            if c4base == 0:
                return 0
            BombTime = pm.read_float(c4base + m_flTimerLength) - (time.time() - BombPlantedTime)
            return BombTime if (BombTime >= 0) else 0
        except Exception as e:
            print(f"Failed to get bomb time: {e}")
            return 0
    
    def isBeingDefused():
        global BombDefusedTime
        try:
            c4base = getC4BaseClass()
            if c4base == 0:
                return False
            BombIsDefused = pm.read_bool(c4base + m_bBeingDefused)
            if (BombIsDefused):
                if (BombDefusedTime == 0):
                    BombDefusedTime = time.time() 
            else:
                BombDefusedTime = 0
            return BombIsDefused
        except Exception as e:
            print(f"Failed to check defuse status: {e}")
            return False
    
    def getDefuseTime():
        try:
            c4base = getC4BaseClass()
            if c4base == 0:
                return 0
            DefuseTime = pm.read_float(c4base + m_flDefuseLength) - (time.time() - BombDefusedTime)
            return DefuseTime if (isBeingDefused() and DefuseTime >= 0) else 0
        except Exception as e:
            print(f"Failed to get defuse time: {e}")
            return 0

    bfont = QtGui.QFont('DejaVu Sans', 10, QtGui.QFont.Bold)

    if settings.get('bomb_esp', 0) == 1:
        if bombisplant():
            BombPosition = getPositionWTS()
            BombTime = getBombTime()
            DefuseTime = getDefuseTime()
        
            if (BombPosition[0] > 0 and BombPosition[1] > 0):
                if DefuseTime > 0:
                    c4_name_text = scene.addText(f'BOMB {round(BombTime, 2)} | DIF {round(DefuseTime, 2)}', bfont)
                else:
                    c4_name_text = scene.addText(f'BOMB {round(BombTime, 2)}', bfont)
                c4_name_x = BombPosition[0]
                c4_name_y = BombPosition[1]
                c4_name_text.setPos(c4_name_x, c4_name_y)
                c4_name_text.setDefaultTextColor(QtGui.QColor(255, 255, 255))

    for i in range(1, 64):
        try:
            if entity_ptr == 0:
                break

            entity_controller = pm.read_longlong(entity_ptr + 0x78 * (i & 0x1FF))
            if entity_controller == 0:
                continue

            entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
            if entity_controller_pawn == 0:
                continue

            entity_list_pawn = pm.read_longlong(entity_list + 0x8 * ((entity_controller_pawn & 0x7FFF) >> 0x9) + 0x10)
            if entity_list_pawn == 0:
                continue

            entity_pawn_addr = pm.read_longlong(entity_list_pawn + 0x78 * (entity_controller_pawn & 0x1FF))
            if entity_pawn_addr == 0 or entity_pawn_addr == local_player_pawn_addr:
                continue

            try:
                entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
                if entity_team == local_player_team and settings.get('esp_mode', 1) == 0:
                    continue

                entity_hp = pm.read_int(entity_pawn_addr + m_iHealth)
                armor_hp = pm.read_int(entity_pawn_addr + m_ArmorValue)
                if entity_hp <= 0:
                    continue

                entity_alive = pm.read_int(entity_pawn_addr + m_lifeState)
                if entity_alive != 256:
                    continue

                weapon_pointer = pm.read_longlong(entity_pawn_addr + m_pClippingWeapon)
                if weapon_pointer != 0:
                    try:
                        weapon_index = pm.read_int(weapon_pointer + m_AttributeManager + m_Item + m_iItemDefinitionIndex)
                        weapon_name = get_weapon_name_by_index(weapon_index)
                    except:
                        weapon_name = "Unknown"
                else:
                    weapon_name = "Unknown"

                color = QtGui.QColor(71, 167, 106) if entity_team == local_player_team else QtGui.QColor(196, 30, 58)
                game_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
                if game_scene == 0:
                    continue
                bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
                if bone_matrix == 0:
                    continue

            except Exception as e:
                print(f"Failed to read entity data: {e}")
                continue

            try:
                headX = pm.read_float(bone_matrix + 6 * 0x20)
                headY = pm.read_float(bone_matrix + 6 * 0x20 + 0x4)
                headZ = pm.read_float(bone_matrix + 6 * 0x20 + 0x8) + 8
                head_pos = w2s(view_matrix, headX, headY, headZ, window_width, window_height)
                if head_pos[1] < 0:
                    continue
                    
                legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
                leg_pos = w2s(view_matrix, headX, headY, legZ, window_width, window_height)
                
                if settings.get('line_rendering', 1) == 1:
                    bottom_left_x = head_pos[0] - (head_pos[0] - leg_pos[0]) // 2
                    bottom_y = leg_pos[1]
                    line = scene.addLine(bottom_left_x, bottom_y, no_center_x, no_center_y, QtGui.QPen(color, 1))

                deltaZ = abs(head_pos[1] - leg_pos[1])
                leftX = head_pos[0] - deltaZ // 4
                rightX = head_pos[0] + deltaZ // 4
                # Use custom box color
                box_color = QtGui.QColor(
                    settings.get('esp_box_color_r', 255),
                    settings.get('esp_box_color_g', 0),
                    settings.get('esp_box_color_b', 0)
                )
                rect = scene.addRect(QtCore.QRectF(leftX, head_pos[1], rightX - leftX, leg_pos[1] - head_pos[1]), QtGui.QPen(box_color, 1), QtCore.Qt.NoBrush)

                if settings.get('hp_bar_rendering', 1) == 1:
                    max_hp = 100
                    hp_percentage = min(1.0, max(0.0, entity_hp / max_hp))
                    hp_bar_width = 2
                    hp_bar_height = deltaZ
                    hp_bar_x_left = leftX - hp_bar_width - 2
                    hp_bar_y_top = head_pos[1]
                    hp_bar = scene.addRect(QtCore.QRectF(hp_bar_x_left, hp_bar_y_top, hp_bar_width, hp_bar_height), QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(0, 0, 0))
                    current_hp_height = hp_bar_height * hp_percentage
                    hp_bar_y_bottom = hp_bar_y_top + hp_bar_height - current_hp_height
                    # Use custom health color
                    health_color = QtGui.QColor(
                        settings.get('esp_health_color_r', 0),
                        settings.get('esp_health_color_g', 0),
                        settings.get('esp_health_color_b', 255)
                    )
                    hp_bar_current = scene.addRect(QtCore.QRectF(hp_bar_x_left, hp_bar_y_bottom, hp_bar_width, current_hp_height), QtGui.QPen(QtCore.Qt.NoPen), health_color)
                    max_armor_hp = 100
                    armor_hp_percentage = min(1.0, max(0.0, armor_hp / max_armor_hp))
                    armor_bar_width = 2
                    armor_bar_height = deltaZ
                    armor_bar_x_left = hp_bar_x_left - armor_bar_width - 2
                    armor_bar_y_top = head_pos[1]
                
                    armor_bar = scene.addRect(QtCore.QRectF(armor_bar_x_left, armor_bar_y_top, armor_bar_width, armor_bar_height), QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(0, 0, 0))
                    current_armor_height = armor_bar_height * armor_hp_percentage
                    armor_bar_y_bottom = armor_bar_y_top + armor_bar_height - current_armor_height
                    armor_bar_current = scene.addRect(QtCore.QRectF(armor_bar_x_left, armor_bar_y_bottom, armor_bar_width, current_armor_height), QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(62, 95, 138))


                if settings.get('head_hitbox_rendering', 1) == 1:
                    head_hitbox_size = (rightX - leftX) / 5
                    head_hitbox_radius = head_hitbox_size * 2 ** 0.5 / 2
                    head_hitbox_x = leftX + 2.5 * head_hitbox_size
                    head_hitbox_y = head_pos[1] + deltaZ / 9
                    # Use custom head color
                    head_color = QtGui.QColor(
                        settings.get('esp_head_color_r', 255),
                        settings.get('esp_head_color_g', 255),
                        settings.get('esp_head_color_b', 0),
                        128
                    )
                    ellipse = scene.addEllipse(QtCore.QRectF(head_hitbox_x - head_hitbox_radius, head_hitbox_y - head_hitbox_radius, head_hitbox_radius * 2, head_hitbox_radius * 2), QtGui.QPen(QtCore.Qt.NoPen), head_color)

                if settings.get('bons', 0) == 1:
                    # Use custom bone color
                    bone_color = QtGui.QColor(
                        settings.get('esp_bone_color_r', 0),
                        settings.get('esp_bone_color_g', 255),
                        settings.get('esp_bone_color_b', 0)
                    )
                    draw_bones(scene, pm, bone_matrix, view_matrix, window_width, window_height, bone_color)

                if settings.get('nickname', 0) == 1:
                    player_name = pm.read_string(entity_controller + m_iszPlayerName, 32)
                    font_size = max(6, min(18, deltaZ / 25))
                    font = QtGui.QFont('DejaVu Sans', font_size, QtGui.QFont.Bold)
                    name_text = scene.addText(player_name, font)
                    text_rect = name_text.boundingRect()
                    name_x = head_pos[0] - text_rect.width() / 2
                    name_y = head_pos[1] - text_rect.height()
                    name_text.setPos(name_x, name_y)
                    # Use custom name color
                    name_color = QtGui.QColor(
                        settings.get('esp_name_color_r', 255),
                        settings.get('esp_name_color_g', 255),
                        settings.get('esp_name_color_b', 255)
                    )
                    name_text.setDefaultTextColor(name_color)
                
                if settings.get('weapon', 0) == 1:
                    weapon_name_text = scene.addText(weapon_name, font)
                    text_rect = weapon_name_text.boundingRect()
                    weapon_name_x = head_pos[0] - text_rect.width() / 2
                    weapon_name_y = head_pos[1] + deltaZ
                    weapon_name_text.setPos(weapon_name_x, weapon_name_y)
                    # Use custom weapon color
                    weapon_color = QtGui.QColor(
                        settings.get('esp_weapon_color_r', 255),
                        settings.get('esp_weapon_color_g', 0),
                        settings.get('esp_weapon_color_b', 255)
                    )
                    weapon_name_text.setDefaultTextColor(weapon_color)
                
                # Draw sniper crosshair if enabled and player has sniper rifle
                if settings.get('sniper_crosshair', 0) == 1 and is_sniper_rifle(weapon_index):
                    # Draw white dot crosshair at player's head position
                    crosshair_size = 3
                    crosshair_x = head_pos[0] - crosshair_size / 2
                    crosshair_y = head_pos[1] - crosshair_size / 2
                    
                    # Create white dot crosshair
                    crosshair_dot = scene.addEllipse(
                        QtCore.QRectF(crosshair_x, crosshair_y, crosshair_size, crosshair_size),
                        QtGui.QPen(QtGui.QColor(255, 255, 255), 1),
                        QtGui.QBrush(QtGui.QColor(255, 255, 255))
                    )


                # Draw aimbot FOV indicator
                if settings.get('aim_active', 0) == 1:
                    center_x = window_width / 2
                    center_y = window_height / 2
                    fov = settings.get('aim_fov', 50)
                    fov_pixels = (fov / 90.0) * min(center_x, center_y)
                    
                    # Draw FOV circle
                    fov_ellipse = scene.addEllipse(
                        QtCore.QRectF(center_x - fov_pixels, center_y - fov_pixels, fov_pixels * 2, fov_pixels * 2), 
                        QtGui.QPen(QtGui.QColor(0, 255, 0, 64), 1), 
                        QtCore.Qt.NoBrush
                    )
                    
                    # Draw radius indicator if enabled
                    if settings.get('radius', 0) != 0:
                        screen_radius = settings['radius'] / 100.0 * min(center_x, center_y)
                        radius_ellipse = scene.addEllipse(
                            QtCore.QRectF(center_x - screen_radius, center_y - screen_radius, screen_radius * 2, screen_radius * 2), 
                            QtGui.QPen(QtGui.QColor(255, 255, 255, 32), 0.5), 
                            QtCore.Qt.NoBrush
                        )

            except Exception as e:
                print(f"Failed to render ESP for entity {i}: {e}")
                continue
        except Exception as e:
            print(f"Failed to process entity {i}: {e}")
            continue

def get_weapon_name_by_index(index):
    weapon_names = {
    32: "P2000",
    61: "USP-S",
    4: "Glock",
    2: "Dual Berettas",
    36: "P250",
    30: "Tec-9",
    63: "CZ75-Auto",
    1: "Desert Eagle",
    3: "Five-SeveN",
    64: "R8",
    35: "Nova",
    25: "XM1014",
    27: "MAG-7",
    29: "Sawed-Off",
    14: "M249",
    28: "Negev",
    17: "MAC-10",
    23: "MP5-SD",
    24: "UMP-45",
    19: "P90",
    26: "Bizon",
    34: "MP9",
    33: "MP7",
    10: "FAMAS",
    16: "M4A4",
    60: "M4A1-S",
    8: "AUG",
    43: "Galil",
    7: "AK-47",
    39: "SG 553",
    40: "SSG 08",
    9: "AWP",
    38: "SCAR-20",
    11: "G3SG1",
    43: "Flashbang",
    44: "Hegrenade",
    45: "Smoke",
    46: "Molotov",
    47: "Decoy",
    48: "Incgrenage",
    49: "C4",
    31: "Taser",
    42: "Knife",
    41: "Knife Gold",
    59: "Knife",
    80: "Knife Ghost",
    500: "Knife Bayonet",
    505: "Knife Flip",
    506: "Knife Gut",
    507: "Knife Karambit",
    508: "Knife M9",
    509: "Knife Tactica",
    512: "Knife Falchion",
    514: "Knife Survival Bowie",
    515: "Knife Butterfly",
    516: "Knife Rush",
    519: "Knife Ursus",
    520: "Knife Gypsy Jackknife",
    522: "Knife Stiletto",
    523: "Knife Widowmaker"
}
    return weapon_names.get(index, 'Unknown')

def is_sniper_rifle(weapon_index):
    """Check if the weapon is a sniper rifle"""
    sniper_weapons = {
        9: "AWP",
        40: "SSG 08", 
        38: "SCAR-20",
        11: "G3SG1"
    }
    return weapon_index in sniper_weapons

def draw_bones(scene, pm, bone_matrix, view_matrix, width, height, player_color):
    bone_ids = {
        "head": 6,
        "neck": 5,
        "spine": 4,
        "pelvis": 0,
        "left_shoulder": 13,
        "left_elbow": 14,
        "left_wrist": 15,
        "right_shoulder": 9,
        "right_elbow": 10,
        "right_wrist": 11,
        "left_hip": 25,
        "left_knee": 26,
        "left_ankle": 27,
        "right_hip": 22,
        "right_knee": 23,
        "right_ankle": 24,
    }
    bone_connections = [
        ("head", "neck"),
        ("neck", "spine"),
        ("spine", "pelvis"),
        ("pelvis", "left_hip"),
        ("left_hip", "left_knee"),
        ("left_knee", "left_ankle"),
        ("pelvis", "right_hip"),
        ("right_hip", "right_knee"),
        ("right_knee", "right_ankle"),
        ("neck", "left_shoulder"),
        ("left_shoulder", "left_elbow"),
        ("left_elbow", "left_wrist"),
        ("neck", "right_shoulder"),
        ("right_shoulder", "right_elbow"),
        ("right_elbow", "right_wrist"),
    ]
    bone_positions = {}
    try:
        for bone_name, bone_id in bone_ids.items():
            try:
                boneX = pm.read_float(bone_matrix + bone_id * 0x20)
                boneY = pm.read_float(bone_matrix + bone_id * 0x20 + 0x4)
                boneZ = pm.read_float(bone_matrix + bone_id * 0x20 + 0x8)
                bone_pos = w2s(view_matrix, boneX, boneY, boneZ, width, height)
                if bone_pos[0] != -999 and bone_pos[1] != -999:
                    bone_positions[bone_name] = bone_pos
            except Exception as e:
                continue
                
        for connection in bone_connections:
            if connection[0] in bone_positions and connection[1] in bone_positions:
                try:
                    # Use player color for skeleton
                    skeleton_color = QtGui.QColor(player_color.red(), player_color.green(), player_color.blue(), 200)
                    scene.addLine(
                        bone_positions[connection[0]][0], bone_positions[connection[0]][1],
                        bone_positions[connection[1]][0], bone_positions[connection[1]][1],
                        QtGui.QPen(skeleton_color, 2)
                    )
                except Exception as e:
                    continue
    except Exception as e:
        pass

def esp_main():
    settings = load_settings()
    app = QtWidgets.QApplication(sys.argv)
    window = ESPWindow(settings)
    window.show()
    
    # Check for kill switch periodically
    def check_kill_switch():
        global kill_switch_active
        if kill_switch_active:
            app.quit()
            return
        QtCore.QTimer.singleShot(100, check_kill_switch)
    
    check_kill_switch()
    sys.exit(app.exec())

# Trigger Bot
def triggerbot():
    # Get offsets with error handling
    try:
        offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json', timeout=10).json()
        client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json', timeout=10).json()
    except Exception as e:
        print(f"Failed to get offsets for triggerbot: {e}")
        return
    
    try:
        dwEntityList = offsets['client.dll']['dwEntityList']
        dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
        m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
        m_iIDEntIndex = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_iIDEntIndex']
        m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']
    except KeyError as e:
        print(f"Missing offset for triggerbot: {e}")
        return
    mouse = Controller()
    default_settings = {
        "keyboards": "X",
        "trigger_bot_active": 1,
        "esp_mode": 1
    }

    def load_settings():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return default_settings

    def main(settings):
        pm = pymem.Pymem("cs2.exe")
        client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
        while True:
            # Check for kill switch
            global kill_switch_active
            if kill_switch_active:
                break
                
            try:
                trigger_bot_active = settings.get("trigger_bot_active", 0)
                attack_all = settings.get("esp_mode", 1)
                keyboards = settings.get("keyboards", "X")
                # Handle special keys
                if keyboards == "ALT":
                    key_pressed = win32api.GetAsyncKeyState(win32con.VK_MENU)
                elif keyboards == "CTRL":
                    key_pressed = win32api.GetAsyncKeyState(win32con.VK_CONTROL)
                elif keyboards == "SHIFT":
                    key_pressed = win32api.GetAsyncKeyState(win32con.VK_SHIFT)
                elif keyboards == "SPACE":
                    key_pressed = win32api.GetAsyncKeyState(win32con.VK_SPACE)
                elif len(keyboards) == 1:
                    key_pressed = win32api.GetAsyncKeyState(ord(keyboards))
                else:
                    key_pressed = False
                
                if key_pressed:
                    if trigger_bot_active == 1:
                        try:
                            player = pm.read_longlong(client + dwLocalPlayerPawn)
                            entityId = pm.read_int(player + m_iIDEntIndex)
                            if entityId > 0:
                                entList = pm.read_longlong(client + dwEntityList)
                                entEntry = pm.read_longlong(entList + 0x8 * (entityId >> 9) + 0x10)
                                entity = pm.read_longlong(entEntry + 120 * (entityId & 0x1FF))
                                entityTeam = pm.read_int(entity + m_iTeamNum)
                                playerTeam = pm.read_int(player + m_iTeamNum)
                                if (attack_all == 1) or (entityTeam != playerTeam and attack_all == 0):
                                    entityHp = pm.read_int(entity + m_iHealth)
                                    if entityHp > 0:
                                        mouse.press(Button.left)
                                        time.sleep(0.03)
                                        mouse.release(Button.left)
                        except Exception:
                            pass
                    time.sleep(0.03)
                else:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                break
            except Exception:
                time.sleep(1)

    def start_main_thread(settings):
        while True:
            main(settings)

    def setup_watcher(app, settings):
        watcher = QFileSystemWatcher()
        watcher.addPath(CONFIG_FILE)
        def reload_settings():
            new_settings = load_settings()
            settings.update(new_settings)
        watcher.fileChanged.connect(reload_settings)
        app.exec()

    def main_program():
        app = QCoreApplication(sys.argv)
        settings = load_settings()
        threading.Thread(target=start_main_thread, args=(settings,), daemon=True).start()
        setup_watcher(app, settings)

    main_program()



# Aim Bot
def aim():
    default_settings = {
        'esp_rendering': 1,
        'esp_mode': 1,
        'keyboard': "ALT",
        'aim_active': 1,
        'aim_mode': 1,
        'radius': 20,
        'aim_mode_distance': 1
    }

    def get_window_size(window_name="Counter-Strike 2"):
        hwnd = win32gui.FindWindow(None, window_name)
        if hwnd:
            rect = win32gui.GetClientRect(hwnd)
            return rect[2] - rect[0], rect[3] - rect[1]
        return 1920, 1080

    def load_settings():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return default_settings

    def get_offsets_and_client_dll():
        try:
            offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json', timeout=10).json()
            client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json', timeout=10).json()
            return offsets, client_dll
        except Exception as e:
            print(f"Failed to get offsets for aimbot: {e}")
            return None, None

    def get_targets_for_aimbot(pm, client, offsets, client_dll, window_size, settings):
        """Get targets for aimbot functionality"""
        width, height = window_size
        target_list = []
        
        if settings.get('aim_active', 0) == 0:
            return target_list
            
        try:
            dwEntityList = offsets['client.dll']['dwEntityList']
            dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
            dwViewMatrix = offsets['client.dll']['dwViewMatrix']
            m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
            m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
            m_pGameSceneNode = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode']
            m_modelState = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']
            m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
            m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']
            
            view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]
            local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
            
            if local_player_pawn_addr == 0:
                return target_list
                
            try:
                local_player_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
            except:
                return target_list
                
            entity_list = pm.read_longlong(client + dwEntityList)
            entity_ptr = pm.read_longlong(entity_list + 0x10)
            
            if entity_ptr == 0:
                return target_list
                
            center_x = width / 2
            center_y = height / 2
            fov = settings.get('aim_fov', 50)
            fov_pixels = (fov / 90.0) * min(center_x, center_y)
            
            for i in range(1, 64):
                try:
                    entity_controller = pm.read_longlong(entity_ptr + 0x78 * (i & 0x1FF))
                    if entity_controller == 0:
                        continue

                    entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
                    if entity_controller_pawn == 0:
                        continue

                    entity_list_pawn = pm.read_longlong(entity_list + 0x8 * ((entity_controller_pawn & 0x7FFF) >> 0x9) + 0x10)
                    if entity_list_pawn == 0:
                        continue

                    entity_pawn_addr = pm.read_longlong(entity_list_pawn + 0x78 * (entity_controller_pawn & 0x1FF))
                    if entity_pawn_addr == 0 or entity_pawn_addr == local_player_pawn_addr:
                        continue

                    # Check if entity is alive and on different team
                    entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
                    if entity_team == local_player_team:
                        continue
                        
                    entity_hp = pm.read_int(entity_pawn_addr + m_iHealth)
                    if entity_hp <= 0:
                        continue
                        
                    entity_alive = pm.read_int(entity_pawn_addr + m_lifeState)
                    if entity_alive != 256:
                        continue

                    # Get entity position
                    game_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
                    if game_scene == 0:
                        continue
                        
                    bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
                    if bone_matrix == 0:
                        continue

                    # Get head position (bone 6 = head)
                    headX = pm.read_float(bone_matrix + 6 * 0x20)
                    headY = pm.read_float(bone_matrix + 6 * 0x20 + 0x4)
                    headZ = pm.read_float(bone_matrix + 6 * 0x20 + 0x8) + 8
                    head_pos = w2s(view_matrix, headX, headY, headZ, width, height)
                    
                    # Get body position (bone 4 = chest)
                    bodyX = pm.read_float(bone_matrix + 4 * 0x20)
                    bodyY = pm.read_float(bone_matrix + 4 * 0x20 + 0x4)
                    bodyZ = pm.read_float(bone_matrix + 4 * 0x20 + 0x8)
                    body_pos = w2s(view_matrix, bodyX, bodyY, bodyZ, width, height)
                    
                    # Get neck position (bone 5 = neck)
                    neckX = pm.read_float(bone_matrix + 5 * 0x20)
                    neckY = pm.read_float(bone_matrix + 5 * 0x20 + 0x4)
                    neckZ = pm.read_float(bone_matrix + 5 * 0x20 + 0x8)
                    neck_pos = w2s(view_matrix, neckX, neckY, neckZ, width, height)
                    
                    # Get leg positions (bones 23, 24 = legs)
                    leg1X = pm.read_float(bone_matrix + 23 * 0x20)
                    leg1Y = pm.read_float(bone_matrix + 23 * 0x20 + 0x4)
                    leg1Z = pm.read_float(bone_matrix + 23 * 0x20 + 0x8)
                    leg1_pos = w2s(view_matrix, leg1X, leg1Y, leg1Z, width, height)
                    
                    leg2X = pm.read_float(bone_matrix + 24 * 0x20)
                    leg2Y = pm.read_float(bone_matrix + 24 * 0x20 + 0x4)
                    leg2Z = pm.read_float(bone_matrix + 24 * 0x20 + 0x8)
                    leg2_pos = w2s(view_matrix, leg2X, leg2Y, leg2Z, width, height)
                    
                    # Calculate center position (average of head and body)
                    center_pos = ((head_pos[0] + body_pos[0]) / 2, (head_pos[1] + body_pos[1]) / 2)
                    
                    # Calculate upper body position (between head and chest)
                    upper_body_pos = ((head_pos[0] + body_pos[0]) / 2, (head_pos[1] + body_pos[1]) * 0.7 + head_pos[1] * 0.3)
                    
                    if head_pos[1] < 0 or body_pos[1] < 0:
                        continue
                        
                    # Calculate distance to center (FOV check) - use head position for FOV
                    distance_2d = math.sqrt((head_pos[0] - center_x)**2 + (head_pos[1] - center_y)**2)
                    
                    if distance_2d <= fov_pixels:
                        target_info = {
                            'head_pos': head_pos,
                            'body_pos': body_pos,
                            'neck_pos': neck_pos,
                            'leg1_pos': leg1_pos,
                            'leg2_pos': leg2_pos,
                            'center_pos': center_pos,
                            'upper_body_pos': upper_body_pos,
                            'pos': head_pos,  # Default to head position
                            'distance_2d': distance_2d,
                            'health': entity_hp,
                            'team': entity_team
                        }
                        target_list.append(target_info)
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Aimbot target detection error: {e}")
            
        return target_list

    def silent_aim(target_list, settings):
        """Silent aim function that shoots without moving crosshair"""
        if not target_list:
            return False
            
        center_x = win32api.GetSystemMetrics(0) // 2
        center_y = win32api.GetSystemMetrics(1) // 2
        
        # Get silent aim settings
        silent_fov = settings.get('silent_aim_fov', 30)
        silent_smoothing = settings.get('silent_aim_smoothing', 0.5)
        target_mode = settings.get('aim_target_mode', 'head')  # Use new targeting system
        
        # Convert FOV to screen pixels
        fov_pixels = (silent_fov / 90.0) * min(center_x, center_y)
        
        # Find best target within silent aim FOV
        best_target = None
        best_score = float('inf')
        
        for target in target_list:
            # Use head position for FOV check
            head_pos = target.get('head_pos', target['pos'])
            distance_2d = math.sqrt((head_pos[0] - center_x)**2 + (head_pos[1] - center_y)**2)
            
            if distance_2d <= fov_pixels:
                # Calculate score (closer is better)
                score = distance_2d
                
                # Prioritize low health targets
                health_penalty = target.get('health', 100) * 0.1
                score += health_penalty
                
                if score < best_score:
                    best_score = score
                    best_target = target
        
        if best_target:
            # Choose target position based on new targeting system
            if target_mode == 'head':
                target_x, target_y = best_target['head_pos']
                # Apply head offset
                head_offset = settings.get('head_offset', 3)
                target_y += head_offset
                # Apply head precision
                head_precision = settings.get('head_precision', 100) / 100.0
                if head_precision < 1.0:
                    import random
                    target_x += random.uniform(-5 * (1 - head_precision), 5 * (1 - head_precision))
                    target_y += random.uniform(-5 * (1 - head_precision), 5 * (1 - head_precision))
                    
            elif target_mode == 'neck':
                target_x, target_y = best_target['neck_pos']
                # Apply neck offset
                neck_offset = settings.get('neck_offset', 8)
                target_y += neck_offset
                
            elif target_mode == 'chest':
                target_x, target_y = best_target['body_pos']
                
            elif target_mode == 'legs':
                # Use average of both legs
                leg1_x, leg1_y = best_target['leg1_pos']
                leg2_x, leg2_y = best_target['leg2_pos']
                target_x = (leg1_x + leg2_x) / 2
                target_y = (leg1_y + leg2_y) / 2
                
            elif target_mode == 'center':
                target_x, target_y = best_target['center_pos']
                
            elif target_mode == 'upper_body':
                target_x, target_y = best_target['upper_body_pos']
                
            else:  # Default to head
                target_x, target_y = best_target['head_pos']
            
            # Calculate the angle to the target
            delta_x = target_x - center_x
            delta_y = target_y - center_y
            
            # For true silent aim, we need to use a different approach
            # Instead of moving the mouse, we'll use a more sophisticated method
            
            # Calculate the exact movement needed
            move_x = int(delta_x)
            move_y = int(delta_y)
            
            # For silent aim, we want to move the mouse to the target and shoot
            # The key is to do this very quickly so it appears "silent"
            
            # Move mouse to target position
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, move_x, move_y, 0, 0)
            
            # Very small delay to ensure the movement is registered
            time.sleep(0.001)
            
            # Shoot
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.001)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            
            # Move mouse back to original position
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, -move_x, -move_y, 0, 0)
            
            return True
        
        return False

    def aimbot(target_list, radius, aim_mode_distance, fov, settings):
        global locked_target
        
        if not target_list:
            locked_target = None
            return
            
        center_x = win32api.GetSystemMetrics(0) // 2
        center_y = win32api.GetSystemMetrics(1) // 2
        
        # Convert FOV to screen pixels (approximate)
        fov_pixels = (fov / 90.0) * min(center_x, center_y)
        
        # If we have a locked target, check if it's still valid
        if locked_target:
            # Check if locked target is still in target list and within FOV
            target_found = False
            closest_target = None
            closest_distance = float('inf')
            
            for target in target_list:
                # Calculate distance between current locked target and this target
                target_distance = math.sqrt(
                    (target['pos'][0] - locked_target['pos'][0])**2 + 
                    (target['pos'][1] - locked_target['pos'][1])**2
                )
                
                # If this target is very close to our locked target, it's likely the same player
                if target_distance < 50:  # 50 pixel tolerance for same player
                    dist = target.get('distance_2d', float('inf'))
                    if dist <= fov_pixels * 2:  # Allow more tolerance
                        if target_distance < closest_distance:
                            closest_distance = target_distance
                            closest_target = target
                            target_found = True
            
            if target_found and closest_target:
                locked_target = closest_target
            elif not target_found:
                locked_target = None
        
        # If no locked target, find the best target within FOV
        if not locked_target:
            best_target = None
            best_score = float('inf')
            
            for target in target_list:
                dist = target.get('distance_2d', float('inf'))
                
                # Check if target is within FOV
                if dist <= fov_pixels:
                    # Calculate score based on distance and size
                    if aim_mode_distance == 1:
                        # Prefer closest to crosshair
                        score = dist
                    else:
                        # Prefer largest target (closest in 3D)
                        deltaZ = target.get('deltaZ', 0)
                        score = dist - (deltaZ * 0.1)  # Factor in target size
                    
                    # Prioritize targets with lower health (easier to kill)
                    health_penalty = target.get('health', 100) * 0.1
                    score += health_penalty
                    
                    if score < best_score:
                        best_score = score
                        best_target = target
            
            if best_target:
                locked_target = best_target
        
        # Aim at locked target with smoothing
        if locked_target:
            # Choose target position based on new targeting system
            target_mode = settings.get('aim_target_mode', 'head')
            
            if target_mode == 'head':
                target_x, target_y = locked_target['head_pos']
                # Apply head offset
                head_offset = settings.get('head_offset', 3)
                target_y += head_offset
                # Apply head precision
                head_precision = settings.get('head_precision', 100) / 100.0
                if head_precision < 1.0:
                    # Add some randomness for lower precision
                    import random
                    target_x += random.uniform(-5 * (1 - head_precision), 5 * (1 - head_precision))
                    target_y += random.uniform(-5 * (1 - head_precision), 5 * (1 - head_precision))
                    
            elif target_mode == 'neck':
                target_x, target_y = locked_target['neck_pos']
                # Apply neck offset
                neck_offset = settings.get('neck_offset', 8)
                target_y += neck_offset
                
            elif target_mode == 'chest':
                target_x, target_y = locked_target['body_pos']
                
            elif target_mode == 'legs':
                # Use average of both legs
                leg1_x, leg1_y = locked_target['leg1_pos']
                leg2_x, leg2_y = locked_target['leg2_pos']
                target_x = (leg1_x + leg2_x) / 2
                target_y = (leg1_y + leg2_y) / 2
                
            elif target_mode == 'center':
                target_x, target_y = locked_target['center_pos']
                
            elif target_mode == 'upper_body':
                target_x, target_y = locked_target['upper_body_pos']
                
            else:  # Default to head
                target_x, target_y = locked_target['head_pos']
            
            # Calculate distance to target
            delta_x = target_x - center_x
            delta_y = target_y - center_y
            distance = math.sqrt(delta_x**2 + delta_y**2)
            
            # Only move if we're not already very close to target
            if distance > 2:  # 2 pixel threshold
                # Smooth movement instead of instant snap
                smoothing_factor = settings.get('aim_smoothing', 0.3)  # Get from settings
                
                move_x = int(delta_x * smoothing_factor)
                move_y = int(delta_y * smoothing_factor)
                
                # Move mouse to target
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, move_x, move_y, 0, 0)

    def main(settings):
        global kill_switch_active, recoil_control
        offsets, client_dll = get_offsets_and_client_dll()
        window_size = get_window_size()
        pm = pymem.Pymem("cs2.exe")
        client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
        while True:
            # Check for kill switch
            if kill_switch_active:
                break
                
            target_list = []
            # Get targets for aimbot
            target_list = get_targets_for_aimbot(pm, client, offsets, client_dll, window_size, settings)
            # Handle key binding for aimbot
            aim_key = settings.get('keyboard', 'ALT')
            if aim_key == "ALT":
                key_pressed = win32api.GetAsyncKeyState(win32con.VK_MENU)
            elif aim_key == "CTRL":
                key_pressed = win32api.GetAsyncKeyState(win32con.VK_CONTROL)
            elif aim_key == "SHIFT":
                key_pressed = win32api.GetAsyncKeyState(win32con.VK_SHIFT)
            elif aim_key == "SPACE":
                key_pressed = win32api.GetAsyncKeyState(win32con.VK_SPACE)
            elif len(aim_key) == 1:
                key_pressed = win32api.GetAsyncKeyState(ord(aim_key))
            else:
                key_pressed = False
            
            # Handle silent aim key binding
            silent_aim_key = settings.get('silent_aim_key', 'SHIFT')
            if silent_aim_key == "ALT":
                silent_key_pressed = win32api.GetAsyncKeyState(win32con.VK_MENU)
            elif silent_aim_key == "CTRL":
                silent_key_pressed = win32api.GetAsyncKeyState(win32con.VK_CONTROL)
            elif silent_aim_key == "SHIFT":
                silent_key_pressed = win32api.GetAsyncKeyState(win32con.VK_SHIFT)
            elif silent_aim_key == "SPACE":
                silent_key_pressed = win32api.GetAsyncKeyState(win32con.VK_SPACE)
            elif len(silent_aim_key) == 1:
                silent_key_pressed = win32api.GetAsyncKeyState(ord(silent_aim_key))
            else:
                silent_key_pressed = False
            
            if key_pressed:
                # Update current weapon for recoil control
                recoil_control.current_weapon = recoil_control.get_current_weapon(pm, client, offsets, client_dll)
                
                aimbot(target_list, settings.get('radius', 50), settings.get('aim_mode_distance', 1), settings.get('aim_fov', 50), settings)
                
                # Check for mouse click (shooting) and apply recoil control
                if win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000:
                    # Player is shooting, apply recoil control
                    if settings.get('recoil_control_enabled', 1):
                        recoil_control.apply_recoil_control(settings)
                
                time.sleep(0.005)  # 5ms delay to reduce flickering
            elif silent_key_pressed and settings.get('silent_aim', 0) == 1:
                # Silent aim is enabled and key is pressed
                if len(target_list) > 0:
                    # Update current weapon for recoil control
                    recoil_control.current_weapon = recoil_control.get_current_weapon(pm, client, offsets, client_dll)
                    
                    print(f"Silent aim triggered with {len(target_list)} targets")
                    silent_aim(target_list, settings)
                    
                    # Check for mouse click (shooting) and apply recoil control
                    if win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000:
                        # Player is shooting, apply recoil control
                        if settings.get('recoil_control_enabled', 1):
                            recoil_control.apply_recoil_control(settings)
                
                time.sleep(0.005)  # Faster response for silent aim
            else:
                time.sleep(0.001)

    def start_main_thread(settings):
        while True:
            main(settings)

    def setup_watcher(app, settings):
        watcher = QFileSystemWatcher()
        watcher.addPath(CONFIG_FILE)
        def reload_settings():
            new_settings = load_settings()
            settings.update(new_settings)
        watcher.fileChanged.connect(reload_settings)
        app.exec()

    def main_program():
        app = QCoreApplication(sys.argv)
        settings = load_settings()
        threading.Thread(target=start_main_thread, args=(settings,), daemon=True).start()
        setup_watcher(app, settings)

    main_program()

if __name__ == "__main__":
    print("=== Goon Ware CS2 Cheat ===")
    print("Waiting for CS2 to start...")
    print("Press '=' key to instantly close the cheat (Kill Switch)")
    
    # Start kill switch listener in a separate thread
    kill_switch_thread = threading.Thread(target=start_kill_switch_listener, daemon=True)
    kill_switch_thread.start()
    
    # Wait for CS2 process to be available
    while True:
        if kill_switch_active:
            print("Kill switch activated during startup!")
            sys.exit(0)
            
        try:
            pm = pymem.Pymem("cs2.exe")
            client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
            print("CS2 found! Starting Goon Ware cheat...")
            break
        except Exception as e:
            print(f"Waiting for CS2: {e}")
            time.sleep(2)
    
    # Wait a bit more for CS2 to fully initialize
    time.sleep(3)
    
    try:
        process1 = multiprocessing.Process(target=configurator)
        process2 = multiprocessing.Process(target=esp_main)
        process3 = multiprocessing.Process(target=triggerbot)
        process4 = multiprocessing.Process(target=aim)

        process1.start()
        process2.start()
        process3.start()
        process4.start()

        # Monitor processes and check for kill switch
        while True:
            if kill_switch_active:
                print("Kill switch activated! Terminating all processes...")
                process1.terminate()
                process2.terminate()
                process3.terminate()
                process4.terminate()
                break
                
            if not process1.is_alive() or not process2.is_alive() or not process3.is_alive() or not process4.is_alive():
                print("One or more processes died, shutting down...")
                break
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("Shutting down...")
        process1.terminate()
        process2.terminate()
        process3.terminate()
        process4.terminate()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Goon Ware cheat has been closed.")