import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import threading
import sys

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern MP3/MP4 İndirici")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Stil ayarları
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('Title.TLabel', background='#f0f0f0', font=('Arial', 16, 'bold'))
        style.configure('TButton', font=('Arial', 10))
        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'))
        
        # Ana çerçeve
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Başlık
        title_label = ttk.Label(main_frame, text="Modern MP3/MP4 İndirici", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Sekmeler
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # MP3 Manuel sekmesi
        mp3_manual_frame = ttk.Frame(notebook, padding="10")
        notebook.add(mp3_manual_frame, text="MP3 İndir (Şarkı-Ad)")
        
        ttk.Label(mp3_manual_frame, text="Şarkı adı ve sanatçı:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.track_entry = ttk.Entry(mp3_manual_frame, width=50)
        self.track_entry.grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(mp3_manual_frame, text="İndir", command=self.download_mp3_manual).grid(row=1, column=1, pady=10, sticky=tk.E)
        
        # YouTube MP3 sekmesi
        yt_mp3_frame = ttk.Frame(notebook, padding="10")
        notebook.add(yt_mp3_frame, text="YouTube'dan MP3")
        
        ttk.Label(yt_mp3_frame, text="YouTube URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.yt_mp3_entry = ttk.Entry(yt_mp3_frame, width=50)
        self.yt_mp3_entry.grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(yt_mp3_frame, text="İndir", command=self.download_yt_mp3).grid(row=1, column=1, pady=10, sticky=tk.E)
        
        # SoundCloud sekmesi
        sc_frame = ttk.Frame(notebook, padding="10")
        notebook.add(sc_frame, text="SoundCloud'dan MP3")
        
        ttk.Label(sc_frame, text="SoundCloud URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sc_entry = ttk.Entry(sc_frame, width=50)
        self.sc_entry.grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(sc_frame, text="İndir", command=self.download_soundcloud).grid(row=1, column=1, pady=10, sticky=tk.E)
        
        # YouTube Video sekmesi
        yt_video_frame = ttk.Frame(notebook, padding="10")
        notebook.add(yt_video_frame, text="YouTube'dan Video")
        
        ttk.Label(yt_video_frame, text="YouTube URL veya arama:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.yt_video_entry = ttk.Entry(yt_video_frame, width=50)
        self.yt_video_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(yt_video_frame, text="Kalite:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.StringVar()
        quality_combo = ttk.Combobox(yt_video_frame, textvariable=self.quality_var, width=20)
        quality_combo['values'] = ('360p', '480p', '720p (HD)', '1080p (Full HD)', '1440p (2K)', '2160p (4K)')
        quality_combo.current(2)  # Varsayılan 720p
        quality_combo.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        ttk.Button(yt_video_frame, text="İndir", command=self.download_yt_video).grid(row=2, column=1, pady=10, sticky=tk.E)
        
        # Toplu MP3 sekmesi
        bulk_mp3_frame = ttk.Frame(notebook, padding="10")
        notebook.add(bulk_mp3_frame, text="Toplu MP3 İndir")
        
        ttk.Label(bulk_mp3_frame, text="Şarkı listesi (her satıra bir şarkı):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.bulk_text = scrolledtext.ScrolledText(bulk_mp3_frame, width=50, height=10)
        self.bulk_text.grid(row=1, column=0, columnspan=2, pady=5, padx=5)
        ttk.Button(bulk_mp3_frame, text="İndir", command=self.download_bulk_mp3).grid(row=2, column=1, pady=10, sticky=tk.E)
        
        # Durum çıktısı
        ttk.Label(main_frame, text="İşlem Durumu:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        self.status_text = scrolledtext.ScrolledText(main_frame, width=80, height=15, state='disabled')
        self.status_text.grid(row=3, column=0, columnspan=2, pady=5)
        
        # İlerleme çubuğu
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Batch dosyasının yolu
        self.batch_file = "MP3_MP4_indir.bat"
        
        # Bin klasörü kontrolü
        self.bin_dir = "bin"
        if not os.path.exists(self.bin_dir):
            os.makedirs(self.bin_dir)
            self.log_message("UYARI: 'bin' klasörü oluşturuldu. Lütfen yt-dlp.exe ve ffmpeg.exe dosyalarını bu klasöre ekleyin.")
            messagebox.showwarning("Uyarı", "'bin' klasörü oluşturuldu. Lütfen yt-dlp.exe ve ffmpeg.exe dosyalarını bu klasöre ekleyin.")
        
        # Batch dosyasını kontrol et ve oluştur
        if not os.path.exists(self.batch_file):
            self.create_batch_file()
            self.log_message("Batch dosyası oluşturuldu.")
    
    def create_batch_file(self):
        """Batch dosyasını oluştur"""
        batch_content = r"""@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: === ANA MENÜ ===
:MAIN_MENU
cls
echo.
echo =========================================
echo         ALL-IN-ONE DOWNLOADER
echo =========================================
echo 1. MP3 indir (Sanatci - Sarki)
echo 2. YouTube linkten Mp3
echo 3. Soundcloud linkten Mp3
echo 4. YouTube linkten Video (kalite secenekleriyle)
echo 5. Toplu MP3 Indir (Sanatci - Sarki listesi)
echo 6. Cikis
echo =========================================
set /p "CHOICE=Seciminiz (1-6): "

if "%CHOICE%"=="1" goto MP3_MANUAL
if "%CHOICE%"=="2" goto YTMP3
if "%CHOICE%"=="3" goto SOUNDCLOUD
if "%CHOICE%"=="4" goto YTMP4
if "%CHOICE%"=="5" goto BULK_MP3
if "%CHOICE%"=="6" exit /b
echo Gecersiz secim, tekrar deneyin.
timeout /t 2 >nul
goto MAIN_MENU

:: === MANUEL MP3 ===
:MP3_MANUAL
cls
if not exist "MP3" mkdir "MP3"

if not exist "bin\yt-dlp.exe" (
    echo [HATA] yt-dlp.exe 'bin' klasorunde bulunamadi.
    goto END
)
if not exist "bin\ffmpeg.exe" (
    echo [HATA] ffmpeg.exe 'bin' klasorunde bulunamadi.
    goto END
)

echo =========================================
echo [MP3 - Manuel] Sarki adini ve sanatciyi girin:
echo Ornek: Sanatci - Sarki Adi
echo =========================================
set /p "track_info=Sarki adi ve sanatci: "
if "%track_info%"=="" (
    echo [HATA] Girdi bos olamaz.
    goto END
)

echo.
echo [INDIRME] Aranıyor ve indiriliyor...
call :YTSEARCH_SILENT "%track_info%"

echo.
echo ===== INDIRME OZETI =====
if exist "MP3\*.mp3" (
    echo [BASARI] Indirme islemi tamamlandi!
    echo [DOSYA] Indirilen dosyalar:
    for %%f in ("MP3\*.mp3") do echo - %%~nxf
) else (
    echo [HATA] Hicbir MP3 indirilemedi
)
goto CLEANUP

:: === BULK MP3 ===
:BULK_MP3
cls
if not exist "MP3" mkdir "MP3"

if not exist "bin\yt-dlp.exe" (
    echo [HATA] yt-dlp.exe 'bin' klasorunde bulunamadi.
    goto BULK_END
)
if not exist "bin\ffmpeg.exe" (
    echo [HATA] ffmpeg.exe 'bin' klasorunde bulunamadi.
    goto BULK_END
)

echo =========================================
echo [Toplu MP3] Birden fazla sarki indirin
echo Ornek: Sanatci1 - Sarki1, Sanatci2 - Sarki2
echo =========================================
set /p "track_list=Sanatci - Sarki listesi (virgul ile ayrin): "
if "%track_list%"=="" (
    echo [HATA] Girdi bos olamaz.
    goto BULK_END
)

setlocal enabledelayedexpansion
set "input=%track_list%"
set "input=!input:"=!"
set count=0
set success_count=0
set error_count=0

:PROCESS_NEXT
if "!input!"=="" goto BULK_SUMMARY
for /f "tokens=1* delims=," %%a in ("!input!") do (
    set "current=%%a"
    set "input=%%b"
)

rem Boşluk temizleme
call :TRIM "current"

if "!current!"=="" (
    echo [UYARI] Bos girdi atlandi.
    goto PROCESS_NEXT
)

set /a count+=1
echo.
echo ===== [!count!] Indiriliyor: !current! =====
call :YTSEARCH_SILENT "!current!"

if !errorlevel! equ 0 (
    set /a success_count+=1
) else (
    set /a error_count+=1
)

goto PROCESS_NEXT

:BULK_SUMMARY
echo.
echo ===== TOPLU INDIRME OZETI =====
echo Toplam giris: %count%
echo Basarili: %success_count%
echo Hatali: %error_count%
echo ===============================
endlocal
goto CLEANUP

:BULK_END
if defined endlocal endlocal
goto CLEANUP

:: === YOUTUBE MP3 ===
:YTMP3
cls
if not exist "MP3" mkdir "MP3"

if not exist "bin\yt-dlp.exe" (
    echo [HATA] yt-dlp.exe 'bin' klasorunde bulunamadi.
    goto END
)
if not exist "bin\ffmpeg.exe" (
    echo [HATA] ffmpeg.exe 'bin' klasorunde bulunamadi.
    goto END
)

echo =========================================
echo [YouTube -> MP3] 320 kbps indirici
echo =========================================
set /p "INPUT=YouTube URL girin: "
if "%INPUT%"=="" (
    echo [HATA] Girdi bos olamaz.
    goto END
)

call :YT2MP3_SILENT "%INPUT%"
goto CLEANUP

:: === SOUNDCLOUD ===
:SOUNDCLOUD
cls
if not exist "MP3" mkdir "MP3"

if not exist "bin\yt-dlp.exe" (
    echo [HATA] yt-dlp.exe 'bin' klasorunde bulunamadi.
    goto END
)
if not exist "bin\ffmpeg.exe" (
    echo [HATA] ffmpeg.exe 'bin' klasorunde bulunamadi.
    goto END
)

echo =========================================
echo [SoundCloud -> MP3] 320 kbps indirici
echo =========================================
set /p "INPUT=SoundCloud URL girin: "
if "%INPUT%"=="" (
    echo [HATA] Girdi bos olamaz.
    goto END
)

echo.
echo [INDIRME] SoundCloud'dan indiriliyor...
bin\yt-dlp.exe -x --audio-format mp3 --audio-quality 320k ^
    --ffmpeg-location "bin\ffmpeg.exe" ^
    --ignore-errors --no-check-certificates ^
    --no-warnings --console-title ^
    -o "MP3/%%(title)s.%%(ext)s" "%INPUT%" 2>nul

echo.
echo ===== INDIRME OZETI =====
if exist "MP3\*.mp3" (
    echo [BASARI] Indirme islemi tamamlandi!
    echo [DOSYA] Indirilen dosyalar:
    for %%f in ("MP3\*.mp3") do echo - %%~nxf
) else (
    echo [HATA] Hicbir MP3 indirilemedi
)
goto CLEANUP

:: === YOUTUBE VIDEO ===
:YTMP4
cls
if not exist "MP4" mkdir "MP4"

if not exist "bin\yt-dlp.exe" (
    echo [HATA] yt-dlp.exe 'bin' klasorunde bulunamadi.
    goto END
)
if not exist "bin\ffmpeg.exe" (
    echo [HATA] ffmpeg.exe 'bin' klasorunde bulunamadi.
    goto END
)

echo =========================================
echo [YouTube -> Video] Kalite secmeli indirici
echo =========================================
set /p "INPUT=YouTube URL veya arama terimi: "
if "%INPUT%"=="" (
    echo [HATA] Girdi bos olamaz.
    goto END
)

echo.
echo Secenekler:
echo  1^) 360p
echo  2^) 480p
echo  3^) 720p (HD^)
echo  4^) 1080p (Full HD^)
echo  5^) 1440p (2K^)
echo  6^) 2160p (4K^)
set /p "CHOICE=Kalite (1-6^): "

set "MAXH="
if "%CHOICE%"=="1" set "MAXH=360"
if "%CHOICE%"=="2" set "MAXH=480"
if "%CHOICE%"=="3" set "MAXH=720"
if "%CHOICE%"=="4" set "MAXH=1080"
if "%CHOICE%"=="5" set "MAXH=1440"
if "%CHOICE%"=="6" set "MAXH=2160"

if not defined MAXH (
    echo [UYARI] Gecersiz secim, varsayilan 720p kullanilacak.
    set "MAXH=720"
)

set "Q=%INPUT%"
set "ISURL="
if /i "!Q:~0,4!"=="http" set "ISURL=1"

if defined ISURL (
    echo.
    echo [INDIRME] Video indiriliyor...
    bin\yt-dlp.exe -f "bestvideo[height<=%MAXH%]+bestaudio/best[height<=%MAXH%]" ^
        --ffmpeg-location "bin\ffmpeg.exe" ^
        --ignore-errors --no-check-certificates ^
        --extractor-args "youtube:player-client=android" ^
        --merge-output-format mp4 ^
        --no-warnings --console-title ^
        -o "MP4\%%(title)s.%%(ext)s" "%Q%" 2>nul
) else (
    echo.
    echo [INDIRME] Video aranıyor ve indiriliyor...
    bin\yt-dlp.exe -f "bestvideo[height<=%MAXH%]+bestaudio/best[height<=%MAXH%]" ^
        --ffmpeg-location "bin\ffmpeg.exe" ^
        --ignore-errors --no-check-certificates ^
        --extractor-args "youtube:player-client=android" ^
        --merge-output-format mp4 ^
        --no-warnings --console-title ^
        -o "MP4\%%(title)s.%%(ext)s" "ytsearch1:%Q%" 2>nul
)

echo.
echo ===== INDIRME OZETI (MP4^) =====
if exist "MP4\*.*" (
    echo [BASARI] Indirme islemi tamamlandi!
    echo [DOSYA] Indirilen dosyalar:
    for %%F in ("MP4\*.*") do echo - %%~nxF
) else (
    echo [UYARI] MP4 klasorunde dosya bulunamadi.
)
goto CLEANUP

:: === SESSIZ MP3 INDIRME FONKSIYONLARI ===
:YTSEARCH_SILENT
echo [INDIRME] İşlem devam ediyor...
set "LAST_LINE="
for /f "tokens=*" %%a in ('bin\yt-dlp.exe -x --audio-format mp3 --audio-quality 320k ^
    --ffmpeg-location "bin\ffmpeg.exe" ^
    --ignore-errors --no-check-certificates ^
    --no-warnings --console-title ^
    --extractor-args "youtube:player-client=android" ^
    --throttled-rate 100K ^
    --progress-template "download:[%%(progress.downloaded_bytes)s/%%(progress.total_bytes)s] %%(progress._percent_str)s - %%(progress._speed_str)s - ETA: %%(progress._eta_str)s" ^
    -o "MP3/%%(title)s.%%(ext)s" "ytsearch1:%~1" 2^>^&1') do (
    set "LINE=%%a"
    set "LAST_LINE=%%a"
    echo !LINE! | findstr /C:"download:" >nul && (
        cls
        echo.
        echo =========================================
        echo         INDIRME DURUMU
        echo =========================================
        echo [INDIRME] İşlem devam ediyor...
        echo !LINE!
        echo =========================================
    )
)
exit /b %errorlevel%

:YT2MP3_SILENT
set "Q=%~1"
set "ISURL="
if /i "!Q:~0,4!"=="http" set "ISURL=1"

if defined ISURL (
    echo [INDIRME] İşlem devam ediyor...
    set "LAST_LINE="
    for /f "tokens=*" %%a in ('bin\yt-dlp.exe -x --audio-format mp3 --audio-quality 320k ^
        --ffmpeg-location "bin\ffmpeg.exe" ^
        --ignore-errors --no-check-certificates ^
        --no-warnings --console-title ^
        --extractor-args "youtube:player-client=android" ^
        --throttled-rate 100K ^
        --progress-template "download:[%%(progress.downloaded_bytes)s/%%(progress.total_bytes)s] %%(progress._percent_str)s - %%(progress._speed_str)s - ETA: %%(progress._eta_str)s" ^
        -o "MP3/%%(title)s.%%(ext)s" "%Q%" 2^>^&1') do (
        set "LINE=%%a"
        set "LAST_LINE=%%a"
        echo !LINE! | findstr /C:"download:" >nul && (
            cls
            echo.
            echo =========================================
            echo         INDIRME DURUMU
            echo =========================================
            echo [INDIRME] İşlem devam ediyor...
            echo !LINE!
            echo =========================================
        )
    )
) else (
    call :YTSEARCH_SILENT "%Q%"
)
exit /b %ERRORLEVEL%

:: === BOŞLUK TEMİZLEME ===
:TRIM
setlocal enabledelayedexpansion
set "var=%~1"
set "str=!%var%!"

:TRIM_LOOP
if "!str:~0,1!"==" " (
    set "str=!str:~1!"
    goto TRIM_LOOP
)
if "!str:~-1!"==" " (
    set "str=!str:~0,-1!"
    goto TRIM_LOOP
)
endlocal & set "%~1=%str%"
goto :eof

:: === GELIŞMİŞ TEMIZLIK ===
:CLEANUP
echo.
echo [TEMIZLIK] Gecici dosyalar temizleniyor...
del /q *.tmp 2>nul
del /q *.temp.* 2>nul
del /q *.part 2>nul
del /q *.ytdl 2>nul
del /q "MP3\*.tmp" 2>nul
del /q "MP3\*.part" 2>nul
del /q "MP4\*.tmp" 2>nul
del /q "MP4\*.part" 2>nul
del /q "MP3\*.ytdl" 2>nul
del /q "MP4\*.ytdl" 2>nul
echo [TEMIZLIK] Temizlik tamamlandı.
goto END

:: === SON ===
:END
echo.
echo =========================================
echo [BITTI] Ana menuye donmek icin bir tusa basin...
echo =========================================
pause >nul
goto MAIN_MENU
"""
        
        with open(self.batch_file, "w", encoding="utf-8") as f:
            f.write(batch_content)
    
    def log_message(self, message):
        """Durum kısmına mesaj yaz"""
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
    
    def run_batch_command(self, command_index, parameter=""):
        """Batch scriptini çalıştır"""
        try:
            self.progress.start()
            self.log_message(f"İşlem başlatılıyor...")
            
            # Batch scriptini çalıştır
            cmd = ["cmd", "/c", "chcp", "65001", ">", "nul", "&", self.batch_file, str(command_index)]
            if parameter:
                cmd.append(parameter)
            
            process = subprocess.Popen(
                " ".join(cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Çıktıyı gerçek zamanlı olarak al
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_message(output.strip())
            
            return_code = process.poll()
            if return_code == 0:
                self.log_message("İşlem başarıyla tamamlandı!")
                messagebox.showinfo("Başarılı", "İndirme işlemi tamamlandı!")
            else:
                self.log_message(f"İşlem hata kodu ile sonlandı: {return_code}")
                messagebox.showerror("Hata", "İndirme işleminde hata oluştu!")
                
        except Exception as e:
            self.log_message(f"Hata: {str(e)}")
            messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")
        finally:
            self.progress.stop()
    
    def download_mp3_manual(self):
        """MP3 Manuel indirme"""
        track_info = self.track_entry.get().strip()
        if not track_info:
            messagebox.showwarning("Uyarı", "Lütfen şarkı adı ve sanatçı bilgisini girin!")
            return
        
        # Thread'de çalıştır
        thread = threading.Thread(target=self.run_batch_command, args=(1, f'"{track_info}"'))
        thread.daemon = True
        thread.start()
    
    def download_yt_mp3(self):
        """YouTube'dan MP3 indirme"""
        url = self.yt_mp3_entry.get().strip()
        if not url:
            messagebox.showwarning("Uyarı", "Lütfen YouTube URL'sini girin!")
            return
        
        # Thread'de çalıştır
        thread = threading.Thread(target=self.run_batch_command, args=(2, f'"{url}"'))
        thread.daemon = True
        thread.start()
    
    def download_soundcloud(self):
        """SoundCloud'dan MP3 indirme"""
        url = self.sc_entry.get().strip()
        if not url:
            messagebox.showwarning("Uyarı", "Lütfen SoundCloud URL'sini girin!")
            return
        
        # Thread'de çalıştır
        thread = threading.Thread(target=self.run_batch_command, args=(3, f'"{url}"'))
        thread.daemon = True
        thread.start()
    
    def download_yt_video(self):
        """YouTube'dan video indirme"""
        url = self.yt_video_entry.get().strip()
        if not url:
            messagebox.showwarning("Uyarı", "Lütfen YouTube URL'sini veya arama terimini girin!")
            return
        
        # Kalite seçeneğini sayıya çevir
        quality_map = {
            '360p': '1',
            '480p': '2', 
            '720p (HD)': '3',
            '1080p (Full HD)': '4',
            '1440p (2K)': '5',
            '2160p (4K)': '6'
        }
        
        quality = self.quality_var.get()
        if quality not in quality_map:
            quality = '720p (HD)'
        
        # Thread'de çalıştır
        thread = threading.Thread(target=self.run_batch_command, args=(4, f'"{url}" {quality_map[quality]}'))
        thread.daemon = True
        thread.start()
    
    def download_bulk_mp3(self):
        """Toplu MP3 indirme"""
        tracks = self.bulk_text.get("1.0", tk.END).strip()
        if not tracks:
            messagebox.showwarning("Uyarı", "Lütfen şarkı listesini girin!")
            return
        
        # Geçici dosyaya yaz
        with open("temp_tracks.txt", "w", encoding="utf-8") as f:
            f.write(tracks)
        
        # Thread'de çalıştır
        thread = threading.Thread(target=self.run_batch_command, args=(5, '"temp_tracks.txt"'))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()