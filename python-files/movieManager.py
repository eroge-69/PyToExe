import wx
import ffmpeg
import json
import os
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from mutagen.mp3 import MP3
import subprocess
import tempfile
from datetime import datetime

class FilmYoneticiApp(wx.App):
    def OnInit(self):
        self.frame = MainFrame()
        self.frame.Show()
        return True

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Film Yöneticisi", size=(600, 400))
        self.panel = wx.Panel(self)
        self.panel.SetAccessibleName("Ana Panel")
        self.projects = []
        self.project_file = "projects.json"
        self.load_projects()
        
        # Arayüz
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.new_project_button = wx.Button(self.panel, label="Yeni Proje")
        self.new_project_button.SetAccessibleName("Yeni Proje Oluştur")
        self.sizer.Add(self.new_project_button, flag=wx.ALL, border=10)
        
        self.project_list = wx.ListCtrl(self.panel, style=wx.LC_REPORT)
        self.project_list.SetAccessibleName("Proje Listesi")
        self.project_list.InsertColumn(0, "Proje Adı", width=200)
        self.project_list.InsertColumn(1, "Süre (sn)", width=100)
        self.project_list.InsertColumn(2, "Düzenle", width=100)
        self.project_list.InsertColumn(3, "Sil", width=100)
        self.project_list.InsertColumn(4, "Dışa Aktar", width=100)
        self.sizer.Add(self.project_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        
        self.panel.SetSizer(self.sizer)
        
        # Olay bağlamaları
        self.new_project_button.Bind(wx.EVT_BUTTON, self.on_new_project)
        self.project_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_project_action)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        self.update_project_list()
    
    def load_projects(self):
        if os.path.exists(self.project_file):
            with open(self.project_file, "r") as f:
                self.projects = json.load(f)
    
    def save_projects(self):
        with open(self.project_file, "w") as f:
            json.dump(self.projects, f, indent=4)
    
    def update_project_list(self):
        self.project_list.DeleteAllItems()
        for i, project in enumerate(self.projects):
            duration = sum(audio["duration"] for audio in project["audio_files"])
            self.project_list.InsertItem(i, project["name"])
            self.project_list.SetItem(i, 1, f"{duration:.2f}")
            self.project_list.SetItem(i, 2, "Düzenle")
            self.project_list.SetItem(i, 3, "Sil")
            self.project_list.SetItem(i, 4, "Dışa Aktar")
    
    def on_new_project(self, event):
        name = wx.GetTextFromUser("Proje adını girin (boş bırakırsanız tarih kullanılır):", "Yeni Proje")
        if not name:
            name = datetime.now().strftime("%Y-%m-%d")
        self.projects.append({"name": name, "audio_files": [], "current_time": 0.0, "tracks": [[]]})
        self.save_projects()
        self.update_project_list()
        self.open_editor(len(self.projects) - 1)
    
    def on_project_action(self, event):
        item = event.Index
        col = self.project_list.GetFocusedItem()
        if col == 2:
            self.open_editor(item)
        elif col == 3:
            dialog = wx.MessageDialog(self, f"'{self.projects[item]['name']}' projesini silmek istediğinizden emin misiniz?",
                                     "Onay", wx.YES_NO | wx.ICON_QUESTION)
            dialog.SetAccessibleName("Proje Silme Onayı")
            if dialog.ShowModal() == wx.ID_YES:
                self.projects.pop(item)
                self.save_projects()
                self.update_project_list()
        elif col == 4:
            self.export_project(item)
    
    def open_editor(self, project_idx):
        editor = EditorFrame(self, project_idx, self.projects[project_idx])
        editor.Show()
    
    def export_project(self, project_idx):
        project = self.projects[project_idx]
        dialog = QualitySettingsDialog(self)
        if dialog.ShowModal() == wx.ID_OK:
            bitrate = dialog.bitrate_choice.GetStringSelection()
            sample_rate = dialog.sample_rate_choice.GetStringSelection()
            output_path = os.path.join(os.path.expanduser("~/Desktop"), f"{project['name']}.mp3")
            self.merge_audio_files(project["audio_files"], output_path, bitrate, sample_rate)
        dialog.Destroy()
    
    def merge_audio_files(self, audio_files, output_path, bitrate, sample_rate):
        try:
            streams = []
            for audio in audio_files:
                stream = ffmpeg.input(audio["path"])
                stream = stream.filter("volume", audio["volume"])
                stream = stream.filter("atempo", audio["speed"])
                streams.append(stream)
            if streams:
                output = ffmpeg.concat(*streams, v=0, a=1).output(output_path, format="mp3", ab=bitrate, ar=sample_rate)
                ffmpeg.run(output)
                wx.MessageBox("Proje masaüstüne dışa aktarıldı!", "Başarılı", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"Hata: {str(e)}", "Hata", wx.OK | wx.ICON_ERROR)
    
    def on_close(self, event):
        self.save_projects()
        self.Destroy()

class EditorFrame(wx.Frame):
    def __init__(self, parent, project_idx, project):
        super().__init__(parent, title=f"Düzenle: {project['name']} - Film Yöneticisi", size=(800, 500))
        self.panel = wx.Panel(self)
        self.panel.SetAccessibleName("Düzenleme Paneli")
        self.project_idx = project_idx
        self.project = project
        self.current_time = project.get("current_time", 0.0)
        self.current_track = 0
        self.current_subtrack = 0
        self.playing = False
        self.demo_playing = False
        self.recording = False
        self.paused = False
        self.temp_file = None
        self.demo_temp_file = None
        self.recorded_audio = []
        
        # Sürükle-bırak desteği
        self.panel.SetDropTarget(FileDropTarget(self))
        
        # Arayüz
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Sağ üst köşede dışa aktar butonu
        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.export_button = wx.Button(self.panel, label="Dışa Aktar")
        self.export_button.SetAccessibleName("Filmi Dışa Aktar")
        self.top_sizer.AddStretchSpacer()
        self.top_sizer.Add(self.export_button, flag=wx.ALL, border=10)
        self.sizer.Add(self.top_sizer, flag=wx.EXPAND)
        
        # Ses kaydedici paneli
        self.recorder_panel = wx.Panel(self.panel)
        self.recorder_panel.SetAccessibleName("Ses Kaydedici")
        self.recorder_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.record_button = wx.Button(self.recorder_panel, label="Kaydet")
        self.record_button.SetAccessibleName("Ses Kaydını Başlat")
        self.pause_button = wx.Button(self.recorder_panel, label="Duraklat")
        self.pause_button.SetAccessibleName("Kaydı Duraklat")
        self.resume_button = wx.Button(self.recorder_panel, label="Devam Et")
        self.resume_button.SetAccessibleName("Kayda Devam Et")
        self.stop_record_button = wx.Button(self.recorder_panel, label="Durdur")
        self.stop_record_button.SetAccessibleName("Kaydı Durdur")
        self.close_recorder_button = wx.Button(self.recorder_panel, label="Kapat")
        self.close_recorder_button.SetAccessibleName("Ses Kaydediciyi Kapat")
        self.recorder_sizer.Add(self.record_button, flag=wx.ALL, border=5)
        self.recorder_sizer.Add(self.pause_button, flag=wx.ALL, border=5)
        self.recorder_sizer.Add(self.resume_button, flag=wx.ALL, border=5)
        self.recorder_sizer.Add(self.stop_record_button, flag=wx.ALL, border=5)
        self.recorder_sizer.Add(self.close_recorder_button, flag=wx.ALL, border=5)
        self.recorder_panel.SetSizer(self.recorder_sizer)
        self.recorder_panel.Hide()
        self.sizer.Add(self.recorder_panel, flag=wx.ALL, border=10)
        
        self.play_button = wx.Button(self.panel, label="Oynat", size=(100, 50))
        self.play_button.SetAccessibleName("Oynat veya Durdur")
        self.sizer.Add(self.play_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        
        self.stop_demo_button = wx.Button(self.panel, label="Kısa Demoyu Kapat", size=(150, 30))
        self.stop_demo_button.SetAccessibleName("Kısa Demoyu Kapat")
        self.stop_demo_button.Hide()
        self.sizer.Add(self.stop_demo_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        
        self.progress_bar = wx.Gauge(self.panel, range=100)
        self.progress_bar.SetAccessibleName("Dışa Aktarma İlerleme Çubuğu")
        self.progress_bar.Hide()
        self.sizer.Add(self.progress_bar, flag=wx.EXPAND | wx.ALL, border=10)
        
        self.progress_label = wx.StaticText(self.panel, label="")
        self.progress_label.SetAccessibleName("Dışa Aktarma Durumu")
        self.progress_label.Hide()
        self.sizer.Add(self.progress_label, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        
        self.timeline = wx.Slider(self.panel, value=int(self.current_time), minValue=0, maxValue=1000)
        self.timeline.SetAccessibleName("Zaman Çizelgesi")
        self.sizer.Add(self.timeline, flag=wx.EXPAND | wx.ALL, border=10)
        
        self.track_list = wx.ListBox(self.panel, style=wx.LB_SINGLE)
        self.track_list.SetAccessibleName("İzler Listesi")
        self.sizer.Add(self.track_list, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        
        self.add_button = wx.Button(self.panel, label="Ses Dosyası Ekle")
        self.add_button.SetAccessibleName("Ses Dosyası Ekle")
        self.sizer.Add(self.add_button, flag=wx.ALL, border=5)
        
        self.control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.remove_button = wx.Button(self.panel, label="Kaldır")
        self.remove_button.SetAccessibleName("Seçili Sesi Kaldır")
        self.options_button = wx.Button(self.panel, label="Diğer Seçenekler")
        self.options_button.SetAccessibleName("Ses Ayarları")
        self.control_sizer.Add(self.remove_button, flag=wx.ALL, border=5)
        self.control_sizer.Add(self.options_button, flag=wx.ALL, border=5)
        self.sizer.Add(self.control_sizer, flag=wx.ALIGN_CENTER)
        
        self.panel.SetSizer(self.sizer)
        
        # Olay bağlamaları
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add_audio)
        self.remove_button.Bind(wx.EVT_BUTTON, self.on_remove_audio)
        self.options_button.Bind(wx.EVT_BUTTON, self.on_options)
        self.track_list.Bind(wx.EVT_LISTBOX, self.on_select_track)
        self.play_button.Bind(wx.EVT_BUTTON, self.on_play)
        self.stop_demo_button.Bind(wx.EVT_BUTTON, self.on_stop_demo)
        self.export_button.Bind(wx.EVT_BUTTON, self.on_export)
        self.record_button.Bind(wx.EVT_BUTTON, self.on_record)
        self.pause_button.Bind(wx.EVT_BUTTON, self.on_pause)
        self.resume_button.Bind(wx.EVT_BUTTON, self.on_resume)
        self.stop_record_button.Bind(wx.EVT_BUTTON, self.on_stop_record)
        self.close_recorder_button.Bind(wx.EVT_BUTTON, self.on_close_recorder)
        self.timeline.Bind(wx.EVT_SLIDER, self.on_timeline_change)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
        self.update_track_list()
        self.remove_button.Enable(False)
        self.options_button.Enable(False)
    
    def update_track_list(self):
        self.track_list.Clear()
        for i, track in enumerate(self.project["tracks"]):
            track_name = f"İz {i + 1}: "
            if track:
                track_name += f"{os.path.basename(track[0]['path'])} ({track[0]['duration']:.2f} sn)"
            else:
                track_name += "Boş"
            self.track_list.Append(track_name)
        self.track_list.SetSelection(self.current_track)
        total_duration = sum(audio["duration"] / audio["speed"] for audio in self.project["audio_files"])
        self.timeline.SetMax(int(total_duration * 1000))
        self.timeline.SetValue(int(self.current_time * 1000))
    
    def get_audio_duration(self, path):
        try:
            if path.endswith(".mp3"):
                audio = MP3(path)
                return audio.info.length
            return 0.0
        except:
            return 0.0
    
    def on_add_audio(self, event):
        dialog = wx.Dialog(self, title="Ses Ekleme Seçenekleri")
        dialog.SetAccessibleName("Ses Ekleme Seçenekleri Penceresi")
        sizer = wx.BoxSizer(wx.VERTICAL)
        record_button = wx.Button(dialog, label="Ses Kaydet")
        record_button.SetAccessibleName("Ses Kaydet")
        add_button = wx.Button(dialog, label="Ses Ekle")
        add_button.SetAccessibleName("Ses Dosyası Ekle")
        sizer.Add(record_button, flag=wx.ALL, border=5)
        sizer.Add(add_button, flag=wx.ALL, border=5)
        dialog.SetSizer(sizer)
        sizer.Fit(dialog)
        
        def on_record(evt):
            dialog.EndModal(wx.ID_OK)
            self.start_recorder()
        
        def on_add(evt):
            dialog.EndModal(wx.ID_OK)
            self.add_existing_audio()
        
        record_button.Bind(wx.EVT_BUTTON, on_record)
        add_button.Bind(wx.EVT_BUTTON, on_add)
        
        dialog.ShowModal()
        dialog.Destroy()
    
    def add_existing_audio(self):
        with wx.FileDialog(self, "Ses dosyası seç (MP3)", wildcard="MP3 files (*.mp3)|*.mp3",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            fileDialog.SetAccessibleName("Ses Dosyası Seçme Penceresi")
            if fileDialog.ShowModal() == wx.ID_OK:
                path = fileDialog.GetPath()
                self.add_audio_to_track(path)
    
    def start_recorder(self):
        self.recorder_panel.Show()
        self.record_button.Enable(True)
        self.pause_button.Enable(False)
        self.resume_button.Enable(False)
        self.stop_record_button.Enable(False)
        self.close_recorder_button.Enable(True)
        self.panel.Layout()
    
    def on_record(self, event):
        self.recording = True
        self.recorded_audio = []
        self.record_button.Enable(False)
        self.pause_button.Enable(True)
        self.resume_button.Enable(False)
        self.stop_record_button.Enable(True)
        self.close_recorder_button.Enable(True)
        self.recorder_thread = sd.InputStream(samplerate=44100, channels=1, callback=self.record_callback)
        self.recorder_thread.start()
    
    def record_callback(self, indata, frames, time, status):
        if self.recording and not self.paused:
            self.recorded_audio.append(indata.copy())
    
    def on_pause(self, event):
        self.paused = True
        self.pause_button.Enable(False)
        self.resume_button.Enable(True)
    
    def on_resume(self, event):
        self.paused = False
        self.pause_button.Enable(True)
        self.resume_button.Enable(False)
    
    def on_stop_record(self, event):
        self.recording = False
        self.paused = False
        self.recorder_thread.stop()
        self.recorder_thread.close()
        self.recorder_panel.Hide()
        self.panel.Layout()
        
        if self.recorded_audio:
            temp_wav = tempfile.NamedTemporaryFile(suffix=".wav").name
            audio_data = np.concatenate(self.recorded_audio, axis=0)
            write(temp_wav, 44100, audio_data)
            output_path = os.path.join(os.path.expanduser("~/Desktop"),
                                      f"{self.project['name']}_kayıt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3")
            try:
                stream = ffmpeg.input(temp_wav)
                stream = stream.output(output_path, format="mp3")
                ffmpeg.run(stream)
                self.add_audio_to_track(output_path)
            except Exception as e:
                wx.MessageBox(f"Kayıt kaydetme hatası: {str(e)}", "Hata", wx.OK | wx.ICON_ERROR)
    
    def on_close_recorder(self, event):
        if self.recording:
            dialog = wx.MessageDialog(self, "Şu anda ses kaydediyorsunuz. Çıkarsanız kaydınız iptal edilecek. Devam etmek istiyor musunuz?",
                                     "Kayıt İptal Onayı", wx.YES_NO | wx.ICON_QUESTION)
            dialog.SetAccessibleName("Kayıt İptal Onayı Penceresi")
            if dialog.ShowModal() == wx.ID_YES:
                self.recording = False
                self.paused = False
                self.recorder_thread.stop()
                self.recorder_thread.close()
                self.recorded_audio = []  # Kayıt verilerini sıfırla
                self.recorder_panel.Hide()
                self.panel.Layout()
            else:
                self.paused = True
                self.pause_button.Enable(False)
                self.resume_button.Enable(True)
                self.panel.Layout()
        else:
            self.recorder_panel.Hide()
            self.panel.Layout()
    
    def add_audio_to_track(self, path):
        if not path.endswith(".mp3"):
            wx.MessageBox("Sadece MP3 dosyaları destekleniyor!", "Hata", wx.OK | wx.ICON_ERROR)
            return
        duration = self.get_audio_duration(path)
        while len(self.project["tracks"]) <= self.current_track:
            self.project["tracks"].append([])
        if not self.project["tracks"][self.current_track]:
            self.project["tracks"][self.current_track].append({"path": path, "volume": 1.0, "speed": 1.0, "duration": duration})
            self.project["audio_files"].append({"path": path, "volume": 1.0, "speed": 1.0, "duration": duration})
        self.update_track_list()
        self.save_project()
    
    def on_remove_audio(self, event):
        if self.current_track < len(self.project["tracks"]) and self.project["tracks"][self.current_track]:
            dialog = wx.MessageDialog(self, "Bu ses dosyasını kaldırmak istediğinizden emin misiniz?",
                                     "Onay", wx.YES_NO | wx.ICON_QUESTION)
            dialog.SetAccessibleName("Ses Kaldırma Onayı")
            if dialog.ShowModal() == wx.ID_YES:
                self.project["tracks"][self.current_track].pop(self.current_subtrack)
                self.project["audio_files"].pop(self.current_track)
                if not self.project["tracks"][self.current_track]:
                    self.project["tracks"].pop(self.current_track)
                    if self.current_track >= len(self.project["tracks"]):
                        self.current_track = max(0, len(self.project["tracks"]) - 1)
                self.update_track_list()
                self.save_project()
                self.remove_button.Enable(False)
                self.options_button.Enable(False)
    
    def on_options(self, event):
        if self.current_track < len(self.project["tracks"]) and self.project["tracks"][self.current_track]:
            audio = self.project["tracks"][self.current_track][self.current_subtrack]
            dialog = OptionsDialog(self, audio)
            if dialog.ShowModal() == wx.ID_OK:
                audio["volume"] = dialog.volume_slider.GetValue() / 100.0
                audio["speed"] = dialog.speed_slider.GetValue() / 100.0
                self.update_track_list()
                self.save_project()
                self.play_demo(audio)
            dialog.Destroy()
    
    def play_demo(self, audio):
        self.stop_demo_button.Show()
        self.demo_playing = True
        self.demo_temp_file = tempfile.NamedTemporaryFile(suffix=".mp3").name
        try:
            stream = ffmpeg.input(audio["path"]).filter("volume", audio["volume"]).filter("atempo", audio["speed"])
            stream = stream.output(self.demo_temp_file, t=5)
            ffmpeg.run(stream)
            subprocess.Popen(["ffmpeg", "-i", self.demo_temp_file, "-f", "mp3", "pipe:"])
            self.panel.Layout()
        except Exception as e:
            wx.MessageBox(f"Demo oynatma hatası: {str(e)}", "Hata", wx.OK | wx.ICON_ERROR)
            self.stop_demo_button.Hide()
            self.demo_playing = False
    
    def on_stop_demo(self, event):
        if self.demo_playing:
            subprocess.run(["pkill", "-f", "ffmpeg"])
            self.stop_demo_button.Hide()
            self.demo_playing = False
            self.panel.Layout()
    
    def on_play(self, event):
        if not self.playing:
            self.play_button.SetLabel("Durdur")
            self.play_button.SetAccessibleName("Durdur")
            self.playing = True
            self.temp_file = tempfile.NamedTemporaryFile(suffix=".mp3").name
            self.merge_audio_files(self.project["audio_files"], self.temp_file, "64k", "22050")
            subprocess.Popen(["ffmpeg", "-i", self.temp_file, "-ss", str(self.current_time), "-f", "mp3", "pipe:"])
        else:
            self.play_button.SetLabel("Oynat")
            self.play_button.SetAccessibleName("Oynat")
            self.playing = False
            subprocess.run(["pkill", "-f", "ffmpeg"])
    
    def on_export(self, event):
        dialog = QualitySettingsDialog(self)
        if dialog.ShowModal() == wx.ID_OK:
            bitrate = dialog.bitrate_choice.GetStringSelection()
            sample_rate = dialog.sample_rate_choice.GetStringSelection()
            self.progress_bar.Show()
            self.progress_label.SetLabel("Filminiz dışa aktarılıyor...")
            self.progress_label.Show()
            self.panel.Layout()
            self.progress_bar.Pulse()
            
            output_path = os.path.join(os.path.expanduser("~/Desktop"), f"{self.project['name']}.mp3")
            self.merge_audio_files(self.project["audio_files"], output_path, bitrate, sample_rate)
            
            self.progress_bar.Hide()
            self.progress_label.Hide()
            self.panel.Layout()
        dialog.Destroy()
    
    def merge_audio_files(self, audio_files, output_path, bitrate, sample_rate):
        try:
            streams = []
            for audio in audio_files:
                stream = ffmpeg.input(audio["path"])
                stream = stream.filter("volume", audio["volume"])
                stream = stream.filter("atempo", audio["speed"])
                streams.append(stream)
            if streams:
                output = ffmpeg.concat(*streams, v=0, a=1).output(output_path, format="mp3", ab=bitrate, ar=sample_rate)
                ffmpeg.run(output)
                wx.MessageBox("Proje masaüstüne dışa aktarıldı!", "Başarılı", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"Hata: {str(e)}", "Hata", wx.OK | wx.ICON_ERROR)
    
    def on_timeline_change(self, event):
        self.current_time = self.timeline.GetValue() / 1000.0
        self.save_project()
    
    def on_select_track(self, event):
        self.current_track = self.track_list.GetSelection()
        self.current_subtrack = 0
        self.remove_button.Enable(self.current_track < len(self.project["tracks"]) and self.project["tracks"][self.current_track])
        self.options_button.Enable(self.current_track < len(self.project["tracks"]) and self.project["tracks"][self.current_track])
    
    def on_key_press(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_UP:
            self.current_track = max(0, self.current_track - 1)
            self.current_subtrack = 0
            self.track_list.SetSelection(self.current_track)
            self.update_track_list()
        elif keycode == wx.WXK_DOWN:
            self.current_track = min(len(self.project["tracks"]), self.current_track + 1)
            self.current_subtrack = 0
            self.track_list.SetSelection(self.current_track)
            self.update_track_list()
        elif keycode == wx.WXK_LEFT and event.ControlDown():
            if self.current_track < len(self.project["tracks"]) and self.project["tracks"][self.current_track]:
                self.current_subtrack = max(0, self.current_subtrack - 1)
        elif keycode == wx.WXK_RIGHT and event.ControlDown():
            if self.current_track < len(self.project["tracks"]) and self.project["tracks"][self.current_track]:
                self.current_subtrack = min(len(self.project["tracks"][self.current_track]) - 1, self.current_subtrack + 1)
        elif keycode == wx.WXK_UP and event.AltDown():
            self.current_track = max(0, self.current_track - 1)
            self.current_subtrack = 0
            self.track_list.SetSelection(self.current_track)
            self.update_track_list()
        elif keycode == wx.WXK_DOWN and event.AltDown():
            self.current_track = min(len(self.project["tracks"]), self.current_track + 1)
            self.current_subtrack = 0
            self.track_list.SetSelection(self.current_track)
            self.update_track_list()
        elif keycode == wx.WXK_LEFT:
            self.current_time = max(0, self.current_time - 1.0)
            self.timeline.SetValue(int(self.current_time * 1000))
        elif keycode == wx.WXK_RIGHT:
            total_duration = sum(audio["duration"] / audio["speed"] for audio in self.project["audio_files"])
            self.current_time = min(total_duration, self.current_time + 1.0)
            self.timeline.SetValue(int(self.current_time * 1000))
        elif keycode == wx.WXK_RETURN:
            self.on_add_audio(None)
        self.save_project()
        event.Skip()
    
    def save_project(self):
        self.project["current_time"] = self.current_time
        self.GetParent().save_projects()
    
    def on_close(self, event):
        if self.playing or self.demo_playing or self.recording:
            subprocess.run(["pkill", "-f", "ffmpeg"])
            if self.recording:
                self.recorder_thread.stop()
                self.recorder_thread.close()
        self.save_project()
        self.Destroy()

class QualitySettingsDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="MP3 Kalite Ayarları")
        self.SetAccessibleName("MP3 Kalite Ayarları Penceresi")
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sizer.Add(wx.StaticText(self, label="Bitrate (kbps):"), flag=wx.ALL, border=5)
        self.bitrate_choice = wx.Choice(self, choices=["64k", "128k", "192k", "256k", "320k"])
        self.bitrate_choice.SetAccessibleName("Bitrate Seçimi")
        self.bitrate_choice.SetSelection(0)  # Varsayılan: 64 kbps
        sizer.Add(self.bitrate_choice, flag=wx.EXPAND | wx.ALL, border=5)
        
        sizer.Add(wx.StaticText(self, label="Sample Rate (Hz):"), flag=wx.ALL, border=5)
        self.sample_rate_choice = wx.Choice(self, choices=["22050", "44100", "48000"])
        self.sample_rate_choice.SetAccessibleName("Sample Rate Seçimi")
        self.sample_rate_choice.SetSelection(0)  # Varsayılan: 22050 Hz
        sizer.Add(self.sample_rate_choice, flag=wx.EXPAND | wx.ALL, border=5)
        
        btn_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        
        self.SetSizer(sizer)
        sizer.Fit(self)

class OptionsDialog(wx.Dialog):
    def __init__(self, parent, audio):
        super().__init__(parent, title="Ses Ayarları")
        self.SetAccessibleName("Ses Ayarları Penceresi")
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sizer.Add(wx.StaticText(self, label="Ses Seviyesi (%):"), flag=wx.ALL, border=5)
        self.volume_slider = wx.Slider(self, value=int(audio["volume"] * 100), minValue=0, maxValue=100)
        self.volume_slider.SetAccessibleName("Ses Seviyesi Ayarı")
        sizer.Add(self.volume_slider, flag=wx.EXPAND | wx.ALL, border=5)
        
        sizer.Add(wx.StaticText(self, label="Ses Hızı (%):"), flag=wx.ALL, border=5)
        self.speed_slider = wx.Slider(self, value=int(audio["speed"] * 100), minValue=50, maxValue=200)
        self.speed_slider.SetAccessibleName("Ses Hızı Ayarı")
        sizer.Add(self.speed_slider, flag=wx.EXPAND | wx.ALL, border=5)
        
        btn_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        
        self.SetSizer(sizer)
        sizer.Fit(self)

class FileDropTarget(wx.FileDropTarget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
    
    def OnDropFiles(self, x, y, filenames):
        for path in filenames:
            if path.endswith(".mp3"):
                self.editor.add_audio_to_track(path)
        return True

if __name__ == "__main__":
    app = FilmYoneticiApp()
    app.MainLoop()