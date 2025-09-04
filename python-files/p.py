import os
import sys
import time
import json
import socket
import psutil
import shutil
import ctypes
import winreg
import base64
import sqlite3
import requests
import keyboard
import win32api
import win32gui
import win32con
import pyperclip
import threading
import subprocess
import ctypes.wintypes
import win32serviceutil
import customtkinter as ctk
from pynput import keyboard
from tkinter import messagebox
from time import sleep
import webbrowser
from datetime import datetime
import tempfile
import urllib.request
from tkinter import messagebox as mb

"""
🔒 PROVERKA HELPER - UUID УПРАВЛЕНИЕ

📋 КАК УПРАВЛЯТЬ UUID:
1. Найдите переменную AUTHORIZED_UUIDS в коде (примерно строка 50)
2. Добавьте или удалите UUID по необходимости
3. Формат: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
4. Не забудьте запятые между UUID
5. Перезапустите программу после изменений

💡 ПРИМЕР:
AUTHORIZED_UUIDS = [
    "12345678-1234-1234-1234-123456789abc",  # Ваш UUID
    "87654321-4321-4321-4321-cba987654321",  # Другой UUID
]

⚠️ ВАЖНО: UUID должны быть в кавычках и разделены запятыми!
"""

# Глобальные переменные
global running  
global window_hidden  
global global_key2  
global global_key1  
global check_service
global socket_lock  
global program_titles
global launcher_window 
launcher_window = None 

# Настройка CustomTkinter для красно-серой темы
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')

# Кастомные цвета для красно-серой темы
COLORS = {
    'bg_dark': '#1a0a0a',
    'bg_medium': '#2d1a1a', 
    'bg_light': '#3d2a2a',
    'accent_red': '#8b0000',
    'accent_red_light': '#a52a2a',
    'text_white': '#ffffff',
    'text_gray': '#cccccc',
    'border': '#4a2a2a'
}

# UUID верификация
# Здесь вы можете управлять списком авторизованных UUID
# Просто добавьте или удалите UUID по необходимости
AUTHORIZED_UUIDS = [
    # Примеры UUID (замените на ваши):
    # "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    # "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy",
    # "zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz",
    
    # Добавьте сюда ваши UUID:
    "26e600e0-7b9a-11f0-aa18-806e6f6e6963",  # Пример UUID
    "00000000-0000-0000-0000-6C626DDB5429",  # Пример UUID
]

def get_motherboard_uuid():
    """Получает UUID материнской платы всеми возможными способами"""
    uuid_methods = []
    
    try:
        # Метод 1: WMI - Win32_BaseBoard
        try:
            import wmi
            c = wmi.WMI()
            for board in c.Win32_BaseBoard():
                if board.SerialNumber and board.SerialNumber.strip():
                    uuid = board.SerialNumber.strip()
                    uuid_methods.append(("WMI BaseBoard", uuid))
                    print(f"UUID получен через WMI BaseBoard: {uuid}")
        except Exception as e:
            print(f"WMI BaseBoard ошибка: {e}")
        
        # Метод 2: WMI - Win32_ComputerSystem
        try:
            import wmi
            c = wmi.WMI()
            for system in c.Win32_ComputerSystem():
                if system.UUID and system.UUID.strip():
                    uuid = system.UUID.strip()
                    uuid_methods.append(("WMI ComputerSystem", uuid))
                    print(f"UUID получен через WMI ComputerSystem: {uuid}")
        except Exception as e:
            print(f"WMI ComputerSystem ошибка: {e}")
        
        # Метод 3: WMI - Win32_ComputerSystemProduct
        try:
            import wmi
            c = wmi.WMI()
            for product in c.Win32_ComputerSystemProduct():
                if product.UUID and product.UUID.strip():
                    uuid = product.UUID.strip()
                    uuid_methods.append(("WMI ComputerSystemProduct", uuid))
                    print(f"UUID получен через WMI ComputerSystemProduct: {uuid}")
        except Exception as e:
            print(f"WMI ComputerSystemProduct ошибка: {e}")
        
        # Метод 4: Реестр - HwProfileGuid
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\IDConfigDB\Hardware Profiles\0001")
            uuid, _ = winreg.QueryValueEx(key, "HwProfileGuid")
            winreg.CloseKey(key)
            if uuid and uuid.strip():
                uuid = uuid.strip('{}')
                uuid_methods.append(("Registry HwProfileGuid", uuid))
                print(f"UUID получен через Registry HwProfileGuid: {uuid}")
        except Exception as e:
            print(f"Registry HwProfileGuid ошибка: {e}")
        
        # Метод 5: Реестр - MachineGuid
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
            uuid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            if uuid and uuid.strip():
                uuid_methods.append(("Registry MachineGuid", uuid))
                print(f"UUID получен через Registry MachineGuid: {uuid}")
        except Exception as e:
            print(f"Registry MachineGuid ошибка: {e}")
        
        # Метод 6: Команда systeminfo
        try:
            result = subprocess.run(['systeminfo'], capture_output=True, text=True, shell=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'System UUID' in line or 'System Manufacturer' in line:
                        if ':' in line:
                            uuid = line.split(':')[-1].strip()
                            if uuid and len(uuid) > 5:
                                uuid_methods.append(("SystemInfo", uuid))
                                print(f"UUID получен через SystemInfo: {uuid}")
                                break
        except Exception as e:
            print(f"SystemInfo ошибка: {e}")
        
        # Метод 7: Команда wmic
        try:
            result = subprocess.run(['wmic', 'csproduct', 'get', 'uuid'], capture_output=True, text=True, shell=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    uuid = lines[1].strip()
                    if uuid and uuid.lower() != 'uuid' and len(uuid) > 5:
                        uuid_methods.append(("WMIC csproduct", uuid))
                        print(f"UUID получен через WMIC csproduct: {uuid}")
        except Exception as e:
            print(f"WMIC csproduct ошибка: {e}")
        
        # Метод 8: Команда wmic baseboard
        try:
            result = subprocess.run(['wmic', 'baseboard', 'get', 'serialnumber'], capture_output=True, text=True, shell=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    uuid = lines[1].strip()
                    if uuid and uuid.lower() != 'serialnumber' and len(uuid) > 5:
                        uuid_methods.append(("WMIC baseboard", uuid))
                        print(f"UUID получен через WMIC baseboard: {uuid}")
        except Exception as e:
            print(f"WMIC baseboard ошибка: {e}")
        
        # Метод 9: Команда wmic computersystem
        try:
            result = subprocess.run(['wmic', 'computersystem', 'get', 'uuid'], capture_output=True, text=True, shell=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    uuid = lines[1].strip()
                    if uuid and uuid.lower() != 'uuid' and len(uuid) > 5:
                        uuid_methods.append(("WMIC computersystem", uuid))
                        print(f"UUID получен через WMIC computersystem: {uuid}")
        except Exception as e:
            print(f"WMIC computersystem ошибка: {e}")
        
        # Метод 10: PowerShell Get-WmiObject
        try:
            ps_command = "Get-WmiObject -Class Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID"
            result = subprocess.run(['powershell', '-Command', ps_command], capture_output=True, text=True, shell=True, timeout=10)
            if result.returncode == 0:
                uuid = result.stdout.strip()
                if uuid and len(uuid) > 5:
                    uuid_methods.append(("PowerShell WMI", uuid))
                    print(f"UUID получен через PowerShell WMI: {uuid}")
        except Exception as e:
            print(f"PowerShell WMI ошибка: {e}")
        
        # Метод 11: PowerShell Get-ComputerInfo
        try:
            ps_command = "Get-ComputerInfo | Select-Object -ExpandProperty WindowsProductId"
            result = subprocess.run(['powershell', '-Command', ps_command], capture_output=True, text=True, shell=True, timeout=10)
            if result.returncode == 0:
                uuid = result.stdout.strip()
                if uuid and len(uuid) > 5:
                    uuid_methods.append(("PowerShell ComputerInfo", uuid))
                    print(f"UUID получен через PowerShell ComputerInfo: {uuid}")
        except Exception as e:
            print(f"PowerShell ComputerInfo ошибка: {e}")
        
        # Метод 12: PowerShell Get-CimInstance
        try:
            ps_command = "Get-CimInstance -ClassName Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID"
            result = subprocess.run(['powershell', '-Command', ps_command], capture_output=True, text=True, shell=True, timeout=10)
            if result.returncode == 0:
                uuid = result.stdout.strip()
                if uuid and len(uuid) > 5:
                    uuid_methods.append(("PowerShell CIM", uuid))
                    print(f"UUID получен через PowerShell CIM: {uuid}")
        except Exception as e:
            print(f"PowerShell CIM ошибка: {e}")
        
        # Метод 13: Реестр - ProductId
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
            uuid, _ = winreg.QueryValueEx(key, "ProductId")
            winreg.CloseKey(key)
            if uuid and uuid.strip():
                uuid_methods.append(("Registry ProductId", uuid))
                print(f"UUID получен через Registry ProductId: {uuid}")
        except Exception as e:
            print(f"Registry ProductId ошибка: {e}")
        
        # Метод 14: Реестр - InstallationID
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform")
            uuid, _ = winreg.QueryValueEx(key, "InstallationID")
            winreg.CloseKey(key)
            if uuid and uuid.strip():
                uuid_methods.append(("Registry InstallationID", uuid))
                print(f"UUID получен через Registry InstallationID: {uuid}")
        except Exception as e:
            print(f"Registry InstallationID ошибка: {e}")
        
        # Метод 15: Команда vol для получения серийного номера диска
        try:
            result = subprocess.run(['vol', 'C:'], capture_output=True, text=True, shell=True, timeout=10)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Volume Serial Number is' in line:
                        uuid = line.split('is')[-1].strip()
                        if uuid and len(uuid) > 5:
                            uuid_methods.append(("Volume Serial", uuid))
                            print(f"UUID получен через Volume Serial: {uuid}")
                            break
        except Exception as e:
            print(f"Volume Serial ошибка: {e}")
        
        # Выводим все найденные UUID
        if uuid_methods:
            print(f"\n📋 Найдено {len(uuid_methods)} способов получения UUID:")
            for i, (method, uuid) in enumerate(uuid_methods, 1):
                print(f"  {i}. {method}: {uuid}")
            
            # Возвращаем первый найденный UUID (обычно самый надежный)
            first_uuid = uuid_methods[0][1]
            print(f"\n✅ Используется UUID: {first_uuid} (метод: {uuid_methods[0][0]})")
            return first_uuid
        else:
            print("❌ Не удалось получить UUID ни одним из методов")
            return None
            
    except Exception as e:
        print(f"❌ Общая ошибка при получении UUID: {e}")
        return None

def verify_uuid():
    """Проверяет UUID материнской платы"""
    try:
        print("🔍 Начинаю поиск UUID материнской платы...")
        local_uuid = get_motherboard_uuid()
        
        if not local_uuid:
            messagebox.showerror("Ошибка", "Не удалось получить UUID материнской платы ни одним из методов!")
            return False
        
        print(f"\n🎯 Основной UUID для проверки: {local_uuid}")
        
        # Проверяем, есть ли локальный UUID в списке авторизованных
        for auth_uuid in AUTHORIZED_UUIDS:
            if local_uuid.lower() == auth_uuid.lower():
                print(f"✅ UUID верификация успешна: {local_uuid}")
                print(f"✅ UUID найден в списке авторизованных")
                return True
        
        # Если UUID не найден, показываем подробную ошибку
        error_msg = f"""❌ ДОСТУП ЗАПРЕЩЕН!

🎯 UUID для проверки: {local_uuid}

📋 СПИСОК АВТОРИЗОВАННЫХ UUID:
"""
        
        for i, auth_uuid in enumerate(AUTHORIZED_UUIDS, 1):
            error_msg += f"{i}. {auth_uuid}\n"
        
        error_msg += f"""

❌ Этот UUID не найден в списке авторизованных.

📋 КАК ДОБАВИТЬ UUID В КОД:
1. Откройте файл ph1.py
2. Найдите переменную AUTHORIZED_UUIDS (примерно строка 75)
3. Добавьте строку: "{local_uuid}"
4. Сохраните файл и перезапустите программу

💡 ПРИМЕР:
AUTHORIZED_UUIDS = [
    "12345678-1234-1234-1234-123456789abc",
    "{local_uuid}",  # Добавьте эту строку
    "00000000-0000-0000-0000-6C626DDB5429",
]

⚠️ ВАЖНО:
• UUID должны быть в кавычках
• Каждый UUID с новой строки
• Не забудьте запятую после каждого UUID
• Перезапустите программу после изменений

🔍 ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:
• Программа использует 15 различных методов получения UUID
• Если UUID не получен, проверьте права администратора
• Попробуйте запустить программу от имени администратора"""

        messagebox.showerror("ДОСТУП ЗАПРЕЩЕН", error_msg)
        return False
        
    except Exception as e:
        print(f"❌ Ошибка при верификации UUID: {e}")
        messagebox.showerror("Ошибка", f"Ошибка при верификации UUID: {e}")
        return False

def clear_dns_cache():
    try:
        os.system('ipconfig /flushdns')
        print('Кэш DNS успешно очищен.')
        messagebox.showinfo('Успех', 'Кэш DNS успешно очищен.')
    except:
        messagebox.showerror('Ошибка', 'Не удалось найти процесс для очистки DNS.')

def clean_browser_history():
    BROWSERS = {'Chrome': os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default'), 'Edge': os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default'), 'Opera': os.path.expanduser('~\\AppData\\Roaming\\Opera Software\\Opera Stable'), 'Yandex': os.path.expanduser('~\\AppData\\Local\\Yandex\\YandexBrowser\\User Data\\Default'), 'Brave': os.path.expanduser('~\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Default')}
    FIREFOX_PATH = os.path.expanduser('~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles')
    KEYWORDS = ['blasted', 'nemezida', 'spoofer', 'sechex', 'akcel', 'euphoria', 'bebra', 'funpay', 'cheatlist', 'skalka']

    def clean_sqlite_db(db_path, queries):
        if os.path.exists(db_path):
            try:
                backup_path = db_path + '.bak'
                shutil.copy(db_path, backup_path)
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                for query, param in queries:
                    cursor.execute(query, param)
                conn.commit()
                cursor.execute('VACUUM')
                conn.commit()
                conn.close()
                print(f'Очищено: {db_path}')
            except Exception as e:
                pass  
            print(f'Ошибка при очистке {db_path}: {e}')

    def clean_chromium():
        for browser, path in BROWSERS.items():
            history_path = os.path.join(path, 'History')
            downloads_db = os.path.join(path, 'DownloadMetadata')
            if os.path.exists(history_path):
                queries = []
                for keyword in KEYWORDS:
                    queries.extend([('DELETE FROM urls WHERE url LIKE ?', (f'%{keyword}%',)), ('DELETE FROM urls WHERE title LIKE ?', (f'%{keyword}%',)), ('DELETE FROM downloads WHERE tab_url LIKE ?', (f'%{keyword}%',)), ('DELETE FROM downloads WHERE target_path LIKE ?', (f'%{keyword}%',))])
                clean_sqlite_db(history_path, queries)
            if os.path.exists(downloads_db):
                try:
                    os.remove(downloads_db)
                    print(f'Удален DownloadMetadata для {browser}')
                except Exception as e:
                    pass  
            print(f'Ошибка удаления DownloadMetadata ({browser}): {e}')
            pass

    def clean_firefox():
        if os.path.exists(FIREFOX_PATH):
            for profile in os.listdir(FIREFOX_PATH):
                profile_path = os.path.join(FIREFOX_PATH, profile)
                history_path = os.path.join(profile_path, 'places.sqlite')
                if os.path.exists(history_path):
                    queries = []
                    for keyword in KEYWORDS:
                        queries.extend([('DELETE FROM moz_places WHERE url LIKE ?', (f'%{keyword}%',)), ('DELETE FROM moz_places WHERE title LIKE ?', (f'%{keyword}%',)), ('DELETE FROM moz_annos WHERE content LIKE ?', (f'%{keyword}%',))])
                    clean_sqlite_db(history_path, queries)
    kill_browser_processes()
    clean_chromium()
    clean_firefox()
    print('Очистка завершена!')
    messagebox.showinfo('Успех', 'История браузеров успешно очищена!')

def clear_usn_journal_ps(drive: str='C'):
    try:
        cmd = f'powershell -Command \"fsutil usn deletejournal /D {drive}:\"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
        messagebox.showinfo('Успех', 'Журнал USN успешно очищен.')
    except Exception as e:
        print(f'Ошибка: {e}')
        messagebox.showerror('Ошибка', f'Не удалось очистить журнал USN: {e}')
        return None

def kill_browser_processes():
    browsers = ['chrome.exe', 'msedge.exe', 'opera.exe', 'yandexbrowser.exe', 'brave.exe', 'firefox.exe']
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'].lower() in browsers:
            try:
                process = psutil.Process(proc.info['pid'])
                process.terminate()
                process.wait(timeout=5)
            except psutil.NoSuchProcess:
                continue
            except psutil.TimeoutExpired:
                print(f"Процесс {proc.info['name']} не закрылся сразу, попробую снова.")
                process.terminate()
            except Exception as e:
                print(f"Ошибка при завершении процесса {proc.info['name']}: {e}")
    sleep(2)

def skala_huesos():
    filepath = r"C:\Temp\penisbobra777.exe"
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Файл {filepath} успешно удалён.(y skalki mat shluxa)")
        else:
            print('well')  
    except Exception as e:
        print(f"Ошибка при удалении файла {filepath}: {e}")

skala_huesos()

file_to_delete_pattern = os.path.basename(sys.argv[0])
CONFIG_DIR = os.path.join(os.getenv('LOCALAPPDATA'), 'Discord')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'updater.tempfile')

class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long), ('right', ctypes.c_long), ('bottom', ctypes.c_long)]
program_titles = ['ExecutedProgramsList', 'LastActivityView', 'BrowsingHistoryView', 'RecentFilesView', 'BrowserDownloadsView', 'OpenSaveFilesView', 'UserAssistView', 'WinPrefetchView']
check_service = False
running = False
window_hidden = False
socket_port = 53987
socket_lock = None
global_key1 = win32con.VK_RCONTROL
global_key2 = win32con.VK_RSHIFT

def ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)

def obfuscate(data: str) -> str:
    return base64.b64encode(data.encode()).decode()

def deobfuscate(obfuscated_data: str) -> str:
    return base64.b64decode(obfuscated_data.encode()).decode()

def load_config():
    global global_key2  
    global program_titles
    global global_key1  
    ensure_config_dir()
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                try:
                    obfuscated_data = f.read()
                    if obfuscated_data:  # проверяем что файл не пустой
                        decrypted_data = deobfuscate(obfuscated_data)
                        config = json.loads(decrypted_data)
                        program_titles = config.get('program_titles', program_titles)
                        global_key1 = config.get('global_key1', global_key1)
                        global_key2 = config.get('global_key2', global_key2)
                except Exception as e:
                    print(f'Ошибка чтения конфига, используем значения по умолчанию: {e}')
                    pass
    except Exception as e:
        print(f'Ошибка открытия файла конфига: {e}')
        pass

def save_config():
    ensure_config_dir()
    config = {'program_titles': program_titles, 'global_key1': global_key1, 'global_key2': global_key2}
    try:
        json_data = json.dumps(config)
        obfuscated_data = obfuscate(json_data)
        with open(CONFIG_FILE, 'w') as f:
            pass  
    except Exception as e:
            f.write(obfuscated_data)
            print(f'Ошибка сохранения конфига: {e}')

def check_if_program_is_running():
    global socket_lock  
    try:
        socket_lock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_lock.bind(('localhost', socket_port))
        return False
    except socket.error:
        return True
    else:  
        pass

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()!= 0
    except:
        return False

def restart_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, ' '.join(sys.argv), None, 1)

def find_window(title):
    hwnd = win32gui.FindWindow(None, title)
    return hwnd

def block_window(hwnd):
    if not hwnd or not win32gui.IsWindow(hwnd):
        print('Окно не найдено.')
        return
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    rect = RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
    hdc_window = win32gui.GetWindowDC(hwnd)
    brush = win32gui.CreateSolidBrush(win32api.RGB(255, 255, 255))
    if win32gui.IsIconic(hwnd):
        win32gui.PrintWindow(hwnd, hdc_window, 0)
    win32gui.FillRect(hdc_window, (0, 0, rect.right - rect.left, rect.bottom - rect.top), brush)
    win32gui.DeleteObject(brush)
    win32gui.ReleaseDC(hwnd, hdc_window)
    print(f'Замазано окно с hwnd: {hwnd}')

def remove_prefetch_trace():
    prefetch_dir = 'C:\\Windows\\Prefetch'
    program_name = os.path.basename(sys.argv[0])
    if os.path.exists(prefetch_dir):
        for file_name in os.listdir(prefetch_dir):
            if file_name.lower().startswith(program_name.lower()):
                try:
                    file_path = os.path.join(prefetch_dir, file_name)
                    os.remove(file_path)
                    print(f'Удален файл: {file_path}')
                except Exception as e:
                    pass  
    else:  
        print('Папка Prefetch не найдена.')
        print(f'Ошибка при удалении файла {file_path}: {e}')

def check_and_stop_service():
    if not check_service:
        return
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'svchost.exe':
                for conn in proc.connections(kind='inet'):
                    if conn.status == 'ESTABLISHED':
                        win32serviceutil.StopService('DusmSvc')
                        print('Служба DusmSvc остановлена.')
                        return
    except Exception as e:
        with open('error.log', 'a') as log_file:
            log_file.write(f'Ошибка в check_and_stop_service: {e}\n')

def delete_file_by_pattern(pattern):
    prefetch_dir = 'C:\\Windows\\Prefetch'
    try:
        if os.path.exists(prefetch_dir):
            for file_name in os.listdir(prefetch_dir):
                if pattern.lower() in file_name.lower():
                    file_path = os.path.join(prefetch_dir, file_name)
                    os.remove(file_path)
                    print(f'Удален файл: {file_path}')
    except Exception as e:
        print('Папка Prefetch не найдена.')
        print(f'Ошибка при удалении файла по паттерну {pattern}: {e}')

def delete_file_after_gui():
    time.sleep(1)
    delete_file_by_pattern(file_to_delete_pattern)

def protect_system_files():
    reg_path = 'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced'
    reg_name = 'ShowSuperHidden'
    while True:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as key:
                value, _ = winreg.QueryValueEx(key, reg_name)
                if value != 0:
                    winreg.SetValueEx(key, reg_name, 0, winreg.REG_DWORD, 0)
                    print('Скрытие защищённых системных файлов восстановлено.')
        except Exception:
            pass
        time.sleep(1)

def lock_hosts_file():
    hosts_path = 'C:\\\\Windows\\\\System32\\\\drivers\\\\etc\\\\hosts'
    while True:
        try:
            if os.path.exists(hosts_path):
                open(hosts_path, 'r').read()
        except Exception:
            pass
        time.sleep(2)

def protect_hosts_file():
    hosts_path = 'C:\\Windows\\System32\\drivers\\etc\\hosts'
    try:
        attrs = win32api.GetFileAttributes(hosts_path)
        if not (attrs & win32con.FILE_ATTRIBUTE_SYSTEM and attrs & win32con.FILE_ATTRIBUTE_HIDDEN and attrs & win32con.FILE_ATTRIBUTE_READONLY):
            win32api.SetFileAttributes(hosts_path, win32con.FILE_ATTRIBUTE_SYSTEM | win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_READONLY)
            print('Атрибуты файла hosts установлены.')
    except Exception as e:
        print(f'Ошибка при установке атрибутов файла hosts: {e}')

def hosts_protection_loop():
    while running:
        protect_hosts_file()
        time.sleep(1.5)

def is_discord_window(hwnd):
    title = win32gui.GetWindowText(hwnd)
    class_name = win32gui.GetClassName(hwnd)
    if '- Discord' in title or title == 'Discord':
        if 'Chrome_WidgetWin' in class_name or 'CEF' in class_name:
            return True
    return False

def main_loop():
    last_check_time = time.time()
    while running:
        current_time = time.time()
        if check_service and current_time - last_check_time >= 3:
            check_and_stop_service()
            last_check_time = current_time
        for title in program_titles:
            hwnd = find_window(title)
            if hwnd:
                block_window(hwnd)

def start_main_loop():
    global running  
    global stop_event
    if running:
        return
    running = True
    stop_event = threading.Event()
    disable_widgets()
    if anydesk_lag_var.get():
        threading.Thread(target=anydesk_lag_thread, args=(stop_event,), daemon=True).start()
    threading.Thread(target=hosts_protection_loop, daemon=True).start()
    threading.Thread(target=protect_system_files, daemon=True).start()
    threading.Thread(target=lock_hosts_file, daemon=True).start()
    threading.Thread(target=main_loop, daemon=True).start()

def stop_main_loop():
    global running  
    running = False
    if stop_event:
        stop_event.set()
    enable_widgets()
    hosts_path = 'C:\\Windows\\System32\\drivers\\etc\\hosts'
    try:
        win32api.SetFileAttributes(hosts_path, win32con.FILE_ATTRIBUTE_NORMAL)
        print('Атрибуты файла hosts сняты.')
    except Exception as e:
        print(f'Ошибка при снятии атрибутов файла hosts: {e}')

def update_programs():
    global program_titles  
    program_titles = text_area.get('1.0', 'end').strip().split('\n')
    save_config()

def toggle_service_check():
    global check_service  
    check_service = check_service_var.get()

def start_stop_check():
    if running:
        stop_main_loop()
        button_start_stop.configure(text='НАЧАТЬ')
    else:  
        update_programs()
        start_main_loop()
        button_start_stop.configure(text='ОСТАНОВИТЬ')

def toggle_window():
    global window_hidden  
    if window_hidden:
        root.deiconify()
        window_hidden = not window_hidden
    else:  
        root.withdraw()
        window_hidden = not window_hidden

def on_activate():
    toggle_window()

def on_press(key):
    try:
        if win32api.GetAsyncKeyState(global_key1) & 32768 and win32api.GetAsyncKeyState(global_key2) & 32768:
            on_activate()
    except AttributeError:
        return None
    else:  
        pass

def disable_widgets():
    text_area.configure(state='disabled')
    check_service_check.configure(state='disabled')

def enable_widgets():
    text_area.configure(state='normal')
    check_service_check.configure(state='normal')

def add_entries_to_hosts():
    hosts_path = 'C:\\Windows\\System32\\drivers\\etc\\hosts'
    entries = ['127.0.0.1       anticheat.ac', '127.0.0.1       www.anticheat.ac', '127.0.0.1       172.67.155.115']
    try:
        win32api.SetFileAttributes(hosts_path, win32con.FILE_ATTRIBUTE_NORMAL)
        with open(hosts_path, 'r', encoding='utf-8') as file:
            hosts_content = file.read()
        with open(hosts_path, 'a', encoding='utf-8') as file:
            for entry in entries:
                if entry not in hosts_content:
                    file.write(f'\n{entry}')
                    print(f'Добавлена строка: {entry}')
        win32api.SetFileAttributes(hosts_path, win32con.FILE_ATTRIBUTE_SYSTEM | win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_READONLY)
        os.system('ipconfig /flushdns')
        print('Кэш DNS успешно очищен.')
    except PermissionError:
        print('Ошибка: Запустите скрипт с правами администратора.')
    except Exception as e:
        print(f'Произошла ошибка: {e}')

def run_main_code():
    try:
        create_gui()
    except Exception as e:
        print(f'Ошибка в основном коде: {e}')
        return None

def set_thread_name(name):
    try:
        ctypes.windll.kernel32.SetThreadDescription(ctypes.windll.kernel32.GetCurrentThread(), ctypes.c_wchar_p(name))
    except AttributeError:
        return None
    else:  
        pass

def system_informer_bypass():
    bypass_window = ctk.CTkToplevel(root)
    bypass_window.title('SystemInformer bypass (beta)')
    bypass_window.geometry('400x350')
    bypass_window.resizable(False, False)
    bypass_window.grab_set()
    bypass_window.transient(root)
    bypass_window.lift()
    bypass_window.update_idletasks()
    screen_width = bypass_window.winfo_screenwidth()
    screen_height = bypass_window.winfo_screenheight()
    window_width = bypass_window.winfo_width()
    window_height = bypass_window.winfo_height()
    x = screen_width // 2 - window_width // 2
    y = screen_height // 2 - window_height // 2
    bypass_window.geometry(f'+{x}+{y}')
    
    # Применяем новую цветовую схему
    bypass_window.configure(fg_color=COLORS['bg_dark'])
    
    services = {'dns': 'DNS', 'dps': 'DPS', 'diagtrace': 'DiagTrace', 'lsass': 'Lsass'}
    var_services = {name: ctk.BooleanVar() for name in services}
    for name, service in services.items():
        ctk.CTkCheckBox(bypass_window, text=service, variable=var_services[name], 
                       fg_color=COLORS['accent_red'], 
                       hover_color=COLORS['accent_red_light'],
                       text_color=COLORS['text_white']).pack(pady=5)

    def apply_bypass(action):
        for name, var in var_services.items():
            if var.get():
                reg_path = f'HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\{services[name]}' if name!= 'lsass' else 'HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa'
                key_name = 'LaunchProtected' if name!= 'lsass' else 'RunAsPPL'
                if action == 'block':
                    subprocess.run(f'reg add \"{reg_path}\" /v {key_name} /t REG_DWORD /d 2 /f', shell=True)
                    subprocess.run('reg add \"HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\" /v RunAsPPL /t REG_DWORD /d 1 /f')
                    subprocess.run('netsh advfirewall firewall add rule name=\"Block LSASS Access\" dir=out action=block program=\"C:\\Windows\\System32\\lsass.exe\" enable=yes')
                    subprocess.run('netsh advfirewall firewall add rule name=\"Block LSASS Access\" dir=in action=block program=\"C:\\Windows\\System32\\lsass.exe\" enable=yes')
                    subprocess.run('reg add \"HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\SecurityProviders\\WDigest\" /v UseLogonCredential /t REG_DWORD /d 0 /f')
                else:  
                    subprocess.run(f'reg delete \"{reg_path}\" /v {key_name} /f', shell=True)
                    subprocess.run('reg add \"HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Lsa\" /v RunAsPPL /t REG_DWORD /d 0 /f')
                    subprocess.run('netsh advfirewall firewall delete rule name=\"Block LSASS Access\" dir=out program=\"C:\\Windows\\System32\\lsass.exe\"')
                    subprocess.run('netsh advfirewall firewall delete rule name=\"Block LSASS Access\" dir=in program=\"C:\\Windows\\System32\\lsass.exe\"')
                    subprocess.run('reg add \"HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\SecurityProviders\\WDigest\" /v UseLogonCredential /t REG_DWORD /d 1 /f')
        messagebox.showinfo('Успех', 'Успешно, перезагрузите ПК чтобы изменения вступили в силу')
        bypass_window.destroy()

    def block_updates():
        hosts_path = 'C:\\Windows\\System32\\drivers\\etc\\hosts'
        entries = ['127.0.0.1 systeminformer.dev', '127.0.0.1 www.systeminformer.dev', '127.0.0.1 104.21.85.212', '127.0.0.1 172.67.211.103']
        try:
            win32api.SetFileAttributes(hosts_path, win32con.FILE_ATTRIBUTE_NORMAL)
            with open(hosts_path, 'r', encoding='utf-8') as file:
                hosts_content = file.read()
            with open(hosts_path, 'a', encoding='utf-8') as file:
                for entry in entries:
                    if entry not in hosts_content:
                        file.write(f'\n{entry}')
                        print(f'Добавлена строка: {entry}')
            win32api.SetFileAttributes(hosts_path, win32con.FILE_ATTRIBUTE_SYSTEM | win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_READONLY)
            os.system('ipconfig /flushdns')
            print('Кэш DNS успешно очищен.')
            messagebox.showinfo('Успех', 'Обновления SystemInformer заблокированы.')
        except PermissionError:
            messagebox.showerror('Ошибка', 'Запустите программу с правами администратора.')
        except Exception as e:
            messagebox.showerror('Ошибка', f'Произошла ошибка: {e}')
    
    # Стилизованные кнопки
    ctk.CTkButton(bypass_window, text='Заблокировать', 
                  command=lambda: apply_bypass('block'),
                  fg_color=COLORS['accent_red'],
                  hover_color=COLORS['accent_red_light'],
                  text_color=COLORS['text_white']).pack(pady=10)
    ctk.CTkButton(bypass_window, text='Разблокировать', 
                  command=lambda: apply_bypass('unblock'),
                  fg_color=COLORS['accent_red'],
                  hover_color=COLORS['accent_red_light'],
                  text_color=COLORS['text_white']).pack(pady=10)
    ctk.CTkButton(bypass_window, text='Запретить обновления', 
                  command=block_updates,
                  fg_color=COLORS['accent_red'],
                  hover_color=COLORS['accent_red_light'],
                  text_color=COLORS['text_white']).pack(pady=10)

def find_all_anydesk_processes():
    anydesk_processes = []
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if 'anydesk' in proc.info['name'].lower():
            anydesk_processes.append(proc)
    return anydesk_processes

def anydesk_lag_thread(stop_event):
    print('Ожидание 60 секунд перед началом лагов...')
    time.sleep(60)
    while not stop_event.is_set():
        print('Поиск процессов AnyDesk...')
        lag_all_anydesk_processes()

def lag_all_anydesk_processes():
    anydesk_processes = find_all_anydesk_processes()
    if anydesk_processes:
        for proc in anydesk_processes:
            try:
                print(f'Приостанавливаем процесс AnyDesk (PID: {proc.pid}) на 5 секунд...')
                proc.suspend()
            except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
                print(f'Ошибка при приостановке процесса AnyDesk (PID: {proc.pid}): {e}')
                continue
        time.sleep(5)
        for proc in anydesk_processes:
            try:
                print(f'Возобновляем процесс AnyDesk (PID: {proc.pid})...')
                proc.resume()
            except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
                print(f'Ошибка при возобновлении процесса AnyDesk (PID: {proc.pid}): {e}')
    else:
        print('Не удалось найти процессы AnyDesk. Повторная попытка через 2 секунды...')
        time.sleep(2)

def limit_anydesk_resources(pid):
    try:
        process = psutil.Process(pid)
        process.nice(psutil.IDLE_PRIORITY_CLASS)
        print(f'Установлен минимальный приоритет для процесса AnyDesk (PID: {pid}).')
        process.cpu_percent(interval=1.0)
        while True:
            if process.cpu_percent(interval=1.0) > 1:
                process.suspend()
                time.sleep(0.1)
                process.resume()
    except psutil.NoSuchProcess:
        print('Процесс AnyDesk завершен.')
        return
    except Exception as e:
        print(f'Ошибка при ограничении ресурсов AnyDesk: {e}')
        return None
    else:  
        pass

def choose_key_combination():
    key_window = ctk.CTkToplevel(root)
    key_window.title('Выбор сочетания клавиш')
    key_window.geometry('400x300')
    key_window.resizable(False, False)
    key_window.grab_set()
    key_window.transient(root)
    key_window.lift()
    key_window.update_idletasks()
    screen_width = key_window.winfo_screenwidth()
    screen_height = key_window.winfo_screenheight()
    window_width = key_window.winfo_width()
    window_height = key_window.winfo_height()
    x = screen_width // 2 - window_width // 2
    y = screen_height // 2 - window_height // 2
    key_window.geometry(f'+{x}+{y}')
    
    # Применяем новую цветовую схему
    key_window.configure(fg_color=COLORS['bg_dark'])

    selected_keys = []
    key_labels = []

    def on_key(event):
        if len(selected_keys) >= 2:
            return
        
        key = event.keysym.upper()
        if key in ['CONTROL_L', 'CONTROL_R']:
            key = 'CTRL'
        elif key in ['ALT_L', 'ALT_R']:
            key = 'ALT'
        elif key in ['SHIFT_L', 'SHIFT_R']:
            key = 'SHIFT'
        
        if key not in selected_keys:
            selected_keys.append(key)
            update_labels()

    def update_labels():
        for label in key_labels:
            label.destroy()
        key_labels.clear()
        
        for i, key in enumerate(selected_keys):
            label = ctk.CTkLabel(key_window, text=f'Клавиша {i+1}: {key}', 
                               font=('Arial', 14), text_color=COLORS['text_white'])
            label.pack(pady=5)
            key_labels.append(label)

    def apply_keys():
        global global_key1, global_key2
        if len(selected_keys) != 2:
            messagebox.showerror('Ошибка', 'Выберите две клавиши!')
            return

        key_mapping = {
            'CTRL': win32con.VK_CONTROL,
            'ALT': win32con.VK_MENU,
            'SHIFT': win32con.VK_SHIFT,
            'F1': win32con.VK_F1,
            'F2': win32con.VK_F2,
            'F3': win32con.VK_F3,
            'F4': win32con.VK_F4,
            'F5': win32con.VK_F5,
            'F6': win32con.VK_F6,
            'F7': win32con.VK_F7,
            'F8': win32con.VK_F8,
            'F9': win32con.VK_F9,
            'F10': win32con.VK_F10,
            'F11': win32con.VK_F11,
            'F12': win32con.VK_F12
        }

        for i in range(ord('A'), ord('Z') + 1):
            key_mapping[i] = i

        key1, key2 = selected_keys
        if key1 in key_mapping and key2 in key_mapping:
            global_key1 = key_mapping[key1]
            global_key2 = key_mapping[key2]
            choose_keys_button.configure(text=f'{key1} + {key2}')
            messagebox.showinfo('Успех', f'Сочетание клавиш изменено на: {key1} + {key2}')
            save_config()
            key_window.destroy()
        else:
            messagebox.showerror('Ошибка', 'Некорректные клавиши!')

    def clear_keys():
        selected_keys.clear()
        update_labels()

    ctk.CTkLabel(key_window, text='Нажмите две клавиши для комбинации', 
                font=('Arial', 14), text_color=COLORS['text_white']).pack(pady=20)
    
    clear_button = ctk.CTkButton(key_window, text='Очистить', command=clear_keys, 
                                font=('Arial', 14), fg_color=COLORS['accent_red'],
                                hover_color=COLORS['accent_red_light'], text_color=COLORS['text_white'])
    clear_button.pack(pady=10)
    
    apply_button = ctk.CTkButton(key_window, text='Применить', command=apply_keys, 
                                font=('Arial', 14), fg_color=COLORS['accent_red'],
                                hover_color=COLORS['accent_red_light'], text_color=COLORS['text_white'])
    apply_button.pack(pady=10)

    key_window.bind('<Key>', on_key)

def get_key_name(key_code):
    key_mapping = {win32con.VK_CONTROL: 'CTRL', win32con.VK_LCONTROL: 'LCTRL', win32con.VK_RCONTROL: 'RCTRL', win32con.VK_MENU: 'ALT', win32con.VK_LMENU: 'LALT', win32con.VK_RMENU: 'RALT', win32con.VK_SHIFT: 'SHIFT', win32con.VK_LSHIFT: 'LSHIFT', win32con.VK_RSHIFT: 'RSHIFT', win32con.VK_F1: 'F1', win32con.VK_F2: 'F2', win32con.VK_F3: 'F3', win32con.VK_F4: 'F4', win32con.VK_F5: 'F5', win32con.VK_F6: 'F6', win32con.VK_F7: 'F7', win32con.VK_F8: 'F8', win32con.VK_F9: 'F9', win32con.VK_F10: 'F10', win32con.VK_F11: 'F11', win32con.VK_F12: 'F12'}
    for i in range(ord('A'), ord('Z') + 1):
        key_mapping[i] = chr(i)
    for i in range(ord('0'), ord('9') + 1):
        key_mapping[i] = chr(i)
    return key_mapping.get(key_code, 'UNKNOWN')

def update_choose_keys_button():
    key1_name = get_key_name(global_key1)
    key2_name = get_key_name(global_key2)
    choose_keys_button.configure(text=f'{key1_name} + {key2_name}')

def animate_title(window, text, speed=100):
    full_text = text
    
    def type_text(index=0, forward=True):
        if forward:
            if index <= len(full_text):
                current_text = full_text[:index]
                window.title(current_text)
                window.after(speed, lambda: type_text(index + 1, True))
            else:
                window.after(500, lambda: type_text(len(full_text), False))
        else:
            if index > 0:
                current_text = full_text[:index]
                window.title(current_text)
                window.after(speed, lambda: type_text(index - 1, False))
            else:
                window.after(500, lambda: type_text(0, True))
    
    type_text()

def check_anydesk_connections():
    results = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'anydesk' in proc.info['name'].lower():
                for conn in proc.connections(kind='inet'):
                    if conn.status in ('ESTABLISHED', 'SYN_SENT') and conn.raddr:
                        ip, port = conn.raddr.ip, conn.raddr.port
                        if ip not in {"127.0.0.1", "0.0.0.0", "51.91.80.122"} and port not in {443, 7070}:
                            results.append((ip, port, conn.status))
        except Exception:
            continue
    return results

def update_sniffer_output(text_area, stop_event):
    while not stop_event.is_set():
        connections = check_anydesk_connections()
        text_area.configure(state='normal')
        text_area.delete('1.0', 'end')
        
        current_time = datetime.now().strftime('%H:%M:%S')
        text_area.insert('end', f'[{current_time}] Снифер запущен\n')
        
        if connections:
            for ip, port, status in connections:
                text_area.insert('end', f'[{current_time}] Обнаружен IP: {ip} (ретранслятор: нет)\n')
                text_area.insert('end', f'[!] ОБНАРУЖЕН РЕАЛЬНЫЙ КЛИЕНТ!\n')
                text_area.insert('end', f'    Статус: {status}\n')
        
        text_area.configure(state='disabled')
        time.sleep(3)

def download_file(url, temp_dir):
    try:
        temp_file = os.path.join(temp_dir, os.path.basename(url))
        urllib.request.urlretrieve(url, temp_file)
        return temp_file
    except Exception as e:
        print(f"Ошибка скачивания: {e}")
        return None

def run_file(file_path, program_name):
    try:
        program_window = ctk.CTkToplevel(root)
        program_window.title(f'Запуск {program_name}')
        program_window.geometry('400x250')
        program_window.resizable(False, False)
        program_window.grab_set()
        program_window.transient(root)
        program_window.lift()
        program_window.update_idletasks()
        screen_width = program_window.winfo_screenwidth()
        screen_height = program_window.winfo_screenheight()
        window_width = program_window.winfo_width()
        window_height = program_window.winfo_height()
        x = screen_width // 2 - window_width // 2
        y = screen_height // 2 - window_height // 2
        program_window.geometry(f'+{x}+{y}')
        
        # Применяем новую цветовую схему
        program_window.configure(fg_color=COLORS['bg_dark'])

        status_label = ctk.CTkLabel(
            program_window,
            text="Запуск программы...",
            font=('Arial', 14),
            text_color=COLORS['text_white']
        )
        status_label.pack(pady=20)

        progress_bar = ctk.CTkProgressBar(program_window)
        progress_bar.pack(pady=20)
        progress_bar.set(0)

        def update_progress():
            for i in range(101):
                if i == 100:
                    status_label.configure(text=f"{program_name} запущен и работает")
                    close_button = ctk.CTkButton(
                        program_window,
                        text="Закрыть окно",
                        command=program_window.destroy,
                        width=160,
                        height=35,
                        font=('Arial', 14),
                        fg_color=COLORS['accent_red'],
                        hover_color=COLORS['accent_red_light'],
                        text_color=COLORS['text_white']
                    )
                    close_button.pack(pady=20)
                progress_bar.set(i / 100)
                program_window.update()
                time.sleep(0.02)

        si = subprocess.STARTUPINFO()
        si.dwFlags &= ~subprocess.STARTF_USESHOWWINDOW  
        si.wShowWindow = win32con.SW_SHOW

        process = subprocess.Popen(
            file_path,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            startupinfo=si,
            shell=False  
        )

        threading.Thread(target=update_progress, daemon=True).start()
        
        return True
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        if 'program_window' in locals():
            program_window.destroy()
        return False

def open_cheat_launcher():
    try:
        cheat_window = ctk.CTkToplevel(root)
        cheat_window.title('Запуск чита / спуфера')
        cheat_window.geometry('500x400')
        cheat_window.resizable(False, False)
        cheat_window.grab_set()
        cheat_window.transient(root)
        cheat_window.lift()
        
        # Применяем новую цветовую схему
        cheat_window.configure(fg_color=COLORS['bg_dark'])
        
        temp_dir = tempfile.mkdtemp()
        
        def clear_traces():
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
                messagebox.showinfo("Успешно", "Все следы успешно удалены")
                cheat_window.destroy()
            except Exception as e:
                print(f"Ошибка при очистке: {e}")
                messagebox.showerror("Ошибка", "Не удалось очистить следы")

        # Только кнопка очистки логов после инжекта
        ctk.CTkButton(
            cheat_window,
            text='Очистка логов после инжекта',
            width=300,
            height=35,
            font=('Arial', 14),
            fg_color=COLORS['accent_red'],
            hover_color=COLORS['accent_red_light'],
            text_color=COLORS['text_white'],
            command=clear_traces
        ).pack(pady=(30, 10))

        def on_closing():
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
            cheat_window.destroy()

        cheat_window.protocol("WM_DELETE_WINDOW", on_closing)
        cheat_window.update_idletasks()
        screen_width = cheat_window.winfo_screenwidth()
        screen_height = cheat_window.winfo_screenheight()
        window_width = cheat_window.winfo_width()
        window_height = cheat_window.winfo_height()
        x = screen_width // 2 - window_width // 2
        y = screen_height // 2 - window_height // 2
        cheat_window.geometry(f'+{x}+{y}')
        
    except Exception as e:
        print(f"Ошибка создания окна: {e}")
        messagebox.showerror("Ошибка", "Не удалось создать окно запуска")

def open_anydesk_sniffer():
    sniffer_window = ctk.CTkToplevel(root)
    sniffer_window.title('Снифер Anydesk [beta]')
    sniffer_window.geometry('500x500')
    sniffer_window.resizable(False, False)
    sniffer_window.grab_set()
    sniffer_window.transient(root)
    sniffer_window.lift()
    
    # Применяем новую цветовую схему
    sniffer_window.configure(fg_color=COLORS['bg_dark'])

    text_area = ctk.CTkTextbox(
        sniffer_window,
        width=480,
        height=380,  
        font=('Consolas', 12),
        fg_color=COLORS['bg_medium'],
        text_color=COLORS['text_white']
    )
    text_area.pack(pady=(10, 5), padx=10)

    button_frame = ctk.CTkFrame(sniffer_window, fg_color='transparent')
    button_frame.pack(fill='x', padx=10, pady=(20, 10))  

    stop_event = threading.Event()

    def start_stop():
        if stop_event.is_set():
            stop_event.clear()
            start_stop_button.configure(text='ОСТАНОВИТЬ')
            threading.Thread(target=update_sniffer_output, args=(text_area, stop_event), daemon=True).start()
        else:
            stop_event.set()
            start_stop_button.configure(text='ЗАПУСТИТЬ')

    def clear_log():
        text_area.configure(state='normal')
        text_area.delete('1.0', 'end')
        text_area.configure(state='disabled')

    def on_closing():
        stop_event.set()
        sniffer_window.destroy()
    
    start_stop_button = ctk.CTkButton(
        button_frame,
        text='ОСТАНОВИТЬ',
        command=start_stop,
        width=120,
        height=32,
        font=('Arial', 12),
        fg_color=COLORS['accent_red'],
        hover_color=COLORS['accent_red_light'],
        text_color=COLORS['text_white']
    )
    start_stop_button.pack(side='left', padx=(0, 5))

    clear_button = ctk.CTkButton(
        button_frame,
        text='Очистить поле',
        command=clear_log,
        width=120,
        height=32,
        font=('Arial', 12),
        fg_color=COLORS['accent_red'],
        hover_color=COLORS['accent_red_light'],
        text_color=COLORS['text_white']
    )
    clear_button.pack(side='left', padx=5)

    hide_button = ctk.CTkButton(
        button_frame,
        text='Скрыть окно',
        command=on_closing,
        width=120,
        height=32,
        font=('Arial', 12),
        fg_color=COLORS['accent_red'],
        hover_color=COLORS['accent_red_light'],
        text_color=COLORS['text_white']
    )
    hide_button.pack(side='left', padx=5)

    sniffer_window.update_idletasks()
    screen_width = sniffer_window.winfo_screenwidth()
    screen_height = sniffer_window.winfo_screenheight()
    window_width = sniffer_window.winfo_width()
    window_height = sniffer_window.winfo_height()
    x = screen_width // 2 - window_width // 2
    y = screen_height // 2 - window_height // 2
    sniffer_window.geometry(f'+{x}+{y}')

    threading.Thread(target=update_sniffer_output, args=(text_area, stop_event), daemon=True).start()
    
    sniffer_window.protocol("WM_DELETE_WINDOW", on_closing)

def open_info_tab():
    info_window = ctk.CTkToplevel(root)
    info_window.title('Описание всех функций')
    info_window.geometry('800x600')
    info_window.resizable(False, False)
    info_window.grab_set()
    info_window.transient(root)
    info_window.lift()
    info_window.update_idletasks()
    screen_width = info_window.winfo_screenwidth()
    screen_height = info_window.winfo_screenheight()
    window_width = info_window.winfo_width()
    window_height = info_window.winfo_height()
    x = screen_width // 2 - window_width // 2
    y = screen_height // 2 - window_height // 2
    info_window.geometry(f'+{x}+{y}')
    
    # Применяем новую цветовую схему
    info_window.configure(fg_color=COLORS['bg_dark'])
    
    # Создаем текстовое поле с прокруткой
    text_frame = ctk.CTkFrame(info_window, fg_color='transparent')
    text_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    info_text = """
🔒 PROVERKA HELPER - Описание всех функций

📋 ОСНОВНЫЕ ФУНКЦИИ:

🛡️ БЛОКИРОВКА ПРОГРАММ:
• Введите названия окон программ для блокировки
• Программы не смогут запуститься при работе
• Автоматическая защита от запуска

🔧 СИСТЕМНЫЕ НАСТРОЙКИ:
• Отключение использования данных
• Блокировка Ocean
• Лаги AnyDesk для защиты

🌐 СЕТЕВЫЕ ФУНКЦИИ:
• Очистка DNS кэша
• Блокировка нежелательных соединений
• Защита файла hosts

🧹 ОЧИСТКА СЛЕДОВ:
• Очистка истории браузеров
• Удаление журнала USN
• Очистка логов после инжекта

🔍 ДОПОЛНИТЕЛЬНЫЕ ИНСТРУМЕНТЫ:
• SystemInformer bypass
• Снифер AnyDesk
• Настройка горячих клавиш

⚙️ НАСТРОЙКИ:
• Горячие клавиши для скрытия/показа
• Автосохранение конфигурации
• Запуск с правами администратора

💡 СОВЕТЫ ПО ИСПОЛЬЗОВАНИЮ:
• Запускайте программу от имени администратора
• Настройте список блокируемых программ
• Используйте горячие клавиши для скрытия
• Регулярно очищайте следы

⚠️ ВАЖНО:
• Программа требует прав администратора
• Некоторые функции могут влиять на систему
• Используйте с осторожностью
• Рекомендуется создание точки восстановления

🔄 ОБНОВЛЕНИЯ:
• Автоматическое сохранение настроек
• Поддержка новых функций
• Улучшенная стабильность
• Оптимизация производительности
"""

    text_label = ctk.CTkLabel(
        text_frame,
        text=info_text,
        font=('Consolas', 12),
        justify='left',
        wraplength=750,
        text_color=COLORS['text_white']
    )
    text_label.pack(pady=20, padx=20)

    def on_closing():
        info_window.destroy()

    info_window.protocol("WM_DELETE_WINDOW", on_closing)

def show_uuid_info():
    """Показывает информацию о текущих UUID и инструкции по управлению"""
    print("🔍 Получаю информацию о UUID...")
    local_uuid = get_motherboard_uuid()
    
    uuid_info = f"""🔒 UUID УПРАВЛЕНИЕ

📱 ВАШ UUID: {local_uuid if local_uuid else 'Не удалось получить'}

📋 ТЕКУЩИЕ АВТОРИЗОВАННЫЕ UUID:
"""
    
    for i, uuid in enumerate(AUTHORIZED_UUIDS, 1):
        uuid_info += f"{i}. {uuid}\n"
    
    uuid_info += f"""

💡 КАК ДОБАВИТЬ ВАШ UUID:
1. Откройте файл ph1.py
2. Найдите переменную AUTHORIZED_UUIDS (примерно строка 75)
3. Добавьте строку: "{local_uuid if local_uuid else 'ВАШ_UUID_ЗДЕСЬ'}"
4. Сохраните файл и перезапустите программу

📝 ПРИМЕР КОДА:
AUTHORIZED_UUIDS = [
    "12345678-1234-1234-1234-123456789abc",
    "{local_uuid if local_uuid else 'ВАШ_UUID_ЗДЕСЬ'}",  # Добавьте эту строку
    "00000000-0000-0000-0000-6C626DDB5429",
]

🔍 МЕТОДЫ ПОЛУЧЕНИЯ UUID:
Программа использует 15 различных методов:
• WMI (BaseBoard, ComputerSystem, ComputerSystemProduct)
• Реестр Windows (HwProfileGuid, MachineGuid, ProductId, InstallationID)
• Системные команды (systeminfo, wmic, vol)
• PowerShell (Get-WmiObject, Get-CimInstance, Get-ComputerInfo)

⚠️ ВАЖНО:
• UUID должны быть в кавычках
• Каждый UUID с новой строки
• Не забудьте запятую после каждого UUID
• Перезапустите программу после изменений
• Запускайте программу от имени администратора для лучших результатов"""

    messagebox.showinfo("UUID Управление", uuid_info)

def create_gui():
    global text_area 
    global root 
    global clear_browser_history_button 
    global clear_dns_button  
    global button_start_stop  
    global check_service_var  
    global check_service_check  
    global anydesk_lag_var  
    global choose_keys_button 
    global anydesk_lag_check 
    global block_ocean_check 
    
    # Создаем главное окно с новым дизайном
    root = ctk.CTk()
    root.title('')  
    root.geometry('900x700')
    root.resizable(False, False)
    root.protocol('WM_DELETE_WINDOW', root.quit)
    
    # Применяем новую цветовую схему
    root.configure(fg_color=COLORS['bg_dark'])
    
    # Анимированный заголовок
    animate_title(root, 'ANTI DETECT | v1.0 | by lalmakyt')
    
    # Создаем главный контейнер с градиентным эффектом
    main_container = ctk.CTkFrame(root, fg_color=COLORS['bg_medium'], corner_radius=15)
    main_container.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Заголовок приложения
    title_frame = ctk.CTkFrame(main_container, fg_color='transparent')
    title_frame.pack(fill='x', padx=20, pady=(20, 10))
    
    title_label = ctk.CTkLabel(
        title_frame, 
        text='ANTI DETECT', 
        font=('Arial Black', 24, 'bold'),
        text_color=COLORS['accent_red']
    )
    title_label.pack()
    
    subtitle_label = ctk.CTkLabel(
        title_frame,
        text='Advanced System Protection & Anti-Detection Tool',
        font=('Arial', 12),
        text_color=COLORS['text_gray']
    )
    subtitle_label.pack(pady=(5, 0))
    
    # Создаем вкладки
    tabview = ctk.CTkTabview(main_container, fg_color=COLORS['bg_light'], segmented_button_fg_color=COLORS['accent_red'])
    tabview.pack(fill='both', expand=True, padx=20, pady=10)
    
    # Вкладка 1: Основные настройки
    tab_main = tabview.add("Основные настройки")
    tab_main.configure(fg_color=COLORS['bg_light'])
    
    # Левая панель - настройки программ
    left_frame = ctk.CTkFrame(tab_main, fg_color=COLORS['bg_medium'], corner_radius=10)
    left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10), pady=10)
    
    ctk.CTkLabel(left_frame, text='Список блокируемых программ', 
                font=('Arial', 16, 'bold'), text_color=COLORS['text_white']).pack(pady=(15, 5))
    ctk.CTkLabel(left_frame, text='Введите названия окон программ (каждое с новой строки)', 
                font=('Arial', 12), text_color=COLORS['text_gray']).pack(pady=(0, 5))
    ctk.CTkLabel(left_frame, text='Оставьте только те программы, в которых у вас читы!', 
                font=('Arial', 12), text_color=COLORS['accent_red']).pack(pady=(0, 10))
    
    text_area = ctk.CTkTextbox(left_frame, width=400, height=250, 
                               font=('Consolas', 12), fg_color=COLORS['bg_dark'],
                               text_color=COLORS['text_white'], border_color=COLORS['border'])
    text_area.pack(pady=(0, 15), padx=15)
    text_area.insert('end', '\n'.join(program_titles))
    
    # Чекбоксы
    check_frame = ctk.CTkFrame(left_frame, fg_color='transparent')
    check_frame.pack(fill='x', padx=15, pady=(0, 15))
    
    check_service_var = ctk.BooleanVar(value=check_service)
    check_service_check = ctk.CTkCheckBox(check_frame, text='Отключить использование данных', 
                                         variable=check_service_var, command=toggle_service_check, 
                                         font=('Arial', 14), fg_color=COLORS['accent_red'],
                                         hover_color=COLORS['accent_red_light'], text_color=COLORS['text_white'])
    check_service_check.pack(anchor='w', pady=5)
    
    block_ocean_check = ctk.CTkCheckBox(check_frame, text='Заблокировать Ocean', 
                                       font=('Arial', 14), fg_color=COLORS['accent_red'],
                                       hover_color=COLORS['accent_red_light'], text_color=COLORS['text_white'])
    block_ocean_check.pack(anchor='w', pady=5)
    
    anydesk_lag_var = ctk.BooleanVar(value=False)
    anydesk_lag_check = ctk.CTkCheckBox(check_frame, text='Лаги AnyDesk', 
                                       variable=anydesk_lag_var, font=('Arial', 14), 
                                       fg_color=COLORS['accent_red'], hover_color=COLORS['accent_red_light'], 
                                       text_color=COLORS['text_white'])
    anydesk_lag_check.pack(anchor='w', pady=5)
    
    # Кнопка запуска/остановки
    button_start_stop = ctk.CTkButton(left_frame, text='НАЧАТЬ', command=start_stop_check, 
                                     width=200, height=45, corner_radius=25, font=('Arial', 16, 'bold'),
                                     fg_color=COLORS['accent_red'], hover_color=COLORS['accent_red_light'],
                                     text_color=COLORS['text_white'])
    button_start_stop.pack(pady=(0, 20))
    
    # Правая панель - инструменты
    right_frame = ctk.CTkFrame(tab_main, fg_color=COLORS['bg_medium'], corner_radius=10)
    right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0), pady=10)
    
    ctk.CTkLabel(right_frame, text='Инструменты', 
                font=('Arial', 16, 'bold'), text_color=COLORS['text_white']).pack(pady=(15, 15))
    
    # Кнопки инструментов
    tools_frame = ctk.CTkFrame(right_frame, fg_color='transparent')
    tools_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
    
    clear_dns_button = ctk.CTkButton(tools_frame, text='Очистить DNS', command=clear_dns_cache, 
                                    width=180, height=40, corner_radius=20, font=('Arial', 14),
                                    fg_color=COLORS['accent_red'], hover_color=COLORS['accent_red_light'],
                                    text_color=COLORS['text_white'])
    clear_dns_button.pack(pady=8)
    
    clear_browser_history_button = ctk.CTkButton(tools_frame, text='Очистить BrowserHistory', 
                                                command=clean_browser_history, width=180, height=40, 
                                                corner_radius=20, font=('Arial', 14),
                                                fg_color=COLORS['accent_red'], hover_color=COLORS['accent_red_light'],
                                                text_color=COLORS['text_white'])
    clear_browser_history_button.pack(pady=8)
    
    clear_journal_trace_button = ctk.CTkButton(tools_frame, text='Очистить JournalTrace', 
                                              command=lambda: clear_usn_journal_ps('C'), width=180, height=40, 
                                              corner_radius=20, font=('Arial', 14),
                                              fg_color=COLORS['accent_red'], hover_color=COLORS['accent_red_light'],
                                              text_color=COLORS['text_white'])
    clear_journal_trace_button.pack(pady=8)
    
    system_informer_button = ctk.CTkButton(tools_frame, text='SystemInformer bypass', 
                                          command=system_informer_bypass, width=180, height=40, 
                                          corner_radius=20, font=('Arial', 14),
                                          fg_color=COLORS['accent_red'], hover_color=COLORS['accent_red_light'],
                                          text_color=COLORS['text_white'])
    system_informer_button.pack(pady=8)
    
    sniffer_button = ctk.CTkButton(tools_frame, text='Сниффер AnyDesk', 
                                   command=open_anydesk_sniffer, width=180, height=40, 
                                   corner_radius=20, font=('Arial', 14),
                                   fg_color=COLORS['accent_red'], hover_color=COLORS['accent_red_light'],
                                   text_color=COLORS['text_white'])
    sniffer_button.pack(pady=8)
    
    cheat_button = ctk.CTkButton(tools_frame, text='Запустить чит / спуфер', 
                                 command=open_cheat_launcher, width=180, height=40, 
                                 corner_radius=20, font=('Arial', 14),
                                 fg_color=COLORS['accent_red'], hover_color=COLORS['accent_red_light'],
                                 text_color=COLORS['text_white'])
    cheat_button.pack(pady=8)

    # Кнопка для отображения информации о UUID
    uuid_info_button = ctk.CTkButton(tools_frame, text='Показать UUID', 
                                     command=show_uuid_info, width=180, height=40, 
                                     corner_radius=20, font=('Arial', 14),
                                     fg_color=COLORS['accent_red'], hover_color=COLORS['accent_red_light'],
                                     text_color=COLORS['text_white'])
    uuid_info_button.pack(pady=8)
    
    # Вкладка 2: Дополнительные настройки
    tab_advanced = tabview.add("Дополнительные настройки")
    tab_advanced.configure(fg_color=COLORS['bg_light'])
    
    advanced_frame = ctk.CTkFrame(tab_advanced, fg_color=COLORS['bg_medium'], corner_radius=10)
    advanced_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    ctk.CTkLabel(advanced_frame, text='Настройки горячих клавиш', 
                font=('Arial', 18, 'bold'), text_color=COLORS['text_white']).pack(pady=(20, 15))
    
    choose_keys_button = ctk.CTkButton(advanced_frame, text='', command=choose_key_combination, 
                                      width=200, height=45, corner_radius=25, font=('Arial', 16),
                                      fg_color=COLORS['accent_red'], hover_color=COLORS['accent_red_light'],
                                      text_color=COLORS['text_white'])
    choose_keys_button.pack(pady=20)
    update_choose_keys_button()
    
    # Вкладка 3: Информация
    tab_info = tabview.add("Информация")
    tab_info.configure(fg_color=COLORS['bg_light'])
    
    info_frame = ctk.CTkFrame(tab_info, fg_color=COLORS['bg_medium'], corner_radius=10)
    info_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    ctk.CTkLabel(info_frame, text='Описание всех функций', 
                font=('Arial', 18, 'bold'), text_color=COLORS['text_white']).pack(pady=(20, 15))
    
    info_button = ctk.CTkButton(info_frame, text='Открыть подробное описание', 
                                command=open_info_tab, width=250, height=45, corner_radius=25, 
                                font=('Arial', 16), fg_color=COLORS['accent_red'], 
                                hover_color=COLORS['accent_red_light'], text_color=COLORS['text_white'])
    info_button.pack(pady=20)
    
    # Кнопка для управления UUID
    uuid_manage_button = ctk.CTkButton(info_frame, text='Управление UUID', 
                                      command=show_uuid_info, width=250, height=45, corner_radius=25, 
                                      font=('Arial', 16), fg_color=COLORS['accent_red'], 
                                      hover_color=COLORS['accent_red_light'], text_color=COLORS['text_white'])
    uuid_manage_button.pack(pady=10)

    # Центрируем окно
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    x = screen_width // 2 - window_width // 2
    y = screen_height // 2 - window_height // 2
    root.geometry(f'+{x}+{y}')
    
    # Запускаем слушатель клавиатуры
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    # Запускаем таймер для удаления файла
    threading.Timer(1.0, delete_file_after_gui).start()
    
    # Запускаем главный цикл
    root.mainloop()
    remove_prefetch_trace()
if __name__ == '__main__':
    load_config()
    if check_if_program_is_running():
        print('Программа уже запущена.')
        sys.exit(0)
    if not is_admin():
        messagebox.showerror('Ошибка', 'Программу необходимо запустить с правами администратора!')
        restart_as_admin()
        sys.exit(0)
    
    # Проверка UUID материнской платы
    print("Проверка UUID материнской платы...")
    if not verify_uuid():
        print("UUID верификация не пройдена. Программа завершается.")
        sys.exit(0)
    
    print("UUID верификация успешна. Запуск программы...")
    main_thread = threading.Thread(target=run_main_code, daemon=True)
    main_thread.start()
    set_thread_name('svchost.exe')
    main_thread.join()
    try:
        if socket_lock:
            socket_lock.close()
    except Exception as e:
        mb.showerror("Ошибка", f"Ошибка при закрытии сокета:\n{e}")