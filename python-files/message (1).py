import sys
import math
import urllib.request
from io import BytesIO
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QColor, QPainter, QPixmap, QFont, QPainterPath, QImage
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QPushButton, 
                            QTabWidget, QLabel, QVBoxLayout, QHBoxLayout, QCheckBox,
                            QComboBox, QSlider, QGridLayout)


class PlagueUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(900, 500)

        self.drag_pos = None
        
        # URLs for images - replace these with your actual URLs
        self.logo_url = ""
        self.aim_icon_url = "https://files.catbox.moe/dwn0j3.png"
        self.bullet_icon_url = "https://files.catbox.moe/5itji0.png"
        self.config_icon_url = "https://files.catbox.moe/ddd5bn.png"
        
        # Load logo from URL
        self.logo = self.load_pixmap_from_url(self.logo_url)
        if self.logo:
            self.logo = self.logo.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            # Fallback to a blank pixmap if URL fails
            self.logo = QPixmap(60, 60)
            self.logo.fill(Qt.transparent)

        self.angle = 0
        self.show_key_input = False
        self.show_tabs = False

        # Updated theme colors to match the pink logo
        self.primary_color = QColor(255, 20, 147)  # Deep pink
        self.primary_color_hover = QColor(255, 105, 180)  # Hot pink
        self.accent_color = QColor(255, 69, 180)  # Bright pink
        self.bg_color = QColor(0, 0, 0, 200)

        # Spinner animation
        self.spinner_timer = QTimer()
        self.spinner_timer.timeout.connect(self.update_spinner)
        self.spinner_timer.start(16)

        # Switch to input phase after 5 seconds
        self.phase_timer = QTimer()
        self.phase_timer.setSingleShot(True)
        self.phase_timer.timeout.connect(self.show_input)
        self.phase_timer.start(5000)

        # Input and button - adjust positions for larger window
        self.input_box = QLineEdit(self)
        self.input_box.setPlaceholderText("Enter your key...")
        self.input_box.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 20);
                color: white;
                border: 1px solid rgba(255, 20, 147, 120);
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(255, 20, 147, 200);
            }
        """)
        self.input_box.setFixedWidth(300)
        self.input_box.move(300, 250)
        self.input_box.setVisible(False)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 20, 147, 150);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 105, 180, 200);
            }
            QPushButton:pressed {
                background-color: rgba(220, 20, 130, 180);
            }
        """)
        self.submit_button.setFixedWidth(300)
        self.submit_button.move(300, 300)
        self.submit_button.setVisible(False)
        self.submit_button.clicked.connect(self.on_submit)
        
        # Create tab widget but keep it hidden initially
        self.create_tab_widget()
    
    def load_pixmap_from_url(self, url):
        """Load a QPixmap from a URL with proper headers"""
        try:
            # Create a request with headers that mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://discord.com/',
                'Origin': 'https://discord.com'
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = response.read()
                
            image = QImage()
            image.loadFromData(data)
            return QPixmap.fromImage(image)
        except Exception as e:
            print(f"Error loading image from URL {url}: {e}")
            return None

    def create_tab_widget(self):
        # Create a custom tab widget with manual icon handling
        self.tab_widget = QWidget(self)
        self.tab_widget.setFixedSize(900, 500)
        self.tab_widget.setStyleSheet("background-color: transparent;")
        
        # Main layout for the tab widget
        main_layout = QHBoxLayout(self.tab_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar for tab buttons
        sidebar = QWidget()
        sidebar.setFixedWidth(70)
        sidebar.setStyleSheet("""
            background-color: rgba(30, 30, 30, 200);
            border-top-left-radius: 20px;
            border-bottom-left-radius: 20px;
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(15)
        
        # Create content area
        self.content_area = QWidget()
        self.content_area.setStyleSheet("""
            background-color: rgba(0, 0, 0, 200);
            border-top-right-radius: 20px;
            border-bottom-right-radius: 20px;
        """)
        
        # Create stacked layout for content
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab pages
        aim_tab = QWidget()
        aim_tab.setStyleSheet("background-color: transparent;")
        
        bullet_tab = QWidget()
        bullet_tab.setStyleSheet("background-color: transparent;")
        
        config_tab = QWidget()
        config_tab.setStyleSheet("background-color: transparent;")
        
        # Setup tab content
        self.setup_aim_tab(aim_tab)
        self.setup_bullet_tab(bullet_tab)
        self.setup_config_tab(config_tab)
        
        # Create tab buttons with icons
        self.tab_buttons = []
        self.tab_contents = [aim_tab, bullet_tab, config_tab]
        
        # Aim tab button
        aim_button = self.create_tab_button(self.aim_icon_url)
        aim_button.clicked.connect(lambda: self.switch_tab(0))
        sidebar_layout.addWidget(aim_button)
        self.tab_buttons.append(aim_button)
        
        # Bullet tab button
        bullet_button = self.create_tab_button(self.bullet_icon_url)
        bullet_button.clicked.connect(lambda: self.switch_tab(1))
        sidebar_layout.addWidget(bullet_button)
        self.tab_buttons.append(bullet_button)
        
        # Config tab button
        config_button = self.create_tab_button(self.config_icon_url)
        config_button.clicked.connect(lambda: self.switch_tab(2))
        sidebar_layout.addWidget(config_button)
        self.tab_buttons.append(config_button)
        
        # Add spacer to push buttons to the top
        sidebar_layout.addStretch()
        
        # Add the first tab content to the layout
        self.content_layout.addWidget(aim_tab)
        self.content_layout.addWidget(bullet_tab)
        self.content_layout.addWidget(config_tab)
        
        # Hide all tabs except the first one
        bullet_tab.setVisible(False)
        config_tab.setVisible(False)
        
        # Set the first button as active
        self.switch_tab(0)
        
        # Add sidebar and content area to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_area)
        
        # Hide tab widget initially
        self.tab_widget.setVisible(False)
    
    def create_tab_button(self, icon_url):
        button = QPushButton()
        button.setFixedSize(50, 50)
        
        # Create a layout for the button to center the icon
        layout = QVBoxLayout(button)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Create a label for the icon
        icon_label = QLabel()
        icon_pixmap = self.load_pixmap_from_url(icon_url)
        if icon_pixmap:
            # Don't scale or transform the icon, use it as is
            icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(icon_label)
        
        button.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 30, 30, 200);
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 200);
            }
        """)
        
        return button
    
    def switch_tab(self, index):
        # Update button styles with pink theme
        for i, button in enumerate(self.tab_buttons):
            if i == index:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255, 20, 147, 150);
                        border: none;
                        border-radius: 10px;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(30, 30, 30, 200);
                        border: none;
                        border-radius: 10px;
                    }
                    QPushButton:hover {
                        background-color: rgba(80, 80, 80, 200);
                    }
                """)
        
        # Show the selected tab content and hide others
        for i, tab in enumerate(self.tab_contents):
            tab.setVisible(i == index)

    def setup_aim_tab(self, tab):
        # Create a main horizontal layout to divide the tab into two columns
        main_layout = QHBoxLayout(tab)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Left column - Regular Aimbot settings
        left_column = QVBoxLayout()
        left_column.setSpacing(15)
        
        # Enabled checkbox
        enabled_checkbox = QCheckBox("Enabled")
        enabled_checkbox.setChecked(False)
        left_column.addWidget(enabled_checkbox)
        
        # Aimbot checkbox
        aimbot_checkbox = QCheckBox("Aimbot")
        aimbot_checkbox.setChecked(False)
        left_column.addWidget(aimbot_checkbox)
        
        # Keybind dropdown
        keybind_layout = QHBoxLayout()
        keybind_label = QLabel("Keybind:")
        keybind_dropdown = QComboBox()
        keybind_dropdown.addItems(["None", "Right Mouse", "Mouse 4", "Mouse 5", "V"])
        keybind_layout.addWidget(keybind_label)
        keybind_layout.addWidget(keybind_dropdown)
        keybind_layout.addStretch()
        left_column.addLayout(keybind_layout)
        
        # Closest part checkbox
        closest_part_checkbox = QCheckBox("Closest Part")
        closest_part_checkbox.setChecked(False)
        left_column.addWidget(closest_part_checkbox)
        
        # Knocked checkbox
        knocked_checkbox = QCheckBox("Knocked")
        knocked_checkbox.setChecked(False)
        left_column.addWidget(knocked_checkbox)
        
        # Grabbed checkbox
        grabbed_checkbox = QCheckBox("Grabbed")
        grabbed_checkbox.setChecked(False)
        left_column.addWidget(grabbed_checkbox)
        
        # FOV slider
        fov_layout = QVBoxLayout()
        fov_label_layout = QHBoxLayout()
        fov_label = QLabel("FOV:")
        fov_value = QLabel("50")
        fov_label_layout.addWidget(fov_label)
        fov_label_layout.addStretch()
        fov_label_layout.addWidget(fov_value)
        fov_layout.addLayout(fov_label_layout)
        
        fov_slider = QSlider(Qt.Horizontal)
        fov_slider.setMinimum(1)
        fov_slider.setMaximum(100)
        fov_slider.setValue(50)
        fov_slider.valueChanged.connect(lambda value: fov_value.setText(str(value)))
        fov_layout.addWidget(fov_slider)
        left_column.addLayout(fov_layout)
        
        # Smoothness slider
        smoothness_layout = QVBoxLayout()
        smoothness_label_layout = QHBoxLayout()
        smoothness_label = QLabel("Smoothness:")
        smoothness_value = QLabel("5")
        smoothness_label_layout.addWidget(smoothness_label)
        smoothness_label_layout.addStretch()
        smoothness_label_layout.addWidget(smoothness_value)
        smoothness_layout.addLayout(smoothness_label_layout)
        
        smoothness_slider = QSlider(Qt.Horizontal)
        smoothness_slider.setMinimum(1)
        smoothness_slider.setMaximum(10)
        smoothness_slider.setValue(5)
        smoothness_slider.valueChanged.connect(lambda value: smoothness_value.setText(str(value)))
        smoothness_layout.addWidget(smoothness_slider)
        left_column.addLayout(smoothness_layout)
        
        left_column.addStretch()
        
        # Right column - Silent Aim settings
        right_column = QVBoxLayout()
        right_column.setSpacing(15)
        
        # Silent Aim checkbox
        silent_aim_checkbox = QCheckBox("Silent Aim")
        silent_aim_checkbox.setChecked(False)
        right_column.addWidget(silent_aim_checkbox)
        
        # Anti curve checkbox
        anti_curve_checkbox = QCheckBox("Anti Curve")
        anti_curve_checkbox.setChecked(False)
        right_column.addWidget(anti_curve_checkbox)
        
        # Closest player checkbox
        closest_player_checkbox = QCheckBox("Closest Player")
        closest_player_checkbox.setChecked(False)
        right_column.addWidget(closest_player_checkbox)
        
        # Knocked check checkbox
        knocked_check_checkbox = QCheckBox("Knocked Check")
        knocked_check_checkbox.setChecked(False)
        right_column.addWidget(knocked_check_checkbox)
        
        # Grab check checkbox
        grab_check_checkbox = QCheckBox("Grab Check")
        grab_check_checkbox.setChecked(False)
        right_column.addWidget(grab_check_checkbox)
        
        # Anti lock check checkbox
        anti_lock_checkbox = QCheckBox("Anti Lock Check")
        anti_lock_checkbox.setChecked(False)
        right_column.addWidget(anti_lock_checkbox)
        
        # FOV slider for silent aim
        silent_fov_layout = QVBoxLayout()
        silent_fov_label_layout = QHBoxLayout()
        silent_fov_label = QLabel("FOV:")
        silent_fov_value = QLabel("50")
        silent_fov_label_layout.addWidget(silent_fov_label)
        silent_fov_label_layout.addStretch()
        silent_fov_label_layout.addWidget(silent_fov_value)
        silent_fov_layout.addLayout(silent_fov_label_layout)
        
        silent_fov_slider = QSlider(Qt.Horizontal)
        silent_fov_slider.setMinimum(1)
        silent_fov_slider.setMaximum(100)
        silent_fov_slider.setValue(50)
        silent_fov_slider.valueChanged.connect(lambda value: silent_fov_value.setText(str(value)))
        silent_fov_layout.addWidget(silent_fov_slider)
        right_column.addLayout(silent_fov_layout)
        
        right_column.addStretch()
        
        # Add columns to main layout
        main_layout.addLayout(left_column)
        main_layout.addLayout(right_column)
        
        # Apply pink theme styles to all widgets in this tab
        tab.setStyleSheet("""
            QCheckBox {
                color: white;
                font-family: 'Segoe UI', Arial;
                font-size: 16px;
                font-weight: 500;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid rgba(255, 20, 147, 120);
                background-color: rgba(30, 30, 30, 200);
            }
            
            QCheckBox::indicator:checked {
                background-color: rgba(255, 20, 147, 200);
                border: 1px solid rgba(255, 105, 180, 150);
            }
            
            QCheckBox::indicator:unchecked:hover {
                background-color: rgba(50, 50, 50, 200);
                border: 1px solid rgba(255, 69, 180, 100);
            }
            
            QComboBox {
                background-color: rgba(30, 30, 30, 200);
                color: white;
                border: 1px solid rgba(255, 20, 147, 120);
                border-radius: 5px;
                padding: 5px;
                min-width: 100px;
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: rgba(255, 20, 147, 120);
                border-left-style: solid;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            
            QComboBox QAbstractItemView {
                background-color: rgba(30, 30, 30, 200);
                color: white;
                selection-background-color: rgba(255, 20, 147, 150);
                selection-color: white;
                border: 1px solid rgba(255, 20, 147, 120);
            }
            
            QSlider::groove:horizontal {
                border: 1px solid rgba(255, 20, 147, 120);
                height: 8px;
                background: rgba(30, 30, 30, 200);
                margin: 2px 0;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: rgba(255, 20, 147, 200);
                border: 1px solid rgba(255, 105, 180, 150);
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            
            QSlider::handle:horizontal:hover {
                background: rgba(255, 105, 180, 220);
            }
            
            QLabel {
                color: white;
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
            }
        """)

    def setup_bullet_tab(self, tab):
        # Create a main layout for the bullet tab
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(15)
        
        # Trigger Bot checkbox
        trigger_bot_checkbox = QCheckBox("Trigger Bot")
        trigger_bot_checkbox.setChecked(False)
        main_layout.addWidget(trigger_bot_checkbox)
        
        # Keybind dropdown
        keybind_layout = QHBoxLayout()
        keybind_label = QLabel("Keybind:")
        keybind_dropdown = QComboBox()
        keybind_dropdown.addItems(["None", "Right Mouse", "Mouse 4", "Mouse 5", "V"])
        keybind_layout.addWidget(keybind_label)
        keybind_layout.addWidget(keybind_dropdown)
        keybind_layout.addStretch()
        main_layout.addLayout(keybind_layout)
        
        # Delay slider
        delay_layout = QVBoxLayout()
        delay_label_layout = QHBoxLayout()
        delay_label = QLabel("Delay:")
        delay_value = QLabel("50")
        delay_label_layout.addWidget(delay_label)
        delay_label_layout.addStretch()
        delay_label_layout.addWidget(delay_value)
        delay_layout.addLayout(delay_label_layout)
        
        delay_slider = QSlider(Qt.Horizontal)
        delay_slider.setMinimum(1)
        delay_slider.setMaximum(200)
        delay_slider.setValue(50)
        delay_slider.valueChanged.connect(lambda value: delay_value.setText(str(value)))
        delay_layout.addWidget(delay_slider)
        main_layout.addLayout(delay_layout)
        
        # FOV slider
        fov_layout = QVBoxLayout()
        fov_label_layout = QHBoxLayout()
        fov_label = QLabel("FOV:")
        fov_value = QLabel("50")
        fov_label_layout.addWidget(fov_label)
        fov_label_layout.addStretch()
        fov_label_layout.addWidget(fov_value)
        fov_layout.addLayout(fov_label_layout)
        
        fov_slider = QSlider(Qt.Horizontal)
        fov_slider.setMinimum(1)
        fov_slider.setMaximum(100)
        fov_slider.setValue(50)
        fov_slider.valueChanged.connect(lambda value: fov_value.setText(str(value)))
        fov_layout.addWidget(fov_slider)
        main_layout.addLayout(fov_layout)
        
        # Knocked check checkbox
        knocked_check_checkbox = QCheckBox("Knocked Check")
        knocked_check_checkbox.setChecked(False)
        main_layout.addWidget(knocked_check_checkbox)
        
        # Grab check checkbox
        grab_check_checkbox = QCheckBox("Grab Check")
        grab_check_checkbox.setChecked(False)
        main_layout.addWidget(grab_check_checkbox)
        
        main_layout.addStretch()
        
        # Apply pink theme styles to all widgets in this tab
        tab.setStyleSheet("""
            QCheckBox {
                color: white;
                font-family: 'Segoe UI', Arial;
                font-size: 16px;
                font-weight: 500;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid rgba(255, 20, 147, 120);
                background-color: rgba(30, 30, 30, 200);
            }
            
            QCheckBox::indicator:checked {
                background-color: rgba(255, 20, 147, 200);
                border: 1px solid rgba(255, 105, 180, 150);
            }
            
            QCheckBox::indicator:unchecked:hover {
                background-color: rgba(50, 50, 50, 200);
                border: 1px solid rgba(255, 69, 180, 100);
            }
            
            QComboBox {
                background-color: rgba(30, 30, 30, 200);
                color: white;
                border: 1px solid rgba(255, 20, 147, 120);
                border-radius: 5px;
                padding: 5px;
                min-width: 100px;
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: rgba(255, 20, 147, 120);
                border-left-style: solid;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            
            QComboBox QAbstractItemView {
                background-color: rgba(30, 30, 30, 200);
                color: white;
                selection-background-color: rgba(255, 20, 147, 150);
                selection-color: white;
                border: 1px solid rgba(255, 20, 147, 120);
            }
            
            QSlider::groove:horizontal {
                border: 1px solid rgba(255, 20, 147, 120);
                height: 8px;
                background: rgba(30, 30, 30, 200);
                margin: 2px 0;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: rgba(255, 20, 147, 200);
                border: 1px solid rgba(255, 105, 180, 150);
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            
            QSlider::handle:horizontal:hover {
                background: rgba(255, 105, 180, 220);
            }
            
            QLabel {
                color: white;
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
            }
        """)

    def setup_config_tab(self, tab):
        # Create a main layout for the config tab
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Config name text box
        config_name_layout = QVBoxLayout()
        config_name_label = QLabel("Config Name:")
        config_name_label.setStyleSheet("font-size: 16px; font-weight: 500;")
        config_name_input = QLineEdit()
        config_name_input.setPlaceholderText("Enter config name...")
        config_name_input.setFixedHeight(40)
        
        config_name_layout.addWidget(config_name_label)
        config_name_layout.addWidget(config_name_input)
        main_layout.addLayout(config_name_layout)
        
        # Config selection dropdown
        config_select_layout = QVBoxLayout()
        config_select_label = QLabel("Select Config:")
        config_select_label.setStyleSheet("font-size: 16px; font-weight: 500;")
        config_select_dropdown = QComboBox()
        config_select_dropdown.addItems(["..", "BLATANTASF.cfg", "legit.cfg", "OWNERS CONFIG.cfg"])
        config_select_dropdown.setFixedHeight(40)
        
        config_select_layout.addWidget(config_select_label)
        config_select_layout.addWidget(config_select_dropdown)
        main_layout.addLayout(config_select_layout)
        
        # Save and Load buttons
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.setFixedSize(200, 40)
        
        load_button = QPushButton("Load")
        load_button.setFixedSize(200, 40)
        
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(load_button)
        buttons_layout.setSpacing(20)
        
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()
        
        # Apply pink theme styles to all widgets in this tab
        tab.setStyleSheet("""
            QLabel {
                color: white;
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
            }
            
            QLineEdit {
                background-color: rgba(30, 30, 30, 200);
                color: white;
                border: 1px solid rgba(255, 20, 147, 120);
                border-radius: 5px;
                padding: 8px;
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
            }
            
            QLineEdit:focus {
                border: 2px solid rgba(255, 20, 147, 200);
            }
            
            QComboBox {
                background-color: rgba(30, 30, 30, 200);
                color: white;
                border: 1px solid rgba(255, 20, 147, 120);
                border-radius: 5px;
                padding: 5px;
                min-width: 100px;
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: rgba(255, 20, 147, 120);
                border-left-style: solid;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            
            QComboBox QAbstractItemView {
                background-color: rgba(30, 30, 30, 200);
                color: white;
                selection-background-color: rgba(255, 20, 147, 150);
                selection-color: white;
                border: 1px solid rgba(255, 20, 147, 120);
            }
            
            QPushButton {
                background-color: rgba(255, 20, 147, 150);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: rgba(255, 105, 180, 200);
            }
            
            QPushButton:pressed {
                background-color: rgba(220, 20, 130, 180);
            }
        """)

    def update_spinner(self):
        if not self.show_key_input and not self.show_tabs:
            self.angle += 2
            if self.angle >= 360:
                self.angle = 0
        self.update()

    def show_input(self):
        self.show_key_input = True
        self.input_box.setVisible(True)
        self.submit_button.setVisible(True)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background with rounded corners
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.width(), self.height()), 20, 20)
        painter.setClipPath(path)
        
        painter.setBrush(self.bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)

        if not self.show_key_input and not self.show_tabs:
            self.draw_spinner(painter)

        if not self.show_key_input and not self.show_tabs:
            self.draw_spinner(painter)
            # Logo (bottom center during spinner phase)
            painter.drawPixmap((self.width() - self.logo.width()) // 2, 350, self.logo)
        elif self.show_key_input and not self.show_tabs:
            # Logo (top center)
            painter.drawPixmap((self.width() - self.logo.width()) // 2, 100, self.logo)

            # Text: "Enter your key" below logo with pink color
            painter.setPen(self.primary_color)
            painter.setFont(QFont("Segoe UI", 22, QFont.Bold))
            painter.drawText(self.rect(), Qt.AlignTop | Qt.AlignHCenter, "\n\n\n\nEnter your key")

    def draw_spinner(self, painter):
        radius = 40
        center_x = self.width() // 2
        center_y = 250 - 80

        for i in range(12):
            alpha = 255 * ((i + 1) / 12)
            angle = math.radians((self.angle + i * 30) % 360)
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            # Updated spinner color to pink
            color = QColor(self.primary_color.red(), self.primary_color.green(), self.primary_color.blue(), int(alpha))
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(x) - 4, int(y) - 4, 8, 8)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def on_submit(self):
        # Hide input screen, show the loading animation again for 1 second
        self.input_box.setVisible(False)
        self.submit_button.setVisible(False)
        self.show_key_input = False
        self.angle = 0
        
        # Show loading animation for 1 second before showing tabs
        QTimer.singleShot(1000, self.display_tabs)

    def display_tabs(self):
        # Show the tab widget with a smooth fade-in effect
        self.show_tabs = True
        self.tab_widget.setVisible(True)
        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlagueUI()
    window.show()
    sys.exit(app.exec_())
