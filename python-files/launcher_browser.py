from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
import sys

# Eigene Seite zum Abfangen von Spezial-Links wie fivem://
class CustomWebEnginePage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if url.scheme() in ["fivem", "steam", "ts3server"]:
            QDesktopServices.openUrl(url)  # öffnet mit dem Standard-Programm
            return False  # nicht im internen Browser öffnen
        return super().acceptNavigationRequest(url, _type, isMainFrame)

# Hauptfenster mit integriertem Browser
class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Launcher")
        self.setGeometry(100, 100, 1280, 720)

        self.browser = QWebEngineView()
        self.browser.setPage(CustomWebEnginePage(self.browser))

        # Deine Website
        self.browser.load(QUrl("http://185.117.3.155/Server-launcher+admin_panel/launcher.html"))

        self.setCentralWidget(self.browser)
        self.showMaximized()

# App starten
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    sys.exit(app.exec_())
