import wx
import json
import os

DATA_FILE = "robot_qna.json"


class RobotApp(wx.Frame):
    def __init__(self, parent, title):
        super(RobotApp, self).__init__(parent, title=title, size=(800, 600))

        # QNA bankasını yükle
        self.qna_bank = self.load_qna()

        splitter = wx.SplitterWindow(self)
        self.tree_panel = wx.Panel(splitter)
        self.content_panel = wx.Panel(splitter)

        # Sol taraftaki ağaç görünümü
        tree_sizer = wx.BoxSizer(wx.VERTICAL)
        self.tree = wx.TreeCtrl(self.tree_panel, style=wx.TR_DEFAULT_STYLE)
        root = self.tree.AddRoot("Kategoriler")
        self.sohbet_item = self.tree.AppendItem(root, "Sohbet")
        self.ogret_item = self.tree.AppendItem(root, "Robota Öğret")
        self.tree.ExpandAll()
        tree_sizer.Add(self.tree, 1, wx.EXPAND)
        self.tree_panel.SetSizer(tree_sizer)

        # İçerik alanı
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content_panel.SetSizer(self.content_sizer)

        splitter.SplitVertically(self.tree_panel, self.content_panel, 200)

        # Ağaç seçim olayı
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_category_changed)

        # Başlangıçta sohbeti aç
        self.show_chat_panel()

    # === Sohbet ekranı ===
    def show_chat_panel(self):
        self.clear_content()
        panel = wx.Panel(self.content_panel)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.chat_log = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.chat_input = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        send_btn = wx.Button(panel, label="Gönder")

        sizer.Add(self.chat_log, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.chat_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        sizer.Add(send_btn, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        panel.SetSizer(sizer)
        self.content_sizer.Add(panel, 1, wx.EXPAND)
        self.content_panel.Layout()

        self.chat_input.Bind(wx.EVT_TEXT_ENTER, self.on_send_message)
        send_btn.Bind(wx.EVT_BUTTON, self.on_send_message)

    def on_send_message(self, event):
        msg = self.chat_input.GetValue().strip()
        if not msg:
            return
        self.chat_log.AppendText(f"Sen: {msg}\n")
        self.chat_input.SetValue("")

        # Robotun cevabı
        if msg in self.qna_bank:
            reply = self.qna_bank[msg]
        else:
            reply = "Bu konuyu bilmiyorum. Bana öğretmek ister miydiniz?"
        self.chat_log.AppendText(f"Robot: {reply}\n")

    # === Öğret ekranı ===
    def show_teach_panel(self):
        self.clear_content()
        panel = wx.Panel(self.content_panel)
        sizer = wx.BoxSizer(wx.VERTICAL)

        info = wx.StaticText(
            panel,
            label="Bu kategoride, Robotunuza soru cevap çiftleri öğretebilirsiniz.",
        )
        ok_btn = wx.Button(panel, label="Tamam")

        sizer.Add(info, 0, wx.ALL, 10)
        sizer.Add(ok_btn, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

        panel.SetSizer(sizer)
        self.content_sizer.Add(panel, 1, wx.EXPAND)
        self.content_panel.Layout()

        ok_btn.Bind(wx.EVT_BUTTON, self.show_empty_teach_panel)

    def show_empty_teach_panel(self, event=None):
        self.clear_content()
        panel = wx.Panel(self.content_panel)
        sizer = wx.BoxSizer(wx.VERTICAL)

        add_btn = wx.Button(panel, label="Ekle")
        sizer.Add(add_btn, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        panel.SetSizer(sizer)
        self.content_sizer.Add(panel, 1, wx.EXPAND)
        self.content_panel.Layout()

        add_btn.Bind(wx.EVT_BUTTON, self.on_add_qna)

    def on_add_qna(self, event):
        dlg = wx.Dialog(self, "Yeni Soru-Cevap Ekle", size=(400, 250))
        vbox = wx.BoxSizer(wx.VERTICAL)

        q_label = wx.StaticText(dlg, label="Soru:")
        self.q_input = wx.TextCtrl(dlg)
        a_label = wx.StaticText(dlg, label="Cevap:")
        self.a_input = wx.TextCtrl(dlg)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        save_btn = wx.Button(dlg, label="Kaydet")
        cancel_btn = wx.Button(dlg, label="İptal")
        hbox.Add(save_btn, 0, wx.ALL, 5)
        hbox.Add(cancel_btn, 0, wx.ALL, 5)

        vbox.Add(q_label, 0, wx.ALL, 5)
        vbox.Add(self.q_input, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(a_label, 0, wx.ALL, 5)
        vbox.Add(self.a_input, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(hbox, 0, wx.ALIGN_RIGHT)

        dlg.SetSizer(vbox)

        save_btn.Bind(wx.EVT_BUTTON, lambda evt: self.save_qna(evt, dlg))
        cancel_btn.Bind(wx.EVT_BUTTON, lambda evt: dlg.Destroy())

        dlg.ShowModal()

    def save_qna(self, event, dlg):
        q = self.q_input.GetValue().strip()
        a = self.a_input.GetValue().strip()
        if q and a:
            self.qna_bank[q] = a
            self.save_qna_to_file()
        dlg.Destroy()

    # === Yardımcı ===
    def clear_content(self):
        for child in self.content_panel.GetChildren():
            child.Destroy()
        self.content_sizer.Clear()

    def on_category_changed(self, event):
        item = event.GetItem()
        if item == self.sohbet_item:
            self.show_chat_panel()
        elif item == self.ogret_item:
            self.show_teach_panel()

    # === Dosya işlemleri ===
    def save_qna_to_file(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.qna_bank, f, ensure_ascii=False, indent=4)
        except Exception as e:
            wx.LogError(f"Kaydetme hatası: {e}")

    def load_qna(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}


if __name__ == "__main__":
    app = wx.App(False)
    frame = RobotApp(None, "Robot")
    frame.Show()
    app.MainLoop()
