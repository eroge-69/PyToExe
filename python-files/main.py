import sys, os, json
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QLineEdit, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QObject, QEvent, QUrl

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".mybrowser_config.json")

class GlobalKeyFilter(QObject):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            self.callback(event.key())
        return False  # اجازه بده رویداد به مقصد اصلی بره

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Custom Browser")
        self.resize(900, 600)

        # کلید مخفی: 9 بار ↑ + Escape
        self.key_sequence = []
        self.secret_sequence = [Qt.Key_Up]*9 + [Qt.Key_Escape]

        # مرورگر
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)

        # کانفیگ
        self.config = self.load_config()
        if not self.config:
            self.open_config()
        else:
            self.load_page()

    def handle_key(self, key):
        self.key_sequence.append(key)
        if len(self.key_sequence) > len(self.secret_sequence):
            self.key_sequence = self.key_sequence[-len(self.secret_sequence):]
        if self.key_sequence == self.secret_sequence:
            print("Secret sequence detected! Opening settings...")
            self.open_config()
            self.key_sequence = []

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        return None

    def save_config(self):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f)

    def open_config(self):
        ip, ok = QInputDialog.getText(self, "Settings", "IP Address:", QLineEdit.Normal,
                                      self.config["ip"] if self.config else "")
        if not ok or not ip:
            return

        # بررسی معتبر بودن IP
        parts = ip.split(".")
        if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
            QMessageBox.warning(self, "Invalid IP", "IP Address is not valid!")
            return

        user, ok = QInputDialog.getText(self, "Settings", "Username:", QLineEdit.Normal,
                                        self.config["user"] if self.config else "")
        if not ok or not user:
            return
        passwd, ok = QInputDialog.getText(self, "Settings", "Password:", QLineEdit.Password,
                                          self.config["pass"] if self.config else "")
        if not ok or not passwd:
            return

        self.config = {"ip": ip, "user": user, "pass": passwd}
        self.save_config()
        self.load_page()

    def load_page(self):
        url = f"http://{self.config['ip']}/s/?mmk&u={self.config['user']}&p={self.config['pass']}"
        print(f"Loading: {url}")
        self.browser.setUrl(QUrl(url))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = BrowserWindow()

    # نصب فیلتر کلید روی کل QApplication
    global_filter = GlobalKeyFilter(win.handle_key)
    app.installEventFilter(global_filter)

    win.show()
    sys.exit(app.exec_())
