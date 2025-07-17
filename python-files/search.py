import sys
import requests
import time
from PyQt5.QtCore import QUrl, Qt, QByteArray, QTimer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, 
                            QWidget, QLineEdit, QToolBar, QAction, QStatusBar, 
                            QMessageBox, QMenu, QInputDialog)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineSettings, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineHttpRequest, QWebEngineUrlScheme
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkProxy

# For Tor integration
TOR_AVAILABLE = False
try:
    import stem
    from stem.control import Controller
    from stem import Signal
    TOR_AVAILABLE = True
except ImportError:
    pass

class AdBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()
        self.blocked_domains = [
            'doubleclick.net',
            'googleadservices.com',
            'googlesyndication.com',
            'adservice.google.com',
            'ads.youtube.com',
            'ad.*.com',
            'track.*.com',
            'analytics.*.com'
        ]
    
    def interceptRequest(self, info: QWebEngineHttpRequest):
        url = info.requestUrl().toString()
        if any(domain in url for domain in self.blocked_domains):
            info.block(True)

class WebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.parent_tab = parent
        
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if "Content Security Policy" in message:
            return
        if "preload" in message and "not used" in message:
            return
        if "was preloaded but not used" in message:
            return
            
        if self.parent_tab and hasattr(self.parent_tab, 'parent_browser'):
            self.parent_tab.parent_browser.status.showMessage(f"JS: {message[:100]}", 3000)

class BrowserTab(QWebEngineView):
    def __init__(self, private=False, parent=None):
        super().__init__(parent)
        self.parent_browser = parent
        self.private = private
        self.cookies_cleaned = False
        
        if private:
            self.profile = QWebEngineProfile("PrivateProfile_" + str(id(self)))
            self.profile.setHttpCacheType(QWebEngineProfile.NoCache)
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
            
            self.page = WebEnginePage(self.profile, self)
            self.setPage(self.page)
        else:
            self.profile = QWebEngineProfile.defaultProfile()
            self.profile.setUrlRequestInterceptor(AdBlocker())
            self.page = WebEnginePage(self.profile, self)
            self.setPage(self.page)
        
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, not private)
        settings.setAttribute(QWebEngineSettings.ScreenCaptureEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, True)
        settings.setAttribute(QWebEngineSettings.ErrorPageEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, False)
        
        settings.setAttribute(QWebEngineSettings.AutoLoadIconsForPage, False)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, False)
        
        self.urlChanged.connect(self.update_url)
        self.titleChanged.connect(self.update_title)
        self.loadStarted.connect(self.on_load_start)
        self.loadFinished.connect(self.on_load_finish)
    
    def update_url(self, url):
        if self.parent_browser:
            self.parent_browser.address_bar.setText(url.toString())
    
    def update_title(self, title):
        if self.parent_browser:
            self.parent_browser.setWindowTitle(f"{title} - Anonymous Browser")
            if self.parent_browser.tabs.currentWidget() == self:
                self.parent_browser.address_bar.setPlaceholderText(f"Search or enter address - {title}")
    
    def on_load_start(self):
        if self.parent_browser:
            self.parent_browser.status.showMessage("Loading...")
    
    def on_load_finish(self, ok):
        if self.parent_browser:
            status = "Loaded successfully" if ok else "Load failed"
            self.parent_browser.status.showMessage(status, 2000)
    
    def clean_cookies(self):
        """Clean all cookies for this tab"""
        if not self.private and not self.cookies_cleaned:
            cookie_store = self.profile.cookieStore()
            cookie_store.deleteAllCookies()
            self.cookies_cleaned = True

class AnonymousBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Anonymous Browser")
        self.resize(1200, 800)
        
        # Search engines
        self.search_engines = {
            "DuckDuckGo": "https://duckduckgo.com/?q={}",
            "Google": "https://www.google.com/search?q={}",
            "Bing": "https://www.bing.com/search?q={}",
            "Yahoo": "https://search.yahoo.com/search?p={}",
            "Startpage": "https://www.startpage.com/do/search?query={}",
            "Qwant": "https://www.qwant.com/?q={}"
        }
        self.current_search_engine = "DuckDuckGo"
        
        # Tor settings
        self.tor_enabled = False
        self.tor_controller = None
        self.tor_port = 9050  # Default Tor SOCKS port
        self.control_port = 9051  # Default Tor control port
        
        # Set window icon (incognito logo)
        self.setWindowIcon(self.load_icon("https://cdn.worldvectorlogo.com/logos/incognito-1.svg"))
        
        QWebEngineUrlScheme.registerScheme(QWebEngineUrlScheme(b"about"))
        
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)
        
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.layout.addWidget(self.tabs)
        
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        
        # Navigation buttons with icons
        self.back_button = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        self.back_button.setShortcut(QKeySequence.Back)
        self.back_button.triggered.connect(self.navigate_back)
        self.toolbar.addAction(self.back_button)
        
        self.forward_button = QAction(QIcon.fromTheme("go-next"), "Forward", self)
        self.forward_button.setShortcut(QKeySequence.Forward)
        self.forward_button.triggered.connect(self.navigate_forward)
        self.toolbar.addAction(self.forward_button)
        
        self.reload_button = QAction(QIcon.fromTheme("view-refresh"), "Reload", self)
        self.reload_button.setShortcut(QKeySequence.Refresh)
        self.reload_button.triggered.connect(self.reload_page)
        self.toolbar.addAction(self.reload_button)
        
        self.home_button = QAction(QIcon.fromTheme("go-home"), "Home", self)
        self.home_button.triggered.connect(self.navigate_home)
        self.toolbar.addAction(self.home_button)
        
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Search or enter address")
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.address_bar)
        
        # Search engine menu
        self.search_engine_menu = QMenu("Search Engine", self)
        self.update_search_engine_menu()
        self.search_engine_action = QAction("Search Engine", self)
        self.search_engine_action.setMenu(self.search_engine_menu)
        self.toolbar.addAction(self.search_engine_action)
        
        # New Tab button with icon
        self.new_tab_button = QAction(QIcon.fromTheme("tab-new"), "New Tab", self)
        self.new_tab_button.setShortcut(QKeySequence.AddTab)
        self.new_tab_button.triggered.connect(lambda: self.add_tab())
        self.toolbar.addAction(self.new_tab_button)
        
        # Private Tab button with incognito icon
        incognito_icon = self.load_icon("https://cdn.worldvectorlogo.com/logos/incognito-1.svg")
        self.private_tab_button = QAction(incognito_icon, "New Private Tab", self)
        self.private_tab_button.setShortcut("Ctrl+Shift+P")
        self.private_tab_button.triggered.connect(lambda: self.add_tab(private=True))
        self.toolbar.addAction(self.private_tab_button)
        
        # Tor button
        self.tor_button = QAction("Tor: Off", self)
        self.tor_button.triggered.connect(self.toggle_tor)
        self.toolbar.addAction(self.tor_button)
        
        # VPN status indicator (simulated)
        self.vpn_status = False
        self.vpn_button = QAction("VPN: Off", self)
        self.vpn_button.triggered.connect(self.toggle_vpn)
        self.toolbar.addAction(self.vpn_button)
        
        # Auto-clean cookies setting
        self.auto_clean_cookies = True
        self.cookie_clean_action = QAction("Auto-Clean Cookies: On", self)
        self.cookie_clean_action.triggered.connect(self.toggle_cookie_clean)
        self.toolbar.addAction(self.cookie_clean_action)
        
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        # Timer for periodic status updates
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
        
        self.add_tab(QUrl("https://start.duckduckgo.com"))
        self.apply_dark_theme()
    
    def load_icon(self, url):
        """Load icon from URL or use fallback"""
        try:
            response = requests.get(url, timeout=3)
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            return QIcon(pixmap)
        except:
            return QIcon.fromTheme("user-trash")
    
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QToolBar {
                background-color: #3d3d3d;
                border: none;
                padding: 2px;
            }
            QLineEdit {
                background-color: #4d4d4d;
                color: #ffffff;
                border: 1px solid #5d5d5d;
                border-radius: 4px;
                padding: 5px;
                min-width: 300px;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #5d5d5d;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
                border-bottom: 2px solid #1a73e8;
            }
            QTabBar::tab:hover {
                background-color: #4d4d4d;
            }
            QStatusBar {
                background-color: #3d3d3d;
                color: #aaaaaa;
            }
            QMenu {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #5d5d5d;
            }
            QMenu::item:selected {
                background-color: #1a73e8;
            }
        """)
    
    def add_tab(self, url=None, private=False):
        browser = BrowserTab(private, self)
        
        if url:
            if isinstance(url, QUrl):
                browser.setUrl(url)
            else:
                browser.setUrl(QUrl(url))
        else:
            browser.setUrl(QUrl("https://start.duckduckgo.com"))
        
        tab_text = "Private Tab" if private else "New Tab"
        tab_index = self.tabs.addTab(browser, tab_text)
        
        # Set tab icon
        if private:
            incognito_icon = self.load_icon("https://cdn.worldvectorlogo.com/logos/incognito-1.svg")
            self.tabs.setTabIcon(tab_index, incognito_icon)
        
        self.tabs.setCurrentIndex(tab_index)
        self.tabs.setTabToolTip(tab_index, "Loading...")
        
        browser.iconChanged.connect(lambda icon, tab_index=tab_index: 
                                  self.tabs.setTabIcon(tab_index, icon))
        browser.titleChanged.connect(lambda title, browser=browser: 
                                   self.update_tab_title(browser, title))
        
        return browser
    
    def close_tab(self, index):
        if self.tabs.count() < 2:
            return
            
        widget = self.tabs.widget(index)
        
        # Auto-clean cookies when closing tab
        if self.auto_clean_cookies and hasattr(widget, 'clean_cookies'):
            widget.clean_cookies()
            
        if hasattr(widget, 'profile') and widget.private:
            widget.profile.deleteLater()
        widget.deleteLater()
        self.tabs.removeTab(index)
    
    def current_tab_changed(self, index):
        if index >= 0:
            browser = self.tabs.currentWidget()
            if browser:
                self.address_bar.setText(browser.url().toString())
                self.address_bar.setPlaceholderText(f"Search or enter address - {browser.title()}")
    
    def update_tab_title(self, browser, title):
        index = self.tabs.indexOf(browser)
        if index != -1:
            tab_text = "Private: " + title[:15] + "..." if browser.private else title[:20] + "..."
            self.tabs.setTabText(index, tab_text)
            self.tabs.setTabToolTip(index, title)
    
    def navigate_to_url(self):
        text = self.address_bar.text().strip()
        
        if not text:
            return
            
        # Check if it's a direct URL
        if ("." in text or "/" in text) and " " not in text:
            if not text.startswith(("http://", "https://", "about:", "file:")):
                text = "https://" + text
        else:
            # It's a search query
            text = self.search_engines[self.current_search_engine].format(text)
        
        browser = self.tabs.currentWidget()
        if browser:
            browser.setUrl(QUrl(text))
    
    def navigate_home(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.setUrl(QUrl("https://start.duckduckgo.com"))
    
    def navigate_back(self):
        browser = self.tabs.currentWidget()
        if browser and browser.history().canGoBack():
            browser.back()
    
    def navigate_forward(self):
        browser = self.tabs.currentWidget()
        if browser and browser.history().canGoForward():
            browser.forward()
    
    def reload_page(self):
        browser = self.tabs.currentWidget()
        if browser:
            browser.reload()
    
    def update_search_engine_menu(self):
        """Update the search engine menu with available options"""
        self.search_engine_menu.clear()
        for engine in self.search_engines:
            action = self.search_engine_menu.addAction(engine)
            action.setCheckable(True)
            action.setChecked(engine == self.current_search_engine)
            action.triggered.connect(lambda checked, e=engine: self.set_search_engine(e))
    
    def set_search_engine(self, engine):
        """Set the current search engine"""
        if engine in self.search_engines:
            self.current_search_engine = engine
            self.update_search_engine_menu()
            self.status.showMessage(f"Search engine set to {engine}", 2000)
    
    def toggle_vpn(self):
        """Toggle VPN status (simulated)"""
        self.vpn_status = not self.vpn_status
        self.vpn_button.setText(f"VPN: {'On' if self.vpn_status else 'Off'}")
        
        if self.vpn_status:
            self.status.showMessage("VPN connected - Your traffic is encrypted", 3000)
        else:
            self.status.showMessage("VPN disconnected - Your traffic is not encrypted", 3000)
    
    def toggle_cookie_clean(self):
        """Toggle auto-clean cookies setting"""
        self.auto_clean_cookies = not self.auto_clean_cookies
        self.cookie_clean_action.setText(f"Auto-Clean Cookies: {'On' if self.auto_clean_cookies else 'Off'}")
        self.status.showMessage(f"Auto-clean cookies {'enabled' if self.auto_clean_cookies else 'disabled'}", 2000)
    
    def toggle_tor(self):
        """Toggle Tor connection"""
        if not TOR_AVAILABLE:
            self.show_tor_install_instructions()
            return
            
        if self.tor_enabled:
            self.disable_tor()
        else:
            self.enable_tor()
    
    def show_tor_install_instructions(self):
        """Show instructions for installing Tor"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Tor Not Available")
        msg.setText("To use Tor functionality, you need to:")
        msg.setInformativeText(
            "1. Install Tor Browser or Tor service\n"
            "2. Install Python stem library: pip install stem\n"
            "3. Make sure Tor is running with control port enabled"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def enable_tor(self):
        """Enable Tor routing"""
        try:
            # Try to connect to Tor control port
            self.tor_controller = Controller.from_port(port=self.control_port)
            self.tor_controller.authenticate()
            
            # Verify Tor is working
            if not self.tor_controller.is_newnym_available():
                QMessageBox.warning(self, "Tor Not Ready", 
                                  "Tor is not ready for a new identity. Please wait.")
                self.tor_controller.close()
                self.tor_controller = None
                return
            
            # Get a new identity
            self.tor_controller.signal(Signal.NEWNYM)
            
            self.tor_enabled = True
            self.tor_button.setText("Tor: On")
            self.status.showMessage("Tor enabled - Your traffic is routed through the Tor network", 3000)
            
            # Configure proxy settings
            proxy = QNetworkProxy()
            proxy.setType(QNetworkProxy.Socks5Proxy)
            proxy.setHostName("localhost")
            proxy.setPort(self.tor_port)
            QNetworkProxy.setApplicationProxy(proxy)
            
        except Exception as e:
            error_msg = (
                f"Failed to connect to Tor control port ({self.control_port}):\n"
                f"{str(e)}\n\n"
                "Make sure Tor is running with control port enabled.\n"
                "For Tor Browser, enable control port in torrc file."
            )
            QMessageBox.warning(self, "Tor Connection Failed", error_msg)
            self.tor_enabled = False
            self.tor_button.setText("Tor: Off")
            if hasattr(self, 'tor_controller') and self.tor_controller:
                try:
                    self.tor_controller.close()
                except:
                    pass
                self.tor_controller = None
    
    def disable_tor(self):
        """Disable Tor routing"""
        if self.tor_controller:
            try:
                self.tor_controller.close()
            except:
                pass
            
        self.tor_controller = None
        self.tor_enabled = False
        self.tor_button.setText("Tor: Off")
        
        # Reset proxy settings
        QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.NoProxy))
        self.status.showMessage("Tor disabled - Your traffic is not routed through Tor", 3000)
    
    def update_status(self):
        """Update status bar with current information"""
        status_parts = []
        
        if self.vpn_status:
            status_parts.append("VPN: On")
        else:
            status_parts.append("VPN: Off")
            
        if self.tor_enabled:
            status_parts.append("Tor: On")
        else:
            status_parts.append("Tor: Off")
            
        if self.auto_clean_cookies:
            status_parts.append("Auto-Clean: On")
        else:
            status_parts.append("Auto-Clean: Off")
            
        browser = self.tabs.currentWidget()
        if browser:
            status_parts.append(f"Search: {self.current_search_engine}")
            
        self.status.showMessage(" | ".join(status_parts))
    
    def closeEvent(self, event):
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if hasattr(browser, 'private') and browser.private:
                browser.profile.deleteLater()
        
        reply = QMessageBox.question(
            self, "Exit Confirmation",
            "Are you sure you want to exit? All private tabs will be closed permanently.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clean up Tor connection if active
            if self.tor_enabled:
                self.disable_tor()
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Anonymous Browser")
    app.setApplicationDisplayName("Anonymous Browser")
    
    # Set app icon (will also be used for window icon)
    try:
        response = requests.get("https://cdn.worldvectorlogo.com/logos/incognito-1.svg", timeout=3)
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        app.setWindowIcon(QIcon(pixmap))
    except:
        app.setWindowIcon(QIcon.fromTheme("web-browser"))
    
    browser = AnonymousBrowser()
    browser.show()
    sys.exit(app.exec_())