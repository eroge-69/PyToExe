import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QGridLayout, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from pynput import mouse, keyboard
import threading

PROFILE_DIR = "profiles"
PROFILE_FILE = os.path.join(PROFILE_DIR, "default.json")

# Ensure profile directory exists
os.makedirs(PROFILE_DIR, exist_ok=True)

class MouseKeyMapper(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MouseKeyMapper")
        self.resize(500, 400)

        self.key_inputs = {}
        self.listener = None
        self.mapping_enabled = False

        self.kb = keyboard.Controller()

        layout = QGridLayout()

        # Create labels and key mapping fields
        for i in range(10):
            btn_label = QLabel(f"Mouse Button {i + 1}")
            key_input = QLineEdit()
            layout.addWidget(btn_label, i, 0)
            layout.addWidget(key_input, i, 1)
            self.key_inputs[f"Button {i + 1}"] = key_input

        # Control buttons
        self.load_btn = QPushButton("Load Profile")
        self.save_btn = QPushButton("Save Profile")
        self.start_btn = QPushButton("Start Mapping")
        layout.addWidget(self.load_btn, 11, 0)
        layout.addWidget(self.save_btn, 11, 1)
        layout.addWidget(self.start_btn, 12, 0, 1, 2)

        self.setLayout(layout)

        self.load_btn.clicked.connect(self.load_profile)
        self.save_btn.clicked.connect(self.save_profile)
        self.start_btn.clicked.connect(self.toggle_mapping)

        self.button_mapping = {}

    def load_profile(self):
        try:
            with open(PROFILE_FILE, "r") as f:
                self.button_mapping = json.load(f)["button_mappings"]
                for btn, key in self.button_mapping.items():
                    if btn in self.key_inputs:
                        self.key_inputs[btn].setText(key)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load profile:\n{e}")

    def save_profile(self):
        self.button_mapping = {
            btn: field.text()
            for btn, field in self.key_inputs.items()
        }
        try:
            with open(PROFILE_FILE, "w") as f:
                json.dump({"button_mappings": self.button_mapping}, f, indent=4)
            QMessageBox.information(self, "Saved", "Profile saved successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save profile:\n{e}")

    def toggle_mapping(self):
        if self.mapping_enabled:
            self.mapping_enabled = False
            self.start_btn.setText("Start Mapping")
            if self.listener:
                self.listener.stop()
        else:
            self.mapping_enabled = True
            self.start_btn.setText("Stop Mapping")
            self.button_mapping = {
                btn: field.text()
                for btn, field in self.key_inputs.items()
            }
            self.listener = mouse.Listener(on_click=self.on_click)
            threading.Thread(target=self.listener.start, daemon=True).start()

    def on_click(self, x, y, button, pressed):
        if not pressed:
            return
        btn_name = str(button).split(".")[-1].capitalize()
        for i in range(1, 11):
            if button == getattr(mouse.Button, f"x_button{i}", None) or btn_name == f"Button{i}":
                key_combo = self.button_mapping.get(f"Button {i}", "")
                if key_combo:
                    self.press_keys(key_combo)
                break

    def press_keys(self, combo):
        keys = combo.split('+')
        pressed = []
        try:
            for k in keys:
                k = k.strip()
                key = getattr(keyboard.Key, k.lower(), None) or k
                self.kb.press(key)
                pressed.append(key)
            for key in reversed(pressed):
                self.kb.release(key)
        except Exception as e:
            print(f"Error pressing keys: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MouseKeyMapper()
    window.show()
    sys.exit(app.exec_())
