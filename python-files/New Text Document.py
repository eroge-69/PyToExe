import sys
import os
import pyautogui
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox

# اینجا مسیر دلخواه خودت رو تعیین کن
SAVE_FOLDER = r"C:\MyScreenshots"

# اگر فولدر وجود نداشت، بسازش
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

class ScreenshotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dual Screenshot Tool")
        self.setGeometry(100, 100, 300, 160)

        self.button1 = QPushButton("Take Screenshot 1", self)
        self.button1.setGeometry(50, 30, 200, 40)
        self.button1.clicked.connect(self.take_screenshot_1)

        self.button2 = QPushButton("Take Screenshot 2", self)
        self.button2.setGeometry(50, 90, 200, 40)
        self.button2.clicked.connect(self.take_screenshot_2)

    def take_screenshot_1(self):
        path = os.path.join(SAVE_FOLDER, "screenshot1.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        QMessageBox.information(self, "Done", f"Screenshot 1 saved:\n{path}")

    def take_screenshot_2(self):
        path = os.path.join(SAVE_FOLDER, "screenshot2.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        QMessageBox.information(self, "Done", f"Screenshot 2 saved:\n{path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenshotApp()
    window.show()
    sys.exit(app.exec_())
