import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import json
import os
import sys
import ctypes
import winreg
import threading
import requests
from pathlib import Path

class WindowsSetupTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows Kurulum Sonrası Ayarlar ve Uygulama Yükleyici")
        self.root.geometry("900x700")
        
        # Yönetici kontrolü
        if not self.is_admin():
            self.restart_as_admin()
        
        # Uygulama listesi
        self.apps = []
        self.load_apps_list()
        
        # Ayarlar
        self.settings = {}
        self.load_settings()
        
        # Arayüz oluştur
        self.create_widgets()
        
        # Winget kontrolü
        if not self.is_winget_installed():
            self.install_winget()
        
    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def restart_as_admin(self):
        # Kendini yönetici olarak yeniden başlat
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit()
        
    def load_apps_list(self):
        # Uygulama listesini apps.json dosyasından yükle
        try:
            with open('apps.json', 'r', encoding='utf-8') as f:
                self.apps = json.load(f)
        except:
            # Varsayılan uygulama listesi
            self.apps = [
                {"name": "Google Chrome", "command": 'winget install Google.Chrome -e --id', "category": "Web Tarayıcılar", "checked": False},
                {"name": "Firefox", "command": 'winget install Mozilla.Firefox -e --id', "category": "Web Tarayıcılar", "checked": False},
                {"name": "VLC Media Player", "command": 'winget install VideoLAN.VLC -e --id', "category": "Medya", "checked": False},
                {"name": "7-Zip", "command": 'winget install 7zip.7zip -e --id', "category": "Araçlar", "checked": False},
                {"name": "VSCode", "command": 'winget install Microsoft.VisualStudioCode -e --id', "category": "Geliştirme", "checked": False},
                {"name": "Spotify", "command": 'winget install Spotify.Spotify -e --id', "category": "Medya", "checked": False},
                {"name": "Discord", "command": 'winget install Discord.Discord -e --id', "category": "İletişim", "checked": False},
                {"name": "Steam", "command": 'winget install Valve.Steam -e --id', "category": "Oyun", "checked": False},
                {"name": "Notepad++", "command": 'winget install Notepad++.Notepad++ -e --id', "category": "Araçlar", "checked": False},
                {"name": "Adobe Reader DC", "command": 'winget install Adobe.AdobeAcrobatReaderDC -e --id', "category": "Araçlar", "checked": False},
                {"name": "WinRAR", "command": 'winget install RARLab.WinRAR -e --id', "category": "Araçlar", "checked": False},
                {"name": "Python", "command": 'winget install Python.Python.3 -e --id', "category": "Geliştirme", "checked": False},
                {"name": "Git", "command": 'winget install Git.Git -e --id', "category": "Geliştirme", "checked": False},
                {"name": "Node.js", "command": 'winget install OpenJS.NodeJS -e --id', "category": "Geliştirme", "checked": False},
                {"name": "Telegram", "command": 'winget install Telegram.TelegramDesktop -e --id', "category": "İletişim", "checked": False},
                {"name": "WhatsApp", "command": 'winget install WhatsApp.WhatsApp -e --id', "category": "İletişim", "checked": False},
                {"name": "Zoom", "command": 'winget install Zoom.Zoom -e --id', "category": "İletişim", "checked": False},
                {"name": "TeamViewer", "command": 'winget install TeamViewer.TeamViewer -e --id', "category": "Araçlar", "checked": False},
                {"name": "qBittorrent", "command": 'winget install qBittorrent.qBittorrent -e --id', "category": "Araçlar", "checked": False},
                {"name": "Blender", "command": 'winget install BlenderFoundation.Blender -e --id', "category": "Grafik & Tasarım", "checked": False},
                {"name": "GIMP", "command": 'winget install GIMP.GIMP -e --id', "category": "Grafik & Tasarım", "checked": False},
                {"name": "OBS Studio", "command": 'winget install OBSProject.OBSStudio -e --id', "category": "Medya", "checked": False},
                {"name": "Microsoft Office", "command": 'winget install Microsoft.Office -e --id', "category": "Ofis", "checked": False},
                {"name": "LibreOffice", "command": 'winget install TheDocumentFoundation.LibreOffice -e --id', "category": "Ofis", "checked": False},
            ]
        
    def load_settings(self):
        # Ayarları settings.json dosyasından yükle
        try:
            with open('settings.json', 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        except:
            # Varsayılan ayarlar
            self.settings = {
                "telemetry": False,
                "cortana": False,
                "onedrive": False,
                "bing": False,
                "edge": False,
                "widgets": False,
                "game_bar": False,
                "tips": False,
                "advertising": False,
                "location_tracking": False,
                "background_apps": False,
                "visual_effects": True,
                "power_plan": "High performance",
                "dark_mode": False,
                "taskbar_alignment": "center"
            }
        
    def save_settings(self):
        # Ayarları settings.json dosyasına kaydet
        with open('settings.json', 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4)
        
    def create_widgets(self):
        # Notebook (sekmeler) oluştur
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Uygulama yükleme sekmesi
        apps_frame = ttk.Frame(notebook, padding=10)
        notebook.add(apps_frame, text='Uygulama Yükleme')
        
        # Kategori filtreleme
        filter_frame = ttk.Frame(apps_frame)
        filter_frame.pack(fill='x', pady=5)
        
        ttk.Label(filter_frame, text="Kategori Filtresi:").pack(side='left', padx=5)
        self.category_var = tk.StringVar()
        categories = list(set([app.get('category', 'Diğer') for app in self.apps]))
        categories.sort()
        categories.insert(0, "Tümü")
        category_combo = ttk.Combobox(filter_frame, textvariable=self.category_var, values=categories, state="readonly")
        category_combo.set("Tümü")
        category_combo.pack(side='left', padx=5)
        category_combo.bind('<<ComboboxSelected>>', self.filter_apps)
        
        # Arama kutusu
        ttk.Label(filter_frame, text="Arama:").pack(side='left', padx=(20, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.filter_apps)
        
        # Uygulama listesi için çerçeve
        list_frame = ttk.Frame(apps_frame)
        list_frame.pack(fill='both', expand=True, pady=5)
        
        # Treeview ile uygulama listesi
        columns = ('selected', 'name', 'category')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', selectmode='browse')
        
        # Sütun başlıkları
        self.tree.heading('selected', text='Seçim', anchor='w')
        self.tree.heading('name', text='Uygulama Adı', anchor='w')
        self.tree.heading('category', text='Kategori', anchor='w')
        
        # Sütun genişlikleri
        self.tree.column('selected', width=50, minwidth=50)
        self.tree.column('name', width=250, minwidth=150)
        self.tree.column('category', width=150, minwidth=100)
        
        # Kaydırma çubuğu
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Uygulamaları treeview'a ekle
        self.populate_apps_list()
        
        # Butonlar
        button_frame = ttk.Frame(apps_frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="Tümünü Seç", command=self.select_all).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Seçimi Temizle", command=self.clear_selection).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Seçilenleri Yükle", command=self.install_selected_apps).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Özel Komut Çalıştır", command=self.run_custom_command).pack(side='right', padx=5)
        
        # Windows ayarları sekmesi
        settings_frame = ttk.Frame(notebook, padding=10)
        notebook.add(settings_frame, text='Windows Ayarları')
        
        # Ayarları kaydırılabilir çerçeve içine al
        settings_canvas = tk.Canvas(settings_frame)
        scrollbar_settings = ttk.Scrollbar(settings_frame, orient='vertical', command=settings_canvas.yview)
        scrollable_frame = ttk.Frame(settings_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all"))
        )
        
        settings_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        settings_canvas.configure(yscrollcommand=scrollbar_settings.set)
        
        settings_canvas.pack(side="left", fill="both", expand=True)
        scrollbar_settings.pack(side="right", fill="y")
        
        # Gizlilik ve güvenlik ayarları
        ttk.Label(scrollable_frame, text="Gizlilik ve Güvenlik Ayarları", font=('Arial', 12, 'bold')).pack(anchor='w', pady=5)
        
        self.var_telemetry = tk.BooleanVar(value=self.settings.get('telemetry', False))
        ttk.Checkbutton(scrollable_frame, text="Telemetri verilerini devre dışı bırak", 
                       variable=self.var_telemetry).pack(anchor='w', pady=2)
        
        self.var_cortana = tk.BooleanVar(value=self.settings.get('cortana', False))
        ttk.Checkbutton(scrollable_frame, text="Cortana'yı devre dışı bırak", 
                       variable=self.var_cortana).pack(anchor='w', pady=2)
        
        self.var_bing = tk.BooleanVar(value=self.settings.get('bing', False))
        ttk.Checkbutton(scrollable_frame, text="Windows Search'te Bing entegrasyonunu devre dışı bırak", 
                       variable=self.var_bing).pack(anchor='w', pady=2)
        
        self.var_widgets = tk.BooleanVar(value=self.settings.get('widgets', False))
        ttk.Checkbutton(scrollable_frame, text="Widget'ları devre dışı bırak", 
                       variable=self.var_widgets).pack(anchor='w', pady=2)
        
        self.var_game_bar = tk.BooleanVar(value=self.settings.get('game_bar', False))
        ttk.Checkbutton(scrollable_frame, text="Oyun çubuğunu devre dışı bırak", 
                       variable=self.var_game_bar).pack(anchor='w', pady=2)
        
        self.var_tips = tk.BooleanVar(value=self.settings.get('tips', False))
        ttk.Checkbutton(scrollable_frame, text="Windows ipuçlarını devre dışı bırak", 
                       variable=self.var_tips).pack(anchor='w', pady=2)
        
        self.var_advertising = tk.BooleanVar(value=self.settings.get('advertising', False))
        ttk.Checkbutton(scrollable_frame, text="Reklam kimliğini devre dışı bırak", 
                       variable=self.var_advertising).pack(anchor='w', pady=2)
        
        self.var_location_tracking = tk.BooleanVar(value=self.settings.get('location_tracking', False))
        ttk.Checkbutton(scrollable_frame, text="Konum izlemeyi devre dışı bırak", 
                       variable=self.var_location_tracking).pack(anchor='w', pady=2)
        
        self.var_background_apps = tk.BooleanVar(value=self.settings.get('background_apps', False))
        ttk.Checkbutton(scrollable_frame, text="Arka plan uygulamalarını devre dışı bırak", 
                       variable=self.var_background_apps).pack(anchor='w', pady=2)
        
        # Sistem performans ayarları
        ttk.Label(scrollable_frame, text="Sistem Performans Ayarları", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(15, 5))
        
        self.var_visual_effects = tk.BooleanVar(value=self.settings.get('visual_effects', True))
        ttk.Checkbutton(scrollable_frame, text="Görsel efektleri en iyi performans için ayarla", 
                       variable=self.var_visual_effects).pack(anchor='w', pady=2)
        
        ttk.Label(scrollable_frame, text="Güç planı:").pack(anchor='w', pady=2)
        self.power_plan_var = tk.StringVar(value=self.settings.get('power_plan', 'Yüksek performans'))
        power_plans = ["Yüksek performans", "Dengeli", "Güç tasarrufu"]
        ttk.Combobox(scrollable_frame, textvariable=self.power_plan_var, values=power_plans, state="readonly").pack(anchor='w', pady=2)
        
        # Kişiselleştirme ayarları
        ttk.Label(scrollable_frame, text="Kişiselleştirme Ayarları", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(15, 5))
        
        self.var_dark_mode = tk.BooleanVar(value=self.settings.get('dark_mode', False))
        ttk.Checkbutton(scrollable_frame, text="Koyu modu etkinleştir", 
                       variable=self.var_dark_mode).pack(anchor='w', pady=2)
        
        ttk.Label(scrollable_frame, text="Görev çubuğu hizalaması:").pack(anchor='w', pady=2)
        self.taskbar_alignment_var = tk.StringVar(value=self.settings.get('taskbar_alignment', 'center'))
        alignments = ["center", "left"]
        ttk.Combobox(scrollable_frame, textvariable=self.taskbar_alignment_var, values=alignments, state="readonly").pack(anchor='w', pady=2)
        
        # Uygulama kaldırma
        ttk.Label(scrollable_frame, text="Uygulama Kaldırma", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(15, 5))
        
        self.var_onedrive = tk.BooleanVar(value=self.settings.get('onedrive', False))
        ttk.Checkbutton(scrollable_frame, text="OneDrive'ı kaldır", 
                       variable=self.var_onedrive).pack(anchor='w', pady=2)
        
        self.var_edge = tk.BooleanVar(value=self.settings.get('edge', False))
        ttk.Checkbutton(scrollable_frame, text="Microsoft Edge'i kaldır", 
                       variable=self.var_edge).pack(anchor='w', pady=2)
        
        # Ayarları uygula butonu
        ttk.Button(scrollable_frame, text="Ayarları Uygula", command=self.apply_settings).pack(pady=10)
        
        # Sistem bilgisi sekmesi
        sysinfo_frame = ttk.Frame(notebook, padding=10)
        notebook.add(sysinfo_frame, text='Sistem Bilgisi')
        
        # Sistem bilgisi metin kutusu
        sysinfo_text = scrolledtext.ScrolledText(sysinfo_frame, width=80, height=20)
        sysinfo_text.pack(fill='both', expand=True)
        
        # Sistem bilgisini al ve göster
        sys_info = self.get_system_info()
        sysinfo_text.insert('1.0', sys_info)
        sysinfo_text.config(state='disabled')
        
        # Durum çubuğu
        self.status_var = tk.StringVar()
        self.status_var.set("Hazır")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief='sunken', anchor='w')
        status_bar.pack(side='bottom', fill='x')
        
        # İlerleme çubuğu
        self.progress = ttk.Progressbar(self.root, orient='horizontal', length=100, mode='determinate')
        self.progress.pack(side='bottom', fill='x')
    
    def populate_apps_list(self):
        # Treeview'ı temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Uygulamaları treeview'a ekle
        for i, app in enumerate(self.apps):
            self.tree.insert('', 'end', iid=i, values=('❌', app['name'], app.get('category', 'Diğer')))
        
        # Tıklama olayını bağla
        self.tree.bind('<Button-1>', self.on_tree_click)
    
    def on_tree_click(self, event):
        # Tıklanan öğeyi al
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        if item and column == '#1':  # Sadece ilk sütuna (seçim sütunu) tıklandığında
            # Mevcut durumu al ve değiştir
            current_val = self.tree.item(item, 'values')[0]
            new_val = '✅' if current_val == '❌' else '❌'
            
            # Değeri güncelle
            values = list(self.tree.item(item, 'values'))
            values[0] = new_val
            self.tree.item(item, values=values)
            
            # Uygulama listesini güncelle
            index = int(item)
            self.apps[index]['checked'] = (new_val == '✅')
    
    def filter_apps(self, event=None):
        # Filtreleme işlemi
        category = self.category_var.get()
        search_text = self.search_var.get().lower()
        
        # Treeview'ı temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filtrelenmiş uygulamaları ekle
        for i, app in enumerate(self.apps):
            app_category = app.get('category', 'Diğer')
            app_name = app['name'].lower()
            
            # Kategori ve arama metni filtresi
            if (category == "Tümü" or app_category == category) and search_text in app_name:
                checked = '✅' if app['checked'] else '❌'
                self.tree.insert('', 'end', iid=i, values=(checked, app['name'], app_category))
    
    def select_all(self):
        # Tüm uygulamaları seç
        for i, app in enumerate(self.apps):
            app['checked'] = True
            if i in self.tree.get_children():
                values = list(self.tree.item(i, 'values'))
                values[0] = '✅'
                self.tree.item(i, values=values)
    
    def clear_selection(self):
        # Tüm seçimleri temizle
        for i, app in enumerate(self.apps):
            app['checked'] = False
            if i in self.tree.get_children():
                values = list(self.tree.item(i, 'values'))
                values[0] = '❌'
                self.tree.item(i, values=values)
    
    def install_selected_apps(self):
        # Seçilen uygulamaları yükle
        selected_apps = [app for app in self.apps if app['checked']]
        
        if not selected_apps:
            messagebox.showwarning("Uyarı", "Lütfen yüklenecek uygulamaları seçin.")
            return
        
        # Winget kontrolü
        if not self.is_winget_installed():
            messagebox.showerror("Hata", "Winget yüklü değil. Lütfen önce Winget'i yükleyin.")
            return
        
        # İlerleme çubuğunu ayarla
        self.progress['maximum'] = len(selected_apps)
        self.progress['value'] = 0
        
        # Yükleme işlemini ayrı bir thread'de başlat
        thread = threading.Thread(target=self.install_apps_thread, args=(selected_apps,))
        thread.daemon = True
        thread.start()
    
    def install_apps_thread(self, apps):
        # Uygulamaları yükleme thread'i
        for i, app in enumerate(apps):
            self.status_var.set(f"Yükleniyor: {app['name']}")
            self.progress['value'] = i
            
            try:
                # Uygulamayı yükle
                result = subprocess.run(app['command'], shell=True, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    self.status_var.set(f"Yüklendi: {app['name']}")
                else:
                    self.status_var.set(f"Hata: {app['name']} yüklenemedi")
            except subprocess.TimeoutExpired:
                self.status_var.set(f"Zaman aşımı: {app['name']}")
            except Exception as e:
                self.status_var.set(f"Hata: {str(e)}")
        
        self.progress['value'] = len(apps)
        self.status_var.set("Yükleme tamamlandı")
        messagebox.showinfo("Bilgi", "Seçilen uygulamaların yüklenmesi tamamlandı.")
    
    def run_custom_command(self):
        # Özel komut çalıştırma penceresi
        custom_window = tk.Toplevel(self.root)
        custom_window.title("Özel Komut Çalıştır")
        custom_window.geometry("500x300")
        
        ttk.Label(custom_window, text="Çalıştırılacak komut:").pack(pady=5)
        command_entry = ttk.Entry(custom_window, width=50)
        command_entry.pack(pady=5, padx=10, fill='x')
        
        ttk.Label(custom_window, text="Çıktı:").pack(pady=5)
        output_text = scrolledtext.ScrolledText(custom_window, width=60, height=10)
        output_text.pack(pady=5, padx=10, fill='both', expand=True)
        
        def execute_command():
            command = command_entry.get()
            if not command:
                messagebox.showwarning("Uyarı", "Lütfen bir komut girin.")
                return
            
            try:
                output_text.delete('1.0', 'end')
                output_text.insert('end', f"Çalıştırılıyor: {command}\n\n")
                
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
                
                if result.stdout:
                    output_text.insert('end', "Çıktı:\n")
                    output_text.insert('end', result.stdout)
                
                if result.stderr:
                    output_text.insert('end', "\nHatalar:\n")
                    output_text.insert('end', result.stderr)
                
                output_text.insert('end', f"\n\nÇıkış kodu: {result.returncode}")
                
            except Exception as e:
                output_text.insert('end', f"Hata: {str(e)}")
        
        ttk.Button(custom_window, text="Çalıştır", command=execute_command).pack(pady=10)
    
    def is_winget_installed(self):
        try:
            subprocess.run("winget --version", shell=True, capture_output=True, check=True)
            return True
        except:
            return False
    
    def install_winget(self):
        # Winget'i yükle
        self.status_var.set("Winget yükleniyor...")
        try:
            # Microsoft Store'dan App Installer'ı yükle
            result = subprocess.run("start ms-appinstaller:?source=https://aka.ms/getwinget", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.status_var.set("Winget yüklendi. Lütfen uygulamayı yeniden başlatın.")
            else:
                self.status_var.set("Winget yüklenirken hata oluştu.")
        except Exception as e:
            self.status_var.set(f"Winget yüklenirken hata: {str(e)}")
    
    def apply_settings(self):
        # Ayarları uygula
        self.status_var.set("Ayarlar uygulanıyor...")
        self.root.update()
        
        try:
            # Ayarları kaydet
            self.settings = {
                "telemetry": self.var_telemetry.get(),
                "cortana": self.var_cortana.get(),
                "onedrive": self.var_onedrive.get(),
                "bing": self.var_bing.get(),
                "edge": self.var_edge.get(),
                "widgets": self.var_widgets.get(),
                "game_bar": self.var_game_bar.get(),
                "tips": self.var_tips.get(),
                "advertising": self.var_advertising.get(),
                "location_tracking": self.var_location_tracking.get(),
                "background_apps": self.var_background_apps.get(),
                "visual_effects": self.var_visual_effects.get(),
                "power_plan": self.power_plan_var.get(),
                "dark_mode": self.var_dark_mode.get(),
                "taskbar_alignment": self.taskbar_alignment_var.get()
            }
            
            self.save_settings()
            
            # Telemetri ayarlarını uygula
            if self.var_telemetry.get():
                self.disable_telemetry()
            
            # Cortana'yı devre dışı bırak
            if self.var_cortana.get():
                self.disable_cortana()
            
            # OneDrive'ı kaldır
            if self.var_onedrive.get():
                self.uninstall_onedrive()
            
            # Bing entegrasyonunu devre dışı bırak
            if self.var_bing.get():
                self.disable_bing_integration()
            
            # Widget'ları devre dışı bırak
            if self.var_widgets.get():
                self.disable_widgets()
            
            # Oyun çubuğunu devre dışı bırak
            if self.var_game_bar.get():
                self.disable_game_bar()
            
            # Windows ipuçlarını devre dışı bırak
            if self.var_tips.get():
                self.disable_tips()
            
            # Reklam kimliğini devre dışı bırak
            if self.var_advertising.get():
                self.disable_advertising()
            
            # Konum izlemeyi devre dışı bırak
            if self.var_location_tracking.get():
                self.disable_location_tracking()
            
            # Arka plan uygulamalarını devre dışı bırak
            if self.var_background_apps.get():
                self.disable_background_apps()
            
            # Görsel efektleri ayarla
            if self.var_visual_effects.get():
                self.set_visual_effects()
            
            # Güç planını ayarla
            self.set_power_plan(self.power_plan_var.get())
            
            # Koyu modu ayarla
            if self.var_dark_mode.get():
                self.enable_dark_mode()
            
            # Görev çubuğu hizalamasını ayarla
            self.set_taskbar_alignment(self.taskbar_alignment_var.get())
            
            # Edge'i kaldır
            if self.var_edge.get():
                self.uninstall_edge()
            
            self.status_var.set("Ayarlar başarıyla uygulandı")
            messagebox.showinfo("Bilgi", "Ayarlar başarıyla uygulandı. Bazı değişikliklerin etkili olması için bilgisayarı yeniden başlatmanız gerekebilir.")
            
        except Exception as e:
            self.status_var.set(f"Hata: {str(e)}")
            messagebox.showerror("Hata", f"Ayarlar uygulanırken hata oluştu: {str(e)}")
    
    def disable_telemetry(self):
        # Telemetriyi devre dışı bırakmak için registry ayarları
        try:
            # Genel telemetri ayarı
            key = winreg.HKEY_LOCAL_MACHINE
            subkey = r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "AllowTelemetry", 0, winreg.REG_DWORD, 0)
            
            # Diğer telemetri ayarları
            subkey = r"SOFTWARE\Policies\Microsoft\Windows\AppCompat"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "AITEnable", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(registry_key, "DisableInventory", 0, winreg.REG_DWORD, 1)
            
            # Tanılama verileri
            subkey = r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "AllowDeviceNameInTelemetry", 0, winreg.REG_DWORD, 0)
            
            # Uçuş verileri
            subkey = r"SOFTWARE\Policies\Microsoft\Windows\Flighting"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "AllowTelemetry", 0, winreg.REG_DWORD, 0)
            
        except Exception as e:
            raise Exception(f"Telemetri ayarları yapılandırılamadı: {str(e)}")
    
    def disable_cortana(self):
        # Cortana'yı devre dışı bırakmak için registry ayarları
        try:
            key = winreg.HKEY_LOCAL_MACHINE
            subkey = r"SOFTWARE\Policies\Microsoft\Windows\Windows Search"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "AllowCortana", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(registry_key, "DisableWebSearch", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(registry_key, "ConnectedSearchUseWeb", 0, winreg.REG_DWORD, 0)
            
        except Exception as e:
            raise Exception(f"Cortana devre dışı bırakılamadı: {str(e)}")
    
    def uninstall_onedrive(self):
        # OneDrive'ı kaldır
        try:
            # OneDrive kurulumunu kaldır
            result = subprocess.run(
                r"%SystemRoot%\SysWOW64\OneDriveSetup.exe /uninstall", 
                shell=True, capture_output=True, text=True
            )
            
            # OneDrive proseslerini durdur
            subprocess.run("taskkill /f /im OneDrive.exe", shell=True, capture_output=True)
            subprocess.run("taskkill /f /im OneDriveSetup.exe", shell=True, capture_output=True)
            
            # OneDrive kayıt defteri girdilerini temizle
            key = winreg.HKEY_LOCAL_MACHINE
            try:
                winreg.DeleteKey(key, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\OneDrive")
            except:
                pass
            
        except Exception as e:
            raise Exception(f"OneDrive kaldırılamadı: {str(e)}")
    
    def disable_bing_integration(self):
        # Windows Search'te Bing entegrasyonunu devre dışı bırak
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "BingSearchEnabled", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(registry_key, "CortanaConsent", 0, winreg.REG_DWORD, 0)
            
            key = winreg.HKEY_LOCAL_MACHINE
            subkey = r"SOFTWARE\Policies\Microsoft\Windows\Windows Search"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "DisableWebSearch", 0, winreg.REG_DWORD, 1)
            
        except Exception as e:
            raise Exception(f"Bing entegrasyonu devre dışı bırakılamadı: {str(e)}")
    
    def disable_widgets(self):
        # Widget'ları devre dışı bırak
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "DisableWidgets", 0, winreg.REG_DWORD, 1)
            
        except Exception as e:
            raise Exception(f"Widget'lar devre dışı bırakılamadı: {str(e)}")
    
    def disable_game_bar(self):
        # Oyun çubuğunu devre dışı bırak
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "AppCaptureEnabled", 0, winreg.REG_DWORD, 0)
            
            key = winreg.HKEY_LOCAL_MACHINE
            subkey = r"SOFTWARE\Policies\Microsoft\Windows\GameDVR"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "AllowGameDVR", 0, winreg.REG_DWORD, 0)
            
        except Exception as e:
            raise Exception(f"Oyun çubuğu devre dışı bırakılamadı: {str(e)}")
    
    def disable_tips(self):
        # Windows ipuçlarını devre dışı bırak
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "SubscribedContent-310093Enabled", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(registry_key, "SubscribedContent-338389Enabled", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(registry_key, "SubscribedContent-338393Enabled", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(registry_key, "SubscribedContent-353694Enabled", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(registry_key, "SubscribedContent-353696Enabled", 0, winreg.REG_DWORD, 0)
            
        except Exception as e:
            raise Exception(f"Windows ipuçları devre dışı bırakılamadı: {str(e)}")
    
    def disable_advertising(self):
        # Reklam kimliğini devre dışı bırak
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "Enabled", 0, winreg.REG_DWORD, 0)
            
        except Exception as e:
            raise Exception(f"Reklam kimliği devre dışı bırakılamadı: {str(e)}")
    
    def disable_location_tracking(self):
        # Konum izlemeyi devre dışı bırak
        try:
            key = winreg.HKEY_LOCAL_MACHINE
            subkey = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Sensor\Overrides\{BFA794E4-F964-4FDB-90F6-51056BFE4B44}"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "SensorPermissionState", 0, winreg.REG_DWORD, 0)
            
            key = winreg.HKEY_CURRENT_USER
            subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\DeviceAccess\Global\{BFA794E4-F964-4FDB-90F6-51056BFE4B44}"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "Value", 0, winreg.REG_SZ, "Deny")
            
        except Exception as e:
            raise Exception(f"Konum izleme devre dışı bırakılamadı: {str(e)}")
    
    def disable_background_apps(self):
        # Arka plan uygulamalarını devre dışı bırak
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "GlobalUserDisabled", 0, winreg.REG_DWORD, 1)
            
        except Exception as e:
            raise Exception(f"Arka plan uygulamaları devre dışı bırakılamadı: {str(e)}")
    
    def set_visual_effects(self):
        # Görsel efektleri en iyi performans için ayarla
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
            
            # Sistem özellikleri penceresini aç ve performans seçeneklerini ayarla
            subprocess.run("SystemPropertiesPerformance.exe", shell=True)
            
        except Exception as e:
            raise Exception(f"Görsel efektler ayarlanamadı: {str(e)}")
    
    def set_power_plan(self, plan):
        # Güç planını ayarla
        try:
            if plan == "Yüksek performans":
                subprocess.run('powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c', shell=True)
            elif plan == "Güç tasarrufu":
                subprocess.run('powercfg -setactive a1841308-3541-4fab-bc81-f71556f20b4a', shell=True)
            else:  # Dengeli
                subprocess.run('powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e', shell=True)
            
        except Exception as e:
            raise Exception(f"Güç planı ayarlanamadı: {str(e)}")
    
    def enable_dark_mode(self):
        # Koyu modu etkinleştir
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            with winreg.CreateKey(key, subkey) as registry_key:
                winreg.SetValueEx(registry_key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(registry_key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, 0)
            
        except Exception as e:
            raise Exception(f"Koyu mod etkinleştirilemedi: {str(e)}")
    
    def set_taskbar_alignment(self, alignment):
        # Görev çubuğu hizalamasını ayarla
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            with winreg.CreateKey(key, subkey) as registry_key:
                value = 1 if alignment == "center" else 0
                winreg.SetValueEx(registry_key, "TaskbarAl", 0, winreg.REG_DWORD, value)
            
            # Explorer'ı yeniden başlat
            subprocess.run("taskkill /f /im explorer.exe", shell=True, capture_output=True)
            subprocess.run("start explorer.exe", shell=True)
            
        except Exception as e:
            raise Exception(f"Görev çubuğu hizalaması ayarlanamadı: {str(e)}")
    
    def uninstall_edge(self):
        # Microsoft Edge'i kaldır
        try:
            result = subprocess.run(
                "winget uninstall Microsoft.Edge -e --id", 
                shell=True, capture_output=True, text=True
            )
            if result.returncode != 0:
                # Alternatif kaldırma yöntemi
                subprocess.run(
                    r'C:\Program Files (x86)\Microsoft\Edge\Application\*\Installer\setup.exe --uninstall --system-level --force-uninstall', 
                    shell=True
                )
            
        except Exception as e:
            raise Exception(f"Microsoft Edge kaldırılamadı: {str(e)}")
    
    def get_system_info(self):
        # Sistem bilgilerini al
        try:
            info = []
            
            # İşletim sistemi bilgisi
            result = subprocess.run('systeminfo | findstr /B /C:"OS Name" /C:"OS Version"', shell=True, capture_output=True, text=True)
            info.append("=== İşletim Sistemi Bilgisi ===\n")
            info.append(result.stdout)
            
            # Donanım bilgisi
            result = subprocess.run('systeminfo | findstr /B /C:"System Model" /C:"Processor(s)" /C:"Total Physical Memory"', shell=True, capture_output=True, text=True)
            info.append("\n=== Donanım Bilgisi ===\n")
            info.append(result.stdout)
            
            # Disk bilgisi
            result = subprocess.run('wmic diskdrive get size,model', shell=True, capture_output=True, text=True)
            info.append("\n=== Disk Bilgisi ===\n")
            info.append(result.stdout)
            
            # Ağ bilgisi
            result = subprocess.run('ipconfig | findstr IPv4', shell=True, capture_output=True, text=True)
            info.append("\n=== Ağ Bilgisi ===\n")
            info.append(result.stdout)
            
            return "\n".join(info)
            
        except Exception as e:
            return f"Sistem bilgisi alınamadı: {str(e)}"

if __name__ == "__main__":
    root = tk.Tk()
    app = WindowsSetupTool(root)
    root.mainloop()