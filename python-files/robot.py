# -*- coding: utf-8 -*-
"""
Sohbet Robotu - wxPython Tabanlı Uygulama
- JSON / XML konfigürasyon
- Bilgi tabanı yönetimi
- Ses oynatma (playsound)
- Çok dillilik (Türkçe ve Azerbaycanca)
- Ekran okuyucularla erişilebilirlik (NVDA, JAWS, Narrator)

Gerekli: wxPython, playsound, lxml
"""

import sys
import os
import json
import datetime
import logging
from pathlib import Path
import wx
from lxml import etree
from playsound import playsound

# Loglama
logging.basicConfig(
    level=logging.DEBUG,
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
        "chat_input_label": "Mesajınızı yazın:",
        "chat_history_label": "Sohbet Geçmişi",
        "robot_name_label": "Robot Adı:",
        "interface_language_label": "Arayüz Dili:",
        "save_format_label": "Kaydetme Türü:",
        "color_label": "Arka Plan Rengi:",
        "show_history_label": "Sohbet Geçmişini Göster",
        "add_question_label": "Soru Ekle:",
        "add_answer_label": "Cevap Ekle:",
        "add_sound_label": "Ses Dosyası Ekle (isteğe bağlı):",
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
        "format_standard": "JSON",
        "format_advanced": "XML",
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
        "chat_input_label": "Mesajınızı bura yazın:",
        "chat_history_label": "Söhbət Tarixçəsi",
        "robot_name_label": "Robot Adı:",
        "interface_language_label": "İnterfeys Dili:",
        "save_format_label": "Saxlama Növü:",
        "color_label": "Arxa Plan Rəngi:",
        "show_history_label": "Söhbət Tarixçəsini Göstər",
        "add_question_label": "Sual Əlavə Et:",
        "add_answer_label": "Cavab Əlavə Et:",
        "add_sound_label": "Səs Faylı Əlavə Et (istəyə bağlı):",
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
        "format_standard": "JSON",
        "format_advanced": "XML",
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
    "color": "white",
    "interface_language": "tr",
    "response_language": "tr",
    "save_format": "JSON",
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
        if os.path.exists(CONFIG_FILE_JSON):
            with open(CONFIG_FILE_JSON, "r", encoding="utf-8") as f:
                config = json.load(f)
            logger.info(f"JSON konfigürasyon dosyası yüklendi: {CONFIG_FILE_JSON}")
        elif os.path.exists(CONFIG_FILE_XML):
            tree = etree.parse(CONFIG_FILE_XML)
            root = tree.getroot()
            config = {
                "robot_name": root.findtext("robot_name", DEFAULT_CONFIG["robot_name"]),
                "color": root.findtext("color", DEFAULT_CONFIG["color"]),
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
            logger.info(f"XML konfigürasyon dosyası yüklendi: {CONFIG_FILE_XML}")
        else:
            logger.info("Konfigürasyon dosyası bulunamadı, varsayılanlar kullanılıyor.")
            config = DEFAULT_CONFIG.copy()
            ensure_config_directory()
            if save_config(config):
                logger.info("Varsayılan konfigürasyon dosyası oluşturuldu.")
            else:
                logger.error("Varsayılan konfigürasyon dosyası oluşturulamadı.")
                wx.MessageBox("Varsayılan konfigürasyon dosyası oluşturulamadı.", "Hata", wx.OK | wx.ICON_WARNING)
        for k, v in DEFAULT_CONFIG.items():
            if k not in config:
                config[k] = v
        return config
    except Exception as e:
        logger.error(f"Konfigürasyon yükleme hatası: {e}")
        wx.MessageBox(f"Konfigürasyon yüklenemedi: {e}", "Hata", wx.OK | wx.ICON_WARNING)
        return DEFAULT_CONFIG.copy()

def save_config(config: dict) -> bool:
    """Konfigürasyon dosyasını kaydeder."""
    try:
        ensure_config_directory()
        if config.get("save_format", "JSON") == "JSON":
            with open(CONFIG_FILE_JSON, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            if os.path.exists(CONFIG_FILE_XML):
                os.remove(CONFIG_FILE_XML)
                logger.info(f"Eski XML dosyası silindi: {CONFIG_FILE_XML}")
            logger.info(f"Konfigürasyon JSON olarak kaydedildi: {CONFIG_FILE_JSON}")
        else:
            root = etree.Element("config")
            for key in ["robot_name", "color", "interface_language", "response_language", "save_format"]:
                etree.SubElement(root, key).text = str(config.get(key, ""))
            etree.SubElement(root, "show_history").text = "True" if config.get("show_history") else "False"
            kb_el = etree.SubElement(root, "knowledge_base")
            for item in config.get("knowledge_base", []):
                item_el = etree.SubElement(kb_el, "item")
                for k, v in item.items():
                    etree.SubElement(item_el, k).text = v
            ch_el = etree.SubElement(root, "chat_history")
            for msg in config.get("chat_history", []):
                item = etree.SubElement(ch_el, "item")
                for k, v in msg.items():
                    etree.SubElement(item, k).text = v
            tree = etree.ElementTree(root)
            tree.write(CONFIG_FILE_XML, encoding="utf-8", xml_declaration=True)
            if os.path.exists(CONFIG_FILE_JSON):
                os.remove(CONFIG_FILE_JSON)
                logger.info(f"Eski JSON dosyası silindi: {CONFIG_FILE_JSON}")
            logger.info(f"Konfigürasyon XML olarak kaydedildi: {CONFIG_FILE_XML}")
        return True
    except PermissionError as e:
        logger.error(f"Dosya yazma izni hatası: {e}")
        wx.MessageBox(f"Dosya yazma izni hatası: {e}", "Hata", wx.OK | wx.ICON_ERROR)
        return False
    except Exception as e:
        logger.error(f"Konfigürasyon kaydetme hatası: {e}")
        wx.MessageBox(f"Konfigürasyon kaydedilemedi: {e}", "Hata", wx.OK | wx.ICON_ERROR)
        return False

# Ana Pencere
class ChatBotApp(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Sohbet Robotu", size=(800, 600))
        self.config = load_config()
        self.t = TEXTS.get(self.config.get("interface_language", "tr"), TEXTS["tr"])
        self.SetTitle(self.t["app_title"])
        self.SetBackgroundColour(self.config["color"])

        # Sekmeler
        self.notebook = wx.Notebook(self)
        self.chat_panel = wx.Panel(self.notebook)
        self.teach_panel = wx.Panel(self.notebook)
        self.sounds_panel = wx.Panel(self.notebook)
        self.settings_panel = wx.Panel(self.notebook)
        self.notebook.AddPage(self.chat_panel, self.t["chat_tab"])
        self.notebook.AddPage(self.teach_panel, self.t["teach_tab"])
        self.notebook.AddPage(self.sounds_panel, self.t["sounds_tab"])
        self.notebook.AddPage(self.settings_panel, self.t["settings_tab"])

        self._init_chat_panel()
        self._init_teach_panel()
        self._init_sounds_panel()
        self._init_settings_panel()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

        self._load_chat_history()
        self._load_kb_to_table()
        self._load_sounds_to_table()
        self._load_settings_to_ui()
        self.append_chat(system=True, text=self.t["welcome_msg"])

    def _init_chat_panel(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.chat_history_view = wx.TextCtrl(self.chat_panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.chat_history_view.SetLabel(self.t["chat_history_label"])
        sizer.Add(self.chat_history_view, 1, wx.EXPAND | wx.ALL, 5)

        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.chat_input_label = wx.StaticText(self.chat_panel, label=self.t["chat_input_label"])
        input_sizer.Add(self.chat_input_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.chat_input = wx.TextCtrl(self.chat_panel)
        self.chat_input.Bind(wx.EVT_TEXT_ENTER, self.on_send)
        input_sizer.Add(self.chat_input, 1, wx.EXPAND | wx.RIGHT, 5)
        self.send_button = wx.Button(self.chat_panel, label=self.t["send_button"])
        self.send_button.Bind(wx.EVT_BUTTON, self.on_send)
        input_sizer.Add(self.send_button, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.chat_panel.SetSizer(sizer)

    def _init_teach_panel(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.kb_list = wx.ListCtrl(self.teach_panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.kb_list.InsertColumn(0, self.t["question_label"], width=200)
        self.kb_list.InsertColumn(1, self.t["answer_label"], width=200)
        self.kb_list.InsertColumn(2, self.t["sound_label"], width=200)
        sizer.Add(self.kb_list, 1, wx.EXPAND | wx.ALL, 5)

        form_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.q_label = wx.StaticText(self.teach_panel, label=self.t["add_question_label"])
        self.q_input = wx.TextCtrl(self.teach_panel)
        form_sizer.Add(self.q_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        form_sizer.Add(self.q_input, 1, wx.EXPAND | wx.RIGHT, 5)
        self.a_label = wx.StaticText(self.teach_panel, label=self.t["add_answer_label"])
        self.a_input = wx.TextCtrl(self.teach_panel)
        form_sizer.Add(self.a_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        form_sizer.Add(self.a_input, 1, wx.EXPAND | wx.RIGHT, 5)
        self.s_label = wx.StaticText(self.teach_panel, label=self.t["add_sound_label"])
        self.s_input = wx.TextCtrl(self.teach_panel)
        self.choose_sound_button = wx.Button(self.teach_panel, label="...")
        self.choose_sound_button.Bind(wx.EVT_BUTTON, self.choose_sound_file)
        form_sizer.Add(self.s_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        form_sizer.Add(self.s_input, 1, wx.EXPAND | wx.RIGHT, 5)
        form_sizer.Add(self.choose_sound_button, 0, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(form_sizer, 0, wx.EXPAND | wx.ALL, 5)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_kb_button = wx.Button(self.teach_panel, label=self.t["add_button"])
        self.add_kb_button.Bind(wx.EVT_BUTTON, self.add_kb_item)
        self.remove_kb_button = wx.Button(self.teach_panel, label=self.t["remove_button"])
        self.remove_kb_button.Bind(wx.EVT_BUTTON, self.remove_kb_selected)
        self.save_kb_button = wx.Button(self.teach_panel, label=self.t["save_button"])
        self.save_kb_button.Bind(wx.EVT_BUTTON, self.save_kb_from_table)
        button_sizer.Add(self.add_kb_button, 0, wx.RIGHT, 5)
        button_sizer.Add(self.remove_kb_button, 0, wx.RIGHT, 5)
        button_sizer.AddStretchSpacer()
        button_sizer.Add(self.save_kb_button, 0)
        sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.teach_panel.SetSizer(sizer)

    def _init_sounds_panel(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.sounds_list = wx.ListCtrl(self.sounds_panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.sounds_list.InsertColumn(0, self.t["question_label"], width=200)
        self.sounds_list.InsertColumn(1, self.t["answer_label"], width=200)
        self.sounds_list.InsertColumn(2, self.t["sound_label"], width=200)
        self.sounds_list.InsertColumn(3, self.t["action_label"], width=100)
        sizer.Add(self.sounds_list, 1, wx.EXPAND | wx.ALL, 5)
        self.sounds_panel.SetSizer(sizer)

    def _init_settings_panel(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        form_sizer = wx.FlexGridSizer(5, 2, 5, 5)
        form_sizer.AddGrowableCol(1)

        self.robot_name_label = wx.StaticText(self.settings_panel, label=self.t["robot_name_label"])
        self.robot_name_input = wx.TextCtrl(self.settings_panel, value=self.config["robot_name"])
        form_sizer.Add(self.robot_name_label, 0, wx.ALIGN_CENTER_VERTICAL)
        form_sizer.Add(self.robot_name_input, 1, wx.EXPAND)

        self.lang_label = wx.StaticText(self.settings_panel, label=self.t["interface_language_label"])
        self.lang_combo = wx.Choice(self.settings_panel, choices=list(TEXTS.keys()))
        self.lang_combo.SetStringSelection(self.config["interface_language"])
        form_sizer.Add(self.lang_label, 0, wx.ALIGN_CENTER_VERTICAL)
        form_sizer.Add(self.lang_combo, 1, wx.EXPAND)

        self.save_format_label = wx.StaticText(self.settings_panel, label=self.t["save_format_label"])
        self.save_format_combo = wx.Choice(self.settings_panel, choices=[self.t["format_standard"], self.t["format_advanced"]])
        self.save_format_combo.SetStringSelection(self.t[self.config["save_format"].lower()])
        form_sizer.Add(self.save_format_label, 0, wx.ALIGN_CENTER_VERTICAL)
        form_sizer.Add(self.save_format_combo, 1, wx.EXPAND)

        self.color_label = wx.StaticText(self.settings_panel, label=self.t["color_label"])
        self.color_combo = wx.Choice(self.settings_panel, choices=["white", "lightgray", "lightblue", "lightgreen"])
        self.color_combo.SetStringSelection(self.config["color"])
        form_sizer.Add(self.color_label, 0, wx.ALIGN_CENTER_VERTICAL)
        form_sizer.Add(self.color_combo, 1, wx.EXPAND)

        self.show_history_label = wx.StaticText(self.settings_panel, label=self.t["show_history_label"])
        self.show_history_check = wx.CheckBox(self.settings_panel)
        self.show_history_check.SetValue(self.config["show_history"])
        form_sizer.Add(self.show_history_label, 0, wx.ALIGN_CENTER_VERTICAL)
        form_sizer.Add(self.show_history_check, 0)

        sizer.Add(form_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.AddStretchSpacer()

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.save_settings_button = wx.Button(self.settings_panel, label=self.t["save_button"])
        self.save_settings_button.Bind(wx.EVT_BUTTON, self.save_settings_from_ui)
        self.reset_settings_button = wx.Button(self.settings_panel, label=self.t["reset_button"])
        self.reset_settings_button.Bind(wx.EVT_BUTTON, self.reset_settings)
        button_sizer.AddStretchSpacer()
        button_sizer.Add(self.save_settings_button, 0, wx.RIGHT, 5)
        button_sizer.Add(self.reset_settings_button, 0)
        sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.settings_panel.SetSizer(sizer)

    def _retranslate_ui(self):
        self.t = TEXTS.get(self.config.get("interface_language", "tr"), TEXTS["tr"])
        self.SetTitle(self.t["app_title"])
        self.notebook.SetPageText(0, self.t["chat_tab"])
        self.notebook.SetPageText(1, self.t["teach_tab"])
        self.notebook.SetPageText(2, self.t["sounds_tab"])
        self.notebook.SetPageText(3, self.t["settings_tab"])
        self.chat_input_label.SetLabel(self.t["chat_input_label"])
        self.chat_history_view.SetLabel(self.t["chat_history_label"])
        self.send_button.SetLabel(self.t["send_button"])
        self.kb_list.SetColumn(0, wx.ListItem(self.t["question_label"]))
        self.kb_list.SetColumn(1, wx.ListItem(self.t["answer_label"]))
        self.kb_list.SetColumn(2, wx.ListItem(self.t["sound_label"]))
        self.q_label.SetLabel(self.t["add_question_label"])
        self.a_label.SetLabel(self.t["add_answer_label"])
        self.s_label.SetLabel(self.t["add_sound_label"])
        self.add_kb_button.SetLabe