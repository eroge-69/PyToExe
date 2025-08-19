# main.py
# A simple web browser built with Python and PyQt6

import sys
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QStatusBar, QProgressBar
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PyQt6.QtGui import QAction, QIcon

class BrowserWindow(QMainWindow):
    """Main window for the web browser application."""

    def __init__(self, *args, **kwargs):
        super(BrowserWindow, self).__init__(*args, **kwargs)

        # --- Set up the main window ---
        self.setWindowTitle("Gemini Browser")
        # You can set a window icon here if you have an .ico file
        # self.setWindowIcon(QIcon('path/to/your/icon.ico'))
        self.resize(1200, 800)

        # --- Create the web engine view ---
        self.browser = QWebEngineView()
        # Set a default homepage
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.setCentralWidget(self.browser)

        # --- Create status bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add a progress bar to the status bar
        self.progress_bar = QProgressBar()
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.browser.loadProgress.connect(self.progress_bar.setValue)
        self.progress_bar.hide() # Hide it initially

        # --- Create the navigation toolbar ---
        nav_toolbar = QToolBar("Navigation")
        self.addToolBar(nav_toolbar)

        # --- Add navigation buttons and URL bar to the toolbar ---
        
        # Back Button
        back_btn = QAction("Back", self)
        back_btn.setStatusTip("Go back to the previous page")
        back_btn.triggered.connect(self.browser.back)
        nav_toolbar.addAction(back_btn)

        # Forward Button
        forward_btn = QAction("Forward", self)
        forward_btn.setStatusTip("Go forward to the next page")
        forward_btn.triggered.connect(self.browser.forward)
        nav_toolbar.addAction(forward_btn)

        # Reload Button
        reload_btn = QAction("Reload", self)
        reload_btn.setStatusTip("Reload the current page")
        reload_btn.triggered.connect(self.browser.reload)
        nav_toolbar.addAction(reload_btn)

        # Home Button
        home_btn = QAction("Home", self)
        home_btn.setStatusTip("Go to the home page")
        home_btn.triggered.connect(self.navigate_home)
        nav_toolbar.addAction(home_btn)

        nav_toolbar.addSeparator()

        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_toolbar.addWidget(self.url_bar)

        # --- Connect browser signals to update UI ---
        self.browser.urlChanged.connect(self.update_url_bar)
        self.browser.loadFinished.connect(self.update_title)
        self.browser.loadStarted.connect(lambda: self.progress_bar.show())
        self.browser.loadFinished.connect(lambda: self.progress_bar.hide())


    def navigate_home(self):
        """Navigates the browser to the default homepage."""
        self.browser.setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        """Navigates to the URL entered in the URL bar."""
        q = QUrl(self.url_bar.text())
        # Add 'http://' scheme if missing for proper navigation
        if q.scheme() == "":
            q.setScheme("http")
        self.browser.setUrl(q)

    def update_url_bar(self, q):
        """Updates the URL bar with the current URL of the browser."""
        # We don't want to update the URL bar if the user is typing
        if not self.url_bar.hasFocus():
            self.url_bar.setText(q.toString())
        self.url_bar.setCursorPosition(0)

    def update_title(self):
        """Updates the window title with the current page title."""
        title = self.browser.page().title()
        self.setWindowTitle(f"{title} - Gemini Browser")


if __name__ == "__main__":
    # --- Initialize the application ---
    app = QApplication(sys.argv)
    # Set the application name (useful for some OS features)
    app.setApplicationName("GeminiBrowser")

    # --- Create and show the main window ---
    window = BrowserWindow()
    window.show()

    # --- Start the application's event loop ---
    sys.exit(app.exec())
