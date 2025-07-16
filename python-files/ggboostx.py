import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox
import subprocess
import os

class GGBoostX(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GGBoostX - Made by Haaziq")
        self.setStyleSheet("background-color: #111; color: #0f0; font-size: 14px;")
        self.setGeometry(100, 100, 400, 200)
        layout = QVBoxLayout()

        self.label = QLabel("GGBoostX 🔥 FPS Booster
Created by Haaziq", self)
        layout.addWidget(self.label)

        self.boost_button = QPushButton("BOOST NOW 💥")
        self.boost_button.setStyleSheet("background-color: #0f0; color: #000; font-weight: bold; padding: 10px;")
        self.boost_button.clicked.connect(self.apply_boosts)
        layout.addWidget(self.boost_button)

        self.setLayout(layout)

    def apply_boosts(self):
        try:
            # Registry tweaks (example)
            tweaks = [
                r'reg add "HKLM\SYSTEM\ControlSet001\Control\Power" /v CsEnabled /t REG_DWORD /d 0 /f',
                r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f',
                r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f',
                r'reg add "HKLM\SYSTEM\CurrentControlSet\Services\SysMain" /v Start /t REG_DWORD /d 4 /f',
                r'reg add "HKCU\Control Panel\Desktop" /v MenuShowDelay /t REG_SZ /d 0 /f'
            ]
            for cmd in tweaks:
                subprocess.run(cmd, shell=True)
            QMessageBox.information(self, "GGBoostX", "All tweaks applied! Restart recommended.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = GGBoostX()
    win.show()
    sys.exit(app.exec_())
