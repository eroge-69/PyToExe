import sys
import io
import threading
import requests
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QGuiApplication
from pynput import keyboard

class ScreenshotUploader(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.upload_url = ""
        self.trigger_key = "print_screen"
        self.listener_thread = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Screenshot Uploader Config')
        self.resize(400, 200)

        layout = QtWidgets.QVBoxLayout()

        self.url_input = QtWidgets.QLineEdit(self)
        self.url_input.setPlaceholderText("Вставьте сюда URL для загрузки")
        layout.addWidget(self.url_input)

        self.key_input = QtWidgets.QLineEdit(self)
        self.key_input.setPlaceholderText("Введите клавишу для скриншота (например, print_screen)")
        layout.addWidget(self.key_input)

        self.start_btn = QtWidgets.QPushButton('Запустить в фоне', self)
        self.start_btn.clicked.connect(self.start_background_mode)
        layout.addWidget(self.start_btn)

        self.setLayout(layout)

    def start_background_mode(self):
        self.upload_url = self.url_input.text().strip()
        self.trigger_key = self.key_input.text().strip().lower()
        if not self.upload_url or not self.trigger_key:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите URL и клавишу.")
            return

        self.hide()  # Скрыть окно
        self.listener_thread = threading.Thread(target=self.listen_keyboard, daemon=True)
        self.listener_thread.start()

    def listen_keyboard(self):
        def on_press(key):
            try:
                if key.char == self.trigger_key:
                    self.take_screenshot_and_upload()
            except AttributeError:
                if key.name == self.trigger_key:
                    self.take_screenshot_and_upload()
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    def take_screenshot_and_upload(self):
        app = QGuiApplication.instance()
        screen = app.primaryScreen()
        screenshot = screen.grabWindow(0)

        buffer = io.BytesIO()
        screenshot.save(buffer, 'PNG')
        buffer.seek(0)

        try:
            response = requests.post(
                self.upload_url,
                files={'file': ('screenshot.png', buffer, 'image/png')}
            )
            print("Статус загрузки:", response.status_code)
        except Exception as e:
            print("Ошибка при загрузке:", e)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    uploader = ScreenshotUploader()
    uploader.show()
    sys.exit(app.exec_())
