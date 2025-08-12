\
    # NetFix - Tray network watcher for Windows
    # Requires: Python 3.8+, pyqt5, psutil (psutil optional)
    # To build EXE (on your machine): pip install pyinstaller pyqt5 psutil
    # pyinstaller --onefile --windowed --add-data "green_32x32.png;." --add-data "red_32x32.png;." netfix.py

    import sys
    import subprocess
    import time
    import socket
    import os
    from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
    from PyQt5.QtGui import QIcon, QPixmap
    from PyQt5.QtCore import QTimer

    # Config
    PING_HOST = "8.8.8.8"
    CHECK_INTERVAL = 10_000  # ms
    RELEASE_SLEEP = 2  # seconds after release before renew

    def internet_connected(timeout=3):
        try:
            socket.create_connection((PING_HOST, 53), timeout=timeout)
            return True
        except OSError:
            return False

    def run_cmd(cmd, hide_output=True):
        # run command, return (rc, stdout+stderr)
        try:
            if hide_output:
                proc = subprocess.run(cmd, shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                return proc.returncode, proc.stdout
            else:
                proc = subprocess.run(cmd, shell=True, check=False, text=True)
                return proc.returncode, None
        except Exception as e:
            return -1, str(e)

    def reset_network():
        # Full reset: flush DNS, release & renew DHCP lease
        run_cmd("ipconfig /flushdns")
        run_cmd("ipconfig /release")
        time.sleep(RELEASE_SLEEP)
        run_cmd("ipconfig /renew")

    class NetFixTray:
        def __init__(self):
            self.app = QApplication(sys.argv)
            self.app.setQuitOnLastWindowClosed(False)

            # Icons (look for packaged resources next to exe)
            base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
            green_path = os.path.join(base_dir, "green_32x32.png")
            red_path = os.path.join(base_dir, "red_32x32.png")

            self.icon_ok = QIcon(QPixmap(green_path))
            self.icon_bad = QIcon(QPixmap(red_path))

            self.tray = QSystemTrayIcon()
            self.tray.setIcon(self.icon_ok)
            self.tray.setVisible(True)

            menu = QMenu()
            status_action = QAction("Проверить сейчас")
            status_action.triggered.connect(self.manual_check)
            menu.addAction(status_action)
            menu.addSeparator()
            quit_action = QAction("Выйти")
            quit_action.triggered.connect(self.app.quit)
            menu.addAction(quit_action)
            self.tray.setContextMenu(menu)

            self.timer = QTimer()
            self.timer.timeout.connect(self.check_connection)
            self.timer.start(CHECK_INTERVAL)

            # initial check
            QTimer.singleShot(1000, self.check_connection)

        def manual_check(self):
            self.check_connection(manual=True)

        def check_connection(self, manual=False):
            if internet_connected():
                self.tray.setIcon(self.icon_ok)
                self.tray.setToolTip("NetFix: интернет есть")
            else:
                self.tray.setIcon(self.icon_bad)
                self.tray.setToolTip("NetFix: нет интернета — выполняется сброс")
                # perform reset
                reset_network()
                # after reset, wait a bit and re-check
                time.sleep(3)
                if internet_connected():
                    self.tray.showMessage("NetFix", "Соединение восстановлено после сброса.", QSystemTrayIcon.Information, 3000)
                else:
                    self.tray.showMessage("NetFix", "Сброс выполнен, но соединение не восстановлено.", QSystemTrayIcon.Warning, 5000)

        def run(self):
            sys.exit(self.app.exec_())

    if __name__ == "__main__":
        tray = NetFixTray()
        tray.run()
