# -*- coding: utf-8 -*-

import wx
import wx.aui
import wx.lib.newevent
import sqlite3
import json
import os
import sys
import logging
import datetime
import shutil
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# Pygame'i sesler için dahil et
try:
    import pygame.mixer
except ImportError:
    pygame = None
    print("Pygame bulunamadı. Sesler çalışmayacak.")

# Loglama ayarları
logging.basicConfig(filename='errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Ana klasör yapısını oluşturma
APP_DIR = "robot_yazilimi"
SOUNDS_DIR = os.path.join(APP_DIR, "sounds")
BACKUPS_DIR = os.path.join(APP_DIR, "backups")
os.makedirs(APP_DIR, exist_ok=True)
os.makedirs(SOUNDS_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)

# Veritabanı ve JSON dosya yolları
DB_PATH = os.path.join(APP_DIR, "robot.db")
ROBOT_DATA_JSON = os.path.join(APP_DIR, "robot_data.json")
JOKES_JSON = os.path.join(APP_DIR, "jokes.json")
SETTINGS_JSON = os.path.join(APP_DIR, "ayarlar.json")
MOTOR_SETTINGS_JSON = os.path.join(APP_DIR, "motor_settings.json")

# Varsayılan ayarlar
DEFAULT_SETTINGS = {
    "yanit_hizi": 0,
    "arkaplan_rengi": "#FFFFFF",
    "yazi_tipi_boyutu": 10,
    "otomatik_kaydetme": True,
    "espri_sikligi": 5,
    "rastgele_ses_oynatma": True,
    "theme": "light"
}
DEFAULT_JOKES = [
    "Neden bilgisayarlar dans edemez? Çünkü sadece bit'leri vardır!",
    "Bir programcı, bir bara gider ve bir bira sipariş eder. Bar taburesi bir daha barı ziyaret etmez...",
    "101010... Bu bir espriydi, güldün mü?"
]
DEFAULT_MOTOR_SETTINGS = {
    "Kollar": {"Motor1": [0, 180], "Motor2": [0, 180]},
    "Bacaklar": {"Motor3": [0, 180], "Motor4": [0, 180]},
    "Ayaklar": {"Motor5": [0, 180], "Motor6": [0, 180], "Motor7": [0, 180], "Motor8": [0, 180]},
    "Parmaklar": {"Motor9": [0, 180], "Motor10": [0, 180], "Motor11": [0, 180], "Motor12": [0, 180],
                   "Motor13": [0, 180], "Motor14": [0, 180], "Motor15": [0, 180], "Motor16": [0, 180]}
}

# Özel etkinlik tanımları
UpdateUIEvent, EVT_UPDATE_UI = wx.lib.newevent.NewEvent()
JokeEvent, EVT_JOKE = wx.lib.newevent.NewEvent()

# Veritabanı ve JSON işlemleri için bir sınıf
class DataManager:
    """Veritabanı ve JSON dosyalarını yönetir."""
    def __init__(self):
        self.conn = None
        self.connect_db()
        self.backup_count = 0
        self.executor = ThreadPoolExecutor(max_workers=1)

    def connect_db(self):
        try:
            self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sorular (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    soru TEXT COLLATE NOCASE UNIQUE,
                    cevap TEXT,
                    ses_dosyasi TEXT,
                    eklenme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
            cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_soru ON sorular(LOWER(soru))')
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Veritabanı bağlantı hatası: {e}")
            wx.MessageBox(f"Veritabanı bağlanamadı: {e}", "Hata", wx.OK | wx.ICON_ERROR)
            self.conn = None

    def close_db(self):
        if self.conn:
            self.conn.close()

    def load_json(self, file_path, default_data):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.save_json(file_path, default_data)
            return default_data

    def save_json(self, file_path, data):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"JSON kaydetme hatası ({file_path}): {e}")
            return False

    def backup_data(self):
        self.backup_count += 1
        if self.backup_count % 10 == 0:
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            backup_db = os.path.join(BACKUPS_DIR, f"robot_db_{timestamp}.db")
            backup_json = os.path.join(BACKUPS_DIR, f"robot_data_{timestamp}.json")
            try:
                shutil.copy(DB_PATH, backup_db)
                shutil.copy(ROBOT_DATA_JSON, backup_json)
                self.post_status_message("Veriler yedeklendi.", 5000)
            except Exception as e:
                logging.error(f"Yedekleme hatası: {e}")
                self.post_status_message("Yedekleme hatası!", 5000)

    def post_status_message(self, message, timeout=2000):
        # Durum çubuğuna mesaj göndermek için bir helper fonksiyon
        wx.CallAfter(wx.GetApp().GetTopWindow().GetStatusBar().SetStatusText, message)
        wx.CallAfter(wx.GetApp().GetTopWindow().GetStatusBar().SetStatusText, "", timeout)

    def add_or_update_entry(self, soru, cevap, ses_dosyasi=None, auto_save=True):
        if not self.conn:
            return False
        
        # Async ekleme işlemi için ThreadPoolExecutor kullan
        future = self.executor.submit(self._add_or_update_entry_thread, soru, cevap, ses_dosyasi, auto_save)
        return future.result()

    def _add_or_update_entry_thread(self, soru, cevap, ses_dosyasi, auto_save):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT soru FROM sorular WHERE LOWER(soru) = LOWER(?)", (soru,))
            existing_entry = cursor.fetchone()

            if existing_entry:
                choice = wx.YES_NO | wx.YES_DEFAULT
                if wx.MessageBox("Bu soru zaten mevcut, güncellemek ister misiniz?", "Soru Mevcut", choice) == wx.YES:
                    cursor.execute("UPDATE sorular SET cevap = ?, ses_dosyasi = ?, eklenme_tarihi = CURRENT_TIMESTAMP WHERE LOWER(soru) = LOWER(?)", (cevap, ses_dosyasi, soru))
                    self.conn.commit()
                    self.post_status_message("Soru güncellendi.", 2000)
                    if auto_save:
                        self.sync_to_json()
                    return True
                else:
                    self.post_status_message("İşlem iptal edildi.", 2000)
                    return False
            else:
                cursor.execute("INSERT INTO sorular (soru, cevap, ses_dosyasi) VALUES (?, ?, ?)", (soru, cevap, ses_dosyasi))
                self.conn.commit()
                self.post_status_message("Soru eklendi.", 2000)
                if auto_save:
                    self.sync_to_json()
                return True
        except sqlite3.Error as e:
            logging.error(f"Veritabanı ekleme/güncelleme hatası: {e}")
            self.post_status_message("Veritabanı hatası!", 3000)
            return False

    def delete_entry(self, soru):
        if not self.conn:
            return False
        
        future = self.executor.submit(self._delete_entry_thread, soru)
        return future.result()
    
    def _delete_entry_thread(self, soru):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM sorular WHERE LOWER(soru) = LOWER(?)", (soru,))
            self.conn.commit()
            self.post_status_message("Soru silindi.", 2000)
            self.sync_to_json()
            return True
        except sqlite3.Error as e:
            logging.error(f"Veritabanı silme hatası: {e}")
            self.post_status_message("Veritabanı hatası!", 3000)
            return False

    def fetch_all(self):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        cursor.execute("SELECT soru, cevap, eklenme_tarihi, ses_dosyasi FROM sorular ORDER BY eklenme_tarihi DESC")
        return cursor.fetchall()
    
    def search_entries(self, query):
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        cursor.execute("SELECT soru, cevap, eklenme_tarihi, ses_dosyasi FROM sorular WHERE LOWER(soru) LIKE ? OR LOWER(cevap) LIKE ?", (f"%{query.lower()}%", f"%{query.lower()}%"))
        return cursor.fetchall()
    
    def get_response(self, user_message):
        if not self.conn:
            return None, None
        
        future = self.executor.submit(self._get_response_thread, user_message)
        return future.result()

    def _get_response_thread(self, user_message):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT cevap, ses_dosyasi FROM sorular WHERE LOWER(soru) = LOWER(?)", (user_message,))
            result = cursor.fetchone()
            if result:
                return result[0], result[1]
            return None, None
        except sqlite3.Error as e:
            logging.error(f"Sorgu hatası: {e}")
            return None, None

    def sync_to_json(self):
        future = self.executor.submit(self._sync_to_json_thread)
        return future.result()

    def _sync_to_json_thread(self):
        try:
            all_data = self.fetch_all()
            data_dict = {}
            for soru, cevap, _, ses_dosyasi in all_data:
                data_dict[soru] = {"cevap": cevap, "ses": ses_dosyasi or ""}
            self.save_json(ROBOT_DATA_JSON, data_dict)
            self.backup_data()
            return True
        except Exception as e:
            logging.error(f"JSON senkronizasyon hatası: {e}")
            return False

    def import_json_data(self):
        future = self.executor.submit(self._import_json_data_thread)
        return future.result()

    def _import_json_data_thread(self):
        try:
            data_files = [f for f in os.listdir(APP_DIR) if f.endswith('.json')]
            imported_count = 0
            for filename in data_files:
                file_path = os.path.join(APP_DIR, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, dict):
                            for key, value in data.items():
                                if isinstance(value, dict) and "cevap" in value:
                                    soru = key
                                    cevap = value["cevap"]
                                    ses = value.get("ses", "")
                                    self._add_or_update_entry_thread(soru, cevap, ses, False) # Auto-save'i kapat
                                    imported_count += 1
                                elif isinstance(value, str):
                                    soru = key
                                    cevap = value
                                    self._add_or_update_entry_thread(soru, cevap, None, False)
                                    imported_count += 1
                    except json.JSONDecodeError as e:
                        logging.error(f"Geçersiz JSON dosyası: {filename} - {e}")

            self.sync_to_json() # Tüm işlemlerden sonra tek seferde senkronize et
            self.post_status_message(f"{imported_count} veri JSON'lardan toplandı.", 5000)
            return True
        except Exception as e:
            logging.error(f"JSON veri toplama hatası: {e}")
            self.post_status_message("Veri toplama hatası!", 5000)
            return False

# Ana Uygulama Panelleri
class BasePanel(wx.Panel):
    """Ortak paneller için temel sınıf."""
    def __init__(self, parent, data_manager, settings):
        super().__init__(parent)
        self.data_manager = data_manager
        self.settings = settings
        self.SetBackgroundColour(self.settings.get("arkaplan_rengi"))
        self.Bind(EVT_UPDATE_UI, self.on_update_ui)
        self.on_update_ui() # Başlangıçta UI'yi ayarla

    def on_update_ui(self, event=None):
        self.SetBackgroundColour(self.settings.get("arkaplan_rengi"))
        self.Refresh()
        self.Update()

class OgretPanel(BasePanel):
    """Robota Öğret sekmesi için panel."""
    def __init__(self, parent, data_manager, settings):
        super().__init__(parent, data_manager, settings)

        self.SetAccessible(wx.Accessible(self))
        self.GetAccessible().SetRole(wx.ACC_ROLE_PANE)
        self.GetAccessible().SetName("Robota Öğret Paneli")
        self.GetAccessible().SetDescription("Robot için soru-cevap çiftleri eklemek ve yönetmek için kullanılır.")

        # UI elemanları
        self.soru_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH)
        self.soru_text.SetHint("Soru girin...")
        self.soru_text.SetAccessible(wx.Accessible(self.soru_text))
        self.soru_text.GetAccessible().SetName("Soru Giriş Kutusu")

        self.cevap_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH)
        self.cevap_text.SetHint("Cevap girin...")
        self.cevap_text.SetAccessible(wx.Accessible(self.cevap_text))
        self.cevap_text.GetAccessible().SetName("Cevap Giriş Kutusu")

        self.ses_file_picker = wx.FilePickerCtrl(self, message="Ses Dosyası Seçin", wildcard="WAV dosyaları (*.wav)|*.wav", style=wx.FLP_DEFAULT_STYLE)
        self.ses_file_picker.SetAccessible(wx.Accessible(self.ses_file_picker))
        self.ses_file_picker.GetAccessible().SetName("Ses Dosyası Seçici")

        self.add_button = wx.Button(self, label="Ekle")
        self.add_button.SetAccessible(wx.Accessible(self.add_button))
        self.add_button.GetAccessible().SetName("Ekle Butonu")
        self.add_button.SetToolTip("Yeni bir soru-cevap çifti ekler. (Kısayol: Alt+E)")
        self.Bind(wx.EVT_BUTTON, self.on_add, self.add_button)

        self.update_button = wx.Button(self, label="Düzenle")
        self.update_button.SetAccessible(wx.Accessible(self.update_button))
        self.update_button.GetAccessible().SetName("Düzenle Butonu")
        self.update_button.SetToolTip("Seçili soru-cevap çiftini günceller.")
        self.Bind(wx.EVT_BUTTON, self.on_update, self.update_button)

        self.delete_button = wx.Button(self, label="Sil")
        self.delete_button.SetAccessible(wx.Accessible(self.delete_button))
        self.delete_button.GetAccessible().SetName("Sil Butonu")
        self.delete_button.SetToolTip("Seçili soru-cevap çiftini siler.")
        self.Bind(wx.EVT_BUTTON, self.on_delete, self.delete_button)

        self.search_ctrl = wx.SearchCtrl(self)
        self.search_ctrl.SetHint("Arama...")
        self.search_ctrl.SetAccessible(wx.Accessible(self.search_ctrl))
        self.search_ctrl.GetAccessible().SetName("Arama Kutusu")
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.on_search, self.search_ctrl)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_search, self.search_ctrl)

        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES | wx.LC_VRULES)
        self.list_ctrl.InsertColumn(0, "Soru")
        self.list_ctrl.InsertColumn(1, "Cevap")
        self.list_ctrl.InsertColumn(2, "Eklenme Tarihi")
        self.list_ctrl.InsertColumn(3, "Ses Dosyası")

        self.list_ctrl.SetAccessible(wx.Accessible(self.list_ctrl))
        self.list_ctrl.GetAccessible().SetName("Soru-Cevap Listesi")
        self.list_ctrl.GetAccessible().SetDescription("Veritabanındaki tüm soru-cevap çiftlerini listeler.")

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_list_item_selected, self.list_ctrl)

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        input_grid = wx.GridSizer(3, 2, 10, 10)
        input_grid.Add(wx.StaticText(self, label="Soru:"), 0, wx.ALIGN_CENTER_VERTICAL)
        input_grid.Add(self.soru_text, 1, wx.EXPAND)
        input_grid.Add(wx.StaticText(self, label="Cevap:"), 0, wx.ALIGN_CENTER_VERTICAL)
        input_grid.Add(self.cevap_text, 1, wx.EXPAND)
        input_grid.Add(wx.StaticText(self, label="Ses Dosyası:"), 0, wx.ALIGN_CENTER_VERTICAL)
        input_grid.Add(self.ses_file_picker, 1, wx.EXPAND)

        button_hbox = wx.BoxSizer(wx.HORIZONTAL)
        button_hbox.Add(self.add_button, 1, wx.EXPAND | wx.ALL, 5)
        button_hbox.Add(self.update_button, 1, wx.EXPAND | wx.ALL, 5)
        button_hbox.Add(self.delete_button, 1, wx.EXPAND | wx.ALL, 5)

        vbox.Add(input_grid, 0, wx.EXPAND | wx.ALL, 10)
        vbox.Add(button_hbox, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self.search_ctrl, 0, wx.EXPAND | wx.ALL, 10)
        vbox.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(vbox)
        self.Layout()

        self.load_data()

    def load_data(self):
        self.list_ctrl.DeleteAllItems()
        data = self.data_manager.fetch_all()
        for row in data:
            index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), row[0])
            self.list_ctrl.SetItem(index, 1, row[1])
            self.list_ctrl.SetItem(index, 2, row[2])
            self.list_ctrl.SetItem(index, 3, row[3] if row[3] else "")
        self.list_ctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_ctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_ctrl.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_ctrl.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)

    def on_add(self, event):
        soru = self.soru_text.GetValue().strip()
        cevap = self.cevap_text.GetValue().strip()
        ses_dosyasi = self.ses_file_picker.GetPath()
        
        if not soru or not cevap:
            wx.MessageBox("Soru ve cevap alanları boş bırakılamaz.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        
        if len(soru) < 5:
            wx.MessageBox("Soru en az 5 karakter olmalıdır.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return

        if self.data_manager.add_or_update_entry(soru, cevap, ses_dosyasi if ses_dosyasi else None, self.settings.get("otomatik_kaydetme")):
            self.load_data()
            self.clear_fields()

    def on_update(self, event):
        index = self.list_ctrl.GetFirstSelected()
        if index == -1:
            wx.MessageBox("Lütfen düzenlemek için bir öğe seçin.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        
        soru_old = self.list_ctrl.GetItemText(index, 0)
        soru_new = self.soru_text.GetValue().strip()
        cevap_new = self.cevap_text.GetValue().strip()
        ses_dosyasi_new = self.ses_file_picker.GetPath()
        
        if not soru_new or not cevap_new:
            wx.MessageBox("Soru ve cevap alanları boş bırakılamaz.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return

        self.data_manager.delete_entry(soru_old)
        if self.data_manager.add_or_update_entry(soru_new, cevap_new, ses_dosyasi_new if ses_dosyasi_new else None, self.settings.get("otomatik_kaydetme")):
            self.load_data()
            self.clear_fields()

    def on_delete(self, event):
        index = self.list_ctrl.GetFirstSelected()
        if index == -1:
            wx.MessageBox("Lütfen silmek için bir öğe seçin.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        
        soru = self.list_ctrl.GetItemText(index, 0)
        
        if wx.MessageBox(f"'{soru}' sorusunu silmek istediğinizden emin misiniz?", "Silme Onayı", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            if self.data_manager.delete_entry(soru):
                self.load_data()
                self.clear_fields()

    def on_list_item_selected(self, event):
        index = event.GetIndex()
        soru = self.list_ctrl.GetItemText(index, 0)
        cevap = self.list_ctrl.GetItemText(index, 1)
        ses_dosyasi = self.list_ctrl.GetItemText(index, 3)

        self.soru_text.SetValue(soru)
        self.cevap_text.SetValue(cevap)
        self.ses_file_picker.SetPath(ses_dosyasi)

    def on_search(self, event):
        query = self.search_ctrl.GetValue()
        self.list_ctrl.DeleteAllItems()
        data = self.data_manager.search_entries(query)
        for row in data:
            index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), row[0])
            self.list_ctrl.SetItem(index, 1, row[1])
            self.list_ctrl.SetItem(index, 2, row[2])
            self.list_ctrl.SetItem(index, 3, row[3] if row[3] else "")
        self.list_ctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_ctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_ctrl.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
        self.list_ctrl.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
    
    def clear_fields(self):
        self.soru_text.Clear()
        self.cevap_text.Clear()
        self.ses_file_picker.SetPath("")

class SohbetPanel(BasePanel):
    """Sohbet sekmesi için panel."""
    def __init__(self, parent, data_manager, settings, sound_manager):
        super().__init__(parent, data_manager, settings)
        self.sound_manager = sound_manager

        self.SetAccessible(wx.Accessible(self))
        self.GetAccessible().SetRole(wx.ACC_ROLE_PANE)
        self.GetAccessible().SetName("Sohbet Paneli")
        self.GetAccessible().SetDescription("Robot ile sohbet etmek için kullanılır.")

        self.chat_history = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        self.chat_history.SetAccessible(wx.Accessible(self.chat_history))
        self.chat_history.GetAccessible().SetName("Sohbet Geçmişi")
        self.chat_history.GetAccessible().SetDescription("Kullanıcı ve robot arasındaki mesajları gösterir.")
        
        self.message_input = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
        self.message_input.SetAccessible(wx.Accessible(self.message_input))
        self.message_input.GetAccessible().SetName("Mesaj Giriş Alanı")
        self.message_input.GetAccessible().SetDescription("Robot'a mesajınızı yazın ve göndermek için Enter tuşuna basın.")
        self.message_input.Bind(wx.EVT_TEXT_ENTER, self.on_send)

        send_button = wx.Button(self, label="Gönder")
        send_button.SetAccessible(wx.Accessible(send_button))
        send_button.GetAccessible().SetName("Gönder Butonu")
        send_button.GetAccessible().SetDescription("Mesajınızı robot'a gönderir.")
        self.Bind(wx.EVT_BUTTON, self.on_send, send_button)

        clear_button = wx.Button(self, label="Temizle")
        clear_button.SetAccessible(wx.Accessible(clear_button))
        clear_button.GetAccessible().SetName("Temizle Butonu")
        self.Bind(wx.EVT_BUTTON, self.on_clear, clear_button)

        export_button = wx.Button(self, label="Dışa Aktar")
        export_button.SetAccessible(wx.Accessible(export_button))
        export_button.GetAccessible().SetName("Sohbeti Dışa Aktar Butonu")
        self.Bind(wx.EVT_BUTTON, self.on_export, export_button)

        # Layout
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.chat_history, 1, wx.EXPAND | wx.ALL, 5)

        input_hbox = wx.BoxSizer(wx.HORIZONTAL)
        input_hbox.Add(self.message_input, 1, wx.EXPAND | wx.ALL, 5)
        input_hbox.Add(send_button, 0, wx.ALL, 5)
        
        button_hbox = wx.BoxSizer(wx.HORIZONTAL)
        button_hbox.Add(clear_button, 1, wx.EXPAND | wx.ALL, 5)
        button_hbox.Add(export_button, 1, wx.EXPAND | wx.ALL, 5)

        vbox.Add(input_hbox, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(button_hbox, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(vbox)
        self.Layout()
        
        self.robot_image = wx.Image(os.path.join(APP_DIR, "robot_silhouette.png"), wx.BITMAP_TYPE_PNG).Scale(32, 32).ConvertToBitmap() if os.path.exists(os.path.join(APP_DIR, "robot_silhouette.png")) else None
        self.user_image = wx.Image(os.path.join(APP_DIR, "user_silhouette.png"), wx.BITMAP_TYPE_PNG).Scale(32, 32).ConvertToBitmap() if os.path.exists(os.path.join(APP_DIR, "user_silhouette.png")) else None

    def on_send(self, event):
        user_message = self.message_input.GetValue().strip()
        if not user_message:
            wx.MessageBox("Boş mesaj gönderilemez.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return

        self.append_message("Kullanıcı", user_message, (0, 0, 255), self.user_image)
        self.message_input.Clear()
        
        # Yanıtı al ve bekleme süresini ayarla
        robot_response, sound_file = self.data_manager.get_response(user_message)
        response_delay = self.settings.get("yanit_hizi", 0)

        # Yanıtı bir thread'de işle
        wx.CallLater(int(response_delay * 1000), self.process_robot_response, robot_response, sound_file)
        
    def process_robot_response(self, robot_response, sound_file):
        if robot_response:
            response_text = robot_response
            if sound_file and os.path.exists(sound_file):
                self.sound_manager.play_sound(sound_file)
        else:
            response_text = "Bu konuyu bilmiyorum, bana öğretmek ister miydiniz?"
            if self.settings.get("rastgele_ses_oynatma"):
                self.sound_manager.play_random_sound()
        
        self.append_message("Robot", response_text, (0, 128, 0), self.robot_image)

    def append_message(self, speaker, message, color, image_bitmap):
        # Profil resmi ekle
        if image_bitmap:
            self.chat_history.BeginAlignment(wx.ALIGN_LEFT if speaker == "Robot" else wx.ALIGN_RIGHT)
            self.chat_history.WriteImage(image_bitmap)
            self.chat_history.EndAlignment()

        # Metni ekle ve renklendir
        self.chat_history.BeginAll()
        self.chat_history.BeginTextColour(color)
        self.chat_history.AppendText(f"{speaker}: {message}\n\n")
        self.chat_history.EndTextColour()
        self.chat_history.EndAll()
        
        # Otomatik aşağı kaydırma
        self.chat_history.SetInsertionPointEnd()

    def on_clear(self, event):
        self.chat_history.Clear()
        self.data_manager.post_status_message("Sohbet geçmişi temizlendi.", 2000)

    def on_export(self, event):
        with wx.FileDialog(self, "Sohbet Geçmişini Kaydet", wildcard="Metin Dosyaları (*.txt)|*.txt",
                           defaultFile="chat_history.txt", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            
            pathname = dlg.GetPath()
            try:
                with open(pathname, 'w', encoding='utf-8') as f:
                    f.write(self.chat_history.GetValue())
                wx.MessageBox("Dışa aktarma tamamlandı.", "Başarılı", wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                logging.error(f"Sohbet dışa aktarma hatası: {e}")
                wx.MessageBox("Sohbet geçmişi kaydedilirken bir hata oluştu.", "Hata", wx.OK | wx.ICON_ERROR)

class AyarlarPanel(BasePanel):
    """Ayarlar sekmesi için panel."""
    def __init__(self, parent, data_manager, settings, sound_manager):
        super().__init__(parent, data_manager, settings)
        self.sound_manager = sound_manager
        self.settings = settings

        self.SetAccessible(wx.Accessible(self))
        self.GetAccessible().SetRole(wx.ACC_ROLE_PANE)
        self.GetAccessible().SetName("Ayarlar Paneli")
        self.GetAccessible().SetDescription("Robot ve uygulamanın genel ayarlarını düzenlemek için kullanılır.")
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        grid_sizer = wx.GridBagSizer(5, 5)

        # Yanıt Hızı
        grid_sizer.Add(wx.StaticText(self, label="Yanıt Hızı (sn):"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.response_speed_slider = wx.Slider(self, value=self.settings.get("yanit_hizi"), minValue=0, maxValue=5, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        grid_sizer.Add(self.response_speed_slider, pos=(0, 1), flag=wx.EXPAND)
        self.Bind(wx.EVT_SLIDER, self.on_setting_changed, self.response_speed_slider)
        
        # Arka Plan Rengi
        grid_sizer.Add(wx.StaticText(self, label="Arka Plan Rengi:"), pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.bg_color_picker = wx.ColourPickerCtrl(self, colour=self.settings.get("arkaplan_rengi"))
        grid_sizer.Add(self.bg_color_picker, pos=(1, 1), flag=wx.EXPAND)
        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.on_setting_changed, self.bg_color_picker)

        # Yazı Tipi Boyutu
        grid_sizer.Add(wx.StaticText(self, label="Yazı Tipi Boyutu:"), pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.font_size_spin = wx.SpinCtrl(self, value=self.settings.get("yazi_tipi_boyutu"), min=8, max=24)
        grid_sizer.Add(self.font_size_spin, pos=(2, 1), flag=wx.EXPAND)
        self.Bind(wx.EVT_SPINCTRL, self.on_setting_changed, self.font_size_spin)

        # Otomatik Kaydetme
        self.auto_save_checkbox = wx.CheckBox(self, label="Robota Öğret Sekmesinde Otomatik Kaydet")
        self.auto_save_checkbox.SetValue(self.settings.get("otomatik_kaydetme"))
        grid_sizer.Add(self.auto_save_checkbox, pos=(3, 0), span=(1, 2), flag=wx.EXPAND)
        self.Bind(wx.EVT_CHECKBOX, self.on_setting_changed, self.auto_save_checkbox)

        # Espri Sıklığı
        grid_sizer.Add(wx.StaticText(self, label="Espri Sıklığı (dk):"), pos=(4, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.joke_frequency_slider = wx.Slider(self, value=self.settings.get("espri_sikligi"), minValue=1, maxValue=10, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        grid_sizer.Add(self.joke_frequency_slider, pos=(4, 1), flag=wx.EXPAND)
        self.Bind(wx.EVT_SLIDER, self.on_setting_changed, self.joke_frequency_slider)

        # Rastgele Ses Oynatma
        self.random_sound_checkbox = wx.CheckBox(self, label="Sohbet Eşleşmesi Bulunamadığında Rastgele Ses Oynat")
        self.random_sound_checkbox.SetValue(self.settings.get("rastgele_ses_oynatma"))
        grid_sizer.Add(self.random_sound_checkbox, pos=(5, 0), span=(1, 2), flag=wx.EXPAND)
        self.Bind(wx.EVT_CHECKBOX, self.on_setting_changed, self.random_sound_checkbox)

        # Yeni Espri Ekleme
        grid_sizer.Add(wx.StaticText(self, label="Yeni Espri:"), pos=(6, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        self.new_joke_input = wx.TextCtrl(self)
        grid_sizer.Add(self.new_joke_input, pos=(6, 1), flag=wx.EXPAND)
        add_joke_button = wx.Button(self, label="Ekle")
        grid_sizer.Add(add_joke_button, pos=(7, 1), flag=wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.on_add_joke, add_joke_button)

        # Veritabanı Sıfırlama
        reset_db_button = wx.Button(self, label="Veritabanını Sıfırla")
        grid_sizer.Add(reset_db_button, pos=(8, 0), span=(1, 2), flag=wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.on_reset_db, reset_db_button)

        vbox.Add(grid_sizer, 0, wx.EXPAND | wx.ALL, 15)
        vbox.AddStretchSpacer(1)
        self.SetSizer(vbox)
        self.Layout()

    def on_setting_changed(self, event):
        self.settings["yanit_hizi"] = self.response_speed_slider.GetValue()
        self.settings["arkaplan_rengi"] = self.bg_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.settings["yazi_tipi_boyutu"] = self.font_size_spin.GetValue()
        self.settings["otomatik_kaydetme"] = self.auto_save_checkbox.GetValue()
        self.settings["espri_sikligi"] = self.joke_frequency_slider.GetValue()
        self.settings["rastgele_ses_oynatma"] = self.random_sound_checkbox.GetValue()
        
        self.data_manager.save_json(SETTINGS_JSON, self.settings)
        wx.PostEvent(self.GetParent().GetParent().GetEventHandler(), UpdateUIEvent())

    def on_add_joke(self, event):
        new_joke = self.new_joke_input.GetValue().strip()
        if new_joke:
            jokes = self.data_manager.load_json(JOKES_JSON, DEFAULT_JOKES)
            jokes.append(new_joke)
            if self.data_manager.save_json(JOKES_JSON, jokes):
                self.new_joke_input.Clear()
                self.data_manager.post_status_message("Espri eklendi.", 2000)
        else:
            wx.MessageBox("Espri boş bırakılamaz.", "Uyarı", wx.OK | wx.ICON_WARNING)

    def on_reset_db(self, event):
        if wx.MessageBox("Veritabanını sıfırlamak istediğinizden emin misiniz? Bu işlem geri alınamaz.", "Onay", wx.YES_NO | wx.ICON_EXCLAMATION) == wx.YES:
            try:
                if os.path.exists(DB_PATH):
                    os.remove(DB_PATH)
                self.data_manager.connect_db()
                self.data_manager.post_status_message("Veritabanı sıfırlandı.", 3000)
            except Exception as e:
                logging.error(f"Veritabanı sıfırlama hatası: {e}")
                wx.MessageBox("Veritabanı sıfırlanırken bir hata oluştu.", "Hata", wx.OK | wx.ICON_ERROR)

class SoundManager:
    """Pygame ile sesleri yönetir."""
    def __init__(self):
        self.is_ready = False
        self.joke_timer = None
        self.jokes = []

        if pygame and not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
                self.is_ready = True
            except pygame.error as e:
                logging.error(f"Pygame başlatma hatası: {e}")
                self.is_ready = False
        else:
            self.is_ready = True

    def play_sound(self, file_path):
        if not self.is_ready or not os.path.exists(file_path):
            return
        
        try:
            sound = pygame.mixer.Sound(file_path)
            sound.play()
        except Exception as e:
            logging.error(f"Ses oynatma hatası ({file_path}): {e}")

    def load_jokes(self, jokes):
        self.jokes = jokes

    def start_joke_timer(self, interval_min):
        if self.joke_timer:
            self.joke_timer.cancel()
        
        if interval_min > 0 and self.jokes:
            interval_sec = interval_min * 60
            self.joke_timer = threading.Timer(interval_sec, self.show_random_joke)
            self.joke_timer.daemon = True
            self.joke_timer.start()

    def show_random_joke(self):
        if self.jokes:
            joke = random.choice(self.jokes)
            wx.CallAfter(wx.GetApp().GetTopWindow().GetStatusBar().SetStatusText, joke)
            wx.CallLater(5000, wx.GetApp().GetTopWindow().GetStatusBar().SetStatusText, "")
        
        # Sonraki espri için zamanlayıcıyı yeniden başlat
        self.start_joke_timer(wx.GetApp().settings.get("espri_sikligi"))

    def play_random_sound(self):
        if not self.is_ready:
            return
        
        try:
            sound_files = [os.path.join(SOUNDS_DIR, f) for f in os.listdir(SOUNDS_DIR) if f.endswith('.wav')]
            if sound_files:
                sound_file = random.choice(sound_files)
                self.play_sound(sound_file)
        except Exception as e:
            logging.error(f"Rastgele ses oynatma hatası: {e}")

class SeslerPanel(BasePanel):
    """Sesler sekmesi için panel."""
    def __init__(self, parent, data_manager, settings, sound_manager):
        super().__init__(parent, data_manager, settings)
        self.sound_manager = sound_manager

        self.SetAccessible(wx.Accessible(self))
        self.GetAccessible().SetRole(wx.ACC_ROLE_PANE)
        self.GetAccessible().SetName("Sesler Paneli")

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.file_picker = wx.FilePickerCtrl(self, message="Ses Dosyası Ekle...", wildcard="WAV dosyaları (*.wav)|*.wav", style=wx.FLP_DEFAULT_STYLE | wx.FLP_OPEN)
        self.file_picker.SetAccessible(wx.Accessible(self.file_picker))
        self.file_picker.GetAccessible().SetName("Ses Dosyası Seçici")
        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.on_file_selected, self.file_picker)

        self.sound_listbox = wx.ListBox(self, choices=[], style=wx.LB_SINGLE)
        self.sound_listbox.SetAccessible(wx.Accessible(self.sound_listbox))
        self.sound_listbox.GetAccessible().SetName("Mevcut Sesler Listesi")

        button_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.play_button = wx.Button(self, label="Oynat")
        self.play_button.SetAccessible(wx.Accessible(self.play_button))
        self.play_button.GetAccessible().SetName("Sesi Oynat")
        self.play_button.Bind(wx.EVT_BUTTON, self.on_play_sound)

        self.add_button = wx.Button(self, label="Ekle")
        self.add_button.SetAccessible(wx.Accessible(self.add_button))
        self.add_button.GetAccessible().SetName("Sesi Ekle")
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add_sound)

        self.delete_button = wx.Button(self, label="Sil")
        self.delete_button.SetAccessible(wx.Accessible(self.delete_button))
        self.delete_button.GetAccessible().SetName("Sesi Sil")
        self.delete_button.Bind(wx.EVT_BUTTON, self.on_delete_sound)

        button_hbox.Add(self.play_button, 1, wx.EXPAND | wx.ALL, 5)
        button_hbox.Add(self.add_button, 1, wx.EXPAND | wx.ALL, 5)
        button_hbox.Add(self.delete_button, 1, wx.EXPAND | wx.ALL, 5)

        vbox.Add(self.file_picker, 0, wx.EXPAND | wx.ALL, 10)
        vbox.Add(self.sound_listbox, 1, wx.EXPAND | wx.ALL, 10)
        vbox.Add(button_hbox, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(vbox)
        self.load_sounds()
    
    def load_sounds(self):
        self.sound_listbox.Clear()
        try:
            files = sorted([f for f in os.listdir(SOUNDS_DIR) if f.endswith('.wav')])
            self.sound_listbox.Set(files)
        except FileNotFoundError:
            self.data_manager.post_status_message("Ses klasörü bulunamadı.", 3000)

    def on_file_selected(self, event):
        path = self.file_picker.GetPath()
        if path:
            self.add_button.Enable()
        else:
            self.add_button.Disable()
    
    def on_add_sound(self, event):
        src_path = self.file_picker.GetPath()
        if not src_path:
            return
        
        dst_path = os.path.join(SOUNDS_DIR, os.path.basename(src_path))
        try:
            shutil.copy(src_path, dst_path)
            self.data_manager.post_status_message(f"{os.path.basename(src_path)} eklendi.", 2000)
            self.load_sounds()
        except Exception as e:
            logging.error(f"Ses dosyası kopyalama hatası: {e}")
            wx.MessageBox("Ses dosyası eklenirken bir hata oluştu.", "Hata", wx.OK | wx.ICON_ERROR)

    def on_play_sound(self, event):
        selection = self.sound_listbox.GetStringSelection()
        if selection:
            sound_path = os.path.join(SOUNDS_DIR, selection)
            self.sound_manager.play_sound(sound_path)
        else:
            wx.MessageBox("Oynatmak için bir ses dosyası seçin.", "Uyarı", wx.OK | wx.ICON_WARNING)

    def on_delete_sound(self, event):
        selection = self.sound_listbox.GetStringSelection()
        if selection:
            if wx.MessageBox(f"'{selection}' ses dosyasını silmek istediğinizden emin misiniz?", "Silme Onayı", wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
                try:
                    os.remove(os.path.join(SOUNDS_DIR, selection))
                    self.data_manager.post_status_message(f"{selection} silindi.", 2000)
                    self.load_sounds()
                except OSError as e:
                    logging.error(f"Ses dosyası silme hatası: {e}")
                    wx.MessageBox("Ses dosyası silinirken bir hata oluştu.", "Hata", wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox("Silmek için bir ses dosyası seçin.", "Uyarı", wx.OK | wx.ICON_WARNING)

class MotorPanel(BasePanel):
    """Motor Koordinasyon Hareketleri sekmesi için panel."""
    def __init__(self, parent, data_manager, settings):
        super().__init__(parent, data_manager, settings)
        self.motor_settings = self.data_manager.load_json(MOTOR_SETTINGS_JSON, DEFAULT_MOTOR_SETTINGS)

        self.SetAccessible(wx.Accessible(self))
        self.GetAccessible().SetRole(wx.ACC_ROLE_PANE)
        self.GetAccessible().SetName("Motor Paneli")
        self.GetAccessible().SetDescription("Sanal robot motor ayarlarını yönetmek için kullanılır.")
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.tree_ctrl = wx.TreeCtrl(self, style=wx.TR_HIDE_ROOT | wx.TR_DEFAULT_STYLE)
        self.tree_ctrl.SetAccessible(wx.Accessible(self.tree_ctrl))
        self.tree_ctrl.GetAccessible().SetName("Motor Ağacı")

        root = self.tree_ctrl.AddRoot("Motorlar")
        for category, motors in self.motor_settings.items():
            cat_item = self.tree_ctrl.AppendItem(root, category)
            for motor_name, angles in motors.items():
                self.tree_ctrl.AppendItem(cat_item, motor_name, data=angles)
        
        self.tree_ctrl.ExpandAll()
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_item_selected, self.tree_ctrl)

        self.min_spin = wx.SpinCtrl(self, min=0, max=360)
        self.max_spin = wx.SpinCtrl(self, min=0, max=360)

        grid_sizer = wx.GridBagSizer(5, 5)
        grid_sizer.Add(wx.StaticText(self, label="Min. Açı:"), pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.min_spin, pos=(0, 1), flag=wx.EXPAND)
        grid_sizer.Add(wx.StaticText(self, label="Max. Açı:"), pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.max_spin, pos=(1, 1), flag=wx.EXPAND)

        button_hbox = wx.BoxSizer(wx.HORIZONTAL)
        apply_button = wx.Button(self, label="Uygula")
        test_button = wx.Button(self, label="Test Et")
        self.Bind(wx.EVT_BUTTON, self.on_apply, apply_button)
        self.Bind(wx.EVT_BUTTON, self.on_test, test_button)
        button_hbox.Add(apply_button, 1, wx.EXPAND | wx.ALL, 5)
        button_hbox.Add(test_button, 1, wx.EXPAND | wx.ALL, 5)

        vbox.Add(self.tree_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        vbox.Add(grid_sizer, 0, wx.EXPAND | wx.ALL, 10)
        vbox.Add(button_hbox, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(vbox)
        self.Layout()

    def on_tree_item_selected(self, event):
        item = event.GetItem()
        if self.tree_ctrl.GetItemParent(item) != self.tree_ctrl.GetRootItem() and item:
            data = self.tree_ctrl.GetItemData(item)
            if data and isinstance(data, list) and len(data) == 2:
                self.min_spin.SetValue(data[0])
                self.max_spin.SetValue(data[1])
            else:
                self.min_spin.SetValue(0)
                self.max_spin.SetValue(180)

    def on_apply(self, event):
        item = self.tree_ctrl.GetSelection()
        if not item or self.tree_ctrl.GetItemParent(item) == self.tree_ctrl.GetRootItem():
            wx.MessageBox("Lütfen bir motor seçin.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return

        min_val = self.min_spin.GetValue()
        max_val = self.max_spin.GetValue()
        
        if min_val > max_val:
            wx.MessageBox("Minimum açı, maksimum açıdan büyük olamaz.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return

        motor_name = self.tree_ctrl.GetItemText(item)
        category_item = self.tree_ctrl.GetItemParent(item)
        category_name = self.tree_ctrl.GetItemText(category_item)

        self.motor_settings[category_name][motor_name] = [min_val, max_val]
        
        if self.data_manager.save_json(MOTOR_SETTINGS_JSON, self.motor_settings):
            self.data_manager.post_status_message("Motor ayarları kaydedildi.", 2000)
        
        # Ağaçtaki veriyi güncelle
        self.tree_ctrl.SetItemData(item, [min_val, max_val])

    def on_test(self, event):
        item = self.tree_ctrl.GetSelection()
        if not item or self.tree_ctrl.GetItemParent(item) == self.tree_ctrl.GetRootItem():
            wx.MessageBox("Lütfen test etmek için bir motor seçin.", "Uyarı", wx.OK | wx.ICON_WARNING)
            return
        
        motor_name = self.tree_ctrl.GetItemText(item)
        min_val, max_val = self.tree_ctrl.GetItemData(item)

        status_text = f"Sanal motor hareketi: {motor_name} {min_val} derece ile {max_val} derece arasında hareket ediyor."
        print(status_text)
        self.data_manager.post_status_message(status_text, 5000)


class MainFrame(wx.Frame):
    """Ana uygulama penceresi."""
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(800, 600))
        self.SetMinSize((600, 400))
        self.Centre()
        
        self.data_manager = DataManager()
        self.settings = self.data_manager.load_json(SETTINGS_JSON, DEFAULT_SETTINGS)
        
        # Tema uyumluluğu
        if wx.SystemSettings.GetAppearance().IsDark():
            self.settings["theme"] = "dark"
        else:
            self.settings["theme"] = "light"
        
        # Pygame ses yöneticisini başlat
        self.sound_manager = SoundManager()
        self.sound_manager.load_jokes(self.data_manager.load_json(JOKES_JSON, DEFAULT_JOKES))
        self.sound_manager.start_joke_timer(self.settings.get("espri_sikligi"))

        # Pencere simgesi
        if getattr(sys, 'frozen', False):
            # PyInstaller ile paketlendiğinde
            icon_path = os.path.join(sys._MEIPASS, 'robot_icon.ico')
        else:
            icon_path = os.path.join(APP_DIR, 'robot_icon.ico')
            # Varsayılan ikon dosyası yoksa oluştur
            if not os.path.exists(icon_path):
                # Örnek bir ikon oluşturma (sadece bir placeholder)
                icon_image = wx.Bitmap(32, 32)
                dc = wx.MemoryDC(icon_image)
                dc.SetBackground(wx.Brush(wx.BLUE))
                dc.Clear()
                dc.DrawCircle(16, 16, 14)
                dc.DrawLine(5, 16, 27, 16)
                dc.SetTextForeground(wx.WHITE)
                dc.DrawText("R", 10, 10)
                icon = wx.Icon(icon_image)
                icon.SaveFile(icon_path, wx.BITMAP_TYPE_ICO)

        if os.path.exists(icon_path):
            self.SetIcon(wx.Icon(icon_path))
        
        self.CreateStatusBar()
        self.GetStatusBar().SetStatusText("Hazır")

        self.setup_menu()
        self.setup_ui()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(EVT_UPDATE_UI, self.on_update_ui)

        # Klavye kısayolları
        self.accel_table = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('S'), self.FindWindowByName('send_button').GetId() if self.FindWindowByName('send_button') else wx.ID_ANY),
            (wx.ACCEL_CTRL, ord('N'), self.FindWindowByName('add_button').GetId() if self.FindWindowByName('add_button') else wx.ID_ANY),
            (wx.ACCEL_ALT, ord('T'), self.on_collect_json),
            (wx.ACCEL_CTRL, ord('Q'), self.on_exit),
        ])
        self.SetAcceleratorTable(self.accel_table)

    def setup_menu(self):
        menu_bar = wx.MenuBar()

        file_menu = wx.Menu()
        exit_item = file_menu.Append(wx.ID_EXIT, "Çıkış\tCtrl+Q", "Uygulamadan çık")
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)

        edit_menu = wx.Menu()
        clear_item = edit_menu.Append(wx.ID_CLEAR, "Temizle", "Seçili alanı temizler")
        self.Bind(wx.EVT_MENU, self.on_clear_selection, clear_item)
        
        collect_json_item = edit_menu.Append(wx.ID_ANY, "JSON'ları Topla\tAlt+T", "Tüm JSON verilerini veritabanına aktarır.")
        self.Bind(wx.EVT_MENU, self.on_collect_json, collect_json_item)

        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "Hakkında", "Uygulama hakkında bilgi")
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

        menu_bar.Append(file_menu, "Dosya")
        menu_bar.Append(edit_menu, "Düzenle")
        menu_bar.Append(help_menu, "Yardım")
        self.SetMenuBar(menu_bar)

    def setup_ui(self):
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Sol Taraf: Kategori Listesi
        self.categories = ["Robota Öğret", "Sohbet", "Ayarlar", "Sesler", "Motor Koordinasyon Hareketleri"]
        self.list_box = wx.ListBox(self, choices=self.categories, style=wx.LB_SINGLE)
        self.list_box.SetAccessible(wx.Accessible(self.list_box))
        self.list_box.GetAccessible().SetName("Kategori Listesi")
        self.list_box.GetAccessible().SetDescription("Uygulama işlevleri arasında gezinmek için bir liste.")
        self.Bind(wx.EVT_LISTBOX, self.on_category_selected, self.list_box)

        # Sağ Taraf: Dinamik Paneller
        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE | wx.SP_3D)
        
        left_panel = wx.Panel(self.splitter)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.list_box, 1, wx.EXPAND | wx.ALL, 5)
        left_panel.SetSizer(left_sizer)

        self.right_panel_container = wx.Panel(self.splitter)
        self.right_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_panel_container.SetSizer(self.right_panel_sizer)

        self.panels = {
            "Robota Öğret": OgretPanel(self.right_panel_container, self.data_manager, self.settings),
            "Sohbet": SohbetPanel(self.right_panel_container, self.data_manager, self.settings, self.sound_manager),
            "Ayarlar": AyarlarPanel(self.right_panel_container, self.data_manager, self.settings, self.sound_manager),
            "Sesler": SeslerPanel(self.right_panel_container, self.data_manager, self.settings, self.sound_manager),
            "Motor Koordinasyon Hareketleri": MotorPanel(self.right_panel_container, self.data_manager, self.settings)
        }

        for panel in self.panels.values():
            self.right_panel_sizer.Add(panel, 1, wx.EXPAND | wx.ALL, 5)
            panel.Hide()

        self.splitter.SplitVertically(left_panel, self.right_panel_container, 200)

        main_sizer.Add(self.splitter, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()

        # Varsayılan olarak Sohbet panelini göster
        self.on_category_selected(None, category="Sohbet")
        self.list_box.SetSelection(1)

    def on_category_selected(self, event, category=None):
        if not category:
            category = self.list_box.GetStringSelection()
        
        self.SetTitle(f"Robot Yazılımı - {category}")
        
        for panel_name, panel in self.panels.items():
            if panel_name == category:
                panel.Show()
                panel.GetParent().Layout()
            else:
                panel.Hide()
        
        self.right_panel_container.Layout()
        
        if event:
            # NVDA için odak ayarı
            wx.CallAfter(self.panels[category].SetFocus)
            
    def on_update_ui(self, event):
        # Ayarlar değiştiğinde tüm panellerin arayüzünü güncelle
        for panel in self.panels.values():
            wx.PostEvent(panel.GetEventHandler(), UpdateUIEvent())

    def on_collect_json(self, event):
        self.data_manager.import_json_data()
        self.panels["Robota Öğret"].load_data()

    def on_clear_selection(self, event):
        focused_window = self.FindFocus()
        if isinstance(focused_window, wx.TextCtrl):
            focused_window.Clear()
        
    def on_about(self, event):
        about_info = wx.adv.AboutDialogInfo()
        about_info.Name = "Robot Yazılımı"
        about_info.Version = "1.0"
        about_info.Copyright = f"(C) 2024, Python Geliştiricisi"
        about_info.Description = "Gelişmiş özelliklere sahip kullanıcı dostu bir robot uygulamasıdır."
        about_info.WebSite = "https://github.com/ornek-kullanici/robot-yazilimi"
        about_info.Developers = ["AI Robot Yazılımcı"]
        wx.adv.AboutBox(about_info)

    def on_exit(self, event):
        self.Close()
        
    def on_close(self, event):
        self.data_manager.close_db()
        self.sound_manager.joke_timer.cancel()
        event.Skip()

# Ana uygulama sınıfı
class RobotApp(wx.App):
    def OnInit(self):
        # Uygulama başlatıldığında varsayılan ayarları yükle
        self.settings = DataManager().load_json(SETTINGS_JSON, DEFAULT_SETTINGS)
        # Sistem teması kontrolü
        self.settings["theme"] = "dark" if wx.SystemSettings.GetAppearance().IsDark() else "light"

        # PyInstaller konsol sorununu çözme
        if getattr(sys, 'frozen', False):
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')

        # Varsayılan dosya yoksa oluştur
        self.create_default_files()
        
        main_frame = MainFrame(None, "Robot Yazılımı")
        main_frame.Show(True)
        return True

    def create_default_files(self):
        # Eğer yoksa varsayılan JSON dosyalarını oluştur
        DataManager().save_json(JOKES_JSON, DataManager().load_json(JOKES_JSON, DEFAULT_JOKES))
        DataManager().save_json(SETTINGS_JSON, DataManager().load_json(SETTINGS_JSON, DEFAULT_SETTINGS))
        DataManager().save_json(MOTOR_SETTINGS_JSON, DataManager().load_json(MOTOR_SETTINGS_JSON, DEFAULT_MOTOR_SETTINGS))
        DataManager().save_json(ROBOT_DATA_JSON, {}) # Boş başlat
        
        # Varsayılan siluet resimleri oluştur
        user_img_path = os.path.join(APP_DIR, 'user_silhouette.png')
        robot_img_path = os.path.join(APP_DIR, 'robot_silhouette.png')
        if not os.path.exists(user_img_path):
            img = wx.Bitmap(32, 32)
            dc = wx.MemoryDC(img)
            dc.SetBackground(wx.Brush(wx.LIGHT_GREY))
            dc.Clear()
            dc.SetBrush(wx.Brush(wx.GREY))
            dc.DrawCircle(16, 10, 8)
            dc.DrawRectangle(8, 18, 16, 12)
            img.SaveFile(user_img_path, wx.BITMAP_TYPE_PNG)

        if not os.path.exists(robot_img_path):
            img = wx.Bitmap(32, 32)
            dc = wx.MemoryDC(img)
            dc.SetBackground(wx.Brush(wx.BLACK))
            dc.Clear()
            dc.SetBrush(wx.Brush(wx.GREEN))
            dc.DrawRectangle(6, 6, 20, 20)
            img.SaveFile(robot_img_path, wx.BITMAP_TYPE_PNG)
            
if __name__ == '__main__':
    app = RobotApp(False)
    app.MainLoop()