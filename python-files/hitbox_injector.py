import win32process
import win32gui
import win32con
import keyboard
import time
import struct
from ctypes import windll, c_ulong, c_int, byref

# Находим процесс Minecraft
def find_minecraft_process():
    def enum_windows_proc(hwnd, lparam):
        if win32gui.GetWindowText(hwnd).lower().find("minecraft") != -1:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            lparam.append(pid)
        return True
    
    pids = []
    win32gui.EnumWindows(enum_windows_proc, pids)
    return pids[0] if pids else None

# Инъекция в процесс
def inject_code(pid, hitbox_size):
    process_handle = windll.kernel32.OpenProcess(0x1F0FFF, False, pid)
    if not process_handle:
        print("Не удалось открыть процесс!")
        return False
    
    # Адрес памяти для хитбоксов (гипотетический, требует отладки)
    HITBOX_ADDRESS = 0x12345678  # Замените на реальный адрес после анализа
    size_bytes = struct.pack("f", hitbox_size)
    
    written = c_ulong(0)
    windll.kernel32.WriteProcessMemory(
        process_handle, HITBOX_ADDRESS, size_bytes, len(size_bytes), byref(written)
    )
    
    windll.kernel32.CloseHandle(process_handle)
    return written.value > 0

# Основная логика
def main():
    print("Поиск Minecraft...")
    pid = find_minecraft_process()
    if not pid:
        print("Minecraft не найден! Запустите игру.")
        return
    
    hitbox_size = 1.0  # Начальный размер хитбокса
    hooked = True
    
    print("Программа активна. Используйте стрелки вверх/вниз для изменения хитбоксов, DEL для выхода.")
    
    while hooked:
        if keyboard.is_pressed("up"):
            hitbox_size = min(hitbox_size + 0.1, 2.0)  # Макс. 2x
            if inject_code(pid, hitbox_size):
                print(f"Хитбокс увеличен до {hitbox_size:.1f}x")
            time.sleep(0.2)
        
        if keyboard.is_pressed("down"):
            hitbox_size = max(hitbox_size - 0.1, 0.5)  # Мин. 0.5x
            if inject_code(pid, hitbox_size):
                print(f"Хитбокс уменьшен до {hitbox_size:.1f}x")
            time.sleep(0.2)
        
        if keyboard.is_pressed("delete"):
            print("Анхук. Выход...")
            hooked = False
        
        time.sleep(0.01)

if __name__ == "__main__":
    main()