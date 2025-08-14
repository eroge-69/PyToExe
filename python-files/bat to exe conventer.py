import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import subprocess
import tempfile
import base64
import sys

class BatToExeConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("BAT to EXE Converter v2.1")
        
        # Ekran boyutlarını al ve uygun boyut ayarla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Pencere boyutunu ekran boyutuna göre ayarla (maksimum 80% ekran)
        window_width = min(950, int(screen_width * 0.8))
        window_height = min(750, int(screen_height * 0.8))
        
        # Pencereyi ortala
        pos_x = (screen_width // 2) - (window_width // 2)
        pos_y = (screen_height // 2) - (window_height // 2)
        
        self.root.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
        self.root.configure(bg='#1e1e1e')
        self.root.minsize(800, 600)  # Minimum boyut
        
        # İkon ayarla
        try:
            self.root.iconbitmap(default="bat2exe.ico")
        except:
            pass
        
        self.bat_content = ""
        self.version = "2.1"
        self.setup_ui()
        
        # Başlangıçta kontrol et
        self.check_requirements()
    
    def check_requirements(self):
        """Gerekli programları kontrol et"""
        missing = []
        
        # PyInstaller kontrol
        try:
            result = subprocess.run(['pyinstaller', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                missing.append("PyInstaller")
        except FileNotFoundError:
            missing.append("PyInstaller")
        
        if missing:
            msg = f"Eksik gereksinimler bulundu:\n\n"
            for item in missing:
                msg += f"❌ {item}\n"
            msg += f"\nKurulum için terminalde şu komutu çalıştırın:\npip install pyinstaller\n\n"
            msg += "Kurulum tamamlandıktan sonra programı yeniden başlatın."
            
            messagebox.showwarning("Gereksinimler", msg)
            self.status_var.set("❌ Gereksinimler eksik - pip install pyinstaller")
        else:
            self.status_var.set("✅ Tüm gereksinimler mevcut")
    
    def setup_ui(self):
        # Ana scrollable canvas
        canvas = tk.Canvas(self.root, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1e1e1e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Ana container
        main_container = tk.Frame(scrollable_frame, bg='#1e1e1e')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header
        header_frame = tk.Frame(main_container, bg='#1e1e1e')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(
            header_frame, 
            text="🦇 BAT to EXE Converter", 
            font=("Segoe UI", 18, "bold"),
            bg='#1e1e1e', 
            fg='#00ff88'
        )
        title_label.pack()
        
        version_label = tk.Label(
            header_frame,
            text=f"Versiyon {self.version} • Batch dosyalarınızı executable'a çevirin",
            font=("Segoe UI", 10),
            bg='#1e1e1e',
            fg='#888888'
        )
        version_label.pack(pady=(5, 0))
        
        # Sürüm bilgileri butonu
        info_btn = tk.Button(
            header_frame,
            text="ℹ️ Hakkında",
            command=self.show_about,
            bg='#444444',
            fg='white',
            font=("Segoe UI", 8),
            relief='flat',
            cursor='hand2'
        )
        info_btn.pack(pady=(5, 0))
        
        # Dosya seçim bölümü
        file_section = tk.LabelFrame(
            main_container, 
            text=" 📁 BAT Dosyası Seçin ",
            bg='#1e1e1e', 
            fg='#ffffff',
            font=("Segoe UI", 10, "bold"),
            relief='groove',
            bd=2
        )
        file_section.pack(fill=tk.X, pady=(0, 10))
        
        file_inner = tk.Frame(file_section, bg='#1e1e1e')
        file_inner.pack(fill=tk.X, padx=10, pady=8)
        
        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(
            file_inner, 
            textvariable=self.file_path_var,
            bg='#2d2d2d', 
            fg='#ffffff', 
            font=("Consolas", 9),
            relief='flat',
            bd=5
        )
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        browse_btn = tk.Button(
            file_inner,
            text="📂 Gözat",
            command=self.browse_file,
            bg='#0078d4',
            fg='white',
            font=("Segoe UI", 9, "bold"),
            relief='flat',
            cursor='hand2',
            padx=15
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Kod editörü bölümü - Yüksekliği azalttık
        editor_section = tk.LabelFrame(
            main_container,
            text=" 📝 BAT Kod Editörü ",
            bg='#1e1e1e',
            fg='#ffffff',
            font=("Segoe UI", 10, "bold"),
            relief='groove',
            bd=2
        )
        editor_section.pack(fill=tk.X, pady=(0, 10))
        
        editor_inner = tk.Frame(editor_section, bg='#1e1e1e')
        editor_inner.pack(fill=tk.X, padx=10, pady=8)
        
        # Araç çubuğu
        toolbar = tk.Frame(editor_inner, bg='#1e1e1e')
        toolbar.pack(fill=tk.X, pady=(0, 8))
        
        sample_btn = tk.Button(
            toolbar,
            text="🔥 Örnek Kod",
            command=self.load_sample,
            bg='#ff6b35',
            fg='white',
            font=("Segoe UI", 8, "bold"),
            relief='flat',
            cursor='hand2'
        )
        sample_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        clear_btn = tk.Button(
            toolbar,
            text="🗑️ Temizle",
            command=self.clear_editor,
            bg='#dc3545',
            fg='white',
            font=("Segoe UI", 8, "bold"),
            relief='flat',
            cursor='hand2'
        )
        clear_btn.pack(side=tk.LEFT)
        
        # Editör - Sabit yükseklik
        self.text_editor = scrolledtext.ScrolledText(
            editor_inner,
            bg='#0d1117',
            fg='#c9d1d9',
            font=("Consolas", 10),
            insertbackground='#ffffff',
            selectbackground='#264f78',
            relief='flat',
            bd=5,
            wrap=tk.NONE,
            height=12  # Sabit yükseklik
        )
        self.text_editor.pack(fill=tk.X)
        
        # Seçenekler bölümü
        options_section = tk.LabelFrame(
            main_container,
            text=" ⚙️ EXE Seçenekleri ",
            bg='#1e1e1e',
            fg='#ffffff',
            font=("Segoe UI", 10, "bold"),
            relief='groove',
            bd=2
        )
        options_section.pack(fill=tk.X, pady=(0, 10))
        
        options_inner = tk.Frame(options_section, bg='#1e1e1e')
        options_inner.pack(fill=tk.X, padx=10, pady=8)
        
        # Üst satır - Checkboxlar
        top_options = tk.Frame(options_inner, bg='#1e1e1e')
        top_options.pack(fill=tk.X, pady=(0, 5))
        
        self.invisible_var = tk.BooleanVar()
        invisible_check = tk.Checkbutton(
            top_options,
            text="👻 Gizli çalışma (konsol gizli)",
            variable=self.invisible_var,
            bg='#1e1e1e',
            fg='#ffffff',
            selectcolor='#2d2d2d',
            font=("Segoe UI", 9),
            activebackground='#1e1e1e',
            activeforeground='#ffffff'
        )
        invisible_check.pack(side=tk.LEFT)
        
        self.admin_var = tk.BooleanVar()
        admin_check = tk.Checkbutton(
            top_options,
            text="🛡️ Admin yetkisi iste",
            variable=self.admin_var,
            bg='#1e1e1e',
            fg='#ffffff',
            selectcolor='#2d2d2d',
            font=("Segoe UI", 9),
            activebackground='#1e1e1e',
            activeforeground='#ffffff'
        )
        admin_check.pack(side=tk.LEFT, padx=(20, 0))
        
        # Alt satır - EXE adı
        bottom_options = tk.Frame(options_inner, bg='#1e1e1e')
        bottom_options.pack(fill=tk.X)
        
        tk.Label(
            bottom_options,
            text="📦 EXE Adı:",
            bg='#1e1e1e',
            fg='#ffffff',
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT)
        
        self.exe_name_var = tk.StringVar(value="program.exe")
        exe_name_entry = tk.Entry(
            bottom_options,
            textvariable=self.exe_name_var,
            bg='#2d2d2d',
            fg='#ffffff',
            font=("Consolas", 9),
            width=25,
            relief='flat',
            bd=5
        )
        exe_name_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Ana dönüştürme butonu
        convert_btn = tk.Button(
            main_container,
            text="🚀 EXE'YE DÖNÜŞTÜR",
            command=self.convert_to_exe,
            bg='#28a745',
            fg='white',
            font=("Segoe UI", 12, "bold"),
            relief='flat',
            cursor='hand2',
            height=2
        )
        convert_btn.pack(pady=(0, 10), fill=tk.X)
        
        # Durum çubuğu - Her zaman altta sabit
        status_frame = tk.Frame(self.root, bg='#2d2d2d', relief='sunken', bd=1)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="Program başlatıldı...")
        status_bar = tk.Label(
            status_frame,
            textvariable=self.status_var,
            bg='#2d2d2d',
            fg='#ffffff',
            font=("Segoe UI", 8),
            anchor='w'
        )
        status_bar.pack(fill=tk.X, padx=5, pady=2)
        
        # Canvas'ı pack et
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel binding
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def show_about(self):
        """Hakkında penceresi göster"""
        about_window = tk.Toplevel(self.root)
        about_window.title("Hakkında")
        about_window.geometry("400x350")
        about_window.configure(bg='#1e1e1e')
        about_window.resizable(False, False)
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Pencereyi ortala
        about_window.geometry("+{}+{}".format(
            self.root.winfo_x() + 250, 
            self.root.winfo_y() + 100
        ))
        
        tk.Label(
            about_window,
            text="🦇 BAT to EXE Converter",
            font=("Segoe UI", 16, "bold"),
            bg='#1e1e1e',
            fg='#00ff88'
        ).pack(pady=(20, 10))
        
        info_text = f"""Versiyon: {self.version}
Geliştirici: Python & Tkinter

📋 Özellikler:
• BAT dosyalarını EXE'ye dönüştürür
• Gizli çalışma seçeneği
• Admin yetkileri desteği
• Özel EXE adlandırma
• Kod editörü entegreli
• Örnek kod şablonları

🔧 Gereksinimler:
• Python 3.6+
• PyInstaller

📅 Son Güncelleme: 2025
🌟 Tamamen ücretsiz ve açık kaynak"""
        
        tk.Label(
            about_window,
            text=info_text,
            font=("Segoe UI", 9),
            bg='#1e1e1e',
            fg='#ffffff',
            justify='left'
        ).pack(pady=10, padx=20)
        
        tk.Button(
            about_window,
            text="✅ Tamam",
            command=about_window.destroy,
            bg='#0078d4',
            fg='white',
            font=("Segoe UI", 9, "bold"),
            relief='flat',
            cursor='hand2',
            width=15
        ).pack(pady=20)
    
    def browse_file(self):
        """BAT dosyası seç"""
        file_path = filedialog.askopenfilename(
            title="BAT dosyası seçin",
            filetypes=[
                ("Batch files", "*.bat *.cmd"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                self.text_editor.delete(1.0, tk.END)
                self.text_editor.insert(1.0, content)
                self.status_var.set(f"✅ Dosya yüklendi: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya okunamadı: {str(e)}")
                self.status_var.set("❌ Dosya okuma hatası")
    
    def load_sample(self):
        """Örnek BAT kodu yükle"""
        sample_code = '''@echo off
title 🦇 BAT to EXE Test Programı
color 0a
mode con cols=80 lines=30

echo.
echo ████████████████████████████████████████████████████████████████████████████████
echo ██                                                                            ██
echo ██                        BAT to EXE Test Programı                           ██
echo ██                              v1.0                                         ██
echo ██                                                                            ██
echo ████████████████████████████████████████████████████████████████████████████████
echo.
echo Merhaba %USERNAME%!
echo Bu program BAT to EXE Converter ile oluşturulmuştur.
echo.
echo Sistem Bilgileri:
echo ==================
echo 🖥️  Bilgisayar Adı: %COMPUTERNAME%
echo 👤 Kullanıcı Adı: %USERNAME%
echo 📅 Tarih: %DATE%
echo 🕐 Saat: %TIME%
echo 💻 İşletim Sistemi: %OS%
echo 📁 Mevcut Klasör: %CD%
echo.

:menu
echo ════════════════════════════════════════════════════════════════════════════════
echo                                   MENÜ
echo ════════════════════════════════════════════════════════════════════════════════
echo.
echo [1] 📁 Dosya listesi göster
echo [2] 💾 Disk kullanımını göster  
echo [3] 🌐 Ağ bağlantılarını göster
echo [4] 🔍 Sistem bilgilerini göster
echo [5] 📊 Çalışan işlemleri göster
echo [6] 🎨 Renk değiştir
echo [0] ❌ Çıkış
echo.
set /p "choice=Seçiminizi yapın (0-6): "

if "%choice%"=="1" goto files
if "%choice%"=="2" goto disk
if "%choice%"=="3" goto network
if "%choice%"=="4" goto sysinfo
if "%choice%"=="5" goto processes
if "%choice%"=="6" goto colors
if "%choice%"=="0" goto exit

echo ❌ Geçersiz seçim! Lütfen 0-6 arasında bir sayı girin.
ping localhost -n 2 >nul
goto menu

:files
cls
echo 📁 DOSYA LİSTESİ
echo ════════════════════════════════════════════════════════════════════════════════
dir /b /a
echo.
pause
goto menu

:disk
cls
echo 💾 DİSK KULLANIMI
echo ════════════════════════════════════════════════════════════════════════════════
wmic logicaldisk get size,freespace,caption
echo.
pause
goto menu

:network
cls
echo 🌐 AĞ BAĞLANTILARI
echo ════════════════════════════════════════════════════════════════════════════════
ipconfig
echo.
pause
goto menu

:sysinfo
cls
echo 🔍 SİSTEM BİLGİLERİ
echo ════════════════════════════════════════════════════════════════════════════════
systeminfo
echo.
pause
goto menu

:processes
cls
echo 📊 ÇALIŞAN İŞLEMLER
echo ════════════════════════════════════════════════════════════════════════════════
tasklist
echo.
pause
goto menu

:colors
cls
echo 🎨 RENK SEÇİMİ
echo ════════════════════════════════════════════════════════════════════════════════
echo [1] Yeşil    [4] Sarı
echo [2] Mavi     [5] Mor  
echo [3] Kırmızı  [6] Beyaz
echo.
set /p "color_choice=Renk seçin (1-6): "

if "%color_choice%"=="1" color a
if "%color_choice%"=="2" color 0b
if "%color_choice%"=="3" color 4
if "%color_choice%"=="4" color 0e
if "%color_choice%"=="5" color 0d
if "%color_choice%"=="6" color 0f

goto menu

:exit
cls
echo.
echo ████████████████████████████████████████████████████████████████████████████████
echo ██                            TEŞEKKÜRLER!                                   ██
echo ██                   BAT to EXE Converter kullandığınız için                 ██
echo ██                              teşekkürler!                                 ██
echo ████████████████████████████████████████████████████████████████████████████████
echo.
echo Çıkış yapılıyor...
for /l %%i in (3,-1,1) do (
    echo %%i saniye kaldı...
    ping localhost -n 2 >nul
)
exit'''
        
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.insert(1.0, sample_code)
        self.status_var.set("🔥 Örnek kod yüklendi")
    
    def clear_editor(self):
        """Editörü temizle"""
        if messagebox.askyesno("Temizle", "Editördeki tüm kod silinecek. Emin misiniz?"):
            self.text_editor.delete(1.0, tk.END)
            self.status_var.set("🗑️ Editör temizlendi")
    
    def convert_to_exe(self):
        """BAT kodunu EXE'ye dönüştür"""
        bat_content = self.text_editor.get(1.0, tk.END).strip()
        if not bat_content:
            messagebox.showerror("Hata", "BAT kodu boş!\n\nLütfen kod yazın veya dosya yükleyin.")
            return
        
        exe_name = self.exe_name_var.get().strip()
        if not exe_name:
            exe_name = "program.exe"
        elif not exe_name.endswith('.exe'):
            exe_name += '.exe'
        
        try:
            self.status_var.set("🔄 Dönüştürülüyor...")
            self.root.update()
            
            # Çıktı klasörü seç
            output_dir = filedialog.askdirectory(title="EXE dosyasını nereye kaydetmek istiyorsunuz?")
            if not output_dir:
                self.status_var.set("❌ İşlem iptal edildi")
                return
            
            # Python wrapper script oluştur
            python_script = self.create_python_wrapper(bat_content)
            
            # Geçici Python dosyası oluştur
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_py:
                temp_py.write(python_script)
                temp_py_path = temp_py.name
            
            # PyInstaller komutu oluştur
            base_name = exe_name.replace('.exe', '')
            cmd = [
                sys.executable, '-m', 'PyInstaller',
                '--onefile',
                '--distpath', output_dir,
                '--workpath', os.path.join(output_dir, 'build'),
                '--specpath', os.path.join(output_dir, 'spec'),
                '--name', base_name,
                '--clean'
            ]
            
            if self.invisible_var.get():
                cmd.append('--windowed')
                
            cmd.append(temp_py_path)
            
            # PyInstaller'ı çalıştır
            self.status_var.set("🔧 PyInstaller çalışıyor...")
            self.root.update()
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=output_dir)
            
            # Geçici dosyayı temizle
            try:
                os.unlink(temp_py_path)
            except:
                pass
            
            if result.returncode == 0:
                exe_path = os.path.join(output_dir, exe_name)
                self.status_var.set(f"✅ Başarılı! EXE oluşturuldu: {exe_name}")
                
                msg = f"🎉 BAT dosyası başarıyla EXE'ye dönüştürüldü!\n\n"
                msg += f"📂 Konum: {output_dir}\n"
                msg += f"📦 Dosya: {exe_name}\n\n"
                msg += f"Dosyayı açmak istiyor musunuz?"
                
                if messagebox.askyesno("Başarılı!", msg):
                    try:
                        os.startfile(output_dir)
                    except:
                        pass
            else:
                error_msg = result.stderr or result.stdout or "Bilinmeyen hata"
                raise Exception(error_msg)
                
        except FileNotFoundError:
            msg = "❌ PyInstaller bulunamadı!\n\n"
            msg += "Lütfen terminalde şu komutu çalıştırın:\n"
            msg += "pip install pyinstaller\n\n"
            msg += "Kurulum tamamlandıktan sonra tekrar deneyin."
            messagebox.showerror("PyInstaller Bulunamadı", msg)
            self.status_var.set("❌ PyInstaller bulunamadı")
        except Exception as e:
            error_msg = str(e)
            messagebox.showerror("Dönüştürme Hatası", f"Hata oluştu:\n\n{error_msg}")
            self.status_var.set("❌ Dönüştürme hatası")
    
    def create_python_wrapper(self, bat_content):
        """BAT içeriği için Python wrapper oluştur"""
        # BAT içeriğini base64 ile encode et
        encoded_bat = base64.b64encode(bat_content.encode('utf-8')).decode('ascii')
        
        admin_request = ""
        if self.admin_var.get():
            admin_request = '''
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if is_admin():
        return True
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return False

if not run_as_admin():
    sys.exit(0)
'''
        
        wrapper_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BAT to EXE Converter - Generated Executable
Created with BAT to EXE Converter v{self.version}
"""

import subprocess
import tempfile
import os
import base64
import sys
{admin_request}

def main():
    """Ana fonksiyon - BAT kodunu çalıştır"""
    try:
        # BAT içeriğini decode et
        bat_content = base64.b64decode("{encoded_bat}").decode('utf-8')
        
        # Geçici BAT dosyası oluştur
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='utf-8') as temp_bat:
            temp_bat.write(bat_content)
            temp_bat_path = temp_bat.name
        
        # BAT dosyasını çalıştır
        process = subprocess.Popen(
            [temp_bat_path], 
            shell=True,
            cwd=os.path.dirname(os.path.abspath(sys.argv[0]))
        )
        process.wait()
        
    except Exception as e:
        print(f"Hata: {{e}}")
        input("Devam etmek için Enter'a basın...")
    finally:
        # Geçici dosyayı temizle
        try:
            if 'temp_bat_path' in locals() and os.path.exists(temp_bat_path):
                os.unlink(temp_bat_path)
        except:
            pass

if __name__ == "__main__":
    main()'''
        
        return wrapper_code

def main():
    """Ana program başlatıcı"""
    root = tk.Tk()
    app = BatToExeConverter(root)
    
    # Program kapanırken onay sor
    def on_closing():
        if messagebox.askokcancel("Çıkış", "Programdan çıkmak istediğinizden emin misiniz?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()