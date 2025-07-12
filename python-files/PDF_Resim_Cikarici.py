import fitz  # PyMuPDF
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from collections import defaultdict
from PIL import Image, ImageTk
import io
import threading
import math

class ResimOnizleme:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Çıkarılan Resimler")
        self.window.geometry("900x600")
        self.window.configure(bg="#f8fafc")
        
        # Resim referanslarını tutmak için liste
        self.photo_references = []
        
        # Başlık
        ttk.Label(self.window, text="Çıkarılan Resimler", 
                font=("Arial", 18, "bold"), background="#2563eb", foreground="white", anchor="center").pack(fill=tk.X, pady=10)
        
        # Canvas ve scrollbar
        canvas_frame = ttk.Frame(self.window)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#f8fafc", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Kapat butonu
        ttk.Button(self.window, text="Kapat", command=self.window.destroy, style="Accent.TButton").pack(pady=10)
    
    def resim_ekle(self, image_path, image_name):
        """Önizleme penceresine resim ekler (grid ile)"""
        try:
            img = Image.open(image_path)
            img.thumbnail((140, 140), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            idx = len(self.scrollable_frame.winfo_children())
            row, col = divmod(idx, 5)
            frame = ttk.Frame(self.scrollable_frame, style="Card.TFrame", padding=8)
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            img_label = ttk.Label(frame, image=photo, background="#f8fafc")
            img_label.pack()
            # Referansı korumak için listeye ekle
            self.photo_references.append(photo)
            ttk.Label(frame, text=image_name, font=("Arial", 9), background="#f8fafc", foreground="#222").pack()
            size_kb = os.path.getsize(image_path) / 1024
            ttk.Label(frame, text=f"{size_kb:.1f} KB", font=("Arial", 8), background="#f8fafc", foreground="#666").pack()
        except Exception as e:
            print(f"Resim yüklenirken hata: {e}")

class ModernButton(tk.Button):
    """Modern görünümlü buton sınıfı"""
    def __init__(self, parent, **kwargs):
        # Varsayılan stil
        default_style = {
            'font': ('Arial', 10),
            'relief': 'flat',
            'borderwidth': 0,
            'cursor': 'hand2',
            'padx': 15,
            'pady': 8
        }
        default_style.update(kwargs)
        super().__init__(parent, **default_style)
        
        # Hover efektleri
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        
        # Animasyon için değişkenler
        self.animation_id = None
        self.original_bg = self.cget('bg')
        self.original_fg = self.cget('fg')
    
    def on_enter(self, event):
        """Mouse üzerine geldiğinde"""
        if self.animation_id:
            self.after_cancel(self.animation_id)
        
        # Hover rengini hesapla
        bg_color = self.cget('bg')
        if bg_color == '#4CAF50':  # Yeşil
            hover_bg = '#45a049'
        elif bg_color == '#2196F3':  # Mavi
            hover_bg = '#1976D2'
        elif bg_color == '#FF5722':  # Kırmızı
            hover_bg = '#D32F2F'
        elif bg_color == '#9C27B0':  # Mor
            hover_bg = '#7B1FA2'
        elif bg_color == '#00BCD4':  # Cyan
            hover_bg = '#0097A7'
        elif bg_color == '#FF9800':  # Turuncu
            hover_bg = '#F57C00'
        elif bg_color == '#607D8B':  # Gri
            hover_bg = '#455A64'
        else:
            hover_bg = '#E0E0E0'
        
        self.configure(bg=hover_bg)
    
    def on_leave(self, event):
        """Mouse ayrıldığında"""
        if self.animation_id:
            self.after_cancel(self.animation_id)
        self.configure(bg=self.original_bg)
    
    def on_click(self, event):
        """Tıklama animasyonu"""
        original_bg = self.cget('bg')
        self.configure(bg='#CCCCCC')
        self.animation_id = self.after(100, lambda: self.configure(bg=original_bg))

class AnimatedProgressBar(ttk.Progressbar):
    """Animasyonlu progress bar"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.animation_speed = 0.05
        self.animation_running = False
        self.pulse_value = 0
    
    def start_animation(self):
        """Animasyonu başlat"""
        self.animation_running = True
        self.pulse_animation()
    
    def stop_animation(self):
        """Animasyonu durdur"""
        self.animation_running = False
    
    def pulse_animation(self):
        """Pulse animasyonu"""
        if not self.animation_running:
            return
        
        self.pulse_value += 0.1
        if self.pulse_value > 2 * math.pi:
            self.pulse_value = 0
        
        # Pulse efekti için alpha değeri
        alpha = abs(math.sin(self.pulse_value)) * 0.3 + 0.7
        
        # Progress bar rengini güncelle
        style = ttk.Style()
        style.configure("Animated.Horizontal.TProgressbar", 
                       background=f'#{int(76 * alpha):02x}{int(175 * alpha):02x}{int(80 * alpha):02x}')
        
        self.after(50, self.pulse_animation)

class PDFResimCikarici:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF Resim Çıkarıcı v6.0")
        self.root.geometry("650x700")
        self.setup_styles()
        self.setup_ui()
        self.processed_images = set()
        self.extracted_images = []
        self.load_history()
        self.cancel_operation = False
        self.current_theme = "light"
        self.load_settings()
    
    def setup_styles(self):
        """Modern stil ayarları"""
        style = ttk.Style()
        
        # Ana tema renkleri
        self.colors = {
            'primary': '#2563eb',
            'secondary': '#64748b',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'info': '#06b6d4',
            'light': '#f8fafc',
            'dark': '#1e293b',
            'white': '#ffffff',
            'gray_100': '#f1f5f9',
            'gray_200': '#e2e8f0',
            'gray_300': '#cbd5e1',
            'gray_400': '#94a3b8',
            'gray_500': '#64748b',
            'gray_600': '#475569',
            'gray_700': '#334155',
            'gray_800': '#1e293b',
            'gray_900': '#0f172a'
        }
        
        # Progress bar stilleri
        style.configure("Animated.Horizontal.TProgressbar",
                       background=self.colors['success'],
                       troughcolor=self.colors['gray_200'],
                       thickness=12,
                       borderwidth=0)
        
        # Frame stilleri
        style.configure("Card.TFrame",
                       background=self.colors['white'],
                       relief="flat",
                       borderwidth=1)
        
        # Label stilleri
        style.configure("Title.TLabel",
                       font=("Arial", 16, "bold"),
                       background=self.colors['primary'],
                       foreground=self.colors['white'])
        
        style.configure("Subtitle.TLabel",
                       font=("Arial", 12, "bold"),
                       background=self.colors['gray_100'],
                       foreground=self.colors['gray_800'])
        
        style.configure("Info.TLabel",
                       font=("Arial", 10),
                       background=self.colors['white'],
                       foreground=self.colors['gray_600'])
    
    def setup_ui(self):
        """Modern arayüz kurulumu"""
        # Ana pencere ayarları
        self.root.configure(bg=self.colors['light'])
        self.root.option_add('*Font', 'Arial 10')
        
        # Başlık bölümü
        self.create_header()
        
        # Ana içerik
        main_frame = tk.Frame(self.root, bg=self.colors['light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # PDF Seçme bölümü
        self.create_pdf_section(main_frame)
        
        # Klasör Seçme bölümü
        self.create_folder_section(main_frame)
        
        # Ayarlar bölümü
        self.create_settings_section(main_frame)
        
        # İlerleme bölümü
        self.create_progress_section(main_frame)
        
        # Butonlar bölümü
        self.create_buttons_section(main_frame)
        
        # Durum çubuğu
        self.create_status_bar()
        
        # Animasyonlu progress bar
        self.progress_bar = AnimatedProgressBar(main_frame, style="Animated.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=(10, 5))
    
    def create_header(self):
        """Başlık bölümü"""
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Logo/İkon simülasyonu (emoji kullanarak)
        logo_label = tk.Label(header_frame, text="📄", font=("Arial", 24), 
                             bg=self.colors['primary'], fg=self.colors['white'])
        logo_label.pack(side=tk.LEFT, padx=(20, 10), pady=20)
        
        # Başlık
        title_label = tk.Label(header_frame, text="PDF Resim Çıkarıcı", 
                              font=("Arial", 20, "bold"), 
                              bg=self.colors['primary'], fg=self.colors['white'])
        title_label.pack(side=tk.LEFT, pady=20)
        
        # Versiyon
        version_label = tk.Label(header_frame, text="v6.0", 
                                font=("Arial", 12), 
                                bg=self.colors['primary'], fg=self.colors['gray_300'])
        version_label.pack(side=tk.RIGHT, padx=20, pady=20)
    
    def create_pdf_section(self, parent):
        """PDF seçme bölümü"""
        section_frame = tk.Frame(parent, bg=self.colors['white'], relief="flat", bd=1)
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Başlık
        title_frame = tk.Frame(section_frame, bg=self.colors['gray_100'])
        title_frame.pack(fill=tk.X)
        
        tk.Label(title_frame, text="📁 PDF Dosyası Seçimi", 
                font=("Arial", 12, "bold"), 
                bg=self.colors['gray_100'], fg=self.colors['gray_800']).pack(anchor=tk.W, padx=15, pady=10)
        
        # İçerik
        content_frame = tk.Frame(section_frame, bg=self.colors['white'])
        content_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Dosya yolu girişi
        self.pdf_path_entry = tk.Entry(content_frame, font=("Arial", 10), 
                                      bg=self.colors['gray_100'], fg=self.colors['gray_800'],
                                      relief="flat", bd=8)
        self.pdf_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Butonlar
        button_frame = tk.Frame(content_frame, bg=self.colors['white'])
        button_frame.pack(side=tk.RIGHT)
        
        ModernButton(button_frame, text="📂 Dosya Seç", command=self.select_pdf,
                    bg=self.colors['primary'], fg=self.colors['white']).pack(side=tk.LEFT, padx=2)
        
        ModernButton(button_frame, text="🕒 Geçmiş", command=self.show_history,
                    bg=self.colors['warning'], fg=self.colors['white']).pack(side=tk.LEFT, padx=2)
    
    def create_folder_section(self, parent):
        """Klasör seçme bölümü"""
        section_frame = tk.Frame(parent, bg=self.colors['white'], relief="flat", bd=1)
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Başlık
        title_frame = tk.Frame(section_frame, bg=self.colors['gray_100'])
        title_frame.pack(fill=tk.X)
        
        tk.Label(title_frame, text="📂 Kayıt Klasörü", 
                font=("Arial", 12, "bold"), 
                bg=self.colors['gray_100'], fg=self.colors['gray_800']).pack(anchor=tk.W, padx=15, pady=10)
        
        # İçerik
        content_frame = tk.Frame(section_frame, bg=self.colors['white'])
        content_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Klasör yolu girişi
        self.folder_path_entry = tk.Entry(content_frame, font=("Arial", 10), 
                                         bg=self.colors['gray_100'], fg=self.colors['gray_800'],
                                         relief="flat", bd=8)
        self.folder_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Butonlar
        button_frame = tk.Frame(content_frame, bg=self.colors['white'])
        button_frame.pack(side=tk.RIGHT)
        
        ModernButton(button_frame, text="📁 Klasör Seç", command=self.select_folder,
                    bg=self.colors['primary'], fg=self.colors['white']).pack(side=tk.LEFT, padx=2)
        
        ModernButton(button_frame, text="⚡ Batch", command=self.batch_process,
                    bg=self.colors['info'], fg=self.colors['white']).pack(side=tk.LEFT, padx=2)
    
    def create_settings_section(self, parent):
        """Ayarlar bölümü"""
        section_frame = tk.Frame(parent, bg=self.colors['white'], relief="flat", bd=1)
        section_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Başlık
        title_frame = tk.Frame(section_frame, bg=self.colors['gray_100'])
        title_frame.pack(fill=tk.X)
        
        tk.Label(title_frame, text="⚙️ Ayarlar", 
                font=("Arial", 12, "bold"), 
                bg=self.colors['gray_100'], fg=self.colors['gray_800']).pack(anchor=tk.W, padx=15, pady=10)
        
        # İçerik
        content_frame = tk.Frame(section_frame, bg=self.colors['white'])
        content_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Grid düzeni için
        settings_grid = tk.Frame(content_frame, bg=self.colors['white'])
        settings_grid.pack(fill=tk.X)
        
        # Resim İsim Formatı
        tk.Label(settings_grid, text="📝 Resim İsim Formatı:", 
                font=("Arial", 10), bg=self.colors['white'], fg=self.colors['gray_700']).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.name_format = ttk.Combobox(settings_grid, values=[
            "sayfa_{page}_resim_{img}.{ext}",
            "resim_{num}.{ext}",
            "{pdfname}_sayfa{page}_{img}.{ext}",
            "{pdfname}_{num}.{ext}"
        ], width=40, font=("Arial", 9))
        self.name_format.set("sayfa_{page}_resim_{img}.{ext}")
        self.name_format.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Minimum Resim Boyutu
        tk.Label(settings_grid, text="📏 Min. Resim Boyutu (KB):", 
                font=("Arial", 10), bg=self.colors['white'], fg=self.colors['gray_700']).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.min_size_var = tk.StringVar(value="10")
        min_size_entry = tk.Entry(settings_grid, textvariable=self.min_size_var, width=10, 
                                 font=("Arial", 9), bg=self.colors['gray_100'], relief="flat", bd=5)
        min_size_entry.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Resim Formatları
        tk.Label(settings_grid, text="🖼️ Resim Formatları:", 
                font=("Arial", 10), bg=self.colors['white'], fg=self.colors['gray_700']).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.format_var = tk.StringVar(value="jpeg,png,gif,bmp")
        format_entry = tk.Entry(settings_grid, textvariable=self.format_var, width=40, 
                               font=("Arial", 9), bg=self.colors['gray_100'], relief="flat", bd=5)
        format_entry.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Çıkarılan resim uzantısı
        tk.Label(settings_grid, text="🔄 Çıkarılan Resim Uzantısı:", 
                font=("Arial", 10), bg=self.colors['white'], fg=self.colors['gray_700']).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.output_format = ttk.Combobox(settings_grid, values=[
            "Orijinal format korunsun",
            "JPEG (.jpg)",
            "PNG (.png)",
            "BMP (.bmp)",
            "TIFF (.tiff)",
            "WebP (.webp)"
        ], width=30, font=("Arial", 9))
        self.output_format.set("Orijinal format korunsun")
        self.output_format.grid(row=3, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Kalite ayarı
        tk.Label(settings_grid, text="🎯 JPEG Kalitesi (%):", 
                font=("Arial", 10), bg=self.colors['white'], fg=self.colors['gray_700']).grid(row=4, column=0, sticky=tk.W, pady=5)
        
        self.jpeg_quality = tk.StringVar(value="100")
        quality_spinbox = tk.Spinbox(settings_grid, from_=1, to=100, textvariable=self.jpeg_quality, 
                                    width=10, font=("Arial", 9), bg=self.colors['gray_100'], relief="flat", bd=5)
        quality_spinbox.grid(row=4, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Resim boyutlandırma
        tk.Label(settings_grid, text="📐 Resim Boyutlandırma:", 
                font=("Arial", 10), bg=self.colors['white'], fg=self.colors['gray_700']).grid(row=5, column=0, sticky=tk.W, pady=5)
        
        self.resize_option = ttk.Combobox(settings_grid, values=[
            "Orijinal boyut korunsun",
            "Maksimum genişlik (px)",
            "Maksimum yükseklik (px)",
            "Yüzde olarak küçült",
            "Sabit boyut (px)"
        ], width=25, font=("Arial", 9))
        self.resize_option.set("Orijinal boyut korunsun")
        self.resize_option.grid(row=5, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Boyut değeri
        tk.Label(settings_grid, text="📏 Boyut Değeri:", 
                font=("Arial", 10), bg=self.colors['white'], fg=self.colors['gray_700']).grid(row=6, column=0, sticky=tk.W, pady=5)
        
        self.resize_value = tk.StringVar(value="800")
        resize_spinbox = tk.Spinbox(settings_grid, from_=50, to=4000, textvariable=self.resize_value, 
                                   width=10, font=("Arial", 9), bg=self.colors['gray_100'], relief="flat", bd=5)
        resize_spinbox.grid(row=6, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Checkbox'lar için ayrı frame
        checkbox_frame = tk.Frame(content_frame, bg=self.colors['white'])
        checkbox_frame.pack(fill=tk.X, pady=10)
        
        # Alt klasör oluştur
        self.create_subfolders = tk.BooleanVar(value=True)
        subfolder_check = tk.Checkbutton(checkbox_frame, text="📁 Her PDF için ayrı klasör oluştur", 
                                        variable=self.create_subfolders, bg=self.colors['white'], 
                                        fg=self.colors['gray_700'], font=("Arial", 9),
                                        selectcolor=self.colors['primary'])
        subfolder_check.pack(anchor=tk.W, pady=2)
        
        # İşlem sonrası klasör aç
        self.open_folder_after = tk.BooleanVar(value=False)
        open_folder_check = tk.Checkbutton(checkbox_frame, text="🔓 İşlem sonrası klasörü aç", 
                                          variable=self.open_folder_after, bg=self.colors['white'], 
                                          fg=self.colors['gray_700'], font=("Arial", 9),
                                          selectcolor=self.colors['primary'])
        open_folder_check.pack(anchor=tk.W, pady=2)
    
    def create_progress_section(self, parent):
        """İlerleme bölümü"""
        progress_frame = tk.Frame(parent, bg=self.colors['white'], relief="flat", bd=1)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Başlık
        title_frame = tk.Frame(progress_frame, bg=self.colors['gray_100'])
        title_frame.pack(fill=tk.X)
        
        tk.Label(title_frame, text="📊 İşlem Durumu", 
                font=("Arial", 12, "bold"), 
                bg=self.colors['gray_100'], fg=self.colors['gray_800']).pack(anchor=tk.W, padx=15, pady=10)
        
        # İçerik
        content_frame = tk.Frame(progress_frame, bg=self.colors['white'])
        content_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Progress bar
        self.progress = ttk.Progressbar(content_frame, orient="horizontal", mode="determinate", 
                                       style="Animated.Horizontal.TProgressbar")
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Progress label
        self.progress_label = tk.Label(content_frame, text="Hazır", 
                                      font=("Arial", 10), 
                                      bg=self.colors['white'], fg=self.colors['gray_600'])
        self.progress_label.pack()
    
    def create_buttons_section(self, parent):
        """Butonlar bölümü"""
        button_frame = tk.Frame(parent, bg=self.colors['light'])
        button_frame.pack(pady=15)
        
        # Ana butonlar
        main_buttons_frame = tk.Frame(button_frame, bg=self.colors['light'])
        main_buttons_frame.pack()
        
        self.extract_button = ModernButton(main_buttons_frame, text="🚀 Resimleri Çıkar", 
                                          command=self.start_extraction,
                                          bg=self.colors['success'], fg=self.colors['white'],
                                          font=("Arial", 12, "bold"), padx=25, pady=12)
        self.extract_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ModernButton(main_buttons_frame, text="❌ İptal", 
                                         command=self.cancel_extraction,
                                         bg=self.colors['danger'], fg=self.colors['white'],
                                         font=("Arial", 11), padx=20, pady=10, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        # İkincil butonlar
        secondary_buttons_frame = tk.Frame(button_frame, bg=self.colors['light'])
        secondary_buttons_frame.pack(pady=10)
        
        ModernButton(secondary_buttons_frame, text="👁️ Önizleme", command=self.show_preview,
                    bg=self.colors['info'], fg=self.colors['white'],
                    font=("Arial", 10), padx=15, pady=8).pack(side=tk.LEFT, padx=3)
        
        ModernButton(secondary_buttons_frame, text="📈 İstatistik", command=self.show_statistics,
                    bg=self.colors['warning'], fg=self.colors['white'],
                    font=("Arial", 10), padx=15, pady=8).pack(side=tk.LEFT, padx=3)
        
        ModernButton(secondary_buttons_frame, text="⚙️ Ayarlar", command=self.show_settings,
                    bg=self.colors['secondary'], fg=self.colors['white'],
                    font=("Arial", 10), padx=15, pady=8).pack(side=tk.LEFT, padx=3)
        
        ModernButton(secondary_buttons_frame, text="🚪 Çıkış", command=self.root.quit,
                    bg=self.colors['danger'], fg=self.colors['white'],
                    font=("Arial", 10), padx=15, pady=8).pack(side=tk.LEFT, padx=3)
    
    def create_status_bar(self):
        """Durum çubuğu"""
        self.status_var = tk.StringVar()
        self.status_var.set("Hazır")
        
        status_bar = tk.Frame(self.root, bg=self.colors['gray_200'], height=25)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)
        
        status_label = tk.Label(status_bar, textvariable=self.status_var, 
                               font=("Arial", 9), 
                               bg=self.colors['gray_200'], fg=self.colors['gray_700'],
                               anchor=tk.W)
        status_label.pack(fill=tk.X, padx=10, pady=5)
    
    def load_history(self):
        """İşlem geçmişini yükler"""
        self.history_file = os.path.join(os.path.expanduser("~"), ".pdf_extractor_history.txt")
        self.history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = [line.strip() for line in f.readlines() if line.strip()]
            except:
                self.history = []
    
    def save_history(self, pdf_path):
        """İşlem geçmişini kaydeder"""
        if pdf_path not in self.history:
            self.history.insert(0, pdf_path)
            self.history = self.history[:10]  # Son 10 dosyayı tut
            
            try:
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    for path in self.history:
                        f.write(path + '\n')
            except:
                pass
    
    def load_settings(self):
        """Kullanıcı ayarlarını yükler"""
        self.settings_file = os.path.join(os.path.expanduser("~"), ".pdf_extractor_settings.json")
        self.settings = {
            "theme": "light",
            "output_format": "Orijinal format korunsun",
            "jpeg_quality": "95",
            "resize_option": "Orijinal boyut korunsun",
            "resize_value": "800",
            "min_size": "10",
            "allowed_formats": "jpeg,png,gif,bmp",
            "create_subfolders": True,
            "open_folder_after": False
        }
        
        if os.path.exists(self.settings_file):
            try:
                import json
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
            except:
                pass
    
    def save_settings(self):
        """Kullanıcı ayarlarını kaydeder"""
        try:
            import json
            current_settings = {
                "theme": self.current_theme,
                "output_format": self.output_format.get(),
                "jpeg_quality": self.jpeg_quality.get(),
                "resize_option": self.resize_option.get(),
                "resize_value": self.resize_value.get(),
                "min_size": self.min_size_var.get(),
                "allowed_formats": self.format_var.get(),
                "create_subfolders": self.create_subfolders.get(),
                "open_folder_after": self.open_folder_after.get()
            }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(current_settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata: {e}")
    
    def apply_theme(self, theme):
        """Temayı uygular"""
        self.current_theme = theme
        
        if theme == "dark":
            bg_color = "#2C2C2C"
            fg_color = "#FFFFFF"
            button_bg = "#404040"
            entry_bg = "#404040"
            entry_fg = "#FFFFFF"
        else:  # light theme
            bg_color = "#f5f5f5"
            fg_color = "#000000"
            button_bg = "#2196F3"
            entry_bg = "#FFFFFF"
            entry_fg = "#000000"
        
        # Ana pencere
        self.root.configure(bg=bg_color)
        
        # Tüm widget'ları güncelle
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=bg_color)
            elif isinstance(widget, tk.Label):
                widget.configure(bg=bg_color, fg=fg_color)
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=entry_bg, fg=entry_fg)
            elif isinstance(widget, tk.Button):
                widget.configure(bg=button_bg, fg=fg_color)
    
    def show_settings(self):
        """Ayarlar penceresini gösterir"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Uygulama Ayarları")
        settings_window.geometry("450x550")
        settings_window.configure(bg=self.colors['light'])
        
        # Başlık
        header_frame = tk.Frame(settings_window, bg=self.colors['primary'], height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="⚙️ Uygulama Ayarları", 
                font=("Arial", 16, "bold"), bg=self.colors['primary'], fg=self.colors['white']).pack(pady=15)
        
        # Ana içerik
        main_frame = tk.Frame(settings_window, bg=self.colors['light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Tema seçimi
        theme_section = tk.Frame(main_frame, bg=self.colors['white'], relief="flat", bd=1)
        theme_section.pack(fill=tk.X, pady=(0, 15))
        
        # Tema başlığı
        theme_title = tk.Frame(theme_section, bg=self.colors['gray_100'])
        theme_title.pack(fill=tk.X)
        tk.Label(theme_title, text="🎨 Tema Seçimi", 
                font=("Arial", 12, "bold"), bg=self.colors['gray_100'], fg=self.colors['gray_800']).pack(anchor=tk.W, padx=15, pady=10)
        
        # Tema seçenekleri
        theme_content = tk.Frame(theme_section, bg=self.colors['white'])
        theme_content.pack(fill=tk.X, padx=15, pady=15)
        
        theme_var = tk.StringVar(value=self.current_theme)
        tk.Radiobutton(theme_content, text="☀️ Açık Tema", variable=theme_var, value="light", 
                      font=("Arial", 10), bg=self.colors['white'], fg=self.colors['gray_700'],
                      selectcolor=self.colors['primary'], command=lambda: self.apply_theme("light")).pack(anchor=tk.W, pady=5)
        tk.Radiobutton(theme_content, text="🌙 Koyu Tema", variable=theme_var, value="dark", 
                      font=("Arial", 10), bg=self.colors['white'], fg=self.colors['gray_700'],
                      selectcolor=self.colors['primary'], command=lambda: self.apply_theme("dark")).pack(anchor=tk.W, pady=5)
        
        # Diğer ayarlar
        other_section = tk.Frame(main_frame, bg=self.colors['white'], relief="flat", bd=1)
        other_section.pack(fill=tk.X, pady=(0, 15))
        
        # Diğer ayarlar başlığı
        other_title = tk.Frame(other_section, bg=self.colors['gray_100'])
        other_title.pack(fill=tk.X)
        tk.Label(other_title, text="🔧 Diğer Ayarlar", 
                font=("Arial", 12, "bold"), bg=self.colors['gray_100'], fg=self.colors['gray_800']).pack(anchor=tk.W, padx=15, pady=10)
        
        # Diğer ayarlar içeriği
        other_content = tk.Frame(other_section, bg=self.colors['white'])
        other_content.pack(fill=tk.X, padx=15, pady=15)
        
        # Otomatik güncelleme kontrolü
        self.auto_update = tk.BooleanVar(value=True)
        tk.Checkbutton(other_content, text="🔄 Otomatik güncelleme kontrolü", 
                      variable=self.auto_update, font=("Arial", 10), bg=self.colors['white'], 
                      fg=self.colors['gray_700'], selectcolor=self.colors['primary']).pack(anchor=tk.W, pady=5)
        
        # Sistem tray
        self.system_tray = tk.BooleanVar(value=False)
        tk.Checkbutton(other_content, text="📱 Sistem tray'de çalıştır", 
                      variable=self.system_tray, font=("Arial", 10), bg=self.colors['white'], 
                      fg=self.colors['gray_700'], selectcolor=self.colors['primary']).pack(anchor=tk.W, pady=5)
        
        # Butonlar
        button_frame = tk.Frame(main_frame, bg=self.colors['light'])
        button_frame.pack(pady=20)
        
        def save_and_close():
            self.save_settings()
            settings_window.destroy()
        
        ModernButton(button_frame, text="💾 Kaydet", command=save_and_close,
                    bg=self.colors['success'], fg=self.colors['white'],
                    font=("Arial", 11), padx=25, pady=10).pack(side=tk.LEFT, padx=5)
        
        ModernButton(button_frame, text="❌ İptal", command=settings_window.destroy,
                    bg=self.colors['danger'], fg=self.colors['white'],
                    font=("Arial", 11), padx=25, pady=10).pack(side=tk.LEFT, padx=5)
    
    def show_history(self):
        """İşlem geçmişini gösterir"""
        if not self.history:
            messagebox.showinfo("Geçmiş", "Henüz işlenmiş dosya bulunmuyor.")
            return
        
        history_window = tk.Toplevel(self.root)
        history_window.title("🕒 İşlem Geçmişi")
        history_window.geometry("500x400")
        history_window.configure(bg=self.colors['light'])
        
        # Başlık
        header_frame = tk.Frame(history_window, bg=self.colors['primary'], height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🕒 Son İşlenen Dosyalar", 
                font=("Arial", 16, "bold"), bg=self.colors['primary'], fg=self.colors['white']).pack(pady=15)
        
        # Ana içerik
        main_frame = tk.Frame(history_window, bg=self.colors['light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Liste başlığı
        list_title = tk.Frame(main_frame, bg=self.colors['gray_100'])
        list_title.pack(fill=tk.X, pady=(0, 10))
        tk.Label(list_title, text="📄 Dosya Listesi", 
                font=("Arial", 12, "bold"), bg=self.colors['gray_100'], fg=self.colors['gray_800']).pack(anchor=tk.W, padx=15, pady=10)
        
        # Liste
        list_frame = tk.Frame(main_frame, bg=self.colors['white'], relief="flat", bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        listbox = tk.Listbox(list_frame, font=("Arial", 10), bg=self.colors['white'], 
                            fg=self.colors['gray_800'], selectmode=tk.SINGLE, 
                            selectbackground=self.colors['primary'], selectforeground=self.colors['white'],
                            relief="flat", bd=0, highlightthickness=1, highlightcolor=self.colors['gray_300'])
        listbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        for i, path in enumerate(self.history, 1):
            filename = os.path.basename(path)
            listbox.insert(tk.END, f"{i}. {filename}")
        
        # Butonlar
        button_frame = tk.Frame(main_frame, bg=self.colors['light'])
        button_frame.pack(pady=10)
        
        def select_from_history():
            selection = listbox.curselection()
            if selection:
                selected_path = self.history[selection[0]]
                self.pdf_path_entry.delete(0, tk.END)
                self.pdf_path_entry.insert(0, selected_path)
                history_window.destroy()
        
        ModernButton(button_frame, text="✅ Seç", command=select_from_history,
                    bg=self.colors['success'], fg=self.colors['white'],
                    font=("Arial", 11), padx=25, pady=10).pack(side=tk.LEFT, padx=5)
        
        ModernButton(button_frame, text="❌ Kapat", command=history_window.destroy,
                    bg=self.colors['danger'], fg=self.colors['white'],
                    font=("Arial", 11), padx=25, pady=10).pack(side=tk.LEFT, padx=5)
    
    def select_pdf(self):
        file_paths = filedialog.askopenfilenames(
            title="PDF Dosyaları Seçin",
            filetypes=[("PDF Dosyaları", "*.pdf"), ("Tüm Dosyalar", "*.*")]
        )
        if file_paths:
            # Birden fazla dosya seçildiyse, ilkini ana alana koy
            self.pdf_path_entry.delete(0, tk.END)
            self.pdf_path_entry.insert(0, file_paths[0])
            
            # Seçilen tüm dosyaları sakla
            self.selected_pdfs = file_paths
            
            # Varsayılan klasör adını ayarla
            if len(file_paths) == 1:
                default_folder = os.path.join(os.path.dirname(file_paths[0]), 
                                             os.path.splitext(os.path.basename(file_paths[0]))[0] + "_resimler")
            else:
                default_folder = os.path.join(os.path.dirname(file_paths[0]), "PDF_Resimler")
            
            self.folder_path_entry.delete(0, tk.END)
            self.folder_path_entry.insert(0, default_folder)
            
            # Seçilen dosya sayısını göster
            if len(file_paths) > 1:
                self.status_var.set(f"{len(file_paths)} PDF dosyası seçildi")
    
    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Resimlerin Kaydedileceği Klasörü Seçin")
        if folder_path:
            self.folder_path_entry.delete(0, tk.END)
            self.folder_path_entry.insert(0, folder_path)
    
    def batch_process(self):
        """Birden fazla PDF dosyasını batch olarak işler"""
        pdf_paths = filedialog.askopenfilenames(
            title="Birden Fazla PDF Dosyası Seçin",
            filetypes=[("PDF Dosyaları", "*.pdf"), ("Tüm Dosyalar", "*.*")]
        )
        if pdf_paths:
            output_folder = self.folder_path_entry.get()
            if not output_folder:
                messagebox.showerror("Hata", "Lütfen bir kayıt klasörü seçin!")
                return
            
            # Animasyonlu progress bar'ı başlat
            self.progress_bar.start_animation()
            self.progress["value"] = 0
            self.progress_label.config(text="İşleniyor...")
            self.status_var.set("Batch işlemi başlatılıyor...")
            self.root.update_idletasks()
            
            try:
                start_time = time.time()
                total_images = self.extract_multiple_pdfs(pdf_paths, output_folder)
                elapsed_time = time.time() - start_time
                
                if total_images > 0:
                    messagebox.showinfo(
                        "Başarılı",
                        f"{total_images} resim başarıyla çıkarıldı!\n\n"
                        f"Konum: {output_folder}\n"
                        f"Süre: {elapsed_time:.2f} saniye"
                    )
                    self.status_var.set(f"{total_images} resim başarıyla çıkarıldı")
                    self.progress_label.config(text="Tamamlandı")
                    
                    # İşlem sonrası klasör açma
                    if self.open_folder_after.get():
                        try:
                            os.startfile(output_folder)
                        except FileNotFoundError:
                            messagebox.showwarning("Uyarı", f"Klasör bulunamadı: {output_folder}")
                        except Exception as e:
                            messagebox.showerror("Hata", f"Klasör açılırken hata oluştu: {e}")
                else:
                    messagebox.showwarning(
                        "Uyarı",
                        "Seçilen PDF dosyalarında çıkarılacak resim bulunamadı!"
                    )
                    self.status_var.set("Resim bulunamadı")
            except Exception as e:
                messagebox.showerror("Hata", str(e))
                self.status_var.set(f"Hata: {str(e)}")
                self.progress_label.config(text="Hata oluştu")
            finally:
                # Animasyonu durdur
                self.progress_bar.stop_animation()
                self.progress["value"] = 100
                self.extract_button.config(state=tk.NORMAL)
                self.cancel_button.config(state=tk.DISABLED)
    
    def convert_image_format(self, image_bytes, original_ext, target_format):
        """Resim formatını dönüştürür"""
        if target_format == "Orijinal format korunsun":
            return image_bytes, original_ext
        
        try:
            # Bytes'ı PIL Image'e çevir
            img = Image.open(io.BytesIO(image_bytes))
            
            # Boyutlandırma işlemi
            resize_option = self.resize_option.get()
            resize_value = self.resize_value.get()
            img = self.resize_image(img, resize_option, resize_value)
            
            # RGB moduna çevir (JPEG için gerekli)
            if target_format in ["JPEG (.jpg)", "WebP (.webp)"] and img.mode in ['RGBA', 'LA', 'P']:
                # Şeffaflık varsa beyaz arka plan ekle
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])  # Alpha kanalını maske olarak kullan
                    img = background
                else:
                    img = img.convert('RGB')
            
            # Yeni format için bytes buffer oluştur
            output_buffer = io.BytesIO()
            
            # Format seçeneklerini ayarla
            if target_format == "JPEG (.jpg)":
                img.save(output_buffer, format='JPEG', quality=int(self.jpeg_quality.get()), optimize=True)
                new_ext = "jpg"
            elif target_format == "PNG (.png)":
                img.save(output_buffer, format='PNG', optimize=True)
                new_ext = "png"
            elif target_format == "BMP (.bmp)":
                img.save(output_buffer, format='BMP')
                new_ext = "bmp"
            elif target_format == "TIFF (.tiff)":
                img.save(output_buffer, format='TIFF', compression='tiff_lzw')
                new_ext = "tiff"
            elif target_format == "WebP (.webp)":
                img.save(output_buffer, format='WebP', quality=int(self.jpeg_quality.get()), method=6)
                new_ext = "webp"
            else:
                return image_bytes, original_ext
            
            return output_buffer.getvalue(), new_ext
            
        except Exception as e:
            print(f"Format dönüştürme hatası: {e}")
            return image_bytes, original_ext
    
    def resize_image(self, img, resize_option, resize_value):
        """Resmi boyutlandırır"""
        if resize_option == "Orijinal boyut korunsun":
            return img
        
        try:
            original_width, original_height = img.size
            
            if resize_option == "Maksimum genişlik (px)":
                max_width = int(resize_value)
                if original_width <= max_width:
                    return img
                ratio = max_width / original_width
                new_width = max_width
                new_height = int(original_height * ratio)
                
            elif resize_option == "Maksimum yükseklik (px)":
                max_height = int(resize_value)
                if original_height <= max_height:
                    return img
                ratio = max_height / original_height
                new_height = max_height
                new_width = int(original_width * ratio)
                
            elif resize_option == "Yüzde olarak küçült":
                percentage = int(resize_value) / 100
                new_width = int(original_width * percentage)
                new_height = int(original_height * percentage)
                
            elif resize_option == "Sabit boyut (px)":
                new_width = int(resize_value)
                new_height = int(resize_value)
                
            else:
                return img
            
            # Boyutlandırma işlemi
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            return resized_img
            
        except Exception as e:
            print(f"Boyutlandırma hatası: {e}")
            return img
    
    def extract_images(self, pdf_path, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        self.processed_images = set()  # Her çalıştırmada sıfırla
        total_images = 0
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # Ayarları al
        min_size_kb = float(self.min_size_var.get())
        allowed_formats = [f.strip().lower() for f in self.format_var.get().split(',')]
        
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            # Önce tüm resimleri ve hangi sayfada olduklarını bul
            image_map = defaultdict(list)
            for page_no in range(total_pages):
                page = doc[page_no]
                for img in page.get_images(full=True):
                    xref = img[0]
                    if xref not in self.processed_images:
                        self.processed_images.add(xref)
                        image_map[page_no].append((xref, img))
            
            # Resimleri çıkar ve kaydet
            global_img_num = 1
            for page_no, images in image_map.items():
                for img_index, (xref, img) in enumerate(images, start=1):
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"].lower()
                    
                    # Format kontrolü
                    if image_ext not in allowed_formats:
                        continue
                    
                    # Boyut kontrolü
                    image_size_kb = len(image_bytes) / 1024
                    if image_size_kb < min_size_kb:
                        continue
                    
                    # Format dönüştürme
                    target_format = self.output_format.get()
                    converted_bytes, final_ext = self.convert_image_format(image_bytes, image_ext, target_format)
                    
                    # Format değişikliği bilgisi
                    if target_format != "Orijinal format korunsun" and final_ext != image_ext:
                        self.status_var.set(f"Format dönüştürülüyor: {image_ext} → {final_ext}")
                        self.root.update_idletasks()
                    
                    # Resim adını formatla
                    img_name = self.name_format.get().format(
                        page=page_no+1,
                        img=img_index,
                        num=global_img_num,
                        ext=final_ext,
                        pdfname=pdf_name
                    )
                    
                    image_path = os.path.join(output_folder, img_name)
                    
                    with open(image_path, "wb") as f:
                        f.write(converted_bytes)
                    
                    # Çıkarılan resmi listeye ekle
                    self.extracted_images.append((image_path, img_name))
                    
                    total_images += 1
                    global_img_num += 1
                
                # İlerlemeyi güncelle
                progress = (page_no + 1) / total_pages * 100
                self.progress["value"] = progress
                self.progress_label.config(
                    text=f"Sayfa {page_no+1}/{total_pages} - {total_images} resim çıkarıldı"
                )
                self.status_var.set(f"İşleniyor... Sayfa {page_no+1}/{total_pages}")
                self.root.update_idletasks()
                
                # İptal kontrolü
                if self.cancel_operation:
                    self.status_var.set("İşlem iptal edildi")
                    return total_images
            
            doc.close()
            return total_images
        
        except Exception as e:
            if 'doc' in locals():
                doc.close()
            raise Exception(f"PDF işlenirken hata: {str(e)}")
    
    def extract_multiple_pdfs(self, pdf_paths, output_folder):
        """Birden fazla PDF dosyasından resim çıkarır"""
        total_images = 0
        total_pdfs = len(pdf_paths)
        
        for i, pdf_path in enumerate(pdf_paths):
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            # Alt klasör oluştur
            if self.create_subfolders.get():
                pdf_output_folder = os.path.join(output_folder, pdf_name)
            else:
                pdf_output_folder = output_folder
            
            self.status_var.set(f"İşleniyor: {pdf_name} ({i+1}/{total_pdfs})")
            self.root.update_idletasks()
            
            try:
                images_count = self.extract_images(pdf_path, pdf_output_folder)
                total_images += images_count
                
                # Genel ilerleme
                overall_progress = (i + 1) / total_pdfs * 100
                self.progress["value"] = overall_progress
                self.progress_label.config(
                    text=f"PDF {i+1}/{total_pdfs} - Toplam {total_images} resim"
                )
                
            except Exception as e:
                messagebox.showwarning(f"Uyarı - {pdf_name}", str(e))
                continue
        
        return total_images
    
    def show_preview(self):
        """Çıkarılan resimlerin önizlemesini gösterir"""
        if not self.extracted_images:
            messagebox.showinfo("Önizleme", "Henüz resim çıkarılmadı!")
            return
        
        preview_window = ResimOnizleme(self.root)
        for image_path, image_name in self.extracted_images:
            preview_window.resim_ekle(image_path, image_name)
    
    def show_statistics(self):
        """Çıkarılan resimlerin istatistiklerini gösterir"""
        if not self.extracted_images:
            messagebox.showinfo("İstatistik", "Henüz resim çıkarılmadı veya çıkarılan resim yok.")
            return
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Çıkarılan Resim İstatistikleri")
        stats_window.geometry("400x500")
        stats_window.configure(bg=self.colors['light'])
        
        # Başlık
        header_frame = tk.Frame(stats_window, bg=self.colors['primary'], height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📊 Çıkarılan Resim İstatistikleri", 
                font=("Arial", 16, "bold"), bg=self.colors['primary'], fg=self.colors['white']).pack(pady=15)
        
        # Ana içerik
        main_frame = tk.Frame(stats_window, bg=self.colors['light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # İstatistik bilgileri
        total_images = len(self.extracted_images)
        total_size_kb = sum(os.path.getsize(img_path) / 1024 for img_path, _ in self.extracted_images)
        
        # Genel istatistikler
        general_section = tk.Frame(main_frame, bg=self.colors['white'], relief="flat", bd=1)
        general_section.pack(fill=tk.X, pady=(0, 15))
        
        # Genel başlık
        general_title = tk.Frame(general_section, bg=self.colors['gray_100'])
        general_title.pack(fill=tk.X)
        tk.Label(general_title, text="📈 Genel İstatistikler", 
                font=("Arial", 12, "bold"), bg=self.colors['gray_100'], fg=self.colors['gray_800']).pack(anchor=tk.W, padx=15, pady=10)
        
        # Genel içerik
        general_content = tk.Frame(general_section, bg=self.colors['white'])
        general_content.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(general_content, text=f"🖼️ Toplam Çıkarılan Resim Sayısı: {total_images}", 
                font=("Arial", 11), bg=self.colors['white'], fg=self.colors['gray_700']).pack(anchor=tk.W, pady=5)
        tk.Label(general_content, text=f"💾 Toplam Çıkarılan Resim Boyutu: {total_size_kb:.2f} KB", 
                font=("Arial", 11), bg=self.colors['white'], fg=self.colors['gray_700']).pack(anchor=tk.W, pady=5)
        
        # Resim formatlarına göre dağılım
        format_stats = defaultdict(int)
        for _, image_name in self.extracted_images:
            ext = os.path.splitext(image_name)[1].lower()
            if ext in format_stats:
                format_stats[ext] += 1
            else:
                format_stats[ext] = 1
        
        # Format dağılımı
        format_section = tk.Frame(main_frame, bg=self.colors['white'], relief="flat", bd=1)
        format_section.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Format başlık
        format_title = tk.Frame(format_section, bg=self.colors['gray_100'])
        format_title.pack(fill=tk.X)
        tk.Label(format_title, text="📋 Resim Formatlarına Göre Dağılım", 
                font=("Arial", 12, "bold"), bg=self.colors['gray_100'], fg=self.colors['gray_800']).pack(anchor=tk.W, padx=15, pady=10)
        
        # Format içerik
        format_content = tk.Frame(format_section, bg=self.colors['white'])
        format_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        for ext, count in format_stats.items():
            percentage = (count / total_images) * 100
            tk.Label(format_content, text=f"📄 {ext}: {count} adet ({percentage:.1f}%)", 
                    font=("Arial", 10), bg=self.colors['white'], fg=self.colors['gray_600']).pack(anchor=tk.W, pady=3)
        
        # Butonlar
        button_frame = tk.Frame(main_frame, bg=self.colors['light'])
        button_frame.pack(pady=10)
        
        ModernButton(button_frame, text="❌ Kapat", command=stats_window.destroy,
                    bg=self.colors['danger'], fg=self.colors['white'],
                    font=("Arial", 11), padx=25, pady=10).pack()
    
    def cancel_extraction(self):
        """İşlemi iptal eder"""
        self.cancel_operation = True
        self.status_var.set("İşlem iptal ediliyor...")
        self.cancel_button.config(state=tk.DISABLED)
        # Animasyonu durdur
        self.progress_bar.stop_animation()
    
    def start_extraction(self):
        pdf_path = self.pdf_path_entry.get()
        output_folder = self.folder_path_entry.get()
        
        if not pdf_path:
            messagebox.showerror("Hata", "Lütfen bir PDF dosyası seçin!")
            return
        
        if not output_folder:
            messagebox.showerror("Hata", "Lütfen bir kayıt klasörü seçin!")
            return
        
        # Animasyonlu progress bar'ı başlat
        self.progress_bar.start_animation()
        self.progress["value"] = 0
        self.progress_label.config(text="Başlatılıyor...")
        self.status_var.set("İşlem başlatılıyor...")
        self.root.update_idletasks()
        
        # Buton durumlarını güncelle
        self.extract_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.cancel_operation = False
        
        try:
            start_time = time.time()
            
            # Çoklu dosya işleme
            if hasattr(self, 'selected_pdfs') and len(self.selected_pdfs) > 1:
                image_count = self.extract_multiple_pdfs(self.selected_pdfs, output_folder)
                # Geçmişe kaydet
                for pdf_path in self.selected_pdfs:
                    self.save_history(pdf_path)
            else:
                image_count = self.extract_images(pdf_path, output_folder)
                # Geçmişe kaydet
                self.save_history(pdf_path)
            
            elapsed_time = time.time() - start_time
            
            if image_count > 0:
                messagebox.showinfo(
                    "Başarılı",
                    f"{image_count} resim başarıyla çıkarıldı!\n\n"
                    f"Konum: {output_folder}\n"
                    f"Süre: {elapsed_time:.2f} saniye"
                )
                self.status_var.set(f"{image_count} resim başarıyla çıkarıldı")
                self.progress_label.config(text="Tamamlandı")
                
                # İşlem sonrası klasör açma
                if self.open_folder_after.get():
                    try:
                        os.startfile(output_folder)
                    except FileNotFoundError:
                        messagebox.showwarning("Uyarı", f"Klasör bulunamadı: {output_folder}")
                    except Exception as e:
                        messagebox.showerror("Hata", f"Klasör açılırken hata oluştu: {e}")
            else:
                messagebox.showwarning(
                    "Uyarı",
                    "PDF dosyasında çıkarılacak resim bulunamadı!"
                )
                self.status_var.set("Resim bulunamadı")
        
        except Exception as e:
            messagebox.showerror("Hata", str(e))
            self.status_var.set(f"Hata: {str(e)}")
            self.progress_label.config(text="Hata oluştu")
        
        # Animasyonu durdur
        self.progress_bar.stop_animation()
        self.progress["value"] = 100
        # İşlem tamamlandığında butonları tekrar etkinleştir
        self.extract_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = PDFResimCikarici()
    app.root.mainloop()
