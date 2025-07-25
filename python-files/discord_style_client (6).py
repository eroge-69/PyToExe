import sys
import json
import ssl
import threading
import base64
from io import BytesIO

import websocket
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QListWidget, QStackedWidget,
    QDialog, QFormLayout, QFileDialog, QInputDialog
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

SERVER_URL = "wss://46.247.108.38:6187"

class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Настройки профиля")
        self.setFixedSize(300, 250)
        layout = QVBoxLayout(self)
        form = QFormLayout()

        btn_avatar = QPushButton("Изменить аватар")
        btn_avatar.clicked.connect(parent.choose_avatar)
        form.addRow("Аватар:", btn_avatar)

        btn_nick = QPushButton("Сменить ник")
        btn_nick.clicked.connect(parent.change_nickname)
        form.addRow("Никнейм:", btn_nick)

        btn_pass = QPushButton("Сменить пароль")
        btn_pass.clicked.connect(parent.change_password)
        form.addRow("Пароль:", btn_pass)

        btn_theme = QPushButton("Переключить тему")
        btn_theme.clicked.connect(parent.toggle_theme)
        form.addRow("Тема:", btn_theme)

        layout.addLayout(form)

class DiscordClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Discord-клиент")
        self.resize(800, 600)
        self.username = ""
        self.avatar = ""
        self.theme = 'dark'
        self.friends = []
        self.current_chat = 'All'

        self.ws_app = None
        self.image_cache = {}

        # Стек страниц
        self.stack = QStackedWidget()
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stack)

        # Инициализация страниц
        self._init_login_page()
        self._init_chat_page()

        # Показываем страницу входа
        self.stack.setCurrentWidget(self.login_page)

        # Подключаем WebSocket
        self._connect_ws()

        self.apply_theme()

    def apply_theme(self):
        if self.theme == 'dark':
            bg = '#2f3136'; fg = 'white'
        else:
            bg = 'white'; fg = 'black'
        self.setStyleSheet(f"background-color: {bg}; color: {fg};")

    def toggle_theme(self):
        self.theme = 'light' if self.theme=='dark' else 'dark'
        self.apply_theme()

    def _init_login_page(self):
        self.login_page = QWidget()
        layout = QVBoxLayout(self.login_page)

        title = QLabel("Вход в Discord")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Имя пользователя")
        layout.addWidget(self.login_username)

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Пароль")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.login_password)

        btn_layout = QHBoxLayout()
        login_btn = QPushButton("Войти")
        reg_btn   = QPushButton("Регистрация")
        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(reg_btn)
        layout.addLayout(btn_layout)

        self.login_status = QLabel("")
        self.login_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.login_status)

        login_btn.clicked.connect(self._on_login)
        reg_btn.clicked.connect(self._on_register)

        self.stack.addWidget(self.login_page)

    def _init_chat_page(self):
        self.chat_page = QWidget()
        main_layout = QVBoxLayout(self.chat_page)

        content_layout = QHBoxLayout()

        # Список друзей
        left_panel = QVBoxLayout()
        self.friends_list = QListWidget()
        self.friends_list.addItem("All")
        self.friends_list.addItem("У вас пока нет друзей")
        self.friends_list.currentTextChanged.connect(self.change_chat_context)
        left_panel.addWidget(QLabel("Чаты"))
        left_panel.addWidget(self.friends_list)
        btn_add = QPushButton("Добавить друга")
        btn_add.clicked.connect(self.add_friend)
        left_panel.addWidget(btn_add)
        content_layout.addLayout(left_panel)

        # Область чата
        chat_layout = QVBoxLayout()
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        chat_layout.addWidget(self.chat_history)

        input_layout = QHBoxLayout()
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Введите сообщение...")
        send_btn = QPushButton("Отправить")
        send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(self.msg_input)
        input_layout.addWidget(send_btn)
        chat_layout.addLayout(input_layout)

        content_layout.addLayout(chat_layout)
        main_layout.addLayout(content_layout)

        # Кнопка настроек и выход
        bottom_layout = QHBoxLayout()
        btn_settings = QPushButton("Настройки")
        btn_settings.clicked.connect(self.show_settings)
        btn_logout = QPushButton("Выйти")
        btn_logout.clicked.connect(lambda: self.stack.setCurrentWidget(self.login_page))
        bottom_layout.addWidget(btn_settings)
        bottom_layout.addWidget(btn_logout)
        main_layout.addLayout(bottom_layout)

        self.stack.addWidget(self.chat_page)

    def change_chat_context(self, text):
        self.current_chat = text
        self.chat_history.clear()

    def add_friend(self):
        new, ok = QInputDialog.getText(self, "Добавить друга", "Ник друга:")
        if ok and new:
            self.friends.append(new)
            self.friends_list.addItem(new)

    def _connect_ws(self):
        def on_message(ws, message):
            try:
                data = json.loads(message)
            except:
                return
            t = data.get("type")
            # Private messaging
            if t == 'private_message':
                frm = data.get('from')
                msg = data.get('message')
                if self.current_chat == frm:
                    self.chat_history.append(f"(ЛС) {frm}: {msg}")
                return
            if t in ("logged_in", "registered"):
                self.login_status.setText("")
                self.stack.setCurrentWidget(self.chat_page)
                return
            if t == "message" and self.current_chat == 'All':
                user, txt = data.get("username"), data.get("message")
                self.chat_history.append(f"{user}: {txt}")
            if data.get("error"):
                self.login_status.setText(f"❌ {data['error']}")

        def on_open(ws): print("✅ Подключено")
        def on_error(ws, err): print("❌ Ошибка:", err)
        def on_close(ws): print("🔒 Закрыто")

        self.ws_app = websocket.WebSocketApp(
            SERVER_URL,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        thread = threading.Thread(
            target=lambda: self.ws_app.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}),
            daemon=True
        )
        thread.start()

    def _on_login(self):
        uname = self.login_username.text().strip()
        pwd   = self.login_password.text().strip()
        if not uname or not pwd:
            self.login_status.setText("Введите имя и пароль")
            return
        self.username = uname
        self.ws_app.send(json.dumps({"type":"login","username":uname,"password":pwd}))

    def _on_register(self):
        uname = self.login_username.text().strip()
        pwd   = self.login_password.text().strip()
        if not uname or not pwd:
            self.login_status.setText("Введите имя и пароль")
            return
        self.username = uname
        self.ws_app.send(json.dumps({
            "type": "register",
            "username": uname,
            "password": pwd,
            "avatar": self.avatar
        }))

    def _send_message(self):
        msg = self.msg_input.text().strip()
        if not msg: return
        if self.current_chat == 'All':
            payload={"type":"message","username":self.username,"message":msg}
        else:
            payload={"type":"private_message","from":self.username,"to":self.current_chat,"message":msg}
        self.ws_app.send(json.dumps(payload))
        if self.current_chat != 'All':
            self.chat_history.append(f"(Вы → {self.current_chat}): {msg}")
        else:
            self.chat_history.append(f"{self.username}: {msg}")
        self.msg_input.clear()

    def choose_avatar(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выбрать аватар", filter="Images (*.png *.jpg)")
        if path:
            with open(path, "rb") as f:
                self.avatar = base64.b64encode(f.read()).decode()

    def change_nickname(self):
        new, ok = QInputDialog.getText(self, "Сменить ник", "Новый ник:")
        if ok and new:
            self.username = new

    def change_password(self):
        new, ok = QInputDialog.getText(self, "Сменить пароль", "Новый пароль:", QLineEdit.EchoMode.Password)
        if ok and new:
            self.ws_app.send(json.dumps({"type":"change_password","username":self.username,"new_password":new}))

    def show_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = DiscordClient()
    client.show()
    sys.exit(app.exec())
