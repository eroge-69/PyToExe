import sys
import os
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QWidget, QStackedLayout
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage

class BrowserApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.var = False  # False = Scratch visible, True = Discord visible
        self.setWindowTitle("Scratch Desktop")

        # Create a persistent profile directory
        profile_path = os.path.join(os.getcwd(), "browser_profile")
        os.makedirs(profile_path, exist_ok=True)

        # Create and assign persistent profile
        self.profile = QWebEngineProfile("PersistentProfile", self)
        self.profile.setPersistentStoragePath(profile_path)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)

        # Create pages and views for both sites
        self.discord_page = QWebEnginePage(self.profile, self)
        self.discord_view = QWebEngineView(self)
        self.discord_view.setPage(self.discord_page)
        self.discord_view.load(QUrl("https://discord.com/app"))

        self.scratch_page = QWebEnginePage(self.profile, self)
        self.scratch_view = QWebEngineView(self)
        self.scratch_view.setPage(self.scratch_page)
        self.scratch_view.load(QUrl("https://scratch.mit.edu"))

        # Create a stacked layout to hold both webviews
        container = QWidget()
        self.stack = QStackedLayout()
        container.setLayout(self.stack)
        self.stack.addWidget(self.scratch_view)  # index 0
        self.stack.addWidget(self.discord_view)  # index 1
        self.setCentralWidget(container)

        # Show Scratch initially (index 0)
        self.stack.setCurrentIndex(0)

        self.showMaximized()

        # Hotkey: ALT+X (Windows/Linux), OPTION+X (Mac)
        shortcut = QShortcut(QKeySequence("Alt+X"), self)
        shortcut.activated.connect(self.toggle_site)

    def toggle_site(self):
        self.var = not self.var
        # If var True show Discord (index 1), else Scratch (index 0)
        self.stack.setCurrentIndex(1 if self.var else 0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = BrowserApp()
    browser.show()
    sys.exit(app.exec_())
