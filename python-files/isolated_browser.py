#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Isolated Tabs Browser с менеджером закладок
"""

import sys
import uuid
import tempfile
import shutil
import json
import os
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QLineEdit, QToolBar, QAction, QMessageBox, QStatusBar, QMenu,
    QDialog, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QVBoxLayout
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage

ICON_PATH = "icons"
BOOKMARKS_FILE = "bookmarks.json"


class BrowserTab(QWidget):
    def __init__(self, url="https://www.google.com"):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self._storage_dir = tempfile.mkdtemp(prefix="qprofile_")
        profile_name = f"profile_{uuid.uuid4().hex}"

        self.profile = QWebEngineProfile(profile_name, self)
        self.profile.setCachePath(self._storage_dir)
        self.profile.setPersistentStoragePath(self._storage_dir)

        self.page = QWebEnginePage(self.profile, self)
        self.view = QWebEngineView(self)
        self.view.setPage(self.page)

        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.context_menu)

        self.view.load(QUrl(url))
        self.layout.addWidget(self.view)

    def context_menu(self, pos):
        menu = QMenu()
        menu.addAction("Назад", self.view.back)
        menu.addAction("Вперёд", self.view.forward)
        menu.addAction("Обновить", self.view.reload)
        menu.addSeparator()
        menu.addAction("Сохранить в закладки", self.add_bookmark)
        menu.exec_(self.view.mapToGlobal(pos))

    def add_bookmark(self):
        main = self.window()
        if hasattr(main, "add_bookmark"):
            main.add_bookmark(self.view.title(), self.view.url().toString())

    def cleanup(self):
        try:
            shutil.rmtree(self._storage_dir)
        except:
            pass


class BookmarkManagerDialog(QDialog):
    def __init__(self, bookmarks, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Менеджер закладок")
        self.resize(600, 400)
        self.bookmarks = bookmarks  # Ссылка на список из главного окна

        self.table = QTableWidget(len(self.bookmarks), 2)
        self.table.setHorizontalHeaderLabels(["Название", "URL"])
        self.load_table()

        self.btn_add = QPushButton("Добавить")
        self.btn_delete = QPushButton("Удалить выбранные")
        self.btn_save = QPushButton("Сохранить")
        self.btn_close = QPushButton("Закрыть")

        self.btn_add.clicked.connect(self.add_row)
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_save.clicked.connect(self.save_bookmarks)
        self.btn_close.clicked.connect(self.close)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.btn_add)
        h_layout.addWidget(self.btn_delete)
        h_layout.addStretch()
        h_layout.addWidget(self.btn_save)
        h_layout.addWidget(self.btn_close)

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.table)
        v_layout.addLayout(h_layout)

        self.setLayout(v_layout)

    def load_table(self):
        self.table.setRowCount(len(self.bookmarks))
        for row, bm in enumerate(self.bookmarks):
            item_title = QTableWidgetItem(bm["title"])
            item_url = QTableWidgetItem(bm["url"])
            self.table.setItem(row, 0, item_title)
            self.table.setItem(row, 1, item_url)

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem("Новая закладка"))
        self.table.setItem(row, 1, QTableWidgetItem("http://"))

    def delete_selected(self):
        selected = set(idx.row() for idx in self.table.selectedIndexes())
        if not selected:
            QMessageBox.information(self, "Удаление", "Выберите строки для удаления")
            return
        for row in sorted(selected, reverse=True):
            self.table.removeRow(row)

    def save_bookmarks(self):
        new_bookmarks = []
        for row in range(self.table.rowCount()):
            title_item = self.table.item(row, 0)
            url_item = self.table.item(row, 1)
            title = title_item.text() if title_item else ""
            url = url_item.text() if url_item else ""
            if url.strip() == "":
                continue
            new_bookmarks.append({"title": title.strip(), "url": url.strip()})
        self.bookmarks.clear()
        self.bookmarks.extend(new_bookmarks)
        main = self.parent()
        if main and hasattr(main, "save_bookmarks"):
            main.save_bookmarks()
        QMessageBox.information(self, "Сохранено", "Закладки сохранены")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Isolated Tabs Browser")
        self.resize(1200, 820)
        self.setWindowIcon(QIcon(f"{ICON_PATH}/browser.png"))
        self.bookmarks = self.load_bookmarks()

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_urlbar_from_tab)
        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(24, 24))
        self.addToolBar(navtb)

        back_btn = QAction(QIcon(f"{ICON_PATH}/back.png"), "Назад", self)
        back_btn.triggered.connect(self.go_back)
        navtb.addAction(back_btn)

        forward_btn = QAction(QIcon(f"{ICON_PATH}/forward.png"), "Вперёд", self)
        forward_btn.triggered.connect(self.go_forward)
        navtb.addAction(forward_btn)

        reload_btn = QAction(QIcon(f"{ICON_PATH}/reload.png"), "Обновить", self)
        reload_btn.triggered.connect(self.reload_page)
        navtb.addAction(reload_btn)

        home_btn = QAction(QIcon(f"{ICON_PATH}/home.png"), "Домой", self)
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        navtb.addSeparator()

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        newtab_btn = QAction(QIcon(f"{ICON_PATH}/newtab.png"), "Новая вкладка", self)
        newtab_btn.triggered.connect(lambda: self.add_new_tab("https://www.google.com"))
        navtb.addAction(newtab_btn)

        bookmark_btn = QAction(QIcon(f"{ICON_PATH}/bookmark.png"), "Закладки", self)
        bookmark_btn.triggered.connect(lambda: self.show_bookmarks_menu(navtb))
        navtb.addAction(bookmark_btn)

        bookmark_mgr_btn = QAction(QIcon(f"{ICON_PATH}/bookmark.png"), "Менеджер закладок", self)
        bookmark_mgr_btn.triggered.connect(self.open_bookmark_manager)
        navtb.addAction(bookmark_mgr_btn)

        about_btn = QAction(QIcon(f"{ICON_PATH}/info.png"), "О браузере", self)
        about_btn.triggered.connect(self.show_about)
        navtb.addAction(about_btn)

        self.bookmark_menu = QMenu("Закладки", self)
        self.update_bookmark_menu()

        self.add_new_tab("https://www.google.com")

    def add_new_tab(self, url="about:blank", switch_to=True):
        tab = BrowserTab(url)
        index = self.tabs.addTab(tab, "Новая вкладка")
        tab.view.titleChanged.connect(lambda t, i=index: self.tabs.setTabText(i, t or "Новая вкладка"))
        tab.view.urlChanged.connect(lambda u, i=index: self.on_url_changed(u, i))
        if switch_to:
            self.tabs.setCurrentIndex(index)

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        if isinstance(widget, BrowserTab):
            widget.cleanup()
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.close()

    def navigate_to_url(self):
        current = self.tabs.currentWidget()
        if isinstance(current, BrowserTab):
            url = self.urlbar.text().strip()
            if not url.startswith(("http://", "https://")):
                url = "http://" + url
            current.view.load(QUrl(url))

    def on_url_changed(self, qurl, index):
        if index == self.tabs.currentIndex():
            self.urlbar.setText(qurl.toString())
            self.status.showMessage(qurl.toString(), 2000)

    def update_urlbar_from_tab(self, index):
        widget = self.tabs.widget(index)
        if isinstance(widget, BrowserTab):
            self.urlbar.setText(widget.view.url().toString())

    def go_back(self):
        current = self.tabs.currentWidget()
        if isinstance(current, BrowserTab):
            current.view.back()

    def go_forward(self):
        current = self.tabs.currentWidget()
        if isinstance(current, BrowserTab):
            current.view.forward()

    def reload_page(self):
        current = self.tabs.currentWidget()
        if isinstance(current, BrowserTab):
            current.view.reload()

    def navigate_home(self):
        current = self.tabs.currentWidget()
        if isinstance(current, BrowserTab):
            current.view.setUrl(QUrl("https://www.google.com"))

    def show_about(self):
        QMessageBox.information(self, "О браузере",
                                "Браузер с изолированными вкладками и менеджером закладок\n"
                                "Каждая вкладка — отдельный профиль (куки, кеш, localStorage)\n"
                                "© 2025")

    # Закладки
    def add_bookmark(self, title, url):
        self.bookmarks.append({"title": title, "url": url})
        self.save_bookmarks()
        self.update_bookmark_menu()

    def load_bookmarks(self):
        if os.path.exists(BOOKMARKS_FILE):
            try:
                with open(BOOKMARKS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_bookmarks(self):
        with open(BOOKMARKS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.bookmarks, f, ensure_ascii=False, indent=2)

    def update_bookmark_menu(self):
        self.bookmark_menu.clear()
        for bm in self.bookmarks:
            self.bookmark_menu.addAction(bm["title"], lambda u=bm["url"]: self.add_new_tab(u))

    def show_bookmarks_menu(self, toolbar):
        self.bookmark_menu.exec_(toolbar.mapToGlobal(toolbar.geometry().bottomLeft()))

    def open_bookmark_manager(self):
        dlg = BookmarkManagerDialog(self.bookmarks, self)
        dlg.exec_()
        self.update_bookmark_menu()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
