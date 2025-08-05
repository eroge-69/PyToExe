# epik17_app.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QUrl, QStandardPaths, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

class PersistentBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set up persistent storage
        storage_path = os.path.join(
            os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) 
            else QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation),
            "epik17_browser_data"
        )
        os.makedirs(storage_path, exist_ok=True)
        
        # Create profile with persistent storage
        self.profile = QWebEngineProfile("epik17_profile", self)
        self.profile.setPersistentStoragePath(storage_path)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        self.profile.setCachePath(os.path.join(storage_path, "cache"))
        
        # Set up the browser
        self.webview = QWebEngineView()
        self.webpage = self.webview.page()
        self.webpage.setProfile(self.profile)
        self.setCentralWidget(self.webview)
        
        # Configure window
        self.setWindowTitle("epik17.xyz")
        self.setGeometry(100, 100, 1200, 800)
        
        # Load application icon (use embedded if available)
        self.load_app_icon()
        
        # Block downloads
        self.profile.downloadRequested.connect(self.block_downloads)
        
        # Load the website
        self.webview.setUrl(QUrl("https://epik17.xyz"))
    
    def load_app_icon(self):
        """Try to load icon from embedded resources first, then download"""
        # Try to use embedded icon if available
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, 'shortlogo.png')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                return
        
        # Fall back to downloading
        self.network_manager = QNetworkAccessManager(self)
        icon_url = QUrl("https://epik17.xyz/content/images/shortlogo.png?t=1754399799")
        request = QNetworkRequest(icon_url)
        self.network_manager.finished.connect(self.on_icon_downloaded)
        self.network_manager.get(request)
    
    def on_icon_downloaded(self, reply):
        """Callback when icon download completes"""
        if reply.error():
            print("Failed to download icon:", reply.errorString())
            return
        
        pixmap = QPixmap()
        pixmap.loadFromData(reply.readAll())
        
        if not pixmap.isNull():
            self.setWindowIcon(QIcon(pixmap))
        reply.deleteLater()
    
    def block_downloads(self, download):
        """Block any download attempts"""
        if "/download" in download.url().toString():
            download.cancel()
            self.webview.page().runJavaScript("alert('Downloads are disabled');")

if __name__ == "__main__":
    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    
    app = QApplication(sys.argv)
    app.setOrganizationName("Epik17")
    app.setApplicationName("Epik17 Viewer")
    
    window = PersistentBrowser()
    window.show()
    sys.exit(app.exec_())