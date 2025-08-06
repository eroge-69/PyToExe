
import sys
import pyautogui
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox

# دو مسیر متفاوت برای ذخیره‌ی دو عکس
SAVE_PATH_1 = r"C:\Users\Public\screenshot1.png"
SAVE_PATH_2 = r"C:\Users\Public\screenshot2.png"

class ScreenshotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("گرفتن اسکرین‌شات (دوگانه)")
        self.setGeometry(100, 100, 300, 160)

        self.button1 = QPushButton("گرفتن اسکرین‌شات 1", self)
        self.button1.setGeometry(50, 30, 200, 40)
        self.button1.clicked.connect(self.take_screenshot_1)

        self.button2 = QPushButton("گرفتن اسکرین‌شات 2", self)
        self.button2.setGeometry(50, 90, 200, 40)
        self.button2.clicked.connect(self.take_screenshot_2)

    def take_screenshot_1(self):
        screenshot = pyautogui.screenshot()
        screenshot.save(SAVE_PATH_1)
        QMessageBox.information(self, "انجام شد", f"اسکرین‌شات 1 ذخیره شد:\n{SAVE_PATH_1}")

    def take_screenshot_2(self):
        screenshot = pyautogui.screenshot()
        screenshot.save(SAVE_PATH_2)
        QMessageBox.information(self, "انجام شد", f"اسکرین‌شات 2 ذخیره شد:\n{SAVE_PATH_2}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenshotApp()
    window.show()
    sys.exit(app.exec_())
