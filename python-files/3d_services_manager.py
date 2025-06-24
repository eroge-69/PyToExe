import sys
import os
import subprocess
import threading
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QFileDialog, QGroupBox, QGridLayout, QSizePolicy, QScrollArea, QLineEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPalette, QFont
import psutil

# --- CONFIG ---
# Service definitions: name, log file, health check port (if any)
SERVICES = [
    {"name": "DECA PROXY", "log": "logs/deca_proxy.log", "port": None},
    {"name": "DECA", "log": "logs/deca_service.log", "port": 8080},
    {"name": "UNITY", "log": "logs/unity_service.log", "port": 8081},
    {"name": "LICENSE", "log": "logs/license_server.log", "port": 5000},
]

# Find all .bat, .ps1, .py scripts in root folder
SCRIPT_EXTS = [".bat", ".ps1", ".py"]

# --- GUI CLASSES ---
class ServiceWidget(QWidget):
    def __init__(self, name, log_path, port=None):
        super().__init__()
        self.name = name
        self.log_path = log_path
        self.port = port
        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(2000)
        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.update_log)
        self.log_timer.start(1000)
        self.last_log = ""

    def init_ui(self):
        layout = QVBoxLayout()
        status_layout = QHBoxLayout()
        self.online_label = QLabel("ONLINE")
        self.offline_label = QLabel("OFFLINE")
        self.set_status(False)
        # Large service name
        name_label = QLabel(self.name)
        name_label.setFont(QFont("Arial", 28, QFont.Bold))
        name_label.setStyleSheet("padding-left: 16px; padding-right: 16px;")
        status_layout.addWidget(self.online_label)
        status_layout.addWidget(name_label)
        status_layout.addWidget(self.offline_label)
        # Restart button
        self.restart_btn = QPushButton("Restart")
        self.restart_btn.setFixedWidth(100)
        self.restart_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.restart_btn.clicked.connect(self.restart_service)
        status_layout.addWidget(self.restart_btn)
        layout.addLayout(status_layout)
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background-color: black; color: white; font-family: monospace;")
        self.log_box.setFixedHeight(120)
        layout.addWidget(self.log_box)
        self.setLayout(layout)

    def set_status(self, online):
        if online:
            self.online_label.setStyleSheet("color: #00FF99; font-weight: bold;")
            self.offline_label.setStyleSheet("color: #888888;")
        else:
            self.online_label.setStyleSheet("color: #888888;")
            self.offline_label.setStyleSheet("color: #FF3333; font-weight: bold;")

    def update_status(self):
        online = False
        if self.port:
            # Try to connect to health endpoint
            import socket
            try:
                s = socket.create_connection(("127.0.0.1", self.port), timeout=0.5)
                s.close()
                online = True
            except Exception:
                online = False
        else:
            # For proxy, check if log file exists and is being written to
            online = os.path.exists(self.log_path) and os.path.getsize(self.log_path) > 0
        self.set_status(online)

    def update_log(self):
        if os.path.exists(self.log_path):
            with open(self.log_path, "r", encoding="utf-8", errors="ignore") as f:
                data = f.read()
                if data != self.last_log:
                    self.log_box.setPlainText(data)
                    self.log_box.moveCursor(11)
                    self.last_log = data

    def restart_service(self):
        # Map service name to script or process
        service_scripts = {
            "DECA PROXY": "deca_proxy.py",
            "DECA": "deca_service.py",
            "UNITY": "unity_service.py",
            "LICENSE": "license_server.py"
        }
        script = service_scripts.get(self.name)
        if script:
            # Kill process by script name, then restart
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if script in ' '.join(proc.info['cmdline']):
                        proc.kill()
                except Exception:
                    pass
            # Restart
            if script.endswith('.py'):
                subprocess.Popen([sys.executable, script])

class ScriptButton(QWidget):
    def __init__(self, script_path):
        super().__init__()
        self.script_path = script_path
        self.init_ui()
    def init_ui(self):
        layout = QHBoxLayout()
        btn = QPushButton(os.path.basename(self.script_path))
        btn.clicked.connect(self.run_script)
        layout.addWidget(btn)
        self.setLayout(layout)
    def run_script(self):
        ext = os.path.splitext(self.script_path)[1].lower()
        if ext == ".bat":
            subprocess.Popen([self.script_path], shell=True)
        elif ext == ".ps1":
            subprocess.Popen(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", self.script_path])
        elif ext == ".py":
            subprocess.Popen([sys.executable, self.script_path])

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CellFree 3D Services Manager")
        self.resize(900, 700)
        layout = QVBoxLayout()
        # Top left: INSTALL1 and INSTALL2 buttons
        install_layout = QHBoxLayout()
        install1_btn = QPushButton("INSTALL1")
        install1_btn.setToolTip("Install Windows Dependencies")
        install1_btn.setFixedSize(120, 40)
        install1_btn.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #2196F3; color: white; border-radius: 8px;")
        install1_btn.clicked.connect(lambda: subprocess.Popen(['cmd.exe', '/c', 'start', '', 'install_windows_dependencies.bat']))
        install2_btn = QPushButton("INSTALL2")
        install2_btn.setToolTip("Install SellFee Complete")
        install2_btn.setFixedSize(120, 40)
        install2_btn.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #4CAF50; color: white; border-radius: 8px;")
        install2_btn.clicked.connect(lambda: subprocess.Popen(['cmd.exe', '/c', 'start', '', 'install_sellfee_complete.bat']))
        install_layout.addWidget(install1_btn)
        install_layout.addWidget(install2_btn)
        layout.addLayout(install_layout)
        # LAUNCH button at the top (styled as a real button)
        launch_btn = QPushButton("LAUNCH 3D SERVICES")
        launch_btn.setFixedHeight(60)
        launch_btn.setStyleSheet("font-size: 26px; font-weight: bold; background-color: #00FF99; color: black; border-radius: 12px; border: 2px solid #009966; margin: 10px;")
        launch_btn.clicked.connect(self.launch_services)
        layout.addWidget(launch_btn, alignment=Qt.AlignTop)
        self.service_widgets = []
        self.script_buttons = []
        for svc in SERVICES:
            w = ServiceWidget(svc["name"], svc["log"], svc["port"])
            self.service_widgets.append(w)
            layout.addWidget(w)
        # Restart all button
        restart_all_btn = QPushButton("Restart All Services")
        restart_all_btn.setFixedHeight(40)
        restart_all_btn.setStyleSheet("font-size: 18px; font-weight: bold;")
        restart_all_btn.clicked.connect(self.restart_all_services)
        layout.addWidget(restart_all_btn)
        # Scripts section
        layout.addWidget(QLabel("\nScripts & Tools:"))
        scripts_box = QGroupBox()
        scripts_layout = QVBoxLayout()
        for root, dirs, files in os.walk("."):
            for f in files:
                if any(f.lower().endswith(ext) for ext in SCRIPT_EXTS):
                    btn = ScriptButton(os.path.join(root, f))
                    self.script_buttons.append(btn)
                    scripts_layout.addWidget(btn)
        scripts_box.setLayout(scripts_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scripts_box)
        layout.addWidget(scroll)
        # Add search box for scripts
        search_layout = QHBoxLayout()
        search_label = QLabel("Quick Find:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to filter scripts/functions...")
        self.search_input.textChanged.connect(self.filter_scripts)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        self.setLayout(layout)

    def filter_scripts(self, text):
        text = text.lower()
        for btn in self.script_buttons:
            btn.setVisible(text in btn.text().lower())

    def restart_all_services(self):
        for w in self.service_widgets:
            w.restart_service()

    def launch_services(self):
        # Launch start_3d_services.bat in a new window, but do NOT close the manager
        subprocess.Popen(['cmd.exe', '/c', 'start', '', 'start_3d_services.bat'])

def main():
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
