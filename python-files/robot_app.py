import wx
import wx.aui
import wx.lib.newevent
import sqlite3
import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
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
CONFIG_DIR.mkdir(exist_ok=True, parents=True)
SOUNDS_DIR.mkdir(exist_ok=True, parents=True)
ASSETS_DIR.mkdir(exist_ok=True, parents=True)
ICONS_DIR.mkdir(exist_ok=True, parents=True)
IMAGES_DIR.mkdir(exist_ok=True, parents=True)

# Örnek ses ve resim dosyaları oluşturma (varsa üzerine yazmaz)
(SOUNDS_DIR / "beep.wav").touch(exist_ok=True)
(IMAGES_DIR / "user_silhouette.png").touch(exist_ok=True)
(IMAGES_DIR / "robot_silhouette.png").touch(exist_ok=True)

DB_PATH = CONFIG_DIR / "robot_data.db"
ROBOT_DATA_JSON = CONFIG_DIR / "robot_data.json"
JOKES_JSON = CONFIG_DIR / "jokes.json"
MOTOR_SETTINGS_JSON = CONFIG_DIR / "motor_settings.json"  # Şimdilik kullanılmıyor; gelecek geliştirmeler için.
SETTINGS_JSON = CONFIG_DIR / "settings.json"

# Loglama ayarları
logging.basicConfig(filename=BASE_DIR / 'errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# ---- Uygulama İçi Özel Event ----
SettingsChangedEvent, EVT_SETTINGS_CHANGED = wx.lib.newevent.NewEvent()

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
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS robot_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    soru TEXT UNIQUE COLLATE NOCASE,
                    cevap TEXT,
                    ses_dosyasi TEXT,
                    eklenme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                '''
            )
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_soru ON robot_data(LOWER(soru))')
            self.conn.commit()

    def add_data(self, soru, cevap, ses_dosyasi=""):
        if not self.conn:
            return False
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
        if not self.conn:
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE robot_data SET cevap = ?, ses_dosyasi = ? WHERE LOWER(soru) = LOWER(?)", (yeni_cevap, yeni_ses_dosyasi, soru))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Veritabanı güncelleme hatası: {e}")
            return False

    def delete_data(self, soru):
        if not self.conn:
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM robot_data WHERE LOWER(soru) = LOWER(?)", (soru,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Veritabanından silme hatası: {e}")
            return False

    def get_all_data(self):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        cursor.execute("SELECT soru, cevap, ses_dosyasi, eklenme_tarihi FROM robot_data ORDER BY eklenme_tarihi DESC")
        return cursor.fetchall()

    def search_data(self, query):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        like = f"%{query.lower()}%"
        cursor.execute("SELECT soru, cevap, ses_dosyasi, eklenme_tarihi FROM robot_data WHERE LOWER(soru) LIKE ? OR LOWER(cevap) LIKE ?", (like, like))
        return cursor.fetchall()

    def get_response(self, soru):
        if not self.conn:
            return (None, None)
        cursor = self.conn.cursor()
        cursor.execute("SELECT cevap, ses_dosyasi FROM robot_data WHERE LOWER(soru) = LOWER(?)", (soru,))
        result = cursor.fetchone()
        return result if result else (None, None)

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
        if isinstance(json_data, dict):
            iterable = json_data.items()
        else:
            iterable = []
        for soru, value in iterable:
            cevap = value.get("cevap", "") if isinstance(value, dict) else ""
            ses = value.get("ses", "") if isinstance(value, dict) else ""
            if not db_handler.add_data(soru, cevap, ses):
                db_handler.update_data(soru, cevap, ses)

# --- Ayar Yönetimi ---
class SettingsHandler:
    DEFAULTS = {
        "yanit_hizi": 0,         # saniye
        "font_size": 11,
        "otomatik_kaydet": True,
        "espri_sikligi": 5
    }

    DEFAULT_JOKES = [
        "Nasreddin Hoca’ya sormuşlar: “Dünyanın en kısa günü hangisidir?” Cevap vermiş: “Paranın bittiği gün!”"
    ]

    def __init__(self, json_handler: JSONHandler):
        self.json_handler = json_handler
        self.settings = self.json_handler.load(SETTINGS_JSON)
        if not isinstance(self.settings, dict) or not self.settings:
            self.settings = dict(SettingsHandler.DEFAULTS)
            self.json_handler.save(SETTINGS_JSON, self.settings)

        jokes = self.json_handler.load(JOKES_JSON)
        if not isinstance(jokes, list) or not jokes:
            jokes = list(SettingsHandler.DEFAULT_JOKES)
            self.json_handler.save(JOKES_JSON, jokes)
        self.jokes = jokes

    def get_setting(self, key):
        return self.settings.get(key, SettingsHandler.DEFAULTS.get(key))

    def set_setting(self, key, value, autosave=True):
        self.settings[key] = value
        if autosave and self.get_setting("otomatik_kaydet"):
            self.save_settings()

    def get_jokes(self):
        return list(self.jokes)

    def set_jokes(self, jokes_list, autosave=True):
        self.jokes = list(jokes_list)
        if autosave and self.get_setting("otomatik_kaydet"):
            self.save_jokes()

    def save_settings(self):
        self.json_handler.save(SETTINGS_JSON, self.settings)

    def save_jokes(self):
        self.json_handler.save(JOKES_JSON, self.jokes)

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
        if not self.is_initialized:
            return
        try:
            path = Path(file_path)
            if not path.exists():
                return
            sound = pygame.mixer.Sound(str(path))
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

        soru_label = wx.StaticText(self, label="Soru:")
        self.soru_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH, size=(-1, 80))
        self.soru_text.SetHint("Soru girin...")
        input_sizer.Add(soru_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        input_sizer.Add(self.soru_text, 1, wx.EXPAND | wx.ALL, 5)

        cevap_label = wx.StaticText(self, label="Cevap:")
        self.cevap_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH, size=(-1, 80))
        self.cevap_text.SetHint("Cevap girin...")
        input_sizer.Add(cevap_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        input_sizer.Add(self.cevap_text, 1, wx.EXPAND | wx.ALL, 5)

        ses_label = wx.StaticText(self, label="Ses (isteğe bağlı):")
        self.ses_choice = wx.Choice(self, choices=[""] + [*AudioManager().get_sounds()])
        input_sizer.Add(ses_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        input_sizer.Add(self.ses_choice, 0, wx.EXPAND | wx.ALL, 5)

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
        self.list_ctrl.InsertColumn(0, "Soru", width=250)
        self.list_ctrl.InsertColumn(1, "Cevap", width=380)
        self.list_ctrl.InsertColumn(2, "Ses", width=120)
        self.list_ctrl.InsertColumn(3, "Eklenme Tarihi", width=160)
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
            self.list_ctrl.SetItem(i, 2, item[2] or "")
            self.list_ctrl.SetItem(i, 3, str(item[3]))

    def on_add(self, event):
        soru = self.soru_text.GetValue().strip()
        cevap = self.cevap_text.GetValue().strip()
        ses = self.ses_choice.GetStringSelection().strip() if self.ses_choice else ""
        if not soru or len(soru) < 5:
            wx.MessageBox("Soru en az 5 karakter olmalıdır.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        if not cevap:
            wx.MessageBox("Cevap boş olamaz.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        if self.db_handler.add_data(soru, cevap, ses):
            self.populate_list()
            self.json_handler.sync_db_to_json(self.db_handler.get_all_data())
            self.GetParent().GetParent().get_status_bar().SetStatusText("Yeni veri başarıyla eklendi.")
            self.on_clear(None)
        else:
            msg_box = wx.MessageDialog(self, "Bu soru mevcut, güncellemek ister misiniz?", "Soru Mevcut", wx.YES_NO | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                self.db_handler.update_data(soru, cevap, ses)
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
        yeni_ses = self.ses_choice.GetStringSelection().strip() if self.ses_choice else ""
        if self.db_handler.update_data(eski_soru, yeni_cevap, yeni_ses):
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
        confirm = wx.MessageBox(f"'{soru}' sorusunu silmek istediğinizden emin misiniz?", "Onay", wx.YES_NO | wx.ICON_QUESTION)
        if confirm == wx.YES:
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
        ses = self.list_ctrl.GetItemText(self.selected_item, 2)
        self.soru_text.SetValue(soru)
        self.cevap_text.SetValue(cevap)
        if self.ses_choice:
            idx = self.ses_choice.FindString(ses)
            if idx != wx.NOT_FOUND:
                self.ses_choice.SetSelection(idx)
            else:
                self.ses_choice.SetSelection(0)

    def on_clear(self, event):
        self.soru_text.Clear()
        self.cevap_text.Clear()
        if self.ses_choice:
            self.ses_choice.SetSelection(0)
        self.selected_item = -1

    def on_search(self, event):
        query = self.search_ctrl.GetValue()
        results = self.db_handler.search_data(query)
        self.populate_list(data=results)

class ChatPanel(wx.Panel):
    def __init__(self, parent, db_handler, json_handler, audio_manager, settings_handler):
        super().__init__(parent)
        self.db_handler = db_handler
        self.json_handler = json_handler
        self.audio_manager = audio_manager
        self.settings_handler = settings_handler
        self.message_count = 0
        self.setup_ui()
        self.apply_font_size(self.settings_handler.get_setting("font_size"))
        self.Bind(EVT_SETTINGS_CHANGED, self.on_settings_changed)

    def setup_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.chat_history = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        user_icon_path = IMAGES_DIR / "user_silhouette.png"
        robot_icon_path = IMAGES_DIR / "robot_silhouette.png"
        self.user_bmp = wx.Image(str(user_icon_path), wx.BITMAP_TYPE_ANY).Scale(32, 32).ConvertToBitmap() if user_icon_path.exists() else None
        self.robot_bmp = wx.Image(str(robot_icon_path), wx.BITMAP_TYPE_ANY).Scale(32, 32).ConvertToBitmap() if robot_icon_path.exists() else None
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.input_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER, size=(-1, 60))
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
        yanit_hizi = self.settings_handler.get_setting("yanit_hizi")
        delay_ms = int(max(0, float(yanit_hizi)) * 1000)
        wx.CallLater(delay_ms, self.generate_response, message)

    def generate_response(self, message):
        response, audio_file = self.db_handler.get_response(message)
        self.message_count += 1
        espri_sikligi = max(1, int(self.settings_handler.get_setting("espri_sikligi")))
        if self.message_count % espri_sikligi == 0:
            jokes = self.settings_handler.get_jokes()
            if jokes:
                joke = random.choice(jokes)
                self.add_message("Robot", joke, "robot")
                self.audio_manager.play_sound(SOUNDS_DIR / "beep.wav")
                return
        if response:
            self.add_message("Robot", response, "robot")
            if audio_file:
                self.audio_manager.play_sound(SOUNDS_DIR / audio_file)
            else:
                self.audio_manager.play_sound(SOUNDS_DIR / "beep.wav")
        else:
            self.add_message("Robot", "Bu konuyu bilmiyorum, bana öğretmek ister miydiniz?", "robot")
            self.audio_manager.play_sound(SOUNDS_DIR / "beep.wav")

    def add_message(self, sender, message, message_type):
        if message_type == "user":
            self.chat_history.BeginAlignment(wx.ALIGN_RIGHT)
            self.chat_history.BeginTextColour(wx.Colour(0, 0, 255))
            if self.user_bmp:
                self.chat_history.WriteImage(self.user_bmp)
            self.chat_history.WriteText(f" {sender}: {message}\n")
        else:
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
        self.message_count = 0

    def on_export_chat(self, event):
        out_path = BASE_DIR / "chat_history.txt"
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(self.chat_history.GetValue())
            wx.MessageBox(f"Sohbet geçmişi '{out_path.name}' dosyasına başarıyla aktarıldı.", "Bilgi", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            logging.error(f"Sohbet dışa aktarım hatası: {e}")
            wx.MessageBox("Sohbet geçmişi aktarılırken bir hata oluştu.", "Hata", wx.OK | wx.ICON_ERROR)

    def apply_font_size(self, size_pt: int):
        try:
            font = self.chat_history.GetFont()
            font.SetPointSize(int(size_pt))
            self.chat_history.SetFont(font)
            self.input_text.SetFont(font)
        except Exception as e:
            logging.error(f"Yazı tipi boyutu uygulanamadı: {e}")

    def on_settings_changed(self, event):
        self.apply_font_size(self.settings_handler.get_setting("font_size"))

class SettingsPanel(wx.Panel):
    def __init__(self, parent, json_handler, settings_handler):
        super().__init__(parent)
        self.json_handler = json_handler
        self.settings_handler = settings_handler
        self.jokes_data = self.settings_handler.get_jokes()
        self.settings = dict(self.settings_handler.settings)
        self.setup_ui()
        self.bind_events()
        self.update_font_size(self.settings.get("font_size", 11))

    def setup_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        speed_sizer = wx.BoxSizer(wx.HORIZONTAL)
        speed_label = wx.StaticText(self, label="Yanıt Hızı (saniye):")
        self.speed_slider = wx.Slider(self, value=int(self.settings["yanit_hizi"]), minValue=0, maxValue=5, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        speed_sizer.Add(speed_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        speed_sizer.Add(self.speed_slider, 1, wx.EXPAND | wx.ALL, 5)

        font_sizer = wx.BoxSizer(wx.HORIZONTAL)
        font_label = wx.StaticText(self, label="Yazı Tipi Boyutu:")
        self.font_spin = wx.SpinCtrl(self, value=str(self.settings["font_size"]), min=8, max=28)
        font_sizer.Add(font_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        font_sizer.Add(self.font_spin, 0, wx.ALL, 5)

        autosave_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.autosave_chk = wx.CheckBox(self, label="Ayarları otomatik kaydet")
        self.autosave_chk.SetValue(bool(self.settings["otomatik_kaydet"]))
        autosave_sizer.Add(self.autosave_chk, 0, wx.ALL, 5)

        joke_sizer = wx.BoxSizer(wx.HORIZONTAL)
        joke_label = wx.StaticText(self, label="Espri Sıklığı (mesaj sayısı):")
        self.joke_slider = wx.Slider(self, value=int(self.settings["espri_sikligi"]), minValue=1, maxValue=20, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        joke_sizer.Add(joke_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        joke_sizer.Add(self.joke_slider, 1, wx.EXPAND | wx.ALL, 5)

        jokes_box = wx.StaticBox(self, label="Fıkralar (her satır bir fıkra)")
        jokes_sizer = wx.StaticBoxSizer(jokes_box, wx.VERTICAL)
        self.jokes_txt = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1, 120))
        self.jokes_txt.SetValue("\n".join(self.jokes_data))
        jokes_sizer.Add(self.jokes_txt, 1, wx.EXPAND | wx.ALL, 5)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.save_btn = wx.Button(self, label="Kaydet")
        self.reset_btn = wx.Button(self, label="Varsayılanlara Dön")
        btn_sizer.Add(self.save_btn, 0, wx.ALL, 5)
        btn_sizer.Add(self.reset_btn, 0, wx.ALL, 5)

        main_sizer.Add(speed_sizer, 0, wx.EXPAND)
        main_sizer.Add(font_sizer, 0, wx.EXPAND)
        main_sizer.Add(autosave_sizer, 0, wx.EXPAND)
        main_sizer.Add(joke_sizer, 0, wx.EXPAND)
        main_sizer.Add(jokes_sizer, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT)

        self.SetSizer(main_sizer)

    def bind_events(self):
        self.speed_slider.Bind(wx.EVT_SLIDER, self.on_change_speed)
        self.font_spin.Bind(wx.EVT_SPINCTRL, self.on_change_font)
        self.autosave_chk.Bind(wx.EVT_CHECKBOX, self.on_toggle_autosave)
        self.joke_slider.Bind(wx.EVT_SLIDER, self.on_change_joke_freq)
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        self.reset_btn.Bind(wx.EVT_BUTTON, self.on_reset_defaults)

    def update_font_size(self, size):
        try:
            font = self.GetFont()
            font.SetPointSize(int(size))
            self.SetFont(font)
            self.Layout()
        except Exception as e:
            logging.error(f"Ayar paneli yazı tipi uygulanamadı: {e}")

    def _broadcast_settings_changed(self):
        evt = SettingsChangedEvent()
        wx.PostEvent(self.GetParent().GetParent(), evt)
        for child in self.GetParent().GetChildren():
            wx.PostEvent(child, evt)

    def on_change_speed(self, event):
        self.settings_handler.set_setting("yanit_hizi", self.speed_slider.GetValue())

    def on_change_font(self, event):
        size = self.font_spin.GetValue()
        self.settings_handler.set_setting("font_size", size)
        self.update_font_size(size)
        self._broadcast_settings_changed()

    def on_toggle_autosave(self, event):
        self.settings_handler.set_setting("otomatik_kaydet", self.autosave_chk.GetValue(), autosave=False)
        self.settings_handler.save_settings()

    def on_change_joke_freq(self, event):
        self.settings_handler.set_setting("espri_sikligi", self.joke_slider.GetValue())

    def on_save(self, event):
        jokes_list = [line.strip() for line in self.jokes_txt.GetValue().splitlines() if line.strip()]
        self.settings_handler.set_jokes(jokes_list, autosave=False)
        self.settings_handler.save_settings()
        self.settings_handler.save_jokes()
        wx.MessageBox("Ayarlar kaydedildi.", "Bilgi", wx.OK | wx.ICON_INFORMATION)

    def on_reset_defaults(self, event):
        self.speed_slider.SetValue(SettingsHandler.DEFAULTS["yanit_hizi"])
        self.font_spin.SetValue(SettingsHandler.DEFAULTS["font_size"])
        self.autosave_chk.SetValue(SettingsHandler.DEFAULTS["otomatik_kaydet"])
        self.joke_slider.SetValue(SettingsHandler.DEFAULTS["espri_sikligi"])
        self.jokes_txt.SetValue("\n".join(SettingsHandler.DEFAULT_JOKES))
        self.on_change_speed(None)
        self.on_change_font(None)
        self.on_toggle_autosave(None)
        self.on_change_joke_freq(None)
        self.on_save(None)

class MainFrame(wx.Frame):
    def __init__(self, parent, title="Robot Sohbet Uygulaması"):
        super().__init__(parent, title=title, size=(1000, 700))
        self.db_handler = DatabaseHandler()
        self.json_handler = JSONHandler()
        try:
            self.json_handler.sync_json_to_db(self.db_handler)
        except Exception as e:
            logging.error(f"Başlangıç senkronizasyon hatası: {e}")
        self.audio_manager = AudioManager()
        self.settings_handler = SettingsHandler(self.json_handler)
        self._build_ui()
        self.Centre()
        self.Show()

    def _build_ui(self):
        self.statusbar = self.CreateStatusBar(1)
        self.statusbar.SetStatusText("Hazır.")
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        export_menu_item = file_menu.Append(wx.ID_SAVE, "Verileri JSON'a Dışa Aktar\tCtrl+S")
        import_menu_item = file_menu.Append(wx.ID_OPEN, "JSON'dan İçe Aktar\tCtrl+O")
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, "Çıkış\tCtrl+Q")
        menubar.Append(file_menu, "Dosya")
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.on_export_json, export_menu_item)
        self.Bind(wx.EVT_MENU, self.on_import_json, import_menu_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.notebook = wx.aui.AuiNotebook(self)
        self.teach_panel = TeachPanel(self.notebook, self.db_handler, self.json_handler)
        self.chat_panel = ChatPanel(self.notebook, self.db_handler, self.json_handler, self.audio_manager, self.settings_handler)
        self.settings_panel = SettingsPanel(self.notebook, self.json_handler, self.settings_handler)
        self.notebook.AddPage(self.chat_panel, "Sohbet", select=True)
        self.notebook.AddPage(self.teach_panel, "Öğret")
        self.notebook.AddPage(self.settings_panel, "Ayarlar")
        self.statusbar.SetStatusText("İpucu: 'Öğret' sekmesinden soru-cevap ekleyin, 'Sohbet' sekmesinde deneyin.")
        self.Bind(EVT_SETTINGS_CHANGED, self.on_settings_changed)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def get_status_bar(self):
        return self.statusbar

    def on_export_json(self, event):
        try:
            self.json_handler.sync_db_to_json(self.db_handler.get_all_data())
            wx.MessageBox(f"Veriler '{ROBOT_DATA_JSON.name}' dosyasına aktarıldı.", "Bilgi", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            logging.error(f"Dışa aktarım hatası: {e}")
            wx.MessageBox("Dışa aktarım sırasında bir hata oluştu.", "Hata", wx.OK | wx.ICON_ERROR)

    def on_import_json(self, event):
        try:
            self.json_handler.sync_json_to_db(self.db_handler)
            self.teach_panel.populate_list()
            wx.MessageBox("JSON'dan içe aktarım tamamlandı.", "Bilgi", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            logging.error(f"İçe aktarım hatası: {e}")
            wx.MessageBox("İçe aktarım sırasında bir hata oluştu.", "Hata", wx.OK | wx.ICON_ERROR)

    def on_exit(self, event):
        self.Close(True)

    def on_settings_changed(self, event):
        try:
            self.chat_panel.apply_font_size(self.settings_handler.get_setting("font_size"))
        except Exception:
            pass

    def on_close(self, event):
        try:
            self.json_handler.sync_db_to_json(self.db_handler.get_all_data())
        except Exception as e:
            logging.error(f"Kapanışta JSON senkronizasyon hatası: {e}")
        try:
            self.db_handler.close()
        except Exception:
            pass
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
        except Exception:
            pass
        self.Destroy()

class App(wx.App):
    def OnInit(self):
        self.SetAppName("RobotSohbetApp")
        MainFrame(None)
        return True

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    app = App(False)
    app.MainLoop()
