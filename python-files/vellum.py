#Copyright Vellum Browser 2025
#Made by Emanuel Correia 
#Current update: "Goodbye Privacy"

# Import stuff (with TAXES)
import sys
import os
import json
import urllib.parse
import time
import subprocess
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import QWebChannel

class SettingsManager:
    def __init__(self):
        self.settings_file = os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation), "VellumBrowser", "settings.json")
        self.settings = {
            "search_engine": "Google",
            "font": "Segoe UI",
            "dark_mode": False,
            "homepage": "https://vellumbrowser.neocities.org/",
            "show_preferred_browser_popup": True
        }
        self.load_settings()
# If any of these don't work I jump
    def load_settings(self):
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings.update(json.load(f))
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def apply_settings(self):
        font = QFont(self.settings["font"], 12)
        QApplication.instance().setFont(font)
        palette = QPalette()
        colors = self.get_colors()
        for role, color in [
            (QPalette.Window, colors['window']),
            (QPalette.WindowText, colors['window_text']),
            (QPalette.Base, colors['base']),
            (QPalette.Text, colors['text']),
            (QPalette.Button, colors['button']),
            (QPalette.ButtonText, colors['button_text']),
            (QPalette.Highlight, colors['highlight']),
            (QPalette.HighlightedText, colors['highlighted_text'])
        ]:
            palette.setColor(role, QColor(*color))
        QApplication.instance().setPalette(palette)
        QApplication.instance().setStyleSheet(self.get_stylesheet(colors))
# PRETTY COLORZZZZ
    def get_colors(self):
        return {
            'window': (30, 30, 30) if self.settings["dark_mode"] else (245, 250, 255),
            'window_text': (200, 200, 200) if self.settings["dark_mode"] else (20, 20, 20),
            'base': (40, 40, 40, 230) if self.settings["dark_mode"] else (255, 255, 255, 230),
            'text': (200, 200, 200) if self.settings["dark_mode"] else (10, 10, 10),
            'button': (50, 50, 50) if self.settings["dark_mode"] else (250, 255, 255),
            'button_text': (200, 200, 200) if self.settings["dark_mode"] else (20, 20, 20),
            'highlight': (0, 130, 225, 200),
            'highlighted_text': (255, 255, 255),
            'border': 'rgba(100, 100, 100, 0.5)' if self.settings["dark_mode"] else 'rgba(80, 80, 80, 0.5)',
            'tab_background': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(60, 60, 60, 0.9), stop:1 rgba(80, 80, 80, 0.9))' if self.settings["dark_mode"] else 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 0.9), stop:1 rgba(170, 190, 210, 0.9))',
            'tab_selected': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 130, 225, 0.95), stop:1 rgba(0, 110, 205, 0.95))',
            'tab_unselected': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(50, 50, 50, 0.9), stop:1 rgba(70, 70, 70, 0.9))' if self.settings["dark_mode"] else 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(200, 220, 240, 0.9), stop:1 rgba(180, 200, 220, 0.9))',
            'toolbar_background': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(50, 50, 50, 0.8), stop:1 rgba(70, 70, 70, 0.8))' if self.settings["dark_mode"] else 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 0.8), stop:1 rgba(190, 210, 230, 0.8))',
            'button_background': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(60, 60, 60, 0.9), stop:1 rgba(80, 80, 80, 0.9))' if self.settings["dark_mode"] else 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 0.9), stop:1 rgba(170, 190, 210, 0.9))',
            'button_hover': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 130, 225, 0.95), stop:1 rgba(0, 110, 205, 0.95))',
            'lineedit_background': 'rgba(60, 60, 60, 0.95)' if self.settings["dark_mode"] else 'rgba(255, 255, 255, 0.95)',
            'lineedit_focus': 'rgba(70, 70, 70, 1.0)' if self.settings["dark_mode"] else 'rgba(255, 255, 255, 1.0)',
            'statusbar_background': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(50, 50, 50, 0.8), stop:1 rgba(70, 70, 70, 0.8))' if self.settings["dark_mode"] else 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 0.8), stop:1 rgba(190, 210, 230, 0.8))',
            'table_background': 'rgba(40, 40, 40, 0.9)' if self.settings["dark_mode"] else 'rgba(255, 255, 255, 0.9)',
            'header_background': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(60, 60, 60, 0.85), stop:1 rgba(80, 80, 80, 0.85))' if self.settings["dark_mode"] else 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 0.85), stop:1 rgba(180, 200, 220, 0.85))',
            'progress_background': 'rgba(60, 60, 60, 0.85)' if self.settings["dark_mode"] else 'rgba(255, 255, 255, 0.85)',
            'progress_chunk': 'qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0068c7, stop:1 #0055b7)',
            'textedit_background': 'rgba(40, 40, 40, 0.9)' if self.settings["dark_mode"] else 'rgba(255, 255, 255, 0.9)',
            'button_pressed': 'rgba(0, 90, 185, 0.9)'
        }
# WARNING: NIGHTMARE FUEL BELOW!
    def get_stylesheet(self, colors):
        return f"""
            QMainWindow, QDialog, QWidget {{ background: {colors['window']}; color: {colors['window_text']}; }}
            QTabWidget::pane {{ border: 1px solid {colors['border']}; border-radius: 8px; background: {colors['base']}; }}
            QTabBar::tab {{ background: {colors['tab_background']}; border: 1px solid {colors['border']}; border-top-left-radius: 8px; border-top-right-radius: 8px; padding: 6px 12px; margin: 2px; min-width: 80px; color: {colors['text']}; }}
            QTabBar::tab:selected {{ background: {colors['tab_selected']}; color: {colors['highlighted_text']}; border-bottom: 2px solid #0068c7; }}
            QTabBar::tab:!selected {{ background: {colors['tab_unselected']}; }}
            QToolBar {{ background: {colors['toolbar_background']}; border-bottom: 1px solid {colors['border']}; spacing: 8px; padding: 6px; margin: 3px; border-radius: 10px; }}
            QPushButton {{ background: {colors['button_background']}; border: 1px solid {colors['border']}; border-radius: 8px; padding: 5px 10px; min-width: 28px; min-height: 28px; color: {colors['button_text']}; }}
            QPushButton:hover {{ background: {colors['button_hover']}; border: 1px solid #0068c7; color: {colors['highlighted_text']}; }}
            QPushButton:pressed {{ background: {colors['button_pressed']}; }}
            QPushButton:checked {{ background: {colors['button_hover']}; color: {colors['highlighted_text']}; border: 1px solid #0068c7; }}
            QLineEdit {{ background: {colors['lineedit_background']}; border: 1px solid {colors['border']}; border-radius: 14px; padding: 5px 10px; color: {colors['text']}; }}
            QLineEdit:focus {{ border: 2px solid #0068c7; background: {colors['lineedit_focus']}; }}
            QStatusBar {{ background: {colors['statusbar_background']}; border-top: 1px solid {colors['border']}; color: {colors['text']}; margin: 3px; border-radius: 8px; }}
            QTableWidget {{ background: {colors['table_background']}; border: 1px solid {colors['border']}; border-radius: 8px; color: {colors['text']}; }}
            QHeaderView::section {{ background: {colors['header_background']}; border: 1px solid {colors['border']}; padding: 4px; border-radius: 4px; color: {colors['text']}; }}
            QProgressBar {{ background: {colors['progress_background']}; border: 2px solid #0048a7; border-radius: 3px; margin: 2px; color: {colors['text']}; }}
            QProgressBar::chunk {{ background: {colors['progress_chunk']}; border-radius: 3px; }}
            QTextEdit, QPlainTextEdit {{ background: {colors['textedit_background']}; border: 1px solid {colors['border']}; border-radius: 8px; padding: 10px; color: {colors['text']}; }}
            QComboBox {{ background: {colors['lineedit_background']}; border: 1px solid {colors['border']}; border-radius: 8px; padding: 5px; color: {colors['text']}; }}
            QComboBox:hover {{ background: {colors['button_hover']}; color: {colors['highlighted_text']}; }}
            QComboBox::drop-down {{ border-left: 1px solid {colors['border']}; }}
            QComboBox QAbstractItemView {{ background: {colors['base']}; color: {colors['text']}; selection-background-color: {colors['highlight']}; selection-color: {colors['highlighted_text']}; }}
            QLabel {{ color: {colors['text']}; }}
            QDockWidget {{ background: {colors['window']}; color: {colors['window_text']}; }}
        """

class PreferredBrowserDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Set Vellum Browser as Default")
        self.setMinimumSize(300, 150)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Would you like to set Vellum Browser as your default browser?"))
        self.dont_ask_again = QCheckBox("Don't ask again")
        layout.addWidget(self.dont_ask_again)
        button_layout = QHBoxLayout()
        yes_button = QPushButton("Yes")
        yes_button.clicked.connect(self.set_default_browser)
        no_button = QPushButton("No")
        no_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def set_default_browser(self):
        try:
            if sys.platform.startswith('win'):
                subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\http\\UserChoice',
                               '/v', 'ProgId', '/d', 'VellumBrowserHTML', '/f'], check=True)
            elif sys.platform.startswith('linux'):
                subprocess.run(['xdg-settings', 'set', 'default-web-browser', 'vellumbrowser.desktop'], check=True)
            elif sys.platform.startswith('darwin'):
                subprocess.run(['defaults', 'write', 'com.apple.LaunchServices/com.apple.launchservices.secure',
                               'LSHandlers', '-array-add', '{"LSHandlerURLScheme" = "http"; "LSHandlerRoleAll" = "org.vellumbrowser";}'], check=True)
            QMessageBox.information(self, "Success", "Vellum Browser set as default browser.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to set default browser: {str(e)}")
        if self.dont_ask_again.isChecked():
            self.parent().settings_manager.settings["show_preferred_browser_popup"] = False
            self.parent().settings_manager.save_settings()
        self.accept()

class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(400, 350)
        self.settings_manager = parent.settings_manager
        layout = QVBoxLayout()

        self.search_combo = QComboBox()
        self.search_combo.addItems(["Google", "Bing", "DuckDuckGo"])
        self.search_combo.setCurrentText(self.settings_manager.settings["search_engine"])
        layout.addWidget(QLabel("Search Engine:"))
        layout.addWidget(self.search_combo)

        self.font_combo = QComboBox()
        self.font_combo.addItems(["Segoe UI", "Arial", "Times New Roman", "Verdana"])
        self.font_combo.setCurrentText(self.settings_manager.settings["font"])
        layout.addWidget(QLabel("Font:"))
        layout.addWidget(self.font_combo)

        self.dark_mode_check = QCheckBox("Dark Mode")
        self.dark_mode_check.setChecked(self.settings_manager.settings["dark_mode"])
        layout.addWidget(self.dark_mode_check)

        self.homepage_edit = QLineEdit(self.settings_manager.settings["homepage"])
        layout.addWidget(QLabel("Homepage:"))
        layout.addWidget(self.homepage_edit)

        self.popup_check = QCheckBox("Show Set Default Browser Popup")
        self.popup_check.setChecked(self.settings_manager.settings["show_preferred_browser_popup"])
        layout.addWidget(self.popup_check)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addStretch()
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def save_settings(self):
        self.settings_manager.settings.update({
            "search_engine": self.search_combo.currentText(),
            "font": self.font_combo.currentText(),
            "dark_mode": self.dark_mode_check.isChecked(),
            "homepage": self.homepage_edit.text().strip() or "https://vellumbrowser.neocities.org/",
            "show_preferred_browser_popup": self.popup_check.isChecked()
        })
        self.settings_manager.save_settings()
        self.settings_manager.apply_settings()
        self.accept()

class BookmarkManager:
    def __init__(self):
        self.bookmarks_file = os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation), "VellumBrowser", "bookmarks.json")
        self.bookmarks = []
        self.load_bookmarks()

    def load_bookmarks(self):
        os.makedirs(os.path.dirname(self.bookmarks_file), exist_ok=True)
        try:
            if os.path.exists(self.bookmarks_file):
                with open(self.bookmarks_file, 'r') as f:
                    self.bookmarks = json.load(f)
        except Exception as e:
            print(f"Error loading bookmarks: {e}")

    def save_bookmarks(self):
        try:
            with open(self.bookmarks_file, 'w') as f:
                json.dump(self.bookmarks, f, indent=2)
        except Exception as e:
            print(f"Error saving bookmarks: {e}")

    def add_bookmark(self, url, title):
        if not any(b['url'] == url for b in self.bookmarks):
            self.bookmarks.append({'title': title, 'url': url, 'date_added': datetime.now().isoformat()})
            self.save_bookmarks()
            return True
        return False

    def remove_bookmark(self, url):
        self.bookmarks = [b for b in self.bookmarks if b['url'] != url]
        self.save_bookmarks()

    def is_bookmarked(self, url):
        return any(b['url'] == url for b in self.bookmarks)

    def import_bookmarks(self, file_path):
        try:
            with open(file_path, 'r') as f:
                imported = json.load(f)
                for bookmark in imported:
                    if not any(b['url'] == bookmark['url'] for b in self.bookmarks):
                        self.bookmarks.append(bookmark)
                self.save_bookmarks()
                return True
        except Exception as e:
            print(f"Error importing bookmarks: {e}")
            return False

    def export_bookmarks(self, file_path):
        try:
            with open(file_path, 'w') as f:
                json.dump(self.bookmarks, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting bookmarks: {e}")
            return False

class BookmarkDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Bookmarks")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout()
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Title", "URL"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        button_layout = QHBoxLayout()
        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self.open_selected)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_selected)
        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self.import_bookmarks)
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_bookmarks)
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.export_button)
        button_layout.addStretch()
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.table.itemSelectionChanged.connect(self.update_buttons)

    def populate_bookmarks(self, bookmarks):
        self.table.setRowCount(0)
        for bookmark in bookmarks:
            row = self.table.rowCount()
            self.table.insertRow(row)
            title_item = QTableWidgetItem(bookmark['title'])
            title_item.setData(Qt.UserRole, bookmark['url'])
            self.table.setItem(row, 0, title_item)
            self.table.setItem(row, 1, QTableWidgetItem(bookmark['url']))

    def update_buttons(self):
        selected = len(self.table.selectedItems()) > 0
        self.open_button.setEnabled(selected)
        self.delete_button.setEnabled(selected)

    def open_selected(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            url = selected_items[0].data(Qt.UserRole)
            self.parent().navigate_to_url_external(url)

    def delete_selected(self):
        selected_rows = {item.row() for item in self.table.selectedItems()}
        for row in sorted(selected_rows, reverse=True):
            url = self.table.item(row, 1).text()
            self.parent().bookmark_manager.remove_bookmark(url)
            self.table.removeRow(row)

    def import_bookmarks(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Bookmarks", "", "JSON Files (*.json)")
        if file_path and self.parent().bookmark_manager.import_bookmarks(file_path):
            self.populate_bookmarks(self.parent().bookmark_manager.bookmarks)
            QMessageBox.information(self, "Success", "Bookmarks imported successfully!")
        elif file_path:
            QMessageBox.warning(self, "Error", "Failed to import bookmarks.")

    def export_bookmarks(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Bookmarks", "bookmarks.json", "JSON Files (*.json)")
        if file_path and self.parent().bookmark_manager.export_bookmarks(file_path):
            QMessageBox.information(self, "Success", "Bookmarks exported successfully!")
        elif file_path:
            QMessageBox.warning(self, "Error", "Failed to export bookmarks.")

class HistoryManager(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("History")
        self.setMinimumSize(800, 600)
        self.history_file = os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation), "VellumBrowser", "history.json")
        self.history_data = []
        self.load_history()
        layout = QVBoxLayout()
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search history...")
        self.search_bar.textChanged.connect(self.filter_history)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_bar)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Title", "URL", "Last Visited", "Visits"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(2, Qt.DescendingOrder)
        button_layout = QHBoxLayout()
        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self.open_selected)
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)
        self.clear_button = QPushButton("Clear All History")
        self.clear_button.clicked.connect(self.clear_history)
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        layout.addLayout(search_layout)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.table.itemSelectionChanged.connect(self.update_buttons)
        self.populate_history()

    def load_history(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.history_data = json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")

    def save_history(self):
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history_data, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def add_history_entry(self, url, title):
        if not url.startswith(("http://", "https://")) or not title:
            return
        now = datetime.now().isoformat()
        existing_entry = next((entry for entry in self.history_data if entry['url'] == url), None)
        if existing_entry:
            existing_entry.update({'visit_count': existing_entry['visit_count'] + 1, 'last_visited': now, 'title': title})
        else:
            self.history_data.append({'title': title, 'url': url, 'first_visited': now, 'last_visited': now, 'visit_count': 1})
        self.save_history()
        self.populate_history()

    def populate_history(self):
        self.table.setRowCount(0)
        for entry in self.history_data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            title_item = QTableWidgetItem(entry['title'])
            title_item.setData(Qt.UserRole, entry['url'])
            self.table.setItem(row, 0, title_item)
            self.table.setItem(row, 1, QTableWidgetItem(entry['url']))
            self.table.setItem(row, 2, QTableWidgetItem(datetime.fromisoformat(entry['last_visited']).strftime("%Y-%m-%d %H:%M:%S")))
            count_item = QTableWidgetItem(str(entry['visit_count']))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, count_item)

    def filter_history(self):
        search_text = self.search_bar.text().lower()
        for row in range(self.table.rowCount()):
            self.table.setRowHidden(row, not (search_text in self.table.item(row, 0).text().lower() or search_text in self.table.item(row, 1).text().lower()))

    def update_buttons(self):
        selected = len(self.table.selectedItems()) > 0
        self.open_button.setEnabled(selected)
        self.delete_button.setEnabled(selected)

    def open_selected(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            self.parent().navigate_to_url_external(selected_items[0].data(Qt.UserRole))

    def delete_selected(self):
        selected_rows = {item.row() for item in self.table.selectedItems()}
        for row in sorted(selected_rows, reverse=True):
            url = self.table.item(row, 1).text()
            self.history_data = [entry for entry in self.history_data if entry['url'] != url]
            self.table.removeRow(row)
        self.save_history()

    def clear_history(self):
        if QMessageBox.question(self, 'Clear History', 'Are you sure you want to delete ALL browsing history?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.history_data = []
            self.table.setRowCount(0)
            self.save_history()

class DownloadManager(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Downloads")
        self.setMinimumSize(600, 400)
        self.downloads = []
        self.download_speeds = {}
        layout = QVBoxLayout()
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Filename", "Progress", "Size", "Speed", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        button_layout = QHBoxLayout()
        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self.open_selected)
        self.open_folder_button = QPushButton("Open Folder")
        self.open_folder_button.clicked.connect(self.open_folder)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_selected)
        self.clear_button = QPushButton("Clear Completed")
        self.clear_button.clicked.connect(self.clear_completed)
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.open_folder_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.table.itemSelectionChanged.connect(self.update_buttons)

    def add_download(self, download):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.downloads.append(download)
        self.download_speeds[row] = {'last_bytes': 0, 'last_time': time.time()}
        filename_item = QTableWidgetItem(os.path.basename(download.path()))
        filename_item.setData(Qt.UserRole, download.path())
        self.table.setItem(row, 0, filename_item)
        progress_widget = QWidget()
        progress_layout = QHBoxLayout(progress_widget)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setTextVisible(False)
        progress_label = QLabel("0%")
        progress_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        progress_label.setMinimumWidth(40)
        progress_layout.addWidget(progress_bar)
        progress_layout.addWidget(progress_label)
        self.table.setCellWidget(row, 1, progress_widget)
        self.table.setItem(row, 2, QTableWidgetItem("0 B"))
        self.table.setItem(row, 3, QTableWidgetItem("0 B/s"))
        self.table.setItem(row, 4, QTableWidgetItem("Downloading"))
        download.downloadProgress.connect(lambda bytesReceived, bytesTotal, r=row: self.update_progress(r, bytesReceived, bytesTotal))
        download.finished.connect(lambda r=row: self.download_finished(r))
        if not self.isVisible():
            self.show()

    def update_progress(self, row, bytesReceived, bytesTotal):
        if bytesTotal > 0:
            percent = int((bytesReceived / bytesTotal) * 100)
            progress_widget = self.table.cellWidget(row, 1)
            progress_widget.findChild(QProgressBar).setValue(percent)
            progress_widget.findChild(QLabel).setText(f"{percent}%")
            self.table.item(row, 2).setText(self.format_size(bytesTotal))
            now = time.time()
            last_bytes, last_time = self.download_speeds[row]['last_bytes'], self.download_speeds[row]['last_time']
            if now > last_time:
                self.table.item(row, 3).setText(f"{self.format_size((bytesReceived - last_bytes) / (now - last_time))}/s")
            self.download_speeds[row].update({'last_bytes': bytesReceived, 'last_time': now})

    def download_finished(self, row):
        status_item = self.table.item(row, 4)
        download = self.downloads[row]
        status_item.setText({QWebEngineDownloadItem.DownloadCompleted: "Completed", QWebEngineDownloadItem.DownloadCancelled: "Canceled"}.get(download.state(), "Error"))
        status_item.setForeground(QBrush(QColor(0, 128, 0) if download.state() == QWebEngineDownloadItem.DownloadCompleted else QColor(128, 0, 0)))

    def format_size(self, bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"

    def update_buttons(self):
        selected_rows = {item.row() for item in self.table.selectedItems()}
        self.open_button.setEnabled(False)
        self.open_folder_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        if selected_rows:
            row = next(iter(selected_rows))
            is_completed = self.table.item(row, 4).text() == "Completed"
            self.open_button.setEnabled(is_completed)
            self.open_folder_button.setEnabled(is_completed)
            self.cancel_button.setEnabled(not is_completed)

    def open_selected(self):
        selected_rows = {item.row() for item in self.table.selectedItems()}
        if selected_rows:
            path = self.table.item(next(iter(selected_rows)), 0).data(Qt.UserRole)
            if os.path.exists(path):
                if not QDesktopServices.openUrl(QUrl.fromLocalFile(path)):
                    QMessageBox.warning(self, "Error", "Could not open file with default application")
            else:
                QMessageBox.warning(self, "Error", "The file no longer exists.")

    def open_folder(self):
        selected_rows = {item.row() for item in self.table.selectedItems()}
        if selected_rows:
            path = self.table.item(next(iter(selected_rows)), 0).data(Qt.UserRole)
            if os.path.exists(path):
                if not QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(path))):
                    QMessageBox.warning(self, "Error", "Could not open folder in file explorer")
            else:
                QMessageBox.warning(self, "Error", "The file no longer exists.")

    def cancel_selected(self):
        selected_rows = {item.row() for item in self.table.selectedItems()}
        if selected_rows:
            row = next(iter(selected_rows))
            download = self.downloads[row]
            if download.state() == QWebEngineDownloadItem.DownloadInProgress:
                download.cancel()
                self.table.item(row, 4).setText("Canceled")
                self.table.item(row, 4).setForeground(QBrush(QColor(128, 0, 0)))

    def clear_completed(self):
        for row in range(self.table.rowCount() - 1, -1, -1):
            if self.table.item(row, 4).text() in ["Completed", "Canceled", "Error"]:
                self.table.removeRow(row)
                del self.downloads[row]
                del self.download_speeds[row]
# YES CHINESE STEAL ME' NAME AND DATA
class CreditsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Vellum Browser Credits")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout()
        table = QTableWidget(1, 3)
        table.setHorizontalHeaderLabels(["Creator", "Version", "Special Thanks"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.setItem(0, 0, QTableWidgetItem("Made By Emanuel"))
        table.setItem(0, 1, QTableWidgetItem("Version 2.2"))
        table.setItem(0, 2, QTableWidgetItem("Rodrigo Magro and Francisco"))
        layout.addWidget(table)
        thanks_label = QLabel("Thank you for installing the browser, it’s a small project that takes a lot of work and I hope you enjoy!")
        thanks_label.setWordWrap(True)
        layout.addWidget(thanks_label)
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

class HelpDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Vellum Browser Help")
        self.setMinimumSize(800, 600)
        self.current_button = None
        layout = QHBoxLayout()
        button_panel = QWidget()
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignTop)
        self.help_content = {
            "Introduction": """
                <h2>Introduction</h2><p>Welcome to Vellum Browser, a lightweight, fast, and feature-rich web browser. Visit <span style="color: blue;">https://vellumbrowser.neocities.org/</span>.</p>
                <h3>Getting Started</h3><p>- Enter a URL or search query in the address bar and press <b>Enter</b> or click "Go".<br>- Use navigation buttons (⌂, ◀, ▶, ⟳).<br>- Right-click tabs for advanced options.<br>- Customize settings via the ⚙ button.<br>- Press <b>Ctrl+?</b> for help.<br>- Press <b>F11</b> for fullscreen.<br>- Press <b>Ctrl+End</b> to move cursor to end of address bar.</p>
                <h3>Keybinds</h3><p>- <b>Ctrl+?</b>: Help<br>- <b>Esc</b>: Clear address bar<br>- <b>F11</b>: Fullscreen<br>- <b>Ctrl+End</b>: Move cursor to end</p>""",
            "New Tab": """
                <h2>New Tab</h2><p>Open a fresh tab at your homepage.</p><h3>Usage</h3><p>- Click "+" or press <b>Ctrl+T</b>.<br>- Close tabs with "x" or right-click.</p><h3>Keybinds</h3><p>- <b>Ctrl+T</b>: New tab</p>""",
            "Bookmarks": """
                <h2>Bookmarks</h2><p>Save favorite websites.</p><h3>Usage</h3><p>- Click "★" or press <b>Ctrl+B</b>.<br>- Access via "✰ Bookmarks".</p><h3>Keybinds</h3><p>- <b>Ctrl+B</b>: Toggle bookmark</p>""",
            "History": """
                <h2>History</h2><p>Track and revisit websites.</p><h3>Usage</h3><p>- Open via "🕮" or <b>Ctrl+H</b>.<br>- Search with the search bar.</p><h3>Keybinds</h3><p>- <b>Ctrl+H</b>: History</p>""",
            "Downloads": """
                <h2>Downloads</h2><p>Manage downloaded files.</p><h3>Usage</h3><p>- Open via "↓".<br>- Monitor progress, open files, or cancel.</p>""",
            "Credits": """
                <h2>Credits</h2><p>Acknowledges the team.</p><h3>Usage</h3><p>- Open via <b>Ctrl+J</b>.</p><h3>Keybinds</h3><p>- <b>Ctrl+J</b>: Credits</p>""",
            "Console": """
                <h2>Debug Console</h2><p>Inspect JavaScript logs and execute scripts.</p><h3>Usage</h3><p>- Toggle with <b>F12</b> or right-click tab.<br>- Enter JavaScript code.</p><h3>Keybinds</h3><p>- <b>F12</b>: Console</p>""",
            "Settings": """
                <h2>Settings</h2><p>Customize your experience.</p><h3>Usage</h3><p>- Open via "⚙".<br>- Choose search engine, font, dark mode, homepage, and default browser popup.</p>"""
        }
        self.buttons = {section: QPushButton(section) for section in self.help_content}
        for section, btn in self.buttons.items():
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, s=section: self.show_section(s))
            button_layout.addWidget(btn)
        self.buttons["Introduction"].setChecked(True)
        button_layout.addStretch()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        button_panel.setLayout(button_layout)
        self.help_text = QTextEdit()
        self.help_text.setReadOnly(True)
        self.help_text.setFont(QFont("Segoe UI", 12))
        self.show_section("Introduction")
        layout.addWidget(button_panel, 1)
        layout.addWidget(self.help_text, 3)
        self.setLayout(layout)

    def show_section(self, section):
        self.help_text.setHtml(self.help_content[section])
        if self.current_button:
            self.buttons[self.current_button].setChecked(False)
        self.buttons[section].setChecked(True)
        self.current_button = section

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vellum Browser")
        self.setGeometry(100, 100, 1024, 768)
        self.is_fullscreen = False
        self.normal_geometry = self.geometry()
        self.toolbar_visible = True
        self.statusbar_visible = True
        self.pinned_tabs = []
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.setCentralWidget(self.tabs)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_url_from_tab)
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.show_tab_context_menu)
        self.setup_managers()
        self.setup_ui()
        self.add_new_tab()
        self.setup_shortcuts()
        self.settings_manager.apply_settings()
        settings = QSettings("VellumBrowser", "AppSettings")
        if not settings.value("hasShownPreferredBrowserPopup", False, type=bool) and self.settings_manager.settings["show_preferred_browser_popup"]:
            self._preferred_browser_dialog.show()
            settings.setValue("hasShownPreferredBrowserPopup", True)

    def setup_managers(self):
        self._settings_manager = SettingsManager()
        self._bookmark_manager = BookmarkManager()
        self._history_manager = HistoryManager(self)
        self._download_manager = DownloadManager(self)
        self._credits_dialog = CreditsDialog(self)
        self._help_dialog = HelpDialog(self)
        self._preferred_browser_dialog = PreferredBrowserDialog(self)
        self._settings_dialog = SettingsDialog(self)

    def setup_ui(self):
        self.toolbar = QToolBar("Navigation", self)
        self.toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.toolbar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.toolbar.customContextMenuRequested.connect(self.show_toolbar_context_menu)
        self.home_btn = QPushButton("⌂")
        self.home_btn.clicked.connect(self.go_home)
        self.back_btn = QPushButton("◀")
        self.back_btn.clicked.connect(lambda: self.animate_button(self.back_btn, self.back))
        self.forward_btn = QPushButton("▶")
        self.forward_btn.clicked.connect(lambda: self.animate_button(self.forward_btn, self.forward))
        self.reload_btn = QPushButton("⟳")
        self.reload_btn.clicked.connect(self.reload)
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter website address or search query")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.installEventFilter(self)
        self.bookmark_btn = QPushButton("★")
        self.bookmark_btn.setFixedSize(28, 28)
        self.bookmark_btn.setStyleSheet("QPushButton { border: none; background: transparent; } QPushButton:hover { color: #0068c7; } QPushButton:checked { color: #ffcc00; }")
        self.bookmark_btn.setCheckable(True)
        self.bookmark_btn.clicked.connect(self.toggle_bookmark)
        url_container = QWidget()
        url_layout = QHBoxLayout(url_container)
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.addWidget(self.url_bar)
        url_layout.addWidget(self.bookmark_btn)
        self.go_btn = QPushButton("Go")
        self.go_btn.clicked.connect(self.navigate_to_url)
        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.clicked.connect(self.add_new_tab)
        self.downloads_btn = QPushButton("↓")
        self.downloads_btn.clicked.connect(self._download_manager.show)
        self.history_btn = QPushButton("🕮")
        self.history_btn.clicked.connect(self._history_manager.show)
        self.bookmarks_menu_btn = QPushButton("✰ Bookmarks")
        self.bookmarks_menu_btn.clicked.connect(self.show_bookmarks)
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.clicked.connect(self._settings_dialog.show)
        self.help_btn = QPushButton("?")
        self.help_btn.clicked.connect(self._help_dialog.show)
        for btn in [self.home_btn, self.back_btn, self.forward_btn, self.reload_btn, url_container, self.go_btn, self.new_tab_btn, self.downloads_btn, self.history_btn, self.bookmarks_menu_btn, self.settings_btn, self.help_btn]:
            self.toolbar.addWidget(btn)
        self.status = QStatusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setTextVisible(False)
        self.status.addPermanentWidget(self.progress_bar)
        self.progress_bar.hide()
        self.setStatusBar(self.status)
        self.reload_timer = QTimer(self)
        self.reload_timer.timeout.connect(self.update_reload_animation)
# LAZY MODE
    def setup_shortcuts(self):
        shortcuts = [
            ("Ctrl+T", self.add_new_tab),
            ("Ctrl+Shift+T", lambda: self.add_new_tab(private=True)),
            ("Ctrl+B", self.toggle_bookmark),
            ("Ctrl+H", self._history_manager.show),
            ("Ctrl+J", self._credits_dialog.show),
            ("Ctrl+?", self._help_dialog.show),
            ("F11", self.toggle_fullscreen),
            ("Ctrl+End", lambda: (self.url_bar.setFocus(), self.url_bar.setCursorPosition(len(self.url_bar.text())))),
            ("F12", self.toggle_debug_console)
        ]
        for key, slot in shortcuts:
            QShortcut(QKeySequence(key), self).activated.connect(slot)

    def animate_button(self, button, action):
        rect = button.geometry()
        anim_group = QSequentialAnimationGroup()
        offset = -3 if button == self.back_btn else 3 if button == self.forward_btn else 0
        anim_out = QPropertyAnimation(button, b"geometry")
        anim_out.setStartValue(rect)
        anim_out.setEndValue(QRect(rect.x() + offset, rect.y(), rect.width(), rect.height()))
        anim_out.setDuration(100)
        anim_back = QPropertyAnimation(button, b"geometry")
        anim_back.setStartValue(QRect(rect.x() + offset, rect.y(), rect.width(), rect.height()))
        anim_back.setEndValue(rect)
        anim_back.setDuration(100)
        anim_group.addAnimation(anim_out)
        anim_group.addAnimation(anim_back)
        anim_group.start(QAbstractAnimation.DeleteWhenStopped)
        action()

    def eventFilter(self, obj, event):
        if obj == self.url_bar and event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self.url_bar.clear()
            return True
        return super().eventFilter(obj, event)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.normal_geometry = self.geometry()
            self.toolbar_visible = self.toolbar.isVisible()
            self.statusbar_visible = self.status.isVisible()
            self.toolbar.hide()
            self.status.hide()
            self.showFullScreen()
        else:
            self.showNormal()
            self.setGeometry(self.normal_geometry)
            if self.toolbar_visible:
                self.toolbar.show()
            if self.statusbar_visible:
                self.status.show()
        self.status.showMessage(f"Fullscreen mode {'enabled' if self.is_fullscreen else 'disabled'}", 3000)

    def go_home(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.setUrl(QUrl(self.settings_manager.settings["homepage"]))
            self.status.showMessage("Navigated to homepage", 3000)

    def add_new_tab(self, url=None, private=False):
        default_url = "https://vellumbrowser.neocities.org/private" if private else self.settings_manager.settings["homepage"]
        url = url if isinstance(url, str) and url.strip() and url.startswith(("http://", "https://")) else default_url
        browser = QWebEngineView()
        profile = QWebEngineProfile("Private" if private else "Default", browser)
        if private:
            profile.setHttpCacheType(QWebEngineProfile.NoCache)
            profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        profile.setCachePath(os.path.join(QStandardPaths.writableLocation(QStandardPaths.CacheLocation), "VellumBrowser"))
        profile.setHttpCacheMaximumSize(30 * 1024 * 1024)
        profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
        page = QWebEnginePage(profile, browser)
        browser.setPage(page)
        settings = page.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        browser.setUrl(QUrl(url))
        profile.downloadRequested.connect(self.handle_download)
        channel = QWebChannel()
        page.setWebChannel(channel)
        channel.registerObject("browserBridge", self)
        page.createWindow = self.handle_new_window
        index = self.tabs.addTab(browser, "New Tab (Private)" if private else "New Tab")
        self.tabs.setCurrentIndex(index)
        browser.titleChanged.connect(lambda t, b=browser: self.update_tab_title(b, t))
        browser.urlChanged.connect(lambda u, b=browser: self.update_urlbar(u, b))
        browser.page().javaScriptConsoleMessage = self.handle_console_message
        browser.page().loadStarted.connect(lambda: (self.progress_bar.show(), self.status.showMessage("Loading...")))
        browser.page().loadFinished.connect(lambda ok, b=browser: (self.progress_bar.hide(), self.status.showMessage("Failed to load page", 3000) if not ok and b == self.tabs.currentWidget() else None))
        browser.page().loadProgress.connect(self.progress_bar.setValue)
        if not private:
            browser.urlChanged.connect(lambda url: (self._history_manager.add_history_entry(url.toString(), browser.title()), self.update_bookmark_button(url.toString())))
        browser.page().runJavaScript("""
            window.vellumBrowser = {
                openTab: function(url) { Qt.call('browserBridge', 'openTab', url); },
                toggleBookmark: function() { Qt.call('browserBridge', 'toggleBookmark'); },
                showMessage: function(message) { Qt.call('browserBridge', 'showMessage', message); }
            };
            document.addEventListener('DOMContentLoaded', function() {
                if (window.location.hostname.includes('youtube.com')) {
                    const checkButton = setInterval(() => {
                        const fullscreenBtn = document.querySelector('.ytp-fullscreen-button');
                        if (fullscreenBtn && fullscreenBtn.title === 'null') {
                            fullscreenBtn.title = 'Fullscreen';
                            fullscreenBtn.addEventListener('click', () => {
                                const player = document.querySelector('.html5-main-video');
                                if (player) {
                                    if (!document.fullscreenElement) {
                                        player.requestFullscreen().catch(err => console.error('Fullscreen error:', err));
                                    } else {
                                        document.exitFullscreen();
                                    }
                                }
                            });
                            clearInterval(checkButton);
                        }
                    }, 500);
                }
            });
        """)

    @pyqtSlot(str)
    def openTab(self, url):
        self.add_new_tab(url if isinstance(url, str) and url.strip() else None)

    @pyqtSlot()
    def toggleBookmark(self):
        self.toggle_bookmark()

    @pyqtSlot(str)
    def showMessage(self, message):
        self.status.showMessage(message, 5000)

    def handle_download(self, download):
        download_dir = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        suggested_filename = download.url().fileName() or next((bytes(download.request().rawHeader(b"Content-Disposition")).decode().split("filename=")[1].strip('"\'') for h in download.request().rawHeaderList() if b"Content-Disposition" in h and "filename=" in bytes(download.request().rawHeader(h)).decode()), "download")
        path, _ = QFileDialog.getSaveFileName(self, "Save File", os.path.join(download_dir, suggested_filename), "All Files (*)")
        if path:
            download.setPath(path)
            download.accept()
            self._download_manager.add_download(download)
            download.downloadProgress.connect(lambda bytesReceived, bytesTotal: self.status.showMessage(f"Downloading: {self.format_size(bytesReceived)} / {self.format_size(bytesTotal)}"))
            download.finished.connect(lambda: self.status.showMessage("Download completed", 3000))
        else:
            download.cancel()

    def format_size(self, bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024.0:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.1f} TB"

    def handle_new_window(self, _):
        self.add_new_tab()
        return self.tabs.currentWidget().page()

    def close_tab(self, index):
        if self.tabs.count() > 1 and index not in self.pinned_tabs:
            self.tabs.removeTab(index)
        elif self.tabs.count() == 1:
            self.close()

    def update_urlbar(self, url, browser):
        if browser == self.tabs.currentWidget():
            self.url_bar.setText(url.toString())
            self.update_bookmark_button(url.toString())

    def update_tab_title(self, browser, title):
        index = self.tabs.indexOf(browser)
        if index != -1:
            short_title = title[:15] + "..." if len(title) > 15 else title
            self.tabs.setTabText(index, short_title)
            if index == self.tabs.currentIndex():
                self.setWindowTitle(f"{title} - Vellum Browser")
            if index in self.pinned_tabs:
                self.tabs.setTabIcon(index, QIcon.fromTheme("pin"))

    def back(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.back()

    def forward(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.forward()

    def reload(self):
        browser = self.tabs.currentWidget()
        if browser:
            self.reload_timer.start(100)
            browser.reload()

    def update_reload_animation(self):
        icons = ['⟳', '↻', '↺', '⟲']
        browser = self.tabs.currentWidget()
        if browser and self.reload_timer.isActive():
            self.reload_btn.setText(icons[(self.reload_timer.interval() // 100) % len(icons)])
        else:
            self.reload_timer.stop()
            self.reload_btn.setText('⟳')

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url:
            return
        if url.startswith(("http://", "https://")):
            final_url = url
        elif '.' in url and ' ' not in url:
            final_url = f"https://{url}"
        else:
            search_engine = self.settings_manager.settings["search_engine"]
            final_url = {
                "Bing": f"https://www.bing.com/search?q={urllib.parse.quote(url)}",
                "DuckDuckGo": f"https://duckduckgo.com/?q={urllib.parse.quote(url)}",
                "Google": f"https://www.google.com/search?q={urllib.parse.quote(url)}"
            }.get(search_engine, f"https://www.google.com/search?q={urllib.parse.quote(url)}")
        browser = self.tabs.currentWidget()
        if browser:
            browser.setUrl(QUrl(final_url))

    def update_url_from_tab(self, index):
        browser = self.tabs.widget(index)
        if browser:
            self.url_bar.setText(browser.url().toString())
            self.update_bookmark_button(browser.url().toString())

    def handle_console_message(self, level, message, line, source):
        if hasattr(self, 'debug_console') and self.debug_console.isVisible():
            level_str = ["INFO", "WARN", "ERROR"][level] if 0 <= level <= 2 else "UNKNOWN"
            self.console_output.append(f'<span style="color:{["blue", "orange", "red"][level] if 0 <= level <= 2 else "gray"}">[{level_str}] {message} (line {line}, {source})</span>')

    def show_bookmarks(self):
        self.bookmark_dialog.populate_bookmarks(self._bookmark_manager.bookmarks)
        self.bookmark_dialog.show()

    def toggle_bookmark(self):
        browser = self.tabs.currentWidget()
        if browser:
            url, title = browser.url().toString(), browser.title()
            if self._bookmark_manager.is_bookmarked(url):
                self._bookmark_manager.remove_bookmark(url)
                self.bookmark_btn.setChecked(False)
            else:
                self._bookmark_manager.add_bookmark(url, title)
                self.bookmark_btn.setChecked(True)

    def update_bookmark_button(self, url):
        self.bookmark_btn.setChecked(self._bookmark_manager.is_bookmarked(url))

    def navigate_to_url_external(self, url):
        self.url_bar.setText(url)
        self.navigate_to_url()

    def show_tab_context_menu(self, point):
        menu = QMenu(self)
        browser = self.tabs.currentWidget()
        url = browser.url().toString() if browser else ""
        index = self.tabs.currentIndex()
        actions = [
            ("New Tab", self.add_new_tab),
            ("New Private Tab", lambda: self.add_new_tab(private=True)),
            ("Pin Tab" if index not in self.pinned_tabs else "Unpin Tab", lambda: self.toggle_pin_tab(index)),
            ("Inspect Source", self.inspect_source),
            ("Save Page", self.save_page),
            ("Open Console (F12)", self.toggle_debug_console)
        ]
        if url.startswith(("http://", "https://")):
            actions.append(("Remove Bookmark" if self._bookmark_manager.is_bookmarked(url) else "Add Bookmark",
                            lambda: (self._bookmark_manager.remove_bookmark(url) if self._bookmark_manager.is_bookmarked(url) else self._bookmark_manager.add_bookmark(url, browser.title()), self.update_bookmark_button(url))))
        for text, handler in actions:
            menu.addAction(text, handler)
        menu.exec_(self.tabs.mapToGlobal(point))

    def toggle_pin_tab(self, index):
        if index in self.pinned_tabs:
            self.pinned_tabs.remove(index)
            self.tabs.setTabIcon(index, QIcon())
        else:
            self.pinned_tabs.append(index)
            self.tabs.setTabIcon(index, QIcon.fromTheme("pin"))
        self.tabs.tabBar().moveTab(index, 0 if index in self.pinned_tabs else self.tabs.count() - 1)

    def inspect_source(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.page().toHtml(self.display_source)

    def display_source(self, html):
        dialog = QDialog(self)
        dialog.setWindowTitle("Page Source")
        dialog.resize(800, 600)
        text_edit = QTextEdit()
        text_edit.setPlainText(html)
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Consolas", 10))
        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(text_edit)
        dialog.exec_()

    def save_page(self):
        browser = self.tabs.currentWidget()
        if browser:
            file_dialog = QFileDialog(self)
            file_dialog.setDefaultSuffix(".html")
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.setNameFilter("HTML Files (*.html)")
            if file_dialog.exec_():
                browser.page().toHtml(lambda h: self.save_html(h, file_dialog.selectedFiles()[0]))

    def save_html(self, html, path):
        try:
            with open(path, 'w', encoding="utf-8") as f:
                f.write(html)
            QMessageBox.information(self, "Success", "Page saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save page: {str(e)}")

    def toggle_debug_console(self):
        if not hasattr(self, 'debug_console'):
            self.debug_console = QDockWidget("Debug Console", self)
            self.debug_console.setAllowedAreas(Qt.BottomDockWidgetArea)
            self.debug_console.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
            widget = QWidget()
            layout = QVBoxLayout()
            self.console_output = QTextEdit()
            self.console_output.setReadOnly(True)
            self.console_output.setFont(QFont("Consolas", 10))
            console_input = QTextEdit()
            console_input.setPlaceholderText("Enter JavaScript to execute...")
            console_input.setFont(QFont("Consolas", 10))
            console_input.setFixedHeight(100)
            button_layout = QHBoxLayout()
            run_btn = QPushButton("Run Script")
            run_btn.clicked.connect(lambda: self.execute_console_command(console_input))
            clear_btn = QPushButton("Clear Console")
            clear_btn.clicked.connect(self.console_output.clear)
            button_layout.addWidget(run_btn)
            button_layout.addWidget(clear_btn)
            button_layout.addStretch()
            layout.addWidget(self.console_output)
            layout.addWidget(console_input)
            layout.addLayout(button_layout)
            widget.setLayout(layout)
            self.debug_console.setWidget(widget)
            self.addDockWidget(Qt.BottomDockWidgetArea, self.debug_console)
        self.debug_console.setVisible(not self.debug_console.isVisible())

    def execute_console_command(self, input_widget):
        cmd = input_widget.toPlainText().strip()
        if cmd:
            browser = self.tabs.currentWidget()
            if browser:
                self.console_output.append(f'<span style="color:gray">> {cmd}</span>')
                browser.page().runJavaScript(cmd, lambda r: self.console_output.append(f'<span style="color:green">Result: {str(r)}</span>'))
                input_widget.clear()

    def show_toolbar_context_menu(self, point):
        menu = QMenu(self)
        actions = [
            ("New Tab", self.add_new_tab),
            ("New Private Tab", lambda: self.add_new_tab(private=True)),
            ("Bookmarks", self.show_bookmarks),
            ("History", self._history_manager.show),
            ("Downloads", self._download_manager.show),
            ("Settings", self._settings_dialog.show),
            ("Help", self._help_dialog.show),
            ("Toggle Fullscreen (F11)", self.toggle_fullscreen)
        ]
        for text, slot in actions:
            menu.addAction(text, slot)
        menu.exec_(self.toolbar.mapToGlobal(point))

    @property
    def settings_manager(self): return self._settings_manager
    @property
    def bookmark_manager(self): return self._bookmark_manager
    @property
    def bookmark_dialog(self):
        if not hasattr(self, '_bookmark_dialog'):
            self._bookmark_dialog = BookmarkDialog(self)
        return self._bookmark_dialog

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = Browser()
    window.show()
    sys.exit(app.exec_())