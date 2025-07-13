import sys
import threading
import time
import keyboard
from pynput.mouse import Listener as MouseListener
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QGroupBox
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER

class iDreamMacro(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('iDream1337')
        self.setFixedSize(520, 580)
        self.setStyleSheet('background-color: #070549;')
        self.combo_keys = 'WASD'
        self.delay = 90
        self.shortcut_active = False
        self.holding_event = threading.Event()
        self.mouse_listener = MouseListener(on_click=self.handle_mouse_click)
        self.mouse_listener.start()
        threading.Thread(target=self.ensure_max_volume, daemon=True).start()
        self.init_ui()

    def ensure_max_volume(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, 1, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        pass
        try:
            volume.SetMute(0, None)
            volume.SetMasterVolumeLevelScalar(1.0, None)
            time.sleep(1)
        except:
            pass  # postinserted
        pass

    def init_ui(self):
        title_font = QFont('Comic Sans MS', 20, QFont.Bold)
        font = QFont('Comic Sans MS', 12)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        kitty_label = QLabel()
        pix = QPixmap('')
        kitty_label.setPixmap(pix.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        kitty_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(kitty_label)
        title = QLabel('iDream1337 Makro')
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('color: #030122;')
        main_layout.addWidget(title)
        subtitle = QLabel('<i>cracked by idream</i>')
        subtitle.setFont(font)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet('color: white;')
        main_layout.addWidget(subtitle)
        combo_group = QGroupBox('Kombinasyonlar')
        combo_group.setStyleSheet('QGroupBox { color: white; border: 2px dashed #111136; border-radius: 10px; padding: 10px; }')
        combo_layout = QVBoxLayout()
        combos = ['DSAW', 'DWAS', 'WASD', 'WDSA']
        self.combo_buttons = []
        for combo in combos:
            btn = QPushButton(f'{combo}')
            btn.setFont(font)
            btn.setStyleSheet(self.pink_button())
            btn.clicked.connect(lambda _, c=combo: self.select_combo(c))
            self.combo_buttons.append(btn)
            combo_layout.addWidget(btn)
        combo_group.setLayout(combo_layout)
        main_layout.addWidget(combo_group)
        delay_group = QGroupBox('Gecikme Süresi')
        delay_group.setStyleSheet('QGroupBox { color: white; border: 2px dashed #111136; border-radius: 10px; padding: 10px; }')
        delay_layout = QVBoxLayout()
        self.delay_input = QLineEdit(str(self.delay))
        self.delay_input.setFont(font)
        self.delay_input.setAlignment(Qt.AlignCenter)
        self.delay_input.setStyleSheet('background-color: #111136; color: white; padding: 6px; border: 1px solid #111136; border-radius: 4px;')
        self.delay_input.textChanged.connect(self.update_delay)
        delay_layout.addWidget(self.delay_input)
        delay_group.setLayout(delay_layout)
        main_layout.addWidget(delay_group)
        btn_layout = QHBoxLayout()
        self.start_button = QPushButton('Başlat')
        self.start_button.setFont(font)
        self.start_button.setStyleSheet(self.green_button())
        self.start_button.clicked.connect(self.set_start_selected)
        btn_layout.addWidget(self.start_button)
        self.stop_button = QPushButton('Durdur')
        self.stop_button.setFont(font)
        self.stop_button.setStyleSheet(self.red_button())
        self.stop_button.clicked.connect(self.set_stop_selected)
        btn_layout.addWidget(self.stop_button)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def pink_button(self):
        pass
        return 'QPushButton {background-color: #111136; color: white; border: 2px solid white; border-radius: 8px; padding: 8px; font-weight: bold;}QPushButton:hover {background-color: #5f00c4;}'

    def green_button(self):
        pass
        return 'QPushButton {background-color: #111136; color: white; border: none;border-radius: 8px; padding: 10px; font-weight: bold;}QPushButton:hover {background-color: #5f00c4;}'

    def red_button(self):
        pass
        return 'QPushButton {background-color: #111136; color: white; border: none;border-radius: 8px; padding: 10px; font-weight: bold;}QPushButton:hover {background-color: #5f00c4;}'

    def select_combo(self, combo_str):
        self.combo_keys = combo_str
        for btn in self.combo_buttons:
            text = btn.text()
            if combo_str in text:
                btn.setStyleSheet(self.green_button())
            else:  # inserted
                btn.setStyleSheet(self.pink_button())

    def update_delay(self):
        try:
            val = int(self.delay_input.text())
            if 0 <= val <= 1000:
                self.delay = val
        except ValueError:
            return None

    def set_start_selected(self):
        self.shortcut_active = True
        self.start_button.setText('Çalışıyor...')
        self.stop_button.setText('Durdur')

    def set_stop_selected(self):
        self.shortcut_active = False
        self.holding_event.clear()
        self.start_button.setText('Başlat')
        self.stop_button.setText('Durduruldu')

    def handle_mouse_click(self, x, y, button, pressed):
        if not self.shortcut_active:
            pass  # postinserted
        return None

    def continuous_macro(self):
        if self.holding_event.is_set() and self.shortcut_active:
            for key in self.combo_keys:
                if not self.holding_event.is_set():
                    break
            time.sleep(0.01)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = iDreamMacro()
    window.show()
    sys.exit(app.exec_())