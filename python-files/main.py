import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget
from login import LoginWindow
from license_manager import LicenseManager
from download_portal import DownloadPortal
from analytics_dashboard import AnalyticsDashboard
from database import init_db

class MainApp(QMainWindow):
    def __init__(self, username, role):
        super().__init__()
        self.setWindowTitle(f"ZeroLight Dashboard - {username} ({role})")
        tabs = QTabWidget()
        if role == "admin":
            tabs.addTab(LicenseManager(), "License Manager")
            tabs.addTab(AnalyticsDashboard(), "Analytics")
        tabs.addTab(DownloadPortal(), "Downloads")
        self.setCentralWidget(tabs)

def launch_app():
    def handle_login(username, role):
        win = MainApp(username, role)
        win.show()
        app.exec_()

    init_db()
    app = QApplication(sys.argv)
    login = LoginWindow(handle_login)
    login.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    launch_app()