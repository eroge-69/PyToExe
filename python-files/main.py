import sys, os, json, requests, pyperclip, keyboard
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QComboBox, QPushButton,
    QVBoxLayout, QWidget, QSystemTrayIcon, QMenu, QAction, QDialog,
    QLabel, QLineEdit, QHBoxLayout, QMessageBox, QCheckBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QTimer

CONFIG_FILE = "config.json"
DEEPL_URL = "https://api.deepl.com/v2/translate"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # alapértelmezett beállítások
    return {
        "api_key": "",
        "target_lang": "HU",
        "dark_mode": False,
        "hotkey": "ctrl, ctrl"
    }

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

class SettingsDialog(QDialog):
    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.setWindowTitle("Beállítások")
        layout = QVBoxLayout()

        # DeepL API kulcs
        layout.addWidget(QLabel("DeepL API kulcs:"))
        self.api_input = QLineEdit(self.cfg.get("api_key", ""))
        layout.addWidget(self.api_input)

        # Cél nyelv választó
        layout.addWidget(QLabel("Cél nyelv:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["HU", "EN", "DE", "FR", "ES", "IT", "NL", "PL"])
        lang = self.cfg.get("target_lang", "HU")
        if lang in [self.lang_combo.itemText(i) for i in range(self.lang_combo.count())]:
            self.lang_combo.setCurrentText(lang)
        layout.addWidget(self.lang_combo)

        # Sötét mód
        self.darkmode = QCheckBox("Sötét mód használata")
        self.darkmode.setChecked(self.cfg.get("dark_mode", False))
        layout.addWidget(self.darkmode)

        # Gyorsbillentyű
        layout.addWidget(QLabel("Gyorsbillentyű (pl. \"ctrl, ctrl\" vagy \"shift+alt+t\"):"))
        self.hotkey_input = QLineEdit(self.cfg.get("hotkey", "ctrl, ctrl"))
        layout.addWidget(self.hotkey_input)

        # Gombok
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK"); btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Mégse"); btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_ok); btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def accept(self):
        # beállítások mentése
        self.cfg["api_key"]      = self.api_input.text().strip()
        self.cfg["target_lang"]  = self.lang_combo.currentText()
        self.cfg["dark_mode"]    = self.darkmode.isChecked()
        self.cfg["hotkey"]       = self.hotkey_input.text().strip()
        save_config(self.cfg)
        super().accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.ensure_api_key()

        self.setWindowTitle("MiniDeepL")
        self.resize(400, 300)

        # szerkeszthető kimenet
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Itt jelenik meg a fordítás. Szerkeszthető.")
        self.setCentralWidget(self.text_edit)

        # tálca ikon és menü
        self.tray_icon = QSystemTrayIcon(QIcon(self.get_icon_path()), self)
        tray_menu = QMenu()
        tray_menu.addAction("Beállítások", self.open_settings)
        tray_menu.addAction("Kilépés", QApplication.instance().quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

        self.apply_theme()
        self.register_hotkey()

    def get_icon_path(self):
        return os.path.join("icons", "dark.png" if self.cfg.get("dark_mode") else "light.png")

    def apply_theme(self):
        if self.cfg.get("dark_mode"):
            self.setStyleSheet("QWidget { background: #2b2b2b; color: #f0f0f0; }")
        else:
            self.setStyleSheet("")

    def ensure_api_key(self):
        if not self.cfg.get("api_key"):
            dlg = SettingsDialog(self.cfg)
            if dlg.exec() != QDialog.Accepted:
                sys.exit()

    def register_hotkey(self):
        # töröljük a régi hotkeyket, majd újraregisztráljuk
        keyboard.clear_all_hotkeys()
        try:
            keyboard.add_hotkey(
                self.cfg.get("hotkey", "ctrl, ctrl"),
                lambda: QTimer.singleShot(0, self.do_translate)
            )
        except Exception as e:
            QMessageBox.warning(self, "Hiba a gyorsbillentyűnél",
                                f"Nem sikerült beállítani a gyorsbillentyűt:\n{e}")

    def do_translate(self):
        # kigyűjti a kijelölt szöveget
        keyboard.send("ctrl+c")
        QTimer.singleShot(100, self.fetch_and_show)

    def fetch_and_show(self):
        text = pyperclip.paste().strip()
        if not text:
            return

        params = {
            "auth_key": self.cfg["api_key"],
            "text": text,
            "target_lang": self.cfg["target_lang"]
        }
        resp = requests.post(DEEPL_URL, data=params)
        if resp.ok:
            trans = resp.json()["translations"][0]["text"]
            self.text_edit.setPlainText(trans)
            self.showNormal()
            self.activateWindow()
        else:
            QMessageBox.warning(self, "Fordítás sikertelen",
                                f"HTTP {resp.status_code}: {resp.text}")

    def open_settings(self):
        dlg = SettingsDialog(self.cfg, self)
        if dlg.exec() == QDialog.Accepted:
            self.apply_theme()
            self.tray_icon.setIcon(QIcon(self.get_icon_path()))
            self.register_hotkey()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.setVisible(not self.isVisible())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
