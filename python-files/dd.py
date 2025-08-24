import sys
import subprocess
import socket
import json
import urllib.request
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton,
    QInputDialog, QMessageBox
)
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat
from PyQt5.QtCore import QTimer

PASSWORD = "Ashen@123321"
WEBHOOK_URL = "https://discord.com/api/webhooks/1408474394166169731/FR13zrMyHD6Xq8fQf6qWWD819kTfhwATCj5ubJ8NDdfUnHwCtXOcChF-64tGFaD58YwE"

class SOBFOXDetector(QWidget):
    def __init__(self):
        super().__init__()
        self.mpr_detected = False
        self.initUI()
        if not self.check_password("Enter password to open detector"):
            sys.exit(0)
        self.start_monitoring()

    def initUI(self):
        self.setWindowTitle("SOBFOX Detector")
        self.setGeometry(400, 200, 800, 450)
        self.layout = QVBoxLayout()
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.layout.addWidget(self.log)

        self.clear_btn = QPushButton("Clear Logs")
        self.clear_btn.clicked.connect(self.clear_logs)
        self.layout.addWidget(self.clear_btn)

        self.refresh_btn = QPushButton("Manual Refresh")
        self.refresh_btn.clicked.connect(self.check_for_mpr)
        self.layout.addWidget(self.refresh_btn)

        self.output_btn = QPushButton("Send OUTPUT to Discord")
        self.output_btn.clicked.connect(self.send_output)
        self.layout.addWidget(self.output_btn)

        self.setLayout(self.layout)

    def check_password(self, message):
        text, ok = QInputDialog.getText(self, "Password", message)
        return ok and text == PASSWORD

    def append_log(self, message, color="green"):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        self.log.moveCursor(QTextCursor.End)
        self.log.setCurrentCharFormat(fmt)
        self.log.append(message)
        self.log.moveCursor(QTextCursor.End)

    def clear_logs(self):
        if self.check_password("Enter password to clear logs"):
            self.log.clear()
            self.append_log("Logs cleared.", "green")
        else:
            self.append_log("Wrong password! Access denied.", "red")

    def start_monitoring(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_for_mpr)
        self.timer.start(5000)  # 5 seconds

    def check_for_mpr(self):
        try:
            result = subprocess.run(
                ["tasklist", "/m", "mpr.dll"], capture_output=True, text=True
            )
            detected = "mpr.dll" in result.stdout.lower()
            if detected:
                self.mpr_detected = True
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.append_log(f"[DETECTED] SOBFOX | {timestamp}", "red")
            else:
                self.mpr_detected = False
        except Exception as e:
            self.append_log(f"Error checking tasklist: {e}", "yellow")

    def send_output(self):
        if not self.mpr_detected:
            self.append_log("No MPR detected, nothing to send.", "green")
            return
        try:
            pc_name = socket.gethostname()
            local_ip = socket.gethostbyname(pc_name)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            content = f"[OUTPUT] SOBFOX DETECTED | {timestamp} | PC: {pc_name} | Local IP: {local_ip}"
            data = json.dumps({"content": content}).encode()
            req = urllib.request.Request(WEBHOOK_URL, data=data, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req)
            self.append_log("OUTPUT sent to Discord.", "green")
        except Exception as e:
            self.append_log(f"Webhook Error: {e}", "red")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SOBFOXDetector()
    window.show()
    sys.exit(app.exec_())
