from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QTabWidget, QCheckBox, QSlider, QComboBox
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor
import sys

SECRET_KEY = "vegemite.dad"

# FOV Circle Window
class FOVOverlay(QWidget):
    def __init__(self, radius=100):
        super().__init__()
        self.radius = radius
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor(255, 255, 255), 2)
        painter.setPen(pen)
        center = QPoint(self.width() // 2, self.height() // 2)
        painter.drawEllipse(center, self.radius, self.radius)

# Main GUI After Login
class MainGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("vegemite.dev ontop")
        self.setGeometry(300, 200, 600, 400)
        self.setStyleSheet("background-color: red;")
        self.fov_overlay = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background: #aa0000;
                color: white;
                padding: 8px;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: #ff0000;
            }
        """)

        # Aimbot Tab
        aimbot_tab = QWidget()
        aimbot_layout = QVBoxLayout()
        aimbot_layout.setAlignment(Qt.AlignTop)

        self.aimbot_checkbox = QCheckBox("Enable Aimbot")
        self.aimbot_checkbox.setStyleSheet("color: white; font-size: 16px;")
        self.aimbot_checkbox.stateChanged.connect(self.toggle_fov)
        aimbot_layout.addWidget(self.aimbot_checkbox)

        smoothing_label = QLabel("Smoothing")
        smoothing_label.setStyleSheet("color: white;")
        smoothing_slider = QSlider(Qt.Horizontal)
        smoothing_slider.setMinimum(1)
        smoothing_slider.setMaximum(10)
        smoothing_slider.setValue(5)
        aimbot_layout.addWidget(smoothing_label)
        aimbot_layout.addWidget(smoothing_slider)

        target_label = QLabel("Target Bone")
        target_label.setStyleSheet("color: white;")
        target_combo = QComboBox()
        target_combo.addItems(["Head", "Neck", "Chest"])
        target_combo.setStyleSheet("background-color: white; color: red;")
        aimbot_layout.addWidget(target_label)
        aimbot_layout.addWidget(target_combo)

        fov_label = QLabel("FOV Size")
        fov_label.setStyleSheet("color: white;")
        self.fov_input = QLineEdit()
        self.fov_input.setPlaceholderText("e.g., 100")
        self.fov_input.setStyleSheet("background-color: white; color: red; padding: 4px;")
        aimbot_layout.addWidget(fov_label)
        aimbot_layout.addWidget(self.fov_input)

        hotkey_label = QLabel("Enable Hotkey")
        hotkey_label.setStyleSheet("color: white;")
        hotkey_input = QLineEdit()
        hotkey_input.setPlaceholderText("e.g., Right Mouse")
        hotkey_input.setStyleSheet("background-color: white; color: red; padding: 4px;")
        aimbot_layout.addWidget(hotkey_label)
        aimbot_layout.addWidget(hotkey_input)

        aimbot_tab.setLayout(aimbot_layout)
        aimbot_tab.setStyleSheet("background-color: red;")

        # Visuals Tab
        visuals_tab = QWidget()
        visuals_tab.setStyleSheet("background-color: red;")
        visuals_layout = QVBoxLayout()
        visuals_layout.setAlignment(Qt.AlignTop)

        visuals_label = QLabel("ESP Settings")
        visuals_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        visuals_layout.addWidget(visuals_label)

        # ESP checkboxes
        for text in [
            "Show Player Boxes", "Show Health Bars", "Show Names",
            "Show Distance", "Show Crosshair", "Show Tracers"
        ]:
            cb = QCheckBox(text)
            cb.setStyleSheet("color: white; font-size: 14px;")
            visuals_layout.addWidget(cb)

        # Color pickers
        crosshair_color_label = QLabel("Crosshair Color (Hex)")
        crosshair_color_label.setStyleSheet("color: white;")
        crosshair_color_input = QLineEdit()
        crosshair_color_input.setPlaceholderText("#ffffff")
        crosshair_color_input.setStyleSheet("background-color: white; color: red; padding: 4px;")
        visuals_layout.addWidget(crosshair_color_label)
        visuals_layout.addWidget(crosshair_color_input)

        box_color_label = QLabel("Box Color (Hex)")
        box_color_label.setStyleSheet("color: white;")
        box_color_input = QLineEdit()
        box_color_input.setPlaceholderText("#00ff00")
        box_color_input.setStyleSheet("background-color: white; color: red; padding: 4px;")
        visuals_layout.addWidget(box_color_label)
        visuals_layout.addWidget(box_color_input)

        # Line thickness
        thickness_label = QLabel("Line Thickness")
        thickness_label.setStyleSheet("color: white;")
        thickness_slider = QSlider(Qt.Horizontal)
        thickness_slider.setMinimum(1)
        thickness_slider.setMaximum(10)
        thickness_slider.setValue(2)
        visuals_layout.addWidget(thickness_label)
        visuals_layout.addWidget(thickness_slider)

        # Distance units
        distance_unit_label = QLabel("Distance Units")
        distance_unit_label.setStyleSheet("color: white;")
        distance_unit_combo = QComboBox()
        distance_unit_combo.addItems(["Meters", "Studs", "Feet"])
        distance_unit_combo.setStyleSheet("background-color: white; color: red;")
        visuals_layout.addWidget(distance_unit_label)
        visuals_layout.addWidget(distance_unit_combo)

        visuals_tab.setLayout(visuals_layout)

        # Add tabs
        tabs.addTab(aimbot_tab, "Aimbot")
        tabs.addTab(visuals_tab, "Visuals")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def toggle_fov(self, state):
        if state == Qt.Checked:
            try:
                radius = int(self.fov_input.text())
            except ValueError:
                radius = 100
            self.fov_overlay = FOVOverlay(radius)
            self.fov_overlay.show()
        else:
            if self.fov_overlay:
                self.fov_overlay.close()
                self.fov_overlay = None

# Login Screen
class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(350, 250, 300, 150)
        self.setStyleSheet("background-color: #880000; color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Enter your key:")
        self.input = QLineEdit()
        self.input.setPlaceholderText("Key here")
        self.input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.check_key)

        self.error_label = QLabel("")

        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.error_label)
        self.setLayout(layout)

    def check_key(self):
        if self.input.text() == SECRET_KEY:
            self.open_main_gui()
        else:
            self.error_label.setText("Invalid key.")
            self.error_label.setStyleSheet("color: yellow;")

    def open_main_gui(self):
        self.main_window = MainGUI()
        self.main_window.show()
        self.close()

# Run
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginScreen()
    login.show()
    sys.exit(app.exec_())
