import wx
import wx.lib.scrolledpanel as scrolled
import json
import random
import datetime
import os
import pygame
import threading
from dataclasses import dataclass
from typing import List, Dict, Optional

# NVDA tarzı veri modeli
@dataclass
class TeachData:
    questions: List[str]
    answers: List[Dict[str, str]]

@dataclass
class MacroData:
    name: str
    commands: str
    delay: float
    delay_text: str

@dataclass
class Settings:
    robot_name: str = "Otomat"
    user_name: str = ""
    user_surname: str = ""
    greeting_style: str = "Hiçbir Şekilde Hitap Etmesin"
    theme: str = "Aydınlık"
    response_delay: float = 1.0
    show_timestamps: bool = False
    time_format: str = "Basit"
    time_position: str = "Mesaj Başında"
    remember_conversations: bool = True
    play_system_sounds: bool = False
    system_sounds: List[str] = None

    def __post_init__(self):
        if self.system_sounds is None:
            self.system_sounds = []

# NVDA tarzı GUI yardımcı sınıfı
class GuiHelper:
    @staticmethod
    def create_labeled_control(parent, label_text, control_class, **kwargs):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(parent, label=label_text, name=label_text)
        control = control_class(parent, **kwargs)
        control.SetName(label_text)  # Erişilebilirlik için
        label.SetLabelFor(control)  # NVDA için etiket bağlama
        sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        sizer.Add(control, 1, wx.EXPAND | wx.ALL, 5)
        return control, sizer

    @staticmethod
    def add_dialog_buttons(parent, on_save, on_cancel):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        save_btn = wx.Button(parent, label="Kaydet", name="Kaydet")
        cancel_btn = wx.Button(parent, label="İptal", name="İptal")
        save_btn.Bind(wx.EVT_BUTTON, on_save)
        cancel_btn.Bind(wx.EVT_BUTTON, on_cancel)
        sizer.Add(save_btn, 0, wx.ALL, 5)
        sizer.Add(cancel_btn, 0, wx.ALL, 5)
        return sizer

class MacroDialog(wx.Dialog):
    def __init__(self, parent, macro: Optional[MacroData] = None):
        super().__init__(parent, title="Makro Oluştur/Düzenle", size=(400, 300))
        self.macro = macro or MacroData(name="", commands="", delay=0.5, delay_text="Normal")
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.name_ctrl, name_sizer = GuiHelper.create_labeled_control(panel, "Makro Adı:", wx.TextCtrl, value=self.macro.name)
        sizer.Add(name_sizer, 0, wx.EXPAND)

        self.commands_ctrl, commands_sizer = GuiHelper.create_labeled_control(
            panel, "Komut Dizisi (örneğin: sol kolunu kaldır sonra indir):", wx.TextCtrl, value=self.macro.commands, style=wx.TE_MULTILINE
        )
        sizer.Add(commands_sizer, 1, wx.EXPAND)

        self.delay_combo, delay_sizer = GuiHelper.create_labeled_control(
            panel, "Gecikme:", wx.Choice, choices=["Yavaş", "Normal", "Hızlı"], name="Gecikme Seçimi"
        )
        self.delay_combo.SetStringSelection(self.macro.delay_text)
        sizer.Add(delay_sizer, 0, wx.EXPAND)

        sizer.Add(GuiHelper.add_dialog_buttons(panel, self.on_save, lambda evt: self.EndModal(wx.ID_CANCEL)), 0, wx.ALIGN_CENTER)
        panel.SetSizer(sizer)
        self.SetAccessible(wx.Accessible(self))  # Erişilebilirlik için

    def on_save(self, event):
        self.macro.name = self.name_ctrl.GetValue().strip()
        self.macro.commands = self.commands_ctrl.GetValue().strip()
        self.macro.delay_text = self.delay_combo.GetStringSelection()
        self.macro.delay = {"Yavaş": 1.0, "Normal": 0.5, "Hızlı": 0.0}[self.macro.delay_text]
        self.EndModal(wx.ID_OK)

    def get_data(self) -> MacroData:
        return self.macro

class TeachDialog(wx.Dialog):
    def __init__(self, parent, teach_data: Optional[TeachData] = None):
        super().__init__(parent, title="Robota Öğret", size=(600, 500))
        self.panel = scrolled.ScrolledPanel(self)
        self.panel.SetupScrolling()
        self.teach_data = teach_data or TeachData(questions=[""], answers=[{"text": "", "delay": 1.0, "delay_text": "Normal", "sound": ""}])
        self.question_inputs = []
        self.answer_inputs = []
        self.delay_combos = []
        self.sound_inputs = []

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self.panel, label="Sorular:", name="Sorular"), 0, wx.ALL, 5)
        self.question_sizer = wx.BoxSizer(wx.VERTICAL)
        for q in self.teach_data.questions:
            q_input, q_sizer = GuiHelper.create_labeled_control(self.panel, "Soru:", wx.TextCtrl, value=q)
            self.question_inputs.append(q_input)
            self.question_sizer.Add(q_sizer, 0, wx.EXPAND)
        sizer.Add(self.question_sizer, 1, wx.EXPAND)

        add_question_btn = wx.Button(self.panel, label="Soru Ekle", name="Soru Ekle")
        add_question_btn.Bind(wx.EVT_BUTTON, self.add_question)
        sizer.Add(add_question_btn, 0, wx.ALL, 5)

        sizer.Add(wx.StaticText(self.panel, label="Cevaplar:", name="Cevaplar"), 0, wx.ALL, 5)
        self.answer_sizer = wx.BoxSizer(wx.VERTICAL)
        for a in self.teach_data.answers:
            self.add_answer_field(a["text"], a["delay_text"], a["sound"])
        sizer.Add(self.answer_sizer, 1, wx.EXPAND)

        add_answer_btn = wx.Button(self.panel, label="Cevap Ekle", name="Cevap Ekle")
        add_answer_btn.Bind(wx.EVT_BUTTON, self.add_answer)
        sizer.Add(add_answer_btn, 0, wx.ALL, 5)

        sizer.Add(GuiHelper.add_dialog_buttons(self.panel, self.on_save, lambda evt: self.EndModal(wx.ID_CANCEL)), 0, wx.ALIGN_CENTER)
        self.panel.SetSizer(sizer)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        self.SetAccessible(wx.Accessible(self))

    def add_question(self, event):
        q_input, q_sizer = GuiHelper.create_labeled_control(self.panel, "Soru:", wx.TextCtrl)
        self.question_inputs.append(q_input)
        self.question_sizer.Add(q_sizer, 0, wx.EXPAND)
        self.question_sizer.Layout()
        self.panel.SetupScrolling()

    def add_answer_field(self, text="", delay_text="Normal", sound=""):
        answer_panel = wx.Panel(self.panel)
        answer_sizer = wx.BoxSizer(wx.VERTICAL)

        answer_input, answer_sizer_inner = GuiHelper.create_labeled_control(
            answer_panel, f"Cevap {len(self.answer_inputs) + 1}:", wx.TextCtrl, value=text, style=wx.TE_MULTILINE
        )
        answer_sizer.Add(answer_sizer_inner, 1, wx.EXPAND)

        delay_combo, delay_sizer_inner = GuiHelper.create_labeled_control(
            answer_panel, "Yanıt Hızı:", wx.Choice, choices=["Yavaş", "Normal", "Hızlı"], name="Yanıt Hızı"
        )
        delay_combo.SetStringSelection(delay_text)
        answer_sizer.Add(delay_sizer_inner, 0, wx.EXPAND)

        sound_input, sound_sizer = GuiHelper.create_labeled_control(answer_panel, "Ses:", wx.TextCtrl, value=sound, style=wx.TE_READONLY)
        select_btn = wx.Button(answer_panel, label="Ses Seç", name="Ses Seç")
        select_btn.Bind(wx.EVT_BUTTON, lambda evt: self.select_sound(sound_input))
        sound_sizer.Add(select_btn, 0, wx.ALL, 5)

        answer_sizer.Add(sound_sizer, 0, wx.EXPAND)
        answer_panel.SetSizer(answer_sizer)
        self.answer_inputs.append(answer_input)
        self.delay_combos.append(delay_combo)
        self.sound_inputs.append(sound_input)
        self.answer_sizer.Add(answer_panel, 0, wx.EXPAND)
        self.answer_sizer.Layout()
        self.panel.SetupScrolling()

    def select_sound(self, sound_input):
        dialog = wx.FileDialog(self, "WAV Dosyası Seç", wildcard="WAV Files (*.wav)|*.wav", style=wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            sound_input.SetValue(dialog.GetPath())
        dialog.Destroy()

    def on_save(self, event):
        questions = [q.GetValue().strip() for q in self.question_inputs if q.GetValue().strip()]
        answers = [
            {
                "text": a.GetValue().strip(),
                "delay": {"Yavaş": 2.0, "Normal": 1.0, "Hızlı": 0.0}[d.GetStringSelection()],
                "delay_text": d.GetStringSelection(),
                "sound": s.GetValue()
            }
            for a, d, s in zip(self.answer_inputs, self.delay_combos, self.sound_inputs) if a.GetValue().strip()
        ]
        self.teach_data = TeachData(questions=questions, answers=answers)
        self.EndModal(wx.ID_OK)

    def get_data(self) -> TeachData:
        return self.teach_data

class SettingsDialog(wx.Dialog):
    def __init__(self, parent, settings: Settings):
        super().__init__(parent, title="Ayarlar", size=(400, 400))
        self.settings = settings
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.name_ctrl, name_sizer = GuiHelper.create_labeled_control(panel, "Adınız:", wx.TextCtrl, value=self.settings.user_name)
        sizer.Add(name_sizer, 0, wx.EXPAND)

        self.surname_ctrl, surname_sizer = GuiHelper.create_labeled_control(panel, "Soyadınız:", wx.TextCtrl, value=self.settings.user_surname)
        sizer.Add(surname_sizer, 0, wx.EXPAND)

        self.greeting_combo, greeting_sizer = GuiHelper.create_labeled_control(
            panel, "Hitap Şekli:", wx.Choice, choices=[
                "Adımla ve Soyadımla", "Soyadımla ve Adımla", "Sadece Adımla",
                "Sadece Soyadımla", "Hiçbir Şekilde Hitap Etmesin"
            ], name="Hitap Şekli"
        )
        self.greeting_combo.SetStringSelection(self.settings.greeting_style)
        sizer.Add(greeting_sizer, 0, wx.EXPAND)

        self.theme_combo, theme_sizer = GuiHelper.create_labeled_control(
            panel, "Tema:", wx.Choice, choices=["Aydınlık", "Karanlık"], name="Tema Seçimi"
        )
        self.theme_combo.SetStringSelection(self.settings.theme)
        sizer.Add(theme_sizer, 0, wx.EXPAND)

        self.speed_combo, speed_sizer = GuiHelper.create_labeled_control(
            panel, "Yanıt Hızı:", wx.Choice, choices=["Yavaş", "Normal", "Hızlı"], name="Yanıt Hızı"
        )
        self.speed_combo.SetStringSelection({2.0: "Yavaş", 1.0: "Normal", 0.0: "Hızlı"}[self.settings.response_delay])
        sizer.Add(speed_sizer, 0, wx.EXPAND)

        self.show_timestamps = wx.CheckBox(panel, label="Mesaj Tarihlerini Göster", name="Mesaj Tarihlerini Göster")
        self.show_timestamps.SetValue(self.settings.show_timestamps)
        sizer.Add(self.show_timestamps, 0, wx.ALL, 5)

        self.time_format_combo, time_format_sizer = GuiHelper.create_labeled_control(
            panel, "Tarih Formatı:", wx.Choice, choices=["Basit", "Detaylı"], name="Tarih Formatı"
        )
        self.time_format_combo.SetStringSelection(self.settings.time_format)
        sizer.Add(time_format_sizer, 0, wx.EXPAND)

        self.time_position_combo, time_position_sizer = GuiHelper.create_labeled_control(
            panel, "Tarih Konumu:", wx.Choice, choices=["Mesaj Başında", "Mesaj Sonunda"], name="Tarih Konumu"
        )
        self.time_position_combo.SetStringSelection(self.settings.time_position)
        sizer.Add(time_position_sizer, 0, wx.EXPAND)

        self.remember_conversations = wx.CheckBox(panel, label="Görüşmeleri Hatırla", name="Görüşmeleri Hatırla")
        self.remember_conversations.SetValue(self.settings.remember_conversations)
        sizer.Add(self.remember_conversations, 0, wx.ALL, 5)

        self.play_system_sounds = wx.CheckBox(panel, label="Sistem Seslerini Çal", name="Sistem Seslerini Çal")
        self.play_system_sounds.SetValue(self.settings.play_system_sounds)
        sizer.Add(self.play_system_sounds, 0, wx.ALL, 5)

        self.system_sounds_list, system_sounds_sizer = GuiHelper.create_labeled_control(
            panel, "Sistem Sesleri:", wx.ListBox, style=wx.LB_SINGLE, name="Sistem Sesleri"
        )
        for sound in self.settings.system_sounds:
            self.system_sounds_list.Append(sound)
        sizer.Add(system_sounds_sizer, 1, wx.EXPAND)

        add_sound_btn = wx.Button(panel, label="Ses Ekle", name="Ses Ekle")
        add_sound_btn.Bind(wx.EVT_BUTTON, self.add_system_sound)
        sizer.Add(add_sound_btn, 0, wx.ALL, 5)

        sizer.Add(GuiHelper.add_dialog_buttons(panel, self.on_save, lambda evt: self.EndModal(wx.ID_CANCEL)), 0, wx.ALIGN_CENTER)
        panel.SetSizer(sizer)
        self.SetAccessible(wx.Accessible(self))

    def add_system_sound(self, event):
        dialog = wx.FileDialog(self, "WAV Dosyası Seç", wildcard="WAV Files (*.wav)|*.wav", style=wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.system_sounds_list.Append(dialog.GetPath())
        dialog.Destroy()

    def on_save(self, event):
        self.settings.user_name = self.name_ctrl.GetValue().strip()
        self.settings.user_surname = self.surname_ctrl.GetValue().strip()
        self.settings.greeting_style = self.greeting_combo.GetStringSelection()
        self.settings.theme = self.theme_combo.GetStringSelection()
        self.settings.response_delay = {"Yavaş": 2.0, "Normal": 1.0, "Hızlı": 0.0}[self.speed_combo.GetStringSelection()]
        self.settings.show_timestamps = self.show_timestamps.GetValue()
        self.settings.time_format = self.time_format_combo.GetStringSelection()
        self.settings.time_position = self.time_position_combo.GetStringSelection()
        self.settings.remember_conversations = self.remember_conversations.GetValue()
        self.settings.play_system_sounds = self.play_system_sounds.GetValue()
        self.settings.system_sounds = [self.system_sounds_list.GetString(i) for i in range(self.system_sounds_list.GetCount())]
        self.EndModal(wx.ID_OK)

    def get_data(self) -> Settings:
        return self.settings

class RobotApp(wx.App):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.teach_data: List[TeachData] = []
        self.macro_data: List[MacroData] = []
        self.chat_messages: List[str] = []
        self.answer_colors = [
            wx.Colour(173, 216, 230), wx.Colour(144, 238, 144), wx.Colour(255, 182, 193),
            wx.Colour(255, 215, 0), wx.Colour(230, 230, 250)
        ]
        pygame.mixer.init()
        self.conversation_file = "conversations.json"
        if self.settings.remember_conversations:
            self.load_conversations()

    def OnInit(self):
        self.frame = RobotFrame(None, self)
        self.frame.Show()
        return True

    def play_sound(self, sound_path):
        try:
            pygame.mixer.Sound(sound_path).play()
            time.sleep(pygame.mixer.Sound(sound_path).get_length())
        except Exception as e:
            wx.LogError(f"Ses oynatma hatası: {e}")

    def save_conversations(self):
        if self.settings.remember_conversations:
            data = {
                "settings": self.settings.__dict__,
                "teach_data": [td.__dict__ for td in self.teach_data],
                "macro_data": [md.__dict__ for md in self.macro_data],
                "chat_messages": self.chat_messages,
            }
            with open(self.conversation_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

    def load_conversations(self):
        if os.path.exists(self.conversation_file):
            with open(self.conversation_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.settings = Settings(**data.get("settings", {}))
            self.teach_data = [TeachData(**td) for td in data.get("teach_data", [])]
            self.macro_data = [MacroData(**md) for md in data.get("macro_data", [])]
            self.chat_messages = data.get("chat_messages", [])

class RobotFrame(wx.Frame):
    def __init__(self, parent, app: RobotApp):
        super().__init__(parent, title="Robot Yazılımı", size=(800, 600))
        self.app = app
        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.tree = wx.TreeCtrl(self.panel, name="Kategoriler")
        root = self.tree.AddRoot("Kategoriler")
        self.items = {}
        categories = ["Sohbet", "Robota Öğret", "Makro Oluştur", "Ayarlar"]
        for cat in categories:
            item = self.tree.AppendItem(root, cat)
            self.items[cat] = item
        self.tree.Expand(root)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_category_selected)
        self.main_sizer.Add(self.tree, 0, wx.EXPAND | wx.ALL, 5)

        self.notebook = wx.Notebook(self.panel, name="Sekmeler")
        self.chat_page = self.create_chat_page()
        self.teach_page = self.create_teach_page()
        self.macro_page = self.create_macro_page()
        self.settings_page = self.create_settings_page()

        self.notebook.AddPage(self.chat_page, "Sohbet")
        self.notebook.AddPage(self.teach_page, "Robota Öğret")
        self.notebook.AddPage(self.macro_page, "Makro Oluştur")
        self.notebook.AddPage(self.settings_page, "Ayarlar")

        self.main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizer(self.main_sizer)
        self.apply_theme()
        self.update_ui()
        self.SetAccessible(wx.Accessible(self))

    def apply_theme(self):
        bg_color = wx.Colour(255, 255, 255) if self.app.settings.theme == "Aydınlık" else wx.Colour(43, 43, 43)
        user_bg = wx.Colour(200, 200, 200) if self.app.settings.theme == "Aydınlık" else wx.Colour(100, 100, 100)
        self.SetBackgroundColour(bg_color)
        for i in range(self.chat_display.GetCount()):
            item = self.chat_display.GetString(i)
            if item.startswith(f"{self.app.settings.robot_name}:") or item.startswith("Robot:"):
                self.chat_display.SetItemBackgroundColour(i, self.get_answer_color(item))
            else:
                self.chat_display.SetItemBackgroundColour(i, user_bg)
        self.Refresh()

    def get_answer_color(self, text):
        for data in self.app.teach_data:
            for i, answer in enumerate(data.answers):
                if answer["text"] in text:
                    return self.app.answer_colors[i % len(self.app.answer_colors)]
        return wx.Colour(255, 255, 255) if self.app.settings.theme == "Aydınlık" else wx.Colour(64, 64, 64)

    def create_chat_page(self):
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.title_label = wx.StaticText(panel, label=self.app.settings.robot_name, name="Robot Adı")
        self.title_label.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizer.Add(self.title_label, 0, wx.ALL, 5)

        self.chat_display = wx.ListBox(panel, style=wx.LB_MULTIPLE, name="Sohbet Geçmişi")
        sizer.Add(self.chat_display, 1, wx.EXPAND | wx.ALL, 5)

        self.chat_input, input_sizer = GuiHelper.create_labeled_control(panel, "Mesaj:", wx.TextCtrl)
        send_btn = wx.Button(panel, label="Gönder", name="Mesaj Gönder")
        send_btn.Bind(wx.EVT_BUTTON, self.send_chat_message)
        input_sizer.Add(send_btn, 0, wx.ALL, 5)
        sizer.Add(input_sizer, 0, wx.EXPAND)

        panel.SetSizer(sizer)
        return panel

    def create_teach_page(self):
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        add_btn = wx.Button(panel, label="Öğret", name="Öğret")
        add_btn.Bind(wx.EVT_BUTTON, self.add_teach_item)
        sizer.Add(add_btn, 0, wx.ALL, 5)

        self.teach_list = wx.ListBox(panel, style=wx.LB_SINGLE, name="Öğrenilenler")
        self.teach_list.Bind(wx.EVT_RIGHT_DOWN, self.show_teach_context_menu)
        sizer.Add(self.teach_list, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)
        return panel

    def create_macro_page(self):
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        add_btn = wx.Button(panel, label="Makro Ekle", name="Makro Ekle")
        add_btn.Bind(wx.EVT_BUTTON, self.