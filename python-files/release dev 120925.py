import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont, QKeySequence, QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

# Define the Safari-like light theme
SAFARI_THEME_STYLE = """
    QMainWindow {
        background-color: #f5f5f7;
    }
    QToolBar {
        background-color: #e0e0e0;
        border: none;
        padding: 5px;
    }
    QToolButton {
        color: #333333;
        background-color: transparent;
        border: none;
        padding: 8px;
        margin: 2px;
        min-width: 30px;
    }
    QToolButton:hover {
        background-color: #d0d0d0;
        border-radius: 5px;
    }
    QLineEdit {
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #c0c0c0;
        border-radius: 18px;
        padding: 5px 15px;
        font-family: 'Helvetica Neue', 'Arial', sans-serif;
        font-size: 12pt;
    }
    QTabWidget::pane {
        border: none;
    }
    QTabBar {
        qproperty-drawBase: 0;
        border-bottom: 1px solid #c0c0c0;
    }
    QTabBar::tab {
        background: #e0e0e0;
        border: none;
        color: #555555;
        padding: 8px 18px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-right: 2px;
        font-family: 'Helvetica Neue', 'Arial', sans-serif;
        font-size: 10pt;
    }
    QTabBar::tab:selected {
        background: #f5f5f7;
        color: #000000;
        font-weight: bold;
    }
    QTabBar::tab:hover {
        background-color: #d0d0d0;
    }
    QDialog {
        background-color: #f5f5f7;
        color: #000000;
    }
    QLabel {
        color: #000000;
        font-family: 'Helvetica Neue', 'Arial', sans-serif;
    }
    QComboBox {
        background-color: #ffffff;
        border: 1px solid #c0c0c0;
        border-radius: 5px;
        padding: 3px;
        font-family: 'Helvetica Neue', 'Arial', sans-serif;
    }
    QPushButton {
        background-color: #007aff;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 8px 15px;
        font-family: 'Helvetica Neue', 'Arial', sans-serif;
    }
    QPushButton:hover {
        background-color: #005bb5;
    }
"""

class InPrivateProfile(QWebEngineProfile):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHttpCacheType(QWebEngineProfile.NoCache)
        self.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)

class InPrivateTab(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setUrl(QUrl("https://www.google.com/"))
        profile = InPrivateProfile(self)
        self.setPage(QWebEnginePage(profile, self))

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.setStyleSheet(parent.styleSheet())
        self.setFixedSize(350, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        search_engine_label = QLabel("Default Search Engine:")
        layout.addWidget(search_engine_label)
        
        self.search_engine_combo = QComboBox()
        self.search_engine_combo.addItems(["Google", "DuckDuckGo", "Bing", "Baidu"])
        
        current_engine = parent.default_search_engine_name
        index = self.search_engine_combo.findText(current_engine)
        if index != -1:
            self.search_engine_combo.setCurrentIndex(index)
            
        layout.addWidget(self.search_engine_combo)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        layout.addWidget(save_btn)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setStyleSheet(SAFARI_THEME_STYLE)
        
        self.resize(1200, 800)
        self.setWindowTitle('Gnikcah browzer')
        self.setWindowIcon(QIcon('browser_icon.png')) # Add a window icon if you have one

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabBar(CustomTabBar(self))
        self.setCentralWidget(self.tabs)

        self.default_search_engine = "https://www.google.com/search?q="
        self.default_search_engine_name = "Google"

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setFont(QFont("Helvetica Neue", 12))
        self.url_bar.setPlaceholderText("Search or enter website name")

        # Global menu bar
        self.create_menu_bar()

        navbar = QToolBar("Navigation")
        navbar.setIconSize(QSize(22, 22))
        self.addToolBar(Qt.TopToolBarArea, navbar)

        # Safari-like navigation icons (using Unicode characters for cross-platform support)
        back_btn = QAction('◀', self)
        back_btn.triggered.connect(self.navigate_back)
        navbar.addAction(back_btn)

        forward_btn = QAction('▶', self)
        forward_btn.triggered.connect(self.navigate_forward)
        navbar.addAction(forward_btn)

        reload_btn = QAction('⟳', self)
        reload_btn.triggered.connect(self.reload_current_tab)
        navbar.addAction(reload_btn)

        navbar.addSeparator()
        navbar.addWidget(self.url_bar)
        navbar.addSeparator()

        new_tab_btn = QAction('+', self)
        new_tab_btn.setShortcut(QKeySequence("Ctrl+T"))
        new_tab_btn.triggered.connect(lambda: self.add_new_tab())
        navbar.addAction(new_tab_btn)

        home_btn = QAction('🏠', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        inprivate_tab_btn = QAction('🔒', self)
        inprivate_tab_btn.setShortcut(QKeySequence("Ctrl+Shift+N"))
        inprivate_tab_btn.triggered.connect(self.add_inprivate_tab)
        navbar.addAction(inprivate_tab_btn)
        
        # Add the first tab
        self.add_new_tab()
    
    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")

        new_tab_action = QAction("New Tab", self)
        new_tab_action.setShortcut(QKeySequence("Ctrl+T"))
        new_tab_action.triggered.connect(lambda: self.add_new_tab())
        file_menu.addAction(new_tab_action)

        new_private_window_action = QAction("New Private Window", self)
        new_private_window_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        new_private_window_action.triggered.connect(lambda: self.add_inprivate_tab())
        file_menu.addAction(new_private_window_action)

        close_tab_action = QAction("Close Tab", self)
        close_tab_action.setShortcut(QKeySequence("Ctrl+W"))
        close_tab_action.triggered.connect(self.close_current_tab_shortcut)
        file_menu.addAction(close_tab_action)

        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Edit Menu
        edit_menu = menu_bar.addMenu("&Edit")
        # Add a placeholder 'Settings' option
        settings_action = QAction("Settings...", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self.show_settings)
        edit_menu.addAction(settings_action)

    def show_settings(self):
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec_() == QDialog.Accepted:
            selected_engine_name = settings_dialog.search_engine_combo.currentText()
            self.set_search_engine(selected_engine_name)

    def set_search_engine(self, engine_name):
        self.default_search_engine_name = engine_name
        if engine_name == "Google":
            self.default_search_engine = "https://www.google.com/search?q="
        elif engine_name == "DuckDuckGo":
            self.default_search_engine = "https://duckduckgo.com/?q="
        elif engine_name == "Bing":
            self.default_search_engine = "https://www.bing.com/search?q="
        elif engine_name == "Baidu":
            self.default_search_engine = "https://www.baidu.com/s?wd="
        
        QMessageBox.information(self, "Settings Updated", f"Default search engine set to {engine_name}.")

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl('https://www.google.com/')
        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_url_bar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))
        self.current_browser = browser
        return browser

    def add_new_tab_with_url_bar(self):
        url_text = self.url_bar.text()
        if not url_text:
            self.add_new_tab()
        else:
            url = QUrl(url_text)
            self.add_new_tab(url, url_text)

    def add_inprivate_tab(self):
        browser = InPrivateTab()
        i = self.tabs.addTab(browser, 'Private Tab')
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_url_bar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))


    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def close_current_tab_shortcut(self):
        i = self.tabs.currentIndex()
        self.close_current_tab(i)

    def current_tab_changed(self, i):
        self.current_browser = self.tabs.widget(i)
        if self.current_browser:
            self.update_url_bar(self.current_browser.url(), self.current_browser)

    def update_url_bar(self, q, browser=None):
        if browser != self.current_browser:
            return
        self.url_bar.setText(q.toString())

    def navigate_home(self):
        if self.current_browser:
            self.current_browser.setUrl(QUrl('https://google.com'))

    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return
        
        # Check if it's a URL
        if '.' in text and not text.startswith(('http://', 'https://')):
            url = 'http://' + text
        else:
            search_query = QUrl.toPercentEncoding(text.encode('utf-8'))
            url = self.default_search_engine + search_query
        
        q = QUrl(url)
        if self.current_browser:
            self.current_browser.setUrl(q)

    def navigate_back(self):
        if self.current_browser:
            self.current_browser.back()

    def navigate_forward(self):
        if self.current_browser:
            self.current_browser.forward()

    def reload_current_tab(self):
        if self.current_browser:
            self.current_browser.reload()

class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.setElideMode(Qt.ElideRight)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName('Gnikcah browzer')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())