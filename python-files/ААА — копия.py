import sys, random, string, json, os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer

# sounddevice проверка
try:
    import sounddevice as sd
    import soundfile as sf
    SOUND_OK = True
except ImportError:
    SOUND_OK = False

LOG_FILE = "logs.json"
SUPPORT_FILE = "support_logs.json"

def load_logs(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_logs(file_path, logs):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

# Окно настроек
class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setStyleSheet("background-color:#2c2f33;color:white;")
        self.setGeometry(300, 200, 400, 300)
        layout = QVBoxLayout()

        # Ник
        self.nick_input = QLineEdit(parent.nickname.text())
        self.nick_input.setPlaceholderText("Введите новый ник")
        self.nick_btn = QPushButton("Сменить ник")
        self.nick_btn.clicked.connect(lambda: self.change_nick(parent))
        layout.addWidget(QLabel("Изменить ник:"))
        layout.addWidget(self.nick_input)
        layout.addWidget(self.nick_btn)

        # Микрофон
        self.mic_btn = QPushButton("Выбрать/Тест микрофона")
        self.mic_btn.clicked.connect(parent.test_mic)
        layout.addWidget(self.mic_btn)

        # Тема
        self.theme_btn = QPushButton("Сменить тему (светлая/тёмная)")
        self.theme_btn.clicked.connect(parent.toggle_theme)
        layout.addWidget(self.theme_btn)

        # Уведомления (заглушка)
        self.notify_btn = QPushButton("Настройки уведомлений (заглушка)")
        layout.addWidget(self.notify_btn)

        self.setLayout(layout)

    def change_nick(self, parent):
        new_nick = self.nick_input.text().strip()
        if new_nick:
            parent.nickname.setText(new_nick)
            QMessageBox.information(self, "Ник", f"Ник изменен на: {new_nick}")

# Основной Messenger
class Messenger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Messenger v5")
        self.setGeometry(150,150,950,600)
        self.setStyleSheet("background-color:#2c2f33;color:white;")
        self.logs = load_logs(LOG_FILE)
        self.current_room = None
        self.current_contact = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Контакты
        self.contacts = QListWidget()
        self.contacts.addItem("AI Bot")
        self.contacts.itemClicked.connect(self.select_contact)

        # Правая панель
        right_panel = QVBoxLayout()
        top_panel = QHBoxLayout()

        self.avatar = QLabel("😀")
        self.nickname = QLabel("Ваш ник")
        self.search_btn = QPushButton("Поиск")
        self.settings_btn = QPushButton("Настройки")
        self.call_btn = QPushButton("📞")
        self.room_create_btn = QPushButton("Создать комнату")
        self.room_join_btn = QPushButton("Войти по коду")
        self.support_btn = QPushButton("Поддержка")

        for b in [self.search_btn,self.settings_btn,self.call_btn,self.room_create_btn,self.room_join_btn,self.support_btn]:
            b.setStyleSheet("background-color:#7289da;color:white;border-radius:5px;padding:5px;")

        self.search_btn.clicked.connect(self.search_contact)
        self.settings_btn.clicked.connect(self.open_settings)
        self.call_btn.clicked.connect(self.call_user)
        self.room_create_btn.clicked.connect(self.create_room)
        self.room_join_btn.clicked.connect(self.join_room)
        self.support_btn.clicked.connect(self.open_support)

        top_panel.addWidget(self.avatar)
        top_panel.addWidget(self.nickname)
        top_panel.addStretch()
        for b in [self.search_btn,self.settings_btn,self.call_btn,self.room_create_btn,self.room_join_btn,self.support_btn]:
            top_panel.addWidget(b)

        # Чат
        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)

        # Ввод сообщения
        bottom_panel = QHBoxLayout()
        self.msg_input = QLineEdit()
        self.send_btn = QPushButton("Отправить")
        self.send_btn.clicked.connect(self.send_message)
        bottom_panel.addWidget(self.msg_input)
        bottom_panel.addWidget(self.send_btn)

        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.contacts)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addLayout(top_panel)
        right_layout.addWidget(self.chat_box)
        right_layout.addLayout(bottom_panel)
        splitter.addWidget(right_widget)
        splitter.setSizes([200,700])
        layout.addWidget(splitter)

        # VPN
        self.vpn_checkbox = QCheckBox("Radmin VPN подключён")
        right_layout.addWidget(self.vpn_checkbox)

    def select_contact(self, item):
        self.current_contact = item.text()
        self.chat_box.append(f"<p style='color:#a3e3a3;'>Вы выбрали контакт: {self.current_contact}</p>")

    def send_message(self):
        if not self.current_contact:
            QMessageBox.warning(self,"Ошибка","Выберите контакт")
            return
        text = self.msg_input.text().strip()
        if text:
            self.chat_box.append(f"<p style='color:#7289da;text-align:right;'>Вы -> {self.current_contact}: {text}</p>")
            self.msg_input.clear()
            self.logs.setdefault("messages",[]).append({"to":self.current_contact,"text":text})
            save_logs(LOG_FILE,self.logs)

    def call_user(self):
        if not self.current_contact:
            QMessageBox.warning(self,"Ошибка","Выберите контакт")
            return
        QMessageBox.information(self,"Звонок",f"Вы звоните {self.current_contact}")

    def create_room(self):
        if not self.vpn_checkbox.isChecked():
            QMessageBox.warning(self,"VPN","Включите Radmin VPN")
            return
        code = ''.join(random.choices(string.ascii_uppercase+string.digits,k=6))
        self.current_room = code
        QMessageBox.information(self,"Комната",f"Комната создана. Код: {code}")
        self.logs.setdefault("rooms",[]).append({"created":code})
        save_logs(LOG_FILE,self.logs)

    def join_room(self):
        if not self.vpn_checkbox.isChecked():
            QMessageBox.warning(self,"VPN","Включите Radmin VPN")
            return
        code, ok = QInputDialog.getText(self,"Войти в комнату","Введите код комнаты")
        if ok and code:
            self.current_room = code
            QMessageBox.information(self,"Комната",f"Вы вошли в комнату {code}")
            self.logs.setdefault("rooms",[]).append({"joined":code})
            save_logs(LOG_FILE,self.logs)

    def search_contact(self):
        QMessageBox.information(self,"Поиск","Поиск контактов пока заглушка")

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec_()

    def toggle_theme(self):
        if self.styleSheet().find("#2c2f33")>=0:
            self.setStyleSheet("background-color:white;color:black;")
        else:
            self.setStyleSheet("background-color:#2c2f33;color:white;")

    def test_mic(self):
        if not SOUND_OK:
            QMessageBox.information(self,"Микрофон","Библиотека sounddevice не установлена.\nУстановите: pip install sounddevice numpy")
            return
        try:
            devices = sd.query_devices()
            QMessageBox.information(self,"Микрофон",f"Найдено устройств: {len(devices)}")
        except Exception as e:
            QMessageBox.warning(self,"Ошибка микрофона",str(e))

    def open_support(self):
        dlg = SupportDialog(self)
        dlg.exec_()

# Чат поддержки
class SupportDialog(QDialog):
    def __init__(self,parent):
        super().__init__(parent)
        self.setWindowTitle("Поддержка")
        self.setGeometry(400,200,400,400)
        self.setStyleSheet("background-color:#2c2f33;color:white;")
        layout = QVBoxLayout()
        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        self.input_box = QLineEdit()
        self.send_btn = QPushButton("Отправить")
        self.send_btn.clicked.connect(self.send_message)
        layout.addWidget(self.chat_box)
        hl = QHBoxLayout()
        hl.addWidget(self.input_box)
        hl.addWidget(self.send_btn)
        layout.addLayout(hl)
        self.setLayout(layout)
        self.logs = load_logs(SUPPORT_FILE)

    def send_message(self):
        text = self.input_box.text().strip()
        if text:
            self.chat_box.append(f"Support: {text}")
            self.logs.setdefault("messages",[]).append({"from":"Support","text":text})
            save_logs(SUPPORT_FILE,self.logs)
            self.input_box.clear()

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = Messenger()
    window.show()
    sys.exit(app.exec_())
