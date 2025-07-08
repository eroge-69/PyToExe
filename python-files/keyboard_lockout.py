import subprocess, sys, os
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton,
                             QVBoxLayout, QLabel, QCheckBox, QMessageBox)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

DEVICE_ID = "ACPI\\PNP0303"

def disable_keyboard():
    return subprocess.run(["devcon.exe", "disable", DEVICE_ID]).returncode == 0

def enable_keyboard():
    return subprocess.run(["devcon.exe", "enable", DEVICE_ID]).returncode == 0

def block_reinstall():
    subprocess.run([
        "reg", "add",
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DeviceInstall\Restrictions",
        "/v", "DenyDeviceIDs", "/t", "REG_DWORD", "/d", "1", "/f"
    ])
    subprocess.run([
        "reg", "add",
        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DeviceInstall\Restrictions\DenyDeviceIDs",
        "/v", "1", "/t", "REG_SZ", "/d", DEVICE_ID, "/f"
    ])

class LockoutApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keyboard Lockout Utility")
        self.setStyleSheet("background:#1e1e1e; color:#eee;")
        self.setFixedSize(300,200)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Internal Keyboard: {DEVICE_ID}", alignment=Qt.AlignCenter))
        self.chk = QCheckBox("Prevent driver reinstall")
        layout.addWidget(self.chk)
        btn_d = QPushButton("🔒 Disable")
        btn_d.clicked.connect(self.try_disable)
        layout.addWidget(btn_d)
        btn_e = QPushButton("🔓 Enable")
        btn_e.clicked.connect(self.try_enable)
        layout.addWidget(btn_e)
        self.setLayout(layout)

    def try_disable(self):
        if disable_keyboard():
            if self.chk.isChecked(): block_reinstall()
            QMessageBox.information(self, "Done", "Keyboard disabled")
        else:
            QMessageBox.critical(self, "Error", "Failed to disable")

    def try_enable(self):
        if enable_keyboard():
            QMessageBox.information(self, "Done", "Keyboard enabled")
        else:
            QMessageBox.critical(self, "Error", "Failed to enable")

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = LockoutApp()
    w.show()
    sys.exit(app.exec())

