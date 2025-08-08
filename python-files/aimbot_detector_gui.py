
import os
import psutil
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout, QLabel
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

AIMBOT_KEYWORDS = [
    "torch", "yolov5", "bettercam", "SendInput", "mouse_event",
    "aimbot", "overlay", "PyQt5", "win32api", "GetKeyState"
]

class AimbotDetector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Aimbot Detector")
        self.setGeometry(200, 200, 500, 400)

        layout = QVBoxLayout()

        self.status_label = QLabel("Status: Not scanned")
        self.status_label.setStyleSheet("color: gray")
        layout.addWidget(self.status_label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.scan_button = QPushButton("🔍 Scan for Aimbots")
        self.scan_button.clicked.connect(self.scan)
        layout.addWidget(self.scan_button)

        self.kill_button = QPushButton("💀 Kill Detected Process")
        self.kill_button.clicked.connect(self.kill)
        layout.addWidget(self.kill_button)

        self.setLayout(layout)
        self.detected_pid = None

    def log_message(self, message, color="black"):
        self.log.setTextColor(QColor(color))
        self.log.append(message)

    def scan(self):
        self.log.clear()
        self.status_label.setText("Status: Scanning...")
        self.status_label.setStyleSheet("color: orange")
        self.detected_pid = None

        found = False

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = " ".join(proc.info['cmdline']).lower()
                for keyword in AIMBOT_KEYWORDS:
                    if keyword in cmdline:
                        self.log_message(f"⚠️ Detected: {proc.info['name']} (PID: {proc.info['pid']})", "red")
                        self.detected_pid = proc.info['pid']
                        found = True
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if found:
            self.status_label.setText("Status: Aimbot Detected!")
            self.status_label.setStyleSheet("color: red")
        else:
            self.status_label.setText("Status: No Aimbots Found")
            self.status_label.setStyleSheet("color: green")

    def kill(self):
        if self.detected_pid:
            try:
                p = psutil.Process(self.detected_pid)
                p.terminate()
                self.log_message(f"✅ Killed process PID: {self.detected_pid}", "blue")
                self.status_label.setText("Status: Aimbot Terminated")
                self.status_label.setStyleSheet("color: blue")
                self.detected_pid = None
            except Exception as e:
                self.log_message(f"❌ Error killing process: {e}", "red")
        else:
            self.log_message("No process selected.", "gray")

if __name__ == "__main__":
    app = QApplication([])
    window = AimbotDetector()
    window.show()
    app.exec_()
