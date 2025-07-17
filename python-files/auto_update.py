import sys
import os
import requests
import tempfile
import importlib.util
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLabel, QProgressBar, QFrame, QSplashScreen, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QBrush

# Hilangkan console di Windows jika bukan debug
if sys.platform == 'win32':
    import ctypes
    if 'DEBUG' not in os.environ:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Konfigurasi GitHub
GITHUB_CONFIG = {
    "username": "Kalantopus",
    "repository": "SLBNTGT",
    "branch": "main",
    "file_path": "surat_app.py"
}

class GitHubUpdater(QThread):
    update_progress = pyqtSignal(int)
    update_status = pyqtSignal(str)
    update_finished = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self.raw_url = (
            f"https://raw.githubusercontent.com/{GITHUB_CONFIG['username']}/"
            f"{GITHUB_CONFIG['repository']}/{GITHUB_CONFIG['branch']}/"
            f"{GITHUB_CONFIG['file_path']}"
        )

    def run(self):
        try:
            self.update_status.emit("🔍 Mengecek update...")
            self.update_progress.emit(20)
            local_file = os.path.join(tempfile.gettempdir(), "surat_app_latest.py")
            self.update_status.emit("📥 Mengunduh file dari GitHub...")
            self.update_progress.emit(50)
            response = requests.get(self.raw_url, timeout=30)
            response.raise_for_status()
            self.update_status.emit("💾 Menyimpan file...")
            self.update_progress.emit(80)
            with open(local_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            self.update_status.emit("✅ Update berhasil!")
            self.update_progress.emit(100)
            self.update_finished.emit(True, local_file)
        except requests.exceptions.RequestException as e:
            self.update_status.emit("❌ Gagal update")
            self.update_finished.emit(False, f"Koneksi error: {e}")
        except Exception as e:
            self.update_status.emit("❌ Error")
            self.update_finished.emit(False, str(e))

class ModernSplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor(76, 175, 80))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(pixmap.rect(), QBrush(QColor(76, 175, 80)))
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 24, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "📨 Surat App\n\nLoading...")
        painter.end()
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

class UpdateWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUI()
        self.updater = GitHubUpdater()
        self.updater.update_progress.connect(self.update_progress)
        self.updater.update_status.connect(self.update_status)
        self.updater.update_finished.connect(self.update_finished)

    def setupUI(self):
        self.setWindowTitle("🔄 Update - Surat App")
        self.setFixedSize(500, 200)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.center_window()

        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        hlayout = QVBoxLayout(header)
        title = QLabel("🔄 Auto Update")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("Mengecek update dari GitHub...")
        subtitle.setStyleSheet("color: white; font-size: 12px;")
        subtitle.setAlignment(Qt.AlignCenter)
        hlayout.addWidget(title)
        hlayout.addWidget(subtitle)

        self.status_label = QLabel("Memulai update...")
        self.status_label.setStyleSheet("font-size: 14px; color: #333;")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f0f0f0;
                text-align: center;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 6px;
            }
        """)

        layout.addWidget(header)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addStretch()
        self.setCentralWidget(main_widget)

    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        self.move((screen.width() - window.width()) // 2, (screen.height() - window.height()) // 2)

    def update_progress(self, val):
        self.progress_bar.setValue(val)

    def update_status(self, text):
        self.status_label.setText(text)

    def update_finished(self, success, result):
        if success:
            self.load_main_app(result)
        else:
            QMessageBox.critical(self, "Gagal", f"{result}")
            sys.exit(1)

    def load_main_app(self, file_path):
        try:
            spec = importlib.util.spec_from_file_location("surat_app", file_path)
            surat_app = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(surat_app)
            self.close()
            if hasattr(surat_app, 'SuratApp'):
                self.main_app = surat_app.SuratApp()
                self.main_app.show()
            else:
                QMessageBox.critical(self, "Error", "Class SuratApp tidak ditemukan.")
                sys.exit(1)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal load app: {e}")
            sys.exit(1)

class AutoUpdateApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setFont(QFont("Segoe UI", 10))
        os.environ["QT_LOGGING_RULES"] = "qt.qpa.plugin=false"

    def run(self):
        splash = ModernSplashScreen()
        splash.show()
        QTimer.singleShot(1000, lambda: self.start_update(splash))
        return self.app.exec_()

    def start_update(self, splash):
        splash.close()
        self.update_window = UpdateWindow()
        self.update_window.show()
        self.update_window.updater.start()

if __name__ == "__main__":
    auto_app = AutoUpdateApp()
    sys.exit(auto_app.run())
