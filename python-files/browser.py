import sys
import os
import re
import json
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage , QWebEngineDownloadRequest, QWebEngineProfile, QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo, QWebEnginePage as CorePage
from PyQt6.QtWidgets import *
from PyQt6 import QtGui
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtNetwork import QNetworkCookieJar, QNetworkCookie


# ✅ Optional: Enable media stream in Chromium backend
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-media-stream"


class AdBlocker(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info: QWebEngineUrlRequestInfo):
        url = info.requestUrl().toString()

        ad_domains = [
            'doubleclick.net', 'googleadservices.com', 'ads.youtube.com', 
            'pagead2.googlesyndication.com', 'adnxs.com', 'trackcmp.net', 
            'adroll.com', 'googlesyndication.com', 'securepubads.g.doubleclick.net', 
            'ytads.youtube.com', 'static.wolf-327b.com', 'cdn.wolf-327b.com', 
            'acdn.tsyndicate.com', 'adservice.google.com'
        ]

        if any(domain in url for domain in ad_domains) or re.search(r'\b(ad|track|analytics|advertisement|served)\b', url, re.IGNORECASE):
            print(f"Blocked: {url}")
            info.block(True)


class CustomWebEngineProfile(QWebEngineProfile):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUrlRequestInterceptor(AdBlocker())  # Set your ad blocker if needed

        # Initialize cookie store
        self.cookie_store = self.cookieStore()

    def get_cookies(self, url):
        """Get cookies for a specific URL."""
        cookies = self.cookie_store.cookiesForUrl(QUrl(url))
        return cookies

    def set_cookie(self, page: QWebEnginePage, cookie_dict: dict):
        """Inject cookies using JavaScript."""
        for key, value in cookie_dict.items():
            js_code = f"document.cookie = '{key}={value}; path=/';"
            page.runJavaScript(js_code)


    def clear_cookies(self):
        """Clear all cookies."""
        self.cookie_store.deleteAllCookies()


class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.featurePermissionRequested.connect(self.handle_feature_permission)
        

    def handle_feature_permission(self, url, feature):
        if feature in (
            CorePage.Feature.MediaAudioCapture,
            CorePage.Feature.MediaVideoCapture,
            CorePage.Feature.MediaAudioVideoCapture,
        ):
            # Display a permission dialog asking the user
            reply = self.ask_permission(feature)

            if reply == QMessageBox.StandardButton.Yes:
                self.setFeaturePermission(
                    url,
                    feature,
                    CorePage.PermissionPolicy.PermissionGrantedByUser
                )
            else:
                self.setFeaturePermission(
                    url,
                    feature,
                    CorePage.PermissionPolicy.PermissionDeniedByUser
                )

    def ask_permission(self, feature):
        # Create the permission dialog
        msg = QMessageBox(self.main_window)  # Use main_window as the parent widget
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("Permission Request")

        if feature == CorePage.Feature.MediaAudioCapture:
            msg.setText("This website wants to use your microphone. Do you allow it?")
        elif feature == CorePage.Feature.MediaVideoCapture:
            msg.setText("This website wants to use your camera. Do you allow it?")
        elif feature == CorePage.Feature.MediaAudioVideoCapture:
            msg.setText("This website wants to use both your microphone and camera. Do you allow it?")

        # Use StandardButton.Yes instead of QMessageBox.Yes
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        reply = msg.exec()

        return reply  # Return user's choice

    
    def createWindow(self, _type):
        if self.main_window:
            return self.main_window.create_new_tab_from_page()
        return None
    


class BrowserTab(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout(self)
        self.browser = QWebEngineView()

        self.interceptor = AdBlocker()
        QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(self.interceptor)

        self.page = CustomWebEnginePage(self.browser, main_window=self.main_window)
        self.browser.setPage(self.page)

        self.browser.setUrl(QUrl("https://google.com"))
        self.layout.addWidget(self.browser)
        self.setLayout(self.layout)

    def createWindow(self, type: int) -> 'QWebEngineView':
        return self.browser


def read_text_file_lines(filepath):
    lines = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                lines.append(line.rstrip('\n'))
    return lines


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Sbrows")
        self.setGeometry(100, 100, 1200, 800)
        self.showMaximized()
        self.setStyleSheet('font-size: 15px;')
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.profile = CustomWebEngineProfile()

        self.profile.downloadRequested.connect(self.handle_download)


        self.history = []
        self.load_history()

        self.completer = QCompleter(read_text_file_lines('links.txt'))
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self.tabs = QTabWidget()
        self.new_tab_button = QToolButton()
        self.new_tab_button.setText('+')
        self.new_tab_button.setStyleSheet('font-size: 25px; font-weight:bold;')
        self.new_tab_button.setToolTip('Open New Tab')
        self.new_tab_button.clicked.connect(lambda: self.add_new_tab(QUrl("https://google.com"), "New Tab"))
        self.tabs.setCornerWidget(self.new_tab_button, Qt.Corner.TopRightCorner)

        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)
        self.tabs.setMovable(True)
        self.tabs.setStyleSheet(
            'QTabBar::tab { padding: 5px 5px;min-width:100px; max-width:280px; margin: 1px 5px; text-align: left; border-radius: 5px; height: 20px; font-size: 15px; }'
            'QTabBar::tab:!selected {border:1px solid #6d6d6e;}'
            'QTabBar::tab:selected {border:1px solid #305db8; background-color:#335987;}')
        self.tabs.setTabShape(QTabWidget.TabShape.Rounded)
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)

        self.setCentralWidget(self.tabs)

        self.init_ui()
        self.add_new_tab(QUrl("https://google.com"), "New Tab")

    def create_new_tab_from_page(self):
        """Create a new tab from the current page."""
        current_browser = self.current_browser()
        if current_browser:
            new_tab = BrowserTab(self)
            new_tab.browser.setPage(current_browser.page())
            new_tab.browser.setUrl(current_browser.url())
            self.add_new_tab(new_tab.browser.url(), "New Tab")
            return new_tab.browser
        return None

    def init_ui(self):
        navbar = QToolBar()
        self.addToolBar(navbar)
        navbar.setMovable(True)
        navbar.setStyleSheet('font-size: 20px;')

        back_btn = QAction('🡸', self)
        back_btn.setShortcut('Alt+Left')
        back_btn.setToolTip('Go Back')
        back_btn.triggered.connect(lambda: self.current_browser().back())
        navbar.addAction(back_btn)

        reload_btn = QAction('⟲', self)
        reload_btn.setIcon(QIcon.fromTheme("view-refresh"))
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        navbar.addAction(reload_btn)
        reload_btn.setShortcut('Ctrl+R')
        reload_btn.setToolTip('Reload Page')


        forward_btn = QAction('🡺', self)
        forward_btn.setShortcut('Alt+Right')
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        navbar.addAction(forward_btn)
        forward_btn.setShortcut('Alt+Right')
        forward_btn.setToolTip('Go Forward')

        home_btn = QAction('🏠︎', self)
        home_btn.setIcon(QIcon.fromTheme("go-home"))
        home_btn.triggered.connect(lambda: self.current_browser().setUrl(QUrl("https://google.com")))
        home_btn.setToolTip('Go Home')
        home_btn.setShortcut('Ctrl+H')
        navbar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setStyleSheet('margin:5px;')
        navbar.addWidget(self.url_bar)
        self.url_bar.setCompleter(self.completer)
        self.url_bar.setPlaceholderText("Enter URL or search...")
        self.url_bar.setClearButtonEnabled(True)
        self.url_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.url_bar.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)  # Disable context menu
        self.url_bar.setStyleSheet('QLineEdit {font-size:15px; border: 1px solid #6d6d6e; border-radius: 5px; padding: 5px; margin: 3px; }')


         # Create a button to toggle the side panel
        toggle_sidebar_btn = QAction('☰', self)  # Hamburger button
        toggle_sidebar_btn.triggered.connect(self.toggle_sidebar)
        toggle_sidebar_btn.setShortcut('Ctrl+B')
        toggle_sidebar_btn.setToolTip('History and more')
        navbar.addAction(toggle_sidebar_btn)

        # Create a side panel with buttons
        self.create_sidebar()

    def create_sidebar(self):
        self.sidebar = QDockWidget("Sidebar", self)
        self.sidebar.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                                  QDockWidget.DockWidgetFeature.DockWidgetMovable)
    
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
    
        # --- Group 1: Tab Management ---
        tab_group = QGroupBox("Tab Management")
        tab_layout = QVBoxLayout()
        new_tab_btn = QPushButton("New Tab")
        new_tab_btn.clicked.connect(lambda: self.add_new_tab(QUrl("https://google.com"), "New Tab"))
        new_window_btn = QPushButton("New Window")
        new_window_btn.clicked.connect(self.open_new_window)
        tab_layout.addWidget(new_tab_btn)
        tab_layout.addWidget(new_window_btn)
        tab_group.setLayout(tab_layout)
        sidebar_layout.addWidget(tab_group)
    
        # --- Group 2: Privacy Controls ---
        privacy_group = QGroupBox("Privacy Controls")
        privacy_layout = QVBoxLayout()
        clear_cookies_btn = QPushButton("Clear Cookies")
        clear_cookies_btn.clicked.connect(self.clear_cookies)
        privacy_layout.addWidget(clear_cookies_btn)
        privacy_group.setLayout(privacy_layout)
        sidebar_layout.addWidget(privacy_group)
    
        # --- Group 3: History ---
        history_group = QGroupBox("History")
        history_layout = QVBoxLayout()
        show_history_btn = QPushButton("Show History")
        show_history_btn.clicked.connect(self.show_history)
        history_layout.addWidget(show_history_btn)
        history_group.setLayout(history_layout)
        sidebar_layout.addWidget(history_group)
    
        # --- Misc ---
        close_btn = QPushButton("Close Browser")
        close_btn.clicked.connect(self.close)
        sidebar_layout.addWidget(close_btn)
    
        sidebar_layout.addStretch()
        self.sidebar.setWidget(sidebar_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.sidebar)
        self.sidebar.setVisible(False)
        self.sidebar.setFixedWidth(220)
    def toggle_sidebar(self):
        """Toggle the sidebar visibility."""
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def handle_download(self, download: QWebEngineDownloadRequest):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", download.downloadFileName())
        if not save_path:
            download.cancel()
            return

        download.setDownloadFileName(os.path.basename(save_path))
        download.setPath(save_path)
        download.accept()

        # Progress Dialog
        progress_dialog = QProgressDialog(f"Downloading {download.downloadFileName()}...", "Cancel", 0, 100, self)
        progress_dialog.setWindowTitle("Download Progress")
        progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress_dialog.setAutoClose(True)
        progress_dialog.show()

        def update_progress(received, total):
            if total > 0:
                percent = int((received / total) * 100)
                progress_dialog.setValue(percent)
                progress_dialog.setLabelText(
                    f"{download.downloadFileName()}: {received // 1024} KB of {total // 1024} KB"
                )

        def on_finished():
            progress_dialog.close()
            QMessageBox.information(self, "Download Finished", f"File saved to:\n{save_path}")

        def on_cancel():
            download.cancel()
            progress_dialog.close()

        download.downloadProgress.connect(update_progress)
        download.finished.connect(on_finished)
        progress_dialog.canceled.connect(on_cancel)


    def clear_cookies(self):
        """Clear all cookies."""
        self.profile.clear_cookies()
        print("Cookies cleared")

    def show_history(self):
        """Show the browsing history in a dialog with delete and clear options."""
        history_window = QDialog(self)
        history_window.setWindowTitle("History")
        history_layout = QVBoxLayout()

        # Create a QListWidget to display history items
        history_list = QListWidget()

        # Add history URLs to the list
        for entry in self.history:
            item = QListWidgetItem(entry)
            history_list.addItem(item)

        # Create the "Delete" button to delete selected history item
        def delete_selected_history():
            selected_item = history_list.selectedItems()
            if selected_item:
                item = selected_item[0]
                history_url = item.text()
                response = QMessageBox.question(self, 'Confirm Deletion', 
                                                f"Are you sure you want to delete '{history_url}' from history?", 
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if response == QMessageBox.StandardButton.Yes:
                    # Remove from history and update the saved file
                    self.history.remove(history_url)
                    self.save_history()  # Update the history file
                    history_list.takeItem(history_list.row(item))  # Remove item from the list

        # Create the "Clear History" button to clear all history
        def clear_all_history():
            response = QMessageBox.question(self, 'Clear All History', 
                                            "Are you sure you want to clear all browsing history?", 
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if response == QMessageBox.StandardButton.Yes:
                # Clear history and update the saved file
                self.history.clear()
                self.save_history()  # Clear history in the file
                history_list.clear()  # Clear all items from the list
                QMessageBox.information(self, 'History Cleared', 'All browsing history has been cleared.')

        # Add the "Delete" and "Clear All" buttons
        delete_btn = QPushButton("Delete Selected History", self)
        delete_btn.clicked.connect(delete_selected_history)
        history_layout.addWidget(history_list)
        history_layout.addWidget(delete_btn)

        clear_btn = QPushButton("Clear All History", self)
        clear_btn.clicked.connect(clear_all_history)
        history_layout.addWidget(clear_btn)

        history_window.setLayout(history_layout)
        history_window.exec()
    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl("https://google.com")

        new_tab = BrowserTab(self)
        new_tab.browser.setUrl(qurl)
        i = self.tabs.addTab(new_tab, label)
        self.tabs.setCurrentIndex(i)

        #loading_icon = QtGui.QIcon("loading.gif")
        loading_icon = QIcon.fromTheme("view-refresh")
        self.tabs.setTabIcon(i, loading_icon)

        new_tab.browser.loadStarted.connect(lambda: self.tabs.setTabIcon(self.tabs.indexOf(new_tab), QtGui.QIcon("loading.gif")))
        new_tab.browser.iconChanged.connect(
            lambda icon, tab=new_tab: self.set_tab_icon(icon, self.tabs.indexOf(tab)))
        new_tab.browser.urlChanged.connect(lambda q, b=new_tab.browser: self.update_url_bar(q))
        new_tab.browser.titleChanged.connect(lambda title, tab=new_tab: self.update_tab_title(title, tab))
        new_tab.browser.loadProgress.connect(lambda progress, tab=new_tab: self.update_tab_title(f"{progress}% - loading...", tab))
        new_tab.browser.loadFinished.connect(lambda ok, tab=new_tab: self.update_url_bar(tab.browser.url()))
        new_tab.browser.loadFinished.connect(lambda ok, tab=new_tab: self.update_tab_title(tab.browser.title(), tab))

        # Update history on new page load
        self.update_history(qurl)

    def open_new_window(self):
        new_window = MainWindow()
        new_window.show()

        # Store reference to avoid being garbage collected
        if not hasattr(self, 'child_windows'):
            self.child_windows = []
        self.child_windows.append(new_window)

    def update_history(self, url):
        """Update the browsing history."""
        if url not in self.history:
            self.history.insert(0, url.toString()) 
            if len(self.history) > 50:
                self.history.pop(0)
        self.save_history()

    def save_history(self):
        """Save the browsing history to a file."""
        with open('history.json', 'w') as file:
            json.dump(self.history, file)

    def load_history(self):
        """Load the browsing history from a file."""
        if os.path.exists('history.json'):
            with open('history.json', 'r') as file:
                self.history = json.load(file)

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url.startswith(("http://", "https://")):
            if re.match(r'^[\w\-]+(\.[\w\-]+)+.*$', url):
                url = "https://" + url
            else:
                url = f"https://www.google.com/search?q={QUrl.toPercentEncoding(url).data().decode()}"
        self.current_browser().setUrl(QUrl(url))
        self.update_history(QUrl(url))
        

    def update_url_bar(self, qurl=None):
        # Ensure qurl is a valid QUrl object or convert it to one
        if isinstance(qurl, QUrl):
            url = qurl
        elif isinstance(qurl, str):
            url = QUrl(qurl)
        else:
            # If qurl is None or invalid, use the current URL of the browser
            browser = self.current_browser()
            if browser:
                url = browser.url()
            else:
                url = QUrl()

        # Update the URL bar text
        self.url_bar.setText(url.toString())

        # Remove old icon action if any
        if hasattr(self, 'lock_action'):
            self.url_bar.removeAction(self.lock_action)

        # Choose icon and color based on the scheme
        if url.scheme() == "https":
            icon = QIcon('img/locked.png') 
        else:
            icon = QIcon('img/unlocked.png')

        # Add icon to the left side of the URL bar
        self.lock_action = self.url_bar.addAction(icon, QLineEdit.ActionPosition.LeadingPosition)
    
    
    
    def current_browser(self):
        current_widget = self.tabs.currentWidget()
        return current_widget.browser if current_widget else None

    def update_tab_title(self, title, tab):
        index = self.tabs.indexOf(tab)
        if index >= 0:
            self.tabs.setTabText(index, title)

    def set_tab_icon(self, icon, index):
        self.tabs.setTabIcon(index, icon)

    def close_current_tab(self, index):
        if self.tabs.count() > 1:
            tab_widget = self.tabs.widget(index)
            if isinstance(tab_widget, BrowserTab):
                browser = tab_widget.browser
                browser.stop()  # Stop loading
                browser.setUrl(QUrl("about:blank"))  # Navigate to blank
                browser.page().deleteLater()  # Clean up page resources
                browser.deleteLater()  # Clean up browser
                tab_widget.deleteLater()  # Clean up container
            self.tabs.removeTab(index)
        else:
            self.close()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())