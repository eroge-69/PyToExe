import os
import subprocess
import socket
import time
import webbrowser
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


# Config
XAMPP_PATH = r"C:\xampp"
APACHE_START = os.path.join(XAMPP_PATH, "apache_start.bat")
MYSQL_START = os.path.join(XAMPP_PATH, "mysql_start.bat")

def is_port_open(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)
            s.connect(('127.0.0.1', port))
            return True
        except:
            return False


class WorkerThread(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def run(self):
        # Steps of the check with progress updates
        total_steps = 5
        current_step = 0

        if not os.path.isdir(XAMPP_PATH):
            self.status.emit(f"XAMPP not found in {XAMPP_PATH}. Please install it.")
            self.finished.emit(False)
            return

        self.status.emit("Checking Apache status...")
        time.sleep(0.5)
        if not is_port_open(80):
            self.status.emit("Apache not running. Starting Apache...")
            self.start_apache()
            time.sleep(5)
        else:
            self.status.emit("Apache is running.")
        current_step += 1
        self.progress.emit(int(current_step / total_steps * 100))

        self.status.emit("Checking MySQL status...")
        time.sleep(0.5)
        if not is_port_open(3306):
            self.status.emit("MySQL not running. Starting MySQL...")
            self.start_mysql()
            time.sleep(5)
        else:
            self.status.emit("MySQL is running.")
        current_step += 1
        self.progress.emit(int(current_step / total_steps * 100))

        # Double-check ports
        if is_port_open(80) and is_port_open(3306):
            self.status.emit("All services running!")
            self.progress.emit(100)
            self.finished.emit(True)
        else:
            self.status.emit("Failed to start Apache or MySQL.")
            self.finished.emit(False)

    def start_apache(self):
        if os.path.isfile(APACHE_START):
            subprocess.Popen([APACHE_START], shell=True)
        else:
            self.status.emit("Apache start script not found!")

    def start_mysql(self):
        if os.path.isfile(MYSQL_START):
            subprocess.Popen([MYSQL_START], shell=True)
        else:
            self.status.emit("MySQL start script not found!")


class LauncherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SDS Launcher")
        self.setFixedSize(400, 200)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
        self.setup_ui()

        self.worker = WorkerThread()
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.check_finished)

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title_label = QLabel("🎓 SDS System Launcher")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        self.status_label = QLabel("Press 'Launch SDS' to start checks.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

        self.launch_button = QPushButton("Launch SDS")
        self.launch_button.clicked.connect(self.on_launch_clicked)
        self.layout.addWidget(self.launch_button)

    def update_progress(self, val):
        self.progress_bar.setValue(val)

    def update_status(self, message):
        self.status_label.setText(message)

    def check_finished(self, success):
        self.launch_button.setEnabled(True)
        if success:
            self.status_label.setText("✅ Services running, opening SDS...")
            webbrowser.open("http://localhost")
        else:
            QMessageBox.critical(self, "Error", "Could not start Apache or MySQL. Check XAMPP manually.")
            self.status_label.setText("❌ Failed to start required services.")

    def on_launch_clicked(self):
        self.launch_button.setEnabled(False)
        self.status_label.setText("Starting service checks...")
        self.progress_bar.setValue(0)
        self.worker.start()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = LauncherApp()
    window.show()
    sys.exit(app.exec())
