#!/usr/bin/env python3
"""
QUANTUM DOT - Complete Desktop Application
A polished, hacker-themed control panel with three tabs and full functionality.
"""

import sys
import json
import random
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from collections import deque

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                               QComboBox, QLineEdit, QTextEdit, QCheckBox,
                               QScrollArea, QFrame, QSizePolicy, QMessageBox,
                               QProgressBar, QGraphicsDropShadowEffect)
from PySide6.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve, 
                           QSequentialAnimationGroup, Property, QSize, 
                           QPoint, QRect)
from PySide6.QtGui import (QFont, QFontDatabase, QPalette, QColor, 
                          QPainter, QLinearGradient, QPen, QBrush,
                          QPainterPath, QKeySequence, QShortcut,
                          QMouseEvent, QEnterEvent)


@dataclass
class Profile:
    """Profile data structure for saving/loading settings."""
    name: str
    description: str
    main_toggles: Dict[str, bool]
    main_dropdowns: Dict[str, str]
    esp_toggles: Dict[str, bool]
    created: str = ""


class QuantumDotApp(QMainWindow):
    """Main application window for Quantum Dot control panel."""
    
    def __init__(self):
        super().__init__()
        self.profiles: List[Profile] = []
        self.current_profile = Profile("Default", "", {}, {}, {})
        self.undo_stack = deque(maxlen=10)
        self.redo_stack = deque(maxlen=10)
        self.preview_mode = False
        self.ui_locked = False
        
        self.setup_application()
        self.create_assets()
        self.setup_ui()
        self.setup_animations()
        self.load_profiles()
        self.setup_shortcuts()
        
    def setup_application(self):
        """Configure application window and styles."""
        self.setWindowTitle("QUANTUM DOT")
        self.setFixedSize(900, 600)
        self.setStyleSheet(self.get_stylesheet())
        
        # Center on screen
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
    def get_stylesheet(self) -> str:
        """Return the complete QSS stylesheet for hacker aesthetic."""
        return """
        /* Main Window */
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0a0a12, stop:0.5 #121018, stop:1 #0a0a12);
            border: 1px solid #2a1e2a;
            border-radius: 12px;
        }
        
        /* Central Widget */
        #centralWidget {
            background: transparent;
            border-left: 3px solid #c22b2b;
        }
        
        /* Header */
        #header {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1a1525, stop:0.5 #2a1e3a, stop:1 #1a1525);
            border-bottom: 1px solid #332244;
            border-radius: 8px 8px 0 0;
        }
        
        #title {
            color: #ffffff;
            font-family: "Segoe UI", "Arial";
            font-size: 28px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 3px;
        }
        
        #subtitle {
            color: #c22b2b;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 11px;
            letter-spacing: 1px;
        }
        
        /* Tab Buttons */
        QPushButton[tabButton="true"] {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2a243a, stop:0.5 #1e1a2a, stop:1 #2a243a);
            color: #a0a0c0;
            border: 1px solid #3a2e4a;
            border-radius: 15px;
            padding: 8px 20px;
            font-family: "Segoe UI";
            font-size: 12px;
            font-weight: normal;
            min-width: 80px;
        }
        
        QPushButton[tabButton="true"]:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3a2e4a, stop:0.5 #2a243a, stop:1 #3a2e4a);
            color: #c0c0ff;
            border: 1px solid #4a3e5a;
        }
        
        QPushButton[tabButton="true"]:checked {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #c22b2b, stop:0.5 #a21b1b, stop:1 #c22b2b);
            color: #ffffff;
            border: 1px solid #d23b3b;
            font-weight: bold;
        }
        
        /* Control Panels */
        #controlPanel {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1a1628, stop:0.3 #1f1b2b, stop:1 #1a1628);
            border: 1px solid #2a2640;
            border-radius: 8px;
        }
        
        /* Control Rows */
        #controlRow {
            background: transparent;
            border: none;
        }
        
        QLabel[controlLabel="true"] {
            color: #c0c0e0;
            font-family: "Consolas", monospace;
            font-size: 11px;
            font-weight: normal;
            padding: 2px;
        }
        
        /* Dropdowns */
        QComboBox {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2a2640, stop:1 #1e1a30);
            color: #a0a0c0;
            border: 1px solid #3a3650;
            border-radius: 4px;
            padding: 4px 8px;
            font-family: "Consolas", monospace;
            font-size: 10px;
            min-width: 80px;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid #a0a0c0;
            width: 0;
            height: 0;
        }
        
        QComboBox QAbstractItemView {
            background: #1a1628;
            border: 1px solid #3a3650;
            color: #a0a0c0;
            selection-background-color: #c22b2b;
        }
        
        /* Toggle Buttons */
        QPushButton[toggleButton="true"] {
            background: #c22b2b;
            border: 1px solid #d23b3b;
            border-radius: 3px;
            min-width: 16px;
            max-width: 16px;
            min-height: 16px;
            max-height: 16px;
        }
        
        QPushButton[toggleButton="true"]:checked {
            background: #27ae60;
            border: 1px solid #37be70;
        }
        
        /* ESP Feature Rows */
        #espRow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1a1628, stop:0.02 #2a1e3a, stop:1 #1a1628);
            border: 1px solid #252136;
            border-radius: 4px;
        }
        
        QLabel[espLabel="true"] {
            color: #b0b0d0;
            font-family: "Consolas", monospace;
            font-size: 10px;
            padding: 4px 8px;
        }
        
        /* Search Box */
        QLineEdit {
            background: #1a1628;
            color: #a0a0c0;
            border: 1px solid #3a3650;
            border-radius: 4px;
            padding: 6px 8px;
            font-family: "Consolas", monospace;
            font-size: 11px;
        }
        
        QLineEdit:focus {
            border: 1px solid #c22b2b;
        }
        
        /* Profile Controls */
        QTextEdit {
            background: #1a1628;
            color: #a0a0c0;
            border: 1px solid #3a3650;
            border-radius: 4px;
            padding: 6px 8px;
            font-family: "Consolas", monospace;
            font-size: 11px;
        }
        
        /* Action Buttons */
        QPushButton[actionButton="true"] {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2a2640, stop:0.5 #1e1a30, stop:1 #2a2640);
            color: #a0a0c0;
            border: 1px solid #3a3650;
            border-radius: 4px;
            padding: 6px 12px;
            font-family: "Segoe UI";
            font-size: 11px;
            font-weight: normal;
        }
        
        QPushButton[actionButton="true"]:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3a3650, stop:0.5 #2a2640, stop:1 #3a3650);
            border: 1px solid #4a4660;
        }
        
        QPushButton[actionButton="true"]:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1a1620, stop:0.5 #2a2640, stop:1 #1a1620);
        }
        
        /* Toast Message */
        #toast {
            background: #c22b2b;
            color: #ffffff;
            border: 1px solid #d23b3b;
            border-radius: 4px;
            padding: 8px 12px;
            font-family: "Consolas", monospace;
            font-size: 10px;
        }
        
        /* Graph Canvas */
        #graphCanvas {
            background: #151220;
            border: 1px solid #2a2640;
            border-radius: 4px;
        }
        """
    
    def create_assets(self):
        """Create necessary directories and placeholder assets."""
        assets_dir = Path("assets")
        assets_dir.mkdir(exist_ok=True)
        
        # Create placeholder note
        note_file = assets_dir / "PLACEHOLDER_ASSETS.txt"
        note_file.write_text("""Placeholder Assets Directory

Replace these files with your actual assets:
- banner.png: Header background image (900x80 recommended)
- logo.png: Application icon (64x64 recommended)

The application will work without these files - placeholder graphics are used.
""")
    
    def setup_ui(self):
        """Create and arrange all UI components."""
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create header
        self.create_header(main_layout)
        
        # Create tab buttons
        self.create_tab_buttons(main_layout)
        
        # Create tab content area
        self.create_tab_content(main_layout)
        
        # Create status bar
        self.create_status_bar(main_layout)
        
    def create_header(self, parent_layout):
        """Create the application header with title and subtitle."""
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(80)
        
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Main title
        title = QLabel("QUANTUM DOT")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        
        # Subtitle with red underline effect
        subtitle = QLabel("QUANTUM SILENT TECHNOLOGY")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        
        # Red underline
        underline = QWidget()
        underline.setFixedHeight(2)
        underline.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #c22b2b, stop:1 transparent);")
        underline.setFixedWidth(200)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addWidget(underline, 0, Qt.AlignCenter)
        
        parent_layout.addWidget(header)
    
    def create_tab_buttons(self, parent_layout):
        """Create the tab navigation buttons."""
        tab_widget = QWidget()
        tab_widget.setFixedHeight(50)
        tab_widget.setStyleSheet("background: transparent;")
        
        tab_layout = QHBoxLayout(tab_widget)
        tab_layout.setContentsMargins(20, 5, 20, 5)
        tab_layout.setSpacing(10)
        
        self.tab_buttons = {}
        tabs = ["Main", "Esp", "Profile"]
        
        for tab_name in tabs:
            btn = QPushButton(tab_name)
            btn.setObjectName("tabButton")
            btn.setProperty("tabButton", "true")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, t=tab_name: self.switch_tab(t))
            
            if tab_name == "Main":
                btn.setChecked(True)
                
            tab_layout.addWidget(btn)
            self.tab_buttons[tab_name] = btn
        
        tab_layout.addStretch()
        
        # Add lock UI checkbox
        lock_checkbox = QCheckBox("Lock UI")
        lock_checkbox.setStyleSheet("""
            QCheckBox {
                color: #a0a0c0;
                font-family: "Consolas";
                font-size: 10px;
            }
            QCheckBox::indicator {
                width: 12px;
                height: 12px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #3a3650;
                background: #1a1628;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #c22b2b;
                background: #c22b2b;
            }
        """)
        lock_checkbox.stateChanged.connect(self.toggle_ui_lock)
        tab_layout.addWidget(lock_checkbox)
        
        parent_layout.addWidget(tab_widget)
    
    def create_tab_content(self, parent_layout):
        """Create the main tab content area."""
        self.tab_content = QWidget()
        self.tab_content.setStyleSheet("background: transparent;")
        
        self.tab_stack_layout = QVBoxLayout(self.tab_content)
        self.tab_stack_layout.setContentsMargins(20, 10, 20, 10)
        
        # Create individual tabs
        self.main_tab = self.create_main_tab()
        self.esp_tab = self.create_esp_tab()
        self.profile_tab = self.create_profile_tab()
        
        # Add to stack (initially show main tab)
        self.tab_stack_layout.addWidget(self.main_tab)
        self.current_tab = "Main"
        
        parent_layout.addWidget(self.tab_content)
    
    def create_main_tab(self) -> QWidget:
        """Create the Main tab with controls and graphs."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Graphs section
        graphs_widget = self.create_graphs_section()
        layout.addWidget(graphs_widget)
        
        # Controls section
        controls_widget = self.create_controls_section()
        layout.addWidget(controls_widget)
        
        return tab
    
    def create_graphs_section(self) -> QWidget:
        """Create the graphs/visualization section."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(10)
        
        # QR code placeholder
        qr_placeholder = QLabel("◼ QR CODE")
        qr_placeholder.setStyleSheet("""
            QLabel {
                background: #151220;
                color: #3a3650;
                border: 1px solid #2a2640;
                border-radius: 4px;
                font-family: "Consolas";
                font-size: 10px;
                padding: 20px;
                min-width: 80px;
                max-width: 80px;
                min-height: 80px;
                max-height: 80px;
            }
        """)
        qr_placeholder.setAlignment(Qt.AlignCenter)
        
        # Session activity graph
        session_graph = GraphWidget("Session Activity")
        session_graph.setFixedHeight(80)
        
        # Latency graph
        latency_graph = GraphWidget("Latency")
        latency_graph.setFixedHeight(80)
        
        layout.addWidget(qr_placeholder)
        layout.addWidget(session_graph)
        layout.addWidget(latency_graph)
        
        return widget
    
    def create_controls_section(self) -> QWidget:
        """Create the 2-column control grid."""
        widget = QWidget()
        widget.setObjectName("controlPanel")
        layout = QHBoxLayout(widget)
        layout.setSpacing(20)
        
        # Left column
        left_column = self.create_control_column([
            "MagNet Pull", "Speed 20X", "Teli Kill", "Glitch Fire",
            "No Reload", "Wallhack", "Rapid Fire", "Ignore Knock"
        ])
        
        # Right column  
        right_column = self.create_control_column([
            "Aim Assist", "Trigger Bot", "No Recoil", "Silent Aim",
            "Speed Hack", "Fly Hack", "God Mode", "Anti-Cheat"
        ])
        
        layout.addWidget(left_column)
        layout.addWidget(right_column)
        
        return widget
    
    def create_control_column(self, control_names: List[str]) -> QWidget:
        """Create a column of control rows."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.control_toggles = {}
        self.control_dropdowns = {}
        
        for name in control_names:
            row = self.create_control_row(name)
            layout.addWidget(row)
            
        layout.addStretch()
        return widget
    
    def create_control_row(self, name: str) -> QWidget:
        """Create a single control row with label, dropdown, and toggle."""
        row = QWidget()
        row.setObjectName("controlRow")
        row.setFixedHeight(30)
        
        layout = QHBoxLayout(row)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)
        
        # Label
        label = QLabel(name)
        label.setObjectName("controlLabel")
        label.setProperty("controlLabel", "true")
        
        # Dropdown
        dropdown = QComboBox()
        dropdown.addItems(["NONE", "LOW", "MEDIUM", "HIGH", "EXTREME"])
        dropdown.setCurrentText("NONE")
        dropdown.currentTextChanged.connect(
            lambda text, n=name: self.on_dropdown_changed(n, text)
        )
        
        # Toggle button
        toggle = QPushButton()
        toggle.setObjectName("toggleButton")
        toggle.setProperty("toggleButton", "true")
        toggle.setCheckable(True)
        toggle.clicked.connect(
            lambda checked, n=name: self.on_toggle_changed(n, checked)
        )
        
        layout.addWidget(label)
        layout.addWidget(dropdown)
        layout.addWidget(toggle)
        
        # Store references
        self.control_toggles[name] = toggle
        self.control_dropdowns[name] = dropdown
        
        return row
    
    def create_esp_tab(self) -> QWidget:
        """Create the ESP tab with feature toggles."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        
        # Search and filter section
        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search ESP features...")
        search_input.textChanged.connect(self.filter_esp_features)
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.setProperty("actionButton", "true")
        select_all_btn.clicked.connect(self.select_all_esp)
        
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.setProperty("actionButton", "true")
        deselect_all_btn.clicked.connect(self.deselect_all_esp)
        
        search_layout.addWidget(search_input)
        search_layout.addStretch()
        search_layout.addWidget(select_all_btn)
        search_layout.addWidget(deselect_all_btn)
        
        layout.addWidget(search_widget)
        
        # ESP features scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #1a1628;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3a3650;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4a4660;
            }
        """)
        
        esp_container = QWidget()
        self.esp_layout = QVBoxLayout(esp_container)
        self.esp_layout.setSpacing(5)
        
        # ESP features list
        self.esp_features = [
            "Line", "Box", "Box Corner", "Moco Style", "Shuriken",
            "Black Sky", "Rainbow", "Glow", "Curved Line", "Full Box",
            "Fill Box", "Skeleton", "Distance", "Name Tag", "Health Bar",
            "Weapon Display", "360° Radar", "Minimap Sync", "Team/Enemy Color", 
            "Stream-Proof Mode"
        ]
        
        self.esp_toggles = {}
        for feature in self.esp_features:
            row = self.create_esp_row(feature)
            self.esp_layout.addWidget(row)
            
        self.esp_layout.addStretch()
        scroll.setWidget(esp_container)
        layout.addWidget(scroll)
        
        return tab
    
    def create_esp_row(self, feature: str) -> QWidget:
        """Create a single ESP feature row."""
        row = QWidget()
        row.setObjectName("espRow")
        row.setFixedHeight(35)
        
        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Feature label with special character
        label = QLabel(f"ᵎ!ᵎ Esp – {feature}")
        label.setObjectName("espLabel")
        label.setProperty("espLabel", "true")
        
        # Toggle button
        toggle = QPushButton()
        toggle.setObjectName("toggleButton")
        toggle.setProperty("toggleButton", "true")
        toggle.setCheckable(True)
        toggle.clicked.connect(
            lambda checked, f=feature: self.on_esp_toggle_changed(f, checked)
        )
        
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(toggle)
        
        self.esp_toggles[feature] = toggle
        return row
    
    def create_profile_tab(self) -> QWidget:
        """Create the Profile tab for saving/loading settings."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Profile name
        name_layout = QHBoxLayout()
        name_label = QLabel("Profile Name:")
        name_label.setStyleSheet("color: #c0c0e0; font-family: Consolas; font-size: 11px;")
        
        self.profile_name_input = QLineEdit()
        self.profile_name_input.setPlaceholderText("Enter profile name...")
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.profile_name_input)
        layout.addLayout(name_layout)
        
        # Description
        desc_label = QLabel("Description:")
        desc_label.setStyleSheet("color: #c0c0e0; font-family: Consolas; font-size: 11px;")
        
        self.profile_desc_input = QTextEdit()
        self.profile_desc_input.setMaximumHeight(80)
        self.profile_desc_input.setPlaceholderText("Enter profile description...")
        
        layout.addWidget(desc_label)
        layout.addWidget(self.profile_desc_input)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Profile")
        save_btn.setProperty("actionButton", "true")
        save_btn.clicked.connect(self.save_profile)
        
        load_btn = QPushButton("Load Profile")
        load_btn.setProperty("actionButton", "true")
        load_btn.clicked.connect(self.load_profile)
        
        delete_btn = QPushButton("Delete Profile")
        delete_btn.setProperty("actionButton", "true")
        delete_btn.clicked.connect(self.delete_profile)
        
        export_btn = QPushButton("Export Profile")
        export_btn.setProperty("actionButton", "true")
        export_btn.clicked.connect(self.export_profile)
        
        import_btn = QPushButton("Import Profile")
        import_btn.setProperty("actionButton", "true")
        import_btn.clicked.connect(self.import_profile)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(load_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(export_btn)
        button_layout.addWidget(import_btn)
        
        layout.addLayout(button_layout)
        
        # Profile dropdown
        profile_layout = QHBoxLayout()
        profile_label = QLabel("Saved Profiles:")
        profile_label.setStyleSheet("color: #c0c0e0; font-family: Consolas; font-size: 11px;")
        
        self.profile_dropdown = QComboBox()
        self.profile_dropdown.currentTextChanged.connect(self.on_profile_selected)
        
        profile_layout.addWidget(profile_label)
        profile_layout.addWidget(self.profile_dropdown)
        layout.addLayout(profile_layout)
        
        # Preview area
        preview_label = QLabel("Active Features Preview:")
        preview_label.setStyleSheet("color: #c0c0e0; font-family: Consolas; font-size: 11px;")
        
        self.preview_area = QLabel("No active features")
        self.preview_area.setStyleSheet("""
            QLabel {
                background: #151220;
                color: #a0a0c0;
                border: 1px solid #2a2640;
                border-radius: 4px;
                padding: 10px;
                font-family: Consolas;
                font-size: 10px;
                min-height: 60px;
            }
        """)
        self.preview_area.setWordWrap(True)
        
        layout.addWidget(preview_label)
        layout.addWidget(self.preview_area)
        
        return tab
    
    def create_status_bar(self, parent_layout):
        """Create the status bar with toast messages."""
        status_widget = QWidget()
        status_widget.setFixedHeight(30)
        status_widget.setStyleSheet("background: transparent;")
        
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(20, 5, 20, 5)
        
        # Toast message area
        self.toast_label = QLabel("Ready")
        self.toast_label.setObjectName("toast")
        self.toast_label.setVisible(False)
        
        status_layout.addWidget(self.toast_label)
        status_layout.addStretch()
        
        # Preview mode indicator
        preview_label = QLabel("Preview Mode: OFF")
        preview_label.setStyleSheet("color: #a0a0c0; font-family: Consolas; font-size: 9px;")
        preview_label.setProperty("previewMode", "false")
        
        status_layout.addWidget(preview_label)
        
        parent_layout.addWidget(status_widget)
    
    def setup_animations(self):
        """Setup UI animations and timers."""
        # Graph animation timer
        self.graph_timer = QTimer()
        self.graph_timer.timeout.connect(self.update_graphs)
        self.graph_timer.start(100)  # Update every 100ms
        
        # Toast animation
        self.toast_animation = QPropertyAnimation(self.toast_label, b"windowOpacity")
        self.toast_animation.setDuration(2000)
        self.toast_animation.setStartValue(0.0)
        self.toast_animation.setEndValue(1.0)
        self.toast_animation.finished.connect(self.hide_toast)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Undo/Redo
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self.redo)
        
        # Toggle shortcuts for first 4 controls
        shortcuts = ["Ctrl+1", "Ctrl+2", "Ctrl+3", "Ctrl+4"]
        control_names = ["MagNet Pull", "Speed 20X", "Teli Kill", "Glitch Fire"]
        
        for shortcut, control in zip(shortcuts, control_names):
            QShortcut(QKeySequence(shortcut), self).activated.connect(
                lambda c=control: self.toggle_control(c)
            )
    
    def switch_tab(self, tab_name: str):
        """Switch between tabs with animation."""
        if tab_name == self.current_tab:
            return
            
        # Update button states
        for name, btn in self.tab_buttons.items():
            btn.setChecked(name == tab_name)
        
        # Remove current tab
        current_widget = self.tab_stack_layout.takeAt(0).widget()
        current_widget.setVisible(False)
        
        # Add new tab
        new_tab = getattr(self, f"{tab_name.lower()}_tab")
        self.tab_stack_layout.addWidget(new_tab)
        new_tab.setVisible(True)
        
        self.current_tab = tab_name
        
        # Show tab switch toast
        self.show_toast(f"Switched to {tab_name} tab")
    
    def toggle_control(self, control_name: str):
        """Toggle a control using keyboard shortcut."""
        if control_name in self.control_toggles:
            toggle = self.control_toggles[control_name]
            toggle.setChecked(not toggle.isChecked())
    
    def on_toggle_changed(self, control_name: str, state: bool):
        """Handle control toggle changes."""
        if self.ui_locked:
            return
            
        action = f"{control_name} {'ENABLED' if state else 'DISABLED'}"
        self.show_toast(action)
        
        if not self.preview_mode:
            self.save_state_to_undo_stack()
    
    def on_esp_toggle_changed(self, feature: str, state: bool):
        """Handle ESP toggle changes."""
        if self.ui_locked:
            return
            
        action = f"ESP {feature} {'ENABLED' if state else 'DISABLED'}"
        self.show_toast(action)
        
        if not self.preview_mode:
            self.save_state_to_undo_stack()
        self.update_preview()
    
    def on_dropdown_changed(self, control_name: str, value: str):
        """Handle dropdown selection changes."""
        if self.ui_locked:
            return
            
        if value != "NONE":
            self.show_toast(f"{control_name} set to {value}")
        
        if not self.preview_mode:
            self.save_state_to_undo_stack()
    
    def filter_esp_features(self, text: str):
        """Filter ESP features based on search text."""
        for i in range(self.esp_layout.count() - 1):  # -1 for stretch
            item = self.esp_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    feature_text = widget.findChild(QLabel).text().lower()
                    widget.setVisible(text.lower() in feature_text)
    
    def select_all_esp(self):
        """Select all visible ESP features."""
        for i in range(self.esp_layout.count() - 1):
            item = self.esp_layout.itemAt(i)
            if item and item.widget() and item.widget().isVisible():
                toggle = item.widget().findChild(QPushButton)
                if toggle:
                    toggle.setChecked(True)
    
    def deselect_all_esp(self):
        """Deselect all visible ESP features."""
        for i in range(self.esp_layout.count() - 1):
            item = self.esp_layout.itemAt(i)
            if item and item.widget() and item.widget().isVisible():
                toggle = item.widget().findChild(QPushButton)
                if toggle:
                    toggle.setChecked(False)
    
    def toggle_ui_lock(self, state: int):
        """Toggle UI lock state."""
        self.ui_locked = bool(state)
        lock_state = "LOCKED" if self.ui_locked else "UNLOCKED"
        self.show_toast(f"UI {lock_state}")
    
    def show_toast(self, message: str):
        """Show a temporary toast message."""
        self.toast_label.setText(message)
        self.toast_label.setVisible(True)
        
        # Start hide timer
        QTimer.singleShot(2000, self.hide_toast)
    
    def hide_toast(self):
        """Hide the toast message."""
        self.toast_label.setVisible(False)
    
    def update_graphs(self):
        """Update the animated graphs."""
        # This would update graph widgets in a real implementation
        pass
    
    def save_state_to_undo_stack(self):
        """Save current state to undo stack."""
        state = {
            "main_toggles": {name: btn.isChecked() for name, btn in self.control_toggles.items()},
            "esp_toggles": {name: btn.isChecked() for name, btn in self.esp_toggles.items()}
        }
        self.undo_stack.append(state)
        self.redo_stack.clear()
    
    def undo(self):
        """Undo last action."""
        if self.undo_stack and not self.ui_locked:
            state = self.undo_stack.pop()
            self.redo_stack.append(state)
            self.apply_state(state)
            self.show_toast("Undo")
    
    def redo(self):
        """Redo last undone action."""
        if self.redo_stack and not self.ui_locked:
            state = self.redo_stack.pop()
            self.undo_stack.append(state)
            self.apply_state(state)
            self.show_toast("Redo")
    
    def apply_state(self, state: Dict):
        """Apply a saved state to the UI."""
        for name, checked in state.get("main_toggles", {}).items():
            if name in self.control_toggles:
                self.control_toggles[name].setChecked(checked)
        
        for name, checked in state.get("esp_toggles", {}).items():
            if name in self.esp_toggles:
                self.esp_toggles[name].setChecked(checked)
    
    def save_profile(self):
        """Save current settings as a profile."""
        name = self.profile_name_input.text().strip()
        if not name:
            self.show_toast("Please enter a profile name")
            return
        
        # Collect current state
        main_toggles = {name: btn.isChecked() for name, btn in self.control_toggles.items()}
        main_dropdowns = {name: dropdown.currentText() for name, dropdown in self.control_dropdowns.items()}
        esp_toggles = {name: btn.isChecked() for name, btn in self.esp_toggles.items()}
        
        profile = Profile(
            name=name,
            description=self.profile_desc_input.toPlainText(),
            main_toggles=main_toggles,
            main_dropdowns=main_dropdowns,
            esp_toggles=esp_toggles
        )
        
        # Add or update profile
        existing_index = next((i for i, p in enumerate(self.profiles) if p.name == name), -1)
        if existing_index >= 0:
            self.profiles[existing_index] = profile
        else:
            self.profiles.append(profile)
        
        self.save_profiles()
        self.update_profile_dropdown()
        self.show_toast(f"Profile '{name}' saved")
    
    def load_profile(self):
        """Load selected profile."""
        name = self.profile_dropdown.currentText()
        if not name:
            return
        
        profile = next((p for p in self.profiles if p.name == name), None)
        if profile:
            self.apply_profile(profile)
            self.show_toast(f"Profile '{name}' loaded")
    
    def delete_profile(self):
        """Delete selected profile."""
        name = self.profile_dropdown.currentText()
        if not name or name == "Default":
            return
        
        self.profiles = [p for p in self.profiles if p.name != name]
        self.save_profiles()
        self.update_profile_dropdown()
        self.show_toast(f"Profile '{name}' deleted")
    
    def export_profile(self):
        """Export current profile to file."""
        # Implementation for exporting to JSON file
        self.show_toast("Export feature - Implement file dialog")
    
    def import_profile(self):
        """Import profile from file."""
        # Implementation for importing from JSON file
        self.show_toast("Import feature - Implement file dialog")
    
    def on_profile_selected(self, name: str):
        """Handle profile selection from dropdown."""
        if name:
            self.profile_name_input.setText(name)
            profile = next((p for p in self.profiles if p.name == name), None)
            if profile:
                self.profile_desc_input.setPlainText(profile.description)
    
    def apply_profile(self, profile: Profile):
        """Apply a profile to the UI."""
        for name, checked in profile.main_toggles.items():
            if name in self.control_toggles:
                self.control_toggles[name].setChecked(checked)
        
        for name, value in profile.main_dropdowns.items():
            if name in self.control_dropdowns:
                self.control_dropdowns[name].setCurrentText(value)
        
        for name, checked in profile.esp_toggles.items():
            if name in self.esp_toggles:
                self.esp_toggles[name].setChecked(checked)
        
        self.update_preview()
    
    def update_preview(self):
        """Update the active features preview."""
        active_features = []
        
        for name, toggle in self.control_toggles.items():
            if toggle.isChecked():
                active_features.append(name)
        
        for name, toggle in self.esp_toggles.items():
            if toggle.isChecked():
                active_features.append(f"ESP {name}")
        
        if active_features:
            self.preview_area.setText(", ".join(active_features))
        else:
            self.preview_area.setText("No active features")
    
    def load_profiles(self):
        """Load profiles from persistent storage."""
        # In a real implementation, this would load from a JSON file
        self.profiles = []
        self.update_profile_dropdown()
    
    def save_profiles(self):
        """Save profiles to persistent storage."""
        # In a real implementation, this would save to a JSON file
        pass
    
    def update_profile_dropdown(self):
        """Update the profile dropdown with current profiles."""
        self.profile_dropdown.clear()
        for profile in self.profiles:
            self.profile_dropdown.addItem(profile.name)


class GraphWidget(QWidget):
    """A simple animated graph widget."""
    
    def __init__(self, title: str):
        super().__init__()
        self.title = title
        self.data = [0] * 50
        self.setFixedHeight(80)
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)
    
    def update_data(self):
        """Update graph data with random values."""
        self.data.pop(0)
        self.data.append(random.randint(0, 100))
        self.update()
    
    def paintEvent(self, event):
        """Paint the graph."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(21, 18, 32))
        
        # Draw border
        painter.setPen(QPen(QColor(42, 38, 64), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        
        # Draw title
        painter.setPen(QPen(QColor(160, 160, 192)))
        painter.setFont(QFont("Consolas", 8))
        painter.drawText(5, 12, self.title)
        
        # Draw graph
        if len(self.data) > 1:
            width = self.width() - 10
            height = self.height() - 25
            x_step = width / (len(self.data) - 1)
            
            path = QPainterPath()
            path.moveTo(5, self.height() - 10 - (self.data[0] / 100 * height))
            
            for i, value in enumerate(self.data[1:], 1):
                x = 5 + i * x_step
                y = self.height() - 10 - (value / 100 * height)
                path.lineTo(x, y)
            
            # Draw graph line
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor(194, 43, 43))
            gradient.setColorAt(1, QColor(101, 31, 255))
            
            painter.setPen(QPen(QBrush(gradient), 2))
            painter.drawPath(path)
            
            # Draw fill
            fill_path = QPainterPath(path)
            fill_path.lineTo(self.width() - 5, self.height() - 10)
            fill_path.lineTo(5, self.height() - 10)
            fill_path.closeSubpath()
            
            fill_gradient = QLinearGradient(0, 0, 0, self.height())
            fill_gradient.setColorAt(0, QColor(194, 43, 43, 80))
            fill_gradient.setColorAt(1, QColor(101, 31, 255, 40))
            
            painter.fillPath(fill_path, QBrush(fill_gradient))


def main():
    """Application entry point."""
    # Create application
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Quantum Dot")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    window = QuantumDotApp()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()