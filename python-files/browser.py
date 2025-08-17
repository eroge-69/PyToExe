import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QLineEdit, QMainWindow, QToolBar, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mini Przeglądarka w Pythonie")
        self.setGeometry(100, 100, 1200, 800)

        # Okno przeglądarki
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.setCentralWidget(self.browser)

        # Pasek narzędzi
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Pole do wpisywania adresów
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        # Przycisk wstecz
        back_btn = QAction("⏪", self)
        back_btn.triggered.connect(self.browser.back)
        toolbar.addAction(back_btn)

        # Przycisk do przodu
        forward_btn = QAction("⏩", self)
        forward_btn.triggered.connect(self.browser.forward)
        toolbar.addAction(forward_btn)

        # Przycisk odśwież
        reload_btn = QAction("🔄", self)
        reload_btn.triggered.connect(self.browser.reload)
        toolbar.addAction(reload_btn)

        # Synchronizacja paska adresu
        self.browser.urlChanged.connect(self.update_url)


    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            # Jeśli wpiszesz coś bez "http", np. "koty",
            # to otworzy Google Search
            url = "https://www.google.com/search?q=" + url
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())


app = QApplication(sys.argv)
window = Browser()
window.show()
sys.exit(app.exec_())
