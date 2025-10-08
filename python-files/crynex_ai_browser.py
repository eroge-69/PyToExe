import sys, os
from PyQt5.QtCore import Qt, QUrl, QPoint
from PyQt5.QtGui import QIcon, QCloseEvent, QColor, QPalette
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QToolBar, QAction,
    QLineEdit, QTabWidget, QMenu, QPushButton, QSystemTrayIcon, QStyle
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile


# ----------------- Main Browser -----------------
class CrynexBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crynex Browser by ExploitZ3r0")
        self.resize(1200, 800)

        # Dark glass-like theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgba(15, 20, 30, 180);
                color: white;
            }
            QToolBar {
                background: rgba(30, 40, 60, 160);
                border: none;
                padding: 4px;
            }
            QLineEdit {
                background: rgba(255,255,255,0.08);
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 6px;
                padding: 4px 8px;
                selection-background-color: #00aaff;
            }
            QPushButton {
                background: rgba(255,255,255,0.05);
                color: white;
                border-radius: 6px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.2);
            }
            QTabBar::tab {
                background: rgba(40,50,70,180);
                color: white;
                padding: 6px 10px;
                border-radius: 8px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background: rgba(80,130,200,180);
            }
        """)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Toolbar
        navbar = QToolBar()
        self.addToolBar(navbar)

        # Simple icons
        back = QAction("←", self)
        back.triggered.connect(lambda: self.current_browser().back())
        fwd = QAction("→", self)
        fwd.triggered.connect(lambda: self.current_browser().forward())
        reload = QAction("⟳", self)
        reload.triggered.connect(lambda: self.current_browser().reload())
        home = QAction("🏠", self)
        home.triggered.connect(self.navigate_home)
        newtab = QAction("＋", self)
        newtab.triggered.connect(lambda: self.add_tab("https://www.qwant.com/"))

        navbar.addAction(back)
        navbar.addAction(fwd)
        navbar.addAction(reload)
        navbar.addAction(home)
        navbar.addAction(newtab)

        # Search bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address")
        self.url_bar.returnPressed.connect(self.navigate_url)
        navbar.addWidget(self.url_bar)

        # Menu (⋮)
        menu_btn = QPushButton("⋮")
        menu = QMenu()
        menu.addAction("New Tab", lambda: self.add_tab("https://www.qwant.com/"))
        menu.addAction("Google CSE", self.open_cse)
        menu.addAction("AI Chat 💬", self.toggle_ai)
        menu.addSeparator()
        menu.addAction("Exit", self.close)
        menu_btn.setMenu(menu)
        navbar.addWidget(menu_btn)

        # Add first tab
        self.add_tab("https://www.qwant.com/")

        # Floating AI button
        self.floating_ai = FloatingButton(always_on_top=True)
        self.floating_ai.show()

        # System tray
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_icon.setToolTip("Crynex Browser by ExploitZ3r0")

        tray_menu = QMenu()
        tray_menu.addAction("Show / Restore Browser", self.show_browser)
        tray_menu.addAction("Hide Browser", self.hide_browser)
        tray_menu.addAction("Toggle AI Chat 💬", self.toggle_ai)
        tray_menu.addSeparator()
        tray_menu.addAction("Exit", self.quit_browser)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    # -------- Tabs --------
    def add_tab(self, url, label="New Tab"):
        browser = QWebEngineView()
        profile = browser.page().profile()
        profile.downloadRequested.connect(self.handle_download)
        browser.setUrl(QUrl(url))
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.titleChanged.connect(lambda t, b=browser: self.tabs.setTabText(self.tabs.indexOf(b), t))
        browser.urlChanged.connect(lambda u, b=browser: self.update_url(u, b))

    def close_tab(self, i):
        if self.tabs.count() > 1:
            w = self.tabs.widget(i)
            w.deleteLater()
            self.tabs.removeTab(i)

    def current_browser(self):
        return self.tabs.currentWidget()

    # -------- Navigation --------
    def navigate_home(self):
        self.current_browser().setUrl(QUrl("https://www.qwant.com/"))

    def navigate_url(self):
        url = self.url_bar.text().strip()
        if not url.startswith("http"):
            url = f"https://cse.google.com/cse?cx=b4a460a18ca284f6f&q={url}"
        self.current_browser().setUrl(QUrl(url))

    def update_url(self, q, b):
        if b == self.current_browser():
            self.url_bar.setText(q.toString())

    # -------- Menu Actions --------
    def open_cse(self):
        self.add_tab("https://cse.google.com/cse?cx=b4a460a18ca284f6f", "Google Search")

    def handle_download(self, download):
        path = os.path.expanduser("~/Downloads")
        os.makedirs(path, exist_ok=True)
        download.setPath(os.path.join(path, os.path.basename(download.path())))
        download.accept()

    # -------- Tray / AI --------
    def toggle_ai(self):
        if self.floating_ai.isVisible():
            self.floating_ai.hide()
        else:
            self.floating_ai.show()

    def show_browser(self):
        self.showNormal()
        self.activateWindow()

    def hide_browser(self):
        self.hide()

    def quit_browser(self):
        self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event: QCloseEvent):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Crynex Browser",
            "Still running in system tray 💻",
            QSystemTrayIcon.Information,
            3000
        )


# ----------------- AI Chat -----------------
class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CrywereGPT")
        self.resize(480, 600)
        self.setStyleSheet("background-color: #0a0f1f; color: white;")
        self.browser = QWebEngineView()
        self.browser.load(QUrl("https://crywereaigpt.base44.app"))
        self.setCentralWidget(self.browser)


class FloatingButton(QWidget):
    def __init__(self, always_on_top=False):
        super().__init__()
        flags = Qt.FramelessWindowHint | Qt.Tool
        if always_on_top:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.btn = QPushButton("💬")
        self.btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #007bff, stop:1 #00aaff);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 20px;
                padding: 10px;
                min-width: 50px;
                min-height: 50px;
                box-shadow: 0px 0px 10px rgba(0,0,0,0.5);
            }
            QPushButton:hover {
                background-color: #0099ff;
            }
        """)
        self.btn.clicked.connect(self.toggle_chat)
        layout.addWidget(self.btn)
        self.setLayout(layout)

        self.chat_window = None
        self.dragging = False
        self.offset = QPoint(0, 0)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = e.pos()

    def mouseMoveEvent(self, e):
        if self.dragging:
            self.move(self.pos() + (e.pos() - self.offset))

    def mouseReleaseEvent(self, e):
        self.dragging = False

    def toggle_chat(self):
        if self.chat_window and self.chat_window.isVisible():
            self.chat_window.close()
            self.chat_window = None
        else:
            self.chat_window = ChatWindow()
            self.chat_window.show()


# ----------------- Main -----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Crynex Browser + AI")

    # Optional: global dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(15, 20, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)

    win = CrynexBrowser()
    win.show()
    sys.exit(app.exec_())
