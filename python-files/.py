import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QToolBar, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class NiveinBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NiveinBrowser")
        self.setGeometry(100, 100, 1200, 800)

        # Browser widget
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.setCentralWidget(self.browser)

        # Navigation bar
        navbar = QToolBar()
        self.addToolBar(navbar)

        # Back button
        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)

        # Forward button
        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        # Reload button
        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        self.browser.urlChanged.connect(self.update_url)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())


app = QApplication(sys.argv)
window = NiveinBrowser()
window.show()
sys.exit(app.exec_())
