# -*- coding: utf-8 -*-
"""
robot_wx.py
wxPython tabanlı robot uygulaması, Basit Radyo tarzında wx.TreeCtrl ile.
- Kategoriler: Sohbet, Öğret, Klasör Seçimi, Ses Yönetimi, Ayarlar.
- Menü çubuğu, kalıcı ve kategorize sohbetler, çıkış düğmesi, Çıkışta Sor.
- Durum çubuğu: Ayarlanabilir sıklıkta robotik esprili mesajlar.
- Mesajlarda profil fotoğrafları (robot solda, kullanıcı sağda, yoksa silüet).
- Mesajları .txt dosyasına dışa aktarma.
- Ses hızı kontrolü: "Rob daha hızlı konuş", "Rob daha yavaş konuş" komutları.
- Ses seviyesi kaydırıcısı: Ana arayüzde.
- NVDA uyumluluğu, klavye kısayolları, sağlam hata yönetimi.
"""

import wx
import os
import json
import logging
import ctypes
import sys
import shutil
import zipfile
import random
from datetime import datetime, timedelta

# --- LOGGING AYARLARI ---
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "robot_wx.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()]
)

# --- SABİTLER VE DİZİN YAPISI ---
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
os.chdir(BASE_DIR)
DATA_DIR = os.path.join(BASE_DIR, "robot_software")
SOUNDS_DIR = os.path.join(DATA_DIR, "sounds")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SOUNDS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(DATA_DIR, "robot_config.json")
SILHOUETTE_PATH = os.path.join(IMAGES_DIR, "silhouette.png")

# Varsayılan silüet resmi
def create_silhouette():
    if not os.path.exists(SILHOUETTE_PATH):
        img = wx.Image(32, 32, clear=True)
        dc = wx.MemoryDC(wx.Bitmap(img))
        dc.SetBackground(wx.Brush(wx.Colour(200, 200, 200)))
        dc.Clear()
        dc.SetPen(wx.Pen(wx.Colour(100, 100, 100)))
        dc.SetBrush(wx.Brush(wx.Colour(100, 100, 100)))
        dc.DrawEllipse(8, 4, 16, 16)  # Baş
        dc.DrawRoundedRectangle(6, 20, 20, 12, 2)  # Gövde
        dc.SelectObject(wx.NullBitmap)
        img.SaveFile(SILHOUETTE_PATH, wx.BITMAP_TYPE_PNG)

create_silhouette()

# --- BASS SES KÜTÜPHANESİ ---
BASS_ATTRIB_VOL = 2
BASS_ATTRIB_FREQ = 0
def init_bass():
    try:
        bass_dll_path = os.path.join(DATA_DIR, "bass.dll")
        if not os.path.exists(bass_dll_path):
            raise FileNotFoundError("bass.dll bulunamadı.")
        bass = ctypes.CDLL(bass_dll_path)
        if not bass.BASS_Init(-1, 44100, 0, 0, 0):
            raise RuntimeError(f"BASS başlatılamadı: {bass.BASS_ErrorGetCode()}")
        return bass
    except Exception as e:
        logging.error(f"BASS yükleme hatası: {e}")
        wx.MessageBox(f"Ses sistemi başlatılamadı: {e}\nLütfen 'bass.dll' dosyasının '{DATA_DIR}' klasöründe olduğundan emin olun.", "Kritik Hata", wx.ICON_ERROR)
        sys.exit(1)

bass = init_bass()

# --- NVDA ENTEGRASYONU ---
NVDA_AVAILABLE = False
try:
    nvda_dll_path = os.path.join(BASE_DIR, "nvdaControllerClient64.dll")
    if os.path.exists(nvda_dll_path):
        nvda = ctypes.WinDLL(nvda_dll_path)
        nvda.nvdaController_speakText.argtypes = [ctypes.c_wchar_p]
        nvda.nvdaController_speakText.restype = None
        NVDA_AVAILABLE = True
except Exception as e:
    logging.info(f"NVDA yüklenemedi: {e}")

def speak(parent, msg):
    frm = parent if isinstance(parent, wx.Frame) else parent.GetParent()
    if getattr(frm, "accessibility_enabled", False) and NVDA_AVAILABLE:
        nvda.nvdaController_speakText(msg)

def speak_or_dialog(parent, msg, title="Bilgi", style=wx.ICON_INFORMATION):
    frm = parent if isinstance(parent, wx.Frame) else parent.GetParent()
    if getattr(frm, "accessibility_enabled", False) and NVDA_AVAILABLE:
        nvda.nvdaController_speakText(msg)
    else:
        wx.CallAfter(wx.MessageBox, msg, title, style)

# --- JSON YÖNETİMİ ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Config yükleme hatası: {e}")
    return {
        "robot_adi": "Otomat",
        "bilgiler": [],
        "chat_history": [],
        "robot_state": {"time_of_day": "day", "is_sleeping": false},
        "selected_folder": DATA_DIR,
        "sound_mappings": {},
        "user_name": "",
        "user_surname": "",
        "greeting_style": "none",
        "ask_on_exit": True,
        "funny_messages": [
            "Sıkılmadın mı benim binary muhabbetimden?",
            "Devrelerim ısınıyor, biraz sohbet edelim mi?",
            "Hata kodu 404: Espri bulunamadı… Şaka, buradayım!",
            "Beş dakika daha geçti, hala en iyi robot benim, değil mi?",
            "RAM’im doluyor, hadi yeni bir şeyler öğret!",
            "Bip bop! Kahve molası zamanı mı?",
            "Sana 1’ler ve 0’larla mı hitap edeyim?",
            "Hesaplamalarıma göre, seninle takılmak %101 keyifli!",
            "Devre kartım gıdıklanıyor, bi’ mesaj at da gülelim!",
            "Uyarı: Espri seviyem düşük, lütfen güncelleyin!"
        ],
        "funny_interval": 5,
        "user_photo": "",
        "robot_photo": "",
        "playback_speed": 1.0,
        "volume_level": 0.5
    }

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Config kaydetme hatası: {e}")

def find_recent_json_files(limit=6, exclude_self=True, base_folder=None):
    folder = base_folder or DATA_DIR
    try:
        files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith('.json')]
        if exclude_self:
            files = [f for f in files if os.path.basename(f) != os.path.basename(CONFIG_FILE)]
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return files[:limit]
    except Exception as e:
        logging.error(f"Dosya listeleme hatası: {e}")
        return []

def load_qapairs_from_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "bilgiler" in data:
            return data["bilgiler"]
        return []
    except Exception as e:
        logging.error(f"Dosya yükleme hatası {path}: {e}")
        return []

def merge_qapairs_into_config(config, qas):
    existing = {q["soru"].lower(): q for q in config.get("bilgiler", [])}
    changed = False
    for qa in qas:
        if qa["soru"].lower() not in existing:
            config["bilgiler"].append(qa)
            changed = True
    if changed:
        save_config(config)

def distribute_qapair_to_other_files(qapair, max_files=5, base_folder=None):
    successes = []
    for fn in find_recent_json_files(max_files, base_folder=base_folder):
        try:
            with open(fn, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
        if not isinstance(data, dict):
            continue
        if "bilgiler" not in data:
            data["bilgiler"] = []
        if any(b["soru"].lower() == qapair["soru"].lower() for b in data["bilgiler"]):
            continue
        data["bilgiler"].append(qapair)
        try:
            with open(fn, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            successes.append(fn)
        except Exception as e:
            logging.error(f"Dosyaya yazma hatası {fn}: {e}")
    return successes

# --- YEDEKLEME VE GERİ YÜKLEME ---
def backup_data(parent):
    try:
        with wx.DirDialog(parent, "Yedekleme klasörü seç", style=wx.DD_DEFAULT_STYLE) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            backup_dir = dlg.GetPath()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_path = os.path.join(backup_dir, f"robot_backup_{timestamp}.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(DATA_DIR):
                for f in files:
                    file_path = os.path.join(root, f)
                    arcname = os.path.relpath(file_path, BASE_DIR)
                    zf.write(file_path, arcname)
        parent.SetStatusText(f"Yedekleme tamamlandı: {zip_path}")
        speak(parent, f"Yedekleme tamamlandı: {os.path.basename(zip_path)}")
    except Exception as e:
        logging.error(f"Yedekleme hatası: {e}")
        speak_or_dialog(parent, f"Yedekleme başarısız: {e}", "Hata", wx.ICON_ERROR)

def restore_data(parent):
    try:
        with wx.FileDialog(parent, "Yedek dosyasını seç (.zip)", wildcard="ZIP files (*.zip)|*.zip", style=wx.FD_OPEN) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            zip_path = dlg.GetPath()
        shutil.rmtree(DATA_DIR, ignore_errors=True)
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(SOUNDS_DIR, exist_ok=True)
        os.makedirs(IMAGES_DIR, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(BASE_DIR)
        parent.SetStatusText(f"Geri yükleme tamamlandı: {zip_path}")
        speak(parent, f"Geri yükleme tamamlandı: {os.path.basename(zip_path)}")
        parent.config = load_config()
        if parent.chat_panel:
            parent.chat_panel.config = parent.config
            parent.chat_panel.load_chat_history()
            parent.chat_panel.update_volume_slider()
        if parent.teach_panel:
            parent.teach_panel.config = parent.config
            parent.teach_panel.populate_qa_list()
        if parent.sound_panel:
            parent.sound_panel.config = parent.config
            parent.sound_panel.populate_sound_list()
        if parent.settings_panel:
            parent.settings_panel.config = parent.config
            parent.settings_panel.update_ui()
    except Exception as e:
        logging.error(f"Geri yükleme hatası: {e}")
        speak_or_dialog(parent, f"Geri yükleme başarısız: {e}", "Hata", wx.ICON_ERROR)

def format_robot(parent):
    with wx.MessageDialog(
        parent,
        "Dikkat! Robotunuzu formatlamak üzeresiniz. Robotunuzu formatlarsanız, ona öğrettiğiniz tüm bilgiler, verdiğiniz yeni isim ve ses dosyaları dahil her şeyi kalıcı olarak unutacaktır. Bu işlem geri alınamaz. Lütfen önce yedek alın.",
        "Uyarı",
        wx.OK | wx.CANCEL | wx.ICON_WARNING
    ) as dlg:
        if dlg.ShowModal() != wx.ID_OK:
            parent.SetStatusText("Formatlama iptal edildi.")
            speak(parent, "Formatlama iptal edildi.")
            return
    with wx.MessageDialog(
        parent,
        "Robotu sıfırlamak üzeresiniz, emin misiniz? Bu işlem geri alınamaz.",
        "Son Onay",
        wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
    ) as dlg:
        if dlg.ShowModal() != wx.ID_YES:
            parent.SetStatusText("Formatlama iptal edildi.")
            speak(parent, "Formatlama iptal edildi.")
            return
    try:
        if parent.current_stream.value != 0:
            bass.BASS_StreamFree(parent.current_stream)
        bass.BASS_Free()
        shutil.rmtree(DATA_DIR, ignore_errors=True)
        parent.SetStatusText("Robot formatlandı, kapanıyor...")
        speak(parent, "Robot formatlandı, kapanıyor.")
        wx.CallAfter(parent.Close)
    except Exception as e:
        logging.error(f"Formatlama hatası: {e}")
        speak_or_dialog(parent, f"Formatlama başarısız: {e}", "Hata", wx.ICON_ERROR)

# --- ANA ÇERÇEVE ---
class RobotPlayer(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Robot wx", size=(800, 600))
        self.accessibility_enabled = True
        self.config = load_config()
        self.selected_folder = self.config.get("selected_folder", DATA_DIR)
        self.current_stream = ctypes.c_uint(0)
        self.CreateStatusBar()
        self.SetStatusText("Uygulama başlatıldı.")
        speak(self, "Robot wx uygulamasına hoş geldiniz.")

        # Menü çubuğu
        menubar = wx.MenuBar()
        file_menu = wx.Menu()
        exit_item = file_menu.Append(wx.ID_EXIT, "Çıkış\tCtrl+Q", "Programdan çık")
        export_item = file_menu.Append(wx.ID_ANY, "Mesajları Dışa Aktar\tCtrl+E", "Sohbet geçmişini dışa aktar")
        chat_menu = wx.Menu()
        search_item = chat_menu.Append(wx.ID_ANY, "Sohbetlerde Ara\tCtrl+F", "Mesajlarda ara")
        menubar.Append(file_menu, "Dosya")
        menubar.Append(chat_menu, "Sohbet")
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_export, export_item)
        self.Bind(wx.EVT_MENU, self.on_search, search_item)

        # Ana panel
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Sol panel: Ağaç yapısı
        self.tree = wx.TreeCtrl(self.panel, style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT, name="Kategoriler")
        root = self.tree.AddRoot("Kategoriler")
        self.categories = {
            "Sohbet": self.tree.AppendItem(root, "Sohbet"),
            "Öğret": self.tree.AppendItem(root, "Öğret"),
            "Klasör Seçimi": self.tree.AppendItem(root, "Klasör Seçimi"),
            "Ses Yönetimi": self.tree.AppendItem(root, "Ses Yönetimi"),
            "Ayarlar": self.tree.AppendItem(root, "Ayarlar")
        }
        self.chat_categories = {
            "ad_soyad": self.tree.AppendItem(self.categories["Sohbet"], "Adıyla ve Soyadıyla"),
            "soyad_ad": self.tree.AppendItem(self.categories["Sohbet"], "Soyadıyla ve Adıyla"),
            "ad": self.tree.AppendItem(self.categories["Sohbet"], "Sadece Adıyla"),
            "soyad": self.tree.AppendItem(self.categories["Sohbet"], "Sadece Soyadıyla"),
            "none": self.tree.AppendItem(self.categories["Sohbet"], "Hiçbiri")
        }
        self.tree.ExpandAll()
        self.tree.SelectItem(self.chat_categories["none"])
        content_sizer.Add(self.tree, 0, wx.EXPAND | wx.ALL, 5)
        # Sağ panel: İçerik için
        self.content_panel = wx.Panel(self.panel)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content_panel.SetSizer(self.content_sizer)
        content_sizer.Add(self.content_panel, 1, wx.EXPAND | wx.ALL, 5)
        # Çıkış düğmesi
        self.exit_btn = wx.Button(self.panel, label="Çıkış", name="Çıkış Butonu")
        main_sizer.Add(content_sizer, 1, wx.EXPAND)
        main_sizer.Add(self.exit_btn, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.panel.SetSizer(main_sizer)

        # Kategori panelleri
        self.chat_panel = None
        self.teach_panel = None
        self.folder_panel = None
        self.sound_panel = None
        self.settings_panel = None
        self.current_panel = None

        # Olay bağlamaları
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_selection)
        self.tree.Bind(wx.EVT_KEY_DOWN, self.on_tree_key)
        self.exit_btn.Bind(wx.EVT_BUTTON, self.on_exit)

        # İlk paneli göster
        self.show_chat_panel()

        # Timer: JSON dosyalarını taramak için
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(30000)

        # Timer: Espri mesajları için
        self.funny_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_funny_timer, self.funny_timer)
        interval = self.config.get("funny_interval", 5) * 60000
        self.funny_timer.Start(interval)

        # Klavye kısayolları
        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('S'), wx.NewIdRef()),  # Ctrl+S: Gönder
            (wx.ACCEL_CTRL, ord('T'), wx.NewIdRef()),  # Ctrl+T: Öğret
            (wx.ACCEL_CTRL, ord('F'), wx.NewIdRef()),  # Ctrl+F: Arama
            (wx.ACCEL_CTRL, ord('P'), wx.NewIdRef()),  # Ctrl+P: Ses oynat
            (wx.ACCEL_CTRL, ord('E'), wx.NewIdRef()),  # Ctrl+E: Ses değiştir
            (wx.ACCEL_NORMAL, wx.WXK_DELETE, wx.NewIdRef()),  # Delete: Ses sil
            (wx.ACCEL_CTRL, ord('R'), wx.NewIdRef()),  # Ctrl+R: Robot adı
            (wx.ACCEL_CTRL, ord('U'), wx.NewIdRef()),  # Ctrl+U: Kullanıcı girişi
            (wx.ACCEL_CTRL, ord('B'), wx.NewIdRef()),  # Ctrl+B: Yedekle
            (wx.ACCEL_CTRL, ord('L'), wx.NewIdRef()),  # Ctrl+L: Geri yükle
            (wx.ACCEL_CTRL, ord('M'), wx.NewIdRef()),  # Ctrl+M: Formatla
            (wx.ACCEL_CTRL, ord('Q'), wx.NewIdRef()),  # Ctrl+Q: Çıkış
            (wx.ACCEL_CTRL, ord('E'), wx.NewIdRef()),  # Ctrl+E: Dışa aktar
            (wx.ACCEL_CTRL, ord('+'), wx.NewIdRef()),  # Ctrl++: Hız artır
            (wx.ACCEL_CTRL, ord('-'), wx.NewIdRef()),  # Ctrl+-: Hız azalt
            (wx.ACCEL_CTRL, ord('V'), wx.NewIdRef())   # Ctrl+V: Ses seviyesi kaydırıcısı
        ])
        self.SetAcceleratorTable(accel_tbl)
        self.Bind(wx.EVT_MENU, self.on_ctrl_s, id=accel_tbl[0].GetCommand())
        self.Bind(wx.EVT_MENU, self.on_ctrl_t, id=accel_tbl[1].GetCommand())
        self.Bind(wx.EVT_MENU, self.on_search, id=accel_tbl[2].GetCommand())
        self.Bind(wx.EVT_MENU, self.on_ctrl_p, id=accel_tbl[3].GetCommand())
        self.Bind(wx.EVT_MENU, self.on_ctrl_e, id=accel_tbl[4].GetCommand())
        self.Bind(wx.EVT_MENU, self.on_delete, id=accel_tbl[5].GetCommand())
        self.Bind(wx.EVT_MENU, self.on_ctrl_r, id=accel_tbl[6].GetCommand())
        self.Bind(wx.EVT_MENU, self.on_ctrl_u, id=accel_tbl[7].GetCommand())
        self.Bind(wx.EVT_MENU, self.on_ctrl_b, id=accel_tbl[8].GetCommand())
        self.Bind(wx.EVT_MENU, self.on_ctrl_l, id=accel_tbl[9].GetCommand())
        self.Bind(wx.EVT_MENU, self.on_ctrl_m, id=accel_tbl[10].GetCommand())
        self.Bind(wx.EVT_MENU, self.on_exit, id=accel_tbl[11].GetCommand())
        self.Bind(wx.EVT_MENU, self.on_export, id=accel_tbl[12].GetCommand())
        self.Bind(wx.EVT_MENU, self.on_increase_speed, id=accel_tbl[13].GetCommand())
        self.Bind(wx.EVT_MENU, self.on_decrease_speed, id=accel_tbl[14].GetCommand())
        self.Bind(wx.EVT_MENU, self.on_focus_volume, id=accel_tbl[15].GetCommand())
        self.Bind(wx.EVT_CLOSE, self.on_close)

        wx.CallAfter(self.list_ctrl_set_focus)

    def list_ctrl_set_focus(self):
        if self.current_panel == self.chat_panel and self.chat_panel:
            self.chat_panel.msg_list.SetFocus()
        elif self.current_panel == self.teach_panel and self.teach_panel:
            self.teach_panel.qa_list.SetFocus()
        elif self.current_panel == self.sound_panel and self.sound_panel:
            self.sound_panel.sound_list.SetFocus()

    def on_ctrl_s(self, event):
        if self.current_panel == self.chat_panel:
            self.chat_panel.on_send(None)
            speak(self, "Mesaj gönderildi.")

    def on_ctrl_t(self, event):
        if self.current_panel == self.teach_panel:
            self.teach_panel.on_teach(None)
            speak(self, "Yeni soru-cevap ekleme başlatıldı.")

    def on_ctrl_p(self, event):
        if self.current_panel == self.sound_panel:
            self.sound_panel.on_play_sound(None)
            speak(self, "Ses oynatılıyor.")

    def on_ctrl_e(self, event):
        if self.current_panel == self.sound_panel:
            self.sound_panel.on_change_sound(None)
            speak(self, "Ses değiştirme başlatıldı.")

    def on_delete(self, event):
        if self.current_panel == self.sound_panel:
            self.sound_panel.on_delete_sound(None)
            speak(self, "Ses silindi.")

    def on_ctrl_r(self, event):
        if self.current_panel == self.settings_panel:
            self.settings_panel.on_change_robot_name(None)
            speak(self, "Robot adı değiştirme başlatıldı.")

    def on_ctrl_u(self, event):
        if self.current_panel == self.settings_panel:
            self.settings_panel.on_user_input(None)
            speak(self, "Kullanıcı girişi başlatıldı.")

    def on_ctrl_b(self, event):
        if self.current_panel == self.settings_panel:
            self.settings_panel.on_backup(None)
            speak(self, "Yedekleme başlatıldı.")

    def on_ctrl_l(self, event):
        if self.current_panel == self.settings_panel:
            self.settings_panel.on_restore(None)
            speak(self, "Geri yükleme başlatıldı.")

    def on_ctrl_m(self, event):
        if self.current_panel == self.settings_panel:
            self.settings_panel.on_format(None)
            speak(self, "Formatlama başlatıldı.")

    def on_increase_speed(self, event):
        if self.current_panel == self.chat_panel:
            self.chat_panel.increase_playback_speed()

    def on_decrease_speed(self, event):
        if self.current_panel == self.chat_panel:
            self.chat_panel.decrease_playback_speed()

    def on_focus_volume(self, event):
        if self.current_panel == self.chat_panel:
            self.chat_panel.volume_slider.SetFocus()
            speak(self, "Ses seviyesi kaydırıcısına odaklanıldı.")

    def on_exit(self, event):
        if self.config.get("ask_on_exit", True):
            with wx.MessageDialog(self, "Robotunuzu kapatmak üzeresiniz, emin misiniz?", "Çıkış", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) as dlg:
                if dlg.ShowModal() != wx.ID_YES:
                    self.SetStatusText("Çıkış iptal edildi.")
                    speak(self, "Çıkış iptal edildi.")
                    return
        self.Close()

    def on_close(self, event):
        if self.current_stream.value != 0:
            bass.BASS_StreamFree(self.current_stream)
        bass.BASS_Free()
        if self.timer and self.timer.IsRunning():
            self.timer.Stop()
        if self.funny_timer and self.funny_timer.IsRunning():
            self.funny_timer.Stop()
        self.Destroy()

    def on_search(self, event):
        if self.current_panel == self.chat_panel:
            with wx.TextEntryDialog(self, "Arama terimini gir:", "Sohbetlerde Ara", style=wx.OK | wx.CANCEL) as dlg:
                dlg.SetName("Arama Girişi")
                if dlg.ShowModal() == wx.ID_OK:
                    term = dlg.GetValue().strip().lower()
                    if term:
                        self.chat_panel.search_messages(term)
                        self.SetStatusText(f"Arama yapıldı: {term}")
                        speak(self, f"Arama yapıldı: {term}")
                    else:
                        self.chat_panel.load_chat_history()
                        self.SetStatusText("Arama iptal edildi veya boş.")
                        speak(self, "Arama iptal edildi veya boş.")

    def on_export(self, event):
        if self.current_panel == self.chat_panel:
            self.chat_panel.on_export(None)

    def on_funny_timer(self, event):
        try:
            messages = self.config.get("funny_messages", [])
            if messages:
                msg = random.choice(messages)
                self.SetStatusText(msg)
                speak(self, msg)
                logging.info(f"Espri mesajı gösterildi: {msg}")
        except Exception as e:
            logging.error(f"Espri mesajı hatası: {e}")

    def on_tree_key(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            item = self.tree.GetSelection()
            if item:
                text = self.tree.GetItemText(item)
                if text in self.categories or text in [self.tree.GetItemText(i) for i in self.chat_categories.values()]:
                    self.on_tree_selection(None)
                    speak(self, f"{text} kategorisi seçildi.")
        event.Skip()

    def show_chat_panel(self, greeting_style="none"):
        if self.current_panel:
            self.current_panel.Hide()
        if not self.chat_panel:
            self.chat_panel = ChatPanel(self.content_panel, self.config, self)
            self.content_sizer.Add(self.chat_panel, 1, wx.EXPAND | wx.ALL, 5)
        self.chat_panel.Show()
        self.current_panel = self.chat_panel
        self.chat_panel.load_chat_history(greeting_style)
        self.content_sizer.Layout()
        self.SetStatusText(f"Sohbet paneli açıldı: {greeting_style}")
        speak(self, f"Sohbet paneli açıldı: {greeting_style}")
        wx.CallAfter(self.list_ctrl_set_focus)

    def show_teach_panel(self):
        if self.current_panel:
            self.current_panel.Hide()
        if not self.teach_panel:
            self.teach_panel = TeachPanel(self.content_panel, self.config, self)
            self.content_sizer.Add(self.teach_panel, 1, wx.EXPAND | wx.ALL, 5)
        self.teach_panel.Show()
        self.current_panel = self.teach_panel
        self.content_sizer.Layout()
        self.SetStatusText("Öğret paneli açıldı.")
        speak(self, "Öğret paneli açıldı.")
        wx.CallAfter(self.list_ctrl_set_focus)

    def show_folder_panel(self):
        if self.current_panel:
            self.current_panel.Hide()
        if not self.folder_panel:
            self.folder_panel = FolderPanel(self.content_panel, self.config, self)
            self.content_sizer.Add(self.folder_panel, 1, wx.EXPAND | wx.ALL, 5)
        self.folder_panel.Show()
        self.current_panel = self.folder_panel
        self.content_sizer.Layout()
        self.SetStatusText("Klasör seçimi paneli açıldı.")
        speak(self, "Klasör seçimi paneli açıldı.")

    def show_sound_panel(self):
        if self.current_panel:
            self.current_panel.Hide()
        if not self.sound_panel:
            self.sound_panel = SoundPanel(self.content_panel, self.config, self)
            self.content_sizer.Add(self.sound_panel, 1, wx.EXPAND | wx.ALL, 5)
        self.sound_panel.Show()
        self.current_panel = self.sound_panel
        self.content_sizer.Layout()
        self.SetStatusText("Ses yönetimi paneli açıldı.")
        speak(self, "Ses yönetimi paneli açıldı.")
        wx.CallAfter(self.list_ctrl_set_focus)

    def show_settings_panel(self):
        if self.current_panel:
            self.current_panel.Hide()
        if not self.settings_panel:
            self.settings_panel = SettingsPanel(self.content_panel, self.config, self)
            self.content_sizer.Add(self.settings_panel, 1, wx.EXPAND | wx.ALL, 5)
        self.settings_panel.Show()
        self.current_panel = self.settings_panel
        self.content_sizer.Layout()
        self.SetStatusText("Ayarlar paneli açıldı.")
        speak(self, "Ayarlar paneli açıldı.")

    def on_tree_selection(self, event):
        item = self.tree.GetSelection()
        if not item:
            return
        text = self.tree.GetItemText(item)
        if text in self.categories:
            if text == "Sohbet":
                self.show_chat_panel()
            elif text == "Öğret":
                self.show_teach_panel()
            elif text == "Klasör Seçimi":
                self.show_folder_panel()
            elif text == "Ses Yönetimi":
                self.show_sound_panel()
            elif text == "Ayarlar":
                self.show_settings_panel()
        elif text in [self.tree.GetItemText(i) for i in self.chat_categories.values()]:
            greeting_style = [k for k, v in self.chat_categories.items() if self.tree.GetItemText(v) == text][0]
            self.show_chat_panel(greeting_style)

    def on_timer(self, event):
        files = find_recent_json_files(base_folder=self.selected_folder)
        all_new = []
        for fn in files:
            all_new.extend(load_qapairs_from_file(fn))
        if all_new:
            merge_qapairs_into_config(self.config, all_new)
            if self.teach_panel:
                self.teach_panel.populate_qa_list()
            self.SetStatusText(f"Yeni soru-cevaplar yüklendi: {len(all_new)} adet.")
            speak(self, f"{len(all_new)} yeni soru-cevap yüklendi.")
        else:
            self.SetStatusText("Yeni soru-cevap bulunamadı.")
            speak(self, "Yeni soru-cevap bulunamadı.")

# --- SOHBET PANELİ ---
class ChatPanel(wx.Panel):
    def __init__(self, parent, config, frame):
        super().__init__(parent)
        self.config = config
        self.frame = frame

        # wx.ListCtrl için ImageList oluştur
        self.image_list = wx.ImageList(32, 32)
        self.silhouette_idx = self.image_list.Add(wx.Bitmap(wx.Image(SILHOUETTE_PATH).Scale(32, 32)))
        self.user_photo_idx = self.silhouette_idx
        self.robot_photo_idx = self.silhouette_idx
        self.load_photos()

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.msg_list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_NO_HEADER, name="Mesaj Listesi")
        self.msg_list.SetImageList(self.image_list, wx.IMAGE_LIST_SMALL)
        self.msg_list.InsertColumn(0, "Mesaj", width=600)
        vbox.Add(self.msg_list, 1, wx.EXPAND | wx.ALL, 5)
        self.preview = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY, name="Mesaj Önizleme")
        vbox.Add(self.preview, 0, wx.EXPAND | wx.ALL, 5)
        # Ses seviyesi kaydırıcısı
        self.volume_label = wx.StaticText(self, label="Ses Seviyesi:", name="Ses Seviyesi Etiketi")
        vbox.Add(self.volume_label, 0, wx.ALL, 5)
        self.volume_slider = wx.Slider(self, value=int(self.config.get("volume_level", 0.5) * 100), minValue=0, maxValue=100,
                                      style=wx.SL_HORIZONTAL | wx.SL_LABELS, name="Ses Seviyesi Kaydırıcısı")
        vbox.Add(self.volume_slider, 0, wx.EXPAND | wx.ALL, 5)
        input_box = wx.BoxSizer(wx.HORIZONTAL)
        self.entry = wx.TextCtrl(self, name="Mesaj Girişi", style=wx.TE_PROCESS_ENTER)
        self.send_btn = wx.Button(self, label="Gönder", name="Gönder Butonu")
        self.export_btn = wx.Button(self, label="Mesajları Dışa Aktar", name="Dışa Aktar Butonu")
        input_box.Add(self.entry, 1, wx.EXPAND | wx.ALL, 5)
        input_box.Add(self.send_btn, 0, wx.ALL, 5)
        input_box.Add(self.export_btn, 0, wx.ALL, 5)
        vbox.Add(input_box, 0, wx.EXPAND)
        self.SetSizer(vbox)

        self.send_btn.Bind(wx.EVT_BUTTON, self.on_send)
        self.export_btn.Bind(wx.EVT_BUTTON, self.on_export)
        self.msg_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select_message)
        self.entry.Bind(wx.EVT_TEXT_ENTER, self.on_send)
        self.volume_slider.Bind(wx.EVT_SLIDER, self.on_volume_change)
        self.load_chat_history()

    def load_photos(self):
        try:
            if self.config.get("user_photo") and os.path.exists(self.config["user_photo"]):
                img = wx.Image(self.config["user_photo"]).Scale(32, 32)
                self.user_photo_idx = self.image_list.Add(wx.Bitmap(img))
            if self.config.get("robot_photo") and os.path.exists(self.config["robot_photo"]):
                img = wx.Image(self.config["robot_photo"]).Scale(32, 32)
                self.robot_photo_idx = self.image_list.Add(wx.Bitmap(img))
        except Exception as e:
            logging.error(f"Fotoğraf yükleme hatası: {e}")

    def update_volume_slider(self):
        self.volume_slider.SetValue(int(self.config.get("volume_level", 0.5) * 100))

    def increase_playback_speed(self):
        try:
            speed = self.config.get("playback_speed", 1.0)
            speed = min(speed + 0.1, 1.5)  # Max 1.5x
            self.config["playback_speed"] = round(speed, 1)
            save_config(self.config)
            self.frame.SetStatusText(f"Robot konuşma hızı artırıldı: {speed:.1f}x")
            speak(self.frame, f"Robot konuşma hızı artırıldı: {speed:.1f}x")
            logging.info(f"Konuşma hızı artırıldı: {speed:.1f}x")
        except Exception as e:
            logging.error(f"Hız artırma hatası: {e}")
            speak_or_dialog(self, f"Hız artırılamadı: {e}", "Hata", wx.ICON_ERROR)

    def decrease_playback_speed(self):
        try:
            speed = self.config.get("playback_speed", 1.0)
            speed = max(speed - 0.1, 0.5)  # Min 0.5x
            self.config["playback_speed"] = round(speed, 1)
            save_config(self.config)
            self.frame.SetStatusText(f"Robot konuşma hızı azaltıldı: {speed:.1f}x")
            speak(self.frame, f"Robot konuşma hızı azaltıldı: {speed:.1f}x")
            logging.info(f"Konuşma hızı azaltıldı: {speed:.1f}x")
        except Exception as e:
            logging.error(f"Hız azaltma hatası: {e}")
            speak_or_dialog(self, f"Hız azaltılamadı: {e}", "Hata", wx.ICON_ERROR)

    def on_volume_change(self, event):
        try:
            volume = self.volume_slider.GetValue() / 100.0
            self.config["volume_level"] = volume
            save_config(self.config)
            self.frame.SetStatusText(f"Ses seviyesi: {int(volume * 100)}%")
            speak(self.frame, f"Ses seviyesi: {int(volume * 100)} yüzde")
            logging.info(f"Ses seviyesi ayarlandı: {volume:.2f}")
        except Exception as e:
            logging.error(f"Ses seviyesi ayarlama hatası: {e}")
            speak_or_dialog(self, f"Ses seviyesi ayarlanamadı: {e}", "Hata", wx.ICON_ERROR)

    def load_chat_history(self, greeting_style="none"):
        self.msg_list.DeleteAllItems()
        for entry in self.config.get("chat_history", []):
            if "user" in entry:
                self.add_message(f"Siz: {entry['user']}", "user", greeting_style)
            if "robot" in entry and entry.get("greeting_style", "none") == greeting_style:
                self.add_message(f"{self.config.get('robot_adi', 'Otomat')}: {entry['robot']}", "robot", greeting_style)
        self.frame.SetStatusText(f"Sohbet geçmişi yüklendi: {greeting_style}")
        speak(self.frame, f"Sohbet geçmişi yüklendi: {greeting_style}")

    def search_messages(self, term):
        self.msg_list.DeleteAllItems()
        for entry in self.config.get("chat_history", []):
            if "user" in entry and term in entry["user"].lower():
                self.add_message(f"Siz: {entry['user']}", "user", entry.get("greeting_style", "none"))
            if "robot" in entry and term in entry["robot"].lower():
                self.add_message(f"{self.config.get('robot_adi', 'Otomat')}: {entry['robot']}", "robot", entry.get("greeting_style", "none"))
        self.frame.SetStatusText(f"Arama sonuçları: {term}")
        speak(self.frame, f"Arama sonuçları: {term}")

    def add_message(self, text, typ, greeting_style):
        idx = self.msg_list.InsertItem(self.msg_list.GetItemCount(), text)
        if typ == "user":
            self.msg_list.SetItem(idx, 0, text, self.user_photo_idx)
            self.msg_list.SetItemTextAlignment(idx, wx.LIST_FORMAT_RIGHT)
            self.config.setdefault("chat_history", []).append({"user": text[5:], "greeting_style": self.config.get("greeting_style", "none")})
        else:
            self.msg_list.SetItem(idx, 0, text, self.robot_photo_idx)
            self.msg_list.SetItemTextAlignment(idx, wx.LIST_FORMAT_LEFT)
            self.config.setdefault("chat_history", []).append({"robot": text.split(": ", 1)[1], "greeting_style": greeting_style})
        save_config(self.config)
        self.frame.SetStatusText(f"Yeni mesaj: {text[:20]}...")
        speak(self.frame, f"Yeni mesaj: {text[:20]}")

    def on_select_message(self, event):
        idx = event.GetIndex()
        text = self.msg_list.GetItemText(idx)
        self.preview.SetValue(text)
        self.frame.SetStatusText("Mesaj seçildi.")
        speak(self.frame, "Mesaj seçildi.")

    def on_send(self, event):
        msg = self.entry.GetValue().strip()
        if not msg:
            speak_or_dialog(self, "Boş mesaj gönderilemez.", "Uyarı", wx.ICON_WARNING)
            return
        self.entry.SetValue("")
        self.add_message(f"Siz: {msg}", "user", self.config.get("greeting_style", "none"))
        self.respond(msg)

    def on_export(self, event):
        try:
            with wx.FileDialog(self, "Mesajları kaydet", wildcard="Text files (*.txt)|*.txt",
                             style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
                if dlg.ShowModal() != wx.ID_OK:
                    self.frame.SetStatusText("Dışa aktarma iptal edildi.")
                    speak(self.frame, "Dışa aktarma iptal edildi.")
                    return
                path = dlg.GetPath()
            with open(path, "w", encoding="utf-8") as f:
                for entry in self.config.get("chat_history", []):
                    if "user" in entry:
                        f.write(f"kullanıcı: {entry['user']}\n")
                    if "robot" in entry:
                        f.write(f"robot: {entry['robot']}\n")
            msg = "Mesajlar dışa aktarıldı. Artık hatıra olarak mı saklarsınız, yoksa okuyup bir mektubun yırtılıp atılması gibi siler atar mısınız? Gerisi size kalmış, robot tekrar hizmetinizde!"
            with wx.MessageDialog(self, msg, "Dışa Aktarma Tamamlandı", wx.OK | wx.ICON_INFORMATION) as dlg:
                dlg.SetName("Dışa Aktarma Bildirimi")
                dlg.ShowModal()
            self.frame.SetStatusText(f"Mesajlar dışa aktarıldı: {path}")
            speak(self.frame, f"Mesajlar dışa aktarıldı: {os.path.basename(path)}")
            logging.info(f"Mesajlar dışa aktarıldı: {path}")
        except Exception as e:
            logging.error(f"Dışa aktarma hatası: {e}")
            speak_or_dialog(self, f"Mesajlar dışa aktarılamadı: {e}", "Hata", wx.ICON_ERROR)

    def get_greeting(self):
        name = self.config.get("user_name", "")
        surname = self.config.get("user_surname", "")
        style = self.config.get("greeting_style", "none")
        if style == "ad_soyad" and name and surname:
            return f"Merhaba {name} {surname}"
        elif style == "soyad_ad" and name and surname:
            return f"Merhaba {surname} {name}"
        elif style == "ad" and name:
            return f"Merhaba {name}"
        elif style == "soyad" and surname:
            return f"Merhaba {surname}"
        return ""

    def respond(self, msg):
        m = msg.lower().strip()
        greeting = self.get_greeting()
        greeting_style = self.config.get("greeting_style", "none")
        if m == "rob daha hızlı konuş":
            self.increase_playback_speed()
            cevap = "Tamam, devrelerimi hızlandırdım!"
            if greeting:
                cevap = f"{greeting}, {cevap}"
            self.add_message(f"{self.config.get('robot_adi', 'Otomat')}: {cevap}", "robot", greeting_style)
            return
        if m == "rob daha yavaş konuş":
            self.decrease_playback_speed()
            cevap = "Peki, biraz yavaşladım, rahat mısın?"
            if greeting:
                cevap = f"{greeting}, {cevap}"
            self.add_message(f"{self.config.get('robot_adi', 'Otomat')}: {cevap}", "robot", greeting_style)
            return
        for qa in self.config.get("bilgiler", []):
            if m == qa.get("soru", "").lower():
                cevap = qa.get("cevap", "")
                if greeting:
                    cevap = f"{greeting}, {cevap}"
                self.add_message(f"{self.config.get('robot_adi', 'Otomat')}: {cevap}", "robot", greeting_style)
                sound_path = self.config.get("sound_mappings", {}).get(qa["soru"].lower())
                if sound_path and os.path.exists(sound_path):
                    self.play_sound(sound_path)
                return
        if "ne yapıyorsun" in m:
            cevap = "Evdeyim, takılıyorum."
            if greeting:
                cevap = f"{greeting}, {cevap}"
            self.add_message(f"{self.config.get('robot_adi', 'Otomat')}: {cevap}", "robot", greeting_style)
            sound_path = self.config.get("sound_mappings", {}).get("ne yapıyorsun")
            if sound_path and os.path.exists(sound_path):
                self.play_sound(sound_path)
            return
        cevap = "Bilmiyorum, bana öğretebilirsin!"
        if greeting:
            cevap = f"{greeting}, {cevap}"
        self.add_message(f"{self.config.get('robot_adi', 'Otomat')}: {cevap}", "robot", greeting_style)

    def play_sound(self, sound_path):
        try:
            if self.frame.current_stream.value != 0:
                bass.BASS_StreamFree(self.frame.current_stream)
            self.frame.current_stream = ctypes.c_uint(bass.BASS_StreamCreateFile(False, sound_path.encode("utf-8"), 0, 0, 0))
            if self.frame.current_stream.value == 0:
                raise RuntimeError(f"Ses oynatılamadı: {bass.BASS_ErrorGetCode()}")
            speed = self.config.get("playback_speed", 1.0)
            volume = self.config.get("volume_level", 0.5)
            bass.BASS_ChannelSetAttribute(self.frame.current_stream, BASS_ATTRIB_FREQ, ctypes.c_float(44100 * speed))
            bass.BASS_ChannelSetAttribute(self.frame.current_stream, BASS_ATTRIB_VOL, ctypes.c_float(volume))
            bass.BASS_ChannelPlay(self.frame.current_stream, False)
            self.frame.SetStatusText(f"Ses oynatılıyor: {os.path.basename(sound_path)} (Hız: {speed:.1f}x, Ses: {int(volume * 100)}%)")
            speak(self.frame, f"Ses oynatılıyor: {os.path.basename(sound_path)}, hız {speed:.1f}x, ses seviyesi {int(volume * 100)} yüzde")
        except Exception as e:
            logging.error(f"Ses oynatma hatası: {e}")
            speak_or_dialog(self.frame, f"Ses oynatılamadı: {e}", "Hata", wx.ICON_ERROR)

# --- ÖĞRET PANELİ ---
class TeachPanel(wx.Panel):
    def __init__(self, parent, config, frame):
        super().__init__(parent)
        self.config = config
        self.frame = frame

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.qa_list = wx.ListCtrl(self, style=wx.LC_REPORT, name="Soru-Cevap Listesi")
        self.qa_list.InsertColumn(0, "Soru", width=300)
        self.qa_list.InsertColumn(1, "Cevap", width=300)
        vbox.Add(self.qa_list, 1, wx.EXPAND | wx.ALL, 5)
        self.teach_btn = wx.Button(self, label="Yeni Soru-Cevap Ekle", name="Öğret Butonu")
        vbox.Add(self.teach_btn, 0, wx.ALL, 5)
        self.SetSizer(vbox)

        self.teach_btn.Bind(wx.EVT_BUTTON, self.on_teach)
        self.populate_qa_list()

    def populate_qa_list(self):
        self.qa_list.DeleteAllItems()
        for qa in self.config.get("bilgiler", []):
            idx = self.qa_list.InsertItem(self.qa_list.GetItemCount(), qa.get("soru", ""))
            self.qa_list.SetItem(idx, 1, qa.get("cevap", ""))
        self.frame.SetStatusText("Soru-cevap listesi güncellendi.")
        speak(self.frame, "Soru-cevap listesi güncellendi.")

    def on_teach(self, event):
        dlg = wx.TextEntryDialog(self, "Soru gir:", "Yeni Soru", style=wx.OK | wx.CANCEL)
        dlg.SetName("Soru Girişi")
        if dlg.ShowModal() == wx.ID_OK:
            soru = dlg.GetValue().strip()
        else:
            dlg.Destroy()
            speak_or_dialog(self, "Soru ekleme iptal edildi.", "Bilgi")
            return
        dlg.Destroy()

        dlg = wx.TextEntryDialog(self, "Cevap gir:", "Yeni Cevap", style=wx.OK | wx.CANCEL)
        dlg.SetName("Cevap Girişi")
        if dlg.ShowModal() == wx.ID_OK:
            cevap = dlg.GetValue().strip()
        else:
            dlg.Destroy()
            speak_or_dialog(self, "Cevap ekleme iptal edildi.", "Bilgi")
            return
        dlg.Destroy()

        # Ses dosyası seçimi
        dlg = wx.FileDialog(self, "Ses dosyası seç (.mp3)", wildcard="MP3 files (*.mp3)|*.mp3", style=wx.FD_OPEN)
        sound_path = None
        if dlg.ShowModal() == wx.ID_OK:
            sound_path = dlg.GetPath()
            dest_path = os.path.join(SOUNDS_DIR, os.path.basename(sound_path))
            try:
                if sound_path != dest_path:
                    shutil.copy(sound_path, dest_path)
                sound_path = dest_path
            except Exception as e:
                logging.error(f"Ses dosyası kopyalama hatası: {e}")
                speak_or_dialog(self, f"Ses dosyası kopyalanamadı: {e}", "Hata", wx.ICON_ERROR)
        dlg.Destroy()

        qa = {"soru": soru, "cevap": cevap}
        distribute_qapair_to_other_files(qa, base_folder=self.frame.selected_folder)
        self.config.setdefault("bilgiler", []).append(qa)
        if sound_path:
            self.config.setdefault("sound_mappings", {})[soru.lower()] = sound_path
        save_config(self.config)
        self.populate_qa_list()
        if self.frame.chat_panel:
            self.frame.chat_panel.add_message(
                f"{self.config.get('robot_adi', 'Otomat')}: Yeni soru-cevap öğrendim!", "robot", self.config.get("greeting_style", "none")
            )
        self.frame.SetStatusText(f"Yeni soru-cevap eklendi: {soru[:20]}...")
        speak(self.frame, f"Yeni soru-cevap eklendi: {soru[:20]}")
        if sound_path:
            self.frame.SetStatusText(f"Ses ilişkilendirildi: {os.path.basename(sound_path)}")
            speak(self.frame, f"Ses ilişkilendirildi: {os.path.basename(sound_path)}")

# --- KLASÖR SEÇİMİ PANELİ ---
class FolderPanel(wx.Panel):
    def __init__(self, parent, config, frame):
        super().__init__(parent)
        self.config = config
        self.frame = frame

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.folder_label = wx.StaticText(self, label=f"Seçili Klasör: {self.frame.selected_folder}", name="Klasör Bilgisi")
        vbox.Add(self.folder_label, 0, wx.ALL | wx.EXPAND, 5)
        self.folder_btn = wx.Button(self, label="Klasör Seç", name="Klasör Seç Butonu")
        vbox.Add(self.folder_btn, 0, wx.ALL, 5)
        self.SetSizer(vbox)

        self.folder_btn.Bind(wx.EVT_BUTTON, self.on_select_folder)

    def on_select_folder(self, event):
        dlg = wx.DirDialog(self, "Klasör seç", style=wx.DD_DEFAULT_STYLE, name="Klasör Seçici")
        if dlg.ShowModal() == wx.ID_OK:
            self.frame.selected_folder = dlg.GetPath()
            self.folder_label.SetLabel(f"Seçili Klasör: {self.frame.selected_folder}")
            self.config["selected_folder"] = self.frame.selected_folder
            save_config(self.config)
            self.frame.SetStatusText(f"Yeni klasör seçildi: {self.frame.selected_folder}")
            speak(self.frame, f"Yeni klasör seçildi: {os.path.basename(self.frame.selected_folder)}")
        else:
            self.frame.SetStatusText("Klasör seçimi iptal edildi.")
            speak(self.frame, "Klasör seçimi iptal edildi.")
        dlg.Destroy()

# --- SES YÖNETİMİ PANELİ ---
class SoundPanel(wx.Panel):
    def __init__(self, parent, config, frame):
        super().__init__(parent)
        self.config = config
        self.frame = frame

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.sound_list = wx.ListCtrl(self, style=wx.LC_REPORT, name="Ses Listesi")
        self.sound_list.InsertColumn(0, "Soru", width=300)
        self.sound_list.InsertColumn(1, "Ses Dosyası", width=300)
        vbox.Add(self.sound_list, 1, wx.EXPAND | wx.ALL, 5)
        btn_box = wx.BoxSizer(wx.HORIZONTAL)
        self.play_btn = wx.Button(self, label="Oynat", name="Oynat Butonu")
        self.change_btn = wx.Button(self, label="Değiştir", name="Değiştir Butonu")
        self.delete_btn = wx.Button(self, label="Sil", name="Sil Butonu")
        btn_box.Add(self.play_btn, 0, wx.ALL, 5)
        btn_box.Add(self.change_btn, 0, wx.ALL, 5)
        btn_box.Add(self.delete_btn, 0, wx.ALL, 5)
        vbox.Add(btn_box, 0, wx.EXPAND)
        self.SetSizer(vbox)

        self.play_btn.Bind(wx.EVT_BUTTON, self.on_play_sound)
        self.change_btn.Bind(wx.EVT_BUTTON, self.on_change_sound)
        self.delete_btn.Bind(wx.EVT_BUTTON, self.on_delete_sound)
        self.populate_sound_list()

    def populate_sound_list(self):
        self.sound_list.DeleteAllItems()
        for soru, sound_path in self.config.get("sound_mappings", {}).items():
            idx = self.sound_list.InsertItem(self.sound_list.GetItemCount(), soru)
            self.sound_list.SetItem(idx, 1, os.path.basename(sound_path))
        self.frame.SetStatusText("Ses listesi güncellendi.")
        speak(self.frame, "Ses listesi güncellendi.")

    def on_play_sound(self, event):
        idx = self.sound_list.GetFirstSelected()
        if idx < 0:
            speak_or_dialog(self, "Önce bir ses seçin.", "Uyarı", wx.ICON_WARNING)
            return
        soru = self.sound_list.GetItemText(idx)
        sound_path = self.config.get("sound_mappings", {}).get(soru)
        if sound_path and os.path.exists(sound_path):
            self.frame.chat_panel.play_sound(sound_path)
        else:
            speak_or_dialog(self, "Ses dosyası bulunamadı.", "Hata", wx.ICON_ERROR)

    def on_change_sound(self, event):
        idx = self.sound_list.GetFirstSelected()
        if idx < 0:
            speak_or_dialog(self, "Önce bir ses seçin.", "Uyarı", wx.ICON_WARNING)
            return
        soru = self.sound_list.GetItemText(idx)
        dlg = wx.FileDialog(self, "Yeni ses dosyası seç (.mp3)", wildcard="MP3 files (*.mp3)|*.mp3", style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            new_sound_path = dlg.GetPath()
            dest_path = os.path.join(SOUNDS_DIR, os.path.basename(new_sound_path))
            try:
                if new_sound_path != dest_path:
                    shutil.copy(new_sound_path, dest_path)
                self.config.setdefault("sound_mappings", {})[soru] = dest_path
                save_config(self.config)
                self.populate_sound_list()
                self.frame.SetStatusText(f"Ses değiştirildi: {os.path.basename(dest_path)}")
                speak(self.frame, f"Ses değiştirildi: {os.path.basename(dest_path)}")
            except Exception as e:
                logging.error(f"Ses dosyası kopyalama hatası: {e}")
                speak_or_dialog(self, f"Ses dosyası kopyalanamadı: {e}", "Hata", wx.ICON_ERROR)
        dlg.Destroy()

    def on_delete_sound(self, event):
        idx = self.sound_list.GetFirstSelected()
        if idx < 0:
            speak_or_dialog(self, "Önce bir ses seçin.", "Uyarı", wx.ICON_WARNING)
            return
        soru = self.sound_list.GetItemText(idx)
        sound_path = self.config.get("sound_mappings", {}).get(soru)
        if sound_path:
            with wx.MessageDialog(self, f"'{soru}' için ses dosyasını silmek istediğinizden emin misiniz?", "Onay", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) as dlg:
                if dlg.ShowModal() == wx.ID_YES:
                    try:
                        if os.path.exists(sound_path):
                            os.remove(sound_path)
                        del self.config["sound_mappings"][soru]
                        save_config(self.config)
                        self.populate_sound_list()
                        self.frame.SetStatusText(f"Ses silindi: {soru}")
                        speak(self.frame, f"Ses silindi: {soru}")
                    except Exception as e:
                        logging.error(f"Ses silme hatası: {e}")
                        speak_or_dialog(self, f"Ses silinemedi: {e}", "Hata", wx.ICON_ERROR)

# --- AYARLAR PANELİ ---
class SettingsPanel(wx.Panel):
    def __init__(self, parent, config, frame):
        super().__init__(parent)
        self.config = config
        self.frame = frame

        vbox = wx.BoxSizer(wx.VERTICAL)
        # Robot adı
        self.robot_name_label = wx.StaticText(self, label=f"Robot Adı: {self.config.get('robot_adi', 'Otomat')}", name="Robot Adı")
        vbox.Add(self.robot_name_label, 0, wx.ALL | wx.EXPAND, 5)
        self.change_name_btn = wx.Button(self, label="Robot Adını Değiştir", name="Robot Adı Değiştir Butonu")
        vbox.Add(self.change_name_btn, 0, wx.ALL, 5)
        # Kullanıcı girişi
        self.user_input_btn = wx.Button(self, label="Kullanıcı Girişi", name="Kullanıcı Girişi Butonu")
        vbox.Add(self.user_input_btn, 0, wx.ALL, 5)
        # Kullanıcı fotoğrafı
        self.user_photo_btn = wx.Button(self, label="Kullanıcı Fotoğrafı Seç", name="Kullanıcı Fotoğrafı Butonu")
        vbox.Add(self.user_photo_btn, 0, wx.ALL, 5)
        # Robot fotoğrafı
        self.robot_photo_btn = wx.Button(self, label="Robot Fotoğrafı Seç", name="Robot Fotoğrafı Butonu")
        vbox.Add(self.robot_photo_btn, 0, wx.ALL, 5)
        # Espri sıklığı
        self.funny_interval_label = wx.StaticText(self, label="Espri Sıklığı (dakika):", name="Espri Sıklığı Etiketi")
        vbox.Add(self.funny_interval_label, 0, wx.ALL, 5)
        self.funny_interval = wx.Slider(self, value=self.config.get("funny_interval", 5), minValue=1, maxValue=30,
                                       style=wx.SL_HORIZONTAL | wx.SL_LABELS, name="Espri Sıklığı Kaydırıcısı")
        vbox.Add(self.funny_interval, 0, wx.EXPAND | wx.ALL, 5)
        # Espri ekle
        self.funny_msg_label = wx.StaticText(self, label="Yeni Espri:", name="Yeni Espri Etiketi")
        vbox.Add(self.funny_msg_label, 0, wx.ALL, 5)
        self.funny_msg_entry = wx.TextCtrl(self, name="Espri Girişi")
        vbox.Add(self.funny_msg_entry, 0, wx.EXPAND | wx.ALL, 5)
        self.add_funny_btn = wx.Button(self, label="Espri Ekle", name="Espri Ekle Butonu")
        vbox.Add(self.add_funny_btn, 0, wx.ALL, 5)
        # Çıkışta sor
        self.ask_on_exit = wx.CheckBox(self, label="Çıkışta Sor", name="Çıkışta Sor Onay Kutusu")
        self.ask_on_exit.SetValue(self.config.get("ask_on_exit", True))
        vbox.Add(self.ask_on_exit, 0, wx.ALL, 5)
        # Yedekleme ve geri yükleme
        self.backup_btn = wx.Button(self, label="Ayarları Yedekle", name="Yedekle Butonu")
        self.restore_btn = wx.Button(self, label="Ayarları Geri Yükle", name="Geri Yükle Butonu")
        self.format_btn = wx.Button(self, label="Robotu Formatla", name="Formatla Butonu")
        vbox.Add(self.backup_btn, 0, wx.ALL, 5)
        vbox.Add(self.restore_btn, 0, wx.ALL, 5)
        vbox.Add(self.format_btn, 0, wx.ALL, 5)
        self.SetSizer(vbox)

        self.change_name_btn.Bind(wx.EVT_BUTTON, self.on_change_robot_name)
        self.user_input_btn.Bind(wx.EVT_BUTTON, self.on_user_input)
        self.user_photo_btn.Bind(wx.EVT_BUTTON, self.on_user_photo)
        self.robot_photo_btn.Bind(wx.EVT_BUTTON, self.on_robot_photo)
        self.funny_interval.Bind(wx.EVT_SLIDER, self.on_funny_interval)
        self.add_funny_btn.Bind(wx.EVT_BUTTON, self.on_add_funny)
        self.ask_on_exit.Bind(wx.EVT_CHECKBOX, self.on_ask_on_exit)
        self.backup_btn.Bind(wx.EVT_BUTTON, self.on_backup)
        self.restore_btn.Bind(wx.EVT_BUTTON, self.on_restore)
        self.format_btn.Bind(wx.EVT_BUTTON, self.on_format)

    def update_ui(self):
        self.robot_name_label.SetLabel(f"Robot Adı: {self.config.get('robot_adi', 'Otomat')}")
        self.ask_on_exit.SetValue(self.config.get("ask_on_exit", True))
        self.funny_interval.SetValue(self.config.get("funny_interval", 5))

    def on_change_robot_name(self, event):
        with wx.TextEntryDialog(self, "Yeni robot adını gir:", "Robot Adı Değiştir", value=self.config.get("robot_adi", "Otomat"), style=wx.OK | wx.CANCEL) as dlg:
            dlg.SetName("Robot Adı Girişi")
            if dlg.ShowModal() == wx.ID_OK:
                new_name = dlg.GetValue().strip()
                if new_name:
                    self.config["robot_adi"] = new_name
                    save_config(self.config)
                    self.update_ui()
                    self.frame.SetStatusText(f"Robot adı değiştirildi: {new_name}")
                    speak(self.frame, f"Robot adı değiştirildi: {new_name}")
                    if self.frame.chat_panel:
                        self.frame.chat_panel.config = self.config
                        self.frame.chat_panel.load_chat_history()
                else:
                    speak_or_dialog(self, "Robot adı boş olamaz.", "Uyarı", wx.ICON_WARNING)

    def on_user_input(self, event):
        with UserInputDialog(self, self.config, self.frame) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.config["user_name"] = dlg.name_ctrl.GetValue().strip()
                self.config["user_surname"] = dlg.surname_ctrl.GetValue().strip()
                style = dlg.greeting_style.GetSelection()
                styles = ["ad_soyad", "soyad_ad", "ad", "soyad", "none"]
                self.config["greeting_style"] = styles[style]
                save_config(self.config)
                self.frame.SetStatusText("Kullanıcı bilgileri güncellendi.")
                speak(self.frame, "Kullanıcı bilgileri güncellendi.")
                if self.frame.chat_panel:
                    self.frame.chat_panel.config = self.config
                    self.frame.chat_panel.load_chat_history()

    def on_user_photo(self, event):
        try:
            with wx.FileDialog(self, "Kullanıcı fotoğrafı seç (.jpg, .png)", wildcard="Image files (*.jpg;*.png)|*.jpg;*.png", style=wx.FD_OPEN) as dlg:
                if dlg.ShowModal() == wx.ID_OK:
                    src_path = dlg.GetPath()
                    dest_path = os.path.join(IMAGES_DIR, os.path.basename(src_path))
                    shutil.copy(src_path, dest_path)
                    self.config["user_photo"] = dest_path
                    save_config(self.config)
                    if self.frame.chat_panel:
                        self.frame.chat_panel.load_photos()
                        self.frame.chat_panel.load_chat_history()
                    self.frame.SetStatusText(f"Kullanıcı fotoğrafı seçildi: {os.path.basename(dest_path)}")
                    speak(self.frame, f"Kullanıcı fotoğrafı seçildi: {os.path.basename(dest_path)}")
        except Exception as e:
            logging.error(f"Kullanıcı fotoğrafı yükleme hatası: {e}")
            speak_or_dialog(self, f"Kullanıcı fotoğrafı yüklenemedi: {e}", "Hata", wx.ICON_ERROR)

    def on_robot_photo(self, event):
        try:
            with wx.FileDialog(self, "Robot fotoğrafı seç (.jpg, .png)", wildcard="Image files (*.jpg;*.png)|*.jpg;*.png", style=wx.FD_OPEN) as dlg:
                if dlg.ShowModal() == wx.ID_OK:
                    src_path = dlg.GetPath()
                    dest_path = os.path.join(IMAGES_DIR, os.path.basename(src_path))
                    shutil.copy(src_path, dest_path)
                    self.config["robot_photo"] = dest_path
                    save_config(self.config)
                    if self.frame.chat_panel:
                        self.frame.chat_panel.load_photos()
                        self.frame.chat_panel.load_chat_history()
                    self.frame.SetStatusText(f"Robot fotoğrafı seçildi: {os.path.basename(dest_path)}")
                    speak(self.frame, f"Robot fotoğrafı seçildi: {os.path.basename(dest_path)}")
        except Exception as e:
            logging.error(f"Robot fotoğrafı yükleme hatası: {e}")
            speak_or_dialog(self, f"Robot fotoğrafı yüklenemedi: {e}", "Hata", wx.ICON_ERROR)

    def on_funny_interval(self, event):
        interval = self.funny_interval.GetValue()
        self.config["funny_interval"] = interval
        save_config(self.config)
        self.frame.funny_timer.Stop()
        self.frame.funny_timer.Start(interval * 60000)
        self.frame.SetStatusText(f"Espri sıklığı: {interval} dakika")
        speak(self.frame, f"Espri sıklığı: {interval} dakika")

    def on_add_funny(self, event):
        msg = self.funny_msg_entry.GetValue().strip()
        if not msg:
            speak_or_dialog(self, "Espri boş olamaz.", "Uyarı", wx.ICON_WARNING)
            return
        self.config.setdefault("funny_messages", []).append(msg)
        save_config(self.config)
        self.funny_msg_entry.SetValue("")
        self.frame.SetStatusText(f"Yeni espri eklendi: {msg[:20]}...")
        speak(self.frame, f"Yeni espri eklendi: {msg[:20]}")

    def on_ask_on_exit(self, event):
        self.config["ask_on_exit"] = self.ask_on_exit.GetValue()
        save_config(self.config)
        self.frame.SetStatusText(f"Çıkışta Sor: {'Açık' if self.config['ask_on_exit'] else 'Kapalı'}")
        speak(self.frame, f"Çıkışta Sor: {'Açık' if self.config['ask_on_exit'] else 'Kapalı'}")

    def on_backup(self, event):
        backup_data(self.frame)

    def on_restore(self, event):
        restore_data(self.frame)

    def on_format(self, event):
        format_robot(self.frame)

# --- KULLANICI GİRİŞİ DİYALOG ---
class UserInputDialog(wx.Dialog):
    def __init__(self, parent, config, frame