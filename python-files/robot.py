# -*- coding: utf-8 -*-
"""
Sohbet Robotu - Tek Dosya Uygulaması (PyQt5)
- JSON / XML konfigürasyon
- Bilgi tabanı yönetimi
- Ses oynatma (QMediaPlayer)
- Çok dillilik (TEXTS)

Gerekli: PyQt5
"""

import sys
import os
import json
import datetime
import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QCheckBox, QComboBox, QLabel,
    QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox, QFormLayout, QTabWidget, QToolButton
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# Loglama
logging.basicConfig(
    level=logging.INFO,
    filename='chatbot_app.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sabitler
CONFIG_FILE_JSON = "chatbot_config.json"
CONFIG_FILE_XML = "chatbot_config.xml"

# Dil Metinleri
TEXTS = {
    "tr": {
        "app_title": "Sohbet Robotu",
        "chat_tab": "Sohbet",
        "teach_tab": "Robota Öğret",
        "sounds_tab": "Sesler",
        "settings_tab": "Ayarlar",
        "welcome_msg": "Merhaba! Ben bir sohbet robotuyum. Bilgi bankamda olanı paylaşırım, sır tutamam. Özel verilerinizi paylaşırken dikkatli olun.",
        "no_answer": "Üzgünüm, bu soruya yanıtım yok. Bana öğretmek ister misiniz?",
        "send_button": "Gönder",
        "chat_input_placeholder": "Mesajınızı buraya yazın...",
        "chat_history_placeholder": "Sohbet geçmişi burada görünür.",
        "robot_name_label": "Robot Adı",
        "interface_language_label": "Arayüz Dili",
        "save_format_label": "Kaydetme Türü",
        "color_label": "Robot Rengi",
        "show_history_label": "Sohbet Geçmişini Göster",
        "add_question": "Soru Ekle",
        "add_answer": "Cevap Ekle",
        "add_sound": "Ses Dosyası Ekle (isteğe bağlı)",
        "add_button": "Ekle",
        "remove_button": "Seçileni Sil",
        "save_button": "Kaydet",
        "reset_button": "Sıfırla",
        "play_button": "Oynat",
        "success_save": "Ayarlar kaydedildi!",
        "error_save": "Ayarlar kaydedilemedi: {}",
        "success_reset": "Konfigürasyon sıfırlandı!",
        "error_reset": "Konfigürasyon sıfırlanamadı: {}",
        "question_label": "Soru",
        "answer_label": "Cevap",
        "sound_label": "Ses Dosyası",
        "action_label": "Eylem",
        "choose_sound": "Ses Dosyası Seç",
        "format_standard": "standart",
        "format_advanced": "gelişmiş",
        "restart_required": "Arayüz dili değişikliğinin etkili olması için lütfen uygulamayı yeniden başlatın.",
        "kb_save_success": "Bilgi tabanı başarıyla kaydedildi!",
        "kb_save_error": "Bilgi tabanı kaydedilemedi: {}"
    },
    "az": {
        "app_title": "Söhbət Robotu",
        "chat_tab": "Söhbət",
        "teach_tab": "Robota Öyrət",
        "sounds_tab": "Səslər",
        "settings_tab": "Tənzimləmələr",
        "welcome_msg": "Salam! Mən bir söhbət robotuyam. Bilik bazamda olanı bölüşərəm, sirr saxlamıram. Şəxsi məlumatlarınızı paylaşarkən diqqətli olun.",
        "no_answer": "Üzr istəyirəm, bu suala cavabım yoxdur. Mənə öyrətmək istəyirsinizmi?",
        "send_button": "Göndər",
        "chat_input_placeholder": "Mesajınızı bura yazın...",
        "chat_history_placeholder": "Söhbət tarixçəsi burada görünür.",
        "robot_name_label": "Robot Adı",
        "interface_language_label": "İnterfeys Dili",
        "save_format_label": "Saxlama Növü",
        "color_label": "Robot Rəngi",
        "show_history_label": "Söhbət Tarixçəsini Göstər",
        "add_question": "Sual Əlavə Et",
        "add_answer": "Cavab Əlavə Et",
        "add_sound": "Səs Faylı Əlavə Et (istəyə bağlı)",
        "add_button": "Əlavə Et",
        "remove_button": "Seçiləni Sil",
        "save_button": "Saxla",
        "reset_button": "Sıfırla",
        "play_button": "Oynat",
        "success_save": "Tənzimləmələr saxlanıldı!",
        "error_save": "Tənzimləmələr saxlanıla bilmədi: {}",
        "success_reset": "Konfiqurasiya sıfırlandı!",
        "error_reset": "Konfiqurasiya sıfırlana bilmədi: {}",
        "question_label": "Sual",
        "answer_label": "Cavab",
        "sound_label": "Səs Faylı",
        "action_label": "Fəaliyyət",
        "choose_sound": "Səs Faylı Seç",
        "format_standard": "standart",
        "format_advanced": "gelişmiş",
        "restart_required": "İnterfeys dili dəyişikliyinin qüvvəyə minməsi üçün lütfən tətbiqi yenidən başladın.",
        "kb_save_success": "Bilik bazası müvəffəqiyyətlə saxlanıldı!",
        "kb_save_error": "Bilik bazası saxlanıla bilmədi: {}"
    }
}

# Yardımcı Fonksiyonlar
def normalize_text(s: str) -> str:
    return " ".join(s.strip().lower().split()) if s else ""

def now_iso() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")

# Konfigürasyon Yönetimi
DEFAULT_CONFIG = {
    "robot_name": "ChatBot",
    "color": "blue",
    "restless": False,
    "interface_language": "tr",
    "response_language": "tr",
    "save_format": "standart",
    "show_history": True,
    "knowledge_base": [
        {"question": "türkiye", "answer": "Türkiye'nin başkenti Ankara'dır.", "sound": ""},
        {"question": "azerbaycan", "answer": "Azerbaycan'ın başkenti Bakü'dür.", "sound": ""},
        {"question": "kazakistan", "answer": "Kazakistan'ın başkenti Astana'dır.", "sound": ""}
    ],
    "chat_history": []
}

def ensure_config_directory():
    """Konfigürasyon dosyasının kaydedileceği dizini oluşturur."""
    config_dir = os.path.dirname(CONFIG_FILE_JSON)
    if config_dir and not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir)
            logger.info(f"Dizin oluşturuldu: {config_dir}")
        except Exception as e:
            logger.error(f"Dizin oluşturma hatası: {e}")
            raise

def load_config() -> dict:
    """Konfigürasyon dosyasını yükler, yoksa varsayılanları oluşturur."""
    try:
        if os.path.exists(CONFIG_FILE_XML):
            tree = ET.parse(CONFIG_FILE_XML)
            root = tree.getroot()
            config = {
                "robot_name": root.findtext("robot_name", DEFAULT_CONFIG["robot_name"]),
                "color": root.findtext("color", DEFAULT_CONFIG["color"]),
                "restless": root.findtext("restless", "False").lower() == "true",
                "interface_language": root.findtext("interface_language", DEFAULT_CONFIG["interface_language"]),
                "response_language": root.findtext("response_language", DEFAULT_CONFIG["response_language"]),
                "save_format": root.findtext("save_format", DEFAULT_CONFIG["save_format"]),
                "show_history": root.findtext("show_history", "True").lower() == "true",
                "knowledge_base": [],
                "chat_history": []
            }
            for item in root.find("knowledge_base").findall("item"):
                config["knowledge_base"].append({
                    "question": item.findtext("question", ""),
                    "answer": item.findtext("answer", ""),
                    "sound": item.findtext("sound", "")
                })
            for msg in root.find("chat_history").findall("item"):
                config["chat_history"].append({
                    "question": msg.findtext("question", ""),
                    "answer": msg.findtext("answer", ""),
                    "time": msg.findtext("time", now_iso())
                })
        elif os.path.exists(CONFIG_FILE_JSON):
            with open(CONFIG_FILE_JSON, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            logger.info("Konfigürasyon dosyası bulunamadı, varsayılanlar kullanılıyor.")
            config = DEFAULT_CONFIG.copy()
            ensure_config_directory()
            if save_config(config):
                logger.info("Varsayılan konfigürasyon dosyası oluşturuldu.")
            else:
                logger.error("Varsayılan konfigürasyon dosyası oluşturulamadı.")
                QMessageBox.warning(None, "Uyarı", "Varsayılan konfigürasyon dosyası oluşturulamadı.")
            return config

        for k, v in DEFAULT_CONFIG.items():
            if k not in config:
                config[k] = v
        return config
    except Exception as e:
        logger.error(f"Konfigürasyon yükleme hatası: {e}")
        QMessageBox.warning(None, "Uyarı", f"Konfigürasyon yüklenemedi: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: dict) -> bool:
    """Konfigürasyon dosyasını kaydeder."""
    try:
        ensure_config_directory()
        if config.get("save_format", "standart") == "standart":
            with open(CONFIG_FILE_JSON, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            if os.path.exists(CONFIG_FILE_XML):
                os.remove(CONFIG_FILE_XML)
                logger.info(f"Eski XML dosyası silindi: {CONFIG_FILE_XML}")
        else:
            root = ET.Element("config")
            for key in ["robot_name", "color", "interface_language", "response_language", "save_format"]:
                ET.SubElement(root, key).text = str(config.get(key, ""))
            ET.SubElement(root, "restless").text = "True" if config.get("restless") else "False"
            ET.SubElement(root, "show_history").text = "True" if config.get("show_history") else "False"

            kb_el = ET.SubElement(root, "knowledge_base")
            for item in config.get("knowledge_base", []):
                item_el = ET.SubElement(kb_el, "item")
                for k, v in item.items():
                    ET.SubElement(item_el, k).text = v

            ch_el = ET.SubElement(root, "chat_history")
            for msg in config.get("chat_history", []):
                item = ET.SubElement(ch_el, "item")
                for k, v in msg.items():
                    ET.SubElement(item, k).text = v

            tree = ET.ElementTree(root)
            tree.write(CONFIG_FILE_XML, encoding="utf-8", xml_declaration=True)
            if os.path.exists(CONFIG_FILE_JSON):
                os.remove(CONFIG_FILE_JSON)
                logger.info(f"Eski JSON dosyası silindi: {CONFIG_FILE_JSON}")

        logger.info(f"Konfigürasyon kaydedildi: {CONFIG_FILE_JSON if config.get('save_format', 'standart') == 'standart' else CONFIG_FILE_XML}")
        return True
    except PermissionError as e:
        logger.error(f"Dosya yazma izni hatası: {e}")
        QMessageBox.warning(None, "Hata", f"Dosya yazma izni hatası: {e}")
        return False
    except Exception as e:
        logger.error(f"Konfigürasyon kaydetme hatası: {e}")
        QMessageBox.warning(None, "Hata", f"Konfigürasyon kaydedilemedi: {e}")
        return False

# Ana Pencere
class ChatBotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.t = TEXTS.get(self.config.get("interface_language", "tr"), TEXTS["tr"])
        self.setWindowTitle(self.t["app_title"])
        self.resize(980, 640)

        self.player = QMediaPlayer()
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self._init_chat_tab()
        self._init_teach_tab()
        self._init_sounds_tab()
        self._init_settings_tab()

        self._load_kb_to_table()
        self._load_sounds_to_table()
        self._load_settings_to_ui()
        self._load_chat_history()
        self.append_chat(system=True, text=self.t["welcome_msg"])

    def _init_chat_tab(self):
        self.chat_tab = QWidget()
        layout = QVBoxLayout(self.chat_tab)
        self.chat_history_view = QTextEdit()
        self.chat_history_view.setReadOnly(True)
        layout.addWidget(self.chat_history_view)

        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText(self.t["chat_input_placeholder"])
        self.chat_input.returnPressed.connect(self.on_send)
        input_layout.addWidget(self.chat_input)
        self.send_btn = QPushButton(self.t["send_button"])
        self.send_btn.clicked.connect(self.on_send)
        input_layout.addWidget(self.send_btn)

        layout.addLayout(input_layout)
        self.tabs.addTab(self.chat_tab, self.t["chat_tab"])

    def _init_teach_tab(self):
        self.teach_tab = QWidget()
        layout = QVBoxLayout(self.teach_tab)

        self.kb_table = QTableWidget(0, 3)
        self.kb_table.setHorizontalHeaderLabels([self.t["question_label"], self.t["answer_label"], self.t["sound_label"]])
        self.kb_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.kb_table)

        form_layout = QHBoxLayout()
        self.q_input = QLineEdit()
        self.q_input.setPlaceholderText(self.t["add_question"])
        self.a_input = QLineEdit()
        self.a_input.setPlaceholderText(self.t["add_answer"])
        self.s_input = QLineEdit()
        self.s_input.setPlaceholderText(self.t["add_sound"])
        choose_sound_btn = QToolButton()
        choose_sound_btn.setText("...")
        choose_sound_btn.clicked.connect(self.choose_sound_file)

        sound_layout = QHBoxLayout()
        sound_layout.addWidget(self.s_input)
        sound_layout.addWidget(choose_sound_btn)

        form_layout.addWidget(self.q_input)
        form_layout.addWidget(self.a_input)
        form_layout.addLayout(sound_layout)

        button_layout = QHBoxLayout()
        self.add_kb_btn = QPushButton(self.t["add_button"])
        self.add_kb_btn.clicked.connect(self.add_kb_item)
        self.remove_kb_btn = QPushButton(self.t["remove_button"])
        self.remove_kb_btn.clicked.connect(self.remove_kb_selected)
        self.save_kb_btn = QPushButton(self.t["save_button"])
        self.save_kb_btn.clicked.connect(self.save_kb_from_table)

        button_layout.addWidget(self.add_kb_btn)
        button_layout.addWidget(self.remove_kb_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_kb_btn)

        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        self.tabs.addTab(self.teach_tab, self.t["teach_tab"])

    def _init_sounds_tab(self):
        self.sounds_tab = QWidget()
        layout = QVBoxLayout(self.sounds_tab)
        self.sounds_table = QTableWidget(0, 4)
        self.sounds_table.setHorizontalHeaderLabels([self.t["question_label"], self.t["answer_label"], self.t["sound_label"], self.t["action_label"]])
        self.sounds_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.sounds_table)
        self.tabs.addTab(self.sounds_tab, self.t["sounds_tab"])

    def _init_settings_tab(self):
        self.settings_tab = QWidget()
        layout = QVBoxLayout(self.settings_tab)
        form = QFormLayout()

        self.robot_name_input = QLineEdit(self.config["robot_name"])
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(TEXTS.keys())
        self.save_format_combo = QComboBox()
        self.save_format_combo.addItems([self.t["format_standard"], self.t["format_advanced"]])
        self.color_combo = QComboBox()
        self.color_combo.addItems(["blue", "green", "red", "orange", "purple", "black"])
        self.show_history_check = QCheckBox()
        self.show_history_check.setChecked(self.config.get("show_history", True))

        form.addRow(self.t["robot_name_label"], self.robot_name_input)
        form.addRow(self.t["interface_language_label"], self.lang_combo)
        form.addRow(self.t["save_format_label"], self.save_format_combo)
        form.addRow(self.t["color_label"], self.color_combo)
        form.addRow(self.t["show_history_label"], self.show_history_check)

        layout.addLayout(form)
        layout.addStretch()

        btn_layout = QHBoxLayout()
        self.save_settings_btn = QPushButton(self.t["save_button"])
        self.save_settings_btn.clicked.connect(self.save_settings_from_ui)
        self.reset_settings_btn = QPushButton(self.t["reset_button"])
        self.reset_settings_btn.clicked.connect(self.reset_settings)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_settings_btn)
        btn_layout.addWidget(self.reset_settings_btn)

        layout.addLayout(btn_layout)
        self.tabs.addTab(self.settings_tab, self.t["settings_tab"])

    def _retranslate_ui(self):
        self.t = TEXTS.get(self.config.get("interface_language", "tr"), TEXTS["tr"])
        self.setWindowTitle(self.t["app_title"])
        self.tabs.setTabText(0, self.t["chat_tab"])
        self.tabs.setTabText(1, self.t["teach_tab"])
        self.tabs.setTabText(2, self.t["sounds_tab"])
        self.tabs.setTabText(3, self.t["settings_tab"])
        self.chat_history_view.setPlaceholderText(self.t["chat_history_placeholder"])
        self.chat_input.setPlaceholderText(self.t["chat_input_placeholder"])
        self.send_btn.setText(self.t["send_button"])
        self.kb_table.setHorizontalHeaderLabels([self.t["question_label"], self.t["answer_label"], self.t["sound_label"]])
        self.q_input.setPlaceholderText(self.t["add_question"])
        self.a_input.setPlaceholderText(self.t["add_answer"])
        self.s_input.setPlaceholderText(self.t["add_sound"])
        self.add_kb_btn.setText(self.t["add_button"])
        self.remove_kb_btn.setText(self.t["remove_button"])
        self.save_kb_btn.setText(self.t["save_button"])
        self.sounds_table.setHorizontalHeaderLabels([self.t["question_label"], self.t["answer_label"], self.t["sound_label"], self.t["action_label"]])
        self.save_settings_btn.setText(self.t["save_button"])
        self.reset_settings_btn.setText(self.t["reset_button"])

    def _load_chat_history(self):
        if self.config.get("show_history", True):
            self.chat_history_view.clear()
            for entry in self.config.get("chat_history", []):
                self.append_chat(user=True, text=entry.get("question", ""))
                self.append_chat(user=False, text=entry.get("answer", ""))

    def _load_kb_to_table(self):
        self.kb_table.setRowCount(0)
        for item in self.config.get("knowledge_base", []):
            self.add_kb_item(item["question"], item["answer"], item["sound"], False)

    def _load_sounds_to_table(self):
        self.sounds_table.setRowCount(0)
        for item in self.config.get("knowledge_base", []):
            if item.get("sound"):
                row = self.sounds_table.rowCount()
                self.sounds_table.insertRow(row)
                self.sounds_table.setItem(row, 0, QTableWidgetItem(item["question"]))
                self.sounds_table.setItem(row, 1, QTableWidgetItem(item["answer"]))
                self.sounds_table.setItem(row, 2, QTableWidgetItem(item["sound"]))
                play_btn = QPushButton(self.t["play_button"])
                play_btn.clicked.connect(lambda _, path=item["sound"]: self.play_sound(path))
                self.sounds_table.setCellWidget(row, 3, play_btn)

    def _load_settings_to_ui(self):
        self.robot_name_input.setText(self.config.get("robot_name", ""))
        self.lang_combo.setCurrentText(self.config.get("interface_language", "tr"))
        self.save_format_combo.setCurrentText(self.t[self.config.get("save_format", "standart")])
        self.color_combo.setCurrentText(self.config.get("color", "blue"))
        self.show_history_check.setChecked(self.config.get("show_history", True))

    def on_send(self):
        question = self.chat_input.text().strip()
        if not question:
            return
        self.append_chat(user=True, text=question)
        normalized_question = normalize_text(question)
        answer = self.t["no_answer"]
        sound = ""
        for item in self.config.get("knowledge_base", []):
            if normalize_text(item["question"]) == normalized_question:
                answer = item["answer"]
                sound = item[