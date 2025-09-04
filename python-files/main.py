import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QToolBar, QAction,
    QTabWidget, QWidget, QVBoxLayout, QPushButton, QMenu, QInputDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt


BOOKMARKS_FILE = "bookmarks.json"


class BrowserTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout(self)
        self.view = QWebEngineView()
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)

        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        menu = QMenu()
        add_bookmark_action = menu.addAction("📌 Add to Bookmarks")
        action = menu.exec_(self.view.mapToGlobal(position))

        if action == add_bookmark_action:
            title = self.view.title() or "Untitled"
            url = self.view.url().toString()
            self.main_window.add_bookmark(title, url, save=True)


class BookmarkButton(QPushButton):
    def __init__(self, name, url, main_window):
        super().__init__(name)
        self.url = url
        self.main_window = main_window

        self.clicked.connect(lambda: main_window.current_view().setUrl(QUrl(url)))
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        menu = QMenu()
        rename_action = menu.addAction("✏️ Rename")
        delete_action = menu.addAction("🗑️ Remove")
        action = menu.exec_(self.mapToGlobal(pos))

        if action == rename_action:
            new_name, ok = QInputDialog.getText(self, "Rename Bookmark", "New name:")
            if ok and new_name:
                self.setText(new_name)
                self.main_window.update_bookmark_name(self.url, new_name)

        elif action == delete_action:
            self.setParent(None)
            self.main_window.remove_bookmark(self.url)


class PyChrome(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyChrome")
        self.setGeometry(100, 100, 1200, 800)
        self.bookmarks = []

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_url_bar_from_tab)
        self.setCentralWidget(self.tabs)

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.url_bar)

        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(self.add_tab)
        self.toolbar.addAction(new_tab_action)

        self.bookmark_bar = QToolBar("Bookmarks")
        self.addToolBar(self.bookmark_bar)

        self.load_bookmarks()
        self.add_tab("https://www.google.com")

    def add_bookmark(self, name, url, save=False):
        if any(b['url'] == url for b in self.bookmarks):
            return

        btn = BookmarkButton(name, url, self)
        self.bookmark_bar.addWidget(btn)
        self.bookmarks.append({'name': name, 'url': url})

        if save:
            self.save_bookmarks()

    def remove_bookmark(self, url):
        self.bookmarks = [b for b in self.bookmarks if b['url'] != url]
        self.save_bookmarks()

    def update_bookmark_name(self, url, new_name):
        for b in self.bookmarks:
            if b['url'] == url:
                b['name'] = new_name
                break
        self.save_bookmarks()

    def save_bookmarks(self):
        with open(BOOKMARKS_FILE, 'w') as f:
            json.dump(self.bookmarks, f)

    def load_bookmarks(self):
        if os.path.exists(BOOKMARKS_FILE):
            with open(BOOKMARKS_FILE, 'r') as f:
                try:
                    self.bookmarks = json.load(f)
                except json.JSONDecodeError:
                    self.bookmarks = []

        for bm in self.bookmarks:
            self.add_bookmark(bm['name'], bm['url'], save=False)

    def add_tab(self, url="https://www.google.com"):
        if not url:
            url = "https://www.google.com"

        tab = BrowserTab(self)
        index = self.tabs.addTab(tab, "New Tab")
        self.tabs.setCurrentIndex(index)

        view = tab.view
        view.setUrl(QUrl(url))
        view.urlChanged.connect(lambda url, i=index: self.on_url_changed(url, i))

    def on_url_changed(self, url, index):
        if self.tabs.currentIndex() == index:
            self.url_bar.setText(url.toString())
        self.tabs.setTabText(index, url.host() or "New Tab")

    def current_view(self):
        return self.tabs.currentWidget().view

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if "." in text or text.startswith("http"):
            if not text.startswith("http"):
                text = "http://" + text
            url = QUrl(text)
        else:
            url = QUrl(f"https://www.google.com/search?q={text}")
        self.current_view().setUrl(url)

    def update_url_bar_from_tab(self, index):
        tab = self.tabs.widget(index)
        if tab:
            self.url_bar.setText(tab.view.url().toString())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PyChrome()
    window.show()
    sys.exit(app.exec_())
