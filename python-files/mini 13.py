import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QAction,
    QTabWidget, QWidget, QVBoxLayout, QListWidget, QDockWidget,
    QPushButton, QLabel, QFileDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtCore import Qt, QUrl

# Simple ad/tracker blocking
BLOCKED_DOMAINS = [
    "ads.", "doubleclick.net", "googlesyndication.com",
    "tracker.", "analytics.", "facebook.com/tr"
]

class BlockerPage(QWebEnginePage):
    def __init__(self, *args, blocked_domains=None, blocked_count_callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.blocked_domains = blocked_domains or []
        self.blocked_count_callback = blocked_count_callback

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        host = url.host()
        for domain in self.blocked_domains:
            if domain in host:
                if self.blocked_count_callback:
                    self.blocked_count_callback()
                return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)

class HeavyBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HeavyBrowser")
        self.resize(1400, 900)

        # Keep track of blocked ads
        self.ads_blocked = 0
        self.is_fullscreen = False

        # Main tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Toolbar
        self.create_toolbar()

        # Side panel for bookmarks
        self.create_side_panel()

        # Downloads list
        self.downloads = []

        # First tab = homepage
        self.add_new_tab("home")

    def create_toolbar(self):
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        # Back
        self.back_btn = QAction("←", self)
        self.back_btn.triggered.connect(lambda: self.current_webview().back())
        self.toolbar.addAction(self.back_btn)

        # Forward
        self.forward_btn = QAction("→", self)
        self.forward_btn.triggered.connect(lambda: self.current_webview().forward())
        self.toolbar.addAction(self.forward_btn)

        # Reload
        self.reload_btn = QAction("⟳", self)
        self.reload_btn.triggered.connect(lambda: self.current_webview().reload())
        self.toolbar.addAction(self.reload_btn)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Google or enter URL")
        self.search_bar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.search_bar)

        # Bookmarks toggle
        self.bookmarks_btn = QAction("★", self)
        self.bookmarks_btn.triggered.connect(self.toggle_bookmarks)
        self.toolbar.addAction(self.bookmarks_btn)

        # Downloads
        self.download_btn = QAction("⬇", self)
        self.download_btn.triggered.connect(self.show_downloads)
        self.toolbar.addAction(self.download_btn)

        # New tab
        self.new_tab_btn = QAction("+", self)
        self.new_tab_btn.triggered.connect(lambda: self.add_new_tab("https://www.google.com"))
        self.toolbar.addAction(self.new_tab_btn)

        # Fullscreen toggle
        self.fullscreen_btn = QAction("⛶", self)
        self.fullscreen_btn.triggered.connect(self.toggle_fullscreen)
        self.toolbar.addAction(self.fullscreen_btn)

    def create_side_panel(self):
        self.bookmarks_dock = QDockWidget("Bookmarks", self)
        self.bookmarks_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.bookmarks_panel = QListWidget()
        self.bookmarks_panel.addItems(["https://www.google.com", "https://www.wikipedia.org"])
        self.bookmarks_panel.itemClicked.connect(lambda item: self.add_new_tab(item.text()))
        self.bookmarks_dock.setWidget(self.bookmarks_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.bookmarks_dock)
        self.bookmarks_dock.hide()

    def toggle_bookmarks(self):
        if self.bookmarks_dock.isVisible():
            self.bookmarks_dock.hide()
        else:
            self.bookmarks_dock.show()

    def add_new_tab(self, url):
        webview = QWebEngineView()
        page = BlockerPage(blocked_domains=BLOCKED_DOMAINS, blocked_count_callback=self.increment_block_count)
        webview.setPage(page)

        # Fullscreen support
        page.fullScreenRequested.connect(self.handle_fullscreen_request)

        if url == "home":
            webview.setHtml(f"<h1 style='color:white;background-color:#222;padding:20px;'>Welcome to HeavyBrowser</h1>"
                            f"<p style='color:white;'>Ads & Trackers blocked: {self.ads_blocked}</p>")
        else:
            webview.setUrl(QUrl(url))

        idx = self.tabs.addTab(webview, "New Tab")
        self.tabs.setCurrentIndex(idx)

    def current_webview(self):
        return self.tabs.currentWidget()

    def close_tab(self, index):
        self.tabs.removeTab(index)

    def navigate_to_url(self):
        url_text = self.search_bar.text()
        if "." in url_text:
            url = QUrl(url_text if url_text.startswith("http") else "http://" + url_text)
        else:
            url = QUrl(f"https://www.google.com/search?q={url_text}")
        self.current_webview().setUrl(url)

    def increment_block_count(self):
        self.ads_blocked += 1
        # Update homepage if open
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if hasattr(w, 'url') and w.url().toString() == "about:blank":
                w.setHtml(f"<h1 style='color:white;background-color:#222;padding:20px;'>Welcome to HeavyBrowser</h1>"
                          f"<p style='color:white;'>Ads & Trackers blocked: {self.ads_blocked}</p>")

    def show_downloads(self):
        dlg = QWidget()
        dlg.setWindowTitle("Downloads")
        layout = QVBoxLayout()
        for d in self.downloads:
            layout.addWidget(QLabel(d))
        dlg.setLayout(layout)
        dlg.resize(400, 300)
        dlg.show()

    def handle_fullscreen_request(self, request):
        if request.toggleOn():
            self.showFullScreen()
            self.is_fullscreen = True
        else:
            self.showNormal()
            self.is_fullscreen = False
        request.accept()

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = HeavyBrowser()
    browser.show()
    sys.exit(app.exec_())
