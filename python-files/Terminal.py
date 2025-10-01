import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QComboBox, QLabel, QFontDialog,
    QMessageBox, QGroupBox, QGridLayout
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QTextCursor  
import serial
import serial.tools.list_ports


CONFIG_FILE = "config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки конфига: {e}")
    return {
        "com_port": "",
        "baud_rate": 4800,
        "font_family": "Courier New",
        "font_size": 14,
        "clear_sequence_hex": "1B4A",             # Очищает экран
        "move_cursor_sequence_hex": "1B41",       # Перемещает курсор
        "button1_hex": "1B",       # AT\r
        "button2_hex": "0A" # AT+CMD\r
    }


def save_config(cfg):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения конфига: {e}")


def hex_to_bytes(hex_str):
    try:
        return bytes.fromhex(hex_str)
    except ValueError:
        return b''


def bytes_to_hex_str(data):
    return ' '.join(f'{b:02X}' for b in data)


class TerminalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Terminal (ASCII/HEX)")
        self.resize(1000, 700)
        self.config = load_config()
        self.serial = None
        self.clear_seq = hex_to_bytes(self.config["clear_sequence_hex"])
        self.move_cursor_seq = hex_to_bytes(self.config["move_cursor_sequence_hex"])
        
        self.init_ui()
        self.load_settings_to_ui()
        self.update_com_ports()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)
        self.timer.setInterval(50)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Группа подключения
        connection_group = QGroupBox("Подключение")
        conn_layout = QGridLayout()
        
        conn_layout.addWidget(QLabel("COM-порт:"), 0, 0)
        self.port_combo = QComboBox()
        conn_layout.addWidget(self.port_combo, 0, 1)
        
        conn_layout.addWidget(QLabel("Скорость:"), 1, 0)
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["4800", "9600"])
        conn_layout.addWidget(self.baud_combo, 1, 1)
        
        self.connect_btn = QPushButton("Подключить")
        self.connect_btn.setCheckable(True)
        self.connect_btn.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_btn, 0, 2, 2, 1)
        
        connection_group.setLayout(conn_layout)
        main_layout.addWidget(connection_group)

        # Терминал
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        main_layout.addWidget(self.terminal, 1)

        # Панель отправки
        send_group = QGroupBox("Отправка команд")
        send_layout = QHBoxLayout()
        
        # ASCII команда
        ascii_layout = QVBoxLayout()
        ascii_layout.addWidget(QLabel("ASCII команда:"))
        self.ascii_input = QLineEdit()
        self.ascii_input.setPlaceholderText("Пример: AT+CMD\\r\\n")
        ascii_layout.addWidget(self.ascii_input)
        
        ascii_btn = QPushButton("Отправить ASCII")
        ascii_btn.clicked.connect(self.send_ascii_command)
        ascii_layout.addWidget(ascii_btn)
        
        send_layout.addLayout(ascii_layout)

        # HEX кнопки
        hex_layout = QVBoxLayout()
        hex_layout.addWidget(QLabel("HEX команды:"))
        
        self.btn1 = QPushButton("АРП2 (HEX)")
        self.btn1.clicked.connect(lambda: self.send_hex_command(self.config["button1_hex"]))
        hex_layout.addWidget(self.btn1)
        
        self.btn2 = QPushButton("ПС (HEX)")
        self.btn2.clicked.connect(lambda: self.send_hex_command(self.config["button2_hex"]))
        hex_layout.addWidget(self.btn2)
        
        send_layout.addLayout(hex_layout)

        # Настройка шрифта
        font_btn = QPushButton("Шрифт")
        font_btn.clicked.connect(self.choose_font)
        send_layout.addWidget(font_btn)
        
        send_group.setLayout(send_layout)
        main_layout.addWidget(send_group)

    def load_settings_to_ui(self):
        font = QFont(
            self.config.get("font_family", "Courier New"),
            self.config.get("font_size", 10)
        )
        self.terminal.setFont(font)
        
        baud_str = str(self.config.get("baud_rate", 9600))
        if baud_str in [self.baud_combo.itemText(i) for i in range(self.baud_combo.count())]:
            self.baud_combo.setCurrentText(baud_str)

    def update_com_ports(self):
        self.port_combo.clear()
        ports = [p.device for p in serial.tools.list_ports.comports()]
        
        if not ports:
            self.port_combo.addItem("Нет доступных портов")
            self.connect_btn.setEnabled(False)
        else:
            self.port_combo.addItems(ports)
            self.connect_btn.setEnabled(True)
            
            if self.config["com_port"] in ports:
                self.port_combo.setCurrentText(self.config["com_port"])
            elif ports:
                self.port_combo.setCurrentIndex(0)

    def toggle_connection(self):
        if self.connect_btn.isChecked():
            self.connect_serial()
        else:
            self.disconnect_serial()

    def connect_serial(self):
        port = self.port_combo.currentText()
        baud = int(self.baud_combo.currentText())
        
        try:
            self.serial = serial.Serial(port, baud, timeout=0.1)
            self.connect_btn.setText("Отключить")
            self.terminal.append(f"Подключено к {port} [{baud}]")
            self.timer.start()
            self.config["com_port"] = port
            self.config["baud_rate"] = baud
            save_config(self.config)
        except Exception as e:
            self.connect_btn.setChecked(False)
            QMessageBox.critical(self, "Ошибка подключения", f"Не удалось подключиться:\n{str(e)}")

    def disconnect_serial(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.timer.stop()
        self.connect_btn.setText("Подключить")
        self.terminal.append("Отключено")

    def read_serial(self):
        if not self.serial or not self.serial.is_open:
            return
            
        try:
            data = self.serial.read(1024)
            if data:
                hex_str = bytes_to_hex_str(data)
                ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data)
                
                 # Проверка на последовательность очистки
                if self.clear_seq and self.clear_seq in data:
                    self.terminal.clear()
                    self.terminal.append(f"[Очищено по HEX: {self.config['clear_sequence_hex']}]")
                    cursor = self.terminal.textCursor()
                    cursor.movePosition(QTextCursor.Start)
                    self.terminal.setTextCursor(cursor)
                # Проверка на последовательность перемещения курсора
                elif self.move_cursor_seq and self.move_cursor_seq in data:
                    cursor = self.terminal.textCursor()
                    cursor.movePosition(QTextCursor.Start)
                    self.terminal.setTextCursor(cursor)
                    self.terminal.append(f"[Курсор перемещён по HEX: {self.config['move_cursor_sequence_hex']}]")
                else:
                    self.terminal.append(f">>> HEX: {hex_str}")
                    self.terminal.append(f">>> ASCII: {ascii_str}")
                    # Перемещаем курсор в конец (обычное поведение)
                    cursor = self.terminal.textCursor()
                    cursor.movePosition(QTextCursor.End)
                    self.terminal.setTextCursor(cursor)
        except Exception as e:
            self.terminal.append(f"[ОШИБКА] {str(e)}")

    def send_ascii_command(self):
        command = self.ascii_input.text().strip()
        if not command:
            return
            
        if not self.serial or not self.serial.is_open:
            QMessageBox.warning(self, "Ошибка", "Сначала подключитесь к порту")
            return
            
        try:
            self.serial.write(command.encode('utf-8'))
            self.terminal.append(f"<<< Отправлено (ASCII): {command}")
            self.ascii_input.clear()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка отправки", str(e))

    def send_hex_command(self, hex_str):
        if not self.serial or not self.serial.is_open:
            QMessageBox.warning(self, "Ошибка", "Сначала подключитесь к порту")
            return
            
        data = hex_to_bytes(hex_str)
        if data:
            try:
                self.serial.write(data)
                self.terminal.append(f"<<< Отправлено (HEX): {bytes_to_hex_str(data)}")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка отправки", str(e))
        else:
            QMessageBox.warning(self, "Ошибка", "Некорректный HEX-формат")

    def choose_font(self):
        current_font = self.terminal.font()
        font, ok = QFontDialog.getFont(current_font, self)
        if ok:
            self.terminal.setFont(font)
            self.config["font_family"] = font.family()
            self.config["font_size"] = font.pointSize()
            save_config(self.config)

    def closeEvent(self, event):
        self.disconnect_serial()
        save_config(self.config)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TerminalApp()
    window.show()
    sys.exit(app.exec_())