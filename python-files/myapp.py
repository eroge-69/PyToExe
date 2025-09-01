import sys
from PyQt5.QtCore import Qt, QUrl, QDateTime, QEventLoop, QTimer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QPushButton, QLabel, QHBoxLayout, QDialog, QAction,
                             QTextEdit, QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtNetwork import QNetworkCookie


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 400)

        main_layout = QVBoxLayout()

        label = QLabel("Application Settings")
        label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")

        buttons_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                font-size: 13px;
                background: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.update_cookies_display)

        reset_btn = QPushButton("🗑️ Reset Cookies")
        reset_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                font-size: 13px;
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                margin-left: 10px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        reset_btn.clicked.connect(self.reset_cookies)

        buttons_layout.addWidget(refresh_btn)
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addStretch()

        self.cookie_display = QTextEdit()
        self.cookie_display.setReadOnly(True)
        self.cookie_display.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
            }
        """)

        main_layout.addWidget(label)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(QLabel("Current Cookies:"))
        main_layout.addWidget(self.cookie_display, 1)  # Expandable

        self.setLayout(main_layout)

        self.update_cookies_display()

    def get_cookies(self, timeout=2000):
        """Return a list of cookies, waits up to timeout ms"""
        cookies = []
        profile = QWebEngineProfile.defaultProfile()
        cookie_store = profile.cookieStore()

        loop = QEventLoop()

        def on_cookie_added(cookie):
            cookies.append(cookie)

        cookie_store.cookieAdded.connect(on_cookie_added)
        cookie_store.loadAllCookies()

        QTimer.singleShot(timeout, loop.quit)
        loop.exec_()

        cookie_store.cookieAdded.disconnect(on_cookie_added)
        return cookies

    def update_cookies_display(self):
        cookies = self.get_cookies()
        if not cookies:
            self.cookie_display.setText("No cookies found.")
            return

        cookie_text = []
        for cookie in cookies:
            name = cookie.name().data().decode('utf-8', errors='replace')
            value = cookie.value().data().decode('utf-8', errors='replace')
            cookie_text.append(f"🔹 {name} = {value}")
            cookie_text.append(f"   Domain: {cookie.domain()}")
            cookie_text.append(f"   Path: {cookie.path()}")
            cookie_text.append(f"   Expires: {cookie.expirationDate().toString() if not cookie.isSessionCookie() else 'Session'}")
            cookie_text.append(f"   Secure: {'Yes' if cookie.isSecure() else 'No'}")
            cookie_text.append(f"   HTTP Only: {'Yes' if cookie.isHttpOnly() else 'No'}")
            cookie_text.append("")

        self.cookie_display.setText("\n".join(cookie_text))

    def reset_cookies(self):
        try:
            profile = QWebEngineProfile.defaultProfile()
            cookie_store = profile.cookieStore()
            cookie_store.deleteAllCookies()

            def set_cookie(name, value, domain='recivics.uk'):
                cookie = QNetworkCookie(name.encode(), str(value).encode())
                cookie.setDomain(domain)
                cookie.setExpirationDate(QDateTime.currentDateTime().addYears(1))
                cookie_store.setCookie(cookie, QUrl("http://" + domain))

            set_cookie('facebook_interacted', 'true')
            set_cookie('has_seen_dummy', 'true')

            QMessageBox.information(self, "Success", "Cookies have been reset!")
            self.update_cookies_display()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset cookies: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Desktop App")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.profile = QWebEngineProfile.defaultProfile()
        self.cookie_store = self.profile.cookieStore()

        self.set_default_cookies()

        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl("http://recivics.uk"))
        self.web_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.web_view.customContextMenuRequested.connect(self.show_context_menu)

        self.layout.addWidget(self.web_view)

        self.setStyleSheet("""
            QMainWindow {
                background: white;
            }
            QWebEngineView {
                border: none;
            }
        """)

    def set_default_cookies(self):
        def set_cookie(name, value, domain='recivics.uk'):
            cookie = QNetworkCookie(name.encode(), str(value).encode())
            cookie.setDomain(domain)
            cookie.setExpirationDate(QDateTime.currentDateTime().addYears(1))
            self.cookie_store.setCookie(cookie, QUrl("http://" + domain))

        set_cookie('facebook_interacted', 'true')
        set_cookie('has_seen_dummy', 'true')

    def show_context_menu(self, pos):
        menu = self.web_view.page().createStandardContextMenu()
        menu.addSeparator()
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        menu.exec_(self.web_view.mapToGlobal(pos))

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

