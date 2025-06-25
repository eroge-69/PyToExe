import threading
import cv2
import numpy as np
import mss
import time
import sys
import pygetwindow as gw
from pynput.keyboard import Controller, Listener, Key
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QSlider, QVBoxLayout,
    QHBoxLayout, QCheckBox, QStackedLayout, QListWidget,
    QComboBox, QPushButton, QGridLayout, QGroupBox, QScrollArea,
    QColorDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont

# ===== CONFIG =====
trigger_percent = 87
autotime_enabled = True
monitor = {"top": 300, "left": 600, "width": 800, "height": 600}
lower_pink = np.array([140, 100, 100])
upper_pink = np.array([170, 255, 255])
keyboard_controller = Controller()

# Autotime variables
manual_max_height = None
lock_after_height = 80
max_meter_height = 0
locked = False
last_percent = -1
smoothed_percent = 0
triggered = False

# Manual timing sliders
manual_timer1_duration = 0.50
manual_timer2_duration = 0.75
manual_timer1_key = None
manual_timer2_key = None
manual_timing_active = False

# ===== DRIBBLE MOVES DATA =====
DRIBBLE_MOVES = {
    "Behind Back": {
        "sequences": [["z", "x"], ["c", "x"]],
        "assigned_key": None
    },
    "Spin": {
        "sequences": [["z", "x", "c"], ["c", "x", "z"]],
        "assigned_key": None
    },
    "Back Hesitation": {
        "sequences": [["z", "v"], ["c", "v"]],
        "assigned_key": None
    },
    "Double Cross": {
        "sequences": [["z", "z"], ["c", "c"]],
        "assigned_key": None
    },
    "Double Behind Back": {
        "sequences": [["z", "z", "z"], ["c", "c", "c"]],
        "assigned_key": None
    },
    "Cross Back": {
        "sequences": [["x", "x"]],
        "assigned_key": None
    },
    "Under Front": {
        "sequences": [["v", "v"]],
        "assigned_key": None
    },
    "Under Back": {
        "sequences": [["v", "x"]],
        "assigned_key": None
    },
    "Under Side": {
        "sequences": [["v", "z"], ["v", "c"]],
        "assigned_key": None
    },
    "Under Double": {
        "sequences": [["v", "z", "z"], ["v", "c", "c"]],
        "assigned_key": None
    }
}

# Signal class for thread communication
class SignalEmitter(QObject):
    status_update = pyqtSignal(str)

# Global signal emitter
signal_emitter = SignalEmitter()

# ===== MANUAL TIMING =====
def execute_manual_timing(duration):
    global manual_timing_active, triggered
    if manual_timing_active:
        return
    
    manual_timing_active = True
    try:
        print(f"[MANUAL TIMING] Holding E for {duration:.2f} seconds (AutoTime paused)")
        keyboard_controller.press('e')
        time.sleep(duration)
        keyboard_controller.release('e')
        print(f"[MANUAL TIMING] Released E after {duration:.2f} seconds")
        
        # Reset autotime trigger state so it can work again
        triggered = False
        
        # Small delay before resuming autotime to ensure clean transition
        time.sleep(0.1)
        print("[MANUAL TIMING] AutoTime resumed")
        
    except Exception as e:
        print(f"[MANUAL TIMING ERROR] {e}")
        keyboard_controller.release('e')  # Make sure E is released
    finally:
        manual_timing_active = False

# ===== MACRO EXECUTION =====
macro_execution_active = False
macros_enabled = True

def execute_macro(move_name):
    global macro_execution_active
    if macro_execution_active or not macros_enabled:
        return
    
    macro_execution_active = True
    try:
        move_data = DRIBBLE_MOVES[move_name]
        sequences = move_data["sequences"]
        
        print(f"[MACRO] Starting execution of {move_name}")
        print(f"[MACRO] Sequences: {sequences}")
        
        # Execute first sequence
        for key in sequences[0]:
            print(f"[MACRO] Pressing {key}")
            keyboard_controller.press(key)
            time.sleep(0.02)
            keyboard_controller.release(key)
            time.sleep(0.02)
        
        # If there are multiple sequences, wait and execute the second
        if len(sequences) > 1:
            time.sleep(0.1)  # 100ms wait as requested
            for key in sequences[1]:
                print(f"[MACRO] Pressing {key} (second sequence)")
                keyboard_controller.press(key)
                time.sleep(0.02)
                keyboard_controller.release(key)
                time.sleep(0.02)
        
        print(f"[MACRO] Completed {move_name}")
    except Exception as e:
        print(f"[MACRO ERROR] {e}")
    finally:
        macro_execution_active = False

# ===== ACTIVE WINDOW CHECK =====
def is_roblox_active():
    try:
        window = gw.getActiveWindow()
        if window:
            window_title = window.title.lower()
            # Check for Roblox or any window for testing purposes
            return "roblox" in window_title or "xot" in window_title
        return False
    except Exception as e:
        print(f"[DEBUG] Window check error: {e}")
        return True  # Return True if we can't check, to allow testing

# ===== MODERN GUI CLASS =====
class XOTApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("rh2 external")
        self.setGeometry(200, 200, 1000, 700)
        self.accent_color = "#7C5CFA"
        self.setStyleSheet(f"""
            background-color: #13151A;
            color: #F4F4F4;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        
        self.macro_listeners = {}  # Store active key listeners

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.addItem("Shooting")
        self.sidebar.addItem(" Macros")
        self.sidebar.addItem(" Settings")
        self.sidebar.setFixedWidth(160)
        self.sidebar.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                color: #8F93A2;
                font-size: 18px;
                border: none;
                padding-top: 24px;
                font-weight: bold;
            }}
            QListWidget::item:selected {{
                background: #23263A;
                color: {self.accent_color};
                border-radius: 8px;
            }}
        """)
        self.sidebar.setCurrentRow(0)

        # Top tab bar
        self.top_tab_bar = QHBoxLayout()
        self.general_tab = QLabel("Gaming Assistant")
        self.set_general_tab_style()
        self.top_tab_bar.addWidget(self.general_tab)
        self.top_tab_bar.addStretch(1)

        # Main content area
        self.stack_layout = QStackedLayout()
        self.shooting_tab = self.create_shooting_tab()
        self.macros_tab = self.create_macros_tab()
        self.settings_tab = self.create_settings_tab()
        
        self.stack_layout.addWidget(self.shooting_tab)
        self.stack_layout.addWidget(self.macros_tab)
        self.stack_layout.addWidget(self.settings_tab)
        self.stack_layout.setCurrentIndex(0)
        self.sidebar.currentRowChanged.connect(self.stack_layout.setCurrentIndex)

        # Main vertical layout for content
        self.content_layout = QVBoxLayout()
        self.content_layout.addLayout(self.top_tab_bar)
        self.content_layout.addSpacing(8)
        self.content_layout.addLayout(self.stack_layout)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        # Main horizontal layout
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addSpacing(20)
        self.main_layout.addLayout(self.content_layout)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.main_layout)
        
        # Start keyboard listener for macros
        self.start_macro_listener()
        
        # Start status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_autotime_status)
        self.status_timer.start(100)  # Update every 100ms

    def set_general_tab_style(self):
        self.general_tab.setStyleSheet(f"""
            background-color: #181A20;
            color: {self.accent_color};
            border-radius: 12px;
            padding: 8px 32px;
            font-size: 20px;
            font-weight: bold;
            border: 2px solid {self.accent_color};
        """)

    def create_shooting_tab(self):
        shooting_tab = QWidget()
        shooting_layout = QVBoxLayout()

        # AutoTime Section
        autotime_group = QGroupBox("AutoTime Detection")
        autotime_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 2px solid #333;
                border-radius: 8px;
                margin: 5px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
            }
        """)
        autotime_layout = QVBoxLayout()

        # Enable/Disable toggle
        self.toggle = QCheckBox("Enable AutoTime")
        self.toggle.setChecked(True)
        self.toggle.setStyleSheet(f"""
            QCheckBox {{
                color: white;
                font-size: 14px;
                padding: 5px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: #23263A;
                border: 2px solid #666;
                border-radius: 4px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.accent_color};
                border: 2px solid {self.accent_color};
                border-radius: 4px;
            }}
        """)
        self.toggle.stateChanged.connect(self.toggle_changed)
        autotime_layout.addWidget(self.toggle)

        # Trigger percentage slider
        trigger_row = QHBoxLayout()
        trigger_label = QLabel("Trigger At")
        trigger_label.setStyleSheet("color: #8F93A2; font-weight: normal; font-size: 14px;")
        trigger_row.addWidget(trigger_label)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(trigger_percent)
        self.slider.valueChanged.connect(self.update_slider)
        self.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: none;
                height: 8px;
                background: #23263A;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {self.accent_color};
                border: none;
                width: 22px;
                height: 22px;
                margin: -8px 0;
                border-radius: 11px;
                box-shadow: 0 2px 8px {self.accent_color}44;
            }}
            QSlider::sub-page:horizontal {{
                background: {self.accent_color};
                border-radius: 4px;
            }}
            QSlider::add-page:horizontal {{
                background: #23263A;
                border-radius: 4px;
            }}
        """)
        trigger_row.addWidget(self.slider, 2)
        
        self.slider_label = QLabel(f"{trigger_percent}%")
        self.slider_label.setStyleSheet("color: #F4F4F4; font-size: 13px; min-width: 40px; padding-right: 8px;")
        trigger_row.addWidget(self.slider_label)
        autotime_layout.addLayout(trigger_row)

        # Monitor area settings
        monitor_top_row = QHBoxLayout()
        top_label = QLabel("Monitor Top")
        top_label.setStyleSheet("color: #8F93A2; font-weight: normal; font-size: 14px;")
        monitor_top_row.addWidget(top_label)
        self.monitor_top = QSlider(Qt.Orientation.Horizontal)
        self.monitor_top.setRange(0, 1000)
        self.monitor_top.setValue(monitor["top"])
        self.monitor_top.valueChanged.connect(self.update_monitor_top)
        self.monitor_top.setStyleSheet(self.slider.styleSheet())
        monitor_top_row.addWidget(self.monitor_top, 2)
        self.monitor_top_label = QLabel(str(monitor["top"]))
        self.monitor_top_label.setStyleSheet("color: #F4F4F4; font-size: 13px; min-width: 40px; padding-right: 8px;")
        monitor_top_row.addWidget(self.monitor_top_label)
        autotime_layout.addLayout(monitor_top_row)

        monitor_left_row = QHBoxLayout()
        left_label = QLabel("Monitor Left")
        left_label.setStyleSheet("color: #8F93A2; font-weight: normal; font-size: 14px;")
        monitor_left_row.addWidget(left_label)
        self.monitor_left = QSlider(Qt.Orientation.Horizontal)
        self.monitor_left.setRange(0, 2000)
        self.monitor_left.setValue(monitor["left"])
        self.monitor_left.valueChanged.connect(self.update_monitor_left)
        self.monitor_left.setStyleSheet(self.slider.styleSheet())
        monitor_left_row.addWidget(self.monitor_left, 2)
        self.monitor_left_label = QLabel(str(monitor["left"]))
        self.monitor_left_label.setStyleSheet("color: #F4F4F4; font-size: 13px; min-width: 40px; padding-right: 8px;")
        monitor_left_row.addWidget(self.monitor_left_label)
        autotime_layout.addLayout(monitor_left_row)

        # Reset button
        reset_button = QPushButton("Reset Meter Detection")
        reset_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.accent_color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self.accent_color}CC;
            }}
            QPushButton:pressed {{
                background-color: {self.accent_color}AA;
            }}
        """)
        reset_button.clicked.connect(self.reset_meter_detection)
        autotime_layout.addWidget(reset_button)

        # Status label
        self.autotime_status = QLabel("Status: Waiting for meter...")
        self.autotime_status.setStyleSheet("color: #8F93A2; font-size: 12px; padding: 5px;")
        autotime_layout.addWidget(self.autotime_status)

        autotime_group.setLayout(autotime_layout)
        shooting_layout.addWidget(autotime_group)

        # Manual Timing Section
        manual_group = QGroupBox("Manual Timing")
        manual_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 2px solid #333;
                border-radius: 8px;
                margin: 5px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
            }
        """)
        manual_layout = QVBoxLayout()

        # Description
        desc = QLabel("Set custom hold durations for E key with keybinds (0.01-1.00 seconds)")
        desc.setStyleSheet("color: #8F93A2; font-size: 12px; font-weight: normal; padding: 5px;")
        manual_layout.addWidget(desc)

        # Timer 1
        timer1_row = QHBoxLayout()
        timer1_label = QLabel("Timer 1")
        timer1_label.setStyleSheet("color: #8F93A2; font-weight: normal; font-size: 14px; min-width: 60px;")
        timer1_row.addWidget(timer1_label)

        self.timer1_slider = QSlider(Qt.Orientation.Horizontal)
        self.timer1_slider.setRange(1, 100)
        self.timer1_slider.setValue(int(manual_timer1_duration * 100))
        self.timer1_slider.valueChanged.connect(self.update_timer1_slider)
        self.timer1_slider.setStyleSheet(self.slider.styleSheet())
        timer1_row.addWidget(self.timer1_slider, 2)

        self.timer1_value = QLabel(f"{manual_timer1_duration:.2f}s")
        self.timer1_value.setStyleSheet("color: #F4F4F4; font-size: 13px; min-width: 48px;")
        timer1_row.addWidget(self.timer1_value)

        self.timer1_key_label = QLabel("Not Set")
        self.timer1_key_label.setStyleSheet("color: #ff6666; font-weight: normal; min-width: 60px; text-align: center;")
        timer1_row.addWidget(self.timer1_key_label)

        timer1_buttons = QHBoxLayout()
        self.timer1_set_button = QPushButton("Set")
        self.timer1_set_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #23263A;
                color: white;
                border: 1px solid #666;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: #2A2F3A; }}
        """)
        self.timer1_set_button.clicked.connect(lambda: self.set_timer_key(1))
        timer1_buttons.addWidget(self.timer1_set_button)

        timer1_clear = QPushButton("Clear")
        timer1_clear.setStyleSheet("""
            QPushButton {
                background-color: #664444;
                color: white;
                border: 1px solid #666;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #775555; }
        """)
        timer1_clear.clicked.connect(lambda: self.clear_timer_key(1))
        timer1_buttons.addWidget(timer1_clear)

        timer1_test = QPushButton("Test")
        timer1_test.setStyleSheet("""
            QPushButton {
                background-color: #446644;
                color: white;
                border: 1px solid #666;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #557755; }
        """)
        timer1_test.clicked.connect(lambda: self.test_timer(1))
        timer1_buttons.addWidget(timer1_test)

        timer1_row.addLayout(timer1_buttons)
        manual_layout.addLayout(timer1_row)

        # Timer 2
        timer2_row = QHBoxLayout()
        timer2_label = QLabel("Timer 2")
        timer2_label.setStyleSheet("color: #8F93A2; font-weight: normal; font-size: 14px; min-width: 60px;")
        timer2_row.addWidget(timer2_label)

        self.timer2_slider = QSlider(Qt.Orientation.Horizontal)
        self.timer2_slider.setRange(1, 100)
        self.timer2_slider.setValue(int(manual_timer2_duration * 100))
        self.timer2_slider.valueChanged.connect(self.update_timer2_slider)
        self.timer2_slider.setStyleSheet(self.slider.styleSheet())
        timer2_row.addWidget(self.timer2_slider, 2)

        self.timer2_value = QLabel(f"{manual_timer2_duration:.2f}s")
        self.timer2_value.setStyleSheet("color: #F4F4F4; font-size: 13px; min-width: 48px;")
        timer2_row.addWidget(self.timer2_value)

        self.timer2_key_label = QLabel("Not Set")
        self.timer2_key_label.setStyleSheet("color: #ff6666; font-weight: normal; min-width: 60px; text-align: center;")
        timer2_row.addWidget(self.timer2_key_label)

        timer2_buttons = QHBoxLayout()
        self.timer2_set_button = QPushButton("Set")
        self.timer2_set_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #23263A;
                color: white;
                border: 1px solid #666;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: #2A2F3A; }}
        """)
        self.timer2_set_button.clicked.connect(lambda: self.set_timer_key(2))
        timer2_buttons.addWidget(self.timer2_set_button)

        timer2_clear = QPushButton("Clear")
        timer2_clear.setStyleSheet("""
            QPushButton {
                background-color: #664444;
                color: white;
                border: 1px solid #666;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #775555; }
        """)
        timer2_clear.clicked.connect(lambda: self.clear_timer_key(2))
        timer2_buttons.addWidget(timer2_clear)

        timer2_test = QPushButton("Test")
        timer2_test.setStyleSheet("""
            QPushButton {
                background-color: #446644;
                color: white;
                border: 1px solid #666;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #557755; }
        """)
        timer2_test.clicked.connect(lambda: self.test_timer(2))
        timer2_buttons.addWidget(timer2_test)

        timer2_row.addLayout(timer2_buttons)
        manual_layout.addLayout(timer2_row)

        manual_group.setLayout(manual_layout)
        shooting_layout.addWidget(manual_group)

        shooting_layout.addStretch()
        shooting_tab.setLayout(shooting_layout)
        return shooting_tab

    def create_macros_tab(self):
        macros_tab = QWidget()
        main_layout = QVBoxLayout()
        
        # Control section
        control_layout = QHBoxLayout()
        
        # Enable/Disable macros
        self.macros_toggle = QCheckBox("Enable Macros")
        self.macros_toggle.setChecked(True)
        self.macros_toggle.setStyleSheet(f"""
            QCheckBox {{
                color: white;
                font-size: 14px;
                padding: 5px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: #23263A;
                border: 2px solid #666;
                border-radius: 4px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.accent_color};
                border: 2px solid {self.accent_color};
                border-radius: 4px;
            }}
        """)
        self.macros_toggle.stateChanged.connect(self.toggle_macros)
        control_layout.addWidget(self.macros_toggle)
        
        # Test button
        test_button = QPushButton("Test Macro System")
        test_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.accent_color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self.accent_color}CC;
            }}
        """)
        test_button.clicked.connect(self.test_macro_system)
        control_layout.addWidget(test_button)
        
        control_layout.addStretch()
        main_layout.addLayout(control_layout)
        
        # Description
        desc = QLabel("Assign keys to dribble moves. Click 'Set Key' and press the key you want to use.")
        desc.setStyleSheet("color: #8F93A2; font-size: 12px; padding: 5px;")
        main_layout.addWidget(desc)
        
        # Status label
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #66ff66; font-size: 12px; padding: 5px;")
        main_layout.addWidget(self.status_label)
        
        # Scroll area for moves
        scroll = QScrollArea()
        scroll.setStyleSheet("background-color: transparent; border: 1px solid #333; border-radius: 8px;")
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        self.macro_widgets = {}
        
        for move_name, move_data in DRIBBLE_MOVES.items():
            group = QGroupBox(move_name)
            group.setStyleSheet("""
                QGroupBox {
                    color: white;
                    border: 2px solid #333;
                    border-radius: 8px;
                    margin: 5px;
                    padding-top: 15px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 8px 0 8px;
                }
            """)
            
            group_layout = QHBoxLayout()
            
            # Show sequences
            sequences_text = " / ".join([" → ".join(seq).upper() for seq in move_data["sequences"]])
            seq_label = QLabel(f"Sequences: {sequences_text}")
            seq_label.setStyleSheet("color: #8F93A2; font-weight: normal; font-size: 12px;")
            group_layout.addWidget(seq_label)
            
            group_layout.addStretch()
            
            # Current key display
            key_label = QLabel("Not Set")
            key_label.setStyleSheet("color: #ff6666; font-weight: normal; min-width: 60px; text-align: center;")
            group_layout.addWidget(key_label)
            
            # Buttons
            buttons_layout = QHBoxLayout()
            
            set_button = QPushButton("Set Key")
            set_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #23263A;
                    color: white;
                    border: 1px solid #666;
                    padding: 4px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                }}
                QPushButton:hover {{ background-color: #2A2F3A; }}
            """)
            set_button.clicked.connect(lambda checked, name=move_name: self.set_macro_key(name))
            buttons_layout.addWidget(set_button)
            
            test_move_button = QPushButton("Test")
            test_move_button.setStyleSheet("""
                QPushButton {
                    background-color: #446644;
                    color: white;
                    border: 1px solid #666;
                    padding: 4px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover { background-color: #557755; }
            """)
            test_move_button.clicked.connect(lambda checked, name=move_name: self.test_individual_macro(name))
            buttons_layout.addWidget(test_move_button)
            
            clear_button = QPushButton("Clear")
            clear_button.setStyleSheet("""
                QPushButton {
                    background-color: #664444;
                    color: white;
                    border: 1px solid #666;
                    padding: 4px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover { background-color: #775555; }
            """)
            clear_button.clicked.connect(lambda checked, name=move_name: self.clear_macro_key(name))
            buttons_layout.addWidget(clear_button)
            
            group_layout.addLayout(buttons_layout)
            group.setLayout(group_layout)
            scroll_layout.addWidget(group)
            
            self.macro_widgets[move_name] = {
                'key_label': key_label,
                'set_button': set_button
            }
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)
        
        macros_tab.setLayout(main_layout)
        return macros_tab

    def create_settings_tab(self):
        settings_tab = QWidget()
        layout = QVBoxLayout()
        layout.addSpacing(40)
        
        accent_label = QLabel("Accent Color:")
        accent_label.setStyleSheet("color: #8F93A2; font-size: 15px; font-weight: bold;")
        layout.addWidget(accent_label)
        
        color_btn = QPushButton()
        color_btn.setText(self.accent_color)
        color_btn.setStyleSheet(f"background: {self.accent_color}; color: #fff; border-radius: 8px; font-size: 16px; padding: 8px 24px; margin: 10px 0;")
        
        def pick_color():
            dlg = QColorDialog()
            dlg.setCurrentColor(Qt.GlobalColor.blue)
            if dlg.exec():
                new_color = dlg.currentColor().name()
                self.accent_color = new_color
                color_btn.setText(new_color)
                color_btn.setStyleSheet(f"background: {new_color}; color: #fff; border-radius: 8px; font-size: 16px; padding: 8px 24px; margin: 10px 0;")
                self.refresh_accent_color()
        
        color_btn.clicked.connect(pick_color)
        layout.addWidget(color_btn)
        layout.addStretch(1)
        settings_tab.setLayout(layout)
        return settings_tab

    def refresh_accent_color(self):
        # Refresh all widgets that use accent color
        accent = self.accent_color
        self.sidebar.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                color: #8F93A2;
                font-size: 18px;
                border: none;
                padding-top: 24px;
                font-weight: bold;
            }}
            QListWidget::item:selected {{
                background: #23263A;
                color: {accent};
                border-radius: 8px;
            }}
        """)
        
        self.set_general_tab_style()
        
        # Update sliders
        slider_style = f"""
            QSlider::groove:horizontal {{
                border: none;
                height: 8px;
                background: #23263A;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {accent};
                border: none;
                width: 22px;
                height: 22px;
                margin: -8px 0;
                border-radius: 11px;
                box-shadow: 0 2px 8px {accent}44;
            }}
            QSlider::sub-page:horizontal {{
                background: {accent};
                border-radius: 4px;
            }}
            QSlider::add-page:horizontal {{
                background: #23263A;
                border-radius: 4px;
            }}
        """
        self.slider.setStyleSheet(slider_style)
        self.monitor_top.setStyleSheet(slider_style)
        self.monitor_left.setStyleSheet(slider_style)
        self.timer1_slider.setStyleSheet(slider_style)
        self.timer2_slider.setStyleSheet(slider_style)

    # All the original functionality methods
    def toggle_macros(self, state):
        global macros_enabled
        macros_enabled = (state == Qt.CheckState.Checked)
        status = "Enabled" if macros_enabled else "Disabled"
        color = "#66ff66" if macros_enabled else "#ff6666"
        self.status_label.setText(f"Status: Macros {status}")
        self.status_label.setStyleSheet(f"color: {color}; font-size: 12px; padding: 5px;")
        print(f"[MACRO] Macros {status}")

    def test_macro_system(self):
        print("[TEST] Testing macro system...")
        self.status_label.setText("Status: Testing macro system...")
        self.status_label.setStyleSheet("color: #ffff66; font-size: 12px; padding: 5px;")
        
        try:
            keyboard_controller.press('1')
            keyboard_controller.release('1')
            print("[TEST] Keyboard controller working")
            self.status_label.setText("Status: Macro system working - keyboard controller OK")
            self.status_label.setStyleSheet("color: #66ff66; font-size: 12px; padding: 5px;")
        except Exception as e:
            print(f"[TEST ERROR] Keyboard controller failed: {e}")
            self.status_label.setText("Status: ERROR - Keyboard controller failed")
            self.status_label.setStyleSheet("color: #ff6666; font-size: 12px; padding: 5px;")

    def test_individual_macro(self, move_name):
        print(f"[TEST] Testing {move_name}")
        threading.Thread(target=execute_macro, args=(move_name,), daemon=True).start()

    def test_timer(self, timer_num):
        if timer_num == 1:
            duration = manual_timer1_duration
        else:
            duration = manual_timer2_duration
        print(f"[TEST] Testing Timer {timer_num} with duration {duration:.2f}s")
        threading.Thread(target=execute_manual_timing, args=(duration,), daemon=True).start()

    def set_macro_key(self, move_name):
        button = self.macro_widgets[move_name]['set_button']
        button.setText("Press a key...")
        button.setEnabled(False)
        
        def on_key_press(key):
            try:
                if hasattr(key, 'char') and key.char is not None:
                    key_char = key.char.lower()
                else:
                    key_name = str(key).replace('Key.', '').lower()
                    key_char = key_name
                
                print(f"[DEBUG] Setting key '{key_char}' for {move_name}")
                
                DRIBBLE_MOVES[move_name]['assigned_key'] = key_char
                
                self.macro_widgets[move_name]['key_label'].setText(key_char.upper())
                self.macro_widgets[move_name]['key_label'].setStyleSheet("color: #66ff66; font-weight: normal; min-width: 60px; text-align: center;")
                button.setText("Set Key")
                button.setEnabled(True)
                
                print(f"[MACRO] Assigned '{key_char}' to {move_name}")
                return False
            except Exception as e:
                print(f"[DEBUG ERROR] Set key error: {e}")
                button.setText("Set Key")
                button.setEnabled(True)
                return False
        
        temp_listener = Listener(on_press=on_key_press)
        temp_listener.start()

    def clear_macro_key(self, move_name):
        DRIBBLE_MOVES[move_name]['assigned_key'] = None
        self.macro_widgets[move_name]['key_label'].setText("Not Set")
        self.macro_widgets[move_name]['key_label'].setStyleSheet("color: #ff6666; font-weight: normal; min-width: 60px; text-align: center;")
        print(f"[MACRO] Cleared key for {move_name}")

    def start_macro_listener(self):
        def on_key_press(key):
            try:
                if hasattr(key, 'char') and key.char is not None:
                    key_char = key.char.lower()
                else:
                    key_name = str(key).replace('Key.', '').lower()
                    key_char = key_name
                
                print(f"[DEBUG] Key pressed: {key_char}")
                
                if not is_roblox_active():
                    return
                
                print(f"[DEBUG] Roblox is active, checking for key: {key_char}")
                
                global manual_timer1_key, manual_timer2_key, manual_timer1_duration, manual_timer2_duration
                
                if manual_timer1_key and manual_timer1_key.lower() == key_char:
                    print(f"[DEBUG] Found Timer 1 key {key_char}, duration: {manual_timer1_duration:.2f}")
                    threading.Thread(target=execute_manual_timing, args=(manual_timer1_duration,), daemon=True).start()
                    return
                    
                if manual_timer2_key and manual_timer2_key.lower() == key_char:
                    print(f"[DEBUG] Found Timer 2 key {key_char}, duration: {manual_timer2_duration:.2f}")
                    threading.Thread(target=execute_manual_timing, args=(manual_timer2_duration,), daemon=True).start()
                    return
                
                for move_name, move_data in DRIBBLE_MOVES.items():
                    assigned_key = move_data['assigned_key']
                    if assigned_key and assigned_key.lower() == key_char:
                        print(f"[DEBUG] Found macro {move_name} for key {key_char}")
                        threading.Thread(target=execute_macro, args=(move_name,), daemon=True).start()
                        break
            except Exception as e:
                print(f"[DEBUG ERROR] Key listener error: {e}")
        
        print("[DEBUG] Starting macro key listener...")
        self.key_listener = Listener(on_press=on_key_press)
        self.key_listener.start()

    def update_slider(self, value):
        global trigger_percent
        trigger_percent = value
        self.slider_label.setText(f"{value}%")

    def update_monitor_top(self, value):
        global monitor
        monitor["top"] = value
        self.monitor_top_label.setText(str(value))

    def update_monitor_left(self, value):
        global monitor
        monitor["left"] = value
        self.monitor_left_label.setText(str(value))

    def reset_meter_detection(self):
        global max_meter_height, locked, last_percent, smoothed_percent, triggered
        max_meter_height = 0
        locked = False
        last_percent = -1
        smoothed_percent = 0
        triggered = False
        self.autotime_status.setText("Status: Meter detection reset - waiting for new meter...")
        self.autotime_status.setStyleSheet("color: #66ff66; font-size: 12px; padding: 5px;")
        print("[AUTOTIME] Meter detection reset")

    def update_autotime_status(self):
        global last_percent, max_meter_height, locked, triggered, manual_timing_active
        
        if manual_timing_active:
            self.autotime_status.setText("Status: Manual timing active - AutoTime paused")
            self.autotime_status.setStyleSheet("color: #ff9900; font-size: 12px; padding: 5px;")
        elif last_percent >= 0:
            status = f"Meter: {last_percent}% | Max Height: {max_meter_height} | {'Locked' if locked else 'Detecting'}"
            if triggered:
                status += " | TRIGGERED!"
                color = "#ffff66"
            else:
                color = "#66ff66"
            self.autotime_status.setText(status)
            self.autotime_status.setStyleSheet(f"color: {color}; font-size: 12px; padding: 5px;")
        else:
            self.autotime_status.setText("Status: Waiting for meter...")
            self.autotime_status.setStyleSheet("color: #8F93A2; font-size: 12px; padding: 5px;")

    def update_timer1_slider(self, value):
        global manual_timer1_duration
        manual_timer1_duration = value / 100.0
        self.timer1_value.setText(f"{manual_timer1_duration:.2f}s")

    def update_timer2_slider(self, value):
        global manual_timer2_duration
        manual_timer2_duration = value / 100.0
        self.timer2_value.setText(f"{manual_timer2_duration:.2f}s")

    def set_timer_key(self, timer_num):
        if timer_num == 1:
            button = self.timer1_set_button
            key_label = self.timer1_key_label
        else:
            button = self.timer2_set_button
            key_label = self.timer2_key_label
            
        button.setText("Press a key...")
        button.setEnabled(False)
        
        def on_key_press(key):
            try:
                if hasattr(key, 'char') and key.char is not None:
                    key_char = key.char.lower()
                else:
                    key_name = str(key).replace('Key.', '').lower()
                    key_char = key_name
                
                print(f"[DEBUG] Setting timer {timer_num} key to '{key_char}'")
                
                global manual_timer1_key, manual_timer2_key
                if timer_num == 1:
                    manual_timer1_key = key_char
                else:
                    manual_timer2_key = key_char
                
                key_label.setText(key_char.upper())
                key_label.setStyleSheet("color: #66ff66; font-weight: normal; min-width: 60px; text-align: center;")
                button.setText("Set")
                button.setEnabled(True)
                
                print(f"[TIMER] Assigned '{key_char}' to Timer {timer_num}")
                return False
            except Exception as e:
                print(f"[DEBUG ERROR] Timer key set error: {e}")
                button.setText("Set")
                button.setEnabled(True)
                return False
        
        temp_listener = Listener(on_press=on_key_press)
        temp_listener.start()

    def clear_timer_key(self, timer_num):
        global manual_timer1_key, manual_timer2_key
        if timer_num == 1:
            manual_timer1_key = None
            self.timer1_key_label.setText("Not Set")
            self.timer1_key_label.setStyleSheet("color: #ff6666; font-weight: normal; min-width: 60px; text-align: center;")
            print("[TIMER] Cleared Timer 1 key")
        else:
            manual_timer2_key = None
            self.timer2_key_label.setText("Not Set")
            self.timer2_key_label.setStyleSheet("color: #ff6666; font-weight: normal; min-width: 60px; text-align: center;")
            print("[TIMER] Cleared Timer 2 key")

    def toggle_changed(self, state):
        global autotime_enabled
        autotime_enabled = (state == Qt.CheckState.Checked)

    def closeEvent(self, event):
        if hasattr(self, 'key_listener'):
            self.key_listener.stop()
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
        event.accept()

# ===== DETECTION LOOP =====
def detection_loop():
    global autotime_enabled, trigger_percent, max_meter_height, locked, last_percent, smoothed_percent, triggered, manual_timing_active
    sct = mss.mss()
    prev_detected = False

    while True:
        if not is_roblox_active():
            time.sleep(0.1)
            continue

        if manual_timing_active:
            time.sleep(0.01)
            continue

        img = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, lower_pink, upper_pink)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        meter_found = False
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = h / float(w) if w != 0 else 0
            
            if aspect_ratio > 3 and h > 20:
                meter_found = True
                
                if manual_max_height:
                    max_meter_height = manual_max_height
                    locked = True
                elif not locked and h >= lock_after_height:
                    max_meter_height = h
                    locked = True
                    print(f"[=] Max height locked at: {max_meter_height}")
                
                if max_meter_height > 0:
                    raw_percent = (h / max_meter_height) * 100
                    raw_percent = max(0, min(100, raw_percent))
                    
                    smoothed_percent = smoothed_percent * 0.85 + raw_percent * 0.15
                    rounded_percent = int(smoothed_percent)
                    
                    if not triggered and autotime_enabled and not manual_timing_active and rounded_percent >= trigger_percent:
                        print(f"[🔫] AutoTime triggered at {rounded_percent}% — pressing E")
                        keyboard_controller.press('e')
                        keyboard_controller.release('e')
                        triggered = True
                    
                    if rounded_percent != last_percent:
                        print(f"[+] Meter Fill: {rounded_percent}%")
                        last_percent = rounded_percent
                break

        if not meter_found and prev_detected:
            print("[-] Meter disappeared.")
            last_percent = -1
            smoothed_percent = 0
            triggered = False

        prev_detected = meter_found
        time.sleep(0.005)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main_window = XOTApp()
    main_window.show()
    threading.Thread(target=detection_loop, daemon=True).start()
    
    print("=== XOT Gaming Assistant Started ===")
    print("\nFeatures:")
    print("- AutoTime: Computer vision meter detection with automatic E key pressing")
    print("- Manual Timing: Custom hold durations with assignable keybinds")
    print("- Dribble Macros: 10 different basketball moves with key assignments")
    print("- Modern UI: Customizable accent colors and professional design")
    print("\nUse the GUI to configure all settings and key assignments\n")
    
    sys.exit(app.exec())
