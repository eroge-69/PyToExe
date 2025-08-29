import sys
import time
import json
import os
import socket
from scapy.all import IP, ICMP, sr1
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QTextEdit, QLabel, QComboBox, QHBoxLayout,
    QListWidget, QListWidgetItem, QMessageBox, QSplitter
)
from PyQt6.QtGui import QFont, QColor, QTextCursor
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl


class Aqua(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aqua")
        self.setGeometry(300, 200, 900, 600)
        self.contacts = []  # Список контактів у форматі {name: "", ip: "", is_dynamic: False}
        self.current_contact = None
        self.message_counter = 0
        self.load_contacts()

        # --- Аквамаринова тема для спілкування ---
        self.setStyleSheet("""
            QWidget {
                background-color: #e0f7fa;
                color: #006064;
                font-family: 'Segoe UI', 'Arial';
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                background-color: #ffffff;
                border: 2px solid #4db6ac;
                border-radius: 8px;
                padding: 6px;
                color: #006064;
            }
            QPushButton {
                background-color: #26a69a;
                border-radius: 10px;
                padding: 8px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #4db6ac;
            }
            QPushButton:disabled {
                background-color: #b2dfdb;
                color: #80cbc4;
            }
            QComboBox {
                background-color: #ffffff;
                border: 2px solid #4db6ac;
                border-radius: 8px;
                padding: 4px;
                color: #006064;
            }
            QLabel {
                color: #00796b;
                font-weight: bold;
            }
            QListWidget {
                background-color: #ffffff;
                border: 2px solid #4db6ac;
                border-radius: 8px;
                color: #006064;
            }
            QListWidget::item:selected {
                background-color: #b2ebf2;
                color: #006064;
            }
            QSplitter::handle {
                background-color: #4db6ac;
            }
        """)

        main_layout = QHBoxLayout()

        # Ліва панель - контакти
        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(0, 0, 10, 0)
        
        contacts_label = QLabel("Контакти:")
        contacts_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        left_panel.addWidget(contacts_label)
        
        self.contacts_list = QListWidget()
        self.contacts_list.itemClicked.connect(self.select_contact)
        self.update_contacts_list()
        left_panel.addWidget(self.contacts_list)
        
        # Додавання нового контакту
        add_layout = QVBoxLayout()
        
        name_layout = QHBoxLayout()
        name_label = QLabel("Ім'я:")
        name_label.setFixedWidth(50)
        name_layout.addWidget(name_label)
        self.contact_name_input = QLineEdit()
        self.contact_name_input.setPlaceholderText("Ім'я контакту")
        name_layout.addWidget(self.contact_name_input)
        add_layout.addLayout(name_layout)
        
        ip_layout = QHBoxLayout()
        ip_label = QLabel("IP:")
        ip_label.setFixedWidth(50)
        ip_layout.addWidget(ip_label)
        self.contact_ip_input = QLineEdit()
        self.contact_ip_input.setPlaceholderText("IP або домен")
        ip_layout.addWidget(self.contact_ip_input)
        add_layout.addLayout(ip_layout)
        
        dynamic_layout = QHBoxLayout()
        self.dynamic_ip_checkbox = QCheckBox("Динамічна IP")
        dynamic_layout.addWidget(self.dynamic_ip_checkbox)
        add_layout.addLayout(dynamic_layout)
        
        add_btn = QPushButton("Додати контакт")
        add_btn.clicked.connect(self.add_contact)
        add_layout.addWidget(add_btn)
        
        left_panel.addLayout(add_layout)

        # Права панель - чат
        right_panel = QVBoxLayout()

        # Заголовок чату
        self.chat_title = QLabel("Оберіть контакт для спілкування")
        title_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        self.chat_title.setFont(title_font)
        self.chat_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chat_title.setStyleSheet("color: #00897b; padding: 10px;")
        right_panel.addWidget(self.chat_title)

        # Вікно чату
        self.chat_display = QTextEdit()
        self.chat_display.setFont(QFont("Consolas", 11))
        self.chat_display.setReadOnly(True)
        right_panel.addWidget(self.chat_display)

        # Панель введення повідомлення
        message_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Введіть повідомлення...")
        self.message_input.returnPressed.connect(self.send_message)
        message_layout.addWidget(self.message_input)
        
        self.send_btn = QPushButton("Надіслати")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setEnabled(False)
        message_layout.addWidget(self.send_btn)
        
        right_panel.addLayout(message_layout)

        # Статусний рядок
        self.status_label = QLabel("Статус: Готовий до спілкування")
        font = QFont("Segoe UI", 9)
        font.setItalic(True)
        self.status_label.setFont(font)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.status_label.setStyleSheet("padding: 5px; background-color: #b2ebf2; border-radius: 5px;")
        right_panel.addWidget(self.status_label)

        # Додаємо панелі до головного layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)
        
        self.setLayout(main_layout)
        
        # Таймер для перевірки вхідних повідомлень
        self.message_timer = QTimer()
        self.message_timer.timeout.connect(self.check_incoming_messages)
        self.message_timer.start(3000)  # Перевірка кожні 3 секунди
        
        # Таймер для оновлення динамічних IP
        self.dynamic_ip_timer = QTimer()
        self.dynamic_ip_timer.timeout.connect(self.update_dynamic_ips)
        self.dynamic_ip_timer.start(60000)  # Перевірка кожну хвилину

    def load_contacts(self):
        try:
            if os.path.exists('aqua_contacts.json'):
                with open('aqua_contacts.json', 'r') as f:
                    self.contacts = json.load(f)
        except:
            self.contacts = []

    def save_contacts(self):
        try:
            with open('aqua_contacts.json', 'w') as f:
                json.dump(self.contacts, f)
        except:
            pass

    def update_contacts_list(self):
        self.contacts_list.clear()
        for contact in self.contacts:
            display_name = contact['name']
            if contact.get('is_dynamic', False):
                display_name += " 🌐"
            item = QListWidgetItem(display_name)
            item.setData(Qt.ItemDataRole.UserRole, contact)
            self.contacts_list.addItem(item)

    def add_contact(self):
        name = self.contact_name_input.text().strip()
        ip = self.contact_ip_input.text().strip()
        is_dynamic = self.dynamic_ip_checkbox.isChecked()
        
        if not name or not ip:
            QMessageBox.warning(self, "Попередження", "Будь ласка, введіть ім'я та IP адресу")
            return
            
        # Перевіряємо, чи IP/домен валідний
        try:
            # Спроба резолвингу доменного імені
            if not ip.replace('.', '').isdigit():  # Якщо не IP, а домен
                resolved_ip = socket.gethostbyname(ip)
                self.chat_display.append(f"ℹ️ Домен {ip} резолвиться в {resolved_ip}")
            else:
                # Перевірка формату IP
                socket.inet_aton(ip)  # Викине виняток для невалідного IP
        except Exception as e:
            QMessageBox.warning(self, "Попередження", f"Невалідна IP адреса або домен: {str(e)}")
            return
        
        # Перевіряємо, чи контакт вже існує
        for contact in self.contacts:
            if contact['name'] == name:
                QMessageBox.warning(self, "Попередження", "Контакт з таким ім'ям вже існує")
                return
                
        self.contacts.append({
            'name': name,
            'ip': ip,
            'is_dynamic': is_dynamic,
            'last_known_ip': ip  # Для динамічних IP
        })
        
        self.update_contacts_list()
        self.save_contacts()
        self.contact_name_input.clear()
        self.contact_ip_input.clear()
        self.dynamic_ip_checkbox.setChecked(False)

    def select_contact(self, item):
        contact_data = item.data(Qt.ItemDataRole.UserRole)
        self.current_contact = contact_data
        self.chat_title.setText(f"Чат з {contact_data['name']}")
        self.send_btn.setEnabled(True)
        self.display_chat_history()

    def display_chat_history(self):
        self.chat_display.clear()
        self.chat_display.append("🚀 Ласкаво просимо до Aqua!")
        
        if self.current_contact.get('is_dynamic', False):
            self.chat_display.append("🌐 Цей контакт має динамічну IP адресу")
            self.chat_display.append("📡 Aqua автоматично оновлює IP при змінах")
        
        self.chat_display.append("💬 Починайте спілкування")
        self.chat_display.append("----------------------------------------")

    def resolve_dynamic_ip(self, contact):
        """Спроба резолвингу IP для контактів з динамічною адресою"""
        try:
            if contact.get('is_dynamic', False):
                # Якщо це доменне ім'я, резолвимо його
                if not contact['ip'].replace('.', '').isdigit():
                    new_ip = socket.gethostbyname(contact['ip'])
                    if new_ip != contact.get('last_known_ip', ''):
                        contact['last_known_ip'] = new_ip
                        self.chat_display.append(f"🌐 Оновлено IP для {contact['name']}: {new_ip}")
                        self.save_contacts()
                    return new_ip
                # Якщо це вже IP, просто повертаємо його
                return contact['ip']
            else:
                # Для статичних IP просто повертаємо значення
                return contact['ip']
        except Exception as e:
            self.chat_display.append(f"⚠️ Помилка резолвингу IP для {contact['name']}: {str(e)}")
            return None

    def send_message(self):
        if not self.current_contact or not self.message_input.text().strip():
            return
            
        message = self.message_input.text().strip()
        self.message_counter += 1
        
        # Отримуємо поточну IP адресу (особливо важливо для динамічних IP)
        target_ip = self.resolve_dynamic_ip(self.current_contact)
        if not target_ip:
            self.chat_display.append(f"❌ Не вдалося визначити IP адресу для {self.current_contact['name']}")
            return
            
        # Відправляємо повідомлення
        try:
            custom_id = self.message_counter % 65535
            packet = IP(dst=target_ip)/ICMP(id=custom_id, seq=1)
            
            self.status_label.setText("Статус: Надсилання повідомлення...")
            reply = sr1(packet, verbose=0, timeout=3)
            
            if reply:
                self.chat_display.append(f"👤 Ви для {self.current_contact['name']}: {message}")
                self.chat_display.append(f"   ✅ Повідомлення доставлено до {target_ip}")
                self.status_label.setText("Статус: Повідомлення доставлено")
                
                cursor = self.chat_display.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.chat_display.setTextCursor(cursor)
            else:
                self.chat_display.append(f"👤 Ви для {self.current_contact['name']}: {message}")
                self.chat_display.append(f"   ❌ Помилка доставки до {target_ip}")
                self.status_label.setText("Статус: Помилка доставки")
                
        except Exception as e:
            self.chat_display.append(f"👤 Ви для {self.current_contact['name']}: {message}")
            self.chat_display.append(f"   ⚠️ Помилка: {str(e)}")
            self.status_label.setText("Статус: Помилка відправки")
        
        self.message_input.clear()

    def check_incoming_messages(self):
        # Перевіряємо активність всіх контактів
        for contact in self.contacts:
            try:
                target_ip = self.resolve_dynamic_ip(contact)
                if not target_ip:
                    continue
                    
                packet = IP(dst=target_ip)/ICMP(id=9999, seq=1)
                reply = sr1(packet, verbose=0, timeout=1)
                
                if reply and reply.src == target_ip:
                    if self.current_contact and self.current_contact['name'] == contact['name']:
                        self.chat_display.append(f"📨 {contact['name']} онлайн ({target_ip})")
                        self.status_label.setText("Статус: Контакт онлайн")
                        
                        cursor = self.chat_display.textCursor()
                        cursor.movePosition(QTextCursor.MoveOperation.End)
                        self.chat_display.setTextCursor(cursor)
                        
            except:
                pass

    def update_dynamic_ips(self):
        """Періодично оновлює IP адреси для контактів з динамічними IP"""
        for contact in self.contacts:
            if contact.get('is_dynamic', False):
                self.resolve_dynamic_ip(contact)

    def closeEvent(self, event):
        self.save_contacts()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Aqua()
    window.show()
    sys.exit(app.exec())