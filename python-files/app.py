import sys
import os
import threading
import configparser
from PyQt5 import QtWidgets, QtCore, QtGui
from pynput import mouse, keyboard
import win32api

# --- Constants ---
SLIDER_PARAMS = [
    ("Right", -20, 20),
    ("Down", -20, 20),
    ("Left", -20, 20),
    ("Up", -20, 20),
    ("Delay", 1, 100)
]
INI_SECTION = "Recoil"

SIDEBAR_SECTIONS = [
    "Legitbot", "Aim Assist", "Players", "Chams", "Items", "Visuals", "World", "View", "Indicators", "Miscellaneous", "Inventory", "Configs"
]

class Sidebar(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(120)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 24, 0, 24)
        layout.setSpacing(8)
        for section in SIDEBAR_SECTIONS:
            lbl = QtWidgets.QLabel(section)
            lbl.setObjectName("sidebarLabel")
            lbl.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            layout.addWidget(lbl)
        layout.addStretch()

# --- Main Application Class ---
class RecoilApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("itzaJ - Mouse Recoil INI Manager")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(800, 600)
        self.selected_dir = None
        self.ini_files = []
        self.current_ini = None
        self.slider_widgets = {}
        self.mouse_thread = None
        self.mouse_thread_running = threading.Event()
        self.listener = None
        self.init_ui()
        self.setStyleSheet(self.load_qss())

    def load_qss(self):
        # QSS inspired by the screenshot
        return """
        QWidget { background: #181a20; color: #e6e6e6; font-family: 'Segoe UI', 'Arial'; font-size: 13px; }
        QFrame#sidebar { background: #1e2128; border-right: 2px solid #23242a; }
        QLabel#sidebarLabel { color: #b0b3ba; font-size: 14px; padding: 8px 18px; font-weight: 600; }
        QLabel#sidebarLabel:first-child { color: #ff3c57; font-size: 16px; font-weight: bold; }
        QGroupBox { border: 1.5px solid #23242a; border-radius: 10px; margin-top: 18px; background: #23242a; }
        QGroupBox:title { subcontrol-origin: margin; left: 16px; padding: 0 6px 0 6px; color: #ff3c57; font-size: 16px; font-weight: bold; }
        QLabel#title { color: #ff3c57; font-size: 28px; font-weight: bold; letter-spacing: 1px; }
        QLabel#subtitle { color: #b0b3ba; font-size: 15px; font-weight: bold; }
        QPushButton, QComboBox, QLineEdit { background: #23242a; border: 1.5px solid #35363c; border-radius: 8px; padding: 7px 16px; }
        QPushButton { color: #e6e6e6; font-weight: bold; }
        QPushButton:hover { background: #292b32; border: 1.5px solid #ff3c57; }
        QPushButton#toggle { background: #ff3c57; color: #fff; border: none; border-radius: 16px; padding: 7px 24px; font-size: 15px; }
        QPushButton#toggle[checked="true"] { background: #50fa7b; color: #23272e; }
        QSlider::groove:horizontal { height: 8px; background: #35363c; border-radius: 4px; }
        QSlider::handle:horizontal { background: #ff3c57; width: 18px; border-radius: 9px; margin: -5px 0; }
        QSlider::sub-page:horizontal { background: #ff3c57; border-radius: 4px; }
        QSlider::add-page:horizontal { background: #23242a; border-radius: 4px; }
        QComboBox QAbstractItemView { background: #23242a; color: #e6e6e6; selection-background-color: #35363c; }
        QCheckBox { spacing: 8px; }
        QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; border: 2px solid #35363c; background: #23242a; }
        QCheckBox::indicator:checked { background: #ff3c57; border: 2px solid #ff3c57; }
        QCheckBox::indicator:unchecked { background: #23242a; border: 2px solid #35363c; }
        QLineEdit { color: #e6e6e6; }
        """

    def init_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = Sidebar()
        main_layout.addWidget(sidebar)

        # Main content area
        content = QtWidgets.QWidget()
        main_layout.addWidget(content)
        layout = QtWidgets.QVBoxLayout(content)
        layout.setSpacing(16)
        layout.setContentsMargins(32, 24, 32, 24)

        # Title
        title = QtWidgets.QLabel("itzaJ", objectName="title")
        title.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        layout.addWidget(title)
        subtitle = QtWidgets.QLabel("Mouse Recoil INI Manager", objectName="subtitle")
        subtitle.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        layout.addWidget(subtitle)

        # Loaded INI
        loaded_layout = QtWidgets.QHBoxLayout()
        loaded_label = QtWidgets.QLabel("Loaded INI:")
        loaded_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.loaded_ini_label = QtWidgets.QLabel("None")
        loaded_layout.addWidget(loaded_label)
        loaded_layout.addWidget(self.loaded_ini_label)
        loaded_layout.addStretch()
        layout.addLayout(loaded_layout)

        # Top controls
        top_layout = QtWidgets.QHBoxLayout()
        self.ini_combo = QtWidgets.QComboBox()
        self.ini_combo.currentIndexChanged.connect(self.on_ini_selected)
        top_layout.addWidget(self.ini_combo)
        browse_btn = QtWidgets.QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_dir)
        top_layout.addWidget(browse_btn)
        self.toggle_btn = QtWidgets.QPushButton("Toggle ON", objectName="toggle")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.clicked.connect(self.toggle_mouse_mover)
        self.toggle_btn.setEnabled(False)
        top_layout.addWidget(self.toggle_btn)
        self.toggle_status = QtWidgets.QLabel("OFF")
        self.toggle_status.setStyleSheet("font-weight: bold; color: #ff3c57; font-size: 14px;")
        top_layout.addWidget(self.toggle_status)
        layout.addLayout(top_layout)

        # Sliders group
        sliders_group = QtWidgets.QGroupBox("Create/Edit INI")
        sliders_layout = QtWidgets.QVBoxLayout(sliders_group)
        for param, minv, maxv in SLIDER_PARAMS:
            row = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(f"{param}:")
            label.setMinimumWidth(70)
            label.setStyleSheet("font-weight: bold; font-size: 14px;")
            slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            slider.setMinimum(minv)
            slider.setMaximum(maxv)
            slider.setValue(0)
            slider.setSingleStep(1)
            value_lbl = QtWidgets.QLabel("0")
            value_lbl.setMinimumWidth(36)
            value_lbl.setAlignment(QtCore.Qt.AlignCenter)
            slider.valueChanged.connect(lambda val, l=value_lbl: l.setText(str(val)))
            row.addWidget(label)
            row.addWidget(slider)
            row.addWidget(value_lbl)
            sliders_layout.addLayout(row)
            self.slider_widgets[param] = (slider, value_lbl)
        layout.addWidget(sliders_group)

        # Bottom controls
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(QtWidgets.QLabel("File Name:"))
        self.filename_entry = QtWidgets.QLineEdit()
        bottom_layout.addWidget(self.filename_entry)
        save_btn = QtWidgets.QPushButton("Save INI")
        save_btn.clicked.connect(self.save_ini)
        bottom_layout.addWidget(save_btn)
        layout.addLayout(bottom_layout)

    # --- Directory Browsing and INI Management ---
    def browse_dir(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.selected_dir = dir_path
            self.refresh_ini_list()

    def refresh_ini_list(self):
        if not self.selected_dir:
            return
        self.ini_files = [f for f in os.listdir(self.selected_dir) if f.lower().endswith('.ini')]
        self.ini_combo.clear()
        self.ini_combo.addItems(self.ini_files)
        if self.ini_files:
            self.ini_combo.setCurrentIndex(0)
            self.on_ini_selected()
        else:
            self.loaded_ini_label.setText("None")
            self.toggle_btn.setEnabled(False)

    def on_ini_selected(self):
        idx = self.ini_combo.currentIndex()
        if idx < 0 or not self.ini_files:
            return
        fname = self.ini_files[idx]
        self.current_ini = fname
        self.loaded_ini_label.setText(fname)
        self.load_ini_values()
        self.toggle_btn.setEnabled(True)

    def load_ini_values(self):
        if not self.selected_dir or not self.current_ini:
            return
        path = os.path.join(self.selected_dir, self.current_ini)
        config = configparser.ConfigParser()
        try:
            config.read(path)
            section = config[INI_SECTION] if INI_SECTION in config else {}
            for param, _, _ in SLIDER_PARAMS:
                val = int(section.get(param, 0))
                slider, value_lbl = self.slider_widgets[param]
                slider.setValue(val)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load INI: {e}")

    def save_ini(self):
        if not self.selected_dir:
            QtWidgets.QMessageBox.critical(self, "Error", "No directory selected.")
            return
        fname = self.filename_entry.text().strip()
        if not fname:
            QtWidgets.QMessageBox.critical(self, "Error", "Please enter a file name.")
            return
        if not fname.lower().endswith('.ini'):
            fname += '.ini'
        path = os.path.join(self.selected_dir, fname)
        config = configparser.ConfigParser()
        config[INI_SECTION] = {param: str(self.slider_widgets[param][0].value()) for param, _, _ in SLIDER_PARAMS}
        try:
            with open(path, 'w') as f:
                config.write(f)
            self.refresh_ini_list()
            self.ini_combo.setCurrentText(fname)
            self.loaded_ini_label.setText(fname)
            QtWidgets.QMessageBox.information(self, "Saved", f"INI file '{fname}' saved.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save INI: {e}")

    # --- Mouse Mover Thread ---
    def toggle_mouse_mover(self):
        if self.mouse_thread_running.is_set():
            self.mouse_thread_running.clear()
            self.toggle_btn.setText("Toggle ON")
            self.toggle_btn.setChecked(False)
            self.toggle_status.setText("OFF")
            self.toggle_status.setStyleSheet("font-weight: bold; color: #ff3c57; font-size: 14px;")
        else:
            if not self.current_ini:
                QtWidgets.QMessageBox.critical(self, "Error", "No INI file loaded.")
                return
            self.mouse_thread_running.set()
            self.toggle_btn.setText("Toggle OFF")
            self.toggle_btn.setChecked(True)
            self.toggle_status.setText("ON")
            self.toggle_status.setStyleSheet("font-weight: bold; color: #50fa7b; font-size: 14px;")
            if not self.mouse_thread or not self.mouse_thread.is_alive():
                self.mouse_thread = threading.Thread(target=self.mouse_mover_loop, daemon=True)
                self.mouse_thread.start()
            if not self.listener:
                self.listener = MouseKeyboardListener(self)
                self.listener.start()

    def mouse_mover_loop(self):
        while self.mouse_thread_running.is_set():
            if self.listener and self.listener.both_buttons_held():
                vals = {param: self.slider_widgets[param][0].value() for param, _, _ in SLIDER_PARAMS}
                dx = vals["Right"] - vals["Left"]
                dy = vals["Down"] - vals["Up"]
                dx = int(dx / 2)
                dy = int(dy / 2)
                if dx != 0 or dy != 0:
                    x, y = win32api.GetCursorPos()
                    win32api.SetCursorPos((x + dx, y + dy))
                threading.Event().wait(vals["Delay"] / 1000)
            else:
                threading.Event().wait(0.01)

# --- Mouse/Keyboard Listener ---
class MouseKeyboardListener:
    def __init__(self, app):
        self.app = app
        self.mouse_buttons = set()
        self.kb_listener = None
        self.mouse_listener = None
        self.running = True

    def start(self):
        self.kb_listener = keyboard.Listener(on_press=self.on_kb_press, on_release=self.on_kb_release)
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.kb_listener.start()
        self.mouse_listener.start()

    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            self.mouse_buttons.add(button)
        else:
            self.mouse_buttons.discard(button)

    def on_kb_press(self, key):
        pass
    def on_kb_release(self, key):
        pass

    def both_buttons_held(self):
        return mouse.Button.left in self.mouse_buttons and mouse.Button.right in self.mouse_buttons

# --- Main ---
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RecoilApp()
    window.show()
    sys.exit(app.exec_())
