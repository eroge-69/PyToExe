import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QToolBar, QToolButton,
    QTabWidget, QWidget, QVBoxLayout, QDialog, QPushButton
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

BOOKMARKS_FILE = "bookmarks.json"

class BrowserTab(QWidget):
    def __init__(self, parent=None, url="https://www.google.com"):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))
        self.layout.addWidget(self.browser)
        self.setLayout(self.layout)

class MinimalBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Browser")
        self.setGeometry(100, 100, 1000, 700)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
                color: #ffffff;
            }
            QToolBar {
                background-color: #1e1e1e;
                spacing: 6px;
            }
            QLineEdit {
                background-color: #2c2c2c;
                color: #ffffff;
                border: 1px solid #444;
                padding: 4px;
                border-radius: 4px;
            }
            QToolButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555;
                padding: 6px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #505050;
                border: 1px solid #888;
            }
            QToolButton:pressed {
                background-color: #666666;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #505050;
                border: 1px solid #888;
            }
            QPushButton:pressed {
                background-color: #666666;
            }
        """)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        self.bookmarks = self.load_bookmarks()

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.url_bar)

        self.add_toolbar_buttons()
        self.add_new_tab()

    def add_toolbar_buttons(self):
        def create_button(text, callback):
            btn = QToolButton()
            btn.setText(text)
            btn.clicked.connect(callback)
            self.toolbar.addWidget(btn)

        create_button("←", lambda: self.current_browser().back())
        create_button("→", lambda: self.current_browser().forward())
        create_button("⟳", lambda: self.current_browser().reload())
        create_button("★", self.add_bookmark)
        create_button("📂", self.show_bookmarks)
        create_button("+", self.add_new_tab)

    def current_browser(self):
        return self.tabs.currentWidget().browser

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "https://" + url
        self.current_browser().setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())

    def add_new_tab(self, url="https://www.google.com"):
        tab = BrowserTab(url=url)
        tab.browser.urlChanged.connect(self.update_url)
        index = self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentIndex(index)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def add_bookmark(self):
        url = self.current_browser().url().toString()
        if url not in self.bookmarks:
            self.bookmarks.append(url)
            self.save_bookmarks()
            print(f"Закладка добавлена: {url}")

    def show_bookmarks(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Закладки")
        layout = QVBoxLayout()
        for url in self.bookmarks:
            btn = QPushButton(url)
            btn.clicked.connect(lambda _, u=url: self.current_browser().setUrl(QUrl(u)))
            layout.addWidget(btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def load_bookmarks(self):
        if os.path.exists(BOOKMARKS_FILE):
            with open(BOOKMARKS_FILE, "r") as f:
                return json.load(f)
        return []

    def save_bookmarks(self):
        with open(BOOKMARKS_FILE, "w") as f:
            json.dump(self.bookmarks, f)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MinimalBrowser()
    window.show()
    sys.exit(app.exec_())
