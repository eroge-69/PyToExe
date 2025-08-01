import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os

class DVJMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DVJ Software')
        self.setGeometry(100, 100, 1200, 800)
        self.webview = QWebEngineView(self)
        html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'index.html'))
        self.webview.load(QUrl.fromLocalFile(html_path))
        self.setCentralWidget(self.webview)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DVJMainWindow()
    window.show()
    sys.exit(app.exec_())
