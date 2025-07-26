import sys
import os
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QToolBar,
    QLineEdit, QAction, QPushButton, QFileDialog, QInputDialog, QListWidget,
    QDialog, QLabel, QMessageBox, QProgressBar, QSizePolicy
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtGui import QPalette, QColor, QFont

BOOKMARKS_FILE = "bookmarks.txt"
HISTORY_FILE = "history.txt"
CONFIG_FILE = "config.txt"

def load_bookmarks():
    if os.path.exists(BOOKMARKS_FILE):
        with open(BOOKMARKS_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]
    return []

def save_bookmark(url):
    bookmarks = load_bookmarks()
    if url not in bookmarks:
        with open(BOOKMARKS_FILE, 'a', encoding='utf-8') as f:
            f.write(url + "\n")

def save_history(url):
    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(url + "\n")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            line = f.readline().strip()
            if line:
                return line
    return "https://www.google.com"

def save_config(homepage_url):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        f.write(homepage_url + "\n")

class BrowserTab(QWidget):
    def __init__(self, incognito=False, homepage=None):
        super().__init__()
        self.incognito = incognito

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)

        if incognito:
            self.profile = QWebEngineProfile()
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
            self.profile.setCachePath("")  # не сохраняем кеш
            self.profile.setPersistentStoragePath("")
            self.browser = QWebEngineView()
            self.browser.setPage(QWebEngineView(self).page())
            self.browser.page().setProfile(self.profile)
        else:
            self.browser = QWebEngineView()

        self.browser.setUrl(QUrl(homepage or load_config()))
        if not incognito:
            self.browser.urlChanged.connect(lambda url: save_history(url.toString()))

        self.layout.addWidget(self.browser)
        self.setLayout(self.layout)

class BookmarkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Закладки")
        self.setGeometry(200, 200, 500, 350)
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.addItems(load_bookmarks())
        self.list_widget.setFont(QFont("Segoe UI", 11))
        layout.addWidget(self.list_widget)

        self.open_button = QPushButton("Открыть")
        self.open_button.setFont(QFont("Segoe UI", 11))
        self.open_button.clicked.connect(self.open_selected)
        layout.addWidget(self.open_button)

        self.setLayout(layout)
        self.selected_url = None

    def open_selected(self):
        item = self.list_widget.currentItem()
        if item:
            self.selected_url = item.text()
            self.accept()

class DownloadItemWidget(QDialog):
    def __init__(self, download_item, parent=None):
        super().__init__(parent)
        self.download_item = download_item
        self.setWindowTitle(f"Скачивание: {download_item.path().split('/')[-1]}")
        self.setGeometry(300, 300, 450, 100)
        layout = QVBoxLayout()
        self.label = QLabel(f"Скачивание: {download_item.path()}")
        layout.addWidget(self.label)
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        self.setLayout(layout)

        download_item.downloadProgress.connect(self.on_progress)
        download_item.finished.connect(self.on_finished)
        download_item.accept()

    def on_progress(self, received, total):
        if total > 0:
            self.progress.setValue(int(received * 100 / total))

    def on_finished(self):
        self.label.setText("Скачивание завершено!")
        self.progress.setValue(100)

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F Browser")
        self.setGeometry(100, 100, 1300, 900)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)
        self.setCentralWidget(self.tabs)

        self.add_new_tab(homepage=load_config())

        self.menu_bar = self.menuBar()
        self.settings_menu = self.menu_bar.addMenu("Настройки")

        set_homepage_action = QAction("Установить стартовую страницу", self)
        set_homepage_action.triggered.connect(self.set_homepage)
        self.settings_menu.addAction(set_homepage_action)

        navtb = QToolBar("Навигация")
        navtb.setIconSize(QSize(28, 28))
        navtb.setMovable(False)
        navtb.setStyleSheet("QToolBar {spacing: 12px; padding: 8px;}")
        self.addToolBar(navtb)

        font_btn = QFont("Segoe UI", 14, QFont.Bold)

        self.back_btn = QAction("←", self)
        self.back_btn.setFont(font_btn)
        self.back_btn.triggered.connect(lambda: self.tabs.currentWidget().browser.back())
        navtb.addAction(self.back_btn)

        self.forward_btn = QAction("→", self)
        self.forward_btn.setFont(font_btn)
        self.forward_btn.triggered.connect(lambda: self.tabs.currentWidget().browser.forward())
        navtb.addAction(self.forward_btn)

        self.reload_btn = QAction("⟳", self)
        self.reload_btn.setFont(font_btn)
        self.reload_btn.triggered.connect(lambda: self.tabs.currentWidget().browser.reload())
        navtb.addAction(self.reload_btn)

        self.home_btn = QAction("🏠", self)
        self.home_btn.setFont(font_btn)
        self.home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(self.home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.setFont(QFont("Segoe UI", 14))
        self.url_bar.setMinimumWidth(600)
        self.url_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.url_bar)

        self.bookmark_btn = QAction("⭐", self)
        self.bookmark_btn.setFont(font_btn)
        self.bookmark_btn.triggered.connect(self.add_bookmark)
        navtb.addAction(self.bookmark_btn)

        self.view_bookmarks_btn = QAction("📚", self)
        self.view_bookmarks_btn.setFont(font_btn)
        self.view_bookmarks_btn.triggered.connect(self.view_bookmarks)
        navtb.addAction(self.view_bookmarks_btn)

        self.new_tab_btn = QAction("+ Вкладка", self)
        self.new_tab_btn.setFont(font_btn)
        self.new_tab_btn.triggered.connect(lambda: self.add_new_tab(homepage=load_config()))
        navtb.addAction(self.new_tab_btn)

        self.incognito_tab_btn = QAction("🕵️‍♂️ Инкогнито", self)
        self.incognito_tab_btn.setFont(font_btn)
        self.incognito_tab_btn.triggered.connect(self.add_incognito_tab)
        navtb.addAction(self.incognito_tab_btn)

        self.fullscreen_btn = QAction("🖥", self)
        self.fullscreen_btn.setFont(font_btn)
        self.fullscreen_btn.triggered.connect(self.toggle_fullscreen)
        navtb.addAction(self.fullscreen_btn)

        self.set_dark_mode()

        self.downloads = []

        profile = QWebEngineProfile.defaultProfile()
        profile.downloadRequested.connect(self.on_downloadRequested)

        self.shortcut_fullscreen = QAction(self)
        self.shortcut_fullscreen.setShortcut("F11")
        self.shortcut_fullscreen.triggered.connect(self.toggle_fullscreen)
        self.addAction(self.shortcut_fullscreen)

    def set_dark_mode(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, QColor(45, 45, 45))
        palette.setColor(QPalette.AlternateBase, QColor(30, 30, 30))
        palette.setColor(QPalette.ToolTipBase, Qt.lightGray)
        palette.setColor(QPalette.ToolTipText, Qt.lightGray)
        palette.setColor(QPalette.Text, Qt.gray)
        palette.setColor(QPalette.Button, QColor(45, 45, 45))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        QApplication.instance().setPalette(palette)

    def add_new_tab(self, homepage=None):
        tab = BrowserTab(incognito=False, homepage=homepage)
        i = self.tabs.addTab(tab, "Новая вкладка")
        self.tabs.setCurrentIndex(i)
        tab.browser.urlChanged.connect(lambda qurl, browser=tab.browser:
                                       self.update_url_bar(qurl, browser))
        tab.browser.titleChanged.connect(lambda title, i=i: self.tabs.setTabText(i, title))

    def add_incognito_tab(self):
        tab = BrowserTab(incognito=True, homepage=load_config())
        i = self.tabs.addTab(tab, "Инкогнито")
        self.tabs.setCurrentIndex(i)
        tab.browser.urlChanged.connect(lambda qurl, browser=tab.browser:
                                       self.update_url_bar(qurl, browser))
        tab.browser.titleChanged.connect(lambda title, i=i: self.tabs.setTabText(i, title))

    def close_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)

    def navigate_home(self):
        self.tabs.currentWidget().browser.setUrl(QUrl(load_config()))

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "https://www.google.com/search?q=" + url.replace(" ", "+")
        self.tabs.currentWidget().browser.setUrl(QUrl(url))

    def update_url_bar(self, q=None, browser=None):
        if browser != self.tabs.currentWidget().browser:
            return
        self.url_bar.setText(self.tabs.currentWidget().browser.url().toString())
        self.url_bar.setCursorPosition(0)

    def add_bookmark(self):
        url = self.tabs.currentWidget().browser.url().toString()
        save_bookmark(url)
        QMessageBox.information(self, "Закладки", f"Ссылка добавлена в закладки:\n{url}")

    def view_bookmarks(self):
        dialog = BookmarkDialog(self)
        if dialog.exec_():
            if dialog.selected_url:
                self.tabs.currentWidget().browser.setUrl(QUrl(dialog.selected_url))

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def on_downloadRequested(self, download):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", download.path())
        if path:
            download.setPath(path)
            dlg = DownloadItemWidget(download, self)
            dlg.show()
            self.downloads.append(dlg)
            download.accept()
        else:
            download.cancel()

    def set_homepage(self):
        current_homepage = load_config()
        url, ok = QInputDialog.getText(self, "Стартовая страница",
                                       "Введите URL стартовой страницы:",
                                       text=current_homepage)
        if ok and url:
            if not url.startswith("http"):
                url = "https://" + url
            save_config(url)
            QMessageBox.information(self, "Стартовая страница",
                                    f"Стартовая страница установлена на:\n{url}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = Browser()
    browser.show()
    sys.exit(app.exec_())
