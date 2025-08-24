# -*- coding: utf-8 -*-
"""
robot_wx.py
wxPython tabanlı robot uygulaması, ağaç yapısı (wx.TreeCtrl) ile kategorili mimari.
- Sol tarafta wx.TreeCtrl ile kategoriler: Sohbet, Öğret, Klasör Seçimi.
- Sağ tarafta seçilen kategoriye göre dinamik paneller.
- Sohbet: Kullanıcı mesajları ve robot cevapları listede.
- Öğret: Yeni soru-cevap ekler, JSON dosyalarına dağıtır.
- Klasör Seçimi: JSON dosyalarının taranacağı klasörü seçer.
- Durum Çubuğu: İşlemler hakkında bilgi verir.
"""

import wx
import os
import json
from datetime import datetime, timedelta

CONFIG_FILE = "robot_config.json"

# --- JSON Yönetimi ---
def load_config():
    """robot_config.json dosyasını yükler veya varsayılan config döndürür."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Config yükleme hatası: {e}")
    return {
        "robot_adi": "Robo",
        "bilgiler": [],
        "chat_history": [],
        "robot_state": {"time_of_day": "day", "is_sleeping": False},
        "selected_folder": os.getcwd()
    }

def save_config(cfg):
    """Config'i robot_config.json dosyasına kaydeder."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Config kaydetme hatası: {e}")

def find_recent_json_files(limit=6, exclude_self=True, base_folder=None):
    """Belirtilen klasördeki en son JSON dosyalarını bulur."""
    folder = base_folder or os.getcwd()
    try:
        files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith('.json')]
    except Exception as e:
        print(f"Dosya listeleme hatası: {e}")
        return []
    if exclude_self:
        files = [f for f in files if not os.path.basename(f) == CONFIG_FILE]
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return files[:limit]

def load_qapairs_from_file(path):
    """JSON dosyasından soru-cevap çiftlerini yükler."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "bilgiler" in data:
            return data["bilgiler"]
        return []
    except Exception as e:
        print(f"Dosya yükleme hatası {path}: {e}")
        return []

def merge_qapairs_into_config(config, qas):
    """Yeni soru-cevap çiftlerini config'e birleştirir, tekrarları önler."""
    existing = {q["soru"].lower(): q for q in config.get("bilgiler", [])}
    changed = False
    for qa in qas:
        if qa["soru"].lower() not in existing:
            config["bilgiler"].append(qa)
            changed = True
    if changed:
        save_config(config)

def distribute_qapair_to_other_files(qapair, max_files=5, base_folder=None):
    """Yeni soru-cevap çifti diğer JSON dosyalarına dağıtır."""
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
            print(f"Dosyaya yazma hatası {fn}: {e}")
    return successes

# --- Ana Çerçeve ---
class RobotPlayer(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Robot wx", size=(800, 600))
        self.config = load_config()
        self.selected_folder = self.config.get("selected_folder", os.getcwd())
        self.CreateStatusBar()  # Durum çubuğu
        self.SetStatusText("Hazır.")

        # Ana panel
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Sol panel: Ağaç yapısı (wx.TreeCtrl)
        self.tree = wx.TreeCtrl(self.panel, style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT)
        root = self.tree.AddRoot("Kategoriler")
        self.categories = {
            "Sohbet": self.tree.AppendItem(root, "Sohbet"),
            "Öğret": self.tree.AppendItem(root, "Öğret"),
            "Klasör Seçimi": self.tree.AppendItem(root, "Klasör Seçimi")
        }
        self.tree.ExpandAll()
        main_sizer.Add(self.tree, 0, wx.EXPAND | wx.ALL, 5)

        # Sağ panel: İçerik için
        self.content_panel = wx.Panel(self.panel)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content_panel.SetSizer(self.content_sizer)
        main_sizer.Add(self.content_panel, 1, wx.EXPAND | wx.ALL, 5)

        self.panel.SetSizer(main_sizer)

        # Kategori panelleri
        self.chat_panel = None
        self.teach_panel = None
        self.folder_panel = None
        self.current_panel = None

        # Ağaç seçimi için olay bağlama
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_tree_selection)

        # İlk paneli göster (Sohbet)
        self.show_chat_panel()

        # Timer: JSON dosyalarını taramak için
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(30000)  # 30 saniye

    def show_chat_panel(self):
        """Sohbet panelini gösterir."""
        if self.current_panel:
            self.current_panel.Hide()
        if not self.chat_panel:
            self.chat_panel = ChatPanel(self.content_panel, self.config, self)
            self.content_sizer.Add(self.chat_panel, 1, wx.EXPAND | wx.ALL, 5)
        self.chat_panel.Show()
        self.current_panel = self.chat_panel
        self.content_sizer.Layout()
        self.SetStatusText("Sohbet paneli açıldı.")

    def show_teach_panel(self):
        """Öğret panelini gösterir."""
        if self.current_panel:
            self.current_panel.Hide()
        if not self.teach_panel:
            self.teach_panel = TeachPanel(self.content_panel, self.config, self)
            self.content_sizer.Add(self.teach_panel, 1, wx.EXPAND | wx.ALL, 5)
        self.teach_panel.Show()
        self.current_panel = self.teach_panel
        self.content_sizer.Layout()
        self.SetStatusText("Öğret paneli açıldı.")

    def show_folder_panel(self):
        """Klasör seçimi panelini gösterir."""
        if self.current_panel:
            self.current_panel.Hide()
        if not self.folder_panel:
            self.folder_panel = FolderPanel(self.content_panel, self.config, self)
            self.content_sizer.Add(self.folder_panel, 1, wx.EXPAND | wx.ALL, 5)
        self.folder_panel.Show()
        self.current_panel = self.folder_panel
        self.content_sizer.Layout()
        self.SetStatusText("Klasör seçimi paneli açıldı.")

    def on_tree_selection(self, event):
        """Ağaçtaki kategori seçimine göre paneli değiştirir."""
        item = self.tree.GetSelection()
        if not item:
            return
        text = self.tree.GetItemText(item)
        if text == "Sohbet":
            self.show_chat_panel()
        elif text == "Öğret":
            self.show_teach_panel()
        elif text == "Klasör Seçimi":
            self.show_folder_panel()

    def on_timer(self, event):
        """Periyodik olarak JSON dosyalarını tarar."""
        files = find_recent_json_files(base_folder=self.selected_folder)
        all_new = []
        for fn in files:
            all_new.extend(load_qapairs_from_file(fn))
        if all_new:
            merge_qapairs_into_config(self.config, all_new)
            if self.teach_panel:
                self.teach_panel.populate_qa_list()
            self.SetStatusText(f"Yeni soru-cevaplar yüklendi: {len(all_new)} adet.")
        else:
            self.SetStatusText("Yeni soru-cevap bulunamadı.")

    def __del__(self):
        """Temizlik işlemleri."""
        if self.timer and self.timer.IsRunning():
            self.timer.Stop()

# --- Sohbet Paneli ---
class ChatPanel(wx.Panel):
    def __init__(self, parent, config, frame):
        super().__init__(parent)
        self.config = config
        self.frame = frame

        # Düzen
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Mesaj listesi
        self.msg_list = wx.ListBox(self)
        vbox.Add(self.msg_list, 1, wx.EXPAND | wx.ALL, 5)

        # Mesaj önizleme
        self.preview = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        vbox.Add(self.preview, 0, wx.EXPAND | wx.ALL, 5)

        # Mesaj girişi ve gönder butonu
        input_box = wx.BoxSizer(wx.HORIZONTAL)
        self.entry = wx.TextCtrl(self)
        self.send_btn = wx.Button(self, label="Gönder")
        input_box.Add(self.entry, 1, wx.EXPAND | wx.ALL, 5)
        input_box.Add(self.send_btn, 0, wx.ALL, 5)
        vbox.Add(input_box, 0, wx.EXPAND)

        self.SetSizer(vbox)

        # Olay bağlamaları
        self.send_btn.Bind(wx.EVT_BUTTON, self.on_send)
        self.msg_list.Bind(wx.EVT_LISTBOX, self.on_select_message)

        # Sohbet geçmişini yükle
        self.load_chat_history()

    def load_chat_history(self):
        """Sohbet geçmişini yükler ve listeye ekler."""
        for entry in self.config.get("chat_history", []):
            if "user" in entry:
                self.add_message(f"Siz: {entry['user']}", "user")
            if "robot" in entry:
                self.add_message(f"{self.config.get('robot_adi', 'Robo')}: {entry['robot']}", "robot")
        self.frame.SetStatusText("Sohbet geçmişi yüklendi.")

    def add_message(self, text, typ):
        """Mesajı listeye ekler ve config'e kaydeder."""
        self.msg_list.Append(text)
        self.msg_list.SetClientData(self.msg_list.GetCount() - 1, {"type": typ, "text": text})
        if typ == "user":
            self.config.setdefault("chat_history", []).append({"user": text[5:]})
        else:
            self.config.setdefault("chat_history", []).append({"robot": text.split(": ", 1)[1]})
        save_config(self.config)
        self.frame.SetStatusText(f"Yeni mesaj: {text[:20]}...")

    def on_select_message(self, event):
        """Seçilen mesajı önizlemede gösterir."""
        data = self.msg_list.GetClientData(event.GetSelection())
        if data:
            self.preview.SetValue(data["text"])
            self.frame.SetStatusText("Mesaj seçildi.")

    def on_send(self, event):
        """Mesaj gönderimini işler."""
        msg = self.entry.GetValue().strip()
        if not msg:
            self.frame.SetStatusText("Boş mesaj gönderilemez.")
            return
        self.entry.SetValue("")
        self.add_message(f"Siz: {msg}", "user")
        self.respond(msg)

    def respond(self, msg):
        """Mesaja yanıt üretir."""
        m = msg.lower().strip()
        for qa in self.config.get("bilgiler", []):
            if m == qa.get("soru", "").lower():
                self.add_message(f"{self.config.get('robot_adi', 'Robo')}: {qa.get('cevap', '')}", "robot")
                return
        if "ne yapıyorsun" in m:
            self.add_message(f"{self.config.get('robot_adi', 'Robo')}: Evdeyim, takılıyorum.", "robot")
            return
        self.add_message(f"{self.config.get('robot_adi', 'Robo')}: Bilmiyorum, bana öğretebilirsin!", "robot")

# --- Öğret Paneli ---
class TeachPanel(wx.Panel):
    def __init__(self, parent, config, frame):
        super().__init__(parent)
        self.config = config
        self.frame = frame

        # Düzen
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Soru-cevap listesi
        self.qa_list = wx.ListCtrl(self, style=wx.LC_REPORT)
        self.qa_list.InsertColumn(0, "Soru", width=300)
        self.qa_list.InsertColumn(1, "Cevap", width=300)
        vbox.Add(self.qa_list, 1, wx.EXPAND | wx.ALL, 5)

        # Öğret butonu
        self.teach_btn = wx.Button(self, label="Yeni Soru-Cevap Ekle")
        vbox.Add(self.teach_btn, 0, wx.ALL, 5)

        self.SetSizer(vbox)

        # Olay bağlama
        self.teach_btn.Bind(wx.EVT_BUTTON, self.on_teach)

        # Soru-cevap listesini doldur
        self.populate_qa_list()

    def populate_qa_list(self):
        """Soru-cevap listesini doldurur."""
        self.qa_list.DeleteAllItems()
        for qa in self.config.get("bilgiler", []):
            idx = self.qa_list.InsertItem(self.qa_list.GetItemCount(), qa.get("soru", ""))
            self.qa_list.SetItem(idx, 1, qa.get("cevap", ""))
        self.frame.SetStatusText("Soru-cevap listesi güncellendi.")

    def on_teach(self, event):
        """Yeni soru-cevap çifti ekler."""
        dlg = wx.TextEntryDialog(self, "Soru gir:", "Yeni Soru")
        if dlg.ShowModal() == wx.ID_OK:
            soru = dlg.GetValue().strip()
        else:
            dlg.Destroy()
            self.frame.SetStatusText("Soru ekleme iptal edildi.")
            return
        dlg.Destroy()

        dlg = wx.TextEntryDialog(self, "Cevap gir:", "Yeni Cevap")
        if dlg.ShowModal() == wx.ID_OK:
            cevap = dlg.GetValue().strip()
        else:
            dlg.Destroy()
            self.frame.SetStatusText("Cevap ekleme iptal edildi.")
            return
        dlg.Destroy()

        qa = {"soru": soru, "cevap": cevap}
        distribute_qapair_to_other_files(qa, base_folder=self.frame.selected_folder)
        self.config.setdefault("bilgiler", []).append(qa)
        save_config(self.config)
        self.populate_qa_list()
        self.frame.chat_panel.add_message(
            f"{self.config.get('robot_adi', 'Robo')}: Yeni soru-cevap öğrendim!", "robot"
        ) if self.frame.chat_panel else None
        self.frame.SetStatusText(f"Yeni soru-cevap eklendi: {soru[:20]}...")

# --- Klasör Seçimi Paneli ---
class FolderPanel(wx.Panel):
    def __init__(self, parent, config, frame):
        super().__init__(parent)
        self.config = config
        self.frame = frame

        # Düzen
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Klasör bilgisi
        self.folder_label = wx.StaticText(self, label=f"Seçili Klasör: {self.frame.selected_folder}")
        vbox.Add(self.folder_label, 0, wx.ALL | wx.EXPAND, 5)

        # Klasör seç butonu
        self.folder_btn = wx.Button(self, label="Klasör Seç")
        vbox.Add(self.folder_btn, 0, wx.ALL, 5)

        self.SetSizer(vbox)

        # Olay bağlama
        self.folder_btn.Bind(wx.EVT_BUTTON, self.on_select_folder)

    def on_select_folder(self, event):
        """Klasör seçimini işler."""
        dlg = wx.DirDialog(self, "Klasör seç")
        if dlg.ShowModal() == wx.ID_OK:
            self.frame.selected_folder = dlg.GetPath()
            self.folder_label.SetLabel(f"Seçili Klasör: {self.frame.selected_folder}")
            self.config["selected_folder"] = self.frame.selected_folder
            save_config(self.config)
            self.frame.SetStatusText(f"Yeni klasör seçildi: {self.frame.selected_folder}")
        else:
            self.frame.SetStatusText("Klasör seçimi iptal edildi.")
        dlg.Destroy()

# --- Main ---
if __name__ == "__main__":
    app = wx.App(False)
    frame = RobotPlayer()
    frame.Show()
    app.MainLoop()