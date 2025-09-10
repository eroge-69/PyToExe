import sys, os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget, QMessageBox,
    QComboBox, QListWidget, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush
from PyQt5.QtCore import Qt
import json
import random
import string
from cryptography.fernet import Fernet
DATA_FILE = "passwords.json"
KEY_FILE = "key.key"
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
else:
    with open(KEY_FILE, "rb") as f:
        key = f.read()

fernet = Fernet(key)
THEMES = {
    "Neon Green": {"bg": "#121212", "text": "#39FF14", "btn": "#00FF00", "input": "#1e1e1e"},
    "Cyberpunk": {"bg": "#1b1b2f", "text": "#00ffe0", "btn": "#ff00ff", "input": "#2c2c54"},
    "Dracula": {"bg": "#282a36", "text": "#f8f8f2", "btn": "#6272a4", "input": "#44475a"},
    "Matrix": {"bg": "#0b0b0b", "text": "#00ff41", "btn": "#008f11", "input": "#111111"},
    "PurpleNight": {"bg": "#1a001a", "text": "#e0c3fc", "btn": "#8e44ad", "input": "#2a002a"},
    "Monokai": {"bg": "#272822", "text": "#f8f8f2", "btn": "#f92672", "input": "#3e3d32"},
    "BlueOcean": {"bg": "#001f2d", "text": "#aee3f5", "btn": "#00a8e8", "input": "#003459"},
    "Solarized": {"bg": "#002b36", "text": "#839496", "btn": "#268bd2", "input": "#073642"},
    "RedAlert": {"bg": "#1a0d0d", "text": "#ff4d4d", "btn": "#ff1a1a", "input": "#330000"},
    "OrangeSun": {"bg": "#2b1a0d", "text": "#ffb347", "btn": "#ff8000", "input": "#4d2600"},
}
class PasswordManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GreenBax Password Manager")
        self.showMaximized()
        self.current_theme = "Neon Green"
        self.passwords = []
        self.load_data()

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setStyleSheet("QTabBar::tab { min-width: 150px; font-size:16px; }")
        self.setCentralWidget(self.tabs)

        self.main_tab = QWidget()
        self.tabs.addTab(self.main_tab, "🔑 Passwords")
        self.setup_main_tab()

        self.settings_tab = QWidget()
        self.tabs.addTab(self.settings_tab, "⚙ Settings")
        self.setup_settings_tab()

        self.about_tab = QWidget()
        self.tabs.addTab(self.about_tab, "ℹ About")
        self.setup_about_tab()

        self.apply_theme()
    def setup_main_tab(self):
        layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.entry_title = QLineEdit()
        self.entry_title.setPlaceholderText("Title / Website")
        self.entry_title.setFont(QFont("Arial", 16))
        input_layout.addWidget(self.entry_title)

        self.entry_password = QLineEdit()
        self.entry_password.setPlaceholderText("Password")
        self.entry_password.setFont(QFont("Arial", 16))
        input_layout.addWidget(self.entry_password)

        layout.addLayout(input_layout)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("➕ Add")
        add_btn.clicked.connect(self.add_password)
        self.add_shadow(add_btn)
        btn_layout.addWidget(add_btn)

        generate_btn = QPushButton("🎲 Generate")
        generate_btn.clicked.connect(self.generate_password)
        self.add_shadow(generate_btn)
        btn_layout.addWidget(generate_btn)

        del_btn = QPushButton("🗑 Delete Selected")
        del_btn.clicked.connect(self.delete_password)
        self.add_shadow(del_btn)
        btn_layout.addWidget(del_btn)

        copy_btn = QPushButton("📋 Copy Selected")
        copy_btn.clicked.connect(self.copy_password)
        self.add_shadow(copy_btn)
        btn_layout.addWidget(copy_btn)

        layout.addLayout(btn_layout)

        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont("Arial", 16))
        layout.addWidget(self.list_widget)

        self.main_tab.setLayout(layout)
        self.refresh_list()

    def setup_settings_tab(self):
        layout = QVBoxLayout()
        self.theme_select = QComboBox()
        self.theme_select.setFont(QFont("Arial", 16))
        self.theme_select.addItems(THEMES.keys())
        self.theme_select.setCurrentText(self.current_theme)
        self.theme_select.currentTextChanged.connect(self.change_theme)
        layout.addWidget(QLabel("Choose Theme:"))
        layout.addWidget(self.theme_select)
        self.settings_tab.setLayout(layout)

    def setup_about_tab(self):
        layout = QVBoxLayout()
        label = QLabel("GreenBax Password Manager\nDeveloper: Parsa\nGreen Bax My Team")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 22, QFont.Bold))
        layout.addWidget(label)
        self.about_tab.setLayout(layout)
    def apply_theme(self):
        theme = THEMES[self.current_theme]
        bg, txt, btn, inp = theme["bg"], theme["text"], theme["btn"], theme["input"]

        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(bg))
        gradient.setColorAt(1, QColor("#000000"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

        widgets = [self.entry_title, self.entry_password, self.list_widget]
        for w in widgets:
            w.setStyleSheet(f"background-color: {inp}; color: {txt}; border-radius:8px; font-size:16px;")

        buttons = self.findChildren(QPushButton)
        for btn_w in buttons:
            btn_w.setStyleSheet(f"""
                QPushButton {{
                    background-color: {btn};
                    color: {txt};
                    border-radius: 12px;
                    padding: 12px;
                    font-size:18px;
                }}
                QPushButton:hover {{
                    background-color: {txt};
                    color: {btn};
                }}
            """)

        self.tabs.setStyleSheet(f"""
            QTabBar::tab {{
                background: {inp};
                color: {txt};
                padding: 12px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 16px;
                min-width: 150px;
            }}
            QTabBar::tab:selected {{
                background: {btn};
                color: white;
            }}
            QTabWidget::pane {{
                border: 2px solid {btn};
                top: -1px;
            }}
        """)

    def change_theme(self, name):
        self.current_theme = name
        self.apply_theme()

    def add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0)
        shadow.setColor(QColor(0, 0, 0, 160))
        widget.setGraphicsEffect(shadow)
    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                enc_list = json.load(f)
                self.passwords = []
                for item in enc_list:
                    decrypted = fernet.decrypt(item["password"].encode()).decode()
                    self.passwords.append({"title": item["title"], "password": decrypted})
        else:
            self.passwords = []

    def save_data(self):
        enc_list = []
        for item in self.passwords:
            enc = fernet.encrypt(item["password"].encode()).decode()
            enc_list.append({"title": item["title"], "password": enc})
        with open(DATA_FILE, "w") as f:
            json.dump(enc_list, f, indent=4)

    def refresh_list(self):
        self.list_widget.clear()
        for item in self.passwords:
            self.list_widget.addItem(f"{item['title']}")

    def add_password(self):
        title = self.entry_title.text().strip()
        password = self.entry_password.text().strip()
        if not title or not password:
            QMessageBox.warning(self, "Error", "Please enter both title and password")
            return
        self.passwords.append({"title": title, "password": password})
        self.save_data()
        self.refresh_list()
        self.entry_title.clear()
        self.entry_password.clear()

    def delete_password(self):
        selected = self.list_widget.currentRow()
        if selected >= 0:
            self.passwords.pop(selected)
            self.save_data()
            self.refresh_list()

    def copy_password(self):
        selected = self.list_widget.currentRow()
        if selected >= 0:
            QApplication.clipboard().setText(self.passwords[selected]["password"])
            QMessageBox.information(self, "Copied", "Password copied to clipboard")

    def generate_password(self):
        chars = string.ascii_letters + string.digits + string.punctuation
        pwd = ''.join(random.choice(chars) for _ in range(16))
        self.entry_password.setText(pwd)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordManager()
    window.show()
    sys.exit(app.exec_())
