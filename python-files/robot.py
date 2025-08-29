import wx
import wx.aui
import wx.lib.newevent
import sqlite3
import json
import logging
import os
import sys
import time
from pathlib import Path
from datetime import datetime
import threading
import random
import pygame

# --- Proje Klasör ve Dosya Yolları ---
BASE_DIR = Path(__file__).parent
CONFIG_DIR = BASE_DIR / "config"
SOUNDS_DIR = BASE_DIR / "sounds"
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
IMAGES_DIR = ASSETS_DIR / "images"

# Dosyaların varlığını kontrol et ve oluştur
CONFIG_DIR.mkdir(exist_ok=True)
SOUNDS_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)
ICONS_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

DB_PATH = CONFIG_DIR / "robot_data.db"
ROBOT_DATA_JSON = CONFIG_DIR / "robot_data.json"
JOKES_JSON = CONFIG_DIR / "jokes.json"
MOTOR_SETTINGS_JSON = CONFIG_DIR / "motor_settings.json"
SETTINGS_JSON = CONFIG_DIR / "settings.json"

# Loglama ayarları
logging.basicConfig(filename=BASE_DIR / 'errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Veritabanı ve JSON İşlemleri Sınıfları ---
class DatabaseHandler:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = sqlite3.connect(DB_PATH)
            self.setup_db()
        except sqlite3.Error as e:
            logging.error(f"Veritabanı bağlantı hatası: {e}")
            self.conn = None
            wx.CallAfter(wx.MessageBox, f"Veritabanı bağlanamadı: {e}", "Hata", wx.OK | wx.ICON_ERROR)

    def setup_db(self):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS robot_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    soru TEXT UNIQUE COLLATE NOCASE,
                    cevap TEXT,
                    ses_dosyasi TEXT,
                    eklenme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_soru ON robot_data(LOWER(soru))
            ''')
            self.conn.commit()

    def add_data(self, soru, cevap, ses_dosyasi=""):
        if not self.conn: return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO robot_data (soru, cevap, ses_dosyasi) VALUES (?, ?, ?)", (soru, cevap, ses_dosyasi))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            logging.error(f"Veritabanına veri ekleme hatası: {e}")
            return False

    def update_data(self, soru, yeni_cevap, yeni_ses_dosyasi=""):
        if not self.conn: return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE robot_data SET cevap = ?, ses_dosyasi = ? WHERE LOWER(soru) = LOWER(?)", (yeni_cevap, yeni_ses_dosyasi, soru))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Veritabanı güncelleme hatası: {e}")
            return False

    def delete_data(self, soru):
        if not self.conn: return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM robot_data WHERE LOWER(soru) = LOWER(?)", (soru,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Veritabanından silme hatası: {e}")
            return False

    def get_all_data(self):
        if not self.conn: return []
        cursor = self.conn.cursor()
        cursor.execute("SELECT soru, cevap, ses_dosyasi, eklenme_tarihi FROM robot_data ORDER BY eklenme_tarihi DESC")
        return cursor.fetchall()

    def search_data(self, query):
        if not self.conn: return []
        cursor = self.conn.cursor()
        cursor.execute("SELECT soru, cevap, ses_dosyasi, eklenme_tarihi FROM robot_data WHERE LOWER(soru) LIKE ? OR LOWER(cevap) LIKE ?", (f"%{query.lower()}%", f"%{query.lower()}%"))
        return cursor.fetchall()

    def get_response(self, soru):
        if not self.conn: return None, None
        cursor = self.conn.cursor()
        cursor.execute("SELECT cevap, ses_dosyasi FROM robot_data WHERE LOWER(soru) = LOWER(?)", (soru,))
        result = cursor.fetchone()
        return result

    def close(self):
        if self.conn:
            self.conn.close()

class JSONHandler:
    def load(self, file_path):
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logging.error(f"JSON dosya okuma hatası: {file_path}, {e}")
                return {}
        return {}

    def save(self, file_path, data):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"JSON dosyasına yazma hatası: {file_path}, {e}")

    def sync_db_to_json(self, db_data):
        json_data = {}
        for soru, cevap, ses, _ in db_data:
            json_data[soru] = {"cevap": cevap, "ses": ses}
        self.save(ROBOT_DATA_JSON, json_data)

    def sync_json_to_db(self, db_handler):
        json_data = self.load(ROBOT_DATA_JSON)
        for soru, value in json_data.items():
            cevap = value.get("cevap", "")
            ses = value.get("ses", "")
            if not db_handler.add_data(soru, cevap, ses):
                db_handler.update_data(soru, cevap, ses)

# --- Ses İşlemleri Sınıfı ---
class AudioManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.is_initialized = True
        except pygame.error as e:
            logging.error(f"Pygame mixer başlatılamadı: {e}")
            self.is_initialized = False
            wx.CallAfter(wx.MessageBox, "Ses sistemi başlatılamadı. Ses özellikleri devre dışı bırakıldı.", "Uyarı", wx.OK | wx.ICON_WARNING)

    def play_sound(self, file_path):
        if not self.is_initialized or not Path(file_path).exists():
            return
        try:
            sound = pygame.mixer.Sound(file_path)
            sound.play()
        except pygame.error as e:
            logging.error(f"Ses dosyası oynatılamadı: {file_path}, Hata: {e}")

    def get_sounds(self):
        return [f.name for f in SOUNDS_DIR.iterdir() if f.suffix.lower() == '.wav']

# --- UI Panelleri ---

class TeachPanel(wx.Panel):
    def __init__(self, parent, db_handler, json_handler):
        super().__init__(parent)
        self.db_handler = db_handler
        self.json_handler = json_handler
        self.selected_item = -1
        self.setup_ui()
        self.populate_list()

    def setup_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.search_ctrl = wx.SearchCtrl(self, size=(200, -1), style=wx.TE_PROCESS_ENTER)
        self.search_ctrl.SetHint("Arama...")
        search_sizer.Add(self.search_ctrl, 0, wx.ALL, 5)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search, self.search_ctrl)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_search, self.search_ctrl)

        data_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        input_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Soru TextCtrl
        soru_label = wx.StaticText(self, label="Soru:")
        self.soru_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH, size=(-1, 80))
        self.soru_text.SetHint("Soru girin...")
        input_sizer.Add(soru_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        input_sizer.Add(self.soru_text, 1, wx.EXPAND | wx.ALL, 5)
        
        # Cevap TextCtrl
        cevap_label = wx.StaticText(self, label="Cevap:")
        self.cevap_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH, size=(-1, 80))
        self.cevap_text.SetHint("Cevap girin...")
        input_sizer.Add(cevap_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        input_sizer.Add(self.cevap_text, 1, wx.EXPAND | wx.ALL, 5)

        # Butonlar
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.add_btn = wx.Button(self, label="Ekle")
        self.edit_btn = wx.Button(self, label="Düzenle")
        self.delete_btn = wx.Button(self, label="Sil")
        self.clear_btn = wx.Button(self, label="Temizle")
        button_sizer.Add(self.add_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.edit_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.delete_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.clear_btn, 0, wx.ALL, 5)
        
        input_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER)
        
        data_sizer.Add(input_sizer, 1, wx.EXPAND)

        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN)
        self.list_ctrl.InsertColumn(0, "Soru", width=200)
        self.list_ctrl.InsertColumn(1, "Cevap", width=300)
        self.list_ctrl.InsertColumn(2, "Eklenme Tarihi", width=150)
        
        data_sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 5)

        main_sizer.Add(search_sizer, 0, wx.EXPAND)
        main_sizer.Add(data_sizer, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add)
        self.edit_btn.Bind(wx.EVT_BUTTON, self.on_edit)
        self.delete_btn.Bind(wx.EVT_BUTTON, self.on_delete)
        self.clear_btn.Bind(wx.EVT_BUTTON, self.on_clear)
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_list_select)

    def populate_list(self, data=None):
        self.list_ctrl.DeleteAllItems()
        if data is None:
            data = self.db_handler.get_all_data()
        
        for i, item in enumerate(data):
            self.list_ctrl.InsertItem(i, item[0])
            self.list_ctrl.SetItem(i, 1, item[1])
            self.list_ctrl.SetItem(i, 2, item[3])

    def on_add(self, event):
        soru = self.soru_text.GetValue().strip()
        cevap = self.cevap_text.GetValue().strip()
        if not soru or len(soru) < 5:
            wx.MessageBox("Soru en az 5 karakter olmalıdır.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        if not cevap:
            wx.MessageBox("Cevap boş olamaz.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        
        if self.db_handler.add_data(soru, cevap):
            self.populate_list()
            self.json_handler.sync_db_to_json(self.db_handler.get_all_data())
            self.GetParent().GetParent().get_status_bar().SetStatusText("Yeni veri başarıyla eklendi.")
            self.on_clear(None)
        else:
            msg_box = wx.MessageDialog(self, "Bu soru mevcut, güncellemek ister misiniz?", "Soru Mevcut", wx.YES_NO | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                self.db_handler.update_data(soru, cevap)
                self.populate_list()
                self.json_handler.sync_db_to_json(self.db_handler.get_all_data())
                self.GetParent().GetParent().get_status_bar().SetStatusText("Veri başarıyla güncellendi.")
            msg_box.Destroy()

    def on_edit(self, event):
        if self.selected_item == -1:
            wx.MessageBox("Lütfen düzenlemek için bir öğe seçin.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        
        eski_soru = self.list_ctrl.GetItemText(self.selected_item, 0)
        yeni_cevap = self.cevap_text.GetValue().strip()

        if self.db_handler.update_data(eski_soru, yeni_cevap):
            self.populate_list()
            self.json_handler.sync_db_to_json(self.db_handler.get_all_data())
            self.GetParent().GetParent().get_status_bar().SetStatusText("Veri başarıyla güncellendi.")
        else:
            wx.MessageBox("Düzenleme işlemi başarısız.", "Hata", wx.OK | wx.ICON_ERROR)

    def on_delete(self, event):
        if self.selected_item == -1:
            wx.MessageBox("Lütfen silmek için bir öğe seçin.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return

        soru = self.list_ctrl.GetItemText(self.selected_item, 0)
        confirm_box = wx.MessageBox(f"'{soru}' sorusunu silmek istediğinizden emin misiniz?", "Onay", wx.YES_NO | wx.ICON_QUESTION)
        
        if confirm_box == wx.YES:
            if self.db_handler.delete_data(soru):
                self.populate_list()
                self.json_handler.sync_db_to_json(self.db_handler.get_all_data())
                self.GetParent().GetParent().get_status_bar().SetStatusText("Veri başarıyla silindi.")
                self.on_clear(None)
            else:
                wx.MessageBox("Silme işlemi başarısız.", "Hata", wx.OK | wx.ICON_ERROR)

    def on_list_select(self, event):
        self.selected_item = event.GetIndex()
        soru = self.list_ctrl.GetItemText(self.selected_item, 0)
        cevap = self.list_ctrl.GetItemText(self.selected_item, 1)
        self.soru_text.SetValue(soru)
        self.cevap_text.SetValue(cevap)

    def on_clear(self, event):
        self.soru_text.Clear()
        self.cevap_text.Clear()
        self.selected_item = -1

    def on_search(self, event):
        query = self.search_ctrl.GetValue()
        results = self.db_handler.search_data(query)
        self.populate_list(data=results)

class ChatPanel(wx.Panel):
    def __init__(self, parent, db_handler, json_handler, audio_manager):
        super().__init__(parent)
        self.db_handler = db_handler
        self.json_handler = json_handler
        self.audio_manager = audio_manager
        self.setup_ui()
    
    def setup_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.chat_history = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        
        # Kullanıcı ve Robot ikonları
        user_icon_path = IMAGES_DIR / "user_silhouette.png"
        robot_icon_path = IMAGES_DIR / "robot_silhouette.png"
        self.user_bmp = wx.Image(str(user_icon_path), wx.BITMAP_TYPE_ANY).Scale(32, 32).ConvertToBitmap() if user_icon_path.exists() else None
        self.robot_bmp = wx.Image(str(robot_icon_path), wx.BITMAP_TYPE_ANY).Scale(32, 32).ConvertToBitmap() if robot_icon_path.exists() else None
        
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.input_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
        self.send_btn = wx.Button(self, label="Gönder")
        self.clear_btn = wx.Button(self, label="Temizle")
        self.export_btn = wx.Button(self, label="Dışa Aktar")

        input_sizer.Add(self.input_text, 1, wx.EXPAND | wx.ALL, 5)
        input_sizer.Add(self.send_btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        input_sizer.Add(self.clear_btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        input_sizer.Add(self.export_btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        main_sizer.Add(self.chat_history, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(input_sizer, 0, wx.EXPAND)

        self.SetSizer(main_sizer)
        
        self.send_btn.Bind(wx.EVT_BUTTON, self.on_send_message)
        self.input_text.Bind(wx.EVT_TEXT_ENTER, self.on_send_message)
        self.clear_btn.Bind(wx.EVT_BUTTON, self.on_clear_chat)
        self.export_btn.Bind(wx.EVT_BUTTON, self.on_export_chat)

    def on_send_message(self, event):
        message = self.input_text.GetValue().strip()
        if not message:
            return
        
        self.add_message("Kullanıcı", message, "user")
        self.input_text.Clear()
        
        response, audio_file = self.db_handler.get_response(message)
        
        if response:
            self.add_message("Robot", response, "robot")
            if audio_file and (SOUNDS_DIR / audio_file).exists():
                self.audio_manager.play_sound(SOUNDS_DIR / audio_file)
            else:
                self.audio_manager.play_sound(SOUNDS_DIR / "beep.wav")
        else:
            self.add_message("Robot", "Bu konuyu bilmiyorum, bana öğretmek ister miydiniz?", "robot")
            self.audio_manager.play_sound(SOUNDS_DIR / "beep.wav")

    def add_message(self, sender, message, message_type):
        
        start = self.chat_history.GetLastPosition()
        
        if message_type == "user":
            self.chat_history.BeginAlignment(wx.ALIGN_RIGHT)
            self.chat_history.BeginTextColour(wx.Colour(0, 0, 255))
            if self.user_bmp:
                self.chat_history.WriteImage(self.user_bmp)
            self.chat_history.WriteText(f" {sender}: {message}\n")
        else: # robot
            self.chat_history.BeginAlignment(wx.ALIGN_LEFT)
            self.chat_history.BeginTextColour(wx.Colour(0, 128, 0))
            if self.robot_bmp:
                self.chat_history.WriteImage(self.robot_bmp)
            self.chat_history.WriteText(f" {sender}: {message}\n")

        self.chat_history.EndTextColour()
        self.chat_history.EndAlignment()
        self.chat_history.SetInsertionPointEnd()

    def on_clear_chat(self, event):
        self.chat_history.Clear()
        self.GetParent().GetParent().get_status_bar().SetStatusText("Sohbet geçmişi temizlendi.")

    def on_export_chat(self, event):
        with open("chat_history.txt", "w", encoding="utf-8") as f:
            f.write(self.chat_history.GetValue())
        wx.MessageBox("Sohbet geçmişi 'chat_history.txt' dosyasına başarıyla aktarıldı.", "Bilgi", wx.OK | wx.ICON_INFORMATION)

class SettingsPanel(wx.Panel):
    def __init__(self, parent, json_handler):
        super().__init__(parent)
        self.json_handler = json_handler
        self.settings = self.json_handler.load(SETTINGS_JSON)
        if not self.settings:
            self.settings = {"yanit_hizi": 0, "font_size": 10, "otomatik_kaydet": True, "espri_sikligi": 5}
            self.json_handler.save(SETTINGS_JSON, self.settings)
        self.setup_ui()

    def setup_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Yanıt Hızı
        speed_sizer = wx.BoxSizer(wx.HORIZONTAL)
        speed_label = wx.StaticText(self, label="Yanıt Hızı (saniye):")
        self.speed_slider = wx.Slider(self, value=self.settings["yanit_hizi"], minValue=0, maxValue=5, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        speed_sizer.Add(speed_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        speed_sizer.Add(self.speed_slider, 1, wx.EXPAND | wx.ALL, 5)
        
        # Yazı Tipi Boyutu
        font_sizer = wx.BoxSizer(wx.HORIZONTAL)
        font_label = wx.StaticText(self, label="Yazı Tipi Boyutu:")
        self.font_spin = wx.SpinCtrl(self, value=str(self.settings["font_size"]), min=8, max=24)
        font_sizer.Add(font_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        font_sizer.Add(self.font_spin, 0, wx.ALL, 5)
        
        # Otomatik Kaydetme
        self.autosave_check = wx.CheckBox(self, label="Otomatik JSON Kaydetme")
        self.autosave_check.SetValue(self.settings["otomatik_kaydet"])
        
        # Espri Sıklığı
        joke_sizer = wx.BoxSizer(wx.HORIZONTAL)
        joke_label = wx.StaticText(self, label="Espri Sıklığı (dakika):")
        self.joke_slider = wx.Slider(self, value=self.settings["espri_sikligi"], minValue=1, maxValue=10, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        joke_sizer.Add(joke_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        joke_sizer.Add(self.joke_slider, 1, wx.EXPAND | wx.ALL, 5)
        
        # Espri Ekleme
        joke_add_sizer = wx.BoxSizer(wx.HORIZONTAL)
        joke_add_label = wx.StaticText(self, label="Yeni Espri Ekle:")
        self.joke_text = wx.TextCtrl(self, size=(250, -1))
        self.add_joke_btn = wx.Button(self, label="Ekle")
        joke_add_sizer.Add(joke_add_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        joke_add_sizer.Add(self.joke_text, 1, wx.ALL, 5)
        joke_add_sizer.Add(self.add_joke_btn, 0, wx.ALL, 5)

        # Butonlar
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.save_btn = wx.Button(self, label="Ayarları Kaydet")
        self.reset_btn = wx.Button(self, label="Veritabanını Sıfırla")
        button_sizer.Add(self.save_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.reset_btn, 0, wx.ALL, 5)

        main_sizer.Add(speed_sizer, 0, wx.EXPAND)
        main_sizer.Add(font_sizer, 0, wx.EXPAND)
        main_sizer.Add(self.autosave_check, 0, wx.ALL, 5)
        main_sizer.Add(joke_sizer, 0, wx.EXPAND)
        main_sizer.Add(joke_add_sizer, 0, wx.EXPAND)
        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER)
        
        self.SetSizer(main_sizer)

        self.save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        self.reset_btn.Bind(wx.EVT_BUTTON, self.on_reset_db)
        self.add_joke_btn.Bind(wx.EVT_BUTTON, self.on_add_joke)

    def on_save(self, event):
        self.settings["yanit_hizi"] = self.speed_slider.GetValue()
        self.settings["font_size"] = self.font_spin.GetValue()
        self.settings["otomatik_kaydet"] = self.autosave_check.GetValue()
        self.settings["espri_sikligi"] = self.joke_slider.GetValue()
        self.json_handler.save(SETTINGS_JSON, self.settings)
        wx.MessageBox("Ayarlar başarıyla kaydedildi.", "Bilgi", wx.OK | wx.ICON_INFORMATION)
        self.GetParent().GetParent().get_status_bar().SetStatusText("Ayarlar kaydedildi.")

    def on_reset_db(self, event):
        confirm = wx.MessageBox("Veritabanını sıfırlamak istediğinizden emin misiniz? Tüm öğretilen veriler silinecektir.", "Uyarı", wx.YES_NO | wx.ICON_WARNING)
        if confirm == wx.YES:
            try:
                os.remove(DB_PATH)
                self.GetParent().GetParent().db_handler.connect()
                wx.MessageBox("Veritabanı başarıyla sıfırlandı.", "Bilgi", wx.OK | wx.ICON_INFORMATION)
                self.GetParent().GetParent().get_status_bar().SetStatusText("Veritabanı sıfırlandı.")
            except OSError as e:
                logging.error(f"Veritabanı sıfırlama hatası: {e}")
                wx.MessageBox("Veritabanı sıfırlama başarısız.", "Hata", wx.OK | wx.ICON_ERROR)

    def on_add_joke(self, event):
        joke = self.joke_text.GetValue().strip()
        if not joke:
            wx.MessageBox("Lütfen bir espri girin.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        
        jokes_data = self.json_handler.load(JOKES_JSON)
        if "jokes" not in jokes_data:
            jokes_data["jokes"] = []
        
        jokes_data["jokes"].append(joke)
        self.json_handler.save(JOKES_JSON, jokes_data)
        self.joke_text.Clear()
        self.GetParent().GetParent().get_status_bar().SetStatusText("Espri başarıyla eklendi.")


class SoundsPanel(wx.Panel):
    def __init__(self, parent, audio_manager, db_handler):
        super().__init__(parent)
        self.audio_manager = audio_manager
        self.db_handler = db_handler
        self.setup_ui()
    
    def setup_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Ses Dosyası Seçimi
        sound_file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.file_picker = wx.FilePickerCtrl(self, message="Ses Dosyası Seçin", wildcard="WAV dosyaları (*.wav)|*.wav")
        sound_file_sizer.Add(self.file_picker, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(sound_file_sizer, 0, wx.EXPAND)

        # Ses Listesi
        self.sound_list = wx.ListBox(self, choices=self.audio_manager.get_sounds(), style=wx.LB_SINGLE)
        main_sizer.Add(self.sound_list, 1, wx.EXPAND | wx.ALL, 5)

        # Butonlar
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.play_btn = wx.Button(self, label="Oynat")
        self.add_btn = wx.Button(self, label="Ekle")
        self.delete_btn = wx.Button(self, label="Sil")
        button_sizer.Add(self.play_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.add_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.delete_btn, 0, wx.ALL, 5)
        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER)

        self.SetSizer(main_sizer)

        self.play_btn.Bind(wx.EVT_BUTTON, self.on_play_sound)
        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add_sound)
        self.delete_btn.Bind(wx.EVT_BUTTON, self.on_delete_sound)

    def on_play_sound(self, event):
        selection = self.sound_list.GetSelection()
        if selection != wx.NOT_FOUND:
            sound_file = self.sound_list.GetString(selection)
            self.audio_manager.play_sound(SOUNDS_DIR / sound_file)

    def on_add_sound(self, event):
        source_path = Path(self.file_picker.GetPath())
        if source_path.exists() and source_path.suffix.lower() == ".wav":
            dest_path = SOUNDS_DIR / source_path.name
            try:
                import shutil
                shutil.copy(source_path, dest_path)
                self.sound_list.Set(self.audio_manager.get_sounds())
                self.GetParent().GetParent().get_status_bar().SetStatusText(f"{source_path.name} başarıyla eklendi.")
            except Exception as e:
                wx.MessageBox(f"Dosya kopyalama hatası: {e}", "Hata", wx.OK | wx.ICON_ERROR)

    def on_delete_sound(self, event):
        selection = self.sound_list.GetSelection()
        if selection != wx.NOT_FOUND:
            sound_file = self.sound_list.GetString(selection)
            confirm = wx.MessageBox(f"{sound_file} dosyasını silmek istediğinizden emin misiniz?", "Onay", wx.YES_NO | wx.ICON_QUESTION)
            if confirm == wx.YES:
                try:
                    os.remove(SOUNDS_DIR / sound_file)
                    self.sound_list.Set(self.audio_manager.get_sounds())
                    self.GetParent().GetParent().get_status_bar().SetStatusText(f"{sound_file} başarıyla silindi.")
                except OSError as e:
                    wx.MessageBox(f"Dosya silme hatası: {e}", "Hata", wx.OK | wx.ICON_ERROR)

class MotorPanel(wx.Panel):
    def __init__(self, parent, json_handler):
        super().__init__(parent)
        self.json_handler = json_handler
        self.settings = self.json_handler.load(MOTOR_SETTINGS_JSON)
        if not self.settings:
            self.settings = {
                "Kollar": [{"id": 1, "min": 0, "max": 180}, {"id": 2, "min": 0, "max": 180}],
                "Bacaklar": [{"id": 3, "min": 0, "max": 180}, {"id": 4, "min": 0, "max": 180}],
                "Ayaklar": [{"id": 5, "min": 0, "max": 180}, {"id": 6, "min": 0, "max": 180}, {"id": 7, "min": 0, "max": 180}, {"id": 8, "min": 0, "max": 180}],
                "Parmaklar": [{"id": 9, "min": 0, "max": 180}, {"id": 10, "min": 0, "max": 180}, {"id": 11, "min": 0, "max": 180}, {"id": 12, "min": 0, "max": 180},
                             {"id": 13, "min": 0, "max": 180}, {"id": 14, "min": 0, "max": 180}, {"id": 15, "min": 0, "max": 180}, {"id": 16, "min": 0, "max": 180}],
            }
            self.json_handler.save(MOTOR_SETTINGS_JSON, self.settings)
        self.setup_ui()
    
    def setup_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.tree = wx.TreeCtrl(self, style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.TR_ROW_LINES)
        
        self.root = self.tree.AddRoot("Motorlar")
        self.populate_tree()

        self.apply_btn = wx.Button(self, label="Uygula")
        self.test_btn = wx.Button(self, label="Test Et")

        main_sizer.Add(self.tree, 1, wx.EXPAND | wx.ALL, 5)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.apply_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.test_btn, 0, wx.ALL, 5)
        main_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER)
        
        self.SetSizer(main_sizer)

        self.apply_btn.Bind(wx.EVT_BUTTON, self.on_apply)
        self.test_btn.Bind(wx.EVT_BUTTON, self.on_test)

    def populate_tree(self):
        self.motor_controls = {}
        for category, motors in self.settings.items():
            category_item = self.tree.AppendItem(self.root, category)
            for motor in motors:
                motor_item = self.tree.AppendItem(category_item, f"Motor {motor['id']}")
                self.tree.SetItemData(motor_item, motor)
                
                panel = wx.Panel(self.tree)
                sizer = wx.BoxSizer(wx.HORIZONTAL)
                min_label = wx.StaticText(panel, label="Min Açı:")
                min_spin = wx.SpinCtrl(panel, value=str(motor['min']), min=0, max=360)
                max_label = wx.StaticText(panel, label="Max Açı:")
                max_spin = wx.SpinCtrl(panel, value=str(motor['max']), min=0, max=360)
                
                sizer.Add(min_label, 0, wx.ALL, 2)
                sizer.Add(min_spin, 1, wx.ALL, 2)
                sizer.Add(max_label, 0, wx.ALL, 2)
                sizer.Add(max_spin, 1, wx.ALL, 2)
                panel.SetSizer(sizer)
                
                self.tree.SetItemWindow(motor_item, panel)
                self.motor_controls[motor_item] = {"min": min_spin, "max": max_spin}

    def on_apply(self, event):
        new_settings = {}
        for category_item, category_name in self.tree.GetItemChildren(self.root):
            category_motors = []
            for motor_item, motor_name in self.tree.GetItemChildren(category_item):
                data = self.tree.GetItemData(motor_item)
                controls = self.motor_controls[motor_item]
                motor_id = data.get("id")
                min_val = controls["min"].GetValue()
                max_val = controls["max"].GetValue()
                category_motors.append({"id": motor_id, "min": min_val, "max": max_val})
            new_settings[category_name] = category_motors
        
        self.json_handler.save(MOTOR_SETTINGS_JSON, new_settings)
        self.settings = new_settings
        self.GetParent().GetParent().get_status_bar().SetStatusText("Motor ayarları başarıyla kaydedildi.")

    def on_test(self, event):
        selected_item = self.tree.GetSelection()
        if not selected_item or self.tree.GetItemParent(selected_item) == self.root:
            wx.MessageBox("Lütfen test etmek için bir motor seçin.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        
        controls = self.motor_controls.get(selected_item)
        if controls:
            motor_name = self.tree.GetItemText(selected_item)
            min_val = controls["min"].GetValue()
            max_val = controls["max"].GetValue()
            
            # Simülasyon
            print(f"Motor: {motor_name}, Min: {min_val}, Max: {max_val} test ediliyor...")
            wx.MessageBox(f"{motor_name} simülasyonu başlatıldı.\nMin: {min_val} derece\nMax: {max_val} derece", "Simülasyon", wx.OK | wx.ICON_INFORMATION)


# --- Ana Pencere ve Uygulama Sınıfı ---
class MainFrame(wx.Frame):
    def __init__(self, db_handler, json_handler, audio_manager):
        super().__init__(None, title="Robot Yazılımı", size=(800, 600), style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)
        self.SetMinSize((600, 400))
        
        self.db_handler = db_handler
        self.json_handler = json_handler
        self.audio_manager = audio_manager
        self.jokes = self.json_handler.load(JOKES_JSON).get("jokes", [])
        self.current_panel = None
        self.joke_timer = None
        
        self.setup_ui()
        self.setup_menu()
        self.show_panel('Sohbet')
        self.start_joke_timer()

    def get_status_bar(self):
        return self.GetStatusBar()

    def setup_ui(self):
        self.SetIcon(wx.Icon(str(ICONS_DIR / "robot_icon.ico")))
        self.statusbar = self.CreateStatusBar(1)
        self.statusbar.SetStatusText("Hazır")

        main_splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        
        self.left_panel = wx.Panel(main_splitter)
        self.right_panel = wx.Panel(main_splitter)
        
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        categories = ["Sohbet", "Robota Öğret", "Ayarlar", "Sesler", "Motor Koordinasyon Hareketleri"]
        self.category_list = wx.ListBox(self.left_panel, choices=categories, style=wx.LB_SINGLE)
        left_sizer.Add(self.category_list, 1, wx.EXPAND | wx.ALL, 5)
        self.left_panel.SetSizer(left_sizer)

        self.panel_map = {
            "Sohbet": ChatPanel(self.right_panel, self.db_handler, self.json_handler, self.audio_manager),
            "Robota Öğret": TeachPanel(self.right_panel, self.db_handler, self.json_handler),
            "Ayarlar": SettingsPanel(self.right_panel, self.json_handler),
            "Sesler": SoundsPanel(self.right_panel, self.audio_manager, self.db_handler),
            "Motor Koordinasyon Hareketleri": MotorPanel(self.right_panel, self.json_handler)
        }
        
        for panel in self.panel_map.values():
            panel.Hide()

        main_splitter.SplitVertically(self.left_panel, self.right_panel, 150)
        
        self.Bind(wx.EVT_LISTBOX, self.on_category_select, self.category_list)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def setup_menu(self):
        menu_bar = wx.MenuBar()
        
        file_menu = wx.Menu()
        exit_item = file_menu.Append(wx.ID_EXIT, "Çıkış\tCtrl+Q", "Uygulamayı kapat")
        menu_bar.Append(file_menu, "&Dosya")
        
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "Hakkında", "Uygulama hakkında bilgi")
        menu_bar.Append(help_menu, "&Yardım")

        self.SetMenuBar(menu_bar)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

    def on_category_select(self, event):
        selection = event.GetString()
        self.show_panel(selection)

    def show_panel(self, panel_name):
        if self.current_panel:
            self.current_panel.Hide()
        
        panel_to_show = self.panel_map.get(panel_name)
        if panel_to_show:
            panel_to_show.Show()
            self.current_panel = panel_to_show
            self.Layout()
    
    def on_about(self, event):
        info = wx.adv.AboutDialogInfo()
        info.SetName("Robot Yazılımı")
        info.SetVersion("1.0")
        info.SetDescription("Kullanıcı dostu sohbet robotu sistemi. wxPython ile geliştirilmiştir.")
        info.SetDevelopers(["Yapay Zeka Asistanı"])
        info.SetCopyright(f"© {datetime.now().year}")
        info.SetLicence("MIT License")
        wx.adv.AboutBox(info)

    def on_exit(self, event):
        self.Close(True)

    def on_close(self, event):
        self.db_handler.close()
        if self.joke_timer:
            self.joke_timer.Stop()
        self.Destroy()

    def start_joke_timer(self):
        settings = self.json_handler.load(SETTINGS_JSON)
        interval = settings.get("espri_sikligi", 5) * 60 * 1000  # Dakikayı milisaniyeye çevir
        
        self.joke_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.show_joke, self.joke_timer)
        self.joke_timer.Start(interval)

    def show_joke(self, event):
        if self.jokes:
            joke = random.choice(self.jokes)
            self.statusbar.SetStatusText(joke)

# --- Uygulama Başlangıç Noktası ---
class RobotApp(wx.App):
    def OnInit(self):
        self.db_handler = DatabaseHandler()
        self.json_handler = JSONHandler()
        self.audio_manager = AudioManager()
        
        # JSON'dan veritabanına senkronizasyon
        self.json_handler.sync_json_to_db(self.db_handler)

        main_frame = MainFrame(self.db_handler, self.json_handler, self.audio_manager)
        main_frame.Show()
        self.SetTopWindow(main_frame)
        return True

if __name__ == '__main__':
    app = RobotApp()
    app.MainLoop()