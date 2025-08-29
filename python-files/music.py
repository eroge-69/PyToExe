import wx
import wx.media
import os
import random
import sys
import math
import json
import time

class EqualizerDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Ekolayzır Ayarları", size=(400, 300))
        self.parent = parent
        self.eq_settings = parent.eq_settings.copy()
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        eq_sizer = wx.BoxSizer(wx.VERTICAL)
        self.eq_sliders = {}
        for band in ["60 Hz", "250 Hz", "1 kHz", "4 kHz", "16 kHz"]:
            band_label = wx.StaticText(self, label=band)
            slider = wx.Slider(self, value=self.eq_settings[band], minValue=-12, maxValue=12)
            slider.Bind(wx.EVT_SLIDER, lambda e, b=band: self.on_eq_change(b, e))
            self.eq_sliders[band] = slider
            eq_sizer.Add(band_label, 0, wx.ALL, 2)
            eq_sizer.Add(slider, 0, wx.EXPAND | wx.ALL, 2)
        
        preset_label = wx.StaticText(self, label="Ekolayzır Ön Ayarları")
        self.eq_preset_choice = wx.Choice(self, choices=["Düz", "Pop", "Rock", "Klasik", "Jazz"])
        self.eq_preset_choice.SetSelection(0)
        self.eq_preset_choice.Bind(wx.EVT_CHOICE, self.on_eq_preset)
        eq_sizer.Add(preset_label, 0, wx.ALL, 5)
        eq_sizer.Add(self.eq_preset_choice, 0, wx.ALL, 5)
        
        reset_btn = wx.Button(self, label="Ekolayzırı Sıfırla")
        reset_btn.Bind(wx.EVT_BUTTON, self.on_eq_reset)
        eq_sizer.Add(reset_btn, 0, wx.ALL, 5)
        
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(self, wx.ID_OK, label="Tamam")
        cancel_btn = wx.Button(self, wx.ID_CANCEL, label="İptal")
        btn_sizer.Add(ok_btn, 0, wx.ALL, 5)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        
        sizer.Add(eq_sizer, 1, wx.EXPAND | wx.ALL, 10)
        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER)
        self.SetSizer(sizer)
        
    def on_eq_change(self, band, event):
        self.eq_settings[band] = self.eq_sliders[band].GetValue()
        print(f"Ekolayzır güncellendi: {band} = {self.eq_settings[band]} dB")
        
    def on_eq_preset(self, event):
        preset = self.eq_preset_choice.GetStringSelection()
        presets = {
            "Düz": {"60 Hz": 0, "250 Hz": 0, "1 kHz": 0, "4 kHz": 0, "16 kHz": 0},
            "Pop": {"60 Hz": 4, "250 Hz": 2, "1 kHz": 0, "4 kHz": 2, "16 kHz": 4},
            "Rock": {"60 Hz": 8, "250 Hz": 4, "1 kHz": -2, "4 kHz": 4, "16 kHz": 8},
            "Klasik": {"60 Hz": 2, "250 Hz": 0, "1 kHz": 0, "4 kHz": 0, "16 kHz": 2},
            "Jazz": {"60 Hz": 4, "250 Hz": 2, "1 kHz": 2, "4 kHz": 2, "16 kHz": 4}
        }
        for band, value in presets[preset].items():
            self.eq_settings[band] = value
            self.eq_sliders[band].SetValue(value)
        print(f"Ekolayzır ön ayarı uygulandı: {preset}")
        
    def on_eq_reset(self, event):
        for band in self.eq_settings:
            self.eq_settings[band] = 0
            self.eq_sliders[band].SetValue(0)
        self.eq_preset_choice.SetSelection(0)
        print("Ekolayzır sıfırlandı")

class MusicPlayer(wx.Frame):
    def __init__(self, title, file_to_play=None):
        super().__init__(None, title=title, size=(800, 600))
        
        self.current_song = None
        self.playlist_data = []  # (path, name, artist, duration)
        self.played_songs = []
        self.queue_data = []  # Kuyruk için index'ler
        self.is_playing = False
        self.visualization_on = False
        self.visual_type = "Hipnotik Daireler"
        self.show_categories = True
        self.theme = "Aydınlık"
        self.playback_speed = 1.0
        self.shuffle_mode = False
        self.volume_visible = False
        self.volume_fixed = False
        self.crossfade_enabled = False
        self.crossfade_duration = 0
        self.skip_silence_enabled = False
        self.silence_threshold = -40
        self.silence_min_duration = 500
        self.prevent_duplicates = False
        self.prevent_repeats = False
        self.eq_settings = {
            "60 Hz": 0, "250 Hz": 0, "1 kHz": 0, "4 kHz": 0, "16 kHz": 0
        }
        self.artist_groups = {}
        self.mini_player_visible = True  # Mini oynatıcı varsayılan açık
        
        # Notebook
        self.notebook = wx.Notebook(self)
        self.main_panel = wx.Panel(self.notebook)
        self.notebook.AddPage(self.main_panel, "Ana Ekran")
        self.settings_panel = wx.Panel(self.notebook)
        self.notebook.AddPage(self.settings_panel, "Ayarlar")
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_page_changed)
        
        # Media Ctrl
        self.media_ctrl = wx.media.MediaCtrl(self.main_panel)
        
        # Categories Tree
        self.categories_tree = wx.TreeCtrl(self.main_panel, style=wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS)
        root = self.categories_tree.AddRoot("Kök")
        self.categories_tree.AppendItem(root, "Çalma Listeleri")
        self.categories_tree.AppendItem(root, "Parçalar")
        self.artist_node = self.categories_tree.AppendItem(root, "Sanatçılar")
        self.categories_tree.AppendItem(root, "Albümler")
        self.categories_tree.AppendItem(root, "Türler")
        self.categories_tree.AppendItem(root, "Besteciler")
        self.categories_tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_category_select)
        
        # Playlist
        self.playlist = wx.ListCtrl(self.main_panel, style=wx.LC_REPORT)
        self.playlist.InsertColumn(0, "Şarkı Adı", width=200)
        self.playlist.InsertColumn(1, "Sanatçı", width=150)
        self.playlist.InsertColumn(2, "Süre", width=100)
        self.playlist.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select_song)
        self.playlist.Bind(wx.EVT_CHAR, self.on_playlist_key)
        self.playlist.Bind(wx.EVT_CONTEXT_MENU, self.on_playlist_context_menu)
        
        # Queue List
        self.queue_list = wx.ListCtrl(self.main_panel, style=wx.LC_REPORT)
        self.queue_list.InsertColumn(0, "Kuyruk Şarkı Adı", width=200)
        self.queue_list.InsertColumn(1, "Sanatçı", width=150)
        self.queue_list.Bind(wx.EVT_CONTEXT_MENU, self.on_queue_context_menu)
        
        # Song Info
        self.song_info = wx.StaticText(self.main_panel, label="Şu an çalan: Yok")
        
        # Progress Slider
        self.progress = wx.Slider(self.main_panel)
        self.progress_timer = wx.Timer(self)
        self.progress_timer.Bind(wx.EVT_TIMER, self.update_progress)
        
        # Visual Panel
        self.visual_panel = wx.Panel(self.main_panel, size=(200, 200))
        self.visual_panel.Bind(wx.EVT_PAINT, self.on_paint_visual)
        self.visual_timer = wx.Timer(self)
        self.visual_timer.Bind(wx.EVT_TIMER, self.update_visual)
        
        # Mini Player (Ana panelde)
        self.mini_player = wx.Panel(self.main_panel)
        self.mini_song_info = wx.StaticText(self.mini_player, label="Şu an çalan: Yok", style=wx.ST_ELLIPSIZE_END)
        self.mini_play_btn = wx.Button(self.mini_player, label="▶", size=(30, 30))
        self.mini_pause_btn = wx.Button(self.mini_player, label="||", size=(30, 30))
        self.mini_next_btn = wx.Button(self.mini_player, label=">>", size=(30, 30))
        self.mini_prev_btn = wx.Button(self.mini_player, label="<<", size=(30, 30))
        self.mini_forward_btn = wx.Button(self.mini_player, label="+10s", size=(40, 30))
        self.mini_progress = wx.Slider(self.mini_player, size=(100, -1))
        self.mini_full_ui_btn = wx.Button(self.mini_player, label="Tam Arayüz", size=(80, 30))
        
        mini_sizer = wx.BoxSizer(wx.HORIZONTAL)
        mini_sizer.Add(self.mini_song_info, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        mini_sizer.Add(self.mini_play_btn, 0, wx.ALL, 2)
        mini_sizer.Add(self.mini_pause_btn, 0, wx.ALL, 2)
        mini_sizer.Add(self.mini_next_btn, 0, wx.ALL, 2)
        mini_sizer.Add(self.mini_prev_btn, 0, wx.ALL, 2)
        mini_sizer.Add(self.mini_forward_btn, 0, wx.ALL, 2)
        mini_sizer.Add(self.mini_progress, 1, wx.ALL | wx.EXPAND, 2)
        mini_sizer.Add(self.mini_full_ui_btn, 0, wx.ALL, 2)
        self.mini_player.SetSizer(mini_sizer)
        
        # Mini Player (Ayarlar sekmesinde)
        self.settings_mini_player = wx.Panel(self.settings_panel)
        self.settings_mini_song_info = wx.StaticText(self.settings_mini_player, label="Şu an çalan: Yok", style=wx.ST_ELLIPSIZE_END)
        self.settings_mini_play_btn = wx.Button(self.settings_mini_player, label="▶", size=(30, 30))
        self.settings_mini_pause_btn = wx.Button(self.settings_mini_player, label="||", size=(30, 30))
        self.settings_mini_next_btn = wx.Button(self.settings_mini_player, label=">>", size=(30, 30))
        self.settings_mini_prev_btn = wx.Button(self.settings_mini_player, label="<<", size=(30, 30))
        self.settings_mini_forward_btn = wx.Button(self.settings_mini_player, label="+10s", size=(40, 30))
        self.settings_mini_progress = wx.Slider(self.settings_mini_player, size=(100, -1))
        
        settings_mini_sizer = wx.BoxSizer(wx.HORIZONTAL)
        settings_mini_sizer.Add(self.settings_mini_song_info, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        settings_mini_sizer.Add(self.settings_mini_play_btn, 0, wx.ALL, 2)
        settings_mini_sizer.Add(self.settings_mini_pause_btn, 0, wx.ALL, 2)
        settings_mini_sizer.Add(self.settings_mini_next_btn, 0, wx.ALL, 2)
        settings_mini_sizer.Add(self.settings_mini_prev_btn, 0, wx.ALL, 2)
        settings_mini_sizer.Add(self.settings_mini_forward_btn, 0, wx.ALL, 2)
        settings_mini_sizer.Add(self.settings_mini_progress, 1, wx.ALL | wx.EXPAND, 2)
        self.settings_mini_player.SetSizer(settings_mini_sizer)
        
        # Controls
        self.play_btn = wx.Button(self.main_panel, label="Oynat")
        self.pause_btn = wx.Button(self.main_panel, label="Duraklat")
        self.stop_btn = wx.Button(self.main_panel, label="Durdur")
        self.next_btn = wx.Button(self.main_panel, label="Sonraki")
        self.prev_btn = wx.Button(self.main_panel, label="Önceki")
        self.forward_btn = wx.Button(self.main_panel, label="İleri Sar (10s)")
        self.shuffle_btn = wx.Button(self.main_panel, label="Karıştır (Sıralı)")
        self.volume_btn = wx.Button(self.main_panel, label="Ses Seviyesi")
        self.playlist_btn = wx.Button(self.main_panel, label="Şarkı Listesi")
        self.add_file_btn = wx.Button(self.main_panel, label="Dosya Seç")
        self.add_folder_btn = wx.Button(self.main_panel, label="Klasör Seç")
        self.eq_btn = wx.Button(self.main_panel, label="Ekolayzır")
        self.save_list_btn = wx.Button(self.main_panel, label="Listeyi Kaydet")
        
        # Volume Slider
        self.volume_slider = wx.Slider(self.main_panel, value=100, minValue=0, maxValue=100)
        self.volume_slider.Bind(wx.EVT_SLIDER, self.on_volume_change)
        self.volume_slider.Hide()
        
        # Main Layout
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.top_sizer.Add(self.add_file_btn, 0, wx.ALL, 5)
        self.top_sizer.Add(self.add_folder_btn, 0, wx.ALL, 5)
        self.top_sizer.Add(self.eq_btn, 0, wx.ALL, 5)
        self.top_sizer.Add(self.save_list_btn, 0, wx.ALL, 5)
        self.top_sizer.AddStretchSpacer()
        self.top_sizer.Add(self.volume_slider, 1, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(self.top_sizer, 0, wx.EXPAND)
        
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.left_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.left_sizer.Add(self.categories_tree, 1, wx.EXPAND | wx.ALL, 5)
        
        self.right_sizer.Add(self.playlist, 1, wx.EXPAND | wx.ALL, 5)
        self.right_sizer.Add(self.queue_list, 1, wx.EXPAND | wx.ALL, 5)
        self.right_sizer.Add(self.song_info, 0, wx.ALL, 5)
        self.right_sizer.Add(self.progress, 0, wx.EXPAND | wx.ALL, 5)
        self.right_sizer.Add(self.visual_panel, 0, wx.EXPAND | wx.ALL, 5)
        
        self.control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.control_sizer.Add(self.play_btn, 0, wx.ALL, 5)
        self.control_sizer.Add(self.pause_btn, 0, wx.ALL, 5)
        self.control_sizer.Add(self.stop_btn, 0, wx.ALL, 5)
        self.control_sizer.Add(self.next_btn, 0, wx.ALL, 5)
        self.control_sizer.Add(self.prev_btn, 0, wx.ALL, 5)
        self.control_sizer.Add(self.forward_btn, 0, wx.ALL, 5)
        self.control_sizer.Add(self.shuffle_btn, 0, wx.ALL, 5)
        self.control_sizer.Add(self.volume_btn, 0, wx.ALL, 5)
        self.control_sizer.Add(self.playlist_btn, 0, wx.ALL, 5)
        
        self.right_sizer.Add(self.control_sizer, 0, wx.ALIGN_CENTER)
        self.right_sizer.Add(self.mini_player, 0, wx.EXPAND | wx.ALL, 5)
        
        content_sizer.Add(self.left_sizer, 0, wx.EXPAND)
        content_sizer.Add(self.right_sizer, 1, wx.EXPAND)
        self.main_sizer.Add(content_sizer, 1, wx.EXPAND)
        
        self.main_panel.SetSizer(self.main_sizer)
        
        # Settings Layout
        settings_sizer = wx.BoxSizer(wx.VERTICAL)
        
        speed_label = wx.StaticText(self.settings_panel, label="Oynatma Hızı (0.5x - 2x)")
        self.speed_slider = wx.Slider(self.settings_panel, value=10, minValue=5, maxValue=20)
        self.speed_slider.Bind(wx.EVT_SLIDER, self.on_speed_change)
        settings_sizer.Add(speed_label, 0, wx.ALL, 5)
        settings_sizer.Add(self.speed_slider, 0, wx.EXPAND | wx.ALL, 5)
        
        self.categories_check = wx.CheckBox(self.settings_panel, label="Sol Kategorileri Göster")
        self.categories_check.SetValue(True)
        self.categories_check.Bind(wx.EVT_CHECKBOX, self.on_toggle_categories)
        settings_sizer.Add(self.categories_check, 0, wx.ALL, 5)
        
        theme_label = wx.StaticText(self.settings_panel, label="Tema")
        self.theme_choice = wx.Choice(self.settings_panel, choices=["Aydınlık", "Karanlık"])
        self.theme_choice.SetSelection(0)
        self.theme_choice.Bind(wx.EVT_CHOICE, self.on_theme_change)
        settings_sizer.Add(theme_label, 0, wx.ALL, 5)
        self.theme_choice.Bind(wx.EVT_CHOICE, self.on_theme_change)
        settings_sizer.Add(self.theme_choice, 0, wx.ALL, 5)
        
        self.visual_check = wx.CheckBox(self.settings_panel, label="Animasyon Göster")
        self.visual_check.Bind(wx.EVT_CHECKBOX, self.on_toggle_visual)
        settings_sizer.Add(self.visual_check, 0, wx.ALL, 5)
        
        visual_type_label = wx.StaticText(self.settings_panel, label="Animasyon Tipi")
        self.visual_type_choice = wx.Choice(self.settings_panel, choices=["Hipnotik Daireler", "Rastgele Çizgiler", "Dalga Efekti", "Parlayan Kareler", "Yıldızlar", "Spiral", "Uçuşan Notalar", "Fireworks", "Waveform"])
        self.visual_type_choice.SetSelection(0)
        self.visual_type_choice.Bind(wx.EVT_CHOICE, self.on_visual_type_change)
        settings_sizer.Add(visual_type_label, 0, wx.ALL, 5)
        settings_sizer.Add(self.visual_type_choice, 0, wx.ALL, 5)
        
        self.volume_fixed_check = wx.CheckBox(self.settings_panel, label="Ses Seviyesini Sabit Tut")
        self.volume_fixed_check.Bind(wx.EVT_CHECKBOX, self.on_toggle_volume_fixed)
        settings_sizer.Add(self.volume_fixed_check, 0, wx.ALL, 5)
        
        self.crossfade_check = wx.CheckBox(self.settings_panel, label="Çapraz Sönümlemeyi Etkinleştir")
        self.crossfade_check.Bind(wx.EVT_CHECKBOX, self.on_toggle_crossfade)
        settings_sizer.Add(self.crossfade_check, 0, wx.ALL, 5)
        
        crossfade_label = wx.StaticText(self.settings_panel, label="Çapraz Sönümleme Süresi (0-10s)")
        self.crossfade_slider = wx.Slider(self.settings_panel, value=0, minValue=0, maxValue=100)
        self.crossfade_slider.Enable(False)
        self.crossfade_slider.Bind(wx.EVT_SLIDER, self.on_crossfade_change)
        settings_sizer.Add(crossfade_label, 0, wx.ALL, 5)
        settings_sizer.Add(self.crossfade_slider, 0, wx.EXPAND | wx.ALL, 5)
        
        self.skip_silence_check = wx.CheckBox(self.settings_panel, label="Sessiz Süreleri Atla")
        self.skip_silence_check.Bind(wx.EVT_CHECKBOX, self.on_toggle_skip_silence)
        settings_sizer.Add(self.skip_silence_check, 0, wx.ALL, 5)
        
        silence_threshold_label = wx.StaticText(self.settings_panel, label="Sessizlik Eşiği (dB)")
        self.silence_threshold_slider = wx.Slider(self.settings_panel, value=-40, minValue=-60, maxValue=0)
        self.silence_threshold_slider.Enable(False)
        self.silence_threshold_slider.Bind(wx.EVT_SLIDER, self.on_silence_threshold_change)
        settings_sizer.Add(silence_threshold_label, 0, wx.ALL, 5)
        settings_sizer.Add(self.silence_threshold_slider, 0, wx.EXPAND | wx.ALL, 5)
        
        silence_duration_label = wx.StaticText(self.settings_panel, label="Minimum Sessizlik Süresi (ms)")
        self.silence_duration_slider = wx.Slider(self.settings_panel, value=500, minValue=100, maxValue=2000)
        self.silence_duration_slider.Enable(False)
        self.silence_duration_slider.Bind(wx.EVT_SLIDER, self.on_silence_duration_change)
        settings_sizer.Add(silence_duration_label, 0, wx.ALL, 5)
        settings_sizer.Add(self.silence_duration_slider, 0, wx.EXPAND | wx.ALL, 5)
        
        self.prevent_duplicates_check = wx.CheckBox(self.settings_panel, label="Yinelenen Şarkılara İzin Verme")
        self.prevent_duplicates_check.Bind(wx.EVT_CHECKBOX, self.on_toggle_prevent_duplicates)
        settings_sizer.Add(self.prevent_duplicates_check, 0, wx.ALL, 5)
        
        self.prevent_repeats_check = wx.CheckBox(self.settings_panel, label="Sırada Tekrarlara İzin Verme")
        self.prevent_repeats_check.Bind(wx.EVT_CHECKBOX, self.on_toggle_prevent_repeats)
        settings_sizer.Add(self.prevent_repeats_check, 0, wx.ALL, 5)
        
        self.import_playlist_btn = wx.Button(self.settings_panel, label="Çalma Listesini İçe Aktar")
        self.import_playlist_btn.Bind(wx.EVT_BUTTON, self.on_import_playlist)
        settings_sizer.Add(self.import_playlist_btn, 0, wx.ALL, 5)
        
        self.export_playlist_btn = wx.Button(self.settings_panel, label="Çalma Listesini Dışa Aktar")
        self.export_playlist_btn.Bind(wx.EVT_BUTTON, self.on_export_playlist)
        settings_sizer.Add(self.export_playlist_btn, 0, wx.ALL, 5)
        
        settings_sizer.Add(self.settings_mini_player, 0, wx.EXPAND | wx.ALL, 5)
        
        self.settings_panel.SetSizer(settings_sizer)
        
        # Bindings
        self.add_file_btn.Bind(wx.EVT_BUTTON, self.on_add_file)
        self.add_folder_btn.Bind(wx.EVT_BUTTON, self.on_add_folder)
        self.save_list_btn.Bind(wx.EVT_BUTTON, self.on_save_list_to_desktop)
        self.eq_btn.Bind(wx.EVT_BUTTON, self.on_show_equalizer)
        self.play_btn.Bind(wx.EVT_BUTTON, self.on_play)
        self.pause_btn.Bind(wx.EVT_BUTTON, self.on_pause)
        self.stop_btn.Bind(wx.EVT_BUTTON, self.on_stop)
        self.next_btn.Bind(wx.EVT_BUTTON, self.on_next)
        self.prev_btn.Bind(wx.EVT_BUTTON, self.on_prev)
        self.forward_btn.Bind(wx.EVT_BUTTON, self.on_forward)
        self.shuffle_btn.Bind(wx.EVT_BUTTON, self.on_shuffle)
        self.volume_btn.Bind(wx.EVT_BUTTON, self.on_toggle_volume)
        self.playlist_btn.Bind(wx.EVT_BUTTON, self.on_show_playlist)
        self.media_ctrl.Bind(wx.EVT_MEDIA_LOADED, self.on_media_loaded)
        self.media_ctrl.Bind(wx.EVT_MEDIA_FINISHED, self.on_media_finished)
        self.progress.Bind(wx.EVT_SLIDER, self.on_seek)
        
        # Mini Player Bindings
        self.mini_play_btn.Bind(wx.EVT_BUTTON, self.on_play)
        self.mini_pause_btn.Bind(wx.EVT_BUTTON, self.on_pause)
        self.mini_next_btn.Bind(wx.EVT_BUTTON, self.on_next)
        self.mini_prev_btn.Bind(wx.EVT_BUTTON, self.on_prev)
        self.mini_forward_btn.Bind(wx.EVT_BUTTON, self.on_forward)
        self.mini_progress.Bind(wx.EVT_SLIDER, self.on_seek)
        self.mini_full_ui_btn.Bind(wx.EVT_BUTTON, self.on_toggle_mini_player)
        
        self.settings_mini_play_btn.Bind(wx.EVT_BUTTON, self.on_play)
        self.settings_mini_pause_btn.Bind(wx.EVT_BUTTON, self.on_pause)
        self.settings_mini_next_btn.Bind(wx.EVT_BUTTON, self.on_next)
        self.settings_mini_prev_btn.Bind(wx.EVT_BUTTON, self.on_prev)
        self.settings_mini_forward_btn.Bind(wx.EVT_BUTTON, self.on_forward)
        self.settings_mini_progress.Bind(wx.EVT_SLIDER, self.on_seek)
        
        # Theme
        self.apply_theme()
        
        self.Centre()
        
        if file_to_play and os.path.exists(file_to_play):
            self.add_to_playlist(file_to_play)
            self.current_song = 0
            self.load_song()
            self.on_play(None)
        
    def on_page_changed(self, event):
        # Ayarlar sekmesine geçince mini oynatıcıyı güncelle
        if self.notebook.GetSelection() == 1:  # Ayarlar sekmesi
            self.update_mini_player()
        event.Skip()
        
    def on_toggle_mini_player(self, event):
        self.mini_player_visible = not self.mini_player_visible
        self.control_sizer.ShowItems(self.mini_player_visible)
        self.playlist.Show(self.mini_player_visible)
        self.queue_list.Show(self.mini_player_visible)
        self.visual_panel.Show(self.mini_player_visible and self.visualization_on)
        self.song_info.Show(self.mini_player_visible)
        self.progress.Show(self.mini_player_visible)
        self.mini_player.Show(not self.mini_player_visible)
        self.main_panel.Layout()
        
    def update_mini_player(self):
        if self.current_song is not None:
            path, name, artist, _ = self.playlist_data[self.current_song]
            label = f"Şu an çalan: {name} - {artist}"
            self.mini_song_info.SetLabel(label)
            self.settings_mini_song_info.SetLabel(label)
        else:
            self.mini_song_info.SetLabel("Şu an çalan: Yok")
            self.settings_mini_song_info.SetLabel("Şu an çalan: Yok")
        
    def on_add_folder(self, event):
        with wx.DirDialog(self, "Klasör seç", style=wx.DD_DEFAULT_STYLE) as dirDialog:
            if dirDialog.ShowModal() == wx.ID_OK:
                folder_path = dirDialog.GetPath()
                mp3_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp3')]
                if not mp3_files:
                    wx.MessageBox("Klasörde MP3 dosyası bulunamadı.", "Bilgi", wx.OK | wx.ICON_INFORMATION)
                    return
                for f in mp3_files:
                    path = os.path.join(folder_path, f)
                    self.add_to_playlist(path)
        
    def on_save_list_to_desktop(self, event):
        if not self.playlist_data:
            wx.MessageBox("Çalma listesi boş.", "Hata", wx.OK | wx.ICON_ERROR)
            return
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        json_path = os.path.join(desktop, "music_list.json")
        data = []
        for p, n, a, d in self.playlist_data:
            try:
                created_time = time.ctime(os.path.getctime(p))
                modified_time = time.ctime(os.path.getmtime(p))
                size_bytes = os.path.getsize(p)
                year = "Bilinmiyor"
                data.append({"path": p, "name": n, "artist": a, "duration": d, "created_time": created_time, "modified_time": modified_time, "size_bytes": size_bytes, "year": year})
            except Exception as e:
                data.append({"path": p, "name": n, "artist": a, "duration": d, "error": str(e)})
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        wx.MessageBox("Müzik listeniz ve meta verileriniz masaüstüne kaydedildi.", "Bilgi", wx.OK | wx.ICON_INFORMATION)
        
    def on_category_select(self, event):
        selected = self.categories_tree.GetItemText(event.GetItem())
        if selected in self.artist_groups:
            self.playlist.DeleteAllItems()
            for idx in self.artist_groups[selected]:
                path, name, artist, duration = self.playlist_data[idx]
                index = self.playlist.InsertItem(self.playlist.GetItemCount(), name)
                self.playlist.SetItem(index, 1, artist)
                self.playlist.SetItem(index, 2, duration)
        
    def on_playlist_context_menu(self, event):
        menu = wx.Menu()
        queue_item = menu.Append(-1, "Kuyruğa Ekle")
        sort_item = menu.Append(-1, "Sırala")
        self.Bind(wx.EVT_MENU, self.on_add_to_queue, queue_item)
        self.Bind(wx.EVT_MENU, self.on_sort_menu, sort_item)
        self.playlist.PopupMenu(menu)
        menu.Destroy()
        
    def on_queue_context_menu(self, event):
        menu = wx.Menu()
        sort_item = menu.Append(-1, "Sırala")
        self.Bind(wx.EVT_MENU, self.on_sort_menu_queue, sort_item)
        self.queue_list.PopupMenu(menu)
        menu.Destroy()
        
    def on_sort_menu(self, event):
        menu = wx.Menu()
        name_item = menu.Append(-1, "Ad'a Göre")
        artist_item = menu.Append(-1, "Sanatçı'ya Göre")
        duration_item = menu.Append(-1, "Süre'ye Göre")
        self.Bind(wx.EVT_MENU, lambda e: self.sort_playlist('name'), name_item)
        self.Bind(wx.EVT_MENU, lambda e: self.sort_playlist('artist'), artist_item)
        self.Bind(wx.EVT_MENU, lambda e: self.sort_playlist('duration'), duration_item)
        self.playlist.PopupMenu(menu)
        menu.Destroy()
        
    def on_sort_menu_queue(self, event):
        menu = wx.Menu()
        name_item = menu.Append(-1, "Ad'a Göre")
        artist_item = menu.Append(-1, "Sanatçı'ya Göre")
        self.Bind(wx.EVT_MENU, lambda e: self.sort_queue('name'), name_item)
        self.Bind(wx.EVT_MENU, lambda e: self.sort_queue('artist'), artist_item)
        self.queue_list.PopupMenu(menu)
        menu.Destroy()
        
    def sort_playlist(self, key):
        if key == 'name':
            self.playlist_data.sort(key=lambda x: x[1])
        elif key == 'artist':
            self.playlist_data.sort(key=lambda x: x[2])
        elif key == 'duration':
            self.playlist_data.sort(key=lambda x: x[3])
        self.refresh_playlist()
        
    def sort_queue(self, key):
        if key == 'name':
            self.queue_data.sort(key=lambda idx: self.playlist_data[idx][1])
        elif key == 'artist':
            self.queue_data.sort(key=lambda idx: self.playlist_data[idx][2])
        self.refresh_queue()
        
    def refresh_playlist(self):
        self.playlist.DeleteAllItems()
        for i, (path, name, artist, duration) in enumerate(self.playlist_data):
            index = self.playlist.InsertItem(i, name)
            self.playlist.SetItem(index, 1, artist)
            self.playlist.SetItem(index, 2, duration)
        
    def refresh_queue(self):
        self.queue_list.DeleteAllItems()
        for i, idx in enumerate(self.queue_data):
            name = self.playlist_data[idx][1]
            artist = self.playlist_data[idx][2]
            q_index = self.queue_list.InsertItem(i, name)
            self.queue_list.SetItem(q_index, 1, artist)
        
    def add_to_playlist(self, path):
        if self.prevent_duplicates and path in [p[0] for p in self.playlist_data]:
            wx.MessageBox(f"'{os.path.basename(path)}' zaten çalma listesinde.", "Yinelenen Şarkı", wx.OK | wx.ICON_WARNING)
            return
        name = os.path.basename(path).replace('.mp3', '')
        artist = "Bilinmiyor"
        duration = "00:00"
        self.playlist_data.append((path, name, artist, duration))
        index = self.playlist.InsertItem(self.playlist.GetItemCount(), name)
        self.playlist.SetItem(index, 1, artist)
        self.playlist.SetItem(index, 2, duration)
        if artist not in self.artist_groups:
            self.artist_groups[artist] = []
            self.categories_tree.AppendItem(self.artist_node, artist)
        self.artist_groups[artist].append(len(self.playlist_data) - 1)
        self.update_mini_player()
        
    def on_add_to_queue(self, event):
        index = self.playlist.GetFirstSelected()
        if index != -1:
            self.queue_data.append(index)
            name = self.playlist_data[index][1]
            artist = self.playlist_data[index][2]
            q_index = self.queue_list.InsertItem(self.queue_list.GetItemCount(), name)
            self.queue_list.SetItem(q_index, 1, artist)
        
    def on_show_equalizer(self, event):
        dlg = EqualizerDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.eq_settings = dlg.eq_settings.copy()
            print("Ekolayzır ayarları kaydedildi:", self.eq_settings)
        dlg.Destroy()
        
    def on_add_file(self, event):
        with wx.FileDialog(self, "Müzik dosyası seç", wildcard="MP3 files (*.mp3)|*.mp3",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_OK:
                paths = fileDialog.GetPaths()
                for path in paths:
                    if path.lower().endswith('.mp3'):
                        self.add_to_playlist(path)
                    else:
                        wx.MessageBox("Bu şarkı oynatılamıyor çünkü müzik çalar bunu desteklemiyor.", "Hata", wx.OK | wx.ICON_ERROR)
        
    def on_select_song(self, event):
        self.current_song = event.GetIndex()
        self.load_song()
        
    def load_song(self):
        if self.current_song is not None:
            path, name, artist, _ = self.playlist_data[self.current_song]
            if self.media_ctrl.Load(path):
                self.song_info.SetLabel(f"Şu an çalan: {name} - {artist}")
                self.update_mini_player()
            else:
                wx.MessageBox("Şarkı yüklenemedi.", "Hata", wx.OK | wx.ICON_ERROR)
        
    def on_play(self, event):
        if not self.is_playing:
            self.media_ctrl.Play()
            self.is_playing = True
            self.progress_timer.Start(1000)
            self.mini_progress.Enable()
            self.settings_mini_progress.Enable()
            if self.visualization_on:
                self.visual_timer.Start(50)
            if self.current_song is not None and self.prevent_repeats:
                self.played_songs.append(self.current_song)
        self.media_ctrl.SetPlaybackRate(self.playback_speed)
        
    def on_pause(self, event):
        if self.is_playing:
            self.media_ctrl.Pause()
            self.is_playing = False
            self.progress_timer.Stop()
            self.visual_timer.Stop()
        
    def on_stop(self, event):
        self.media_ctrl.Stop()
        self.is_playing = False
        self.progress_timer.Stop()
        self.visual_timer.Stop()
        self.progress.SetValue(0)
        self.mini_progress.SetValue(0)
        self.settings_mini_progress.SetValue(0)
        
    def on_next(self, event):
        if self.queue_data:
            self.current_song = self.queue_data.pop(0)
            self.queue_list.DeleteItem(0)
            self.load_song()
            if self.is_playing:
                self.on_play(None)
        elif self.playlist_data:
            if self.crossfade_enabled:
                self.fade_out_and_next()
            else:
                if self.shuffle_mode:
                    available = [i for i in range(len(self.playlist_data)) if not self.prevent_repeats or i not in self.played_songs]
                    if not available:
                        self.played_songs.clear()
                        available = list(range(len(self.playlist_data)))
                    self.current_song = random.choice(available)
                else:
                    self.current_song = (self.current_song + 1) % len(self.playlist_data)
                self.load_song()
                if self.is_playing:
                    self.on_play(None)
        
    def fade_out_and_next(self):
        fade_steps = 10
        fade_interval = (self.crossfade_duration * 100) // fade_steps
        current_vol = self.media_ctrl.GetVolume()
        vol_step = current_vol / fade_steps
        for _ in range(fade_steps):
            current_vol -= vol_step
            self.media_ctrl.SetVolume(max(0, current_vol))
            wx.MilliSleep(fade_interval)
        self.media_ctrl.Stop()
        available = [i for i in range(len(self.playlist_data)) if not self.prevent_repeats or i not in self.played_songs]
        if not available:
            self.played_songs.clear()
            available = list(range(len(self.playlist_data)))
        self.current_song = random.choice(available) if self.shuffle_mode else (self.current_song + 1) % len(self.playlist_data)
        self.load_song()
        self.media_ctrl.SetVolume(0)
        self.on_play(None)
        current_vol = 0
        for _ in range(fade_steps):
            current_vol += vol_step
            self.media_ctrl.SetVolume(min(1, current_vol))
            wx.MilliSleep(fade_interval)
        
    def on_prev(self, event):
        if self.playlist_data:
            if self.shuffle_mode:
                available = [i for i in range(len(self.playlist_data)) if not self.prevent_repeats or i not in self.played_songs]
                if not available:
                    self.played_songs.clear()
                    available = list(range(len(self.playlist_data)))
                self.current_song = random.choice(available)
            else:
                self.current_song = (self.current_song - 1) % len(self.playlist_data)
            self.load_song()
            if self.is_playing:
                self.on_play(None)
        
    def on_forward(self, event):
        pos = self.media_ctrl.Tell()
        self.media_ctrl.Seek(pos + 10000)
        
    def on_shuffle(self, event):
        menu = wx.Menu()
        random_item = menu.Append(-1, "Rastgele Çal")
        sequential_item = menu.Append(-1, "Sıralı Çal")
        self.Bind(wx.EVT_MENU, lambda e: self.set_shuffle(True), random_item)
        self.Bind(wx.EVT_MENU, lambda e: self.set_shuffle(False), sequential_item)
        self.shuffle_btn.PopupMenu(menu)
        menu.Destroy()
        
    def set_shuffle(self, mode):
        self.shuffle_mode = mode
        self.shuffle_btn.SetLabel("Karıştır (Rastgele)" if mode else "Karıştır (Sıralı)")
        
    def on_toggle_volume(self, event):
        if self.volume_fixed:
            return
        self.volume_visible = not self.volume_visible
        self.volume_slider.Show(self.volume_visible)
        self.main_panel.Layout()
        
    def on_toggle_volume_fixed(self, event):
        self.volume_fixed = self.volume_fixed_check.GetValue()
        self.volume_slider.Show(self.volume_fixed)
        self.volume_btn.Enable(not self.volume_fixed)
        self.main_panel.Layout()
        
    def on_show_playlist(self, event):
        dlg = wx.Dialog(self, title="Şarkı Listesi", size=(400, 300))
        list_ctrl = wx.ListCtrl(dlg, style=wx.LC_REPORT)
        list_ctrl.InsertColumn(0, "Şarkı Adı", width=200)
        list_ctrl.InsertColumn(1, "Sanatçı", width=150)
        for i, (_, name, artist, _) in enumerate(self.playlist_data):
            index = list_ctrl.InsertItem(i, name)
            list_ctrl.SetItem(index, 1, artist)
        list_ctrl.Bind(wx.EVT_CHAR, self.on_playlist_key)
        list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, lambda e: setattr(self, 'temp_selected', e.GetIndex()))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(list_ctrl, 1, wx.EXPAND)
        dlg.SetSizer(sizer)
        dlg.ShowModal()
        dlg.Destroy()
        
    def on_playlist_key(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN and hasattr(self, 'temp_selected'):
            self.current_song = self.temp_selected
            self.load_song()
            self.on_play(None)
        event.Skip()
        
    def on_seek(self, event):
        pos = self.progress.GetValue()
        self.mini_progress.SetValue(pos)
        self.settings_mini_progress.SetValue(pos)
        self.media_ctrl.Seek(pos * 1000)
        
    def update_progress(self, event):
        if self.media_ctrl.GetState() == wx.media.MEDIASTATE_PLAYING:
            length = self.media_ctrl.Length()
            pos = self.media_ctrl.Tell()
            self.progress.SetRange(0, length // 1000)
            self.progress.SetValue(pos // 1000)
            self.mini_progress.SetRange(0, length // 1000)
            self.mini_progress.SetValue(pos // 1000)
            self.settings_mini_progress.SetRange(0, length // 1000)
            self.settings_mini_progress.SetValue(pos // 1000)
            if self.skip_silence_enabled:
                pass
        
    def on_media_loaded(self, event):
        length = self.media_ctrl.Length() // 1000
        mins, secs = divmod(length, 60)
        duration = f"{mins:02d}:{secs:02d}"
        if self.current_song is not None:
            self.playlist.SetItem(self.current_song, 2, duration)
            self.playlist_data[self.current_song] = self.playlist_data[self.current_song][:3] + (duration,)
        
    def on_media_finished(self, event):
        self.on_next(None)
        
    def on_volume_change(self, event):
        vol = self.volume_slider.GetValue() / 100.0
        self.media_ctrl.SetVolume(vol)
        
    def on_speed_change(self, event):
        self.playback_speed = self.speed_slider.GetValue() / 10.0
        if self.is_playing:
            self.media_ctrl.SetPlaybackRate(self.playback_speed)
        
    def on_toggle_categories(self, event):
        self.show_categories = self.categories_check.GetValue()
        self.categories_tree.Show(self.show_categories)
        self.main_panel.Layout()
        
    def on_theme_change(self, event):
        self.theme = self.theme_choice.GetStringSelection()
        self.apply_theme()
        
    def apply_theme(self):
        if self.theme == "Aydınlık":
            bg_color = wx.WHITE
            fg_color = wx.BLACK
        else:
            bg_color = wx.BLACK
            fg_color = wx.WHITE
        
        panels = [self.main_panel, self.settings_panel, self.visual_panel, self.mini_player, self.settings_mini_player]
        for panel in panels:
            panel.SetBackgroundColour(bg_color)
            panel.SetForegroundColour(fg_color)
        
        controls = [self.song_info, self.playlist, self.queue_list, self.categories_tree, self.progress, self.volume_slider,
                    self.play_btn, self.pause_btn, self.stop_btn, self.next_btn, self.prev_btn, self.forward_btn,
                    self.shuffle_btn, self.volume_btn, self.playlist_btn, self.add_file_btn, self.add_folder_btn, self.eq_btn, self.save_list_btn,
                    self.mini_song_info, self.mini_play_btn, self.mini_pause_btn, self.mini_next_btn, self.mini_prev_btn, self.mini_forward_btn, self.mini_progress, self.mini_full_ui_btn,
                    self.settings_mini_song_info, self.settings_mini_play_btn, self.settings_mini_pause_btn, self.settings_mini_next_btn, self.settings_mini_prev_btn, self.settings_mini_forward_btn, self.settings_mini_progress]
        for ctrl in controls:
            ctrl.SetBackgroundColour(bg_color)
            ctrl.SetForegroundColour(fg_color)
        
        self.Refresh()
        
    def on_toggle_visual(self, event):
        self.visualization_on = self.visual_check.GetValue()
        self.visual_panel.Show(self.visualization_on)
        if self.is_playing and self.visualization_on:
            self.visual_timer.Start(50)
        else:
            self.visual_timer.Stop()
        self.main_panel.Layout()
        
    def on_visual_type_change(self, event):
        self.visual_type = self.visual_type_choice.GetStringSelection()
        
    def on_paint_visual(self, event):
        dc = wx.PaintDC(self.visual_panel)
        width, height = self.visual_panel.GetSize()
        dc.Clear()
        
        if self.visual_type == "Hipnotik Daireler":
            for i in range(20):
                color = wx.Colour(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                dc.SetPen(wx.Pen(color, 2))
                dc.SetBrush(wx.Brush(color, wx.BRUSHSTYLE_TRANSPARENT))
                radius = random.randint(10, min(width, height) // 2)
                x, y = width // 2 + random.randint(-50, 50), height // 2 + random.randint(-50, 50)
                dc.DrawCircle(x, y, radius)
                
        elif self.visual_type == "Rastgele Çizgiler":
            for _ in range(30):
                color = wx.Colour(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                dc.SetPen(wx.Pen(color, random.randint(1, 5)))
                x1, y1 = random.randint(0, width), random.randint(0, height)
                x2, y2 = random.randint(0, width), random.randint(0, height)
                dc.DrawLine(x1, y1, x2, y2)
                
        elif self.visual_type == "Dalga Efekti":
            dc.SetPen(wx.Pen(wx.BLUE, 3))
            for i in range(0, width, 10):
                y = height // 2 + int(50 * random.random() * (1 if random.random() > 0.5 else -1))
                dc.DrawLine(i, height // 2, i + 10, y)
                
        elif self.visual_type == "Parlayan Kareler":
            for _ in range(15):
                color = wx.Colour(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                dc.SetBrush(wx.Brush(color))
                size = random.randint(10, 50)
                x, y = random.randint(0, width - size), random.randint(0, height - size)
                dc.DrawRectangle(x, y, size, size)
                
        elif self.visual_type == "Yıldızlar":
            for _ in range(50):
                color = wx.Colour(255, 255, random.randint(200, 255))
                dc.SetPen(wx.Pen(color))
                dc.SetBrush(wx.Brush(color))
                x, y = random.randint(0, width), random.randint(0, height)
                dc.DrawCircle(x, y, 2)
                if random.random() > 0.8:
                    dc.DrawLine(x-5, y, x+5, y)
                    dc.DrawLine(x, y-5, x, y+5)
                
        elif self.visual_type == "Spiral":
            center_x, center_y = width // 2, height // 2
            angle = 0
            radius = 0
            color = wx.Colour(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            dc.SetPen(wx.Pen(color, 2))
            for _ in range(100):
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                dc.DrawPoint(int(x), int(y))
                angle += 0.1
                radius += 0.5
                
        elif self.visual_type == "Uçuşan Notalar":
            notes = ['♩', '♪', '♫', '♬', '♭', '♮', '♯']
            for _ in range(20):
                color = wx.Colour(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                dc.SetTextForeground(color)
                dc.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                note = random.choice(notes)
                x, y = random.randint(0, width), random.randint(0, height)
                dc.DrawText(note, x, y)
                
        elif self.visual_type == "Fireworks":
            for _ in range(20):
                color = wx.Colour(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                dc.SetPen(wx.Pen(color))
                dc.SetBrush(wx.Brush(color))
                x, y = random.randint(0, width), random.randint(0, height)
                dc.DrawCircle(x, y, random.randint(5, 15))
                for i in range(5):
                    angle = random.uniform(0, 2 * math.pi)
                    end_x = x + random.randint(20, 50) * math.cos(angle)
                    end_y = y + random.randint(20, 50) * math.sin(angle)
                    dc.DrawLine(x, y, int(end_x), int(end_y))
        
        elif self.visual_type == "Waveform":
            dc.SetPen(wx.Pen(wx.GREEN, 3))
            for i in range(0, width, 5):
                y1 = height // 2 + random.randint(-50, 50)
                y2 = height // 2 + random.randint(-50, 50)
                dc.DrawLine(i, y1, i + 5, y2)
        
    def update_visual(self, event):
        self.visual_panel.Refresh()
        
    def on_toggle_crossfade(self, event):
        self.crossfade_enabled = self.crossfade_check.GetValue()
        self.crossfade_slider.Enable(self.crossfade_enabled)
        
    def on_crossfade_change(self, event):
        self.crossfade_duration = self.crossfade_slider.GetValue()
        
    def on_toggle_skip_silence(self, event):
        self.skip_silence_enabled = self.skip_silence_check.GetValue()
        self.silence_threshold_slider.Enable(self.skip_silence_enabled)
        self.silence_duration_slider.Enable(self.skip_silence_enabled)
        
    def on_silence_threshold_change(self, event):
        self.silence_threshold = self.silence_threshold_slider.GetValue()
        
    def on_silence_duration_change(self, event):
        self.silence_min_duration = self.silence_duration_slider.GetValue()
        
    def on_toggle_prevent_duplicates(self, event):
        self.prevent_duplicates = self.prevent_duplicates_check.GetValue()
        
    def on_toggle_prevent_repeats(self, event):
        self.prevent_repeats = self.prevent_repeats_check.GetValue()
        if not self.prevent_repeats:
            self.played_songs.clear()
            
    def on_import_playlist(self, event):
        with wx.FileDialog(self, "Çalma listesi seç", wildcard="M3U files (*.m3u)|*.m3u",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_OK:
                path = fileDialog.GetPath()
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and os.path.exists(line) and line.lower().endswith('.mp3'):
                                self.add_to_playlist(line)
                except Exception as e:
                    wx.MessageBox(f"Çalma listesi yüklenemedi: {e}", "Hata", wx.OK | wx.ICON_ERROR)
                
    def on_export_playlist(self, event):
        with wx.FileDialog(self, "Çalma listesini kaydet", wildcard="M3U files (*.m3u)|*.m3u",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_OK:
                path = fileDialog.GetPath()
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write("#EXTM3U\n")
                        for song_path, name, artist, _ in self.playlist_data:
                            f.write(f"#EXTINF:-1,{name} - {artist}\n{song_path}\n")
                    wx.MessageBox("Çalma listesi dışa aktarıldı.", "Başarılı", wx.OK | wx.ICON_INFORMATION)
                except Exception as e:
                    wx.MessageBox(f"Dışa aktarma başarısız: {e}", "Hata", wx.OK | wx.ICON_ERROR)

if __name__ == "__main__":
    app = wx.App()
    file_to_play = sys.argv[1] if len(sys.argv) > 1 else None
    frame = MusicPlayer("Müzik Çalar", file_to_play)
    frame.Show()
    app.MainLoop()