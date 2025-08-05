
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class WebApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cloudcover Music")
        self.setGeometry(100, 100, 1280, 720)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://tune.cloudcovermusic.com/#/webautologin/OTEzNDA6MzI1Nzg6MC43MzE2MjE1OTA5NDEwMDI5"))
        self.setCentralWidget(self.browser)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebApp()
    window.show()
    sys.exit(app.exec_())
