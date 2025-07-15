import sys
import pyperclip
from PyQt5.QtCore import QUrl, Qt, QPoint, pyqtSignal, QEvent
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLabel,
                             QHBoxLayout, QPushButton, QStackedWidget,
                             QLineEdit, QFrame, QStyle)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtGui import QColor
from pynput import keyboard
from threading import Thread
import urllib.parse

# --- Windows-specific DPI and style handling ---
if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

    def enable_snap_assist(hwnd):
        """Adds native window styles to allow snapping and resizing."""
        GWL_STYLE = -16
        WS_OVERLAPPEDWINDOW = 0x00CF0000
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, WS_OVERLAPPEDWINDOW)

        SWP_NOSIZE = 0x0001
        SWP_NOMOVE = 0x0002
        SWP_NOZORDER = 0x0004
        SWP_FRAMECHANGED = 0x0020
        ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0,
            SWP_NOSIZE | SWP_NOMOVE | SWP_NOZORDER | SWP_FRAMECHANGED)


class HotkeyManager(Thread):
    def __init__(self, window):
        super().__init__(daemon=True)
        self.window = window

    def run(self):
        hotkeys = {
            '<ctrl>+<alt>+d': lambda: self.window.lookup_signal.emit(),
            '<ctrl>+<tab>': lambda: self.window.cycle_signal.emit()
        }
        with keyboard.GlobalHotKeys(hotkeys) as listener:
            listener.join()


class DictionaryLookup(QMainWindow):
    lookup_signal = pyqtSignal()
    cycle_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.previous_word = ""
        self.border_width = 8

        self.sites = {
            "dict.cc": "https://m.dict.cc/deen/?s={}",
            "DWDS": "https://www.dwds.de/wb/{}",
            "Verbformen": "https://www.verbformen.com/?w={}",
            "Google Bilder": "https://www.google.com/search?tbm=isch&q={}&hl=de&gl=DE"
        }
        self.site_buttons = []
        self.web_views = []

        self._setup_window()
        self._create_widgets()

        self.lookup_signal.connect(self.lookup_from_clipboard)
        self.cycle_signal.connect(self.cycle_sites)

        hotkey_thread = HotkeyManager(self)
        hotkey_thread.start()

        if sys.platform == "win32":
            hwnd = int(self.winId())
            enable_snap_assist(hwnd)

    def _setup_window(self):
        self.setWindowTitle('Deutsche Wortbücher')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 600, 800)
        self.setMinimumSize(500, 650)

        app_icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.setWindowIcon(app_icon)

        dark_palette = self.palette()
        dark_palette.setColor(dark_palette.Window, QColor(36, 36, 36))
        dark_palette.setColor(dark_palette.WindowText, Qt.white)
        self.setPalette(dark_palette)

    def _create_widgets(self):
        main_container = QFrame()
        main_container.setObjectName("mainContainer")
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)

        title_bar = self._create_title_bar()
        main_layout.addWidget(title_bar)

        content_area = QFrame()
        content_area.setObjectName("contentArea")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        main_layout.addWidget(content_area)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Wort zum Nachschlagen eingeben...")
        self.search_input.returnPressed.connect(self.lookup_from_input)
        search_layout.addWidget(self.search_input)

        search_btn = QPushButton("🔍")
        search_btn.setFixedSize(40, 40)
        search_btn.clicked.connect(self.lookup_from_input)
        search_layout.addWidget(search_btn)
        content_layout.addLayout(search_layout)

        sites_bar = QHBoxLayout()
        for name in self.sites.keys():
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.clicked.connect(self.switch_site)
            sites_bar.addWidget(btn)
            self.site_buttons.append(btn)
        content_layout.addLayout(sites_bar)

        self.web_stack = QStackedWidget()
        for _ in self.sites:
            view = QWebEngineView()
            view.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            view.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
            self.web_stack.addWidget(view)
            self.web_views.append(view)
        content_layout.addWidget(self.web_stack)

        status_bar = QHBoxLayout()
        self.word_label = QLabel("Bereit - Drücken Sie Strg+Alt+D")
        status_bar.addWidget(self.word_label)
        status_bar.addStretch()
        lookup_btn = QPushButton("Zwischenablage nachschlagen")
        lookup_btn.clicked.connect(self.lookup_from_clipboard)
        status_bar.addWidget(lookup_btn)
        content_layout.addLayout(status_bar)

        self.setCentralWidget(main_container)
        self.site_buttons[0].setChecked(True)
        self.setStyleSheet(self._get_stylesheet())

    def _create_title_bar(self):
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(40)
        self.title_bar.setObjectName("titleBar")
        title_bar_layout = QHBoxLayout(self.title_bar)
        title_bar_layout.setContentsMargins(10, 0, 5, 0)

        logo_label = QLabel()
        logo_label.setPixmap(self.style().standardIcon(QStyle.SP_ComputerIcon).pixmap(24, 24))
        title_bar_layout.addWidget(logo_label)

        title_label = QLabel("Deutsche Wortbücher")
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()

        return self.title_bar

    def _get_stylesheet(self):
        return """
            QFrame#mainContainer {
                background-color: #242424;
                border-radius: 10px;
                border: 1px solid #444;
            }
            QFrame#contentArea {
                background-color: #242424;
            }
            QFrame#titleBar {
                background-color: #1F1F1F;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom: 1px solid #444;
            }
            QLabel { color: #E0E0E0; font-size: 14px; }
            QLineEdit { 
                padding: 8px 12px; background-color: #2B2B2B; border: 1px solid #444; 
                border-radius: 5px; color: #E0E0E0; font-size: 14px;
            }
            QPushButton {
                padding: 8px 16px; background-color: #404040; border: none;
                border-radius: 5px; color: white; font-size: 14px;
            }
            QPushButton:hover { background-color: #555; }
            QPushButton:pressed { background-color: #666; }
            QPushButton:checked { background-color: #1F6AA5; }
        """

    def lookup_word(self, word):
        word = word.strip()
        if not word or word == self.previous_word:
            self.activateWindow()
            self.raise_()
            return
        self.previous_word = word
        self.word_label.setText(f"Nachschlagen: {word}")
        self.search_input.setText(word)

        encoded_word = urllib.parse.quote_plus(word)
        for i, site_name in enumerate(self.sites.keys()):
            url_template = self.sites[site_name]
            url = url_template.format(encoded_word)
            self.web_views[i].load(QUrl(url))

        self.activateWindow()
        self.raise_()

    def lookup_from_clipboard(self):
        try:
            word = pyperclip.paste()
            self.lookup_word(word)
        except Exception as e:
            print(f"Clipboard error: {e}")

    def lookup_from_input(self):
        self.lookup_word(self.search_input.text())

    def switch_site(self):
        sender = self.sender()
        index = self.site_buttons.index(sender)
        self.web_stack.setCurrentIndex(index)
        for btn in self.site_buttons:
            btn.setChecked(btn is sender)

    def cycle_sites(self):
        current_index = self.web_stack.currentIndex()
        next_index = (current_index + 1) % len(self.sites)
        self.site_buttons[next_index].setChecked(True)
        self.site_buttons[next_index].clicked.emit()


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    window = DictionaryLookup()
    window.show()
    sys.exit(app.exec_())
