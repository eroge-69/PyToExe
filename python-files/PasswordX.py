import os
import shutil
import json
import base64
import hashlib
import datetime
import random
import time
import string
import sys
import socket
import threading
from PySide6.QtCore import QObject
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
from PySide6.QtCore import Qt, QSize, QTimer, QCoreApplication, QLibraryInfo, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QStackedWidget,
    QMessageBox, QInputDialog, QFormLayout, QGroupBox, QCheckBox,
    QDialog, QFrame, QSizePolicy, QTextEdit, QTextBrowser
)
from PySide6.QtGui import QFont, QIcon, QColor


# Конфигурация системы
VAULTS_DIR = "vaults"
MAX_ATTEMPTS = 3
LOCK_TIME = 300
MIN_PASSWORD_LENGTH = 15
PIN_LENGTH = 4
MESSENGER_PORT = 9999


class SecurityCheck:
    @staticmethod
    def verify_integrity():
        return True

    @staticmethod
    def check_time_access():
        now = datetime.datetime.now().time()
        start_time = datetime.time(7, 0)
        end_time = datetime.time(23, 0)
        return start_time <= now <= end_time


class PasswordGeneratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Генератор паролей")
        self.setFixedSize(400, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QLabel {
                font-size: 12px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLineEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                padding: 5px;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        layout = QVBoxLayout()
        self.length_label = QLabel("Длина пароля (12-50):")
        self.length_input = QLineEdit("20")
        options_group = QGroupBox("Типы символов")
        options_layout = QVBoxLayout()
        self.upper_check = QCheckBox("Заглавные буквы (A-Z)")
        self.upper_check.setChecked(True)
        self.lower_check = QCheckBox("Строчные буквы (a-z)")
        self.lower_check.setChecked(True)
        self.digits_check = QCheckBox("Цифры (0-9)")
        self.digits_check.setChecked(True)
        self.symbols_check = QCheckBox("Спецсимволы (!@#$%)")
        self.symbols_check.setChecked(True)
        self.rus_check = QCheckBox("Русские буквы")
        options_layout.addWidget(self.upper_check)
        options_layout.addWidget(self.lower_check)
        options_layout.addWidget(self.digits_check)
        options_layout.addWidget(self.symbols_check)
        options_layout.addWidget(self.rus_check)
        options_group.setLayout(options_layout)
        self.password_label = QLabel("Сгенерированный пароль:")
        self.password_output = QLineEdit()
        self.password_output.setReadOnly(True)
        self.generate_btn = QPushButton("Сгенерировать")
        self.generate_btn.clicked.connect(self.generate_password)
        self.copy_btn = QPushButton("Копировать в буфер")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.accept)
        layout.addWidget(self.length_label)
        layout.addWidget(self.length_input)
        layout.addWidget(options_group)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_output)
        layout.addWidget(self.generate_btn)
        layout.addWidget(self.copy_btn)
        layout.addWidget(self.close_btn)
        self.setLayout(layout)
        self.generate_password()

    def generate_password(self):
        try:
            length = int(self.length_input.text())
            length = max(12, min(50, length))
            chars = ""
            if self.upper_check.isChecked(): chars += string.ascii_uppercase
            if self.lower_check.isChecked(): chars += string.ascii_lowercase
            if self.digits_check.isChecked(): chars += string.digits
            if self.symbols_check.isChecked(): chars += "!@#$%^&*()_+-=[]{}|;:,.<>?~"
            if self.rus_check.isChecked(): chars += "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
            if not chars:
                self.password_output.setText("Выберите хотя бы один тип символов!")
                return
            password = ''.join(random.choice(chars) for _ in range(length))
            password_list = list(password)
            random.shuffle(password_list)
            password = ''.join(password_list)
            self.password_output.setText(password)
        except Exception as e:
            self.password_output.setText("Ошибка генерации пароля")

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.password_output.text())
        QMessageBox.information(self, "Скопировано", "Пароль скопирован в буфер обмена!")


class LocalMessenger(QObject):
    message_received = Signal(str)

    def __init__(self, host='127.0.0.1', port=9999):
        super().__init__()
        self.host = host
        self.port = port
        self.running = False
        self.sock = None
        self.clients = []

    def start_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.running = True
        threading.Thread(target=self.accept_connections, daemon=True).start()

    def accept_connections(self):
        while self.running:
            client, addr = self.sock.accept()
            self.clients.append(client)
            threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()

    def handle_client(self, client):
        while self.running:
            try:
                msg = client.recv(1024)
                if not msg:
                    break
                self.message_received.emit(msg.decode())
            except:
                break
        client.close()

    def send_message(self, message, target_ip=None):
        if not target_ip:
            for client in self.clients:
                client.sendall(message.encode())
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((target_ip, self.port))
                sock.sendall(message.encode())
            finally:
                sock.close()


class PasswordVaultApp(QMainWindow):
    def __init__(self):
        super().__init__()
        plugins_path = QLibraryInfo.location(QLibraryInfo.PluginsPath)
        if plugins_path:
            os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugins_path

        if not SecurityCheck.verify_integrity():
            QMessageBox.critical(None, "Ошибка безопасности", 
                                "Обнаружена модификация программы! Приложение будет закрыто.")
            sys.exit(1)

        self.setWindowTitle("UltraSecure Vault 2.0")
        self.setGeometry(100, 100, 900, 650)
        self.setMinimumSize(800, 600)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1f2d;
            }
            QWidget {
                background-color: #1a1f2d;
                color: #ecf0f1;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
            QPushButton#danger {
                background-color: #e74c3c;
            }
            QPushButton#danger:hover {
                background-color: #c0392b;
            }
            QLineEdit, QListWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 14px;
            }
            QLabel#title {
                font-size: 24px;
                font-weight: bold;
                color: #3498db;
            }
            QLabel#subtitle {
                font-size: 16px;
                color: #bdc3c7;
            }
            QGroupBox {
                border: 1px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                font-size: 16px;
                color: #3498db;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #34495e;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QStackedWidget {
                background-color: #1a1f2d;
                border: none;
            }
        """)

        self.key = None
        self.salt = None
        self.entries = []
        self.notes = []
        self.user_id = None
        self.attempts = 0
        self.vault_path = None

        os.makedirs(VAULTS_DIR, exist_ok=True)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        title_label = QLabel("ULTRA SECURE VAULT")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        subtitle_label = QLabel("Военное шифрование для ваших паролей")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)

        self.main_layout.addWidget(title_label)
        self.main_layout.addWidget(subtitle_label)

        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        self.create_welcome_screen()
        self.create_login_screen()
        self.create_register_screen()
        self.create_main_screen()
        self.create_entry_form()
        self.create_notes_screen()
        self.create_messenger_screen()
        self.create_note_form()

        self.messenger = LocalMessenger()
        self.messenger.message_received.connect(self.handle_incoming_message)
        self.messenger.start_server()

        self.stacked_widget.setCurrentIndex(0)

    def create_notes_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        title_label = QLabel("МОИ ЗАМЕТКИ")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)

        self.notes_list = QListWidget()
        self.notes_list.setMinimumHeight(300)
        self.notes_list.itemDoubleClicked.connect(self.edit_note)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить заметку")
        add_btn.clicked.connect(self.show_note_form)
        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_selected_note)
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_selected_note)
        back_btn = QPushButton("Назад")
        back_btn.clicked.connect(self.show_main_screen)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(back_btn)

        layout.addWidget(title_label)
        layout.addWidget(self.notes_list)
        layout.addLayout(btn_layout)

        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)

    def create_messenger_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        title_label = QLabel("ЛОКАЛЬНЫЙ МЕССЕНДЖЕР")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)

        self.chat_log = QTextBrowser()
        self.chat_log.setOpenExternalLinks(False)
        self.chat_log.setReadOnly(True)
        self.chat_log.setMinimumHeight(300)

        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)

        input_layout = QHBoxLayout()
        ip_input = QLineEdit("127.0.0.1")
        send_btn = QPushButton("Отправить")
        send_btn.clicked.connect(lambda: self.messenger.send_message(
            f"[{self.user_id}] {self.message_input.toPlainText()}",
            ip_input.text()
        ))

        input_layout.addWidget(ip_input)
        input_layout.addWidget(send_btn)

        back_btn = QPushButton("Назад")
        back_btn.clicked.connect(self.show_main_screen)

        layout.addWidget(title_label)
        layout.addWidget(self.chat_log)
        layout.addWidget(self.message_input)
        layout.addLayout(input_layout)
        layout.addWidget(back_btn)

        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)

    def handle_incoming_message(self, message):
        self.chat_log.append(message)

    def show_messenger(self):
        self.chat_log.clear()
        self.stacked_widget.setCurrentIndex(5)

    def show_notes(self):
        self.update_notes_list()
        self.stacked_widget.setCurrentIndex(4)

    def update_notes_list(self):
        self.notes_list.clear()
        for i, note in enumerate(self.notes, 1):
            item_text = f"{i}. {note['title']}"
            self.notes_list.addItem(item_text)

    def edit_note(self, item):
        index = self.notes_list.row(item)
        if 0 <= index < len(self.notes):
            self.show_note_form(self.notes[index])

    def edit_selected_note(self):
        selected_items = self.notes_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите заметку для редактирования!")
            return
        index = self.notes_list.row(selected_items[0])
        if 0 <= index < len(self.notes):
            self.show_note_form(self.notes[index])

    def delete_selected_note(self):
        selected_items = self.notes_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите заметку для удаления!")
            return
        index = self.notes_list.row(selected_items[0])
        if 0 <= index < len(self.notes):
            reply = QMessageBox.question(self, "Подтверждение", 
                                        "Вы уверены, что хотите удалить эту заметку?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                del self.notes[index]
                self.save_vault()
                self.update_notes_list()

    def save_note(self):
        title = self.note_title_input.text().strip()
        content = self.note_content_input.toPlainText()
        if not title or not content:
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны для заполнения!")
            return

        if self.current_note_index is not None:
            entry = self.notes[self.current_note_index]
            entry['title'] = title
            entry['content'] = content
            entry['last_modified'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        else:
            self.notes.append({
                'title': title,
                'content': content,
                'created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                'last_modified': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
        self.save_vault()
        self.show_notes()

    def show_note_form(self, note=None):
        self.note_title_input.clear()
        self.note_content_input.clear()
        if note:
            self.note_title_input.setText(note.get('title', ''))
            self.note_content_input.setText(note.get('content', ''))
            self.current_note_index = self.notes.index(note)
            self.note_title.setText("РЕДАКТИРОВАНИЕ ЗАМЕТКИ")
        else:
            self.note_title.setText("НОВАЯ ЗАМЕТКА")
            self.current_note_index = None
        self.stacked_widget.setCurrentIndex(6)

    def create_note_form(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        self.note_title = QLabel("НОВАЯ ЗАМЕТКА")
        self.note_title.setObjectName("title")
        self.note_title.setAlignment(Qt.AlignCenter)

        form_group = QGroupBox("Содержание заметки")
        form_layout = QFormLayout()
        self.note_title_input = QLineEdit()
        self.note_title_input.setPlaceholderText("Заголовок заметки")
        self.note_content_input = QTextEdit()
        self.note_content_input.setMinimumHeight(200)
        form_layout.addRow("Заголовок:", self.note_title_input)
        form_layout.addRow("Текст:", self.note_content_input)
        form_group.setLayout(form_layout)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_note)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.show_notes)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)

        layout.addWidget(self.note_title)
        layout.addWidget(form_group)
        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)

    def save_vault(self):
        if not self.user_id or not self.vault_path:
            return
        try:
            data_str = json.dumps({
                "passwords": self.entries,
                "notes": self.notes
            })
            cipher = AES.new(self.key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(data_str.encode('utf-8'))
            encrypted_data = cipher.nonce + tag + ciphertext
            with open(os.path.join(self.vault_path, "vault.dat"), 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить данные: {str(e)}")

    def create_welcome_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setPixmap(QIcon.fromTheme("security-high").pixmap(120, 120))
        desc_label = QLabel("""
            <center>
            <p>Самый защищенный менеджер паролей в мире</p>
            <p>Ваши данные защищены военным шифрованием AES-256</p>
            <p>и никогда не покидают ваше устройство</p>
            </center>
        """)
        desc_label.setObjectName("subtitle")
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        login_btn = QPushButton("Вход в систему")
        login_btn.setMinimumHeight(50)
        login_btn.clicked.connect(self.show_login)
        register_btn = QPushButton("Регистрация")
        register_btn.setMinimumHeight(50)
        register_btn.clicked.connect(self.show_register)
        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(register_btn)
        layout.addWidget(icon_label)
        layout.addWidget(desc_label)
        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)

    def create_login_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        title_label = QLabel("АВТОРИЗАЦИЯ В СИСТЕМЕ")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        form_group = QGroupBox("Введите ваши данные")
        form_layout = QFormLayout()
        self.login_id_input = QLineEdit()
        self.login_id_input.setPlaceholderText("Ваш уникальный ID")
        self.login_password_input = QLineEdit()
        self.login_password_input.setPlaceholderText("Мастер-пароль")
        self.login_password_input.setEchoMode(QLineEdit.Password)
        self.login_pin_input = QLineEdit()
        self.login_pin_input.setPlaceholderText("PIN-код")
        self.login_pin_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("ID:", self.login_id_input)
        form_layout.addRow("Мастер-пароль:", self.login_password_input)
        form_layout.addRow("PIN-код:", self.login_pin_input)
        form_group.setLayout(form_layout)
        captcha_group = QGroupBox("Подтверждение безопасности")
        captcha_layout = QVBoxLayout()
        self.captcha_label = QLabel("Решите пример:")
        self.captcha_example = QLabel("")
        self.captcha_example.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.captcha_input = QLineEdit()
        self.captcha_input.setPlaceholderText("Ответ")
        captcha_layout.addWidget(self.captcha_label)
        captcha_layout.addWidget(self.captcha_example)
        captcha_layout.addWidget(self.captcha_input)
        captcha_group.setLayout(captcha_layout)
        btn_layout = QHBoxLayout()
        login_btn = QPushButton("Войти")
        login_btn.setMinimumHeight(45)
        login_btn.clicked.connect(self.perform_login)
        back_btn = QPushButton("Назад")
        back_btn.setMinimumHeight(45)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        btn_layout.addWidget(back_btn)
        btn_layout.addWidget(login_btn)
        self.login_status = QLabel("")
        self.login_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.login_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addWidget(form_group)
        layout.addWidget(captcha_group)
        layout.addWidget(self.login_status)
        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)
        self.generate_captcha()

    def create_register_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        title_label = QLabel("РЕГИСТРАЦИЯ НОВОГО ПОЛЬЗОВАТЕЛЯ")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        form_group = QGroupBox("Создайте учетную запись")
        form_layout = QFormLayout()
        self.register_id_input = QLineEdit()
        self.register_id_input.setPlaceholderText("Придумайте уникальный ID")
        self.register_password_input = QLineEdit()
        self.register_password_input.setPlaceholderText("Мастер-пароль (мин. 15 символов)")
        self.register_password_input.setEchoMode(QLineEdit.Password)
        self.register_confirm_input = QLineEdit()
        self.register_confirm_input.setPlaceholderText("Подтвердите мастер-пароль")
        self.register_confirm_input.setEchoMode(QLineEdit.Password)
        self.register_pin_input = QLineEdit()
        self.register_pin_input.setPlaceholderText("4-значный PIN-код")
        self.register_pin_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("ID:", self.register_id_input)
        form_layout.addRow("Мастер-пароль:", self.register_password_input)
        form_layout.addRow("Подтверждение:", self.register_confirm_input)
        form_layout.addRow("PIN-код:", self.register_pin_input)
        form_group.setLayout(form_layout)
        btn_layout = QHBoxLayout()
        register_btn = QPushButton("Зарегистрироваться")
        register_btn.setMinimumHeight(45)
        register_btn.clicked.connect(self.perform_register)
        back_btn = QPushButton("Назад")
        back_btn.setMinimumHeight(45)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        btn_layout.addWidget(back_btn)
        btn_layout.addWidget(register_btn)
        self.register_status = QLabel("")
        self.register_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.register_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addWidget(form_group)
        layout.addWidget(self.register_status)
        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)

    def create_main_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        self.main_title = QLabel("ДОБРО ПОЖАЛОВАТЬ")
        self.main_title.setObjectName("title")
        self.main_title.setAlignment(Qt.AlignCenter)
        user_info = QLabel(f"Пользователь: {self.user_id} | Записей: 0")
        user_info.setObjectName("subtitle")
        user_info.setAlignment(Qt.AlignCenter)
        self.entries_list = QListWidget()
        self.entries_list.setMinimumHeight(300)
        self.entries_list.itemDoubleClicked.connect(self.edit_entry)
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить запись")
        add_btn.clicked.connect(self.show_entry_form)
        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.edit_selected_entry)
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_selected_entry)
        generate_btn = QPushButton("Генератор паролей")
        generate_btn.clicked.connect(self.show_password_generator)
        messenger_btn = QPushButton("Мессенджер")
        messenger_btn.clicked.connect(self.show_messenger)
        logout_btn = QPushButton("Выход")
        logout_btn.clicked.connect(self.logout)
        emergency_btn = QPushButton("Экстренное удаление")
        emergency_btn.setObjectName("danger")
        emergency_btn.clicked.connect(self.emergency_wipe)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(generate_btn)
        btn_layout.addWidget(messenger_btn)
        btn_layout.addWidget(logout_btn)
        btn_layout.addWidget(emergency_btn)
        layout.addWidget(self.main_title)
        layout.addWidget(user_info)
        layout.addWidget(self.entries_list)
        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)

    def create_entry_form(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        self.entry_title = QLabel("НОВАЯ ЗАПИСЬ")
        self.entry_title.setObjectName("title")
        self.entry_title.setAlignment(Qt.AlignCenter)
        form_group = QGroupBox("Детали записи")
        form_layout = QFormLayout()
        self.entry_service_input = QLineEdit()
        self.entry_service_input.setPlaceholderText("Название сервиса/сайта")
        self.entry_username_input = QLineEdit()
        self.entry_username_input.setPlaceholderText("Логин/Email")
        self.entry_password_input = QLineEdit()
        self.entry_password_input.setPlaceholderText("Пароль")
        self.entry_password_input.setEchoMode(QLineEdit.Password)
        self.show_password_check = QCheckBox("Показать пароль")
        self.show_password_check.stateChanged.connect(self.toggle_password_visibility)
        self.generate_password_btn = QPushButton("Сгенерировать пароль")
        self.generate_password_btn.clicked.connect(self.show_password_generator)
        form_layout.addRow("Сервис:", self.entry_service_input)
        form_layout.addRow("Логин:", self.entry_username_input)
        form_layout.addRow("Пароль:", self.entry_password_input)
        form_layout.addRow("", self.show_password_check)
        form_layout.addRow("", self.generate_password_btn)
        form_group.setLayout(form_layout)
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_entry)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.show_main_screen)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addWidget(self.entry_title)
        layout.addWidget(form_group)
        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)

    def toggle_password_visibility(self):
        if self.show_password_check.isChecked():
            self.entry_password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.entry_password_input.setEchoMode(QLineEdit.Password)

    def show_welcome(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_login(self):
        self.login_id_input.clear()
        self.login_password_input.clear()
        self.login_pin_input.clear()
        self.login_status.clear()
        self.generate_captcha()
        self.stacked_widget.setCurrentIndex(1)

    def show_register(self):
        self.register_id_input.clear()
        self.register_password_input.clear()
        self.register_confirm_input.clear()
        self.register_pin_input.clear()
        self.register_status.clear()
        self.stacked_widget.setCurrentIndex(2)

    def show_main_screen(self):
        self.update_entries_list()
        self.stacked_widget.setCurrentIndex(3)

    def show_entry_form(self, entry=None):
        self.entry_service_input.clear()
        self.entry_username_input.clear()
        self.entry_password_input.clear()
        self.show_password_check.setChecked(False)
        self.entry_password_input.setEchoMode(QLineEdit.Password)
        if entry:
            self.entry_title.setText("РЕДАКТИРОВАНИЕ ЗАПИСИ")
            self.entry_service_input.setText(entry.get('service', ''))
            self.entry_username_input.setText(entry.get('username', ''))
            self.entry_password_input.setText(entry.get('password', ''))
            self.current_entry_index = self.entries.index(entry)
        else:
            self.entry_title.setText("НОВАЯ ЗАПИСЬ")
            self.current_entry_index = None
        self.stacked_widget.setCurrentIndex(4)

    def show_password_generator(self):
        generator = PasswordGeneratorDialog(self)
        if generator.exec_() == QDialog.Accepted:
            generated_password = generator.password_output.text()
            if generated_password and len(generated_password) > 10:
                self.entry_password_input.setText(generated_password)

    def generate_captcha(self):
        a = random.randint(15, 60)
        b = random.randint(5, 25)
        c = random.randint(1, 10)
        ops = ['+', '-', '*']
        problem = f"({a} {random.choice(ops)} {b}) {random.choice(ops)} {c}"
        self.captcha_problem = problem
        self.captcha_answer = eval(problem)
        self.captcha_example.setText(problem)
        self.captcha_input.clear()

    def perform_login(self):
        user_id = self.login_id_input.text().strip()
        password = self.login_password_input.text()
        pin = self.login_pin_input.text()
        captcha_answer = self.captcha_input.text().strip()
        if not user_id or not password or not pin or not captcha_answer:
            self.login_status.setText("Все поля обязательны для заполнения!")
            return
        try:
            captcha_answer = int(captcha_answer)
        except:
            self.login_status.setText("Некорректный ответ на капчу!")
            self.generate_captcha()
            return
        if captcha_answer != self.captcha_answer:
            self.login_status.setText("Неверная капча! Попробуйте снова.")
            self.generate_captcha()
            self.attempts += 1
            return
        vault_path = os.path.join(VAULTS_DIR, f"{user_id}_vault")
        salt_file = os.path.join(vault_path, "salt.bin")
        vault_file = os.path.join(vault_path, "vault.dat")
        if not os.path.exists(salt_file) or not os.path.exists(vault_file):
            self.login_status.setText("Пользователь не найден!")
            self.attempts += 1
            return
        try:
            with open(salt_file, 'rb') as f:
                salt = f.read()
            key = scrypt(password, salt, key_len=32, N=2**20, r=8, p=1)
            with open(vault_file, 'rb') as f:
                encrypted = f.read()
            nonce, tag, ciphertext = encrypted[:16], encrypted[16:32], encrypted[32:]
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            data_str = cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
            entries = json.loads(data_str)
            if len(pin) != PIN_LENGTH:
                self.login_status.setText("Неверный PIN-код!")
                self.attempts += 1
                return
            security_question_file = os.path.join(vault_path, "security.json")
            if os.path.exists(security_question_file):
                with open(security_question_file, 'r') as f:
                    sec_data = json.load(f)
                answer, ok = QInputDialog.getText(self, "Контрольный вопрос", sec_data.get("question", ""))
                if not ok or not answer.strip():
                    self.login_status.setText("Требуется ответ на контрольный вопрос!")
                    return
                hashed_answer = hashlib.sha256(answer.encode()).hexdigest()
                if hashed_answer != sec_data.get("answer_hash"):
                    self.login_status.setText("Неверный ответ на контрольный вопрос!")
                    self.attempts += 1
                    return
            if pin == sec_data.get("emergency_pin"):
                self.emergency_wipe(user_id, vault_path)
                return
            now = datetime.datetime.now().time()
            start_time = datetime.time(7, 0)
            end_time = datetime.time(23, 0)
            if not (start_time <= now <= end_time):
                self.login_status.setText("Время входа ограничено (07:00–23:00)!")
                return
            self.user_id = user_id
            self.key = key
            self.salt = salt
            self.entries = entries.get("passwords", [])
            self.notes = entries.get("notes", [])
            self.vault_path = vault_path
            self.attempts = 0
            self.main_title.setText(f"ДОБРО ПОЖАЛОВАТЬ, {user_id}")
            self.show_main_screen()
        except Exception as e:
            self.login_status.setText("Неверный пароль или повреждены данные!")
            self.attempts += 1
            if self.attempts >= MAX_ATTEMPTS:
                self.emergency_wipe(user_id, vault_path)

    def perform_register(self):
        user_id = self.register_id_input.text().strip()
        password = self.register_password_input.text()
        confirm = self.register_confirm_input.text()
        pin = self.register_pin_input.text()
        if not user_id or not password or not confirm or not pin:
            self.register_status.setText("Все поля обязательны для заполнения!")
            return
        if len(password) < MIN_PASSWORD_LENGTH:
            self.register_status.setText(f"Пароль должен быть не менее {MIN_PASSWORD_LENGTH} символов!")
            return
        if password != confirm:
            self.register_status.setText("Пароли не совпадают!")
            return
        if len(pin) != PIN_LENGTH or not pin.isdigit():
            self.register_status.setText("PIN должен состоять из 4 цифр!")
            return
        vault_path = os.path.join(VAULTS_DIR, f"{user_id}_vault")
        if os.path.exists(vault_path):
            self.register_status.setText("Этот ID уже занят! Выберите другой.")
            return
        os.makedirs(vault_path, exist_ok=True)
        salt = get_random_bytes(32)
        key = scrypt(password, salt, key_len=32, N=2**20, r=8, p=1)
        with open(os.path.join(vault_path, "salt.bin"), 'wb') as f:
            f.write(salt)
        entries = []
        data_str = json.dumps(entries)
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data_str.encode('utf-8'))
        encrypted_data = cipher.nonce + tag + ciphertext
        with open(os.path.join(vault_path, "vault.dat"), 'wb') as f:
            f.write(encrypted_data)
        security_question, ok = QInputDialog.getText(self, "Контрольный вопрос", "Введите свой контрольный вопрос:")
        if not ok or not security_question.strip():
            self.register_status.setText("Требуется контрольный вопрос!")
            return
        security_answer, ok = QInputDialog.getText(self, "Ответ на вопрос", "Введите ответ на ваш вопрос:")
        if not ok or not security_answer.strip():
            self.register_status.setText("Требуется ответ на контрольный вопрос!")
            return
        hashed_answer = hashlib.sha256(security_answer.encode()).hexdigest()
        emergency_pin = pin[::-1]
        with open(os.path.join(vault_path, "security.json"), 'w') as f:
            json.dump({
                "question": security_question,
                "answer_hash": hashed_answer,
                "emergency_pin": emergency_pin
            }, f)
        self.user_id = user_id
        self.key = key
        self.salt = salt
        self.entries = entries
        self.vault_path = vault_path
        self.main_title.setText(f"ДОБРО ПОЖАЛОВАТЬ, {user_id}")
        self.show_main_screen()

    def update_entries_list(self):
        self.entries_list.clear()
        for i, entry in enumerate(self.entries, 1):
            item_text = f"{i}. {entry['service']} - {entry['username']}"
            self.entries_list.addItem(item_text)

    def save_vault(self):
        if not self.user_id or not self.vault_path:
            return
        try:
            data_str = json.dumps({
                "passwords": self.entries,
                "notes": self.notes
            })
            cipher = AES.new(self.key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(data_str.encode('utf-8'))
            encrypted_data = cipher.nonce + tag + ciphertext
            with open(os.path.join(self.vault_path, "vault.dat"), 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить данные: {str(e)}")

    def save_entry(self):
        service = self.entry_service_input.text().strip()
        username = self.entry_username_input.text().strip()
        password = self.entry_password_input.text()
        if not service or not username or not password:
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны для заполнения!")
            return
        if self.current_entry_index is not None:
            entry = self.entries[self.current_entry_index]
            entry['service'] = service
            entry['username'] = username
            entry['password'] = password
        else:
            self.entries.append({
                'service': service,
                'username': username,
                'password': password,
                'created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                'last_modified': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
        self.save_vault()
        self.show_main_screen()

    def edit_selected_entry(self):
        selected_items = self.entries_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования!")
            return
        index = self.entries_list.row(selected_items[0])
        if 0 <= index < len(self.entries):
            self.show_entry_form(self.entries[index])

    def delete_selected_entry(self):
        selected_items = self.entries_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления!")
            return
        index = self.entries_list.row(selected_items[0])
        if 0 <= index < len(self.entries):
            reply = QMessageBox.question(self, "Подтверждение", 
                                        "Вы уверены, что хотите удалить эту запись?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                del self.entries[index]
                self.save_vault()
                self.update_entries_list()

    def logout(self):
        self.user_id = None
        self.key = None
        self.salt = None
        self.entries = []
        self.notes = []
        self.vault_path = None
        self.show_welcome()

    def emergency_wipe(self, user_id=None, vault_path=None):
        user_id = user_id or self.user_id
        vault_path = vault_path or self.vault_path
        if not user_id or not vault_path:
            return
        confirm, ok = QInputDialog.getText(self, "Экстренное удаление",
                                          f"Введите ваш ID ({user_id}) для подтверждения:")
        if not ok or confirm != user_id:
            return
        countdown = 5
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("ЭКСТРЕННОЕ УДАЛЕНИЕ")
        msg_box.setText(f"<b>ВСЕ ДАННЫЕ ПОЛЬЗОВАТЕЛЯ '{user_id}' БУДУТ УДАЛЕНЫ!</b><br>"
                       "Это действие необратимо!")
        msg_box.setInformativeText(f"Удаление через: {countdown} сек.")
        msg_box.setStandardButtons(QMessageBox.Cancel)
        msg_box.setIcon(QMessageBox.Critical)
        timer = QTimer()
        timer.setInterval(1000)
        def update_countdown():
            nonlocal countdown
            countdown -= 1
            if countdown > 0:
                msg_box.setInformativeText(f"Удаление через: {countdown} сек.")
            else:
                timer.stop()
                msg_box.done(QMessageBox.Ok)
        timer.timeout.connect(update_countdown)
        timer.start()
        if msg_box.exec_() == QMessageBox.Cancel:
            timer.stop()
            return
        if os.path.exists(vault_path):
            try:
                for root, dirs, files in os.walk(vault_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'wb') as f:
                                f.write(get_random_bytes(1024))
                        except:
                            pass
                shutil.rmtree(vault_path)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {str(e)}")
        self.logout()
        QMessageBox.information(self, "Удалено", f"Все данные пользователя '{user_id}' были уничтожены!")

    def edit_entry(self, item):
        index = self.entries_list.row(item)
        if 0 <= index < len(self.entries):
            self.show_entry_form(self.entries[index])


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        window = PasswordVaultApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        if sys.platform == "win32":
            input("Нажмите Enter для выхода...")