import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLineEdit,
    QToolBar, QAction, QHBoxLayout, QTabBar, QMenu
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt


class BrowserTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.layout.addWidget(self.browser)
        self.setLayout(self.layout)

    def navigate_to(self, url):
        if not url.startswith("http"):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quilix")
        self.setGeometry(100, 100, 1200, 800)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setDocumentMode(True)
        self.setCentralWidget(self.tabs)

        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_urlbar)

        self.navbar = QToolBar()
        self.addToolBar(self.navbar)

        back_btn = QAction("←", self)
        back_btn.triggered.connect(self.go_back)
        self.navbar.addAction(back_btn)

        forward_btn = QAction("→", self)
        forward_btn.triggered.connect(self.go_forward)
        self.navbar.addAction(forward_btn)

        reload_btn = QAction("⟳", self)
        reload_btn.triggered.connect(self.reload_page)
        self.navbar.addAction(reload_btn)

        home_btn = QAction("🏠", self)
        home_btn.triggered.connect(self.navigate_home)
        self.navbar.addAction(home_btn)

        new_tab_btn = QAction("➕ Вкладка", self)
        new_tab_btn.triggered.connect(self.add_new_tab)
        self.navbar.addAction(new_tab_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)

        self.add_new_tab()

    def add_new_tab(self, url=None):
        new_tab = BrowserTab(self)
        i = self.tabs.addTab(new_tab, "Новая вкладка")
        self.tabs.setCurrentIndex(i)
        new_tab.browser.urlChanged.connect(self.update_urlbar)
        new_tab.browser.loadFinished.connect(lambda: self.tabs.setTabText(i, new_tab.browser.page().title()))
        new_tab.browser.setContextMenuPolicy(Qt.CustomContextMenu)
        new_tab.browser.customContextMenuRequested.connect(self.context_menu)

        if url:
            new_tab.navigate_to(url)

    def close_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)

    def current_browser(self):
        return self.tabs.currentWidget().browser

    def navigate_home(self):
        self.current_browser().setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        url = self.url_bar.text()
        self.current_browser().setUrl(QUrl(url if url.startswith("http") else "http://" + url))

    def update_urlbar(self, *args):
        browser = self.current_browser()
        if browser:
            self.url_bar.setText(browser.url().toString())

    def go_back(self):
        self.current_browser().back()

    def go_forward(self):
        self.current_browser().forward()

    def reload_page(self):
        self.current_browser().reload()

    def context_menu(self, point):
        menu = QMenu()
        menu.addAction("Назад", self.go_back)
        menu.addAction("Вперёд", self.go_forward)
        menu.addAction("Обновить", self.reload_page)
        menu.addAction("Домой", self.navigate_home)
        menu.exec_(self.sender().mapToGlobal(point))


app = QApplication(sys.argv)
QApplication.setApplicationName("Quilix")
window = Browser()
window.show()
sys.exit(app.exec_())