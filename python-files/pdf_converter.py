import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import os
import threading
from pathlib import Path
import io

class PDFConverterApp:
    def __init__(self):
        # Hlavní okno
        self.root = TkinterDnD.Tk()
        self.root.title("PDF na obrázek - Converter")
        self.root.geometry("850x850")
        self.root.configure(bg="#f8fafc")
        
        # Nastav minimální šířku okna
        self.root.minsize(750, 600)
        
        # Proměnné
        self.pdf_doc = None
        self.current_page = 0
        self.total_pages = 0
        self.pdf_path = ""
        self.dpi_var = tk.IntVar(value=150)
        self.preview_photo = None
        
        # Nové proměnné pro formát
        self.format_var = tk.StringVar(value="PNG")
        self.jpeg_quality_var = tk.IntVar(value=95)
        self.png_transparent_var = tk.BooleanVar(value=False)
        self.detailed_naming_var = tk.BooleanVar(value=True)
        
        # Status label pro zprávy
        self.status_message = ""
        
        self.setup_ui()
        self.setup_drag_drop()
        
        # Bind resize event pro aktualizaci wraplength
        self.root.bind('<Configure>', lambda e: self.root.after_idle(self.update_wraplength))
        
    def update_wraplength(self):
        """Aktualizuj wraplength podle šířky okna"""
        try:
            window_width = self.root.winfo_width()
            # Očekávaná šířka pro text = okno - paddingy - marginy
            text_width = max(400, window_width - 150)  # Minimum 400px, jinak okno - 150px
            self.file_info_label.config(wraplength=text_width)
        except:
            pass  # Ignoruj chyby při resize
        
    def setup_ui(self):
        # Drop zone - fixed nahoře se stejným nastavením jako main_frame
        self.drop_frame = tk.Frame(self.root, bg="#ffffff", relief=tk.FLAT, bd=0)
        self.drop_frame.pack(fill=tk.X, padx=40, pady=(25, 15), ipady=25)
        self.drop_frame.config(highlightbackground="#e2e8f0", highlightthickness=2)
        
        drop_label = tk.Label(self.drop_frame, text="Přetáhni PDF soubor sem nebo klikni pro výběr", 
                             font=("Segoe UI", 14), bg="#ffffff", fg="#64748b", cursor="hand2")
        drop_label.pack(expand=True)
        drop_label.bind("<Button-1>", self.select_file)
        
        # Scrollable container pro zbytek
        canvas = tk.Canvas(self.root, bg="#f8fafc", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#f8fafc")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Hlavní frame - přizpůsobuje se šířce okna
        main_frame = tk.Frame(self.scrollable_frame, bg="#f8fafc")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 25))
        
        # Info o souboru - přizpůsobuje se šířce
        self.file_info_frame = tk.Frame(main_frame, bg="#f0fdf4", relief=tk.FLAT, bd=0)
        self.file_info_frame.config(highlightbackground="#bbf7d0", highlightthickness=1)
        self.file_info_label = tk.Label(self.file_info_frame, text="", font=("Segoe UI", 11), 
                                       bg="#f0fdf4", fg="#166534", wraplength=400)
        self.file_info_label.pack(padx=15, pady=8, fill=tk.X)
        self.file_info_frame.pack(fill=tk.X, pady=(15, 10))
        
        # Status řádek - přizpůsobuje se šířce
        self.status_frame = tk.Frame(main_frame, bg="#eff6ff", relief=tk.FLAT, bd=0)
        self.status_frame.config(highlightbackground="#93c5fd", highlightthickness=1)
        self.status_label = tk.Label(self.status_frame, text="Připraveno k exportu...", 
                                    font=("Segoe UI", 10), bg="#eff6ff", fg="#1d4ed8")
        self.status_label.pack(padx=15, pady=6)
        self.status_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Ovládání - přizpůsobuje se šířce
        self.controls_frame = tk.LabelFrame(main_frame, text="Nastavení exportu", 
                                           font=("Segoe UI", 13, "bold"), bg="#f8fafc", fg="#1e293b",
                                           relief=tk.FLAT, bd=0, padx=20, pady=15)
        self.controls_frame.config(highlightbackground="#e2e8f0", highlightthickness=1)
        self.controls_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Výběr formátu
        format_frame = tk.Frame(self.controls_frame, bg="#f8fafc")
        format_frame.pack(fill=tk.X, padx=0, pady=(0, 12))
        
        tk.Label(format_frame, text="Formát výstupu:", font=("Segoe UI", 12, "bold"), 
                bg="#f8fafc", fg="#374151").pack(side=tk.LEFT)
        
        self.png_radio = tk.Radiobutton(format_frame, text="PNG", variable=self.format_var, 
                                       value="PNG", bg="#f8fafc", font=("Segoe UI", 11),
                                       command=self.on_format_change, fg="#374151")
        self.png_radio.pack(side=tk.LEFT, padx=(20, 15))
        
        self.jpeg_radio = tk.Radiobutton(format_frame, text="JPEG", variable=self.format_var, 
                                        value="JPEG", bg="#f8fafc", font=("Segoe UI", 11),
                                        command=self.on_format_change, fg="#374151")
        self.jpeg_radio.pack(side=tk.LEFT, padx=5)
        
        # DPI slider
        dpi_frame = tk.Frame(self.controls_frame, bg="#f8fafc")
        dpi_frame.pack(fill=tk.X, padx=0, pady=(0, 12))
        
        tk.Label(dpi_frame, text="Kvalita (DPI):", font=("Segoe UI", 12, "bold"), 
                bg="#f8fafc", fg="#374151").pack(side=tk.LEFT)
        
        self.dpi_scale = tk.Scale(dpi_frame, from_=72, to=300, orient=tk.HORIZONTAL, 
                                 variable=self.dpi_var, command=self.update_calculations,
                                 bg="#f8fafc", highlightthickness=0, troughcolor="#e2e8f0",
                                 font=("Segoe UI", 10), length=300)
        self.dpi_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(20, 15))
        
        self.dpi_label = tk.Label(dpi_frame, text="150", font=("Segoe UI", 11, "bold"), 
                                 bg="#3b82f6", fg="white", padx=15, pady=6)
        self.dpi_label.pack(side=tk.RIGHT)
        
        # JPEG nastavení
        self.jpeg_frame = tk.Frame(self.controls_frame, bg="#f8fafc")
        self.jpeg_frame.pack(fill=tk.X, padx=0, pady=(0, 12))
        
        tk.Label(self.jpeg_frame, text="JPEG kvalita:", font=("Segoe UI", 12, "bold"), 
                bg="#f8fafc", fg="#374151").pack(side=tk.LEFT)
        
        self.jpeg_scale = tk.Scale(self.jpeg_frame, from_=1, to=100, orient=tk.HORIZONTAL, 
                                  variable=self.jpeg_quality_var, command=self.update_calculations,
                                  bg="#f8fafc", highlightthickness=0, troughcolor="#e2e8f0",
                                  font=("Segoe UI", 10), length=300)
        self.jpeg_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(20, 15))
        
        self.jpeg_label = tk.Label(self.jpeg_frame, text="95%", font=("Segoe UI", 11, "bold"), 
                                  bg="#f97316", fg="white", padx=15, pady=6)
        self.jpeg_label.pack(side=tk.RIGHT)
        
        # PNG nastavení
        self.png_frame = tk.Frame(self.controls_frame, bg="#f8fafc")
        self.png_frame.pack(fill=tk.X, padx=0, pady=(0, 12))
        
        tk.Label(self.png_frame, text="PNG možnosti:", font=("Segoe UI", 12, "bold"), 
                bg="#f8fafc", fg="#374151").pack(side=tk.LEFT)
        
        self.transparent_check = tk.Checkbutton(self.png_frame, text="Transparentní pozadí", 
                                               variable=self.png_transparent_var, bg="#f8fafc",
                                               font=("Segoe UI", 11), command=self.update_calculations,
                                               fg="#374151")
        self.transparent_check.pack(side=tk.LEFT, padx=(30, 0))
        
        # Pojmenování souborů
        naming_frame = tk.Frame(self.controls_frame, bg="#f8fafc")
        naming_frame.pack(fill=tk.X, padx=0, pady=(0, 15))
        
        tk.Label(naming_frame, text="Pojmenování:", font=("Segoe UI", 12, "bold"), 
                bg="#f8fafc", fg="#374151").pack(side=tk.LEFT)
        
        self.detailed_naming_check = tk.Checkbutton(naming_frame, text="Detailní pojmenování (s DPI a kvalitou)", 
                                                   variable=self.detailed_naming_var, bg="#f8fafc",
                                                   font=("Segoe UI", 11), fg="#374151")
        self.detailed_naming_check.pack(side=tk.LEFT, padx=(30, 0))
        
        # Info grid - kompaktnější
        info_frame = tk.Frame(self.controls_frame, bg="#f8fafc")
        info_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Rozlišení
        res_frame = tk.Frame(info_frame, bg="#ffffff", relief=tk.FLAT, bd=0)
        res_frame.config(highlightbackground="#e2e8f0", highlightthickness=1)
        res_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(res_frame, text="Rozlišení výstupu", font=("Segoe UI", 10), 
                bg="#ffffff", fg="#64748b").pack(pady=(10, 4))
        self.resolution_label = tk.Label(res_frame, text="-", font=("Segoe UI", 14, "bold"), 
                                        bg="#ffffff", fg="#1e293b")
        self.resolution_label.pack(pady=(0, 10))
        
        # Velikost
        size_frame = tk.Frame(info_frame, bg="#ffffff", relief=tk.FLAT, bd=0)
        size_frame.config(highlightbackground="#e2e8f0", highlightthickness=1)
        size_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(size_frame, text="Přibližná velikost", font=("Segoe UI", 10), 
                bg="#ffffff", fg="#64748b").pack(pady=(10, 4))
        self.size_label = tk.Label(size_frame, text="-", font=("Segoe UI", 14, "bold"), 
                                  bg="#ffffff", fg="#1e293b")
        self.size_label.pack(pady=(0, 10))
        
        # Export tlačítka - přizpůsobují se šířce
        self.export_frame = tk.Frame(main_frame, bg="#f8fafc")
        self.export_frame.pack(fill=tk.X, pady=(15, 20))
        
        self.export_current_btn = tk.Button(self.export_frame, text="Uložit aktuální stránku", 
                                           state=tk.DISABLED, command=self.export_current_page,
                                           bg="#10b981", fg="white", font=("Segoe UI", 11, "bold"),
                                           relief=tk.FLAT, padx=25, pady=12)
        self.export_current_btn.pack(side=tk.LEFT, padx=8)
        
        self.export_all_btn = tk.Button(self.export_frame, text="Uložit všechny stránky", 
                                       state=tk.DISABLED, command=self.export_all_pages,
                                       bg="#ef4444", fg="white", font=("Segoe UI", 11, "bold"),
                                       relief=tk.FLAT, padx=25, pady=12)
        self.export_all_btn.pack(side=tk.LEFT, padx=8)
        
        # Náhled - přizpůsobuje se šířce a výšce
        self.preview_frame = tk.LabelFrame(main_frame, text="Náhled stránky", 
                                          font=("Segoe UI", 13, "bold"), bg="#f8fafc", fg="#1e293b",
                                          relief=tk.FLAT, bd=0, padx=15, pady=12)
        self.preview_frame.config(highlightbackground="#e2e8f0", highlightthickness=1)
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas pro náhled - přizpůsobuje se šířce
        canvas_frame = tk.Frame(self.preview_frame, bg="#ffffff")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, 8))
        canvas_frame.config(highlightbackground="#e2e8f0", highlightthickness=1)
        
        self.preview_canvas = tk.Label(canvas_frame, text="Náhled se zobrazí po načtení PDF", 
                                      font=("Segoe UI", 14), bg="#ffffff", fg="#94a3b8", 
                                      relief=tk.FLAT, bd=0)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Ovládání stránek
        page_frame = tk.Frame(self.preview_frame, bg="#f8fafc")
        page_frame.pack(pady=(0, 8))
        
        self.prev_btn = tk.Button(page_frame, text="◀ Předchozí", state=tk.DISABLED, 
                                 command=self.prev_page, bg="#94a3b8", fg="white",
                                 font=("Segoe UI", 10), relief=tk.FLAT, padx=15, pady=8)
        self.prev_btn.pack(side=tk.LEFT, padx=8)
        
        self.page_label = tk.Label(page_frame, text="Stránka - z -", font=("Segoe UI", 11, "bold"), 
                                  bg="#f8fafc", fg="#1e293b")
        self.page_label.pack(side=tk.LEFT, padx=20)
        
        self.next_btn = tk.Button(page_frame, text="Následující ▶", state=tk.DISABLED, 
                                 command=self.next_page, bg="#94a3b8", fg="white",
                                 font=("Segoe UI", 10), relief=tk.FLAT, padx=15, pady=8)
        self.next_btn.pack(side=tk.LEFT, padx=8)
        
        # Skryj kontroly na začátku
        self.file_info_frame.pack_forget()
        self.status_frame.pack_forget()
        self.controls_frame.pack_forget()
        self.export_frame.pack_forget()
        self.preview_frame.pack_forget()
        
        # Nastav počáteční stav formátových ovládání
        self.on_format_change()
        
    def setup_drag_drop(self):
        # Nastavení drag & drop pro hlavní okno a drop container
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Přidej drag & drop i na drop_frame
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)
        
    def on_format_change(self):
        """Aktualizuj UI podle vybraného formátu"""
        format_type = self.format_var.get()
        
        if format_type == "PNG":
            self.jpeg_frame.pack_forget()
            self.png_frame.pack(fill=tk.X, padx=0, pady=(0, 12))
        else:  # JPEG
            self.png_frame.pack_forget()
            self.jpeg_frame.pack(fill=tk.X, padx=0, pady=(0, 12))
        
        self.update_calculations()
        
    def handle_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = files[0]
            if file_path.lower().endswith('.pdf'):
                self.load_pdf(file_path)
            else:
                self.show_status("Prosím přetáhni pouze PDF soubor", "#ef4444")
    
    def select_file(self, event=None):
        file_path = filedialog.askopenfilename(
            title="Vyber PDF soubor",
            filetypes=[("PDF soubory", "*.pdf"), ("Všechny soubory", "*.*")]
        )
        if file_path:
            self.load_pdf(file_path)
    
    def load_pdf(self, file_path):
        try:
            # Načti PDF
            self.pdf_doc = fitz.open(file_path)
            self.total_pages = len(self.pdf_doc)
            self.current_page = 0
            self.pdf_path = file_path
            
            # Zobraz info o souboru
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            file_name = os.path.basename(file_path)
            
            self.file_info_label.config(
                text=f"{file_name} | Velikost: {file_size_mb:.2f} MB | Stránek: {self.total_pages}"
            )
            
            # Aktualizuj wraplength po načtení PDF
            self.root.after(100, self.update_wraplength)
            
            # Zobraz kontroly - export tlačítka přesunutá výše
            self.file_info_frame.pack(fill=tk.X, pady=(15, 10))
            self.status_frame.pack(fill=tk.X, pady=(0, 15))
            self.controls_frame.pack(fill=tk.X, pady=(0, 15))
            self.export_frame.pack(fill=tk.X, pady=(15, 20))
            self.preview_frame.pack(fill=tk.BOTH, expand=True)
            
            # Aktivuj tlačítka
            self.export_current_btn.config(state=tk.NORMAL, bg="#10b981")
            self.export_all_btn.config(state=tk.NORMAL, bg="#ef4444")
            self.update_page_controls()
            
            # Načti první stránku
            self.load_page_preview()
            self.update_calculations()
            
        except Exception as e:
            self.show_status(f"Chyba načítání PDF: {str(e)}", "#ef4444")
    
    def load_page_preview(self):
        if not self.pdf_doc:
            return
            
        try:
            page = self.pdf_doc[self.current_page]
            
            # Vytvoř náhled s menším rozlišením
            matrix = fitz.Matrix(1.5, 1.5)  # 108 DPI pro náhled
            pix = page.get_pixmap(matrix=matrix, alpha=False)  # Bez alpha pro náhled
            img_data = pix.tobytes("ppm")
            
            # Převeď na PIL Image
            img = Image.open(io.BytesIO(img_data))
            
            # Změň velikost pro náhled (max 500px)
            img.thumbnail((500, 500), Image.Resampling.LANCZOS)
            
            # Převeď na PhotoImage
            self.preview_photo = ImageTk.PhotoImage(img)
            self.preview_canvas.config(image=self.preview_photo, text="")
            
        except Exception as e:
            self.preview_canvas.config(image="", text=f"Chyba při načítání náhledu: {str(e)}")
    
    def update_calculations(self, event=None):
        if not self.pdf_doc:
            return
            
        dpi = self.dpi_var.get()
        format_type = self.format_var.get()
        
        self.dpi_label.config(text=str(dpi))
        
        if format_type == "JPEG":
            quality = self.jpeg_quality_var.get()
            self.jpeg_label.config(text=f"{quality}%")
        
        try:
            page = self.pdf_doc[self.current_page]
            
            # Vypočti rozměry při daném DPI
            matrix = fitz.Matrix(dpi / 72, dpi / 72)
            rect = page.rect
            width = int(rect.width * matrix.a)
            height = int(rect.height * matrix.d)
            
            # Odhad velikosti souboru podle formátu (opravené realistické hodnoty)
            pixel_count = width * height
            
            if format_type == "PNG":
                # PNG: RGB (3 bytes) nebo RGBA (4 bytes), s velmi efektivní kompresí
                bytes_per_pixel = 4 if self.png_transparent_var.get() else 3
                compression_ratio = 0.08  # PNG má mnohem lepší kompresi než jsem odhadoval
                estimated_bytes = pixel_count * bytes_per_pixel * compression_ratio
            else:  # JPEG
                # JPEG: kvalita ovlivňuje velikost - realističtější odhady
                quality = self.jpeg_quality_var.get()
                bytes_per_pixel = 3  # RGB
                # Kvalita 1-100: JPEG má velmi efektivní kompresi
                if quality >= 90:
                    compression_factor = 0.06  # Vysoká kvalita
                elif quality >= 70:
                    compression_factor = 0.04  # Střední kvalita  
                elif quality >= 50:
                    compression_factor = 0.03  # Nižší kvalita
                else:
                    compression_factor = 0.02  # Velmi nízká kvalita
                estimated_bytes = pixel_count * bytes_per_pixel * compression_factor
            
            estimated_mb = estimated_bytes / (1024 * 1024)
            
            self.resolution_label.config(text=f"{width} × {height}")
            
            # Barva podle velikosti
            if estimated_mb < 1:
                color = "#10b981"  # zelená
                size_text = f"~{estimated_mb:.1f} MB"
            elif estimated_mb < 5:
                color = "#f97316"  # oranžová
                size_text = f"~{estimated_mb:.1f} MB"
            else:
                color = "#ef4444"  # červená
                size_text = f"~{estimated_mb:.1f} MB"
            
            self.size_label.config(text=size_text, fg=color)
            
        except Exception as e:
            self.resolution_label.config(text="Chyba")
            self.size_label.config(text="Chyba")
    
    def update_page_controls(self):
        if not self.pdf_doc:
            return
            
        self.page_label.config(text=f"Stránka {self.current_page + 1} z {self.total_pages}")
        
        self.prev_btn.config(
            state=tk.NORMAL if self.current_page > 0 else tk.DISABLED,
            bg="#3b82f6" if self.current_page > 0 else "#94a3b8"
        )
        
        self.next_btn.config(
            state=tk.NORMAL if self.current_page < self.total_pages - 1 else tk.DISABLED,
            bg="#3b82f6" if self.current_page < self.total_pages - 1 else "#94a3b8"
        )
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_page_preview()
            self.update_page_controls()
            self.update_calculations()
    
    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.load_page_preview()
            self.update_page_controls()
            self.update_calculations()
    
    def export_page_to_format(self, page, output_path):
        """Export stránky do zvoleného formátu"""
        dpi = self.dpi_var.get()
        format_type = self.format_var.get()
        
        matrix = fitz.Matrix(dpi / 72, dpi / 72)
        
        if format_type == "PNG":
            # PNG s možností transparentního pozadí
            alpha = self.png_transparent_var.get()
            pix = page.get_pixmap(matrix=matrix, alpha=alpha)
            
            if alpha:
                # Transparentní PNG
                pix.save(str(output_path))
            else:
                # PNG s bílým pozadím
                img_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(img_data))
                # Přidej bílé pozadí
                white_bg = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    white_bg.paste(img, mask=img.split()[-1])  # Použij alpha kanál jako masku
                else:
                    white_bg = img
                white_bg.save(str(output_path), "PNG")
        
        else:  # JPEG
            # JPEG s nastavenou kvalitou
            quality = self.jpeg_quality_var.get()
            pix = page.get_pixmap(matrix=matrix, alpha=False)  # JPEG nepodporuje alpha
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            img.save(str(output_path), "JPEG", quality=quality, optimize=True)
    
    def get_filename(self, page_number, total_pages):
        """Vytvoř název souboru podle nastavení"""
        dpi = self.dpi_var.get()
        format_type = self.format_var.get()
        extension = "png" if format_type == "PNG" else "jpg"
        
        if self.detailed_naming_var.get():
            # Detailní pojmenování s DPI a kvalitou
            if format_type == "PNG" and self.png_transparent_var.get():
                return f"stranka_{page_number + 1:03d}_{dpi}dpi_transparent.{extension}"
            elif format_type == "JPEG":
                quality = self.jpeg_quality_var.get()
                return f"stranka_{page_number + 1:03d}_{dpi}dpi_q{quality}.{extension}"
            else:
                return f"stranka_{page_number + 1:03d}_{dpi}dpi.{extension}"
        else:
            # Jednoduché pojmenování podle originálu
            pdf_name = Path(self.pdf_path).stem
            if total_pages > 1:
                return f"{pdf_name}_stranka_{page_number + 1:03d}.{extension}"
            else:
                return f"{pdf_name}.{extension}"
    
    def show_status(self, message, color="#10b981"):
        """Zobraz status zprávu"""
        self.status_label.config(text=message, fg=color)
        self.root.update()
    
    def export_current_page(self):
        if not self.pdf_doc:
            return
            
        # Vytvoř výstupní složku vedle PDF
        output_dir = Path(self.pdf_path).parent / f"{Path(self.pdf_path).stem}_obrazky"
        output_dir.mkdir(exist_ok=True)
        
        try:
            self.export_current_btn.config(text="Ukládám...", state=tk.DISABLED)
            self.show_status("Ukládám stránku...", "#f97316")
            
            page = self.pdf_doc[self.current_page]
            
            # Název souboru
            filename = self.get_filename(self.current_page, self.total_pages)
            output_path = output_dir / filename
            
            # Export do zvoleného formátu
            self.export_page_to_format(page, output_path)
            
            self.show_status(f"Stránka uložena: {filename}", "#10b981")
            
        except Exception as e:
            self.show_status(f"Chyba: {str(e)}", "#ef4444")
        finally:
            self.export_current_btn.config(text="Uložit aktuální stránku", state=tk.NORMAL)
    
    def export_all_pages(self):
        if not self.pdf_doc:
            return
        
        # Vytvoř výstupní složku vedle PDF
        output_dir = Path(self.pdf_path).parent / f"{Path(self.pdf_path).stem}_obrazky"
        output_dir.mkdir(exist_ok=True)
        
        def export_thread():
            try:
                for i in range(self.total_pages):
                    # Aktualizuj UI
                    self.root.after(0, lambda i=i: self.export_all_btn.config(
                        text=f"Ukládám {i+1}/{self.total_pages}..."
                    ))
                    self.root.after(0, lambda i=i: self.show_status(
                        f"Ukládám stránku {i+1} z {self.total_pages}...", "#f97316"
                    ))
                    
                    page = self.pdf_doc[i]
                    
                    # Název souboru
                    filename = self.get_filename(i, self.total_pages)
                    output_path = output_dir / filename
                    
                    # Export do zvoleného formátu
                    self.export_page_to_format(page, output_path)
                
                # Hotovo
                self.root.after(0, lambda: self.show_status(
                    f"Všechny stránky ({self.total_pages}) uloženy do složky!", "#10b981"
                ))
                
            except Exception as e:
                self.root.after(0, lambda: self.show_status(
                    f"Chyba při exportu: {str(e)}", "#ef4444"
                ))
            finally:
                self.root.after(0, lambda: self.export_all_btn.config(
                    text="Uložit všechny stránky", state=tk.NORMAL
                ))
        
        self.export_all_btn.config(state=tk.DISABLED)
        threading.Thread(target=export_thread, daemon=True).start()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PDFConverterApp()
    app.run()
