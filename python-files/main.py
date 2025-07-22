import os
from PyQt5.QtWidgets import QApplication
from main_window import Window

import sys
# os.system("C:\Software\WinPython\WPy64-39100\python-3.9.10.amd64\python.exe -m PyQt5.uic.pyuic -o resources//ui//main_window_ui.py resources//ui//main_window.ui")

# Main
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.setWindowTitle('Bundles Maker')
    # win.showMaximized()
    win.show()
    sys.exit(app.exec())
