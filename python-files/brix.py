import sys
import ctypes
import winreg
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QLineEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl

# -------------------
# تنظیمات
# -------------------
APP_NAME = "Brix"
URL = "https://mock.irsafam.org"
PASSWORD = "243523@"

# -------------------
# بلاک کلیدها و Task Manager
# -------------------
def block_system_keys():
    import keyboard
    # بلاک Alt+Tab، WinKey و Ctrl+Esc
    keyboard.block_key('alt+tab')
    keyboard.block_key('windows')
    keyboard.block_key('ctrl+esc')

def unblock_system_keys():
    import keyboard
    keyboard.unblock_key('alt+tab')
    keyboard.unblock_key('windows')
    keyboard.unblock_key('ctrl+esc')

def disable_task_manager():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
            0, winreg.KEY_SET_VALUE
        )
    except FileNotFoundError:
        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        )
    winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
    winreg.CloseKey(key)

def enable_task_manager():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
            0, winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, "DisableTaskMgr")
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass

# -------------------
# کلاس Kiosk Browser
# -------------------
class KioskBrowser(QMainWindow):
    def __init__(self, url):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.showFullScreen()

        self.browser = QWebEngineView()
        self.browser.load(QUrl(url))
        self.setCentralWidget(self.browser)

    def keyPressEvent(self, event):
        # ESC یا Alt+F4 برای خروج
        if event.key() == Qt.Key_Escape or (event.key() == Qt.Key_F4 and event.modifiers() & Qt.AltModifier):
            self.ask_password_and_exit()

    def ask_password_and_exit(self):
        pwd, ok = QInputDialog.getText(self, APP_NAME, "Enter password to exit:", QLineEdit.Password)
        if ok and pwd == PASSWORD:
            unblock_system_keys()
            enable_task_manager()
            QApplication.quit()

# -------------------
# اجرا
# -------------------
if __name__ == "__main__":
    import subprocess
    import sys
    import os

    # نصب خودکار پکیج‌ها اگر موجود نبودن
    try:
        import PyQt5
        import PyQtWebEngine
        import keyboard
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5", "PyQtWebEngine", "keyboard"])

    # بلاک کلیدها و Task Manager
    block_system_keys()
    disable_task_manager()

    app = QApplication(sys.argv)
    window = KioskBrowser(URL)
    window.show()
    exit_code = app.exec_()

    # آزادسازی کلیدها بعد از خروج
    unblock_system_keys()
    enable_task_manager()
    sys.exit(exit_code)
