# kiosk_browser.py
import sys
from PyQt5 import QtCore, QtWidgets, QtGui   # <- doplneno QtGui
from PyQt5.QtWebEngineWidgets import QWebEngineView

URL = "http://192.168.0.104:8000/"

class KioskBrowser(QtWidgets.QMainWindow):
    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.init_ui()

    def init_ui(self):
        # Web view
        self.webview = QWebEngineView(self)
        self.webview.setUrl(QtCore.QUrl(self.url))
        self.setCentralWidget(self.webview)

        # Window flags: bez rámečku
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        # Fullscreen
        self.showFullScreen()

    def keyPressEvent(self, event: QtGui.QKeyEvent):  # type: ignore
        # Esc nebo Ctrl+Q = ukoncit
        if event.key() == QtCore.Qt.Key_Escape or (
            event.key() == QtCore.Qt.Key_Q and event.modifiers() & QtCore.Qt.ControlModifier
        ):
            QtWidgets.QApplication.quit()
        else:
            super().keyPressEvent(event)


def main():
    app = QtWidgets.QApplication(sys.argv)
    browser = KioskBrowser(URL)
    browser.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
