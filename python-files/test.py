import os
import sys
import time
import tempfile
import base64
import traceback

from PyQt5 import QtCore, QtGui, QtWidgets
import mss
import mss.tools

# OpenAI импортируем динамически, чтобы можно было запускать GUI без ключа,
# но для работы с API пакет openai должен быть установлен.
try:
    import openai
except Exception:
    openai = None

# ---------------------------------------------------------
# Настройки
# ---------------------------------------------------------
MODEL_NAME = "gpt-5-vision-preview"
# ---------------------------------------------------------


def take_screenshot_to_file(filename: str):
    """Скриншот всего экрана, сохраняет в filename (PNG)."""
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # первый монитор (весь экран)
        sct_img = sct.grab(monitor)
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)


class APICallThread(QtCore.QThread):
    """В отдельном потоке делаем снимок и вызываем OpenAI API."""
    result_ready = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        try:
            if openai is None:
                raise RuntimeError("Пакет openai не установлен. Установи через: pip install openai")

            # Проверяем, что ключ есть
            if not getattr(openai, "api_key", None):
                raise RuntimeError("OpenAI API key не найден. Перезапусти приложение и введи ключ при запросе.")

            # временный файл
            tmp_dir = tempfile.gettempdir()
            fname = os.path.join(tmp_dir, f"mts_screenshot_{int(time.time())}.png")

            take_screenshot_to_file(fname)

            # читаем файл и кодируем
            with open(fname, "rb") as f:
                b = f.read()
            b64 = base64.b64encode(b).decode()

            messages = [
                {"role": "system", "content": "Ты эксперт по тестам. Отвечай кратко в формате: 'Начало вопроса... → Правильный ответ'."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Найди правильные ответы на картинке ниже:"},
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64," + b64}}
                ]}
            ]

            # Выполняем запрос
            response = openai.chat.completions.create(
                model=MODEL_NAME,
                messages=messages
            )

            text = ""
            try:
                text = response.choices[0].message.content
            except Exception:
                try:
                    text = response.choices[0].text
                except Exception:
                    text = str(response)

            self.result_ready.emit(text)

            try:
                os.remove(fname)
            except Exception:
                pass

        except Exception as e:
            tb = traceback.format_exc()
            self.error.emit(f"{str(e)}\n\n{tb}")


class MiniPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.expanded = False
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Mini Test Solver")
        flags = QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool
        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.min_width = 80
        self.min_height = 200
        self.max_width = 400
        self.height = 200

        self.resize(self.min_width, self.min_height)

        self.bg = QtWidgets.QFrame(self)
        self.bg.setGeometry(0, 0, self.min_width, self.min_height)
        self.bg.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 20, 20, 220);
                border-radius: 10px;
            }
        """)

        self.btn_capture = QtWidgets.QPushButton("📸", self.bg)
        self.btn_capture.setGeometry(10, 10, 60, 40)
        self.btn_capture.setStyleSheet(self._btn_style())
        self.


btn_capture.clicked.connect(self.on_capture_clicked)

        self.btn_close = QtWidgets.QPushButton("✖", self.bg)
        self.btn_close.setGeometry(10, 150, 60, 40)
        self.btn_close.setStyleSheet(self._btn_style())
        self.btn_close.clicked.connect(self.close)

        self.text_area = QtWidgets.QTextEdit(self.bg)
        self.text_area.setGeometry(90, 10, self.max_width - 100, self.height - 20)
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet("""
            QTextEdit {
                background: transparent;
                color: #ff6b6b;
                border: none;
                font-family: Consolas, monospace;
                font-size: 12px;
            }
        """)
        self.text_area.hide()

        screen_geo = QtWidgets.QApplication.primaryScreen().availableGeometry()
        x = screen_geo.width() - (self.min_width + 20)
        y = 120
        self.move(x, y)

        self.old_pos = None

        self.loading = QtWidgets.QLabel(self.bg)
        self.loading.setGeometry(10, 60, 60, 20)
        self.loading.setText("")
        self.loading.setStyleSheet("color: #cccccc;")

        self.show()

    def _btn_style(self):
        return """
        QPushButton {
            background: #222;
            color: #ff6b6b;
            border: none;
            font-size: 16px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background: #2b2b2b;
            color: #ffffff;
        }
        """

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if not self.old_pos:
            return
        delta = event.globalPos() - self.old_pos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def toggle_expand(self):
        if self.expanded:
            self.resize(self.min_width, self.min_height)
            self.bg.resize(self.min_width, self.min_height)
            self.text_area.hide()
        else:
            self.resize(self.max_width, self.height)
            self.bg.resize(self.max_width, self.height)
            self.text_area.show()
        self.expanded = not self.expanded

    def on_capture_clicked(self):
        if self.worker and self.worker.isRunning():
            return

        self.loading.setText("⏳")
        self.btn_capture.setEnabled(False)
        self.worker = APICallThread()
        self.worker.result_ready.connect(self.on_result)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    @QtCore.pyqtSlot(str)
    def on_result(self, text: str):
        if not self.expanded:
            self.toggle_expand()
        self.text_area.append(text + "\n")
        self.loading.setText("")

    @QtCore.pyqtSlot(str)
    def on_error(self, err: str):
        if not self.expanded:
            self.toggle_expand()
        self.text_area.append("⚠ Ошибка:\n" + err + "\n")
        self.loading.setText("")

    def on_finished(self):
        self.btn_capture.setEnabled(True)


def request_api_key_dialog(app) -> str | None:
    """
    Показывает окно ввода API-ключа (парольное поле).
    Возвращает строку ключа или None, если пользователь отменил.
    """
    # QInputDialog требует QApplication уже созданного
    dlg = QtWidgets.QInputDialog()
    dlg.setWindowTitle("OpenAI API Key")
    dlg.setLabelText("Введи OpenAI API-ключ (каждый запуск):")
    dlg.setTextEchoMode(QtWidgets.QLineEdit.Password)
    ok = dlg.exec_()
    if ok:
        key = dlg.textValue().strip()
        if key:
            return key
    return None


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

    # Запрашиваем ключ у пользователя при запуске
    key = request_api_key_dialog(app)
    if not key:
        QtWidgets.QMessageBox.

warning(None, "No key", "API-ключ не введён. Приложение закроется.")
        sys.exit(0)

    if openai is None:
        QtWidgets.QMessageBox.critical(None, "Missing package", "Пакет openai не установлен. Установи через: pip install openai")
        sys.exit(1)

    # Устанавливаем ключ для openai
    openai.api_key = key

    panel = MiniPanel()
    sys.exit(app.exec_())


if name == "__main__":
    main()