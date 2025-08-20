import sys
import json
import os
import threading
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QLineEdit, QPushButton, QTabWidget, QCheckBox,
                             QComboBox, QLabel, QDialog, QFileDialog, QTableWidget,
                             QTableWidgetItem, QMessageBox)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

CONFIG_FILE = "robot_config.json"

# --- JSON Management ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "robot_adi": "Robo",
        "renk": "Mavi",
        "robotu_goster": True,
        "ifade_modu": "dinamik",
        "huzursuzluk": False,
        "huzursuzluk_tipi": "rastgele",
        "bilgiler": [],
        "sesler": {},
        "islem_sesleri": {},
        "islem_seslerini_cal": True
    }

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# --- Chat Panel ---
class ChatPanel(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.player = QMediaPlayer()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        
        self.chat_input = QLineEdit()
        layout.addWidget(self.chat_input)
        
        self.send_button = QPushButton("Gönder")
        self.send_button.clicked.connect(self.on_send)
        layout.addWidget(self.send_button)
        
        self.setLayout(layout)

    def on_send(self):
        user_msg = self.chat_input.text().strip()
        if user_msg:
            self.chat_display.append(f"Siz: {user_msg}")
            self.chat_input.clear()
            self.sohbet_cevapla(user_msg)

    def sohbet_cevapla(self, mesaj):
        for item in self.config["bilgiler"]:
            if mesaj.lower() == item["soru"].lower():
                cevap = item["cevap"]
                self.chat_display.append(f"{self.config['robot_adi']}: {cevap}")
                ses = item.get("ses", "")
                if ses and os.path.exists(ses):
                    self.play_sound(ses)
                return
        cevap = ("Üzgünüm, bu konuyu bilmiyorum.\n"
                 "Ama öğretirseniz hem siz bana yardımcı olursunuz\n"
                 "hem de ben size daha sonrasında yardımcı olabilirim.")
        self.chat_display.append(f"{self.config['robot_adi']}: {cevap}")

    def play_sound(self, ses_path):
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(ses_path)))
        self.player.play()

# --- Teach Panel ---
class TeachPanel(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        self.info_label = QLabel("Hiçbir şey bilmiyorum, önce eğitim verin.")
        layout.addWidget(self.info_label)
        
        self.ok_button = QPushButton("Tamam")
        self.ok_button.clicked.connect(self.on_ok)
        layout.addWidget(self.ok_button)
        
        self.setLayout(layout)

    def on_ok(self):
        self.info_label.hide()
        self.ok_button.hide()
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Soru", "Cevap", "Ses"])
        layout = self.layout()
        layout.addWidget(self.table)
        
        self.add_button = QPushButton("Ekle")
        self.add_button.clicked.connect(self.on_add)
        layout.addWidget(self.add_button)
        
        self.populate_table()
        self.setLayout(layout)

    def populate_table(self):
        self.table.setRowCount(0)
        for item in self.config["bilgiler"]:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(item["soru"]))
            self.table.setItem(row, 1, QTableWidgetItem(item["cevap"]))
            self.table.setItem(row, 2, QTableWidgetItem(item.get("ses", "")))

    def on_add(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Yeni Soru-Cevap")
        layout = QVBoxLayout()
        
        soru_label = QLabel("Soru:")
        soru_input = QLineEdit()
        layout.addWidget(soru_label)
        layout.addWidget(soru_input)
        
        cevap_label = QLabel("Cevap:")
        cevap_input = QLineEdit()
        layout.addWidget(cevap_label)
        layout.addWidget(cevap_input)
        
        ses_button = QPushButton("Ses Ekle (Opsiyonel)")
        layout.addWidget(ses_button)
        
        save_button = QPushButton("Kaydet")
        layout.addWidget(save_button)
        
        dialog.setLayout(layout)
        
        def on_ses_ekle():
            file_path, _ = QFileDialog.getOpenFileName(self, "Ses Dosyası Seç", "", "WAV files (*.wav)")
            if file_path:
                base = os.path.basename(file_path)
                name, _ = os.path.splitext(base)
                if not name.isdigit():
                    QMessageBox.critical(self, "Hata", "Dosya adı sadece sayı olmalıdır!")
                    return
                dialog.ses_path = file_path
        
        def on_save():
            soru = soru_input.text().strip()
            cevap = cevap_input.text().strip()
            ses = getattr(dialog, "ses_path", "")
            if soru and cevap:
                self.config["bilgiler"].append({"soru": soru, "cevap": cevap, "ses": ses})
                save_config(self.config)
                self.populate_table()
                dialog.accept()
            else:
                QMessageBox.critical(self, "Hata", "Soru ve cevap boş olamaz!")
        
        ses_button.clicked.connect(on_ses_ekle)
        save_button.clicked.connect(on_save)
        dialog.exec_()

# --- Settings Panel ---
class SettingsPanel(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        self.name_button = QPushButton("Robot Adı Belirle")
        self.name_button.clicked.connect(self.set_robot_name)
        layout.addWidget(self.name_button)
        
        self.show_robot_cb = QCheckBox("Robotu Göster")
        self.show_robot_cb.setChecked(self.config.get("robotu_goster", True))
        layout.addWidget(self.show_robot_cb)
        
        layout.addWidget(QLabel("Yüz İfadesi Modu"))
        self.expression_combo = QComboBox()
        self.expression_combo.addItems(["Dinamik", "Sabit"])
        self.expression_combo.setCurrentText(self.config.get("ifade_modu", "dinamik").capitalize())
        layout.addWidget(self.expression_combo)
        
        layout.addWidget(QLabel("Robot Rengi"))
        self.color_combo = QComboBox()
        colors = ["Kırmızı", "Mavi", "Yeşil", "Sarı", "Turuncu", "Mor", "Pembe", "Siyah", "Kahverengi", "Lacivert"]
        self.color_combo.addItems(colors)
        self.color_combo.setCurrentText(self.config.get("renk", "Mavi"))
        layout.addWidget(self.color_combo)
        
        self.restless_cb = QCheckBox("Huzursuz Robot Sendromu")
        self.restless_cb.setChecked(self.config.get("huzursuzluk", False))
        layout.addWidget(self.restless_cb)
        
        layout.addWidget(QLabel("Huzursuzluk Tipi"))
        self.restless_type_combo = QComboBox()
        self.restless_type_combo.addItems(["Rastgele", "Döngüsel"])
        self.restless_type_combo.setCurrentText(self.config.get("huzursuzluk_tipi", "rastgele").capitalize())
        layout.addWidget(self.restless_type_combo)
        
        self.setLayout(layout)

    def set_robot_name(self):
        name, ok = QInputDialog.getText(self, "Robot Adı", "Robotun adını girin:", text=self.config["robot_adi"])
        if ok and name.strip():
            self.config["robot_adi"] = name.strip()
            save_config(self.config)

# --- Animation Function ---
def start_robot_animation(config):
    def animate():
        while True:
            if config.get("robotu_goster", True):
                # Placeholder for robot animation (ASCII or graphical)
                if config.get("huzursuzluk", False):
                    # Implement random or cyclic animation logic here
                    pass
            time.sleep(0.5)
    t = threading.Thread(target=animate, daemon=True)
    t.start()

# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.setWindowTitle("Robot Uygulaması")
        self.setGeometry(100, 100, 800, 600)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.chat_panel = ChatPanel(self.config)
        self.teach_panel = TeachPanel(self.config)
        self.settings_panel = SettingsPanel(self.config)
        
        self.tabs.addTab(self.chat_panel, "Sohbet")
        self.tabs.addTab(self.teach_panel, "Öğret")
        self.tabs.addTab(self.settings_panel, "Ayarlar")
        
        start_robot_animation(self.config)

    def closeEvent(self, event):
        save_config(self.config)
        event.accept()

# --- Application Entry Point ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())