import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *

# Set high DPI attributes
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q={}",
    "Bing": "https://www.bing.com/search?q={}",
    "Yahoo": "https://search.yahoo.com/search?p={}",
    "DuckDuckGo": "https://duckduckgo.com/?q={}",
    "Yandex": "https://yandex.com/search/?text={}"
}

class WebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def acceptNavigationRequest(self, url, type, isMainFrame):
        # Force all links to open in same tab
        return True

class ZRoBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Z-Ro Browser")
        self.setGeometry(15, 15, 800, 450)
        
        # Setup retro dark theme
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #ffffff;
                color: #000000;
                font-family: 'Courier New', monospace;
            }
            QTabWidget::pane {
                border: 0;
            }
            QTabBar::tab {
                background: #ffffff;
                color: #000000;
                padding: 8px;
                border: 1px solid #000000;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-color: #000000;
            }
            QLineEdit {
                background: #ffffff;
                color: #000000;
                border: 1px solid #000000;
                padding: 5px;
                font-family: 'Courier New', monospace;
                height: 24px;
            }
            QPushButton {
                background: #ffffff;
                color: #000000;
                border: 1px solid #000000;
                padding: 5px 10px;
                min-width: 30px;
                height: 24px;
            }
            QPushButton:hover {
                background: #005500;
            }
            QComboBox {
                background: #ffffff;
                color: #000000;
                border: 1px solid #000000;
                padding: 2px;
                height: 24px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                width: 20px;
                border-left: 1px solid #000000;
            }
            QStatusBar {
                background: #ffffff;
                color: #000000;
                border-top: 1px solid #000000;
                font-size: 11px;
            }
        """)
        
        # Central widget and layout
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        
        # Add new tab button
        new_tab_btn = QPushButton("+")
        new_tab_btn.setFixedWidth(30)
        new_tab_btn.clicked.connect(self.add_new_tab)
        self.tabs.setCornerWidget(new_tab_btn, Qt.TopRightCorner)
        
        # Create initial tab
        self.add_new_tab()
        
        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        # Configure web engine settings
        settings = QWebEngineSettings.globalSettings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        
        # Keyboard shortcuts
        QShortcut(QKeySequence("Alt+S"), self, self.focus_search)
        QShortcut(QKeySequence("Alt+N"), self, self.add_new_tab)
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)
        
        self.show()
    
    def add_new_tab(self, url=None):
        # Create browser widget
        browser = QWebEngineView()
        browser.setPage(WebEnginePage(browser))
        browser.setUrl(QUrl(url if url else "about:blank"))
        
        # Create tab content widget
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Navigation bar
        nav_bar = QWidget()
        nav_bar.setFixedHeight(36)
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(5, 5, 5, 5)
        nav_layout.setSpacing(5)
        
        # Navigation buttons
        back_btn = QPushButton("←")
        back_btn.setFixedWidth(30)
        back_btn.clicked.connect(lambda: browser.back())
        
        forward_btn = QPushButton("→")
        forward_btn.setFixedWidth(30)
        forward_btn.clicked.connect(lambda: browser.forward())
        
        refresh_btn = QPushButton("↻")
        refresh_btn.setFixedWidth(30)
        refresh_btn.clicked.connect(lambda: browser.reload())
        
        # URL bar
        url_bar = QLineEdit()
        url_bar.returnPressed.connect(lambda: self.navigate_to_url(browser, url_bar))
        
        # Search toggle
        search_toggle = QComboBox()
        search_toggle.addItems(SEARCH_ENGINES.keys())
        search_toggle.setCurrentIndex(0)
        search_toggle.setFixedWidth(120)
        
        nav_layout.addWidget(back_btn)
        nav_layout.addWidget(forward_btn)
        nav_layout.addWidget(refresh_btn)
        nav_layout.addWidget(url_bar)
        nav_layout.addWidget(search_toggle)
        
        # Add widgets to layout
        layout.addWidget(nav_bar)
        layout.addWidget(browser)
        
        # Add tab
        index = self.tabs.addTab(tab_widget, "New Tab")
        self.tabs.setCurrentIndex(index)
        
        # Connect signals
        browser.urlChanged.connect(lambda q: self.update_urlbar(q, url_bar, browser))
        browser.loadStarted.connect(self.page_loading)
        browser.loadFinished.connect(self.page_loaded)
        browser.page().fullScreenRequested.connect(self.handle_fullscreen_request)
        
        # Set start page if no URL provided
        if not url:
            self.show_start_page(browser)
    
    def handle_fullscreen_request(self, request):
        request.accept()
        if request.toggleOn():
            self.showFullScreen()
        else:
            self.showNormal()
    
    def show_start_page(self, browser):
        html = f"""
        <!DOCTYPE html>
        <html style="background:#fff;height:100%;color:#000;font-family:'Courier New',monospace">
        <body style="display:flex;justify-content:center;align-items:center;height:100%;margin:0;">
            <div style="text-align:center;">
                <h1 style="font-size:2.5em;color:#000;">Z-RO BROWSER</h1>
                <form action="#" onsubmit="navigate(this);return false;">
                    <input type="text" id="search" style="background:#fff;color:#000;border:2px solid #000;
                    padding:10px;width:400px;font-family:'Courier New',monospace;font-size:16px;"
                    placeholder="Enter search or URL">
                    <button type="submit" style="background:#ffffff;color:#000;border:2px solid #000;
                    padding:10px;font-family:'Courier New',monospace;cursor:pointer;">GO</button>
                </form>
                <p style="margin-top:30px;color:#080;">Simple | Barebone | Just Browse it</p>
                <h7 style="margin-top:25px;color:#080;">Made by Neowdymium</h7>
            </div>
            <script>
                function navigate(form) {{
                    const input = form.querySelector('#search').value;
                    if (!input) return;
                    
                    if (input.includes('.') || input.includes('://')) {{
                        window.location.href = input.includes('://') ? input : 'http://' + input;
                    }} else {{
                        window.location.href = `{SEARCH_ENGINES["Google"]}`.replace('{{}}', encodeURIComponent(input));
                    }}
                }}
            </script>
        </body>
        </html>
        """
        browser.setHtml(html, QUrl("about:start"))
    
    def navigate_to_url(self, browser, url_bar):
        text = url_bar.text()
        
        if "." in text and " " not in text:
            if not text.startswith(("http://", "https://")):
                text = "http://" + text
            browser.setUrl(QUrl(text))
        else:
            engine = url_bar.parent().layout().itemAt(4).widget().currentText()
            search_url = SEARCH_ENGINES[engine].format(text)
            browser.setUrl(QUrl(search_url))
    
    def update_urlbar(self, q, url_bar, browser):
        url_bar.setText(q.toString())
        url_bar.setCursorPosition(0)
        
        # Update tab title
        title = browser.page().title()
        index = self.tabs.currentIndex()
        self.tabs.setTabText(index, title[:20] + "..." if len(title) > 20 else title)
    
    def page_loading(self):
        self.status.showMessage("Loading...")
    
    def page_loaded(self):
        self.status.showMessage("Ready")
    
    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
    
    def focus_search(self):
        current_url_bar = self.tabs.currentWidget().layout().itemAt(0).widget().layout().itemAt(3).widget()
        current_url_bar.setFocus()
        current_url_bar.selectAll()
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def contextMenuEvent(self, event):
        # Simplified context menu with only basic actions
        current_browser = self.tabs.currentWidget().layout().itemAt(1).widget()
        
        menu = QMenu(self)
        menu.addAction("Back", lambda: current_browser.back())
        menu.addAction("Forward", lambda: current_browser.forward())
        menu.addAction("Reload", lambda: current_browser.reload())
        menu.exec_(event.globalPos())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    browser = ZRoBrowser()
    sys.exit(app.exec_())
