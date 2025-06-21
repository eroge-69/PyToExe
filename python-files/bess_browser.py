import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QMessageBox
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import urllib.request

class BessBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BESS Browser")
        self.setMinimumSize(1000, 700)

        # Check internet
        if not self.check_internet():
            QMessageBox.critical(self, "No Internet", "Please connect to the internet.")
            sys.exit()

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.bessguards.com"))

        # Buttons
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.browser.back)

        forward_btn = QPushButton("Forward")
        forward_btn.clicked.connect(self.browser.forward)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.browser.reload)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(back_btn)
        btn_layout.addWidget(forward_btn)
        btn_layout.addWidget(refresh_btn)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addLayout(btn_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def check_internet(self):
        try:
            urllib.request.urlopen('https://www.google.com', timeout=3)
            return True
        except:
            return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BessBrowser()
    window.show()
    sys.exit(app.exec_())
